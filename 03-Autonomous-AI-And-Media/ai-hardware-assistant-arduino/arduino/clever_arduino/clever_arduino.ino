#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);
Servo s;

// ================= PINS =================
int soundPin = 3;   // SOUND D3
int pirPin = 2;     // MOTION D2
int ledPin = 7;     // LED D7

// ================= SYSTEM =================
String input = "";
String state = "READY";

// ================= CLAP =================
bool lastSoundState = HIGH;   // 🔥 inverted
unsigned long lastClapTime = 0;

// ================= MOTION =================
int motionCount = 0;
bool motionCooldown = false;
unsigned long motionTime = 0;

// ================= SERVO =================
int servoPos = 90;
bool servoDir = true;
unsigned long lastServoMove = 0;

// ================= LCD =================
bool showMessageMode = false;
String currentMsg = "";
int charIndex = 0;
int dots = 0;
unsigned long lastUpdate = 0;
unsigned long messageTime = 0;

// ================= SETUP =================
void setup() {
  Serial.begin(9600);

  pinMode(soundPin, INPUT);
  pinMode(pirPin, INPUT);
  pinMode(ledPin, OUTPUT);

  s.attach(10);

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0,0);
  lcd.print("CLEVER AI");
  lcd.setCursor(0,1);
  lcd.print("Ready...");

  Serial.println("ARD:READY");
}

// ================= LOOP =================
void loop() {

  readSerial();

  checkClap();
  checkMotion();

  if (showMessageMode) typingEffect();
  else stateAnimation();
}

// ================= CLAP (FIXED 1111) =================
void checkClap() {

  int sound = digitalRead(soundPin);

  // 🔥 inverted detection (1111 fix)
  if (sound == LOW && lastSoundState == HIGH &&
      millis() - lastClapTime > 1200) {

    Serial.println("👏 Clap Detected");

    clapAction();

    lastClapTime = millis();
  }

  lastSoundState = sound;
}

// ================= MOTION =================
void checkMotion() {

  if (motionCooldown) {
    if (millis() - motionTime > 120000) {
      motionCooldown = false;
      motionCount = 0;
      Serial.println("🚶 Motion UNLOCKED");
    }
    return;
  }

  if (digitalRead(pirPin) == HIGH) {

    Serial.println("🚶 Motion Detected");

    motionCount++;

    motionAction();

    delay(2000);

    if (motionCount >= 3) {

      Serial.println("⛔ LOCK 2 MIN");

      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print("Sleeping...");
      lcd.setCursor(0,1);
      lcd.print("Do not disturb");

      digitalWrite(ledPin, LOW);

      motionCooldown = true;
      motionTime = millis();

      delay(2000);
      lcd.clear();
    }
  }
}

// ================= SERIAL =================
void readSerial() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      processCommand(input);
      input = "";
    } else {
      input += c;
    }
  }
}

void processCommand(String cmd) {
  cmd.trim();

  if (cmd == "PING") Serial.println("PONG");

  else if (cmd.startsWith("LCD:")) {
    currentMsg = cmd.substring(4);
    charIndex = 0;
    lcd.clear();
    showMessageMode = true;
    messageTime = millis();
  }

  else if (cmd == "CLEAR") {
    lcd.clear();
    showMessageMode = false;
  }

  else if (cmd.startsWith("STATE:")) {
    state = cmd.substring(6);
  }

  else if (cmd == "LED_ON") digitalWrite(ledPin, HIGH);
  else if (cmd == "LED_OFF") digitalWrite(ledPin, LOW);
  else if (cmd == "SERVO") servoMove();
}

// ================= ACTIONS =================
void servoMove() {
  for(int i=70;i<=110;i++){
    s.write(i);
    delay(8);
  }
  for(int i=110;i>=70;i--){
    s.write(i);
    delay(8);
  }
}

void clapAction() {

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Clap Detected!");
  lcd.setCursor(0,1);
  lcd.print("Hello 😎");

  digitalWrite(ledPin, HIGH);
  servoMove();
  digitalWrite(ledPin, LOW);

  delay(1500);
  lcd.clear();
}

void motionAction() {

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Motion!");
  lcd.setCursor(0,1);
  lcd.print("Welcome Human");

  digitalWrite(ledPin, HIGH);
  servoMove();
  digitalWrite(ledPin, LOW);

  delay(1500);
  lcd.clear();
}

// ================= LCD =================
void typingEffect() {

  if (millis() - lastUpdate < 40) return;
  lastUpdate = millis();

  if (charIndex < currentMsg.length()) {

    int row = (charIndex < 16) ? 0 : 1;
    int col = (charIndex < 16) ? charIndex : charIndex - 16;

    lcd.setCursor(col, row);
    lcd.print(currentMsg[charIndex]);

    charIndex++;
  }

  if (charIndex >= currentMsg.length() && millis() - messageTime > 2000) {
    lcd.clear();
    showMessageMode = false;
  }
}

// ================= STATE =================
void stateAnimation() {

  if (millis() - lastUpdate < 400) return;
  lastUpdate = millis();

  lcd.setCursor(0,0);

  if (state == "LISTENING") {
    lcd.print("Listening...   ");
    lcd.setCursor(0,1);
    lcd.print("Speak now      ");
  }

  else if (state == "THINKING") {
    lcd.print("Thinking...    ");
    lcd.setCursor(0,1);
    lcd.print("Processing");

    for (int i=0;i<dots;i++) lcd.print(".");
    dots = (dots+1)%4;
  }

  else if (state == "SPEAKING") {

    lcd.print("AI Speaking... ");
    lcd.setCursor(0,1);
    lcd.print("Talking...     ");

    // 🔥 smooth servo
    if (millis() - lastServoMove > 20) {
      lastServoMove = millis();

      if (servoDir) servoPos++;
      else servoPos--;

      if (servoPos >= 110) servoDir = false;
      if (servoPos <= 70) servoDir = true;

      s.write(servoPos);
    }
  }

  else {
    lcd.print("CLEVER AI      ");
    lcd.setCursor(0,1);
    lcd.print("Ready...       ");
  }
}