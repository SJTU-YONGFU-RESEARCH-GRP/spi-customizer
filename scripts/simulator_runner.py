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

from scripts.config_parser import SPIConfig


class RTLSimulator:
    """Runs RTL simulation with Icarus Verilog and Cocotb"""

    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)

    def check_dependencies(self) -> bool:
        """Check if required tools are installed"""
        missing_tools = []
        if not shutil.which('iverilog'):
            missing_tools.append('iverilog')
        if not shutil.which('vvp'):
            missing_tools.append('vvp')

        if missing_tools:
            print(f"❌ Missing required tools: {', '.join(missing_tools)}")
            print("RTL simulation requires real Icarus Verilog (iverilog + vvp).")
            return False

        print("✅ All required tools found (iverilog, vvp)")
        return True

    def compile_design(self, verilog_files: list, top_module: str, config=None) -> bool:
        """
        Compile Verilog design with Icarus Verilog

        Args:
            verilog_files: List of Verilog file paths
            top_module: Name of the top-level module
            config: SPI configuration (optional)

        Returns:
            True if compilation successful
        """

        print(f"🔨 Compiling {len(verilog_files)} Verilog files...")

        iverilog_cmd = shutil.which('iverilog')
        if not iverilog_cmd:
            print("❌ iverilog not found - cannot compile")
            return False

        print(f"   Using Icarus Verilog compiler: {iverilog_cmd}")

        issue_dir = self.results_dir / f"issue-{config.issue_number}" if hasattr(config, 'issue_number') else self.results_dir
        issue_dir.mkdir(exist_ok=True)
        data_dir = issue_dir / 'data'
        logs_dir = issue_dir / 'logs'
        data_dir.mkdir(exist_ok=True)
        logs_dir.mkdir(exist_ok=True)

        simulation_file = str(data_dir / 'spi_simulation')
        cmd = [iverilog_cmd, '-o', simulation_file]
        cmd.extend(verilog_files)

        try:
            print(f"   Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )

            log_file = str(logs_dir / 'compilation.log')
            with open(log_file, 'w') as f:
                f.write("Icarus Verilog compilation log\n")
                f.write("=" * 50 + "\n")
                f.write(f"Command: {' '.join(cmd)}\n")
                f.write(f"Working directory: {os.getcwd()}\n")
                f.write(f"Return code: {result.returncode}\n")
                if result.stdout:
                    f.write(f"STDOUT:\n{result.stdout}\n")
                if result.stderr:
                    f.write(f"STDERR:\n{result.stderr}\n")
                f.write("Compilation: SUCCESS\n" if result.returncode == 0 else "Compilation: FAILED\n")

            if result.returncode == 0:
                print(f"✅ Compilation successful: {simulation_file}")
                print(f"✅ Compilation log: {log_file}")
                return True

            print(f"❌ Compilation failed with exit code {result.returncode}")
            print("STDERR:")
            print(result.stderr)
            print(f"📝 Compilation log: {log_file}")
            return False

        except Exception as e:
            print(f"❌ Compilation error: {e}")
            return False

    def run_simulation(self, test_duration: str = "standard", config=None) -> bool:
        """
        Run the compiled simulation with VCD dump

        Args:
            test_duration: Test duration level (brief, standard, comprehensive)
            config: SPI configuration (optional)

        Returns:
            True if simulation completed successfully
        """

        print("🎯 Running simulation with VCD dump...")

        # Determine simulation time based on test duration
        sim_times = {
            'brief': '10us',
            'standard': '100us',
            'comprehensive': '1ms'
        }
        sim_time = sim_times.get(test_duration, '100us')

        # Check if we have compiled simulation (from real iverilog)
        # Try issue-specific directory first, then root directory
        issue_dir = None
        if hasattr(config, 'issue_number'):
            issue_dir = self.results_dir / f"issue-{config.issue_number}"
            data_dir = issue_dir / 'data'
            logs_dir = issue_dir / 'logs'
            data_dir.mkdir(exist_ok=True)
            logs_dir.mkdir(exist_ok=True)
            simulation_file = str(data_dir / 'spi_simulation')
            if not os.path.exists(simulation_file):
                simulation_file = str(self.results_dir / 'spi_simulation')
        else:
            simulation_file = str(self.results_dir / 'spi_simulation')
            issue_dir = self.results_dir

        if not os.path.exists(simulation_file):
            print("❌ No compiled simulation found - cannot run vvp")
            return False

        vvp_exec = shutil.which('vvp')
        if not vvp_exec:
            print("❌ vvp not found - cannot run simulation")
            return False

        if issue_dir:
            data_dir = issue_dir / 'data'
            logs_dir = issue_dir / 'logs'
            data_dir.mkdir(exist_ok=True)
            logs_dir.mkdir(exist_ok=True)

        vcd_file = str(data_dir / 'spi_waveform.vcd')
        simulation_file = str(data_dir / 'spi_simulation')
        cmd = [vvp_exec, '-n', simulation_file]

        log_file = str(logs_dir / 'simulation.log')
        try:
            print(f"🔧 Running RTL simulation: {' '.join(cmd)}")
            print(f"   Simulation time: {sim_time}")
            print(f"   VCD output: {vcd_file}")

            with open(log_file, 'w') as f:
                f.write("Icarus Verilog simulation log\n")
                f.write("=" * 50 + "\n")
                f.write(f"Command: {' '.join(cmd)}\n")
                f.write(f"Simulation time: {sim_time}\n")
                f.write(f"VCD file: {vcd_file}\n")
                f.write(f"Working directory: {os.getcwd()}\n\n")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=900,
                env={**os.environ, 'VCD_FILE': vcd_file}
            )

            with open(log_file, 'a') as f:
                f.write(f"Return code: {result.returncode}\n")
                if result.stdout:
                    f.write(f"STDOUT:\n{result.stdout}\n")
                if result.stderr:
                    f.write(f"STDERR:\n{result.stderr}\n")

            if result.returncode != 0:
                print(f"❌ Simulation failed with exit code {result.returncode}")
                print(f"📝 Simulation log: {log_file}")
                return False

            if not os.path.exists(vcd_file):
                print("❌ Simulation completed but VCD file was not generated")
                print(f"📝 Simulation log: {log_file}")
                return False

            gtkw_file = str(data_dir / 'spi_waveform.gtkw')
            with open(gtkw_file, 'w') as f:
                f.write("[*\n")
                f.write("[*]\n")
                f.write("[sst]\n")
                f.write(f"{data_dir / 'spi_waveform.vcd'}\n")
                f.write("[timeline] 1\n")
                f.write("[analog] 0\n")
                f.write("[waves] 0\n")

            print(f"✅ VCD generated: {vcd_file} ({os.path.getsize(vcd_file)} bytes)")
            print(f"✅ Simulation log: {log_file}")
            return True

        except subprocess.TimeoutExpired:
            with open(log_file, 'a') as f:
                f.write("TIMEOUT: Simulation exceeded 900 seconds\n")
            print("⏰ RTL Simulation timed out (900 seconds)")
            print(f"📝 Simulation log: {log_file}")
            return False
        except Exception as e:
            print(f"❌ Simulation error: {e}")
            print(f"📝 Simulation log: {log_file}")
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

        # Generate GTKWave save file in the same directory as the VCD file
        vcd_path = Path(vcd_file)
        data_dir = vcd_path.parent
        save_file = str(data_dir / 'spi_waveform.gtkw')

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

        # Step 1: Compile design
        if not self.compile_design(verilog_files, top_module, config):
            print("❌ Compilation failed - cannot proceed with simulation")
            return False

        # Step 2: Run simulation with VCD generation
        if not self.run_simulation("standard", config):
            print("❌ Simulation failed")
            return False

        # Step 3: Check for generated files in issue directory
        if hasattr(config, 'issue_number'):
            issue_dir = self.results_dir / f"issue-{config.issue_number}"
            data_dir = issue_dir / 'data'
            vcd_file = str(data_dir / 'spi_waveform.vcd')
            if not os.path.exists(vcd_file):
                print("❌ No VCD file generated - cannot proceed with evidence-based analysis")
                return False

            self.generate_waveform(vcd_file)
            print("🎉 RTL simulation completed successfully!")
            return True
        else:
            print("⚠️  No issue number available, simulation completed")
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
        code_dir = issue_dir / 'code'
        code_dir.mkdir(exist_ok=True)

        test_file = code_dir / 'test_spi.py'
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
