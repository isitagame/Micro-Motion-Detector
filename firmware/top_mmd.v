`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/17/2022 03:05:07 PM
// Design Name: 
// Module Name: top_mmd
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
//   Toplevel for MicroMotion Detector. 
//   For production.
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

module top_mmd #(parameter ADDRSIZE = 10, DATASIZE = 8, COUNTSIZE = 32)
(
  input  [4:0]  okUH,
  output [3:0]  okHU,
  input  [3:0]  okRSVD,
  inout  [31:0] okUHU,
  inout         okAA,
  input         sys_clkp,
  input         sys_clkn,
  input         c_ch1,
  input         c_ch2
    );

// target interface bus
wire c_clk, c_rst;
wire g_clk, g_rst, g_rst_fifo;
wire [112:0] okHE;
wire [64:0]  okEH;
wire [31:0] ep00wire, ep20wire, ep21wire, ep22wire;

assign g_rst = ep00wire[0];
assign g_rst_fifo = ep00wire[1]; //FIFO reset signal receive from PC. After FIFO reset, waiting for 30 clcoks to allow asserting WE/RE signals. On PC, first reset FIFO, then wait 0.001 s, then reset.

//sys_clk 
wire sys_clk;
IBUFGDS osc_clk(.O(sys_clk), .I(sys_clkp), .IB(sys_clkn));

//c_clk 460MHz 
clk_wiz_460mhz myclk(.clk_460MHz(c_clk), .clk_in1(sys_clk));
assign c_rst = g_rst;

//Simulated micromotion detector (a data generator)
//wire c_valid;
//wire [15:0] g_data, c_data;
//sim_receiver sim_receiver(.g_clk(c_clk), .g_rst(c_rst), 
//    .g_valid(c_valid), .g_data(c_data));

// Photon Counter 
wire [ COUNTSIZE-1 : 0 ] g_photon_cnt;
assign ep20wire = g_photon_cnt; // for wireOut photon count 
photon_counter #(COUNTSIZE) photon_counter(.g_rst(g_rst), .g_clk(g_clk), .g_ch1(c_ch1), .g_photon_cnt(g_photon_cnt));
    
// MicroMotion Detector
wire g_valid;
wire c_detect, c_detect_c2g;
wire [ DATASIZE-1 : 0 ] c_diff, c_diff_c2g, c_ch2_period, c_ch2_period_sync2ff;
wire [ COUNTSIZE-1 : 0 ] c_diff_count, c_diff_count_c2g;
//wire [ DATASIZE-1 : 0 ] c_diff_count_8;
micromotion_detect #(DATASIZE, COUNTSIZE) mmd(.c_clk(c_clk), .c_rst(c_rst), .c_ch1(c_ch1), .c_ch2(c_ch2), 
    .c_detect(c_detect), .c_ch2_period(c_ch2_period), .c_diff(c_diff), .c_diff_count(c_diff_count));
//assign c_diff_count = {24'd0, c_diff_count_8};

sync2ff #(.N(8)) sync_ch2_period(.clk(g_clk), .rst(g_rst), .d(c_ch2_period), .q(c_ch2_period_sync2ff)); //sync 2 flip_flops to deal metastablility problem
assign ep22wire = {24'd0, c_ch2_period_sync2ff}; // for wireOut ch2 period 

// CDC (Clock Domain Crossing)
wire [ DATASIZE-1 : 0 ] g_sync2_diff;
wire [ COUNTSIZE-1 : 0 ] g_sync2_diff_count;

cdc_c2g #(DATASIZE, COUNTSIZE) cdc_c2g(.c_clk(c_clk), .c_rst(c_rst),  
    .c_detect(c_detect), .c_diff(c_diff), .c_diff_count(c_diff_count),
    .c_detect_c2g(c_detect_c2g), .c_diff_c2g(c_diff_c2g), .c_diff_count_c2g(c_diff_count_c2g));
cdc_g2ram #(DATASIZE, COUNTSIZE) cdc_g2ram(.g_clk(g_clk), .g_rst(g_rst), 
    .c_detect_c2g(c_detect_c2g), .c_diff_c2g(c_diff_c2g), .c_diff_count_c2g(c_diff_count_c2g),
    .g_valid(g_valid), .g_sync2_diff(g_sync2_diff), .g_sync2_diff_count(g_sync2_diff_count));
    
assign ep21wire = g_sync2_diff_count;  // for wireOut diff count 

// FIFO 
wire g_fifofull, g_fifoempty;
wire [17:0] g_fifodatacount_w;
wire [15:0] g_fifodatacount_r;
wire [31:0] g_fifo_out;

wire g_goot_to_wr, g_good_to_rd;
assign g_goot_to_wr = (g_fifodatacount_w < 131072 - 128); //HARD CODING. Write data bus is 8 bits. 
assign g_good_to_rd = (g_fifodatacount_r > 0); // HARD CODING. Read data bus is 32 bits.

reg g_wren; // For FIFO write
reg g_pipeO_ready; // For FIFO read
reg [ DATASIZE-1 : 0 ] g_reg_fifo_in;
always @(posedge g_clk, posedge g_rst_fifo) begin
  if (g_rst_fifo) begin
    g_wren <= 0;
    g_pipeO_ready <= 0;
  end
  else begin
    if (g_valid && g_goot_to_wr) begin  
      g_wren <= 1;
      g_reg_fifo_in <= g_sync2_diff; // data to be written into FIFO
    end
    else g_wren <= 0;
    
    if (g_good_to_rd) g_pipeO_ready <= 1;
    else g_pipeO_ready <= 0;
  end
end 


fifo_generator_0 fifo(.clk(g_clk), .srst(g_rst_fifo),
    .din(g_reg_fifo_in), .wr_en(g_wren), .rd_en(g_piperead), .dout(g_fifo_out),
    .full(g_fifofull), .empty(g_fifoempty), .wr_data_count(g_fifodatacount_w), 
    .rd_data_count(g_fifodatacount_r));
    
reg [ 31 : 0 ] g_fifodatacount_r_reg;
always @(posedge g_clk) begin
  g_fifodatacount_r_reg <= {16'd0, g_fifodatacount_r}; // store in reg for output
end
    
wire [31:0] pipeO_data;
assign pipeO_data = g_fifo_out; 
wire [65*6-1:0] okEHx;

// okHost
okHost okHI( .okUH(okUH), .okHU(okHU), .okUHU(okUHU),
    .okRSVD(okRSVD), .okAA(okAA), .okClk(g_clk), 
    .okHE(okHE), .okEH(okEH));
    
okWireOR # (.N(6)) wireOR(okEH, okEHx);

okWireIn wi00(.okHE(okHE), .ep_addr(8'h00), .ep_dataout(ep00wire));
okWireOut wo20(.okHE(okHE), .okEH(okEHx[ 0*65 +: 65 ]), .ep_addr(8'h20), .ep_datain(ep20wire));
okWireOut wo21(.okHE(okHE), .okEH(okEHx[ 1*65 +: 65 ]), .ep_addr(8'h21), .ep_datain(ep21wire));
okWireOut wo22(.okHE(okHE), .okEH(okEHx[ 2*65 +: 65 ]), .ep_addr(8'h22), .ep_datain(ep22wire));
okWireOut wo23(.okHE(okHE), .okEH(okEHx[ 3*65 +: 65 ]), .ep_addr(8'h23), .ep_datain(g_fifodatacount_r_reg));
okBTPipeOut poA1(.okHE(okHE), .okEH(okEHx[ 5*65 +: 65 ]), .ep_addr(8'ha0), .ep_read(g_piperead), 
       .ep_blockstrobe(), .ep_datain(pipeO_data), .ep_ready(g_pipeO_ready));   
    
endmodule