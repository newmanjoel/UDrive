#include "motor_controller.h"
#include "DRV8704.h"

#define DATAOUT 11//MOSI
#define DATAIN  12//MISO
#define SPICLOCK  13//sck
#define SLAVESELECT 10//ss


bool stringComplete = false;
String toSend = "";
unsigned long time;
unsigned long motor_time;

Motor m1;
DRV8704 mc;
// DRV8704_Settings mc_settings; // in the future for more testing this will need to be changed

void setup() {
  SerialUSB.begin(9600); // Initialize Serial Monitor USB
  Serial1.begin(9600); // Initialize hardware serial port, pins 0/1
  // Must have both lines!
  while (!SerialUSB) ; // Wait for Serial monitor to open
  // Send a welcome message to the serial monitor:

  m1.begin(2, 5, 7, 5);
  m2.begin(6, 7, 7, 5);
  mc.begin(SLAVESELECT);
  attachInterrupt(digitalPinToInterrupt(7), isr_m1_a, CHANGE);
  //attachInterrupt(digitalPinToInterrupt(5), isr_m1_b, CHANGE);
  motor_time = time= millis();
  m1.EnablePID();
  m1.SetSetpoint(0);
  pinMode(3, OUTPUT);
  digitalWrite(3, false); // this is the reset pin
  pinMode(4, OUTPUT);
  digitalWrite(4, true); // this is the sleep pin // leave this pin alone
  pinMode(DATAOUT, OUTPUT);
  pinMode(DATAIN, INPUT);
  pinMode(SPICLOCK, OUTPUT);
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


  if (millis() - time > 1) {
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
      m2.SetSetpoint(toSend.substring(first_comma+1, second_comma).toFloat());
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
      double manual_speed_2 = (double) toSend.substring(first_comma+1, second_comma).toFloat();
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
    else if (first.equals("D")) {
      m1.SetWheelSize((double) toSend.substring(1).toFloat());
      m2.SetWheelSize(m1.GetWheelSize());
    }
    else if (first.equals("T")) {
      // set the ticks per rev
    }
    else if (first.equals("A")) {
      // set the max acceleration
    }


  }
}





