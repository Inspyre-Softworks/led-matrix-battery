from led_matrix_battery.led_matrix.controller.controller import LEDMatrixController


def get_controllers(threaded: bool = False) -> list[LEDMatrixController]:
    from led_matrix_battery.led_matrix.constants import DEVICES

    return [LEDMatrixController(device, 100, thread_safe=True) for device in DEVICES]
