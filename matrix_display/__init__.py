"""Matrix display utilities extracted from the original project."""

from importlib import import_module
import sys

_SUBMODULES = [
    'Scripts',
    'constants',
    'controller',
    'display',
    'errors',
    'fonts',
    'helpers',
    'hardware',
    'led_matrix',
    'status',
    'tools',
]

def __getattr__(name):
    if name in _SUBMODULES:
        module = import_module(f'led_matrix_battery.led_matrix.{name}')
        sys.modules[f'{__name__}.{name}'] = module
        return module
    base = import_module('led_matrix_battery.led_matrix')
    return getattr(base, name)

# Avoid importing the full original package at import time to keep dependencies
# optional.  ``__all__`` is therefore left empty and modules are loaded lazily
# via ``__getattr__`` when accessed.
__all__ = []
