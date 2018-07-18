# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 13:38:10 2018

@author: joell
"""

from g_settings import *

class PidScreen(QtGui.QWidget):
    def __init__(self): #THIS IS SUPER IMPORTANT
    	super(self.__class__, self).__init__() #THIS IS SUPER IMPORTANT
    	uic.loadUi('pid.ui', self) #THIS IS WHERE YOU LOAD THE .UI FILE
    	self.horizontalSlider_kp.valueChanged.connect(self.slider_changed_kp)
    	self.horizontalSlider_ki.valueChanged.connect(self.slider_changed_ki)
    	self.horizontalSlider_kd.valueChanged.connect(self.slider_changed_kd)

    def slider_changed_kp(self):
        self.spinner_kp.setValue(float(self.horizontalSlider_kp.value())/100)
        mc.pid_values[0] = self.spinner_kp.value()

    def slider_changed_ki(self):
        self.spinner_ki.setValue(float(self.horizontalSlider_ki.value())/100)

    def slider_changed_kd(self):
        self.spinner_kd.setValue(float(self.horizontalSlider_kd.value())/100)

