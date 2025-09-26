#!/usr/bin/env python3
"""
RTL Simulator Runner
Compiles and runs Verilog simulation using Icarus Verilog and Cocotb
"""

import os
import subprocess
import shutil
import sys
from pathlib import Path

# Add current directory to path for imports (must be before any relative imports)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config_parser import SPIConfig


class RTLSimulator:
    """Runs RTL simulation with Icarus Verilog and Cocotb"""

    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)

    def check_dependencies(self) -> bool:
        """Check if required tools are installed"""
        required_tools = ['iverilog', 'vvp', 'gtkwave']

        missing_tools = []
        for tool in required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)

        if missing_tools:
            print(f"❌ Missing required tools: {', '.join(missing_tools)}")
            print("Please install them using:")
            print("  Ubuntu/Debian: sudo apt-get install iverilog gtkwave")
            print("  Fedora/CentOS: sudo dnf install iverilog gtkwave")
            print("  macOS: brew install icarus-verilog gtkwave")
            return False

        print("✅ All required tools found")
        return True

    def compile_design(self, verilog_files: list, top_module: str) -> bool:
        """
        Compile Verilog design with Icarus Verilog

        Args:
            verilog_files: List of Verilog file paths
            top_module: Name of the top-level module

        Returns:
            True if compilation successful
        """

        print(f"🔨 Compiling {len(verilog_files)} Verilog files...")

        cmd = ['iverilog', '-o', str(self.results_dir / 'spi_simulation')]
        cmd.extend(verilog_files)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.results_dir
            )

            if result.returncode == 0:
                print("✅ Compilation successful")
                return True
            else:
                print(f"❌ Compilation failed: {result.stderr}")
                return False

        except FileNotFoundError:
            print("❌ iverilog not found. Please install Icarus Verilog.")
            return False

    def run_simulation(self, test_duration: str = "standard") -> bool:
        """
        Run the compiled simulation

        Args:
            test_duration: Test duration level (brief, standard, comprehensive)

        Returns:
            True if simulation completed successfully
        """

        print("🎯 Running simulation...")

        # Determine simulation time based on test duration
        sim_times = {
            'brief': '10us',
            'standard': '100us',
            'comprehensive': '1ms'
        }
        sim_time = sim_times.get(test_duration, '100us')

        cmd = ['vvp', '-n', str(self.results_dir / 'spi_simulation')]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )

            if result.returncode == 0:
                print("✅ Simulation completed successfully")
                print("📊 Simulation output:")
                print(result.stdout)
                return True
            else:
                print(f"❌ Simulation failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("⏰ Simulation timed out (60 seconds)")
            return False
        except FileNotFoundError:
            print("❌ vvp (iverilog runtime) not found")
            return False

    def generate_waveform(self, vcd_file: str = None) -> bool:
        """
        Generate waveform viewer file

        Args:
            vcd_file: Path to VCD file (optional)

        Returns:
            True if waveform generation successful
        """

        if vcd_file is None:
            vcd_file = str(self.results_dir / 'spi_waveform.vcd')

        if not os.path.exists(vcd_file):
            print(f"⚠️  VCD file not found: {vcd_file}")
            return False

        # Generate GTKWave save file
        save_file = str(self.results_dir / 'spi_waveform.gtkw')

        # Create basic GTKWave save file
        gtkw_content = f"""[*
[*]
[sst]
{os.path.basename(vcd_file)}
[timeline] 1
[analog] 0
[waves] 0
"""

        with open(save_file, 'w') as f:
            f.write(gtkw_content)

        print(f"✅ Generated GTKWave save file: {save_file}")
        return True

    def run_full_simulation(self, config: SPIConfig, verilog_files: list, top_module: str) -> bool:
        """
        Run complete simulation flow

        Args:
            config: SPI configuration
            verilog_files: List of Verilog files to simulate
            top_module: Top-level module name

        Returns:
            True if all steps successful
        """

        print("🚀 Starting complete RTL simulation flow...")

        # Step 1: Check dependencies
        if not self.check_dependencies():
            return False

        # Step 2: Compile design
        if not self.compile_design(verilog_files, top_module):
            return False

        # Step 3: Run simulation
        if not self.run_simulation(config.test_duration):
            return False

        # Step 4: Generate waveform
        self.generate_waveform()

        print("🎉 RTL simulation completed successfully!")
        return True

    def create_cocotb_test(self, config: SPIConfig) -> str:
        """
        Create a simple Cocotb test for verification

        Args:
            config: SPI configuration

        Returns:
            Path to created test file
        """

        # Select appropriate test data based on data width
        if config.data_width == 8:
            test_data = "0xA5"
            data_str = "A5"
        elif config.data_width == 16:
            test_data = "0xA5A5"
            data_str = "A5A5"
        else:
            test_data = "0xA5A5A5A5"
            data_str = "A5A5A5A5"

        test_content = f'''import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, FallingEdge
import random

@cocotb.test()
async def test_spi_transmission(dut):
    """Test SPI master transmission"""

    # Create clock
    clock = Clock(dut.clk, 20, units="ns")  # 50MHz clock
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await Timer(100, units="ns")
    dut.rst_n.value = 1
    await Timer(100, units="ns")

    # Test data
    test_data = {test_data}  # Pattern based on data width
    dut.tx_data.value = test_data
    dut.miso.value = 0x5A5A5A5A  # Response pattern

    # Start transmission
    dut.start_tx.value = 1
    await Timer(20, units="ns")
    dut.start_tx.value = 0

    # Wait for completion
    while dut.busy.value == 1:
        await Timer(100, units="ns")

    # Check results
    await Timer(100, units="ns")

    # Verify slave select was activated
    assert dut.ss_n.value == 0, "Slave select should be active"

    # Verify interrupt was generated
    assert dut.irq.value == 1, "Interrupt should be generated"

    print(f"✅ SPI transmission test passed for {config.data_width}-bit data: 0x{data_str}")
'''

        # Ensure issue-specific results directory exists
        issue_dir = self.results_dir / f'issue-{config.issue_number}'
        issue_dir.mkdir(exist_ok=True)

        test_file = issue_dir / 'test_spi.py'
        with open(test_file, 'w') as f:
            f.write(test_content)

        print(f"✅ Created Cocotb test: {test_file}")
        return str(test_file)


def main():
    """Test the RTL simulator with sample files"""

    # Create sample configuration
    config = SPIConfig(
        issue_number=456,
        mode=0,
        clock_frequency=25.0,
        data_width=16,
        num_slaves=1,
        test_duration="brief"
    )

    simulator = RTLSimulator()

    # Generate sample Verilog files
    from verilog_generator import VerilogGenerator
    generator = VerilogGenerator()

    core_file = generator.save_verilog_file(config, "test_spi_core.v")
    tb_file = generator.save_testbench(config, "test_spi_tb.v")

    verilog_files = [core_file, tb_file]
    top_module = "spi_master_tb"

    # Run simulation
    success = simulator.run_full_simulation(config, verilog_files, top_module)

    if success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
