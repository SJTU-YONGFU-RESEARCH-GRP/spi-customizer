#!/usr/bin/env python3
"""
Python-based SPI Verification
Performs basic verification of generated Verilog using Python tools
Works in venv environments without requiring system RTL tools
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

def analyze_verilog_structure(file_path: str) -> Dict[str, Any]:
    """Analyze Verilog file structure and extract key information"""

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    with open(file_path, 'r') as f:
        content = f.read()

    analysis = {
        "filename": os.path.basename(file_path),
        "size": len(content),
        "lines": len(content.splitlines()),
        "has_module": "module" in content,
        "has_parameters": "parameter" in content,
        "has_ports": "input" in content or "output" in content,
        "has_logic": "always" in content or "assign" in content,
        "spi_specific": {
            "has_sclk": "sclk" in content.lower() or "sck" in content.lower(),
            "has_mosi": "mosi" in content.lower(),
            "has_miso": "miso" in content.lower(),
            "has_ss": "ss" in content.lower() or "cs" in content.lower() or "ss_n" in content.lower(),
            "has_spi_states": any(state in content.lower() for state in ["idle", "setup", "transmit", "receive"]),
            "has_clock_divider": "clk" in content.lower() and ("counter" in content.lower() or "divider" in content.lower()),
        }
    }

    # Extract parameters
    param_matches = re.findall(r'parameter\s+(\w+)\s*=\s*([^,\n]+)', content, re.IGNORECASE | re.MULTILINE)
    analysis["parameters"] = {name: value.strip() for name, value in param_matches}

    # Extract ports
    input_matches = re.findall(r'input\s+(?:wire\s+)?(?:reg\s+)?(\w+)', content, re.IGNORECASE | re.MULTILINE)
    output_matches = re.findall(r'output\s+(?:wire\s+)?(?:reg\s+)?(\w+)', content, re.IGNORECASE | re.MULTILINE)
    analysis["ports"] = {
        "inputs": input_matches,
        "outputs": output_matches
    }

    return analysis

def verify_spi_core(verilog_file: str) -> Dict[str, Any]:
    """Verify SPI core implementation"""

    analysis = analyze_verilog_structure(verilog_file)

    if "error" in analysis:
        return analysis

    verification = {
        "file_analysis": analysis,
        "spi_verification": {},
        "issues": [],
        "recommendations": []
    }

    # SPI-specific checks
    spi_check = analysis["spi_specific"]

    # Check for required SPI signals (case-insensitive)
    required_signals = ["sclk", "mosi", "miso", "ss"]
    missing_signals = []
    for sig in required_signals:
        found = False
        for check_name in [f"has_{sig}", f"has_{sig.upper()}"]:
            if spi_check.get(check_name, False):
                found = True
                break
        if not found:
            missing_signals.append(sig)

    if missing_signals:
        verification["issues"].append(f"Missing SPI signals: {missing_signals}")
    else:
        verification["spi_verification"]["signals_complete"] = True

    # Check for SPI logic elements
    logic_checks = {
        "state_machine": spi_check["has_spi_states"],
        "clock_generation": spi_check["has_clock_divider"],
        "data_shift": "shift" in analysis.get("parameters", {})
    }

    verification["spi_verification"]["logic_elements"] = logic_checks

    # Parameter validation
    params = analysis.get("parameters", {})
    if "MODE" in params:
        mode = int(params["MODE"])
        if mode not in [0, 1, 2, 3]:
            verification["issues"].append(f"Invalid SPI mode: {mode}")

    if "DATA_WIDTH" in params:
        width = int(params["DATA_WIDTH"])
        if width < 8 or width > 64:
            verification["issues"].append(f"Unusual data width: {width} bits")


    # Generate recommendations
    if not spi_check["has_clock_divider"]:
        verification["recommendations"].append("Consider adding clock divider for SCLK generation")

    if not spi_check["has_spi_states"]:
        verification["recommendations"].append("Consider adding state machine for better SPI control")

    # Overall assessment
    issues_count = len(verification["issues"])
    if issues_count == 0:
        verification["overall"] = "PASS"
        verification["score"] = 100
    elif issues_count <= 2:
        verification["overall"] = "MINOR_ISSUES"
        verification["score"] = 75
    else:
        verification["overall"] = "MAJOR_ISSUES"
        verification["score"] = 50

    return verification

def run_python_verification(config, issue_number) -> Dict[str, Any]:
    """Run Python-based verification of generated files"""

    issue_dir = f"results/issue-{issue_number}"
    print(f"🔍 Running Python-based verification for {issue_number}")

    results = {
        "config": {
            "issue_number": config.issue_number,
            "mode": config.mode,
            "data_width": config.data_width
        },
        "files": {},
        "verification": {},
        "summary": {}
    }

    # Check each generated file
    files_to_check = [
        "spi_master_mode" + str(config.mode) + "_" + str(config.data_width) + "bit.v",
        "spi_master_tb_mode" + str(config.mode) + ".v"
    ]

    for filename in files_to_check:
        file_path = os.path.join(issue_dir, filename)
        if os.path.exists(file_path):
            print(f"   📄 Analyzing {filename}...")
            results["files"][filename] = analyze_verilog_structure(file_path)
        else:
            # Try with simple naming
            simple_filename = f"{config.issue_number}.v" if isinstance(config.issue_number, str) else filename
            file_path = os.path.join(issue_dir, simple_filename)
            if os.path.exists(file_path):
                print(f"   📄 Analyzing {simple_filename}...")
                results["files"][simple_filename] = analyze_verilog_structure(file_path)

    # Verify SPI core if found
    spi_files = [f for f in results["files"].keys() if "spi_master" in f and not f.endswith("_tb.v")]
    if spi_files:
        spi_file = os.path.join(issue_dir, spi_files[0])
        results["verification"]["spi_core"] = verify_spi_core(spi_file)
        print(f"   ✅ SPI core verification: {results['verification']['spi_core']['overall']}")
    else:
        results["verification"]["spi_core"] = {"error": "SPI core file not found"}

    # Calculate summary
    all_issues = []
    all_recommendations = []
    total_score = 0
    verified_files = 0

    for filename, analysis in results["files"].items():
        if "error" not in analysis:
            verified_files += 1
            if "spi_core" in results["verification"]:
                core_verification = results["verification"]["spi_core"]
                if "issues" in core_verification:
                    all_issues.extend(core_verification["issues"])
                if "recommendations" in core_verification:
                    all_recommendations.extend(core_verification["recommendations"])
                if "score" in core_verification:
                    total_score += core_verification["score"]

    results["summary"] = {
        "files_analyzed": len(results["files"]),
        "issues_found": len(all_issues),
        "recommendations": len(all_recommendations),
        "average_score": total_score / max(verified_files, 1),
        "verification_level": "Python-based (limited)" if verified_files > 0 else "No verification"
    }

    return results

def main():
    """Main verification function"""

    if len(sys.argv) < 2:
        print("Usage: python3 scripts/python_verification.py <issue_number>")
        print("Or run from test.py for automatic detection")
        return 1

    try:
        issue_number = sys.argv[1]
        issue_dir = f"results/issue-{issue_number}"

        if not os.path.exists(issue_dir):
            print(f"❌ Issue directory not found: {issue_dir}")
            return 1

        print("🧪 Running Python-based Verification")
        print("=" * 50)

        # Import configuration if available
        config_file = os.path.join(issue_dir, "spi_config.json")
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                print(f"✅ Configuration loaded: Mode {config_data.get('mode', '?')}, {config_data.get('data_width', '?')}-bit")
        else:
            print("⚠️  Configuration file not found - using basic verification")
            config_data = None

        # Run verification
        results = run_python_verification(config_data, issue_number)

        # Display results
        print("\\n📊 Verification Results:")
        print("=" * 30)

        if results["summary"]["files_analyzed"] > 0:
            print(f"✅ Files analyzed: {results['summary']['files_analyzed']}")
            print(f"⚠️  Issues found: {results['summary']['issues_found']}")
            print(f"💡 Recommendations: {results['summary']['recommendations']}")
            print(f"📈 Overall score: {results['summary']['average_score']:.1f}")
            print(f"🔍 Verification level: {results['summary']['verification_level']}")

            if results["summary"]["issues_found"] == 0:
                print("\\n🎉 VERIFICATION PASSED!")
                print("   ✅ Generated SPI core appears to be well-structured")
                print("   ✅ All required elements detected")
                print("   ✅ Ready for RTL simulation (with proper tools)")
            else:
                print(f"\\n⚠️  VERIFICATION COMPLETED WITH ISSUES:")
                for issue in results.get("verification", {}).get("spi_core", {}).get("issues", []):
                    print(f"   • {issue}")
        else:
            print("❌ No files found for verification")

        print("\\n💡 Next Steps:")
        print("   1. For full RTL simulation: Install iverilog/gtkwave")
        print("   2. For online verification: Upload .v files to EDA Playground")
        print("   3. For detailed analysis: Use professional EDA tools")

        return 0

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
