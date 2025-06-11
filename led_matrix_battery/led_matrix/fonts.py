from pathlib import Path
from typing import List

from led_matrix_battery.assets.font_map import FontMap
import json

# Load the default font map shipped with the package
_DEFAULT_FONT_MAP_PATH = Path(__file__).resolve().parents[1] / "assets" / "char_map.json"
with open(_DEFAULT_FONT_MAP_PATH, "r", encoding="utf-8") as f:
    _FONT_DATA = json.load(f)
FONT_MAP = FontMap(font_map=_FONT_DATA)


def convert_font(ch: str) -> List[int]:
    """Return the 5x6 glyph list for a single character."""
    return FONT_MAP.lookup(ch, kind="character")


def convert_symbol(symbol: str) -> List[int]:
    """Return the glyph list for a named symbol."""
    return FONT_MAP.lookup(symbol, kind="symbol")
