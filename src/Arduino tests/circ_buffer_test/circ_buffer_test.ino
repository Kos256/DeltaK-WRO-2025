int UBUFSUZE = 30; // U BUF SIZE = ultrasonic buffer size
float buf_dl[30];
float buf_dr[30];
float buf_du[30];

void shiftArray(float* arr) {
  for (int i = 0; i < UBUFSUZE-1; ++i) {
    arr[i] = arr[i + 1];
  }
}

void setup() {
  Serial.begin(38400);
  delay(100); // wait for serial to finish initalizing
  
  // initialize buffers
  for (int i = 0; i < UBUFSUZE; i++) {
    buf_dl[i] = 0;
  }
  for (int i = 0; i < UBUFSUZE; i++) {
    buf_dr[i] = 0;
  }
  for (int i = 0; i < UBUFSUZE; i++) {
    buf_du[i] = 0;
  }
}

// buffer average
float bufavg(float* arr) {
  int length = UBUFSUZE;
  
  if (length == 0) { // handle edge case where array is empty
    return 0.0f; // or some other default value that makes sense
  }

  float sum = 0.0f;
  for (int i = 0; i < length; ++i) {
    sum += arr[i];
  }

  return sum / length;
}

void showarr(float* arr) {
  int length = UBUFSUZE;
  Serial.print("array: ");
  for (int i = 0; i < length - 1; ++i) {
    Serial.print(arr[i]);
    Serial.print(", ");
  }
  Serial.println(arr[length - 1]);
}

void loop() {
  // put your main code here, to run repeatedly:
  bufavg(buf_dl);
  shiftArray(buf_dl);
  showarr(buf_dl);
  Serial.println("average: " + String(bufavg(buf_dl)));
  while(1);
}
