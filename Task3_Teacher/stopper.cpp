#include <Arduino.h>
#include "stopper.h"

stopper::stopper(int pin)
{
    if (pin == 0) _pin = STOPPER_L_PIN;           // left stopper
    if (pin == 1) _pin = STOPPER_R_PIN;           // right stopper
    if (pin == 2) _pin = BOTTOM_CONVEYOR_PIN;     // bottom conveyor
    if (pin == 3) _pin = DISPATCH_CARGO_PIN;      // dispatch cargo
    if (pin == 4) _pin = RESET_CARGO_PIN;         // reset cargo
    if (pin == 5) _pin = DISPATCH_CARGO_NO_VREP_PIN;
    pinMode(_pin,OUTPUT);        // set pin as the GPIO output pin
    count = 0;
    previousStatus = 0;                    // 0 == open and 1 == close
}

void stopper::close()
{
    if(previousStatus == 0){             // if previous Status = open, reset counting
      count = 0;
    }
    if(count == 0){
      digitalWrite(_pin, HIGH);          // LOW == PULL HIGH (BJT)
      // Serial.println("Pin is: " + String(_pin));
      // Serial.println("Stopper is closed!");
      previousStatus = 1;
      count++;
    }
    
}

void stopper::open()
{
    if(previousStatus == 1){             // if previous Status = close, reset counting
      count = 0;
    }
    if(count == 0){
      digitalWrite(_pin, LOW);         // HIGH == PULL LOW (BJT)
      // Serial.println("Pin is: " + String(_pin));
      // Serial.println("Stopper is Opened!");
      previousStatus = 0;
      count++;
    }
}

void stopper::activate()
{
  if(previousStatus == 0){             // if previous Status = close, reset counting
      count = 0;
    }
    if(count == 0){
      digitalWrite(_pin, HIGH);         // HIGH == PULL LOW (BJT)
      // Serial.println("Pin is: " + String(_pin));
      // Serial.println("Stopper is Opened!");
      previousStatus = 1;
      count++;
    }
}

void stopper::start()
{
  digitalWrite(_pin, LOW);
  previousStatus = 0;
  delay(200);
  if(previousStatus == 0){             // if previous Status = stop, reset counting
      count = 0;
    }
    if(count == 0){
      digitalWrite(_pin, HIGH);         // HIGH == PULL LOW (BJT)
      // Serial.println("Pin is: " + String(_pin));
      // Serial.println("Stopper is Opened!");
      previousStatus = 1;
      count++;
    }
}

void stopper::stop()
{
  if(previousStatus == 1){             // if previous Status = start, reset counting
      count = 0;
    }
    if(count == 0){
      digitalWrite(_pin, LOW);         // HIGH == PULL LOW (BJT)
      // Serial.println("Pin is: " + String(_pin));
      // Serial.println("Stopper is Opened!");
      previousStatus = 0;
      count++;
    }
}
