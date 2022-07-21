// sensor.h

#ifndef sensor_h
#define sensor_h

#include <Arduino.h>

//#define FRONT_SENSOR_PIN 5
//#define LOADING_UNLOADING_SENSOR_PIN 4
//#define END_OPERATION_PIN 3
//#define DISPATCH_SENSOR_PIN 2
//#define RESET_SENSOR_PIN A2
//#define VREP_LOADING_UNLOADING_SENSOR_PIN A3
#define LOCATION_SENSOR_PIN 5
#define CARGO_DETECTOR_PIN 4
#define END_OPERATION_PIN 3
#define HOME_SENSOR_PIN 2
#define RESET_SENSOR_PIN A2
#define PALLET_DETECTOR_PIN A3
class sensor
{
    public:
        sensor(int pin);
        int read();

    private:
        int _pin;
        int count;
        int previousResult;
};

#endif
