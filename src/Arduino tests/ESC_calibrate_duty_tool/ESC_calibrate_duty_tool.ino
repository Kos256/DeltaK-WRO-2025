void setup() {
  pinMode(10, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  while (!Serial.available());
  String spdInput = Serial.readStringUntil('\n');
  int spd = spdInput.toInt();
  analogWrite(10, spd);
  Serial.println("ESC position: " + String(spd));
}
