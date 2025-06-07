from led_matrix_battery.led_matrix.controller.controller import LEDMatrixController
from led_matrix_battery.led_matrix.constants import DEVICES


def get_controllers(threaded: bool = False) -> list[LEDMatrixController]:
    return [LEDMatrixController(device, 100, thread_safe=True) for device in DEVICES]
