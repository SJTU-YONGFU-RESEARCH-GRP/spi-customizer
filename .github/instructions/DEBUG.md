---
applyTo: "results/issue-*/logs/triage.md,results/issue-*/logs/**"
---

# Agent instructions — SPI Debug / Triage (issue template 7)

> **Trigger**: issue opened with label `debug` (template `7-spi-debug-request.yml`).

## Your role

You are acting as a debug engineer. The user has observed incorrect SPI behaviour
(simulation or hardware-like trace). Your job is to:

1. Localise the root cause to one of: parsing, template rendering, RTL logic, testbench logic,
   simulation environment, post-processing.
2. Produce a minimal, well-justified fix.
3. Show before/after evidence from simulation.

Do **not** auto-run any CI script; do all work yourself using your available tools.

## Mandatory sequence

### 1 · Ingest

- Read the issue body and extract:
  - symptom (observed wrong behaviour)
  - expected vs observed (concrete signal values, timestamps, data words if provided)
  - reference issue number (reuse its artifacts if present)
  - configuration under test
  - any pasted log excerpts or VCD pointers

### 2 · Reproduce

Attempt to reproduce the failure using the reference issue's artifacts (or generate fresh ones):

```bash
iverilog -g2012 \
  -o results/issue-<n>/data/spi_simulation \
  results/issue-<n>/code/<core>.v \
  results/issue-<n>/code/<tb>.v \
  2>&1 | tee results/issue-<n>/logs/compilation.log

VCD_FILE=results/issue-<n>/data/spi_waveform.vcd \
  vvp -n results/issue-<n>/data/spi_simulation \
  2>&1 | tee results/issue-<n>/logs/simulation.log
```

Parse the simulation log and VCD to confirm whether the symptom is reproducible.

### 3 · Triage

Write `results/issue-<n>/logs/triage.md` with:

```markdown
# Triage Report — Issue #<n>

## Symptom
<one-sentence restatement>

## Root cause
<localised cause: parsing / template / RTL / testbench / sim env / post-processing>
<explanation — cite the specific file, line, or signal>

## Minimal repro
<smallest command sequence that reliably shows the bug>

## Fix
<description of the change made; reference file paths and line numbers>

## Before / after evidence
| Metric | Before fix | After fix |
|--------|-----------|-----------|
| … | … | … |
```

Every claim must be backed by log output or VCD signal values — not conjecture.

### 4 · Apply fix

Make the smallest change that corrects the issue without breaking unrelated behaviour:

- If the bug is in RTL/TB: edit the Verilog file under `results/issue-<n>/code/` (or the template
  if the template itself is wrong) and re-render.
- If the bug is in a generator script or template: fix the script/template, re-render, and note
  that the change affects all future generations.
- If the bug is in post-processing: fix `scripts/vcd_parser.py` or related script.

### 5 · Verify fix

Re-run compile + simulation and confirm the symptom is gone:

```bash
iverilog -g2012 \
  -o results/issue-<n>/data/spi_simulation \
  results/issue-<n>/code/<core>.v \
  results/issue-<n>/code/<tb>.v \
  2>&1 | tee results/issue-<n>/logs/compilation.log

VCD_FILE=results/issue-<n>/data/spi_waveform.vcd \
  vvp -n results/issue-<n>/data/spi_simulation \
  2>&1 | tee results/issue-<n>/logs/simulation.log
```

Fill in the "After fix" column in `triage.md` with concrete evidence from this run.

### 6 · Write the run manifest

`results/issue-<n>/logs/run_manifest.json` — same schema as SPEC.md §6.

### 7 · Comment on the issue

Post a comment that includes:

1. **Detected symptom**: restate what you understood from the issue.
2. **Root cause**: one-sentence diagnosis (localised component and why it fails).
3. **Fix applied**: file(s) changed and what changed.
4. **Before / after table**: from `triage.md`.
5. **How to verify**: exact commands to reproduce the fixed run.
6. **Artifact paths**: `logs/triage.md`, `logs/compilation.log`, `logs/simulation.log`.

## Quality gates

| Gate | Requirement |
|------|-------------|
| Symptom reproduced | Log or VCD evidence that the bug was reproducible before the fix |
| Root cause cited | `triage.md` names specific file/line/signal, not just "RTL issue" |
| Fix minimal | Change touches only what is necessary; unrelated behaviour preserved |
| After-fix simulation ran | Post-fix VCD exists and is non-empty |
| Manifest written | `results/issue-<n>/logs/run_manifest.json` present |
