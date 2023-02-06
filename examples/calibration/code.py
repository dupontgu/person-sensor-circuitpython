"""
`Person Sensor - Face ID Example`
=================================

Required Hardware:
This script assumes you are using a dev board with
- a built-in STEMMA/QT port for I2C (hooked up to Person Sensor)
- a built-in Neopixel
- 3 momentary buttons/switches hooked to pins A0, A1, and A2 and ground

Usage:
This script continuously polls the Person Sensor for detected faces.
It will print out the full details for any unidentified faces.
If you click one of the buttons (0-2) while a face is in frame, it will tell the Person Sensor to apply that ID (0-2)
to that person moving forward.
After the ID's have been assigned to inidividual faces, the Neopixel should indicate if a given person is in frame.
The red component of the LED will light up if person 0 is in frame, green for person 1, blue for person 2.
There is some artificial "hysteresis" applied to reduce flickering.

PLEASE NOTE THAT YOUR MILEAGE MAY VARY WITH THE ID FEATURE!
Takes some trial and error. Accuracy appears to improve if you ID 2+ unique faces.
"""

import array
import pulseio
import board
from digitalio import DigitalInOut, Direction, Pull
import neopixel
from person_sensor import PersonSensor, MODE_CONTINUOUS, PERSON_SENSOR_NUM_IDS
from calibrate_button import CalibrateButton
import time

# Hysteresis setttings
MAX_CONSECUTIVE_IDS = 10
FOUND_THRESHOLD = MAX_CONSECUTIVE_IDS - 3
LOST_THRESHOLD = MAX_CONSECUTIVE_IDS - FOUND_THRESHOLD

# Can adjust this as needed, though I find lower than 95ish allows false positives through
CONFIDENCE_THRESHOLD = 96

# keep track of repeated IDs
id_tallys = [0 for _ in range(PERSON_SENSOR_NUM_IDS)]

# keep track of which IDs are currently detected (with hysteresis applied)
currently_present = [False for _ in range(PERSON_SENSOR_NUM_IDS)]

pix_color = [0, 0, 0]
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.8, auto_write=True)

i2c = board.STEMMA_I2C()

person_sensor = PersonSensor(i2c)
person_sensor.set_mode(MODE_CONTINUOUS)
person_sensor.enable_id(True)

calibrate_buttons = [board.A0, board.A1, board.A2]
for i, pin in enumerate(calibrate_buttons):
    calibrate_buttons[i] = CalibrateButton(person_sensor, i, pin)

while True:
    for button in calibrate_buttons:
        button.tick()
    faces = person_sensor.get_faces()
    found_faces = [False for _ in range(PERSON_SENSOR_NUM_IDS)]
    for f in faces:
        if f.id >= 0 and f.id_confidence > CONFIDENCE_THRESHOLD:
            found_faces[f.id] = True
        else:
            print("un-id'ed face: ", f)
    for i, b in enumerate(found_faces):
        tally_change = 1 if b else -1
        new_tally = max(0, min(id_tallys[i] + tally_change, MAX_CONSECUTIVE_IDS))
        if new_tally == FOUND_THRESHOLD and not currently_present[i]:
            currently_present[i] = True
            print("id emerged:", i)
        elif new_tally == LOST_THRESHOLD and currently_present[i]:
            currently_present[i] = False
            print("id gone:", i)
        id_tallys[i] = new_tally
    pix_color[0] = 255 if currently_present[0] else 0
    pix_color[1] = 255 if currently_present[1] else 0
    pix_color[2] = 255 if currently_present[2] else 0
    pixel[0] = pix_color
    print(id_tallys, time.time())