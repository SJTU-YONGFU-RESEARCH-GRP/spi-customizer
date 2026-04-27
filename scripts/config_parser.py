#!/usr/bin/env python3
"""
SPI Configuration Parser
Extracts SPI parameters from GitHub issue text and validates them.
"""

import re
import json
import sys
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class SPIConfig:
    """SPI Configuration parameters"""
    issue_number: int
    mode: int
    data_width: int
    num_slaves: int = 1
    selected_slave: int = 0
    slave_active_low: bool = True
    msb_first: bool = True
    interrupts: bool = False
    fifo_buffers: bool = False
    dma_support: bool = False
    multi_master: bool = False
    test_duration: str = "standard"
    clock_jitter_test: bool = False
    clock_frequency: float = 25.0
    waveform_capture: bool = True

    # New enhanced features
    spi_role: str = "master"  # master, slave, dual
    default_data_enabled: bool = False
    default_data_pattern: str = "a5a5"  # a5a5, ffff, 0000, 5555, custom
    default_data_value: str = "A5A5"  # Custom hex value
    clock_divider: int = 2  # System clock divider for SCLK
    fifo_depth: int = 16  # FIFO buffer depth
    max_slaves: int = 8  # Maximum slaves supported
    custom_features: Dict[str, Any] = None  # For future extensions
    email: str = ""
    github_username: str = ""


class SPIConfigParser:
    """Parses GitHub issue text to extract SPI configuration"""

    def __init__(self):
        self.patterns = {
            'mode': r'(?:SPI Mode|Mode)[^0-9]*(\d)',
            'data_width': r'(?:Data Width|Width)[^0-9]*(\d+)',
            'num_slaves': r'(?:Number of Slaves|Slaves)[^0-9]*(\d+)',
            'selected_slave': r'(?:Selected Slave Index|Selected Slave)[^0-9]*(\d+)',
            'clock_freq': r'(?:Clock Frequency|Frequency)[^0-9]*(\d+(?:\.\d+)?)',
            'slave_active': r'\[[^\]]*\]\s*Active (Low|High)',
            'data_order': r'\[[^\]]*\]\s*(MSB|LSB) First',
            'features': r'Special Features([\s\S]*?)(?=###|\n\n|\Z)',
            'test_duration': r'(?:Test Duration|Testing Requirements)[^:]*:?\s*(Brief|Standard|Comprehensive)',
            'clock_jitter': r'Clock Jitter Testing[^:]*:?\s*(Yes|No)',
            'waveform': r'Waveform Capture[^:]*:?\s*(Yes|No)',

            # New enhanced features
            # Matches both "SPI Role: Master" and "**SPI Role**: Master (default)" and section format
            'spi_role': r'SPI Role[^a-zA-Z\n]*(?:\n\s*)*(Master|Slave|Dual)',
            'default_data': r'Default Data[^:]*:?\s*(Enabled|Disabled)',
            'data_pattern': r'Data Pattern[^:]*:?\s*(A5A5|FFFF|0000|5555|Custom)',
            'custom_data': r'Custom Data Value[^:]*:?\s*([0-9A-Fa-f]+)',
            'clock_divider': r'\*\*Clock Divider\*\*:\s*(\d+)',
            'fifo_depth': r'\*\*FIFO Depth\*\*:\s*(\d+)',
            'max_slaves': r'\*\*Maximum Slaves\*\*:\s*(\d+)'
        }
        self.form_labels = {
            'mode': ['SPI Mode'],
            'data_width': ['Data Width'],
            'num_slaves': ['Number of Slaves'],
            'selected_slave': ['Selected Slave Index', 'Selected Slave'],
            'slave_select': ['Slave Select Behavior', 'Slave Select'],
            'data_order': ['Data Order'],
            'spi_role': ['SPI Role'],
            'test_duration': ['Testing Requirements', 'Test Duration'],
            'default_data': ['Default Data'],
            'data_pattern': ['Data Pattern', 'Default Data Pattern'],
            'custom_data': ['Custom Data Value', 'Custom Data Value (Hex)'],
            'clock_divider': ['Clock Divider'],
            'fifo_depth': ['FIFO Depth'],
            'max_slaves': ['Maximum Slaves'],
            'intent': ['Design intent'],
            'transaction_examples': ['Transaction examples (expected)'],
            'acceptance': ['Acceptance criteria (what must be proven)'],
            'what_to_verify': ['What must be verified'],
            'symptom': ['Symptom (what went wrong)'],
            'expected_vs_observed': ['Expected vs observed'],
            'reference_issue': ['Reference issue number (optional)', 'Reference issue number (recommended)'],
            'evidence': ['Evidence (logs / waveform pointers)'],
            'additional_notes': ['Additional Notes'],
            'email': ['Email Address'],
            'github_username': ['GitHub Username'],
        }

    def parse_issue(self, issue_body: str, issue_number: int) -> SPIConfig:
        """
        Parse GitHub issue body to extract SPI configuration

        Args:
            issue_body: The text content of the GitHub issue
            issue_number: GitHub issue number for logging

        Returns:
            SPIConfig object with parsed parameters

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        print(f"Parsing issue #{issue_number}...")

        # Extract all parameters
        params = {}

        # Required parameters
        mode_value = self._extract_form_or_regex(issue_body, 'mode', self.patterns['mode'])
        data_width_value = self._extract_form_or_regex(issue_body, 'data_width', self.patterns['data_width'])

        # Validate required parameters
        if mode_value is None:
            raise ValueError("Missing required parameter: SPI Mode")
        if data_width_value is None:
            raise ValueError("Missing required parameter: Data Width")

        try:
            params['mode'] = int(mode_value)
            params['data_width'] = int(data_width_value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid required parameters: {e}")

        # Optional parameters with defaults
        num_slaves_value = self._extract_form_or_regex(issue_body, 'num_slaves', self.patterns['num_slaves'])
        selected_slave_value = self._extract_form_or_regex(issue_body, 'selected_slave', self.patterns['selected_slave'])
        clock_freq_value = self._extract_single(issue_body, self.patterns['clock_freq'])

        try:
            params['num_slaves'] = int(num_slaves_value) if num_slaves_value else 1
            params['selected_slave'] = int(selected_slave_value) if selected_slave_value else 0
            params['clock_frequency'] = float(clock_freq_value) if clock_freq_value else 25.0
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid optional parameter values: {e}")

        # Parse slave select behavior - handle checkbox format (old) and section/inline dropdown format (new)
        slave_checkbox = re.findall(r'\[[xX]\]\s*Active\s+(Low|High)', issue_body, re.IGNORECASE)
        slave_form_value = self._extract_issue_form_value(issue_body, self.form_labels['slave_select'])
        slave_dropdown = re.search(r'(Active\s+(?:Low|High))', slave_form_value or '', re.IGNORECASE)
        if slave_checkbox:
            params['slave_active_low'] = slave_checkbox[0].lower() == 'low'
        elif slave_dropdown:
            params['slave_active_low'] = 'Low' in slave_dropdown.group(1)
        else:
            params['slave_active_low'] = True  # Default to Active Low

        # Parse data order - handle checkbox format (old) and section/inline dropdown format (new)
        order_checkbox = re.findall(r'\[[xX]\]\s*(MSB|LSB)\s+First', issue_body, re.IGNORECASE)
        order_form_value = self._extract_issue_form_value(issue_body, self.form_labels['data_order'])
        order_dropdown = re.search(r'(MSB|LSB)\s+First', order_form_value or '', re.IGNORECASE)
        if order_checkbox:
            params['msb_first'] = order_checkbox[0].upper() == 'MSB'
        elif order_dropdown:
            params['msb_first'] = order_dropdown.group(1).upper() == 'MSB'
        else:
            params['msb_first'] = True  # Default to MSB First

        # Parse SPI role - for dropdown, extract the selected value
        params['spi_role'] = self._extract_form_or_regex(issue_body, 'spi_role', self.patterns['spi_role']) or 'master'

        # Normalize SPI role to canonical form
        role_lower = params['spi_role'].lower()
        if 'dual' in role_lower:
            params['spi_role'] = 'dual'
        elif 'slave' in role_lower and 'master' not in role_lower:
            params['spi_role'] = 'slave'
        elif 'master' in role_lower:
            params['spi_role'] = 'master'
        else:
            params['spi_role'] = 'master'

        # Feature flags - check for checked checkboxes
        interrupt_matches = re.findall(r'(\[[^\]]*\]\s*Interrupt Support)', issue_body, re.IGNORECASE | re.MULTILINE)
        params['interrupts'] = len([m for m in interrupt_matches if '[x]' in m or '[X]' in m]) > 0

        fifo_matches = re.findall(r'(\[[^\]]*\]\s*FIFO Buffers)', issue_body, re.IGNORECASE | re.MULTILINE)
        params['fifo_buffers'] = len([m for m in fifo_matches if '[x]' in m or '[X]' in m]) > 0

        dma_matches = re.findall(r'(\[[^\]]*\]\s*DMA Support)', issue_body, re.IGNORECASE | re.MULTILINE)
        params['dma_support'] = len([m for m in dma_matches if '[x]' in m or '[X]' in m]) > 0

        multi_master_matches = re.findall(r'(\[[^\]]*\]\s*Multi-master Support)', issue_body, re.IGNORECASE | re.MULTILINE)
        params['multi_master'] = len([m for m in multi_master_matches if '[x]' in m or '[X]' in m]) > 0

        # Test configuration
        params['test_duration'] = self._extract_form_or_regex(issue_body, 'test_duration', self.patterns['test_duration']) or 'standard'

        # Parse testing options - find checked checkboxes
        clock_jitter_matches = re.findall(r'(\[[^\]]*\]\s*Clock Jitter Testing)', issue_body, re.IGNORECASE | re.MULTILINE)
        params['clock_jitter_test'] = len([m for m in clock_jitter_matches if '[x]' in m or '[X]' in m]) > 0

        waveform_matches = re.findall(r'(\[[^\]]*\]\s*Waveform Capture)', issue_body, re.IGNORECASE | re.MULTILINE)
        params['waveform_capture'] = len([m for m in waveform_matches if '[x]' in m or '[X]' in m]) > 0

        # Enhanced features
        default_data_val = self._extract_form_or_regex(issue_body, 'default_data', self.patterns['default_data']) or 'Disabled'
        params['default_data_enabled'] = 'enabled' in default_data_val.lower()
        raw_pattern = self._extract_form_or_regex(issue_body, 'data_pattern', self.patterns['data_pattern']) or 'a5a5'
        params['default_data_pattern'] = self._normalize_data_pattern(raw_pattern)
        params['default_data_value'] = self._extract_form_or_regex(issue_body, 'custom_data', self.patterns['custom_data']) or 'A5A5'

        # Advanced configuration
        clock_div_value = self._extract_form_or_regex(issue_body, 'clock_divider', self.patterns['clock_divider'])
        fifo_depth_value = self._extract_form_or_regex(issue_body, 'fifo_depth', self.patterns['fifo_depth'])
        max_slaves_value = self._extract_form_or_regex(issue_body, 'max_slaves', self.patterns['max_slaves'])

        # Clock divider with validation
        clock_divider = 2  # Default value
        if clock_div_value:
            try:
                value = int(clock_div_value)
                if 1 <= value <= 1024:
                    clock_divider = value
                else:
                    print(f"⚠️ Clock divider {value} out of range (1-1024), using default 2")
            except ValueError:
                print(f"⚠️ Invalid clock divider value: '{clock_div_value}', using default 2")
        params['clock_divider'] = clock_divider

        # FIFO depth with validation
        fifo_depth = 16  # Default value
        if fifo_depth_value:
            try:
                value = int(fifo_depth_value)
                if 2 <= value <= 1024:
                    fifo_depth = value
                else:
                    print(f"⚠️ FIFO depth {value} out of range (2-1024), using default 16")
            except ValueError:
                print(f"⚠️ Invalid FIFO depth value: '{fifo_depth_value}', using default 16")
        params['fifo_depth'] = fifo_depth

        # Maximum slaves with validation
        max_slaves = 8  # Default value
        if max_slaves_value:
            try:
                value = int(max_slaves_value)
                if 1 <= value <= 32:
                    max_slaves = value
                else:
                    print(f"⚠️ Maximum slaves {value} out of range (1-32), using default 8")
            except ValueError:
                print(f"⚠️ Invalid maximum slaves value: '{max_slaves_value}', using default 8")
        params['max_slaves'] = max_slaves

        params['email'] = self._extract_issue_form_value(issue_body, self.form_labels['email']) or ""
        params['github_username'] = self._extract_issue_form_value(issue_body, self.form_labels['github_username']) or ""
        params['custom_features'] = {
            'intent': self._extract_issue_form_value(issue_body, self.form_labels['intent']) or "",
            'transaction_examples': self._extract_issue_form_value(issue_body, self.form_labels['transaction_examples']) or "",
            'acceptance_criteria': self._extract_issue_form_value(issue_body, self.form_labels['acceptance']) or "",
            'what_to_verify': self._extract_issue_form_value(issue_body, self.form_labels['what_to_verify']) or "",
            'symptom': self._extract_issue_form_value(issue_body, self.form_labels['symptom']) or "",
            'expected_vs_observed': self._extract_issue_form_value(issue_body, self.form_labels['expected_vs_observed']) or "",
            'reference_issue': self._extract_issue_form_value(issue_body, self.form_labels['reference_issue']) or "",
            'evidence': self._extract_issue_form_value(issue_body, self.form_labels['evidence']) or "",
            'additional_notes': self._extract_issue_form_value(issue_body, self.form_labels['additional_notes']) or "",
        }

        # Validate configuration
        self._validate_config(params)

        config = SPIConfig(issue_number=issue_number, **params)
        print(f"✅ Successfully parsed configuration: Mode {config.mode}, {config.data_width}-bit")
        return config

    def _extract_single(self, text: str, pattern: str) -> Optional[str]:
        """Extract first match from text using regex pattern"""
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else None

    def _extract_issue_form_value(self, text: str, labels: List[str]) -> Optional[str]:
        """
        Extract value from GitHub issue form markdown blocks:
        ### <Label>
        <value lines>
        """
        for label in labels:
            pattern = rf'^###\s*{re.escape(label)}\s*$([\s\S]*?)(?=^###\s|\Z)'
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if not match:
                continue
            value = match.group(1).strip()
            if not value:
                continue
            # Normalize common GH empty placeholders.
            if value in ['_No response_', 'No response', '_']:
                return ""
            return value
        return None

    def _extract_form_or_regex(self, text: str, form_key: str, regex_pattern: str) -> Optional[str]:
        form_value = self._extract_issue_form_value(text, self.form_labels.get(form_key, []))
        if form_value:
            return form_value.strip()
        return self._extract_single(text, regex_pattern)

    def _normalize_data_pattern(self, raw: str) -> str:
        """
        Normalize issue-form dropdown text to canonical pattern tokens.
        Examples:
          "FFFF (all ones)" -> "ffff"
          "A5A5 (alternating pattern)" -> "a5a5"
        """
        value = (raw or "").strip().lower()
        value = re.sub(r"\s*\(.*\)\s*$", "", value)
        aliases = {
            "a5a5": "a5a5",
            "ffff": "ffff",
            "0000": "0000",
            "5555": "5555",
            "custom": "custom",
        }
        return aliases.get(value, value)

    def _validate_config(self, params: Dict[str, Any]) -> None:
        """Validate the parsed configuration parameters"""

        # Validate SPI mode
        if params['mode'] not in [0, 1, 2, 3]:
            raise ValueError(f"Invalid SPI mode: {params['mode']}. Must be 0, 1, 2, or 3.")

        # Validate data width
        if params['data_width'] not in [8, 16, 32] and not (1 <= params['data_width'] <= 64):
            raise ValueError(f"Data width {params['data_width']} bits is not supported (1-64 bits or standard 8/16/32)")

        # Validate number of slaves
        if not (1 <= params['num_slaves'] <= 32):
            raise ValueError(f"Number of slaves {params['num_slaves']} is out of range (1-32)")

        # Validate selected slave index
        if not (0 <= params['selected_slave'] < params['num_slaves']):
            raise ValueError(
                f"Selected slave index {params['selected_slave']} out of range for num_slaves={params['num_slaves']}"
            )

        # Validate test duration
        if params['test_duration'].lower() not in ['brief', 'standard', 'comprehensive']:
            raise ValueError(f"Invalid test duration: {params['test_duration']}")

        # Validate SPI role
        if params['spi_role'].lower() not in ['master', 'slave', 'dual']:
            raise ValueError(f"Invalid SPI role: {params['spi_role']}")

        # Validate data pattern
        valid_patterns = ['a5a5', 'ffff', '0000', '5555', 'custom']
        if params['default_data_pattern'].lower() not in valid_patterns:
            raise ValueError(f"Invalid data pattern: {params['default_data_pattern']}")

        # Validate custom data value if pattern is custom
        if params['default_data_pattern'].lower() == 'custom':
            try:
                int(params['default_data_value'], 16)
            except ValueError:
                raise ValueError(f"Invalid custom data value: {params['default_data_value']}")

        # Validate clock divider
        if params['clock_divider'] < 1 or params['clock_divider'] > 1024:
            raise ValueError(f"Clock divider {params['clock_divider']} out of range (1-1024)")

        # Validate FIFO depth
        if params['fifo_depth'] < 2 or params['fifo_depth'] > 1024:
            raise ValueError(f"FIFO depth {params['fifo_depth']} out of range (2-1024)")

        # Validate max slaves
        if params['max_slaves'] < 1 or params['max_slaves'] > 32:
            raise ValueError(f"Max slaves {params['max_slaves']} out of range (1-32)")
        if params['num_slaves'] > params['max_slaves']:
            raise ValueError(
                f"Number of slaves {params['num_slaves']} exceeds max_slaves {params['max_slaves']}"
            )


def main():
    """Main function for testing the parser"""
    if len(sys.argv) != 2:
        print("Usage: python config_parser.py <issue_number>")
        sys.exit(1)
    issue_number = int(sys.argv[1])

    # Sample issue text for testing
    sample_issue = """
    ## SPI Configuration Request

    ### Basic Configuration
    - **SPI Mode**: 0
    - **Data Width**: 16

    ### Advanced Configuration
    - **Number of Slaves**: 2
    - **Slave Select Behavior**:
      - [x] Active Low
    - **Data Order**:
      - [x] MSB First
    - **Special Features**:
      - [x] Interrupt Support
      - [ ] FIFO Buffers
      - [ ] DMA Support
      - [ ] Multi-master Support

    ### Testing Requirements
    - **Test Duration**: Standard
    - **Clock Jitter Testing**: Yes
    - **Waveform Capture**: Yes
    """

    try:
        parser = SPIConfigParser()
        config = parser.parse_issue(sample_issue, issue_number)

        # Create issue-specific results directory
        issue_dir = f'results/issue-{issue_number}'
        os.makedirs(issue_dir, exist_ok=True)

        # Save configuration to JSON
        config_file = os.path.join(issue_dir, 'spi_config.json')
        with open(config_file, 'w') as f:
            json.dump({
                'issue_number': issue_number,
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
                'clock_jitter_test': config.clock_jitter_test,
                'clock_frequency': config.clock_frequency,
                'waveform_capture': config.waveform_capture
            }, f, indent=2)

        print(f"✅ Configuration saved to {config_file}")

    except Exception as e:
        print(f"❌ Error parsing configuration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
