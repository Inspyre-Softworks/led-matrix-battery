from __future__ import annotations

import threading
from typing import Any, List

from inspyre_toolbox.chrono import sleep as ist_sleep
from serial.tools.list_ports_common import ListPortInfo

from led_matrix_battery.led_matrix.helpers.device import get_devices
from led_matrix_battery.led_matrix.constants import HEIGHT, WIDTH
from led_matrix_battery.inputmodule.ledmatrix import render_matrix
from led_matrix_battery.led_matrix.errors import MalformedGridError


def load_blank_grid(width: int = WIDTH, height: int = HEIGHT) -> Grid:
    pass



def is_valid_grid(grid: Any, width: int, height: int) -> bool:
    """
    Check if a grid is valid.

    A grid is valid if it is a list of lists of 0s and 1s, and the length of each list is equal to the width and height.

    Parameters:
        grid (Any):
            The grid to check.

        width (int):
            The expected width (in pixels) of the grid.

        height (int):
            The expected height (in pixels) of the grid.

    Returns:
        bool:
            True if the grid is valid, False otherwise.
    """
    return (
        isinstance(grid, list)
        and len(grid) == width
        and all(
            isinstance(col, list)
            and len(col) == height
            and all(cell in (0, 1) for cell in col)
            for col in grid
        )
    )


def hold_pattern(dev, grid: List[List[int]], reapply_interval: float = 55.00) -> None:
    """
    Hold the state of the LED matrix indefinitely, only updating the display every `reapply_interval` seconds.

    This is useful for maintaining a static display on the LED matrix without having a constant refresh/computation
    load.

    Parameters:
        dev (ListPortInfo):
            The serial com device/port to use.

        grid (List[List[int]])::
            The grid to display on the LED matrix.

        reapply_interval (Union[float, int]):
            The interval in seconds at which to reapply the grid state to the LED matrix. Default is 55 seconds,
            maximum is 60 (the number of seconds before the matrix turns all the LEDs off unless a new state is
            applied)

    Returns:
        None
    """
    if not isinstance(dev, ListPortInfo):
        raise TypeError(f"dev must be a ListPortInfo object, not {type(dev)}")

    if not isinstance(grid, list) or not is_valid_grid(grid, 9, 34):
        raise MalformedGridError(f"grid must be a 9x34 list of 0/1, not {type(grid)}")

    def worker(interval):
        global running
        running.state = True
        while running:
            ist_sleep(interval)
            render_matrix(dev, grid)

    thread = threading.Thread(target=worker, args=(reapply_interval,), daemon=True)
    thread.start()
