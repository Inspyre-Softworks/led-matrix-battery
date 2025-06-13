"""


Author: 
    Inspyre Softworks

Project:
    led-matrix-battery

File: 
    ${DIR_PATH}/${FILE_NAME}
 

Description:
    $DESCRIPTION

"""
from led_matrix_battery.inputmodule import send_command, CommandVals, PatternVals, font
from led_matrix_battery.led_matrix.display.patterns import all_brightnesses, every_nth_row, every_nth_col
from led_matrix_battery.led_matrix.helpers.status_handler import set_status


def percentage(dev, p):
    """Fill a percentage of the screen. Bottom to top"""
    send_command(dev, CommandVals.Pattern, [PatternVals.Percentage, p])


def animate(dev, b: bool):
    """Tell the firmware to start/stop animation.
    Scrolls the currently saved grid vertically down."""
    if b:
        set_status('animate')
    send_command(dev, CommandVals.Animate, [b])


def get_animate(dev):
    """Tell the firmware to start/stop animation.
    Scrolls the currently saved grid vertically down."""
    res = send_command(dev, CommandVals.Animate, with_response=True)
    return bool(res[0])


def build_matrix(matrix):
    """Build a matrix from a list of lists"""
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

    return vals


def render_matrix(dev, matrix):
    vals = build_matrix(matrix)

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


def show_string(dev, s):
    """Render a string with up to five letters"""
    show_font(dev, [font.convert_font(letter) for letter in str(s)[:5]])


def show_font(dev, font_items):
    """Render up to five 5x6 pixel font items"""
    # Initialize a byte array with all pixels off
    vals = [0x00 for _ in range(39)]

    # Process each font item (character/symbol)
    for digit_i, digit_pixels in enumerate(font_items):
        # Calculate vertical offset for this character
        # Each character is placed 7 pixels apart vertically
        offset = digit_i * 7

        # Process each pixel in the 5x6 character grid
        for pixel_x in range(5):
            for pixel_y in range(6):
                # Convert 2D coordinates to 1D index in the font data
                # Font data is stored as a 1D array in row-major order
                pixel_value = digit_pixels[pixel_x + pixel_y * 5]

                # Calculate the position in the LED matrix
                # Characters start at x=2 (to center them) and are stacked vertically
                # with the calculated offset
                i = (2 + pixel_x) + (9 * (pixel_y + offset))

                # If this pixel should be on
                if pixel_value:
                    # Calculate which byte and bit to set
                    byte_index = int(i / 8)
                    bit_position = i % 8

                    # Set the bit in the appropriate byte
                    vals[byte_index] = vals[byte_index] | (1 << bit_position)

    # Send the command to display the characters
    send_command(dev, CommandVals.Draw, vals)


def show_symbols(dev, symbols):
    """Render a list of up to five symbols
    Can use letters/numbers or symbol names, like 'sun', ':)'"""
    font_items = []
    for symbol in symbols:
        s = font.convert_symbol(symbol)
        if not s:
            s = font.convert_font(symbol)
        font_items.append(s)

    show_font(dev, font_items)
