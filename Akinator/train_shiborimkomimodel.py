import os
import sys
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import pickle
from Akinator.utils import make_pokemon_list_and_categorical_values
from management.commands.generate_question import get_dynamic_questions
from management.commands.question_templates import *
# from Akinator.views import *  # 不要

def filter_candidates_by_answers(sample, candidates, candidate_features):
    """回答に基づいて候補を絞り込む"""
    filtered_candidates = []
    for candidate_idx in candidates:
        is_valid = True
        for q_idx, answer in enumerate(sample):
            if answer == -1:
                continue
            if candidate_features[candidate_idx][q_idx] != answer:
                is_valid = False
                break
        if is_valid:
            filtered_candidates.append(candidate_idx)
    return filtered_candidates

def select_best_question(sample, candidates, candidate_features):
    """エントロピーが最大になる質問を選択"""
    if not candidates:
        return -1
    best_idx = -1
    best_score = -1
    for qidx, ans in enumerate(sample):
        if ans != -1:
            continue
        yes_candidates = [i for i in candidates if candidate_features[i][qidx] == 1]
        no_candidates = [i for i in candidates if candidate_features[i][qidx] == 0]
        total_candidates = len(candidates)
        if total_candidates == 0:
            continue
        p_yes = len(yes_candidates) / total_candidates
        p_no = len(no_candidates) / total_candidates
        entropy = 0
        for p in [p_yes, p_no]:
            if p > 0:
                entropy -= p * np.log2(p)
        if entropy > best_score:
            best_score = entropy
            best_idx = qidx
    return best_idx

def generate_candidate_features(pokemon_list, question_list):
    """
    pokemon_list: 各ポケモンのdictリスト
    question_list: get_dynamic_questionsで得たdictリスト
    戻り値: 全ポケモン×全質問 の0/1/-1テーブル, question_list
    """
    features = []
    for poke in pokemon_list:
        poke_feat = []
        for q in question_list:
            key = q["key"]
            val = q["value"]
            # key種別ごとに判定
            poke_val = poke.get(key)
            if key in ["type", "color", "has_special_skill", "characteristic"]:
                # typeやskill等
                if isinstance(poke_val, list):
                    poke_feat.append(1 if val in poke_val else 0)
                else:
                    poke_feat.append(1 if val == poke_val else 0)
            elif key in ["can_fly", "is_legendary", "is_fossil", "has_sash"]:
                poke_feat.append(1 if bool(poke.get(key, False)) else 0)
            elif key in ["weight", "height", "evolution"]:
                try:
                    poke_feat.append(1 if float(poke.get(key, 0)) >= float(val) else 0)
                except Exception:
                    poke_feat.append(0)
            else:
                poke_feat.append(-1)  # 未知質問など
        features.append(poke_feat)
        
    print("最終features shape:", len(features), len(features[0]))
    print("最終question_list件数:", len(question_list))
    return features, question_list

def generate_realistic_sample(pokemon_list, candidate_features, max_questions=10):
    """より現実的な学習サンプルを生成"""
    num_questions = len(candidate_features[0])
    sample = [-1] * num_questions
    candidates = list(range(len(pokemon_list)))
    question_sequence = []
    for _ in range(max_questions):
        if len(candidates) <= 1:
            break
        next_q = select_best_question(sample, candidates, candidate_features)
        if next_q == -1:
            break
        answer = np.random.choice([0, 1])
        sample[next_q] = answer
        candidates = filter_candidates_by_answers(sample, candidates, candidate_features)
        question_sequence.append(next_q)
        if not candidates:
            break
    return sample, question_sequence

# ============ main ===============

num_samples = 2000
pokemon_list, categorical_values = make_pokemon_list_and_categorical_values()
question_list = get_dynamic_questions()  # ←本番と同じdictリスト
candidate_features, question_list = generate_candidate_features(pokemon_list, question_list)

num_questions = len(question_list)
num_pokemons = len(pokemon_list)

print(f"ポケモン数: {num_pokemons}")
print(f"質問数: {num_questions}")

X = []
y = []
valid_samples = 0

for i in range(num_samples):
    if i % 500 == 0:
        print(f"サンプル生成中: {i}/{num_samples}")
    try:
        sample, question_sequence = generate_realistic_sample(
            pokemon_list, candidate_features, max_questions=8
        )
        temp_sample = [-1] * num_questions
        temp_candidates = list(range(num_pokemons))
        for step, asked_q in enumerate(question_sequence):
            next_q = select_best_question(temp_sample, temp_candidates, candidate_features)
            if next_q != -1 and len(temp_candidates) > 1:
                X.append(temp_sample.copy())
                y.append(next_q)
                valid_samples += 1
            temp_sample[asked_q] = sample[asked_q]
            temp_candidates = filter_candidates_by_answers(temp_sample, temp_candidates, candidate_features)
            if len(temp_candidates) <= 1:
                break
    except Exception as e:
        print(f"サンプル生成エラー: {e}")
        continue

print(f"有効なサンプル数: {valid_samples}")

if valid_samples == 0:
    print("有効なサンプルが生成されませんでした。")
    sys.exit(1)

X = np.array(X)
y = np.array(y)

X_embed = X + 1  # -1,0,1→0,1,2

print(f"学習データ形状: {X.shape}")
print(f"ラベルデータ形状: {y.shape}")

model = keras.Sequential([
    layers.Input(shape=(num_questions,)),
    layers.Embedding(input_dim=3, output_dim=16),
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(64, activation='relu'),
    layers.Dense(num_questions, activation='softmax'),
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("モデル学習開始...")
history = model.fit(
    X_embed, y,
    epochs=20,
    batch_size=32,
    validation_split=0.2,
    verbose=1
)

model.save("question_selector_model.keras")
print("モデルを保存しました: question_selector_model.keras")

print(f"最終訓練精度: {history.history['accuracy'][-1]:.4f}")
print(f"最終検証精度: {history.history['val_accuracy'][-1]:.4f}")

model_config = {
    'num_questions': num_questions,
    'num_pokemons': num_pokemons,
    'model_type': 'question_selector'
}

with open('model_config.pkl', 'wb') as f:
    pickle.dump(model_config, f)
with open('question_list.pkl', 'wb') as f:
    pickle.dump(question_list, f)
with open('candidate_features.pkl', 'wb') as f:
    pickle.dump(candidate_features, f)
with open('pokemon_list.pkl', 'wb') as f:
    pickle.dump(pokemon_list, f)

print("すべてのデータファイルが正常に保存されました！")