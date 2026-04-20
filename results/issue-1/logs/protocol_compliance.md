# SPI Protocol Compliance (evidence-based)

## Configuration
- Mode: 3 (CPOL=1, CPHA=1)
- Data width: 8
- Data order: MSB First
- Slave select polarity: Active Low

## Checks

| Check | Result | Notes |
|---|---:|---|
| `SCLK_idle_level_matches_CPOL` | **FAIL** | At busy=0 transition time 0ns, sclk=0 but expected idle 1. |
| `SS_n_matches_busy_window` | **NOT_RUN** | Multi-bit ss_n observed; framing check not implemented for bus-valued ss_n. |
| `MOSI_does_not_change_on_sampling_edge` | **PASS** | Checked 9 sampling edges (rising). |

## Evidence pointers
- VCD: `results/issue-1/data/spi_waveform.vcd`
- Timescale: `(1, 'ns')`
