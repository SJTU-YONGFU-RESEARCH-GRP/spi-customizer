#!/usr/bin/env python3
"""
Deterministic replay-matrix expander for numeric-space conformance coverage.

Builds a full cartesian target over:
  - mode: 0..3
  - role: master/slave/dual
  - data_width: configurable integer range
  - ss_polarity: active_low/active_high
  - bit_order: msb_first/lsb_first

Then emits only missing signatures by scanning existing results/issue-*/code/spi_config.json.
"""

import argparse
import itertools
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


Role = str
SSPolarity = str
BitOrder = str
Signature = Tuple[int, Role, int, SSPolarity, BitOrder]


def _signature_from_config(config: Dict[str, object]) -> Optional[Signature]:
    try:
        mode = int(config.get("mode", 0))
        role = str(config.get("spi_role", "")).strip().lower()
        data_width = int(config.get("data_width", 0))
        active_low = bool(config.get("slave_active_low", True))
        msb_first = bool(config.get("msb_first", True))
    except (TypeError, ValueError):
        return None
    if role not in {"master", "slave", "dual"}:
        return None
    if mode not in {0, 1, 2, 3} or data_width <= 0:
        return None
    ss = "active_low" if active_low else "active_high"
    order = "msb_first" if msb_first else "lsb_first"
    return (mode, role, data_width, ss, order)


def _load_existing_signatures(results_dir: Path) -> Set[Signature]:
    signatures: Set[Signature] = set()
    for issue_dir in sorted(results_dir.glob("issue-*")):
        config_path = issue_dir / "code" / "spi_config.json"
        if not config_path.exists():
            continue
        try:
            config = json.loads(config_path.read_text(encoding="utf-8", errors="ignore"))
        except json.JSONDecodeError:
            continue
        sig = _signature_from_config(config)
        if sig is not None:
            signatures.add(sig)
    return signatures


def _load_existing_configs(results_dir: Path) -> List[Dict[str, object]]:
    configs: List[Dict[str, object]] = []
    for issue_dir in sorted(results_dir.glob("issue-*")):
        config_path = issue_dir / "code" / "spi_config.json"
        if not config_path.exists():
            continue
        try:
            config = json.loads(config_path.read_text(encoding="utf-8", errors="ignore"))
        except json.JSONDecodeError:
            continue
        if isinstance(config, dict):
            configs.append(config)
    return configs


def _build_target_signatures(width_start: int, width_end: int) -> List[Signature]:
    modes = [0, 1, 2, 3]
    roles: List[Role] = ["master", "slave", "dual"]
    polarities: List[SSPolarity] = ["active_low", "active_high"]
    orders: List[BitOrder] = ["msb_first", "lsb_first"]
    widths = list(range(width_start, width_end + 1))
    targets = list(itertools.product(modes, roles, widths, polarities, orders))
    return sorted(targets, key=lambda x: (x[2], x[0], x[1], x[3], x[4]))


def _role_label(role: Role) -> str:
    if role == "master":
        return "Master"
    if role == "slave":
        return "Slave"
    return "Dual (both master and slave)"


def _build_issue_body(sig: Signature, case_index: int) -> str:
    mode, role, width, ss, order = sig
    active_low = ss == "active_low"
    msb_first = order == "msb_first"

    if role == "slave":
        num_slaves = 3
        selected_slave = 0
    else:
        num_slaves = 5
        selected_slave = 0 if (case_index % 2 == 0) else min(3, num_slaves - 1)

    pattern_seed = ["A5A5", "FFFF", "0000", "5555"][case_index % 4]
    duration = ["brief", "standard", "comprehensive"][case_index % 3].capitalize()

    return f"""## SPI Configuration
### SPI Mode
{mode}

### Data Width
{width}

### Number of Slaves
{num_slaves}

### Selected Slave Index
{selected_slave}

### Slave Select Behavior
{"Active Low" if active_low else "Active High"}

### Data Order
{"MSB First" if msb_first else "LSB First"}

### SPI Role
{_role_label(role)}

### Test Duration
{duration}

### Default Data
Enabled

### Data Pattern
{pattern_seed}

### Special Features
- [x] Interrupt Support
- [{'x' if (case_index % 2 == 0) else ' '}] FIFO Buffers
- [{'x' if (case_index % 3 == 0) else ' '}] DMA Support
- [{'x' if (case_index % 4 == 0) else ' '}] Multi-master Support

### Testing Options
- [{'x' if (case_index % 2 == 1) else ' '}] Clock Jitter Testing
- [x] Waveform Capture
"""


def _parse_bool(value: str) -> bool:
    v = value.strip().lower()
    if v in {"1", "true", "yes", "y", "on"}:
        return True
    if v in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def _feature_flag(config: Dict[str, object], feature: str) -> bool:
    if feature == "interrupts":
        return bool(config.get("interrupts", False))
    if feature == "fifo_buffers":
        return bool(config.get("fifo_buffers", False))
    if feature == "dma_support":
        return bool(config.get("dma_support", False))
    if feature == "multi_master":
        return bool(config.get("multi_master", False))
    raise ValueError(f"Unsupported feature: {feature}")


def _has_feature_combo(configs: List[Dict[str, object]], left: str, left_val: bool, right: str, right_val: bool) -> bool:
    for cfg in configs:
        if _feature_flag(cfg, left) == left_val and _feature_flag(cfg, right) == right_val:
            return True
    return False


def _build_issue_body_with_feature_override(
    sig: Signature,
    case_index: int,
    feature_override: Optional[Dict[str, bool]] = None,
) -> str:
    mode, role, width, ss, order = sig
    active_low = ss == "active_low"
    msb_first = order == "msb_first"

    if role == "slave":
        num_slaves = 3
        selected_slave = 0
    else:
        num_slaves = 5
        selected_slave = 0 if (case_index % 2 == 0) else min(3, num_slaves - 1)

    pattern_seed = ["A5A5", "FFFF", "0000", "5555"][case_index % 4]
    duration = ["brief", "standard", "comprehensive"][case_index % 3].capitalize()

    overrides = feature_override or {}
    interrupts = overrides.get("interrupts", True)
    fifo_buffers = overrides.get("fifo_buffers", case_index % 2 == 0)
    dma_support = overrides.get("dma_support", case_index % 3 == 0)
    multi_master = overrides.get("multi_master", case_index % 4 == 0)

    return f"""## SPI Configuration
### SPI Mode
{mode}

### Data Width
{width}

### Number of Slaves
{num_slaves}

### Selected Slave Index
{selected_slave}

### Slave Select Behavior
{"Active Low" if active_low else "Active High"}

### Data Order
{"MSB First" if msb_first else "LSB First"}

### SPI Role
{_role_label(role)}

### Test Duration
{duration}

### Default Data
Enabled

### Data Pattern
{pattern_seed}

### Special Features
- [{'x' if interrupts else ' '}] Interrupt Support
- [{'x' if fifo_buffers else ' '}] FIFO Buffers
- [{'x' if dma_support else ' '}] DMA Support
- [{'x' if multi_master else ' '}] Multi-master Support

### Testing Options
- [{'x' if (case_index % 2 == 1) else ' '}] Clock Jitter Testing
- [x] Waveform Capture
"""


def _next_issue_id(results_dir: Path) -> int:
    max_id = 1001
    for issue_dir in results_dir.glob("issue-*"):
        raw = issue_dir.name.replace("issue-", "").strip()
        if raw.isdigit():
            max_id = max(max_id, int(raw))
    return max_id + 1


def _run_process_issue(repo_root: Path, issue_id: int, issue_body: str) -> int:
    env = os.environ.copy()
    env["LOCAL_ISSUE_BODY"] = issue_body
    process = subprocess.run(
        ["python3", "scripts/process_issue.py", str(issue_id)],
        cwd=repo_root,
        env=env,
        check=False,
    )
    return int(process.returncode)


def _run_replay_validation(repo_root: Path, compact_target: int) -> int:
    cmd = ["python3", "scripts/replay_validation.py", "--compact-modern-target", str(compact_target)]
    return int(subprocess.run(cmd, cwd=repo_root, check=False).returncode)


def _parse_report_policy(report_path: Path) -> Dict[str, str]:
    text = report_path.read_text(encoding="utf-8", errors="ignore") if report_path.exists() else ""
    def _extract(name: str) -> str:
        m = re.search(rf"`{re.escape(name)}`:\s+\*\*(PASS|FAIL|NOT_RUN)\*\*", text)
        return m.group(1) if m else "UNKNOWN"
    return {
        "release_gate_modern": _extract("release_gate_modern"),
        "conformance_gate": _extract("conformance_gate"),
        "negative_suite_ok": _extract("negative_suite_ok"),
        "signoff_gate": _extract("signoff_gate"),
        "coverage_gap": _extract("coverage_gap"),
    }


def _parse_missing_feature_pairs(report_path: Path) -> List[Tuple[str, bool, str, bool]]:
    text = report_path.read_text(encoding="utf-8", errors="ignore") if report_path.exists() else ""
    rows = re.findall(r"^\|\s*(interrupts|fifo_buffers|dma_support|multi_master)\s+x\s+(interrupts|fifo_buffers|dma_support|multi_master)\s+\|\s+\d+\s*/\s*\d+\s+\|\s*([^|]+)\|$", text, flags=re.MULTILINE)
    missing: List[Tuple[str, bool, str, bool]] = []
    for left, right, miss in rows:
        missing_cell = miss.strip()
        if missing_cell.lower() == "none":
            continue
        tuples = re.findall(r"\((True|False)\s*,\s*(True|False)\)", missing_cell)
        for a, b in tuples:
            missing.append((left, a == "True", right, b == "True"))
    return missing


def _parse_has_coverage_gap_details(report_path: Path) -> bool:
    text = report_path.read_text(encoding="utf-8", errors="ignore") if report_path.exists() else ""
    return "- `coverage_gap_details`:" in text


def _generate_batch(repo_root: Path, args: argparse.Namespace, feature_pair: Optional[Tuple[str, bool, str, bool]] = None) -> int:
    cmd = [
        "python3",
        "scripts/expand_replay_matrix.py",
        "--repo-root",
        str(repo_root),
        "--width-start",
        str(args.width_start),
        "--width-end",
        str(args.width_end),
        "--max-cases",
        str(1 if feature_pair else args.max_cases),
    ]
    if feature_pair:
        left, left_val, right, right_val = feature_pair
        cmd += ["--target-feature-pair", f"{left}={str(left_val).lower()},{right}={str(right_val).lower()}"]
    if args.start_issue_id > 0:
        cmd += ["--start-issue-id", str(args.start_issue_id)]
    return int(subprocess.run(cmd, cwd=repo_root, check=False).returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Expand replay matrix over numeric parameter space.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--width-start", type=int, default=1, help="Start data width (inclusive).")
    parser.add_argument("--width-end", type=int, default=32, help="End data width (inclusive).")
    parser.add_argument("--max-cases", type=int, default=24, help="Maximum number of new cases to generate this run.")
    parser.add_argument("--start-issue-id", type=int, default=0, help="Override issue numbering start (0 = auto).")
    parser.add_argument(
        "--target-feature-pair",
        default="",
        help="Optional feature pair target in form featureA=value,featureB=value (e.g. interrupts=false,fifo_buffers=true).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned cases without generating.")
    parser.add_argument("--auto-close", action="store_true", help="Iteratively generate until coverage closure while gates stay PASS.")
    parser.add_argument("--max-iterations", type=int, default=8, help="Maximum auto-close iterations.")
    parser.add_argument("--replay-compact-target", type=int, default=500, help="Compact target passed to replay_validation during auto-close.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    results_dir = repo_root / "results"
    if not results_dir.exists():
        print(f"Missing results directory: {results_dir}")
        return 1
    if args.width_start <= 0 or args.width_end < args.width_start:
        print("Invalid width range.")
        return 1
    if args.max_cases <= 0:
        print("max-cases must be positive.")
        return 1
    if args.max_iterations <= 0:
        print("max-iterations must be positive.")
        return 1
    supported_features = {"interrupts", "fifo_buffers", "dma_support", "multi_master"}

    if args.auto_close:
        report_path = repo_root / "docs" / "SPI_REPLAY_VALIDATION_REPORT.md"
        for iteration in range(1, args.max_iterations + 1):
            print(f"\n=== Auto-close iteration {iteration}/{args.max_iterations} ===")
            rc = _run_replay_validation(repo_root, args.replay_compact_target)
            if rc != 0:
                print("Replay validation failed; stopping auto-close.")
                return 1
            policy = _parse_report_policy(report_path)
            if policy["release_gate_modern"] != "PASS" or policy["conformance_gate"] != "PASS" or policy["negative_suite_ok"] != "PASS":
                print(f"Gate regression detected: {policy}")
                return 1
            pair_gaps = _parse_missing_feature_pairs(report_path)
            has_cov_gap = _parse_has_coverage_gap_details(report_path)
            if not pair_gaps and not has_cov_gap:
                print("Coverage closure reached with stable gates.")
                return 0
            next_pair = pair_gaps[0] if pair_gaps else None
            if next_pair:
                print(
                    "Generating targeted pair-closure case for "
                    f"{next_pair[0]}={next_pair[1]}, {next_pair[2]}={next_pair[3]}"
                )
            else:
                print("Generating numeric-space closure batch.")
            gen_rc = _generate_batch(repo_root, args, feature_pair=next_pair)
            if gen_rc != 0:
                print("Generation batch failed; stopping auto-close.")
                return 1
        print("Auto-close stopped at max iterations before closure.")
        return 1

    existing = _load_existing_signatures(results_dir)
    existing_configs = _load_existing_configs(results_dir)
    targets = _build_target_signatures(args.width_start, args.width_end)
    missing = [sig for sig in targets if sig not in existing]
    planned = missing[: args.max_cases]
    feature_override: Optional[Dict[str, bool]] = None

    if args.target_feature_pair.strip():
        parts = [p.strip() for p in args.target_feature_pair.split(",") if p.strip()]
        if len(parts) != 2 or any("=" not in p for p in parts):
            print("Invalid --target-feature-pair format. Use featureA=value,featureB=value")
            return 1
        parsed: Dict[str, bool] = {}
        for part in parts:
            key, raw_val = [s.strip() for s in part.split("=", 1)]
            if key not in supported_features:
                print(f"Unsupported feature in pair target: {key}")
                return 1
            parsed[key] = _parse_bool(raw_val)
        keys = list(parsed.keys())
        left, right = keys[0], keys[1]
        left_val, right_val = parsed[left], parsed[right]
        if _has_feature_combo(existing_configs, left, left_val, right, right_val):
            print(
                "Target feature pair already covered by existing cases: "
                f"{left}={left_val}, {right}={right_val}"
            )
            return 0
        print(
            "Target feature pair missing and will be generated: "
            f"{left}={left_val}, {right}={right_val}"
        )
        feature_override = parsed
        if not planned:
            # Numeric matrix may already be closed; generate one deterministic targeted case anyway.
            planned = targets[:1]

    print(f"Target signatures: {len(targets)}")
    print(f"Existing signatures: {len(existing)}")
    print(f"Missing signatures: {len(missing)}")
    print(f"Planned this run: {len(planned)}")
    if not planned:
        print("No missing signatures to generate.")
        return 0

    for idx, sig in enumerate(planned):
        mode, role, width, ss, order = sig
        print(f"  - mode={mode} role={role} width={width} ss={ss} order={order}")

    if args.dry_run:
        return 0

    next_issue = args.start_issue_id if args.start_issue_id > 0 else _next_issue_id(results_dir)
    failures = 0
    for idx, sig in enumerate(planned):
        issue_id = next_issue + idx
        if feature_override:
            body = _build_issue_body_with_feature_override(sig, idx, feature_override=feature_override)
        else:
            body = _build_issue_body(sig, idx)
        print(f"\n=== Generating issue-{issue_id} ===")
        rc = _run_process_issue(repo_root, issue_id, body)
        if rc != 0:
            failures += 1
            print(f"issue-{issue_id} failed with code {rc}")
        else:
            print(f"issue-{issue_id} completed")

    if failures:
        print(f"Completed with failures: {failures}/{len(planned)}")
        return 1
    print(f"Generated {len(planned)} deterministic replay-matrix cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
