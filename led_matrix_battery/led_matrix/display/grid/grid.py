# led_matrix_battery.led_matrix.display.grid.grid
"""
Grid module for LED Matrix display.

Author: 
    Inspyre Softworks

Project:
    led-matrix-battery

File: 
    led_matrix_battery/led_matrix/display/grid/grid.py

Description:
    This module provides the Grid class which represents a 2D grid of pixels
    for the LED matrix display. It handles grid creation, manipulation, and
    loading from files.
"""

import itertools
from pathlib import Path
from typing import List, Optional, Union, ClassVar, Type, Any, Dict  # Added Any, Dict
from ...constants import WIDTH as __WIDTH, HEIGHT as __HEIGHT, PRESETS_DIR
from ...helpers import load_from_file
from .helpers import is_valid_grid, generate_blank_grid
from led_matrix_battery.common.helpers import coerce_to_int

MATRIX_HEIGHT = __HEIGHT
"""int: Height of the LED matrix grid in pixels.
This constant defines the default height for new Grid instances and for loading operations.
"""

MATRIX_WIDTH = __WIDTH
"""int: Width of the LED matrix grid in pixels.
This constant defines the default width for new Grid instances and for loading operations.
"""


class Grid:
    """A 2D column-major grid for the LED display (grid[x][y], 9×34)."""

    def __init__(
        self,
        width: int = MATRIX_WIDTH,
        height: int = MATRIX_HEIGHT,
        fill_value: int = 0,
        init_grid: List[List[int]] = None
    ) -> None:
        """
        Initialize a Grid. If `init_grid` is provided, it must be column-major
        with shape (width × height). Otherwise, create a blank grid.
        """
        if init_grid is not None:
            if not is_valid_grid(init_grid, width, height):
                raise ValueError(f"init_grid must be {width}×{height} column-major 0/1 list")
            self._grid = [col[:] for col in init_grid]
        else:
            if fill_value not in (0, 1):
                raise ValueError("fill_value must be 0 or 1")
            self._grid = generate_blank_grid(width=width, height=height, fill_value=fill_value)

        self._width = width
        self._height = height
        self._fill_value = fill_value

    @property
    def grid(self) -> List[List[int]]:
        """Defensive copy of the column-major grid data."""
        return [col[:] for col in self._grid]

    @grid.setter
    def grid(self, value: List[List[int]]) -> None:
        """Replace the internal grid; must be column-major and correct shape."""
        if not is_valid_grid(value, self._width, self._height):
            raise ValueError(f"grid must be {self._width}×{self._height} column-major 0/1 list")
        self._grid = [col[:] for col in value]

    @property
    def width(self) -> int:
        """Number of columns."""
        return self._width

    @property
    def height(self) -> int:
        """Number of rows."""
        return self._height

    @property
    def fill_value(self) -> int:
        """Default pixel fill (0 or 1)."""
        return self._fill_value

    @fill_value.setter
    def fill_value(self, v: int) -> None:
        """Set default pixel fill; must be 0 or 1."""
        if not isinstance(v, int) or v not in (0, 1):
            raise ValueError("fill_value must be 0 or 1")
        self._fill_value = v

    @property
    def cols(self) -> int:
        """Alias for width."""
        return self._width

    @property
    def rows(self) -> int:
        """Alias for height."""
        return self._height

    @classmethod
    def load_blank_grid(
        cls,
        width: int = MATRIX_WIDTH,
        height: int = MATRIX_HEIGHT,
        fill_value: int = 0
    ) -> List[List[int]]:
        """Return a new blank column-major grid."""
        return generate_blank_grid(width=width, height=height, fill_value=fill_value)

    @classmethod
    def from_spec(
        cls,
        spec: List[List[int]]
    ) -> 'Grid':
        """Instantiate directly from a column-major spec list."""
        return cls(init_grid=spec)

    @classmethod
    def from_file(
        cls,
        filename: Union[str, Path],
        frame_number: int = 0,
        height: int = MATRIX_HEIGHT,
        width: int = MATRIX_WIDTH
    ) -> 'Grid':
        """
        Load a column-major grid from file (single grid or frames of grids).
        """
        raw = load_from_file(str(filename))
        # Single-grid JSON: list of lists
        if isinstance(raw, list) and raw and isinstance(raw[0], list):
            grid_data = raw
        # Frame-list JSON: list of dicts
        elif isinstance(raw, list) and all(isinstance(f, dict) for f in raw):
            frame = raw[frame_number]
            grid_data = frame.get('grid')
            if not isinstance(grid_data, list):
                raise ValueError(f"Frame {frame_number} missing 'grid' list")
        else:
            raise ValueError("Unsupported file structure for grid data.")

        if not is_valid_grid(grid_data, width, height):
            raise ValueError(f"Loaded grid is not {width}×{height} column-major 0/1 list")

        return cls(width=width, height=height, init_grid=grid_data)

    def draw(self, device: Any) -> None:
        """Draw this grid via device.draw_grid(grid)."""
        if not hasattr(device, 'draw_grid') or not callable(device.draw_grid):
            raise AttributeError("device.draw_grid(grid) not available")
        device.draw_grid(self)

    def get_pixel_value(self, x: int, y: int) -> int:
        """Return the value at column x, row y."""
        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            raise IndexError(f"({x},{y}) out of bounds {self._width}×{self._height}")
        return self._grid[x][y]

    def get_shifted(
        self,
        dx: int = 0,
        dy: int = 0,
        wrap: bool = False
    ) -> 'Grid':
        """
        Return a new Grid shifted by (dx, dy):
          - dx > 0 moves right, dx < 0 moves left
          - dy > 0 moves down, dy < 0 moves up
        If wrap=True, shifts wrap around edges; otherwise, out-of-bounds fill with fill_value.
        """
        new = generate_blank_grid(self._width, self._height, self._fill_value)
        for c in range(self._width):
            for r in range(self._height):
                src_c = (c + dx) % self._width if wrap else c + dx
                src_r = (r + dy) % self._height if wrap else r + dy
                if 0 <= src_c < self._width and 0 <= src_r < self._height:
                    new[c][r] = self._grid[src_c][src_r]
        return Grid(width=self._width, height=self._height, fill_value=self._fill_value, init_grid=new)



# class Grid:
#     """
#     A 2D grid of pixels for the LED matrix display.
#
#     This class represents a grid of pixels that can be displayed on an LED matrix.
#     It provides methods for creating, manipulating, and loading grids from files.
#     """
#
#     @classmethod
#     def load_blank_grid(cls, width=MATRIX_WIDTH, height=MATRIX_HEIGHT, fill_value=0):
#         return generate_blank_grid(width=width, height=height)
#
#     def __init__(
#             self,
#             width: int = MATRIX_WIDTH,
#             height: int = MATRIX_HEIGHT,
#             fill_value: int = 0,
#             init_grid: Optional[List[List[int]]] = None
#     ) -> None:
#         """
#         Initialize a new Grid instance.
#
#         Args:
#             width (int):
#                 Width of the grid in pixels. Defaults to
#                 :const:`led_matrix_battery.led_matrix.display.grid.grid.MATRIX_WIDTH`.
#
#             height (int):
#                 Height of the grid in pixels. Defaults to
#                 :const:`led_matrix_battery.led_matrix.display.grid.grid.MATRIX_HEIGHT`.
#
#             fill_value (int):
#                 Value to fill empty cells with (0 or 1, defaults to 0).
#
#             init_grid (Optional[List[List[int]]]):
#                 Initial grid data. If None, creates an empty grid. If this is provided, all previous args are ignored.
#         """
#         self.__fill_value = None
#         self.__grid = None
#         self.__height = None
#         self.__width = None
#
#         self.fill_value = fill_value
#         # Set width and height carefully, respecting immutability if grid is set later
#
#         if init_grid is not None:
#             # If init_grid is provided, dimensions are derived from it, overriding width/height args
#
#             self.grid = [row[:] for row in init_grid]  # Use slicing for a shallow copy
#
#
#         else:
#             # If no init_grid, use width/height to create a blank grid
#             self.grid = self.load_blank_grid(self.width, self.height, self.fill_value)  # Pass fill_value
#             self._process_grid_dimensions()  # Ensure width/height are consistent
#
#     def _process_grid_dimensions(self) -> None:
#         """
#         Calculate and set the dimensions of the grid based on the grid data.
#
#         This is an internal method used to update the width and height properties
#         based on the current grid data. It should be called after `self.__grid` is set.
#
#         Raises:
#             ValueError: If the grid is empty (None) or malformed.
#         """
#         if self.__grid is None:
#             raise ValueError('Grid data is None, cannot process dimensions.')
#
#         if not self.__grid:  # Empty list for grid (no rows)
#             self.__height = 0
#             self.__width = 0
#             return
#
#         self.__height = len(self.__grid)
#         first_row_len = len(self.__grid[0]) if self.__height > 0 and self.__grid[0] is not None else 0
#         for row in self.__grid:
#             if len(row) != first_row_len:
#                 raise ValueError("Grid rows have inconsistent lengths.")
#         self.__width = first_row_len
#
#     @property
#     def cols(self) -> int:
#         """
#         Get the number of columns in the grid.
#
#         Returns:
#             int: The width of the grid (number of columns).
#         """
#         return self.width
#
#     @property
#     def fill_value(self) -> int:
#         """
#         Get the current fill value for empty cells.
#
#         Returns:
#             int: The fill value (0 or 1).
#         """
#         return self.__fill_value
#
#     @fill_value.setter
#     def fill_value(self, new: int) -> None:
#         """
#         Set the fill value for empty cells.
#
#         Args:
#             new (int): The new fill value (must be 0 or 1).
#
#         Raises:
#             TypeError: If the new value is not an integer.
#             ValueError: If the new value is not 0 or 1.
#         """
#         if not isinstance(new, int):
#             raise TypeError("Fill value must be an integer")
#
#         if new not in {0, 1}:
#             raise ValueError("Fill value must be 0 or 1")
#         self.__fill_value = new
#
#     @property
#     def grid(self) -> List[List[int]]:
#         """
#         Get the current grid data.
#
#         Returns:
#             List[List[int]]: A 2D list representing the grid data.
#                            Returns a defensive copy.
#         """
#         if self.__grid is None:
#             self.__grid = load_blank_grid(self.width, self.height, self.fill_value)
#         return [row[:] for row in self.__grid]
#
#     @grid.setter
#     def grid(self, value: List[List[int]]) -> None:
#         """
#         Set the grid data.
#         Args:
#             value (List[List[int]]): A 2D list representing the new grid data.
#         Raises:
#             ValueError: If the provided grid data is invalid.
#         """
#         temp_width = len(value)
#         temp_height = len(value[0]) if temp_width > 0 else 0
#         # print(temp_width, temp_height)
#         # print(value)
#
#         if not is_valid_grid(value, width=temp_width, height=temp_height):
#             raise ValueError('Invalid grid data provided.')
#
#         self.__grid = [row[:] for row in value]
#         self._process_grid_dimensions()
#
#     @property
#     def height(self) -> int:
#         """
#         Get the height of the grid (number of rows).
#         Returns:
#             int: The number of rows in the grid.
#         """
#         if self.__height is None and self.__grid is not None:
#             self._process_grid_dimensions()
#         elif self.__height is None:
#             raise ValueError("Height not initialized and grid is not set.")
#         return self.__height
#
#     @height.setter
#     def height(self, new: int) -> None:
#         """
#         Set the height of the grid.
#         Args:
#             new (int): The new height value.
#         Raises:
#             RuntimeError: If the grid is already initialized and dimensions are considered immutable.
#             ValueError: If the new height is not a positive integer.
#         """
#         if self.__grid is not None:
#             raise RuntimeError('Grid dimensions are immutable once data is set.')
#
#         if not isinstance(new, int) or new <= 0:
#             new = coerce_to_int(new)
#             if new is None:
#                 raise TypeError("Height must be an integer.")
#
#         if new < 0:
#             raise ValueError("Height must be a positive integer.")
#
#         self.__height = new
#
#     @property
#     def rows(self) -> int:
#         """
#         Get the number of rows in the grid.
#         Returns:
#             int: The height of the grid (number of rows).
#         """
#         return self.height
#
#     @property
#     def width(self) -> int:
#         """
#         Get the width of the grid (number of columns).
#         Returns:
#             int: The width of the grid.
#         """
#         if not self.__width and self.__grid is not None:
#             return len(self.grid[0])
#
#         return self.__width or MATRIX_WIDTH
#
#     @width.setter
#     def width(self, new: int) -> None:
#         """
#         Set the width of the grid.
#         Args:
#             new (int): The new width value.
#         Raises:
#             RuntimeError: If the grid is already initialized and dimensions are considered immutable.
#             ValueError: If the new width is not a positive integer.
#         """
#         if self.__grid is not None:
#             raise RuntimeError('Grid dimensions are immutable once data is set.')
#
#         if not isinstance(new, int):
#             new = coerce_to_int(new)
#             if new is None:
#                 raise TypeError("Width must be an integer.")
#
#         if new < 0:
#             raise ValueError("Width must be a positive integer.")
#
#         self.__width = new
#
#     @classmethod
#     def from_spec(cls, spec: List[List[int]]) -> 'Grid':
#         """
#         Creates a Grid instance from a specification list.
#         Args:
#             spec (List[List[int]]): A 2D list representing the grid data.
#         Returns:
#             Grid: A new Grid instance initialized with the provided specification.
#         Raises:
#             ValueError: If the specification is empty or malformed.
#         """
#         if not spec or not isinstance(spec, list):
#             raise ValueError("Specification cannot be empty and must be a list.")
#         if not all(isinstance(row, list) for row in spec):
#             raise ValueError("Each item in specification must be a list (row).")
#
#         height = len(spec)
#         width = len(spec[0]) if height > 0 else 0
#
#         if height > 0:
#             for r_idx, row_data in enumerate(spec):
#                 if len(row_data) != width:
#                     raise ValueError(f"Row {r_idx} has inconsistent length. Expected {width}, got {len(row_data)}.")
#
#         return cls(width=width, height=height, init_grid=spec)
#
#     @classmethod
#     def _extract_grid_from_loaded_data(
#             cls: Type['Grid'],
#             loaded_data: Any,  # Data structure from load_from_file
#             filename: Union[str, Path],
#             frame_number: int
#     ) -> List[List[int]]:
#         """
#         Extracts a single grid (List[List[int]]) from the loaded file data.
#
#         Handles cases where loaded_data is a single grid or a list of frames.
#
#         Args:
#             loaded_data: The data returned by `load_from_file`.
#             filename: The name of the file, for error messages.
#             frame_number: The specific frame to extract if loaded_data is a list of frames.
#
#         Returns:
#             List[List[int]]: The extracted grid data.
#
#         Raises:
#             ValueError: If the data structure is unsupported, file is empty,
#                         frame number is out of bounds, or frame is missing 'grid' key.
#         """
#         if not isinstance(loaded_data, list):
#             raise ValueError(
#                 f"Could not parse data from file '{filename}'. Expected list, got {type(loaded_data).__name__}.")
#         if not loaded_data:
#             raise ValueError(f"File '{filename}' is empty or contains no valid grid data.")
#
#         grid_to_load: Optional[List[List[int]]] = None
#
#         # Case 1: loaded_data is a list of lists (single grid)
#         if all(isinstance(item, list) for item in loaded_data):
#             # Ensure all sub-items are also lists (rows of integers)
#             if not all(isinstance(sub_item, list) for sub_item in loaded_data) or \
#                     not all(isinstance(val, int) for row in loaded_data for val in row):
#                 raise ValueError(f"File '{filename}' contains a single grid with invalid format.")
#             grid_to_load = loaded_data
#         # Case 2: loaded_data is a list of dicts (frames)
#         elif all(isinstance(item, dict) for item in loaded_data):
#             if not (0 <= frame_number < len(loaded_data)):
#                 raise ValueError(
#                     f"Frame number {frame_number} is out of bounds for file '{filename}' "
#                     f"which contains {len(loaded_data)} frames."
#                 )
#             frame_data = loaded_data[frame_number]
#             if 'grid' not in frame_data or not isinstance(frame_data['grid'], list):
#                 raise ValueError(f"Frame {frame_number} in '{filename}' does not contain a valid 'grid' key.")
#             grid_to_load = frame_data['grid']
#             # Further validation for grid_to_load structure
#             if not all(isinstance(row, list) for row in grid_to_load) or \
#                     not all(isinstance(val, int) for row in grid_to_load for val in row):
#                 raise ValueError(f"Grid data in frame {frame_number} of '{filename}' has invalid format.")
#         else:
#             raise ValueError(
#                 f"Unsupported data structure in file '{filename}'. Expected list of lists or list of dicts.")
#
#         if grid_to_load is None:  # Should be caught by above logic, but as a safeguard
#             raise ValueError(f"Failed to extract grid data from '{filename}'.")
#
#         return grid_to_load
#
#     @classmethod
#     def _validate_loaded_grid_dimensions(
#             cls: Type['Grid'],
#             grid_data: List[List[int]],
#             expected_width: int,
#             expected_height: int,
#             filename: Union[str, Path]
#     ) -> None:
#         """
#         Validates the dimensions of the loaded grid data against expected dimensions.
#
#         Args:
#             grid_data: The grid data (List[List[int]]) to validate.
#             expected_width: The width the grid is expected to have.
#             expected_height: The height the grid is expected to have.
#             filename: The name of the file, for error messages.
#
#         Raises:
#             ValueError: If the grid dimensions do not match the expected dimensions,
#                         or if the grid structure itself is invalid (e.g., inconsistent row lengths).
#         """
#         loaded_height = len(grid_data)
#         loaded_width = len(grid_data[0]) if loaded_height > 0 and grid_data[0] is not None else 0
#
#         # Check for inconsistent row lengths first
#         if loaded_height > 0:
#             for i, row in enumerate(grid_data):
#                 if not isinstance(row, list):  # Ensure each row is a list
#                     raise ValueError(f"Invalid grid structure in '{filename}': row {i} is not a list.")
#                 if len(row) != loaded_width:
#                     raise ValueError(
#                         f"Inconsistent row lengths in grid from file '{filename}'. "
#                         f"Row {i} has length {len(row)}, expected {loaded_width}."
#                     )
#
#         # If non-default expected_width/height were passed to from_file, validate against them.
#         # MATRIX_WIDTH and MATRIX_HEIGHT are the defaults if not overridden.
#         if (expected_width != MATRIX_WIDTH or expected_height != MATRIX_HEIGHT):
#             if loaded_width != expected_width or loaded_height != expected_height:
#                 raise ValueError(
#                     f"Grid dimensions from file '{filename}' ({loaded_width}x{loaded_height}) "
#                     f"do not match expected dimensions ({expected_width}x{expected_height})."
#                 )
#
#         # Final structural validation using is_valid_grid, now using the determined loaded_width/height
#         # This also re-checks for consistent row lengths and cell values if is_valid_grid is thorough.
#         if not is_valid_grid(grid_data, loaded_width,loaded_height):
#             raise ValueError(f"Data loaded from '{filename}' is not a valid grid structure according to is_valid_grid.")
#
#     @classmethod
#     def from_file(
#             cls: Type['Grid'],
#             filename: Union[str, Path],
#             frame_number: int = 0,
#             height: int = MATRIX_HEIGHT,  # Expected height, defaults to module constant
#             width: int = MATRIX_WIDTH  # Expected width, defaults to module constant
#     ) -> 'Grid':  # Changed Optional['Grid'] to 'Grid' as it now raises on failure
#         """
#         Loads a grid from a file.
#
#         The file can contain a single grid or multiple frames.
#         If `height` and `width` are provided (and are not the module defaults),
#         they are used to validate the loaded grid dimensions. Otherwise, the
#         dimensions from the file are used.
#
#         Args:
#             filename (Union[str, Path]):
#                 The path to the file to load from.
#             frame_number (int, optional):
#                 The frame number to load if the file contains multiple frames.
#                 Defaults to 0.
#             height (int, optional):
#                 Expected height of the grid. Defaults to
#                 :const:`led_matrix_battery.led_matrix.display.grid.grid.MATRIX_HEIGHT`.
#                 Used for validation if different from the default.
#             width (int, optional):
#                 Expected width of the grid. Defaults to
#                 :const:`led_matrix_battery.led_matrix.display.grid.grid.MATRIX_WIDTH`.
#                 Used for validation if different from the default.
#
#         Returns:
#             Grid: The loaded grid.
#
#         Raises:
#             ValueError: If the grid file is invalid, frame number is out of bounds,
#                         loaded grid dimensions mismatch expected dimensions (if specified),
#                         or data structure is unsupported.
#             FileNotFoundError: If the specified file does not exist (raised by load_from_file).
#             IsADirectoryError: If the specified path is a directory (raised by load_from_file).
#         """
#         # Step 1: Load raw data from the file
#         # load_from_file is expected to handle FileNotFoundError, IsADirectoryError,
#         # and basic parsing errors (e.g., invalid JSON).
#         raw_loaded_data = load_from_file(str(filename))
#
#         # Step 2: Extract the specific grid data (List[List[int]]) from raw_loaded_data
#         grid_to_load = cls._extract_grid_from_loaded_data(raw_loaded_data, filename, frame_number)
#
#         # Step 3: Determine actual dimensions from the extracted grid_to_load
#         actual_loaded_height = len(grid_to_load)
#         actual_loaded_width = len(grid_to_load[0]) if actual_loaded_height > 0 and grid_to_load[0] is not None else 0
#
#         # Step 4: Validate these dimensions and the grid structure.
#         # The `height` and `width` parameters to `from_file` are treated as "expected" dimensions.
#         # If they are the defaults (MATRIX_HEIGHT, MATRIX_WIDTH), we don't strictly enforce them;
#         # the file's dimensions take precedence. If they are explicitly set to something else,
#         # then we enforce that the loaded grid matches these explicit expectations.
#         cls._validate_loaded_grid_dimensions(grid_to_load, width, height, filename)
#
#         # Step 5: Create and return the Grid instance using the validated grid data.
#         # The width and height for the new Grid instance should be from the *actual* loaded data.
#         return cls(width=actual_loaded_width, height=actual_loaded_height, init_grid=grid_to_load)
#
#     def draw(self, device: object) -> None:
#         """
#         Draw this grid on the specified device.
#         Args:
#             device (object): The display device. It must have a `draw_grid` method
#                              that accepts a Grid instance or compatible data.
#         Raises:
#             AttributeError: If the device does not have a `draw_grid` method.
#             TypeError: If the `draw_grid` method is not callable.
#         """
#         if not hasattr(device, 'draw_grid'):
#             raise AttributeError("The provided device object does not have a 'draw_grid' method.")
#         if not callable(device.draw_grid):
#             raise TypeError("The 'draw_grid' attribute on the device object is not callable.")
#         device.draw_grid(self)
#
#     def get_pixel_value(self, x: int, y: int) -> int:
#         """
#         Gets the value of a pixel at the specified coordinates.
#         Args:
#             x (int): The x-coordinate of the pixel (column index, 0 to width-1).
#             y (int): The y-coordinate of the pixel (row index, 0 to height-1).
#         Returns:
#             int: The value of the pixel at the specified coordinates (e.g., 0 or 1).
#         Raises:
#             IndexError: If the coordinates (x, y) are outside the grid boundaries.
#         """
#         if not (0 <= y < self.height and 0 <= x < self.width):
#             raise IndexError(f"Coordinates ({x}, {y}) are out of bounds for grid of size {self.width}x{self.height}.")
#         return self.__grid[y][x]
#
#     def get_shifted_down(self, n: int = 1, wrap: bool = False) -> 'Grid':
#         """
#         Creates a new grid with content shifted down by n rows.
#         Args:
#             n (int, optional): Number of rows to shift down. Defaults to 1.
#             wrap (bool, optional): Whether to wrap content from bottom to top.
#                                    Defaults to False.
#         Returns:
#             Grid: A new Grid instance with the shifted content.
#         """
#         # zero-size shortcut
#         if self.height == 0 or self.width == 0:
#             blank = generate_blank_grid(
#                 width=self.width,
#                 height=self.height,
#                 fill_value=self.fill_value
#             )
#             return Grid(
#                 width=self.width,
#                 height=self.height,
#                 fill_value=self.fill_value,
#                 init_grid=blank
#             )
#
#         # 1) normalize raw __grid into column-major form
#         raw = self.__grid
#         if len(raw) == self.height and len(raw[0]) == self.width:
#             # looks like row-major [[col0,...,col8], ...] — transpose it
#             col_grid = [
#                 [raw[r][c] for r in range(self.height)]
#                 for c in range(self.width)
#             ]
#         else:
#             # already column-major
#             col_grid = raw
#
#         # 2) make a blank column-major grid
#         new_data = generate_blank_grid(
#             width=self.width,
#             height=self.height,
#             fill_value=self.fill_value
#         )
#
#         # 3) do the shift
#         for c_idx in range(self.width):
#             for r_idx in range(self.height):
#                 src_r = r_idx - n
#                 if wrap:
#                     src_r %= self.height
#                     new_data[c_idx][r_idx] = col_grid[c_idx][src_r]
#                 else:
#                     if 0 <= src_r < self.height:
#                         new_data[c_idx][r_idx] = col_grid[c_idx][src_r]
#
#         # 4) build your new Grid
#         return Grid(
#             width=self.width,
#             height=self.height,
#             fill_value=self.fill_value,
#             init_grid=new_data
#         )

    # @classmethod
    # def load_blank_grid(
    #         cls: Type['Grid'],
    #         width: Optional[int] = None,
    #         height: Optional[int] = None,
    #         fill_value: int = 0
    # ) -> 'Grid':
    #     """
    #     Creates a new blank grid with the specified dimensions and fill value.
    #     Args:
    #         width (Optional[int], optional):
    #             Width of the grid. Defaults to
    #             :const:`led_matrix_battery.led_matrix.display.grid.grid.MATRIX_WIDTH` if None.
    #         height (Optional[int], optional):
    #             Height of the grid. Defaults to
    #             :const:`led_matrix_battery.led_matrix.display.grid.grid.MATRIX_HEIGHT` if None.
    #         fill_value (int, optional):
    #             The value to fill the blank grid with (0 or 1). Defaults to 0.
    #     Returns:
    #         Grid: A new Grid instance initialized with blank data.
    #     Note:
    #         This method now directly creates a grid filled with `fill_value`.
    #     """
    #     actual_width = width if width is not None else MATRIX_WIDTH
    #     actual_height = height if height is not None else MATRIX_HEIGHT
    #
    #     if not isinstance(actual_width, int) or actual_width <= 0:
    #         raise ValueError("Width must be a positive integer.")
    #     if not isinstance(actual_height, int) or actual_height <= 0:
    #         raise ValueError("Height must be a positive integer.")
    #     if fill_value not in {0, 1}:
    #         raise ValueError("Fill value must be 0 or 1.")
    #
    #     blank_grid_data = [[fill_value for _ in range(actual_width)] for _ in range(actual_height)]
    #
    #     return cls(
    #         width=actual_width,
    #         height=actual_height,
    #         fill_value=fill_value,
    #         init_grid=blank_grid_data
    #     )
