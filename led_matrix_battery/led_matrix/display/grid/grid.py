"""


Author: 
    Inspyre Softworks

Project:
    led-matrix-battery

File: 
    led_matrix_battery/led_matrix/display/grid/grid.py
 

Description:
    

"""
from typing import List, Optional
from ...constants import WIDTH as MATRIX_WIDTH, HEIGHT as MATRIX_HEIGHT, PRESETS_DIR
from ...helpers import load_from_file
from .helpers import is_valid_grid


class Grid:
    def __init__(
            self,
            width: int = MATRIX_WIDTH,
            height: int = MATRIX_HEIGHT,
            fill_value: int = 0,
            init_grid: Optional[List[List[int]]] = None
    ):
        """
        Initialize a new Grid instance.

        Args:
            width: Width of the grid in pixels. Defaults to MATRIX_WIDTH.
            height: Height of the grid in pixels. Defaults to MATRIX_HEIGHT.
            fill_value: Value to fill empty cells with (0 or 1). Defaults to 0.
            init_grid: Initial grid data. If None, creates an empty grid.
        """
        # Initialize private attributes to None
        self.__fill_value = None
        self.__grid       = None
        self.__height     = None
        self.__width      = None

        # Set properties through setters to ensure validation
        self.fill_value = fill_value
        self.height = height
        self.width = width

        # Initialize the grid data
        if init_grid is not None:
            # Create a deep copy of the input grid to avoid modifying the original
            self.grid = [row.copy() for row in init_grid]
        else:
            # Create a blank grid if no initial grid is provided
            self.load_blank_grid

    def _process_grid_dimensions(self):
        """
        Calculate and set the dimensions of the grid based on the grid data.

        This method is called when a new grid is set to update the width and height
        properties based on the actual dimensions of the grid data.

        Raises:
            ValueError: If the grid is empty (None).
        """
        # Ensure the grid exists before trying to process its dimensions
        if self.__grid is None:
            raise ValueError('Grid is empty')

        # Width is the number of columns (outer list length)
        self.__width = len(self.__grid)

        # Height is the number of rows (length of first inner list)
        # If the grid has no columns, height is 0
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

        if new in {0, 1}:
            self.__fill_value = new
        else:
            raise ValueError("Fill value must be 0 or 1")

    @property
    def grid(self) -> list[list[int]]:
        if self.__grid is None:
            self.__grid = [[0] * self.height for _ in range(self.width)]

        return self.__grid

    @grid.setter
    def grid(self, value: list[list[int]]):
        if self.__grid is not None:
            raise RuntimeError('Grid is immutable')

        if not is_valid_grid(value, self.width, self.height):
            raise ValueError('Invalid grid data')

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
            return None if self.__grid is None else len(self.__grid)
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
        # TODO document why this method is empty
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
            if is_valid_grid(from_file, width, height):
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


    def load_blank_grid(self, width: int = None, height: int = None):
        width = width or self.width or MATRIX_WIDTH
        height = height or self.height or MATRIX_HEIGHT
        return load_from_file(PRE)
