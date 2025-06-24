CATEGORICAL_COLUMNS = [
    ("type", "{}タイプですか？"),
    ("color", "色は{}ですか？"),
    ("habitat", "{}に生息していますか？"),
    ("feature", "外見的特徴は「{}」ですか？"),
    ("has_special_skill", "{}を覚えますか？"),
    ("characteristic", "特性は{}ですか？"),
    ("initial", "ポケモン名の頭文字は「{}」ですか？"),
]

BINARY_COLUMNS = [
    ("can_fly", "空を飛べますか？"),
    ("is_legendary", "伝説のポケモンですか？"),
    ("is_fossil", "化石ポケモンですか？"),
    ("has_sash", "そのポケモンはサトシが持っていましたか？"),
]

NUMERIC_COLUMNS = [
    ("weight", "重さは{}kg以上ですか？", [10, 30, 100]),
    ("height", "大きさは{}m以上ですか？", [1, 2, 5]),
    ("evolution", "進化段階は{}以上ですか？", [2, 3]),
]
