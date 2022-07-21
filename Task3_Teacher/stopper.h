// stopper.h

#ifndef stopper_h
#define stopper_h

#include <Arduino.h>

#define STOPPER_L_PIN 13
#define STOPPER_R_PIN 12
#define BOTTOM_CONVEYOR_PIN 11
#define DISPATCH_CARGO_PIN 10
#define RESET_CARGO_PIN 9
#define DISPATCH_CARGO_NO_VREP_PIN 8

class stopper
{
    public:
        stopper(int pin);
        void close();
        void open();
        void activate();
        void start();
        void stop();

    private:
        int _pin;
        int count;
        int previousStatus; // 0 == open, 1 == close
};

#endif
