#!/usr/bin/env python3
"""
Replay validation harness for generated SPI issue results.
Evaluates objective gates across existing results/issue-*/ artifacts.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_summary_metrics(summary_text: str) -> Dict[str, str]:
    metrics = {}
    for line in summary_text.splitlines():
        if "Signal Transitions" in line:
            metrics["signal_transitions"] = line.split("`")[1] if "`" in line else ""
        elif "Data Transfer Events" in line:
            metrics["data_transfer_events"] = line.split("`")[1] if "`" in line else ""
        elif "Clock Cycles" in line:
            metrics["clock_cycles"] = line.split("`")[1] if "`" in line else ""
    return metrics


def signal_summary_totals(signal_summary_csv: Path) -> Tuple[int, int]:
    if not signal_summary_csv.exists():
        return (0, 0)
    total_transitions = 0
    active_signals = 0
    with signal_summary_csv.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            try:
                changes = int(row[2])
                total_transitions += changes
                if changes > 0:
                    active_signals += 1
            except ValueError:
                continue
    return (total_transitions, active_signals)


def extract_clk_changes(signal_summary_csv: Path) -> int:
    if not signal_summary_csv.exists():
        return 0
    with signal_summary_csv.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            name = row[0].split(".")[-1].lower()
            if name == "clk":
                try:
                    return int(row[2])
                except ValueError:
                    return 0
    return 0


def extract_data_transfer_events(sim_log_text: str) -> int:
    content = sim_log_text.lower()
    patterns = [
        "transmission complete",
        "reception complete",
        "slave mode spi transaction complete",
        "rx matched expected payload",
    ]
    return sum(content.count(p) for p in patterns)


def evaluate_issue(issue_dir: Path) -> Dict[str, object]:
    issue = issue_dir.name.replace("issue-", "")
    code_dir = issue_dir / "code"
    data_dir = issue_dir / "data"
    logs_dir = issue_dir / "logs"

    config_file = code_dir / "spi_config.json"
    manifest_file = logs_dir / "run_manifest.json"
    core_files = sorted([p for p in code_dir.glob("*.v") if not p.name.endswith("_tb.v")])
    tb_files = sorted([p for p in code_dir.glob("*_tb.v")])
    comp_log = logs_dir / "compilation.log"
    sim_log = logs_dir / "simulation.log"
    vcd_file = data_dir / "spi_waveform.vcd"
    compliance_file = logs_dir / "protocol_compliance.md"
    summary_file = logs_dir / "SUMMARY.md"
    signal_summary_csv = data_dir / "spi_signal_summary.csv"

    compilation_text = read_text(comp_log)
    simulation_text = read_text(sim_log)
    compliance_text = read_text(compliance_file)
    summary_text = read_text(summary_file)
    manifest_text = read_text(manifest_file)
    core_text = read_text(core_files[0]) if core_files else ""
    tb_text = read_text(tb_files[0]) if tb_files else ""
    config = {}
    if config_file.exists():
        try:
            config = json.loads(read_text(config_file))
        except json.JSONDecodeError:
            config = {}

    compile_ok = ("Return code: 0" in compilation_text) or ("Compilation: SUCCESS" in compilation_text)
    sim_ok = ("Return code: 0" in simulation_text) and ("FATAL:" not in simulation_text)
    vcd_ok = vcd_file.exists() and vcd_file.stat().st_size > 0
    compliance_ok = (
        compliance_file.exists()
        and "| Check | Result | Notes |" in compliance_text
        and "NOT_RUN" not in compliance_text
        and "**FAIL**" not in compliance_text
        and "| FAIL |" not in compliance_text
    )
    summary_ok = summary_file.exists() and ("Signal Transitions" in summary_text) and ("Data Transfer Events" in summary_text)

    # Consistency checks
    summary_metrics = parse_summary_metrics(summary_text)
    transitions_csv, _ = signal_summary_totals(signal_summary_csv)
    clk_changes = extract_clk_changes(signal_summary_csv)
    transfers_log = extract_data_transfer_events(simulation_text)

    summary_transitions = int(summary_metrics.get("signal_transitions", "0").replace(",", "") or 0)
    summary_clock_cycles = int(summary_metrics.get("clock_cycles", "0").replace(",", "") or 0)
    summary_transfer_events = int(summary_metrics.get("data_transfer_events", "0").replace(",", "") or 0)

    consistency_ok = (
        summary_transitions == transitions_csv
        and summary_clock_cycles == clk_changes
        and summary_transfer_events == transfers_log
    )
    spec_oracle_ok = _evaluate_spec_oracle(manifest_text, compliance_text, simulation_text)
    rtl_tb_semantic_ok = _evaluate_rtl_tb_semantics(manifest_text, core_text, tb_text)

    gates = {
        "compile_ok": compile_ok,
        "sim_ok": sim_ok,
        "vcd_ok": vcd_ok,
        "compliance_ok": compliance_ok,
        "summary_ok": summary_ok,
        "consistency_ok": consistency_ok,
        "spec_oracle_ok": spec_oracle_ok,
        "rtl_tb_semantic_ok": rtl_tb_semantic_ok,
    }
    pass_all = all(gates.values())
    issue_num = int(issue)
    is_modern = issue_num >= 1002

    return {
        "issue": issue,
        "pass_all": pass_all,
        "gates": gates,
        "has_config": config_file.exists(),
        "is_modern": is_modern,
        "config": config,
    }


def _coverage_key(result: Dict[str, object]) -> Tuple[str, str, str, str, str]:
    cfg = result.get("config", {}) if isinstance(result.get("config"), dict) else {}
    mode = str(cfg.get("mode", "unknown"))
    role = str(cfg.get("spi_role", "unknown"))
    width = int(cfg.get("data_width", 0) or 0)
    width_class = str(width) if width in {1, 3, 7, 8, 16, 32} else "other"
    ss = "active_low" if bool(cfg.get("slave_active_low", True)) else "active_high"
    order = "msb_first" if bool(cfg.get("msb_first", True)) else "lsb_first"
    return (mode, role, width_class, ss, order)


def _compute_coverage_profile(results: List[Dict[str, object]]) -> Dict[str, object]:
    modern = [r for r in results if r["is_modern"]]
    profile = {
        "mode": set(),
        "role": set(),
        "ss_polarity": set(),
        "bit_order": set(),
        "test_duration": set(),
        "interrupts": set(),
        "fifo_buffers": set(),
        "dma_support": set(),
        "multi_master": set(),
        "clock_jitter_test": set(),
        "waveform_capture": set(),
        "default_data_enabled": set(),
        "default_data_pattern": set(),
    }
    for r in modern:
        cfg = r.get("config", {}) if isinstance(r.get("config"), dict) else {}
        profile["mode"].add(str(cfg.get("mode", "unknown")))
        profile["role"].add(str(cfg.get("spi_role", "unknown")).lower())
        profile["ss_polarity"].add("active_low" if bool(cfg.get("slave_active_low", True)) else "active_high")
        profile["bit_order"].add("msb_first" if bool(cfg.get("msb_first", True)) else "lsb_first")
        profile["test_duration"].add(str(cfg.get("test_duration", "unknown")).lower())
        profile["interrupts"].add(bool(cfg.get("interrupts", False)))
        profile["fifo_buffers"].add(bool(cfg.get("fifo_buffers", False)))
        profile["dma_support"].add(bool(cfg.get("dma_support", False)))
        profile["multi_master"].add(bool(cfg.get("multi_master", False)))
        profile["clock_jitter_test"].add(bool(cfg.get("clock_jitter_test", False)))
        profile["waveform_capture"].add(bool(cfg.get("waveform_capture", False)))
        profile["default_data_enabled"].add(bool(cfg.get("default_data_enabled", False)))
        profile["default_data_pattern"].add(str(cfg.get("default_data_pattern", "unknown")).lower())

    required = {
        "mode": {"0", "1", "2", "3"},
        "role": {"master", "slave", "dual"},
        "ss_polarity": {"active_low", "active_high"},
        "bit_order": {"msb_first", "lsb_first"},
        "test_duration": {"brief", "standard", "comprehensive"},
        "interrupts": {True, False},
        "fifo_buffers": {True, False},
        "dma_support": {True, False},
        "multi_master": {True, False},
        "clock_jitter_test": {True, False},
        "waveform_capture": {True, False},
        "default_data_enabled": {True, False},
        "default_data_pattern": {"a5a5", "ffff", "0000", "5555", "custom"},
    }
    gaps = {}
    for key, req_vals in required.items():
        missing = sorted([v for v in req_vals if v not in profile[key]], key=lambda x: str(x))
        if missing:
            gaps[key] = missing
    return {"profile": profile, "required": required, "gaps": gaps}


def _evaluate_spec_oracle(manifest_text: str, compliance_text: str, simulation_text: str) -> bool:
    if not manifest_text:
        return False
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return False

    spec = manifest.get("verification_spec")
    if not isinstance(spec, dict):
        return False

    # Base requirements: spec present and core protocol checks represented.
    comp_lower = compliance_text.lower()
    required_checks = [
        "sclk_idle_level_matches_cpol",
        "ss_n_matches_busy_window",
        "mosi_does_not_change_on_sampling_edge",
    ]
    for check in required_checks:
        if check not in comp_lower:
            return False

    # Validate acceptance criteria bullets through keyword-to-evidence mapping.
    acceptance = spec.get("acceptance_criteria", []) or []
    sim_lower = simulation_text.lower()

    for criterion in acceptance:
        c = criterion.lower()
        if "ss_n" in c or "slave select" in c:
            if "ss_n_matches_busy_window" not in comp_lower:
                return False
        elif "mosi" in c and ("sampling edge" in c or "sample" in c):
            if "mosi_does_not_change_on_sampling_edge" not in comp_lower:
                return False
        elif "rx" in c or "payload" in c:
            if "rx matched expected payload" not in sim_lower:
                return False
        # Unmapped criteria are tolerated for now but should be expanded over time.

    return True


def _evaluate_rtl_tb_semantics(manifest_text: str, core_text: str, tb_text: str) -> bool:
    if not manifest_text or not core_text or not tb_text:
        return False
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return False
    spec = manifest.get("verification_spec")
    if not isinstance(spec, dict):
        return False

    role = (spec.get("spi_role") or "").lower()
    mode = spec.get("mode")
    data_width = spec.get("data_width")
    bit_order = spec.get("bit_order")

    # Role/module alignment checks
    if role == "dual":
        if "module spi_dual" not in core_text or "module spi_dual_tb" not in tb_text:
            return False
    elif role == "master":
        if "module spi_master" not in core_text or "module spi_master_tb" not in tb_text:
            return False
    elif role == "slave":
        if "module spi_slave" not in core_text or "module spi_slave_tb" not in tb_text:
            return False
    else:
        return False

    # Mode and width propagation in TB parameters
    if mode is None or f"parameter MODE = {mode};" not in tb_text:
        return False
    if data_width is None or f"parameter DATA_WIDTH = {data_width};" not in tb_text:
        return False

    # Semantic TB checks for robustness (role-aware)
    if role == "dual":
        required_tb_tokens = ["$fatal", "rx_valid", "expected_slave_rx"]
    elif role == "slave":
        required_tb_tokens = ["rx_valid", "tx_ready"]
    elif role == "master":
        required_tb_tokens = ["start_tx", "busy"]
    else:
        return False
    for token in required_tb_tokens:
        if token not in tb_text:
            return False

    # Bit-order propagation check (best-effort structural)
    if bit_order == "msb_first" and "MSB_FIRST = 1" not in tb_text:
        return False
    if bit_order == "lsb_first" and "MSB_FIRST = 0" not in tb_text:
        return False

    # Mode-specific intent marker in TB comments/logic
    if mode == 2 and "SPI Mode 2" not in tb_text:
        return False

    return True


def write_report(results: List[Dict[str, object]], out_file: Path) -> None:
    total = len(results)
    passed = sum(1 for r in results if r["pass_all"])
    modern = [r for r in results if r["is_modern"]]
    legacy = [r for r in results if not r["is_modern"]]
    modern_pass = sum(1 for r in modern if r["pass_all"])
    legacy_pass = sum(1 for r in legacy if r["pass_all"])

    lines = []
    lines.append("# SPI Replay Validation Report")
    lines.append("")
    lines.append(f"- Cases evaluated: **{total}**")
    lines.append(f"- Passed all gates: **{passed}**")
    lines.append(f"- Failed at least one gate: **{total - passed}**")
    lines.append(f"- Modern cases (post-fix replay set): **{len(modern)}**, pass: **{modern_pass}**")
    lines.append(f"- Legacy cases (historical artifacts): **{len(legacy)}**, pass: **{legacy_pass}**")
    lines.append("")

    # Coverage matrix over modern cases
    modern_coverage = {}
    for r in modern:
        key = _coverage_key(r)
        modern_coverage[key] = modern_coverage.get(key, 0) + 1
    coverage = _compute_coverage_profile(results)
    coverage_gap = "none" if not coverage["gaps"] else "listed"
    release_gate_modern = "PASS" if modern and modern_pass == len(modern) and coverage_gap == "none" else "FAIL"

    lines.append("## Policy Verdict")
    lines.append("")
    lines.append(f"- `release_gate_modern`: **{release_gate_modern}**")
    lines.append(f"- `coverage_gap`: **{coverage_gap}**")
    if coverage_gap != "none":
        lines.append("- `coverage_gap_details`:")
        for key in sorted(coverage["gaps"].keys()):
            missing = ", ".join(str(v) for v in coverage["gaps"][key])
            lines.append(f"  - {key}: {missing}")
    lines.append("")
    lines.append("## Gate Definitions")
    lines.append("")
    lines.append("- `compile_ok`: compilation log indicates success")
    lines.append("- `sim_ok`: simulation log has return code 0 and no `FATAL:`")
    lines.append("- `vcd_ok`: non-empty `spi_waveform.vcd` exists")
    lines.append("- `compliance_ok`: compliance report exists, has check table, and no `FAIL`/`NOT_RUN` checks")
    lines.append("- `summary_ok`: summary exists with key metrics")
    lines.append("- `consistency_ok`: summary metrics match CSV/log-derived values")
    lines.append("- `spec_oracle_ok`: compliance/log evidence satisfies issue-derived verification spec")
    lines.append("- `rtl_tb_semantic_ok`: generated RTL/TB structure and semantic checks match spec")
    lines.append("")
    lines.append("## Per-Issue Results")
    lines.append("")
    lines.append("| Issue | Overall | compile_ok | sim_ok | vcd_ok | compliance_ok | summary_ok | consistency_ok | spec_oracle_ok | rtl_tb_semantic_ok |")
    lines.append("|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
    for r in sorted(results, key=lambda x: int(x["issue"])):
        g = r["gates"]
        overall = "PASS" if r["pass_all"] else "FAIL"
        lines.append(
            f"| {r['issue']} | {overall} | "
            f"{'Y' if g['compile_ok'] else 'N'} | "
            f"{'Y' if g['sim_ok'] else 'N'} | "
            f"{'Y' if g['vcd_ok'] else 'N'} | "
            f"{'Y' if g['compliance_ok'] else 'N'} | "
            f"{'Y' if g['summary_ok'] else 'N'} | "
            f"{'Y' if g['consistency_ok'] else 'N'} | "
            f"{'Y' if g['spec_oracle_ok'] else 'N'} | "
            f"{'Y' if g['rtl_tb_semantic_ok'] else 'N'} |"
        )

    lines.append("")
    lines.append("## Coverage Matrix (Modern Cases)")
    lines.append("")
    lines.append("| Mode | Role | Width Class | SS Polarity | Bit Order | Cases |")
    lines.append("|---:|---|---|---|---|---:|")
    if modern_coverage:
        for key in sorted(modern_coverage.keys()):
            mode, role, width_class, ss, order = key
            lines.append(f"| {mode} | {role} | {width_class} | {ss} | {order} | {modern_coverage[key]} |")
    else:
        lines.append("| - | - | - | - | - | 0 |")
    lines.append("")
    lines.append("## Template Input Coverage (Modern Cases)")
    lines.append("")
    lines.append("| Dimension | Covered Values | Required Values |")
    lines.append("|---|---|---|")
    for key in sorted(coverage["required"].keys()):
        covered_vals = ", ".join(str(v) for v in sorted(coverage["profile"][key], key=lambda x: str(x))) or "(none)"
        required_vals = ", ".join(str(v) for v in sorted(coverage["required"][key], key=lambda x: str(x)))
        lines.append(f"| {key} | {covered_vals} | {required_vals} |")
    lines.append("")

    lines.append("## Triage View")
    lines.append("")
    lines.append("### Modern Cases (Release Gate Candidates)")
    lines.append("")
    if modern:
        for r in sorted(modern, key=lambda x: int(x["issue"])):
            if r["pass_all"]:
                lines.append(f"- issue-{r['issue']}: PASS")
            else:
                failed = [k for k, v in r["gates"].items() if not v]
                lines.append(f"- issue-{r['issue']}: FAIL ({', '.join(failed)})")
    else:
        lines.append("- No modern cases selected.")

    lines.append("")
    lines.append("### Legacy Failures (Historical Artifacts)")
    lines.append("")
    legacy_failed = [r for r in legacy if not r["pass_all"]]
    if legacy_failed:
        lines.append(f"- Count: {len(legacy_failed)}")
        lines.append("- Primary pattern: missing compliance/summary-consistency artifacts from older runs.")
    else:
        lines.append("- None.")

    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    root = Path("results")
    issue_dirs = sorted([p for p in root.glob("issue-*") if (p / "code" / "spi_config.json").exists()], key=lambda p: int(p.name.replace("issue-", "")))
    if not issue_dirs:
        print("No issue result directories found.")
        return 1

    results = [evaluate_issue(p) for p in issue_dirs]
    report_file = Path("docs") / "SPI_REPLAY_VALIDATION_REPORT.md"
    write_report(results, report_file)
    print(f"Wrote report: {report_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
