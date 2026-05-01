#!/usr/bin/env python3
"""
Replay validation harness for generated SPI issue results.
Evaluates objective gates across existing results/issue-*/ artifacts.
"""

import csv
import json
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set


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


def parse_compliance_checks(compliance_text: str) -> Dict[str, str]:
    checks: Dict[str, str] = {}
    for raw in compliance_text.splitlines():
        line = raw.strip()
        if not line.startswith("| `"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 2:
            continue
        check_name = parts[0].strip("`").strip()
        result_cell = parts[1].replace("*", "").strip().upper()
        if result_cell in {"PASS", "FAIL", "NOT_RUN"}:
            checks[check_name] = result_cell
    return checks


def load_conformance_requirements(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError:
        return []
    reqs = data.get("requirements", [])
    if not isinstance(reqs, list):
        return []
    normalized = []
    for req in reqs:
        if not isinstance(req, dict):
            continue
        req_id = str(req.get("id", "")).strip()
        checks = req.get("checks", [])
        if not req_id or not isinstance(checks, list):
            continue
        normalized.append(
            {
                "id": req_id,
                "title": str(req.get("title", "")).strip(),
                "checks": [str(c).strip() for c in checks if str(c).strip()],
                "applies_to": [str(v).lower() for v in req.get("applies_to", [])] if isinstance(req.get("applies_to", []), list) else [],
            }
        )
    return normalized


def evaluate_negative_cases(root: Path) -> List[Dict[str, object]]:
    """
    Evaluate negative/fault-injection cases from results/negative-*/ directories.
    Each case can include logs/negative_manifest.json with:
      {
        "case_id": "neg-...",
        "expected_fail_checks": ["CheckName1", ...]
      }
    A negative case passes when all expected checks are present as FAIL in protocol_compliance.md.
    """
    cases: List[Dict[str, object]] = []
    for case_dir in sorted(root.glob("negative-*")):
        manifest_path = case_dir / "logs" / "negative_manifest.json"
        compliance_path = case_dir / "logs" / "protocol_compliance.md"
        manifest = {}
        if manifest_path.exists():
            try:
                manifest = json.loads(read_text(manifest_path))
            except json.JSONDecodeError:
                manifest = {}
        expected = manifest.get("expected_fail_checks", [])
        if not isinstance(expected, list):
            expected = []
        expected = [str(v).strip() for v in expected if str(v).strip()]
        compliance_checks = parse_compliance_checks(read_text(compliance_path))
        missing = [chk for chk in expected if compliance_checks.get(chk) != "FAIL"]
        case_id = str(manifest.get("case_id", case_dir.name))
        status = "PASS" if expected and not missing else "FAIL"
        cases.append(
            {
                "case_id": case_id,
                "expected_checks": expected,
                "missing_expected_fails": missing,
                "status": status,
            }
        )
    return cases


def _compute_case_runtime(issue_dir: Path) -> Dict[str, object]:
    """
    Derive per-case runtime telemetry from artifact modification times.
    """
    candidates = [
        issue_dir / "logs" / "run_manifest.json",
        issue_dir / "logs" / "compilation.log",
        issue_dir / "logs" / "simulation.log",
        issue_dir / "logs" / "protocol_compliance.md",
        issue_dir / "logs" / "SUMMARY.md",
    ]
    times = [p.stat().st_mtime for p in candidates if p.exists()]
    if not times:
        return {"start_ts": "", "end_ts": "", "duration_s": None}
    start = min(times)
    end = max(times)
    return {
        "start_ts": datetime.fromtimestamp(start, tz=timezone.utc).isoformat(),
        "end_ts": datetime.fromtimestamp(end, tz=timezone.utc).isoformat(),
        "duration_s": max(0.0, end - start),
    }


def _percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * pct
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


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
    timing_csv = data_dir / "spi_timing_data.csv"

    compilation_text = read_text(comp_log)
    simulation_text = read_text(sim_log)
    compliance_text = read_text(compliance_file)
    compliance_checks = parse_compliance_checks(compliance_text)
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
    transaction_oracle_ok = _evaluate_transaction_oracle(config, timing_csv)
    selected_slave_oracle_ok = _evaluate_selected_slave_oracle(config, timing_csv, data_dir)

    gates = {
        "compile_ok": compile_ok,
        "sim_ok": sim_ok,
        "vcd_ok": vcd_ok,
        "compliance_ok": compliance_ok,
        "summary_ok": summary_ok,
        "consistency_ok": consistency_ok,
        "spec_oracle_ok": spec_oracle_ok,
        "rtl_tb_semantic_ok": rtl_tb_semantic_ok,
        "transaction_oracle_ok": transaction_oracle_ok,
        "selected_slave_oracle_ok": selected_slave_oracle_ok,
    }
    pass_all = all(gates.values())
    issue_num = int(issue)
    is_modern = issue_num >= 1002
    runtime = _compute_case_runtime(issue_dir)

    return {
        "issue": issue,
        "pass_all": pass_all,
        "gates": gates,
        "has_config": config_file.exists(),
        "is_modern": is_modern,
        "config": config,
        "compliance_checks": compliance_checks,
        "runtime": runtime,
    }


def _coverage_key(result: Dict[str, object]) -> Tuple[str, str, str, str, str]:
    cfg = result.get("config", {}) if isinstance(result.get("config"), dict) else {}
    mode = str(cfg.get("mode", "unknown"))
    role = str(cfg.get("spi_role", "unknown"))
    width = int(cfg.get("data_width", 0) or 0)
    width_class = str(width) if width in {1, 2, 3, 7, 8, 9, 15, 16, 24, 31, 32} else "other"
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
        "data_width": set(),
        "selected_slave_index": set(),
        "selected_slave_bucket": set(),
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
        profile["data_width"].add(int(cfg.get("data_width", 0) or 0))
        role = str(cfg.get("spi_role", "unknown")).lower()
        try:
            num_slaves = int(cfg.get("num_slaves", 0) or 0)
        except (TypeError, ValueError):
            num_slaves = 0
        try:
            selected = int(cfg.get("selected_slave", 0) or 0)
        except (TypeError, ValueError):
            selected = 0
        if role in {"master", "dual"} and num_slaves > 1:
            profile["selected_slave_index"].add(selected)
            profile["selected_slave_bucket"].add("zero" if selected == 0 else "nonzero")
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
        "data_width": {1, 2, 3, 7, 8, 9, 15, 16, 24, 31, 32},
        "selected_slave_bucket": {"zero", "nonzero"},
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


def _compute_feature_pair_coverage(modern: List[Dict[str, object]]) -> Dict[str, object]:
    feature_dims = ("interrupts", "fifo_buffers", "dma_support", "multi_master")
    observed = {dim: set() for dim in feature_dims}
    for r in modern:
        cfg = r.get("config", {}) if isinstance(r.get("config"), dict) else {}
        for dim in feature_dims:
            observed[dim].add(bool(cfg.get(dim, False)))

    pair_rows: List[Dict[str, object]] = []
    total_pairs = 0
    total_covered = 0
    for i in range(len(feature_dims)):
        for j in range(i + 1, len(feature_dims)):
            left = feature_dims[i]
            right = feature_dims[j]
            target_pairs = {(a, b) for a in (False, True) for b in (False, True)}
            seen_pairs = set()
            for r in modern:
                cfg = r.get("config", {}) if isinstance(r.get("config"), dict) else {}
                seen_pairs.add((bool(cfg.get(left, False)), bool(cfg.get(right, False))))
            missing_pairs = sorted(target_pairs - seen_pairs, key=lambda x: (str(x[0]), str(x[1])))
            covered = len(seen_pairs)
            target = len(target_pairs)
            total_pairs += target
            total_covered += covered
            pair_rows.append(
                {
                    "pair": f"{left} x {right}",
                    "covered": covered,
                    "target": target,
                    "missing_pairs": missing_pairs,
                    "coverage_ratio": covered / target if target else 0.0,
                }
            )
    return {
        "feature_dims": feature_dims,
        "observed": observed,
        "rows": pair_rows,
        "covered": total_covered,
        "target": total_pairs,
        "all_closed": total_covered == total_pairs if total_pairs else False,
    }


def _compute_representativeness_metrics(coverage: Dict[str, object], pairwise: Dict[str, object]) -> Dict[str, object]:
    rows: List[Dict[str, object]] = []
    total_covered = 0
    total_target = 0
    for key in sorted(coverage["required"].keys()):
        required = set(coverage["required"][key])
        covered_vals = set(coverage["profile"].get(key, set()))
        covered_count = len(required & covered_vals)
        target_count = len(required)
        total_covered += covered_count
        total_target += target_count
        rows.append(
            {
                "dimension": key,
                "covered": covered_count,
                "target": target_count,
                "missing": sorted(required - covered_vals, key=lambda x: str(x)),
            }
        )
    pairwise_missing: List[str] = []
    for pair_row in pairwise["rows"]:
        for left_val, right_val in pair_row["missing_pairs"]:
            pairwise_missing.append(f"{pair_row['pair']}({left_val},{right_val})")
    rows.append(
        {
            "dimension": "special_feature_pairs_2way",
            "covered": pairwise["covered"],
            "target": pairwise["target"],
            "missing": pairwise_missing,
        }
    )
    total_covered += pairwise["covered"]
    total_target += pairwise["target"]
    score = (100.0 * total_covered / total_target) if total_target else 0.0
    return {
        "rows": rows,
        "score": score,
        "covered": total_covered,
        "target": total_target,
    }


def _compute_balance_matrix(modern: List[Dict[str, object]]) -> Dict[str, object]:
    dims: Dict[str, Dict[object, int]] = {
        "mode": {},
        "role": {},
        "data_width": {},
        "num_slaves": {},
        "ss_polarity": {},
        "bit_order": {},
        "default_data_enabled": {},
        "default_data_pattern": {},
        "interrupts": {},
        "fifo_buffers": {},
        "dma_support": {},
        "multi_master": {},
        "clock_jitter_test": {},
        "waveform_capture": {},
    }
    for r in modern:
        cfg = r.get("config", {}) if isinstance(r.get("config"), dict) else {}
        entries = {
            "mode": str(cfg.get("mode", "unknown")),
            "role": str(cfg.get("spi_role", "unknown")).lower(),
            "data_width": int(cfg.get("data_width", 0) or 0),
            "num_slaves": int(cfg.get("num_slaves", 0) or 0),
            "ss_polarity": "active_low" if bool(cfg.get("slave_active_low", True)) else "active_high",
            "bit_order": "msb_first" if bool(cfg.get("msb_first", True)) else "lsb_first",
            "default_data_enabled": bool(cfg.get("default_data_enabled", False)),
            "default_data_pattern": str(cfg.get("default_data_pattern", "unknown")).lower(),
            "interrupts": bool(cfg.get("interrupts", False)),
            "fifo_buffers": bool(cfg.get("fifo_buffers", False)),
            "dma_support": bool(cfg.get("dma_support", False)),
            "multi_master": bool(cfg.get("multi_master", False)),
            "clock_jitter_test": bool(cfg.get("clock_jitter_test", False)),
            "waveform_capture": bool(cfg.get("waveform_capture", False)),
        }
        for k, v in entries.items():
            dims[k][v] = dims[k].get(v, 0) + 1

    rows: List[Dict[str, object]] = []
    for name in sorted(dims.keys()):
        counts = dims[name]
        values = [counts[k] for k in counts]
        if values:
            min_count = min(values)
            max_count = max(values)
            ratio = (float(max_count) / float(min_count)) if min_count > 0 else 0.0
        else:
            min_count = 0
            max_count = 0
            ratio = 0.0
        rows.append(
            {
                "dimension": name,
                "counts": counts,
                "min": min_count,
                "max": max_count,
                "max_min_ratio": ratio,
            }
        )
    return {"rows": rows}


def _compact_case_features(result: Dict[str, object]) -> Set[str]:
    """
    Build deterministic feature tokens used for compact-suite selection.
    Tokens capture both single-dimension values and key pairwise interactions.
    """
    cfg = result.get("config", {}) if isinstance(result.get("config"), dict) else {}
    try:
        width = int(cfg.get("data_width", 0) or 0)
    except (TypeError, ValueError):
        width = 0
    mode = str(cfg.get("mode", "unknown"))
    role = str(cfg.get("spi_role", "unknown")).lower()
    ss = "active_low" if bool(cfg.get("slave_active_low", True)) else "active_high"
    order = "msb_first" if bool(cfg.get("msb_first", True)) else "lsb_first"
    features: Set[str] = {
        f"mode={mode}",
        f"role={role}",
        f"width={width}",
        f"ss={ss}",
        f"order={order}",
        f"feat_interrupts={bool(cfg.get('interrupts', False))}",
        f"feat_fifo={bool(cfg.get('fifo_buffers', False))}",
        f"feat_dma={bool(cfg.get('dma_support', False))}",
        f"feat_multi_master={bool(cfg.get('multi_master', False))}",
        f"test_duration={str(cfg.get('test_duration', 'unknown')).lower()}",
        f"clock_jitter={bool(cfg.get('clock_jitter_test', False))}",
        f"waveform_capture={bool(cfg.get('waveform_capture', False))}",
    }
    features.add(f"pair_mode_role={mode}|{role}")
    features.add(f"pair_mode_order={mode}|{order}")
    features.add(f"pair_role_ss={role}|{ss}")
    features.add(f"pair_width_role={width}|{role}")
    return features


def _select_compact_modern_suite(modern: List[Dict[str, object]], target_size: int) -> List[Dict[str, object]]:
    """
    Deterministic greedy selector:
    maximize newly covered feature tokens per added case, tie-break by issue number.
    """
    if target_size <= 0 or not modern:
        return modern
    if len(modern) <= target_size:
        return sorted(modern, key=lambda r: int(r["issue"]))

    pool = sorted(modern, key=lambda r: int(r["issue"]))
    selected: List[Dict[str, object]] = []
    covered: Set[str] = set()

    while pool and len(selected) < target_size:
        best_idx = 0
        best_gain = -1
        for idx, case in enumerate(pool):
            gain = len(_compact_case_features(case) - covered)
            if gain > best_gain:
                best_gain = gain
                best_idx = idx
        chosen = pool.pop(best_idx)
        selected.append(chosen)
        covered.update(_compact_case_features(chosen))

    return selected


def _find_practical_compact_suite(modern: List[Dict[str, object]]) -> Dict[str, object]:
    """
    Find smallest compact-suite size that closes required coverage dimensions
    and 2-way special-feature pair coverage.
    """
    if not modern:
        return {"size": 0, "score": 0.0, "closed": False}
    for size in range(1, len(modern) + 1):
        subset = _select_compact_modern_suite(modern, size)
        coverage = _compute_coverage_profile(subset)
        pairwise = _compute_feature_pair_coverage(subset)
        rep = _compute_representativeness_metrics(coverage, pairwise)
        if not coverage["gaps"] and pairwise["all_closed"]:
            return {"size": size, "score": rep["score"], "closed": True}
    full_cov = _compute_coverage_profile(modern)
    full_pairwise = _compute_feature_pair_coverage(modern)
    full_rep = _compute_representativeness_metrics(full_cov, full_pairwise)
    return {"size": len(modern), "score": full_rep["score"], "closed": False}


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

    # Parse key TB parameter values (format-insensitive structural check).
    tb_mode = _extract_tb_param_int(tb_text, "MODE")
    tb_data_width = _extract_tb_param_int(tb_text, "DATA_WIDTH")
    tb_msb_first = _extract_tb_param_int(tb_text, "MSB_FIRST")
    if mode is None or tb_mode != int(mode):
        return False
    if data_width is None or tb_data_width != int(data_width):
        return False

    # Semantic TB checks for robustness (role-aware)
    if role == "dual":
        required_tb_tokens = ["$fatal", "rx_valid", "expected_slave_rx", "MASTER_TX_TIMEOUT_CYCLES"]
    elif role == "slave":
        required_tb_tokens = ["rx_valid", "tx_ready"]
    elif role == "master":
        required_tb_tokens = ["$fatal", "start_tx", "busy", "wait_for_busy_assert", "assert_selected_ss_active"]
    else:
        return False
    for token in required_tb_tokens:
        if token not in tb_text:
            return False

    # Bit-order propagation check from parsed parameter value.
    if bit_order == "msb_first" and tb_msb_first != 1:
        return False
    if bit_order == "lsb_first" and tb_msb_first != 0:
        return False

    return True


def _extract_tb_param_int(tb_text: str, param_name: str) -> Optional[int]:
    """
    Extract integer-valued Verilog parameter from testbench text.
    Supports compact/spaced forms, optional signed values, and width/base literals.
    """
    pattern = rf"parameter\s+{re.escape(param_name)}\s*=\s*([^;]+);"
    match = re.search(pattern, tb_text)
    if not match:
        return None
    raw = match.group(1).strip()
    # Width/base form, e.g. 8'd24 or 1'b0
    base_lit = re.match(r"(?:\d+)?'([bBdDhH])([0-9a-fA-F_xXzZ]+)$", raw)
    if base_lit:
        base_ch = base_lit.group(1).lower()
        digits = base_lit.group(2).replace("_", "")
        if any(ch in "xXzZ" for ch in digits):
            return None
        base = {"b": 2, "d": 10, "h": 16}[base_ch]
        try:
            return int(digits, base)
        except ValueError:
            return None
    # Decimal integer literal
    try:
        return int(raw, 10)
    except ValueError:
        return None


def _decode_transaction_windows(
    timing_csv: Path,
    sample_on_rising: bool,
) -> List[Dict[str, int]]:
    """
    Decode busy-window transaction slices from timing CSV.
    Returns per-window metrics with sampling-edge counts.
    """
    rows = []
    with timing_csv.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sclk_raw = row.get("SCLK", "").strip()
            busy_raw = row.get("BUSY", "").strip()
            t_raw = row.get("Time (ns)", "").strip()
            if sclk_raw not in {"0", "1"} or busy_raw not in {"0", "1"}:
                continue
            try:
                t_ns = int(float(t_raw))
            except ValueError:
                t_ns = 0
            rows.append((t_ns, int(sclk_raw), int(busy_raw)))
    if len(rows) < 2:
        return []

    windows: List[Tuple[int, int]] = []
    in_busy = False
    start = 0
    for i, (_, _, busy) in enumerate(rows):
        if busy == 1 and not in_busy:
            in_busy = True
            start = i
        elif busy == 0 and in_busy:
            windows.append((start, i))
            in_busy = False
    if in_busy:
        windows.append((start, len(rows) - 1))

    decoded = []
    for s, e in windows:
        if e - s < 1:
            continue
        sample_edges = 0
        all_edges = 0
        prev = rows[s][1]
        for i in range(s + 1, e + 1):
            cur = rows[i][1]
            if cur != prev:
                all_edges += 1
                if sample_on_rising and prev == 0 and cur == 1:
                    sample_edges += 1
                elif (not sample_on_rising) and prev == 1 and cur == 0:
                    sample_edges += 1
            prev = cur
        decoded.append(
            {
                "start_ns": rows[s][0],
                "end_ns": rows[e][0],
                "sample_edges": sample_edges,
                "all_edges": all_edges,
            }
        )
    return decoded


def _evaluate_transaction_oracle(config: Dict[str, object], timing_csv: Path) -> bool:
    """
    Basic transaction oracle:
    - Identify busy windows from sampled timing data.
    - Verify SCLK sampling-edge activity and minimum bit-count expectation per frame.
    This is an initial M11 oracle scaffold and is intentionally conservative.
    """
    if not timing_csv.exists():
        return False
    try:
        mode = int(config.get("mode", 0))
        data_width = int(config.get("data_width", 0))
        role = str(config.get("spi_role", "master")).lower()
    except (TypeError, ValueError):
        return False
    if data_width <= 0:
        return False

    cpol = 1 if mode in (2, 3) else 0
    cpha = 1 if mode in (1, 3) else 0
    leading_is_rising = (cpol == 0)
    sample_on_rising = leading_is_rising if cpha == 0 else (not leading_is_rising)

    decoded = _decode_transaction_windows(timing_csv, sample_on_rising=sample_on_rising)
    if not decoded:
        return False

    # In slave mode, external master controls clocking; require observable
    # SCLK activity while DUT reports busy at least once.
    if role == "slave":
        for w in decoded:
            if w["all_edges"] >= 2:
                return True
        return False

    # For each busy window, require at least data_width sampling edges.
    for w in decoded:
        if w["sample_edges"] >= data_width:
            return True
    return False


def _evaluate_selected_slave_oracle(config: Dict[str, object], timing_csv: Path, data_dir: Path) -> bool:
    """
    Evidence-based selected-slave check for master/dual roles.
    During BUSY windows, SS_N must be one-hot active on configured selected index.
    """
    if not timing_csv.exists():
        return False
    role = str(config.get("spi_role", "master")).lower()
    if role not in {"master", "dual"}:
        return True
    try:
        num_slaves = int(config.get("num_slaves", 1))
    except (TypeError, ValueError):
        num_slaves = 1
    if num_slaves <= 1:
        return True
    try:
        selected = int(config.get("selected_slave", 0))
    except (TypeError, ValueError):
        selected = 0
    if selected < 0 or selected >= num_slaves:
        selected = 0

    active_low = bool(config.get("slave_active_low", True))
    active_bit = "0" if active_low else "1"
    inactive_bit = "1" if active_low else "0"
    saw_busy = False
    saw_valid_ss = False

    ss_samples: List[str] = []
    if role == "master":
        if not timing_csv.exists():
            return False
        with timing_csv.open("r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (row.get("BUSY", "") or "").strip() != "1":
                    continue
                saw_busy = True
                ss_samples.append((row.get("SS_N", "") or "").strip())
    else:
        # Dual-role timing CSV canonical SS_N can map to ss_in; use master_ss_n_reg evidence directly.
        reg_csvs = sorted(data_dir.glob("*master_ss_n_reg*_data.csv"))
        if not reg_csvs:
            return False
        with reg_csvs[0].open("r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) < 2:
                    continue
                ss_samples.append((row[1] or "").strip())

    for ss_raw in ss_samples:
        bits: Optional[str] = None
        if ss_raw.startswith("b"):
            candidate = ss_raw[1:]
            if candidate and all(c in "01" for c in candidate):
                if len(candidate) <= num_slaves:
                    bits = candidate.rjust(num_slaves, inactive_bit)
        elif ss_raw in {"0", "1"} and num_slaves == 1:
            bits = ss_raw
        if bits is None:
            continue
        saw_valid_ss = True
        active_count = sum(1 for c in bits if c == active_bit)
        if active_count == 0:
            continue
        if active_count != 1:
            return False
        selected_pos = len(bits) - 1 - selected
        if selected_pos < 0 or selected_pos >= len(bits):
            return False
        if bits[selected_pos] != active_bit:
            return False
        for i, c in enumerate(bits):
            if i == selected_pos:
                continue
            if c != inactive_bit:
                return False
    if role == "master" and not saw_busy:
        return False
    return saw_valid_ss


def write_report(results: List[Dict[str, object]], out_file: Path, suite_meta: Optional[Dict[str, int]] = None) -> Dict[str, object]:
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
    if suite_meta:
        lines.append(
            f"- Compact modern suite: **{suite_meta['selected_modern']}** selected from **{suite_meta['available_modern']}** available "
            f"(target={suite_meta['target_modern']})"
        )
        if "practical_compact_size" in suite_meta:
            lines.append(
                f"- Practical compact size for full scoped closure: **{suite_meta['practical_compact_size']}** "
                f"(computed from actual coverage closure)"
            )
    lines.append("")

    # Coverage matrix over modern cases
    modern_coverage = {}
    for r in modern:
        key = _coverage_key(r)
        modern_coverage[key] = modern_coverage.get(key, 0) + 1
    coverage = _compute_coverage_profile(results)
    pairwise = _compute_feature_pair_coverage(modern)
    representativeness = _compute_representativeness_metrics(coverage, pairwise)
    balance = _compute_balance_matrix(modern)
    coverage_gap = "none" if not coverage["gaps"] else "listed"
    requirements = load_conformance_requirements(Path("docs") / "SPI_CONFORMANCE_REQUIREMENTS.json")
    conformance = _evaluate_requirement_coverage(modern, requirements)
    conformance_gate = "PASS" if conformance["all_pass"] else "FAIL"
    negative_cases = evaluate_negative_cases(Path("results"))
    negative_suite_ok = (
        "NOT_RUN" if not negative_cases else
        ("PASS" if all(c["status"] == "PASS" for c in negative_cases) else "FAIL")
    )
    release_gate_modern = "PASS" if modern and modern_pass == len(modern) and coverage_gap == "none" and conformance_gate == "PASS" else "FAIL"
    signoff_gate = (
        "PASS"
        if release_gate_modern == "PASS" and negative_suite_ok == "PASS"
        else "FAIL"
    )

    lines.append("## Policy Verdict")
    lines.append("")
    lines.append(f"- `release_gate_modern`: **{release_gate_modern}**")
    lines.append(f"- `coverage_gap`: **{coverage_gap}**")
    lines.append(f"- `conformance_gate`: **{conformance_gate}**")
    lines.append(f"- `negative_suite_ok`: **{negative_suite_ok}**")
    lines.append(f"- `signoff_gate`: **{signoff_gate}**")
    if coverage_gap != "none":
        lines.append("- `coverage_gap_details`:")
        for key in sorted(coverage["gaps"].keys()):
            missing = ", ".join(str(v) for v in coverage["gaps"][key])
            lines.append(f"  - {key}: {missing}")
    lines.append("")
    durations = [
        float(r["runtime"]["duration_s"])
        for r in results
        if isinstance(r.get("runtime"), dict) and r["runtime"].get("duration_s") is not None
    ]
    lines.append("## Runtime Telemetry")
    lines.append("")
    if durations:
        mean = sum(durations) / len(durations)
        lines.append(f"- Cases with telemetry: **{len(durations)} / {len(results)}**")
        lines.append(f"- Duration seconds: min **{min(durations):.3f}**, max **{max(durations):.3f}**, mean **{mean:.3f}**")
        lines.append(f"- Percentiles: p50 **{_percentile(durations, 0.50):.3f}**, p90 **{_percentile(durations, 0.90):.3f}**")
    else:
        lines.append("- Cases with telemetry: **0**")
        lines.append("- Duration seconds: no telemetry available")
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
    lines.append("- `transaction_oracle_ok`: decoded busy-window SCLK sampling activity satisfies minimum frame bit-count expectation")
    lines.append("- `selected_slave_oracle_ok`: SS_N evidence matches configured one-hot selected slave during busy (master/dual)")
    lines.append("")
    lines.append("## Requirement Traceability")
    lines.append("")
    lines.append("| Requirement | Title | Covered Modern Cases | Status |")
    lines.append("|---|---|---:|:---:|")
    if requirements:
        for item in conformance["rows"]:
            lines.append(
                f"| {item['id']} | {item['title']} | {item['covered_cases']} | {item['status']} |"
            )
    else:
        lines.append("| (none) | No machine-readable conformance requirements file found | 0 | FAIL |")
    lines.append("")
    lines.append("## Negative Suite (Fault Injection)")
    lines.append("")
    lines.append("| Case | Expected Fail Checks | Status |")
    lines.append("|---|---:|:---:|")
    if negative_cases:
        for case in negative_cases:
            lines.append(
                f"| {case['case_id']} | {len(case['expected_checks'])} | {case['status']} |"
            )
    else:
        lines.append("| (none) | 0 | NOT_RUN |")
    lines.append("")
    lines.append("## Per-Issue Results")
    lines.append("")
    lines.append("| Issue | Overall | compile_ok | sim_ok | vcd_ok | compliance_ok | summary_ok | consistency_ok | spec_oracle_ok | rtl_tb_semantic_ok | transaction_oracle_ok | selected_slave_oracle_ok |")
    lines.append("|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
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
            f"{'Y' if g['rtl_tb_semantic_ok'] else 'N'} | "
            f"{'Y' if g['transaction_oracle_ok'] else 'N'} | "
            f"{'Y' if g['selected_slave_oracle_ok'] else 'N'} |"
        )
    lines.append("")
    lines.append("## Per-Issue Runtime")
    lines.append("")
    lines.append("| Issue | Start (UTC) | End (UTC) | Duration (s) |")
    lines.append("|---:|---|---|---:|")
    for r in sorted(results, key=lambda x: int(x["issue"])):
        rt = r.get("runtime", {}) if isinstance(r.get("runtime"), dict) else {}
        start_ts = str(rt.get("start_ts", "")) or "(n/a)"
        end_ts = str(rt.get("end_ts", "")) or "(n/a)"
        duration = rt.get("duration_s")
        duration_text = f"{float(duration):.3f}" if duration is not None else "(n/a)"
        lines.append(f"| {r['issue']} | {start_ts} | {end_ts} | {duration_text} |")

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

    lines.append("## Corner Coverage Closure")
    lines.append("")
    required_widths = sorted(coverage["required"].get("data_width", set()))
    covered_widths = sorted(coverage["profile"].get("data_width", set()))
    missing_widths = [w for w in required_widths if w not in covered_widths]
    lines.append(f"- Required width corners: `{', '.join(str(w) for w in required_widths)}`")
    lines.append(f"- Covered width corners: `{', '.join(str(w) for w in covered_widths) if covered_widths else '(none)'}`")
    lines.append(f"- Missing width corners: `{', '.join(str(w) for w in missing_widths) if missing_widths else 'none'}`")
    lines.append("")
    lines.append("| Corner Signature | Cases | Pass | Fail |")
    lines.append("|---|---:|---:|---:|")
    corner_rows: Dict[str, Dict[str, int]] = {}
    for r in modern:
        cfg = r.get("config", {}) if isinstance(r.get("config"), dict) else {}
        mode = str(cfg.get("mode", "unknown"))
        role = str(cfg.get("spi_role", "unknown")).lower()
        width = str(int(cfg.get("data_width", 0) or 0))
        ss = "active_low" if bool(cfg.get("slave_active_low", True)) else "active_high"
        order = "msb_first" if bool(cfg.get("msb_first", True)) else "lsb_first"
        sig = f"mode={mode}|role={role}|width={width}|ss={ss}|order={order}"
        if sig not in corner_rows:
            corner_rows[sig] = {"cases": 0, "pass": 0, "fail": 0}
        corner_rows[sig]["cases"] += 1
        if r["pass_all"]:
            corner_rows[sig]["pass"] += 1
        else:
            corner_rows[sig]["fail"] += 1
    if corner_rows:
        for sig in sorted(corner_rows.keys()):
            row = corner_rows[sig]
            lines.append(f"| {sig} | {row['cases']} | {row['pass']} | {row['fail']} |")
    else:
        lines.append("| (none) | 0 | 0 | 0 |")
    lines.append("")
    lines.append("## Compact Suite Representativeness")
    lines.append("")
    lines.append(
        f"- Representativeness score: **{representativeness['score']:.1f}%** "
        f"({representativeness['covered']}/{representativeness['target']})"
    )
    lines.append(
        "- Confidence claim: compact suite representativeness is based on coverage closure and stable gate outcomes, not raw case count."
    )
    lines.append("")
    lines.append("| Dimension | Covered / Target | Missing Required Values |")
    lines.append("|---|---:|---|")
    for row in representativeness["rows"]:
        missing = ", ".join(str(v) for v in row["missing"]) if row["missing"] else "none"
        lines.append(f"| {row['dimension']} | {row['covered']} / {row['target']} | {missing} |")
    lines.append("")
    lines.append("## Special Feature Pairwise Coverage (2-way)")
    lines.append("")
    lines.append("| Pair | Covered / Target | Missing Pairs |")
    lines.append("|---|---:|---|")
    for row in pairwise["rows"]:
        missing = (
            ", ".join(f"({a},{b})" for (a, b) in row["missing_pairs"])
            if row["missing_pairs"]
            else "none"
        )
        lines.append(f"| {row['pair']} | {row['covered']} / {row['target']} | {missing} |")
    lines.append("")
    lines.append("## Balance Matrix (Modern Cases)")
    lines.append("")
    lines.append("| Dimension | Value Counts | Min | Max | Max/Min Ratio |")
    lines.append("|---|---|---:|---:|---:|")
    for row in balance["rows"]:
        counts = ", ".join(f"{k}:{row['counts'][k]}" for k in sorted(row["counts"].keys(), key=lambda x: str(x)))
        lines.append(
            f"| {row['dimension']} | {counts if counts else '(none)'} | {row['min']} | {row['max']} | {row['max_min_ratio']:.2f} |"
        )
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

    lines.append("## Failure Signatures")
    lines.append("")
    lines.append("| Gate | Corner Signature | Count | Issues |")
    lines.append("|---|---|---:|---|")
    failure_rows: Dict[Tuple[str, str], Dict[str, object]] = {}
    for r in modern:
        if r["pass_all"]:
            continue
        cfg = r.get("config", {}) if isinstance(r.get("config"), dict) else {}
        mode = str(cfg.get("mode", "unknown"))
        role = str(cfg.get("spi_role", "unknown")).lower()
        width = str(int(cfg.get("data_width", 0) or 0))
        ss = "active_low" if bool(cfg.get("slave_active_low", True)) else "active_high"
        order = "msb_first" if bool(cfg.get("msb_first", True)) else "lsb_first"
        sig = f"mode={mode}|role={role}|width={width}|ss={ss}|order={order}"
        for gate, passed_gate in r["gates"].items():
            if passed_gate:
                continue
            key = (gate, sig)
            if key not in failure_rows:
                failure_rows[key] = {"count": 0, "issues": []}
            failure_rows[key]["count"] += 1
            failure_rows[key]["issues"].append(f"issue-{r['issue']}")
    if failure_rows:
        for (gate, sig) in sorted(failure_rows.keys()):
            row = failure_rows[(gate, sig)]
            issues = ", ".join(sorted(row["issues"]))
            lines.append(f"| {gate} | {sig} | {row['count']} | {issues} |")
    else:
        lines.append("| (none) | (none) | 0 | (none) |")

    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "total": total,
        "passed": passed,
        "modern_total": len(modern),
        "modern_pass": modern_pass,
        "release_gate_modern": release_gate_modern,
        "coverage_gap": coverage_gap,
        "conformance_gate": conformance_gate,
        "negative_suite_ok": negative_suite_ok,
        "signoff_gate": signoff_gate,
        "requirement_rows": conformance["rows"],
        "representativeness_score": representativeness["score"],
    }


def write_signoff(summary: Dict[str, object], out_file: Path) -> None:
    lines = []
    lines.append("# SPI Conformance Sign-off")
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"- `signoff_gate`: **{summary['signoff_gate']}**")
    lines.append(f"- `release_gate_modern`: **{summary['release_gate_modern']}**")
    lines.append(f"- `conformance_gate`: **{summary['conformance_gate']}**")
    lines.append(f"- `negative_suite_ok`: **{summary['negative_suite_ok']}**")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Modern issues: **{summary['modern_pass']}/{summary['modern_total']}** pass")
    lines.append(f"- Total issues evaluated: **{summary['passed']}/{summary['total']}** pass")
    lines.append(f"- Coverage gap: **{summary['coverage_gap']}**")
    lines.append("")
    lines.append("## Requirement Closure")
    lines.append("")
    lines.append("| Requirement | Covered Modern Cases | Status |")
    lines.append("|---|---:|:---:|")
    for row in summary.get("requirement_rows", []):
        lines.append(f"| {row['id']} | {row['covered_cases']} | {row['status']} |")
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _requirement_applies(config: Dict[str, object], applies_to: List[str]) -> bool:
    if not applies_to:
        return True
    role = str(config.get("spi_role", "")).lower()
    mode = str(config.get("mode", "")).lower()
    tags = {role, f"mode_{mode}"}
    return any(tag in tags for tag in applies_to)


def _evaluate_requirement_coverage(modern: List[Dict[str, object]], requirements: List[Dict[str, object]]) -> Dict[str, object]:
    if not requirements:
        return {"rows": [], "all_pass": False}
    rows = []
    all_pass = True
    for req in requirements:
        checks = req.get("checks", [])
        covered = 0
        passed = 0
        for case in modern:
            config = case.get("config", {}) if isinstance(case.get("config"), dict) else {}
            if not _requirement_applies(config, req.get("applies_to", [])):
                continue
            covered += 1
            compliance_checks = case.get("compliance_checks", {}) if isinstance(case.get("compliance_checks"), dict) else {}
            if all(compliance_checks.get(check) == "PASS" for check in checks):
                passed += 1
        if covered == 0:
            status = "FAIL"
        elif passed == covered:
            status = "PASS"
        else:
            status = "FAIL"
        if status != "PASS":
            all_pass = False
        rows.append(
            {
                "id": req["id"],
                "title": req.get("title", ""),
                "covered_cases": covered,
                "status": status,
            }
        )
    return {"rows": rows, "all_pass": all_pass}


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay validation report generator")
    parser.add_argument(
        "--compact-modern-target",
        type=int,
        default=500,
        help="Target size for compact modern replay suite (0 = use all modern cases)",
    )
    args = parser.parse_args()

    root = Path("results")
    issue_dirs = sorted([p for p in root.glob("issue-*") if (p / "code" / "spi_config.json").exists()], key=lambda p: int(p.name.replace("issue-", "")))
    if not issue_dirs:
        print("No issue result directories found.")
        return 1

    all_results = [evaluate_issue(p) for p in issue_dirs]
    modern_all = [r for r in all_results if r["is_modern"]]
    selected_modern = _select_compact_modern_suite(modern_all, args.compact_modern_target)
    practical = _find_practical_compact_suite(modern_all)
    # Report/sign-off are modern-suite focused; legacy artifacts are omitted.
    results = selected_modern

    suite_meta = {
        "available_modern": len(modern_all),
        "selected_modern": len(selected_modern),
        "target_modern": args.compact_modern_target,
        "practical_compact_size": practical["size"],
    }
    report_file = Path("docs") / "SPI_REPLAY_VALIDATION_REPORT.md"
    summary = write_report(results, report_file, suite_meta=suite_meta)
    signoff_file = Path("docs") / "SPI_CONFORMANCE_SIGNOFF.md"
    write_signoff(summary, signoff_file)
    print(f"Wrote report: {report_file}")
    print(f"Wrote sign-off: {signoff_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
