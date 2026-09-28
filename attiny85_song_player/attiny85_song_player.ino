/*
 * ATtiny85 SSTC Interrupter (Fixed Tempo, Volume-Only Control)
 * -------------------------------------------------------------------------
 * Pin Map:
 *   A3 (PB3) - Volume / Pulse-Width Potentiometer
 *   D1 (PB1) - Output to Gate Driver / Optocoupler
 * -------------------------------------------------------------------------
 */

#include <avr/io.h>
#include <avr/pgmspace.h>
#include <avr/wdt.h>

#include "song_data.h"

// ---------------- Pin Assignments ----------------
const uint8_t VOL_PIN  = A3;  // Volume pot only
const uint8_t GATE_PIN = 1;   // PB1 -> Optocoupler / Driver

// ---------------- 300V Safety Constraints ----------------
const uint16_t MIN_ON_TIME_US      = 100;  // Minimum for arc breakdown
const uint16_t ABSOLUTE_MAX_ON_US  = 1000; // 1ms pulse width ceiling
const uint16_t MIN_OFF_TIME_US     = 150;  // Gate discharge margin
const uint8_t  MAX_DUTY_CYCLE_PERC = 10;   // Dynamic 10% duty cycle cap

void setup() {
  wdt_disable(); // Watchdog disabled to prevent RF reset loops
  
  pinMode(GATE_PIN, OUTPUT);
  digitalWrite(GATE_PIN, LOW);
  
  pinMode(VOL_PIN, INPUT);
}

void loop() {
  playCompressedSong(full_midi_song, full_midi_song_len);
  delay(1500); // 1.5s delay before repeating
}

void playCompressedSong(const CompressedNote *song, uint16_t len) {
  for (uint16_t i = 0; i < len; i++) {
    uint8_t noteIdx = pgm_read_byte(&song[i].note_idx);
    uint8_t ticks   = pgm_read_byte(&song[i].ticks);
    
    uint16_t freq   = pgm_read_word(&note_freqs[noteIdx]);
    uint32_t dur_ms = (uint32_t)ticks * BASE_TICK_MS; // Fixed 1:1 speed

    playNote(freq, (uint16_t)dur_ms);
    
    digitalWrite(GATE_PIN, LOW);
    
    // Staccato articulation gap between notes
    uint32_t restTime = dur_ms / 10;
    if (restTime > 0) {
      delay(restTime);
    }
  }
}

void playNote(uint16_t freq, uint16_t duration_ms) {
  if (freq == 0 || duration_ms == 0) {
    digitalWrite(GATE_PIN, LOW);
    if (duration_ms > 0) delay(duration_ms);
    return;
  }

  uint32_t periodUs = 1000000UL / freq;
  
  // Calculate dynamic 10% duty cycle limit per note pitch
  uint32_t dutyMaxOn = (periodUs * MAX_DUTY_CYCLE_PERC) / 100;
  uint32_t hardMaxOn = (periodUs > MIN_OFF_TIME_US) ? (periodUs - MIN_OFF_TIME_US) : 0;
  
  uint16_t safeMaxOnTime = ABSOLUTE_MAX_ON_US;
  if (dutyMaxOn < safeMaxOnTime) safeMaxOnTime = (uint16_t)dutyMaxOn;
  if (hardMaxOn < safeMaxOnTime) safeMaxOnTime = (uint16_t)hardMaxOn;

  if (safeMaxOnTime < MIN_ON_TIME_US) {
    safeMaxOnTime = MIN_ON_TIME_US;
  }

  // Read volume potentiometer and enforce safety cap
  uint16_t requestedOnTime = readVolumePulseWidth();
  uint16_t onTime = (requestedOnTime > safeMaxOnTime) ? safeMaxOnTime : requestedOnTime;

  if (onTime >= periodUs) {
    onTime = periodUs / 2;
  }

  uint32_t offTime = periodUs - onTime;
  uint32_t numCycles = ((uint32_t)duration_ms * 1000UL) / periodUs;

  for (uint32_t i = 0; i < numCycles; i++) {
    digitalWrite(GATE_PIN, HIGH);
    delayMicroseconds(onTime);
    
    digitalWrite(GATE_PIN, LOW);
    
    uint32_t remainingOff = offTime;
    while (remainingOff > 10000) {
      delayMicroseconds(10000);
      remainingOff -= 10000;
    }
    delayMicroseconds(remainingOff);
  }
  
  digitalWrite(GATE_PIN, LOW);
}

// Reads Volume Potentiometer (A3) with floor & noise filtering
uint16_t readVolumePulseWidth() {
  uint32_t sum = 0;
  for (uint8_t i = 0; i < 4; i++) {
    sum += analogRead(VOL_PIN);
  }
  uint16_t raw = sum / 4;
  uint16_t val = map(raw, 0, 1023, MIN_ON_TIME_US, ABSOLUTE_MAX_ON_US);
  return (val < MIN_ON_TIME_US) ? MIN_ON_TIME_US : val;
}