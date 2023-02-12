# person-sensor-circuitpython
CircuitPython driver for the [Person Sensor](https://usefulsensors.com/person-sensor/) by Useful Sensors.

## Basic Usage

1. Copy `person_sensor.py` into the `lib` folder on your CircuitPython device.

2. From the (Adafruit CircuitPython library bundle)[https://circuitpython.org/libraries], 
copy `adafruit_ticks.mpy` into the `lib` folder on your CircuitPython device.

3. In your code, initialize a `busio.I2C` instance (and make sure it's the one your Person Sensor is wired too!):

```python
import busio
import board


# if your board has a stemma/qt connector
i2c = board.STEMMA_I2C()

# alternatively, if you're using the SDA/SCL pins:
# i2c = busio.I2C(board.SCL, board.SDA)
```

4. Initialize a `PersonSensor` instance:

```python
from person_sensor import PersonSensor

person_sensor = PersonSensor(i2c)
```

5. Query the Person Sensor for detected faces:

```python
while True:
    faces = person_sensor.get_faces()
    print(faces)
```

## Resources

* [Official Device Docs](https://github.com/usefulsensors/person_sensor_docs)
    * (Note that this repo is currently up to date with [commit e03b5c9](https://github.com/usefulsensors/person_sensor_docs/tree/e03b5c9ef691d0dcbd03f1d02af68db1d567e919))
* [Official CircuitPython Examples](https://github.com/usefulsensors/person_sensor_circuit_python)
* [Alternative Library Implementation](https://github.com/robotastic/CircuitPython_UsefulSensors_PersonDetector) by robotastic
