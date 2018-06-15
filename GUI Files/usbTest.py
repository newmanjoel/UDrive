# -*- coding: utf-8 -*-
"""
Created on Mon Jun 04 17:55:33 2018

@author: joell
"""

import json
counting = 0
import serial
from termcolor import colored


from PyQt4 import QtCore, QtGui, uic  # Import the PyQt4 module we'll need
from PyQt4.QtCore import *
import sys  # We need sys so that we can pass argv to QApplication
import numpy as np
import time
import socket
import threading


base_time = time.time()
setpoint_data = np.array([0.0, 0.0])
output_data = np.array([0.0, 0.0])
input_data = np.array([0.0, 0.0])
xdata = np.array([0.0, 1.0])
run_flag = True
write_flag = False
data_size = 1000

arduino_input = ""



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
        global run_flag, ser, write_flag, arduino_input
        try:
            while run_flag:
                if(write_flag):
                    ser.write(arduino_input)
                    write_flag = False
                read_byte = ser.readline().strip()
                #print colored("-> {}".format(read_byte),'green')
                self.signals.result.emit(read_byte)
        except Exception as e:
            print e


#t1 = threading.Thread(target=get_arduino_data)

class MainScreen(QtGui.QMainWindow):
    def __init__(self):
        '''
        This is the main screen that the user interacts with.

        '''
        super(self.__class__, self).__init__()
        uic.loadUi('usbTest_GUI.ui', self)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.displayGraph)
        timer.start(500)
        self.threadpool = QtCore.QThreadPool()
        print "I can start threads on {} threads".format(self.threadpool.maxThreadCount())
        self.worker = Worker()
        self.worker.signals.result.connect(self.print_output)
        self.threadpool.start(self.worker)
        self.setpoint_button.clicked.connect(self.send_setpoint)
        self.pid_button.clicked.connect(self.send_pid)

    def closeEvent(self,event):
        global run_flag
        run_flag = False
        event.accept()

    def send_setpoint(self):
        global write_flag, arduino_input
        print "Trying to send the value of {} to the USB".format(self.setpoint_spinner.value())
        arduino_input = "S{} ".format(self.setpoint_spinner.value())
        write_flag = True


    def print_output(self, s):
        global setpoint_data
        global output_data
        global input_data
        global data_size

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

        except SyntaxError:
            print colored("-> {} -> ".format(s), "green")

        print colored("-> {}".format(s), "green")



    def send_pid(self):
        global write_flag, arduino_input
        print "Trying to send the value of {},{}, and {} to the USB".format(
                                                        self.kp_spinner.value(),
                                                        self.ki_spinner.value(),
                                                        self.kd_spinner.value()
                                                        )
        arduino_input = "P{},{},{} ".format(
                                    self.kp_spinner.value(),
                                    self.ki_spinner.value(),
                                    self.kd_spinner.value()
                                    )
        write_flag = True


    def displayGraph(self):
        global setpoint_data
        global output_data
        global input_data
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
    print colored("trying to conect to the arduino", 'magenta')
    ser = serial.Serial('COM21',9600,timeout=None)
    print colored("connected to the arduino", 'magenta')
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = MainScreen()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app
finally:
    ser.close()
    print colored("arduino closed", 'magenta')
