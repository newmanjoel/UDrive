# -*- coding: utf-8 -*-
"""
Created on Mon Jun 04 17:55:33 2018

@author: joell

Lines 214-270 are all the code for connecting the GUI to the code
"""


from PyQt4 import QtCore, QtGui, uic  # Import the PyQt4 module we'll need
from PyQt4.QtCore import *
import sys  # We need sys so that we can pass argv to QApplication
class Pid(QtGui.QWidget):
    def __init__(self): #THIS IS SUPER IMPORTANT
    	super(self.__class__, self).__init__() #THIS IS SUPER IMPORTANT
    	uic.loadUi('pid.ui', self) #THIS IS WHERE YOU LOAD THE .UI FILE
    	self.horizontalSlider_kp.valueChanged.connect(self.slider_changed_kp)
    	self.horizontalSlider_ki.valueChanged.connect(self.slider_changed_ki)
    	self.horizontalSlider_kd.valueChanged.connect(self.slider_changed_kd)

app = QtGui.QApplication(sys.argv) # this is important needs to be before the g_settings
    def slider_changed_kp(self):
        self.spinner_kp.setValue(float(self.horizontalSlider_kp.value())/100)
        mc.pid_values[0] = self.spinner_kp.value()

from g_settings import * # all the global variables
    def slider_changed_ki(self):
        self.spinner_ki.setValue(float(self.horizontalSlider_ki.value())/100)

    def slider_changed_kd(self):
        self.spinner_kd.setValue(float(self.horizontalSlider_kd.value())/100)

class MainScreen(QtGui.QMainWindow):
    def __init__(self): #THIS IS SUPER IMPORTANT
        global debug_window
        from usbWorker import Worker
        '''
        This is the main screen that the user interacts with.

        '''
        super(self.__class__, self).__init__() #THIS IS SUPER IMPORTANT
        uic.loadUi('Main_Window.ui', self) #THIS IS WHERE YOU LOAD THE .UI FILE
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.displayGraph)
        timer.start(500)
        self.threadpool = QtCore.QThreadPool()

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

        mcd_action = QtGui.QAction("&Motor Driver Settings", self)
        mcd_action.setStatusTip("Configure the DRV8704 Settings")
        mcd_action.triggered.connect(self.show_mcd_callback)

        config_menu = main_menu.addMenu("&Config")
        config_menu.addAction(power_action)
        config_menu.addAction(debug_action)
        config_menu.addAction(mcd_action)
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
        debug_window.debug_output("starting up the main window")

    def closeEvent(self, event):
        global run_flag
        run_flag = False
        debug_window.close()
        serial_window.close()
        self.close()
        event.accept()

    def show_mcd_callback(self):
        debug_window.debug_output("showing the mcd window")
        mcd_window.show()

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
        global m1_output_data
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
                        m1_output_data = np.append(m1_output_data, split_csv[i])
                    else:
                        m1_output_data = np.roll(m1_output_data, -1)
                        m1_output_data[-1] = split_csv[i]
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
        global m1_output_data
        global input_data
        global current_data
        global xdata

        ''' plot the data! '''

        self.mplwidget.axes.plot(np.linspace(0, 10, len(input_data), endpoint=True), input_data, 'b-',  # blue solid line
                                 np.linspace(0, 10, len(m1_output_data), endpoint=True) , m1_output_data, 'g:',  # green dotted line
                                 np.linspace(0, 10, len(setpoint_data), endpoint=True) , setpoint_data, 'r--'  # red dashed line
                                 )

        ''' labels are nice to have '''
        self.mplwidget.axes.set_xlabel("time")
        self.mplwidget.axes.set_ylabel("arbartary scale")

        ''' redraw the graph to display the new graph '''
        self.mplwidget.draw()



try:
    global ser, mc, debug_window, serial_window, form
    debug_window.debug_output("trying to start the mc")
    # mc = UDrive(ser)

    #debug_window = DebugScreen()
    #serial_window = SerialScreen()
    form = MainScreen() #this is important

    form.show() #this is important
    app.exec_() #this is important
finally:
    if(mc.uC is not None):
        mc.uC.close()
        print colored("arduino closed", 'magenta')
    else:
        print colored("no arduino connected", "magenta")
