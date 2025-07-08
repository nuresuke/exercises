from Akinator.models import Pokemon
import pandas as pd
from collections import defaultdict
from Akinator.management.commands.question_templates import *

def get_kanto_types_list():
    # カントー地方＝図鑑番号1〜151
    kanto_pokemon = (
        Pokemon.objects.filter(zukan_no__gte=1, zukan_no__lte=151)
        .order_by('zukan_no')
    )
    types_list = []
    for poke in kanto_pokemon:
        type_list = poke.type.split("/") if poke.type else []
        types_list.append(type_list)
    return types_list

from collections import defaultdict
from Akinator.models import Pokemon

def make_pokemon_list_and_categorical_values():
    def split_types(type_str):
        if not type_str:
            return []
        return type_str.split("/")
    pokemon_list = []
    categorical_values = defaultdict(set)
    # 必要なら.filter(zukan_no__gte=1, zukan_no__lte=151) でカントー限定も可
    for p in Pokemon.objects.all():
        poke = {
            "name":p.name,
            "type": split_types(p.type),
            "color": p.color,
            "habitat": p.habitat,
            "feature": p.feature,
            "has_special_skill": p.has_special_skill,
            "characteristic": p.characteristic,
            "initial": p.name[0] if p.name else "",
            "can_fly": bool(p.can_fly),
            "is_legendary": bool(p.is_legendary),
            "is_fossil": bool(p.is_fossil),
            "has_sash": bool(p.has_sash),
            "weight": float(p.weight),
            "height": float(p.height),
            "evolution": int(p.evolution),
        }
        pokemon_list.append(poke)
        # categorical値抽出
        for key, _ in CATEGORICAL_COLUMNS:
            val = poke.get(key)
            if isinstance(val, list):
                for v in val:
                    categorical_values[key].add(v)
            else:
                categorical_values[key].add(val)
    categorical_values = {k: sorted(list(vs)) for k, vs in categorical_values.items()}
    return pokemon_list, categorical_values

def generate_candidate_features(pokemon_list, question_list):
    features = []
    for poke in pokemon_list:  # pokeはdict
        poke_feat = []
        for q in question_list:
            key = q["key"]
            val = q["value"]
            poke_val = poke.get(key)
            # 属性の種類ごとに判定する
            if key in ["type", "color", "has_special_skill", "characteristic", "feature", "habitat", "initial"]:
                if isinstance(poke_val, list):
                    poke_feat.append(1 if val in poke_val else 0)
                else:
                    poke_feat.append(1 if val == poke_val else 0)
            elif key in ["can_fly", "is_legendary", "is_fossil", "has_sash"]:
                poke_feat.append(1 if bool(poke.get(key, False)) else 0)
            elif key in ["weight", "height", "evolution"]:
                try:
                    poke_feat.append(1 if float(poke.get(key, 0)) >= float(val) else 0)
                except Exception:
                    poke_feat.append(0)
            else:
                poke_feat.append(-1)  # 未知質問
        features.append(poke_feat)
    return features, question_list