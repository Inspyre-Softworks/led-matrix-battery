"""
Display module for LED Matrix.

This module provides functions for displaying various content on the LED matrix,
including patterns, text, and media.
"""

# Import and re-export all display-related functions
from .patterns import (
    pattern, light_leds, breathing, eq
)

from .text import show_string, show_font, show_symbols

