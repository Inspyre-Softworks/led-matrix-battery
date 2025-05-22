from .constants import *
from .controller import LEDMatrixController
from .hardware import (
    CommandVals, PatternVals, Game, GameControlVal, GameOfLifeStartParam,
    animate, get_animate, brightness, get_brightness, get_pwm_freq, pwm_freq,
    percentage, send_command, send_serial, disconnect_dev, bootloader_jump,
    get_version
)
from .display import (
    pattern, render_matrix, light_leds, checkerboard, every_nth_col,
    every_nth_row, all_brightnesses, breathing, eq, send_col, commit_cols,
    show_string, show_font, show_symbols,
    image, image_greyscale, camera, video, pixel_to_brightness
)


def get_controllers():
    return [LEDMatrixController(device, 100) for device in DEVICES]
