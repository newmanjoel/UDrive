# -*- coding: utf-8 -*-
"""
Created on Sun Jul 08 18:24:12 2018

@author: joell
"""
import time
import numpy as np
from termcolor import colored

from PyQt4 import QtCore, QtGui, uic  # Import the PyQt4 module we'll need
from PyQt4.QtCore import *

import serial
import serial.tools.list_ports as list_ports

from UDrive_program import UDrive
from Debug_program import DebugScreen
from Serial_program import SerialScreen
from Motor_Driver_Settings import MCD_Settings

base_time = time.time()
setpoint_data = np.array([0.0, 0.0])
m1_output_data = np.array([0.0, 0.0])
m1_output_data = np.array([0.0, 0.0])
input_data = np.array([0.0, 0.0])
current_data = np.array([0.0, 0.0])
xdata = np.array([0.0, 1.0])
run_flag = True
write_flag = False
data_size = 1000
arduino_input = ""

debug_window = DebugScreen() # this has to be the first window that is created

ser = None
mc = UDrive(ser)


serial_window = SerialScreen() # mc has to be created before this
mcd_window = MCD_Settings()

print "starting up the gobal settings"

