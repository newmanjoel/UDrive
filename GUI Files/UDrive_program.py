# -*- coding: utf-8 -*-
"""
Created on Sun Jul 08 18:57:32 2018

@author: joell
"""
from g_settings import *

class UDrive():
    '''
    This class is the commands that you can send to the UDrive motor driver

    '''

    def __init__(self, ser=None):
        global debug_window
        '''
        motor information can be found [here](https://www.robotshop.com/ca/en/12v-313rpm-4166oz-in-hd-premium-planetary-gearmotor-encoder.html)

        '''
        self.rpm = 0
        self.manual_speed_1 = 0
        self.manual_speed_2 = 0
        self.velocity_speed_1 = 0
        self.velocity_speed_2 = 0
        self.pid_en = 0
        self.pid_values = [1, 10, 0] #kp, ki, kd
        self.wheel_diam = 0.01  # 10 cm
        self.ticks_per_rev = 1296
        self.mode_to_send = 0
        self.data_to_send = 0
        self.uC = ser
        self.debug_print = True
        self.reverse_1 = False
        self.reverse_2 = False
        self.send_enable = False

        self.arduino_input = ""
        self.write_flag = False
        print "starting the uDriver"

    def send(self):
        if(self.write_flag):
            self.write_data(self.arduino_input)
            self.write_flag = False
            # debug_window.debug_output("sending: |{}|".format(arduino_input))
            # print colored("sending: |{}|".format(local_send), color="green")

    def stop(self):
        self.send_enable = True
        self.write_data("M0,0")
        #self.send_enable = False

    def update(self):
        self.send()
        return self.read_data()

    def read_data(self):
        if(self.uC is not None):
            return self.uC.readline().strip()
        return None

    def write_data(self, what_to_write=""):
        if(self.uC is not None and self.send_enable):
            self.uC.write(what_to_write)

    def manual(self, value_1, value_2):
        if(self.reverse_1):
            value_1 = -value_1
        if(self.reverse_2):
            value_2 = -value_2
        self.arduino_input = "M{},{} ".format(value_1, value_2)
        self.write_flag = True

    def velocity(self, value_1, value_2):
        if(self.reverse_1):
            value_1 = -value_1
        if(self.reverse_2):
            value_2 = -value_2
        # print "V{},{}".format(value_1, value_2)
        self.arduino_input = "V{},{} ".format(value_1, value_2)
        self.write_flag = True

    def send_pid(self):
        self.arduino_input = "P{},{},{} ".format(
                                            self.pid_values[0],
                                            self.pid_values[1],
                                            self.pid_values[2]
                                            )
        self.write_flag = True