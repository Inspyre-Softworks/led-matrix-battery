from __future__ import annotations

"""LED matrix aware progress bars."""

from typing import Optional, Any, Iterable

from tqdm import tqdm as _tqdm

try:
    from led_matrix_battery.led_matrix.helpers.device import DEVICES
    from led_matrix_battery.led_matrix.controller.controller import LEDMatrixController
except Exception:  # pragma: no cover - dependency issues
    DEVICES = []
    LEDMatrixController = None  # type: ignore


class LEDTqdm(_tqdm):
    """A ``tqdm`` subclass that also renders progress on an LED matrix."""

    def __init__(self, *args: Any, use_led: bool = True, matrix: Optional[Any] = None,
                 **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._matrix = None
        if use_led:
            self._matrix = self._init_matrix(matrix)
        self._last_percent = -1

    @staticmethod
    def _init_matrix(matrix: Optional[Any]):
        if matrix is not None:
            if isinstance(matrix, LEDMatrixController):
                return matrix
            try:
                return LEDMatrixController(matrix, 100)
            except Exception:
                return None
        if DEVICES:
            try:
                return LEDMatrixController(DEVICES[0], 100)
            except Exception:
                return None
        return None

    def _render_led(self) -> None:
        if not self._matrix or not self.total:
            return
        percent = int(self.n / self.total * 100)
        if percent != self._last_percent:
            try:
                self._matrix.draw_percentage(percent)
            except Exception:
                # Ignore hardware errors in progress display
                pass
            self._last_percent = percent

    def update(self, n: int = 1) -> None:  # type: ignore[override]
        super().update(n)
        self._render_led()


def tqdm(iterable: Optional[Iterable[Any]] = None, *args: Any, **kwargs: Any):
    """Return an :class:`LEDTqdm` instance like ``tqdm.tqdm``."""
    return LEDTqdm(iterable, *args, **kwargs)
