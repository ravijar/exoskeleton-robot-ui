void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT);
  randomSeed(analogRead(0));
}

void loop() {
  handleSerialCommand();  // continuously check for new commands
  delay(50);              // small delay to ease serial processing
}

// --- Serial Command Handler ---
void handleSerialCommand() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "GET_ENCODER_VALUE") {
      int enc = getEncoderValue();
      Serial.print("ENCODER_VALUE:");
      Serial.println(enc);
    } else if (cmd.startsWith("SET_ENCODER_VALUE:")) {
      String valStr = cmd.substring(cmd.indexOf(':') + 1);
      Serial.println("ENCODER_VALUE_SET");
    } else {
      Serial.println("UNKNOWN_COMMAND");
    }
  }
}

// --- Simulate Encoder Value ---
int getEncoderValue() {
  return random(0, 30001);  // 0–30000
}
