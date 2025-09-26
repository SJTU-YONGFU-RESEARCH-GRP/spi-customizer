#!/bin/bash
"""
RTL Tools Installation Script
Installs Icarus Verilog and GTKWave for SPI simulation and verification
"""

echo "🔧 Installing RTL Simulation Tools"
echo "=================================="

# Detect OS and install appropriate packages
if command -v apt-get &> /dev/null; then
    echo "📦 Detected Debian/Ubuntu-based system"
    echo "Installing with apt-get..."
    sudo apt-get update
    sudo apt-get install -y iverilog gtkwave
elif command -v dnf &> /dev/null; then
    echo "📦 Detected Fedora/RHEL-based system"
    echo "Installing with dnf..."
    sudo dnf install -y iverilog gtkwave
elif command -v yum &> /dev/null; then
    echo "📦 Detected RHEL/CentOS-based system"
    echo "Installing with yum..."
    sudo yum install -y iverilog gtkwave
elif command -v brew &> /dev/null; then
    echo "📦 Detected macOS with Homebrew"
    echo "Installing with brew..."
    brew install icarus-verilog gtkwave
else
    echo "❌ Unsupported system. Please install manually:"
    echo "   Ubuntu/Debian: sudo apt-get install iverilog gtkwave"
    echo "   Fedora/RHEL:   sudo dnf install iverilog gtkwave"
    echo "   macOS:         brew install icarus-verilog gtkwave"
    exit 1
fi

# Verify installation
echo -e "\n🔍 Verifying installation..."
echo "Checking for required tools:"

tools=("iverilog" "vvp" "gtkwave")
all_installed=true

for tool in "${tools[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo "   ✅ $tool: $(which $tool)"
    else
        echo "   ❌ $tool: Not found"
        all_installed=false
    fi
done

if [ "$all_installed" = true ]; then
    echo -e "\n🎉 All RTL tools installed successfully!"
    echo "You can now run full SPI verification with:"
    echo "   python3 scripts/test.py [configuration]"
    echo ""
    echo "The system will:"
    echo "   ✅ Generate Verilog code"
    echo "   ✅ Compile with Icarus Verilog"
    echo "   ✅ Run RTL simulation"
    echo "   ✅ Generate waveform files"
    echo "   ✅ Verify timing requirements"
else
    echo -e "\n❌ Some tools failed to install"
    echo "Please install manually and try again"
fi
