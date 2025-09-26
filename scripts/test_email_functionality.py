#!/usr/bin/env python3
"""
Email Functionality Test Script
Tests the complete email workflow locally without GitHub
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config_parser import SPIConfigParser
from verilog_generator import VerilogGenerator
from email_sender import EmailSender

def create_test_issue_content(email_address="yongfu.li@sjtu.edu.cn"):
    """Create test issue content with specified email"""
    return f"""
# Test SPI Configuration

This is a test form to verify that GitHub issue forms are working correctly.

## SPI Mode
0

## Data Width
8

## Email
{email_address}
"""

def test_config_parsing():
    """Test configuration parsing"""
    print("🔍 Testing configuration parsing...")

    issue_content = create_test_issue_content()
    parser = SPIConfigParser()
    config = parser.parse_issue(issue_content, 999)

    print(f"   ✅ Mode: {config.mode}")
    print(f"   ✅ Data Width: {config.data_width}")
    print(f"   ✅ Email: {config.email}")
    print(f"   ✅ GitHub Username: {config.github_username}")

    return config

def test_verilog_generation(config):
    """Test Verilog file generation"""
    print("🔧 Testing Verilog generation...")

    generator = VerilogGenerator()
    core_file = generator.save_verilog_file(config)
    tb_file = generator.save_testbench(config)

    print(f"   ✅ Core file: {os.path.basename(core_file)}")
    print(f"   ✅ Testbench: {os.path.basename(tb_file)}")

    return core_file, tb_file

def test_email_dry_run(config, attachments=None):
    """Test email functionality (dry run)"""
    print("📧 Testing email functionality...")

    sender = EmailSender()

    # Check if SMTP credentials are configured
    if not sender.username or not sender.password:
        print("   ⚠️  SMTP credentials not configured")
        print("   📝 To enable email:")
        print("      1. Set environment variables:")
        print("         export SMTP_USERNAME='liyongfu.sg@gmail.com'")
        print("         export SMTP_PASSWORD='your_16_char_app_password'")
        print("      2. Or configure GitHub repository secrets")
        return False

    # Simulate sending email
    print(f"   📨 Would send email to: {config.email}")
    print(f"   🔧 SMTP Server: {sender.smtp_server}:{sender.smtp_port}")
    print(f"   👤 From: {sender.username}")

    if attachments:
        print(f"   📎 Attachments: {len(attachments)} files")

    return True

def test_full_workflow():
    """Test the complete workflow"""
    print("🚀 SPI Customizer Email Workflow Test")
    print("=" * 50)

    try:
        # Step 1: Parse configuration
        config = test_config_parsing()
        print()

        # Step 2: Generate files
        core_file, tb_file = test_verilog_generation(config)
        print()

        # Step 3: Test email (dry run)
        attachments = [core_file, tb_file] if os.path.exists(core_file) else []
        email_ready = test_email_dry_run(config, attachments)
        print()

        # Step 4: Summary
        print("🎯 Test Results:")
        print("=" * 30)
        print("✅ Configuration parsing: PASSED")
        print("✅ Verilog generation: PASSED")
        print(f"📧 Email functionality: {'READY' if email_ready else 'NOT CONFIGURED'}")

        if email_ready:
            print("✨ All systems operational!")
            print("🚀 Ready for GitHub deployment!")
        else:
            print("⚠️  Email needs configuration")
            print("📖 See setup instructions above")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_with_real_email():
    """Test with actual email sending (requires SMTP credentials)"""
    print("📧 Testing with REAL email sending...")

    try:
        config = test_config_parsing()
        core_file, tb_file = test_verilog_generation(config)

        # Create attachments list
        attachments = []
        for filename in ['spi_config.json', 'spi_master.v', 'spi_master_tb.v']:
            filepath = os.path.join('results', filename)
            if os.path.exists(filepath):
                attachments.append(filepath)

        # Send real email
        sender = EmailSender()
        success = sender.send_results_email(config.__dict__, attachments)

        if success:
            print("✅ Email sent successfully!")
            print(f"📨 Sent to: {config.email}")
        else:
            print("❌ Email failed to send")

        return success

    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Full workflow test (dry run)")
    print("2. Real email test (requires SMTP credentials)")

    # Check if running in automated mode (CI or script)
    if os.environ.get('CI') or len(sys.argv) > 1:
        choice = sys.argv[1] if len(sys.argv) > 1 else "1"
    else:
        try:
            choice = input("Enter choice (1 or 2): ").strip()
        except EOFError:
            choice = "1"  # Default to dry run

    if choice == "2":
        if os.environ.get('SMTP_USERNAME') and os.environ.get('SMTP_PASSWORD'):
            test_with_real_email()
        else:
            print("❌ SMTP credentials not set. Use option 1 for dry run.")
            test_full_workflow()
    else:
        test_full_workflow()
