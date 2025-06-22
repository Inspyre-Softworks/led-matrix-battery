from .commands import PatternVals
from is_matrix_forge.led_matrix.commands.map import CommandVals
from is_matrix_forge.led_matrix.commands import send_command
from .stencils import all_brightnesses, every_nth_row, every_nth_col, checkerboard


PATTERN_MAP = {
    "All LEDs on": lambda dev: send_command(dev, CommandVals.Pattern, [PatternVals.FullBrightness]),
    "Gradient (0-13% Brightness)": lambda dev: send_command(dev, CommandVals.Pattern, [PatternVals.Gradient]),
    "Double Gradient (0-7-0% Brightness)": lambda dev: send_command(dev, CommandVals.Pattern, [PatternVals.DoubleGradient]),
    "\"LOTUS\" sideways": lambda dev: send_command(dev, CommandVals.Pattern, [PatternVals.DisplayLotus]),
    "Zigzag": lambda dev: send_command(dev, CommandVals.Pattern, [PatternVals.ZigZag]),
    "\"PANIC\"": lambda dev: send_command(dev, CommandVals.Pattern, [PatternVals.DisplayPanic]),
    "\"LOTUS\" Top Down": lambda dev: send_command(dev, CommandVals.Pattern, [PatternVals.DisplayLotus2]),
    "All brightness levels (1 LED each)": lambda dev: all_brightnesses(dev),
    "Every Second Row": lambda dev: every_nth_row(dev, 2),
    "Every Third Row": lambda dev: every_nth_row(dev, 3),
    "Every Fourth Row": lambda dev: every_nth_row(dev, 4),
    "Every Fifth Row": lambda dev: every_nth_row(dev, 5),
    "Every Sixth Row": lambda dev: every_nth_row(dev, 6),
    "Every Second Col": lambda dev: every_nth_col(dev, 2),
    "Every Third Col": lambda dev: every_nth_col(dev, 3),
    "Every Fourth Col": lambda dev: every_nth_col(dev, 4),
    "Every Fifth Col": lambda dev: every_nth_col(dev, 5),
    "Checkerboard": lambda dev: checkerboard(dev, 1),
    "Double Checkerboard": lambda dev: checkerboard(dev, 2),
    "Triple Checkerboard": lambda dev: checkerboard(dev, 3),
    "Quad Checkerboard": lambda dev: checkerboard(dev, 4),
}