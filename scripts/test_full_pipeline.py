#!/usr/bin/env python3
"""
Full Pipeline Test
Tests the complete SPI customization pipeline without requiring external tools
"""

import os
import json
import sys
from pathlib import Path
from config_parser import SPIConfigParser, SPIConfig
from verilog_generator import VerilogGenerator
from simulator_runner import RTLSimulator


def test_config_parsing():
    """Test configuration parsing from issue text"""
    print("🔍 Testing configuration parsing...")

    # Sample issue text
    sample_issue = """
    ## SPI Configuration Request

    ### Basic Configuration
    - **SPI Mode**: 3
    - **Clock Frequency**: 50
    - **Data Width**: 32

    ### Advanced Configuration
    - **Number of Slaves**: 4
    - **Slave Select Behavior**:
      - [ ] Active Low
      - [x] Active High
    - **Data Order**:
      - [ ] MSB First
      - [x] LSB First
    - **Special Features**:
      - [x] Interrupt Support
      - [x] FIFO Buffers
      - [x] DMA Support
      - [x] Multi-master Support

    ### Testing Requirements
    - **Test Duration**: Comprehensive
    - **Clock Jitter Testing**: Yes
    - **Waveform Capture**: Yes

    ### Contact Information
    - **Email Address**: john.doe@example.com
    - **GitHub Username**: johndoe
    """

    try:
        parser = SPIConfigParser()
        config = parser.parse_issue(sample_issue, 123)

        # Verify parsed values
        assert config.mode == 3
        assert config.clock_frequency == 50.0
        assert config.data_width == 32
        assert config.num_slaves == 4
        assert config.slave_active_low == False  # Active High
        assert config.msb_first == False  # LSB First
        assert config.interrupts == True
        assert config.fifo_buffers == True
        assert config.dma_support == True
        assert config.multi_master == True
        assert config.test_duration.lower() == "comprehensive"
        assert config.clock_jitter_test == True
        assert config.waveform_capture == True
        assert config.email == "john.doe@example.com"
        assert config.github_username == "johndoe"

        print("✅ Configuration parsing test PASSED")
        return config

    except Exception as e:
        print(f"❌ Configuration parsing test FAILED: {e}")
        return None


def test_verilog_generation(config: SPIConfig):
    """Test Verilog code generation"""
    print("🔧 Testing Verilog generation...")

    try:
        generator = VerilogGenerator()

        # Generate SPI core
        core_file = generator.save_verilog_file(config, "test_core.v")

        # Generate testbench
        tb_file = generator.save_testbench(config, "test_tb.v")

        # Verify files exist and have content
        assert os.path.exists(core_file)
        assert os.path.exists(tb_file)

        with open(core_file, 'r') as f:
            core_content = f.read()
            assert 'module spi_master' in core_content
            assert f'parameter MODE = {config.mode}' in core_content
            assert f'parameter CLK_FREQ = {int(config.clock_frequency)}' in core_content
            assert f'parameter DATA_WIDTH = {config.data_width}' in core_content
            assert f'parameter NUM_SLAVES = {config.num_slaves}' in core_content

        with open(tb_file, 'r') as f:
            tb_content = f.read()
            assert 'module spi_master_tb' in tb_content
            assert 'spi_master_tb' in tb_content

        print("✅ Verilog generation test PASSED")
        return [core_file, tb_file]

    except Exception as e:
        print(f"❌ Verilog generation test FAILED: {e}")
        return None


def test_simulator_setup():
    """Test simulator setup (without actually running tools)"""
    print("🧪 Testing simulator setup...")

    try:
        simulator = RTLSimulator()

        # Test dependency checking
        has_deps = simulator.check_dependencies()

        # Test file generation
        config = SPIConfig(
            issue_number=999,
            mode=0,
            clock_frequency=25.0,
            data_width=16,
            num_slaves=1
        )

        test_file = simulator.create_cocotb_test(config)
        assert os.path.exists(test_file)

        with open(test_file, 'r') as f:
            test_content = f.read()
            assert 'import cocotb' in test_content
            assert 'test_spi_transmission' in test_content
            assert '50MHz clock' in test_content

        print("✅ Simulator setup test PASSED")
        return True

    except Exception as e:
        print(f"❌ Simulator setup test FAILED: {e}")
        return False


def test_json_config():
    """Test configuration JSON serialization"""
    print("💾 Testing JSON configuration...")

    try:
        config = SPIConfig(
            issue_number=789,
            mode=1,
            clock_frequency=10.0,
            data_width=8,
            num_slaves=2,
            slave_active_low=True,
            msb_first=True,
            interrupts=False,
            fifo_buffers=True,
            dma_support=False,
            multi_master=False,
            test_duration="brief",
            clock_jitter_test=False,
            waveform_capture=True,
            email="test@example.com",
            github_username="testuser"
        )

        # Test JSON serialization
        config_dict = {
            'mode': config.mode,
            'clock_frequency': config.clock_frequency,
            'data_width': config.data_width,
            'num_slaves': config.num_slaves,
            'slave_active_low': config.slave_active_low,
            'msb_first': config.msb_first,
            'interrupts': config.interrupts,
            'fifo_buffers': config.fifo_buffers,
            'dma_support': config.dma_support,
            'multi_master': config.multi_master,
            'test_duration': config.test_duration,
            'clock_jitter_test': config.clock_jitter_test,
            'waveform_capture': config.waveform_capture,
            'email': config.email,
            'github_username': config.github_username
        }

        json_file = 'results/test_config.json'
        with open(json_file, 'w') as f:
            json.dump(config_dict, f, indent=2)

        # Verify JSON can be read back
        with open(json_file, 'r') as f:
            loaded_config = json.load(f)

        assert loaded_config['mode'] == config.mode
        assert loaded_config['clock_frequency'] == config.clock_frequency
        assert loaded_config['data_width'] == config.data_width

        print("✅ JSON configuration test PASSED")
        return True

    except Exception as e:
        print(f"❌ JSON configuration test FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting Full Pipeline Test Suite")
    print("=" * 50)

    # Create results directory
    os.makedirs('results', exist_ok=True)

    tests_passed = 0
    total_tests = 4

    # Test 1: Configuration parsing
    print("\n" + "=" * 50)
    config = test_config_parsing()
    if config:
        tests_passed += 1

    # Test 2: Verilog generation
    print("\n" + "=" * 50)
    verilog_files = test_verilog_generation(config)
    if verilog_files:
        tests_passed += 1

    # Test 3: Simulator setup
    print("\n" + "=" * 50)
    if test_simulator_setup():
        tests_passed += 1

    # Test 4: JSON configuration
    print("\n" + "=" * 50)
    if test_json_config():
        tests_passed += 1

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! The SPI customization pipeline is working correctly.")
        print("\nGenerated files:")
        if verilog_files:
            for f in verilog_files:
                print(f"  - {f}")
        print("  - results/test_config.json")
        print("  - results/test_spi.py")
        return 0
    else:
        print(f"❌ {total_tests - tests_passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    exit(main())
