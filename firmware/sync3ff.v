`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/18/2022 10:29:26 AM
// Design Name: 
// Module Name: sync3ff
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


module sync3ff #(parameter N = 16)
(
  input [ N-1:0 ] d,
  input clk, rst,
  output reg [ N-1:0 ] q
    );

reg [ N-1:0 ] q1, q2;
always @(posedge clk, posedge rst) begin
  if (rst) {q2, q1, q} <= 0; 
  else {q2, q1, q} <= {q1, d, q2};
end
endmodule
