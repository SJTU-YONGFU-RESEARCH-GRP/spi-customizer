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

        # Calculate derived parameters
        derived_params = self._calculate_derived_params(config)

        # Generate code
        verilog_code = template.render(
            MODE=config.mode,
            CLK_FREQ=config.clock_frequency,
            DATA_WIDTH=config.data_width,
            NUM_SLAVES=config.num_slaves,
            SLAVE_ACTIVE_LOW=config.slave_active_low,
            MSB_FIRST=config.msb_first,
            derived_params=derived_params
        )

        return verilog_code

    def _calculate_derived_params(self, config: SPIConfig) -> dict:
        """Calculate derived parameters for the Verilog module"""

        # SCLK half period calculation (assuming 50MHz system clock)
        system_clock = 50_000_000  # 50 MHz
        target_sclk = config.clock_frequency * 1_000_000  # Convert to Hz
        sclk_half_period = system_clock // (2 * target_sclk)

        return {
            'sclk_half_period': sclk_half_period,
            'system_clock': system_clock,
            'target_sclk': target_sclk
        }

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
                filename = f"spi_master_mode{config.mode}_{config.clock_frequency}MHz_{config.data_width}bit.v"

        verilog_code = self.generate_spi_core(config)

        # Ensure issue-specific results directory exists
        issue_dir = f'results/issue-{config.issue_number}'
        os.makedirs(issue_dir, exist_ok=True)

        filepath = os.path.join(issue_dir, filename)
        with open(filepath, 'w') as f:
            f.write(verilog_code)

        print(f"✅ Generated Verilog code: {filepath}")
        return filepath

    def generate_testbench(self, config: SPIConfig) -> str:
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
    parameter CLK_FREQ = {{ config.clock_frequency | int }};
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
        .CLK_FREQ(CLK_FREQ),
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

    // Test sequence
    initial begin
        // Initialize
        rst_n = 0;
        start_tx = 0;
        start_rx = 0;
        tx_data = 0;
        miso = 0;

        #100;
        rst_n = 1;
        #100;

        // Test transmission
        {% for slave in range(config.num_slaves) %}
        // Test slave {{ slave }}
        tx_data = {{ "16'd43690" if config.data_width == 16 else ("32'hABCD_EF12" if config.data_width == 32 else "8'hA5") }};
        start_tx = 1;
        #20;
        start_tx = 0;

        wait (!busy);
        $display("Transmission complete for slave {{ slave }}");

        {% endfor %}

        // Test reception
        start_rx = 1;
        #20;
        start_rx = 0;

        // Simulate slave response
        #50;
        miso = 1;
        #50;
        miso = 0;

        wait (!busy);
        $display("Reception complete");

        #1000;
        $finish;
    end

    // Waveform dumping
    initial begin
        $dumpfile("spi_waveform.vcd");
        $dumpvars(0, spi_master_tb);
    end

endmodule
"""

        template = Template(testbench_template)
        testbench_code = template.render(config=config)

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
                filename = f"spi_master_tb_mode{config.mode}_{config.clock_frequency}MHz.v"

        testbench_code = self.generate_testbench(config)

        # Ensure issue-specific results directory exists
        issue_dir = f'results/issue-{config.issue_number}'
        os.makedirs(issue_dir, exist_ok=True)

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
        clock_frequency=25.0,
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
