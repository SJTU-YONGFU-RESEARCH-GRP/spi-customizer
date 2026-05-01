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
- `DONE`

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
- `DONE`

---

### Milestone 10 - Conformance Spec and Traceability

**Objective**
- Introduce machine-readable conformance requirements and requirement-to-evidence traceability in replay reporting.

**Primary Files**
- `docs/SPI_CONFORMANCE_REQUIREMENTS.json`
- `scripts/replay_validation.py`
- `docs/SPI_REPLAY_VALIDATION_REPORT.md`

**Tasks**
- Define versioned conformance requirements with explicit compliance-check mappings.
- Evaluate requirement coverage/pass status across modern issues.
- Emit requirement traceability table and conformance gate in replay report.

**Exit Criteria**
- Replay report contains a requirement traceability section.
- Conformance gate is computed from machine-readable requirements.

**Status**
- `DONE`

---

### Milestone 11 - Transaction Decoder Oracle

**Objective**
- Implement frame-level protocol decoding from waveform evidence and compare decoded behavior to expected transaction intent.

**Primary Files**
- `scripts/vcd_parser.py`
- `scripts/replay_validation.py`
- `docs/SPI_REPLAY_VALIDATION_REPORT.md`

**Tasks**
- Add transaction extraction from `SS_N/SCLK/MOSI/MISO` into normalized frame records.
- Reconstruct payloads per mode (`0/1/2/3`), bit order, and transfer width.
- Emit oracle checks that compare decoded frame payload/length/framing with expected behavior from generated testbenches/manifests.

**Exit Criteria**
- Replay report includes decoder-oracle outcomes per modern issue.
- Modern issues pass decoder-oracle checks for covered scenarios.

**Status**
- `IN_PROGRESS`

---

### Milestone 12 - Timing Conformance Windows

**Objective**
- Add explicit setup/hold and edge-to-data timing checks with deterministic tolerances.

**Primary Files**
- `scripts/vcd_parser.py`
- `docs/SPI_CONFORMANCE_REQUIREMENTS.json`
- `docs/SPI_REPLAY_VALIDATION_REPORT.md`

**Tasks**
- Define timing-window requirements (setup/hold around sampling edges) and tolerance policy.
- Implement timing checks from decoded transitions with `PASS/FAIL/INCONCLUSIVE` semantics.
- Track timing conformance in requirement traceability output.

**Exit Criteria**
- Timing conformance checks are represented in machine-readable requirements.
- Replay report shows timing requirement statuses across modern issues.

**Status**
- `DONE`

---

### Milestone 13 - Negative and Fault-Injection Conformance

**Objective**
- Ensure conformance checks fail for known-invalid protocol behaviors and produce discriminative evidence.

**Primary Files**
- `templates/*_tb.v.tmpl`
- `scripts/replay_validation.py`
- `docs/SPI_REPLAY_VALIDATION_REPORT.md`

**Tasks**
- Add controlled negative scenarios (bad SS framing, wrong edge data changes, invalid bit counts).
- Validate that compliance/oracle checks flag expected failures with correct check IDs.
- Separate negative-test results from normal modern release-gate cohort.

**Exit Criteria**
- Negative suite shows expected-fail outcomes with deterministic evidence.
- No false-pass on injected protocol violations.

**Status**
- `DONE`

---

### Milestone 14 - Coverage Closure and Certification Sign-off

**Objective**
- Establish requirement-level coverage closure and sign-off artifacts suitable for conformance claims.

**Primary Files**
- `docs/SPI_CONFORMANCE_REQUIREMENTS.json`
- `docs/SPI_REPLAY_VALIDATION_REPORT.md`
- `docs/SPI_CONFORMANCE_SIGNOFF.md`

**Tasks**
- Add requirement coverage metrics (`covered/pass/fail/not-covered`) and closure rules.
- Emit sign-off summary artifact with toolchain/version traceability and gate verdict.
- Enforce release policy requiring coverage closure + conformance gate pass.

**Exit Criteria**
- Sign-off document is generated and linked from replay report.
- Release gate reflects requirement-coverage closure and conformance pass.

**Status**
- `DONE`

---

### Milestone 15 - Modern Issue Expansion and Stress Coverage

**Objective**
- Expand the modern issue corpus beyond baseline coverage to increase stress/scenario diversity and reduce overfitting to the current 10-case set.

**Primary Files**
- `docs/SPI_CUSTOMIZER_FIX_PLAN.md`
- `docs/SPI_REPLAY_VALIDATION_REPORT.md`
- `results/issue-10xx/`

**Tasks**
- Add new modern issues that increase scenario depth across:
  - data widths: include non-baseline values (e.g., `1`, `3`, `7`, and additional `24/32` stress mixes)
  - roles/modes: additional mode-role combinations already covered functionally but with different timing/features
  - SS behavior: multi-slave patterns and active-high/active-low framing stress
  - feature vectors: denser combinations of interrupts/FIFO/DMA/multi-master/jitter/waveform options
- Tag newly added modern issues in progress log with purpose (which gap/stress axis they target).
- Rerun full modern replay after each batch and track:
  - modern pass count
  - conformance gate
  - negative-suite gate
  - sign-off gate

**Exit Criteria**
- Modern issue pool expanded from 10 to at least 16 passing modern issues.
- Replay report remains `release_gate_modern=PASS`, `conformance_gate=PASS`, `negative_suite_ok=PASS`, and `signoff_gate=PASS`.
- Progress log includes per-batch evidence of newly added issue IDs and replay outcomes.

**Status**
- `IN_PROGRESS`

---

### Milestone 16 - SS Semantics, Multi-Slave Selection, and Robust Semantic Gates

**Objective**
- Close remaining generator/validation gaps by unifying SS-active semantics across reporting, removing fixed slave-index behavior, and replacing fragile token checks with evidence-based semantic gates.

**Primary Files**
- `scripts/vcd_parser.py`
- `templates/spi_core.v.tmpl`
- `templates/spi_dual.v.tmpl`
- `templates/spi_master_tb.v.tmpl`
- `templates/spi_dual_tb.v.tmpl`
- `scripts/replay_validation.py`

**Tasks**
- SS statistics and plotting consistency:
  - Replace hardcoded `b0`/`b111` assumptions in plot/stat paths with a shared polarity-aware SS-active predicate.
  - Ensure `_add_signal_statistics()` and related helpers derive SS activity from configured polarity and bus width.
- Multi-slave master selection policy:
  - Remove fixed `master_ss_n_reg[0]` behavior in dual/master templates.
  - Introduce deterministic selected-slave policy (generated parameter/input-driven index) and propagate to TB/config.
  - Verify waveform and CSV show one-hot selection for the selected index.
- TB wording/intent alignment:
  - Update comments/messages that assume "slave 0" to reference selected slave index semantics.
  - Keep oracle/report language consistent with generated selection policy.
- Replay semantic gate hardening:
  - Migrate key semantic checks from source-token presence to evidence-based checks (parsed generated parameters + waveform/compliance evidence).
  - Reduce formatting sensitivity in `scripts/replay_validation.py`.
- SS_N graph readability standardization:
  - Keep SS_N waveform at digital active/inactive levels (not raw bus magnitude).
  - Add sparse transition annotations using semantic labels (`IDLE`, `SEL[n]`, `MULTI/INV`) instead of dense raw bus text per sample.
  - Keep raw bus vectors available in CSV/log evidence while using semantic labels for static plot readability.

**Exit Criteria**
- SS statistics, compliance, and plots use the same polarity-aware active predicate.
- Multi-slave generated RTL/TB support deterministic non-hardcoded slave selection behavior.
- No stale "slave 0" assumptions remain in TB intent/reporting for parameterized selection.
- Replay semantic gate no longer depends on brittle formatting/token strings for critical verdicts.

**Status**
- `IN_PROGRESS`

---

### Milestone 17 - Slave Testbench Failure-Mode Hardening

**Objective**
- Upgrade generated slave testbench self-checking to catch functional/protocol RTL failures instead of relying on basic stimulus completion.

**Primary Files**
- `templates/spi_slave_tb.v.tmpl`
- `scripts/replay_validation.py`

**Tasks**
- Replace non-deterministic slave stimulus with deterministic vectors tied to expected payload.
- Add mandatory `$fatal` checks for:
  - `rx_valid` assertion within bounded timeout
  - received payload equality vs expected word
  - transaction framing sanity (`ss_in` active/inactive boundaries)
- Add mode/bit-order-aware expected reconstruction checks in TB (not display-only).
- Wire new slave TB assertion evidence into replay gate criteria.

**Exit Criteria**
- Slave TB fails deterministically on payload/framing regressions.
- Replay reports slave-specific semantic gate failures when injected regressions are present.

**Status**
- `IN_PROGRESS`

---

### Milestone 18 - Master and Dual Testbench Robustness Closure

**Objective**
- Close remaining master/dual blind spots by enforcing scoreboard-style checks and fail-fast timeout behavior.

**Primary Files**
- `templates/spi_master_tb.v.tmpl`
- `templates/spi_dual_tb.v.tmpl`
- `scripts/replay_validation.py`

**Tasks**
- Master TB:
  - Add deterministic MISO response modeling and expected RX scoreboard across mode/bit-order variants.
  - Add strict per-transaction pass/fail assertions (`$fatal`) for RX correctness and completion timing.
- Dual TB:
  - Convert warning-only timeout paths to fail-fast assertions.
  - Extend dual-path checks to validate both master-side and slave-side transfer outcomes under one run.
- Replay integration:
  - Add/strengthen evidence-based gates confirming TB assertion coverage for master/dual templates.

**Exit Criteria**
- Master and dual TBs fail on timeout/protocol/payload regressions with explicit assertion evidence.
- Replay catches injected master/dual regressions that previously passed.

**Status**
- `DONE`

---

### Milestone 19 - Model-Based Corner Robustness (Long-Run)

**Objective**
- Replace corner-by-corner fixes with a unified, model-based SPI transaction correctness strategy that scales to new corner inputs.

**Primary Files**
- `templates/spi_slave.v.tmpl`
- `templates/spi_slave_tb.v.tmpl`
- `templates/spi_master_tb.v.tmpl`
- `templates/spi_dual_tb.v.tmpl`
- `scripts/replay_validation.py`
- `docs/SPI_REPLAY_VALIDATION_REPORT.md`

**Tasks**
- Refactor receive semantics to a single deterministic sample-count model:
  - explicit sampled-bit indexing by `bit_counter`
  - completion driven by sampled bit count instead of ad-hoc post-rotation behavior
- Align TB checks to a reference transaction model (mode/bit-order/data-width aware) and keep fail-fast assertions.
- Expand replay corner matrix systematically (not ad-hoc):
  - widths `{1,2,3,7,8,9,15,16,24,31,32}`
  - modes `0/1/2/3`
  - both bit orders and both SS polarities
  - role-aware cohorts (`master/slave/dual`)
- Add replay evidence fields showing corner coverage closure and corner-specific failure signatures.

**Exit Criteria**
- New corner additions do not require bespoke alignment patches.
- Replay demonstrates stable pass behavior across systematic corner matrix.
- Corner regressions fail with deterministic TB/replay evidence.

**Status**
- `DONE`

---

### Milestone 20 - Selected-Slave Index Sweep (Parser->Generator->TB->Replay)

**Objective**
- Provide end-to-end, evidence-backed multi-slave index coverage by wiring selected-slave index through config parsing, code generation, TB execution, and replay policy.

**Primary Files**
- `scripts/config_parser.py`
- `scripts/verilog_generator.py`
- `templates/spi_core.v.tmpl`
- `templates/spi_dual.v.tmpl`
- `templates/spi_master_tb.v.tmpl`
- `templates/spi_dual_tb.v.tmpl`
- `scripts/process_issue.py`
- `scripts/replay_validation.py`
- `docs/SPI_REPLAY_VALIDATION_REPORT.md`

**Tasks**
- Parser/config plumbing:
  - add `selected_slave` to parsed/validated config with range check `0 <= selected_slave < num_slaves`.
  - persist `selected_slave` into generated `spi_config.json` and run manifest.
- Generator/template wiring:
  - drive `SELECTED_SLAVE` from parsed config in master/dual RTL and TB templates.
- Coverage implementation:
  - add replay coverage tracking for selected-slave index and expose coverage gaps.
  - add modern sweep issues with non-zero selected indices for multi-slave master/dual corners.
- Oracle/gate policy:
  - keep `selected_slave_oracle_ok` as required pass and ensure it evaluates against configured index values from sweep set.

**Exit Criteria**
- Selected-slave index is configurable from issue input and visible in generated config/manifest/RTL/TB.
- Replay report shows selected-index coverage evidence (including non-zero indices) with no index-coverage gap for scoped sweep policy.
- Modern replay and sign-off remain PASS with index sweep included.

**Status**
- `DONE`

---

### Milestone 21 - Deterministic Full-Grid Replay Scheduler (Numeric Space)

**Objective**
- Convert numeric-space expansion from ad-hoc issue additions into a deterministic, budgeted full-grid scheduler that continuously fills remaining matrix signatures while preserving green policy gates.

**Primary Files**
- `scripts/expand_replay_matrix.py`
- `scripts/replay_validation.py`
- `docs/SPI_REPLAY_VALIDATION_REPORT.md`
- `docs/SPI_CONFORMANCE_SIGNOFF.md`

**Tasks**
- Add deterministic full-grid target generation over:
  - mode `0/1/2/3`
  - role `master/slave/dual`
  - data width range (configurable; default `1..32`)
  - SS polarity `active_low/active_high`
  - bit order `msb_first/lsb_first`
- Compute already-covered signatures from existing `results/issue-*/code/spi_config.json` and generate only missing signatures.
- Enforce runtime budget via bounded batch size (`--max-cases`) and deterministic ordering.
- Keep replay/sign-off green after each expansion batch by fixing uncovered generator/compliance corner regressions before proceeding.

**Exit Criteria**
- Deterministic scheduler script exists and can emit missing signatures in bounded batches.
- At least one scheduler batch is generated and replayed successfully.
- Replay policy remains green after regression closure (`release_gate_modern=PASS`, `conformance_gate=PASS`, `signoff_gate=PASS`).

**Status**
- `IN_PROGRESS`

---

### Milestone 22 - Replay Validation Coverage and Telemetry Expansion

**Objective**
- Upgrade replay validation to explicitly support compact-suite claim reporting with stronger coverage metrics, targeted case expansion, and runtime telemetry.

**Primary Files**
- `scripts/replay_validation.py`
- `scripts/expand_replay_matrix.py`
- `docs/SPI_REPLAY_VALIDATION_REPORT.md`
- `docs/SPI_CONFORMANCE_SIGNOFF.md`

**Tasks**
- Expand coverage targets from pass/fail to coverage metrics:
  - Define explicit replay coverage dimensions:
    - mode, role, width bucket, SS polarity, bit order
    - special-feature tuple: `(interrupts, fifo, dma, multi_master)`
    - selected-slave bucket (`zero` vs `nonzero`)
    - test options (`clock_jitter_test`, `waveform_capture`)
  - Report coverage as `covered / target` per dimension.
  - Add pairwise interaction coverage for special features (all 2-way feature pairs).
- Add higher-coverage replay case generation:
  - Build target matrix for missing combinations (including rare tuples).
  - Auto-generate new replay issues for uncovered points.
  - Re-run replay iteratively until:
    - required corners are covered
    - modern-set gate pass remains stable.
- Add runtime telemetry per replay case:
  - Capture start timestamp, end timestamp, and total duration (seconds) for each case.
  - Compute/report aggregate latency metrics:
    - min
    - max
    - mean
    - p50/p90.

**Exit Criteria**
- Replay report includes `covered / target` coverage summaries for required dimensions.
- Replay report includes 2-way special-feature interaction coverage status.
- Replay expansion loop can generate/close uncovered corners while keeping modern gates stable.
- Replay report includes per-case runtime and aggregate stats (`min/max/mean/p50/p90`).

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
| 2026-04-27 | M10 | IN_PROGRESS | Added machine-readable conformance requirements file `docs/SPI_CONFORMANCE_REQUIREMENTS.json` and integrated requirement parsing into `scripts/replay_validation.py` |
| 2026-04-27 | M10 | DONE | Replay report now emits requirement traceability and `conformance_gate`; modern suite revalidated under updated compliance and remains 10/10 PASS (`release_gate_modern=PASS`) |
| 2026-04-27 | M11 | IN_PROGRESS | Milestone created; next execution step is implementing waveform transaction decoder oracle and wiring it into replay gating |
| 2026-04-27 | M11 | IN_PROGRESS | Added initial `transaction_oracle_ok` replay gate using timing-derived busy windows and sampling-edge expectations; refined role-aware behavior for slave mode and revalidated modern suite to 10/10 PASS |
| 2026-04-27 | M11 | IN_PROGRESS | Upgraded transaction oracle to explicit busy-window frame decoding (`start/end/sampling-edge counts`) and validated replay remains modern 10/10 PASS with `transaction_oracle_ok` active |
| 2026-04-27 | M12 | DONE | Added timing-window compliance check `MOSI_setup_hold_window_ok` in `scripts/vcd_parser.py`, extended machine-readable requirements with `SPI-CONF-005`, regenerated modern compliance reports, and reran replay with modern 10/10 PASS (`conformance_gate=PASS`) |
| 2026-04-27 | M13 | IN_PROGRESS | Added negative-suite tracking in replay report and created first fault-injection case `results/negative-001`; replay now evaluates `negative_suite_ok=PASS` with expected-fail checks validated |
| 2026-04-27 | M13 | DONE | Negative suite formalized with `negative-001` manifest + expected-fail evidence and integrated replay evaluation (`negative_suite_ok=PASS`) |
| 2026-04-27 | M14 | DONE | Added generated sign-off artifact `docs/SPI_CONFORMANCE_SIGNOFF.md` and sign-off policy verdict (`signoff_gate`) in replay reporting; current sign-off PASS |
| 2026-04-27 | M15 | IN_PROGRESS | Coverage expansion milestone created to grow modern issue corpus with stress-focused scenarios while maintaining PASS across release/conformance/negative/sign-off gates |
| 2026-04-27 | M15 | IN_PROGRESS | Added narrow-width modern cases `issue-1012` (mode0/master/1-bit), `issue-1013` (mode1/slave/3-bit), and `issue-1014` (mode3/master/7-bit) and regenerated replay/sign-off artifacts |
| 2026-04-27 | M15 | IN_PROGRESS | Resolved false-negative semantic gate during batch expansion by extending replay semantic token matching for compact TB parameter forms (`MODE=...`, `DATA_WIDTH=...`, `MSB_FIRST=...`) in `scripts/replay_validation.py`; current replay is modern `13/13 PASS` with all policy gates PASS |
| 2026-04-27 | M15 | IN_PROGRESS | Added 24/32-bit stress modern cases `issue-1015` (mode3/master/24-bit, active-high SS), `issue-1016` (mode1/dual/32-bit, active-high SS), and `issue-1017` (mode0/slave/24-bit, active-low SS) and regenerated replay/sign-off artifacts |
| 2026-04-27 | M15 | IN_PROGRESS | Batch 2 replay outcome: modern `16/16 PASS` with `release_gate_modern=PASS`, `conformance_gate=PASS`, `negative_suite_ok=PASS`, and `signoff_gate=PASS` |
| 2026-04-27 | M15 | IN_PROGRESS | Reintroduced failing-intent debug coverage as `issue-1018` (mode2/master/24-bit/active-high SS) and `issue-1019` (mode0/slave/24-bit/active-high SS) to drive generator/compliance root-cause fixes instead of substituting easier variants |
| 2026-04-27 | M15 | IN_PROGRESS | Fixed root causes: (1) removed brittle mode-2 comment marker dependency in `scripts/replay_validation.py` semantic gate, (2) made `templates/spi_slave_tb.v.tmpl` SS stimulus polarity-aware (`SS_ACTIVE`/`SS_INACTIVE`) and width-driven (`repeat(DATA_WIDTH)`), (3) hardened `scripts/vcd_parser.py` SS framing checks to evaluate around boundary transitions (`before`/`just_after`) |
| 2026-04-27 | M15 | IN_PROGRESS | Post-fix replay with debug-intent cases included: modern `18/18 PASS`, `release_gate_modern=PASS`, `conformance_gate=PASS`, `negative_suite_ok=PASS`, `signoff_gate=PASS` |
| 2026-04-27 | M15 | IN_PROGRESS | Added debug-focused batch with `issue-1020` (mode2/dual/24-bit/active-high SS/LSB-first), `issue-1021` (mode1/slave/32-bit/active-high SS/MSB-first), and `issue-1022` (mode2/master/32-bit/active-low SS/LSB-first) |
| 2026-04-27 | M15 | IN_PROGRESS | Root-cause fixes from `issue-1020`: updated `templates/spi_dual_tb.v.tmpl` to use polarity-aware SS activation (`SS_ACTIVE`/`SS_INACTIVE`), full-width slave transaction stimulus (`SLAVE_TEST_BITS=DATA_WIDTH`), and bit-order-aware transmit sequencing; updated `templates/spi_dual.v.tmpl` slave transaction edge detection to use configured SS polarity instead of active-low hardcoding |
| 2026-04-27 | M15 | IN_PROGRESS | Post-fix replay after batch expansion: modern `21/21 PASS`, `release_gate_modern=PASS`, `conformance_gate=PASS`, `negative_suite_ok=PASS`, `signoff_gate=PASS` |
| 2026-04-27 | M15 | IN_PROGRESS | Added active-high dual corner batch: `issue-1023` (mode0/dual/16-bit/active-high/MSB-first), `issue-1024` (mode3/dual/16-bit/active-high/LSB-first), and `issue-1025` (mode1/dual/16-bit/active-low/LSB-first) |
| 2026-04-27 | M15 | IN_PROGRESS | Replay after corner-batch expansion: modern `24/24 PASS`, `release_gate_modern=PASS`, `conformance_gate=PASS`, `negative_suite_ok=PASS`, `signoff_gate=PASS` |
| 2026-04-27 | M15 | IN_PROGRESS | Added stress-extension batch: `issue-1026` (mode1/dual/24-bit/active-high/LSB-first), `issue-1027` (mode0/master/32-bit/active-high/MSB-first), and `issue-1028` (mode2/slave/16-bit/active-high/LSB-first) |
| 2026-04-27 | M15 | IN_PROGRESS | Replay after stress-extension batch: modern `27/27 PASS`, `release_gate_modern=PASS`, `conformance_gate=PASS`, `negative_suite_ok=PASS`, `signoff_gate=PASS` |
| 2026-04-27 | M15 | IN_PROGRESS | Added high-width mix batch: `issue-1029` (mode2/dual/32-bit/active-low/MSB-first), `issue-1030` (mode3/slave/32-bit/active-low/MSB-first), and `issue-1031` (mode1/master/24-bit/active-low/LSB-first) |
| 2026-04-27 | M15 | IN_PROGRESS | Replay after high-width mix batch: modern `30/30 PASS`, `release_gate_modern=PASS`, `conformance_gate=PASS`, `negative_suite_ok=PASS`, `signoff_gate=PASS` |
| 2026-04-27 | M16 | IN_PROGRESS | Added focused fix-track for remaining gaps: (1) SS stats use polarity-aware predicate, (2) parameterized multi-slave selection replacing fixed `[0]`, (3) TB/oracle wording alignment for selected slave index, (4) replay semantic gates migrated from token checks to parameter/evidence-based validation |
| 2026-04-27 | M16 | IN_PROGRESS | Added SS_N graph-readability standard to milestone scope: semantic sparse annotations (`IDLE`/`SEL[n]`/`MULTI/INV`) on digital active/inactive trace, with full raw vectors retained in CSV/log evidence |
| 2026-04-27 | M16 | IN_PROGRESS | Implemented deterministic slave-selection parameterization in templates: added `SELECTED_SLAVE` to `spi_master`/`spi_dual` cores and TBs, replaced fixed index `[0]` with clamped selectable index policy |
| 2026-04-27 | M16 | IN_PROGRESS | Regenerated `issue-1031` to validate selection policy: `spi_SS_N_data.csv` now shows deterministic one-hot active vector (`b111110`) instead of all-active `b0` pattern |
| 2026-04-27 | M16 | IN_PROGRESS | Hardened semantic gate in `scripts/replay_validation.py`: replaced key mode/width/bit-order token scans with parsed TB parameter extraction (`_extract_tb_param_int`) and revalidated report generation |
| 2026-04-27 | M16 | IN_PROGRESS | Implemented SS_N sparse semantic annotations in `scripts/vcd_parser.py` (`IDLE`/`SEL[n]`/`MULTI`/`INV`) on transition points and regenerated `issue-1031` plots to refresh output |
| 2026-04-27 | M16 | IN_PROGRESS | Added replay selected-slave evidence gate `selected_slave_oracle_ok` in `scripts/replay_validation.py` (master/dual BUSY-window one-hot check vs configured selected index) and regenerated replay/sign-off reports |
| 2026-04-27 | M16 | IN_PROGRESS | Bulk-regenerated modern corpus `issue-1002..issue-1031` from saved configs to refresh RTL/TB/sim/CSV/graphs under new `SELECTED_SLAVE` + SS annotation updates |
| 2026-04-27 | M16 | IN_PROGRESS | Fixed selected-slave oracle evidence parsing (Verilog bit-index mapping + normalized compact SS vectors like `b1`/`b0`), scoped gate to master-role evidence for current canonical SS_N mapping, and restored replay policy to modern `30/30 PASS` with all gates PASS |
| 2026-04-27 | M16 | IN_PROGRESS | Completed dual-role selected-slave evidence path: `selected_slave_oracle_ok` now validates dual issues via `master_ss_n_reg` CSV (instead of ambiguous canonical `SS_N`), supports compact vector normalization, and enforces one-hot selected-index behavior on active samples |
| 2026-04-27 | M16 | DONE | Milestone 16 closure: SS semantics/stats/plots unified, multi-slave template selection parameterized (`SELECTED_SLAVE`), TB wording aligned, semantic/replay gates hardened to parsed/evidence-based checks, and modern replay/sign-off remains `30/30 PASS` with all policy gates PASS |
| 2026-04-27 | M17 | PENDING | Added slave-testbench robustness milestone to introduce deterministic stimulus, assertion-based payload/framing checks, and replay evidence gating for slave failure modes |
| 2026-04-27 | M18 | PENDING | Added master/dual robustness milestone for scoreboard checks and strict fail-fast timeout/assert behavior, plus replay gate strengthening |
| 2026-04-27 | M17 | IN_PROGRESS | Hardened `templates/spi_slave_tb.v.tmpl` with deterministic full-width payload drive, bounded busy/rx_valid timeout assertions, and explicit RX payload equality `$fatal` checks (removed random-only pass path) |
| 2026-04-27 | M17 | IN_PROGRESS | New slave TB checks exposed RTL width bug; fixed `templates/spi_slave.v.tmpl` `bit_counter` from 3-bit to 16-bit and validated with regenerated `issue-1017` (simulation PASS with strengthened assertions) |
| 2026-04-27 | M18 | IN_PROGRESS | Hardened `templates/spi_master_tb.v.tmpl` with fail-fast `busy` assertion waits and selected-slave SS one-hot checks; hardened `templates/spi_dual_tb.v.tmpl` by converting master timeout warning to `$fatal` and adding active-transaction SS assertions |
| 2026-04-27 | M18 | IN_PROGRESS | Strengthened replay semantic gate (`scripts/replay_validation.py`) to require master robustness tokens (`wait_for_busy_assert`, `assert_selected_ss_active`) and dual timeout assertion token (`MASTER_TX_TIMEOUT_CYCLES`) |
| 2026-04-27 | M18 | IN_PROGRESS | Regenerated modern corpus after M18 TB hardening; surfaced simulation failures concentrated in slave mode (e.g., mode1 payload mismatch), indicating newly exposed RTL timing/edge defects under stronger checks |
| 2026-04-27 | M18 | IN_PROGRESS | Applied additional slave-side RTL corrections in `templates/spi_slave.v.tmpl` (mode-correct edge selection and state transition adjustments); mode1 slave payload mismatch remains open for root-cause closure |
| 2026-04-27 | M18 | IN_PROGRESS | Deep-dive on persistent mode1 slave mismatch (`issue-1006`, observed `expected=0xa5a5a5 got=0x25a5a5`): tightened slave TB timing windows and added first-edge capture attempt in slave core; mismatch remains reproducible and is tracked as active blocker before M18 closure |
| 2026-04-27 | M18 | IN_PROGRESS | Closed primary CPHA alignment defect for normal widths: `issue-1006` now passes after slave RX normalization update; modern replay improved to `29/30` |
| 2026-04-27 | M18 | IN_PROGRESS | Remaining blocker isolated to narrow-width corner (`issue-1013`, mode1 + 3-bit + LSB-first): tried CDC hold-window tuning and indexed bit-capture refactor in `templates/spi_slave.v.tmpl`; mismatch (`expected=0x5 got=0x3`) remains reproducible |
| 2026-04-27 | M18 | DONE | Completed slave corner closure by enforcing deterministic receive publish path (`rx_data_reg <= shift_reg_rx`), sample-count-based `rx_valid`, and indexed bit capture in `templates/spi_slave.v.tmpl`; full modern replay restored to `30/30 PASS` with all policy gates PASS |
| 2026-04-27 | M19 | IN_PROGRESS | Long-run model-based corner robustness track opened to prevent future ad-hoc corner patches and drive systematic matrix-based validation |
| 2026-04-27 | M19 | IN_PROGRESS | Expanded replay coverage policy in `scripts/replay_validation.py` to enforce explicit width-corner set `{1,2,3,7,8,9,15,16,24,31,32}` and report concrete missing widths |
| 2026-04-27 | M19 | IN_PROGRESS | Added modern corner issues for missing widths: `issue-1032` (2-bit master), `issue-1033` (9-bit dual), `issue-1034` (15-bit slave), `issue-1035` (31-bit master) |
| 2026-04-27 | M19 | IN_PROGRESS | Post-expansion replay/sign-off: modern `34/34 PASS`, `coverage_gap=none`, `release_gate_modern=PASS`, `conformance_gate=PASS`, `negative_suite_ok=PASS`, `signoff_gate=PASS` |
| 2026-04-27 | M19 | IN_PROGRESS | Extended replay report with `Corner Coverage Closure` section and corner-signature pass/fail table (`mode|role|width|ss|order`) to localize future regressions quickly |
| 2026-04-27 | M19 | IN_PROGRESS | Added `Failure Signatures` section in replay report grouping failures by gate + corner signature with issue lists for deterministic regression triage (currently empty under all-pass state) |
| 2026-04-27 | M19 | DONE | Final closure validation rerun complete: modern `34/34 PASS`, `coverage_gap=none`, policy/sign-off gates PASS, and replay report includes both `Corner Coverage Closure` and `Failure Signatures` sections for long-run corner regression management |
| 2026-04-27 | M19 | DONE | Fixed 1-bit slave compile-path defect in `templates/spi_slave.v.tmpl` by guarding `shift_reg_tx` shifts for `DATA_WIDTH==1`; validated via new `issue-1036` (1-bit slave) with compile/sim PASS and full artifact generation |
| 2026-04-28 | M19 | DONE | Refreshed replay/sign-off with the new 1-bit slave case included: modern `35/35 PASS`, `coverage_gap=none`, and all policy gates remain PASS |
| 2026-04-28 | M20 | IN_PROGRESS | Started selected-slave sweep milestone by wiring parser->generator->templates->manifest/config path: added validated `selected_slave` field and template parameter binding for master/dual RTL and TB generation |
| 2026-04-28 | M20 | IN_PROGRESS | Added selected-index coverage policy in replay (`selected_slave_bucket` = `zero|nonzero`) and integrated into coverage-gap evaluation |
| 2026-04-28 | M20 | IN_PROGRESS | Added non-zero selected-index sweep cases `issue-1037` (master, selected_slave=2) and `issue-1038` (dual, selected_slave=3), with config/manifest persistence and simulation PASS |
| 2026-04-28 | M20 | DONE | End-to-end selected-slave path closure complete: parser->generator->TB->replay wired, selected-slave oracle green, replay policy PASS with modern `37/37 PASS` and `coverage_gap=none` including selected-index coverage |
| 2026-04-28 | M20 | DONE | Added user-facing `Selected Slave Index` field to legacy issue template and tightened config validation (`num_slaves <= max_slaves`) to keep selected-index sweep inputs consistent with declared limits |
| 2026-04-28 | M20 | DONE | Fixed SS graph semantic index labeling for compact bus encodings in `scripts/vcd_parser.py` (normalize SS width + Verilog bit-order index mapping), validated on `issue-1038` and revalidated replay/sign-off with modern `37/37 PASS` |
| 2026-04-28 | M21 | IN_PROGRESS | Added deterministic numeric-space scheduler `scripts/expand_replay_matrix.py` (full-grid target, missing-signature diff, bounded `--max-cases` generation, deterministic ordering) |
| 2026-04-28 | M21 | IN_PROGRESS | Generated two bounded scheduler batches (new modern cases through `issue-1098`) and refreshed replay/sign-off; expansion exposed `mode=1/master/width=1` compliance `NOT_RUN` corner |
| 2026-04-28 | M21 | IN_PROGRESS | Closed exposed corner regressions by fixing CPHA=1 receive boundary in `templates/spi_core.v.tmpl` and active-edge boundary filtering in `scripts/vcd_parser.py`; replay/sign-off restored to green with modern `94/94 PASS` |
| 2026-04-30 | M22 | PENDING | Added replay-validation enhancement scope for coverage metrics, higher-coverage matrix generation, pairwise feature interactions, and per-case runtime telemetry |
| 2026-04-30 | M22 | IN_PROGRESS | Implemented Step 1 in `scripts/replay_validation.py`: added `covered/target` representativeness table, 2-way special-feature pair coverage table, and aggregate representativeness score in `docs/SPI_REPLAY_VALIDATION_REPORT.md` (current score `69/70`, missing pair `interrupts=False x fifo_buffers=True`) |
| 2026-04-30 | M22 | IN_PROGRESS | Implemented Step 2 gap-driven generation support in `scripts/expand_replay_matrix.py` via `--target-feature-pair` and generated targeted case `issue-1099`; replay rerun now reports full pairwise closure (`special_feature_pairs_2way: 24/24`) and representativeness `70/70` |
| 2026-04-30 | M22 | IN_PROGRESS | Implemented Step 3 runtime telemetry in `scripts/replay_validation.py`: per-case `start/end/duration` table plus aggregate latency metrics (`min/max/mean/p50/p90`) now emitted in `docs/SPI_REPLAY_VALIDATION_REPORT.md` |
| 2026-04-30 | M22 | DONE | Implemented Step 4 iterative auto-close loop in `scripts/expand_replay_matrix.py` (`--auto-close`) with replay gate checks and closure detection; sanity run exits on stable closure in iteration 1 |
| 2026-04-30 | M22 | DONE | Re-ran full modern replay after telemetry upgrade (`--compact-modern-target 0`): report confirms modern `95/95 PASS`, `coverage_gap=none`, representativeness `70/70`, feature-pair closure `24/24`, and practical compact size computed from observed closure (`95`) |

## Status Legend

- `PENDING`: not started
- `IN_PROGRESS`: currently being implemented/validated
- `BLOCKED`: cannot proceed due to identified blocker
- `DONE`: milestone exit criteria met
