############################################################################
# XEM7305 - Xilinx constraints file
#
# Pin mappings for the XEM7305.  Use this as a template and comment out 
# the pins that are not used in your design.  (By default, map will fail
# if this file contains constraints for signals not in your design).
#
# Copyright (c) 2004-2016 Opal Kelly Incorporated
############################################################################

set_property CFGBVS GND [current_design]
set_property CONFIG_VOLTAGE 1.8 [current_design]
set_property BITSTREAM.GENERAL.COMPRESS True [current_design]

############################################################################
#System Clock
set_property IOSTANDARD LVDS_25 [get_ports {sys_clkp}]
set_property PACKAGE_PIN R2 [get_ports {sys_clkp}]
set_property IOSTANDARD LVDS_25 [get_ports {sys_clkn}]
set_property PACKAGE_PIN R1 [get_ports {sys_clkn}]
create_clock -name sys_clk -period 5 [get_ports sys_clkp]

############################################################################
## FrontPanel Host Interface
############################################################################
set_property PACKAGE_PIN T14 [get_ports {okHU[0]}]
set_property PACKAGE_PIN V14 [get_ports {okHU[1]}]
set_property PACKAGE_PIN T13 [get_ports {okHU[2]}]
set_property PACKAGE_PIN P13 [get_ports {okHU[3]}]
set_property SLEW FAST [get_ports {okHU[*]}]
set_property IOSTANDARD LVCMOS18 [get_ports {okHU[*]}]

set_property PACKAGE_PIN N15 [get_ports {okUH[0]}]
set_property PACKAGE_PIN R16 [get_ports {okUH[1]}]
set_property PACKAGE_PIN U15 [get_ports {okUH[2]}]
set_property PACKAGE_PIN V17 [get_ports {okUH[3]}]
set_property PACKAGE_PIN M13 [get_ports {okUH[4]}]
set_property IOSTANDARD LVCMOS18 [get_ports {okUH[*]}]

set_property PACKAGE_PIN T18 [get_ports {okUHU[0]}]
set_property PACKAGE_PIN R18 [get_ports {okUHU[1]}]
set_property PACKAGE_PIN P18 [get_ports {okUHU[2]}]
set_property PACKAGE_PIN N18 [get_ports {okUHU[3]}]
set_property PACKAGE_PIN M18 [get_ports {okUHU[4]}]
set_property PACKAGE_PIN M17 [get_ports {okUHU[5]}]
set_property PACKAGE_PIN M16 [get_ports {okUHU[6]}]
set_property PACKAGE_PIN N13 [get_ports {okUHU[7]}]
set_property PACKAGE_PIN N14 [get_ports {okUHU[8]}]
set_property PACKAGE_PIN M14 [get_ports {okUHU[9]}]
set_property PACKAGE_PIN L18 [get_ports {okUHU[10]}]
set_property PACKAGE_PIN L17 [get_ports {okUHU[11]}]
set_property PACKAGE_PIN M15 [get_ports {okUHU[12]}]
set_property PACKAGE_PIN L14 [get_ports {okUHU[13]}]
set_property PACKAGE_PIN K18 [get_ports {okUHU[14]}]
set_property PACKAGE_PIN K17 [get_ports {okUHU[15]}]
set_property PACKAGE_PIN R13 [get_ports {okUHU[16]}]
set_property PACKAGE_PIN P16 [get_ports {okUHU[17]}]
set_property PACKAGE_PIN P17 [get_ports {okUHU[18]}]
set_property PACKAGE_PIN V13 [get_ports {okUHU[19]}]
set_property PACKAGE_PIN P14 [get_ports {okUHU[20]}]
set_property PACKAGE_PIN U12 [get_ports {okUHU[21]}]
set_property PACKAGE_PIN T11 [get_ports {okUHU[22]}]
set_property PACKAGE_PIN P15 [get_ports {okUHU[23]}]
set_property PACKAGE_PIN U11 [get_ports {okUHU[24]}]
set_property PACKAGE_PIN V15 [get_ports {okUHU[25]}]
set_property PACKAGE_PIN R17 [get_ports {okUHU[26]}]
set_property PACKAGE_PIN U18 [get_ports {okUHU[27]}]
set_property PACKAGE_PIN T12 [get_ports {okUHU[28]}]
set_property PACKAGE_PIN L16 [get_ports {okUHU[29]}]
set_property PACKAGE_PIN V16 [get_ports {okUHU[30]}]
set_property PACKAGE_PIN T15 [get_ports {okUHU[31]}]
set_property SLEW FAST [get_ports {okUHU[*]}]
set_property IOSTANDARD LVCMOS18 [get_ports {okUHU[*]}]

set_property PACKAGE_PIN U17 [get_ports {okRSVD[0]}]
set_property PACKAGE_PIN U16 [get_ports {okRSVD[1]}]
set_property PACKAGE_PIN R15 [get_ports {okRSVD[2]}]
set_property PACKAGE_PIN V12 [get_ports {okRSVD[3]}]
set_property IOSTANDARD LVCMOS18 [get_ports {okRSVD[*]}]

set_property PACKAGE_PIN R11 [get_ports {okAA}]
set_property IOSTANDARD LVCMOS18 [get_ports {okAA}]


create_clock -name okUH0 -period 9.920 [get_ports {okUH[0]}]

set_input_delay -add_delay -max -clock [get_clocks {okUH0}]  8.000 [get_ports {okUH[*]}]
set_input_delay -add_delay -min -clock [get_clocks {okUH0}] 10.000 [get_ports {okUH[*]}]
set_multicycle_path -setup -from [get_ports {okUH[*]}] 2

set_input_delay -add_delay -max -clock [get_clocks {okUH0}]  8.000 [get_ports {okUHU[*]}]
set_input_delay -add_delay -min -clock [get_clocks {okUH0}]  2.000 [get_ports {okUHU[*]}]
set_multicycle_path -setup -from [get_ports {okUHU[*]}] 2

set_output_delay -add_delay -max -clock [get_clocks {okUH0}]  2.000 [get_ports {okHU[*]}]
set_output_delay -add_delay -min -clock [get_clocks {okUH0}]  -0.500 [get_ports {okHU[*]}]

set_output_delay -add_delay -max -clock [get_clocks {okUH0}]  2.000 [get_ports {okUHU[*]}]
set_output_delay -add_delay -min -clock [get_clocks {okUH0}]  -0.500 [get_ports {okUHU[*]}]

# LEDs #####################################################################
set_property PACKAGE_PIN J5 [get_ports {led[0]}]
set_property PACKAGE_PIN G6 [get_ports {led[1]}]
set_property IOSTANDARD LVCMOS15 [get_ports {led[0]}]
set_property IOSTANDARD LVCMOS15 [get_ports {led[1]}]
set_property PACKAGE_PIN R12 [get_ports {led[2]}]
set_property PACKAGE_PIN L13 [get_ports {led[3]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led[2]}]
set_property IOSTANDARD LVCMOS18 [get_ports {led[3]}]

# Ch1 and Ch2 #########################################
set_property IOSTANDARD LVCMOS25 [get_ports {c_ch1}]
set_property IOSTANDARD LVCMOS25 [get_ports {c_ch2}]
#set_property PACKAGE_PIN V5 [get_ports {c_ch1}]
set_property PACKAGE_PIN V4 [get_ports {c_ch1}]
set_property PACKAGE_PIN V3 [get_ports {c_ch2}]

# clock groups
set_clock_groups -asynchronous -group [get_clocks clk_460MHz_clk_wiz_460mhz] -group [get_clocks mmcm0_clk0]
#set_clock_groups -asynchronous -group [get_clocks {clk_460MHz_clk_wiz_460mhz}] -group [get_clocks {mmcm0_clk0}]
#set_clock_groups -asynchronous -group [get_clocks -of_objects [get_pins myclk/inst/clk_460MHz_clk_wiz_460mhz]] -group [get_clocks {mmcm0_clk0}]
#set_clock_groups -asynchronous -group [get_clocks -of [get_pins myclk/inst/clk_460MHz]] -group [get_clocks {mmcm0_clk0}]