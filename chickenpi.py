#!/usr/bin/python

###### IMPORT STATEMENTS ######
# Import all required functions/libraries
import RPi.GPIO as GPIO
import time
import signal
import sys
import json
import urllib2
import os
import Adafruit_DHT
import smbus
import struct
from requests_toolbelt import MultipartEncoder
import requests
from time import gmtime, strftime


###### VARIABLES ######
# Define script-level variables
# Define GPIO pin variables
MOTOR_PIN_1 = 15
MOTOR_PIN_2 = 18
HALL_TOP_PIN = 16
HALL_BOTTOM_PIN = 40
DHT_GPIO = 17
LDR_PIN = 12
IRLED_PIN = 37
# Temp directory location
TEMP_DIR = "/chickenpi/tmp/"
# Log directory location
LOG_DIR = "/chickenpi/log/"
# Image directory location
IMG_DIR = "/chickenpi/images/"
# Log file location
LOG_FILE = LOG_DIR + "chickenpi-" + strftime("%Y%m%d%H%M%S", gmtime()) + ".log"
# Lock file location
LOCK_FILE = TEMP_DIR + "chickenpi.lock"
# Door timer
DOOR_TIMER = 75
# Closing finish delay
DOOR_CLOSE_DELAY = 1
# ARDUINO I2C ADDRESS
I2C_ADDRESS = 0x04
# Spark variables
SPARK_ACCESS_TOKEN = "<TO BE COMPLETED>"
SPARK_ROOM_ID = "<TO BE COMPLETED>"
# Logging
LOGGING = "yes"


###### FUNCTION DEFINITIONS ######
# Setup GPIO board/pins function
def Setup_GPIO():
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(MOTOR_PIN_1,GPIO.OUT)
        GPIO.setup(MOTOR_PIN_2,GPIO.OUT)
        GPIO.output(MOTOR_PIN_1,False)
        GPIO.output(MOTOR_PIN_2,False)
        GPIO.setup(IRLED_PIN,GPIO.OUT)
        GPIO.output(IRLED_PIN,False)
        GPIO.setup(HALL_TOP_PIN,GPIO.IN)
        GPIO.setup(HALL_BOTTOM_PIN,GPIO.IN)

# Stop the motor
def Motor_Stop():
        GPIO.output(MOTOR_PIN_1,False)
        GPIO.output(MOTOR_PIN_2,False)

# Clean exit function (Stops Motor, cleans GPIO)
def Cleanup_Exit():
        Motor_Stop()
        GPIO.cleanup()
        if os.path.isfile(LOCK_FILE):
                os.remove(LOCK_FILE)
        sys.exit(0)

# Post message to Spark
def Spark_Message(message):
        data = {"roomId": SPARK_ROOM_ID, "text": message}
        url = "https://api.ciscospark.com/v1/messages"
        request = urllib2.Request(url, json.dumps(data), headers={"Accept" : "application/json", "Content-Type" : "application/json"})
        request.add_header("Authorization", "Bearer " + SPARK_ACCESS_TOKEN)
        contents = urllib2.urlopen(request).read()

# Post file to Spark
def Spark_File(filepath, filetype):
        filebase, filename = os.path.split(filepath)
        my_fields={'roomId': SPARK_ROOM_ID, 'text': '', 'files': (filename, open(filepath, 'rb'), filetype)}
        url = "https://api.ciscospark.com/v1/messages"
        m = MultipartEncoder(fields=my_fields)
        r = requests.post(url, data=m, headers={'Content-Type': m.content_type, 'Authorization': 'Bearer ' + SPARK_ACCESS_TOKEN})

# Write command/data to Arduino
def I2C_Write_Data(value):
        I2C_BUS.write_byte(I2C_ADDRESS, value)
        return -1

# Read result from Arduino
def I2C_Read_Data():
        return I2C_BUS.read_i2c_block_data(I2C_ADDRESS, 0);

# Convert data to float
def Get_Float(data, index):
        bytes = data[4*index:(index+1)*4]
        return struct.unpack('f', "".join(map(chr, bytes)))[0]

# Get image from camera and post to Spark or simply save and return image filename
def Get_Camera(retimage=None):
        GPIO.output(IRLED_PIN,True)
        cameraimage = IMG_DIR + "chickenpi-" + strftime("%Y%m%d%H%M%S", gmtime()) + ".jpg"
        cameracmd = "/usr/bin/raspistill -w 600 -h 600 -o " + cameraimage
        os.system(cameracmd)
        GPIO.output(IRLED_PIN,False)
        if retimage is None:
                Spark_File(cameraimage, "image/jpg")
                if os.path.isfile(cameraimage):
                        os.remove(cameraimage)
        else:
                return cameraimage

# Write to log file
def Log_Message(message):
        if LOGGING == "yes":
                logfile = open(LOG_FILE, "a")
                logfile.write(message)
                logfile.close()


###### START OF MAIN CODE ######
try:
        # Check command line arguments
        if len(sys.argv) < 2:
                print "Too few arguments."
                print "Options:"
                print "\topen"
                print "\tclose"
                print "\tstatus"
                print "\ttemperature"
                print "\thumidity"
                print "\toutside"
                print "\tlight"
                print "\thalltop"
                print "\thallbottom"
                print "\tcamera"
                print "\tcamcap"
                sys.exit(0)
        if len(sys.argv) > 3:
                print "Too many arguments."
                print "Options:"
                print "\topen"
                print "\tclose"
                print "\tstatus"
                print "\ttemperature"
                print "\thumidity"
                print "\toutside"
                print "\tlight"
                print "\thalltop"
                print "\thallbottom"
                print "\tcamera"
                print "\tcamcap"
                sys.exit(0)

        # Set action from command line argument
        if sys.argv[1] == "open":
                ACTION = "open"
        elif sys.argv[1] == "close":
                ACTION = "close"
        elif sys.argv[1] == "status":
                ACTION = "status"
        elif sys.argv[1] == "temperature":
                ACTION = "temperature"
        elif sys.argv[1] == "humidity":
                ACTION = "humidity"
        elif sys.argv[1] == "outside":
                ACTION = "outside"
        elif sys.argv[1] == "light":
                ACTION = "light"
        elif sys.argv[1] == "halltop":
                ACTION = "halltop"
        elif sys.argv[1] == "hallbottom":
                ACTION = "hallbottom"
        elif sys.argv[1] == "camera":
                ACTION = "camera"
        elif sys.argv[1] == "camcap":
                ACTION = "camcap"
        else:
                print "Invalid argument specified";
                sys.exit(0)

        if len(sys.argv) == 3:
                if sys.argv[2] == "nolog":
                        LOGGING = "no"

        # First check if an instance of script is already running
        if os.path.isfile(LOCK_FILE):
                print LOCK_FILE + " exists, instance already seems to be running!  Trying again in 5 seconds."
                Log_Message(LOCK_FILE + " exists, instance already seems to be running!  Trying again in 5 seconds.")
                time.sleep(5)

        # Second check if an instance of script is already running
        if os.path.isfile(LOCK_FILE):
                print LOCK_FILE + " exists, instance already seems to be running!  Exiting"
                Log_Message(LOCK_FILE + " exists, instance already seems to be running!  Exiting")
                sys.exit(0)

        # Create lock file
        lockfile = open(LOCK_FILE, "w")
        lockfile.write("chickenpi")
        lockfile.close()


        ### MAIN DOOR FUNCTION ###

        # Setup GPIO
        Setup_GPIO()

        # Check status of door
        if ACTION == "status":
                # Check current door status from Hall Effect sensors
                HALL_TOP=GPIO.input(HALL_TOP_PIN)
                HALL_BOTTOM=GPIO.input(HALL_BOTTOM_PIN)
                if HALL_TOP == 0:
                        print "DOOR STATUS:  OPEN"
                elif HALL_BOTTOM == 0:
                        print "DOOR STATUS:  CLOSED"
                elif HALL_TOP == 1 and HALL_BOTTOM == 1:
                        print "DOOR STATUS:  JAMMED"
                # It should never get here
                else:
                        print "DOOR STATUS:  UNKNOWN"
        # Open door
        elif ACTION == "open":
                # Check current door status from Hall Effect sensors
                HALL_TOP=GPIO.input(HALL_TOP_PIN)
                HALL_BOTTOM=GPIO.input(HALL_BOTTOM_PIN)
                # Start the timer
                TIME_START=time.clock()
                RUN_TIME=0
                print "Opening door"
                while HALL_TOP == 1 and RUN_TIME < DOOR_TIMER:
                        GPIO.output(MOTOR_PIN_1, True)
                        GPIO.output(MOTOR_PIN_2, False)
                        HALL_TOP = GPIO.input(HALL_TOP_PIN)
                        RUN_TIME = time.clock() - TIME_START
                if RUN_TIME >= DOOR_TIMER:
                        Motor_Stop()
                        RUN_TIME = time.clock() - TIME_START
                        Get_Camera()
                        sparkmessage = "ChickenPi:  Something went wrong with door opening! (Run time: {0:0.0f} seconds)".format(RUN_TIME)
                        Spark_Message(sparkmessage)
                        print sparkmessage
#                       Cleanup_Exit()
                if HALL_TOP == 0:
                        Motor_Stop()
                        RUN_TIME = time.clock() - TIME_START
                        Get_Camera()
                        sparkmessage = "ChickenPi:  The door is open! (Run time: {0:0.0f} seconds)".format(RUN_TIME)
                        Spark_Message(sparkmessage)
                        print sparkmessage
#                       Cleanup_Exit()
        # Close door
        elif ACTION == "close":
                # Check current door status from Hall Effect sensors
                HALL_TOP=GPIO.input(HALL_TOP_PIN)
                HALL_BOTTOM=GPIO.input(HALL_BOTTOM_PIN)
                # Start the timer
                TIME_START=time.clock()
                RUN_TIME=0
                print "Closing door"
                while HALL_BOTTOM == 1 and RUN_TIME < DOOR_TIMER:
                        GPIO.output(MOTOR_PIN_2, True)
                        GPIO.output(MOTOR_PIN_1, False)
                        HALL_BOTTOM = GPIO.input(HALL_BOTTOM_PIN)
                        RUN_TIME = time.clock() - TIME_START
                if RUN_TIME >= DOOR_TIMER:
                        Motor_Stop()
                        RUN_TIME = time.clock() - TIME_START
                        Get_Camera()
                        sparkmessage = "ChickenPi:  Something went wrong with door closing! (Run time: {0:0.0f} seconds)".format(RUN_TIME)
                        Spark_Message(sparkmessage)
                        print sparkmessage
#                       Cleanup_Exit()
                if HALL_BOTTOM == 0:
                        time.sleep(DOOR_CLOSE_DELAY)
                        Motor_Stop()
                        RUN_TIME = time.clock() - TIME_START
                        Get_Camera()
                        sparkmessage = "ChickenPi:  The door is closed! (Run time: {0:0.0f} seconds)".format(RUN_TIME)
                        Spark_Message(sparkmessage)
                        print sparkmessage
#                       Cleanup_Exit()
        # Check inside temperature (DHT22)
        elif ACTION == "temperature":
                humidity, temperature = Adafruit_DHT.read_retry(22, DHT_GPIO)
                print 'Inside temperature: {0:0.2f}'.format(temperature)
        # Check inside humidity (DHT22)
        elif ACTION == "humidity":
                humidity, temperature = Adafruit_DHT.read_retry(22, DHT_GPIO)
                print 'Inside humidity: {0:0.0f}'.format(humidity)
        # Check outside temperature (DS18B20 via Arduino)
        elif ACTION == "outside":
                I2C_BUS = smbus.SMBus(1)
                I2C_Write_Data(1)
                time.sleep(1)
                data = I2C_Read_Data()
                sensor = Get_Float(data, 0)
                reading = Get_Float(data, 1)
                print("Outside temperature: {0:.2f}".format(round(reading,2)))
        # Check light level
        elif ACTION == "light":
                ldr_count = 0
                GPIO.setup(LDR_PIN, GPIO.OUT)
                GPIO.output(LDR_PIN, GPIO.LOW)
                time.sleep(0.1)
                GPIO.setup(LDR_PIN, GPIO.IN)
                while (GPIO.input(LDR_PIN) == GPIO.LOW):
                        time.sleep(0.001)
                        ldr_count += 1
                        if ldr_count >= 10000:
                                break
                print 'Light sensor: {0:0.0f}'.format(ldr_count)
        # Check top hall effect sensor
        elif ACTION == "halltop":
                HALL_TOP=GPIO.input(HALL_TOP_PIN)
                print "Top hall effect sensor: " + str(HALL_TOP)
        # Check bottom hall effect sensor
        elif ACTION == "hallbottom":
                HALL_BOTTOM=GPIO.input(HALL_BOTTOM_PIN)
                print "Bottom hall effect sensor: " + str(HALL_BOTTOM)
        elif ACTION == "camera":
                Get_Camera()
                print "Camera image sent"
        elif ACTION == "camcap":
                imgfile = Get_Camera(1)
                print "Image: " + imgfile
        # It should never get to this 'else' statement
        else:
                print "UNKNOWN ACTION!!!"

except KeyboardInterrupt:
        Cleanup_Exit()

except:
        Cleanup_Exit()

# Finally, safely shutdown
finally:
        Cleanup_Exit()
