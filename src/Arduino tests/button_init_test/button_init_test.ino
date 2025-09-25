int iBtn = 12;

int c = -1;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(38400);
  pinMode(iBtn, INPUT_PULLUP);

  delay(500);
  while(digitalRead(iBtn));
  Serial.println("btn routine started");
  bool startpgm = false;
  while(1) {
    c++;
    if (c >= 13) c = 1;
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
}
int pos = 0;
bool mirror = false;

void loop() {
  if (c <= 6) mirror = false;
  else mirror = true;
  if (c <= 6) {
    pos = c;
  }
  else pos = c - 6;
  
  Serial.println("PROGRAM SENT!");
  Serial.print("Recieved value: ");
  Serial.println(c);
  Serial.println("");
  Serial.print("POSITION: "); Serial.println(pos);
  Serial.print("MIRROR??: "); Serial.println(mirror ? "yes" : "no");
  while(1);
}
