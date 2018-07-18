#include "motor_controller.h"
#include "DRV8704.h"

#define DATAOUT 11//MOSI
#define DATAIN  12//MISO
#define SPICLOCK  13//sck
#define SLAVESELECT 10//ss 
#define RESET 9
#define SLEEP 8

#define AOUT1 2
#define AOUT2 3
#define BOUT1 4
#define BOUT2 5

#define ENCODERA 6
#define ENCODERB 7

bool reset_pin = false;
bool sleep_pin = true;



bool stringComplete = false;
String toSend = "";
unsigned long time;
unsigned long motor_time;

Motor m1;
Motor m2;
DRV8704 mc;
// DRV8704_Settings mc_settings; // in the future for more testing this will need to be changed

void setup() {
  SerialUSB.begin(9600); // Initialize Serial Monitor USB
  Serial1.begin(9600); // Initialize hardware serial port, pins 0/1
  // Must have both lines!
  while (!SerialUSB) ; // Wait for Serial monitor to open
  // Send a welcome message to the serial monitor:

  m1.begin(AOUT1, AOUT2, ENCODERA, ENCODERB);
  m2.begin(BOUT1, BOUT2, -1, -1);
  mc.begin(SLAVESELECT);
  mc.set_enable(true);// untested

  attachInterrupt(digitalPinToInterrupt(ENCODERA), isr_m1_a, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODERB), isr_m1_b, CHANGE);
  motor_time = time = millis();
  m1.EnablePID();
  m1.SetSetpoint(0);
  m2.EnablePID();
  m2.SetSetpoint(0);
  pinMode(RESET, OUTPUT);
  digitalWrite(RESET, reset_pin); // this is the reset pin
  pinMode(SLEEP, OUTPUT);
  digitalWrite(SLEEP, sleep_pin); // this is the sleep pin // leave this pin alone
  pinMode(SLAVESELECT, OUTPUT);
  delay(10);
}

void isr_m1_a() {
  m1.isrA();
}
void isr_m1_b() {
  m1.isrB();
}


void loop() {
  if (stringComplete) {
    SerialUSB.println("Sending " + toSend + " to Serial");
    stringComplete = false;
  }
  serialEvent();

  m1.Update();
  m2.Update();


  if (millis() - time > 100) {
    double offset = 0;
    double voltage = (double) analogRead(A0);
    double m1_current = voltage * 3.3 / 1000 - offset;

    SerialUSB.print(m1.GetRawInput());
    SerialUSB.print(",");
    SerialUSB.print(m1.GetSetpoint());
    SerialUSB.print(",");
    SerialUSB.print(m1.GetOutput());
    SerialUSB.print(",");
    SerialUSB.print(m1_current);
    SerialUSB.print(",");
    SerialUSB.print(m2.GetRawInput());
    SerialUSB.print(",");
    SerialUSB.print(m2.GetSetpoint());
    SerialUSB.print(",");
    SerialUSB.print(m2.GetOutput());
    SerialUSB.print(",");
    SerialUSB.println(m1_current);
    //mc.read_status();

    time = millis();
  }

}

void serialEvent() {
  static int speed;

  if (SerialUSB.available()) { // If data is sent to the monitor
    toSend = ""; // Create a new string
    while (SerialUSB.available()) { // While data is available
      // Read from SerialUSB and add to the string:
      toSend += (char)SerialUSB.read();
    }
    stringComplete = true;
    String first = toSend.substring(0, 1);
    if (first.equals("V")) {
      int first_comma = toSend.indexOf(',', 1);
      int second_comma = toSend.indexOf(',', first_comma + 1);
      m1.SetSetpoint(toSend.substring(1, first_comma).toFloat());
      m1.EnablePID();
      m2.SetSetpoint(toSend.substring(first_comma + 1, second_comma).toFloat());
      m2.EnablePID();
    }
    else if (first.equals("P")) {
      int first_comma = toSend.indexOf(',', 1);
      int second_comma = toSend.indexOf(',', first_comma + 1);
      double kp = (double) toSend.substring(1, first_comma).toFloat();
      double ki = (double) toSend.substring(first_comma + 1, second_comma).toFloat();
      double kd = (double) toSend.substring(second_comma + 1).toFloat();
      m1.SetPIDGains(kp, ki, kd);
    }
    else if (first.equals("M")) {
      int first_comma = toSend.indexOf(',', 1);
      int second_comma = toSend.indexOf(',', first_comma + 1);
      double manual_speed_1 = (double) toSend.substring(1, first_comma).toFloat();
      double manual_speed_2 = (double) toSend.substring(first_comma + 1, second_comma).toFloat();
      m1.Manual(manual_speed_1);
      m2.Manual(manual_speed_2);
    }
    else if (first.equals("E")) {
      bool local_enable = false;
      local_enable = (bool) toSend.substring(1, 2);
      if (local_enable) {
        m1.EnablePID();
        m2.EnablePID();
      }
      else {
        m1.DisablePID();
        m2.DisablePID();
      }
    }
    else if (first.equals("W")) {
      m1.SetWheelSize((double) toSend.substring(1).toFloat());
      m2.SetWheelSize(m1.GetWheelSize());
    }
    else if (first.equals("T")) {
      // set the position that you want to go to (go To)
      
    }
    else if (first.equals("A")) {
      // set the max acceleration
    }
    else if (first.equals("R")) {
      // toggle the reset pin
      reset_pin = !reset_pin;
      digitalWrite(RESET, reset_pin);
    }
    else if ( first.equals("S")) {
      // toggle the sleep pin
      sleep_pin = !sleep_pin;
      digitalWrite(SLEEP, sleep_pin);
    }
    else if ( first.equals("D")) {
      // set the settings for the DRV8704
      // have 14 values in total
      DRV8704_Settings new_settings = mc.get_settings();
      int comma_1 = toSend.indexOf(',', 1);
      int comma_2 = toSend.indexOf(',', comma_1 + 1);
      int comma_3 = toSend.indexOf(',', comma_2 + 1);
      int comma_4 = toSend.indexOf(',', comma_3 + 1);
      int comma_5 = toSend.indexOf(',', comma_4 + 1);
      int comma_6 = toSend.indexOf(',', comma_5 + 1);
      int comma_7 = toSend.indexOf(',', comma_6 + 1);
      int comma_8 = toSend.indexOf(',', comma_7 + 1);
      int comma_9 = toSend.indexOf(',', comma_8 + 1);
      int comma_10 = toSend.indexOf(',', comma_9 + 1);
      int comma_11 = toSend.indexOf(',', comma_10 + 1);
      int comma_12 = toSend.indexOf(',', comma_11 + 1);
      int comma_13 = toSend.indexOf(',', comma_12 + 1);

      int enable = (int)toSend.substring(1, comma_1).toInt();
      int A_gain = (int)toSend.substring(comma_1 + 1, comma_2).toInt();
      int dead_time = (int)toSend.substring(comma_2 + 1, comma_3).toInt();
      int torque = (int)toSend.substring(comma_3 + 1, comma_4).toInt();
      int time_off = (int)toSend.substring(comma_4 + 1, comma_5).toInt();
      int blank_time = (int)toSend.substring(comma_5 + 1, comma_6).toInt();
      int decay_time = (int)toSend.substring(comma_6 + 1, comma_7).toInt();
      int decay_mode = (int)toSend.substring(comma_7 + 1, comma_8).toInt();
      int ocp_thresh = (int)toSend.substring(comma_8 + 1, comma_9).toInt();
      int ocp_time = (int)toSend.substring(comma_9 + 1, comma_10).toInt();
      int gd_sink_time = (int)toSend.substring(comma_10 + 1, comma_11).toInt();
      int gd_source_time = (int)toSend.substring(comma_11 + 1, comma_12).toInt();
      int gd_sink_current = (int)toSend.substring(comma_12 + 1, comma_13).toInt();
      int gd_source_current = (int)toSend.substring(comma_13 + 1).toInt();

      if(enable == 1){
        new_settings.enabled = ENBL_Values::ENABLE;
      }
      else{
        new_settings.enabled = ENBL_Values::DISABLE;
      }
      
      
    }


  }
}





