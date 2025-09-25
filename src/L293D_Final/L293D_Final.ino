#include <AFMotor.h>
#include <Servo.h>

#define FWD 1
#define BWD 2
#define BRK 3
#define REL 4

// USRT, USRE, USLT, USLE, USUT, USUE (ultrasonic right/left/up trig/echo)
#define USRT A0
#define USRE A1
#define USLT A2
#define USLE A3
#define USUT A4
#define USUE A5
#define US_BUFSIZE 30

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

void shiftArray(float* arr) {
  for (int i = 0; i < US_BUFSIZE-1; ++i) {
    arr[i] = arr[i + 1];
  }
}


void setup() {
  Serial.begin(38400);
  Serial.print("-start-");
  svo.attach(9);
  motor.setSpeed(200);
  motor.run(RELEASE);

  pinMode(A0, OUTPUT);
//  pinMode(A1, INPUT);
  pinMode(A2, OUTPUT);
//  pinMode(A3, INPUT);
  pinMode(A4, OUTPUT);
//  pinMode(A5, INPUT);

  if (_ZEROCHECK) {
    svo.write(90);
    while(1);
  }
}

bool dir = true;

// debug led
void dl(bool o) {
  digitalWrite(13, o);
}

float buf_dl[30];
float buf_dr[30];
float buf_du[30];

// buffer average
float bufavg(float* arr) {
  int length = US_BUFSIZE;
  
  if (length == 0) { // handle edge case where array is empty
    return 0.0f; // or some other default value that makes sense
  }

  float sum = 0.0f;
  for (int i = 0; i < length; ++i) {
    sum += arr[i];
  }

  return sum / length;
}

float measureDist(int sensor) {
  
  //              T  E
  int uPins[2] = {0, 0};
  
  if (sensor < 0) {
    uPins[0] = USLT;
    uPins[1] = USLE;
  }
  if (sensor == 0) {
    uPins[0] = USUT;
    uPins[1] = USUE;
  }
  if (sensor > 0) {
    uPins[0] = USRT;
    uPins[1] = USRE;
  }
  
  // send pulse
  digitalWrite(uPins[0], LOW);
  delayMicroseconds(10);
  digitalWrite(uPins[0], HIGH);
  delayMicroseconds(2);
  digitalWrite(uPins[0], LOW);

  // Start timing after the HIGH pulse
  long duration = pulseIn(uPins[1], HIGH, 50000UL);

  if (duration == -1) {
    // Timeout occurred, return -1.0f
    return -1.0f;
  }
  else {
    // Calculate distance using the formula: distance = speed * time / 2
    float distance = (duration * 0.034 / 2);

    if (sensor < 0) {
      shiftArray(buf_dl);
      buf_dl[US_BUFSIZE - 1] = distance;
      distance = bufavg(buf_dl);
    }
    if (sensor == 0) {
      shiftArray(buf_du);
      buf_du[US_BUFSIZE - 1] = distance;
      distance = bufavg(buf_du);
    }
    if (sensor > 0) {
      shiftArray(buf_dr);
      buf_dr[US_BUFSIZE - 1] = distance;
      distance = bufavg(buf_dr);
    }

    return distance;
  }
}

void loop() {
  
//  while(0) {
//    Serial.println(measureDist(1));
////    digitalWrite(USLT, LOW);
////    delayMicroseconds(10);
////    digitalWrite(USLT, HIGH);
////    delayMicroseconds(2);
////    digitalWrite(USLT, LOW);
////  
////    // Start timing after the HIGH pulse
////    long duration = pulseIn(USLE, HIGH, 50000UL);
////    Serial.println(duration);
////  }

  // > ??
  // < 90

  Serial.println("began program");

  for (int i = 0; i < 30; i++) {
    measureDist(0);
  }
  
  while (1)//for (int lap = 0; lap < 3; lap++) {
    while (1) //for (int i = 0; i < 4; i++) {
      steer(-10);
      mspd(FWD, 200);

//      if (lap == 0 and i == 0) delay(600);

      float distF = measureDist(0);
      float distR = measureDist(1);
//      float distL = measureDist(-1);
      while(1) {
        distR = measureDist(1);
        distF = measureDist(0);
        Serial.println("gotten: " + String(distF));
        if (distF < 80) { // is front wall close enough?
          distR = measureDist(1);
          if ((distR) > 90) { // is right wall in sight?
            dir = true; // if so, direction should be set to right
          }
          else {
            dir = false; // if not, direction should be set to left
          }
          break;
        }
      }

      Serial.println("rt dist at fwd" + String(distR));
      // brake + reverse
      mspd(BWD, 170); // previously (150 then 170 then 200);
      delay(700); // previously (2200 (with 170 speed))
      
//      int fwdDelay = 1000;
//      if (i == 1) fwdDelay = 700;
//      if (i == 1 and lap == 1) fwdDelay = 1200;
//      delay(fwdDelay);
    
      steer(dir ? 50 : -80); // previously 50
      mspd(FWD, 200); // previously (150 then 170);
//      delay(dir ? 2000 : 2000); // previously (2200 (with 170 speed))
      for (int i = 0; i < 30; i++) {
        delay(dir ? (1200/30) : (1600/30));
        buf_du[i] = 110.0;
      }
  
  steer(0);
  mspd(FWD, 255); delay(750);
  
  mspd(FWD, 0);
  while(1); // halt code
}
