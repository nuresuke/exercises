import tensorflow as tf
import numpy as np

class SimpleQuestionSelector:
    def __init__(self, model_path=None):
        if model_path:
            self.model = tf.keras.models.load_model(model_path)
        else:
            self.model = self._build_dummy_model()
    
    def _build_dummy_model(self):
        # モデル（入力: 368次元、出力: 368次元の質問スコア）
        model = tf.keras.Sequential([
            tf.keras.layers.InputLayer(input_shape=(368,)),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(368, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy')
        return model

    def predict_next_question(self, answers_vector):
        # answers_vector: shape=(10,) の前処理済みベクトル
        preds = self.model(np.array([answers_vector]))
        return np.argmax(preds)  # 一番スコアが高い質問インデックス