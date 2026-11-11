#include <Wire.h>
#include <hd44780.h>
#include <hd44780ioClass/hd44780_I2Cexp.h>

#define PLAY_PIN 4

hd44780_I2Cexp lcd;

void setup() {
  pinMode(PLAY_PIN, OUTPUT);

  lcd.begin(16, 2);
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("AI Assistant");

  lcd.setCursor(0, 1);
  lcd.print("Starting...");

  // ISD play trigger
  digitalWrite(PLAY_PIN, HIGH);
  delay(300);
  digitalWrite(PLAY_PIN, LOW);
}

void loop() {
}
