"""
File: monitor.py
Author: Inspyre-Softworks
Description:
    This file contains the PowerMonitor class, which is used to monitor the battery level of the system.
"""
# Standard library imports
from pathlib import Path
from threading import Thread
import time
from time import sleep
from typing import Union, Optional

from psutil import sensors_battery

# Third-party imports
from serial.tools.list_ports_common import ListPortInfo

# Inspyre-Softworks imports
from inspyre_toolbox.syntactic_sweets.classes.decorators.type_validation import validate_type

# Package imports
from .errors import *
from led_matrix_battery.common.helpers import percentage_to_value
from led_matrix_battery.log_engine import ROOT_LOGGER as PARENT_LOGGER, Loggable
from led_matrix_battery.notify.sounds import PLUGGED_NOTIFY, UNPLUGGED_NOTIFY, Sound
from ..led_matrix.helpers.device import check_device
from led_matrix_battery.led_matrix.display.animations import goodbye_animation
from led_matrix_battery.led_matrix import (
    animate,
    get_animate,
    pattern,
    percentage
)


DEFAULT_PLUGGED_SOUND   = PLUGGED_NOTIFY
DEFAULT_UNPLUGGED_SOUND = UNPLUGGED_NOTIFY


MOD_LOGGER = PARENT_LOGGER.get_child('monitor')


class PowerMonitor(Loggable):

    # Properties
    #
    _running         = False
    __check_interval = 5
    __cycles         = 0


    def __init__(
            self,
            device,
            battery_check_interval: int = 5,
            plugged_alert: Optional[Union[str, Path]] = DEFAULT_PLUGGED_SOUND,
            unplugged_alert: Optional[Union[str, Path]] = DEFAULT_UNPLUGGED_SOUND,

    ):
        super().__init__(MOD_LOGGER)
        self.__dev             = None
        self.__last_state      = None
        self.__plugged_alert   = None
        self.__thread          = None
        self.__unplugged_alert = None

        self.set_device(device)

        # Set some settings
        # First alerts, if provided
        if plugged_alert:
            self.plugged_alert = plugged_alert

        if unplugged_alert:
            self.unplugged_alert = unplugged_alert

        self.dev.brightness = percentage_to_value(5)
        self.__battery_check_interval = battery_check_interval or self.__check_interval

    @property
    def battery_check_interval(self):
        return self.__check_interval

    @battery_check_interval.setter
    @validate_type(int, str, float, preferred_type=float, conversion_funcs=[float])
    def battery_check_interval(self, new):
        log = self.method_logger

        self.__check_interval = new

    @property
    def cycles(self):
        return self.__cycles

    @property
    def dev(self):
        return self.__dev

    @property
    def last_state(self) -> Optional[bool]:
        """
        The state of the connection to the power supply on last-check.

        Returns:
            Optional[bool]:
                True;
                    The device was plugged into power.
                False;
                    The device was unplugged from power.

                None;
                    The monitor hasn't completed a check yet.
        """
        return self.__last_state

    @property
    def plugged_alert(self) -> Sound:
        if not self.__plugged_alert:
            return DEFAULT_PLUGGED_SOUND

        return self.__plugged_alert

    @validate_type(Sound)
    @plugged_alert.setter
    def plugged_alert(self, new):
        if not isinstance(new, Sound):
            raise TypeError(f'plugged_alert must be of type `Sound`, not {type(new)}')

        self.__plugged_alert = new

    @property
    def plugged_in(self):
        return sensors_battery().power_plugged

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, new):
        if not self._running and new:
            raise RuntimeError('Cannot start monitor by setting running to `True`. Use the `start` method instead.')

        if not isinstance(new, bool):
            raise TypeError(f'running must be of type `bool`, not {type(new)}')

        self._running = new

    @property
    def run_time(self):
        if not hasattr(self, 'start_time'):
            raise PowerMonitorNotRunningError('Monitor hasn\'t even been started yet!')

        if not hasattr(self, 'stop_time'):
            recent = time.time()
        else:
            recent = self.stop_time

        return recent - self.start_time

    @property
    def unplugged(self):
        return not self.plugged_in

    @property
    def unplugged_alert(self) -> 'Sound':
        if not self.__unplugged_alert:
            return DEFAULT_UNPLUGGED_SOUND

        return self.__unplugged_alert

    @validate_type()
    @unplugged_alert.setter
    def unplugged_alert(self, new):
        if not isinstance(new, Sound):
            raise TypeError(f'unplugged_alert must be of type `Sound`, not {type(new)}')

        self.__unplugged_alert = new

    def notify(self, which: str):
        """
        Notify the user of a power event (plugged, unplugged).

        Parameters:
            which (str):
                The type of notification to send ('plugged' or 'unplugged').
        """
        log = self.method_logger
        # Just return if the first check hasn't been completed yet.

        if self.last_state is None:
            log.debug('Status: Not yet checked')
            return

        if which.lower() == 'plugged':
            log.debug('Status: Plugged in')
            if not self.last_state:
                log.debug(f'Using {self.plugged_alert} to notify user...')
                self.plugged_alert.notify()
        elif which.lower() == 'unplugged':
            if self.last_state:
                log.debug(f'Using {self.unplugged_alert} to notify user...')
                self.unplugged_alert.notify()

    def set_device(self, device):
        if not isinstance(device, ListPortInfo):
            raise TypeError(f'device must be of type `ListPortInfo`, not {type(device)}')

        if not check_device(device):
            raise ValueError(f'device {device} is not available')

        self.__dev = device

    def run(self):
        """
        Run the power monitor. This is where the main loop of the monitor is located. It (roughly) does the following
        while playing notification sounds when the power supply is plugged in or unplugged:
          1. Check the battery level.
          2. If the power supply is unplugged, display the battery level on the LED matrix.
          3. If the power supply is plugged in, animate the LED matrix.
          4. Repeat.

        Note:
            This method is called by the `start` method and should not be called directly.
        """
        log = self.method_logger
        if not self._running:
            log.error('Monitor is not running')
            raise RuntimeError('Monitor is not running. If you want to start it, use the `start` method.')

        log.debug('Running monitor...')

        self.start_time = time.time()

        while self.running:
            batt = sensors_battery()
            state = batt.power_plugged

            if state:
                self.notify('plugged')
                if self.last_state is not None and not self.last_state:
                    pattern(self.dev, 'Zigzag')
                elif self.last_state is None:
                    pattern(self.dev, 'Zigzag')
                if not get_animate(self.dev):
                    animate(self.dev, True)
            else:
                self.notify('unplugged')
                if get_animate(self.dev):
                    animate(self.dev, False)
                percentage(self.dev, batt.percent)

            self.__last_state = state

            if not self.running:
                break

            self.__cycles += 1

            sleep(self.battery_check_interval)

    def start(self):
        log = self.method_logger
        log.debug('Starting monitor')
        if self.running:
            log.warning('Monitor is already running')
            raise RuntimeError('Monitor is already running')

        self._running = True
        log.debug('Set running to True')

        try:
            self.run()
        except KeyboardInterrupt:
            log.warning('KeyboardInterrupt received, stopping monitor...')
            self.stop(without_salutation=True)

    def stop(self, without_salutation=False, reason=None):
        """
        Stop the power monitor.

        Parameters:
            without_salutation (bool):
                If True, skip the goodbye animation that plays by default on the LED matrix.
        """

        log = self.method_logger

        if not self.running:
            log.error('Monitor is not running')
            raise PowerMonitorNotRunningError("Can't call stop() on a monitor that is not running")
        else:
            log.debug('Stopping monitor...')
            self.stop_time = time.time()
        self.running = False
        log.debug('"running" flag set to False...waiting for thread to finish')

        if not without_salutation:
            goodbye_animation(self.dev)
        else:
            log.debug('Skipping goodbye salutation...')

        if get_animate(self.dev):
            animate(self.dev, False)



def run_power_monitor(
        device:                 ListPortInfo,
        battery_check_interval: int = 5,
        plugged_alert:          Optional[Union[str, Path]] = DEFAULT_PLUGGED_SOUND,
        unplugged_alert:        Optional[Union[str, Path]] = DEFAULT_UNPLUGGED_SOUND,
):
    """
    Run the power monitor.

    Parameters:
        device (ListPortInfo):
            The LED matrix on which to display the battery level.

        battery_check_interval (Optional[Union[int, float, str]]):
            The interval (in seconds) at which to check the battery level.

        plugged_alert (Optional[Union[str, Path]]):
            The filepath to the sound to play when the device is plugged into power.

        unplugged_alert (Optional[Union[str, Path]]):
            The filepath to the sound to play when the device is unplugged from power.

    """
    monitor = PowerMonitor(
        device,
        battery_check_interval=battery_check_interval,
        plugged_alert=plugged_alert,
        unplugged_alert=unplugged_alert
    )

    try:
        monitor.start()
    except KeyboardInterrupt:
        monitor.stop(without_salutation=True)

    return monitor


def run_power_monitor_threaded(
        *args,
        **kwargs
) -> PowerMonitor:
    monitor = Thread(target=run_power_monitor, args=args, kwargs=kwargs)
    monitor.start()
