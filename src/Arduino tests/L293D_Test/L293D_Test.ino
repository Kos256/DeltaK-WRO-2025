#include <AFMotor.h>
#include <Servo.h>

AF_DCMotor motor(3);
Servo svo;

void setup() {
  Serial.begin(9600);
  svo.attach(9);
  motor.setSpeed(255);
  motor.run(RELEASE);
}

bool dir = true;

void loop() {
  motor.run(dir?FORWARD:BACKWARD);
  for (int i = 0; i < 180; i++) {
    svo.write(i);
    delay(4);
  }
  for (int i = 0; i < 180; i++) {
    svo.write(180-i);
    delay(4);
  }
  dir = !dir;
}
