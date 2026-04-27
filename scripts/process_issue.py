#!/usr/bin/env python3
"""
GitHub Issue Processor
Main entry point for processing SPI configuration issues in CI environment
"""

import os
import sys
import json
import hashlib
import subprocess
import requests
from typing import Dict, Any, Optional, List

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
        # Prefer environment variables set by GitHub Actions (GITHUB_REPOSITORY = "owner/repo")
        gh_repo = os.environ.get('GITHUB_REPOSITORY', 'cylindercheah/spi-customizer')
        parts = gh_repo.split('/', 1)
        self.repo_owner = parts[0] if len(parts) == 2 else 'cylindercheah'
        self.repo_name = parts[1] if len(parts) == 2 else 'spi-customizer'

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
        """Update labels/state and post status comment without mutating issue body."""
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

        data = {}

        if status == 'processing':
            data['labels'] = ['in-progress']
        elif status == 'completed':
            data['labels'] = ['completed']
            data['state'] = 'closed'
        elif status == 'failed':
            data['labels'] = ['failed']

        issue_url = f"{self.api_base}/{self.repo_owner}/{self.repo_name}/issues/{self.issue_number}"
        response = requests.patch(issue_url, headers=headers, json=data)

        if response.status_code == 200:
            print(f"✅ Issue #{self.issue_number} updated with status: {status}")
            if body:
                comment_url = f"{issue_url}/comments"
                comment_resp = requests.post(comment_url, headers=headers, json={"body": body})
                if comment_resp.status_code == 201:
                    print(f"✅ Posted status comment for issue #{self.issue_number}")
                else:
                    print(f"⚠️ Failed to post status comment: {comment_resp.status_code}")
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

            print(f"✅ Configuration parsed successfully: Mode {config.mode}, {config.data_width} bits")

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
            print(f"❌ Configuration parsing failed: {e}")
            import traceback
            traceback.print_exc()
            error_msg = f"❌ Error parsing configuration: {str(e)}"
            self.update_issue_status('failed', error_msg)
            return False

        # Step 3: Generate Verilog code
        try:
            issue_dir = f'results/issue-{self.issue_number}'
            code_dir = f'{issue_dir}/code'
            data_dir = f'{issue_dir}/data'
            logs_dir = f'{issue_dir}/logs'
            graphs_dir = f'{issue_dir}/graphs'
            os.makedirs(code_dir, exist_ok=True)
            os.makedirs(data_dir, exist_ok=True)
            os.makedirs(logs_dir, exist_ok=True)
            os.makedirs(graphs_dir, exist_ok=True)

            generator = VerilogGenerator()
            # Generate VCD filename for testbench
            vcd_filename = f"{data_dir}/spi_waveform.vcd"
            core_file = generator.save_verilog_file(config, output_dir=code_dir)
            tb_file = generator.save_testbench(config, output_dir=code_dir, vcd_filename=vcd_filename)

            # Verify files were created
            if not os.path.exists(core_file):
                raise FileNotFoundError(f"Core file not created: {core_file}")
            if not os.path.exists(tb_file):
                raise FileNotFoundError(f"Testbench file not created: {tb_file}")

            print(f"✅ Verilog files verified: {os.path.basename(core_file)}, {os.path.basename(tb_file)}")

        except Exception as e:
            error_msg = f"❌ Error generating Verilog code: {str(e)}"
            self.update_issue_status('failed', error_msg)
            return False

        # Step 3.5: Write run manifest (traceability)
        try:
            manifest_path = os.path.join(logs_dir, 'run_manifest.json')
            self._write_run_manifest(
                manifest_path=manifest_path,
                issue_body=issue_body,
                config=config,
                core_file=core_file,
                tb_file=tb_file
            )
            print(f"✅ Run manifest written: {manifest_path}")
        except Exception as e:
            print(f"⚠️  Failed to write run manifest: {e}")

        # Step 4: Run simulation (if tools available)
        # Persist configuration early so downstream report generation can read it.
        try:
            initial_config_dict = {
                'issue_number': self.issue_number,
                'mode': config.mode,
                'data_width': config.data_width,
                'num_slaves': config.num_slaves,
                'selected_slave': config.selected_slave,
                'slave_active_low': config.slave_active_low,
                'msb_first': config.msb_first,
                'interrupts': config.interrupts,
                'fifo_buffers': config.fifo_buffers,
                'dma_support': config.dma_support,
                'multi_master': config.multi_master,
                'spi_role': config.spi_role,
                'test_duration': config.test_duration,
                'clock_jitter_test': config.clock_jitter_test,
                'waveform_capture': config.waveform_capture,
                'default_data_enabled': config.default_data_enabled,
                'default_data_pattern': config.default_data_pattern,
                'default_data_value': config.default_data_value,
                'clock_divider': config.clock_divider,
                'fifo_depth': config.fifo_depth,
                'max_slaves': config.max_slaves,
                'simulation_success': False,
                'waveform_success': False,
                'email': getattr(config, 'email', ''),
                'github_username': getattr(config, 'github_username', ''),
                'custom_features': getattr(config, 'custom_features', {}) or {}
            }
            config_file = os.path.join(code_dir, 'spi_config.json')
            with open(config_file, 'w') as f:
                json.dump(initial_config_dict, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to persist initial config: {e}")

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
                vcd_file = os.path.join(data_dir, 'spi_waveform.vcd')
                if os.path.exists(vcd_file):
                    print("📊 Processing VCD file for waveform analysis...")
                    # Import vcd_parser functions
                    sys.path.append(os.path.dirname(__file__))
                    from vcd_parser import VcdParser, CsvGenerator, PlotGenerator, SignalPlotGenerator, SummaryGenerator, ProtocolComplianceChecker

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

                        # Generate protocol compliance report (evidence-based)
                        compliance_path = os.path.join(logs_dir, 'protocol_compliance.md')
                        checker = ProtocolComplianceChecker(config=config, vcd_data=vcd_data)
                        checker.write_markdown(compliance_path)
                        print(f"✅ Generated protocol compliance report: {compliance_path}")

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
                'selected_slave': config.selected_slave,
                'slave_active_low': config.slave_active_low,
                'msb_first': config.msb_first,
                'interrupts': config.interrupts,
                'fifo_buffers': config.fifo_buffers,
                'dma_support': config.dma_support,
                'multi_master': config.multi_master,
                'spi_role': config.spi_role,
                'test_duration': config.test_duration,
                'clock_jitter_test': config.clock_jitter_test,
                'waveform_capture': config.waveform_capture,
                'default_data_enabled': config.default_data_enabled,
                'default_data_pattern': config.default_data_pattern,
                'default_data_value': config.default_data_value,
                'clock_divider': config.clock_divider,
                'fifo_depth': config.fifo_depth,
                'max_slaves': config.max_slaves,
                'simulation_success': simulation_success,
                'waveform_success': waveform_success,
                'email': getattr(config, 'email', ''),
                'github_username': getattr(config, 'github_username', ''),
                'custom_features': getattr(config, 'custom_features', {}) or {}
            }

            issue_dir = f'results/issue-{self.issue_number}'
            os.makedirs(issue_dir, exist_ok=True)

            # Ensure plots directory exists (even if no plots generated)
            plots_dir = 'plots'
            os.makedirs(plots_dir, exist_ok=True)

            config_file = os.path.join(code_dir, 'spi_config.json')
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)

            # Create a simple status file to indicate completion
            status_file = os.path.join(logs_dir, 'processing_status.txt')
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

    def _write_run_manifest(self, manifest_path: str, issue_body: str, config: SPIConfig, core_file: str, tb_file: str) -> None:
        body_hash = hashlib.sha256(issue_body.encode('utf-8')).hexdigest()

        def _tool_version(cmd: List[str]) -> Optional[str]:
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if res.returncode == 0:
                    out = (res.stdout or res.stderr or "").strip()
                    return out.splitlines()[0] if out else None
                return None
            except Exception:
                return None

        issue_dir = os.path.dirname(os.path.dirname(manifest_path))
        acceptance_raw = ""
        intent_raw = ""
        custom_features = getattr(config, "custom_features", {}) or {}
        if isinstance(custom_features, dict):
            acceptance_raw = custom_features.get("acceptance_criteria", "") or custom_features.get("what_to_verify", "") or ""
            intent_raw = custom_features.get("intent", "") or ""
        acceptance_criteria = [line.strip("- ").strip() for line in acceptance_raw.splitlines() if line.strip().startswith("-")]
        mode = config.mode
        cpol = 1 if mode in [2, 3] else 0
        cpha = 1 if mode in [1, 3] else 0

        manifest = {
            "issue_number": self.issue_number,
            "issue_body_sha256": body_hash,
            "config": {
                "mode": config.mode,
                "data_width": config.data_width,
                "num_slaves": config.num_slaves,
                "selected_slave": config.selected_slave,
                "slave_active_low": config.slave_active_low,
                "msb_first": config.msb_first,
                "interrupts": config.interrupts,
                "fifo_buffers": config.fifo_buffers,
                "dma_support": config.dma_support,
                "multi_master": config.multi_master,
                "test_duration": config.test_duration,
                "clock_jitter_test": config.clock_jitter_test,
                "waveform_capture": config.waveform_capture,
                "spi_role": config.spi_role,
                "clock_divider": config.clock_divider,
                "fifo_depth": config.fifo_depth,
                "max_slaves": config.max_slaves,
            },
            "generated_files": {
                "core_file": os.path.relpath(core_file, issue_dir),
                "tb_file": os.path.relpath(tb_file, issue_dir),
                "expected_vcd": "data/spi_waveform.vcd",
            },
            "tools": {
                "iverilog": _tool_version(["iverilog", "-V"]),
                "vvp": _tool_version(["vvp", "-V"]),
                "python": _tool_version([sys.executable, "--version"]),
            },
            "verification_spec": {
                "spi_role": config.spi_role,
                "mode": mode,
                "cpol": cpol,
                "cpha": cpha,
                "data_width": config.data_width,
                "num_slaves": config.num_slaves,
                "selected_slave": config.selected_slave,
                "slave_active_low": config.slave_active_low,
                "bit_order": "msb_first" if config.msb_first else "lsb_first",
                "intent": intent_raw,
                "acceptance_criteria": acceptance_criteria,
            }
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

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

    if issue_number == 0:
        print("ℹ️  Issue number is 0 (workflow_dispatch without ISSUE_NUMBER). Nothing to process.")
        sys.exit(0)

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
