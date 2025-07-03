import json
import os
from django.shortcuts import render
from Akinator.management.commands.generate_question import get_dynamic_questions
from django.conf import settings
from .models import Pokemon
from .tf_model import SimpleQuestionSelector
from .utils import *
import tensorflow as tf
import numpy as np
import pickle

with open("pokemon_jp_to_en.json", encoding="utf-8") as f:
        JP_TO_EN = json.load(f)

def load_ai_model_data():
    with open('question_list.pkl', 'rb') as f:
        question_list = pickle.load(f)
    with open('pokemon_list.pkl', 'rb') as f:
        pokemon_list = pickle.load(f)
    with open('candidate_features.pkl', 'rb') as f:
        candidate_features = pickle.load(f)
        
    # ここでprintしてみる
    print("question_list[0]", question_list[0])
    print("pokemon_list[0]", pokemon_list[0])
    print("features[0]", candidate_features[0])

def index_view(request):
    request.session["user_answers"] = {}
    request.session.modified = True
    return render(request, "interface/index.html")

def preparation_view(request):
    return render(request, "interface/preparation.html")

def explanation_view(request):
    return render(request, "interface/explanation.html")

import os
from django.shortcuts import render
from django.conf import settings
import pickle
import numpy as np
import tensorflow as tf

def load_ai_model_data():
    with open('question_list.pkl', 'rb') as f:
        question_list = pickle.load(f)
    with open('pokemon_list.pkl', 'rb') as f:
        pokemon_list = pickle.load(f)
    with open('candidate_features.pkl', 'rb') as f:
        candidate_features = pickle.load(f)
    MODEL_PATH = os.path.join(settings.BASE_DIR, "question_selector_model.keras")
    model = tf.keras.models.load_model(MODEL_PATH)
    return {
        'questions': question_list,
        'pokemons': pokemon_list,
        'features': candidate_features,
        'model': model,
    }

def get_poke_table():
    poke_table = {}
    for p in Pokemon.objects.all():
        en_name = JP_TO_EN.get(p.name)
        if not en_name:
            continue  # 変換できない場合はスキップ
        poke_table[en_name] = {
            "number": f"No.{p.zukan_no:04d}",
            "name": p.name
        }
    return poke_table


def get_answers_vector(request, questions):
    user_answers = request.session.get("user_answers", {})
    answers_vector = []
    for q in questions:
        qid = q.get("id")
        answer = user_answers.get(str(qid))
        answers_vector.append(-1 if answer is None else answer)
    print("answers_vector:", answers_vector)
    return answers_vector

def filter_candidates_by_ai_answers(answers_vector, ai_data):
    candidate_features = ai_data['features']
    pokemon_list = ai_data['pokemons']
    filtered_candidates = []
    debug_info = []
    for i, pokemon in enumerate(pokemon_list):
        is_valid = True
        for q_idx, answer in enumerate(answers_vector):
            if answer == -1:
                continue
            feature_val = candidate_features[i][q_idx]
            if feature_val == -1:
                continue
            if int(feature_val) != int(answer):
                is_valid = False
                debug_info.append(
                    f"{pokemon['name']} 除外: 質問{q_idx} answer={answer}, feature_val={feature_val}"
                )
                break
        if is_valid:
            filtered_candidates.append(pokemon)
    print(f"候補: {len(filtered_candidates)}/{len(pokemon_list)}")
    print("\n".join(debug_info[:151]))  # 最初の50件だけ
    print(filtered_candidates)
    return filtered_candidates

def select_next_question_ai(answers_vector, ai_data):
    model = ai_data['model']
    num_questions = len(ai_data['questions'])
    X_input = np.array([answers_vector + [-1]*(num_questions-len(answers_vector))]) + 1
    predictions = model.predict(X_input, verbose=0)
    sorted_indices = np.argsort(predictions[0])[::-1]
    for idx in sorted_indices:
        if answers_vector[idx] == -1:
            return idx
    return None

def question_view(request):
    ai_data = load_ai_model_data()
    questions = ai_data['questions']

    if request.method == "POST":
        qid = request.POST.get("question_id")
        answer = request.POST.get("answer")
        if qid is not None:
            user_answers = request.session.get("user_answers", {})
            user_answers[str(qid)] = int(answer)
            request.session["user_answers"] = user_answers
            request.session.modified = True

    answers_vector = get_answers_vector(request, questions)
    filtered_candidates = filter_candidates_by_ai_answers(answers_vector, ai_data)
    print(f"候補数: {len(filtered_candidates)}")

    next_q_index = select_next_question_ai(answers_vector, ai_data)
    if next_q_index is None:
        for i, ans in enumerate(answers_vector):
            if ans == -1:
                next_q_index = i
                break

    if next_q_index is not None and 0 <= next_q_index < len(questions):
        next_question = questions[next_q_index]
    else:
        return render(request, "interface/result.html", {
            "candidates": filtered_candidates,
            "message": "全ての質問に回答しました"
        })

    if len(filtered_candidates) <= 1:
        poke_table = get_poke_table()
        poke_table_json = json.dumps(poke_table, ensure_ascii=False)
        # 候補が存在する場合、その名前を取得
        poke_name = filtered_candidates[0]['name'] if filtered_candidates else None
        # 英語名も渡したい場合（例: 'en_name'キーがあれば）
        poke_en_name = JP_TO_EN.get(poke_name) if poke_name else None
        return render(request, "interface/prediction.html", {
        "candidates": filtered_candidates,
        "confidence": 1.0 if filtered_candidates else 0.0,
        "poke_en_name": poke_en_name,
        "poke_table_json": poke_table_json
        })

    return render(
        request,
        "interface/question.html",
        {
            "question": next_question,
            "candidates": filtered_candidates,
            "answers_vector": answers_vector,
        }
    )
