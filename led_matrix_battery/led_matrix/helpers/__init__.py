import serial
from inspyre_toolbox.chrono.sleep import NegateSwitch
from inspyre_toolbox.path_man import provision_path

from ..constants import FWK_MAGIC, RESPONSE_SIZE
from serial.tools.list_ports_common import ListPortInfo

import json
from pathlib import Path
from typing import Union, Optional, List


def get_json_from_file(path: Union[str, Path]):
    path = provision_path(path)
    if not path.exists():
        raise FileNotFoundError(f'Preset file not found: {path}')

    if not path.is_file():
        raise IsADirectoryError(f'Preset file is a directory: {path}')

    with open(path, 'r') as f:
        return json.load(f)


def load_from_file(
        path:              Union[str, Path],
        expected_width:    Optional[int]               = None,
        expected_height:   Optional[int]               = None,
        fallback_duration: Optional[Union[int, float]] = None
) -> List['Frame']:
    """
    Load a list of frames from a file.
    
    Parameters:
        path (Union[str, Path]):
            The path to the file to load.
         
        expected_width (Optional[int]):
            The expected width of the frames in the file. Defaults to 9. 
        
        expected_height (Optional[int]):
            The expected height of the frames in the file. Defaults to 34.
        
        fallback_duration:
            The duration of the frames in the file. Defaults to 0.33 (1/3 of a second).

    Returns:
        List[Frame]:
            A list of frames loaded from the file.
    """
    from led_matrix_battery.led_matrix.display.animations.frame.helpers import migrate_frame
    from led_matrix_battery.led_matrix.display.grid.helpers import is_valid_grid

    width  = expected_width  or 9
    height = expected_height or 34

    json = get_json_from_file(path)

    with open(path, 'r') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"File {path} does not contain a valid JSON array")

    frames = []
    for entry in data:

        if not isinstance(entry, dict) and isinstance(entry, list) and is_valid_grid(entry, width, height):
            entry = migrate_frame(entry, fallback_duration)
            entry['duration'] = fallback_duration or .33

        frames.append(entry)

    return data


def disconnect_dev(dev):
    """
    Disconnect the device from the system.

    Parameters:
        dev (str):
            The device to disconnect.
    """

    global DISCONNECTED_DEVS
    if dev in DISCONNECTED_DEVS:
        return

    DISCONNECTED_DEVS.append(dev)


def send_command(dev, command, parameters=None, with_response=False):
    """
    Send a command to the device using a new serial connection.

    Parameters:
        dev (ListPortInfo):
            The name of the port to send the command to.

        command (list):
            The command to send.

        parameters (list):
            The parameters to send with the command.

        with_response (bool):
            Whether to wait for a response from the device.

    Returns:
        The response from the device, if any.
    """
    if parameters is None:
        parameters = []
    return send_command_raw(dev, FWK_MAGIC + [command] + parameters, with_response)


def send_command_raw(dev, command, with_response=False, response_size=None):
    """
    Send a command to the device using a new serial connection.

    Parameters:
        dev (ListPortInfo):
            The name of the port to send the command to.

        command (list):
            The command to send.

        with_response (bool):
            Whether to wait for a response from the device.

        response_size (int):
            The size of the response to expect.

    Returns:
        The response from the device, if any.
    """
    # print(f"Sending command: {command}")
    res_size = response_size or RESPONSE_SIZE
    try:
        with serial.Serial(dev.device, 115200) as s:
            s.write(command)

            return s.read(res_size) if with_response else None
    except (IOError, OSError) as _ex:
        disconnect_dev(dev.device)
        return None
        # print("Error: ", ex)


def send_serial(dev, s, command):
    """
    Send serial command by using an existing serial connection

    Parameters:
        dev (ListPortInfo):
            The name of the port to send the command to.

        s (`serial.Serial`):
            The serial connection to use.

        command (bytes):
            The command to send.
    """
    try:
        s.write(command)
    except (IOError, OSError) as _ex:
        disconnect_dev(dev.device)
        # print("Error: ", ex)


def identify_devices(devices=None):
    pass


running = NegateSwitch(False)


