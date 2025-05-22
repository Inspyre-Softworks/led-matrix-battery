"""
LED Matrix Controller Module.

This module provides the main controller class for interacting with LED matrix devices.
It handles device communication, animation control, pattern display, and other
operations related to the LED matrix hardware.
"""

from __future__ import annotations

# Standard library
from pathlib import Path
from typing import Optional, Union, Dict, Any

# Third‑party
from serial.tools.list_ports_common import ListPortInfo

# Inspyre‑Softworks
from inspyre_toolbox.syntactic_sweets.classes.decorators.type_validation import \
    validate_type  # For type validation in method parameters
from inspyre_toolbox.syntactic_sweets.classes.decorators.aliases import add_aliases, \
    method_alias  # For adding method aliases
from led_matrix_battery.common.helpers import percentage_to_value  # Converts percentage values to raw hardware values
from led_matrix_battery.log_engine import ROOT_LOGGER as PARENT_LOGGER, Loggable  # Logging functionality
from led_matrix_battery.led_matrix import (
    animate,  # Check if animation is enabled
    brightness as _set_brightness_raw,  # Low-level brightness control
    get_animate,  # Get animation status
    pattern as _set_pattern_raw,  # Low-level pattern display
    percentage as _show_percentage_raw,  # Low-level percentage display
    show_string as _show_string_raw,  # Low-level string display
    render_matrix  # Render a grid on the matrix
)
from led_matrix_battery.led_matrix.constants import SLOT_MAP, HEIGHT, WIDTH
from led_matrix_battery.led_matrix.errors import InvalidBrightnessError  # Error for invalid brightness values

from led_matrix_battery.led_matrix.display.grid.grid import Grid


def generate_blank_grid(width: Optional[int] = None, height: Optional[int] = None) -> Grid:
    return Grid.load_blank_grid()


@add_aliases
class LEDMatrixController:
    """
    Controller class for LED Matrix devices.

    This class provides a high-level interface for interacting with LED matrix
    hardware devices. It handles device communication, animation control,
    pattern display, and other operations.

    Attributes:
        device (ListPortInfo): The connected LED matrix device.
        animating (bool): Whether the device is currently animating.
        location (dict): Physical location information for the device.
        location_abbrev (str): Abbreviated location identifier.
        side_of_keyboard (str): Which side of the keyboard the device is on.
        slot (int): The slot number of the device.
    """

    def __init__(self, device, default_brightness, skip_init_brightness_set: bool = False, skip_init_clear: bool = False, init_grid: Optional[Grid] = None):
        """
        Initialize a new LED Matrix Controller.

        Args:
            device (ListPortInfo): The LED matrix device to control.
            default_brightness (Union[int, float, str]): Default brightness level (0-100).
        """
        self.__default_brightness = self.__normalize_percent(default_brightness)
        self.__device = None
        self.__grid   = None

        self.device = device
        if not skip_init_clear:
            self.clear()

        if not skip_init_brightness_set:
            self.set_brightness(self.__default_brightness)

    @property
    def animating(self) -> bool:
        """
        Check if the device is currently animating.

        Returns:
            bool: True if the device is animating, False otherwise.
        """
        return animate(self.device)

    @property
    def brightness(self):
        return self.__brightness or self.__default_brightness

    @brightness.setter
    def brightness(self, new):
        self.set_brightness(new, True)
        self.__brightness = new

    @property
    def device(self) -> ListPortInfo:
        """
        Get the current LED matrix device.

        Returns:
            ListPortInfo: The current device.
        """
        return self.__device

    @validate_type(ListPortInfo)
    @device.setter
    def device(self, device: ListPortInfo):
        """
        Set the LED matrix device.

        Args:
            device (ListPortInfo): The device to control.

        Raises:
            ValueError: If device is None or empty.
        """
        if not device:
            raise ValueError('Device cannot be None or empty.')

        self.__device = device

    def animate(self, enable: bool = True) -> None:
        """
        Control animation on the LED matrix.

        Args:
            enable (bool, optional): Whether to enable or disable animation. Defaults to True.
        """
        # Call the low-level animate function to control animation on the device
        # The animate function also sets the status to 'animate' when enabled
        animate(self.device, enable)

    def draw_grid(self, grid: 'Grid') -> None:
        """
        Draw a grid on the LED matrix.

        Args:
            grid (Grid): The grid to display on the LED matrix.
        """
        render_matrix(self.device, grid.grid)

    @method_alias('pattern')
    def draw_pattern(self, pattern: str) -> None:
        """
        Draw a pattern on the LED matrix.

        Args:
            pattern (str): The pattern string to display.

        Note:
            This method is aliased as 'pattern'.
        """
        _set_pattern_raw(self.device, pattern)

    @property
    def location(self) -> Dict[str, Any]:
        """
        Get the physical location information for the device.

        Returns:
            Dict[str, Any]: A dictionary containing location information such as
                           abbreviation, side, and slot.
        """
        return SLOT_MAP.get(self.device.location)

    @property
    def location_abbrev(self) -> str:
        """
        Get the abbreviated location identifier for the device.

        Returns:
            str: The abbreviated location identifier (e.g., 'R1', 'L2').
        """
        return self.location['abbrev']

    @property
    def side_of_keyboard(self) -> str:
        """
        Get which side of the keyboard the device is on.

        Returns:
            str: The side of the keyboard ('left' or 'right').
        """
        return self.location['side']

    @property
    def slot(self) -> int:
        """
        Get the slot number of the device.

        Returns:
            int: The slot number (1 or 2).
        """
        return self.location['slot']

    def clear(self) -> None:
        """
        Clear the LED matrix display.

        Generates a blank grid and displays it on the LED matrix.
        """
        data = generate_blank_grid()
        grid = Grid(init_grid=data)
        self.draw_grid(grid)

    def halt_animation(self) -> None:
        """
        Stop any ongoing animation on the LED matrix.

        This method checks if animation is currently running and stops it if needed.
        """
        # Check if animation is currently running
        if self.animating:
            # Call animate with False to stop the animation
            self.animate(False)

    def identify(
            self,
            skip_clear: bool = False
    ) -> None:
        """
        Display identification information on the LED matrix.

        Shows the location abbreviation and device name in sequence,
        repeating three times to help identify the specific LED matrix.

        Args:
            skip_clear (bool, optional): If True, doesn't clear the display
                                         after identification. Defaults to False.
        """
        if not skip_clear:
            self.clear()
        from time import sleep
        acc = 0
        while acc < 3:
            _show_string_raw(self.device, self.location_abbrev)
            sleep(3)
            _show_string_raw(self.device, self.device.name)
            sleep(3)
            acc += 1

        if not skip_clear:
            self.clear()

    def set_brightness(self, brightness: Union[int, float], __from_setter=False) -> None:
        """
        Set the brightness level of the LED matrix.

        Args:
            brightness (Union[int, float]): Brightness level as a percentage (0-100).

        Raises:
            InvalidBrightnessError: If the brightness value is invalid.
        """
        # Convert the percentage (0-100) to a hardware-specific value
        # The hardware expects a different range than the user-friendly percentage
        brightness_value = percentage_to_value(max_value=255, percent=brightness)

        try:
            # Call the low-level function to set the brightness on the device
            _set_brightness_raw(self.device, brightness_value)
        except ValueError as e:
            # If the low-level function raises a ValueError, wrap it in our custom
            # InvalidBrightnessError to provide more context about the error
            raise InvalidBrightnessError(brightness_value) from e

        if not __from_setter:
            self.__brightness = brightness

    @staticmethod
    # Internal methods
    def __normalize_percent(val: Union[int, float, str]) -> int:
        """
        Normalize a percentage value to an integer between 0 and 100.

        Args:
            val (Union[int, float, str]): The value to normalize. Can be an integer,
                                          float, or string (with or without '%').

        Returns:
            int: Normalized percentage value as an integer between 0 and 100.

        Raises:
            ValueError: If the percentage is not between 0 and 100.
        """
        # Handle string input (e.g., "75%") by stripping the '%' character and converting to float
        if isinstance(val, str):
            val = float(val.strip("%"))

        # Convert to float first to handle any decimal values, then round and convert to int
        # This ensures consistent handling of values like 75.6 (becomes 76)
        percent = int(round(float(val)))

        # Validate that the percentage is within the valid range (0-100)
        if not (0 <= percent <= 100):
            raise ValueError("Percentage must be between 0 and 100")

        return percent

    def __repr__(self) -> str:
        """
        Return a string representation of the LEDMatrixController.

        Returns:
            str: A string representation including device, location, and brightness.
        """
        return f"<LEDMatrixController device={self.device!r}(location={self.location!r}) " \
               f"brightness={self.__default_brightness}%>"
