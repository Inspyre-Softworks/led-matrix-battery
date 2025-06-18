"""Power monitor functionality split from the original project."""

from importlib import import_module
import sys

_SUBMODULES = [
    'events',
    'errors',
    'gui',
    'helpers',
    'monitor',
]

def __getattr__(name):
    if name in _SUBMODULES:
        module = import_module(f'led_matrix_battery.monitor.{name}')
        sys.modules[f'{__name__}.{name}'] = module
        return module
    base = import_module('led_matrix_battery.monitor')
    return getattr(base, name)

# Avoid importing the full original package here. Attributes are loaded lazily
# on access through ``__getattr__``.
__all__ = []
