"""
LED Matrix Module.

This module provides a high-level interface for interacting with LED matrix devices.
It combines functionality from various modules to provide a simple API for controlling
LED matrices, displaying patterns, animations, and battery status.
"""

from __future__ import annotations

# Standard library
from pathlib import Path
from typing import Optional, Union, List

# Third-party
from serial.tools.list_ports_common import ListPortInfo

# Inspyre-Softworks
from led_matrix_battery.led_matrix import LEDMatrixController
from led_matrix_battery.led_matrix.display.grid import Grid, generate_blank_grid
from led_matrix_battery.led_matrix.display.animations import goodbye_animation
from led_matrix_battery.led_matrix.helpers.device import get_devices
from led_matrix_battery.common.helpers import percentage_to_value


class LEDMatrix:
    """
    High-level interface for LED Matrix devices.

    This class provides a simplified interface for interacting with LED matrix
    hardware devices. It wraps the LEDMatrixController and provides methods for
    common operations like displaying battery status, patterns, and animations.

    Attributes:
        controller (LEDMatrixController): The controller for the LED matrix device.
        default_brightness (int): The default brightness level (0-100).
    """

    def __init__(self, device: ListPortInfo, default_brightness: int = 50):
        """
        Initialize a new LED Matrix.

        Args:
            device (ListPortInfo): The LED matrix device to control.
            default_brightness (int, optional): Default brightness level (0-100).
                Defaults to 50.
        """
        # Create a controller for the device
        self.controller = LEDMatrixController(device, default_brightness)
        self.default_brightness = default_brightness

        # Set the initial brightness
        self.set_brightness(default_brightness)

    def display_battery_level(self, percentage: int) -> None:
        """
        Display the battery level on the LED matrix.

        Args:
            percentage (int): Battery level percentage (0-100).
        """
        # First, stop any ongoing animation
        self.controller.halt_animation()

        # Use the controller to display the percentage
        # This will call the low-level percentage function
        self.controller.draw_pattern(f"Percentage {percentage}")

    def display_pattern(self, pattern_name: str) -> None:
        """
        Display a predefined pattern on the LED matrix.

        Args:
            pattern_name (str): Name of the pattern to display.
                See the PATTERNS list in ledmatrix.py for available patterns.
        """
        # First, stop any ongoing animation
        self.controller.halt_animation()

        # Use the controller to display the pattern
        self.controller.draw_pattern(pattern_name)

    def start_animation(self) -> None:
        """
        Start animation on the LED matrix.

        This will animate the currently displayed content.
        """
        self.controller.animate(True)

    def stop_animation(self) -> None:
        """
        Stop any ongoing animation on the LED matrix.
        """
        self.controller.halt_animation()

    def clear(self) -> None:
        """
        Clear the LED matrix display.
        """
        self.controller.clear()

    def set_brightness(self, brightness: int) -> None:
        """
        Set the brightness level of the LED matrix.

        Args:
            brightness (int): Brightness level as a percentage (0-100).
        """
        self.controller.set_brightness(brightness)

    def identify(self) -> None:
        """
        Display identification information on the LED matrix.

        This helps identify which LED matrix is which when multiple are connected.
        """
        self.controller.identify()

    def goodbye(self) -> None:
        """
        Display a goodbye animation on the LED matrix.

        This is typically used when shutting down the application.
        """
        # First, stop any ongoing animation
        self.controller.halt_animation()

        # Display the goodbye animation
        goodbye_animation(self.controller.device)

    @staticmethod
    def get_available_devices() -> List[ListPortInfo]:
        """
        Get a list of available LED matrix devices.

        Returns:
            List[ListPortInfo]: List of available devices.
        """
        return get_devices()

    def __repr__(self) -> str:
        """
        Return a string representation of the LEDMatrix.

        Returns:
            str: A string representation including the controller and brightness.
        """
        return f"<LEDMatrix controller={self.controller!r} brightness={self.default_brightness}%>"
