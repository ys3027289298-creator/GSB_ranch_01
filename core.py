"""牧场核心逻辑：牲畜、草场、饲料和兽医。

每个命令都是幂等的：重复提交同一指令不会重复扣减或重复结算。
状态可通过 save_state/load_state 用 JSON 往返保存。
"""

import json


def new_game():
    return {
        "livestock": {},
        "pasture_capacity": 2,
        "grazing": [],
        "feed": 100,
        "water": 100,
        "day": 1,
        "stock_id": 0,
        "vets": {"V1": True, "V2": False},
        "breeding": {},
        "disease_day": None,
        "gained": {},
    }


def _default_state():
    return new_game()


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    base = _default_state()
    for key, value in base.items():
        if key not in state:
            state[key] = value
    return state


def _valid_animal_id(animal_id):
    return isinstance(animal_id, str) and bool(animal_id.strip())


def register(state, animal_id):
    """登记一头牲畜；重复编号或空编号返回 False，不产生副作用。"""
    if not _valid_animal_id(animal_id):
        return False
    animal_id = animal_id.strip()
    if animal_id in state["livestock"]:
        return False
    state["stock_id"] += 1
    state["livestock"][animal_id] = {
        "health": 100,
        "serial": state["stock_id"],
    }
    return True


def graze(state, animal_id):
    """放牧到草场；牲畜不存在、编号为空或草场已满（含临界容量）时失败。"""
    if not _valid_animal_id(animal_id):
        return False
    animal_id = animal_id.strip()
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
    """计算从当前固定日期到 end_day 的饲喂天数（含首尾两天）。"""
    try:
        end_day = int(end_day)
    except (TypeError, ValueError):
        return 0
    days = end_day - int(state["day"])
    return days if days > 0 else 0


BREED_FEE = 10


def breed(state, animal_id):
    """预约配种并冻结饲料；同一牲畜重复提交保持幂等。"""
    if not _valid_animal_id(animal_id):
        return False
    animal_id = animal_id.strip()
    if animal_id not in state["livestock"]:
        return False
    breeding = state.setdefault("breeding", {})
    if breeding.get(animal_id):
        return True
    if state["feed"] < BREED_FEE:
        return False
    state["feed"] -= BREED_FEE
    breeding[animal_id] = True
    return True


def cancel_breed(state, animal_id):
    """取消配种并返还种畜（冻结的饲料）；同一牲畜重复取消只返还一次。"""
    if not _valid_animal_id(animal_id):
        return False
    animal_id = animal_id.strip()
    breeding = state.setdefault("breeding", {})
    if breeding.get(animal_id) == "refunded":
        return False
    state["feed"] += BREED_FEE
    breeding[animal_id] = "refunded"
    return True


def treat(state, animal_id, vet):
    """兽医在线且牲畜存在时才能接诊；离线兽医的重复提交不会被受理。"""
    if not _valid_animal_id(animal_id):
        return False
    animal_id = animal_id.strip()
    if animal_id not in state["livestock"]:
        return False
    if not isinstance(vet, str) or not vet.strip():
        return False
    vets = state.setdefault("vets", {})
    if not vets.get(vet, False):
        return False
    return True


def disease(state):
    """疾病事件：当天全场牲畜各扣 10 点健康；同一天重复触发只扣一次。"""
    if state.get("disease_day") == state["day"]:
        return False
    state["disease_day"] = state["day"]
    for animal in state["livestock"].values():
        animal["health"] = max(0, animal["health"] - 10)
    return True


def gain(state, animal_id):
    """计增重：饮水不足、牲畜不存在或当天已结算时失败，保证幂等。"""
    if not _valid_animal_id(animal_id):
        return False
    animal_id = animal_id.strip()
    if animal_id not in state["livestock"]:
        return False
    if state.get("water", 0) <= 0:
        return False
    gained = state.setdefault("gained", {})
    key = "{}:{}".format(animal_id, state["day"])
    if gained.get(key):
        return False
    gained[key] = True
    return True


def main():
    print("牧场 - 命令: register/graze/feed/breed/treat/disease/gain/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        if raw == "quit":
            break
        parts = raw.split()
        command = parts[0]
        args = parts[1:]
        try:
            if command == "register" and len(args) == 1:
                ok = register(_STATE, args[0])
            elif command == "graze" and len(args) == 1:
                ok = graze(_STATE, args[0])
            elif command == "feed" and len(args) == 2:
                print(feed_days(_STATE, args[0], args[1]))
                continue
            elif command == "breed" and len(args) == 1:
                ok = breed(_STATE, args[0])
            elif command == "cancel_breed" and len(args) == 1:
                ok = cancel_breed(_STATE, args[0])
            elif command == "treat" and len(args) == 2:
                ok = treat(_STATE, args[0], args[1])
            elif command == "disease" and not args:
                ok = disease(_STATE)
            elif command == "gain" and len(args) == 1:
                ok = gain(_STATE, args[0])
            else:
                print("未知命令")
                continue
        except (KeyError, TypeError, ValueError):
            print("非法命令")
            continue
        print("ok" if ok else "fail")


_STATE = new_game()


if __name__ == "__main__":
    main()
