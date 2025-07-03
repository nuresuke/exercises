import requests
import json

def get_jp_to_en_dict():
    jp_to_en = {}
    for i in range(1, 152):  # 1〜151番（初代）
        url = f"https://pokeapi.co/api/v2/pokemon-species/{i}/"
        resp = requests.get(url)
        data = resp.json()
        en_name = data["name"]  # 英語名スラッグ
        # 各言語名を探す
        ja_name = None
        for n in data["names"]:
            if n["language"]["name"] == "ja":
                ja_name = n["name"]
                break
        if ja_name:
            jp_to_en[ja_name] = en_name
            print(f"{ja_name}: {en_name}")
        else:
            print("日本語名見つからず", i)
    return jp_to_en

if __name__ == "__main__":
    jp_to_en = get_jp_to_en_dict()
    with open("pokemon_jp_to_en.json", "w", encoding="utf-8") as f:
        json.dump(jp_to_en, f, ensure_ascii=False, indent=2)
    print("Done! pokemon_jp_to_en.jsonを出力しました")