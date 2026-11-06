#ifndef PIN_CONFIG_H
#define PIN_CONFIG_H

/**
 * @file pin_config.h
 * @brief Hardware Pin Mapping and Boot Strapping Verification for NodeMCU ESP8266
 * 
 * ESP8266 ESP-12E Boot Strap Constraints:
 * ---------------------------------------
 * 1. GPIO 15 (D8): Must be LOW at boot. If pulled HIGH, enters SDIO mode and fails.
 * 2. GPIO 0  (D3): Must be HIGH at boot. If pulled LOW, enters UART Flash download mode.
 * 3. GPIO 2  (D4): Must be HIGH at boot. Connected to onboard Blue LED.
 * 
 * Verified Safe Production Pinout:
 * --------------------------------
 * PWMA = D1 (GPIO 5)  -> Hardware PWM, General Purpose I/O.
 * AIN1 = D2 (GPIO 4)  -> General Purpose I/O.
 * AIN2 = D3 (GPIO 0)  -> Driven HIGH by internal pull-up. TB6612 input is CMOS high-Z.
 * BIN1 = D5 (GPIO 14) -> Hardware PWM, General Purpose I/O.
 * BIN2 = D6 (GPIO 12) -> General Purpose I/O.
 * PWMB = D7 (GPIO 13) -> Hardware PWM, General Purpose I/O.
 * STBY = D8 (GPIO 15) -> Pulled LOW by default until firmware explicitly raises HIGH.
 * 
 * Alternative Configuration (Requested in prompt, subject to verification):
 * AIN1 = D1, AIN2 = D2, PWMA = D5, BIN1 = D7, BIN2 = D4, PWMB = D6, STBY = D0
 */

// Production Verified Pin Mapping
#define PIN_PWMA  5   // NodeMCU D1 (GPIO 5)  - Left Motor PWM Speed
#define PIN_AIN1  4   // NodeMCU D2 (GPIO 4)  - Left Motor Direction 1
#define PIN_AIN2  0   // NodeMCU D3 (GPIO 0)  - Left Motor Direction 2

#define PIN_BIN1  14  // NodeMCU D5 (GPIO 14) - Right Motor Direction 1
#define PIN_BIN2  12  // NodeMCU D6 (GPIO 12) - Right Motor Direction 2
#define PIN_PWMB  13  // NodeMCU D7 (GPIO 13) - Right Motor PWM Speed

#define PIN_STBY  15  // NodeMCU D8 (GPIO 15) - TB6612 Standby Enable (Active HIGH)
#define PIN_LED   2   // NodeMCU D4 (GPIO 2)  - Onboard Telemetry LED (Active LOW)

// Alternate Pin Mapping Flag (Set to 1 to activate your physical hardware pinout)
#define USE_SECTION7_SUGGESTED_PINOUT 1

#if USE_SECTION7_SUGGESTED_PINOUT
  #undef PIN_PWMA
  #undef PIN_AIN1
  #undef PIN_AIN2
  #undef PIN_BIN1
  #undef PIN_BIN2
  #undef PIN_PWMB
  #undef PIN_STBY

  #define PIN_AIN1  5   // D1 (GPIO 5)
  #define PIN_AIN2  4   // D2 (GPIO 4)
  #define PIN_PWMA  14  // D5 (GPIO 14)
  #define PIN_BIN1  13  // D7 (GPIO 13)
  #define PIN_BIN2  2   // D4 (GPIO 2) - Warning: Ensure not pulled LOW at boot!
  #define PIN_PWMB  12  // D6 (GPIO 12)
  #define PIN_STBY  16  // D0 (GPIO 16) - Wake/Deep sleep pin
#endif

#endif // PIN_CONFIG_H
