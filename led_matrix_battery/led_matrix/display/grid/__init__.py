from typing import List, Optional
from led_matrix_battery.led_matrix.constants import (
    WIDTH as MATRIX_WIDTH,
    HEIGHT as MATRIX_HEIGHT,
    DEVICES
)
from led_matrix_battery.led_matrix.helpers import load_from_file
from platformdirs import PlatformDirs


APP_DIRS = PlatformDirs('LEDMatrixLib', appauthor='Inspyre Softworks')







class Grid:
    def __init__(
            self,
            width: int = MATRIX_WIDTH,
            height: int = MATRIX_HEIGHT,
            fill_value: int = 0,
            init_grid: Optional[List[List[int]]] = None
    ):
        self.__fill_value = None
        self.__grid       = None
        self.__height     = None
        self.__width      = None

        self.fill_value = fill_value
        self.height = height
        self.width = width

        if init_grid is not None:
            self.grid = [row.copy() for row in init_grid]
        else:
            self.grid = [
                [self.fill_value for _ in range(self.width)]
                for _ in range(self.height)
            ]


    def _process_grid_dimensions(self):
        if self.__grid is None:
            raise ValueError('Grid is empty')

        self.__width = len(self.__grid)
        self.__height = len(self.__grid[0] if self.width > 0 else 0)

    @property
    def cols(self) -> int:
        return self.width

    @property
    def fill_value(self) -> int:
        return self.__fill_value

    @fill_value.setter
    def fill_value(self, new: int):
        if not isinstance(new, int):
            raise TypeError("Fill value must be an integer")

        if new not in [0, 1]:
            raise ValueError("Fill value must be 0 or 1")

        self.__fill_value = new

    @property
    def grid(self) -> list[list[int]]:
        if self.__grid is None:
            self.__grid = [[0] * self.height for _ in range(self.width)]

        return self.__grid

    @grid.setter
    def grid(self, value: list[list[int]]):
        if self.__grid is not None:
            raise RuntimeError('Grid is immutable')

        self.__grid = value
        self._process_grid_dimensions()

    @property
    def height(self) -> int:
        """
        How tall (in pixels/led rows) is the grid.

        Returns:
            int:
                The number of rows in the grid
        """
        if self.__height is None:
            if self.__grid is None:
                return None
            else:
                return len(self.__grid)
        else:
            return self.__height

    @height.setter
    def height(self, new):
        if self.__grid:
            raise RuntimeError('Grid is immutable')

        self.__height = new

    @property
    def rows(self) -> int:
        return self.height

    @property
    def width(self) -> int:
        return self.__width

    @width.setter
    def width(self, new):
        if self.__grid:
            raise RuntimeError('Grid is immutable')

        self.__width = new

    @classmethod
    def from_spec(cls, spec: list[list[int]]):
        pass

    @classmethod
    def from_file(cls, filename: str, frame_number: int = 0, height: int = MATRIX_HEIGHT, width: int = MATRIX_WIDTH):
        """
        Loads a grid from a file.

        Args:
            filename (str):
                The file to load from.

            frame_number (int, optional):
                The frame number to load. Defaults to 0.

            height (int, optional):
                The height of the grid. Defaults to MATRIX_HEIGHT.

            width (int, optional):
                The width of the grid. Defaults to MATRIX_WIDTH.

        Returns:
            Grid:
                The loaded grid.
        """
        from led_matrix_battery.led_matrix.display.grid.helpers import is_valid_grid
        from_file = load_from_file(filename, width, height)
        if isinstance(from_file[0], list):
            if is_valid_grid(from_file):
                return Grid(width, height, 0, from_file)
            else:
                raise ValueError('Invalid grid file')
        elif isinstance(from_file[frame_number], dict):
            return Grid(width, height, 0, from_file[frame_number]['grid'])
        return None

    def draw(self, device):
        device.draw_grid(self)

    def get_pixel_value(self, x: int, y: int):
        """
        Gets the value of a pixel at the specified coordinates.

        Args:
            x (int):
                The x-coordinate of the pixel (left to right).

            y (int):
                The y-coordinate of the pixel (top to bottom).

        Returns:
            int:
                The value of the pixel at the specified coordinates.
        """
        return self.grid[y][x]

    def get_shifted_down(self, n: int = 1, wrap: bool = False):
        new_data = generate_blank_grid(self.width, self.height, self.fill_value)

        for row in range(self.height):
            src_row = row - n
            for col in range(self.width):
                if wrap:
                    new_data[row][col] = self.grid[src_row % self.height][col]
                else:
                    if 0 <= src_row < self.height:
                        new_data[row][col] = self.get_pixel_value(col, row)

        return Grid(self.width, self.height, self.fill_value, new_data)
