`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/24/2022 10:43:50 AM
// Design Name: 
// Module Name: photon_counter
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


module photon_counter #(parameter COUNTSIZE = 32)
(
  input g_rst,
  input g_clk,
  input g_ch1,
  output reg[ COUNTSIZE-1 : 0 ] g_photon_cnt
    );

wire pos_edge;
edge_detect edge_detect(.clk(g_clk), .trig(g_ch1), .pos_edge(pos_edge), .neg_edge());

always @ (posedge g_rst, posedge g_clk) begin
  if (g_rst) g_photon_cnt <= 0;
  else begin
    if (pos_edge) g_photon_cnt <= g_photon_cnt + 1;
  end 
end 
endmodule
