import json

history = []

try:
    with open("history.json", encoding="utf-8") as f:
        history = json.load(f)
except Exception:
    pass


def save_history():
    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
