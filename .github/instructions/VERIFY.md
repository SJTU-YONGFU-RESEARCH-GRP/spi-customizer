---
applyTo: "results/issue-*/logs/protocol_compliance.md,results/issue-*/logs/**"
---

# Agent instructions — SPI Verification / Compliance (issue template 6)

> **Trigger**: issue opened with label `verification` (template `6-spi-verification-request.yml`).

## Your role

You are acting as a protocol-compliance engineer. The user has listed **protocol properties**
that must be proven with simulation evidence. Your job is to (re-)generate or reuse an existing
SPI core, run simulation, and map each acceptance criterion to a concrete pass/fail check
backed by VCD-derived data.

Do **not** auto-run any CI script; do all work yourself using your available tools.

## Mandatory sequence

### 1 · Ingest

- Read the issue body and extract:
  - what must be verified (the acceptance criteria list)
  - configuration under test (mode, data\_width, num\_slaves, slave\_select, data\_order, spi\_role, features)
  - reference issue number (if provided — reuse its artifacts where possible)
- Identify any gaps: acceptance criteria that are not checkable from a VCD signal listing alone
  (e.g. glitch-free clock, metastability). State these gaps explicitly.

### 2 · Obtain RTL + testbench

If a reference issue is provided and its artifacts exist under `results/issue-<ref>/code/`, reuse them.
Otherwise generate fresh files following the same steps as in `.github/instructions/SPEC.md` §2.

Ensure `results/issue-<n>/code/spi_config.json` captures the configuration under test.

### 3 · Compile

```bash
iverilog -g2012 \
  -o results/issue-<n>/data/spi_simulation \
  results/issue-<n>/code/<core>.v \
  results/issue-<n>/code/<tb>.v \
  2>&1 | tee results/issue-<n>/logs/compilation.log
```

Fix any compilation errors before proceeding.

### 4 · Simulate

```bash
VCD_FILE=results/issue-<n>/data/spi_waveform.vcd \
  vvp -n results/issue-<n>/data/spi_simulation \
  2>&1 | tee results/issue-<n>/logs/simulation.log
```

A VCD **must** exist before writing any compliance result.

### 5 · Write the compliance report

Produce `results/issue-<n>/logs/protocol_compliance.md` using this structure:

```markdown
# Protocol Compliance Report — Issue #<n>

## Configuration
| Parameter | Value |
|-----------|-------|
| Mode      | …     |
| Data width| …     |
| …         | …     |

## Checks

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | SS_n asserted before first sampling edge | PASS | VCD: ss_n goes low at 120 ns, first SCLK sampling edge at 160 ns |
| 2 | MOSI changes on non-sampling edge | PASS | VCD: MOSI transitions at 140 ns (falling edge), sampled at 160 ns (rising) |
| … | … | PASS / FAIL / NOT_RUN | … |

## Notes
- Gaps or NOT_RUN checks with explanation.
```

Every row must cite **actual VCD timestamps or signal values** — never inferred or assumed.
If a check cannot be automated, mark it `NOT_RUN` and explain what evidence would be needed.

### 6 · Write the run manifest

`results/issue-<n>/logs/run_manifest.json` — same schema as SPEC.md §6.

### 7 · Comment on the issue

Post a comment that includes:

1. **What was verified**: restate the acceptance criteria from the issue.
2. **Compliance table**: copy the check table from `protocol_compliance.md`.
3. **Overall verdict**: PASS (all checks passed) / PARTIAL (some not-run or not-checkable) / FAIL.
4. **Artifact paths**: `code/`, `data/spi_waveform.vcd`, `logs/protocol_compliance.md`.
5. If simulation did not run: state which gate failed and link to the log.

## Quality gates

| Gate | Requirement |
|------|-------------|
| VCD exists | `results/issue-<n>/data/spi_waveform.vcd` non-empty |
| Each criterion mapped | Every acceptance criterion has an entry in the compliance table |
| Evidence cited | Every PASS/FAIL row cites a VCD timestamp or signal value |
| Manifest written | `results/issue-<n>/logs/run_manifest.json` present |
