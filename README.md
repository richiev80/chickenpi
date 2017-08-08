# chickenpi

An automated chicken coop door.  At the core, it's a Raspberry Pi Zero W interfacing to some Hall Effect sensors and a DC motor for door open and close automation, but for extra functionality has other components and/or sensors for chicken coop monitoring:

- Temperature & Humidity sensors
- Raspberry Pi NoIR Camera
- Light Dependent Resistor
- IR LED light
- Arduino Uno

It is also "connected" to the [Cisco Spark](https://www.ciscospark.com/) platform for monitoring/reporting as well as remote control.

#### Credit
Credit goes to Eric Escobar for the original idea.  See here for more: http://www.quickanddirtytips.com/tech/gadgets/how-to-automate-your-home-chicken-door-edition

### Components

Following is a list of components used for ChickenPi:

- 1 x Raspberry Pi Zero W
- 1 x Raspberry Pi NoIR Camera
- 1 x Arduino Uno R3
- 1 x 12V DC 10RPM Reversible High Torque Turbo Worm Geared Motor (JGY370)
- 1 x L298N Dual H Bridge DC Stepper Motor Driver Controller Board Module
- 2 x OH137 Hall Effect Unipolar Sensor
- 1 x AM2302 Temperature & Humidity Sensor
- 1 x DS18B20 Waterproof Temperature Sensor
- 1 x Light Dependent Resistor
- 1 x 48 LED IR Light
- 1 x 1uF Capacitor
- 2 x 10k Ohm Resistor
- 2 x 4.7k Ohm Resistor

As well as the above there was also some breadboards, jumper cables, and screw terminal blocks used.

### Hardware Design

_This section is not yet complete and requires validation_

#### GPIO Pins

The Raspberry Pi Zero W has a 40-pin header that offers 17 GPIO pins, which are used by most of the sensors/components for ChickenPi.
There are also 2 i2c pins which are used for connection to the Arduino, which is required for the DS18B20 sensor.

_Note:  The reason for the Arduino is that the DS18B20 sensor seems to cause the Raspberry Pi to lock up after approx. 24hours of operation, requiring a power cycle to restore operation._

Following is the GPIO pin setup:

- Pin 11 (GPIO 17) = AM2302
- Pin 12 (GPIO 18) = LDR
- Pin 15 (GPIO 22) = Motor Controller Pin #1
- Pin 16 (GPIO 23) = Hall Effect Sensor Top
- Pin 18 (GPIO 24) = Motor Controller Pin #2
- Pin 37 (GPIO 26) = Motor Controller Pin #3
- Pin 40 (GPIO 21) = Hall Effect Sensor Bottom

Following is the i2c pin setup:

- Pin 3 (GPIO 2) = Arduino Pin 4 (SDA)
- Pin 5 (GPIO 3) = Arduino Pin 5 (SCL)

### Usage

Following are the command line options for chickenpi.

#### open

Open chicken coop door and send notification, along with camera image, to Cisco Spark room.  The camera image is sent to provide a visual indication of the status of the door upon completion of opening (in case it gets jammed).

```
python chickenpi.py open
```

#### close

Close chicken coop door and send notification, along with camera image, to Cisco Spark room.  The camera image is sent to provide a visual indication of the status of the door upon completion of closing (in case it gets jammed).

```
python chickenpi.py close
```

#### status

Check the status of the chicken coop door and return result:  OPEN, CLOSED, JAMMED, UNKNOWN.

```
python chickenpi.py status
```

#### temperature

Fetch the temperature from the DHT22/AM2302 temperature/humidity sensor and return result.

```
python chickenpi.py temperature
```

#### humidity

Fetch the humidity from the DHT22/AM2302 temperature/humidity sensor and return result.

```
python chickenpi.py humidity
```

#### outside

Fetch the temperature from the DS18B20 (via Arduino) temperature sensor and return result.

```
python chickenpi.py outside
```

#### light

Fetch the light reading from the light dependant resistor and return result.

```
python chickenpi.py light
```

_Note:  The reading from the LDR is simply a time value instead of a direct lux value, and is capped at 10 seconds._

#### halltop

Fetch the reading from the hall effect sensor at the top of the door slot and return result.

```
python chickenpi.py halltop
```

#### hallbottom

Fetch the reading from the hall effect sensor at the bottom of the door slot and return result.

```
python chickenpi.py hallbottom
```

#### camera

Capture the image from the camera and post image to Cisco Spark room.

```
python chickenpi.py camera
```

_Note:  After posting to Cisco Spark, the image file is deleted._

#### camcap

Capture the image from the camera and return the image file name.

```
python chickenpi.py camcap
```

_Note:  The image file is stored on the raspberry pi until manual deletion_


### Variables

Some variables in the script need to be modified.

**TEMP_DIR** - Directory to store temporary files

**LOG_DIR** - Directory to store log files

**IMG_DIR** - Directory to store images captured from Raspberry Pi NoIR Camera

**DOOR_TIMER** - Maximum time in seconds that the door operation should run.  _This is a failsafe for the open/close operation_

**DOOR_CLOSE_DELAY** - This is a coded delay to keep running the close operation after the hall effect sensor detects the door magnet

**SPARK_ACCESS_TOKEN** - Cisco Spark access token

**SPARK_ROOM_ID** - Cisco Spark room ID

**LOGGING** - Yes/No to enable/disable logging


### References

The following are reference URLs:

http://www.quickanddirtytips.com/tech/gadgets/how-to-automate-your-home-chicken-door-edition

https://oscarliang.com/raspberry-pi-arduino-connected-i2c/

