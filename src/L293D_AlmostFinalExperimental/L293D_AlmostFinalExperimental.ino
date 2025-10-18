#include <AFMotor.h>
#include <Servo.h>

#define FWD 1
#define BWD 2
#define BRK 3
#define REL 4

bool _ZEROCHECK = false;
int iBtn = 2;
// bot init pos (on the mat)
int biPos = 5;
/*
 * 1 | 2 | 3
 * 4 | 5 | 6
 */

bool _mirror = false;

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
  Serial.begin(38400);
  pinMode(iBtn, INPUT_PULLUP);
  svo.attach(9);
  motor.setSpeed(200);
  motor.run(RELEASE);

  if (_ZEROCHECK) {
    svo.write(90);
    while(1);
  }

  delay(500);
  while(digitalRead(iBtn));
  Serial.println("btn routine started");
  bool startpgm = false;
  int c = -1;
  while(1) {
    c++;
    Serial.println("pressed! " + String(c));
    long prevm = millis(); // previous millis
    while (1) {
      if (millis() > prevm + 2000) {
        startpgm = true;
        break;
      }
      if (!digitalRead(iBtn)) { // if pressed
        while (!digitalRead(iBtn)); // then wait until released
        break; // and break out
      }
    }

    if (startpgm) break;
  }

  if (c <= 6) _mirror = false;
  else _mirror = true;
  if (c <= 6) {
    biPos = c;
  }
  else biPos = c - 6;
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

  if (!_mirror) {
    for (int lap = 0; lap < 3; lap++) {
      for (int i = 0; i < 4; i++) {
        steer(-10);
        mspd(FWD, 255);
  
        int fwdDelay = 800; // previously 1000
        if (biPos <= 3 and lap == 0 and i == 0) fwdDelay = 500;
//        if (i == 1) fwdDelay = 700;
//        if (i == 1 and lap == 1) fwdDelay = 1200;
        delay(fwdDelay);
      
        steer(50); // previously 50
        mspd(FWD, 170); // previously 150;
        delay(948); // previously 2200 then 1200 then 900 [PERFECT FOR 3S] then 
      }
    }
  }
  else {
    for (int lap = 0; lap < 3; lap++) {
      for (int i = 0; i < 4; i++) {
        steer(-10);
        mspd(FWD, 255);
  
        int fwdDelay = 800; // previously 1000
        if (biPos <= 3 and lap == 0 and i == 0) fwdDelay = 500;
//        if (i == 1) fwdDelay = 700;
//        if (i == 1 and lap == 1) fwdDelay = 1200;
        delay(fwdDelay);
      
        steer(-80); // previously 50
        mspd(FWD, 170); // previously 150;
        delay(1100); // previously 2200 then 1200 then 900 [PERFECT FOR 3S]
      }
    }
  }
  
  
  
  steer(0);
  mspd(FWD, 255); delay(500);
  mspd(FWD, 0); mspd(BWD, 255); delay(100); // spin motor back for 100ms to brake
  mspd(FWD, 0);
  while(1); // halt code
}
