#!/usr/bin/env python3
"""
Test Email Setup
Helps verify SMTP configuration before deploying to GitHub Actions
"""

import os
import sys
from typing import Dict, Any

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from email_sender import EmailSender


def test_email_config():
    """Test email configuration with user input"""

    print("📧 Email Configuration Test")
    print("=" * 50)

    # Get SMTP credentials
    smtp_username = os.environ.get('SMTP_USERNAME') or input("Enter Gmail address: ")
    smtp_password = os.environ.get('SMTP_PASSWORD') or input("Enter Gmail App Password: ")
    test_email = input("Enter test recipient email: ")

    if not smtp_username or not smtp_password or not test_email:
        print("❌ All fields are required")
        return False

    # Set environment variables for testing
    os.environ['SMTP_USERNAME'] = smtp_username
    os.environ['SMTP_PASSWORD'] = smtp_password

    # Create test email
    sender = EmailSender()

    test_config = {
        'issue_number': 999,
        'mode': 0,
        'data_width': 8,
        'num_slaves': 1,
        'slave_active_low': True,
        'msb_first': True,
        'interrupts': False,
        'fifo_buffers': False,
        'dma_support': False,
        'multi_master': False,
        'test_duration': 'standard',
        'simulation_success': True,
        'email': test_email
    }

    print(f"📧 Attempting to send test email to {test_email}...")
    success = sender.send_results_email(test_config)

    if success:
        print("✅ Test email sent successfully!")
        print("📬 Check your inbox (and spam folder) for the test email.")
    else:
        print("❌ Test email failed.")
        print("💡 Make sure:")
        print("   - You have 2FA enabled on Gmail")
        print("   - You generated an App Password (not your regular password)")
        print("   - The App Password is correct")
        print("   - Your Gmail allows less secure apps (if not using App Password)")

    return success


if __name__ == "__main__":
    print("🧪 SPI Customizer Email Setup Test")
    print("This script helps you test your Gmail SMTP configuration.")
    print()

    success = test_email_config()

    if success:
        print("\n🎉 Email configuration is working!")
        print("You can now set SMTP_USERNAME and SMTP_PASSWORD in GitHub repository secrets.")
    else:
        print("\n⚠️  Email configuration needs fixing.")
        print("Please check the troubleshooting steps above.")
