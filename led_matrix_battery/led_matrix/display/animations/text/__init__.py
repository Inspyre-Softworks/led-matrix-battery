from time import sleep
from led_matrix_battery.inputmodule import font
from led_matrix_battery.inputmodule.ledmatrix import send_command, CommandVals


def scroll_text_bottom_to_top(dev, text, delay=0.1):
    # display dimensions
    ROWS, COLS = 34, 9
    BYTES = (ROWS * COLS + 7) // 8  # = 39

    # 1) build the big grid
    font_items = [font.convert_font(c) for c in text]
    total_height = len(font_items) * 7  - 1  # 6 pixels + 1 blank between letters
    big_grid = [[0]*COLS for _ in range(total_height)]

    for idx, glyph in enumerate(font_items):
        base_row = idx * 7
        for x in range(5):
            for y in range(6):
                if glyph[x + y*5]:
                    big_grid[base_row + y][2 + x] = 1  # centered at col 2

    # 2) scroll it!
    for top in range(-ROWS, total_height):
        # extract a ROWS×COLS slice
        window = [
            big_grid[r] if 0 <= r < total_height else [0]*COLS
            for r in range(top, top + ROWS)
        ]

        # flatten to byte array
        vals = [0] * BYTES
        for r, row in enumerate(window):
            for c, bit in enumerate(row):
                if bit:
                    i = r*COLS + c
                    byte, bitpos = divmod(i, 8)
                    vals[byte] |= 1 << bitpos

        # draw and wait
        send_command(dev, CommandVals.Draw, vals)
        sleep(delay)
