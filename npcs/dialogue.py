import json
import random
from pathlib import Path


ALFRED_DIALOGUE_PATH = Path(__file__).resolve().parent.parent / "content" / "alfred_dialogue.json"


def load_alfred_dialogue() -> dict[str, list[str]]:
    if not ALFRED_DIALOGUE_PATH.exists():
        return {}

    try:
        raw_text = ALFRED_DIALOGUE_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        return {}

    if not raw_text:
        return {}

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return {}

    if not isinstance(data, dict):
        return {}

    dialogue: dict[str, list[str]] = {}
    for event_name, lines in data.items():
        if isinstance(event_name, str) and isinstance(lines, list):
            dialogue[event_name] = [line for line in lines if isinstance(line, str)]

    return dialogue


def get_alfred_dialogue_line(event_key: str) -> str | None:
    lines = load_alfred_dialogue().get(event_key, [])
    return random.choice(lines) if lines else None
