# SPI Customizer Tools Directory

This directory contains tools and configuration files for managing Python dependencies and the virtual environment.

## 📦 Requirements Files

### `requirements.txt`
**Full requirements file** - Contains all dependencies needed for complete functionality including:
- Core dependencies (Jinja2, PyYAML, requests)
- RTL simulation and testing (cocotb, pytest)
- Data visualization (matplotlib, numpy)

**Use this for:** Complete development environment with all features.

### `requirements-minimal.txt`
**Minimal requirements file** - Contains only essential dependencies:
- Core dependencies (Jinja2, PyYAML, requests)
- RTL testing (cocotb, pytest)

**Use this for:** Minimal working environment without visualization features.

## 🔄 Updating Requirements

### Automatic Update
Use the `update_requirements.py` script to automatically analyze the current virtual environment and code dependencies:

```bash
# From the project root directory
python3 tools/update_requirements.py
```

This script will:
- ✅ Analyze current virtual environment packages
- ✅ Scan Python source files for imports
- ✅ Update both requirements files automatically
- ✅ Categorize packages by functionality
- ✅ Include version numbers from venv

### Manual Update
If you prefer manual updates:

1. **Check current venv packages:**
   ```bash
   source venv/bin/activate
   pip list --format=freeze
   ```

2. **Check code dependencies:**
   ```bash
   grep -r "^import\|^from.*import" scripts/ | grep -v "__pycache__" | grep -v "scripts\."
   ```

3. **Update requirements files** based on actual usage.

## 🛠️ Virtual Environment Setup

### Initial Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (choose one)
pip install -r tools/requirements.txt          # Full installation
pip install -r tools/requirements-minimal.txt  # Minimal installation

# Install from current venv (if venv already has packages)
pip freeze > tools/requirements.txt
```

### Environment Activation
Always activate the virtual environment before running Python scripts:

```bash
source venv/bin/activate
python3 scripts/email_sender.py
```

### Adding New Dependencies
1. Install new package: `pip install package-name`
2. Update requirements: `python3 tools/update_requirements.py`
3. Or manually add to appropriate requirements file

## 📋 Dependency Categories

### Core Dependencies (Always Required)
- **Jinja2**: Template engine for Verilog code generation
- **PyYAML**: Configuration file parsing
- **requests**: GitHub API communication

### RTL Testing (Always Required)
- **cocotb**: RTL simulation framework
- **pytest**: Testing framework

### Visualization (Optional)
- **matplotlib**: Plotting and visualization
- **numpy**: Numerical computations for matplotlib

## 🧪 Testing Setup

The requirements files are designed to work with the test scripts:

```bash
# Test with minimal setup
pip install -r tools/requirements-minimal.txt
python3 scripts/test_email_functionality.py

# Test with full visualization features
pip install -r tools/requirements.txt
python3 scripts/test_email_workflow.sh
```

## 🔍 Troubleshooting

### Missing Dependencies
If you get import errors, check:
1. Is the virtual environment activated?
2. Are all requirements installed?
3. Does the import match the installed package name?

### Version Conflicts
If you encounter version conflicts:
1. Update requirements files with current versions
2. Consider using newer package versions
3. Test compatibility with existing code

### Platform-Specific Issues
Some packages may have different requirements on different platforms:
- **Linux**: Standard requirements should work
- **macOS**: May need additional system packages
- **Windows**: May need different versions or additional tools
