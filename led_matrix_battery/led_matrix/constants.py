"""
Constants for the input module.
"""

from cv2 import COLOR_BGR2GRAY, COLOR_RGB2GRAY
from led_matrix_battery.inputmodule.helpers import DEVICES

# Serial configuration
DEFAULT_BAUDRATE = 115_200
RESPONSE_SIZE    = 32

# Disconnected device placeholder
DISCONNECTED_DEVS = []

# Hardware identifiers
FWK_MAGIC = [0x32, 0xAC]
PID       = 0x20
SN_PREFIX = 'FRAK'
VID       = 0x32AC

# Grayscale conversion constants
GRAYSCALE_CVT = {
    'camera': COLOR_BGR2GRAY,
    'video': COLOR_RGB2GRAY,
}

# Matrix dimensions
HEIGHT = 34
WIDTH  = 9

# Project URLs
PROJECT_URLS = {
    'github_api': 'https://api.github.com/repos/Inspyre-Softworks/led-matrix-battery/contents/presets?ref=master'
}

# Physical slot mapping
SLOT_MAP = {
    '1-3.2': {'abbrev': 'R1', 'side': 'right', 'slot': 1},
    '1-3.3': {'abbrev': 'R2', 'side': 'right', 'slot': 2},
    '1-4.2': {'abbrev': 'L1', 'side': 'left',  'slot': 1},
    '1-4.3': {'abbrev': 'L2', 'side': 'left',  'slot': 2},
}

# Cleanup
del COLOR_BGR2GRAY, COLOR_RGB2GRAY

__all__ = [
    'DEFAULT_BAUDRATE',
    'DEVICES',
    'DISCONNECTED_DEVS',
    'FWK_MAGIC',
    'GRAYSCALE_CVT',
    'HEIGHT',
    'PID',
    'PROJECT_URLS',
    'RESPONSE_SIZE',
    'SN_PREFIX',
    'SLOT_MAP',
    'VID',
    'WIDTH',
]
