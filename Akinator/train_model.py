import os
import sys
import django

# プロジェクトルート(EXERCISES)をsys.pathに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # 例: 'myproject.settings'
django.setup()

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from Akinator.models import Pokemon
from Akinator.utils import *


#　1.　DataFrame化
qs = Pokemon.objects.all().values()
df = pd.DataFrame(qs)

skill_list = sorted(list(Pokemon.objects.exclude(has_special_skill='').values_list('has_special_skill', flat=True).distinct()))
avil_list = sorted(list(Pokemon.objects.exclude(characteristic='').values_list('characteristic', flat=True).distinct()))

#　3.　特徴量ベクトル化関数
def encode_pokemon(row):
    vec = []
    vec.extend(one_hot_encode_type(row["type"]))       # タイプ
    vec.extend(one_hot_encode_color(row["color"]))          # 色
    vec.extend(one_hot_encode_skill(row["has_special_skill"], skill_list))
    vec.extend(one_hot_encode_avility(row["characteristic"],avil_list))
    vec.extend([int(row["can_fly"])])
    vec.extend([float(row["weight"]), float(row["height"])])
    vec.extend([float(row["evolution"])])
    vec.extend([int(row["is_legendary"])])
    vec.extend([int(row["is_fossil"])])
    vec.append(int(row["has_sash"]))

    return vec

#　4.　入力ベクトルX、ラベルyの作成
X = np.array([encode_pokemon(row) for i, row in df.iterrows()])
y = np.arange(len(df))  # 各ポケモン1サンプル、インデックスがラベル

# 5. one-hotラベル（Keras用）
y_cat = keras.utils.to_categorical(y, num_classes=len(df))

print("学習用特徴量ベクトルのshape:", X.shape)
print("1サンプルの次元数:", X.shape[1])

# 6. モデル構築
model = keras.Sequential([
    keras.layers.Input(shape=(X.shape[1],)),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(len(df), activation='softmax')
])
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 7. 学習
model.fit(X, y_cat, epochs=100, batch_size=16)

# 8. 保存
model.save("pokemon_filter_model.keras")