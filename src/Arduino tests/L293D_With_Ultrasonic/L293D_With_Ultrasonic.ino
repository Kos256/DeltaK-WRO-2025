#include <AFMotor.h>
#include <Servo.h>

#define FWD 1
#define BWD 2
#define BRK 3
#define REL 4

AF_DCMotor motor(3);
Servo svo;

// (set) motor speed
void mspd(int dir, int spd=255) {
  motor.setSpeed(spd);
  //if (dir != 0) motor.run(dir%4 + 1);
  motor.run(dir);
}

void steer(int dir) {
  svo.write(map(dir, 100, -100, 0, 180));
//  svo.write(map(dir, 70, -100, 0, 180));
}

void setup() {
  Serial.begin(9600);
  svo.attach(9);
  motor.setSpeed(200);
  motor.run(RELEASE);

//  svo.write(90); while(1);
}

bool dir = true;

void loop() {
//  motor.run(dir?FORWARD:BACKWARD);
//  for (int i = 0; i < 180; i++) {
//    svo.write(i);
//    delay(4);
//  }
//  for (int i = 0; i < 180; i++) {
//    svo.write(180-i);
//    delay(4);
//  }
//  dir = !dir;

  
  steer(0);
  mspd(FWD);
  delay(1300);

  steer(50);
  mspd(FWD, 150);
  delay(2300);
}
