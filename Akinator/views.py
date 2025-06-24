from django.shortcuts import render,redirect
from .models import Pokemon
import tensorflow as tf
import numpy as np

# Create your views here.
def index_view(request):
    return render(request, "interface/index.html")

def preparation_view(request):
    return render(request, "interface/preparation.html")

def explanation_view(request):
    return render(request, "interface/explanation.html")

def question_view(request):
    return render(request, "interface/question.html")


#文字列のベクトル化
def one_hot_encode_type(type_str):
    type_list = ['みず', 'ほのお', 'くさ','ノーマル', 'ほのお', 'みず', 'くさ', 'でんき', 'こおり', 'かくとう', 'どく', 'じめん', 'ひこう',
                 'エスパー', 'むし', 'いわ', 'ゴースト', 'ドラゴン', 'あく', 'はがね', 'フェアリー']  # すべてのタイプを列挙
    vec = [1 if type_str == t else 0 for t in type_list]
    return vec
def one_hot_encode_color(color_str):
    color_list = ['あか', 'あお', 'きいろ', 'みどり', 'くろ', 'しろ', 'ちゃいろ', 'オレンジ','むらさき', 'グレー', 'ピンク']
    vec = [1 if color_str == c else 0 for c in color_list]
    return vec

#DjangoでDBからポケモン情報を取得し、TensorFlowモデルで条件を満たすポケモンだけ絞り込む基本構造
def pokemon_list_view(request):
    # 1. DBから全ポケモン取得
    pokemons = Pokemon.objects.all()

    # 2. データをTensorFlow用に整形
    features = []
    for p in pokemons:
            feature = []
            feature.extend(one_hot_encode_type(p.type)),     # 文字列→One-Hot
            feature.extend(one_hot_encode_color(p.color)),    # 文字列→One-Hot
            feature.extend([
            p.weight,
            p.height,
            int(p.can_fly),
            int(p.is_legendary),
            int(p.is_fossil),
            int(p.has_special_skill),
            int(p.has_sash),
        ])
            features.append(feature)
    features = np.array(features)

    # 3. TensorFlowで絞り込み
    model = tf.keras.models.load_model('model_path')
    preds = model.predict(features)

    # しきい値を設定して、条件を満たすものだけ抽出
    filtered_pokemons = [p for p, pred in zip(pokemons, preds) if pred > 0.95]

    # 4. テンプレートに渡して表示
    return render(request, "interface/pokemon_list.html", {"pokemons": filtered_pokemons})
