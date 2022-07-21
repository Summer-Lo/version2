'''
Languahe:	Python 3
Author:		Summer	(IC-EIA)
Update:		15/07/2022
Description:

For Arduino input to Raspberry Pi output:
GPIO Pin 13 (Input) [Arduino] 		>> 		GPIO Pin 21 (Input) [Raspberry Pi]		[Left Stopper]
GPIO Pin 12 (Input) [Arduino] 		>> 		GPIO Pin 19 (Input) [Raspberry Pi]		[Right Stopper]
GPIO Pin 11 (Input) [Arduino] 		>> 		GPIO Pin 15 (Input) [Raspberry Pi]		[Bottom Conveyor]
GPIO Pin 10 (Input) [Arduino] 		>> 		GPIO Pin 13 (Input) [Raspberry Pi]		[Dispatch Cargo]
GPIO Pin 9 	(Input) [Arduino] 		>> 		GPIO Pin 11 (Input) [Raspberry Pi]		[Reset Cargo]
GPIO Pin 8 	(Input) [Arduino] 		>> 		GPIO Pin 7 (Input) 	[Raspberry Pi]		[Spare]
GPIO Pin 7 	(Input) [Arduino] 		>> 		GPIO Pin 5 (Input) 	[Raspberry Pi]		[Spare]
GPIO Pin 6 	(Input) [Arduino] 		>> 		GPIO Pin 3 (Input) 	[Raspberry Pi]		[Spare]

Arduino output to Raspberry Pi input:
GPIO Pin 5 	(Output) [Raspberry Pi] 	>> 		GPIO Pin 26 (Input) [Arduino]		[Front Sensor]
GPIO Pin 4 	(Output) [Raspberry Pi] 	>> 		GPIO Pin 24 (Input) [A]rduino]		[Loading and Unloading Station Sensor (virtual)]
GPIO Pin 3 	(Output) [Raspberry Pi] 	>> 		GPIO Pin 22 (Input) [Arduino]		[End operation button]
GPIO Pin 2 	(Output) [Raspberry Pi] 	>> 		GPIO Pin 18 (Input) [A]rduino]		[Dispatching Sensor]
GPIO Pin A2 (Output) [Raspberry Pi] 	>> 		GPIO Pin 16 (Input) [Arduino]		[Reset Sensor]
GPIO Pin A3 (Output) [Raspberry Pi] 	>> 		GPIO Pin 12 (Input) [A]rduino]		[Loading and Unloading Station Sensor]
GPIO Pin A4 (Output) [Raspberry Pi] 	>> 		GPIO Pin 10 (Input) [Arduino]		[Spare]
GPIO Pin A5 (Output) [Raspberry Pi] 	>> 		GPIO Pin 8 (Input) [A]rduino]		[Spare]

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
import client_config as hc

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
	client.subscribe([(host.studentTopic,0),(host.stationTopic,0),(host.statusTopic,0),(host.arduinoTopic,0),(host.piTopic,0)])

def on_message(client, userdata, msg):
	global num_packet, currentStatusPin16, currentStatusPin18
	print(f"Message received from topic {msg.topic} num={num_packet}", msg.payload.decode())
	num_packet += 1

	# 
	if(str(msg.topic) == host.arduinoTopic):
		#print(msg.payload.decode())
		iotData = json.loads(msg.payload.decode())
		messageType = iotData["type"]		#["FS","LUS","EO","DS","RS"]
		station = iotData["location"]
		pallet = iotData["pallet"]
		if(str(messageType) == "FS"):
			if(str(station) == str(host.stationID)): 			# ~RFID read pallet ID and mail the cargo
				GPIO.output(26,1)		# Pin26 (GPIO23) status (sensor)
				hc.statusPin[8] = 1
				hc.currentStatusPin[8] = 1
				print("Pallet is arrived!!")
				stationTimer = threading.Thread(target=timerLeft,args=(3,26,8,))
				stationTimer.start()
			elif(str(station) != str(host.stationID)):
				GPIO.output(26,0)		# Pin26 (GPIO23) status (sensor)
				hc.statusPin[8] = 0
				hc.currentStatusPin[8] = 0
				print("Pallet is leaved!!")
		elif(str(messageType) == "LUS"):
			if(str(station) == str(host.stationID)): 			# ~RFID read pallet ID and mail the cargo
				GPIO.output(12,1)		# Pin12 (GPIO23) status (sensor)
				hc.statusPin[13] = 1
				hc.currentStatusPin[13] = 1
				print("Pallet is arrived!!")
				stationTimer = threading.Thread(target=timerLeft,args=(3,12,13,))
				stationTimer.start()
			elif(str(station) != str(host.stationID)):
				GPIO.output(12,0)		# Pin12 (GPIO23) status (sensor)
				hc.statusPin[13] = 0
				hc.currentStatusPin[13] = 0
				print("Pallet is leaved!!")

	elif(str(msg.topic) == host.statusTopic):
		iotData = json.loads(msg.payload.decode())
		station = iotData["Station"]
		status = iotData["Status"]
		if(str(station) == host.stationID):
			if(str(status) == "end"):
				statusPin18 = GPIO.output(18,1)		# Pin16 (GPIO23) status (sensor)
				currentStatusPin18 = 1
				time.sleep(0.05)
				statusPin18 = GPIO.output(18,0)		# Pin16 (GPIO23) status (sensor)
				currentStatusPin18 = 0
			#elif(str(status) == "reset"):
				#statusPin16 = GPIO.output(18,0)		# Pin16 (GPIO23) status (sensor)
				#currentStatusPin18 = 0

	elif(str(msg.topic) == host.piTopic):
		iotData = json.loads(msg.payload.decode())
		ID = iotData["ID"]
		status = iotData["Status"]
		if(str(ID) == host.piID):
			if(str(status) == "RESET"):
				GPIO.output(33,1)
				time.sleep(0.1)
				GPIO.output(33,0)

def timerLeft(second,pinNo,arrayindex):
	print(f"Timer {second} second is started now!")
	time.sleep(float(second))    	
	print(f"Timer {second} second is ended now!")
	GPIO.output(int(pinNo),0)
	hc.statusPin[int(arrayindex)] = 0
	hc.currentStatusPin[int(arrayindex)] = 0
	print("Pallet is leaved!!")

	
# Raspberry Pi received Arduino signal
def GPIOArduinocheck():
	global currentStatusPin13, currentStatusPin15, currentStatusPin16, currentStatusPin18, countPin13, countPin15, countPin16
	print("--------------------  GPIOChecking <START> --------------------")
	inputMessage = "The Orginional Status : [  "
	for i in range(len(hc.pinID)):
		if (hc.pinMode[i] == "IN"):
			hc.statusPin[i] = GPIO.input(hc.pinID[i])
			inputMessage = inputMessage + f"Pin {i+1} ({str(hc.pinID[i])}) : {str(hc.statusPin[i])}  "
	inputMessage = inputMessage + "]"
	print(inputMessage)
	
	print(f"The activated input GPIO pin is:  Pin {hc.inputActivatePin} : pin Order[{hc.inputActivatePinOrder}]")
	while True:
		time.sleep(0.1)
		#print(hc.inputCurrentStatusPin)
		for i in range(len(hc.inputActivatePin)):
			#print(f"The activated input GPIO pin is:  Pin {hc.inputActivatePin[i]} : pinID[{hc.inputActivatePinOrder[i]}]")
			hc.inputCurrentStatusPin[int(i)] = GPIO.input(hc.inputActivatePin[int(i)])	# from arduino					# Checking current GPIO status
			#print(f"Current StatuMQTTPLCActionPins is {hc.inputCurrentStatusPin}")
			#print(f"Input Status is {hc.inputStatusPin}")
			if(hc.inputCurrentStatusPin[int(i)] != hc.inputStatusPin[int(i)]):
				hc.inputCountPin[int(i)] = 0
				#print("GPIOArduinocheck Reset counting")
				print(f"counting is : {hc.inputCountPin}")
				print(f"Current input activate pin is: {hc.inputActivatePin[i]}")
				if(hc.inputCurrentStatusPin[int(i)] == 1):
					if(hc.inputCountPin[int(i)] == 0):
						message = MQTTsetup.mqtt_message_generator_arduino(str(hc.MQTTStationID[i]),str(hc.MQTTType[i]),str(hc.MQTTStatusAct[i]))
						MQTTsetup.mqtt_publish_record(client,host.arduinoControlTopic,message)
						print(f"Send message {message} to the topic {host.arduinoControlTopic}")
						hc.inputStatusPin[int(i)] = hc.inputCurrentStatusPin[int(i)]
						print(f"Updated status is {hc.inputStatusPin}")
						hc.inputCountPin[int(i)] += 1
						print(f"counting is : {hc.inputCountPin}")
						if(hc.MQTTStatusAct[i] == "Activate"):
							GPIO.output(hc.MQTTPLCActionPin[i],1)
							hc.plcInputCurrentStatusPin[hc.plcInputPin.index(hc.MQTTPLCActionPin[i])] = 1
							hc.plcInputStatusPin[hc.plcInputPin.index(hc.MQTTPLCActionPin[i])] = 1
							print("Current PLC input status in: ", hc.plcInputCurrentStatusPin)
							if(hc.MQTTType[i] == "DC"):
								hc.start_time = time.time()
								message = MQTTsetup.mqtt_message_generator_mailing("cargo2", str(hc.stationID),"Mail","NA")
								MQTTsetup.mqtt_publish_record(client,host.mailingTopic,message)
							pass

				elif(hc.inputCurrentStatusPin[int(i)] == 0):
					if(hc.inputCountPin[int(i)] == 0):
						message = MQTTsetup.mqtt_message_generator_arduino(str(hc.MQTTStationID[i]),str(hc.MQTTType[i]),str(hc.MQTTStatusDeAct[i]))
						MQTTsetup.mqtt_publish_record(client,host.arduinoControlTopic,message)
						print(f"Send message {message} to the topic {host.arduinoControlTopic}")
						hc.inputStatusPin[int(i)] = hc.inputCurrentStatusPin[int(i)]
						print(f"Updated status is {hc.inputStatusPin}")
						hc.inputCountPin[int(i)] += 1
						print(f"counting is : {hc.inputCountPin}")
						if(hc.MQTTStatusDeAct[i] == "Deactivate"):
							GPIO.output(hc.MQTTPLCActionPin[i],0)
							hc.plcInputCurrentStatusPin[hc.plcInputPin.index(hc.MQTTPLCActionPin[i])] = 0
							hc.plcInputStatusPin[hc.plcInputPin.index(hc.MQTTPLCActionPin[i])] = 0
							print("Current PLC input status in: ", hc.plcInputCurrentStatusPin)
							pass
	''' 
	# conplex version for considering whole pinID
	for i in range(len(hc.inputActivatePin)):
		hc.inputActivatePinOrder.append(hc.pinID.index(hc.inputActivatePin[i]))
		print(f"The activated input GPIO pin is:  Pin {hc.inputActivatePin[i]} : pinID[{hc.inputActivatePinOrder[i]}]")
	while True:
		time.sleep(0.1)
		#print(hc.currentStatusPin)
		for i in range(len(hc.inputActivatePin)):
			#print(f"The activated input GPIO pin is:  Pin {hc.inputActivatePin[i]} : pinID[{hc.inputActivatePinOrder[i]}]")
			hc.currentStatusPin[int(hc.inputActivatePinOrder[i])] = GPIO.input(hc.pinID[int(hc.inputActivatePinOrder[i])])					# Checking current GPIO status
			#print(f"Current Status is {hc.currentStatusPin}")
			#print(f"Status is {hc.statusPin}")
			if(hc.currentStatusPin[int(hc.inputActivatePinOrder[i])] != hc.statusPin[int(hc.inputActivatePinOrder[i])]):
				hc.countPin[int(hc.inputActivatePinOrder[i])] = 0
				print("Reset counting")
				#print(f"counting is : {hc.countPin}")
				if(hc.currentStatusPin[int(hc.inputActivatePinOrder[i])] == 1):
					if(hc.countPin[int(hc.inputActivatePinOrder[i])] == 0):
						message = MQTTsetup.mqtt_message_generator_arduino(str(hc.MQTTStationID[i]),str(hc.MQTTType[i]),str(hc.MQTTStatusAct[i]))
						MQTTsetup.mqtt_publish_record(client,host.arduinoControlTopic,message)
						print(f"Send message {message} to the topic {host.arduinoControlTopic}")
						hc.statusPin[int(hc.inputActivatePinOrder[i])] = hc.currentStatusPin[int(hc.inputActivatePinOrder[i])]
						print(f"Updated status is {hc.statusPin}")
						hc.countPin[int(hc.inputActivatePinOrder[i])] += 1
						print(f"counting is : {hc.countPin}")

				elif(hc.currentStatusPin[int(hc.inputActivatePinOrder[i])] == 0):
					if(hc.countPin[int(hc.inputActivatePinOrder[i])] == 0):
						message = MQTTsetup.mqtt_message_generator_arduino(str(hc.MQTTStationID[i]),str(hc.MQTTType[i]),str(hc.MQTTStatusDeAct[i]))
						MQTTsetup.mqtt_publish_record(client,host.arduinoControlTopic,message)
						print(f"Send message {message} to the topic {host.arduinoControlTopic}")
						hc.statusPin[int(hc.inputActivatePinOrder[i])] = hc.currentStatusPin[int(hc.inputActivatePinOrder[i])]
						print(f"Updated status is {hc.statusPin}")
						hc.countPin[int(hc.inputActivatePinOrder[i])] += 1
						print(f"counting is : {hc.countPin}")
	'''
# Raspberry Pi received PLC signal and send to Arduino (Sensor signal)
# Check [29,31,35,37] PLC Pin signal and send to [0,16,18,24] Arduino Pin
def GPIOPLCcheck():
	while(True):
		time.sleep(0.1)
		for i in range(len(hc.plcOutputPin)):
			if(int(hc.plcOutArdInPin[i]) == 0):				# Check whether the output pin equal to 0 (Spare)
				hc.plcOutputCurrentStatusPin[int(i)] = 0	# Set to zero if this is spare pin
			else:
				hc.plcOutputCurrentStatusPin[int(i)] = GPIO.input(hc.plcOutputPin[int(i)])					# Checking current GPIO status
				#print(f"Current PLC Output pin is: {hc.plcOutputPin[int(i)]}")
				#print(f"Current PLC Output Status is: {hc.plcOutputCurrentStatusPin[int(i)]}")
				if(hc.plcOutputCurrentStatusPin[int(i)] != hc.plcOutputStatusPin[int(i)]):
					hc.plcOutputCountPin[int(i)] = 0
					#print("GPIOPLCcheck Reset counting")
					if(hc.plcOutputCurrentStatusPin[int(i)] == 1):
						if(hc.plcOutputCountPin[int(i)] == 0):
							if(str(hc.plcOutputMQTTType[i]) != "SP"):
								print(f"PLC output Pin {hc.plcOutputPin[i]} is activated")
								message = MQTTsetup.mqtt_message_generator_plc(str(hc.MQTTStationID[i]),str(hc.plcOutputMQTTType[i]),str(hc.plcOutputMQTTAct[i]))
								MQTTsetup.mqtt_publish_record(client,host.plcTopic,message)
								print(f"Send message {message} to the topic {host.plcTopic}")
								hc.plcOutputStatusPin[int(i)] = hc.plcOutputCurrentStatusPin[int(i)]
								print(f"Updated status is {hc.plcOutputStatusPin}")
								hc.plcOutputCountPin[int(i)] += 1
								print(f"counting is : {hc.plcOutputCountPin}")
								if(hc.plcOutputMQTTAct[i] == "Arrived"):
									if(hc.plcOutArdInPin[i] != 0):
										GPIO.output(hc.plcOutArdInPin[i],1)
										print(f"Raspberry Pi Pin {hc.plcOutArdInPin[i]} is pulling HIGH!")
										hc.outputStatusPin[hc.outputActivatePin.index(hc.plcOutArdInPin[i])] = 1
										hc.outputCurrentStatusPin[hc.outputActivatePin.index(hc.plcOutArdInPin[i])] = 1
										print("Current Arduino input status is: ", hc.outputCurrentStatusPin)
										pass
								if(str(hc.plcOutputMQTTType[i]) == "DS" and hc.plcOutputMQTTAct[i] == "Arrived"):
									print('--------------- Before ---------------')
									GPIO.output(32,0)
									GPIO.output(36,0)
									GPIO.output(38,0)
									hc.plcInputStatusPin[0] = 0
									hc.plcInputCurrentStatusPin[0] = 0
									hc.plcInputCountPin[0] = 0
									hc.plcInputStatusPin[1] = 0
									hc.plcInputCurrentStatusPin[1] = 0
									hc.plcInputCountPin[1] = 0
									hc.plcInputStatusPin[2] = 0
									hc.plcInputCurrentStatusPin[2] = 0
									hc.plcInputCountPin[2] = 0
									#hc.inputStatusPin[3] = 0
									#hc.inputCountPin[3] = 0				# release the counter from the ardunio signal
									print("Dispatch cargo conveyor is stopped now!")
									print("--------------- After ---------------")
									print(f"Current StatuMQTTPLCActionPins is {hc.inputCurrentStatusPin}")
									print(f"Input Status is {hc.inputStatusPin}")
								if(str(hc.plcOutputMQTTType[i]) == "PLCLUS" and hc.plcOutputMQTTAct[i] == "Arrived"):
									print(time.time() - hc.start_time, "seconds")
									time.sleep(1)
									GPIO.output(32,1)
									GPIO.output(36,1)
									hc.plcInputStatusPin[0] = 1
									hc.plcInputCurrentStatusPin[0] = 1
									hc.plcInputCountPin[0] = 1
									hc.plcInputStatusPin[1] = 1
									hc.plcInputCurrentStatusPin[1] = 1
									hc.plcInputCountPin[1] = 1	

					elif(hc.plcOutputCurrentStatusPin[int(i)] == 0):
						if(hc.plcOutputCountPin[int(i)] == 0):
							if(str(hc.plcOutputMQTTType[i]) != "SP"):
								print(f"PLC output Pin {hc.plcOutputPin[i]} is deactivated")
								message = MQTTsetup.mqtt_message_generator_arduino(str(hc.MQTTStationID[i]),str(hc.plcOutputMQTTType[i]),str(hc.plcOutputMQTTDeact[i]))
								MQTTsetup.mqtt_publish_record(client,host.plcTopic,message)
								print(f"Send message {message} to the topic {host.plcTopic}")
								hc.plcOutputStatusPin[int(i)] = hc.plcOutputCurrentStatusPin[int(i)]
								print(f"Updated status is {hc.plcOutputStatusPin}")
								hc.plcOutputCountPin[int(i)] += 1
								print(f"counting is : {hc.inputCountPin}")
								if(hc.plcOutputMQTTDeact[i] == "Left"):
									if(hc.plcOutArdInPin[i] != 0):
										GPIO.output(hc.plcOutArdInPin[i],0)
										print(f"Raspberry Pi Pin {hc.plcOutArdInPin[i]} is pulling LOW!")
										hc.outputStatusPin[hc.outputActivatePin.index(hc.plcOutArdInPin[i])] = 0
										hc.outputCurrentStatusPin[hc.outputActivatePin.index(hc.plcOutArdInPin[i])] = 0
										print("Current Arduino input status is: ", hc.outputCurrentStatusPin)
										pass
    
if __name__ == '__main__':
	# initialization
	print("--------------------------  Initialization <START> --------------------------")
	GPIO.setmode(GPIO.BOARD)			# Set the GPIO mode (According to Pin number)
	#GPIO.setmode(GPIO.BCM)				# Set the GPIO mode (Accoding to GPIO number)
	# For Raspberry Pi to Arduino
	for i in range(len(hc.pinID)):
		if(str(hc.pinMode[i]) == "OUT"):
			GPIO.setup(hc.pinID[i],GPIO.OUT)
			hc.statusPin[i] = 0
			GPIO.output(hc.pinID[i],0)
			hc.currentStatusPin[i] = 0
		elif(str(hc.pinMode[i]) == "IN"):
			GPIO.setup(hc.pinID[i],GPIO.IN)
			hc.currentStatusPin[i] = GPIO.input(hc.pinID[i])
	headingMessage = "The Orginional Status : ["
	for i in range(len(hc.pinID)):
		headingMessage = headingMessage + f" Pin{int(i)+1} ({hc.pinID[i]}) : {hc.currentStatusPin[i]} ,"
	headingMessage = headingMessage + "]"
	print(headingMessage)
	print("<-------------------- PLC Initialization <START> -------------------->")
	# For Raspberry Pi to PLC
	headingMessage = "The PLC Orginional Status : [\n"
	for i in range(len(hc.plcInputPin)):
		GPIO.setup(hc.plcInputPin[i],GPIO.OUT)
		GPIO.output(hc.plcInputPin[i],0)
		hc.plcInputStatusPin[i] = 0
		hc.plcInputCurrentStatusPin[i] = 0
		headingMessage = headingMessage + f"[RPI OUTPUT] Type: {hc.plcInputMQTTType[int(i)]} : Pin({hc.plcInputPin[i]})\n"
	for i in range(len(hc.plcOutputPin)):
		GPIO.setup(hc.plcOutputPin[i],GPIO.IN)
		hc.plcOutputStatusPin[i] = 0
		hc.plcOutputCurrentStatusPin[i] = 0
		headingMessage = headingMessage + f"[RPI INPUT]  Type: {hc.plcOutputMQTTType[int(i)]} : Pin({hc.plcOutputPin[i]})\n"
	headingMessage = headingMessage + "]"
	print(headingMessage)
	print(f"PLC INPUT Status is: {hc.plcInputStatusPin}")
	print(f"PLC OUTPUT Status is: {hc.plcOutputStatusPin}")
	print(f"PLC CURRENT INPUT Status is: {hc.plcInputCurrentStatusPin}")
	print(f"PLC CURRENT OUTPUT Status is: {hc.plcOutputCurrentStatusPin}")
	print("<-------------------- PLC Initialization <END> -------------------->")
	print("--------------------------  Initialization <END> --------------------------")

	print("--------------------------  MQTTChecking <START> --------------------------")
	'''
	outputMessage = "The Orginional Status : [  "
	for i in range(len(hc.pinID)):
		if (hc.pinMode[i] == "OUT"):
			GPIO.output(hc.pinID[i],0)
			hc.statusPin[i] = 0
			outputMessage = outputMessage + f"Pin {i+1} ({str(hc.plcInputPin[i])}) : {str(hc.statusPin[i])}  "
	outputMessage = outputMessage + "]"
	print(outputMessage)
	for i in range(len(hc.outputActivatePin)):
		hc.outputActivatePinOrder.append(hc.pinID.index(hc.outputActivatePin[i]))
		print(f"The activated output GPIO pin is:  Pin {hc.outputActivatePin[i]} : pinID[{hc.outputActivatePinOrder[i]}]")
	'''
	# MQTT configuration

	time.sleep(0.5)
	print("Host.server is: ", host.server)
	client = MQTTsetup.mqtt_client_setup(host.server)
	#client = MQTTsetup.mqtt_client_setup(host.onlineBroker)
	client.on_connect = on_connect
	client.on_message = on_message
	print("MQTT Connection")
	if(int(hc.mode) == 1):
		GPIO.setup(40,GPIO.OUT)
		GPIO.output(40,0)
	elif(int(hc.mode) == 2):
		GPIO.setup(40,GPIO.OUT)
		GPIO.output(40,1)
	
	GPIO.setup(33,GPIO.OUT)
	# Threading
	GPIOArdchecking = threading.Thread(target=GPIOArduinocheck)
	GPIOArdchecking.start()
	GPIOPLCchecking = threading.Thread(target=GPIOPLCcheck)
	GPIOPLCchecking.start()
	
	
	try:
		while(True):
			client.loop()
	except KeyboardInterrupt:
		print("Interrupted!")
		GPIOArdchecking.join()
		GPIOPLCchecking.join()
		sys.exit(0)
	

