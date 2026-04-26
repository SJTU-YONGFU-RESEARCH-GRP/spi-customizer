# SPI Replay Validation Report

- Cases evaluated: **25**
- Passed all gates: **10**
- Failed at least one gate: **15**
- Modern cases (post-fix replay set): **10**, pass: **10**
- Legacy cases (historical artifacts): **15**, pass: **0**

## Policy Verdict

- `release_gate_modern`: **PASS**
- `coverage_gap`: **none**

## Gate Definitions

- `compile_ok`: compilation log indicates success
- `sim_ok`: simulation log has return code 0 and no `FATAL:`
- `vcd_ok`: non-empty `spi_waveform.vcd` exists
- `compliance_ok`: compliance report exists, has check table, and no `FAIL`/`NOT_RUN` checks
- `summary_ok`: summary exists with key metrics
- `consistency_ok`: summary metrics match CSV/log-derived values
- `spec_oracle_ok`: compliance/log evidence satisfies issue-derived verification spec
- `rtl_tb_semantic_ok`: generated RTL/TB structure and semantic checks match spec

## Per-Issue Results

| Issue | Overall | compile_ok | sim_ok | vcd_ok | compliance_ok | summary_ok | consistency_ok | spec_oracle_ok | rtl_tb_semantic_ok |
|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | FAIL | Y | Y | N | N | Y | N | N | N |
| 3 | FAIL | N | N | Y | Y | Y | Y | N | N |
| 36 | FAIL | Y | Y | Y | N | N | N | N | N |
| 37 | FAIL | Y | Y | Y | N | N | N | N | N |
| 38 | FAIL | Y | Y | Y | N | N | N | N | N |
| 39 | FAIL | Y | Y | Y | N | N | N | N | N |
| 42 | FAIL | Y | Y | Y | N | N | N | N | N |
| 43 | FAIL | Y | Y | Y | N | N | N | N | N |
| 44 | FAIL | Y | Y | Y | N | N | N | N | N |
| 45 | FAIL | Y | Y | Y | N | N | N | N | N |
| 46 | FAIL | Y | Y | Y | N | N | N | N | N |
| 48 | FAIL | Y | N | Y | N | N | N | N | N |
| 49 | FAIL | Y | N | Y | N | N | N | N | N |
| 50 | FAIL | Y | Y | Y | N | N | N | N | N |
| 51 | FAIL | Y | Y | Y | N | N | N | N | N |
| 1002 | PASS | Y | Y | Y | Y | Y | Y | Y | Y |
| 1003 | PASS | Y | Y | Y | Y | Y | Y | Y | Y |
| 1004 | PASS | Y | Y | Y | Y | Y | Y | Y | Y |
| 1005 | PASS | Y | Y | Y | Y | Y | Y | Y | Y |
| 1006 | PASS | Y | Y | Y | Y | Y | Y | Y | Y |
| 1007 | PASS | Y | Y | Y | Y | Y | Y | Y | Y |
| 1008 | PASS | Y | Y | Y | Y | Y | Y | Y | Y |
| 1009 | PASS | Y | Y | Y | Y | Y | Y | Y | Y |
| 1010 | PASS | Y | Y | Y | Y | Y | Y | Y | Y |
| 1011 | PASS | Y | Y | Y | Y | Y | Y | Y | Y |

## Coverage Matrix (Modern Cases)

| Mode | Role | Width Class | SS Polarity | Bit Order | Cases |
|---:|---|---|---|---|---:|
| 0 | master | 16 | active_low | lsb_first | 1 |
| 0 | master | 8 | active_low | lsb_first | 1 |
| 1 | slave | other | active_low | msb_first | 1 |
| 2 | dual | 16 | active_high | msb_first | 1 |
| 2 | dual | 16 | active_low | msb_first | 1 |
| 2 | dual | 32 | active_low | msb_first | 3 |
| 3 | master | 32 | active_low | msb_first | 1 |
| 3 | slave | 8 | active_low | msb_first | 1 |

## Template Input Coverage (Modern Cases)

| Dimension | Covered Values | Required Values |
|---|---|---|
| bit_order | lsb_first, msb_first | lsb_first, msb_first |
| clock_jitter_test | False, True | False, True |
| default_data_enabled | False, True | False, True |
| default_data_pattern | 0000, 5555, a5a5, custom, ffff, unknown | 0000, 5555, a5a5, custom, ffff |
| dma_support | False, True | False, True |
| fifo_buffers | False, True | False, True |
| interrupts | False, True | False, True |
| mode | 0, 1, 2, 3 | 0, 1, 2, 3 |
| multi_master | False, True | False, True |
| role | dual, master, slave | dual, master, slave |
| ss_polarity | active_high, active_low | active_high, active_low |
| test_duration | brief, comprehensive, standard | brief, comprehensive, standard |
| waveform_capture | False, True | False, True |

## Triage View

### Modern Cases (Release Gate Candidates)

- issue-1002: PASS
- issue-1003: PASS
- issue-1004: PASS
- issue-1005: PASS
- issue-1006: PASS
- issue-1007: PASS
- issue-1008: PASS
- issue-1009: PASS
- issue-1010: PASS
- issue-1011: PASS

### Legacy Failures (Historical Artifacts)

- Count: 15
- Primary pattern: missing compliance/summary-consistency artifacts from older runs.
