#!/usr/bin/env python3
"""
Requirements Update Script
Automatically updates requirements files based on current venv and code analysis
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from typing import Set, List, Dict

def get_venv_packages() -> Dict[str, str]:
    """Get packages from current virtual environment"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=freeze"],
                              capture_output=True, text=True, check=True)
        packages = {}
        for line in result.stdout.strip().split('\n'):
            if line and '==' in line:
                package, version = line.split('==', 1)
                packages[package.lower()] = version
        return packages
    except subprocess.CalledProcessError:
        print("❌ Could not get venv packages. Is the venv activated?")
        return {}

def get_code_imports() -> Set[str]:
    """Get all external package imports from Python source files"""
    import_files = []
    for root, dirs, files in os.walk('.'):
        # Skip venv and other non-source directories
        if 'venv' in root or '__pycache__' in root or '.git' in root or 'tools' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                import_files.append(os.path.join(root, file))

    # Known internal modules (local scripts)
    internal_modules = {
        'config_parser', 'verilog_generator', 'simulator_runner', 'email_sender',
        'vcd_parser', 'python_verification', 'process_issue', 'test_full_pipeline'
    }

    # Known internal modules with scripts. prefix
    internal_modules_prefixed = {f'scripts.{mod}' for mod in internal_modules}

    external_imports = set()
    for file_path in import_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find import statements
            import_patterns = [
                r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)\b',
                r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',
                r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import'
            ]

            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    # Clean up the match (remove submodules)
                    clean_match = match.split('.')[0].lower()

                    # Skip relative imports, internal modules, and built-in modules
                    if (not match.startswith('.') and
                        clean_match not in internal_modules and
                        match not in internal_modules_prefixed and
                        clean_match not in {
                            'os', 'sys', 'json', 're', 'subprocess', 'shutil', 'pathlib',
                            'typing', 'dataclasses', 'collections', 'itertools', 'math',
                            'textwrap', 'warnings', 'inspect', 'functools', 'contextlib',
                            'platform', 'random', 'csv', 'smtplib', 'email', 'datetime'
                        }):
                        external_imports.add(clean_match)

        except Exception as e:
            print(f"⚠️  Could not parse {file_path}: {e}")

    return external_imports

def get_matplotlib_deps() -> Set[str]:
    """Get matplotlib and its dependencies"""
    matplotlib_deps = {
        'matplotlib', 'numpy', 'python-dateutil', 'six', 'contourpy', 'cycler',
        'fonttools', 'kiwisolver', 'packaging', 'pillow', 'pyparsing'
    }
    return matplotlib_deps

def update_requirements_file(file_path, packages: Set[str], versions: Dict[str, str]):
    """Update a requirements file with the specified packages"""
    lines = []

    # Add header comment
    file_path_str = str(file_path)
    if 'minimal' in file_path_str:
        lines.append("# Essential dependencies for venv environment (minimal working setup)")
    else:
        lines.append("# Core dependencies (Required for all functionality)")

    # Group packages by category
    core_packages = {'jinja2', 'pyyaml', 'requests'}
    rtl_packages = {'cocotb', 'pytest'}
    viz_packages = get_matplotlib_deps()

    # Sort packages within categories
    core_sorted = sorted(core_packages.intersection(packages))
    rtl_sorted = sorted(rtl_packages.intersection(packages))
    viz_sorted = sorted(viz_packages.intersection(packages))
    other_sorted = sorted(packages - core_packages - rtl_packages - viz_packages)

    # Add core packages
    if core_sorted:
        lines.append("")
        for pkg in core_sorted:
            version = versions.get(pkg, "")
            if version:
                lines.append(f"{pkg}>={version}")
            else:
                lines.append(f"{pkg}")

    # Add RTL packages
    if rtl_sorted:
        if not core_sorted:
            lines.append("")
        else:
            lines.append("")
        lines.append("# RTL Simulation and Testing (Required)")
        for pkg in rtl_sorted:
            version = versions.get(pkg, "")
            if version:
                lines.append(f"{pkg}>={version}")
            else:
                lines.append(f"{pkg}")

    # Add visualization packages
    if viz_sorted:
        lines.append("")
        lines.append("# Data Visualization and Analysis (Required for VCD parsing and plotting)")
        for pkg in viz_sorted:
            version = versions.get(pkg, "")
            if version:
                lines.append(f"{pkg}>={version}")
            else:
                lines.append(f"{pkg}")

    # Add other packages
    if other_sorted:
        lines.append("")
        lines.append("# Additional packages")
        for pkg in other_sorted:
            version = versions.get(pkg, "")
            if version:
                lines.append(f"{pkg}>={version}")
            else:
                lines.append(f"{pkg}")

    # Add footer comments
    lines.extend([
        "",
        "# Email functionality (Built-in with Python)",
        "# smtplib is built into Python - no installation needed",
        "",
        "# Additional utilities (Built-in with Python)",
        "# pathlib and typing are built into Python 3.8+ - no installation needed",
        "",
        "# Optional packages (commented out - install manually if needed)",
        "# cocotb-test>=0.2.0  # For enhanced pytest integration with cocotb"
    ])

    # Write to file
    with open(file_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"✅ Updated {file_path}")

def main():
    """Main function to update requirements files"""
    print("🔍 Analyzing dependencies...")

    # Get current venv packages
    venv_packages = get_venv_packages()
    if not venv_packages:
        return 1

    # Get packages used in code
    code_imports = get_code_imports()

    print(f"📦 Found {len(venv_packages)} packages in venv")
    print(f"📝 Found {len(code_imports)} external imports in code")

    # Get matplotlib dependencies (always include if matplotlib is used)
    matplotlib_deps = get_matplotlib_deps()

    # Packages to include in requirements
    required_packages = code_imports | matplotlib_deps

    print(f"📋 Will include {len(required_packages)} packages in requirements")

    # Update requirements files
    script_dir = Path(__file__).parent

    # Update full requirements
    update_requirements_file(
        script_dir / "requirements.txt",
        required_packages,
        venv_packages
    )

    # Update minimal requirements (only essential packages)
    minimal_packages = code_imports - matplotlib_deps
    update_requirements_file(
        script_dir / "requirements-minimal.txt",
        minimal_packages,
        venv_packages
    )

    print("\n🎯 Requirements files updated successfully!")
    print("\n📝 Summary:")
    print(f"   • Full requirements: {len(required_packages)} packages")
    print(f"   • Minimal requirements: {len(minimal_packages)} packages")

    if matplotlib_deps & code_imports:
        print("   • matplotlib and dependencies included in full requirements")
    else:
        print("   • matplotlib not used in code - not included in requirements")

    return 0

if __name__ == "__main__":
    exit(main())
