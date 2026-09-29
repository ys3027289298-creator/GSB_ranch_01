"""牧场核心逻辑：牲畜、草场、饲料和兽医。"""

import json

MAX_FEED = 100
MAX_HEALTH = 100
BREED_REFUND = 10
DISEASE_COST = 10
TREAT_HEAL = 10


def new_game():
    return {
        "livestock": {},
        "pasture_capacity": 2,
        "feed": 100,
        "water": 100,
        "day": 1,
        "stock_id": 0,
        "vets": ["V1"],
        "grazing": [],
        "cancelled_breeds": [],
        "last_disease_day": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    if not text or not text.strip():
        return new_game()
    return json.loads(text)


def register(state, animal_id):
    if not animal_id or animal_id in state["livestock"]:
        return False
    state["livestock"][animal_id] = {"health": 100}
    state["stock_id"] = state.get("stock_id", 0) + 1
    return True


def graze(state, animal_id):
    if animal_id not in state["livestock"]:
        return False
    grazing = state.setdefault("grazing", [])
    if animal_id in grazing:
        return True
    if len(grazing) >= state["pasture_capacity"]:
        return False
    grazing.append(animal_id)
    return True


def feed_days(state, animal_id, end_day):
    days = end_day - state["day"]
    return days if days > 0 else 0


def cancel_breed(state, animal_id):
    cancelled = state.setdefault("cancelled_breeds", [])
    if animal_id in cancelled:
        return False
    cancelled.append(animal_id)
    state["feed"] = min(MAX_FEED, state["feed"] + BREED_REFUND)
    return True


def treat(state, animal_id, vet):
    if vet not in state.get("vets", []):
        return False
    animal = state["livestock"].get(animal_id)
    if animal is None:
        return False
    animal["health"] = min(MAX_HEALTH, animal["health"] + TREAT_HEAL)
    return True


def disease(state):
    if state.get("last_disease_day") == state["day"]:
        return False
    state["last_disease_day"] = state["day"]
    for animal in state["livestock"].values():
        animal["health"] = max(0, animal["health"] - DISEASE_COST)
    return True


def gain(state, animal_id):
    if state.get("water", 0) <= 0:
        return False
    animal = state["livestock"].get(animal_id)
    if animal is None:
        return False
    state["water"] -= 1
    animal["weight"] = animal.get("weight", 0) + 1
    return True


def main():
    print("牧场 - 命令: register/graze/feed/breed/treat/disease/gain/quit")
    state = new_game()
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        parts = raw.split()
        cmd, args = parts[0], parts[1:]
        if cmd == "register" and len(args) == 1:
            print("ok" if register(state, args[0]) else "fail")
        elif cmd == "graze" and len(args) == 1:
            print("ok" if graze(state, args[0]) else "fail")
        elif cmd == "feed" and len(args) == 2 and args[1].isdigit():
            print(feed_days(state, args[0], int(args[1])))
        elif cmd == "breed" and len(args) == 1:
            print("ok" if cancel_breed(state, args[0]) else "fail")
        elif cmd == "treat" and len(args) == 2:
            print("ok" if treat(state, args[0], args[1]) else "fail")
        elif cmd == "disease" and not args:
            print("ok" if disease(state) else "fail")
        elif cmd == "gain" and len(args) == 1:
            print("ok" if gain(state, args[0]) else "fail")
        else:
            print("未知命令")


if __name__ == "__main__":
    main()
