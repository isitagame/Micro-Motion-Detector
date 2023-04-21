`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/17/2022 05:06:11 PM
// Design Name: 
// Module Name: cdc_g2ram
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module cdc_g2ram  #(parameter DATASIZE = 16, COUNTSIZE = 32)
(
  input g_clk,
  input g_rst,
  input c_detect_c2g,
  input [ DATASIZE-1 : 0 ] c_diff_c2g,
  input [ COUNTSIZE-1 : 0 ] c_diff_count_c2g,
  output g_valid, // valid to write to RAM
  output [ DATASIZE-1 : 0 ] g_sync2_diff,
  output [ COUNTSIZE-1 : 0 ] g_sync2_diff_count
    );

wire g_sync2_detect;
sync2ff #(.N(1)) sync_detect(.clk(g_clk), .rst(g_rst), .d(c_detect_c2g), .q(g_sync2_detect));
sync3ff #(.N(DATASIZE)) sync_diff(.clk(g_clk), .rst(g_rst), .d(c_diff_c2g), .q(g_sync2_diff));
sync3ff #(.N(COUNTSIZE)) sync_diff_count(.clk(g_clk), .rst(g_rst), .d(c_diff_count_c2g), .q(g_sync2_diff_count));
edge_detect ed(.clk(g_clk), .trig(g_sync2_detect), .pos_edge(g_valid), .neg_edge()); // ATTENTION: g_valid detected here will be 1 clock later than g_sync2_detect, and g_sync2_diff, and g_sync2_diff_count. IF test failed, g_sync2_diff and g_sync2_diff_count should be output from sync3ff.

endmodule
