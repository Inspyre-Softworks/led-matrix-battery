from .constants import *
from .controller import LEDMatrixController





def get_controllers():
    return [LEDMatrixController(device, 100) for device in DEVICES]

