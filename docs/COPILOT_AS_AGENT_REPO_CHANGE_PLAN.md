## Implementation plan: Copilot-as-agent workflows in `spi-customizer`

This plan is expressed as **concrete file targets** and **responsibilities** so an agent (or contributor) can implement/extend the Copilot-as-agent model without reverse-engineering.

### CI posture (artifacts over commits)

- **Target**: `.github/workflows/spi-automation.yml`
- **Goal**: Upload per-issue outputs as GitHub Actions artifacts and post issue comments; do not commit generated outputs back to `main`.
- **Implementation**:
  - Install dependencies from `tools/requirements.txt`
  - Keep `actions/upload-artifact` for `results/issue-<n>/**`
  - Remove any workflow steps that modify git identity or push commits

### Issue templates (separate intent types)

- **Target directory**: `.github/ISSUE_TEMPLATE/`
- **Add**:
  - `5-spi-spec-intent.yml` (spec intent: behavior + acceptance criteria)
  - `6-spi-verification-request.yml` (verification intent: explicit protocol checks)
  - `7-spi-debug-request.yml` (debug intent: symptom + evidence + repro config)
- **Keep**:
  - `1-spi-config-form.yml` as a parameter-centric path for users who already know the knobs

### Stable agent behavior (instructions)

- **Target**: `.github/copilot-instructions.md`
- **Goal**: Ensure Copilot behaves as an engineer:
  - evidence-first
  - no synthetic verification
  - traceability requirements
  - required artifacts per issue type

### Traceability: manifest + correct artifact linking

- **Targets**:
  - `scripts/process_issue.py` (write `logs/run_manifest.json`)
  - `scripts/vcd_parser.py` (consume manifest when generating `logs/SUMMARY.md`)
- **Goal**: Make it easy to answer:
  - “Which issue intent/config produced this RTL?”
  - “Which files were generated and where are they?”
  - “Which tools/versions produced the evidence?”
- **Implementation**:
  - `scripts/process_issue.py` writes `results/issue-<n>/logs/run_manifest.json` containing:
    - issue-body hash
    - parsed config (canonical)
    - generated RTL/TB relpaths
    - tool versions (best-effort)
  - `scripts/vcd_parser.py` uses the manifest or `code/` scan to report correct filenames instead of hard-coded placeholders.

### Verification as a first-class artifact (protocol compliance report)

- **Targets**:
  - `scripts/vcd_parser.py` (implement compliance checker; emit `logs/protocol_compliance.md`)
  - `scripts/process_issue.py` (invoke compliance checker after VCD parse)
- **Goal**: Convert “we ran a testbench” into explicit, auditable checks tied to evidence.
- **Implementation**:
  - Run compliance checks only when real VCD evidence exists.
  - Output `results/issue-<n>/logs/protocol_compliance.md` with:
    - configuration recap (mode/CPOL/CPHA/polarity/bit-order)
    - explicit checks (pass/fail/not-run) and notes about missing signals/evidence

### Evidence integrity: prohibit synthetic waveforms

- **Target**: `scripts/simulator_runner.py`
- **Goal**: Ensure compliance/debug results are never based on synthetic VCD output.
- **Implementation**:
  - Require real `iverilog` + `vvp` to compile/simulate.
  - Fail the simulation step if tools are missing or if VCD is not generated.

