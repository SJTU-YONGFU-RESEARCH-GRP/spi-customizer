## Issue-driven Copilot-as-agent workflows for `spi-customizer`

This repo’s baseline workflow is already Issue-driven, but most intent is currently expressed as parameters. The workflow types below separate **spec intent**, **verification intent**, and **debug intent** so an agent can own the engineering reasoning.

### Workflow 1: Spec intent → Generate core + tests

- **Issue template**: `.github/ISSUE_TEMPLATE/5-spi-spec-intent.yml`
- **User intent captured**:
  - Plain-language behavior (what the core must do)
  - Example transactions (expected)
  - Explicit acceptance criteria (what must be proven)
  - Core parameters (mode/width/slaves/role/features)
- **Agent reasoning required**:
  - Translate intent into protocol semantics: CPOL/CPHA sampling edge, SS_n framing, bit order.
  - Detect ambiguity (e.g. user describes “sample on falling edge” but selects Mode 0) and resolve it explicitly.
  - Decide which checks are required to satisfy acceptance criteria.
- **Artifacts produced** (per issue directory):
  - `code/*.v`, `code/*_tb.v`, `code/spi_config.json`
  - `logs/run_manifest.json` (provenance and file list)
  - `logs/protocol_compliance.md` (explicit checks + evidence pointers)
- **Why this improves current flow**:
  - Users can specify “what they need” without being SPI experts.
  - Acceptance criteria becomes a contract the agent must prove, not a tacit assumption.

### Workflow 2: Verification intent → Compliance report tied to evidence

- **Issue template**: `.github/ISSUE_TEMPLATE/6-spi-verification-request.yml`
- **User intent captured**:
  - “What must be verified” (properties and criteria)
  - Parameters under test (for reproduction)
- **Agent reasoning required**:
  - Convert criteria into mode-specific checks:
    - sampling edge correctness (Mode-specific)
    - MOSI change edge correctness (Mode-specific)
    - SS_n framing correctness (asserted for full frame; stable within a frame)
    - bit-order correctness (MSB/LSB)
  - Tie each pass/fail decision to evidence from simulation (VCD + logs).
- **Artifacts produced**:
  - `logs/protocol_compliance.md`
  - `logs/run_manifest.json`
  - Standard simulation + VCD analysis outputs (`data/`, `graphs/`, `logs/SUMMARY.md`)
- **Why this improves current flow**:
  - Turns “we ran a testbench” into “we proved specific protocol properties”.
  - Makes compliance auditable and reproducible.

### Workflow 3: Debug intent → Triage + minimal fix + evidence delta

- **Issue template**: `.github/ISSUE_TEMPLATE/7-spi-debug-request.yml`
- **User intent captured**:
  - Symptom, expected vs observed, and evidence pointers
  - Reference issue number (for reproduction)
- **Agent reasoning required**:
  - Classify likely root cause location:
    - parsing ambiguity (`scripts/config_parser.py`)
    - template wiring (`templates/`)
    - RTL logic bug (generated module)
    - testbench bug (`templates/*_tb.v.tmpl`)
    - simulation environment gap (`scripts/simulator_runner.py`)
    - post-processing/reporting (`scripts/vcd_parser.py`)
  - Reproduce the failure and propose the smallest correct fix.
  - Show a before/after evidence delta (check outcome, log excerpt, waveform metric).
- **Artifacts produced**:
  - `logs/triage.md`
  - Updated compliance report and run manifest for the repro run
- **Why this improves current flow**:
  - Debugging becomes structured and evidence-based.
  - Root cause analysis and decision history stays inside the issue thread.

### Workflow 4: Refactor intent → Maintainability improvements without behavior change

- **Issue template**: (use Feature Request for now: `.github/ISSUE_TEMPLATE/3-feature-request.yml`)
- **User intent captured**:
  - “Refactor for clarity / performance / parameter isolation”
- **Agent reasoning required**:
  - Preserve behavioral invariants across all modes/roles.
  - Prove non-regression by re-running representative configs (existing test suite approach in `scripts/test.py`).
- **Artifacts produced**:
  - Refactor plan + rationale
  - Regression run evidence (logs/manifests)

