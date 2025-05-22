"""
Display module for LED Matrix.

This module provides functions for displaying various content on the LED matrix,
including patterns, text, and media.
"""

# Import and re-export all display-related functions
from .patterns import (
    pattern, render_matrix, light_leds, checkerboard, every_nth_col,
    every_nth_row, all_brightnesses, breathing, eq, send_col, commit_cols
)
from .text import show_string, show_font, show_symbols
from .media import image, image_greyscale, camera, video, pixel_to_brightness
