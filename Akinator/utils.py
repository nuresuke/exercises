#文字列のベクトル化
def one_hot_encode_type(type_str):
    type_list = ['みず', 'ほのお', 'くさ','ノーマル', 'でんき', 'こおり', 'かくとう', 'どく', 'じめん', 'ひこう',
                 'エスパー', 'むし', 'いわ', 'ゴースト', 'ドラゴン', 'あく', 'はがね', 'フェアリー']
    vec = [0] * len(type_list)
    if type_str:
        for t in type_str.split('/'):
            t = t.strip()
            if t in type_list:
                vec[type_list.index(t)] = 1
    return vec

def one_hot_encode_color(color_str):
    color_list = ['あか', 'あお', 'きいろ', 'みどり', 'くろ', 'しろ', 'ちゃいろ', 'オレンジ','むらさき', 'グレー', 'ピンク']
    vec = [1 if color_str == c else 0 for c in color_list]
    return vec

def one_hot_encode_skill(skill, skill_list):
    return [1 if skill == m else 0 for m in skill_list]

def one_hot_encode_avility(avil,avil_list):
    return[1 if avil == m else 0 for m in avil_list]