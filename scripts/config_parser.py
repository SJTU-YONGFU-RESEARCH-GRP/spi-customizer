#!/usr/bin/env python3
"""
SPI Configuration Parser
Extracts SPI parameters from GitHub issue text and validates them.
"""

import re
import json
import sys
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class SPIConfig:
    """SPI Configuration parameters"""
    issue_number: int
    mode: int
    data_width: int
    num_slaves: int = 1
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
    email: str = ""
    github_username: str = ""

    # New enhanced features
    spi_role: str = "master"  # master, slave, dual
    default_data_enabled: bool = False
    default_data_pattern: str = "a5a5"  # a5a5, ffff, 0000, 5555, custom
    default_data_value: str = "A5A5"  # Custom hex value
    clock_divider: int = 2  # System clock divider for SCLK
    fifo_depth: int = 16  # FIFO buffer depth
    max_slaves: int = 8  # Maximum slaves supported
    custom_features: Dict[str, Any] = None  # For future extensions


class SPIConfigParser:
    """Parses GitHub issue text to extract SPI configuration"""

    def __init__(self):
        self.patterns = {
            'mode': r'(?:SPI Mode|Mode)[^0-9]*(\d)',
            'data_width': r'(?:Data Width|Width)[^0-9]*(\d+)',
            'num_slaves': r'(?:Number of Slaves|Slaves)[^0-9]*(\d+)',
            'clock_freq': r'(?:Clock Frequency|Frequency)[^0-9]*(\d+(?:\.\d+)?)',
            'slave_active': r'\[[^\]]*\]\s*Active (Low|High)',
            'data_order': r'\[[^\]]*\]\s*(MSB|LSB) First',
            'features': r'Special Features[^:]*:([\s\S]*?)(?=###|\n\n|\Z)',
            'test_duration': r'Test Duration[^:]*:?\s*(Brief|Standard|Comprehensive)',
            'clock_jitter': r'Clock Jitter Testing[^:]*:?\s*(Yes|No)',
            'waveform': r'Waveform Capture[^:]*:?\s*(Yes|No)',
            'email': r'(?:## Email Address|Email)\s*:?\s*\n?\s*([^\n\r]+)',

            # New enhanced features
            'spi_role': r'SPI Role[^:]*:?\s*(Master|Slave|Dual)',
            'default_data': r'Default Data[^:]*:?\s*(Enabled|Disabled)',
            'data_pattern': r'Data Pattern[^:]*:?\s*(A5A5|FFFF|0000|5555|Custom)',
            'custom_data': r'Custom Data Value[^:]*:?\s*([0-9A-Fa-f]+)',
            'clock_divider': r'Clock Divider[^0-9]*(\d+)',
            'fifo_depth': r'FIFO Depth[^0-9]*(\d+)',
            'max_slaves': r'Maximum Slaves[^0-9]*(\d+)',
            'github_user': r'GitHub Username[^:]*:?\s*([^\n\r]+)'
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
        mode_value = self._extract_single(issue_body, self.patterns['mode'])
        data_width_value = self._extract_single(issue_body, self.patterns['data_width'])

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
        num_slaves_value = self._extract_single(issue_body, self.patterns['num_slaves'])
        clock_freq_value = self._extract_single(issue_body, self.patterns['clock_freq'])

        try:
            params['num_slaves'] = int(num_slaves_value) if num_slaves_value else 1
            params['clock_frequency'] = float(clock_freq_value) if clock_freq_value else 25.0
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid optional parameter values: {e}")

        # Parse slave select behavior - find the line with checked checkbox
        slave_matches = re.findall(r'(\[[^\]]*\]\s*Active (Low|High))', issue_body, re.IGNORECASE | re.MULTILINE)
        slave_checked = [full_line for full_line, value in slave_matches if '[x]' in full_line or '[X]' in full_line]
        params['slave_active_low'] = len(slave_checked) == 0 or 'Low' in slave_checked[0]  # Default to Low if none checked or Low is checked

        # Parse data order - find the line with checked checkbox
        data_order_matches = re.findall(r'(\[[^\]]*\]\s*(MSB|LSB) First)', issue_body, re.IGNORECASE | re.MULTILINE)
        data_order_checked = [full_line for full_line, value in data_order_matches if '[x]' in full_line or '[X]' in full_line]
        params['msb_first'] = len(data_order_checked) == 0 or 'MSB' in data_order_checked[0]  # Default to MSB if none checked or MSB is checked
        email_value = self._extract_single(issue_body, self.patterns['email']) or ''
        params['email'] = email_value.strip()
        params['github_username'] = self._extract_single(issue_body, self.patterns['github_user']) or ''

        # Feature flags
        features_text = self._extract_single(issue_body, self.patterns['features']) or ''
        params['interrupts'] = 'Interrupt' in features_text
        params['fifo_buffers'] = 'FIFO' in features_text
        params['dma_support'] = 'DMA' in features_text
        params['multi_master'] = 'Multi-master' in features_text

        # Test configuration
        params['test_duration'] = self._extract_single(issue_body, self.patterns['test_duration']) or 'standard'
        params['clock_jitter_test'] = 'Yes' in (self._extract_single(issue_body, self.patterns['clock_jitter']) or 'No')
        params['waveform_capture'] = 'Yes' in (self._extract_single(issue_body, self.patterns['waveform']) or 'Yes')

        # Enhanced features
        params['spi_role'] = self._extract_single(issue_body, self.patterns['spi_role']) or 'master'
        params['default_data_enabled'] = 'Enabled' in (self._extract_single(issue_body, self.patterns['default_data']) or 'Disabled')
        params['default_data_pattern'] = self._extract_single(issue_body, self.patterns['data_pattern']) or 'a5a5'
        params['default_data_value'] = self._extract_single(issue_body, self.patterns['custom_data']) or 'A5A5'

        # Advanced configuration
        clock_div_value = self._extract_single(issue_body, self.patterns['clock_divider'])
        fifo_depth_value = self._extract_single(issue_body, self.patterns['fifo_depth'])
        max_slaves_value = self._extract_single(issue_body, self.patterns['max_slaves'])

        params['clock_divider'] = int(clock_div_value) if clock_div_value else 2
        params['fifo_depth'] = int(fifo_depth_value) if fifo_depth_value else 16
        params['max_slaves'] = int(max_slaves_value) if max_slaves_value else 8

        # Validate configuration
        self._validate_config(params)

        config = SPIConfig(issue_number=issue_number, **params)
        print(f"✅ Successfully parsed configuration: Mode {config.mode}, {config.data_width}-bit")
        return config

    def _extract_single(self, text: str, pattern: str) -> Optional[str]:
        """Extract first match from text using regex pattern"""
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else None

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

        # Validate email (required for email functionality)
        if not params['email'] or '@' not in params['email']:
            raise ValueError("Valid email address is required for notification delivery")


def main():
    """Main function for testing the parser"""
    if len(sys.argv) != 2:
        print("Usage: python config_parser.py <issue_number>")
        sys.exit(1)

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

    ### Contact Information
    - **Email Address**: your-email@example.com
    - **GitHub Username**: testuser
    """

    try:
        parser = SPIConfigParser()
        config = parser.parse_issue(sample_issue, int(sys.argv[1]))

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
                'waveform_capture': config.waveform_capture,
                'email': config.email,
                'github_username': config.github_username
            }, f, indent=2)

        print(f"✅ Configuration saved to {config_file}")

    except Exception as e:
        print(f"❌ Error parsing configuration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
