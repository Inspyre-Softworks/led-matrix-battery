from typing import Callable, Dict, Any, Tuple
from .pattern import Pattern
from . import checkerboard
from ... import every_nth_col, every_nth_row, all_brightnesses


class PatternPen:
    """
    Handles selection and execution of LED-matrix patterns. Made specifically for the Framework 16 9x32 LED Matrix
    input-modules.

    Parameters:
        send_command (Callable):
            A function that sends commands to the LED matrix module.
    """

    def __init__(self, send_command: Callable, command_vals: Any, pattern_vals: Any):
        self._send = send_command
        self._cmd = command_vals.Pattern
        self._pvals = pattern_vals
        # Map lowercase pattern names to Pattern objects
        self._patterns: Dict[str, Pattern] = {}
        self._register_defaults()

    def __build_checkerboard_patterns(self):
        """
        Registers checkerboard patterns of increasing frequency.

        This method creates and registers single, double, triple, and quad checkerboard patterns for the LED matrix.
        """
        # Checkerboards of increasing frequency
        names = ["Single", "Double", "Triple", "Quad"]
        for i, prefix in enumerate(names, start=1):
            self.register(f"{prefix} Checkerboard", checkerboard, i)

    def __build_row_col_patterns(self):
        """
        Registers patterns for every nth row and column on the LED matrix.

        This method creates and registers patterns that activate every second, third, fourth, fifth, and sixth row
        and column.
        """
        # Row and column patterns
        ordinals = {2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth", 6: "Sixth"}
        for n, name in ordinals.items():
            self.register(f"Every {name} Row", every_nth_row, n)
            self.register(f"Every {name} Col", every_nth_col, n)

    def _register_defaults(self):
        p = self._pvals

        # Simple firmware patterns
        self.register("All LEDs on", self._send, self._cmd, [p.FullBrightness])
        self.register("Gradient (0-13% Brightness)", self._send, self._cmd, [p.Gradient])
        self.register("Double Gradient (0-7-0% Brightness)", self._send, self._cmd, [p.DoubleGradient])
        self.register('"LOTUS" sideways', self._send, self._cmd, [p.DisplayLotus])
        self.register("Zigzag", self._send, self._cmd, [p.ZigZag])
        self.register('"PANIC"', self._send, self._cmd, [p.DisplayPanic])
        self.register('"LOTUS" Top Down', self._send, self._cmd, [p.DisplayLotus2])

        # All single-brightness steps
        self.register("All brightness levels (1 LED each)", all_brightnesses)

        self.__build_row_col_patterns()

        self.__build_checkerboard_patterns()

    def register(self, name: str, action: Callable[..., None], *args: Any, **kwargs: Any):
        """Add or override a pattern by name (lookup will be case-insensitive)."""
        key = name.lower()
        self._patterns[key] = Pattern(name, action, args, kwargs)

    def display(self, dev: Any, name: str):
        """
        Display the named pattern on the device (case-insensitive).

        Raises:
            ValueError:
                If `name` is not a registered pattern.
        """
        key = name.lower()
        if pattern := self._patterns.get(key):
            pattern.action(dev, *pattern.args, **pattern.kwargs)
        else:
            raise ValueError(f"Invalid pattern: {name!r}")