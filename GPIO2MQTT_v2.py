'''
GPIO Pin 13 (Input) Arduino >> Raspberry Pi		[Left Stopper]
GPIO Pin 15 (Input) Arduino >> Raspberry Pi		[Right Stopper]
GPIO Pin 16 (Output) Raspberry Pi >> Arduino	[Sensor Signal]

Remark: Using BJT level shifter will invert the PULL HIGH and PULL LOW!
'''
import RPi.GPIO as GPIO					# Read and write the GPIO pins
import time
import MQTT_config as host
import MQTTsetup
from datetime import datetime
import paho.mqtt.client as mqtt
import threading
import sys
import json

num_packet = 0
currentStatusPin13 = 1		# (BJT)
currentStatusPin15 = 1		# (BJT)
currentStatusPin16 = 0
currentStatusPin18 = 0


countPin13 = 0
countPin15 = 0
#countPin16 = 0


def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe([(host.studentTopic,0),(host.stationTopic,0),(host.statusTopic,0)])

def on_message(client, userdata, msg):
	global num_packet, currentStatusPin16, currentStatusPin18
	print(f"Message received from topic {msg.topic} num={num_packet}", msg.payload.decode())
	num_packet += 1
	if(str(msg.topic) == host.stationTopic):
		#print(msg.payload.decode())
		iotData = json.loads(msg.payload.decode())
		station = iotData["location"]
		pallet = iotData["pallet"]
		if(str(station) == str(host.stationID) and str(pallet) == str(host.palletID)):				# ~RFID read pallet ID and mail the cargo
			statusPin16 = GPIO.output(16,1)		# Pin16 (GPIO23) status (sensor)
			currentStatusPin16 = 1
			print("Pallet is arrived!!")
		elif(str(station) == str(host.stationID) and str(pallet) == str(int(host.palletID)+3)):
			statusPin16 = GPIO.output(16,1)		# Pin16 (GPIO23) status (sensor)
			currentStatusPin16 = 1
			print("Pallet is arrived!!")
		elif(str(station) != str(host.stationID) and str(pallet) == str(host.palletID)):
			statusPin16 = GPIO.output(16,0)		# Pin16 (GPIO23) status (sensor)
			currentStatusPin16 = 0
			print("Pallet is leaved!!")
		elif(str(station) != str(host.stationID) and str(pallet) == str(int(host.palletID)+3)):
			statusPin16 = GPIO.output(16,0)		# Pin16 (GPIO23) status (sensor)
			currentStatusPin16 = 0
			print("Pallet is leaved!!")
	elif(str(msg.topic) == host.statusTopic):
		iotData = json.loads(msg.payload.decode())
		status = iotData["Status"]
		station = iotData["Station"]
		if(str(station) == str(host.stationID) and (str(status) == "end")):
			statusPin18 = GPIO.output(18,1)		# Pin16 (GPIO23) status (sensor)
			currentStatusPin18 = 1
			time.sleep(0.05)
			statusPin18 = GPIO.output(18,0)		# Pin16 (GPIO23) status (sensor)
			currentStatusPin18 = 0
		#elif(str(status) == "reset"):
			#statusPin16 = GPIO.output(18,0)		# Pin16 (GPIO23) status (sensor)
			#currentStatusPin18 = 0

    	
		
	

def GPIOcheck():
	global currentStatusPin13, currentStatusPin15, currentStatusPin16, currentStatusPin18, countPin13, countPin15, countPin16
	while True:
		time.sleep(0.1)
		'''
		# ---------------------- testing program <start> ----------------------
		input_value = GPIO.input(3)		# Read the Pin 3 status
		print("The status of Pin 3 is: ",input_value)		# return 1 if False, 0 if True 
		time.sleep(0.2)
		input_value = GPIO.input(5)		# Read the Pin 5 status
		print("The status of Pin 5 is: ",input_value)		# return 1 if False, 0 if True 
		time.sleep(0.2)
		input_value = GPIO.input(29)		# Read the Pin 29 status
		print("The status of Pin 29 is: ",input_value)		# return 1 if False, 0 if True 
		time.sleep(0.2)
		# ---------------------- testing program <end> ----------------------
		'''
		# Read GPIO input pin status
		statusPin13 = GPIO.input(11)		# Pin13 (GPIO27) status (Stopper Left)		0 for close, 1 for open
		# print("Current Pin 13 status is: ", statusPin13)
		#rint("previous Pin 13 status is: ", currentStatusPin13)
		statusPin15 = GPIO.input(13)		# Pin15 (GPIO22) status (Stopper Right)
		# print("Current Pin 15 status is: ", statusPin15)
		#print("previous Pin 15 status is: ", currentStatusPin15)
		# reset the counting of Pin
		if(statusPin13 != currentStatusPin13):
			countPin13 = 0
			# print("The counting number of Pin 13 is: ", countPin13)
		if(statusPin15 != currentStatusPin15):
			countPin15 = 0
			# print("The counting number of Pin 15 is: ", countPin15)
		
		# Publish MQTT message if the pin is activate
		if(statusPin13 == 0):
			if(countPin13 == 0):
				# print("The counting number of Pin 13 is: ", countPin13)
				message = MQTTsetup.mqtt_message_generator_mailing("cargo1", host.stationID, "CloseL", datetime.now().strftime("%H:%M:%S"))
				MQTTsetup.mqtt_publish_record(client,host.mailingTopic,message)
				print(f"Send message {message} to the topic {host.mailingTopic}")
				currentStatusPin13 = statusPin13
				countPin13 += 1
		elif(statusPin13 == 1):
			if(countPin13 == 0):
				# print("The counting number of Pin 13 is: ", countPin13)
				message = MQTTsetup.mqtt_message_generator_mailing("cargo1", host.stationID, "OpenL", datetime.now().strftime("%H:%M:%S"))
				MQTTsetup.mqtt_publish_record(client,host.mailingTopic,message)
				print(f"Send message {message} to the topic {host.mailingTopic}")
				currentStatusPin13 = statusPin13
				countPin13 += 1	
			
		if(statusPin15 == 0):
			# print("Pin 15 count: ", countPin15)
			if(countPin15 == 0):
				# print("The counting number of Pin 15 is: ", countPin15)
				message = MQTTsetup.mqtt_message_generator_mailing("cargo1", host.stationID, "CloseR", datetime.now().strftime("%H:%M:%S"))
				MQTTsetup.mqtt_publish_record(client,host.mailingTopic,message)
				print(f"Send message {message} to the topic {host.mailingTopic}")
				currentStatusPin15 = statusPin15
				countPin15 += 1
		elif(statusPin15 == 1):
			if(countPin15 == 0):
				# print("The counting number of Pin 15 is: ", countPin15)
				message = MQTTsetup.mqtt_message_generator_mailing("cargo1", host.stationID, "OpenR", datetime.now().strftime("%H:%M:%S"))
				MQTTsetup.mqtt_publish_record(client,host.mailingTopic,message)
				print(f"Send message {message} to the topic {host.mailingTopic}")
				currentStatusPin15 = statusPin15
				countPin15 += 1
	
    
if __name__ == '__main__':
	# initialization

	
	# GPIO configuration
	GPIO.setmode(GPIO.BOARD)			# Set the GPIO mode (According to Pin number)
	#GPIO.setmode(GPIO.BCM)				# Set the GPIO mode (Accoding to GPIO number)
	GPIO.setup(11,GPIO.IN)				# Configurate pin 13 as a GPIO input pin (Stopper Close)
	GPIO.setup(13,GPIO.IN)				# Configurate pin 15 as a GPIO input pin (Stopper Open)
	GPIO.setup(16,GPIO.OUT)				# Configurate pin 16 as a GPIO output pin (sensor)
	GPIO.setup(18,GPIO.OUT)				# Configurate pin 18 as a GPIO output pin (Node-RED)
	statusPin16 = GPIO.output(16,0)		# Pin16 (GPIO23) status (sensor)
	statusPin18 = GPIO.output(18,0)		# Pin16 (GPIO23) status (sensor)

	
	currentStatusPin13 = GPIO.input(11)				# Should be equal to 0
	print("Original Status for Pin 13 is: ",currentStatusPin13)
	currentStatusPin15 = GPIO.input(13)				# Should be equal to 0
	print("Original Status for Pin 15 is: ",currentStatusPin15)
	currentStatusPin16 = GPIO.input(16)				# Should be equal to 0
	currentStatusPin16 = GPIO.input(18)				# Should be equal to 0

	print(f"Orginional status: [Pin13 : {currentStatusPin13} , Pin15 : {currentStatusPin15}, Pin16 : {currentStatusPin16}, Pin18 : {currentStatusPin18}]")
	
	# MQTT configuration

	print("Host.server is: ", host.server)
	client = MQTTsetup.mqtt_client_setup(host.server)
	#client = MQTTsetup.mqtt_client_setup(host.onlineBroker)
	client.on_connect = on_connect
	client.on_message = on_message
	print("MQTT Connection")
	
	# Threading
	GPIOchecking = threading.Thread(target=GPIOcheck)
	GPIOchecking.start()
	
	try:
		while(True):
			client.loop()
	except KeyboardInterrupt:
		print("Interrupted!")
		GPIOchecking.join()
		sys.exit(0)
	

