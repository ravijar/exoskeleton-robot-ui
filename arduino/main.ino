void setup() {
  Serial.begin(9600);     // USB serial to PC
  pinMode(13, OUTPUT);    // Built-in LED
  randomSeed(analogRead(0)); // Initialize random seed
}

void loop() {
  // Generate and send random x, y, z values
  float x = random(0, 1000) / 10.0;  // e.g., 0.0 to 99.9
  float y = random(0, 1000) / 10.0;
  float z = random(0, 1000) / 10.0;

  Serial.print(x); Serial.print(",");
  Serial.print(y); Serial.print(",");
  Serial.println(z);

  delay(100);  // Send every 100 ms

  // Handle incoming LED command
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "LED_ON") digitalWrite(13, HIGH);
    else if (cmd == "LED_OFF") digitalWrite(13, LOW);
  }
}