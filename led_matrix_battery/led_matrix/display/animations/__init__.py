from time import sleep


from led_matrix_battery.led_matrix import (
    brightness,
    pattern,
    checkerboard,
    show_string,
)


# TODO: Decouple from led_matrix_battery.inputmodule in favor of new code in led_matrix_battery.hardware


def clear(dev):
    brightness(dev, 0)


def checkerboard_cycle(dev):
    frame = 2

    while frame < 5:
        brightness(dev, 25)
        print(f'Processing frame: {frame}')
        sleep(1)
        checkerboard(dev, frame)
        frame += 1


def goodbye_animation(dev):
    clear(dev)
    sleep(.1)
    checkerboard_cycle(dev)
    sleep(.5)
    show_string(dev, 'Bye')
