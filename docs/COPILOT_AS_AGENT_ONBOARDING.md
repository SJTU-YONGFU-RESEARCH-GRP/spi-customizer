## Copilot-as-Agent onboarding for `spi-customizer`

This repository contains scripts and templates for SPI RTL generation and verification, but the intended workflow is **pure agent-driven**: GitHub Issues encode intent, and a Copilot agent owns the engineering reasoning (generation, verification, debugging). Scripts in `scripts/` are optional utilities the agent may choose to use.

### Repository map (start here)

- **Issue processing entrypoint**: `scripts/process_issue.py`
  - Fetch issue body (GitHub API or local override)
  - Parse config → generate RTL/TB → run simulation → run VCD analysis → write per-issue artifacts
  - Update the issue status text (and labels/state in GitHub mode)
- **Issue body → configuration**: `scripts/config_parser.py`
  - Regex-based parsing of the issue body text and validation into `SPIConfig`
- **Config → RTL/TB generation**: `scripts/verilog_generator.py`
  - Renders Jinja templates in `templates/` based on `SPIConfig.spi_role`
- **Simulation**: `scripts/simulator_runner.py`
  - Compiles and runs with Icarus Verilog (`iverilog`/`vvp`)
  - Produces `results/issue-<id>/data/spi_waveform.vcd` and logs
- **Post-sim analysis**: `scripts/vcd_parser.py`
  - VCD parsing, CSV generation, plot generation, and `logs/SUMMARY.md`
- **Issue forms (the user interface)**: `.github/ISSUE_TEMPLATE/`
  - Primary configuration form: `.github/ISSUE_TEMPLATE/1-spi-config-form.yml`
- **Agent instructions (the workflow engine)**: `.github/copilot-instructions.md`

### Current user journey (what a human does today)

- A user opens a GitHub issue using the SPI configuration Issue Form.
- The Copilot agent interprets intent, generates/updates RTL and tests as needed, and produces artifacts under `results/issue-<issue_number>/`.
- The agent reports results (and evidence) back into the issue thread.

### Determinism requirement (non-negotiable)

The agent workflow must be deterministic in **artifacts** and **validation gates**:

- Always produce the same per-issue directory structure under `results/issue-<n>/...`.
- Never claim “verified” unless real `iverilog`/`vvp` simulation ran and produced a VCD.
- Always write `logs/compilation.log`, `logs/simulation.log`, `logs/SUMMARY.md`, `logs/protocol_compliance.md`, and `logs/run_manifest.json`.

### Implicit assumptions (engineering reasoning currently pushed onto humans)

- **Protocol semantics are assumed**: users must know what “Mode 0/1/2/3” means, which edge data is sampled on, and how SS_n should behave for their device.
- **Parameter correctness is fragile**: mismatches (e.g. polarity expectations, bit order, role selection) are easy to specify incorrectly and hard to diagnose from “pass/fail”.
- **Verification is mostly “smoke-test”**: the system produces a waveform and summary, but doesn’t yet treat protocol compliance checks as first-class outputs with explicit acceptance criteria.
- **Traceability is incomplete**: users can’t always answer “which intent produced this RTL?” or “what exactly was checked?” without reading code and logs.

### Pain points to explicitly look for during onboarding

- Where issue inputs can become ambiguous or contradictory after being converted to plain issue-body text.
- Where generated artifacts (RTL/TB/summary) do not fully match what the user asked for (or what the form implies).
- Where simulation failures are not explained in terms a non-SPI expert can act on.
- Where post-processing reports infer “protocol compliance” without an explicit checklist tied to evidence.

### “Copilot-as-Agent” philosophy for this repo

Treat GitHub Issues as the primary UI for an AI engineer:

- A user issue should be able to express **intent**, not just knobs.
- The agent should produce **artifacts with provenance**, not just files.
- The agent should do the reasoning humans do today:
  - translate intent into parameter choices
  - decide what must be verified and how
  - triage failures and propose fixes
  - explain design tradeoffs and limitations

### Ready-to-use onboarding prompt (paste into Copilot/LLM)

```text
You are an AI engineering agent operating inside the repository `spi-customizer`.

Your job is to onboard yourself by exploring the repository as an engineering system, then propose concrete “Copilot-as-agent via GitHub Issues” workflows that improve verification, user experience, and traceability.

Constraints:
- Do not generate code blindly.
- Base every claim on evidence you find in this repo (file paths, templates, scripts).
- Think from first principles: “What reasoning is humans doing today, and how can an agent own it instead?”

Step 1 — Map the system as it exists today
- Identify the components that can support an agent-driven workflow (not a rigid CI pipeline).
- Locate the main entrypoints and understand what each component can produce:
  - `scripts/process_issue.py`
  - `scripts/config_parser.py`
  - `scripts/verilog_generator.py`
  - `scripts/simulator_runner.py`
  - `scripts/vcd_parser.py`
  - templates in `templates/`
  - issue forms in `.github/ISSUE_TEMPLATE/`
  - agent instructions in `.github/copilot-instructions.md`

Step 2 — Identify friction points (engineering, not cosmetics)
- Where can users specify invalid or ambiguous SPI intent?
- Where does the system silently assume protocol details (CPOL/CPHA edge semantics, SS_n behavior, bit order)?
- Where does verification fall short of protocol compliance (what is checked vs what is implied)?
- Where is traceability weak (config→RTL mapping, reproducibility, provenance)?

Step 3 — Propose Copilot-as-agent issue-driven workflows
Reframe GitHub issues as the interface to an AI engineer. Propose concrete issue types (templates) and define:
- What user intent is captured (spec intent / verify intent / debug intent / refactor intent)
- What reasoning the agent must perform
- What artifacts are produced (RTL, TB, compliance report, manifest/provenance, failure triage report)
- How each workflow improves usability and correctness over parameter-only requests

Step 4 — Verification as a first-class outcome
Propose how the agent should generate explicit protocol checks:
- Mode-specific sampling edge checks (CPHA/CPOL)
- SS_n framing checks (assert SS active for the full frame; clean deassert)
- Bit-order checks (MSB/LSB correctness)
- Optional: jitter tolerance checks and timing margin reporting
Tie each check to evidence extracted from simulation artifacts (VCD/logs), not assumptions.

Step 5 — Traceability and provenance
Propose a minimal “run manifest” that links:
- issue content hash / parsed config
- template versions (or git commit)
- tool versions used for simulation
- paths to generated artifacts

Output format:
- A structured analysis with explicit repo citations (file paths)
- A concrete proposal of 3–6 issue templates with reasoning + artifacts
- A prioritized implementation plan: what files to change and why
```

