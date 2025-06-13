from .constants import *
from .hardware import (
    CommandVals, PatternVals, Game, GameControlVal, GameOfLifeStartParam,
    animate, get_animate, brightness, get_brightness, get_pwm_freq, pwm_freq,
    percentage, send_command, send_serial, disconnect_dev, bootloader_jump,
    get_version
)
#from .display import (
#    pattern, render_matrix, light_leds, breathing, eq, show_string, show_font, show_symbols,
#    image, image_greyscale, camera, video, pixel_to_brightness
#)
#from .display.patterns import every_nth_col, every_nth_row, all_brightnesses
#from . import checkerboard, commit_cols, send_col
from .controller.controller import LEDMatrixController


def get_controllers():
    return [LEDMatrixController(device, 100) for device in DEVICES]
