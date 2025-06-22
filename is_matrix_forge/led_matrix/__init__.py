

def get_controllers():
    from is_matrix_forge.led_matrix.controller.controller import LEDMatrixController
    from is_matrix_forge.led_matrix.constants import DEVICES

    return [LEDMatrixController(device, 100) for device in DEVICES]
