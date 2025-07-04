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
from Akinator.utils import *
from management.commands.generate_question import get_dynamic_questions
from management.commands.question_templates import *

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

def calculate_information_gain(sample, question_idx, candidates, candidate_features):
    """dictベースで情報ゲイン（候補減少率の平均）を計算"""
    current_candidates = filter_candidates_by_answers(sample, candidates, candidate_features)
    current_count = len(current_candidates)
    if current_count <= 1:
        return 0.0
    gains = []
    for answer in [0, 1]:
        test_sample = sample.copy()
        test_sample[question_idx] = answer
        test_candidates = filter_candidates_by_answers(test_sample, candidates, candidate_features)
        test_count = len(test_candidates)
        reduction_ratio = (current_count - test_count) / current_count if current_count > 0 else 0.0
        gains.append(reduction_ratio)
    return np.mean(gains) if gains else 0.0

def find_distinguishing_question_idx(sample, candidates, candidate_features):
    """
    候補が2体のときに、その2体を区別できる質問インデックスを返す
    """
    if len(candidates) != 2:
        return None
    idx1, idx2 = candidates
    for qidx, ans in enumerate(sample):
        if ans != -1:
            continue
        val1 = candidate_features[idx1][qidx]
        val2 = candidate_features[idx2][qidx]
        if (val1 == 1 and val2 == 0) or (val1 == 0 and val2 == 1):
            return qidx
    return None

def find_unique_question_idx(sample, candidates, candidate_features):
    """
    候補が3〜5体のときに、1体だけYESで他はNOな質問インデックスを返す
    """
    for qidx, ans in enumerate(sample):
        if ans != -1:
            continue
        yes_candidates = [idx for idx in candidates if candidate_features[idx][qidx] == 1]
        if len(yes_candidates) == 1:
            return qidx
    return None

# ============ main ===============

num_samples = 1000  # 必要に応じて調整
pokemon_list, categorical_values = make_pokemon_list_and_categorical_values()
question_list = get_dynamic_questions()
candidate_features, question_list = generate_candidate_features(pokemon_list, question_list)

num_questions = len(question_list)
num_pokemons = len(pokemon_list)

print(f"ポケモン数: {num_pokemons}")
print(f"質問数: {num_questions}")
print(f"質問例: {question_list[0] if question_list else 'None'}")

X = []
y = []

for sample_idx in range(num_samples):
    if sample_idx % 100 == 0:
        print(f"サンプル生成中: {sample_idx}/{num_samples}")

    # ランダムな回答状態を生成（-1: 未回答, 0: いいえ, 1: はい）
    sample = []
    for _ in range(num_questions):
        choice = np.random.choice([-1, 0, 1], p=[0.7, 0.15, 0.15])
        sample.append(choice)

    # 現在の候補を算出
    candidates = filter_candidates_by_answers(sample, list(range(num_pokemons)), candidate_features)

    # ========== 区別質問ロジック ==========

    # 2体のときは区別質問
    if len(candidates) == 2:
        qidx = find_distinguishing_question_idx(sample, candidates, candidate_features)
        question_scores = [0.0] * num_questions
        if qidx is not None:
            question_scores[qidx] = 1.0
        else:
            question_scores = [1.0 / num_questions] * num_questions
        X.append(sample.copy())
        y.append(question_scores)
        continue

    # 3〜5体のときはユニーク特徴を優先
    if 2 < len(candidates) <= 5:
        qidx = find_unique_question_idx(sample, candidates, candidate_features)
        question_scores = [0.0] * num_questions
        if qidx is not None:
            question_scores[qidx] = 1.0
            X.append(sample.copy())
            y.append(question_scores)
            continue
        # ユニーク特徴がなければ情報ゲインでOK

    # ========== 通常情報ゲインロジック ==========
    question_scores = []
    for question_idx in range(num_questions):
        if sample[question_idx] == -1:
            score = calculate_information_gain(sample, question_idx, candidates, candidate_features)
        else:
            score = 0.0
        question_scores.append(score)
    max_score = max(question_scores) if max(question_scores) > 0 else 1
    if max_score > 0:
        question_scores = [score / max_score for score in question_scores]
    else:
        question_scores = [1.0 / num_questions] * num_questions

    X.append(sample.copy())
    y.append(question_scores)

X = np.array(X)
y = np.array(y)

print(f"データサイズ: X={X.shape}, y={y.shape}")

# 質問選択モデル
model = keras.Sequential([
    keras.layers.Input(shape=(X.shape[1],)),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(y.shape[1], activation='softmax')
])

model.compile(
    optimizer='adam', 
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("モデル訓練開始...")
history = model.fit(
    X, y, 
    epochs=20,
    batch_size=32,
    validation_split=0.2,
    verbose=1
)

model.save("question_selection_model.keras")
print("モデルを保存しました: question_selection_model.keras")

model_config = {
    'num_questions': num_questions,
    'num_pokemons': num_pokemons,
    'model_type': 'question_selection'
}
with open('question_selection_model_config.pkl', 'wb') as f:
    pickle.dump(model_config, f)
with open('question_list.pkl', 'wb') as f:
    pickle.dump(question_list, f)
with open('candidate_features.pkl', 'wb') as f:
    pickle.dump(candidate_features, f)
with open('pokemon_list.pkl', 'wb') as f:
    pickle.dump(pokemon_list, f)

print("すべてのデータファイルが正常に保存されました！")