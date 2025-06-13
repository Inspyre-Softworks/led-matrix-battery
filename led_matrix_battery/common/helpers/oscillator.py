"""
Author: 
    Inspyre Softworks

Project:
    led-matrix-battery

File: 
    led_matrix_battery/common/helpers/oscillator.py

Description:
   Contains the Oscillator class, a simple oscillator that can be used to generate sine waves and other waveforms.

Since:
    v1.0
"""
from typing import Union, Literal

Direction = Literal['up', 'down']

class OscillatingNumberGenerator:
    """
    Infinite generator that walks a value between lower and upper limits by a fixed step,
    reversing its direction whenever a boundary is reached.

    Parameters:

        lower_limit (Union[int, float]):
            The minimum value (inclusive).

        upper_limit (Union[int, float]):
            The maximum value (inclusive).

        step (Union[int, float]):
            How much to add or subtract each iteration (must be > 0).

        initial_direction (Direction):
            'up' to start by adding, 'down' to start by subtracting. Defaults to 'up'.

    Raises:

        ValueError:
            If `lower_limit` > `upper_limit`, if `step` <= 0, or if
            `initial_direction` is invalid.

    Properties:

        current_value (Union[int, float]):
            The value that will be returned on the next `next()` call.

        current_direction (Direction):
            The direction ('up' or 'down') that will be applied next.

    Methods:

        reset():
            Reset the generator to its initial start value and direction.

    Example Usage:

        gen = OscillatingNumberGenerator(lower_limit=0, upper_limit=3, step=1)
        for _ in range(10):
            print(next(gen))  # 0, 1, 2, 3, 2, 1, 0, 1, 2, 3...
    """
    def __init__(
        self,
        lower_limit: Union[int, float],
        upper_limit: Union[int, float],
        step: Union[int, float],
        initial_direction: Direction = 'up'
    ):
        self.__requests = 0
        if lower_limit > upper_limit:
            raise ValueError("lower_limit must be <= upper_limit")
        if step <= 0:
            raise ValueError("step must be > 0")
        if initial_direction not in ('up', 'down'):
            raise ValueError("initial_direction must be 'up' or 'down'")

        self._lower = lower_limit
        self._upper = upper_limit
        self._step = step
        self._initial_direction = initial_direction
        self.reset()

    def __iter__(self):
        return self

    def __next__(self) -> Union[int, float]:
        """
        Return the next value in the sequence.
        """
        self.__requests += 1
        value = self._current

        if self._current_direction == 'up':
            if self._current + self._step > self._upper:
                self._current_direction = 'down'
                self._current -= self._step
            else:
                self._current += self._step
        elif self._current - self._step < self._lower:
            self._current_direction = 'up'
            self._current += self._step
        else:
            self._current -= self._step

        print(self.__requests)
        return value

    def reset(self):
        """
        Reset the generator to its initial start value and direction.
        """
        self._current = self._lower
        self._current_direction = self._initial_direction

    @property
    def current_value(self) -> Union[int, float]:
        """
        The value that will be returned on the next `next()` call.
        """
        return self._current

    @property
    def current_direction(self) -> Direction:
        """
        The direction ('up' or 'down') that will be applied next.
        """
        return self._current_direction
