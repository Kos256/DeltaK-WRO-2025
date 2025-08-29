int in3 = 3;
int in4 = 4;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  mDir(0);
}

void loop() {
  // put your main code here, to run repeatedly:
  mDir(1);
  delay(1000);
  mDir(0);
  delay(1000);
  mDir(-1);
  delay(1000);
  mDir(0);
  delay(1000);
}

void mDir(int d) {
  digitalWrite(in3, (d == 1) ? HIGH : LOW);
  digitalWrite(in4, (d == -1) ? HIGH : LOW);
}
