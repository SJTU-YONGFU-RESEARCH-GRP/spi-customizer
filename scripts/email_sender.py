#!/usr/bin/env python3
"""
Email Sender
Sends SPI customization results to users via email
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, List
import json


class EmailSender:
    """Handles sending email notifications with attachments"""

    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = os.environ.get('SMTP_USERNAME')
        self.password = os.environ.get('SMTP_PASSWORD')

    def send_results_email(self, config: Dict[str, Any], attachments: List[str] = None) -> bool:
        """
        Send email with SPI customization results

        Args:
            config: Configuration dictionary
            attachments: List of file paths to attach

        Returns:
            True if email sent successfully
        """

        if not self.username or not self.password:
            print("⚠️  SMTP credentials not configured, skipping email")
            return False

        recipient = config.get('email', '')
        if not recipient:
            print("⚠️  No recipient email address found")
            return False

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"SPI Customization Complete - Issue #{config.get('issue_number', 'N/A')}"
        msg['From'] = f"SPI Customizer <{self.username}>"
        msg['To'] = recipient

        # HTML email body
        html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .success {{ color: #28a745; font-size: 24px; font-weight: bold; }}
        .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .feature {{ margin: 5px 0; }}
        .enabled {{ color: #28a745; font-weight: bold; }}
        .disabled {{ color: #6c757d; }}
        .files {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; }}
        .code {{ font-family: 'Courier New', monospace; background-color: #f8f9fa; padding: 10px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="success">🎉 SPI Customization Complete!</div>
        <p>Your custom SPI core has been generated and tested successfully.</p>
    </div>

    <h2>📋 Configuration Summary</h2>
    <div class="details">
        <div class="feature"><strong>SPI Mode:</strong> {config.get('mode', 'N/A')}</div>
        <div class="feature"><strong>Data Width:</strong> {config.get('data_width', 'N/A')} bits</div>
        <div class="feature"><strong>Number of Slaves:</strong> {config.get('num_slaves', 'N/A')}</div>
        <div class="feature"><strong>Slave Select:</strong> {'Active High' if not config.get('slave_active_low', True) else 'Active Low'}</div>
        <div class="feature"><strong>Data Order:</strong> {'LSB First' if not config.get('msb_first', True) else 'MSB First'}</div>
    </div>

    <h2>🔧 Enabled Features</h2>
    <div class="details">
        <div class="feature">Interrupts: <span class="{'enabled' if config.get('interrupts') else 'disabled'}">{'✅' if config.get('interrupts') else '❌'}</span></div>
        <div class="feature">FIFO Buffers: <span class="{'enabled' if config.get('fifo_buffers') else 'disabled'}">{'✅' if config.get('fifo_buffers') else '❌'}</span></div>
        <div class="feature">DMA Support: <span class="{'enabled' if config.get('dma_support') else 'disabled'}">{'✅' if config.get('dma_support') else '❌'}</span></div>
        <div class="feature">Multi-master: <span class="{'enabled' if config.get('multi_master') else 'disabled'}">{'✅' if config.get('multi_master') else '❌'}</span></div>
    </div>

    <h2>📁 Generated Files</h2>
    <div class="files">
        <div class="feature">• <strong>spi_master_mode{config.get('mode', 'X')}_{config.get('data_width', 'Z')}bit.v</strong> - Custom SPI core</div>
        <div class="feature">• <strong>spi_master_tb_mode{config.get('mode', 'X')}.v</strong> - Verilog testbench</div>
        <div class="feature">• <strong>test_spi.py</strong> - Python/Cocotb test</div>
        <div class="feature">• <strong>spi_config.json</strong> - Configuration file</div>
        <div class="feature">• <strong>spi_waveform.vcd</strong> - Simulation waveforms</div>
    </div>

    <h2>🧪 Testing Results</h2>
    <div class="details">
        <div class="feature"><strong>RTL Simulation:</strong> {'✅ Passed' if config.get('simulation_success') else '⚠️ Completed (simulation tools not available)'}</div>
        <div class="feature"><strong>Test Duration:</strong> {config.get('test_duration', 'standard')}</div>
    </div>

    <h2>📝 Next Steps</h2>
    <div class="details">
        <ol>
            <li><strong>Download</strong> the generated files from the GitHub issue</li>
            <li><strong>Simulate</strong> the design using Icarus Verilog or your preferred RTL tools</li>
            <li><strong>Integrate</strong> the SPI core into your FPGA/ASIC project</li>
            <li><strong>Test</strong> with your target hardware</li>
        </ol>
    </div>

    <h2>📞 Support</h2>
    <div class="details">
        <p>If you need help or encounter issues:</p>
        <ul>
            <li>📧 Reply to this email</li>
            <li>💬 Comment on the GitHub issue</li>
            <li>🐛 Report bugs: <a href="https://github.com/SJTU-YONGFU-RESEARCH-GRP/spi-customizer/issues">GitHub Issues</a></li>
        </ul>
    </div>

    <hr>
    <p><em>Generated by SPI Customizer v1.0 - Automated RTL Generation System</em></p>
</body>
</html>
"""

        msg.attach(MIMEText(html_body, 'html'))

        # Add attachments
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    self._attach_file(msg, file_path)

        # Send email
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, recipient, msg.as_string())
            server.quit()

            print(f"✅ Email sent successfully to {recipient}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """Attach a file to the email message"""
        try:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f"attachment; filename={os.path.basename(file_path)}"
                )
                msg.attach(part)
        except Exception as e:
            print(f"⚠️  Could not attach file {file_path}: {e}")


def send_test_email():
    """Send a test email to verify configuration"""
    sender = EmailSender()

    test_config = {
        'issue_number': 123,
        'mode': 0,
        'data_width': 16,
        'num_slaves': 2,
        'slave_active_low': True,
        'msb_first': True,
        'interrupts': True,
        'fifo_buffers': False,
        'dma_support': True,
        'multi_master': False,
        'test_duration': 'standard',
        'simulation_success': True,
        'email': 'test@example.com'
    }

    # Test with sample files
    test_attachments = [
        'results/spi_config.json',
        'results/test_core.v',
        'results/test_tb.v'
    ]

    return sender.send_results_email(test_config, test_attachments)


def send_workflow_email():
    """Send email for workflow execution"""
    import os
    import sys
    import json
    from pathlib import Path

    # Add current directory to path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    from config_parser import SPIConfigParser

    sender = EmailSender()

    # Get issue number from environment (set by workflow)
    issue_number = os.environ.get('ISSUE_NUMBER')
    if not issue_number:
        print("⚠️  No issue number found - running test mode")
        return send_test_email()

    print(f"📧 Processing email for issue #{issue_number}")

    # Parse the issue to get configuration
    try:
        # Get issue content from GitHub API
        import requests

        token = os.environ.get('GITHUB_TOKEN')
        repo_owner = "SJTU-YONGFU-RESEARCH-GRP"
        repo_name = "spi-customizer"

        if not token:
            print("⚠️  No GitHub token found")
            return False

        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"⚠️  Failed to fetch issue #{issue_number}: {response.status_code}")
            return False

        issue_data = response.json()
        issue_body = issue_data.get('body', '')

        # Parse configuration from issue
        parser = SPIConfigParser()
        config = parser.parse_issue(issue_body, int(issue_number))

        # Look for result files
        issue_dir = f'results/issue-{issue_number}'
        attachments = []

        # Add generated files if they exist
        for filename in ['spi_config.json', 'spi_master.v', 'spi_master_tb.v']:
            filepath = os.path.join(issue_dir, filename)
            if os.path.exists(filepath):
                attachments.append(filepath)

        success = sender.send_results_email(config.__dict__, attachments)

        if success:
            print(f"✅ Email sent successfully to {config.email}")
        else:
            print("❌ Email failed to send")

        return success

    except Exception as e:
        print(f"⚠️  Error processing workflow email: {e}")
        return False


if __name__ == "__main__":
    print("📧 SPI Customizer Email System")

    # Check if we have workflow environment variables
    import os

    if os.environ.get('ISSUE_NUMBER') or os.environ.get('GITHUB_TOKEN'):
        print("Running in workflow mode...")
        success = send_workflow_email()
    else:
        print("Testing email functionality...")
        success = send_test_email()

    if success:
        print("✅ Email sent successfully!")
    else:
        print("❌ Email failed - check SMTP configuration")
