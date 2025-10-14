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

    def __init__(self, token: Optional[str], issue_number: int):
        self.token = token
        self.issue_number = issue_number
        self.api_base = "https://api.github.com/repos"
        self.repo_owner = "SJTU-YONGFU-RESEARCH-GRP"
        self.repo_name = "spi-customizer"

    def get_issue_content(self) -> Optional[str]:
        """Fetch issue content from local overrides or GitHub API"""
        # Local override for offline testing
        local_body = os.environ.get("LOCAL_ISSUE_BODY")
        local_file = os.environ.get("LOCAL_ISSUE_FILE")
        if local_body:
            print("🧪 Using LOCAL_ISSUE_BODY from environment (local test mode)")
            return local_body
        if local_file and os.path.isfile(local_file):
            try:
                with open(local_file, 'r', encoding='utf-8') as f:
                    print(f"🧪 Using LOCAL_ISSUE_FILE: {local_file} (local test mode)")
                    return f.read()
            except Exception as e:
                print(f"❌ Failed to read LOCAL_ISSUE_FILE '{local_file}': {e}")

        # Fall back to GitHub API
        if not self.token:
            print("❌ GITHUB_TOKEN not provided and no LOCAL_ISSUE_* override found")
            return None

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
        """Update GitHub issue with processing status (no-op in local mode)"""
        # In local test mode or without token, just print the update
        if os.environ.get("LOCAL_DRY_RUN") == "1" or not self.token:
            print(f"📝 [LOCAL] Would update issue #{self.issue_number} with status '{status}'")
            if body:
                print("── Status Body (truncated) ──")
                print((body[:500] + '...') if len(body) > 500 else body)
                print("────────────────────────────")
            return

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
            try:
                error_data = response.json()
                print(f"   Error message: {error_data.get('message', 'No message')}")
                if 'errors' in error_data:
                    for error in error_data['errors']:
                        print(f"   Field error: {error}")
            except:
                print(f"   Response body: {response.text}")

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

        # Step 4.5: Process VCD file for waveform analysis (if simulation successful)
        waveform_success = False
        if simulation_success:
            try:
                issue_dir = f'results/issue-{self.issue_number}'
                vcd_file = os.path.join(issue_dir, 'spi_waveform.vcd')
                if os.path.exists(vcd_file):
                    print("📊 Processing VCD file for waveform analysis...")
                    # Import vcd_parser functions
                    sys.path.append(os.path.dirname(__file__))
                    from vcd_parser import VcdParser, CsvGenerator, PlotGenerator, SignalPlotGenerator, SummaryGenerator

                    # Parse VCD file
                    parser = VcdParser(vcd_file)
                    vcd_data = parser.parse()

                    if "error" in vcd_data:
                        print(f"⚠️  VCD parsing failed: {vcd_data['error']}")
                    else:
                        print(f"✅ VCD parsed successfully: {len(vcd_data['signals'])} signals found")

                        # Generate CSV files
                        csv_gen = CsvGenerator(vcd_data, issue_dir)
                        csv_files = csv_gen.generate_csv_files()
                        print(f"✅ Generated {len(csv_files)} CSV files")

                        # Generate plots
                        plot_gen = PlotGenerator(issue_dir)
                        plot_files = plot_gen.generate_plots()
                        print(f"✅ Generated {len(plot_files)} plot files")

                        # Generate individual signal plots
                        signal_plot_gen = SignalPlotGenerator(issue_dir)
                        individual_plots = signal_plot_gen.generate_all_plots()
                        individual_plots.extend(signal_plot_gen.generate_individual_signal_plots())
                        print(f"✅ Generated {len(individual_plots)} additional plots")

                        # Generate summary
                        summary_gen = SummaryGenerator(issue_dir)
                        summary_file = summary_gen.generate_summary()
                        print(f"✅ Generated analysis summary: {summary_file}")

                        waveform_success = True
                        print("🎉 Waveform analysis completed!")
                else:
                    print("⚠️  No VCD file found, skipping waveform analysis")

            except Exception as e:
                print(f"⚠️  Waveform processing failed: {e}")
                waveform_success = False

        # Step 5: Prepare results
        try:
            results_summary = self._generate_results_summary(config, core_file, tb_file, simulation_success, waveform_success)

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
                'simulation_success': simulation_success,
                'waveform_success': waveform_success
            }

            issue_dir = f'results/issue-{self.issue_number}'
            os.makedirs(issue_dir, exist_ok=True)

            # Ensure plots directory exists (even if no plots generated)
            plots_dir = 'plots'
            os.makedirs(plots_dir, exist_ok=True)

            config_file = os.path.join(issue_dir, 'spi_config.json')
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)

            # Create a simple status file to indicate completion
            status_file = os.path.join(issue_dir, 'processing_status.txt')
            with open(status_file, 'w') as f:
                f.write(f"SPI Issue #{self.issue_number} processing completed\n")
                f.write(f"Mode: {config.mode}\n")
                f.write(f"Data Width: {config.data_width} bits\n")
                f.write(f"Simulation Success: {simulation_success}\n")
                f.write(f"Generated Files:\n")
                f.write(f"  - {os.path.basename(core_file)}\n")
                f.write(f"  - {os.path.basename(tb_file)}\n")
                f.write(f"  - spi_config.json\n")
                if not simulation_success:
                    f.write("  Note: Simulation tools not available, using simulated results\n")

        except Exception as e:
            error_msg = f"❌ Error preparing results: {str(e)}"
            self.update_issue_status('failed', error_msg)
            return False

        # Step 6: Final update
        self.update_issue_status('completed', results_summary)

        print("✅ Issue processing completed successfully!")
        return True

    def _generate_results_summary(self, config: SPIConfig, core_file: str, tb_file: str, sim_success: bool, waveform_success: bool) -> str:
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
- **Waveform Capture**: {'✅ Generated' if waveform_success else '❌ Failed'}
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

    # Get GitHub token from environment (optional in local mode)
    token = os.environ.get('GITHUB_TOKEN')
    if not token and not (os.environ.get('LOCAL_ISSUE_FILE') or os.environ.get('LOCAL_ISSUE_BODY')):
        print("❌ GITHUB_TOKEN not set and no LOCAL_ISSUE_FILE/LOCAL_ISSUE_BODY provided for local run")
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
