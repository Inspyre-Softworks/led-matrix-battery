from led_matrix_battery.led_matrix.display.grid.grid import *  # noqa: F401,F403
from led_matrix_battery.led_matrix.helpers import load_from_file as _load_from_file


# Override Grid.from_spec to infer width and height from the provided spec so the
# behaviour is consistent when the matrix dimensions differ.
_orig_from_spec = Grid.from_spec

@classmethod
def _from_spec(cls, spec):
    width = len(spec)
    height = len(spec[0]) if width else 0
    return cls(width=width, height=height, init_grid=spec)

Grid.from_spec = _from_spec

# Export helper so tests can monkeypatch it
load_from_file = _load_from_file

_orig_from_file = Grid.from_file

@classmethod
def _from_file(cls, filename, frame_number=0, height=MATRIX_HEIGHT, width=MATRIX_WIDTH):
    raw = load_from_file(str(filename))
    if isinstance(raw, list) and raw and isinstance(raw[0], list):
        grid_data = raw
    elif isinstance(raw, list) and all(isinstance(f, dict) for f in raw):
        frame = raw[frame_number]
        grid_data = frame.get('grid')
        if not isinstance(grid_data, list):
            raise ValueError(f"Frame {frame_number} missing 'grid' list")
    else:
        raise ValueError("Unsupported file structure for grid data.")

    # Use the is_valid_grid attribute from this module so tests can patch it
    if not globals()['is_valid_grid'](grid_data, width, height):
        raise ValueError(f"Loaded grid is not {width}×{height} column-major 0/1 list")

    return cls(width=width, height=height, init_grid=grid_data)

Grid.from_file = _from_file
