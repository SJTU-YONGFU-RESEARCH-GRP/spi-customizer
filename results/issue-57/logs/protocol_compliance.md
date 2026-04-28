# SPI Protocol Compliance (evidence-based)

## Configuration
- Mode: 0 (CPOL=0, CPHA=0)
- Data width: 30
- Data order: MSB First
- Slave select polarity: Active Low

## Checks

| Check | Result | Notes |
|---|---:|---|
| `SCLK_idle_level_matches_CPOL` | **PASS** | Checked sclk at 2 master-mode busy=0 boundaries against CPOL=0. |
| `SS_n_matches_busy_window` | **PASS** | Checked ss_n activity at 1 busy=1 boundaries. |
| `SS_n_inactive_when_not_busy` | **PASS** | Checked ss_n inactive state at 2 busy=0 boundaries. |
| `MOSI_does_not_change_on_sampling_edge` | **PASS** | Checked 31 active-transaction sampling edges (rising). |
| `MOSI_setup_hold_window_ok` | **PASS** | Checked 31 sampling edges with >= 1ns setup/hold margin (min observed 20000ns). |
| `SCLK_activity_present_during_busy` | **PASS** | Checked SCLK activity for 1 busy windows. |

## Evidence pointers
- VCD: `results/issue-57/data/spi_waveform.vcd`
- Timescale: `(1, 'ns')`
