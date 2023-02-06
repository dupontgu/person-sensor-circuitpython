import board
from person_sensor import PersonSensor, MODE_CONTINUOUS


i2c = board.STEMMA_I2C()
# alternatively, if you're using the SDA/SCL pins:
# i2c = busio.I2C(board.SCL, board.SDA)

person_sensor = PersonSensor(i2c)
person_sensor.set_mode(MODE_CONTINUOUS)

while True:
    faces = person_sensor.get_faces()
    if len(faces) > 0:
        # for each face the sensor detects, will print something like:
        # [Face(box_confidence=99, box_left=100, box_top=44, box_right=126, box_bottom=90, id_confidence=97, id=2, is_facing=1)]
        print(faces)