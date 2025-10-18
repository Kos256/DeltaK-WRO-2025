#include <AFMotor.h>
#include <Servo.h>

#define FWD 1
#define BWD 2
#define BRK 3
#define REL 4

#define US_TRIG 2 // UltraSonic Trigger Pin
#define US_EL   3 // UltraSonic Echo Left Pin
#define US_ER   4 // UltraSonic Echo Right Pin 
#define uslt  false
#define usrt  true
#define NUM_READINGS 10 // The number of readings in the circular buffer.
#define BUFFER_SIZE (NUM_READINGS * 2) // Size of the buffer array.

AF_DCMotor motor(3);
Servo svo;

// Create two circular buffers, one for each sensor.
float usBufferL[NUM_READINGS];
int usIndexL = 0;
float usBufferR[NUM_READINGS];
int usIndexR = 0;

// Function to add a new reading to both buffers
void addReading(float value, bool side) {
  if (side == true) {
    usBufferR[usIndexR] = value;
    usIndexR = (usIndexR + 1) % NUM_READINGS; // Increment the index and wrap around when full.
  } else {
    usBufferL[usIndexL] = value;
    usIndexL = (usIndexL + 1) % NUM_READINGS; // Increment the index and wrap around when full.
  }
}

// Function to get the average of both buffers
float getAverage(bool side) {
  float sum = 0.0;

  if (side == true) {
    for (int i = 0; i < NUM_READINGS; ++i) {
      sum += usBufferR[i];
    }
  } else {
    for (int i = 0; i < NUM_READINGS; ++i) {
      sum += usBufferL[i];
    }
  }

  return sum / NUM_READINGS;
}

// Update the measureDist function to use both buffers
// false is left, true is right
float measureDist(bool side) {
   if (side && usIndexR != 0) { // only reset the index if we're on the right sensor and it's not empty
      usIndexR = 0;
   } else if (!side && usIndexL != 0) { // only reset the index if we're on the left sensor and it's not empty
      usIndexL = 0;
   }
    
  digitalWrite(US_TRIG, LOW);
  delayMicroseconds(10);
  digitalWrite(US_TRIG, HIGH);
  delayMicroseconds(2);
  digitalWrite(US_TRIG, LOW);

  long duration = pulseIn(side ? US_EL : US_ER, HIGH, 50000UL);

  if (duration == 0) {
    // Timeout → no echo detected
    return -1;
  }

  float dist = duration * 0.0343 / 2;
  addReading(dist, side);

  return getAverage(side);
}

// (set) motor speed
void mspd(int dir, int spd=255) {
  motor.setSpeed(spd);
  //if (dir != 0) motor.run(dir%4 + 1);
  motor.run(dir);
}

void steer(int dir) {
  svo.write(map(dir, 100, -100, 0, 180) - 10);
//  svo.write(map(dir, 70, -100, 0, 180));
}

void dled(bool on=true) {
  digitalWrite(13, on);
}

void setup() {
  Serial.begin(38400);
  pinMode(13, OUTPUT);
  pinMode(US_TRIG, OUTPUT);
  svo.attach(9);
  motor.setSpeed(200);
  motor.run(RELEASE);

  svo.write(90);
  for (int i = 0; i < 4; i++) {
    dled(1); delay(250);
    dled(0); delay(250);
  }

//  svo.write(0); while(1);
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

  
//  steer(0);
//  mspd(FWD);
//  delay(1300);
//
//  steer(50);
//  mspd(FWD, 150);
//  delay(2300);

  svo.write(90 - 25);
  mspd(FWD, 150);

  while(1) {
    float distR = measureDist(usrt);
    delay(50);
    Serial.print(distR);
    Serial.print(" ");
    String dState;
    
    if (distR < 1.5) {
      svo.write(180);
      dState = "d<2 (turn right farther from inner rect)  -";
    }
    else if (distR > 1.5) {
      svo.write(0);
      dState = "d>4 (turn left closer to inner rect)      +";
    }
    else {
      svo.write(90 + 20);
      dState = "2<d<4 (keep straight)                     /";
    }

    Serial.println(dState);
    
    if (distR > 18) break;
  }
  Serial.println("\n*\n-- TURNING --\n*");
  mspd(BRK);
  delay(20);
  svo.write(0);
  mspd(FWD, 90);
  
  delay(2000);

  svo.write(20);
  mspd(FWD, 70);
  
  delay(1000);
  mspd(REL);
//  svo.write(180);
//  while(1); 
}
