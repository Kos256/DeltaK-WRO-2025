void setup() {
  pinMode(9, OUTPUT);
  analogWrite(9, 0);
  Serial.begin(9600);

  while (Serial.available()) Serial.read();

  Serial.print("Send any input to start calibration...");
  while (!Serial.available()) { Serial.print('.'); delay(1000); }
  Serial.println("");  
  String spdInput = Serial.readStringUntil('\n'); // drain serial buffer

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
  while (!Serial.available());
  String spdInput = Serial.readStringUntil('\n');
//  spd = spdInput.toInt();
  analogWrite(9, spd);
  Serial.println("ESC signal: " + String(spd) + "(" + String(btp(spd)) + "% byte duty)");
}

// BTP: byte to percentage (converter)
float btp (int by) {
  return by%256 / 255.0 * 100;
}
