#!/usr/bin/env python3
"""
Parametric Coverage Test for 5-spi-spec-intent.yml Core Parameters

Systematically tests all Core parameters defined in the SPI Spec Intent issue
template (.github/ISSUE_TEMPLATE/5-spi-spec-intent.yml), covering:

  - SPI Mode        : 0, 1, 2, 3
  - Data Width      : 4, 8, 16, 32, 64
  - Number of Slaves: 1, 4, 8, 32
  - Slave Select    : Active Low / Active High
  - Data Order      : MSB First / LSB First
  - SPI Role        : Master / Slave / Dual
  - Special Features: Interrupt, FIFO, DMA, Multi-master (individually + all)
  - Test Duration   : Brief / Standard / Comprehensive
  - Testing Options : Clock Jitter / Waveform Capture

Each test case:
  1. Generates an issue body in the 5-spi-spec-intent.yml section format
  2. Parses it with SPIConfigParser and asserts the correct field values
  3. Generates RTL + testbench with VerilogGenerator and validates key
     parameter strings appear in the generated code
  4. Optionally compiles with iverilog when the tool is available
"""

import os
import re
import sys
import subprocess
import tempfile
import shutil

# Allow running from the scripts/ directory or the repo root
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
for _p in (_SCRIPT_DIR, _REPO_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from config_parser import SPIConfigParser, SPIConfig
from verilog_generator import VerilogGenerator

# ---------------------------------------------------------------------------
# Issue-body builder (mirrors the rendered output of 5-spi-spec-intent.yml)
# ---------------------------------------------------------------------------

def _build_issue(
    spi_mode: int = 0,
    data_width: int = 8,
    num_slaves: int = 1,
    slave_select: str = "Active Low (most common)",
    data_order: str = "MSB First (most common)",
    spi_role: str = "Master (default)",
    interrupt: bool = False,
    fifo: bool = False,
    dma: bool = False,
    multi_master: bool = False,
    test_duration: str = "Standard",
    clock_jitter: bool = False,
    waveform_capture: bool = True,
) -> str:
    """Build an issue body that mirrors the rendered 5-spi-spec-intent.yml form."""

    def _chk(flag: bool) -> str:
        return "x" if flag else " "

    return f"""\
## Design intent

Parametric coverage test for SPI core generation.

## Transaction examples (expected)

- TX: 0xA5 → MOSI shifts bit-by-bit, sampled on the correct edge for Mode {spi_mode}

## SPI Mode

{spi_mode}

## Data Width

{data_width}

## Number of Slaves

{num_slaves}

## Slave Select Behavior

{slave_select}

## Data Order

{data_order}

## SPI Role

{spi_role}

## Special Features

- [{_chk(interrupt)}] Interrupt Support
- [{_chk(fifo)}] FIFO Buffers
- [{_chk(dma)}] DMA Support
- [{_chk(multi_master)}] Multi-master Support

## Testing Requirements

{test_duration}

## Testing Options

- [{_chk(clock_jitter)}] Clock Jitter Testing (tests timing margins)
- [{_chk(waveform_capture)}] Waveform Capture (generates detailed timing diagrams)

## Acceptance criteria (what must be proven)

- SS_n is asserted before the first sampling edge and deasserted after the last bit
- MOSI changes only on the non-sampling edge for the chosen mode
- Bit order matches the configured data order
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PARSER = SPIConfigParser()
_GENERATOR = VerilogGenerator()
_HAS_IVERILOG = shutil.which("iverilog") is not None

_pass = 0
_fail = 0
_results: list[tuple[str, bool, str]] = []


def _record(name: str, ok: bool, detail: str = "") -> None:
    global _pass, _fail
    if ok:
        _pass += 1
        print(f"  ✅ PASS  {name}")
    else:
        _fail += 1
        print(f"  ❌ FAIL  {name}" + (f": {detail}" if detail else ""))
    _results.append((name, ok, detail))


def _run_case(
    name: str,
    issue_number: int,
    issue_body: str,
    expected: dict,
    output_dir: str,
) -> None:
    """Parse, generate, and optionally compile one test case."""
    # --- Step 1: parse ---
    try:
        config = _PARSER.parse_issue(issue_body, issue_number)
    except Exception as exc:
        _record(name, False, f"parse error: {exc}")
        return

    parse_ok = True
    parse_errors = []
    for field, want in expected.items():
        got = getattr(config, field, "<missing>")
        if got != want:
            parse_ok = False
            parse_errors.append(f"{field}: expected={want!r} got={got!r}")
    _record(f"{name}/parse", parse_ok, "; ".join(parse_errors))

    # --- Step 2: generate RTL ---
    code_dir = os.path.join(output_dir, f"issue-{issue_number}", "code")
    os.makedirs(code_dir, exist_ok=True)
    try:
        core_path = _GENERATOR.save_verilog_file(config, output_dir=code_dir)
        tb_path = _GENERATOR.save_testbench(
            config,
            output_dir=code_dir,
            vcd_filename=os.path.join(output_dir, f"issue-{issue_number}", "data", "spi_waveform.vcd"),
        )
    except Exception as exc:
        _record(f"{name}/generate", False, f"generation error: {exc}")
        return

    # Spot-check that key parameters appear in generated RTL
    rtl_text = open(core_path).read()
    gen_ok = True
    gen_errors = []
    checks = {
        f"MODE = {config.mode}": f"MODE = {config.mode}",
        f"DATA_WIDTH = {config.data_width}": f"DATA_WIDTH = {config.data_width}",
    }
    # Slaves only checked for master/dual (slave core doesn't have NUM_SLAVES in the same way)
    if config.spi_role in ("master", "dual"):
        checks[f"NUM_SLAVES = {config.num_slaves}"] = f"NUM_SLAVES = {config.num_slaves}"
    for label, substr in checks.items():
        if substr not in rtl_text:
            gen_ok = False
            gen_errors.append(f"missing '{substr}' in RTL")
    _record(f"{name}/generate", gen_ok, "; ".join(gen_errors))

    # --- Step 3: optional iverilog compile ---
    if _HAS_IVERILOG:
        out_sim = os.path.join(output_dir, f"issue-{issue_number}", "data", "spi_sim")
        os.makedirs(os.path.dirname(out_sim), exist_ok=True)
        result = subprocess.run(
            ["iverilog", "-g2012", "-o", out_sim, core_path, tb_path],
            capture_output=True, text=True, timeout=60,
        )
        compile_ok = result.returncode == 0
        _record(
            f"{name}/compile",
            compile_ok,
            result.stderr.strip() if not compile_ok else "",
        )


# ---------------------------------------------------------------------------
# Test groups
# ---------------------------------------------------------------------------

def _tests_spi_mode(out: str) -> None:
    print("\n── SPI Mode (0–3) ──")
    for mode in [0, 1, 2, 3]:
        issue = _build_issue(spi_mode=mode)
        _run_case(
            f"mode_{mode}",
            1000 + mode,
            issue,
            {"mode": mode, "data_width": 8, "num_slaves": 1,
             "slave_active_low": True, "msb_first": True, "spi_role": "master"},
            out,
        )


def _tests_data_width(out: str) -> None:
    print("\n── Data Width (4, 8, 16, 32, 64) ──")
    for w in [4, 8, 16, 32, 64]:
        issue = _build_issue(spi_mode=0, data_width=w)
        _run_case(
            f"width_{w}",
            1100 + w,
            issue,
            {"mode": 0, "data_width": w},
            out,
        )


def _tests_num_slaves(out: str) -> None:
    print("\n── Number of Slaves (1, 4, 8, 32) ──")
    for n in [1, 4, 8, 32]:
        issue = _build_issue(spi_mode=0, num_slaves=n)
        _run_case(
            f"slaves_{n}",
            1200 + n,
            issue,
            {"num_slaves": n},
            out,
        )


def _tests_slave_select(out: str) -> None:
    print("\n── Slave Select Behavior ──")
    for label, option, expected_low in [
        ("active_low",  "Active Low (most common)", True),
        ("active_high", "Active High",              False),
    ]:
        issue = _build_issue(slave_select=option)
        _run_case(
            f"ss_{label}",
            1300 + (0 if expected_low else 1),
            issue,
            {"slave_active_low": expected_low},
            out,
        )


def _tests_data_order(out: str) -> None:
    print("\n── Data Order ──")
    for label, option, expected_msb in [
        ("msb_first", "MSB First (most common)", True),
        ("lsb_first", "LSB First",               False),
    ]:
        issue = _build_issue(data_order=option)
        _run_case(
            f"order_{label}",
            1400 + (0 if expected_msb else 1),
            issue,
            {"msb_first": expected_msb},
            out,
        )


def _tests_spi_role(out: str) -> None:
    print("\n── SPI Role (Master / Slave / Dual) ──")
    for label, option, expected_role in [
        ("master", "Master (default)",          "master"),
        ("slave",  "Slave",                     "slave"),
        ("dual",   "Dual (both master and slave)", "dual"),
    ]:
        issue = _build_issue(spi_role=option)
        _run_case(
            f"role_{label}",
            1500 + ["master", "slave", "dual"].index(expected_role),
            issue,
            {"spi_role": expected_role},
            out,
        )


def _tests_special_features(out: str) -> None:
    print("\n── Special Features (individually + all combined) ──")
    feature_cases = [
        ("interrupt_only",     True,  False, False, False,
         {"interrupts": True,  "fifo_buffers": False, "dma_support": False, "multi_master": False}),
        ("fifo_only",          False, True,  False, False,
         {"interrupts": False, "fifo_buffers": True,  "dma_support": False, "multi_master": False}),
        ("dma_only",           False, False, True,  False,
         {"interrupts": False, "fifo_buffers": False, "dma_support": True,  "multi_master": False}),
        ("multimaster_only",   False, False, False, True,
         {"interrupts": False, "fifo_buffers": False, "dma_support": False, "multi_master": True}),
        ("all_features",       True,  True,  True,  True,
         {"interrupts": True,  "fifo_buffers": True,  "dma_support": True,  "multi_master": True}),
        ("no_features",        False, False, False, False,
         {"interrupts": False, "fifo_buffers": False, "dma_support": False, "multi_master": False}),
    ]
    for idx, (label, irq, fifo, dma, mm, expected) in enumerate(feature_cases):
        issue = _build_issue(interrupt=irq, fifo=fifo, dma=dma, multi_master=mm)
        _run_case(f"features_{label}", 1600 + idx, issue, expected, out)


def _tests_test_duration(out: str) -> None:
    print("\n── Testing Requirements (Brief / Standard / Comprehensive) ──")
    for idx, duration in enumerate(["Brief", "Standard", "Comprehensive"]):
        issue = _build_issue(test_duration=duration)
        _run_case(
            f"duration_{duration.lower()}",
            1700 + idx,
            issue,
            {"test_duration": duration},
            out,
        )


def _tests_testing_options(out: str) -> None:
    print("\n── Testing Options (Clock Jitter / Waveform Capture) ──")
    for idx, (label, jitter, wave, expected) in enumerate([
        ("jitter_only",    True,  False, {"clock_jitter_test": True,  "waveform_capture": False}),
        ("waveform_only",  False, True,  {"clock_jitter_test": False, "waveform_capture": True}),
        ("both_options",   True,  True,  {"clock_jitter_test": True,  "waveform_capture": True}),
        ("no_options",     False, False, {"clock_jitter_test": False, "waveform_capture": False}),
    ]):
        issue = _build_issue(clock_jitter=jitter, waveform_capture=wave)
        _run_case(f"options_{label}", 1800 + idx, issue, expected, out)


def _tests_combinations(out: str) -> None:
    """Test a handful of interesting multi-parameter combinations."""
    print("\n── Multi-parameter Combinations ──")
    combos = [
        ("mode3_slave_lsb_active_high",
         dict(spi_mode=3, data_width=16, num_slaves=2,
              slave_select="Active High", data_order="LSB First",
              spi_role="Slave", interrupt=True, fifo=True),
         {"mode": 3, "data_width": 16, "num_slaves": 2,
          "slave_active_low": False, "msb_first": False,
          "spi_role": "slave", "interrupts": True, "fifo_buffers": True}),

        ("mode0_dual_64bit_32slaves",
         dict(spi_mode=0, data_width=64, num_slaves=32,
              slave_select="Active Low (most common)", data_order="MSB First (most common)",
              spi_role="Dual (both master and slave)"),
         {"mode": 0, "data_width": 64, "num_slaves": 32,
          "slave_active_low": True, "msb_first": True, "spi_role": "dual"}),

        ("mode2_master_4bit_all_features",
         dict(spi_mode=2, data_width=4, num_slaves=1,
              slave_select="Active Low (most common)", data_order="LSB First",
              spi_role="Master (default)",
              interrupt=True, fifo=True, dma=True, multi_master=True,
              test_duration="Comprehensive", clock_jitter=True, waveform_capture=True),
         {"mode": 2, "data_width": 4, "slave_active_low": True, "msb_first": False,
          "spi_role": "master",
          "interrupts": True, "fifo_buffers": True, "dma_support": True,
          "multi_master": True,
          "test_duration": "Comprehensive",
          "clock_jitter_test": True, "waveform_capture": True}),
    ]
    for idx, (label, build_kwargs, expected) in enumerate(combos):
        issue = _build_issue(**build_kwargs)
        _run_case(f"combo_{label}", 1900 + idx, issue, expected, out)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 65)
    print("  SPI Core Parametric Coverage Test (5-spi-spec-intent.yml)")
    print("=" * 65)

    if _HAS_IVERILOG:
        print(f"  iverilog found — compilation checks ENABLED")
    else:
        print("  iverilog not found — compilation checks SKIPPED")

    out_dir = os.path.join(_REPO_ROOT, "results", "parametric_coverage")
    os.makedirs(out_dir, exist_ok=True)

    _tests_spi_mode(out_dir)
    _tests_data_width(out_dir)
    _tests_num_slaves(out_dir)
    _tests_slave_select(out_dir)
    _tests_data_order(out_dir)
    _tests_spi_role(out_dir)
    _tests_special_features(out_dir)
    _tests_test_duration(out_dir)
    _tests_testing_options(out_dir)
    _tests_combinations(out_dir)

    # Summary
    total = _pass + _fail
    print("\n" + "=" * 65)
    print(f"  RESULTS: {_pass}/{total} passed", end="")
    if _fail:
        print(f"  ({_fail} FAILED)")
        print("\n  Failed tests:")
        for name, ok, detail in _results:
            if not ok:
                print(f"    ❌ {name}: {detail}")
    else:
        print()
    print("=" * 65)

    return 0 if _fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
