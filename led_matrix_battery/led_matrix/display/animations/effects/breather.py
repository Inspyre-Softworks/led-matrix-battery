import threading
import time


class Breather:
    """
    Controls a “breathing” (fade in/out) effect on a controller’s brightness.

    Parameters:
        controller:
            Any object with a mutable `brightness` attribute (0–100).

        min_brightness (int):
            Lowest brightness in the cycle. Defaults to 5.

        max_brightness (int):
            Highest brightness in the cycle. Defaults to 90.

        step (int):
            Amount to change brightness each tick. Defaults to 5.

        breathe_fps (float):
            How many brightness updates per second. Defaults to 30.

    Methods:

        start():
            Launch the breathing loop in a background thread.

        stop():
            Halt the breathing loop and join the thread.
    """
    def __init__(
            self,
            controller,
            min_brightness: int   = 5,
            max_brightness: int   = 90,
            step:           int   = 5,
            breathe_fps:    float = 30.0
    ):
        self.__controller = None

    @property
    def controller(self) -> 'LEDMatrixController':
        """
        The controller for the LED matrix device.

        Returns:
            LEDMatrixController:
                The controller for the LED matrix device.

        See Also:
            led_matrix_battery.led_matrix.controller.LEDMatrixController
        """
        return self.__controller

    @controller.setter
    def controller(self, controller:):

