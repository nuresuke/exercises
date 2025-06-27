import os
from django.shortcuts import render
from Akinator.management.commands.generate_question import get_dynamic_questions
from django.conf import settings
from .models import Pokemon
from .tf_model import SimpleQuestionSelector
from .utils import *
import tensorflow as tf
import numpy as np

# Create your views here.
def index_view(request):
    return render(request, "interface/index.html")

def preparation_view(request):
    return render(request, "interface/preparation.html")

def explanation_view(request):
    return render(request, "interface/explanation.html")


#DjangoでDBからポケモン情報を取得し、TensorFlowモデルで条件を満たすポケモンだけ絞り込む基本構造
def filter_candidates(answers_vector):
    pokemons = Pokemon.objects.all()
    skill_list = sorted(list(Pokemon.objects.exclude(has_special_skill='').values_list('has_special_skill', flat=True).distinct()))
    avil_list = sorted(list(Pokemon.objects.exclude(characteristic='').values_list('characteristic', flat=True).distinct()))
    features = []
    valid_pokemons = []
    for p in pokemons:
        feature = []
        feature.extend(one_hot_encode_type(p.type))
        feature.extend(one_hot_encode_color(p.color))
        feature.extend(one_hot_encode_skill(p.has_special_skill, skill_list))
        feature.extend(one_hot_encode_avility(p.characteristic, avil_list))
        feature.extend([
            p.weight,
            p.height,
            float(p.evolution),
            int(p.can_fly),
            int(p.is_legendary),
            int(p.is_fossil),
            int(p.has_sash),
        ])
        compare_values = [
            p.type,             # 0: type
            p.color,            # 1: color
            p.has_special_skill,# 2: skill
            p.characteristic,   # 3: avility
            p.weight,           # 4: weight
            p.height,           # 5: height
            p.evolution,        # 6: evolution
            int(p.can_fly),     # 7: can_fly
            int(p.is_legendary),# 8: is_legendary
            int(p.is_fossil),   # 9: is_fossil
            int(p.has_sash),    # 10: has_sash
        ]
        is_candidate = True
        for i, ans in enumerate(answers_vector):
            if ans is None:
                continue
            print(f"compare_values[{i}]:", compare_values[i], type(compare_values[i]))
            print(f"ans[{i}]:", ans, type(ans))
            if str(compare_values[i]) != str(ans):
                is_candidate = False
                break
        if is_candidate:
            features.append(feature)
            valid_pokemons.append(p)

    if not features:
        return []

    features = np.array(features)
    MODEL_PATH = os.path.join(settings.BASE_DIR, "pokemon_filter_model.keras")
    model = tf.keras.models.load_model(MODEL_PATH)
    preds = model.predict(features)
    print("preds shape:", preds.shape)
    print("pred example:", preds[0])
    threshold = 0.95
    filtered_pokemons = [
    p for i, p in enumerate(valid_pokemons)
    if preds[i][i] > threshold
    ]
    return filtered_pokemons

def get_answers_vector(request):
    """
    質問リストとユーザー回答履歴（セッション）からanswers_vectorを作成
    """
    all_questions = get_dynamic_questions()
    user_answers = request.session.get("user_answers", {})
    answers_vector = []
    for q in all_questions:
        qid = q.get("id") or q.get("text")
        answer = user_answers.get(str(qid))
        if answer is None:
            answers_vector.append(None)
        else:
            answers_vector.append(answer)
    return answers_vector

def question_view(request):
     all_questions = get_dynamic_questions()
     answers_vector = get_answers_vector(request)
     safe_vector = [a if a is not None else -1 for a in answers_vector]

     # --- ポケモン候補絞り込み ---
     filtered_candidates = filter_candidates(answers_vector)

     # --- 次の質問をAIで選ぶ ---
     # モデルパスは「質問選択用」モデルにしてください
     #MODEL_PATH = os.path.join(settings.BASE_DIR, "question_selector_model.keras")
     selector = SimpleQuestionSelector()
     next_q_index = selector.predict_next_question(safe_vector)
     next_question = all_questions[next_q_index]

     # --- テンプレートに両方渡す！ ---
     return render(
         request,
        "interface/question.html",
        {
            "question": next_question,
            "candidates": filtered_candidates,
            "answers_vector": answers_vector,
        }
    )