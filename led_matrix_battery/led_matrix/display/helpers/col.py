"""


Author: 
    Inspyre Softworks

Project:
    led-matrix-battery

File: 
    ${DIR_PATH}/${FILE_NAME}
 

Description:
    $DESCRIPTION

"""
from led_matrix_battery.led_matrix import send_serial, CommandVals


def commit_cols(dev, s):
    """Commit the changes from sending individual cols with send_col(), displaying the matrix.
    This makes sure that the matrix isn't partially updated."""
    from ...hardware import FWK_MAGIC
    command = FWK_MAGIC + [CommandVals.DrawGreyColBuffer, 0x00]
    send_serial(dev, s, command)


def send_col(dev, s, x, vals):
    """Stage greyscale values for a single column. Must be committed with commit_cols()"""
    from ...hardware import FWK_MAGIC
    command = FWK_MAGIC + [CommandVals.StageGreyCol, x] + vals
    send_serial(dev, s, command)
