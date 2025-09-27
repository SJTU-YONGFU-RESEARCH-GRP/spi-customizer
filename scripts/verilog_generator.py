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

        # Determine which template to use based on SPI role
        if config.spi_role.lower() == "slave":
            template_name = 'spi_slave.v.tmpl'
        elif config.spi_role.lower() == "dual":
            template_name = 'spi_dual.v.tmpl'
        else:  # master or default
            template_name = 'spi_core.v.tmpl'

        template_path = os.path.join(self.template_dir, template_name)
        with open(template_path, 'r') as f:
            template_content = f.read()

        template = Template(template_content)

        # Generate code with all parameters
        verilog_code = template.render(
            # Basic SPI parameters
            MODE=config.mode,
            DATA_WIDTH=config.data_width,
            NUM_SLAVES=config.num_slaves,
            SLAVE_ACTIVE_LOW=config.slave_active_low,
            MSB_FIRST=config.msb_first,

            # Feature flags
            INTERRUPTS=config.interrupts,
            FIFO_BUFFERS=config.fifo_buffers,
            DMA_SUPPORT=config.dma_support,
            MULTI_MASTER=config.multi_master,

            # Enhanced features
            SPI_ROLE=config.spi_role,
            DEFAULT_DATA_ENABLED=config.default_data_enabled,
            DEFAULT_DATA_PATTERN=config.default_data_pattern,
            DEFAULT_DATA_VALUE=config.default_data_value,
            CLOCK_DIVIDER=config.clock_divider,
            FIFO_DEPTH=config.fifo_depth,
            MAX_SLAVES=config.max_slaves,
            CLOCK_FREQUENCY=config.clock_frequency,

            # Test configuration
            TEST_DURATION=config.test_duration,
            CLOCK_JITTER_TEST=config.clock_jitter_test,
            WAVEFORM_CAPTURE=config.waveform_capture
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

        # Use template-based approach for different SPI roles
        if config.spi_role.lower() == "slave":
            template_name = 'spi_slave_tb.v.tmpl'
        elif config.spi_role.lower() == "dual":
            template_name = 'spi_dual_tb.v.tmpl'
        else:  # master or default
            template_name = 'spi_master_tb.v.tmpl'

        template_path = os.path.join(self.template_dir, template_name)
        with open(template_path, 'r') as f:
            template_content = f.read()

        template = Template(template_content)

        # Generate testbench code
        testbench_code = template.render(
            mode=config.mode,
            data_width=config.data_width,
            num_slaves=config.num_slaves,
            slave_active_low=config.slave_active_low,
            msb_first=config.msb_first,
            fifo_depth=config.fifo_depth,
            max_slaves=config.max_slaves,
            clock_divider=config.clock_divider,
            default_data_enabled=config.default_data_enabled,
            default_data_pattern=config.default_data_pattern,
            default_data_value=config.default_data_value,
            vcd_filename=vcd_filename
        )

        return testbench_code

    def save_testbench(self, config: SPIConfig, filename: str = None) -> str:
        """
        Generate and save testbench code to file

        Args:
            config: SPIConfig object
            filename: Output filename (optional)

        Returns:
            Path to generated file
        """

        if filename is None:
            # Use simple naming for string issue numbers (like example1, example2, etc.)
            if isinstance(config.issue_number, str):
                filename = f"{config.issue_number}_tb.v"
            else:
                # Use detailed naming for numeric issue numbers
                filename = f"spi_{config.spi_role.lower()}_tb.v"

        testbench_code = self.generate_testbench(config)

        # Ensure issue-specific results directory exists
        issue_dir = f'results/issue-{config.issue_number}'
        os.makedirs(issue_dir, exist_ok=True)

        filepath = os.path.join(issue_dir, filename)
        with open(filepath, 'w') as f:
            f.write(testbench_code)

        print(f"✅ Generated testbench: {filepath}")
        return filepath

