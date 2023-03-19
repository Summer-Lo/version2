import sys

if len(sys.argv) > 1:
    mode = sys.argv[1]
    print(f"Sys argv is : {sys.argv}")
else:
    correctInput = [1,2]
    mode = input("Please input the Mode ID (1 == V-REP, 2 == PLC): ")
    while(int(mode) not in correctInput):
        print("Invalid Input! Please try again!")
        mode = input("Please input the Mode ID (1 == V-REP, 2 == PLC): ")
# Raspberry Pi ID
stationID = "HP"
# station ID can be ["XH","QP","PD","JD","HP","HMT","SKM","MGK","TST",SWN"]
palletID = "1"
# pallet ID can be ["1","2","3"]
piID = "01"
#pi ID can be ["01","02","03","04","05","06","07","08","09","10","11","12",]

# pin number and order refer to the IO table
pin1 = 21           # Controller - Left Stopper 
pin2 = 19           # Controller - Right Stopper 
pin3 = 15           # Action - Activate bottom conveyor on loading and unloading station
pin4 = 13           # Action - Dispatching cargo
pin5 = 11           # Action - RESET cargo in loading and unloading station
pin6 = 7            # spare
pin7 = 5            # spare
pin8 = 3            # spare
pin9 = 26           # Sensor - (front of the loading and unloading station)
pin10 = 24          # Sensor - Loading and unloading station (physical)
pin11 = 22          # Action - End operation
pin12 = 18          # Sensor - Dispatching position 
pin13 = 16          # Sensor - RESET position
pin14 = 12          # Sensor - Loading and unloading station (virtural)
pin15 = 10          # spare
pin16 = 8           # spare

# Pin config for the main program
pinID = [int(pin1),int(pin2),int(pin3),int(pin4),int(pin5),int(pin6),int(pin7),int(pin8),int(pin9),int(pin10),int(pin11),int(pin12),int(pin13),int(pin14),int(pin15),int(pin16)]
pinMode = ["IN","IN","IN","IN","IN","IN","IN","IN","OUT","OUT","OUT","OUT","OUT","OUT","OUT","OUT"]		# "OUT" == OUTPUT, "IN" == INPUT
statusPin = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
currentStatusPin = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
countPin = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

# input pin config
inputStatusPin = [0,0,0,0,0,0,0,0]
inputCurrentStatusPin = [0,0,0,0,0,0,0,0]
inputCountPin = [0,0,0,0,0,0,0,0]

# output pin config
outputStatusPin = [0,0,0,0,0,0,0,0]
outputCurrentStatusPin = [0,0,0,0,0,0,0,0]
outputCountPin = [0,0,0,0,0,0,0,0]

# PLC config
plcPinID = [32,36,38,40,29,31,35,37]
plcPinMode = ["IN","IN","IN","IN","OUT","OUT","OUT","OUT"]		# PLC: "OUT" == OUTPUT, "IN" == INPUT
plcInputPin = []
plcOutputPin = []
#plcInputPin = [32,36,38,40]        # output to PLC
#plcOutputPin = [29,31,35,37]       # Input to PLC
for i in range(len(plcPinID)):
    if(plcPinMode[i] == "IN"):
        plcInputPin.append(int(plcPinID[i]))
    elif(plcPinMode[i] == "OUT"):
        plcOutputPin.append(int(plcPinID[i]))
plcInputMQTTType = ["BC","RC","DS","SP"]
plcInputStatusPin = [0,0,0,0]
plcInputCurrentStatusPin = [0,0,0,0]
plcInputCountPin = [0,0,0,0]
if(int(mode) == 1):
    plcOutputMQTTType = ["SP","RS","DS","SP"]
    plcOutputMQTTAct = ["Arrived","Arrived","Arrived","Arrived"]
    plcOutputMQTTDeact = ["Left","Left","Left","Left"]
    plcOutArdInPin = [0,16,18,0]
    plcOutputStatusPin = [0,0,0,0]
    plcOutputCurrentStatusPin = [0,0,0,0]
    plcOutputCountPin = [0,0,0,0]
    print("Current Mode is V-REP control")
if(int(mode) == 2):
    plcOutputMQTTType = ["SP","RS","DS","PLCLUS"]
    plcOutputMQTTAct = ["Arrived","Arrived","Arrived","Arrived"]
    plcOutputMQTTDeact = ["Left","Left","Left","Left"]
    plcOutArdInPin = [0,16,18,24]
    plcOutputStatusPin = [0,0,0,0]
    plcOutputCurrentStatusPin = [0,0,0,0]
    plcOutputCountPin = [0,0,0,0]
    print("Current Mode is PLC control")


inputActivatePin = [21,19,15,13,11,7]
inputActivatePinOrder = []
for i in range(len(inputActivatePin)): 
    inputActivatePinOrder.append(int(i))
MQTTStationID = [str(stationID),str(stationID),str(stationID),str(stationID),str(stationID),str(stationID)]
MQTTType = ["SL", "SR", "BC", "DC", "RC","DCNV"]
MQTTStatusAct = ["Close","Close","Activate","Activate","Activate","Activate"]
MQTTStatusDeAct = ["Open","Open","Deactivate","Deactivate","Deactivate","Deactivate"]
MQTTPLCActionPin = [0,0,32,38,36,38]   # Activate action corresponding rasp pi pin to PLC
# BC: to PLC (X1)
# DC: to PLC (X2)
# RC: to PLC (X3)
outputActivatePin = [26,24,22,18,16,12] # 26, 24 from V-REP
outputActivatePinOrder = []
for i in range(len(outputActivatePinOrder)): 
    outputActivatePinOrder.append(int(i))

start_time = 0

