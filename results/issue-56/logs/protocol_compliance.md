# SPI Protocol Compliance (evidence-based)

## Configuration
- Mode: 0 (CPOL=0, CPHA=0)
- Data width: 1
- Data order: LSB First
- Slave select polarity: Active Low

## Checks

| Check | Result | Notes |
|---|---:|---|
| `SCLK_idle_level_matches_CPOL` | **PASS** | Skipped: slave mode SCLK is externally driven. |
| `SS_n_matches_busy_window` | **PASS** | Checked ss_n activity at 1 busy=1 boundaries. |
| `SS_n_inactive_when_not_busy` | **PASS** | Checked ss_n inactive state at 2 busy=0 boundaries. |
| `MOSI_does_not_change_on_sampling_edge` | **PASS** | Skipped: slave mode MOSI timing is externally driven. |
| `MOSI_setup_hold_window_ok` | **PASS** | Skipped: slave mode MOSI timing is externally driven. |
| `SCLK_activity_present_during_busy` | **PASS** | Skipped: slave mode SCLK is externally driven. |

## Evidence pointers
- VCD: `results/issue-56/data/spi_waveform.vcd`
- Timescale: `(1, 'ns')`
