# SPI Protocol Compliance (evidence-based)

## Configuration
- Mode: 3 (CPOL=1, CPHA=1)
- Data width: 16
- Data order: MSB First
- Slave select polarity: Active Low

## Checks

| Check | Result | Notes |
|---|---:|---|
| `SCLK_idle_level_matches_CPOL` | **PASS** | Checked sclk at 6 master-mode busy=0 boundaries against CPOL=1. |
| `SS_n_matches_busy_window` | **PASS** | Checked ss_n activity at 5 busy=1 boundaries. |
| `SS_n_inactive_when_not_busy` | **PASS** | Checked ss_n inactive state at 6 busy=0 boundaries. |
| `MOSI_does_not_change_on_sampling_edge` | **PASS** | Checked 80 active-transaction sampling edges (rising). |
| `MOSI_setup_hold_window_ok` | **PASS** | Checked 80 sampling edges with >= 1ns setup/hold margin (min observed 80000ns). |
| `SCLK_activity_present_during_busy` | **PASS** | Checked SCLK activity for 5 busy windows. |

## Evidence pointers
- VCD: `results/issue-59/data/spi_waveform.vcd`
- Timescale: `(1, 'ns')`
