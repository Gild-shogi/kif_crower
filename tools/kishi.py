import json

def number(player):
    path = "./player_num.json"
    with open(path, mode="r",  encoding="utf-8") as f:
        dic = json.load(f)
    return dic[player]