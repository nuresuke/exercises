from .question_ids import QUESTION_ID_LIST
from .question_templates import CATEGORICAL_COLUMNS, BINARY_COLUMNS, NUMERIC_COLUMNS

# 属性名→compare_valuesのインデックス対応表
ATTR_INDEX_MAP = {
    "type": 0,
    "color": 1,
    "has_special_skill": 2,
    "characteristic": 3,
    "weight": 4,
    "height": 5,
    "evolution": 6,
    "can_fly": 7,
    "is_legendary": 8,
    "is_fossil": 9,
    "has_sash": 10,
}

def get_dynamic_questions():
    cat_templates = dict(CATEGORICAL_COLUMNS)
    bin_templates = dict(BINARY_COLUMNS)
    num_templates = {k: t for k, t, _ in NUMERIC_COLUMNS}
    questions = []
    for qid in QUESTION_ID_LIST:
        key, value = qid.split(":", 1)
        # attr_indexを決定（なければNone）
        attr_index = ATTR_INDEX_MAP.get(key, None)
        if key in cat_templates:
            text = cat_templates[key].format(value)
        elif key in bin_templates:
            text = bin_templates[key]
        elif key in num_templates:
            text = num_templates[key].format(value)
        else:
            text = qid
        questions.append({"id": qid, "key": key, "value": value, "text": text,"attr_index": attr_index,})
    return questions