import time

import serial

from . import font
from . import send_command, CommandVals, PatternVals, FWK_MAGIC, send_serial, brightness

from is_matrix_forge.led_matrix.helpers.status_handler import get_status, set_status

WIDTH = 9
HEIGHT = 34
PATTERNS = [
    "All LEDs on",
    '"LOTUS" sideways',
    "Gradient (0-13% Brightness)",
    "Double Gradient (0-7-0% Brightness)",
    "Zigzag",
    '"PANIC"',
    '"LOTUS" Top Down',
    "All brightness levels (1 LED each)",
    "Every Second Row",
    "Every Third Row",
    "Every Fourth Row",
    "Every Fifth Row",
    "Every Sixth Row",
    "Every Second Col",
    "Every Third Col",
    "Every Fourth Col",
    "Every Fifth Col",
    "Checkerboard",
    "Double Checkerboard",
    "Triple Checkerboard",
    "Quad Checkerboard",
]
PWM_FREQUENCIES = [
    "29kHz",
    "3.6kHz",
    "1.8kHz",
    "900Hz",
]


def get_pwm_freq(dev):
    """Adjust the brightness scaling of the entire screen."""
    res = send_command(dev, CommandVals.PwmFreq, with_response=True)
    freq = int(res[0])
    if freq == 0:
        return 29000
    elif freq == 1:
        return 3600
    elif freq == 2:
        return 1800
    elif freq == 3:
        return 900
    else:
        return None


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


def image_bl(dev, image_file):
    """Display an image in black and white
    Confirmed working with PNG and GIF.
    Must be 9x34 in size.
    Sends everything in a single command
    """
    # Initialize a list of 39 bytes (39*8 = 312 bits, enough for 9x34 = 306 pixels)
    vals = [0 for _ in range(39)]

    from PIL import Image

    # Open the image and convert to RGB format
    im = Image.open(image_file).convert("RGB")
    width, height = im.size

    # Verify image dimensions match the LED matrix size
    assert width == 9
    assert height == 34

    # Get all pixel values as a flat list
    pixel_values = list(im.getdata())

    # Process each pixel
    for i, pixel in enumerate(pixel_values):
        # Calculate average brightness of RGB components
        brightness = sum(pixel) / 3

        # If brightness is above half of max (127.5), consider it "on"
        # This creates a binary black/white effect
        if brightness > 0xFF / 2:
            # Calculate which byte in vals array this pixel belongs to (i/8)
            # Then set the appropriate bit within that byte (i%8)
            # This packs 8 pixels into each byte of the vals array
            vals[int(i / 8)] |= 1 << i % 8

    # Send the packed binary data to the device
    send_command(dev, CommandVals.Draw, vals)


def camera(dev):
    """Play a live view from the webcam, for fun"""
    set_status('camera')
    with serial.Serial(dev.device, 115200) as s:
        import cv2

        capture = cv2.VideoCapture(1)
        ret, frame = capture.read()

        scale_y = HEIGHT / frame.shape[0]

        # Scale the video to 34 pixels height
        dim = (HEIGHT, int(round(frame.shape[1] * scale_y)))
        # Find the starting position to crop the width to be centered
        # For very narrow videos, make sure to stay in bounds
        start_x = max(0, int(round(dim[1] / 2 - WIDTH / 2)))
        end_x = min(dim[1], start_x + WIDTH)

        # Pre-process the video into resized, cropped, grayscale frames
        while get_status() == 'camera':
            ret, frame = capture.read()
            if not ret:
                print("Failed to capture video frames")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            resized = cv2.resize(gray, (dim[1], dim[0]))
            cropped = resized[0:HEIGHT, start_x:end_x]

            for x in range(0, cropped.shape[1]):
                vals = [0 for _ in range(HEIGHT)]

                for y in range(0, HEIGHT):
                    vals[y] = cropped[y, x]

                send_col(dev, s, x, vals)
            commit_cols(dev, s)


def video(dev, video_file):
    set_status('video')
    """Resize and play back a video"""
    with serial.Serial(dev.device, 115200) as s:
        import cv2

        capture = cv2.VideoCapture(video_file)
        ret, frame = capture.read()

        scale_y = HEIGHT / frame.shape[0]

        # Scale the video to 34 pixels height
        dim = (HEIGHT, int(round(frame.shape[1] * scale_y)))
        # Find the starting position to crop the width to be centered
        # For very narrow videos, make sure to stay in bounds
        start_x = max(0, int(round(dim[1] / 2 - WIDTH / 2)))
        end_x = min(dim[1], start_x + WIDTH)

        processed = []

        # Pre-process the video into resized, cropped, grayscale frames
        while get_status() == 'video':
            ret, frame = capture.read()
            if not ret:
                print("Failed to read video frames")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            resized = cv2.resize(gray, (dim[1], dim[0]))
            cropped = resized[0:HEIGHT, start_x:end_x]

            processed.append(cropped)

        # Determine frame delay based on the video's FPS.  Default to 30 FPS if
        # the information isn't available.
        fps = capture.get(cv2.CAP_PROP_FPS)
        try:
            fps = float(fps)
            if fps <= 0 or fps != fps:
                raise ValueError
        except Exception:
            fps = 30.0
        frame_delay = 1.0 / fps

        # Write it out to the module one frame at a time while respecting the
        # frame rate.
        for frame in processed:
            start = time.time()
            for x in range(0, cropped.shape[1]):
                vals = [0 for _ in range(HEIGHT)]

                for y in range(0, HEIGHT):
                    vals[y] = frame[y, x]

                send_col(dev, s, x, vals)
            commit_cols(dev, s)

            elapsed = time.time() - start
            if frame_delay > elapsed:
                time.sleep(frame_delay - elapsed)


def pixel_to_brightness(pixel):
    """Calculate pixel brightness from an RGB triple"""
    assert len(pixel) == 3
    brightness = sum(pixel) / len(pixel)

    # Poor man's scaling to make the greyscale pop better.
    # Should find a good function.
    if brightness > 200:
        brightness = brightness
    elif brightness > 150:
        brightness = brightness * 0.8
    elif brightness > 100:
        brightness = brightness * 0.5
    elif brightness > 50:
        brightness = brightness
    else:
        brightness = brightness * 2

    return int(brightness)


def image_greyscale(dev, image_file):
    """Display an image in greyscale
    Sends each 1x34 column and then commits => 10 commands
    """
    with serial.Serial(dev.device, 115200) as s:
        from PIL import Image

        im = Image.open(image_file).convert("RGB")
        width, height = im.size
        assert width == 9
        assert height == 34
        pixel_values = list(im.getdata())
        for x in range(0, WIDTH):
            vals = [0 for _ in range(HEIGHT)]

            for y in range(HEIGHT):
                vals[y] = pixel_to_brightness(pixel_values[x + y * WIDTH])

            send_col(dev, s, x, vals)
        commit_cols(dev, s)


def send_col(dev, s, x, vals):
    """Stage greyscale values for a single column. Must be committed with commit_cols()"""
    command = FWK_MAGIC + [CommandVals.StageGreyCol, x] + vals
    send_serial(dev, s, command)


def commit_cols(dev, s):
    """Commit the changes from sending individual cols with send_col(), displaying the matrix.
    This makes sure that the matrix isn't partially updated."""
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


def pwm_freq(dev, freq):
    """Display a pattern that's already programmed into the firmware"""
    if freq == "29kHz":
        send_command(dev, CommandVals.PwmFreq, [0])
    elif freq == "3.6kHz":
        send_command(dev, CommandVals.PwmFreq, [1])
    elif freq == "1.8kHz":
        send_command(dev, CommandVals.PwmFreq, [2])
    elif freq == "900Hz":
        send_command(dev, CommandVals.PwmFreq, [3])


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
