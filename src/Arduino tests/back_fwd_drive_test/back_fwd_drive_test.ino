#include <Servo.h>

Servo svo;

int in1 = 5; // forwards
int in2 = 6; // backwards
int svoPin = 9; // servo

void setup() {
  // put your setup code here, to run once:
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  svo.attach(9);
  steer(0);
}

bool smoothTurn = true;

void loop() {
  // put your main code here, to run repeatedly:

  digitalWrite(in1, 1);
  delay(1000);
  digitalWrite(in1, 0);

  if (smoothTurn) {
    for (int i = -50; i < 50; i+=1) {
      steer(i);
      delay(5);
    }
    delay(500);
  }
  else {
    steer(50);
    delay(1000);
  }

  digitalWrite(in1, 1);
  delay(1000);
  digitalWrite(in1, 0);

  if (smoothTurn) {
    for (int i = 50; i > -50; i-=1) {
      steer(i);
      delay(5);
    }
    delay(500);
  }
  else {
    steer(-50);
    delay(1000);
  }
}

void steer(int d) {
  svo.write(map(d, -100, 100, 0, 180));
}

void speeder(int d) {
  // pass
}
