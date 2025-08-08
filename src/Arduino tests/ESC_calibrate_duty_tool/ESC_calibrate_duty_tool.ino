void setup() {
  pinMode(9, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  while (!Serial.available());
  String spdInput = Serial.readStringUntil('\n');
  int spd = spdInput.toInt();
  analogWrite(9, spd);
  Serial.println("ESC position: " + String(spd));
}
