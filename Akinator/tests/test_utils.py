import os
import pickle
import json
import shutil
from django.db import connection
from django.test import TestCase
from django.conf import settings
from Akinator.views import (
    load_ai_model_data,
    get_poke_table,
    get_answers_vector,
    filter_candidates_by_ai_answers,
    select_humanlike_next_question,
    select_next_question_ai,
)
from Akinator.models import Pokemon

class UtilsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # テスト用DBに pokemons テーブルを作成
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pokemons (
                    "図鑑番号" INTEGER PRIMARY KEY,
                    "ポケモン名" VARCHAR(20) NOT NULL,
                    "タイプ" VARCHAR(10) NOT NULL,
                    "色" VARCHAR(20) NOT NULL,
                    "重さ" FLOAT NOT NULL,
                    "大きさ" FLOAT NOT NULL,
                    "進化段階" INTEGER NOT NULL,
                    "飛行可能か" BOOLEAN NOT NULL,
                    "生息地" VARCHAR(50) NOT NULL,
                    "伝説のポケモン" BOOLEAN NOT NULL,
                    "外見的特徴" VARCHAR(50) NOT NULL,
                    "化石ポケモン" BOOLEAN NOT NULL,
                    "代表的な技" VARCHAR(20) NOT NULL,
                    "サトシの所持の有無" BOOLEAN NOT NULL,
                    "特性" VARCHAR(10) NOT NULL,
                    "頭文字" CHAR(1) NOT NULL
                );
            """)
    @classmethod
    def setUpTestData(cls):
        # バックアップ
        for fname in ['question_list.pkl', 'pokemon_list.pkl', 'candidate_features.pkl', 'pokemon_jp_to_en.json',"question_selector_model.keras"]:
            if os.path.exists(fname):
                shutil.copy(fname, fname + '.bak')
        # ダミーデータ作成
        cls.dummy_questions = [{"id": 0, "text": "type:くさ"}, {"id": 1, "text": "type:ほのお"}]
        cls.dummy_pokemons = [{"name": "フシギダネ"}, {"name": "ヒトカゲ"}]
        cls.dummy_features = [[1, 0], [0, 1]]
        cls.dummy_model_path = os.path.join(settings.BASE_DIR, "question_selector_model.keras")
        # ダミーpickle作成
        with open('question_list.pkl', 'wb') as f:
            pickle.dump(cls.dummy_questions, f)
        with open('pokemon_list.pkl', 'wb') as f:
            pickle.dump(cls.dummy_pokemons, f)
        with open('candidate_features.pkl', 'wb') as f:
            pickle.dump(cls.dummy_features, f)
        # ダミーKerasモデル保存
        import tensorflow as tf
        import numpy as np
        from tensorflow import keras
        X = np.random.randint(0, 2, size=(2, 2))
        y = np.random.randint(0, 2, size=(2, 2))
        model = keras.Sequential([
            keras.layers.Input(shape=(2,)),
            keras.layers.Dense(2, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy')
        model.fit(X, y, epochs=1, verbose=0)
        model.save(cls.dummy_model_path)

        # JP_TO_ENダミー作成
        with open("pokemon_jp_to_en.json", "w", encoding="utf-8") as f:
            json.dump({"フシギダネ": "Bulbasaur", "ヒトカゲ": "Charmander"}, f)

    def test_ut_001_load_ai_model_data_normal(self):
        result = load_ai_model_data()
        self.assertIn('questions', result)
        self.assertIn('pokemons', result)
        self.assertIn('features', result)
        self.assertIn('model', result)
        self.assertIsInstance(result['questions'], list)
        self.assertIsInstance(result['pokemons'], list)
        self.assertIsInstance(result['features'], list)

    def test_ut_002_load_ai_model_data_file_not_found(self):
        os.rename('question_list.pkl', 'question_list_bak.pkl')
        try:
            with self.assertRaises(FileNotFoundError):
                load_ai_model_data()
        finally:
            os.rename('question_list_bak.pkl', 'question_list.pkl')

    def test_ut_003_get_poke_table_no_jp_to_en(self):
        Pokemon.objects.create(
    zukan_no=151,
    name="ミュコ",
    type="エスパー",
    color="ピンク",
    weight=4.0,
    height=0.4,
    evolution=1,
    can_fly=False,
    habitat="未知",
    is_legendary=True,
    feature="浮遊",
    is_fossil=False,
    has_special_skill="へんしん",
    has_sash=False,
    characteristic="シンクロ",
    initial="ミ"
)
        with open("pokemon_jp_to_en.json", "w", encoding="utf-8") as f:
            json.dump({"フシギダネ": "Bulbasaur"}, f)
        result = get_poke_table()
        self.assertNotIn("ミュコ", [v["name"] for v in result.values()])

    def test_ut_004_get_poke_table_exists_in_jp_to_en(self):
        Pokemon.objects.create(
        zukan_no=1,
        name="フシギダネ",
        type="くさ",
        color="みどり",
        weight=6.9,
        height=0.7,
        evolution=1,
        can_fly=False,
        habitat="草原",
        is_legendary=False,
        feature="なし",
        is_fossil=False,
        has_special_skill="はっぱカッター",
        has_sash=False,
        characteristic="しんりょく",
        initial="フ"
        )
        with open("pokemon_jp_to_en.json", "w", encoding="utf-8") as f:
            json.dump({"フシギダネ": "Bulbasaur"}, f)
        result = get_poke_table()
        self.assertIn("bulbasaur", result)
        self.assertEqual(result["bulbasaur"]["number"], "No.0001")
        self.assertEqual(result["bulbasaur"]["name"], "フシギダネ")

    def test_ut_005_get_answers_vector_all_unanswered(self):
        class DummyRequest:
            session = {"user_answers": {}}
        questions = [{"id": 0}, {"id": 1}]
        result = get_answers_vector(DummyRequest(), questions)
        self.assertEqual(result, [-1, -1])

    def test_ut_006_get_answers_vector_unknown(self):
        class DummyRequest:
            session = {"user_answers": {"0": -2}}
        questions = [{"id": 0}, {"id": 1}]
        result = get_answers_vector(DummyRequest(), questions)
        self.assertEqual(result, [-2, -1])

    def test_ut_007_filter_candidates_partial_match(self):
        ai_data = {
            'features': [[1, 0], [0, 1]],
            'pokemons': [{"name": "フシギダネ"}, {"name": "ヒトカゲ"}]
        }
        answers_vector = [1, -1]
        result = filter_candidates_by_ai_answers(answers_vector, ai_data)
        self.assertTrue(any([p['name']=="フシギダネ" for p in result]))
        self.assertFalse(any([p['name']=="ヒトカゲ" for p in result]))

    def test_ut_008_filter_candidates_all_unanswered(self):
        ai_data = {
            'features': [[1, 0], [0, 1]],
            'pokemons': [{"name": "フシギダネ"}, {"name": "ヒトカゲ"}]
        }
        answers_vector = [-1, -1]
        result = filter_candidates_by_ai_answers(answers_vector, ai_data)
        self.assertEqual(len(result), 2)

    def test_ut_009_select_humanlike_next_question_distinguishable(self):
        ai_data = {
            'features': [[1, 0], [0, 1]],
            'pokemons': [{"name": "フシギダネ"}, {"name": "ヒトカゲ"}]
        }
        answers_vector = [-1, -1]
        filtered_candidates = ai_data['pokemons']
        qidx = select_humanlike_next_question(answers_vector, filtered_candidates, ai_data)
        self.assertIn(qidx, [0, 1])

    def test_ut_010_select_humanlike_next_question_not_distinguishable(self):
        ai_data = {
            'features': [[1, 1], [1, 1]],
            'pokemons': [{"name": "フシギダネ"}, {"name": "ヒトカゲ"}],
            'model': load_ai_model_data()['model'],
            'questions': [{"id": 0}, {"id": 1}]
        }
        answers_vector = [-1, -1]
        filtered_candidates = ai_data['pokemons']
        qidx = select_humanlike_next_question(answers_vector, filtered_candidates, ai_data)
        self.assertIsNotNone(qidx)  # AI fallback

    def test_ut_011_select_humanlike_next_question_unique_feature(self):
        ai_data = {
            'features': [[1, 0], [0, 1], [1, 1]],
            'pokemons': [{"name": "A"}, {"name": "B"}, {"name": "C"}],
            'model': load_ai_model_data()['model'],
            'questions': [{"id": 0}, {"id": 1}]
        }
        answers_vector = [-1, -1]
        filtered_candidates = ai_data['pokemons']
        qidx = select_humanlike_next_question(answers_vector, filtered_candidates, ai_data)
        self.assertIn(qidx, [0, 1])

    def test_ut_012_select_next_question_ai_unanswered(self):
        ai_data = {
            'features': [[1, 0], [0, 1]],
            'pokemons': [{"name": "A"}, {"name": "B"}],
            'questions': [{"id": 0}, {"id": 1}],
            'model': load_ai_model_data()['model']
        }
        answers_vector = [-1, -1]
        idx = select_next_question_ai(answers_vector, ai_data)
        self.assertIn(idx, [0, 1])
        
    @classmethod
    def tearDownClass(cls):
        # バックアップ復元
        for fname in ['question_list.pkl', 'pokemon_list.pkl', 'candidate_features.pkl', 'pokemon_jp_to_en.json',"question_selector_model.keras"]:
            bak = fname + '.bak'
            if os.path.exists(bak):
                shutil.move(bak, fname)
        super().tearDownClass()