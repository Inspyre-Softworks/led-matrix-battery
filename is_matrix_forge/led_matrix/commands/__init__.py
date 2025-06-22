"""


Author: 
    Inspyre Softworks

Project:
    led-matrix-battery

File: 
    is_matrix_forge/led_matrix/commands/__init__.py
 

Description:
    

"""
from typing import List, Optional, ByteString

import serial
from serial.tools.list_ports_common import ListPortInfo

from is_matrix_forge.led_matrix.constants import RESPONSE_SIZE, FWK_MAGIC
from is_matrix_forge.led_matrix.helpers import disconnect_dev


def send_command_raw(dev: ListPortInfo, command: List[int], with_response: bool = False, response_size: Optional[int] = None) -> Optional[ByteString]:
    """
    Send a command to the device using a new serial connection.

    Args:
        dev (ListPortInfo): The device to send the command to.
        command (List[int]): The command to send.
        with_response (bool, optional): Whether to wait for a response from the device. Defaults to False.
        response_size (Optional[int], optional): The size of the response to expect. Defaults to None.

    Returns:
        Optional[ByteString]: The response from the device, if any, or None if no response or an error occurred.

    Raises:
        IOError, OSError: If there is an error communicating with the device.
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


def send_command(
        dev:           ListPortInfo,
        command:       int,
        parameters:    Optional[List[int]] = None,
        with_response: bool                = False
) -> Optional[ByteString]:
    """
    Send a command to the device using a new serial connection.

    Parameters:
        dev (ListPortInfo):
            The device to send the command to.

        command (int):
            The command to send.

        parameters (Optional[List[int]], optional):
            The parameters to send with the command. Defaults to None.

        with_response (bool, optional):
            Whether to wait for a response from the device. Defaults to False.

    Returns:
        Optional[ByteString]:
            The response from the device, if any, or None if no response or an error occurred.
    """
    if parameters is None:
        parameters = []
    return send_command_raw(dev, FWK_MAGIC + [command] + parameters, with_response)
