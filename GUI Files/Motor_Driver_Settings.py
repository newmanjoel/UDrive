# -*- coding: utf-8 -*-
"""
Created on Sun Jul 08 17:05:20 2018

@author: joell
"""
from PyQt4 import QtCore, QtGui, uic  # Import the PyQt4 module we'll need
from PyQt4.QtCore import *

class MC_Settings(QtGui.QWidget):
    def __init__(self): #THIS IS SUPER IMPORTANT
        super(self.__class__, self).__init__() #THIS IS SUPER IMPORTANT
        uic.loadUi('Motor_Driver_Settings.ui', self) #THIS IS WHERE YOU LOAD THE .UI FILE

        # CTRL TAB

        # TORQUE TAB
        self.spinBox.valueChanged.connect(self.calculate_i_chop)

        # OFF TAB
        self.spinBox_2.valueChanged.connect(self.fixed_time_off)

        # BLANK TAB
        self.spinBox_3.valueChanged.connect(self.current_blank_time)

        # DECAY TAB
        self.spinBox_4.valueChanged.connect(self.decay_trans_time)

        # DRIVE TAB

        # Controls
        self.reset_button.clicked.connect(self.reset_all_values)
        self.send_button.clicked.connect(self.send_all_values)

    def calculate_i_chop(self):
        torque = self.spinBox.value()
        gain_index = self.comboBox_2.currentIndex()
        gain = 0
        if(gain_index==0):
            gain = 5
        elif(gain_index == 1):
            gain = 10
        elif(gain_index == 2):
            gain = 20
        elif(gain_index == 3):
            gain = 40
        self.label_6.setText("I = {:.2}".format((2.75*torque)/(256*gain*0.0075)))

    def fixed_time_off(self):
        t_off = self.spinBox_2.value()
        self.label_9.setText("t_off = {} uS".format(0.525+0.525*t_off))

    def current_blank_time(self):
        t_blank = self.spinBox_3.value()
        self.label_13.setText("Tblank = {} uS".format(0.5+t_blank*0.02))

    def decay_trans_time(self):
        trans_time = self.spinBox_4.getValue()
        self.label_17.setText("T_Decay = {} uS".format(trans_time*0.525))

    def reset_all_values(self):
        self.comboBox.setCurrentIndex(1)
        self.comboBox_2.setCurrentIndex(3)
        self.comboBox_3.setCurrentIndex(0)

        self.spinBox.setValue(255)

        self.spinBox_2.setValue(48)

        self.spinBox_3.setValue(128)

        self.spinBox_4.setValue(16)
        self.comboBox_4.setCurrentIndex(0)

        self.comboBox_5.setCurrentIndex(1)
        self.comboBox_6.setCurrentIndex(1)
        self.comboBox_7.setCurrentIndex(2)
        self.comboBox_19.setCurrentIndex(2)
        self.comboBox_9.setCurrentIndex(3)
        self.comboBox_10.setCurrentIndex(3)

    def send_all_values(self):
        print "SENDING ALL OF THE VALUES"


if (__name__ == "__main__"):
    import sys  # We need sys so that we can pass argv to QApplication
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = MC_Settings()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app

