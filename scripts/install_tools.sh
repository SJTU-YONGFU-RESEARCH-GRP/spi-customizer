#!/bin/bash
"""
RTL Tools Installation Script
Installs Icarus Verilog and GTKWave for SPI simulation and verification
"""

echo "🔧 Installing RTL Simulation Tools"
echo "=================================="

# Check if user has root access
if [ "$EUID" -eq 0 ]; then
    echo "✅ Running with root access"
    HAS_ROOT=true
else
    echo "⚠️  No root access detected"
    HAS_ROOT=false
fi

# Detect OS and install appropriate packages
if command -v apt-get &> /dev/null; then
    echo "📦 Detected Debian/Ubuntu-based system"
    if [ "$HAS_ROOT" = true ]; then
        echo "Installing with apt-get..."
        apt-get update
        apt-get install -y iverilog gtkwave
    else
        echo "❌ Root access required for system packages"
        echo "💡 Options for venv users:"
        echo "   1. Use Docker: docker run -it --rm -v \$(pwd):/workspace spi-tools"
        echo "   2. Ask admin to install: sudo apt-get install iverilog gtkwave"
        echo "   3. Use Python-based tools (limited functionality)"
        exit 1
    fi
elif command -v dnf &> /dev/null; then
    echo "📦 Detected Fedora/RHEL-based system"
    if [ "$HAS_ROOT" = true ]; then
        echo "Installing with dnf..."
        dnf install -y iverilog gtkwave
    else
        echo "❌ Root access required for system packages"
        echo "💡 Options for venv users:"
        echo "   1. Use Docker: docker run -it --rm -v \$(pwd):/workspace spi-tools"
        echo "   2. Ask admin to install: sudo dnf install iverilog gtkwave"
        echo "   3. Use Python-based tools (limited functionality)"
        exit 1
    fi
elif command -v yum &> /dev/null; then
    echo "📦 Detected RHEL/CentOS-based system"
    if [ "$HAS_ROOT" = true ]; then
        echo "Installing with yum..."
        yum install -y iverilog gtkwave
    else
        echo "❌ Root access required for system packages"
        echo "💡 Options for venv users:"
        echo "   1. Use Docker: docker run -it --rm -v \$(pwd):/workspace spi-tools"
        echo "   2. Ask admin to install: sudo yum install iverilog gtkwave"
        echo "   3. Use Python-based tools (limited functionality)"
        exit 1
    fi
elif command -v brew &> /dev/null; then
    echo "📦 Detected macOS with Homebrew"
    echo "Installing with brew..."
    brew install icarus-verilog gtkwave
else
    echo "❌ Unsupported system or no package manager detected"
    echo "💡 Options for venv users:"
    echo "   1. Use Docker: docker run -it --rm -v \$(pwd):/workspace spi-tools"
    echo "   2. Ask admin to install system packages"
    echo "   3. Use Python-based tools (limited functionality)"
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
elif [ "$HAS_ROOT" = false ]; then
    echo -e "\n💡 Alternative Solutions for venv users:"
    echo ""
    echo "1️⃣  Docker Solution (Recommended):"
    echo "   docker run -it --rm -v \$(pwd):/workspace ubuntu:22.04"
    echo "   cd /workspace && apt-get update && apt-get install -y iverilog gtkwave"
    echo "   python3 scripts/test.py [config]"
    echo ""
    echo "2️⃣  Python-based Verification:"
    echo "   pip install myhdl cocotb  # HDL frameworks"
    echo "   python3 scripts/python_verification.py [config]  # Python simulation"
    echo ""
    echo "3️⃣  Ask Administrator:"
    echo "   Ask your system admin to install: sudo apt-get install iverilog gtkwave"
    echo ""
    echo "4️⃣  Use Online Simulators:"
    echo "   - EDA Playground: https://www.edaplayground.com/"
    echo "   - SystemVerilog Online: https://www.systemverilog.io/"
    echo "   - Upload generated .v files and run simulation"
    echo ""
    echo "5️⃣  Local Python Verification (Limited):"
    echo "   python3 -c \"import sys; sys.path.append('.'); from scripts.test import *; print('✅ Python verification available')\""
else
    echo -e "\n❌ Some tools failed to install"
    echo "Please install manually and try again"
fi
