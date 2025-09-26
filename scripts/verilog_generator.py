#!/usr/bin/env python3
"""
SPI Verilog Code Generator
Generates custom SPI core based on configuration parameters
"""

import os
import sys
from jinja2 import Template

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_parser import SPIConfig


class VerilogGenerator:
    """Generates Verilog code from SPI configuration"""

    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')

    def generate_spi_core(self, config: SPIConfig) -> str:
        """
        Generate SPI core Verilog code from configuration

        Args:
            config: SPIConfig object with parameters

        Returns:
            Generated Verilog code as string
        """

        # Load template
        template_path = os.path.join(self.template_dir, 'spi_core.v.tmpl')
        with open(template_path, 'r') as f:
            template_content = f.read()

        template = Template(template_content)

        # Generate code
        verilog_code = template.render(
            MODE=config.mode,
            DATA_WIDTH=config.data_width,
            NUM_SLAVES=config.num_slaves,
            SLAVE_ACTIVE_LOW=config.slave_active_low,
            MSB_FIRST=config.msb_first
        )

        return verilog_code


    def save_verilog_file(self, config: SPIConfig, filename: str = None) -> str:
        """
        Generate and save Verilog code to file

        Args:
            config: SPIConfig object
            filename: Output filename (optional)

        Returns:
            Path to generated file
        """

        if filename is None:
            # Use simple naming for string issue numbers (like example1, example2, etc.)
            if isinstance(config.issue_number, str):
                filename = f"{config.issue_number}.v"
            else:
                # Use detailed naming for numeric issue numbers
                filename = f"spi_master_mode{config.mode}_{config.data_width}bit.v"

        verilog_code = self.generate_spi_core(config)

        # Ensure issue-specific results directory exists
        issue_dir = f'results/issue-{config.issue_number}'
        os.makedirs(issue_dir, exist_ok=True)

        filepath = os.path.join(issue_dir, filename)
        with open(filepath, 'w') as f:
            f.write(verilog_code)

        print(f"✅ Generated Verilog code: {filepath}")
        return filepath

    def generate_testbench(self, config: SPIConfig, vcd_filename: str = "spi_waveform.vcd") -> str:
        """
        Generate testbench for the SPI core

        Args:
            config: SPIConfig object

        Returns:
            Testbench Verilog code as string
        """

        testbench_template = """
`timescale 1ns / 1ps

module spi_master_tb;

    // Parameters
    parameter MODE = {{ config.mode }};
    parameter DATA_WIDTH = {{ config.data_width }};
    parameter NUM_SLAVES = {{ config.num_slaves }};

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
        $display("Configuration: Mode {{ config.mode }}, {{ config.data_width }}-bit data, {{ config.num_slaves }} slaves");

        // Test comprehensive SPI transactions
        {% for slave in range(config.num_slaves) %}

        $display("--- Testing Slave {{ slave }} ---");

        // Test 1: Basic data transmission (16-bit pattern)
        tx_data = {{ "16'hAA55" if config.data_width >= 16 else "8'hA5" }};
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Transmission complete for slave {{ slave }}");

        // Small delay between transactions
        #1000;

        // Test 2: Different data pattern (alternating bits)
        tx_data = {{ "16'hCCCC" if config.data_width >= 16 else "8'hCC" }};
        $display("TX Data: 0x%h", tx_data);
        start_tx = 1;
        #50;
        start_tx = 0;

        wait (!busy);
        $display("✓ Second transmission complete for slave {{ slave }}");

        {% endfor %}

        // Test reception from all slaves
        $display("--- Testing Reception ---");

        {% for slave in range(config.num_slaves) %}
        // Prepare to receive data from slave {{ slave }}
        start_rx = 1;
        #50;
        start_rx = 0;

        // Simulate slave providing response data
        #200;
        // Slave {{ slave }} responds with pattern: 0x{{ "55AA" if config.data_width >= 16 else "5A" }}{{ slave }}
        miso = {{ "1'b1" if (config.mode in [1,3]) else "1'b0" }};  // Data bit based on CPHA
        #100;
        miso = {{ "1'b0" if (config.mode in [1,3]) else "1'b1" }};

        wait (!busy);
        $display("✓ Reception complete from slave {{ slave }}");

        {% endfor %}

        // Test 3: Burst transmission (multiple frames)
        $display("--- Testing Burst Transmission ---");
        {% for i in range(3) %}
        tx_data = {{ "16'h{:04X}".format((i * 0x1111) % 0x10000) if config.data_width >= 16 else "8'h{:02X}".format((i * 0x11) % 0x100) }};
        $display("Burst TX[%d]: 0x%h", {{ i }}, tx_data);
        start_tx = 1;
        #30;
        start_tx = 0;

        wait (!busy);
        $display("✓ Burst transmission {{ i }} complete");
        #500;  // Inter-frame delay
        {% endfor %}

        // Test 4: Continuous read operations
        $display("--- Testing Continuous Read Operations ---");
        {% for slave in range(2 if config.num_slaves > 2 else config.num_slaves) %}
        $display("Reading from slave {{ slave }}...");

        // Simulate multiple read operations
        {% for read in range(2) %}
        start_rx = 1;
        #40;
        start_rx = 0;

        // Simulate slave response with incrementing data
        #150;
        miso = {{ "1'b1" if read == 0 else "1'b0" }};

        wait (!busy);
        $display("✓ Read operation {{ read }} from slave {{ slave }} complete");
        #300;
        {% endfor %}
        {% endfor %}

        // Test 5: Mixed read/write operations
        $display("--- Testing Mixed Read/Write Operations ---");

        // Write configuration data
        tx_data = {{ "16'h1234" if config.data_width >= 16 else "8'h12" }};
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
        $dumpfile("{{ vcd_filename }}");
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
"""

        template = Template(testbench_template)
        testbench_code = template.render(config=config, vcd_filename=vcd_filename)

        return testbench_code

    def save_testbench(self, config: SPIConfig, filename: str = None) -> str:
        """
        Generate and save testbench to file

        Args:
            config: SPIConfig object
            filename: Output filename (optional)

        Returns:
            Path to generated testbench file
        """

        if filename is None:
            # Use simple naming for string issue numbers (like example1, example2, etc.)
            if isinstance(config.issue_number, str):
                filename = f"{config.issue_number}_tb.v"
            else:
                # Use detailed naming for numeric issue numbers
                filename = f"spi_master_tb_mode{config.mode}.v"

        # Ensure issue-specific results directory exists
        issue_dir = f'results/issue-{config.issue_number}'
        os.makedirs(issue_dir, exist_ok=True)

        # Generate VCD filename for this issue
        vcd_filename = f"{issue_dir}/spi_waveform.vcd"

        testbench_code = self.generate_testbench(config, vcd_filename)

        filepath = os.path.join(issue_dir, filename)
        with open(filepath, 'w') as f:
            f.write(testbench_code)

        print(f"✅ Generated testbench: {filepath}")
        return filepath


def main():
    """Test the Verilog generator with sample configuration"""

    # Create sample configuration
    config = SPIConfig(
        issue_number=123,
        mode=0,
        data_width=16,
        num_slaves=2,
        slave_active_low=True,
        msb_first=True,
        interrupts=True,
        fifo_buffers=False,
        dma_support=False,
        multi_master=False,
        test_duration="standard",
        clock_jitter_test=True,
        waveform_capture=True,
        email="test@example.com",
        github_username="testuser"
    )

    generator = VerilogGenerator()

    try:
        # Generate Verilog core
        core_file = generator.save_verilog_file(config)

        # Generate testbench
        tb_file = generator.save_testbench(config)

        print(f"✅ Generated files:")
        print(f"   - {core_file}")
        print(f"   - {tb_file}")

    except Exception as e:
        print(f"❌ Error generating Verilog code: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
