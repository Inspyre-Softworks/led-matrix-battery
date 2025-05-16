from .layout import Layout as MainWindowLayout
from ..base import WindowBase
from ...event.collection import EventCollection
from led_matrix_battery.inputmodule.ledmatrix import brightness
from led_matrix_battery.led_matrix.helpers.device import DEVICES
import time


class MainWindow(WindowBase):
    """
    Main window for the LED Matrix Battery Monitor GUI.
    """
    DEFAULT_TITLE = 'LED Matrix Battery Monitor'
    LAYOUT        = MainWindowLayout()

    def __init__(
            self,
            *args,
            **kwargs
    ):
        if not args and 'title' not in kwargs:
            args = (MainWindow.DEFAULT_TITLE, *args)
        super().__init__(*args, **kwargs)

    def __post_build__(self):
        slider_elem = self.window.find_element('BRIGHTNESS_SLIDER')
        slider_elem.bind(
            '<ButtonRelease-1>',
            lambda event, s=slider_elem: self.window.write_event_value('BRIGHTNESS_SLIDER_DONE', s.get())
        )

    @property
    def EVENT_COLLECTION(self):
        return EventCollection(self)

    def build_event_handlers(self):
        self.EVENT_COLLECTION.create_event(None, self.stop)

    def handle_event(self, event, *args, **kwargs):
        pass

    def run(self):
        if not self.built:
            raise RuntimeError('Window is not built. Call build() first.')

        if not self.running:
            raise RuntimeError('Window is not running. Call start() first.')

        DEBOUNCE_DELAY = 0.3
        last_change = 0
        pending_value = None

        while self.running:
            event, values = self.window.read(timeout=100)
            #print(values)

            if event == 'BRIGHTNESS_SLIDER':
                # record the latest value and timestamp
                pending_value = int(values['BRIGHTNESS_SLIDER'])
                last_change = time.time()

                # if we've got a pending value and it's been quiet for DEBOUNCE_DELAY, apply it
            if pending_value is not None and time.time() - last_change > DEBOUNCE_DELAY:
                brightness(DEVICES[0], pending_value)
                pending_value = None
            if event is None:
                break
