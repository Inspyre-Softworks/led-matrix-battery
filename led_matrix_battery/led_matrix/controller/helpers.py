from time import sleep

def keep_image(controller, breathe=False, breathe_fps=30, interval=0.1, time_between_refreshes=50):

    brightness = controller.brightness
    while controller.keep_image:
        if breathe:
        controller.set_brightness(brightness)



