"""
Module XEM7305_MicroMotion_Detector

Usage: 
  todo
  
"""

import ok
import time
import sys
import ctypes
import numpy as np

class XEM7305_MicroMotion_Detector:
    def __init__(self, dev_serial='', bit_file='micromotion_detector.bit', clock_period=2.173913):
        self._dev_serial = dev_serial # device serial of our FPGA is '2104000VK5'. Open the first FPGA if given a empty serial number ''. Get serial by _device.GetDeviceListSerial(0). 0 ~ the first device.
        self._bit_file = bit_file
        self._clock_period = clock_period
        self.init_dev()

    @property
    def dev_serial(self):
        return self._dev_serial

    @dev_serial.setter
    def dev_serial(self, dev_seri):
        self._dev_serial = dev_seri

    @property
    def bit_file(self):
        return self._bit_file

    @bit_file.setter
    def bit_file(self, bit_f):
        self._bit_file = bit_f

    def init_dev(self):
        self._device = ok.okCFrontPanel()
        if (self._device.GetDeviceCount() < 1):
            sys.exit("Error: no Opal Kelly FPGA device.")
        try: 
            self._device.OpenBySerial(self.dev_serial)
            error = self._device.ConfigureFPGA(self.bit_file)
        except:
            sys.exit("Error: can't open Opal Kelly FPGA device by serial number %s" % self.dev_serial)
        if (error != 0):
            sys.exit("Error: can't program Opal Kelly FPGA device by file %s" % self.bit_file)

    def reset_dev(self):
        """ 
        Set reset signals of fifo and counting circuits to 1s, to reset those circuits,
        then, de-assert the reset signals to 0s, to restart those circuits.
        """
        self._device.SetWireInValue(0x00, 0x01) # reset = 1. To reset other circuits.
        self._device.UpdateWireIns()
        self._device.SetWireInValue(0x00, 0x02) # reset_fifo = 1. To reset FIFO only
        self._device.UpdateWireIns()
        self._device.SetWireInValue(0x00, 0x00) # de-assertion reset_fifo signal
        self._device.UpdateWireIns()
        time.sleep(0.001) # After Reset de-assertion, wait at least 30 clock cycles before asserting WE/RE signals.
        self._device.SetWireInValue(0x00, 0x01) # reset = 1. To reset other circuits.
        self._device.UpdateWireIns()
        self._device.SetWireInValue(0x00, 0x00) # de-assertion reset signal
        self._device.UpdateWireIns()
        
    def clear_dev(self):
        """ 
        Set reset signals of fifo and counting circuits to 1s, to reset those circuits,
        without de-asserting the reset signals to 0s. Those circuits are reset without restart.
        """
        self._device.SetWireInValue(0x00, 0x02) # reset_fifo = 1. To reset FIFO only
        self._device.UpdateWireIns()
        self._device.SetWireInValue(0x00, 0x01) # reset = 1. To reset other circuits.
        self._device.UpdateWireIns()
        
        
        
    def pipe_out(self, buff):
        self._device.ReadFromPipeOut(0xA0, buff) 
        
    def photon_count(self):
        self._device.UpdateWireOuts()
        return self._device.GetWireOutValue(0x20)
    
    def tdiff_count(self):
        self._device.UpdateWireOuts()
        return self._device.GetWireOutValue(0x21)
    
    def TTL_period(self):
        self._device.UpdateWireOuts()
        return self._device.GetWireOutValue(0x22)

    def fifo_r_count(self):
        self._device.UpdateWireOuts()
        return self._device.GetWireOutValue(0x23)
        
    def probe_dev(self):
        self._device.UpdateWireOuts()
        return self._device.GetWireOutValue(0x20), self._device.GetWireOutValue(0x21), self._device.GetWireOutValue(0x22), self._device.GetWireOutValue(0x23)


# here are demos for the using this module.        
if __name__ == '__main__':
    dev = XEM7305_MicroMotion_Detector()
    k = 0
    buff = [bytearray(4*1024), bytearray(4*1024), bytearray(4*1024), bytearray(4*1024), bytearray(4*1024), bytearray(4*1024), bytearray(4*1024), bytearray(4*1024), bytearray(4*1024)]
    ia_out = [[], [], [], [], [], [], [], [], []]  #integers
    photon_count = [0,0,0,0,0,0,0,0,0]
    tdiff_count = [0,0,0,0,0,0,0,0,0]
    TTL_period = [0,0,0,0,0,0,0,0,0]
    fifo_r_count = [0,0,0,0,0,0,0,0,0]
    #demo1: reset fpga, then pipeout 9 times the generated values.
    dev.reset_dev()
    #time.sleep(0.5)
    while (k < 9):
        photon_count[k] = dev.photon_count()
        tdiff_count[k] = dev.tdiff_count()
        TTL_period[k] = dev.TTL_period()
        fifo_r_count[k] = dev.fifo_r_count() # here is the number of the fifo values can be read out
        
        dev.pipe_out(buff[k])
        # fifo_r_count[k] = dev.fifo_r_count() # here is the number of the fifo values not yet pipeouted by the pipeout command. If it is not close 0, especially, if it is increasing, the fifo will have more and more values to be clogged.
        
        time.sleep(0.4) #to simulate delay.
        k = k+1
    
    for j in range(9):
        for i in range(1024):
            ia_out[j].append(buff[j][4*i + 3])
            ia_out[j].append(buff[j][4*i + 2])
            ia_out[j].append(buff[j][4*i + 1])
            ia_out[j].append(buff[j][4*i + 0])
        
        
    print(buff[0][:512])
    print(buff[0][4*1024-512:4*1024])
    print(buff[1][:512])
    print(buff[1][4*1024-512:4*1024])
    print(buff[2][:512])
    print(buff[2][4*1024-512:4*1024])
    print(buff[4][:512])
    print(buff[4][4*1024-512:4*1024])
    
    print("ia[0]")
    print(ia_out[0][:64])
    print(ia_out[0][64:512])
    print(ia_out[0][1*1024-64:1*1024])
    print("ia[1]")
    print(ia_out[1][:64])
    print(ia_out[1][64:512])
    print(ia_out[1][1*1024-64:1*1024])
    print("ia[2]")
    print(ia_out[2][:64])
    print(ia_out[2][64:512])
    print(ia_out[2][1*1024-64:1*1024])
    print("ia[3]")
    print(ia_out[3][:64])
    print(ia_out[3][64:512])
    print(ia_out[3][1*1024-64:1*1024])
    print("ia[4]")
    print(ia_out[4][:64])
    print(ia_out[4][64:512])
    print(ia_out[4][1*1024-64:1*1024])
    print("ia[7]")
    print(ia_out[7][:64])
    print(ia_out[7][64:512])
    print(ia_out[7][1*1024-64:1*1024])
    print("ia[8]")
    print(ia_out[8][:64])
    print(ia_out[8][64:512])
    print(ia_out[8][1*1024-64:1*1024])
    
    print(photon_count)
    print(tdiff_count)
    print(TTL_period)
    print(fifo_r_count)

