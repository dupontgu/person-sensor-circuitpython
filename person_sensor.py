import time, struct
from micropython import const
from collections import namedtuple
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_ticks import ticks_ms

# Constants/struct formatting data from official CircuitPython examples:
# https://github.com/usefulsensors/person_sensor_circuit_python
PERSON_SENSOR_I2C_ADDRESS = const(0x62)
PERSON_SENSOR_I2C_HEADER_FORMAT = "BBH"
PERSON_SENSOR_I2C_HEADER_BYTE_COUNT = struct.calcsize(PERSON_SENSOR_I2C_HEADER_FORMAT)
PERSON_SENSOR_FACE_FORMAT = "BBBBBBbB"
PERSON_SENSOR_FACE_BYTE_COUNT = struct.calcsize(PERSON_SENSOR_FACE_FORMAT)

PERSON_SENSOR_FACE_MAX = 4
PERSON_SENSOR_RESULT_FORMAT = PERSON_SENSOR_I2C_HEADER_FORMAT + \
    "B" + PERSON_SENSOR_FACE_FORMAT * PERSON_SENSOR_FACE_MAX + "H"
PERSON_SENSOR_RESULT_BYTE_COUNT = struct.calcsize(PERSON_SENSOR_RESULT_FORMAT)

# how many unique faces the Person Sensor can try to ID
PERSON_SENSOR_NUM_IDS = const(8)

# minimum amount of time between fresh inferences
PERSON_SENSOR_DELAY = 200 # millis

_REG_ADDR_SET_MODE = const(0x01)
_REG_ADDR_ENABLE_ID = const(0x02)
_REG_ADDR_TRIGGER_SINGLE_SHOT = const(0x03)
_REG_ADDR_LABEL_ID = const(0x04)
_REG_ADDR_PERSIST_IDS = const(0x05)
_REG_ADDR_ERASE_IDS = const(0x06)
_REG_ADDR_DEBUG_MODE = const(0x07)

MODE_STANDBY = const(0x00)
MODE_CONTINUOUS = const(0x01)

_Modes = (MODE_STANDBY, MODE_CONTINUOUS)

PersonSensorFace = namedtuple("Face", ["box_confidence", "box_left", "box_top", "box_right", "box_bottom", "id_confidence", "id", "is_facing"])

class PersonSensor:
    def __init__(self, i2c, auto_delay=True):
        """Initialize a PersonSensor instance that wraps a busio.I2C instance.
        auto_delay -- indicates if this instance should block the minimum recommended 
        time before re-reading face data from the device
        """
        self.auto_delay = auto_delay
        self.i2c = I2CDevice(i2c, PERSON_SENSOR_I2C_ADDRESS)
        self.buffer = None
        self.last_read = ticks_ms()

    def _write(self, data):
        with self.i2c:
            self.i2c.write(data)

    def enable_debug_mode(self, enable):
        """enable (or disable) the indicator LED on the hardware"""
        enable_byte = 0x01 if enable else 0x00
        self._write(bytes([_REG_ADDR_DEBUG_MODE, enable_byte]))

    def enable_id(self, enable):
        """enable (or disable) face identification on the hardware.
        (The device will still report faces, but it will not attempt to assign an ID to each)
        """
        enable_byte = 0x01 if enable else 0x00
        self._write(bytes([_REG_ADDR_ENABLE_ID, enable_byte]))

    def set_mode(self, mode):
        """set the mode on the hardware.

        options are:
        MODE_CONTINUOUS - The hardware will constantly be performing inferences.
        MODE_STANDBY - The hardware will only perform inferences when manually triggered.

        see more:
        https://github.com/usefulsensors/person_sensor_docs#configuration
        """
        if not mode in _Modes:
            raise ValueError("Invalid mode for person sensor")
        self._write(bytes([_REG_ADDR_SET_MODE, mode]))

    def trigger_single_shot(self):
        """From the official docs:
        Trigger a single-shot inference. Only works if the sensor is in standby mode."""
        self._write(bytes([_REG_ADDR_TRIGGER_SINGLE_SHOT, 0x00]))

    def label_next_id(self, id):
        """From the official docs:
        Calibrate the next identified frame as person N, from 0 to 7. If two frames pass with no person, this label is discarded.
        """
        if id < 0 or id >= PERSON_SENSOR_NUM_IDS:
            raise ValueError(f'id must be between 0 and {PERSON_SENSOR_NUM_IDS - 1}')
        self._write(bytes([_REG_ADDR_LABEL_ID, id]))

    def set_persist_ids(self, persist):
        """Tell the hardware whether or not to persist any IDs after the device has been powered off"""
        persist_byte = 0x01 if persist else 0x00
        self._write(bytes([_REG_ADDR_PERSIST_IDS, persist_byte]))

    def erase_ids(self):
        """Erase any IDs that have been labeled using label_next_id"""
        self._write(bytes([_REG_ADDR_ERASE_IDS, 0x00]))
    
    def get_faces(self) -> List[PersonSensorFace]:
        """Query the hardware for the detected faces. Will return a (possibly empty) list of the 
        faces in frame as of the last inference run.
        See https://github.com/usefulsensors/person_sensor_docs#reading-data
        for detailed descriptions of what each property of the PersonSensorFace object represents
        """
        # we have some forced delay time here no matter what, might as well init fresh buffer
        del(self.buffer)
        self.buffer = bytearray(PERSON_SENSOR_RESULT_BYTE_COUNT)

        # if auto_delay is enabled, ensure that at least PERSON_SENSOR_DELAY millis have passed since last reading
        if self.auto_delay:
            now = ticks_ms()
            delta = now - self.last_read
            delay = PERSON_SENSOR_DELAY - delta
            if delta < PERSON_SENSOR_DELAY:
                time.sleep(delay / 1000)
            self.last_read = now + delay
        
        # read the data
        with self.i2c:
            self.i2c.readinto(self.buffer)

        # unpack the data
        offset = 0
        (pad1, pad2, payload_bytes) = struct.unpack_from(PERSON_SENSOR_I2C_HEADER_FORMAT, self.buffer, offset)
        offset = offset + PERSON_SENSOR_I2C_HEADER_BYTE_COUNT

        (num_faces) = struct.unpack_from("B", self.buffer, offset)
        num_faces = int(num_faces[0])
        offset = offset + 1

        faces = []
        for i in range(num_faces):
            face_tuple = struct.unpack_from(PERSON_SENSOR_FACE_FORMAT, self.buffer, offset)
            offset = offset + PERSON_SENSOR_FACE_BYTE_COUNT
            faces.append(PersonSensorFace(*face_tuple))
        
        # should we return this? anybody care?
        checksum = struct.unpack_from("H", self.buffer, offset)
        return faces
