
from led_matrix_battery.led_matrix.controller import LEDMatrixController
from led_matrix_battery.led_matrix.constants import DEVICES
from threading import Thread


threads = []


def identify_devices(devices=None):
    global threads

    if devices is None:
        devices = DEVICES

    controllers = []

    for device in devices:
        controllers.append(LEDMatrixController(device, 100))

    for controller in controllers:
        t = Thread(target=controller.identify)
        threads.append(t)
        t.start()


if __name__ == "__main__":
    identify_devices()
