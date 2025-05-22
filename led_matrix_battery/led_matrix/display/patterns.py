"""
Pattern display module for LED Matrix.

This module provides functions for displaying various patterns on the LED matrix.
It includes functions for displaying checkerboards, gradients, and other visual patterns.
"""

import serial
import time

from ..constants import WIDTH, HEIGHT
from ..hardware import (
    CommandVals, PatternVals, send_command, send_serial,
    brightness, get_status, set_status
)


def pattern(dev, p):
    """Display a pattern that's already programmed into the firmware"""
    if p == "All LEDs on":
        send_command(dev, CommandVals.Pattern, [PatternVals.FullBrightness])
    elif p == "Gradient (0-13% Brightness)":
        send_command(dev, CommandVals.Pattern, [PatternVals.Gradient])
    elif p == "Double Gradient (0-7-0% Brightness)":
        send_command(dev, CommandVals.Pattern, [PatternVals.DoubleGradient])
    elif p == '"LOTUS" sideways':
        send_command(dev, CommandVals.Pattern, [PatternVals.DisplayLotus])
    elif p == "Zigzag":
        send_command(dev, CommandVals.Pattern, [PatternVals.ZigZag])
    elif p == '"PANIC"':
        send_command(dev, CommandVals.Pattern, [PatternVals.DisplayPanic])
    elif p == '"LOTUS" Top Down':
        send_command(dev, CommandVals.Pattern, [PatternVals.DisplayLotus2])
    elif p == "All brightness levels (1 LED each)":
        all_brightnesses(dev)
    elif p == "Every Second Row":
        every_nth_row(dev, 2)
    elif p == "Every Third Row":
        every_nth_row(dev, 3)
    elif p == "Every Fourth Row":
        every_nth_row(dev, 4)
    elif p == "Every Fifth Row":
        every_nth_row(dev, 5)
    elif p == "Every Sixth Row":
        every_nth_row(dev, 6)
    elif p == "Every Second Col":
        every_nth_col(dev, 2)
    elif p == "Every Third Col":
        every_nth_col(dev, 3)
    elif p == "Every Fourth Col":
        every_nth_col(dev, 4)
    elif p == "Every Fifth Col":
        every_nth_col(dev, 4)
    elif p == "Checkerboard":
        checkerboard(dev, 1)
    elif p == "Double Checkerboard":
        checkerboard(dev, 2)
    elif p == "Triple Checkerboard":
        checkerboard(dev, 3)
    elif p == "Quad Checkerboard":
        checkerboard(dev, 4)
    else:
        print("Invalid pattern")


def send_col(dev, s, x, vals):
    """Stage greyscale values for a single column. Must be committed with commit_cols()"""
    from ..hardware import FWK_MAGIC
    command = FWK_MAGIC + [CommandVals.StageGreyCol, x] + vals
    send_serial(dev, s, command)


def commit_cols(dev, s):
    """Commit the changes from sending individual cols with send_col(), displaying the matrix.
    This makes sure that the matrix isn't partially updated."""
    from ..hardware import FWK_MAGIC
    command = FWK_MAGIC + [CommandVals.DrawGreyColBuffer, 0x00]
    send_serial(dev, s, command)


def checkerboard(dev, n):
    with serial.Serial(dev.device, 115200) as s:
        for x in range(0, WIDTH):
            vals = (([0xFF] * n) + ([0x00] * n)) * int(HEIGHT / 2)
            if x % (n * 2) < n:
                # Rotate once
                vals = vals[n:] + vals[:n]

            send_col(dev, s, x, vals)
        commit_cols(dev, s)


def every_nth_col(dev, n):
    with serial.Serial(dev.device, 115200) as s:
        for x in range(0, WIDTH):
            vals = [(0xFF if x % n == 0 else 0) for _ in range(HEIGHT)]

            send_col(dev, s, x, vals)
        commit_cols(dev, s)


def every_nth_row(dev, n):
    with serial.Serial(dev.device, 115200) as s:
        for x in range(0, WIDTH):
            vals = [(0xFF if y % n == 0 else 0) for y in range(HEIGHT)]

            send_col(dev, s, x, vals)
        commit_cols(dev, s)


def all_brightnesses(dev):
    """Increase the brightness with each pixel.
    Only 0-255 available, so it can't fill all 306 LEDs"""
    with serial.Serial(dev.device, 115200) as s:
        for x in range(0, WIDTH):
            vals = [0 for _ in range(HEIGHT)]

            for y in range(HEIGHT):
                brightness = x + WIDTH * y
                if brightness > 255:
                    vals[y] = 0
                else:
                    vals[y] = brightness

            send_col(dev, s, x, vals)
        commit_cols(dev, s)


def breathing(dev):
    """Animate breathing brightness.
    Keeps currently displayed grid"""
    set_status('breathing')
    # Bright ranges appear similar, so we have to go through those faster
    while get_status() == 'breathing':
        # Go quickly from 250 to 50
        for i in range(10):
            time.sleep(0.03)
            brightness(dev, 250 - i * 20)

        # Go slowly from 50 to 0
        for i in range(10):
            time.sleep(0.06)
            brightness(dev, 50 - i * 5)

        # Go slowly from 0 to 50
        for i in range(10):
            time.sleep(0.06)
            brightness(dev, i * 5)

        # Go quickly from 50 to 250
        for i in range(10):
            time.sleep(0.03)
            brightness(dev, 50 + i * 20)


def eq(dev, vals):
    """Display 9 values in equalizer diagram starting from the middle, going up and down"""
    matrix = [[0 for _ in range(34)] for _ in range(9)]

    for col, val in enumerate(vals[:9]):
        row = int(34 / 2)
        above = int(val / 2)
        below = val - above

        for i in range(above):
            matrix[col][row + i] = 0xFF
        for i in range(below):
            matrix[col][row - 1 - i] = 0xFF

    render_matrix(dev, matrix)


def render_matrix(dev, matrix):
    """Show a black/white matrix
    Send everything in a single command"""
    # Initialize a byte array to hold the binary representation of the matrix
    # 39 bytes = 312 bits, which is enough for 9x34 = 306 pixels
    vals = [0x00 for _ in range(39)]

    # Iterate through each position in the 9x34 matrix
    for x in range(9):
        for y in range(34):
            # Convert 2D coordinates to a linear index
            # The matrix is stored in column-major order (y changes faster than x)
            i = x + 9 * y

            # If the pixel at this position is "on" (non-zero)
            if matrix[x][y]:
                # Calculate which byte in the vals array this pixel belongs to
                byte_index = int(i / 8)

                # Calculate which bit within that byte represents this pixel
                bit_position = i % 8

                # Set the corresponding bit in the appropriate byte
                # This efficiently packs 8 pixels into each byte
                vals[byte_index] = vals[byte_index] | (1 << bit_position)

    # Send the packed binary data to the device
    send_command(dev, CommandVals.Draw, vals)


def light_leds(dev, leds):
    """Light a specific number of LEDs"""
    # Initialize a byte array with all LEDs off
    vals = [0x00 for _ in range(39)]

    # Calculate how many complete bytes we need to fill (each byte = 8 LEDs)
    complete_bytes = int(leds / 8)

    # Set all complete bytes to 0xFF (all 8 bits on)
    for byte in range(complete_bytes):
        vals[byte] = 0xFF

    # Handle the remaining LEDs (less than 8) in the last partial byte
    remaining_leds = leds % 8

    # For each remaining LED, set the corresponding bit in the last byte
    # This creates a binary pattern like 00011111 for 5 remaining LEDs
    for i in range(remaining_leds):
        vals[complete_bytes] += 1 << i

    # Send the command to the device to display the pattern
    send_command(dev, CommandVals.Draw, vals)