"""
Name: Viren Mody
Author Code Number: 1140M
Class: CS 342, Fall 2016
Professor: Dale Reed
System: Windows 10/Raspbian - nano

Program: #5, IoT
Due: 11/28/2016 11:59 PM

Program Description:
Implement an Internet of Things (IoT) application that:
1) Must solve some problem or make your life easier.
2) Must communicate with sensors in the real world to gather input, do 
	some transformation on it, and have some sort of output. Please 
	check with me if your design deviates from this.
3) Must include an IoT device that is under your control, not belonging
	to someone else on the Internet.
	
Flood Detector
1) Two water sensors detect water and are caught by event detectors
2) When first water sensor is hit, sends a text by pushbullet
3) When second is hit, sends a text containing rate of water increase
and time before flooding.
"""
# Import Libraries: GPIO for water signal, time for sleep and rate calc.
import RPi.GPIO as GPIO 
import time 
import sys


# Import Libraries: Alerts/Notification by pushbullet and/or email
from pushbullet import Pushbullet
import smtplib 

# Grant program access to Pushbullet API with access token/api key
api_key = "o.neuSwv477vbxuVyrZ23ac8QBO9tFRaKF"
pb = Pushbullet(api_key)

# flag for graceful exit
exitFlag = 0

# globals variables for water increase rate
sensorDistance1 = 0
sensorDistance2 = 0
distanceBetweenSensors = 0
startTime = 0

# Alert Messages
initialAlert = 'Flood Alert! Water level has exceeded sump pump!'
secondAlert = """Flood Alert! 
Water level is {0} inches from the top of the pit and is rising at a rate of {1:.2f} inches/second.
At this rate, water will begin flooding in {2:.2f} seconds"""

# WATER SENSOR SIGNAL CHANNELS
FIRST = 17
SECOND = 22

# LED CHANNELS
GREEN = 5
YELLOW = 6
RED = 13


# Main Function - for ease of readability
def main():
	# Welcome and prompt user for information
	print "Welcome to FloodDetector!"
	global sensorDistance1
	sensorDistance1 = input('Enter in the distance(inches) from the first/lower water sensor to the top of the sump pump pit:')
	global sensorDistance2
	sensorDistance2 = input('Enter in the distance(inches) from the second/higher water sensor to the top of the sump pump pit:')
	global distanceBetweenSensors
	distanceBetweenSensors = sensorDistance1 - sensorDistance2
	print('System Ready: Water Sensors Active...')

	# Reference GPIO Pins by Broadcom SOC Channel
	GPIO.setmode(GPIO.BCM)
	#GPIO.setwarnings(False)
	
	# Setup LED Channels as Output
	GPIO.setup(GREEN, GPIO.OUT)
	GPIO.setup(YELLOW, GPIO.OUT)
	GPIO.setup(RED, GPIO.OUT)
	
	# Initiate GREEN = NO FLOODING LED
	GPIO.output(GREEN, GPIO.HIGH)

	# Setup GPIO Channel/Pins to receive digital INPUT from water sensors
	# and add Event Detection for both sensors both rising and falling
	waterSensorPins = [FIRST, SECOND] 		# I may add 3rd water sensor later
	for channel in waterSensorPins:
		GPIO.setup(channel, GPIO.IN)
		#GPIO.add_event_detect(channel, GPIO.RISING, callback = handleFloodSignal1) 
		#GPIO.add_event_detect(channel, GPIO.BOTH, callback = handleFloodSignal, bouncetime=500) 

	GPIO.add_event_detect(FIRST, GPIO.RISING, callback = handleFloodSignal1) 
	GPIO.add_event_detect(SECOND, GPIO.RISING, callback = handleFloodSignal2) 

	# Force wait for first detection of water to cut down CPU usage
	#GPIO.wait_for_edge(waterSensorPins[0], GPIO.RISING)
		
	# Enter infinite loop after first detection of water
		# Sleep for 5 seconds at a time to cut down CPU usage
		# Wait for events and act accordingly in sendTextAlert
	while True:
		time.sleep(0.1)
		if exitFlag == 1:
			sys.exit()



# This method is called on a detected event:
	# Rise or Fall of either water sensor
def handleFloodSignal1(sensor):  
	global startTime
	startTime = time.time()
	print startTime
	print "WARNING: First Sensor Detecting Flood!"
	ledWarning(1)
	sendTextAlert(initialAlert)
##	else: print "First: Phew - no flooding."

def handleFloodSignal2(sensor):
	print "WARNING: Second Sensor Detecting Flood!"
	elapsedTime = time.time() - startTime
	rate = distanceBetweenSensors/elapsedTime
	timeBeforeFlooding = sensorDistance2/rate
	ledWarning(2)
	nextAlert = secondAlert.format(distanceBetweenSensors,rate,timeBeforeFlooding)
	print(nextAlert)
	sendTextAlert(nextAlert)
	cleanUpAndExit()
##	else: print "Second: Phew - no flooding."	

def ledWarning(count):
	if count == 1:
		GPIO.output(GREEN, GPIO.LOW)
		GPIO.output(YELLOW, GPIO.HIGH)
	elif count == 2:
		GPIO.output(YELLOW, GPIO.LOW)
		for i in range(1,25):
			GPIO.output(RED, GPIO.HIGH)
			time.sleep(0.2)
			GPIO.output(RED, GPIO.LOW)
			time.sleep(0.2)		
			
def sendTextAlert(message):
	push = pb.push_note("WARNING: ", message)

def cleanUpAndExit():
	GPIO.cleanup()
	global exitFlag
	exitFlag = 1

#
# Executable Code Starts Here
#
main()
