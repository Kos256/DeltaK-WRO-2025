#include <Servo.h>

Servo svo;

int in3 = 9;
int in4 = 4;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  svo.attach(10);
  svo.write(90);
  mDir(0);
}

void loop() {
  // put your main code here, to run repeatedly:
//  mDir(1);
//  delay(1000);
//  mDir(0);
//  delay(1000);
//  mDir(-1);
//  delay(1000);
//  mDir(0);
//  delay(1000);

  svo.write(90);
  setSpeed(255);
  delay(1000);

  svo.write(180);
  setSpeed(100);
  delay(1000);
  
  svo.write(90);
  setSpeed(255);
  delay(1000);
  
  svo.write(0);
  setSpeed(100);
  delay(1000);
}

void mDir(int d) {
  digitalWrite(in3, (d == 1) ? HIGH : LOW);
  digitalWrite(in4, (d == -1) ? HIGH : LOW);
}

void setSpeed(int d) {
  if (d == 0) {
    analogWrite(in3, 0);
    analogWrite(in4, 0);
  }

  if (d > 0) {
    analogWrite(in3, d%256);
    analogWrite(in4, 0);
  }

  if (d < 0) {
    analogWrite(in3, 0);
    analogWrite(in4, d%256);
  }
}
