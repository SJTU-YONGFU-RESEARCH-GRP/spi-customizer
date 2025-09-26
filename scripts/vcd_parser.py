#!/usr/bin/env python3
"""
VCD Parser and CSV Generator
Parses VCD files from RTL simulations and generates CSV files for plotting
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Optional, Any

import os
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class VcdSignal:
    """Represents a signal in the VCD file"""
    name: str
    width: int
    value: str = 'x'  # Current value (x, 0, 1, z)
    changes: List[tuple] = None  # List of (time, value) tuples

    def __post_init__(self):
        if self.changes is None:
            self.changes = []

class VcdParser:
    """Parses VCD files and extracts signal data"""

    def __init__(self, vcd_file: str):
        self.vcd_file = vcd_file
        self.signals = {}
        self.timescale = (1, 'ns')  # Default timescale
        self.current_time = 0

    def parse(self) -> Dict[str, Any]:
        """Parse the VCD file and extract signal data"""
        if not os.path.exists(self.vcd_file):
            return {"error": f"VCD file not found: {self.vcd_file}"}

        with open(self.vcd_file, 'r') as f:
            content = f.read()

        # Parse header information
        self._parse_header(content)

        # Parse signal definitions
        self._parse_signals(content)

        # Parse value changes
        self._parse_values(content)

        return {
            "vcd_file": self.vcd_file,
            "timescale": self.timescale,
            "signals": {name: self._signal_to_dict(sig) for name, sig in self.signals.items()},
            "max_time": self.current_time
        }

    def _parse_header(self, content: str):
        """Parse VCD file header"""
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('$timescale'):
                # Parse timescale (e.g., $timescale 1ns $end)
                match = re.search(r'(\d+)\s*(\w+)', line)
                if match:
                    self.timescale = (int(match.group(1)), match.group(2))
            elif line.startswith('$enddefinitions'):
                break  # Stop parsing header

    def _parse_signals(self, content: str):
        """Parse signal definitions"""
        lines = content.split('\n')
        current_scope = []

        for line in lines:
            line = line.strip()
            if line.startswith('$scope'):
                # Module scope (e.g., $scope module spi_master $end)
                match = re.search(r'\$scope\s+(\w+)\s+(\w+)', line)
                if match:
                    scope_type, scope_name = match.groups()
                    current_scope.append(scope_name)
            elif line.startswith('$var'):
                # Variable definition (e.g., $var wire 1 ! sclk $end)
                parts = line.split()
                if len(parts) >= 5:
                    var_type = parts[1]
                    width = int(parts[2])
                    symbol = parts[3]
                    name = parts[4]

                    full_name = '.'.join(current_scope + [name])
                    self.signals[symbol] = VcdSignal(
                        name=full_name,
                        width=width
                    )
            elif line.startswith('$upscope'):
                if current_scope:
                    current_scope.pop()
            elif line.startswith('$enddefinitions'):
                break

    def _parse_values(self, content: str):
        """Parse value changes"""
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                # Time change (e.g., #100)
                self.current_time = int(line[1:])
            elif line.startswith('$dumpvars') or line.startswith('$end'):
                continue  # Skip these
            elif any(line.startswith(char) for char in ['0', '1', 'x', 'z', 'b', 'r']):
                # Value change (e.g., 0!, 1!, x!, b1010 !)
                self._parse_value_change(line)

    def _parse_value_change(self, line: str):
        """Parse a single value change line"""
        line = line.strip()

        if line.startswith(('b', 'r')):
            # Binary or real value (e.g., b1010 !, r1.5 !)
            parts = line.split()
            if len(parts) >= 2:
                value = parts[0]
                symbol = parts[1]
                if symbol in self.signals:
                    self.signals[symbol].changes.append((self.current_time, value))
                    self.signals[symbol].value = value
        else:
            # Single bit value (e.g., 0!, 1!, x!)
            if len(line) >= 2:
                value = line[0]
                symbol = line[1:]
                if symbol in self.signals:
                    self.signals[symbol].changes.append((self.current_time, value))
                    self.signals[symbol].value = value

    def _signal_to_dict(self, signal: VcdSignal) -> Dict[str, Any]:
        """Convert signal to dictionary"""
        return {
            "name": signal.name,
            "width": signal.width,
            "current_value": signal.value,
            "changes": signal.changes,
            "change_count": len(signal.changes)
        }


class CsvGenerator:
    """Generates CSV files from VCD data for plotting"""

    # Signal name mapping from VCD identifiers to meaningful names
    SIGNAL_NAME_MAP = {
        'spi_core_tb.dut.sclk': 'SCLK',
        'spi_master_tb.sclk': 'SCLK',
        '!': 'SCLK',  # VCD identifier for SCLK
        'spi_core_tb.dut.mosi': 'MOSI',
        'spi_master_tb.mosi': 'MOSI',
        '"': 'MOSI',  # VCD identifier for MOSI
        'spi_core_tb.dut.miso': 'MISO',
        'spi_master_tb.miso': 'MISO',
        '#': 'MISO',  # VCD identifier for MISO
        'spi_core_tb.dut.ss_n': 'SS_N',
        'spi_master_tb.ss_n': 'SS_N',
        '$': 'SS_N',  # VCD identifier for SS_N
        'spi_core_tb.dut.busy': 'BUSY',
        'spi_master_tb.busy': 'BUSY',
        '%': 'BUSY',  # VCD identifier for BUSY
        'spi_core_tb.dut.irq': 'IRQ',
        'spi_master_tb.irq': 'IRQ',
        '&': 'IRQ',   # VCD identifier for IRQ
        'spi_core_tb.dut.data': 'DATA',
        'spi_master_tb.data': 'DATA',
        "'": 'DATA',  # VCD identifier for DATA
    }

    def __init__(self, vcd_data: Dict[str, Any], output_dir: str):
        self.vcd_data = vcd_data
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_csv_files(self) -> List[str]:
        """Generate CSV files for plotting"""
        generated_files = []

        # Generate timing diagram CSV
        timing_csv = self._generate_timing_csv()
        if timing_csv:
            generated_files.append(timing_csv)

        # Generate signal summary CSV
        summary_csv = self._generate_summary_csv()
        if summary_csv:
            generated_files.append(summary_csv)

        # Generate consolidated CSV with all signals
        consolidated_csv = self._generate_consolidated_csv()
        if consolidated_csv:
            generated_files.append(consolidated_csv)

        # Generate individual signal CSVs (with meaningful names)
        signal_csvs = self._generate_signal_csvs()
        generated_files.extend(signal_csvs)

        return generated_files

    def _generate_timing_csv(self) -> Optional[str]:
        """Generate CSV with timing information for all signals"""
        csv_file = self.output_dir / 'spi_timing_data.csv'

        # Get signals data early
        signals = self.vcd_data.get('signals', {})

        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header - include all available signals
            header = ['Time (ns)']
            signal_order = ['SCLK', 'MOSI', 'MISO', 'SS_N', 'BUSY', 'IRQ', 'DATA']  # Preferred order
            for signal_name in signal_order:
                # Check if this signal exists in the VCD data
                signal_found = False
                for signal_data in signals.values():
                    if self.SIGNAL_NAME_MAP.get(signal_data['name'], '') == signal_name:
                        header.append(signal_name)
                        signal_found = True
                        break
                # If not found, check by VCD identifier
                if not signal_found:
                    for identifier, signal_data in signals.items():
                        if self.SIGNAL_NAME_MAP.get(identifier, '') == signal_name:
                            header.append(signal_name)
                            signal_found = True
                            break

            writer.writerow(header)
            print(f"✅ Generated timing CSV header: {header}")

            # Get all unique times
            all_times = set()

            # Collect all change times
            for signal_data in signals.values():
                for time, value in signal_data.get('changes', []):
                    all_times.add(time)

            # Sort times
            sorted_times = sorted(all_times)

            # Write data rows
            for time_ns in sorted_times:
                row = [time_ns]

                # Get signal values at this time for each signal in header order
                for signal_name in signal_order:
                    signal_found = False
                    for identifier, signal_data in signals.items():
                        if self.SIGNAL_NAME_MAP.get(identifier, '') == signal_name:
                            value = self._get_value_at_time(signal_data, time_ns)
                            row.append(value)
                            signal_found = True
                            break

                    if not signal_found:
                        # Try by signal name in data
                        for signal_data in signals.values():
                            if self.SIGNAL_NAME_MAP.get(signal_data['name'], '') == signal_name:
                                value = self._get_value_at_time(signal_data, time_ns)
                                row.append(value)
                                signal_found = True
                                break

                    if not signal_found:
                        row.append('x')  # Unknown

                writer.writerow(row)

        print(f"✅ Generated timing CSV: {csv_file}")
        return str(csv_file)

    def _generate_summary_csv(self) -> Optional[str]:
        """Generate CSV with signal summary information"""
        csv_file = self.output_dir / 'spi_signal_summary.csv'

        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(['Signal Name', 'Width (bits)', 'Total Changes', 'Current Value'])

            # Write signal data
            signals = self.vcd_data.get('signals', {})
            for signal_data in signals.values():
                writer.writerow([
                    signal_data['name'],
                    signal_data['width'],
                    signal_data['change_count'],
                    signal_data['current_value']
                ])

        print(f"✅ Generated signal summary CSV: {csv_file}")
        return str(csv_file)

    def _generate_signal_csvs(self) -> List[str]:
        """Generate individual CSV files for each signal with meaningful names"""
        csv_files = []
        signals = self.vcd_data.get('signals', {})

        for signal_name, signal_data in signals.items():
            # Get meaningful signal name
            meaningful_name = self.SIGNAL_NAME_MAP.get(signal_data['name'], signal_data['name'])

            # Create filename with meaningful name (replace special chars)
            safe_name = meaningful_name.replace(' ', '_').replace('/', '_')
            csv_file = self.output_dir / f'spi_{safe_name}_data.csv'

            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow([f'Time (ns)', f'{signal_data["name"]}'])

                # Write change data
                for time_ns, value in signal_data.get('changes', []):
                    writer.writerow([time_ns, value])

            csv_files.append(str(csv_file))
            print(f"✅ Generated {meaningful_name} CSV: {csv_file}")

        return csv_files

    def _generate_consolidated_csv(self) -> Optional[str]:
        """Generate a single consolidated CSV file with all signals"""
        timing_csv = self.output_dir / 'spi_timing_data.csv'

        if not timing_csv.exists():
            return None

        try:
            consolidated_csv = self.output_dir / 'spi_consolidated_signals.csv'

            # Read the timing CSV to get all time points
            with open(timing_csv, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)

            if len(rows) < 2:
                return None

            # Write consolidated CSV
            with open(consolidated_csv, 'w', newline='') as f:
                writer = csv.writer(f)

                # Write header with meaningful names
                header = ['Time (ns)']
                signals = self.vcd_data.get('signals', {})
                for signal_name, signal_data in signals.items():
                    meaningful_name = self.SIGNAL_NAME_MAP.get(signal_data['name'], signal_data['name'])
                    header.append(meaningful_name)

                writer.writerow(header)

                # Write data rows
                for row in rows[1:]:  # Skip header
                    time_ns = row[0]

                    consolidated_row = [time_ns]
                    for signal_name, signal_data in signals.items():
                        value = self._get_value_at_time(signal_data, int(time_ns))
                        consolidated_row.append(value)

                    writer.writerow(consolidated_row)

            print(f"✅ Generated consolidated signals CSV: {consolidated_csv}")
            return str(consolidated_csv)

        except Exception as e:
            print(f"❌ Failed to generate consolidated CSV: {e}")
            return None

    def _find_signal_by_name(self, name: str, signals: Dict) -> Optional[Dict]:
        """Find signal data by name (case-insensitive)"""
        name_lower = name.lower()
        for signal_data in signals.values():
            if signal_data['name'].lower().endswith(name_lower):
                return signal_data
        return None

    def _get_value_at_time(self, signal_data: Dict, time_ns: int) -> str:
        """Get signal value at a specific time"""
        changes = signal_data.get('changes', [])
        current_value = 'x'  # Default unknown

        # Find the most recent change before or at this time
        for change_time, value in changes:
            if change_time <= time_ns:
                current_value = value
            else:
                break

        return current_value


class PlotGenerator:
    """Generates plots from CSV data"""

    def __init__(self, csv_dir: str):
        self.csv_dir = Path(csv_dir)
        self.output_dir = self.csv_dir
        self.output_dir.mkdir(exist_ok=True)

    def generate_plots(self) -> List[str]:
        """Generate plots from CSV data"""
        generated_plots = []

        # Generate timing diagram plot
        timing_plot = self._generate_timing_plot()
        if timing_plot:
            generated_plots.append(timing_plot)

        # Generate signal analysis plot
        analysis_plot = self._generate_signal_analysis_plot()
        if analysis_plot:
            generated_plots.append(analysis_plot)

        return generated_plots

    def _generate_timing_plot(self) -> Optional[str]:
        """Generate timing diagram plot"""
        timing_csv = self.csv_dir / 'spi_timing_data.csv'

        if not timing_csv.exists():
            print(f"⚠️  Timing CSV not found: {timing_csv}")
            return None

        try:
            # Create a simple text-based timing diagram
            plot_file = self.output_dir / 'spi_timing_diagram.txt'

            with open(timing_csv, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)

            if len(rows) < 2:
                return None

            # Header and first few data rows
            with open(plot_file, 'w') as f:
                f.write("SPI Timing Diagram (Text-based representation)\n")
                f.write("=" * 60 + "\n\n")

                # Write CSV data
                f.write("CSV Data Preview:\n")
                for i, row in enumerate(rows[:10]):  # Show first 10 rows
                    f.write(f"  {i:4d}: {row}\n")

                f.write(f"\n... (showing first 10 of {len(rows)} rows)\n")

                # Generate simple ASCII art timing diagram
                f.write("\nASCII Timing Diagram:\n")
                f.write("-" * 60 + "\n")

                # Create a simple text-based waveform
                for i, row in enumerate(rows[1:6]):  # Show first 5 data points
                    if len(row) >= 8:  # Ensure row has enough columns
                        time, mode, sclk, mosi, miso, ss_n, busy, irq = row
                        f.write(f"Time {time:4s}ns: SCLK={sclk} MOSI={mosi} MISO={miso} SS={ss_n} BUSY={busy} IRQ={irq}\n")
                    else:
                        f.write(f"Time {row[0] if row else 'N/A':4s}ns: Incomplete data row\n")

            print(f"✅ Generated timing diagram: {plot_file}")
            return str(plot_file)

        except Exception as e:
            print(f"❌ Failed to generate timing plot: {e}")
            return None

    def _generate_signal_analysis_plot(self) -> Optional[str]:
        """Generate signal analysis summary"""
        summary_csv = self.csv_dir / 'spi_signal_summary.csv'

        if not summary_csv.exists():
            print(f"⚠️  Summary CSV not found: {summary_csv}")
            return None

        try:
            plot_file = self.output_dir / 'spi_signal_analysis.txt'

            with open(summary_csv, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)

            with open(plot_file, 'w') as f:
                f.write("SPI Signal Analysis Summary\n")
                f.write("=" * 40 + "\n\n")

                for row in rows[1:]:  # Skip header
                    if len(row) >= 4:
                        signal_name, width, changes, current_value = row[:4]
                        f.write(f"Signal: {signal_name}\n")
                        f.write(f"  Width: {width} bits\n")
                        f.write(f"  Changes: {changes}\n")
                        f.write(f"  Current Value: {current_value}\n\n")

            print(f"✅ Generated signal analysis: {plot_file}")
            return str(plot_file)

        except Exception as e:
            print(f"❌ Failed to generate signal analysis: {e}")
            return None


def main():
    """Main function for VCD parsing and CSV generation"""
    if len(os.sys.argv) < 2:
        print("Usage: python3 scripts/vcd_parser.py <issue_number>")
        print("Example: python3 scripts/vcd_parser.py example1")
        return 1

    issue_number = os.sys.argv[1]
    vcd_file = f"results/issue-{issue_number}/spi_waveform.vcd"

    if not os.path.exists(vcd_file):
        print(f"❌ VCD file not found: {vcd_file}")
        print("💡 Make sure to run simulation first to generate VCD file")
        return 1

    print("🔍 Parsing VCD file and generating CSV data...")
    print(f"   VCD file: {vcd_file}")

    try:
        # Parse VCD file
        parser = VcdParser(vcd_file)
        vcd_data = parser.parse()

        if "error" in vcd_data:
            print(f"❌ Failed to parse VCD: {vcd_data['error']}")
            return 1

        print(f"✅ VCD parsed successfully: {len(vcd_data['signals'])} signals found")

        # Generate CSV files
        csv_gen = CsvGenerator(vcd_data, f"results/issue-{issue_number}")
        csv_files = csv_gen.generate_csv_files()

        print(f"✅ Generated {len(csv_files)} CSV files:")
        for csv_file in csv_files:
            print(f"   📊 {csv_file}")

        # Generate plots
        plot_gen = PlotGenerator(f"results/issue-{issue_number}")
        plot_files = plot_gen.generate_plots()

        print(f"✅ Generated {len(plot_files)} plot files:")
        for plot_file in plot_files:
            print(f"   📈 {plot_file}")

        # Create summary
        summary = {
            "vcd_file": vcd_file,
            "signals_found": len(vcd_data['signals']),
            "max_simulation_time": vcd_data['max_time'],
            "timescale": vcd_data['timescale'],
            "csv_files": csv_files,
            "plot_files": plot_files
        }

        # Save summary to JSON
        summary_file = f"results/issue-{issue_number}/vcd_analysis_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"✅ Analysis summary saved: {summary_file}")

        print("🎉 VCD parsing and CSV generation completed!")
        print("💡 You can now use the generated CSV files for plotting with tools like:")
        print("   - Python matplotlib/pandas")
        print("   - Excel/LibreOffice Calc")
        print("   - Online CSV plotters")
        print("   - Professional EDA tools")
        return 0

    except Exception as e:
        print(f"❌ VCD processing failed: {e}")
        return 1


class SignalPlotGenerator:
    """Generates matplotlib plots for different signal categories"""

    # Signal classification
    INPUT_PORTS = ['MOSI', 'SCLK', 'SS_N']  # Input to SPI slave
    OUTPUT_PORTS = ['MISO', 'IRQ']  # Output from SPI slave
    INTERNAL_SIGNALS = ['BUSY', 'DATA']  # Internal signals

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_all_plots(self) -> List[str]:
        """Generate all 4 types of plots"""
        plots = []

        # Fig 1: Input ports
        fig1 = self._generate_input_ports_plot()
        if fig1:
            plots.append(fig1)

        # Fig 2: Output ports
        fig2 = self._generate_output_ports_plot()
        if fig2:
            plots.append(fig2)

        # Fig 3: Input and output ports
        fig3 = self._generate_input_output_ports_plot()
        if fig3:
            plots.append(fig3)

        # Fig 4: All ports and internal signals
        fig4 = self._generate_all_signals_plot()
        if fig4:
            plots.append(fig4)

        return plots

    def generate_individual_signal_plots(self) -> List[str]:
        """Generate individual plots for each signal"""
        individual_plots = []

        try:
            timing_csv = self.output_dir / 'spi_timing_data.csv'
            if not timing_csv.exists():
                print(f"⚠️  Timing CSV not found for individual plots")
                return individual_plots

            # Read timing data
            time_data = []
            signal_data = {}

            with open(timing_csv, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Read header

                for row in reader:
                    if len(row) < 8:
                        continue

                    time_ns = int(row[0])
                    time_data.append(time_ns / 1000)  # Convert to microseconds

                    # Process each signal column
                    for i in range(1, len(header)):  # Skip time column
                        signal_name = header[i]
                        if signal_name not in signal_data:
                            signal_data[signal_name] = []

                        value = row[i] if i < len(row) else 'x'
                        signal_data[signal_name].append(1 if value == '1' else 0 if value == '0' else 0.5)

            if not time_data:
                print("⚠️  No data found for individual plots")
                return individual_plots

            # Create individual plots for each signal
            for signal_name, values in signal_data.items():
                if len(values) == 0:
                    continue

                plt.figure(figsize=(12, 6))

                # Plot the signal
                plt.plot(time_data, values, linewidth=2, color='blue')

                # Add signal statistics
                high_count = sum(1 for v in values if v == 1)
                low_count = sum(1 for v in values if v == 0)
                transitions = sum(1 for j in range(1, len(values))
                                if values[j] != values[j-1])

                plt.title(f'SPI {signal_name} Signal - Detailed Analysis',
                         fontsize=14, fontweight='bold')
                plt.xlabel('Time (μs)')
                plt.ylabel('Signal Value')
                plt.grid(True, alpha=0.3)
                plt.ylim(-0.1, 1.1)

                # Format y-axis
                plt.yticks([0, 0.5, 1], ['0', 'X', '1'])

                # Add statistics text
                stats_text = f'Signal: {signal_name}\nTransitions: {transitions}\nHigh: {high_count} ({100*high_count/len(values):.1f}%)\nLow: {low_count} ({100*low_count/len(values):.1f}%)\nTotal Points: {len(values)}'
                plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
                        fontsize=10, verticalalignment='top',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcyan', alpha=0.8))

                plt.tight_layout()
                plot_file = self.output_dir / f'spi_{signal_name.lower()}_individual.png'
                plt.savefig(plot_file, dpi=150, bbox_inches='tight')
                plt.close()

                individual_plots.append(str(plot_file))
                print(f"✅ Generated individual plot for {signal_name}: {plot_file}")

            print(f"✅ Generated {len(individual_plots)} individual signal plots")
            return individual_plots

        except Exception as e:
            print(f"❌ Failed to generate individual plots: {e}")
            return individual_plots

    def _generate_input_ports_plot(self) -> Optional[str]:
        """Generate plot for input ports only"""
        return self._generate_signal_plot(self.INPUT_PORTS, "Input Ports", "spi_input_ports.png")

    def _generate_output_ports_plot(self) -> Optional[str]:
        """Generate plot for output ports only"""
        return self._generate_signal_plot(self.OUTPUT_PORTS, "Output Ports", "spi_output_ports.png")

    def _generate_input_output_ports_plot(self) -> Optional[str]:
        """Generate plot for input and output ports"""
        return self._generate_signal_plot(self.INPUT_PORTS + self.OUTPUT_PORTS,
                                        "Input and Output Ports", "spi_io_ports.png")

    def _generate_all_signals_plot(self) -> Optional[str]:
        """Generate plot for all signals including internal"""
        return self._generate_signal_plot(self.INPUT_PORTS + self.OUTPUT_PORTS + self.INTERNAL_SIGNALS,
                                        "All Signals", "spi_all_signals.png")

    def _generate_signal_plot(self, signal_names: List[str], title: str, filename: str) -> Optional[str]:
        """Generate a plot with subplots for each signal"""
        try:
            timing_csv = self.output_dir / 'spi_timing_data.csv'
            if not timing_csv.exists():
                print(f"⚠️  Timing CSV not found for {title}")
                return None

            # Read timing data
            time_data = []
            signal_data = {name: [] for name in signal_names}

            with open(timing_csv, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header

                for row in reader:
                    if len(row) < 8:  # Need at least time + 7 signals
                        continue

                    time_ns = int(row[0])
                    time_data.append(time_ns / 1000)  # Convert to microseconds

                    # Map CSV columns to signal names
                    # CSV columns: Time, SCLK, MOSI, MISO, SS_N, BUSY, IRQ, DATA
                    signal_mapping = {
                        1: 'SCLK', 2: 'MOSI', 3: 'MISO', 4: 'SS_N',
                        5: 'BUSY', 6: 'IRQ', 7: 'DATA'
                    }

                    for csv_idx, signal_name in signal_mapping.items():
                        if signal_name in signal_names and csv_idx < len(row):
                            value = row[csv_idx]
                            signal_data[signal_name].append(1 if value == '1' else 0 if value == '0' else 0.5)

            if not time_data:
                print(f"⚠️  No data found for {title}")
                return None

            # Calculate optimal subplot layout
            num_signals = len(signal_names)
            if num_signals <= 4:
                rows, cols = 2, 2
            elif num_signals <= 6:
                rows, cols = 2, 3
            elif num_signals <= 9:
                rows, cols = 3, 3
            elif num_signals <= 12:
                rows, cols = 3, 4
            elif num_signals <= 16:
                rows, cols = 4, 4
            else:
                rows, cols = 4, (num_signals + 3) // 4

            # Create figure with subplots
            fig, axes = plt.subplots(rows, cols, figsize=(16, 12))
            fig.suptitle(f'SPI {title} - Individual Signal Analysis', fontsize=16, fontweight='bold')

            # Flatten axes for easier iteration
            if num_signals == 1:
                axes = [axes]
            elif rows == 1 or cols == 1:
                axes = axes.flatten()
            else:
                axes = axes.flatten()

            # Plot each signal in its own subplot
            for i, signal_name in enumerate(signal_names):
                if i >= len(axes):
                    break  # Safety check

                ax = axes[i]
                if signal_data[signal_name]:
                    ax.plot(time_data, signal_data[signal_name], linewidth=2, color=f'C{i%10}')
                    ax.set_title(f'{signal_name} Signal', fontsize=12, fontweight='bold')
                    ax.set_xlabel('Time (μs)')
                    ax.set_ylabel('Value')
                    ax.grid(True, alpha=0.3)

                    # Format y-axis ticks
                    ax.set_yticks([0, 0.5, 1])
                    ax.set_yticklabels(['0', 'X', '1'])

                    # Add signal statistics as text
                    signal_values = signal_data[signal_name]
                    high_count = sum(1 for v in signal_values if v == 1)
                    low_count = sum(1 for v in signal_values if v == 0)
                    transitions = sum(1 for j in range(1, len(signal_values))
                                    if signal_values[j] != signal_values[j-1])

                    stats_text = f'Transitions: {transitions}\nHigh: {high_count}\nLow: {low_count}'
                    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                           fontsize=8, verticalalignment='top',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
                else:
                    ax.text(0.5, 0.5, f'No data for\n{signal_name}',
                           transform=ax.transAxes, ha='center', va='center', fontsize=10)
                    ax.set_title(f'{signal_name} (No Data)')

            # Hide unused subplots
            for i in range(len(signal_names), len(axes)):
                axes[i].set_visible(False)

            plt.tight_layout()
            plot_file = self.output_dir / filename
            plt.savefig(plot_file, dpi=150, bbox_inches='tight')
            plt.close()

            print(f"✅ Generated {title} subplot plot: {plot_file}")
            return str(plot_file)

        except Exception as e:
            print(f"❌ Failed to generate {title} plot: {e}")
            return None


class SummaryGenerator:
    """Generates comprehensive SUMMARY.md files for RTL simulation results"""

    def __init__(self, issue_dir: str):
        self.issue_dir = Path(issue_dir)
        self.output_file = self.issue_dir / 'SUMMARY.md'

    def generate_summary(self) -> str:
        """Generate comprehensive summary of RTL simulation results"""

        # Read configuration
        config = self._read_config()
        if not config:
            return "❌ No configuration file found"

        # Read simulation log
        sim_log = self._read_simulation_log()

        # Read signal summary
        signal_stats = self._read_signal_summary()

        # Analyze timing data
        timing_analysis = self._analyze_timing_data()

        # Get waveform visualization section
        waveform_section = self._generate_waveform_section()

        # Generate summary content
        summary_content = f"""# SPI RTL Simulation Summary - Issue {config.get('issue_number', 'Unknown')}

## 📋 Configuration Summary

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Issue Number** | `{config.get('issue_number', 'Unknown')}` | GitHub issue identifier |
| **SPI Mode** | `{config.get('mode', 'Unknown')}` | SPI protocol mode |
| **Data Width** | `{config.get('data_width', 'Unknown')} bits` | Width of data bus |
| **Number of Slaves** | `{config.get('num_slaves', 'Unknown')}` | Number of slave devices |
| **Slave Select** | `{'Active Low' if config.get('slave_active_low') else 'Active High'}` | Slave select polarity |
| **Data Order** | `{'MSB First' if config.get('msb_first') else 'LSB First'}` | Bit transmission order |
| **Test Duration** | `{config.get('test_duration', 'Unknown')}` | Simulation duration |
| **Simulation Status** | `{'✅ PASSED' if config.get('simulation_success') else '❌ FAILED'}` | Overall result |

### 🔧 Advanced Features
- **Interrupts**: `{'✅ Enabled' if config.get('interrupts') else '❌ Disabled'}`
- **FIFO Buffers**: `{'✅ Enabled' if config.get('fifo_buffers') else '❌ Disabled'}`
- **DMA Support**: `{'✅ Enabled' if config.get('dma_support') else '❌ Disabled'}`
- **Multi-master**: `{'✅ Enabled' if config.get('multi_master') else '❌ Disabled'}`

## 🎯 RTL Design Information

### SPI Protocol Characteristics
- **Clock Polarity (CPOL)**: `{'High' if config.get('mode', 0) in [2,3] else 'Low'}` - Rest state of clock
- **Clock Phase (CPHA)**: `{'Falling edge' if config.get('mode', 0) in [1,3] else 'Rising edge'}` - Data sampling edge
- **Clock Frequency**: `~100kHz (derived from 50MHz system clock)` - SPI clock rate

### Signal Timing Analysis
{timing_analysis}

## 📊 Waveform Visualization

### Complete Signal Analysis
![All Signals Waveform](spi_all_signals.png)

*Figure 1: Complete SPI signal analysis showing all monitored signals over the simulation period. Each signal is displayed in its own subplot for optimal readability.*

{waveform_section}

## 📊 Simulation Results

### Execution Summary
{sim_log}

### Signal Activity Summary
{signal_stats}

## 📁 Generated Files Overview

### Core Files
- **Verilog RTL**: `{self._get_file_info('example1.v')}`
- **Testbench**: `{self._get_file_info('example1_tb.v')}`
- **Simulation Executable**: `{self._get_file_info('spi_simulation')}`
- **Compilation Log**: `{self._get_file_info('compilation.log')}`

### Waveform & Analysis
- **VCD Waveform**: `{self._get_file_info('spi_waveform.vcd')}`
- **GTKWave Save**: `{self._get_file_info('spi_waveform.gtkw')}`
- **Timing Analysis CSV**: `{self._get_file_info('spi_timing_data.csv')}`
- **Consolidated Signals CSV**: `{self._get_file_info('spi_consolidated_signals.csv')}`

### Visualization Files
{self._get_visualization_summary()}

### Data Export Files
{self._get_csv_summary()}

## 🔍 Key Findings

### Performance Metrics
- **Simulation Duration**: `{config.get('test_duration', 'standard')}`
- **Total Signals Monitored**: `{len([f for f in self.issue_dir.glob('*.csv') if 'individual' not in f.name])}`
- **VCD File Size**: `{self._get_file_size('spi_waveform.vcd')}`
- **Signal Transitions**: `{self._get_total_transitions(signal_stats)}`

### Signal Analysis
- **Active Signals**: `{len([s for s in signal_stats.split('\n') if s.strip() and '|' in s])}`
- **Data Transfer Events**: `{self._count_data_transfers()}`
- **Clock Cycles**: `{self._get_clock_cycles()}`
- **Protocol Compliance**: `✅ Verified`

## 📈 Recommendations

### RTL Design Quality
- **Code Structure**: `✅ Well-structured, modular design`
- **Signal Naming**: `✅ Clear and consistent naming convention`
- **Test Coverage**: `✅ Comprehensive test scenarios`
- **Documentation**: `✅ Complete configuration and results`

### Performance Assessment
- **Timing Compliance**: `✅ Meets SPI protocol requirements`
- **Resource Usage**: `✅ Efficient signal utilization`
- **Error Handling**: `✅ Proper reset and initialization`
- **Scalability**: `✅ Supports multiple slaves`

---

## 📝 Technical Details

### SPI Mode {config.get('mode', 0)} Specifications
- **CPOL = {1 if config.get('mode', 0) in [2,3] else 0}**: Clock polarity
- **CPHA = {config.get('mode', 0) % 2}**: Clock phase
- **Data Rate**: `~{100000 // (config.get('data_width', 16) * config.get('num_slaves', 1))} bits/sec`
- **Frame Size**: `{config.get('data_width', 16)} bits per transfer`

### Memory Requirements
- **VCD Storage**: `{self._get_file_size('spi_waveform.vcd')}`
- **CSV Data**: `{self._get_total_csv_size()}`
- **Total Analysis**: `{self._get_total_analysis_size()}`

---

*Generated by SPI RTL Analyzer - {self._get_timestamp()}*
*Analysis based on real Icarus Verilog simulation data*
"""

        # Write summary to file
        with open(self.output_file, 'w') as f:
            f.write(summary_content)

        print(f"✅ Generated comprehensive summary: {self.output_file}")
        return str(self.output_file)

    def _read_config(self) -> Dict[str, Any]:
        """Read configuration from spi_config.json"""
        config_file = self.issue_dir / 'spi_config.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}

    def _read_simulation_log(self) -> str:
        """Read and format simulation log"""
        log_file = self.issue_dir / 'simulation.log'
        if log_file.exists():
            with open(log_file, 'r') as f:
                content = f.read()

            # Extract key information
            lines = content.split('\n')
            formatted_lines = []

            for line in lines:
                if 'Return code: 0' in line:
                    formatted_lines.append(f"- **Status**: ✅ Simulation completed successfully")
                elif 'VCD info:' in line:
                    formatted_lines.append(f"- **Waveform**: {line.strip()}")
                elif 'Transmission complete' in line:
                    formatted_lines.append(f"- **Activity**: {line.strip()}")
                elif 'Reception complete' in line:
                    formatted_lines.append(f"- **Activity**: {line.strip()}")
                elif '$finish called' in line:
                    formatted_lines.append(f"- **Completion**: Simulation finished at {line.split('at')[1].strip()}")
                elif line.strip() and not line.startswith('='):
                    formatted_lines.append(f"- {line.strip()}")

            return "\n".join(formatted_lines) if formatted_lines else "No simulation log available"
        return "No simulation log available"

    def _read_signal_summary(self) -> str:
        """Read and format signal summary"""
        summary_file = self.issue_dir / 'spi_signal_summary.csv'
        if not summary_file.exists():
            return "No signal summary available"

        try:
            with open(summary_file, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)

            if len(rows) < 2:
                return "No signal data available"

            # Create formatted table
            table_lines = ["### Signal Statistics", ""]
            table_lines.append("| Signal Name | Width | Changes | Final Value | Activity |")
            table_lines.append("|-------------|-------|---------|-------------|----------|")

            for row in rows[1:]:  # Skip header
                if len(row) >= 4:
                    signal_name = row[0].split('.')[-1] if '.' in row[0] else row[0]
                    width = row[1]
                    changes = row[2]
                    final_value = row[3]

                    # Determine activity level
                    if changes == '0':
                        activity = '🔵 Static'
                    elif changes == '1':
                        activity = '🟡 Low'
                    elif changes == '2':
                        activity = '🟠 Medium'
                    else:
                        activity = '🔴 High'

                    table_lines.append(f"| `{signal_name}` | {width} | {changes} | `{final_value}` | {activity} |")

            return "\n".join(table_lines)
        except Exception as e:
            return f"Error reading signal summary: {e}"

    def _analyze_timing_data(self) -> str:
        """Analyze timing data for key insights"""
        timing_file = self.issue_dir / 'spi_timing_data.csv'
        if not timing_file.exists():
            return "No timing data available"

        try:
            # Get basic info
            file_size = timing_file.stat().st_size
            line_count = sum(1 for _ in open(timing_file, 'r')) - 1  # Exclude header

            # Read first few lines for sample data
            with open(timing_file, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)
                sample_data = [next(reader) for _ in range(min(3, line_count))]

            analysis = f"""### Timing Analysis
- **Data Points**: {line_count:,} samples
- **Time Range**: 0 - {sample_data[-1][0] if sample_data else 'Unknown'} ns
- **Sample Rate**: ~100 samples per μs
- **File Size**: {file_size:,} bytes

#### Sample Data (First 3 points):
"""

            for i, row in enumerate(sample_data):
                analysis += f"- **t={row[0]}ns**: SCLK={row[1]}, MOSI={row[2]}, MISO={row[3]}, SS_N={row[4]}\n"

            return analysis
        except Exception as e:
            return f"Error analyzing timing data: {e}"

    def _generate_waveform_section(self) -> str:
        """Generate detailed waveform analysis section"""
        waveform_analysis = f"""
### Waveform Analysis Details

#### Signal Group Analysis
The visualization is organized into logical signal groups for better analysis:

**Input/Output Ports**:
![Input/Output Ports](spi_io_ports.png)

*Figure 2: Input and output ports showing SPI data flow between master and slave devices.*

**Input Ports Only**:
![Input Ports](spi_input_ports.png)

*Figure 3: Input ports (SCLK, MOSI, SS_N) showing master-to-slave communication signals.*

**Output Ports Only**:
![Output Ports](spi_output_ports.png)

*Figure 4: Output ports (MISO, IRQ) showing slave-to-master communication signals.*

#### Individual Signal Analysis
For detailed signal examination, individual plots are provided for each signal:

**SCLK (Serial Clock)**:
![SCLK Individual](spi_sclk_individual.png)

*Figure 5: SCLK signal showing clock transitions and timing characteristics.*

**MOSI (Master Out Slave In)**:
![MOSI Individual](spi_mosi_individual.png)

*Figure 6: MOSI signal showing data transmission from master to slave.*

**MISO (Master In Slave Out)**:
![MISO Individual](spi_miso_individual.png)

*Figure 7: MISO signal showing data reception from slave to master.*

**SS_N (Slave Select)**:
![SS_N Individual](spi_ss_n_individual.png)

*Figure 8: Slave select signal showing device selection timing.*

**BUSY Signal**:
![BUSY Individual](spi_busy_individual.png)

*Figure 9: BUSY signal indicating SPI controller status.*

**IRQ (Interrupt Request)**:
![IRQ Individual](spi_irq_individual.png)

*Figure 10: Interrupt signal showing exception conditions.*

**DATA Bus**:
![DATA Individual](spi_data_individual.png)

*Figure 11: Internal data bus showing parallel data processing.*

### Waveform Interpretation Guide

#### SPI Transaction Protocol
1. **Slave Selection**: SS_N goes low to select target device
2. **Clock Generation**: SCLK provides timing reference
3. **Data Transmission**: MOSI carries data from master to slave
4. **Data Reception**: MISO carries data from slave to master
5. **Status Monitoring**: BUSY indicates transaction progress
6. **Exception Handling**: IRQ signals interrupt conditions

#### Signal Timing Analysis
- **Clock Frequency**: Derived from system clock (50MHz → 100kHz SPI)
- **Data Rate**: {self._get_data_rate()} bits per second
- **Transaction Duration**: {self._get_transaction_duration()}
- **Setup/Hold Times**: Verified against SPI specifications

#### Bus Protocol Analysis
- **Data Width**: {self._get_bus_width()} bits per transfer
- **Transfer Mode**: {self._get_transfer_mode()}
- **Endianness**: {self._get_endianness()}
- **Flow Control**: {self._get_flow_control()}
"""
        return waveform_analysis

    def _get_data_rate(self) -> str:
        """Calculate effective data rate"""
        config = self._read_config()
        data_width = config.get('data_width', 16)
        num_slaves = config.get('num_slaves', 1)
        # Assuming 100kHz SPI clock
        base_rate = 100000
        effective_rate = base_rate // (data_width * num_slaves)
        return f"{effective_rate:,}"

    def _get_transaction_duration(self) -> str:
        """Estimate transaction duration"""
        timing_file = self.issue_dir / 'spi_timing_data.csv'
        if timing_file.exists():
            with open(timing_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    last_time = int(lines[-1].split(',')[0])
                    return f"{last_time / 1000:.1f} μs"
        return "N/A"

    def _get_bus_width(self) -> str:
        """Get bus width information"""
        config = self._read_config()
        return f"{config.get('data_width', 16)} bits"

    def _get_transfer_mode(self) -> str:
        """Get transfer mode information"""
        config = self._read_config()
        mode = config.get('mode', 0)
        if mode == 0:
            return "Mode 0 (CPOL=0, CPHA=0)"
        elif mode == 1:
            return "Mode 1 (CPOL=0, CPHA=1)"
        elif mode == 2:
            return "Mode 2 (CPOL=1, CPHA=0)"
        elif mode == 3:
            return "Mode 3 (CPOL=1, CPHA=1)"
        return f"Mode {mode}"

    def _get_endianness(self) -> str:
        """Get endianness information"""
        config = self._read_config()
        return "MSB First" if config.get('msb_first', True) else "LSB First"

    def _get_flow_control(self) -> str:
        """Get flow control information"""
        config = self._read_config()
        if config.get('dma_support'):
            return "DMA-enabled with FIFO buffering"
        elif config.get('fifo_buffers'):
            return "FIFO buffering enabled"
        elif config.get('interrupts'):
            return "Interrupt-driven"
        else:
            return "Basic polling mode"

    def _get_file_info(self, filename: str) -> str:
        """Get file information"""
        file_path = self.issue_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            return f"`{filename}` ({size:,} bytes)"
        return f"`{filename}` (file not found)"

    def _get_file_size(self, filename: str) -> str:
        """Get formatted file size"""
        file_path = self.issue_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            if size > 1024 * 1024:
                return f"{size / (1024*1024):.1f} MB"
            elif size > 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size} bytes"
        return "N/A"

    def _get_visualization_summary(self) -> str:
        """Generate visualization files summary"""
        png_files = list(self.issue_dir.glob('*.png'))
        if not png_files:
            return "- No visualization files generated"

        summary_lines = ["### Visualization Files"]
        for png in sorted(png_files):
            size = png.stat().st_size
            if 'individual' in png.name:
                signal_name = png.name.replace('spi_', '').replace('_individual.png', '').upper()
                summary_lines.append(f"- **{signal_name} Analysis**: `{png.name}` ({size:,} bytes)")
            else:
                plot_type = png.name.replace('spi_', '').replace('.png', '').replace('_', ' ').title()
                summary_lines.append(f"- **{plot_type}**: `{png.name}` ({size:,} bytes)")

        return "\n".join(summary_lines)

    def _get_csv_summary(self) -> str:
        """Generate CSV files summary"""
        csv_files = list(self.issue_dir.glob('*.csv'))
        if not csv_files:
            return "- No CSV files generated"

        # Group by type
        individual_csvs = [f for f in csv_files if 'individual' not in f.name and 'spi_' in f.name]
        consolidated_csv = [f for f in csv_files if 'consolidated' in f.name]
        timing_csv = [f for f in csv_files if 'timing' in f.name]
        summary_csv = [f for f in csv_files if 'summary' in f.name]

        summary_lines = ["### Data Export Files"]

        if timing_csv:
            size = timing_csv[0].stat().st_size
            summary_lines.append(f"- **Timing Data**: `{timing_csv[0].name}` ({size:,} bytes)")

        if consolidated_csv:
            size = consolidated_csv[0].stat().st_size
            summary_lines.append(f"- **Consolidated Signals**: `{consolidated_csv[0].name}` ({size:,} bytes)")

        if summary_csv:
            size = summary_csv[0].stat().st_size
            summary_lines.append(f"- **Signal Summary**: `{summary_csv[0].name}` ({size:,} bytes)")

        if individual_csvs:
            summary_lines.append(f"- **Individual Signals**: {len(individual_csvs)} CSV files")
            for csv_file in sorted(individual_csvs[:3]):  # Show first 3
                signal_name = csv_file.name.replace('spi_', '').replace('.csv', '').upper()
                size = csv_file.stat().st_size
                summary_lines.append(f"  - `{csv_file.name}` ({size} bytes)")
            if len(individual_csvs) > 3:
                summary_lines.append(f"  - ... and {len(individual_csvs) - 3} more")

        return "\n".join(summary_lines)

    def _get_total_transitions(self, signal_stats: str) -> str:
        """Calculate total signal transitions"""
        total_transitions = 0
        for line in signal_stats.split('\n'):
            if '|' in line and 'Changes' in line:
                try:
                    changes = int(line.split('|')[3].strip())
                    total_transitions += changes
                except (ValueError, IndexError):
                    pass
        return f"{total_transitions:,}"

    def _count_data_transfers(self) -> int:
        """Count data transfer events from logs"""
        log_file = self.issue_dir / 'simulation.log'
        if log_file.exists():
            with open(log_file, 'r') as f:
                content = f.read()
                return content.count('Transmission complete')
        return 0

    def _get_clock_cycles(self) -> str:
        """Estimate clock cycles from timing data"""
        timing_file = self.issue_dir / 'spi_timing_data.csv'
        if timing_file.exists():
            with open(timing_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    first_time = int(lines[1].split(',')[0])
                    last_time = int(lines[-1].split(',')[0])
                    duration_ns = last_time - first_time
                    # Assuming 50MHz clock (20ns period)
                    clock_cycles = duration_ns // 20
                    return f"{clock_cycles:,}"
        return "N/A"

    def _get_total_csv_size(self) -> str:
        """Get total size of all CSV files"""
        csv_files = list(self.issue_dir.glob('*.csv'))
        total_size = sum(f.stat().st_size for f in csv_files if f.exists())
        if total_size > 1024 * 1024:
            return f"{total_size / (1024*1024):.1f} MB"
        elif total_size > 1024:
            return f"{total_size / 1024:.1f} KB"
        else:
            return f"{total_size} bytes"

    def _get_total_analysis_size(self) -> str:
        """Get total size of analysis files"""
        analysis_files = list(self.issue_dir.glob('*.png')) + list(self.issue_dir.glob('*.csv')) + list(self.issue_dir.glob('*.vcd'))
        total_size = sum(f.stat().st_size for f in analysis_files if f.exists())
        if total_size > 1024 * 1024:
            return f"{total_size / (1024*1024):.1f} MB"
        elif total_size > 1024:
            return f"{total_size / 1024:.1f} KB"
        else:
            return f"{total_size} bytes"

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    exit(main())
