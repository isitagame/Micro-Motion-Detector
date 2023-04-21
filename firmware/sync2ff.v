`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/17/2022 05:15:59 PM
// Design Name: 
// Module Name: sync2ff
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
//   Synchronizer with 2 Flip-flops. Generates clock-synchronized sig_out from sig_in.
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module sync2ff #(parameter N = 16)
(
  input [ N-1:0 ] d,
  input clk, rst,
  output reg [ N-1:0 ] q
    );

reg [ N-1:0 ] q1;
always @(posedge clk, posedge rst) begin
  if (rst) {q1, q} <= 0; 
  else {q1, q} <= {d, q1};
end 
endmodule
