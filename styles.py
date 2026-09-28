import config

STYLES = {
    "dark": {
        "CARD_FILL_TOP": "#141416",
        "CARD_FILL_BOTTOM": "#141416",
        "CARD_BORDER_TOP": "#2E2E32",
        "CARD_BORDER_BOTTOM": "#2E2E32",
        "CARD_OUTLINE_WIDTH": 5,
        "CARD_SHADOW": "#70000000",
        "DIGIT_FILL": "#FFFFFF",
        "DIGIT_OUTLINE": "#000000",
        "DIGIT_OUTLINE_WIDTH": 9,
        "DIGIT_OUTLINE_WIDTH_SMALL": 6,
        "LABEL_COLOR": "#5A5A5E",
        "GLASS_HIGHLIGHT": "#00FFFFFF",
    },
    "glass": {
        "CARD_FILL_TOP": "#4DFFFFFF",
        "CARD_FILL_BOTTOM": "#14FFFFFF",
        "CARD_BORDER_TOP": "#C8FFFFFF",
        "CARD_BORDER_BOTTOM": "#33FFFFFF",
        "CARD_OUTLINE_WIDTH": 2,
        "CARD_SHADOW": "#66000000",
        "DIGIT_FILL": "#FFFFFF",
        "DIGIT_OUTLINE": "#66000000",
        "DIGIT_OUTLINE_WIDTH": 3,
        "DIGIT_OUTLINE_WIDTH_SMALL": 2,
        "LABEL_COLOR": "#D9FFFFFF",
        "GLASS_HIGHLIGHT": "#5AFFFFFF",
    },
}

NAMES = {"dark": "黑色", "glass": "半透明"}


def apply(name):
    data = STYLES.get(name, STYLES["dark"])
    for key, value in data.items():
        setattr(config, key, value)
    config.STYLE = name
    return name
