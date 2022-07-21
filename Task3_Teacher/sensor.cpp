#include <Arduino.h>
#include "sensor.h"

sensor::sensor(int pin)
{
    if(pin == 0){     //Sensor for Loading and Unloading station (virtual)
      //_pin = 4;
      _pin = CARGO_DETECTOR_PIN;  
    }
    else if(pin == 1){     //End button
      //_pin = 3;
      _pin = END_OPERATION_PIN;
    }
    else if(pin == 2){     //Sensor for front of the Loading and Unloading station
      //_pin = 5; 
      _pin = LOCATION_SENSOR_PIN;  
    }
    else if(pin == 3){     //Sensor for Dispatching process in physical Loading and Unloading Station
      //_pin = 2;
      _pin = HOME_SENSOR_PIN;
    }
    else if(pin == 4){     //Sensor for RESET process in Physical Loading and Unloading station
      //_pin = A2;
      _pin = RESET_SENSOR_PIN;
    }
    else if(pin == 5){    //Sensor for V-REP (Virtural) Loading and Unloading Sensor
      _pin = PALLET_DETECTOR_PIN;
    }
    count = 0;
    previousResult = 0;
    pinMode(_pin,INPUT);        // set pin as the GPIO input pin
}

int sensor::read()
{
    int result = digitalRead(_pin);          // 0 = didn't read the signal / 1 = signal read successfully (BJT Inverted)
    if(result != previousResult){
      count = 0;
    }
    //Serial.println("Counting number is: " + String(count));    
    previousResult = result;
    if(count == 0){
      // Serial.println("The read pin is: " + String(_pin));
      // Serial.println("The Sensor signal is read as: " + String(result));
      
      count ++;
    }
    
    return result;
}
