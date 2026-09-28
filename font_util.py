from PyQt6.QtGui import QFont, QFontDatabase

import config

_CACHED = None
_CACHED_LABEL = None


def _pick(candidates, fallback):
    available = set(QFontDatabase.families())
    for name in candidates:
        if name in available:
            return name
    return fallback


def family():
    global _CACHED
    if _CACHED is None:
        _CACHED = _pick(config.FONT_CANDIDATES, config.FONT_FALLBACK)
    return _CACHED


def label_family():
    global _CACHED_LABEL
    if _CACHED_LABEL is None:
        _CACHED_LABEL = _pick(config.LABEL_FONT_CANDIDATES, config.LABEL_FONT_FALLBACK)
    return _CACHED_LABEL


def value_font(size=None):
    return QFont(family(), config.scaled(size or config.FONT_SIZE), QFont.Weight.Bold)


def unit_font(small=False):
    size = config.UNIT_FONT_SIZE_SMALL if small else config.UNIT_FONT_SIZE
    return QFont(family(), config.scaled(size), QFont.Weight.Bold)


def label_font():
    return QFont(label_family(), config.scaled(config.LABEL_FONT_SIZE), QFont.Weight.Bold)
