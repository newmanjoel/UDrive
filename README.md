# UDrive
Software Controls for the UDrive Motor Controller.

To use the GUI that was developed pyqt4 is needed as well as a few other helper libraries. This should be updated so that is runs in a browser and isnt dependant on funky libraries.
The software that is working (as of last 499) is the "test_sketch_SAMD.ino"; this is the software that should be looked at if you are trying to understand the code.

The pid and the dimmer object is contained inside the motor controller class.
* motor_controller
  * PID_v1
  * DimmerZero

The first major upgrade that this program should get to really really upgrade it is to replace the DimmerZero Class. It is only outputting 1kHz wave when the SAMD is capable of waves around 10MHz. The target frequency should be around 30k~50kHz as this should move it out of our range of hearing. (insert refernce to prove point).

## API
The format for sending information to the UDrive motor controller will mostly be in the format

"{}1{},;{}2{}, " <- *Note the extra space at the end!*


| Mode Name | Mode Description | Regex | Limits |
| -- | -- | -- | -- |
| Manual | Manually set the speed by defining the duty cycle of the square wave in percent| M1{},;{}2{}, | +- 100 |
| Velocity | Run the motor at a constant speed given in RPM | V1{},;{}2{}, | no limit (physical limit) |
| Position | Have the motor act as a servo and hold a position (WIP) | T1{},;{}2{}, | no limit |
| PID | Adjust the PID values of a motor (each motor is separate)| "P1{},{},{};P2{},{},{} " | no limit |
| Driver chip | Adjust settings specific to the motor driver | "D" + "{},"*13 (used to indicate 13 csv) | described on wiki page |
| Reset | Toggle the reset pin on the motor driver | "R" | NA |
| Sleep | Toggle the sleep pin on the motor driver | "S" | NA |
| Read | Read back what the PID's are trying to do {input},{setpoint},{output} for each motor in a string | "~" | NA |
| Driver Status | Read the status on the motor driver chip (will send info back over serial) | "Q" | NA |



## How to send commands
To send commands to the UDrive connect the main board via usb to a computer. On the computer identify which port the UDrive identifies as and open a port with a baud rate of 115200. The commands are all sent as a string over USB. The easiest way to send the commands is using the arduino IDE using the serial monitor (insert link to article explaining).

### Example commands
"M1100,;M20, "
// This will make the first motor go to 100% and the second motor to 0 %

"V120,;M20, "
// This will make the first motor spin at a constant 20 rpm and the second motor at 20% duty cycle.


## Driver Settings

insert the driver settings that are currently in GUI Files > Motor_Driver_Settings


## Reading Motor Driver status
Will return in the format of "Settings: {},{},{},{},{}\n" where data is inside of the brackets. The data that is returned is :
 * overtemp_shutdown
 * channel_A_overcurrent_protection
 * channel_B_overcurrent_protection
 * channel_A_predriver_fault
 * channel_B_predriver_fault
 * undervoltage_lockout
