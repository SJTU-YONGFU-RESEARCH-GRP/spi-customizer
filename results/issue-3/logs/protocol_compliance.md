# SPI Protocol Compliance (evidence-based)

## Configuration
- Mode: 2 (CPOL=1, CPHA=0)
- Data width: 32
- Data order: MSB First
- Slave select polarity: Active Low

## Checks

| Check | Result | Notes |
|---|---:|---|
| `SCLK_idle_level_matches_CPOL` | **PASS** | Checked sclk at 2 master-mode busy=0 boundaries against CPOL=1. |
| `SS_n_matches_busy_window` | **PASS** | Checked ss_n activity at 1 busy=1 boundaries. |
| `MOSI_does_not_change_on_sampling_edge` | **PASS** | Checked 34 sampling edges (falling). |

## Evidence pointers
- VCD: `results/issue-3/data/spi_waveform.vcd`
- Timescale: `(1, 'ns')`
