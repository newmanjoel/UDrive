# -*- coding: utf-8 -*-
"""
Created on Mon Jun 04 17:55:33 2018

@author: joell

Lines 214-270 are all the code for connecting the GUI to the code
"""

import json
counting = 0
import serial
import serial.tools.list_ports as list_ports
from termcolor import colored


from PyQt4 import QtCore, QtGui, uic  # Import the PyQt4 module we'll need
from PyQt4.QtCore import *
import sys  # We need sys so that we can pass argv to QApplication
import numpy as np
import time
import socket
import threading

from struct import pack, unpack, calcsize


base_time = time.time()
setpoint_data = np.array([0.0, 0.0])
output_data = np.array([0.0, 0.0])
input_data = np.array([0.0, 0.0])
current_data = np.array([0.0, 0.0])
xdata = np.array([0.0, 1.0])
run_flag = True
write_flag = False
data_size = 1000

arduino_input = ""

class UDrive():
    '''
    This class is the commands that you can send to the UDrive motor driver

    '''

    def __init__(self,ser):
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


class WorkerSignals(QObject):
    result = pyqtSignal(str)


class Worker(QtCore.QRunnable):
    '''
    WORKER THREAD
    '''
    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        global run_flag, mc
        '''
        This is the loop that polls the USB
        '''
        try:
            while run_flag:
                read_byte = mc.update()
                if(read_byte is not None):
                    self.signals.result.emit(read_byte)
        except Exception as e:
            print e

class TestScreen(QtGui.QWidget):
    def __init__(self): #THIS IS SUPER IMPORTANT
        super(self.__class__, self).__init__() #THIS IS SUPER IMPORTANT
        uic.loadUi('test_popup.ui', self) #THIS IS WHERE YOU LOAD THE .UI FILE
        self.horizontalSlider.valueChanged.connect(self.slider_changed)

    def slider_changed(self):
        self.label.setText("{}".format(self.horizontalSlider.value()))
        print "{}".format(self.horizontalSlider.value())

class DebugScreen(QtGui.QWidget):
    def __init__(self):
        '''
        This is the Debug screen that the user interacts with.

        '''
        super(self.__class__, self).__init__()
        uic.loadUi('Debug_Window.ui', self)
        self.Max_length = 500

    def limit_output(self, additional_text=""):
        '''
        This is where the amount of text in the debug window is limited and addes a new line
        '''
        plain_text = self.debug_output_textbox.toPlainText()
        plain_text += additional_text+"\n"
        return plain_text[-self.Max_length:]

    def debug_output(self, what_to_display):
        '''
        This essentially limits the size, adds a newline, and moves the cursor to the end
        '''
        what_to_display = self.limit_output(what_to_display)
        self.debug_output_textbox.setPlainText(what_to_display)
        self.debug_output_textbox.moveCursor(QtGui.QTextCursor.End)


class SerialScreen(QtGui.QWidget):
    def __init__(self):
        '''
        This is the serial selector screen that the user interacts with.

        '''
        super(self.__class__, self).__init__()
        uic.loadUi('Serial_Port_Selector.ui', self)
        self.getComms()
        self.pushButton_2.clicked.connect(self.ok_callback)
        self.pushButton.clicked.connect(self.time_to_close)

    def getComms(self):
        # print "Getting all of the available ports"
        self.ports = list(list_ports.comports())
        for (port, name, PID) in self.ports:
            # print "Testing {} which is port: {}".format(name, port)
            self.comboBox.addItem("{} -> {}".format(name, port))

    def ok_callback(self):
        global mc
        try:
            print "trying to connect to {}".format(self.ports[self.comboBox.currentIndex()][0])
            ser = serial.Serial(self.ports[self.comboBox.currentIndex()][0],9600,timeout=None)
            mc.uC = ser
            print colored("connected to the arduino", 'magenta')
            self.time_to_close()
        except serial.serialutil.SerialException:
            print colored("Could not connect to the selected Port", "red")

    def time_to_close(self):
        self.close()


class MainScreen(QtGui.QMainWindow):
    def __init__(self): #THIS IS SUPER IMPORTANT
        global debug_window
        '''
        This is the main screen that the user interacts with.

        '''
        super(self.__class__, self).__init__() #THIS IS SUPER IMPORTANT
        uic.loadUi('Main_Window.ui', self) #THIS IS WHERE YOU LOAD THE .UI FILE
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.displayGraph)
        timer.start(500)
        self.threadpool = QtCore.QThreadPool()
        print "I can start threads on {} threads".format(self.threadpool.maxThreadCount())
        self.worker = Worker()
        self.worker.signals.result.connect(self.print_output)
        self.threadpool.start(self.worker)

        self.toggle_powerbar_callback()

        # File Menus
        conn_action = QtGui.QAction("&Connect To UDrive", self)
        conn_action.setShortcut("Ctrl+O")
        conn_action.setStatusTip('Connect to the UDrive system')
        conn_action.triggered.connect(self.connect_to_mc_callback)

        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('&File')
        file_menu.addAction(conn_action)

        # Config Menus
        power_action = QtGui.QAction("&Toggle Power Bars", self)
        power_action.setStatusTip("Enable/Disable Power Bars")
        power_action.triggered.connect(self.toggle_powerbar_callback)

        debug_action = QtGui.QAction("&Debug", self)
        debug_action.setStatusTip("Show the Debug window")
        debug_action.triggered.connect(self.show_debug_callback)

        config_menu = main_menu.addMenu("&Config")
        config_menu.addAction(power_action)
        config_menu.addAction(debug_action)
        # start of all of the connected objects

        # status

        # Commands
        self.start_button.clicked.connect(self.start_pause_callback)
        self.stop_button.clicked.connect(self.stop_callback)
        self.reset_button.clicked.connect(self.reset_callback)

        # Main Command
        self.motor_1_spinner.valueChanged.connect(self.motor_1_callback)
        self.motor_2_spinner.valueChanged.connect(self.motor_2_callback)
        self.comboBox.currentIndexChanged.connect(self.combobox_callback)
        self.motor_1_fwd_rev.clicked.connect(self.motor_1_fwd_rev_callback)
        self.motor_2_fwd_rev.clicked.connect(self.motor_2_fwd_rev_callback)

    def closeEvent(self, event):
        global run_flag
        run_flag = False
        debug_window.close()
        serial_window.close()
        self.close()
        event.accept()

    def show_debug_callback(self):
        debug_window.debug_output("showing the debug window")
        debug_window.show()

    def connect_to_mc_callback(self):
        debug_window.debug_output("connection to micro controller callback")
        serial_window.show()
        # print "Connection to mC callback"

    def toggle_powerbar_callback(self):
        if(self.motor_1_power_bar.isHidden()):
            debug_window.debug_output("Enabling the power bars")
            self.motor_1_power_bar.show()
            self.motor_2_power_bar.show()
        else:
            debug_window.debug_output("Disabling the power bars")
            self.motor_1_power_bar.hide()
            self.motor_2_power_bar.hide()

    def motor_1_fwd_rev_callback(self):
        ''' what is called when you click the reverse button for motor 1 '''
        mc.reverse_1 = not mc.reverse_1
        self.mode_value_callbacks()

    def motor_2_fwd_rev_callback(self):
        ''' what is called when you click the reverse button for motor 2 '''
        mc.reverse_2 = not mc.reverse_2
        self.mode_value_callbacks()

    def motor_1_callback(self):
        ''' what is called when you change the dial or spinner for motor 1'''
        if(self.motor_link.isChecked()):
            self.motor_2_spinner.setValue(self.motor_1_spinner.value())
        self.mode_value_callbacks()

    def motor_2_callback(self):
        ''' what is called when you change the dial or spinner for motor 2 '''
        self.mode_value_callbacks()

    def mode_value_callbacks(self):
        '''
        This is called every time the dials or spinners are changed.

        This is because the meaning of the information changes when the mode changes
        '''
        if(self.comboBox.currentIndex() == 0):
            # this is duty cycle
            self.send_manual()
        elif(self.comboBox.currentIndex() == 2):
            # this is velocity
            self.send_velocity()

    def combobox_callback(self, changed_index):
        '''
        This is called every time you make a CHANGE to the mode dropdown box.

        If you go from one mode to the same mode it will not go into this funciton.
        '''
        debug_window.debug_output("mode changed to {}".format(self.comboBox.currentText()))
        if(changed_index == 0):
            # this is duty cycle
            self.dial_label.setText("Duty Cycle")
        elif(changed_index == 1):
            # this is position
            self.dial_label.setText("Distance in M")
        elif(changed_index == 2):
            # this is Velocity
            self.dial_label.setText("Speed in RPM")


    def start_pause_callback(self):
        '''
        This is called every time you click the start button

        If start is pressed then it changes to pause
        If pause is pressed the it changes to start
        '''
        if(self.start_button.text() == "Start" ):
            debug_window.debug_output("Start Button Pressed")
            mc.send_enable = True
            self.start_button.setText("Pause")
            self.start_button.setToolTip("Stop Streaming data to the micro controller")
            self.mode_value_callbacks()
        elif(self.start_button.text() == "Pause" ):
            debug_window.debug_output("Pause Button Pressed")
            mc.send_enable = False
            self.start_button.setText("Start")
            self.start_button.setToolTip("Start Streaming data to the micro controller")

    def stop_callback(self):
        ''' This is called every time the stop button is pressed '''
        debug_window.debug_output("Stop Button Pressed")
        mc.stop()
        mc.send_enable = False
        self.start_button.setText("Start")
        self.start_button.setToolTip("Start Streaming data to the micro controller")



    def reset_callback(self):
        debug_window.debug_output("Reset Button Pressed")

    def send_velocity(self):
        value_1 = self.motor_1_spinner.value()
        value_2 = self.motor_2_spinner.value()
        mc.velocity(value_1, value_2)

    def send_manual(self):
        value_1 = self.motor_1_spinner.value()
        value_2 = self.motor_2_spinner.value()
        mc.manual(value_1, value_2)

    def print_output(self, s):
        global setpoint_data
        global output_data
        global input_data
        global data_size
        global current_data

        try:
            split_csv = s.split(",")
            for i in range(len(split_csv)):
                split_csv[i] = eval(split_csv[i])
                if(i == 0):
                    if(len(input_data) < data_size):
                        input_data = np.append(input_data, split_csv[i])
                    else:
                        input_data = np.roll(input_data, -1)
                        input_data[-1] = split_csv[i]
                elif(i == 1):
                    if(len(setpoint_data) < data_size):
                        setpoint_data = np.append(setpoint_data, split_csv[i])
                    else:
                        setpoint_data = np.roll(setpoint_data, -1)
                        setpoint_data[-1] = split_csv[i]
                elif(i == 2):
                    if(len(setpoint_data) < data_size):
                        output_data = np.append(output_data, split_csv[i])
                    else:
                        output_data = np.roll(output_data, -1)
                        output_data[-1] = split_csv[i]
                elif(i == 3):
                    if(len(setpoint_data) < data_size):
                        current_data = np.append(current_data, split_csv[i])
                    else:
                        current_data = np.roll(current_data, -1)
                        current_data[-1] = split_csv[i]
                        self.motor_1_power_bar.setValue(int(abs(np.average(current_data)-self.power_offset_spinner.value())*20.526*12))
                        self.label_2.setText("Motor 1 :{}".format(abs(np.average(current_data)-self.power_offset_spinner.value())*12*self.doubleSpinBox.value()))

        except SyntaxError:
            # print colored("-> {} -> ".format(s), "green")
            debug_window.debug_output("-> {}".format(s))
        #print colored("-> {}".format(s), "green")

    def displayGraph(self):
        global setpoint_data
        global output_data
        global input_data
        global current_data
        global xdata

        ''' plot the data! '''

        self.mplwidget.axes.plot(np.linspace(0, 10, len(input_data), endpoint=True), input_data, 'b-',  # blue solid line
                                 np.linspace(0, 10, len(output_data), endpoint=True) , output_data, 'g:',  # green dotted line
                                 np.linspace(0, 10, len(setpoint_data), endpoint=True) , setpoint_data, 'r--'  # red dashed line
                                 )

        ''' labels are nice to have '''
        self.mplwidget.axes.set_xlabel("time")
        self.mplwidget.axes.set_ylabel("arbartary scale")

        ''' redraw the graph to display the new graph '''
        self.mplwidget.draw()



try:
    # print colored("trying to conect to the arduino", 'magenta')
    ser = None
    try:
        ser = serial.Serial('COM21', 9600, timeout=None)
        print colored("connected to the arduino", 'magenta')
    except serial.serialutil.SerialException:
        print colored("Could not connect to an arduino, working in offline mode", "red")
    mc = UDrive(ser)
    app = QtGui.QApplication(sys.argv) # this is important
    debug_window = DebugScreen()
    serial_window = SerialScreen()
    form = MainScreen() #this is important

    form.show() #this is important
    app.exec_() #this is important
finally:
    if(mc.uC is not None):
        mc.uC.close()
        print colored("arduino closed", 'magenta')
    else:
        print colored("no arduino connected", "magenta")
