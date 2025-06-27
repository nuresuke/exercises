from .question_ids import QUESTION_ID_LIST
from .question_templates import CATEGORICAL_COLUMNS, BINARY_COLUMNS, NUMERIC_COLUMNS

def get_dynamic_questions():
    cat_templates = dict(CATEGORICAL_COLUMNS)
    bin_templates = dict(BINARY_COLUMNS)
    num_templates = {k: t for k, t, _ in NUMERIC_COLUMNS}
    questions = []
    for qid in QUESTION_ID_LIST:
        key, value = qid.split(":", 1)
        if key in cat_templates:
            text = cat_templates[key].format(value)
        elif key in bin_templates:
            text = bin_templates[key]
        elif key in num_templates:
            text = num_templates[key].format(value)
        else:
            text = qid
        questions.append({"id": qid, "key": key, "value": value, "text": text})
    return questions