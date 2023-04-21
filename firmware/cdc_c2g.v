`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/17/2022 02:08:21 PM
// Design Name: 
// Module Name: cdc_c2g
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
//   The module is a CDC(Clock Domain Crossing) interface. 
//   It holds signals created in micromotion_detect (count domain, 460MHz) longer enough 
//     to let RAM logic (global domain, 200MHz) to write and read.
//   The design rule is to hold sigal 1.5X long as receiving domain clock.
//   In this design, we extend sigals 460/200 X 1.5 ~ 4 clocks long.
// Dependencies: 
//   
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module cdc_c2g #(parameter DATASIZE = 16, COUNTSIZE = 32)
(
  input c_clk,
  input c_rst,
  input c_detect,
  input [ DATASIZE-1 : 0 ] c_diff,
  input [ COUNTSIZE-1 : 0 ] c_diff_count,
  output reg c_detect_c2g,
  output reg [ DATASIZE-1 : 0 ] c_diff_c2g,
  output reg [ COUNTSIZE-1 : 0 ] c_diff_count_c2g
    );

localparam WAIT = 2'd0,
           HOLD_POS = 2'd1, //to keep the high signal (1) long enough
           HOLD_NEG = 2'd2; //to keep the low signal (0) long enough

localparam CDC_EXTENT_CLOCKS = 3'd7; // attention: hold for 7 clocks. HARD CODING! (460MHz to 100.8MHz. 4.6 x 1.5 = 7)
           
reg [1:0] c_state;
reg [2:0] c_hold_cnt; // attention: hold for 7 clocks. HARD CODING! (460MHz to 100.8MHz. 4.6 x 1.5 = 7)


always @(posedge c_clk, posedge c_rst) begin
  if (c_rst) begin
    c_detect_c2g <= 1'b0;
    c_diff_c2g <= 16'd0;
    c_diff_count_c2g <= 32'd0;
    c_state <= WAIT;
    c_hold_cnt <= 0;
  end 
  else begin
    case (c_state)
      WAIT: begin
        if (c_detect) begin
          c_detect_c2g <= 1;
          c_diff_c2g <= c_diff;
          c_diff_count_c2g <= c_diff_count;
          c_state <= HOLD_POS;
          c_hold_cnt <= 1;
        end           
      end
      HOLD_POS: begin
        if (c_hold_cnt < CDC_EXTENT_CLOCKS) c_hold_cnt <= c_hold_cnt + 1; //attention: hold High for 7 clocks. HARD CODING!
        else begin
          c_state <= HOLD_NEG;
          c_detect_c2g <= 1'b0;
          c_hold_cnt <= 1; 
        end
      end
      HOLD_NEG: begin
        if (c_hold_cnt < CDC_EXTENT_CLOCKS - 1 ) c_hold_cnt <= c_hold_cnt + 1; //attention: hold Low for 7 clocks. HARD CODING! HOLD_NEG is 1 clock shorter than HOLD_POS, because WAIT will add 1 clock to sample a new c_detect.
        else begin
          c_state <= WAIT;
          c_hold_cnt <= 0;
        end
      end
    endcase    
  end 
end 
endmodule
