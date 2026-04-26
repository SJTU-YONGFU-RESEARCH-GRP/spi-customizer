# SPI Customizer Fixing Plan

## Goal

Make `spi-customizer` deterministic and correct from issue spec to generated RTL, testbench, simulation evidence, and result artifacts (`logs/`, `data/`, `graphs/`) without relying on manual agent intervention.

## Scope

- In scope:
  - Issue-template parsing correctness
  - Template-generated RTL/testbench correctness
  - Simulation/logging correctness
  - VCD parsing, compliance checks, summary/graph correctness
  - Replay-based validation over issue corpus
- Out of scope:
  - New SPI features not represented in existing issue templates
  - Non-SPI modules in `proj/`

## Milestones

### Milestone 0 - Baseline and Repro Harness

**Objective**
- Establish a reproducible baseline for known-bad and known-good issue outputs.

**Tasks**
- Define issue replay corpus (historical + synthetic):
  - Roles: master/slave/dual
  - Modes: 0/1/2/3
  - Widths: 8/16/32 (+ one non-byte width)
  - SS polarity and bit-order variants
- Add baseline collection script/test flow to run generation + compile + sim + report for each case.
- Capture baseline results (pass/fail + artifact health).

**Exit Criteria**
- Baseline report exists and lists current failures by category.

**Status**
- `DONE`

---

### Milestone 1 - Testbench Template Correctness

**Objective**
- Ensure generated TB stimulus matches declared transactions and protocol timing.

**Primary Files**
- `templates/spi_dual_tb.v.tmpl`
- (as needed) `templates/spi_master_tb.v.tmpl`, `templates/spi_slave_tb.v.tmpl`

**Tasks**
- Replace hardcoded 7-bit dual-slave transaction with width-aware transfer generation.
- Align display text with actual transmitted bit count and value.
- Add explicit self-check assertions (`$fatal`) for key expected RX/TX behavior.
- Keep mode-aware edge behavior consistent with CPOL/CPHA.

**Exit Criteria**
- Dual-mode replay cases no longer show value/bit-count mismatch.
- Simulation fails loudly when protocol expectations are violated.

**Status**
- `IN_PROGRESS`

---

### Milestone 2 - VCD Parser and Timing/Graph Data Integrity

**Objective**
- Eliminate signal-column mixups and invalid waveform text/CSV interpretation.

**Primary File**
- `scripts/vcd_parser.py`

**Tasks**
- Rework canonical signal discovery (`SCLK`, `MOSI`, `MISO`, `SS_N`, `BUSY`, `IRQ`, `DATA`) using robust name matching.
- Fix timing diagram text generation column unpacking/order.
- Preserve bus-valued `SS_N` semantics in CSV/text/plot paths.
- Validate generated CSVs and plots against sampled VCD values.

**Exit Criteria**
- No mislabeled columns in timing outputs.
- Text/CSV values match underlying VCD signal data in spot checks.

**Status**
- `IN_PROGRESS`

---

### Milestone 3 - Protocol Compliance and Summary Truthfulness

**Objective**
- Ensure compliance and summary outputs are evidence-derived and internally consistent.

**Primary File**
- `scripts/vcd_parser.py`

**Tasks**
- Implement bus-aware `SS_n_matches_busy_window` check for multi-bit `ss_n`.
- Reduce `NOT_RUN` to only genuinely uncheckable criteria.
- Fix transition-count and KPI computations in `SUMMARY.md`.
- Ensure summary metrics reconcile with `spi_signal_summary.csv` and VCD.

**Exit Criteria**
- Compliance report has actionable PASS/FAIL evidence rows with timestamps.
- Summary metrics contain no contradictions.

**Status**
- `IN_PROGRESS`

---

### Milestone 4 - Issue Parsing and Spec-to-Check Mapping

**Objective**
- Make parser robust to issue-template wording and preserve verification intent.

**Primary Files**
- `scripts/config_parser.py`
- (if needed) `.github/ISSUE_TEMPLATE/5-spi-spec-intent.yml`
- (if needed) `.github/ISSUE_TEMPLATE/6-spi-verification-request.yml`
- (if needed) `.github/ISSUE_TEMPLATE/7-spi-debug-request.yml`

**Tasks**
- Harden extraction for current template field phrasing/format.
- Persist acceptance criteria / verification intent for downstream compliance generation.
- Remove ambiguous regex dependence where deterministic parsing is feasible.

**Exit Criteria**
- Replay suite parses intended config/criteria correctly for all targeted issue formats.

**Status**
- `DONE`

---

### Milestone 5 - End-to-End Replay Validation and Release Gate

**Objective**
- Validate full pipeline correctness over issue corpus and define merge gate.

**Primary Files**
- `scripts/test_full_pipeline.py`
- Additional focused tests under `scripts/` (to be added)

**Tasks**
- Add regression assertions for:
  - parser outputs
  - generated RTL/TB structural expectations
  - compile/sim success and VCD existence
  - compliance and summary consistency checks
- Run full replay suite and produce final validation report.

**Exit Criteria**
- All replay cases pass gate checks, or remaining failures are explicitly documented and triaged.

**Status**
- `DONE`

---

### Milestone 6 - Spec-Derived Verification Oracle

**Objective**
- Make validation depend on issue-derived protocol intent, not only artifact existence.

**Primary Files**
- `scripts/config_parser.py`
- `scripts/vcd_parser.py`
- `scripts/replay_validation.py`

**Tasks**
- Build a normalized verification spec object from issue inputs:
  - mode/CPOL/CPHA
  - role
  - data width / bit order
  - SS polarity/framing rules
  - acceptance criteria text
- Persist this spec in `results/issue-<n>/logs/run_manifest.json`.
- Add oracle checks that compare observed behavior against this spec (not static generic checks).

**Exit Criteria**
- Each modern replay case has a spec object and spec-evaluated pass/fail results.

**Status**
- `IN_PROGRESS`

---

### Milestone 7 - RTL/TB Semantic Correctness Coverage

**Objective**
- Verify generated RTL and testbench semantics match the requested behavior.

**Primary Files**
- `templates/*.tmpl`
- `scripts/verilog_generator.py`
- `scripts/replay_validation.py`

**Tasks**
- Add structural + semantic checks for generated RTL/TB, including:
  - role/module alignment (`master/slave/dual`)
  - mode-specific edge behavior in TB stimulus/checks
  - width/bit-order correctness for transfer windows
  - assertions present for key outcomes (`rx_valid`, payload equality, framing)
- Add negative tests where expected failure must occur if behavior is violated.

**Exit Criteria**
- Replay harness reports semantic RTL/TB checks per issue and fails on mismatches.

**Status**
- `DONE`

---

### Milestone 8 - Coverage Matrix and Release Policy

**Objective**
- Ensure sufficient issue-space coverage and enforce release gating on spec correctness.

**Primary Files**
- `docs/SPI_REPLAY_VALIDATION_REPORT.md`
- `scripts/replay_validation.py`

**Tasks**
- Add explicit coverage matrix dimensions to report:
  - mode (0/1/2/3), role, width class (1/3/7/8/16/32), SS polarity, bit order
- Require modern suite to pass spec-based oracle checks (not only compile/sim/VCD).
- Keep legacy artifact failures as informational unless promoted into modern suite.

**Exit Criteria**
- Report includes coverage matrix + policy verdict:
  - `release_gate_modern = PASS|FAIL`
  - `coverage_gap = none|listed`

**Status**
- `DONE`

---

### Milestone 9 - Compliance Robustness Hardening

**Objective**
- Strengthen waveform compliance checks from basic invariants to broader protocol-behavior guards while keeping deterministic pass/fail evidence.

**Primary Files**
- `scripts/vcd_parser.py`
- `docs/SPI_REPLAY_VALIDATION_REPORT.md`

**Tasks**
- Extend compliance checks to include additional protocol guards:
  - `SS_n_inactive_when_not_busy`
  - `SCLK_activity_present_during_busy`
- Keep checks role-aware (`master/slave/dual`) and evidence-based.
- Re-run modern issue corpus and verify modern pass rate under stricter compliance checks.

**Exit Criteria**
- Modern issue compliance reports include new checks.
- Replay report confirms whether modern cases continue to pass under updated compliance logic.

**Status**
- `IN_PROGRESS`

## Global Quality Gates (applied to each replay case)

1. Compilation succeeds (`iverilog -g2012`).
2. Simulation succeeds (`vvp`) and testbench assertions pass (no `FATAL`/`$fatal`).
3. Testbench assertions pass (no `$fatal`).
4. VCD exists and is non-empty.
5. Compliance checks map to evidence (timestamps/signal values).
6. Spec-derived oracle checks pass for issue intent + acceptance criteria.
7. Summary KPIs are internally consistent.
8. RTL/TB semantic checks (role/mode/width/bit-order/framing) pass.
9. Artifacts are generated under `results/issue-<n>/` only.

## Status Reporting Protocol

Status will be updated after each milestone completion (or earlier if blocked) in this file under:
- Milestone `Status`
- Progress log entries below

### Progress Log

| Date (UTC+8) | Milestone | Status | Evidence / Notes |
|---|---|---|---|
| 2026-04-27 | M0 | IN_PROGRESS | Baseline corpus and failure categories documented in `docs/SPI_CUSTOMIZER_BASELINE_M0.md` |
| 2026-04-27 | M1 | IN_PROGRESS | Updated `templates/spi_dual_tb.v.tmpl` to replace hardcoded 7-bit stimulus with width-aware bit loop and added `$fatal` RX checks |
| 2026-04-27 | M1 | IN_PROGRESS | Replayed issue 3: `iverilog -g2012` + `vvp` now passes with `sent 0x5a (8 bits)` and `Slave RX matched expected payload: 0x0000005a` |
| 2026-04-27 | M2 | IN_PROGRESS | Updated `scripts/vcd_parser.py` canonical signal mapping and timing text column parsing; regenerated issue-3 timing artifacts now show consistent header/values (`SCLK=1 MOSI=0 MISO=0 SS=1 BUSY=0 IRQ=0`) |
| 2026-04-27 | M2 | IN_PROGRESS | Added bus-aware SS handling in parser/compliance checks and dual-mode master gating; issue-3 `SS_n_matches_busy_window` now evaluates `PASS` instead of `NOT_RUN/invalid fail` |
| 2026-04-27 | M3 | IN_PROGRESS | Fixed summary KPI derivation in `scripts/vcd_parser.py` (`Signal Transitions`, `Time Range`, `Data Transfer Events`, `Clock Cycles`) to be CSV/log evidence-based; refreshed issue-3 reports with consistent values |
| 2026-04-27 | M3 | IN_PROGRESS | Cleaned summary formatting/count artifacts in `scripts/vcd_parser.py` (duplicate heading injection, `bits bits` wording, canonical individual-signal CSV count); issue-3 summary now renders clean sections |
| 2026-04-27 | M4 | IN_PROGRESS | Hardened form-label parsing in `scripts/config_parser.py` (deterministic `### Field` extraction + regex fallback), added intent/acceptance metadata persistence, and updated `scripts/process_issue.py` to store `custom_features` in generated `spi_config.json` |
| 2026-04-27 | M4 | DONE | End-to-end form replay (`issue-1003`) validated: `spi_role=dual`, intent/acceptance captured in `custom_features`, and `SUMMARY.md` generated correctly with no missing-config failure |
| 2026-04-27 | M5 | IN_PROGRESS | Added replay harness `scripts/replay_validation.py` and generated gate report at `docs/SPI_REPLAY_VALIDATION_REPORT.md` (17 cases evaluated; current pass baseline documented) |
| 2026-04-27 | M5 | IN_PROGRESS | Refined replay report with triage separation (modern release-gate cases vs legacy artifacts); modern set currently: issue-1003 PASS, issue-1002 FAIL (`summary_ok`, `consistency_ok`) |
| 2026-04-27 | M5 | DONE | Refreshed issue-1002 reports and reran replay harness: modern release-gate set now 2/2 PASS (`issue-1002`, `issue-1003`); legacy failures isolated as historical artifacts |
| 2026-04-27 | M6 | IN_PROGRESS | Plan upgraded to spec-derived oracle phase; next implementation step is adding normalized issue spec into manifest + replay validator checks |
| 2026-04-27 | M6 | IN_PROGRESS | Implemented `verification_spec` in run manifest and `spec_oracle_ok` gate in `scripts/replay_validation.py`; refreshed modern replay cases (`issue-1002/1003/1004`) now pass spec-derived oracle checks |
| 2026-04-27 | M7 | DONE | Added `rtl_tb_semantic_ok` gate in `scripts/replay_validation.py` (role/module alignment, mode/width propagation, assertion presence, mode marker checks); modern cases (`issue-1002/1003/1004`) pass |
| 2026-04-27 | M8 | DONE | Extended replay report with coverage matrix and policy verdict fields (`release_gate_modern`, `coverage_gap`) in `docs/SPI_REPLAY_VALIDATION_REPORT.md`; current verdict FAIL due to modern mode coverage gap (missing 0/1/3) |
| 2026-04-27 | M8 | DONE | Expanded coverage to align with `1-spi-config-form` dimensions (features/testing/default-data/role/polarity/order/mode); report now emits `coverage_gap_details` with per-field missing options |
| 2026-04-27 | M8 | IN_PROGRESS | Added modern replays (`issue-1005/1006/1008/1009/1010`), made semantic gate role-aware in `scripts/replay_validation.py`, and refreshed report: modern suite now 8/8 PASS with only remaining coverage gap `mode=3` |
| 2026-04-27 | M8 | DONE | Added mode-3 modern replay (`issue-1011`) and reran validator; `docs/SPI_REPLAY_VALIDATION_REPORT.md` now shows `release_gate_modern=PASS` and `coverage_gap=none` |
| 2026-04-27 | M8 | IN_PROGRESS | Reproduced and fixed `issue-1007` simulation hang (mode3/32-bit master) via core/template fixes (`bit_counter` width, `sclk_gen` reset init, bounded TB waits); latest replay now includes `issue-1007` but marks it FAIL on `compliance_ok` (`SCLK_idle_level_matches_CPOL`) so release gate is currently FAIL |
| 2026-04-27 | M8 | DONE | Finalized mode3/32-bit master behavior for `issue-1007` (CPHA edge handling + completion-on-idle-SCLK + idle-window compliance sampling); `issue-1007` now PASS and replay report returns to modern 10/10 PASS with `release_gate_modern=PASS` |
| 2026-04-27 | M9 | IN_PROGRESS | Added stricter compliance checks in `scripts/vcd_parser.py` (`SS_n_inactive_when_not_busy`, `SCLK_activity_present_during_busy`) and started full modern revalidation |
| 2026-04-27 | M9 | IN_PROGRESS | Revalidated modern issues under updated compliance checks: `issue-1002/1003/1004/1005/1006/1007/1008/1009/1011` PASS, `issue-1010` FAIL (`SS_n_inactive_when_not_busy` with active-high SS), so `release_gate_modern=FAIL` pending dual-mode active-high SS fix |
| 2026-04-27 | M9 | DONE | Fixed dual-mode active-high SS idle/assert behavior in `templates/spi_dual.v.tmpl`, regenerated affected modern issues, and reran replay: modern 10/10 PASS under hardened compliance (`release_gate_modern=PASS`) |

## Status Legend

- `PENDING`: not started
- `IN_PROGRESS`: currently being implemented/validated
- `BLOCKED`: cannot proceed due to identified blocker
- `DONE`: milestone exit criteria met
