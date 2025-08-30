#include <AFMotor.h>
#include <Servo.h>

#define FWD 1
#define BWD 2
#define BRK 3
#define REL 4

bool _ZEROCHECK = false;

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
}

void setup() {
  Serial.begin(9600);
  svo.attach(9);
  motor.setSpeed(200);
  motor.run(RELEASE);

  if (_ZEROCHECK) {
    svo.write(90);
    while(1);
  }
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

  for (int lap = 0; lap < 3; lap++) {
    for (int i = 0; i < 4; i++) {
      steer(-10);
      mspd(FWD, 255);

      int fwdDelay = 1000;
      if (i == 1) fwdDelay = 700;
      if (i == 1 and lap == 1) fwdDelay = 1200;
      delay(fwdDelay);
    
      steer(50); // previously 50
      mspd(FWD, 170); // previously 150;
      delay(2200);
    }
  }
  
  
  steer(0);
  mspd(FWD, 255); delay(500);
  
  mspd(FWD, 0);
  while(1); // halt code
}
