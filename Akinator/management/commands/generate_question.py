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
    "feature": 11,
    "habitat": 12,
    "initial": 13,
}

def get_dynamic_questions(pokemon_list):
    questions = []

    # CATEGORICAL系全値バリエーション
    for key, template in CATEGORICAL_COLUMNS:
        unique_values = set()
        for poke in pokemon_list:
            v = poke.get(key)
            if isinstance(v, list):
                unique_values.update(v)
            elif v is not None:
                unique_values.add(v)
        for val in unique_values:
            qid = f"{key}:{val}"
            text = template.format(val)
            attr_index = ATTR_INDEX_MAP.get(key)
            questions.append({
                "id": qid,
                "key": key,
                "value": val,
                "text": text,
                "attr_index": attr_index,
            })

    # BINARY, NUMERIC系も同様に追加
    for key, template in BINARY_COLUMNS:
        qid = f"{key}:1"
        attr_index = ATTR_INDEX_MAP.get(key)
        questions.append({
            "id": qid,
            "key": key,
            "value": "1",
            "text": template,
            "attr_index": attr_index,
        })

    for key, template, thresholds in NUMERIC_COLUMNS:
        attr_index = ATTR_INDEX_MAP.get(key)
        for val in thresholds:
            qid = f"{key}:{val}"
            text = template.format(val)
            questions.append({
                "id": qid,
                "key": key,
                "value": val,
                "text": text,
                "attr_index": attr_index,
            })

    return questions