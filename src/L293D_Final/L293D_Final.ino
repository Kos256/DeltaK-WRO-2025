#include <AFMotor.h>
#include <Servo.h>

#define FWD 1
#define BWD 2
#define BRK 3
#define REL 4

// USRT, USRE, USLT, USLE (ultrasonic right/left trig/echo)
#define USRT A0
#define USRE A1
#define USLT A2
#define USLE A3
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

void setup() {
  Serial.begin(38400);
  svo.attach(9);
  motor.setSpeed(200);
  motor.run(RELEASE);

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

//// Circular buffers for left and right distance measurements
float buf_distL[US_BUFSIZE];
int buf_idx_L = 0;
int buf_count_L = 0;

float buf_distR[US_BUFSIZE];
int buf_idx_R = 0;
int buf_count_R = 0;

int head = 0; // Initialize the head pointer to the start of the buffer
int tail = 0; // Initialize the tail pointer to the start of the buffer
int count = 0; // Initialize the count variable

//void add(float value) {
//  // Add element to the end of the buffer (circularly)
//  buf_distR[head] = value;
//  head = (head + 1) % US_BUFSIZE;
//  if (count < US_BUFSIZE) count++;
//}
//
//float average() {
//  float sum = 0.0f;
//  for (int i = tail; i != head; ++i) {
//    sum += buf_distR[i];
//  }
//  // Add the last element in case it's not wrapped around
//  if (head > tail) {
//    sum += buf_distR[tail];
//  } else {
//    // Handle wraparound case
//    for (int i = US_BUFSIZE - 1; i >= tail; --i) {
//      sum += buf_distR[i];
//    }
//  }
//  return sum / count;
//}
long measureDist(bool isRightSensor) {
  // Set the trigger pin to LOW for 10us to ensure it's in a known state
  digitalWrite(isRightSensor ? USRT : USLT, LOW);
  delayMicroseconds(10);

  // Send a HIGH pulse to trigger the sensor
  digitalWrite(isRightSensor ? USRT : USLT, HIGH);
  delayMicroseconds(2);
  digitalWrite(isRightSensor ? USRT : USLT, LOW);

  // Start timing after the HIGH pulse
  long duration = pulseIn(isRightSensor ? USRE : USLE, HIGH, 70000UL);

  if (duration == -1) {
    // Timeout occurred, return -1.0f
    return -1.0f;
  }
  else {
    // Calculate distance using the formula: distance = speed * time / 2
    float distance = (duration * 0.034 / 2);
    Serial.println("long dur: " + String(distance));

    if (isRightSensor) {
      buf_distR[buf_idx_R] = distance;
      buf_count_R++;
      buf_idx_R++;

      // Reset counter when full
      if (buf_count_R >= US_BUFSIZE) {
        buf_count_R = 0;
      }

      // Calculate moving average for sensor
      float sum = 0.0f;
      int count = 0;

      // perform avg
      for (int i = 0; i < US_BUFSIZE; i++) {
        if (buf_distL[i] != -1) { // Ignore invalid readings
          sum += buf_distL[i];
          count++;
        }
      }

      // overwrite and apply averaged value
      distance = (count > 0) ? sum / count : distance;
    }
    else { // is left sensor
      buf_distL[buf_idx_L] = distance;
      buf_count_L++;
      buf_idx_L++;

      // Reset counter when full
      if (buf_count_L >= US_BUFSIZE) {
        buf_count_L = 0;
      }

      // Calculate moving average for sensor
      float sum = 0.0f;
      int count = 0;

      // perform avg
      for (int i = 0; i < US_BUFSIZE; i++) {
        if (buf_distR[i] != -1) { // Ignore invalid readings
          sum += buf_distR[i];
          count++;
        }
      }

      // overwrite and apply averaged value
      distance = (count > 0) ? sum / count : distance;
    }

    return distance;
  }

  
}

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


//  while(1) Serial.println(measureDist(true));
  
  for (int lap = 0; lap < 3; lap++) {
    for (int i = 0; i < 4; i++) {
      steer(-10);
      mspd(FWD, 255);

      if (lap == 0 and i == 0) delay(600);
      float distR = measureDist(true);
      while(1) {
        distR = measureDist(true);
        Serial.println("gotten: " + String(distR));
        if (distR > 70) { // wall is not in sight?
          if (distR < 9000) { // check if its not a false spike
            break;
          }
        }
      }

      delay(100);
      
//      int fwdDelay = 1000;
//      if (i == 1) fwdDelay = 700;
//      if (i == 1 and lap == 1) fwdDelay = 1200;
//      delay(fwdDelay);
    
      steer(50); // previously 50
      mspd(FWD, 200); // previously (150 then 170);
      delay(2000); // previously (2200 (with 170 speed))
    }
  }
  
  steer(0);
  mspd(FWD, 255); delay(750);
  
  mspd(FWD, 0);
  while(1); // halt code
}
