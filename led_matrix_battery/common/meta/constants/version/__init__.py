"""


Author: 
    Inspyre Softworks

Project:
    led-matrix-battery

File: 
    led_matrix_battery/common/meta/version/__init__.py
 

Description:
    

"""
from pathlib import Path
import sys
from inspyre_toolbox.ver_man import VersionParser, PyPiVersionInfo, TestPyPiVersionInfo
from inspyre_toolbox.ver_man.helpers import get_version_from_file
from inspyre_toolbox.ver_man.classes.pypi.errors import PyPiPackageNotFoundError

from inspy_logger import InspyLogger

__MOD_LOGGER = InspyLogger(__name__, console_level='debug', no_file_logging=True)


VERSION_FILE = Path(__file__).parent / 'VERSION'

__VERSION__ = get_version_from_file(VERSION_FILE)

VERSION = __VERSION__.version_str

try:
    PYPI_VERSION_INFO = PyPiVersionInfo('led-matrix-battery')
except PyPiPackageNotFoundError as e:
    __MOD_LOGGER.warning("Unable to retrieve version information for package on pypi.org.")

    try:
        PYPI_VERSION_INFO = TestPyPiVersionInfo('led-matrix-battery', VERSION)
    except PyPiPackageNotFoundError as e:
        __MOD_LOGGER.error("Unable to retrieve version information for package on test.pypi.org.")
        PYPI_VERSION_INFO = None
