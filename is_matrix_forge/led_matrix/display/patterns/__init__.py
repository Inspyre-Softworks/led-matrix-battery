"""
Pattern display module for LED Matrix.

This module provides functions for displaying various patterns on the LED matrix.
It includes functions for displaying checkerboards, gradients, and other visual patterns.
"""

import time

from .built_in.stencils import every_nth_row, every_nth_col
from ..helpers import render_matrix
from is_matrix_forge.led_matrix.display.patterns.built_in.stencils import every_nth_row, every_nth_col
from is_matrix_forge.led_matrix.display.helpers.columns import send_col


def breathing(dev):
    """Animate breathing brightness.
    Keeps currently displayed grid"""
    set_status('breathing')
    # Bright ranges appear similar, so we have to go through those faster
    while get_status() == 'breathing':
        # Go quickly from 250 to 50
        for i in range(10):
            time.sleep(0.03)
            brightness(dev, 250 - i * 20)

        # Go slowly from 50 to 0
        for i in range(10):
            time.sleep(0.06)
            brightness(dev, 50 - i * 5)

        # Go slowly from 0 to 50
        for i in range(10):
            time.sleep(0.06)
            brightness(dev, i * 5)

        # Go quickly from 50 to 250
        for i in range(10):
            time.sleep(0.03)
            brightness(dev, 50 + i * 20)


def eq(dev, vals):
    """Display 9 values in equalizer diagram starting from the middle, going up and down"""
    matrix = [[0 for _ in range(34)] for _ in range(9)]

    for col, val in enumerate(vals[:9]):
        row = int(34 / 2)
        above = int(val / 2)
        below = val - above

        for i in range(above):
            matrix[col][row + i] = 0xFF
        for i in range(below):
            matrix[col][row - 1 - i] = 0xFF

    render_matrix(dev, matrix)


