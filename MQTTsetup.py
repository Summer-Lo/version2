import paho.mqtt.client as mqtt
import time
from datetime import datetime
import json

def mqtt_client_setup(server):
    client = mqtt.Client()
    client.connect(server,1883,60) # server = 'ia.ic.polyu.edu.hk'
    return client


def mqtt_publish_record(client,topic,mqtt_message): #topic = "iot/sensor"
    result = client.publish(topic, mqtt_message)
    status = result[0]
    if status == 0:
        print(f"Send `{mqtt_message}` to topic `{topic}`")      # Print the published message and topic
    else:
        print(f"Failed to send message to topic {topic}")    

def mqtt_message_generator_sensor(ID,station,posX,posY,posZ,temp,time):
    #Generate message for node red dashboard display
    '''
    mqtt_message =' { "ID" :' + str(ID)+ \
                ', "Station" :'+ str(station)+ \
                ', "Position X" :'+str(posX)+\
                ', "Position Y":'+str(posY)+\
                ', "Position Z":'+str(posZ) +\
                ', "Tempature":'+str(temp) +\
                ', "Current Time":'+str(time) + ' } '
    '''
    mqtt_message ={ "ID" : str(ID) \
                , "Station" : str(station)\
                , "Position X" :str(posX)\
                , "Position Y":str(posY)\
                , "Position Z":str(posZ) \
                , "Tempature":str(temp) \
                , "Current Time":str(time)   } 
    mqtt_message = json.dumps(mqtt_message)  
    #print(type(mqtt_message))
    return mqtt_message             
         

def mqtt_message_generator_mailing(ID,destination,status,time): # statis = str(failed), str(sucessful), str(mailing)
    #Generate message for node red dashboard display

    mqtt_message ={ "ID" :  str(ID) \
                , "Destination" : str(destination) \
                , "Status" : str(status) \
                , "Current Time" : str(time)   } 
    mqtt_message = json.dumps(mqtt_message)         
    return mqtt_message  

'''
    mqtt_message =' { "total_count" :' + str(total_contact)+ \
                ', "valid_patient_counter" :'+ str(a)+ \
                ', "invalid_patient_counter" :'+str(b)+\
                ', "valid_exit_counter":'+str(c)+\
                ', "invalid_exit_counter":'+str(d) +\
                ', "success_rate":'+str(success_rate) +\
                ', "total_sucess":'+str(a+c) +\
                ', "total_fail":'+str(b+d) + ' } '
'''

def mqtt_message_generator_center(ID,destination,status,time): # statis = str(failed), str(sucessful), str(mailing)
    #Generate message for node red dashboard display

    mqtt_message ={ "ID" :  str(ID) \
                , "Destination" : str(destination) \
                , "Status" : str(status) \
                , "Current Time" : str(time)   } 
    mqtt_message = json.dumps(mqtt_message)         
    return mqtt_message  

def mqtt_message_generator_combine(ID,object,status,time): # statis = str(failed), str(sucessful), str(mailing)
    #Generate message for node red dashboard display

    mqtt_message ={ "ID" :  str(ID) \
                , "Partner" : str(object) \
                , "Status" : str(status) \
                , "Current Time" : str(time)   } 
    mqtt_message = json.dumps(mqtt_message)         
    return mqtt_message  
'''
Type = [SL: Stopper Left,
        SR: Stopper Right,
        BC: Bottom Conveyor,
        DC: Dispatching Cargo,
        RC: Reset Cargo]
'''
def mqtt_message_generator_arduino(stationID,type,status):
    mqtt_message ={ "StationID" :  str(stationID) \
                , "Type" : str(type) \
                , "Status" : str(status) \
                , "Current Time" : str(datetime.now().strftime("%H:%M:%S"))   } 
    mqtt_message = json.dumps(mqtt_message)         
    return mqtt_message  

def mqtt_message_generator_plc(stationID,type,status):
    mqtt_message ={ "StationID" :  str(stationID) \
                , "Type" : str(type) \
                , "Status" : str(status) \
                , "Current Time" : str(datetime.now().strftime("%H:%M:%S"))   } 
    mqtt_message = json.dumps(mqtt_message)         
    return mqtt_message 

if __name__ == '__main__':
    client = mqtt_client_setup('ia.ic.polyu.edu.hk')
    for i in range(10):
        message = mqtt_message_generator_sensor(i,i,0.1,0.2,0.3,37.5,11152021)
        print(message)
        mqtt_publish_record(client, "iot/sensor", message)
        time.sleep(1)
    