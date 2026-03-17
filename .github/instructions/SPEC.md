---
applyTo: "results/issue-*/code/**/*.v,results/issue-*/logs/**"
---

# Agent instructions — SPI Spec / Generate (issue template 5)

> **Trigger**: issue opened with label `spec-intent` (template `5-spi-spec-intent.yml`).

## Your role

You are acting as an RTL engineer. The user has described **intent** (not just parameters).
Your job is to translate that intent into a working SPI core + testbench, simulate it, and
report explicit protocol evidence. Do **not** auto-run any CI script; do all work yourself
using your available tools (`bash`, file editors, git).

## Mandatory sequence

Follow this sequence exactly and do not skip steps.

### 1 · Ingest

- Read the issue body in full.
- Extract:
  - design intent (plain-language description)
  - transaction examples (expected MOSI/MISO behaviour)
  - parameters: mode, data\_width, num\_slaves, slave\_select, data\_order, spi\_role, features, test\_duration
  - acceptance criteria (what must be proven)
- Resolve any ambiguity **explicitly** in your issue comment. Never silently guess.
- Normalise the configuration by writing `results/issue-<n>/code/spi_config.json`.

### 2 · Generate RTL and testbench

Use `scripts/verilog_generator.py` (via `python3`) to render the RTL and testbench:

```bash
python3 scripts/verilog_generator.py  # or call VerilogGenerator directly
```

Files to produce under `results/issue-<n>/code/`:

| File | Description |
|------|-------------|
| `spi_<role>_mode<M>_<W>bit.v` | SPI core (RTL) |
| `spi_<role>_tb.v` | Verilog testbench |
| `spi_config.json` | Parsed configuration |

Key generation rules:
- `DEFAULT_DATA_VALUE` must be **width-correct**: an 8-bit design must use `8'hA5`, not `16'hA5A5`
  (a 16-bit literal in an 8-bit context causes truncation warnings). The helper
  `compute_scaled_default_data_value()` in `verilog_generator.py` handles this — ensure it is called.
- Dual-role testbenches may use `join_any` / `disable fork` (SystemVerilog 2012).
  Always compile with `iverilog -g2012`.

### 3 · Compile (hard gate)

```bash
iverilog -g2012 \
  -o results/issue-<n>/data/spi_simulation \
  results/issue-<n>/code/<core>.v \
  results/issue-<n>/code/<tb>.v \
  2>&1 | tee results/issue-<n>/logs/compilation.log
```

- Write the **exact command** and its output to `results/issue-<n>/logs/compilation.log`.
- Do **not** proceed to simulation if compilation fails. Fix the issue first.

### 4 · Simulate

```bash
VCD_FILE=results/issue-<n>/data/spi_waveform.vcd \
  vvp -n results/issue-<n>/data/spi_simulation \
  2>&1 | tee results/issue-<n>/logs/simulation.log
```

- Write the **exact command** and output to `results/issue-<n>/logs/simulation.log`.
- A VCD must be produced at `results/issue-<n>/data/spi_waveform.vcd`.
- Do **not** claim compliance unless this file exists.

### 5 · Analyse and report

After a successful simulation:

```bash
python3 scripts/vcd_parser.py  # or call VcdParser / SummaryGenerator / ProtocolComplianceChecker directly
```

Produce:

| File | Description |
|------|-------------|
| `results/issue-<n>/logs/SUMMARY.md` | Human-readable waveform summary |
| `results/issue-<n>/logs/protocol_compliance.md` | Explicit pass/fail checks tied to VCD evidence |
| `results/issue-<n>/logs/run_manifest.json` | Traceability: issue hash, config, files, tool versions |
| `results/issue-<n>/graphs/*.png` | Signal plots (if matplotlib available) |

### 6 · Write a run manifest

`results/issue-<n>/logs/run_manifest.json` must contain:

```json
{
  "issue_number": <n>,
  "issue_body_sha256": "<sha256 of raw issue body>",
  "config": { ... },
  "generated_files": { "core_file": "...", "tb_file": "..." },
  "tools": { "iverilog": "<version>", "vvp": "<version>", "python": "<version>" }
}
```

### 7 · Comment on the issue

Post a comment that includes:

1. **Detected intent** (one paragraph restating what you understood).
2. **Protocol behaviour** derived from mode/role/width (edge semantics, SS\_n framing, bit order).
3. **Compliance check table** (from `protocol_compliance.md`) with pass / fail / not-run per check.
4. **Paths to key artifacts** (`code/`, `logs/`, `data/`, `graphs/`).
5. If simulation could not run: state **exactly** which gate failed and link to the relevant log.

## Quality gates

| Gate | Requirement |
|------|-------------|
| RTL generated | `results/issue-<n>/code/*.v` exists and compiles cleanly with `-g2012` |
| Testbench generated | `results/issue-<n>/code/*_tb.v` exists |
| Simulation ran | `results/issue-<n>/data/spi_waveform.vcd` exists and is non-empty |
| Compliance reported | `results/issue-<n>/logs/protocol_compliance.md` maps each acceptance criterion to evidence |
| Manifest written | `results/issue-<n>/logs/run_manifest.json` exists with issue hash and tool versions |
