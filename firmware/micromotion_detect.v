`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/16/2022 03:51:36 PM
// Design Name: 
// Module Name: micromotion_detect
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


module micromotion_detect #(parameter DATASIZE = 8, COUNTSIZE = 32)
(
  input c_clk,
  input c_rst,
  input c_ch1, //ch1 is the photon pulses from PMT, 
  input c_ch2, //ch2 is the Square Wave trig'd by the Sin Wave.
  output reg c_detect,
  output reg [ DATASIZE-1 : 0 ] c_ch2_period,
  output reg [ DATASIZE-1 : 0 ] c_diff,
  output reg [ COUNTSIZE-1 : 0 ] c_diff_count 
    );
  
reg [ DATASIZE-1 : 0 ] c_count;
reg c_start_count;
wire c_ch1_pedge, c_ch2_pedge; 
edge_detect ed1(.clk(c_clk), .trig(c_ch1), .pos_edge(c_ch1_pedge), .neg_edge());
edge_detect ed2(.clk(c_clk), .trig(c_ch2), .pos_edge(c_ch2_pedge), .neg_edge());

always @(posedge c_clk, posedge c_rst) begin
  if (c_rst) begin
    c_detect <= 0;
    c_diff <= 0;
    c_diff_count <= 0;
    c_count <= 0; 
    c_start_count <= 0;
    c_ch2_period <= 0;
  end 
  else begin
    if (c_ch2_pedge) begin
      if (c_count > 1) begin
        c_ch2_period <= c_count; // output ch2 period in the number of clocks
      end
      c_count <= 1; //restart counter for each ch2 rising edge.
      c_start_count <= 1;
    end 
    else if (c_start_count) c_count <= c_count + 1;
    if (c_ch1_pedge && c_start_count) begin
      c_detect <= 1'b1; // a ch1 (photon)  pulse detected
      c_diff <= c_count; // output the number of clocks from ch1 rising to ch2 rising, it should be converted to the number of clocks from ch2 to ch1.
      c_diff_count <= c_diff_count + 1; // increase the number of photon detected.
    end
    if (c_detect) c_detect <= 0; //make the c_detect signal as a one-clock pulse.
  end
end   
  
endmodule
