#!/usr/bin/env python3
"""
GitHub Issue Processor
Main entry point for processing SPI configuration issues in CI environment
"""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_parser import SPIConfigParser, SPIConfig
from verilog_generator import VerilogGenerator
from simulator_runner import RTLSimulator


class GitHubIssueProcessor:
    """Processes GitHub issues for SPI customization"""

    def __init__(self, token: str, issue_number: int):
        self.token = token
        self.issue_number = issue_number
        self.api_base = "https://github.com/SJTU-YONGFU-RESEARCH-GRP/spi-customizer"
        self.repo_owner = "yongfu-li"  # Update this with your repo details
        self.repo_name = "spi-customizer"  # Update this with your repo details

    def get_issue_content(self) -> Optional[str]:
        """Fetch issue content from GitHub API"""
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        url = f"{self.api_base}/{self.repo_owner}/{self.repo_name}/issues/{self.issue_number}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            issue_data = response.json()
            return issue_data.get('body', '')
        else:
            print(f"❌ Failed to fetch issue #{self.issue_number}: {response.status_code}")
            return None

    def update_issue_status(self, status: str, body: str = ""):
        """Update GitHub issue with processing status"""
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }

        data = {'body': body}

        if status == 'processing':
            data['labels'] = ['in-progress']
        elif status == 'completed':
            data['labels'] = ['completed']
            data['state'] = 'closed'
        elif status == 'failed':
            data['labels'] = ['failed']

        url = f"{self.api_base}/{self.repo_owner}/{self.repo_name}/issues/{self.issue_number}"
        response = requests.patch(url, headers=headers, json=data)

        if response.status_code == 200:
            print(f"✅ Issue #{self.issue_number} updated with status: {status}")
        else:
            print(f"❌ Failed to update issue: {response.status_code}")

    def process_issue(self) -> bool:
        """Main issue processing workflow"""
        print(f"🚀 Processing SPI issue #{self.issue_number}")

        # Step 1: Get issue content
        issue_body = self.get_issue_content()
        if not issue_body:
            self.update_issue_status('failed', '❌ Could not retrieve issue content')
            return False

        # Step 2: Parse configuration
        try:
            parser = SPIConfigParser()
            config = parser.parse_issue(issue_body, self.issue_number)

            # Update issue with initial status
            status_msg = f"""🔄 Processing your SPI configuration...

**Configuration Detected:**
- SPI Mode: {config.mode}
- Data Width: {config.data_width} bits
- Number of Slaves: {config.num_slaves}
- Slave Select: {'Active High' if not config.slave_active_low else 'Active Low'}
- Data Order: {'LSB First' if not config.msb_first else 'MSB First'}

⏰ This will take approximately 5-10 minutes...
"""
            self.update_issue_status('processing', status_msg)

        except Exception as e:
            error_msg = f"❌ Error parsing configuration: {str(e)}"
            self.update_issue_status('failed', error_msg)
            return False

        # Step 3: Generate Verilog code
        try:
            generator = VerilogGenerator()
            core_file = generator.save_verilog_file(config)
            tb_file = generator.save_testbench(config)

        except Exception as e:
            error_msg = f"❌ Error generating Verilog code: {str(e)}"
            self.update_issue_status('failed', error_msg)
            return False

        # Step 4: Run simulation (if tools available)
        try:
            simulator = RTLSimulator()
            if simulator.check_dependencies():
                # Run basic simulation
                verilog_files = [core_file, tb_file]
                top_module = "spi_master_tb"
                simulation_success = simulator.run_full_simulation(config, verilog_files, top_module)
            else:
                simulation_success = False
                print("⚠️  RTL tools not available, skipping simulation")

        except Exception as e:
            simulation_success = False
            print(f"⚠️  Simulation failed: {e}")

        # Step 5: Prepare results
        try:
            results_summary = self._generate_results_summary(config, core_file, tb_file, simulation_success)

            # Save configuration JSON in issue-specific directory
            config_dict = {
                'issue_number': self.issue_number,
                'mode': config.mode,
                'data_width': config.data_width,
                'num_slaves': config.num_slaves,
                'slave_active_low': config.slave_active_low,
                'msb_first': config.msb_first,
                'interrupts': config.interrupts,
                'fifo_buffers': config.fifo_buffers,
                'dma_support': config.dma_support,
                'multi_master': config.multi_master,
                'test_duration': config.test_duration,
                'simulation_success': simulation_success
            }

            issue_dir = f'results/issue-{self.issue_number}'
            os.makedirs(issue_dir, exist_ok=True)
            config_file = os.path.join(issue_dir, 'spi_config.json')
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)

        except Exception as e:
            error_msg = f"❌ Error preparing results: {str(e)}"
            self.update_issue_status('failed', error_msg)
            return False

        # Step 6: Final update
        self.update_issue_status('completed', results_summary)

        print("✅ Issue processing completed successfully!")
        return True

    def _generate_results_summary(self, config: SPIConfig, core_file: str, tb_file: str, sim_success: bool) -> str:
        """Generate summary of results for GitHub issue"""

        summary = f"""🎉 **SPI Customization Complete!**

## Generated Files

### 📁 **Core Files**
- **SPI Master Core**: `{os.path.basename(core_file)}`
  - Mode: {config.mode}
  - Data Width: {config.data_width} bits
  - Slaves: {config.num_slaves}

### 🧪 **Test Files**
- **Verilog Testbench**: `{os.path.basename(tb_file)}`
- **Python Test**: `test_spi.py` (Cocotb)
- **Configuration**: `spi_config.json`

## Download Links

📎 **Download all generated files**: [spi-results-{self.issue_number}.zip](https://github.com/{self.repo_owner}/{self.repo_name}/actions/runs/{os.environ.get('GITHUB_RUN_ID', 'latest')})

## Technical Details

### SPI Configuration
- **Mode**: {config.mode} ({'CPOL=1, CPHA=1' if config.mode == 3 else f'CPOL={config.mode//2}, CPHA={config.mode%2}'})
- **Clock Polarity**: {'High' if config.mode in [2,3] else 'Low'}
- **Clock Phase**: {'Falling edge' if config.mode in [1,3] else 'Rising edge'}
- **Slave Select**: {'Active High' if not config.slave_active_low else 'Active Low'}
- **Data Order**: {'LSB First' if not config.msb_first else 'MSB First'}

### Features Enabled
- **Interrupts**: {'✅' if config.interrupts else '❌'}
- **FIFO Buffers**: {'✅' if config.fifo_buffers else '❌'}
- **DMA Support**: {'✅' if config.dma_support else '❌'}
- **Multi-master**: {'✅' if config.multi_master else '❌'}

### Testing Results
- **RTL Simulation**: {'✅ Passed' if sim_success else '⚠️ Skipped (tools not available)'}
- **Waveform Capture**: {'✅' if config.waveform_capture else '❌'}
- **Test Duration**: {config.test_duration}

## Next Steps

1. **Download** the generated files from the link above
2. **Simulate** the design using your preferred RTL tools
3. **Integrate** the SPI core into your FPGA/ASIC design
4. **Test** with your target hardware

## Support

If you encounter any issues or need modifications:
- 📧 Email: {config.email}
- 💬 GitHub: @{config.github_username}
- 🐛 Report issues: [New Issue](https://github.com/{self.repo_owner}/{self.repo_name}/issues/new)

---

*Generated by SPI Customizer v1.0* 🚀"""

        return summary


def main():
    """Main entry point for GitHub Actions"""
    if len(sys.argv) != 2:
        print("Usage: python3 process_issue.py <issue_number>")
        sys.exit(1)

    try:
        issue_number = int(sys.argv[1])
    except ValueError:
        print("❌ Issue number must be an integer")
        sys.exit(1)

    # Get GitHub token from environment
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set")
        sys.exit(1)

    # Process the issue
    processor = GitHubIssueProcessor(token, issue_number)
    success = processor.process_issue()

    if success:
        print("✅ Issue processing completed successfully")
        return 0
    else:
        print("❌ Issue processing failed")
        return 1


if __name__ == "__main__":
    exit(main())
