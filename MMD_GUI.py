# -*- coding: utf-8 -*-
"""
MicroMotion Detector with GUI.
It measures time differences between PMT photon pulses and RF trigger TTL signal triggered by the RF drive sine waveform. The histogram of the time differences will be drawn and automatically updated in a configured interval, adding newly measured values into it.

@author: Seigen Nakasone
            qingyuan.tian@oist.jp
"""

import sys
import time
import XEM7305_MicroMotion_Detector
import numpy as np

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox,  
        QGridLayout, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QRadioButton,
        QSpinBox, QWidget, QMainWindow)


from pyqtgraph import PlotWidget
import pyqtgraph as pg

# const
MIN_PIPEOUT_LEN = 16 # unit: bytes
PIPEOUT_BUS_WIDTH = 4 # unit: bytes
MIN_PIPEOUT_LEN_IN_WORD = MIN_PIPEOUT_LEN // PIPEOUT_BUS_WIDTH
BYTES_PER_TIMEDIFF = 1 
REDRAW_TIME = 20 # pipeOut I/O and plot animation time per update. (70~80ms might be good for matplotlib cla and draw, 20~30 mus might be good for pyqtgraph)
N_PERIOD = 5 # a RF trigger TTL for every 5 RF drive sine waves 
N_MAX_PROBE = 20 # Try 20 times to probe RF trigger TTL and PMT pulses, and to measure firo_r_count to calculate pipeout length. If there are no good RF trigger TTL or PMT signals, notify the user.
SIZE_BINS_DEFAULT = 107 # The number of the bins of the histogram will be 107 if using 21.5MHz sine wave, 5 RF drive sine waves a RF trigger TTL, sampling clock period 2.17 ns. 
PIPEOUT_LENGTH_DEFAULT = 1024
ALARM_PROBING = "Probing ... ... "
ALARM_NO_SIGNALS = "No RF trigger TTL or PMT Signals ! "
ALARM_DETECTING = "IN DETECTING ... ... "
ALARM_STPPED = "STOPPED ... ... "
ALARM_TOO_MANY_PHOTON = "Too many photons arriving in an update interval. Try a shorter interal. "

# global variables to enable simulation or debug features
DEBUG = True
SIMULATE = True

def myfunc(k, n):
    """  The function used to create a distribution """
    return np.sin(N_PERIOD*2*np.pi*k/n)+1.0
    
class MyDistribution:
    """  A distribution used as the input source of the simulator """
    def __init__(self, size_popu=100000, size_samp=1000, size_bins=100, 
                 from_func=1, my_func=None, name_dist='', 
                 samp_only_update_dens=True, normalize = True):
        self._size_popu = size_popu
        self._size_samp = size_samp
        self._size_bins = size_bins
        self._from_func = from_func # 1: create distribution from a function. 0: use a numpy distribution
        self._my_func = my_func
        self._name_dist = name_dist
        self._samp_only_update_dens=samp_only_update_dens #True: only update samp_density for incremental sampling
        self._normalize = normalize
        
    def popu(self):
        self._popu_density = [self._my_func(k,self._size_bins) for k in range(self._size_bins)]
        self._popu_density = self._popu_density / sum(self._popu_density) 
        self._popu = []
        for i in range(self._size_bins):
            self._popu = np.hstack((self._popu, [i] * round(self._popu_density[i]*self._size_popu)))
        if (self._normalize != True):
            self._popu_density, _ = np.histogram(self._popu, self._size_bins, density=False)
        else: 
            self._popu_density, _ = np.histogram(self._popu, self._size_bins, density=True) # in fact, this line is not needed here. the density is already calculated before creating the population. This line is added for readability. 
    
    def samp_init(self):
        self._samp = []
        if (self._normalize == True):
            self._samp_density, _ = np.histogram(self._samp, self._size_bins, density=True)
        else:
            self._samp_density, _ = np.histogram(self._samp, self._size_bins, density=False)

    def samp(self):
        self._samp = np.random.choice(self._popu, self._size_samp)
        if (self._normalize == True):
            self._samp_density, _ = np.histogram(self._samp, self._size_bins, density=True)
        else:
            self._samp_density, _ = np.histogram(self._samp, self._size_bins, density=False)
        
    @property 
    def popu_density(self):
        return self._popu_density
    
    @property 
    def samp_density(self):
        return self._samp_density
    
    @property 
    def size_bins(self):
        return self._size_bins
    

class GraphMMD(PlotWidget):
    """ The widget to draw Micro-Motion Detector histogram """
    def __init__(self, *args, **kwargs):
        super(GraphMMD, self).__init__(*args, **kwargs)
        self.n_from_start = 0 # the number of graph updated from start detecting.
        self.init_dammy_plot()
        
    def init_dammy_plot(self, size_bins = 100):
        """ Draw a dumy graph with dumy parameters """
        self.size_bins = size_bins
        self.xdata = [i for i in range(self.size_bins+1)]  # x values are edges of the bins. len(xdata) = len(ydata) + 1. plot with stepMode=True.
        self.ydata = np.full((self.size_bins),0) # initial to 0s
        self.setBackground('w')
        self.pen = pg.mkPen(color=(255, 0, 0), width=1)
        self.plot_ref =  self.plot(self.xdata, self.ydata, pen=self.pen, stepMode=True, fillLevel=0, brush=(50,50,200,50))
        
    def init_plot(self, size_bins = 100, sampling_period=2.17):
        """ Using the real parameters to initiate the graph. """
        self.size_bins = size_bins
        self.sampling_period = sampling_period
        self.plot_ref.clear() 
        self.n_from_start = 0
        self.xdata = [i*self.sampling_period for i in range(self.size_bins+1)]  # x is edges of bins. len(xdata) = len(ydata) + 1. plot with stepMode=True.
        self.ydata = np.full((self.size_bins),0) # initial to 0s
        self.plot_ref.setData(self.xdata, self.ydata)
        self.setXRange(self.xdata[0], self.xdata[self.size_bins], padding=0)
        
        gtitle = "Histogram of Measured Time Differences"
        gleftlbl = "Number of Photons"
        gbottomlbl = "ns "
        gstyles = {'color':'black', 'font-size':'16px'}
        
        self.setTitle(gtitle, **gstyles)
        self.setLabel('left', gleftlbl, **gstyles)
        self.getAxis('left').setPen('black')
        self.getAxis('left').setTextPen('black')
        self.setLabel('bottom', gbottomlbl, **gstyles)
        self.getAxis('bottom').setPen('black')
        self.getAxis('bottom').setTextPen('black')
    
    def update_plot(self, size_bins = 100, hist=[]):
        """ Update the graph using new values """
        self.n_from_start = self.n_from_start + 1
        
        # advance feature: adjust while size_bins changed. Might not be needed.
        if (self.size_bins > size_bins):
            pass # to be added if needed
        elif (self.size_bins < size_bins):
            pass # to be added if needed
        
        self.ydata = hist
        
        self.setXRange(self.xdata[0], self.xdata[self.size_bins], padding=0)
        self.plot_ref.setData(self.xdata, self.ydata)
    
class MMD():
    """ 
    The Micro_Motion Detector. Pipe out time difference values from a FPGA board, 
    and draw the histogram graph. 
    """
    def __init__(self, *args, **kwargs):
        self.timer = None
        self.init_mmd(self, *args, **kwargs)
        self.init_dummy_plots(self, *args, **kwargs)
    
    def init_mmd(self, *args, **kwargs):
        pass
    
    def init_dummy_plots(self, *args, **kwargs):
        """ initiate plots with dummy parameters """
        self.graph0 = GraphMMD()
        self.graph0.setMinimumSize(800,300)

    def start_mmd(self, dev=None, size_bins=100, updateInterval=200, pipeOutLen=1024, useCondCnt=False, useCondTime=False, condCnt=20000, condTime=3000, condOr=True):
        """ 
        It initiates the plots with real parameters, 
        and start the detector by initiate a timer to  periodically fetch the new time difference values from the FPGA board. 
        The unit of updateInterval: ms.
        """
        # Histogram data
        self.n_update = 0 
        self.time_detected = 0 # unit: ms
        self.cnt_detected = 0 # unit: photon
        self.hist = [0] * size_bins
        self.size_bins = size_bins
        
        # initiate simulator
        self.simulator = MyDistribution(my_func = myfunc, normalize=False, size_bins=size_bins)
        self.simulator.popu()
        
        # initiate plots with real parameters
        self.graph0.init_plot(size_bins=size_bins)

        # prepare to pipeout values from the FPGA board
        if (dev is not None): 
            dev.reset_dev() 
            
        # use a timer to pipeout values from the FPGA board
        # either the real detector or the simulated detector will use this timer
        if (self.timer is not None):
            self.timer.stop()
            del self.timer
        self.timer = QTimer()
        
        self.settingInterval = updateInterval # get the setting from the GUI
        self.interval = updateInterval - REDRAW_TIME # REDRAW_TIME is time needed for I/O and graph render. Set as a const. 
        if (self.interval < 0): 
            self.interval = 0
        if (DEBUG == True):
            print("Timer interval", self.interval)
        self.timer.setInterval(int(self.interval))
        self.timer.timeout.connect(lambda: self.update_mmd(dev=dev, pipeOutLen=pipeOutLen, size_bins=size_bins, useCondCnt=useCondCnt, useCondTime=useCondTime, condCnt=condCnt, condTime=condTime, condOr=condOr)) # fire the function by the timeout event of the timer.
        self.timer.start()
        
    def stop_update(self):
        if (self.timer is not None):
            self.timer.stop()
            
    def update_mmd(self, dev=None, pipeOutLen=1024, size_bins=100, useCondCnt=False, useCondTime=False, condCnt=20000, condTime=3000, condOr=True):
        """ 
        It pipes out the time difference values from the FPGA device, and uses the new  values to update the plot. 
        It is fired periodically by the timeout event of the timer.
        The unit of timer intervals: ms.
        """
        self.n_update = self.n_update + 1 

        # Time difference values.
        pipe_len = pipeOutLen # default length
        if (SIMULATE != True and dev is not None):
            fifo_cnt = dev.fifo_r_count() # length of data in fifo ready to pipeout
            pipe_len = (fifo_cnt // MIN_PIPEOUT_LEN_IN_WORD) * MIN_PIPEOUT_LEN_IN_WORD  # Adjust the pipeOut length
            if (DEBUG):
                print("update # : ", self.n_update)
                print("fifo_cnt, pipe_len ", fifo_cnt, pipe_len ) 
            self.buff = bytearray(PIPEOUT_BUS_WIDTH * pipe_len) # pipeout length adjusted in each update
            dev.pipe_out(self.buff) 
            tdiff_tmp = self.size_bins - np.frombuffer(self.buff, dtype=np.uint8) # np.frombuffer convert a byte array to an int array. The value fetched from FPGA is (time_photon - time_rising_TTL). To mode it by size_bins (period_of_TTL) gets the value (time_rising_TTL - time_photon) we need.
            if (DEBUG): 
                #print(self.buff)
                print(tdiff_tmp)
            hist_tmp, _ = np.histogram(tdiff_tmp, self.size_bins, density=False) 
            self.hist = self.hist + hist_tmp 

        # Simulation: using the simulator(a simulated distribution) to create the histogram. 
        elif (SIMULATE == True):
            # data from a simulator
            self.simulator.samp()
            self.hist = self.hist + self.simulator.samp_density
        
        # To stop the update according the pre-configured conditions
        self.time_detected = self.time_detected + self.settingInterval
        self.cnt_detected = self.cnt_detected + PIPEOUT_BUS_WIDTH * pipe_len
        if (DEBUG):
            print("self.time_detected, self.cnt_detected: ", self.time_detected, self.cnt_detected)
        if (not(useCondCnt or useCondTime)):
            self.condStop = False # no stop condtion is checked.
        else:
            if (condOr): #logic or
                cond1 = (useCondCnt) and (self.cnt_detected > condCnt)
                cond2 = (useCondTime) and (self.time_detected > condTime)
                self.condStop = cond1 or cond2
            else: # logic and
                cond1 = not(useCondCnt) or (self.cnt_detected > condCnt)
                cond2 = not(useCondTime) or (self.time_detected > condTime)
                self.condStop = cond1 and cond2
        
        if (self.condStop): # stop the update
            gstyles = {'color':'red', 'font-size':'16px'}
            gtitle = "Histogram (STOPPED -- Enough Data or Time Out.  )"
            self.graph0.setTitle(gtitle, **gstyles)
            print("STOPPED -- Enough Data or Time Out. ")
            self.stop_update() # stop fetching more data to update the histogram plot
        
        # update the plot
        self.graph0.update_plot(size_bins = size_bins, hist=self.hist)
        

class MainWindow(QMainWindow):
    """  The Mian Window of the GUI """
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.dev = self.getDev()
        self.mmd = self.getMMD()
        self.gui = self.createGUI()
        self.calcConfig()
        self.stop_timer = None
        
        layout = QGridLayout()
        layout.addWidget(self.gui, 0, 0)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setWindowTitle("Micro-Motion Detector")

    def getDev(self):
        """ To get the FPGA device """
        if (SIMULATE != True):
            dev = XEM7305_MicroMotion_Detector.XEM7305_MicroMotion_Detector(bit_file='micromotion_detector.bit')
            return dev
    
    def clrDev(self):
        """ To clear the FPGA device """
        if (SIMULATE != True):
            self.dev.clear_dev()

    def getMMD(self):
        """ To get the Micro-Motion Detector """
        mmd = MMD()
        return mmd

    def calcConfig(self):
        """ get the settings from the GUI """
        self.settingUpdateInterval = self.sbxUpdateInterval.value() # unit: ms
        self.settingUseCondCount = self.ckbCountStop.isChecked()
        self.settingUseCondTime = self.ckbTimeStop.isChecked()
        self.settingCondAnd = self.rdbCondAnd.isChecked() 
        self.settingCondOr = self.rdbCondOr.isChecked()
        try:
            stop_cnt = int(self.leCountStop.text())
        except ValueError:
            stop_cnt = 20000 # default: data number in 2 sec for a 10M/s photon rate
        if (stop_cnt < 100): # too small
            stop_cnt = 20000
        self.settingStopCnt = stop_cnt
        self.leCountStop.setText(str( self.settingStopCnt))
        try:
            stop_time = int(self.leTimeStop.text())
        except ValueError:
            stop_time = 3000 # default: 3 sec
        if (stop_time < 50): # too short
            stop_time = 3000
        self.settingStopTime = stop_time
        self.leTimeStop.setText(str( self.settingStopTime))
        if (DEBUG):
            self.debugInfo()
        
    def start(self):
        """ Start fetching data from the FPGA to draw the graph. """
        self.clrDev()

        # get settings, and calculate all configurations needed 
        self.calcConfig() 

        if (DEBUG == True) :
            self.debugInfo()
        
        # default values will be kept for simulation
        self.TTLPeriod = SIZE_BINS_DEFAULT
        self.fifoReadCountIncr = PIPEOUT_LENGTH_DEFAULT
        if (SIMULATE == True) :
            mydev = None 
        else:
            mydev = self.dev
            # probe the RF trigger TTL and PMT signals
            print(ALARM_PROBING)
            self.TTLPeriod, self.tdiffCountIncr, self.fifoReadCountIncr = self.probeTTLandPMT() 
            readyToDetect = True
            if (self.TTLPeriod <=0  or self.tdiffCountIncr <=0): # no signals
                alarm_tmp = ALARM_NO_SIGNALS
                readyToDetect = False
            elif (self.fifoReadCountIncr <= 0 and self.tdiffCountIncr >= 130000): # Too many photons arriving in an update interval. Fifo write depth is 131072.
                alarm_tmp = ALARM_TOO_MANY_PHOTON 
                readyToDetect = False
            if (not readyToDetect ):
                print(alarm_tmp)
                self.lblAlarm.setText(alarm_tmp)
                self.lblAlarm.setStyleSheet("background-color: Orange")
                if (DEBUG):
                    print(self.TTLPeriod, self.tdiffCountIncr, self.fifoReadCountIncr) # debug
                return # Not ready. No signal, or too many photons. Exit the function. 
            if (DEBUG): 
                print(self.TTLPeriod, self.tdiffCountIncr, self.fifoReadCountIncr) # debug
                
                
        #Ready to detect. To initiate the FPGA device, fetch its output to update the plot
        self.fifoReadCountIncr = (self.fifoReadCountIncr // MIN_PIPEOUT_LEN_IN_WORD) * MIN_PIPEOUT_LEN_IN_WORD # MIN_PIPEOUT_LEN_IN_WORD = 4. Pipeout length should be multiple of 16 in bytes (char) for opal kelly API usb3.0. Here fifo read bus is PIPEOUT_BUS_WIDTH=4 bytes wide, so that this length must be multiple of 16/4 = 4. Because the photon arriving rate might change, this pipeout length is continously adjusted.
        if (DEBUG): 
            print("pipeout length: ", self.fifoReadCountIncr)
            
        # Detecting
        self.mmd.start_mmd(dev=mydev, pipeOutLen=self.fifoReadCountIncr, updateInterval=self.settingUpdateInterval, size_bins=self.TTLPeriod, useCondCnt=self.settingUseCondCount, useCondTime=self.settingUseCondTime, condCnt=self.settingStopCnt, condTime=self.settingStopTime, condOr=self.settingCondOr) 
        print(ALARM_DETECTING)
        self.lblAlarm.setText(ALARM_DETECTING)
        self.lblAlarm.setStyleSheet("background-color: LightGreen") # LightYellow, Orange, Coral, Red


    def probeTTLandPMT(self):
        """ 
            To probe the necessory input signals (RF trigger TTL and PMT pulse).
            If continously probed signals and the data is good for Micro-Motion Detecting, return 3 parameters to the detector (they should be all positive). 
            Otherwise, if no good signals probed for 20 times, time out and return 3 parameters with negtive or zero values to indicate the status.
        """
        TTLPeriod = -1
        tdiffCountIncr = -1
        fifoReadCountIncr = -1
        pre_probed = False
        n_probe = 0
        photon_cnt = 0
        tdiff_cnt = 0
        TTL_prd = 0
        fifo_r_cnt = 0
        pre_tdiff_cnt = 0
        pre_TTL_prd = 0
        pre_fifo_r_cnt = 0
        self.dev.reset_dev()
        while (n_probe < N_MAX_PROBE):
            # print(n_probe, pre_photon_cnt, pre_tdiff_cnt, pre_TTL_prd, pre_fifo_r_cnt, pre_probed) # for debug
            n_probe = n_probe + 1
            time.sleep(self.settingUpdateInterval / 1000.)
            photon_cnt, tdiff_cnt, TTL_prd, fifo_r_cnt = self.dev.probe_dev()
            # print(photon_cnt, tdiff_cnt, TTL_prd, fifo_r_cnt) # for debug
            if (tdiff_cnt > 0 and TTL_prd > 0 and fifo_r_cnt > 0): # Signals probed
                if (pre_probed == True and TTL_prd == pre_TTL_prd): # Probed again, and signals are good. 
                    TTLPeriod = TTL_prd  # to be used as size_bins
                    tdiffCountIncr = tdiff_cnt - pre_tdiff_cnt  # photon count in the interval
                    fifoReadCountIncr = fifo_r_cnt - pre_fifo_r_cnt # to be used as pipeout length
                    break # probe finished
                pre_probed = True  # store the previous probed values
                pre_tdiff_cnt = tdiff_cnt
                pre_TTL_prd = TTL_prd
                pre_fifo_r_cnt = fifo_r_cnt
        return TTLPeriod, tdiffCountIncr, fifoReadCountIncr

    def debugInfo(self):
        print("self.settingUpdateInterval ",self.settingUpdateInterval)
        print("self.settingCondAnd ", self.settingCondAnd)
        print("self.settingCondOr ", self.settingCondOr)
        print("self.settingStopCnt ", self.settingStopCnt)
        print("self.settingStopTime ", self.settingStopTime)
        print("self.settingUseCondCount ", self.settingUseCondCount)
        print("self.settingUseCondTime ", self.settingUseCondTime)

    def stop(self):
        self.mmd.stop_update()
        print(ALARM_STPPED)
        self.lblAlarm.setText(ALARM_STPPED)
        self.lblAlarm.setStyleSheet("background-color: LightGray")
        
    def createGUI(self):
        gui = QWidget()
        layout = QGridLayout()
        layout.addWidget(self.mmd.graph0, 0, 0)
        
        #following parameters will be automatically fetched from real experiment environment
        # rowSineWaveFreq = QHBoxLayout()
        # lblSineWaveFreq = QLabel("Sine Wave Freq.(MHz): ")
        # self.leSineWaveFreq = QLineEdit('21.5')  
        # self.leSineWaveFreq.textEdited.connect(self.calcConfig)
        # rowSineWaveFreq.addWidget(lblSineWaveFreq)
        # rowSineWaveFreq.addWidget(self.leSineWaveFreq)
        # rowSineWaveFreq.addStretch(1)
        # self.sbxTrigTTLPeriodMultiplier = QSpinBox()
        # self.sbxTrigTTLPeriodMultiplier.setValue(5)
        # self.sbxTrigTTLPeriodMultiplier.setRange(1, 10)
        # self.sbxTrigTTLPeriodMultiplier.valueChanged.connect(self.calcConfig)
        # self.sbxTrigTTLPeriodMultiplier.setPrefix("TTL is Triggered in Every     ")
        # self.sbxTrigTTLPeriodMultiplier.setSuffix("     Sine Waves.")
        # rowSineWaveFreq.addWidget(self.sbxTrigTTLPeriodMultiplier)
        # layout.addLayout(rowSineWaveFreq, 1, 0)
        
        # rowAutoPipeOutLen = QHBoxLayout()
        # self.ckbAutoPipeOutLen = QCheckBox("Automatically Adjust PipeOut Length (Necessory For Photons Arriving in Changing Rates)")
        # self.ckbAutoPipeOutLen.setChecked(False)
        # rowAutoPipeOutLen.addWidget(self.ckbAutoPipeOutLen)
        # rowAutoPipeOutLen.addStretch(1)
        # self.ckbPrintLenReadyOut = QCheckBox("Print Data Length Ready to PipeOut ")
        # self.ckbPrintLenReadyOut.setChecked(True)
        # rowAutoPipeOutLen.addWidget(self.ckbPrintLenReadyOut)
        # layout.addLayout(rowAutoPipeOutLen, 1, 0)
        
        rowStopCondition = QHBoxLayout()
        self.ckbCountStop = QCheckBox("Stop if detected photon number >= ")
        self.ckbCountStop.setChecked(True)
        self.leCountStop = QLineEdit('20000')
        #self.leCountStop.textEdited.connect(self.calcConfig)
        rowStopCondition.addWidget(self.ckbCountStop)
        rowStopCondition.addWidget(self.leCountStop)
        rowStopCondition.addStretch(1)
        self.rdbCondAnd = QRadioButton("AND")
        self.rdbCondAnd.setChecked(False)
        self.rdbCondOr = QRadioButton("Or")
        self.rdbCondOr.setChecked(True)
        rowStopCondition.addWidget(self.rdbCondOr)
        rowStopCondition.addWidget(self.rdbCondAnd)
        rowStopCondition.addStretch(1)
        self.ckbTimeStop = QCheckBox("Stop if detecting time (ms) >= ")
        self.ckbTimeStop.setCheckState(False)
        self.leTimeStop = QLineEdit('3000')
        #self.leTimeStop.textEdited.connect(self.calcConfig)
        rowStopCondition.addWidget(self.ckbTimeStop)
        rowStopCondition.addWidget(self.leTimeStop)
        layout.addLayout(rowStopCondition, 1, 0)
        
        rowUpdateInterval = QHBoxLayout()
        self.sbxUpdateInterval = QSpinBox()
        self.sbxUpdateInterval.setRange(100, 1000)
        self.sbxUpdateInterval.setSingleStep(100)
        self.sbxUpdateInterval.setValue(200)
        self.sbxUpdateInterval.setPrefix("Histogram Update Interval:     ")
        self.sbxUpdateInterval.setSuffix("     (ms)")
        self.sbxUpdateInterval.valueChanged.connect(self.calcConfig)
        lblSpace = QLabel(" ")
        rowUpdateInterval.addWidget(self.sbxUpdateInterval)
        rowUpdateInterval.stretch(1)
        rowUpdateInterval.addWidget(lblSpace)
        rowUpdateInterval.stretch(1)
        rowUpdateInterval.addWidget(lblSpace)
        layout.addLayout(rowUpdateInterval, 2, 0)
        layout.addWidget(QLabel("      "), 3, 0)
        
        rowBtn = QHBoxLayout()
        btn = QPushButton("Start")
        btn.clicked.connect(self.start)
        btn2 = QPushButton("Stop")
        btn2.clicked.connect(self.stop)
        rowBtn.addWidget(btn)
        rowBtn.addStretch(1)
        rowBtn.addWidget(btn2)
        layout.addLayout(rowBtn, 4, 0)
        
        self.lblAlarm = QLabel("")
        layout.addWidget(self.lblAlarm)
    
        gui.setLayout(layout)
        return gui

# A sample of the usage of this class.
if __name__ == '__main__':
    # using arguments in python command line to enable debug.
    if 'DEBUG' in sys.argv: 
        DEBUG = True
    else:
        DEBUG = False
    # using arguments in python command line to choose the simulator instead of the real detector.
    if 'SIMU' in sys.argv:
        SIMULATE = True
    else:
        SIMULATE = False

    # Start the program with the GUI
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

    
        