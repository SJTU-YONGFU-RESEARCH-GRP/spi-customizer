# SPI Customizer

A GitHub-based system for automatic generation of custom SPI (Serial Peripheral Interface) cores with RTL simulation and testing.

## Features

- 🚀 **GitHub Issue Integration**: Request custom SPI configurations through GitHub issues
- 🔧 **Automatic Code Generation**: Generates Verilog code based on your specifications
- 🧪 **RTL Simulation**: Tests generated designs with comprehensive testbenches
- 📊 **Waveform Generation**: Creates timing diagrams and performance plots
- 📧 **Email Results**: Delivers results directly to your inbox
- ⚡ **CI/CD Ready**: Fully automated pipeline using GitHub Actions

## How It Works

1. **File an Issue**: Use the GitHub issue template to specify your SPI configuration
2. **Automatic Processing**: The system parses your requirements and generates custom code
3. **RTL Testing**: Generated Verilog is compiled and simulated with testbenches
4. **Results Delivery**: Results are emailed to you with downloadable files
5. **Issue Updates**: The GitHub issue is updated with progress and final results

## Quick Start

### For Users: Requesting a Custom SPI Core

1. Go to the **Issues** tab and click **New Issue**
2. Select **SPI Configuration Request** template
3. Fill in your SPI configuration:
   - **SPI Mode** (0-3)
   - **Clock Frequency** (MHz)
   - **Data Width** (bits)
   - **Number of Slaves**
   - **Advanced options** (interrupts, DMA, etc.)
   - **Contact information**

4. Submit the issue and wait for results!

### Example Configuration

```markdown
## SPI Configuration Request

### Basic Configuration
- **SPI Mode**: 3
- **Clock Frequency**: 25
- **Data Width**: 16

### Advanced Configuration
- **Number of Slaves**: 2
- **Slave Select Behavior**:
  - [ ] Active Low
  - [x] Active High
- **Data Order**:
  - [x] MSB First
  - [ ] LSB First
- **Special Features**:
  - [x] Interrupt Support
  - [x] FIFO Buffers
  - [x] DMA Support
  - [ ] Multi-master Support

### Testing Requirements
- **Test Duration**: Standard
- **Clock Jitter Testing**: Yes
- **Waveform Capture**: Yes

### Contact Information
- **Email Address**: your-email@example.com
- **GitHub Username**: your-username
```

## Architecture

### Core Components

- **Issue Parser** (`scripts/config_parser.py`): Extracts SPI parameters from GitHub issues
- **Verilog Generator** (`scripts/verilog_generator.py`): Creates custom SPI cores
- **RTL Simulator** (`scripts/simulator_runner.py`): Runs simulations and generates waveforms
- **CI Pipeline** (`.github/workflows/`): Automates the entire process

### Generated Files

For each issue, the system creates an organized folder structure:

```
results/issue-<id>/
├── spi_master_modeX_freqY_widthZ.v    # Custom SPI core
├── spi_master_tb_modeX_freqY.v        # Verilog testbench
├── test_spi.py                        # Python/Cocotb test
└── spi_config.json                    # Configuration specification
```

### File Organization

- **Issue-specific folders**: `results/issue-<github_issue_number>/`
- **SPI Core**: `spi_master_mode{mode}_{frequency}MHz_{width}bit.v`
- **Testbench**: `spi_master_tb_mode{mode}_{frequency}MHz.v`
- **Configuration**: `spi_config.json` (includes issue metadata)
- **Waveforms**: Generated during simulation (if tools available)

## Installation

### Local Development

```bash
# Install dependencies
pip install -r tools/requirements.txt

# Install RTL tools
sudo apt-get install iverilog gtkwave  # Ubuntu/Debian
# OR
sudo dnf install iverilog gtkwave      # Fedora/CentOS
# OR
brew install icarus-verilog gtkwave    # macOS
```

### Docker (Alternative)

```bash
# Build and run with Docker
docker build -t spi-customizer .
docker run -it spi-customizer
```

### CI/CD (GitHub Actions)

The system includes pre-configured GitHub Actions workflows that automatically:

1. Parse new SPI configuration issues
2. Generate custom Verilog code
3. Run RTL simulations
4. Create waveforms and plots
5. Email results to users
6. Update and close issues

## Testing

Run the complete test suite:

```bash
python3 scripts/test_full_pipeline.py
```

Run individual tests:

```bash
# Test configuration parsing
python3 scripts/config_parser.py 1

# Test Verilog generation
python3 scripts/verilog_generator.py

# Test RTL simulation setup
python3 scripts/simulator_runner.py
```

## Configuration Parameters

### Basic Settings
- **SPI Mode**: 0, 1, 2, or 3 (CPOL/CPHA combinations)
- **Clock Frequency**: Target frequency in MHz (0.1-200)
- **Data Width**: 8, 16, 32, or custom bits (1-64)

### Advanced Options
- **Number of Slaves**: 1-32 slave devices
- **Slave Select**: Active low or high
- **Data Order**: MSB first or LSB first
- **Special Features**: Interrupts, FIFO buffers, DMA support, multi-master

### Testing Options
- **Test Duration**: Brief, Standard, or Comprehensive
- **Clock Jitter Testing**: Enable/disable timing margin testing
- **Waveform Capture**: Generate detailed timing diagrams

## Example Output

### Generated SPI Core
```verilog
module spi_master #(
    parameter MODE = 3,
    parameter CLK_FREQ = 25,
    parameter DATA_WIDTH = 16,
    parameter NUM_SLAVES = 2
)(
    input  wire clk, rst_n,
    // Control and data interface
    input  wire start_tx, start_rx,
    input  wire [DATA_WIDTH-1:0] tx_data,
    output reg  [DATA_WIDTH-1:0] rx_data,
    output reg busy,
    // SPI interface
    output reg sclk, mosi,
    input  wire miso,
    output reg [NUM_SLAVES-1:0] ss_n
);
    // Implementation...
endmodule
```

### File Structure Example
```
results/issue-123/
├── spi_master_mode3_25MHz_16bit.v
├── spi_master_tb_mode3_25MHz.v
├── test_spi.py
└── spi_config.json
```

### Test Results
- ✅ SPI transmission test passed for 16-bit data
- ✅ Slave select correctly activated (Active High)
- ✅ Interrupt generated on completion
- ✅ Timing requirements met (25MHz clock)

## Requirements

### Software Dependencies
- **Python 3.8+** with pip
- **Icarus Verilog** (iverilog/vvp)
- **GTKWave** (waveform viewer)
- **Jinja2** (template engine)
- **Cocotb** (Python RTL testing)

### Hardware Support
- Supports standard SPI modes (0-3)
- Compatible with most FPGA families
- Configurable timing and protocol options

## License

This project is open source. See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

- 📧 **Email**: support@example.com
- 🐛 **Issues**: Use GitHub Issues for bug reports
- 📖 **Documentation**: Check the docs/ directory
- 💬 **Discussions**: Use GitHub Discussions for questions

---

**Ready to customize your SPI interface?** Just file an issue and let the automation do the rest! 🚀
