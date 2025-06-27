import os
import django

# 1. 環境変数を設定（プロジェクト名は自分の settings.py があるディレクトリ名に合わせて！）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# 2. Djangoを初期化
django.setup()
from Akinator.management.commands.generate_question import get_dynamic_questions

def main():
    questions = get_dynamic_questions()
    question_ids = [q["id"] for q in questions]
    with open("question_ids.py", "w", encoding="utf-8") as f:
        f.write("QUESTION_ID_LIST = [\n")
        for qid in question_ids:
            f.write(f'    "{qid}",\n')
        f.write("]\n")

if __name__ == "__main__":
    main()