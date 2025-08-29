#include <Servo.h>

Servo svo;

void setup() {
  Serial.begin(9600);
  
  pinMode(9, OUTPUT);
  analogWrite(9, 0);
  svo.attach(10);

  svo.write(90);

  while (Serial.available()) Serial.read();

//  Serial.print("Send any input to start calibration...");
//  while (!Serial.available()) { Serial.print('.'); delay(1000); }
//  Serial.println("");  
//  String spdInput = Serial.readStringUntil('\n'); // drain serial buffer

  delay(1000);

  analogWrite(9, 50);
  Serial.println("Sent lower bound (50/255)");
  delay(2000);

  analogWrite(9, 250);
  Serial.println("Sent higher bound (250/255)");
  delay(1000);

  analogWrite(9, 40);
  Serial.println("Sent off signal (40/255)\nCalibration complete! (Send a byte to control speed)");

  
}

int spd = 40;

void loop() {
  analogWrite(9, 197);
  delay(1000);

  svo.write(90 + 30); analogWrite(9, 60);
  delay(500);

  analogWrite(9, 197);
  delay(1000);

  svo.write(90 - 30); analogWrite(9, 60);
  delay(500);
}

// BTP: byte to percentage (converter)
float btp (int by) {
  return by%256 / 255.0 * 100;
}
