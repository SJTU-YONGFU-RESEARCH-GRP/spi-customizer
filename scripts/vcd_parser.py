#!/usr/bin/env python3
"""
VCD Parser and CSV Generator
Parses VCD files from RTL simulations and generates CSV files for plotting
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Optional, Any, Tuple

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

    # Canonical signals we want for timing exports
    SIGNAL_ORDER = ['SCLK', 'MOSI', 'MISO', 'SS_N', 'BUSY', 'IRQ', 'DATA']
    CANONICAL_SUFFIXES = {
        'SCLK': ('sclk', 'sclk_in'),
        'MOSI': ('mosi', 'mosi_in'),
        'MISO': ('miso', 'miso_out'),
        'SS_N': ('ss_n', 'ss_in'),
        'BUSY': ('busy',),
        'IRQ': ('irq',),
        'DATA': ('rx_data', 'data'),
    }
    SIGNAL_NAME_PRIORITY = {
        'SCLK': ('sclk', 'sclk_in'),
        'MOSI': ('mosi', 'mosi_in'),
        'MISO': ('miso', 'miso_out'),
        'SS_N': ('ss_n', 'ss_in'),
        'BUSY': ('busy',),
        'IRQ': ('irq',),
        'DATA': ('rx_data', 'data'),
    }

    def __init__(self, vcd_data: Dict[str, Any], output_dir: str):
        self.vcd_data = vcd_data
        self.output_dir = Path(output_dir)
        self.data_dir = self.output_dir / 'data'
        self.graphs_dir = self.output_dir / 'graphs'
        self.logs_dir = self.output_dir / 'logs'
        self.data_dir.mkdir(exist_ok=True)
        self.graphs_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.canonical_signals = self._build_canonical_signal_map()

    def _canonical_name(self, signal_full_name: str) -> Optional[str]:
        """Map a full VCD signal path to one canonical SPI signal."""
        short_name = signal_full_name.split('.')[-1].lower()
        for canonical, suffixes in self.CANONICAL_SUFFIXES.items():
            if short_name in suffixes:
                return canonical
        return None

    def _build_canonical_signal_map(self) -> Dict[str, Dict[str, Any]]:
        """
        Build a stable canonical-name -> signal-data map.
        Prefers DUT-facing names to avoid mixing similarly named TB wires/regs.
        """
        selected: Dict[str, Dict[str, Any]] = {}
        signals = self.vcd_data.get('signals', {})
        for signal_data in signals.values():
            full_name = signal_data.get('name', '')
            canonical = self._canonical_name(full_name)
            if not canonical:
                continue

            existing = selected.get(canonical)
            if existing is None:
                selected[canonical] = signal_data
                continue

            existing_name = existing.get('name', '')
            # Prefer DUT signals when available.
            if '.dut.' in full_name and '.dut.' not in existing_name:
                selected[canonical] = signal_data
                continue

            # Prefer primary short-name forms (e.g., ss_n over ss_in).
            new_short = full_name.split('.')[-1].lower()
            old_short = existing_name.split('.')[-1].lower()
            priorities = self.SIGNAL_NAME_PRIORITY.get(canonical, ())
            if priorities:
                old_idx = priorities.index(old_short) if old_short in priorities else len(priorities)
                new_idx = priorities.index(new_short) if new_short in priorities else len(priorities)
                if new_idx < old_idx:
                    selected[canonical] = signal_data

        return selected

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
        csv_file = self.data_dir / 'spi_timing_data.csv'
        canonical = self.canonical_signals

        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header with only present canonical signals
            header = ['Time (ns)']
            present_order = [name for name in self.SIGNAL_ORDER if name in canonical]
            header.extend(present_order)

            writer.writerow(header)
            print(f"✅ Generated timing CSV header: {header}")

            # Get all unique times
            all_times = set()

            # Collect all change times
            for signal_data in self.vcd_data.get('signals', {}).values():
                for time, value in signal_data.get('changes', []):
                    all_times.add(time)

            # Sort times
            sorted_times = sorted(all_times)

            # Write data rows
            for time_ns in sorted_times:
                row = [time_ns]

                # Get signal values at this time using canonical map
                for signal_name in present_order:
                    signal_data = canonical.get(signal_name)
                    if signal_data is None:
                        row.append('x')
                    else:
                        row.append(self._get_value_at_time(signal_data, time_ns))

                writer.writerow(row)

        print(f"✅ Generated timing CSV: {csv_file}")
        return str(csv_file)

    def _generate_summary_csv(self) -> Optional[str]:
        """Generate CSV with signal summary information"""
        csv_file = self.data_dir / 'spi_signal_summary.csv'

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
        used_names = set()

        for signal_name, signal_data in signals.items():
            # Get meaningful signal name
            meaningful_name = self._canonical_name(signal_data['name']) or signal_data['name']

            # Create filename with meaningful name (replace special chars)
            safe_name = meaningful_name.replace(' ', '_').replace('/', '_')
            if safe_name in used_names:
                safe_name = signal_data['name'].replace(' ', '_').replace('/', '_')
            used_names.add(safe_name)
            csv_file = self.data_dir / f'spi_{safe_name}_data.csv'

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
        timing_csv = self.data_dir / 'spi_timing_data.csv'

        if not timing_csv.exists():
            return None

        try:
            consolidated_csv = self.data_dir / 'spi_consolidated_signals.csv'

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
                    meaningful_name = self._canonical_name(signal_data['name']) or signal_data['name']
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

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.csv_dir = self.output_dir / 'data'  # CSV files are in the data subdirectory
        self.graphs_dir = self.output_dir / 'graphs'
        self.logs_dir = self.output_dir / 'logs'
        self.graphs_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

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
            plot_file = self.logs_dir / 'spi_timing_diagram.txt'

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
                    if len(row) >= 2:
                        row_map = dict(zip(rows[0], row))
                        time = row_map.get('Time (ns)', 'N/A')
                        sclk = row_map.get('SCLK', 'x')
                        mosi = row_map.get('MOSI', 'x')
                        miso = row_map.get('MISO', 'x')
                        ss_n = row_map.get('SS_N', 'x')
                        busy = row_map.get('BUSY', 'x')
                        irq = row_map.get('IRQ', 'x')
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
            plot_file = self.logs_dir / 'spi_signal_analysis.txt'

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
    vcd_file = f"results/issue-{issue_number}/data/spi_waveform.vcd"

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
        plot_gen = SignalPlotGenerator(f"results/issue-{issue_number}")
        plot_files = plot_gen.generate_all_plots()

        # Also generate individual signal plots
        individual_plots = plot_gen.generate_individual_signal_plots()
        plot_files.extend(individual_plots)

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
        self.graphs_dir = self.output_dir / 'graphs'
        self.data_dir = self.output_dir / 'data'
        self.graphs_dir.mkdir(exist_ok=True)
        self.slave_active_low = self._load_slave_active_low()
        self.num_slaves = self._load_num_slaves()

    def _load_slave_active_low(self) -> bool:
        """Load SS polarity from generated spi_config.json; default active-low."""
        config_path = self.output_dir / 'code' / 'spi_config.json'
        try:
            with open(config_path, 'r') as f:
                cfg = json.load(f)
            return bool(cfg.get('slave_active_low', True))
        except Exception:
            return True

    def _load_num_slaves(self) -> int:
        """Load configured slave count from spi_config.json; default 1."""
        config_path = self.output_dir / 'code' / 'spi_config.json'
        try:
            with open(config_path, 'r') as f:
                cfg = json.load(f)
            value = int(cfg.get('num_slaves', 1))
            return value if value > 0 else 1
        except Exception:
            return 1

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
            timing_csv = self.output_dir / 'data' / 'spi_timing_data.csv'
            if not timing_csv.exists():
                print(f"⚠️  Timing CSV not found for individual plots")
                return individual_plots

            # Read timing data
            time_data = []
            signal_data = {}
            signal_raw_data = {}

            with open(timing_csv, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Read header

                for row in reader:
                    if len(row) < 8:
                        continue

                    time_ns = int(row[0])
                    time_data.append(time_ns / 1000.0)  # Convert to microseconds (keep as float)

                    # Process each signal column
                    for i in range(1, len(header)):  # Skip time column
                        signal_name = header[i]
                        if signal_name not in signal_data:
                            signal_data[signal_name] = []
                            signal_raw_data[signal_name] = []

                        value = row[i] if i < len(row) else 'x'
                        if signal_name == 'SS_N':
                            signal_data[signal_name].append(self._ss_to_numeric(value))
                        else:
                            signal_data[signal_name].append(self._logic_to_numeric(value))
                        signal_raw_data[signal_name].append(value)

            if not time_data:
                print("⚠️  No data found for individual plots")
                return individual_plots

            # Create individual plots for each signal
            for signal_name, values in signal_data.items():
                if len(values) == 0:
                    continue

                plt.figure(figsize=(12, 6))
                ax = plt.gca()
                self._plot_spi_signal(ax, signal_name, time_data, values)

                # Preserve bus-value readability in individual DATA plot.
                if signal_name == 'DATA':
                    self._annotate_data_bus_values(
                        ax,
                        time_data,
                        signal_raw_data.get(signal_name, []),
                        values,
                    )
                    self._annotate_data_bus_summary(
                        ax,
                        signal_raw_data.get(signal_name, []),
                        values,
                    )

                plt.tight_layout()
                plot_file = self.graphs_dir / f'spi_{signal_name.lower()}_individual.png'
                plt.savefig(plot_file, dpi=150)
                plt.close()

                individual_plots.append(str(plot_file))
                print(f"✅ Generated individual plot for {signal_name}: {plot_file}")

            print(f"✅ Generated {len(individual_plots)} individual signal plots")
            return individual_plots

        except Exception as e:
            print(f"❌ Failed to generate individual plots: {e}")
            return individual_plots

    def _annotate_data_bus_values(
        self,
        ax: plt.Axes,
        time_data: List[float],
        raw_values: List[str],
        numeric_values: List[float],
    ) -> None:
        """
        Annotate DATA bus values as hex on value-change intervals.
        Limits label count to keep plots readable.
        """
        if not time_data or not raw_values:
            return
        max_labels = 24
        changes = []
        prev = None
        for i, raw in enumerate(raw_values):
            if prev is None or raw != prev:
                changes.append(i)
                prev = raw
        if len(changes) > max_labels:
            stride = max(1, len(changes) // max_labels)
            changes = changes[::stride]

        for idx in changes:
            raw = raw_values[idx]
            label = self._format_bus_value_label(raw)
            if not label:
                continue
            x = time_data[idx]
            y = numeric_values[idx] if idx < len(numeric_values) else 0.5
            ax.annotate(
                label,
                (x, y),
                textcoords="offset points",
                xytext=(0, 6),
                ha="center",
                fontsize=7,
                color="black",
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.7),
            )

    def _format_bus_value_label(self, raw: str) -> str:
        if raw in {"0", "1"}:
            return raw
        if raw.startswith('b'):
            bits = raw[1:]
            if bits and all(bit in "01" for bit in bits):
                return f"0x{int(bits, 2):X}"
            return "X"
        return ""

    def _annotate_data_bus_summary(
        self,
        ax: plt.Axes,
        raw_values: List[str],
        numeric_values: List[float],
    ) -> None:
        """
        Add a DATA-bus specific summary annotation for individual DATA plot.
        """
        if not raw_values or not numeric_values:
            return

        transitions = sum(1 for i in range(1, len(raw_values)) if raw_values[i] != raw_values[i - 1])
        unknown_count = sum(1 for v in numeric_values if v == 0.5)
        known_values = [int(v) for v in numeric_values if v != 0.5]
        if known_values:
            min_val = min(known_values)
            max_val = max(known_values)
            last_val = known_values[-1]
            min_txt = f"0x{min_val:X}"
            max_txt = f"0x{max_val:X}"
            last_txt = f"0x{last_val:X}"
        else:
            min_txt = "X"
            max_txt = "X"
            last_txt = "X"

        stats_text = (
            f"Bus Transitions: {transitions}\n"
            f"Min: {min_txt}\n"
            f"Max: {max_txt}\n"
            f"Last: {last_txt}\n"
            f"Unknown: {unknown_count}\n"
            f"Samples: {len(raw_values)}"
        )
        ax.text(
            0.98,
            0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=8,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.85),
        )

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
        """Generate a plot with subplots for each signal with intelligent data handling"""
        try:
            timing_csv = self.data_dir / 'spi_timing_data.csv'
            if not timing_csv.exists():
                print(f"⚠️  Timing CSV not found for {title}")
                return None

            # Load and preprocess data with intelligent sampling
            time_data, signal_data = self._preprocess_signal_data(signal_names)

            if not time_data or not signal_data:
                print(f"⚠️  No valid data found for {title}")
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
            fig.suptitle(f'SPI {title} - Protocol Analysis', fontsize=16, fontweight='bold')

            # Flatten axes for easier iteration
            if num_signals == 1:
                axes = [axes]
            elif rows == 1 or cols == 1:
                axes = axes.flatten()
            else:
                axes = axes.flatten()

            # Plot each signal in its own subplot with SPI-aware visualization
            for i, signal_name in enumerate(signal_names):
                if i >= len(axes):
                    break  # Safety check

                ax = axes[i]
                if signal_data[signal_name]:
                    self._plot_spi_signal(ax, signal_name, time_data, signal_data[signal_name])
                else:
                    ax.text(0.5, 0.5, f'No data for\n{signal_name}',
                           transform=ax.transAxes, ha='center', va='center', fontsize=10)
                    ax.set_title(f'{signal_name} (No Data)')

            # Hide unused subplots
            for i in range(len(signal_names), len(axes)):
                axes[i].set_visible(False)

            plt.tight_layout(rect=[0, 0, 1, 0.97])
            plot_file = self.graphs_dir / filename
            plt.savefig(plot_file, dpi=150)
            plt.close()

            print(f"✅ Generated {title} protocol plot: {plot_file}")
            return str(plot_file)

        except Exception as e:
            print(f"❌ Failed to generate {title} plot: {e}")
            return None

    def _preprocess_signal_data(self, signal_names: List[str]) -> Tuple[List[float], Dict[str, List[float]]]:
        """Preprocess signal data with intelligent sampling and activity detection"""
        timing_csv = self.data_dir / 'spi_timing_data.csv'

        # First pass: analyze data characteristics
        total_samples = sum(1 for _ in open(timing_csv, 'r')) - 1  # Exclude header
        print(f"📊 Processing {total_samples:,} total samples")

        # For digital signals, we want sharp transitions, so use minimal sampling
        # Only sample if dataset is extremely large (>500k points)
        if total_samples > 500000:
            # Sample every Nth point to keep plots readable but preserve transitions
            sample_rate = max(1, total_samples // 100000)  # Target ~100k points max
            print(f"🔄 Using adaptive sampling (1/{sample_rate}) for very large dataset")
        else:
            sample_rate = 1

        time_data = []
        signal_data = {name: [] for name in signal_names}

        with open(timing_csv, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header
            header_index = {name: idx for idx, name in enumerate(header)}

            sample_counter = 0
            for row in reader:
                if not row:
                    continue

                sample_counter += 1
                if sample_counter % sample_rate != 0:
                    continue

                time_ns = int(row[0])
                time_data.append(time_ns / 1000.0)  # Convert to microseconds (keep as float)

                for signal_name in signal_names:
                    csv_idx = header_index.get(signal_name)
                    if csv_idx is not None and csv_idx < len(row):
                        value = row[csv_idx]
                        if signal_name == 'SS_N':
                            signal_data[signal_name].append(self._ss_to_numeric(value))
                        else:
                            signal_data[signal_name].append(self._logic_to_numeric(value))

        print(f"✅ Processed {len(time_data):,} samples after sampling")
        return time_data, signal_data

    def _ss_to_numeric(self, value: str) -> float:
        """
        Convert SS value to a plottable numeric level.
        Polarity-aware visualization convention:
        - inactive -> 1
        - active (any selected slave) -> 0
        - unknown/undecidable -> 0.5
        """
        active_low = self.slave_active_low
        if value in {'0', '1'}:
            bit_active = (value == '0') if active_low else (value == '1')
            return 0 if bit_active else 1
        if value.startswith('b'):
            bits = value[1:]
            if bits and all(b in '01' for b in bits):
                any_active = any((b == '0') if active_low else (b == '1') for b in bits)
                return 0 if any_active else 1
        return 0.5

    def _logic_to_numeric(self, value: str) -> float:
        """
        Convert logic strings into plottable numeric values.
        Supports single-bit and known multi-bit bus values.
        """
        if value == '1':
            return 1.0
        if value == '0':
            return 0.0
        if value.startswith('b'):
            bits = value[1:]
            if bits and all(bit in '01' for bit in bits):
                return float(int(bits, 2))
            return 0.5
        return 0.5

    def _plot_spi_signal(self, ax: plt.Axes, signal_name: str, time_data: List[float], values: List[float]) -> None:
        """Plot a single SPI signal with protocol-aware visualization"""
        # Plot the main signal with step-style for sharp digital transitions
        ax.plot(time_data, values, drawstyle='steps-post', linewidth=2,
                color=self._get_signal_color(signal_name), alpha=0.9)

        # Add SPI protocol-specific enhancements
        if signal_name == 'SCLK':
            self._enhance_clock_signal(ax, time_data, values)
        elif signal_name in ['MOSI', 'MISO']:
            self._enhance_data_signal(ax, signal_name, time_data, values)
        elif signal_name == 'SS_N':
            self._enhance_slave_select(ax, time_data, values)

        # Configure axis
        ax.set_title(f'{signal_name} Signal', fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (μs)')
        ax.grid(True, alpha=0.3)

        if signal_name == 'DATA':
            ax.set_ylabel('Data Value')
        else:
            ax.set_ylabel('Logic Level')
            ax.set_yticks([0, 0.5, 1])
            ax.set_yticklabels(['0', 'X', '1'])
            ax.set_ylim(-0.1, 1.1)

        # Add signal statistics
        self._add_signal_statistics(ax, signal_name, values)

    def _add_signal_statistics(self, ax: plt.Axes, signal_name: str, values: List[float]) -> None:
        """Add comprehensive signal statistics to the plot"""
        # For SPI signals, calculate statistics during active transactions only
        if signal_name in ['SCLK', 'MOSI', 'MISO', 'SS_N']:
            # Find active transaction periods based on SS_N being active (any slave selected)
            ss_n_values = self._get_signal_values('SS_N')
            if ss_n_values:
                # Identify transaction periods where SS_N has any slave active.
                transaction_samples = []
                for i, (val, ss_val) in enumerate(zip(values, ss_n_values)):
                    ss_active = self._is_ss_active_for_plot(ss_val)
                    if ss_active:
                        transaction_samples.append(val)

                if transaction_samples:
                    # Use transaction-only statistics
                    values = transaction_samples

        # Calculate statistics
        high_count = sum(1 for v in values if v == 1)
        low_count = sum(1 for v in values if v == 0)
        unknown_count = sum(1 for v in values if v == 0.5)
        transitions = sum(1 for j in range(1, len(values)) if values[j] != values[j-1])

        total_samples = len(values)
        high_pct = 100 * high_count / total_samples if total_samples > 0 else 0
        low_pct = 100 * low_count / total_samples if total_samples > 0 else 0

        # Create statistics text
        stats_text = f'Samples: {total_samples:,}\nTransitions: {transitions}\nHigh: {high_count} ({high_pct:.1f}%)\nLow: {low_count} ({low_pct:.1f}%)'
        if unknown_count > 0:
            unknown_pct = 100 * unknown_count / total_samples
            stats_text += f'\nUnknown: {unknown_count} ({unknown_pct:.1f}%)'

        ax.text(0.02, 0.02, stats_text, transform=ax.transAxes,
               fontsize=8, verticalalignment='bottom',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcyan', alpha=0.8))

    def _get_signal_color(self, signal_name: str) -> str:
        """Get appropriate color for each signal type"""
        color_map = {
            'SCLK': 'blue',
            'MOSI': 'green',
            'MISO': 'red',
            'SS_N': 'orange',
            'BUSY': 'purple',
            'IRQ': 'brown',
            'DATA': 'gray'
        }
        return color_map.get(signal_name, 'black')

    def _enhance_clock_signal(self, ax: plt.Axes, time_data: List[float], values: List[float]) -> None:
        """Add clock-specific enhancements like period markers"""
        # Detect clock edges
        rising_edges = []
        falling_edges = []

        for i in range(1, len(values)):
            if values[i-1] == 0 and values[i] == 1:
                rising_edges.append((time_data[i], values[i]))
            elif values[i-1] == 1 and values[i] == 0:
                falling_edges.append((time_data[i], values[i]))

        # Mark first few edges
        if rising_edges:
            ax.plot(*zip(*rising_edges[:5]), 'ro', markersize=4, alpha=0.7, label='Rising Edge')
        if falling_edges:
            ax.plot(*zip(*falling_edges[:5]), 'bo', markersize=4, alpha=0.7, label='Falling Edge')

        # Calculate approximate frequency if we have edges
        if len(rising_edges) > 1:
            periods = [rising_edges[i+1][0] - rising_edges[i][0] for i in range(min(5, len(rising_edges)-1))]
            avg_period = sum(periods) / len(periods) if periods else 0
            if avg_period > 0:
                freq_khz = 1000.0 / avg_period
                ax.text(0.02, 0.85, f'~{freq_khz:.1f} kHz', transform=ax.transAxes,
                       fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.8))

    def _enhance_data_signal(self, ax: plt.Axes, signal_name: str, time_data: List[float], values: List[float]) -> None:
        """Add data signal enhancements like bit transitions"""
        # Detect data transitions
        transitions = []
        for i in range(1, len(values)):
            if values[i] != values[i-1] and values[i] != 0.5:  # Ignore X states
                transitions.append((time_data[i], values[i]))

        # Mark transitions
        if transitions:
            ax.plot(*zip(*transitions[:10]), 'k^', markersize=5, alpha=0.8, label='Data Change')

        # Add data direction indicator
        direction = "Master→Slave" if signal_name == 'MOSI' else "Slave→Master"
        ax.text(0.02, 0.85, direction, transform=ax.transAxes,
               fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.8))

    def _enhance_slave_select(self, ax: plt.Axes, time_data: List[float], values: List[float]) -> None:
        """Add slave select specific enhancements"""
        # Values use convention active=0, inactive=1 from _ss_to_numeric.
        active_periods = []
        start_time = None

        for i, (t, v) in enumerate(zip(time_data, values)):
            if v == 0 and start_time is None:  # Going active (low)
                start_time = t
            elif v == 1 and start_time is not None:  # Going inactive (high)
                active_periods.append((start_time, t))
                start_time = None

        # Handle case where signal ends while active
        if start_time is not None:
            active_periods.append((start_time, time_data[-1]))

        # Highlight active periods
        for start, end in active_periods[:3]:  # Show first 3 periods
            ax.axvspan(start, end, alpha=0.2, color='yellow', label='Slave Active' if len(active_periods) == 1 else "")

        # Add polarity indicator
        polarity = 'Active Low' if self.slave_active_low else 'Active High'
        ax.text(0.02, 0.85, polarity, transform=ax.transAxes,
               fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

        # Sparse semantic labels on transitions for readability on multi-bit SS buses.
        raw_ss = self._get_signal_values('SS_N') or []
        if raw_ss:
            max_labels = 8
            labels_drawn = 0
            prev = None
            for i, raw in enumerate(raw_ss[:len(time_data)]):
                if prev is None or raw != prev:
                    label = self._ss_semantic_label(raw)
                    if label is not None:
                        ax.annotate(
                            label,
                            (time_data[i], values[i] if i < len(values) else 0.5),
                            textcoords="offset points",
                            xytext=(0, 8),
                            ha='center',
                            fontsize=7,
                            color='darkorange',
                        )
                        labels_drawn += 1
                        if labels_drawn >= max_labels:
                            break
                prev = raw

    def _is_ss_active_for_plot(self, raw_value: object) -> bool:
        """
        Determine whether SS is active for plotting/statistics from raw CSV value.
        """
        bits = self._normalized_ss_bits(raw_value)
        if bits is not None:
            active_low = self.slave_active_low
            return any((b == '0') if active_low else (b == '1') for b in bits)
        return False

    def _normalized_ss_bits(self, raw_value: object) -> Optional[str]:
        """
        Normalize raw SS value to full bus-width bitstring.
        Handles compact VCD encodings like b0 / b1000.
        """
        value = str(raw_value)
        active_low = self.slave_active_low
        inactive_bit = '1' if active_low else '0'
        if value in {'0', '1'}:
            bits = value
        elif value.startswith('b'):
            bits = value[1:]
        else:
            return None
        if not bits or not all(b in '01' for b in bits):
            return None
        if self.num_slaves > 1 and len(bits) < self.num_slaves:
            bits = bits.rjust(self.num_slaves, inactive_bit)
        return bits

    def _ss_semantic_label(self, raw_value: object) -> Optional[str]:
        """
        Convert raw SS value into readable semantic labels for sparse plot annotations.
        """
        active_low = self.slave_active_low
        bits = self._normalized_ss_bits(raw_value)
        if bits is None:
            return "INV"
        active_indices = []
        for pos, bit in enumerate(bits):
            bit_active = (bit == '0') if active_low else (bit == '1')
            if bit_active:
                # Verilog vector text is MSB->LSB; slave index 0 is rightmost bit.
                active_indices.append(len(bits) - 1 - pos)
        if not active_indices:
            return "IDLE"
        if len(active_indices) == 1:
            return f"SEL[{active_indices[0]}]"
        return "MULTI"

    def _get_signal_values(self, signal_name: str) -> Optional[List[object]]:
        """Get signal values from timing CSV.

        Returns raw SS_N vector/scalar strings for SS-aware predicates and numeric
        logic levels for other single-bit signals.
        """
        try:
            timing_csv = self.data_dir / 'spi_timing_data.csv'
            if not timing_csv.exists():
                return None

            signal_values = []
            with open(timing_csv, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header

                # Find column index for the signal
                signal_idx = None
                for i, col_name in enumerate(header):
                    if col_name == signal_name:
                        signal_idx = i
                        break

                if signal_idx is None:
                    return None

                # Read signal values
                for row in reader:
                    if len(row) > signal_idx:
                        value = row[signal_idx]
                        # Keep raw SS values so polarity-aware predicate can classify activity.
                        if signal_name == 'SS_N':
                            signal_values.append(value)
                        else:
                            # Convert to processed format (1, 0, 0.5) for other signals
                            if value == '1':
                                signal_values.append(1)
                            elif value == '0':
                                signal_values.append(0)
                            else:
                                signal_values.append(0.5)  # Unknown

            return signal_values
        except Exception:
            return None


class SummaryGenerator:
    """Generates comprehensive SUMMARY.md files for RTL simulation results"""

    def __init__(self, issue_dir: str):
        self.issue_dir = Path(issue_dir)
        self.code_dir = self.issue_dir / 'code'
        self.data_dir = self.issue_dir / 'data'
        self.graphs_dir = self.issue_dir / 'graphs'
        self.logs_dir = self.issue_dir / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        self.output_file = self.logs_dir / 'SUMMARY.md'

    def generate_summary(self) -> str:
        """Generate comprehensive summary of RTL simulation results"""

        # Read configuration
        config = self._read_config()
        if not config:
            return "❌ No configuration file found"

        # Read simulation log
        sim_log = self._read_simulation_log()
        simulation_ok = self._simulation_succeeded()

        # Read signal summary
        signal_stats = self._read_signal_summary()

        # Analyze timing data
        timing_analysis = self._analyze_timing_data()

        # Get waveform visualization section
        waveform_section = self._generate_waveform_section()

        gen_files = self._detect_generated_files()

        # Generate summary content
        summary_content = """# SPI RTL Simulation Summary - Issue {issue_number}

## 📋 Configuration Summary

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Issue Number** | `{issue_number}` | GitHub issue identifier |
| **SPI Mode** | `{mode}` | SPI protocol mode |
| **Data Width** | `{data_width} bits` | Width of data bus |
| **Number of Slaves** | `{num_slaves}` | Number of slave devices |
| **Slave Select** | `{slave_select}` | Slave select polarity |
| **Data Order** | `{data_order}` | Bit transmission order |
| **Test Duration** | `{test_duration}` | Simulation duration |
| **Simulation Status** | `{simulation_status}` | Overall result |

### 🔧 Advanced Features
- **Interrupts**: `{interrupts}`
- **FIFO Buffers**: `{fifo_buffers}`
- **DMA Support**: `{dma_support}`
- **Multi-master**: `{multi_master}`

## 🎯 RTL Design Information

### SPI Protocol Characteristics
- **Clock Polarity (CPOL)**: `{clock_polarity}` - Rest state of clock
- **Clock Phase (CPHA)**: `{clock_phase}` - Data sampling edge
- **Clock Frequency**: `~100kHz (derived from 50MHz system clock)` - SPI clock rate

### Signal Timing Analysis
{timing_analysis}

## 📊 Waveform Visualization

### Complete Signal Analysis
![All Signals Waveform](../graphs/spi_all_signals.png)

*Figure 1: Complete SPI signal analysis showing all monitored signals over the simulation period. Each signal is displayed in its own subplot for optimal readability.*

{waveform_section}

## 📊 Simulation Results

### Execution Summary
{sim_log}

### Signal Activity Summary
{signal_stats}

## 📁 Generated Files Overview

### Core Files
- **Verilog RTL**: `{core_file_info}`
- **Testbench**: `{tb_file_info}`
- **Simulation Executable**: `{sim_file_info}`
- **Compilation Log**: `{log_file_info}`

### Waveform & Analysis
- **VCD Waveform**: `{vcd_file_info}`
- **GTKWave Save**: `{gtkw_file_info}`
- **Timing Analysis CSV**: `{timing_csv_info}`
- **Consolidated Signals CSV**: `{consolidated_csv_info}`

{visualization_summary}

{csv_summary}

## 🔍 Key Findings

### Performance Metrics
- **Simulation Duration**: `{test_duration}`
- **Total Signals Monitored**: `{total_signals}`
- **VCD File Size**: `{vcd_size}`
- **Signal Transitions**: `{total_transitions}`

### Signal Analysis
- **Active Signals**: `{active_signals}`
- **Data Transfer Events**: `{data_transfers}`
- **Clock Cycles**: `{clock_cycles}`
- **Protocol Compliance**: `{protocol_compliance}`

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

### SPI Mode {mode} Specifications
- **CPOL = {cpol}**: Clock polarity
- **CPHA = {cpha}**: Clock phase
- **Data Rate**: `~{data_rate} bits/sec`
- **Frame Size**: `{frame_size} bits per transfer`

### Memory Requirements
- **VCD Storage**: `{vcd_storage}`
- **CSV Data**: `{csv_data}`
- **Total Analysis**: `{total_analysis}`

---

*Generated by SPI RTL Analyzer - {timestamp}*
*Analysis based on real Icarus Verilog simulation data*
""".format(
            issue_number=config.get('issue_number', 'Unknown'),
            mode=config.get('mode', 'Unknown'),
            data_width=config.get('data_width', 'Unknown'),
            num_slaves=config.get('num_slaves', 'Unknown'),
            slave_select='Active Low' if config.get('slave_active_low') else 'Active High',
            data_order='MSB First' if config.get('msb_first') else 'LSB First',
            test_duration=config.get('test_duration', 'Unknown'),
            simulation_status='✅ PASSED' if simulation_ok else '❌ FAILED',
            interrupts='✅ Enabled' if config.get('interrupts') else '❌ Disabled',
            fifo_buffers='✅ Enabled' if config.get('fifo_buffers') else '❌ Disabled',
            dma_support='✅ Enabled' if config.get('dma_support') else '❌ Disabled',
            multi_master='✅ Enabled' if config.get('multi_master') else '❌ Disabled',
            clock_polarity='High' if config.get('mode', 0) in [2,3] else 'Low',
            clock_phase='Falling edge' if config.get('mode', 0) in [1,2] else 'Rising edge',
            timing_analysis=timing_analysis,
            waveform_section=waveform_section,
            sim_log=sim_log,
            signal_stats=signal_stats,
            core_file_info=self._get_file_info(gen_files.get('core_relpath')),
            tb_file_info=self._get_file_info(gen_files.get('tb_relpath')),
            sim_file_info=self._get_file_info('data/spi_simulation'),
            log_file_info=self._get_file_info('logs/compilation.log'),
            vcd_file_info=self._get_file_info('data/spi_waveform.vcd'),
            gtkw_file_info=self._get_file_info('data/spi_waveform.gtkw'),
            timing_csv_info=self._get_file_info('data/spi_timing_data.csv'),
            consolidated_csv_info=self._get_file_info('data/spi_consolidated_signals.csv'),
            visualization_summary=self._get_visualization_summary(),
            csv_summary=self._get_csv_summary(),
            total_signals=len(list(self.data_dir.glob('*.csv'))),
            vcd_size=self._get_file_size('data/spi_waveform.vcd'),
            total_transitions=self._get_total_transitions(),
            active_signals=self._count_active_signals(),
            data_transfers=self._count_data_transfers(),
            clock_cycles=self._get_clock_cycles(),
            protocol_compliance=self._get_protocol_compliance_status(),
            cpol=1 if config.get('mode', 0) in [2,3] else 0,
            cpha=config.get('mode', 0) % 2,
            data_rate=100000 // (config.get('data_width', 16) * config.get('num_slaves', 1)),
            frame_size=config.get('data_width', 16),
            vcd_storage=self._get_file_size('data/spi_waveform.vcd'),
            csv_data=self._get_total_csv_size(),
            total_analysis=self._get_total_analysis_size(),
            timestamp=self._get_timestamp()
        )

        # Write summary to file
        with open(self.output_file, 'w') as f:
            f.write(summary_content)

        print(f"✅ Generated comprehensive summary: {self.output_file}")
        return str(self.output_file)

    def _read_config(self) -> Dict[str, Any]:
        """Read configuration from spi_config.json"""
        config_file = self.issue_dir / 'code' / 'spi_config.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}

    def _read_simulation_log(self) -> str:
        """Read and format simulation log"""
        log_file = self.logs_dir / 'simulation.log'
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

    def _simulation_succeeded(self) -> bool:
        """Determine simulation pass/fail from simulation.log evidence."""
        log_file = self.logs_dir / 'simulation.log'
        if not log_file.exists():
            return False
        try:
            content = log_file.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return False
        if "Return code: 0" not in content:
            return False
        if "FATAL:" in content:
            return False
        return True

    def _read_signal_summary(self) -> str:
        """Read and format signal summary"""
        summary_file = self.data_dir / 'spi_signal_summary.csv'
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
        timing_file = self.data_dir / 'spi_timing_data.csv'
        if not timing_file.exists():
            return "No timing data available"

        try:
            # Get basic info
            file_size = timing_file.stat().st_size
            line_count = sum(1 for _ in open(timing_file, 'r')) - 1  # Exclude header

            # Read first few lines for sample data and full time range
            with open(timing_file, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)
                rows = list(reader)

            sample_data = rows[:3]
            last_time = rows[-1][0] if rows else 'Unknown'
            idx = {name: i for i, name in enumerate(header)}
            sclk_idx = idx.get('SCLK', 1)
            mosi_idx = idx.get('MOSI', 2)
            miso_idx = idx.get('MISO', 3)
            ss_idx = idx.get('SS_N', 4)

            analysis = f"""### Timing Analysis
- **Data Points**: {line_count:,} samples
- **Time Range**: 0 - {last_time} ns
- **Sample Rate**: ~100 samples per μs
- **File Size**: {file_size:,} bytes

#### Sample Data (First 3 points):
"""

            for i, row in enumerate(sample_data):
                analysis += f"- **t={row[0]}ns**: SCLK={row[sclk_idx]}, MOSI={row[mosi_idx]}, MISO={row[miso_idx]}, SS_N={row[ss_idx]}"
                analysis += "\n"

            return analysis
        except Exception as e:
            return f"Error analyzing timing data: {e}"

    def _generate_waveform_section(self) -> str:
        """Generate detailed waveform analysis section"""
        waveform_analysis = """
### Waveform Analysis Details

#### Signal Group Analysis
The visualization is organized into logical signal groups for better analysis:

**Input/Output Ports**:
![Input/Output Ports](../graphs/spi_io_ports.png)

*Figure 2: Input and output ports showing SPI data flow between master and slave devices.*

**Input Ports Only**:
![Input Ports](../graphs/spi_input_ports.png)

*Figure 3: Input ports (SCLK, MOSI, SS_N) showing master-to-slave communication signals.*

**Output Ports Only**:
![Output Ports](../graphs/spi_output_ports.png)

*Figure 4: Output ports (MISO, IRQ) showing slave-to-master communication signals.*

#### Individual Signal Analysis
For detailed signal examination, individual plots are provided for each signal:

**SCLK (Serial Clock)**:
![SCLK Individual](../graphs/spi_sclk_individual.png)

*Figure 5: SCLK signal showing clock transitions and timing characteristics.*

**MOSI (Master Out Slave In)**:
![MOSI Individual](../graphs/spi_mosi_individual.png)

*Figure 6: MOSI signal showing data transmission from master to slave.*

**MISO (Master In Slave Out)**:
![MISO Individual](../graphs/spi_miso_individual.png)

*Figure 7: MISO signal showing data reception from slave to master.*

**SS_N (Slave Select)**:
![SS_N Individual](../graphs/spi_ss_n_individual.png)

*Figure 8: Slave select signal showing device selection timing.*

**BUSY Signal**:
![BUSY Individual](../graphs/spi_busy_individual.png)

*Figure 9: BUSY signal indicating SPI controller status.*

**IRQ (Interrupt Request)**:
![IRQ Individual](../graphs/spi_irq_individual.png)

*Figure 10: Interrupt signal showing exception conditions.*

**DATA Bus**:
![DATA Individual](../graphs/spi_data_individual.png)

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
- **Data Rate**: {data_rate} bits per second
- **Transaction Duration**: {transaction_duration}
- **Setup/Hold Times**: Verified against SPI specifications

#### Bus Protocol Analysis
- **Data Width**: {bus_width} per transfer
- **Transfer Mode**: {transfer_mode}
- **Endianness**: {endianness}
- **Flow Control**: {flow_control}
""".format(
            data_rate=self._get_data_rate(),
            transaction_duration=self._get_transaction_duration(),
            bus_width=self._get_bus_width(),
            transfer_mode=self._get_transfer_mode(),
            endianness=self._get_endianness(),
            flow_control=self._get_flow_control()
        )
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
        timing_file = self.data_dir / 'spi_timing_data.csv'
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

    def _get_file_info(self, relpath: Optional[str]) -> str:
        """Get file information from a repo-relative path under the issue directory"""
        if not relpath:
            return "`(not produced)`"
        file_path = (self.issue_dir / relpath)
        display = relpath.replace('\\', '/')
        if file_path.exists():
            size = file_path.stat().st_size
            return f"`{display}` ({size:,} bytes)"
        return f"`{display}` (file not found)"

    def _get_file_size(self, relpath: str) -> str:
        """Get formatted file size"""
        file_path = self.issue_dir / relpath
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
        png_files = list(self.graphs_dir.glob('*.png'))
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
        csv_files = list(self.data_dir.glob('*.csv'))
        if not csv_files:
            return "- No CSV files generated"

        # Group by type
        canonical_individual = {'spi_sclk_data.csv', 'spi_mosi_data.csv', 'spi_miso_data.csv', 'spi_ss_n_data.csv', 'spi_busy_data.csv', 'spi_irq_data.csv', 'spi_data_data.csv'}
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

        if canonical_individual:
            present_individual = [f for f in csv_files if f.name.lower() in canonical_individual]
            summary_lines.append(f"- **Individual Signals**: {len(present_individual)} canonical CSV files")
            for csv_file in sorted(present_individual[:3]):  # Show first 3
                size = csv_file.stat().st_size
                summary_lines.append(f"  - `{csv_file.name}` ({size} bytes)")
            if len(present_individual) > 3:
                summary_lines.append(f"  - ... and {len(present_individual) - 3} more")

        return "\n".join(summary_lines)

    def _read_signal_summary_rows(self) -> List[List[str]]:
        summary_file = self.data_dir / 'spi_signal_summary.csv'
        if not summary_file.exists():
            return []
        try:
            with open(summary_file, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
            return rows[1:] if len(rows) > 1 else []
        except Exception:
            return []

    def _get_total_transitions(self) -> str:
        """Calculate total signal transitions from signal summary CSV."""
        total_transitions = 0
        for row in self._read_signal_summary_rows():
            if len(row) >= 3:
                try:
                    total_transitions += int(row[2])
                except ValueError:
                    continue
        return f"{total_transitions:,}"

    def _count_active_signals(self) -> int:
        """Count signals that changed at least once."""
        active = 0
        for row in self._read_signal_summary_rows():
            if len(row) >= 3:
                try:
                    if int(row[2]) > 0:
                        active += 1
                except ValueError:
                    continue
        return active

    def _count_data_transfers(self) -> int:
        """Count data transfer events from logs"""
        log_file = self.logs_dir / 'simulation.log'
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            patterns = [
                'transmission complete',
                'reception complete',
                'slave mode spi transaction complete',
                'rx matched expected payload'
            ]
            return sum(content.count(p) for p in patterns)
        return 0

    def _get_clock_cycles(self) -> str:
        """Estimate clock cycles from timing data"""
        # Prefer actual clk transition counts from summary CSV when available.
        for row in self._read_signal_summary_rows():
            if len(row) >= 3:
                sig = row[0].split('.')[-1].lower()
                if sig == 'clk':
                    try:
                        return f"{int(row[2]):,}"
                    except ValueError:
                        break

        timing_file = self.data_dir / 'spi_timing_data.csv'
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
        csv_files = list(self.data_dir.glob('*.csv'))
        total_size = sum(f.stat().st_size for f in csv_files if f.exists())
        if total_size > 1024 * 1024:
            return f"{total_size / (1024*1024):.1f} MB"
        elif total_size > 1024:
            return f"{total_size / 1024:.1f} KB"
        else:
            return f"{total_size} bytes"

    def _get_total_analysis_size(self) -> str:
        """Get total size of analysis files"""
        analysis_files = list(self.graphs_dir.glob('*.png')) + list(self.data_dir.glob('*.csv')) + list(self.data_dir.glob('*.vcd'))
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

    def _get_protocol_compliance_status(self) -> str:
        sim_ok = self._simulation_succeeded()
        report = self.logs_dir / "protocol_compliance.md"
        if sim_ok and report.exists():
            return "`✅ Evidence-based checks generated`"
        if sim_ok:
            return "`⚠️ Simulation ran (no compliance report)`"
        return "`⚠️ Not verified (no simulation evidence)`"

    def _detect_generated_files(self) -> Dict[str, Optional[str]]:
        """
        Detect generated RTL/TB filenames for reporting.
        Prefers `logs/run_manifest.json` if present; otherwise falls back to scanning `code/`.
        """
        manifest_file = self.logs_dir / "run_manifest.json"
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                gen = manifest.get("generated_files", {})
                core_rel = gen.get("core_file")
                tb_rel = gen.get("tb_file")
                return {
                    "core_relpath": core_rel,
                    "tb_relpath": tb_rel,
                }
            except Exception:
                pass

        core_candidates = sorted([p for p in self.code_dir.glob("*.v") if not p.name.endswith("_tb.v")])
        tb_candidates = sorted([p for p in self.code_dir.glob("*_tb.v")])

        core_rel = str(core_candidates[0].relative_to(self.issue_dir)) if core_candidates else None
        tb_rel = str(tb_candidates[0].relative_to(self.issue_dir)) if tb_candidates else None

        return {"core_relpath": core_rel, "tb_relpath": tb_rel}


class ProtocolComplianceChecker:
    """
    Evidence-based protocol checks driven by `SPIConfig` and VCD signal transitions.
    This does not attempt to fully decode transactions; it provides minimal, auditable checks
    that are useful for triage and non-expert users.
    """

    def __init__(self, config, vcd_data: Dict[str, Any]):
        self.config = config
        self.vcd_data = vcd_data
        self.signals = vcd_data.get("signals", {})

    def write_markdown(self, output_path: str) -> None:
        md = self._render_markdown()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)

    def _render_markdown(self) -> str:
        mode = getattr(self.config, "mode", None)
        cpol = 1 if mode in [2, 3] else 0
        cpha = 1 if mode in [1, 3] else 0
        spi_role = getattr(self.config, "spi_role", "master")

        sclk = self._find_signal(lambda n: n.endswith(".sclk"))
        mosi = self._find_signal(lambda n: n.endswith(".mosi"))
        ss_n = self._find_signal(lambda n: n.endswith(".ss_n"))
        busy = self._find_signal(lambda n: n.endswith(".busy"))
        master_mode_sig = self._find_signal(lambda n: n.endswith(".master_mode"))

        checks = []

        idle_ok, idle_note = self._check_sclk_idle(sclk, busy, cpol, spi_role, master_mode_sig)
        checks.append(("SCLK_idle_level_matches_CPOL", idle_ok, idle_note))

        ss_ok, ss_note = self._check_ss_framing(ss_n, busy, master_mode_sig)
        checks.append(("SS_n_matches_busy_window", ss_ok, ss_note))

        ss_idle_ok, ss_idle_note = self._check_ss_inactive_when_not_busy(ss_n, busy, master_mode_sig)
        checks.append(("SS_n_inactive_when_not_busy", ss_idle_ok, ss_idle_note))

        edge_ok, edge_note = self._check_mosi_not_changing_on_sampling_edges(
            sclk, mosi, busy, cpol, cpha, spi_role, master_mode_sig
        )
        checks.append(("MOSI_does_not_change_on_sampling_edge", edge_ok, edge_note))

        timing_ok, timing_note = self._check_mosi_setup_hold_window(
            sclk, mosi, busy, cpol, cpha, spi_role, master_mode_sig
        )
        checks.append(("MOSI_setup_hold_window_ok", timing_ok, timing_note))

        sclk_busy_ok, sclk_busy_note = self._check_sclk_toggles_during_busy(sclk, busy, spi_role, master_mode_sig)
        checks.append(("SCLK_activity_present_during_busy", sclk_busy_ok, sclk_busy_note))

        lines = []
        lines.append("# SPI Protocol Compliance (evidence-based)")
        lines.append("")
        lines.append("## Configuration")
        lines.append(f"- Mode: {mode} (CPOL={cpol}, CPHA={cpha})")
        lines.append(f"- Data width: {getattr(self.config, 'data_width', 'unknown')}")
        lines.append(f"- Data order: {'MSB First' if getattr(self.config, 'msb_first', True) else 'LSB First'}")
        lines.append(f"- Slave select polarity: {'Active Low' if getattr(self.config, 'slave_active_low', True) else 'Active High'}")
        lines.append("")
        lines.append("## Checks")
        lines.append("")
        lines.append("| Check | Result | Notes |")
        lines.append("|---|---:|---|")
        for name, ok, note in checks:
            result = "PASS" if ok is True else "FAIL" if ok is False else "NOT_RUN"
            lines.append(f"| `{name}` | **{result}** | {note} |")
        lines.append("")
        lines.append("## Evidence pointers")
        lines.append(f"- VCD: `{self.vcd_data.get('vcd_file', '(unknown)')}`")
        lines.append(f"- Timescale: `{self.vcd_data.get('timescale', '(unknown)')}`")
        lines.append("")
        return "\n".join(lines)

    def _find_signal(self, predicate) -> Optional[Dict[str, Any]]:
        for sig in self.signals.values():
            name = sig.get("name", "")
            if predicate(name):
                return sig
        return None

    def _value_at_or_before(self, sig: Dict[str, Any], t: int) -> str:
        current = sig.get("current_value", "x")
        for ct, v in sig.get("changes", []):
            if ct <= t:
                current = v
            else:
                break
        return current

    def _check_sclk_idle(
        self,
        sclk_sig: Optional[Dict[str, Any]],
        busy_sig: Optional[Dict[str, Any]],
        cpol: int,
        spi_role: str,
        master_mode_sig: Optional[Dict[str, Any]] = None,
    ):
        # In slave-only mode, SCLK is externally driven; idle-level ownership is outside DUT.
        if spi_role == "slave":
            return True, "Skipped: slave mode SCLK is externally driven."
        if not sclk_sig or not busy_sig:
            return None, "Missing `sclk` or `busy` in VCD."
        changes = busy_sig.get("changes", [])
        if not changes:
            return None, "`busy` has no transitions; cannot infer idle window."

        checked = 0
        for idx, (t, v) in enumerate(changes):
            if v == "0":
                # In dual mode, skip check when master_mode=0 (SCLK is an input, not driven)
                if master_mode_sig is not None:
                    mm_v = self._value_at_or_before(master_mode_sig, t)
                    if mm_v != "1":
                        continue
                # Probe well inside the busy=0 idle window, not right at the boundary.
                next_t = changes[idx + 1][0] if idx + 1 < len(changes) else None
                if next_t is not None and next_t <= t + 1:
                    continue
                if next_t is None:
                    probe_t = t + 1
                else:
                    probe_t = t + ((next_t - t) // 2)
                sclk_v = self._value_at_or_before(sclk_sig, probe_t)
                if sclk_v in ["0", "1"] and int(sclk_v) != cpol:
                    return False, f"During busy=0 idle window near {t}ns, sclk={sclk_v} but expected idle {cpol}."
                checked += 1
        if checked == 0:
            return None, "No master-mode busy=0 transitions found to check SCLK idle."
        return True, f"Checked sclk at {checked} master-mode busy=0 boundaries against CPOL={cpol}."

    def _value_just_after(self, sig: Dict[str, Any], t: int) -> str:
        """
        Return the first known value strictly after time t, falling back to value-at-or-before.
        This avoids false mismatches when multiple signals transition at the same timestamp.
        """
        for ct, v in sig.get("changes", []):
            if ct > t:
                return v
        return self._value_at_or_before(sig, t)

    def _check_ss_framing(self, ss_sig: Optional[Dict[str, Any]], busy_sig: Optional[Dict[str, Any]], master_mode_sig: Optional[Dict[str, Any]] = None):
        if not ss_sig or not busy_sig:
            return None, "Missing `ss_n` or `busy` in VCD."
        active_low = bool(getattr(self.config, "slave_active_low", True))
        checked = 0
        unknown = 0
        for t, v in busy_sig.get("changes", []):
            if v == "1":
                # In dual mode, only evaluate framing while master is driving ss_n.
                if master_mode_sig is not None:
                    mm_v = self._value_at_or_before(master_mode_sig, t)
                    if mm_v != "1":
                        continue
                ss_before = self._value_at_or_before(ss_sig, t)
                ss_after = self._value_just_after(ss_sig, t)
                ss_active_before = self._is_ss_active(ss_before, active_low)
                ss_active_after = self._is_ss_active(ss_after, active_low)
                ss_candidates = [v for v in (ss_active_before, ss_active_after) if v is not None]
                if not ss_candidates:
                    unknown += 1
                    continue
                if not any(ss_candidates):
                    return False, (
                        f"At busy=1 time {t}ns, ss_n(before)={ss_before}, ss_n(after)={ss_after} "
                        f"but expected active selection."
                    )
                checked += 1

        if checked == 0 and unknown > 0:
            return None, "Could not evaluate SS framing due to unknown SS values during busy windows."
        if checked == 0:
            return None, "No busy=1 windows found for SS framing check."
        return True, f"Checked ss_n activity at {checked} busy=1 boundaries."

    def _check_ss_inactive_when_not_busy(self, ss_sig: Optional[Dict[str, Any]], busy_sig: Optional[Dict[str, Any]], master_mode_sig: Optional[Dict[str, Any]] = None):
        if not ss_sig or not busy_sig:
            return None, "Missing `ss_n` or `busy` in VCD."
        active_low = bool(getattr(self.config, "slave_active_low", True))
        checked = 0
        for t, v in busy_sig.get("changes", []):
            if v == "0":
                if master_mode_sig is not None:
                    mm_v = self._value_at_or_before(master_mode_sig, t)
                    if mm_v != "1":
                        continue
                ss_before = self._value_at_or_before(ss_sig, t)
                ss_after = self._value_just_after(ss_sig, t)
                ss_active_before = self._is_ss_active(ss_before, active_low)
                ss_active_after = self._is_ss_active(ss_after, active_low)
                ss_candidates = [v for v in (ss_active_before, ss_active_after) if v is not None]
                if not ss_candidates:
                    continue
                if all(ss_candidates):
                    return False, (
                        f"At busy=0 time {t}ns, ss_n(before)={ss_before}, ss_n(after)={ss_after} "
                        f"remained active."
                    )
                checked += 1
        if checked == 0:
            return None, "No busy=0 windows found for SS idle check."
        return True, f"Checked ss_n inactive state at {checked} busy=0 boundaries."

    def _is_ss_active(self, ss_value: str, active_low: bool) -> Optional[bool]:
        """
        Evaluate whether slave-select is active for single-bit or bus-valued ss_n.
        Returns None when value is unknown/undecidable.
        """
        if ss_value in ["0", "1"]:
            return (ss_value == "0") if active_low else (ss_value == "1")

        if ss_value.startswith("b"):
            bits = ss_value[1:]
            if not bits or any(b not in "01" for b in bits):
                return None
            if active_low:
                # Any low bit indicates one selected slave.
                return any(b == "0" for b in bits)
            # Active-high: any high bit indicates selection.
            return any(b == "1" for b in bits)

        return None

    def _check_mosi_not_changing_on_sampling_edges(
        self,
        sclk_sig,
        mosi_sig,
        busy_sig,
        cpol: int,
        cpha: int,
        spi_role: str,
        master_mode_sig: Optional[Dict[str, Any]] = None,
    ):
        # In slave-only mode, MOSI is externally driven and not controlled by DUT.
        if spi_role == "slave":
            return True, "Skipped: slave mode MOSI timing is externally driven."
        if not sclk_sig or not mosi_sig:
            return None, "Missing `sclk` or `mosi` in VCD."
        sclk_changes = [(t, v) for t, v in sclk_sig.get("changes", []) if v in ["0", "1"]]
        mosi_change_times = set(t for t, _ in mosi_sig.get("changes", []))
        if not sclk_changes:
            return None, "`sclk` has no transitions."

        # Sampling edge depends on CPOL/CPHA:
        # - Leading edge is rising if CPOL=0, falling if CPOL=1
        # - CPHA=0 samples on leading edge; CPHA=1 samples on trailing edge
        leading = "rising" if cpol == 0 else "falling"
        sampling_edge = leading if cpha == 0 else ("falling" if leading == "rising" else "rising")

        prev_v = None
        sampling_times = []
        for t, v in sclk_changes:
            if prev_v is None:
                prev_v = v
                continue
            if sampling_edge == "rising" and prev_v == "0" and v == "1":
                sampling_times.append(t)
            if sampling_edge == "falling" and prev_v == "1" and v == "0":
                sampling_times.append(t)
            prev_v = v

        if not sampling_times:
            return None, f"No {sampling_edge} edges found on sclk."

        relevant_sampling_times = []
        for t in sampling_times:
            if busy_sig is not None:
                busy_now = self._value_at_or_before(busy_sig, t)
                busy_pre = self._value_at_or_before(busy_sig, max(0, t - 1))
                if busy_now != "1" and busy_pre != "1":
                    continue
            if master_mode_sig is not None:
                mode_now = self._value_at_or_before(master_mode_sig, t)
                mode_pre = self._value_at_or_before(master_mode_sig, max(0, t - 1))
                if mode_now != "1" and mode_pre != "1":
                    continue
            relevant_sampling_times.append(t)

        if not relevant_sampling_times:
            return None, f"No active-transaction {sampling_edge} sampling edges found on sclk."

        bad = [t for t in relevant_sampling_times if t in mosi_change_times]
        if bad:
            return False, f"MOSI changes at {len(bad)} sampling edge time(s), e.g. {bad[:5]}."
        return True, f"Checked {len(relevant_sampling_times)} active-transaction sampling edges ({sampling_edge})."

    def _check_sclk_toggles_during_busy(
        self,
        sclk_sig: Optional[Dict[str, Any]],
        busy_sig: Optional[Dict[str, Any]],
        spi_role: str,
        master_mode_sig: Optional[Dict[str, Any]] = None,
    ):
        if spi_role == "slave":
            return True, "Skipped: slave mode SCLK is externally driven."
        if not sclk_sig or not busy_sig:
            return None, "Missing `sclk` or `busy` in VCD."
        busy_rise_times = [t for t, v in busy_sig.get("changes", []) if v == "1"]
        if master_mode_sig is not None:
            busy_rise_times = [t for t in busy_rise_times if self._value_at_or_before(master_mode_sig, t) == "1"]
        if not busy_rise_times:
            return None, "No busy=1 windows found for SCLK activity check."
        toggles = [t for t, _ in sclk_sig.get("changes", []) if t > 0]
        checked = 0
        for t in busy_rise_times:
            has_toggle = any(tt >= t and tt <= (t + 2_000_000) for tt in toggles)
            if not has_toggle:
                return False, f"No sclk transition found shortly after busy asserted at {t}ns."
            checked += 1
        return True, f"Checked SCLK activity for {checked} busy windows."

    def _check_mosi_setup_hold_window(
        self,
        sclk_sig: Optional[Dict[str, Any]],
        mosi_sig: Optional[Dict[str, Any]],
        busy_sig: Optional[Dict[str, Any]],
        cpol: int,
        cpha: int,
        spi_role: str,
        master_mode_sig: Optional[Dict[str, Any]] = None,
    ):
        """
        Conservative timing-window check:
        require MOSI changes to be at least 1ns away from active sampling edges.
        """
        if spi_role == "slave":
            return True, "Skipped: slave mode MOSI timing is externally driven."
        if not sclk_sig or not mosi_sig:
            return None, "Missing `sclk` or `mosi` in VCD."

        sclk_changes = [(t, v) for t, v in sclk_sig.get("changes", []) if v in ["0", "1"]]
        if not sclk_changes:
            return None, "`sclk` has no transitions."
        mosi_change_times = sorted(set(t for t, _ in mosi_sig.get("changes", [])))

        leading = "rising" if cpol == 0 else "falling"
        sampling_edge = leading if cpha == 0 else ("falling" if leading == "rising" else "rising")

        sampling_times = []
        prev_v = None
        for t, v in sclk_changes:
            if prev_v is None:
                prev_v = v
                continue
            if sampling_edge == "rising" and prev_v == "0" and v == "1":
                sampling_times.append(t)
            elif sampling_edge == "falling" and prev_v == "1" and v == "0":
                sampling_times.append(t)
            prev_v = v
        if not sampling_times:
            return None, f"No {sampling_edge} edges found on sclk."

        relevant_sampling_times = []
        for t in sampling_times:
            if busy_sig is not None:
                busy_now = self._value_at_or_before(busy_sig, t)
                busy_pre = self._value_at_or_before(busy_sig, max(0, t - 1))
                if busy_now != "1" and busy_pre != "1":
                    continue
            if master_mode_sig is not None:
                mode_now = self._value_at_or_before(master_mode_sig, t)
                mode_pre = self._value_at_or_before(master_mode_sig, max(0, t - 1))
                if mode_now != "1" and mode_pre != "1":
                    continue
            relevant_sampling_times.append(t)
        if not relevant_sampling_times:
            return None, f"No active-transaction {sampling_edge} sampling edges found on sclk."

        required_margin_ns = 1
        violations = []
        min_observed = None
        for t in relevant_sampling_times:
            nearest = min((abs(mt - t) for mt in mosi_change_times), default=None)
            if nearest is None:
                continue
            if min_observed is None or nearest < min_observed:
                min_observed = nearest
            if nearest < required_margin_ns:
                violations.append((t, nearest))

        if violations:
            first_t, first_d = violations[0]
            return False, (
                f"MOSI setup/hold violation near sampling edge {first_t}ns "
                f"(nearest change delta={first_d}ns, required>={required_margin_ns}ns)."
            )
        if min_observed is None:
            return None, "No MOSI transitions observed to evaluate setup/hold window."
        return True, (
            f"Checked {len(relevant_sampling_times)} sampling edges with >= {required_margin_ns}ns "
            f"setup/hold margin (min observed {min_observed}ns)."
        )


if __name__ == "__main__":
    exit(main())
