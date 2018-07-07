#include "motor_controller.h"


bool stringComplete = false;
String toSend = "";
unsigned long time;
unsigned long motor_time;

Motor m;

void setup() {
  SerialUSB.begin(9600); // Initialize Serial Monitor USB
  Serial1.begin(9600); // Initialize hardware serial port, pins 0/1
  // Must have both lines!
  while (!SerialUSB) ; // Wait for Serial monitor to open
  // Send a welcome message to the serial monitor:
  SerialUSB.println("Send character(s) to relay it over Serial1");

  m.begin(2, 3, 7, 5);
  attachInterrupt(digitalPinToInterrupt(7), isr_m1_a, CHANGE);
  attachInterrupt(digitalPinToInterrupt(5), isr_m1_b, CHANGE);
  time = millis();
  motor_time = millis();
  pinMode(6, OUTPUT);
  pinMode(A0, INPUT);
  m.EnablePID();
  m.SetSetpoint(-50);
}
void isr_m1_a() {
  m.isrA();
}
void isr_m1_b() {
  m.isrB();
}


void loop() {
  if (stringComplete) {
    SerialUSB.println("Sending " + toSend + " to Serial");
    stringComplete = false;
  }
  serialEvent();

  if (millis() - motor_time > 1) {
    m.Update();
    motor_time = millis();
  }

  if (millis() - time > 1) {
    double offset = 0;
    double voltage = 0;
    voltage = (double) analogRead(A0);
    double temp = voltage*3.3/1000 - offset;
    
    SerialUSB.print(m.GetRawInput());
    SerialUSB.print(",");
    SerialUSB.print(m.GetSetpoint());
    SerialUSB.print(",");
    SerialUSB.print(m.GetOutput());
    SerialUSB.print(",");
    SerialUSB.println(temp);
    

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
      m.SetSetpoint(toSend.substring(1, first_comma).toFloat());
      m.EnablePID();
    }
    else if (first.equals("P")) {
      int first_comma = toSend.indexOf(',', 1);
      int second_comma = toSend.indexOf(',', first_comma + 1);
      double kp = (double) toSend.substring(1, first_comma).toFloat();
      double ki = (double) toSend.substring(first_comma + 1, second_comma).toFloat();
      double kd = (double) toSend.substring(second_comma + 1).toFloat();
      m.SetPIDGains(kp, ki, kd);
    }
    else if (first.equals("M")) {
      int first_comma = toSend.indexOf(',', 1);
      double manual_speed = (double) toSend.substring(1, first_comma).toFloat();
      m.Manual(manual_speed);
    }
    else if (first.equals("E")) {
      bool local_enable = false;
      local_enable = (bool) toSend.substring(1, 2);
      if (local_enable) {
        m.EnablePID();
      }
      else {
        m.DisablePID();
      }
    }
    else if (first.equals("D")) {
      m.SetWheelSize((double) toSend.substring(1).toFloat());
    }
    else if (first.equals("T")) {
      // set the ticks per rev
    }
    else if (first.equals("A")) {
      // set the max acceleration
    }


  }
}





