import json
import os
import sys

from PyQt6.QtCore import Qt

import config

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE = os.path.join(BASE_DIR, "settings.json")

MIN_SCALE = 50
MAX_SCALE = 200


def default_data():
    return {
        "start": int(getattr(Qt.Key, "Key_" + config.DEFAULT_KEYS["start"])),
        "pause": int(getattr(Qt.Key, "Key_" + config.DEFAULT_KEYS["pause"])),
        "reset": int(getattr(Qt.Key, "Key_" + config.DEFAULT_KEYS["reset"])),
        "show_ms": config.DEFAULT_SHOW_MS,
        "scale": config.DEFAULT_SCALE,
        "style": config.DEFAULT_STYLE,
        "layout": config.DEFAULT_LAYOUT,
        "image": config.DEFAULT_IMAGE,
    }

VALID_STYLES = ("dark", "glass")
VALID_LAYOUTS = ("blocks", "bar")


def clamp_scale(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return config.DEFAULT_SCALE
    return max(MIN_SCALE, min(MAX_SCALE, number))


def load():
    data = default_data()
    try:
        with open(FILE, encoding="utf-8") as handle:
            saved = json.load(handle)
        if isinstance(saved, dict):
            for key in data:
                if key in saved:
                    data[key] = saved[key]
    except (OSError, ValueError):
        pass
    data["scale"] = clamp_scale(data["scale"])
    if data["style"] not in VALID_STYLES:
        data["style"] = config.DEFAULT_STYLE
    if data["layout"] not in VALID_LAYOUTS:
        data["layout"] = config.DEFAULT_LAYOUT
    if not isinstance(data["image"], str):
        data["image"] = config.DEFAULT_IMAGE
    return data


def save(data):
    try:
        with open(FILE, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
    except OSError:
        pass
