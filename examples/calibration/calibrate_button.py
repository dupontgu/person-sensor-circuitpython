"""
Helper class for a simple button to trigger calibration for a person sensor.
You can put this at the root of your CIRCUITPY drive, or in the lib folder.
"""

from digitalio import DigitalInOut, Direction, Pull

class CalibrateButton:
    def __init__(self, person_sensor, person_id, gpio_pin):
        self.pressed = False
        self.person_sensor = person_sensor
        self.person_id = person_id
        self.pin = DigitalInOut(gpio_pin)
        self.pin.direction = Direction.INPUT
        self.pin.pull = Pull.UP
    
    def tick(self):
        currently_pressed = not self.pin.value
        if currently_pressed and not self.pressed:
            self.pressed = True
            print("calibrating for id:", self.person_id)
            self.person_sensor.label_next_id(self.person_id)
        elif not currently_pressed and self.pressed:
            self.pressed = False
