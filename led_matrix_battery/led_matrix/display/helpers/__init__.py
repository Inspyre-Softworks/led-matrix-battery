import time
import math


def keep_image(
    controller,
    breathe: bool = False,
    breathe_fps: float = 30,
    interval: float = 0.1,
    time_between_refreshes: float = 50
):
    """
    Continuously hold the current image on-screen, optionally breathing the brightness.

    Args:
        controller: an LEDMatrixController-like object with:
            - .brightness (0-100)
            - .keep_image (bool flag you can set to False to exit)
            - .draw_grid(grid) or .render_current() to re-send the image
            - .set_brightness(value)
        breathe: if True, oscillate brightness in a sinusoidal “breathing” pattern
        breathe_fps: how many brightness steps per second when breathing
        interval: seconds between each brightness step (if breathing)
        time_between_refreshes: seconds to sleep after one full breath cycle
                                 (or between redraws if not breathing)
    """
    base_brightness = controller.brightness
    t = 0.0
    period = 1.0  # one full sine cycle = 1 second
    step = 1.0 / breathe_fps

    while controller.keep_image:
        if breathe:
            # Compute a smooth sine-based oscillation from 0→1→0
            phase = (t % period) / period            # 0.0→1.0
            fade = 0.5 * (1 - math.cos(2 * math.pi * phase))
            bri = int(round(base_brightness * fade))
            controller.set_brightness(bri)
            time.sleep(interval)
            t += interval
        else:
            # just hold at base brightness
            controller.set_brightness(base_brightness)
            time.sleep(time_between_refreshes)

        # re-draw the current image (whatever the controller is holding)
        # assume controller.draw_current() or similar:
        try:
            controller.render_current()
        except AttributeError:
            # fallback to a generic draw call
            controller.draw()
