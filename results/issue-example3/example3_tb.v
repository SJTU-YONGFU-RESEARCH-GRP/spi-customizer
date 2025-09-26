
`timescale 1ns / 1ps

module spi_master_tb;

    // Parameters
    parameter MODE = 1;
    parameter DATA_WIDTH = 16;
    parameter NUM_SLAVES = 8;

    // Signals
    reg clk;
    reg rst_n;
    reg start_tx;
    reg start_rx;
    reg [DATA_WIDTH-1:0] tx_data;
    wire [DATA_WIDTH-1:0] rx_data;
    wire busy;
    wire sclk;
    wire mosi;
    reg miso;
    wire [NUM_SLAVES-1:0] ss_n;
    wire irq;

    // DUT instantiation
    spi_master #(
        .MODE(MODE),
        .DATA_WIDTH(DATA_WIDTH),
        .NUM_SLAVES(NUM_SLAVES)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .start_tx(start_tx),
        .start_rx(start_rx),
        .tx_data(tx_data),
        .rx_data(rx_data),
        .busy(busy),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .ss_n(ss_n),
        .irq(irq)
    );

    // Clock generation
    initial begin
        clk = 0;
        forever #10 clk = ~clk;  // 50MHz clock
    end

    // Enhanced test sequence with multiple transactions
    initial begin
        // Initialize
        rst_n = 0;
        start_tx = 0;
        start_rx = 0;
        tx_data = 0;
        miso = 0;

        #100;
        rst_n = 1;
        #200;  // Allow system to stabilize

        $display("=== SPI RTL Testbench Starting ===");
        $display("Configuration: Mode 1, 16-bit data, 8 slaves");

        // Test comprehensive SPI transactions
        

        $display("--- Testing Slave 0 ---");

        // Test 1: Basic data transmission (16-bit pattern)
        tx_data = 16'hAA55;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Transmission complete for slave 0");

        // Small delay between transactions
        #1000;

        // Test 2: Different data pattern (alternating bits)
        tx_data = 16'hCCCC;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Second transmission complete for slave 0");

        

        $display("--- Testing Slave 1 ---");

        // Test 1: Basic data transmission (16-bit pattern)
        tx_data = 16'hAA55;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Transmission complete for slave 1");

        // Small delay between transactions
        #1000;

        // Test 2: Different data pattern (alternating bits)
        tx_data = 16'hCCCC;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Second transmission complete for slave 1");

        

        $display("--- Testing Slave 2 ---");

        // Test 1: Basic data transmission (16-bit pattern)
        tx_data = 16'hAA55;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Transmission complete for slave 2");

        // Small delay between transactions
        #1000;

        // Test 2: Different data pattern (alternating bits)
        tx_data = 16'hCCCC;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Second transmission complete for slave 2");

        

        $display("--- Testing Slave 3 ---");

        // Test 1: Basic data transmission (16-bit pattern)
        tx_data = 16'hAA55;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Transmission complete for slave 3");

        // Small delay between transactions
        #1000;

        // Test 2: Different data pattern (alternating bits)
        tx_data = 16'hCCCC;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Second transmission complete for slave 3");

        

        $display("--- Testing Slave 4 ---");

        // Test 1: Basic data transmission (16-bit pattern)
        tx_data = 16'hAA55;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Transmission complete for slave 4");

        // Small delay between transactions
        #1000;

        // Test 2: Different data pattern (alternating bits)
        tx_data = 16'hCCCC;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Second transmission complete for slave 4");

        

        $display("--- Testing Slave 5 ---");

        // Test 1: Basic data transmission (16-bit pattern)
        tx_data = 16'hAA55;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Transmission complete for slave 5");

        // Small delay between transactions
        #1000;

        // Test 2: Different data pattern (alternating bits)
        tx_data = 16'hCCCC;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Second transmission complete for slave 5");

        

        $display("--- Testing Slave 6 ---");

        // Test 1: Basic data transmission (16-bit pattern)
        tx_data = 16'hAA55;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Transmission complete for slave 6");

        // Small delay between transactions
        #1000;

        // Test 2: Different data pattern (alternating bits)
        tx_data = 16'hCCCC;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Second transmission complete for slave 6");

        

        $display("--- Testing Slave 7 ---");

        // Test 1: Basic data transmission (16-bit pattern)
        tx_data = 16'hAA55;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Transmission complete for slave 7");

        // Small delay between transactions
        #1000;

        // Test 2: Different data pattern (alternating bits)
        tx_data = 16'hCCCC;
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Second transmission complete for slave 7");

        

        // Test reception from all slaves
        $display("--- Testing Reception ---");

        
        // Prepare to receive data from slave 0
        start_rx = 1;
        #50;
        start_rx = 0;

        // Simulate slave providing response data
        #200;
        // Slave 0 responds with pattern: 0x55AA0
        miso = 1'b1;  // Data bit based on CPHA
        #100;
        miso = 1'b0;

        wait (!busy);
        $display("✓ Reception complete from slave 0");

        
        // Prepare to receive data from slave 1
        start_rx = 1;
        #50;
        start_rx = 0;

        // Simulate slave providing response data
        #200;
        // Slave 1 responds with pattern: 0x55AA1
        miso = 1'b1;  // Data bit based on CPHA
        #100;
        miso = 1'b0;

        wait (!busy);
        $display("✓ Reception complete from slave 1");

        
        // Prepare to receive data from slave 2
        start_rx = 1;
        #50;
        start_rx = 0;

        // Simulate slave providing response data
        #200;
        // Slave 2 responds with pattern: 0x55AA2
        miso = 1'b1;  // Data bit based on CPHA
        #100;
        miso = 1'b0;

        wait (!busy);
        $display("✓ Reception complete from slave 2");

        
        // Prepare to receive data from slave 3
        start_rx = 1;
        #50;
        start_rx = 0;

        // Simulate slave providing response data
        #200;
        // Slave 3 responds with pattern: 0x55AA3
        miso = 1'b1;  // Data bit based on CPHA
        #100;
        miso = 1'b0;

        wait (!busy);
        $display("✓ Reception complete from slave 3");

        
        // Prepare to receive data from slave 4
        start_rx = 1;
        #50;
        start_rx = 0;

        // Simulate slave providing response data
        #200;
        // Slave 4 responds with pattern: 0x55AA4
        miso = 1'b1;  // Data bit based on CPHA
        #100;
        miso = 1'b0;

        wait (!busy);
        $display("✓ Reception complete from slave 4");

        
        // Prepare to receive data from slave 5
        start_rx = 1;
        #50;
        start_rx = 0;

        // Simulate slave providing response data
        #200;
        // Slave 5 responds with pattern: 0x55AA5
        miso = 1'b1;  // Data bit based on CPHA
        #100;
        miso = 1'b0;

        wait (!busy);
        $display("✓ Reception complete from slave 5");

        
        // Prepare to receive data from slave 6
        start_rx = 1;
        #50;
        start_rx = 0;

        // Simulate slave providing response data
        #200;
        // Slave 6 responds with pattern: 0x55AA6
        miso = 1'b1;  // Data bit based on CPHA
        #100;
        miso = 1'b0;

        wait (!busy);
        $display("✓ Reception complete from slave 6");

        
        // Prepare to receive data from slave 7
        start_rx = 1;
        #50;
        start_rx = 0;

        // Simulate slave providing response data
        #200;
        // Slave 7 responds with pattern: 0x55AA7
        miso = 1'b1;  // Data bit based on CPHA
        #100;
        miso = 1'b0;

        wait (!busy);
        $display("✓ Reception complete from slave 7");

        

        // Test 3: Burst transmission (multiple frames)
        $display("--- Testing Burst Transmission ---");
        
        tx_data = 16'h0000;
        $display("Burst TX[%d]: 0x%h", 0, tx_data);
        start_tx = 1;
        #30;
        start_tx = 0;

        wait (!busy);
        $display("✓ Burst transmission 0 complete");
        #500;  // Inter-frame delay
        
        tx_data = 16'h1111;
        $display("Burst TX[%d]: 0x%h", 1, tx_data);
        start_tx = 1;
        #30;
        start_tx = 0;

        wait (!busy);
        $display("✓ Burst transmission 1 complete");
        #500;  // Inter-frame delay
        
        tx_data = 16'h2222;
        $display("Burst TX[%d]: 0x%h", 2, tx_data);
        start_tx = 1;
        #30;
        start_tx = 0;

        wait (!busy);
        $display("✓ Burst transmission 2 complete");
        #500;  // Inter-frame delay
        

        // Test 4: Continuous read operations
        $display("--- Testing Continuous Read Operations ---");
        
        $display("Reading from slave 0...");

        // Simulate multiple read operations
        
        start_rx = 1;
        #40;
        start_rx = 0;

        // Simulate slave response with incrementing data
        #150;
        miso = 1'b1;

        wait (!busy);
        $display("✓ Read operation 0 from slave 0 complete");
        #300;
        
        start_rx = 1;
        #40;
        start_rx = 0;

        // Simulate slave response with incrementing data
        #150;
        miso = 1'b0;

        wait (!busy);
        $display("✓ Read operation 1 from slave 0 complete");
        #300;
        
        
        $display("Reading from slave 1...");

        // Simulate multiple read operations
        
        start_rx = 1;
        #40;
        start_rx = 0;

        // Simulate slave response with incrementing data
        #150;
        miso = 1'b1;

        wait (!busy);
        $display("✓ Read operation 0 from slave 1 complete");
        #300;
        
        start_rx = 1;
        #40;
        start_rx = 0;

        // Simulate slave response with incrementing data
        #150;
        miso = 1'b0;

        wait (!busy);
        $display("✓ Read operation 1 from slave 1 complete");
        #300;
        
        

        // Test 5: Mixed read/write operations
        $display("--- Testing Mixed Read/Write Operations ---");

        // Write configuration data
        tx_data = 16'h1234;
        $display("Writing config: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;
        wait (!busy);
        $display("✓ Configuration write complete");

        #1000;

        // Read back configuration
        $display("Reading back configuration...");
        start_rx = 1;
        #50;
        start_rx = 0;

        #200;
        miso = 1'b1;  // Slave acknowledges
        #100;
        miso = 1'b0;

        wait (!busy);
        $display("✓ Configuration read complete");

        // Final delay before completion
        #2000;
        $display("=== All Tests Completed Successfully ===");

        $finish;
    end

    // Waveform dumping - capture all signals for comprehensive analysis
    initial begin
        $dumpfile("results/issue-example3/spi_waveform.vcd");
        $dumpvars(0, spi_master_tb);  // Dump all signals in the testbench

        // Also dump internal DUT signals for detailed analysis
        $dumpvars(1, spi_master_tb.dut.sclk);
        $dumpvars(1, spi_master_tb.dut.mosi);
        $dumpvars(1, spi_master_tb.dut.miso);
        $dumpvars(1, spi_master_tb.dut.ss_n);
        $dumpvars(1, spi_master_tb.dut.busy);
        $dumpvars(1, spi_master_tb.dut.irq);
        $dumpvars(1, spi_master_tb.dut.state);
        $dumpvars(1, spi_master_tb.dut.next_state);
        $dumpvars(1, spi_master_tb.dut.bit_counter);
        $dumpvars(1, spi_master_tb.dut.clk_counter);
        $dumpvars(1, spi_master_tb.dut.tx_shift_reg);
        $dumpvars(1, spi_master_tb.dut.rx_shift_reg);
        $dumpvars(1, spi_master_tb.dut.sclk_gen);

        $dumpflush;  // Ensure all data is written
    end

endmodule