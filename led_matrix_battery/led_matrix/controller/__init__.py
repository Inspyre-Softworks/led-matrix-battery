from __future__ import annotations

# Standard library
from pathlib import Path
from typing import Optional, Union

# Third‑party
from serial.tools.list_ports_common import ListPortInfo

# Inspyre‑Softworks
from inspyre_toolbox.syntactic_sweets.classes.decorators.type_validation import validate_type
from inspyre_toolbox.syntactic_sweets.classes.decorators.aliases import add_aliases, method_alias
from led_matrix_battery.common.helpers import percentage_to_value
from led_matrix_battery.log_engine import ROOT_LOGGER as PARENT_LOGGER, Loggable
from led_matrix_battery.inputmodule.ledmatrix import (
    animate,
    brightness as _set_brightness_raw,
    get_animate,
    pattern as _set_pattern_raw,
    percentage as _show_percentage_raw,
    show_string as _show_string_raw,
    render_matrix
)
from led_matrix_battery.led_matrix.constants import SLOT_MAP
from led_matrix_battery.led_matrix.errors import InvalidBrightnessError
from led_matrix_battery.led_matrix.display.grid import generate_blank_grid
from led_matrix_battery.led_matrix.display.grid import Grid


@add_aliases
class LEDMatrixController:
    def __init__(self, device, default_brightness):
        self.__default_brightness = self.__normalize_percent(default_brightness)
        self.__device = None

        self.device = device

    @property
    def animating(self):
        return animate(self.device)

    @property
    def device(self):
        return self.__device

    @validate_type(ListPortInfo)
    @device.setter
    def device(self, device: ListPortInfo):
        if not device:
            raise ValueError('Device cannot be None or empty.')

        self.__device = device

    def animate(self, enable=True):
        pass

    def draw_grid(self, grid: 'Grid'):
        render_matrix(self.device, grid.grid)

    @method_alias('pattern')
    def draw_pattern(self, pattern: str) -> None:
        _set_pattern_raw(self.device, pattern)

    @property
    def location(self):
        return SLOT_MAP.get(self.device.location)

    @property
    def location_abbrev(self):
        return self.location['abbrev']

    @property
    def side_of_keyboard(self):
        return self.location['side']

    @property
    def slot(self):
        return self.location['slot']

    def clear(self):
        data = generate_blank_grid()
        grid = Grid(init_grid=data)
        self.draw_grid(grid)

    def halt_animation(self):
        pass

    def identify(
            self,
            skip_clear: bool = False
    ):
        from time import sleep
        acc = 0
        while acc < 3:

            _show_string_raw(self.device, self.location_abbrev)
            sleep(3)
            _show_string_raw(self.device, self.device.name)
            sleep(3)
            acc += 1

        #if not skip_clear:
        #    self.clear()


    def set_brightness(self, brightness: Union[int, float]) -> None:
        brightness_value = percentage_to_value(brightness)
        try:
            _set_brightness_raw(self.device, brightness_value)
        except ValueError as e:
            raise InvalidBrightnessError(brightness_value) from e
        

    @staticmethod
    # Internal methods
    def __normalize_percent(val: Union[int, float, str]) -> int:
        if isinstance(val, str):
            val = float(val.strip("%"))

        percent = int(round(float(val)))

        if not (0 <= percent <= 100):
            raise ValueError("Percentage must be between 0 and 100")

        return percent

    def __repr__(self) -> str:
        return f"<LEDMatrixController device={self.device!r}(location={self.location!r}) " \
        f"brightness={self.__default_brightness}%>"