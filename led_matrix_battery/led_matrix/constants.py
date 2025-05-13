"""
Constants for the input module.
"""
from cv2 import COLOR_BGR2GRAY, COLOR_RGB2GRAY
from led_matrix_battery.inputmodule.helpers import DEVICES


# Hardware identifiers
FWK_MAGIC = [
    0x32,
    0xAC
]
VID       = 0x32AC
PID       = 0x20
SN_PREFIX = 'FRAK'

SLOT_MAP = {
    '1-3.2': {
        'side': 'right',
        'slot': 1,
        'abbrev': 'R1'
    },
    '1-3.3': {
        'side': 'right',
        'slot': 2,
        'abbrev': 'R2'
    },
    '1-4.2':{
        'side': 'left',
        'slot': 1,
        'abbrev': 'L1'
    },
    '1-4.3':{
        'side': 'left',
        'slot': 2,
        'abbrev': 'L2'
    },
}

# Matrix dimensions
WIDTH  = 9
HEIGHT = 34

DEFAULT_BAUDRATE = 115_200
RESPONSE_SIZE    = 32
GRAYSCALE_CVT = {
    'camera': COLOR_BGR2GRAY,
    'video': COLOR_RGB2GRAY,
}

DISCONNECTED_DEVS = []

del COLOR_BGR2GRAY, COLOR_RGB2GRAY


__all__ = [
    'DEFAULT_BAUDRATE',
    'GRAYSCALE_CVT',
    'HEIGHT',
    'VID',
    'PID',
    'SN_PREFIX',
    'WIDTH'
]

