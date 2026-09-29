"""牧场核心逻辑：牲畜、草场、饲料和兽医。"""

import json


def new_game():
    return {
        "livestock": {},
        "pasture_capacity": 2,
        "feed": 100,
        "day": 1,
        "stock_id": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state["stock_id"] += 1
    return state


def register(state, animal_id):
    state["livestock"][animal_id] = {"health": 100}
    return True


def graze(state, animal_id):
    return True


def feed_days(state, animal_id, end_day):
    return (end_day - state["day"]) - 1


def cancel_breed(state, animal_id):
    return True


def treat(state, animal_id, vet):
    return True


def disease(state):
    return True


def gain(state, animal_id):
    return True


def main():
    print("牧场 - 命令: register/graze/feed/breed/treat/disease/gain/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()
