from django.test import TestCase

from django.test import TestCase, Client
from django.urls import reverse
from Akinator.models import Pokemon

class ViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
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

    def test_ut_013_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'interface/index.html')
        self.assertEqual(self.client.session.get('user_answers'), {})

    def test_ut_014_preparation_view(self):
        response = self.client.get(reverse('prepare_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'interface/preparation.html')

    def test_ut_015_explanation_view(self):
        response = self.client.get(reverse('explanation_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'interface/explanation.html')

    def test_ut_016_result_view_with_name(self):
        response = self.client.get(reverse('result_page'), {"name": "フシギダネ"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'interface/result.html')
        self.assertIn('jp_name', response.context)

    def test_ut_017_restart_view(self):
        session = self.client.session
        session['user_answers'] = {'0': 1}
        session['answers_history'] = [{'0': 1}]
        session.save()
        response = self.client.get(reverse('restart'))
        self.assertRedirects(response, reverse('question_page'))
        session = self.client.session
        self.assertEqual(session.get('user_answers'), {})
        self.assertEqual(session.get('answers_history'), [])

    def test_ut_018_question_view_not_correct_under_5(self):
        session = self.client.session
        session['not_correct_count'] = 0
        session.save()
        response = self.client.post(reverse('question_page'), {'action': 'not_correct'})
        self.assertRedirects(response, reverse('question_page'))
        session = self.client.session
        self.assertEqual(session.get('user_answers'), {})
        self.assertEqual(session.get('answers_history'), [])

    def test_ut_019_question_view_not_correct_5th(self):
        session = self.client.session
        session['not_correct_count'] = 4
        session.save()
        response = self.client.post(reverse('question_page'), {'action': 'not_correct'})
        self.assertTemplateUsed(response, 'interface/resultrender.html')
        session = self.client.session
        self.assertEqual(session.get('not_correct_count'), 0)

    def test_ut_020_question_view_undo_with_history(self):
        session = self.client.session
        session['answers_history'] = [{'0': 1}]
        session['user_answers'] = {'0': 1}
        session.save()
        response = self.client.post(reverse('question_page'), {'action': 'undo'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'interface/question.html')
        session = self.client.session
        self.assertEqual(session.get('user_answers'), {'0': 1})

    def test_ut_021_question_view_undo_no_history(self):
        session = self.client.session
        session['answers_history'] = []
        session.save()
        response = self.client.post(reverse('question_page'), {'action': 'undo'})
        self.assertRedirects(response, reverse('question_page'))
        session = self.client.session
        self.assertEqual(session.get('user_answers'), {})
        self.assertEqual(session.get('answers_history'), [])

    def test_ut_022_question_view_answer_unknown(self):
        response = self.client.post(reverse('question_page'), {'question_id': '0', 'answer': '-1'})
        session = self.client.session
        self.assertEqual(session.get('user_answers').get('0'), -2)

    def test_ut_023_question_view_answer_int(self):
        for val in ['0', '1']:
            response = self.client.post(reverse('question_page'), {'question_id': '0', 'answer': val})
            session = self.client.session
            self.assertIsInstance(session.get('user_answers').get('0'), int)

    def test_ut_024_question_view_one_candidate(self):
        # 1体のみになるような状態をモックする必要あり
        # ここではcontextにpoke_jp_nameが含まれることを確認
        response = self.client.get(reverse('question_page'))
        self.assertTemplateUsed(response, 'interface/prediction.html')
        self.assertIn('poke_jp_name', response.context)

    def test_ut_025_question_view_multiple_candidates(self):
        # 複数候補・質問残ありの状態
        response = self.client.get(reverse('question_page'))
        self.assertTemplateUsed(response, 'interface/question.html')
        self.assertIn('question', response.context)
        self.assertIn('candidates', response.context)
        self.assertIn('answers_vector', response.context)

    def test_ut_026_question_view_all_answered(self):
        session = self.client.session
        session['user_answers'] = {'0': 1, '1': 1}
        session.save()
        response = self.client.get(reverse('question_page'))
        self.assertTemplateUsed(response, 'interface/result.html')
        self.assertIn('candidates', response.context)
        self.assertIn('message', response.context)