# Issue Workflow Migration Plan

## Goal

Switch from agent-specific GitHub paths to a single finalized issue-driven generation workflow.

## Scope (Confirmed)

- Keep `/.github/ISSUE_TEMPLATE/1-spi-config-form.yml` unchanged.
- Remove agent-only issue templates:
  - `/.github/ISSUE_TEMPLATE/5-spi-spec-intent.yml`
  - `/.github/ISSUE_TEMPLATE/6-spi-verification-request.yml`
  - `/.github/ISSUE_TEMPLATE/7-spi-debug-request.yml`
- Remove agent-specific instruction files:
  - `/.github/copilot-instructions.md`
  - `/.github/instructions/SPEC.md`
  - `/.github/instructions/VERIFY.md`
  - `/.github/instructions/DEBUG.md`
- Rewrite `/.github/workflows/spi-automation.yml` to the finalized script-driven generation process (issue submission -> generation/simulation/artifacts), without replay/debug gate logic.

## Implementation Steps and Tracking

| Step | Action | Status |
|---|---|---|
| 1 | Create this migration plan document | DONE |
| 2 | Delete templates `5/6/7` | DONE |
| 3 | Delete agent instruction files and `copilot-instructions.md` | DONE |
| 4 | Replace `spi-automation.yml` with finalized issue-processing workflow | DONE |
| 5 | Validate workflow YAML and repo state | DONE |

## Progress Log

| Time (UTC+8) | Step | Status | Notes |
|---|---|---|---|
| 2026-04-28 03:06 | 1 | DONE | Plan created and scope locked to user-approved changes only |
| 2026-04-28 03:07 | 2 | DONE | Removed `5-spi-spec-intent.yml`, `6-spi-verification-request.yml`, `7-spi-debug-request.yml` |
| 2026-04-28 03:07 | 3 | DONE | Removed `.github/copilot-instructions.md` and `.github/instructions/{SPEC,VERIFY,DEBUG}.md` |
| 2026-04-28 03:09 | 4 | DONE | Replaced `.github/workflows/spi-automation.yml` with finalized issue-processing CI (issue event + manual dispatch, `process_issue.py`, artifact upload) |
| 2026-04-28 03:09 | 5 | DONE | Verified workflow YAML parses (`YAML OK`) and confirmed expected file-change set in git status |
| 2026-04-28 03:16 | 4 | DONE | Updated workflow to persist `results/issue-<n>/` into repo tree via commit+push (with no-op guard when no changes) |
| 2026-04-28 03:23 | 4 | DONE | Hardened workflow with safeguards: skip bot-edited issue reruns, per-issue concurrency lock, explicit branch push target, and rebase+retry push loop |
| 2026-04-28 03:23 | 5 | DONE | Revalidated hardened workflow syntax (`YAML OK`) |
| 2026-04-28 03:32 | 4 | DONE | Confirmed strict SPI-template body filter is retained and CI system dependency remains `iverilog` only (no `gtkwave` install) |
| 2026-04-28 03:38 | 4 | DONE | Switched `spi-automation.yml` to run in prebuilt GHCR container `ghcr.io/<owner>/spi-customizer-ci:latest`, removing per-run apt/pip install steps |
| 2026-04-28 03:38 | 4 | DONE | Added `.github/workflows/build-ci-image.yml` to build and publish CI image to GHCR on demand and when Docker/requirements change on `main` |
| 2026-04-28 03:38 | 4 | DONE | Updated `Dockerfile` to keep CI runtime minimal (`iverilog` + Python deps; removed `gtkwave`) |
| 2026-04-28 03:42 | 4 | DONE | Fixed GHCR tag casing bug by switching image references to lowercase org path `ghcr.io/sjtu-yongfu-research-grp/spi-customizer-ci:*` |
| 2026-04-28 03:45 | 4 | DONE | Fixed container dependency resolution by installing `python3-numpy/python3-matplotlib` via apt and switching pip install to `tools/requirements-minimal.txt` |
