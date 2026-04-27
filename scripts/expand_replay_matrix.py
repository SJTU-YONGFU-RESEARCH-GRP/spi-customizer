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


def main() -> int:
    parser = argparse.ArgumentParser(description="Expand replay matrix over numeric parameter space.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--width-start", type=int, default=1, help="Start data width (inclusive).")
    parser.add_argument("--width-end", type=int, default=32, help="End data width (inclusive).")
    parser.add_argument("--max-cases", type=int, default=24, help="Maximum number of new cases to generate this run.")
    parser.add_argument("--start-issue-id", type=int, default=0, help="Override issue numbering start (0 = auto).")
    parser.add_argument("--dry-run", action="store_true", help="Print planned cases without generating.")
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

    existing = _load_existing_signatures(results_dir)
    targets = _build_target_signatures(args.width_start, args.width_end)
    missing = [sig for sig in targets if sig not in existing]
    planned = missing[: args.max_cases]

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
