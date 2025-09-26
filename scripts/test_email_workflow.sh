#!/bin/bash
# Test Email Workflow Script
# Tests the complete SPI customization workflow including email sending locally

set -e  # Exit on any error

echo "🚀 SPI Customizer Email Workflow Test"
echo "====================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Configuration
ISSUE_NUMBER="999"
EMAIL_ADDRESS="yongfu.li@sjtu.edu.cn"
SPI_MODE="0"
DATA_WIDTH="8"

echo "📧 Testing email workflow for: $EMAIL_ADDRESS"
echo "🔧 Configuration: Mode $SPI_MODE, $DATA_WIDTH-bit data"
echo ""

# Step 1: Create test issue content
echo "1️⃣  Creating test issue content..."
cat > /tmp/test_issue.md << EOF
# Test SPI Configuration

This is a test form to verify that GitHub issue forms are working correctly.

## SPI Mode
$SPI_MODE

## Data Width
$DATA_WIDTH

## Email
$EMAIL_ADDRESS
EOF

echo "✅ Test issue created"

# Step 2: Set environment variables (simulate GitHub Actions)
echo "2️⃣  Setting environment variables..."
export GITHUB_TOKEN="test_token"  # Not needed for local test
export ISSUE_NUMBER="$ISSUE_NUMBER"
export SMTP_USERNAME="yongfu.unix@gmail.com"
export SMTP_PASSWORD="your_app_password_here"  # Replace with actual app password

echo "✅ Environment configured"

# Step 3: Test configuration parsing
echo "3️⃣  Testing configuration parsing..."
cd "$PROJECT_ROOT"
python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/scripts')
from config_parser import SPIConfigParser

with open('/tmp/test_issue.md', 'r') as f:
    issue_content = f.read()

parser = SPIConfigParser()
config = parser.parse_issue(issue_content, $ISSUE_NUMBER)

print(f'✅ Parsed: Mode {config.mode}, {config.data_width}-bit')
print(f'📧 Email: {config.email}')
print(f'🐙 GitHub: {config.github_username}')
"

# Step 4: Test Verilog generation
echo "4️⃣  Testing Verilog generation..."
python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/scripts')
from config_parser import SPIConfigParser
from verilog_generator import VerilogGenerator

with open('/tmp/test_issue.md', 'r') as f:
    issue_content = f.read()

parser = SPIConfigParser()
config = parser.parse_issue(issue_content, $ISSUE_NUMBER)

generator = VerilogGenerator()
core_file = generator.save_verilog_file(config)
tb_file = generator.save_testbench(config)

print(f'✅ Generated: {core_file}')
print(f'✅ Generated: {tb_file}')
"

# Step 5: Test email sending (dry run)
echo "5️⃣  Testing email sending (dry run)..."
python3 -c "
import os
from scripts.email_sender import EmailSender

# Create test config
test_config = {
    'issue_number': $ISSUE_NUMBER,
    'mode': $SPI_MODE,
    'data_width': $DATA_WIDTH,
    'email': '$EMAIL_ADDRESS',
    'num_slaves': 1,
    'slave_active_low': True,
    'msb_first': True
}

sender = EmailSender()
print('✅ Email sender initialized')
print('📧 Would send email to: ' + test_config['email'])
print('🔧 SMTP Server: ' + sender.smtp_server)
print('⚠️  Note: To actually send email, set SMTP_USERNAME and SMTP_PASSWORD')
"

# Step 6: Show generated files
echo "6️⃣  Checking generated files..."
echo "Files in results directory:"
ls -la results/ 2>/dev/null || echo "No results directory yet"

echo ""
echo "🎯 Test Summary:"
echo "==============="
echo "✅ Configuration parsing: WORKING"
echo "✅ Verilog generation: WORKING"
echo "✅ Email system: READY (needs SMTP credentials)"
echo ""
echo "📝 To test with real email:"
echo "1. Set your Gmail app password in SMTP_PASSWORD"
echo "2. Run: export SMTP_PASSWORD='your_16_char_app_password'"
echo "3. Run: python3 scripts/email_sender.py"
echo ""
echo "✨ Test completed successfully!"
