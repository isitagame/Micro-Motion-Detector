# Micro-Motion-Detector

- This is a home-made Micro-Motion Detector based on an Opal Kelly XEM7305 FPGA board.
- Its firmware is written in verilog, software(API module and GUI) in python.

##
# Usage
- python MMD_GUI.py

##
# Simulation
- python MMD_GUI.py SIMU 
(If you don't have a FPGA board, this argument can run the program as a simulator.)

##
# Requirments
- Python3.7 or later
- PyQt5
- pyqtgraph 0.12 or later

# Specifications
- Histogram update interval option: 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000 ms.
- Time resolution:  2.17 ns.
- RF trigger frequency range:   > 1.8 MHz (Period < 256 * 2.17 ns ).
- PMT pulse arriving rate range:   
  
  acceptable: 1/s ~ 500K/s 
  
  recommended:  10/s ~ 100K/s
  
  ( Recommended Histogram_update_interval * PMT_pulse_arriving_rate <= 16000 , it is limited by the buff depth )
  
##
# File Description
- MMD_GUI.py: GUI written in Python
- XEM7305_MicroMotion_Detector.py: Module(API) of the detector written in Python
- micromotion_detector.bit: compiled firmware for the detector
- firmware/*: source codes of the firmware
- ok*, _ok*: Opal Kelly API files for the FPGA board (python3.7, Windows)

