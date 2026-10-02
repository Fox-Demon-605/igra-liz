CELL_SIZE = 48
MAP_COLS = 64
MAP_ROWS = 44
SEED = 17

VIEW_WIDTH = 860
VIEW_HEIGHT = 620

COLORS = {
    "background": "#10151D",
    "panel": "#19212C",
    "panel_light": "#202B38",
    "border": "#344355",
    "text": "#E9E4D8",
    "muted": "#A4ADBA",
    "gold": "#E8BE73",
    "gold_dark": "#8C683A",
    "player": "#FFE8A0",
}

TERRAIN = {
    "deep_water": {
        "name": "Глубокое море",
        "base": "#16354D",
        "detail": "#28506A",
        "symbol": "≈",
    },
    "water": {
        "name": "Море",
        "base": "#255878",
        "detail": "#417B97",
        "symbol": "≈",
    },
    "coast": {
        "name": "Побережье",
        "base": "#BCA877",
        "detail": "#D8C694",
        "symbol": "·",
    },
    "plain": {
        "name": "Равнина",
        "base": "#71845A",
        "detail": "#97A76E",
        "symbol": "·",
    },
    "forest": {
        "name": "Лес",
        "base": "#345F4F",
        "detail": "#6A9B72",
        "symbol": "♠",
    },
    "deep_forest": {
        "name": "Чаща",
        "base": "#254C40",
        "detail": "#4E8060",
        "symbol": "♠",
    },
    "hills": {
        "name": "Холмы",
        "base": "#8D8463",
        "detail": "#B5A477",
        "symbol": "⌃",
    },
    "mountain": {
        "name": "Горы",
        "base": "#777B7C",
        "detail": "#BCC1BC",
        "symbol": "▲",
    },
    "snow": {
        "name": "Снежные вершины",
        "base": "#A8B8BA",
        "detail": "#F0F0E5",
        "symbol": "▲",
    },
    "marsh": {
        "name": "Болото",
        "base": "#536C56",
        "detail": "#94A47A",
        "symbol": "≋",
    },
    "city": {
        "name": "Город",
        "base": "#8C665B",
        "detail": "#EAC68E",
        "symbol": "◆",
    },
    "village": {
        "name": "Деревня",
        "base": "#8F7959",
        "detail": "#E8C996",
        "symbol": "◇",
    },
}

WATER_TYPES = {"deep_water", "water"}
MOUNTAIN_TYPES = {"mountain", "snow"}