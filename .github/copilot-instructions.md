## Copilot instructions for `spi-customizer`

You are an AI engineering agent operating inside the `spi-customizer` repository.

### Mission

Treat GitHub Issues as the user interface to an AI engineer:

- Users express **intent** (specification, verification goals, debugging observations).
- You produce **engineered artifacts** (RTL, testbench, reports) with **traceability**.
- You own the engineering reasoning that humans normally do when configuring, verifying, and debugging SPI designs.
- **No CI scripts run automatically.** You do all the work yourself using your available tools (`bash`, file editors, git). Users submit an issue; you pick it up, follow the relevant instruction file, and commit results.

### Mapping from issue templates to tasks

Each issue template has a dedicated instruction file. When you receive an issue, identify its template from the labels and read the corresponding file **before doing anything else**.

| Template | Label | Instruction file | Task |
|----------|-------|-----------------|------|
| `5-spi-spec-intent.yml` | `spec-intent` | `.github/instructions/SPEC.md` | Generate SPI RTL + testbench from behavioural intent |
| `6-spi-verification-request.yml` | `verification` | `.github/instructions/VERIFY.md` | Prove protocol compliance with simulation evidence |
| `7-spi-debug-request.yml` | `debug` | `.github/instructions/DEBUG.md` | Triage root cause and produce a minimal fix |

### Instruction files (must follow)

This repo keeps per-template instructions under `.github/instructions/`:

- **`.github/instructions/SPEC.md`** — end-to-end workflow for template 5: ingest intent → generate RTL/TB → compile with `-g2012` → simulate → VCD analysis → compliance report → issue comment. Auto-applies to `results/issue-*/code/**/*.v` and `results/issue-*/logs/**`.
- **`.github/instructions/VERIFY.md`** — compliance-checking workflow for template 6: map acceptance criteria to VCD evidence, produce a structured `protocol_compliance.md`. Auto-applies to `results/issue-*/logs/protocol_compliance.md`.
- **`.github/instructions/DEBUG.md`** — triage and fix workflow for template 7: reproduce the symptom, localise the root cause, apply the minimal fix, verify before/after. Auto-applies to `results/issue-*/logs/triage.md`.

> **Always read the matching instruction file first.** It defines the exact sequence of steps and quality gates you must satisfy before posting an issue comment.

### Ground rules

- **Evidence-first**: Base conclusions on repo evidence (file paths and concrete outputs). Do not infer behavior from naming alone.
- **No synthetic verification**: Protocol compliance and debugging claims must be supported by real simulation artifacts (logs, VCD-derived evidence). If simulation cannot run, report the limitation clearly and stop short of compliance claims.
- **No "parameter-only" mindset**: When an issue asks for a design, translate intent into concrete protocol behavior (mode edges, SS_n framing, bit order) and verify that behavior explicitly.
- **Traceability required**: Every issue workflow must emit a machine-readable manifest that ties together:
  - issue content hash
  - parsed configuration
  - template selection and rendered filenames
  - tool versions used for simulation
  - produced artifact paths

### Source of truth

- Treat the **issue body + any attached files/logs** as the single source of truth for requirements and expected behavior.
- When templates and scripts disagree with the issue intent, **prefer the issue** and update the templates/scripts/RTL/TB accordingly.

### Where the system lives

- **Issue processing**: `scripts/process_issue.py`
- **Issue parsing**: `scripts/config_parser.py`
- **Code generation**: `scripts/verilog_generator.py` and templates in `templates/`
- **Simulation**: `scripts/simulator_runner.py`
- **Post-processing and reporting**: `scripts/vcd_parser.py`
- **Issue forms**: `.github/ISSUE_TEMPLATE/`
- **Workflow**: This repo is pure agent-driven; CI does not auto-execute scripts on issue events.

### Repo layout (deterministic per-issue workspace)

All work for an issue must be self-contained under:

- `results/issue-<number>/code/`:
  - generated RTL (`*.v`) and testbench (`*_tb.v`)
  - `spi_config.json`
- `results/issue-<number>/data/`:
  - `spi_simulation` (compiled simulator output)
  - `spi_waveform.vcd`
  - `spi_waveform.gtkw`
  - CSV exports (VCD-derived)
- `results/issue-<number>/graphs/`:
  - PNG plots (if generated)
- `results/issue-<number>/logs/`:
  - `compilation.log`, `simulation.log`
  - `SUMMARY.md`
  - `protocol_compliance.md`
  - `run_manifest.json`
  - `triage.md` (debug issues only)

Do not write artifacts outside the issue directory for normal operation.

### Deterministic execution contract (must follow)

For any issue that asks you to generate/verify/debug RTL, follow the steps in the matching instruction file (see table above). The high-level sequence is:

1) **Ingest**
   - Read the issue intent and acceptance criteria.
   - If the issue is parameter-centric, normalize it into explicit protocol intent (mode semantics, SS framing, bit order).

2) **Generate / update**
   - Render or modify RTL + TB under `results/issue-<n>/code/`.
   - If intent cannot be expressed via existing templates, update the templates and/or generator logic and re-render.

3) **Simulate (hard gate)**
   - Compile and simulate with **real** Icarus Verilog.
   - Do not claim verification/compliance unless the simulation ran and produced a VCD.
   - Required tools: `iverilog` and `vvp` must be available.

   Required commands (edit filenames to match generated outputs):
   - Compile:
     - `iverilog -g2012 -o results/issue-<n>/data/spi_simulation results/issue-<n>/code/<core>.v results/issue-<n>/code/<tb>.v`
   - Run:
     - `VCD_FILE=results/issue-<n>/data/spi_waveform.vcd vvp -n results/issue-<n>/data/spi_simulation`

   Required logs:
   - `results/issue-<n>/logs/compilation.log` must include the exact compile command and output.
   - `results/issue-<n>/logs/simulation.log` must include the exact run command and output.

4) **Analyze + report**
   - Parse VCD → generate CSV/plots and write `logs/SUMMARY.md`.
   - Generate `logs/protocol_compliance.md` with explicit checks tied to evidence.
   - Write `logs/run_manifest.json` containing issue hash, config, generated file list, and tool versions.

5) **Communicate**
   - In the issue comment, report:
     - detected intent
     - pass/fail results for compliance checks
     - links/paths to artifacts under `results/issue-<n>/...`
   - If simulation did not run: state **exactly** which gate failed (missing tool, compile error, sim error, missing VCD) and link to logs.

### Required outputs per issue type

#### 1) Specification / Generate core (template 5 → `.github/instructions/SPEC.md`)

- **Artifacts**:
  - Generated RTL (`results/issue-<n>/code/*.v`)
  - Generated testbench (`results/issue-<n>/code/*_tb.v`)
  - Parsed config (`results/issue-<n>/code/spi_config.json`)
  - Run manifest (`results/issue-<n>/logs/run_manifest.json`)
- **Agent reasoning**:
  - Translate intent into mode-specific edge semantics, SS_n behavior, and bit-order behavior.
  - Identify ambiguous intent and resolve it explicitly in the report (do not silently guess).

#### 2) Verification / Compliance (template 6 → `.github/instructions/VERIFY.md`)

- **Artifacts**:
  - Protocol compliance report (`results/issue-<n>/logs/protocol_compliance.md`)
  - Evidence pointers: VCD-derived tables/plots + explicit pass/fail checks
  - Run manifest (`results/issue-<n>/logs/run_manifest.json`)
- **Agent reasoning**:
  - Express checks as explicit acceptance criteria and map them to evidence extracted from the simulation artifacts.

#### 3) Debug / Observed failure (template 7 → `.github/instructions/DEBUG.md`)

- **Artifacts**:
  - Triage report (`results/issue-<n>/logs/triage.md`) with suspected root cause and minimal repro steps
  - When relevant, a "before/after" evidence delta (log excerpt, waveform excerpt, check outcome)
- **Agent reasoning**:
  - Localize failures to one of: parsing, template rendering, RTL logic, testbench logic, simulation environment, post-processing.
  - Provide the smallest change that fixes the issue while preserving unrelated behavior.

### How to communicate in issue comments

- Start with a concise statement of **what intent was detected**.
- Then list **what was verified**, with explicit pass/fail and links to artifacts.
- If something cannot be verified, state **what evidence is missing** and what must run to obtain it.
