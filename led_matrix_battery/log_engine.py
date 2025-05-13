from inspy_logger import InspyLogger, Loggable


PROGNAME = 'LEDMatrixBattery'
AUTHOR = 'Inspyre-Softworks'

INSPY_LOG_LEVEL = 'INFO'

ROOT_LOGGER = InspyLogger(PROGNAME, console_level='info', no_file_logging=True)


__all__ = [
    'Loggable',
    'ROOT_LOGGER',
]
