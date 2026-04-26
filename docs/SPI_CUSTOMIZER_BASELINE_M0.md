# SPI Customizer Baseline Report (Milestone 0)

## Baseline Objective

Establish the current behavior of the generated-output pipeline and identify failure categories before applying template/script fixes.

## Replay Corpus (Initial)

Current corpus selected from existing `results/issue-*/code/spi_config.json` artifacts:

| Issue | Mode | Data Width | Slaves | Notes |
|---|---:|---:|---:|---|
| 1 | 3 | 8 | 4 | feature-heavy config |
| 3 | 2 | 32 | 4 | known dual-mode correctness issue |
| 36 | 2 | 8 | 3 | mode 2 sample |
| 37 | 0 | 8 | 3 | mode 0 sample |
| 39 | 2 | 8 | 3 | brief duration |
| 42 | 2 | 8 | 3 | fifo enabled |
| 46 | 0 | 8 | 3 | all special features enabled |
| 48 | 3 | 7 | 3 | non-byte width |
| 49 | 3 | 1 | 1 | 1-bit width edge case |
| 50 | 3 | 3 | 3 | 3-bit width edge case |
| 51 | 1 | 8 | 1 | mode 1 sample |

## Baseline Findings (Current State)

### A) Verified defects

1. Dual testbench payload mismatch in issue 3:
   - Stimulus claims byte payload (`0x5A`) but transaction is 7 bits.
   - Resulting receive value is truncated/misaligned versus intent.
   - Impact: simulation can report success while functional intent is wrong.

2. Report-layer inconsistency in issue 3:
   - Summary/log artifacts include contradictory metrics and malformed timing mapping.
   - Impact: post-processing output is not always trustworthy as verification evidence.

### B) Structural gaps observed in current artifacts

1. `spi_config.json` does not persist `spi_role` for current stored runs.
2. Historical runs indicate frequent `simulation_success: true` / `waveform_success: true`, but this alone is not a correctness proof without protocol-level checks and TB assertions.

## Failure Categories for Fix Tracking

- `TB_STIMULUS_MISMATCH`: testbench declared transaction != driven bits/edges.
- `VCD_MAPPING_ERROR`: parser/report maps signals/columns incorrectly.
- `COMPLIANCE_GAP`: protocol check is missing or marked not-run despite available evidence.
- `SUMMARY_CONTRADICTION`: KPI fields conflict with parsed signal data.
- `SPEC_TRACE_GAP`: issue intent/acceptance not fully carried into evidence checks.

## Next Action (Milestone 1)

Fix `TB_STIMULUS_MISMATCH` first in templates, then rerun the corpus and recategorize residual failures.
