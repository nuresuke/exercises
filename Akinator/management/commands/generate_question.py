from Akinator.models import Pokemon
from .question_templates import CATEGORICAL_COLUMNS, BINARY_COLUMNS, NUMERIC_COLUMNS

def get_dynamic_questions():
    questions = []
    # カテゴリ型
    for key, template in CATEGORICAL_COLUMNS:
        values = (
            Pokemon.objects.values_list(key, flat=True)
            .exclude(**{f"{key}__isnull": True})
            .exclude(**{f"{key}": ""})
            .distinct()
        )
        for v in values:
            if v:
                questions.append({"key": key, "value": v, "text": template.format(v)})
    # バイナリ型
    for key, template in BINARY_COLUMNS:
        # 1:はい, 0:いいえ で想定
        questions.append({"key": key, "value": "1", "text": template})  # はい
        questions.append({"key": key, "value": "0", "text": template})  # いいえ
    # 数値型
    for key, template, thresholds in NUMERIC_COLUMNS:
        for threshold in thresholds:
            questions.append({"key": key, "value": str(threshold), "text": template.format(threshold)})
    return questions