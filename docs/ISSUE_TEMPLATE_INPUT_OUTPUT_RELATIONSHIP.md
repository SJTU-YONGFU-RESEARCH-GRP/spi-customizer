# Issue Template Input/Output Relationship

This document maps each input from `.github/ISSUE_TEMPLATE/1-spi-config-form.yml` to the generated waveform/data outputs under `results/issue-xxxx/`.

The paths below use `issue-xxxx` as a placeholder for any processed issue result directory.

## SPI Mode

Directly affects:
- SPI clock polarity/phase behavior
- signal timing for `SCLK`
- sampling timing for `MOSI`, `MISO`, and `DATA`

Specific outputs affected:
- `results/issue-xxxx/data/spi_SCLK_data.csv`
- `results/issue-xxxx/data/spi_MOSI_data.csv`
- `results/issue-xxxx/data/spi_MISO_data.csv`
- `results/issue-xxxx/data/spi_DATA_data.csv`
- `results/issue-xxxx/data/spi_timing_data.csv` column `SCLK`
- `results/issue-xxxx/data/spi_timing_data.csv` column `MOSI`
- `results/issue-xxxx/data/spi_timing_data.csv` column `MISO`
- `results/issue-xxxx/data/spi_timing_data.csv` column `DATA`
- `results/issue-xxxx/data/spi_consolidated_signals.csv` columns `SCLK`, `MOSI`, `MISO`, `DATA`
- `results/issue-xxxx/data/spi_signal_summary.csv` rows for `MODE`, `CPOL`, `CPHA`, or role-equivalent internal signals
- `results/issue-xxxx/graphs/spi_sclk_individual.png`
- `results/issue-xxxx/graphs/spi_mosi_individual.png`
- `results/issue-xxxx/graphs/spi_miso_individual.png`
- `results/issue-xxxx/graphs/spi_data_individual.png`
- `results/issue-xxxx/graphs/spi_all_signals.png`
- `results/issue-xxxx/graphs/spi_io_ports.png`
- `results/issue-xxxx/logs/spi_timing_diagram.txt`
- `results/issue-xxxx/logs/spi_signal_analysis.txt`

And the effect is:
- mode `0/1/2/3` changes which clock edge is used for sampling and shifting
- `SCLK` idle level and edge positions change
- `MOSI`, `MISO`, and `DATA` transition times can shift even if the payload is unchanged

## Data Width

Directly affects:
- width of `DATA`, `tx_data`, `rx_data`, and related internal buses
- number of bits transferred per frame
- number of counter steps needed to complete a transfer

Specific outputs affected:
- `results/issue-xxxx/data/spi_DATA_data.csv`
- `results/issue-xxxx/data/spi_timing_data.csv` column `DATA`
- `results/issue-xxxx/data/spi_consolidated_signals.csv` column `DATA`
- `results/issue-xxxx/data/spi_signal_summary.csv` row width for `rx_data`
- `results/issue-xxxx/data/spi_signal_summary.csv` row width for `tx_data`
- `results/issue-xxxx/data/spi_signal_summary.csv` row width for `DEFAULT_DATA_VALUE`
- `results/issue-xxxx/data/spi_spi_master_tb.DATA_WIDTH_data.csv` or role-equivalent `DATA_WIDTH` CSV
- `results/issue-xxxx/data/spi_spi_master_tb.dut.DATA_WIDTH_data.csv` or role-equivalent DUT `DATA_WIDTH` CSV
- `results/issue-xxxx/data/spi_spi_*bit_counter*_data.csv`
- `results/issue-xxxx/data/spi_spi_*rx_data*_data.csv`
- `results/issue-xxxx/data/spi_spi_*tx_data*_data.csv`
- `results/issue-xxxx/graphs/spi_data_individual.png`
- `results/issue-xxxx/graphs/spi_all_signals.png`
- `results/issue-xxxx/logs/spi_signal_analysis.txt`
- `results/issue-xxxx/logs/SUMMARY.md`

And the effect is:
- `8` means `DATA` values are 8 bits wide
- `28` means `DATA` values can grow to 28 bits
- `30` means `DATA` values can grow to 30 bits
- bit counters and transfer length grow with width

## Number of Slaves

Directly affects:
- width of `SS_N`
- number of selectable slave bits in the slave-select bus

Specific outputs affected:
- `results/issue-xxxx/data/spi_SS_N_data.csv`
- `results/issue-xxxx/data/spi_timing_data.csv` column `SS_N`
- `results/issue-xxxx/data/spi_consolidated_signals.csv` column `SS_N`
- `results/issue-xxxx/data/spi_signal_summary.csv` width for `ss_n`
- `results/issue-xxxx/data/spi_spi_*ss_n*_data.csv`
- `results/issue-xxxx/graphs/spi_ss_n_individual.png`
- `results/issue-xxxx/graphs/spi_input_ports.png`
- `results/issue-xxxx/graphs/spi_io_ports.png`
- `results/issue-xxxx/graphs/spi_all_signals.png`
- `results/issue-xxxx/logs/spi_signal_analysis.txt`

And the effect is:
- `2` slaves means `SS_N` values have 2 bits
- `4` slaves means `SS_N` values have 4 bits
- `8` slaves means `SS_N` values have 8 bits

## Selected Slave Index

Directly affects:
- which `SS_N` bit becomes active during a transaction

Specific outputs affected:
- `results/issue-xxxx/data/spi_SS_N_data.csv`
- `results/issue-xxxx/data/spi_timing_data.csv` column `SS_N`
- `results/issue-xxxx/data/spi_consolidated_signals.csv` column `SS_N`
- `results/issue-xxxx/data/spi_spi_*ss_n*_data.csv`
- `results/issue-xxxx/graphs/spi_ss_n_individual.png`
- `results/issue-xxxx/graphs/spi_input_ports.png`
- `results/issue-xxxx/graphs/spi_io_ports.png`
- `results/issue-xxxx/graphs/spi_all_signals.png`
- `results/issue-xxxx/logs/spi_timing_diagram.txt`

And the effect is:
- if selected slave is `1`, one specific `SS_N` bit becomes active
- if selected slave is `2`, a different `SS_N` bit becomes active
- for a 4-bit active-low bus, one example active value is `b1101`

## Slave Select Behavior

Directly affects:
- signal meaning of `SS_N`

Specific outputs affected:
- `results/issue-xxxx/data/spi_SS_N_data.csv`
- `results/issue-xxxx/data/spi_timing_data.csv` column `SS_N`
- `results/issue-xxxx/data/spi_consolidated_signals.csv` column `SS_N`
- `results/issue-xxxx/data/spi_signal_summary.csv` row for `SLAVE_ACTIVE_LOW`
- `results/issue-xxxx/data/spi_spi_*SLAVE_ACTIVE_LOW*_data.csv`
- `results/issue-xxxx/graphs/spi_ss_n_individual.png`
- `results/issue-xxxx/graphs/spi_input_ports.png`
- `results/issue-xxxx/graphs/spi_io_ports.png`
- `results/issue-xxxx/graphs/spi_all_signals.png`

And the effect is:
- active-low: selected slave appears when one bit goes `0`
- active-high: selected slave appears when one bit goes `1`

## Data Order

Directly affects:
- bit order on `MOSI`
- bit assembly order into `DATA`
- bit movement inside shift registers

Specific outputs affected:
- `results/issue-xxxx/data/spi_MOSI_data.csv`
- `results/issue-xxxx/data/spi_DATA_data.csv`
- `results/issue-xxxx/data/spi_timing_data.csv` column `MOSI`
- `results/issue-xxxx/data/spi_timing_data.csv` column `DATA`
- `results/issue-xxxx/data/spi_consolidated_signals.csv` columns `MOSI` and `DATA`
- `results/issue-xxxx/data/spi_signal_summary.csv` row for `MSB_FIRST`
- `results/issue-xxxx/data/spi_spi_*MSB_FIRST*_data.csv`
- `results/issue-xxxx/data/spi_spi_*tx_shift_reg*_data.csv`
- `results/issue-xxxx/data/spi_spi_*rx_shift_reg*_data.csv`
- `results/issue-xxxx/graphs/spi_mosi_individual.png`
- `results/issue-xxxx/graphs/spi_data_individual.png`
- `results/issue-xxxx/graphs/spi_all_signals.png`
- `results/issue-xxxx/logs/spi_signal_analysis.txt`

And the effect is:
- MSB-first sends the highest-order bit first
- LSB-first sends the lowest-order bit first
- the same numeric payload can produce a different bit sequence on `MOSI`
- the growth pattern in `DATA` can appear reversed

## Interrupt Support

Directly affects:
- `IRQ` only when the generated role/RTL actually drives interrupt behavior

Specific outputs affected:
- `results/issue-xxxx/data/spi_IRQ_data.csv`
- `results/issue-xxxx/data/spi_timing_data.csv` column `IRQ`
- `results/issue-xxxx/data/spi_consolidated_signals.csv` column `IRQ`
- `results/issue-xxxx/data/spi_signal_summary.csv` row for `irq`
- `results/issue-xxxx/data/spi_spi_*irq*_data.csv`
- `results/issue-xxxx/graphs/spi_irq_individual.png`
- `results/issue-xxxx/graphs/spi_output_ports.png`
- `results/issue-xxxx/graphs/spi_io_ports.png`
- `results/issue-xxxx/graphs/spi_all_signals.png`
- `results/issue-xxxx/logs/spi_signal_analysis.txt`

And the effect is:
- if interrupt behavior is implemented for that generated design, `IRQ` may pulse or assert
- if not implemented, the parameter may exist but the waveform may remain static

## FIFO Buffers

Directly affects:
- `FIFO_DEPTH` parameter visibility
- FIFO-related internal behavior only if the generated RTL uses it behaviorally

Specific outputs affected:
- `results/issue-xxxx/data/spi_signal_summary.csv` row for `FIFO_DEPTH`
- `results/issue-xxxx/data/spi_spi_*FIFO_DEPTH*_data.csv`
- `results/issue-xxxx/data/spi_spi_*fifo*_data.csv` if FIFO internal signals exist for that role
- `results/issue-xxxx/logs/spi_signal_analysis.txt`
- `results/issue-xxxx/logs/SUMMARY.md`

And the effect is:
- the configured FIFO depth appears in parameter traces
- if FIFO internals are present, storage-related internal signals can change accordingly

## DMA Support

Directly affects:
- no verified direct waveform signal in the current generation flow

Specific outputs affected:
- `results/issue-xxxx/logs/SUMMARY.md`

And the effect is:
- this currently acts as configuration/report metadata rather than a proven waveform-changing input

## Multi-master Support

Directly affects:
- no verified direct waveform signal in the current generation flow

Specific outputs affected:
- `results/issue-xxxx/logs/SUMMARY.md`

And the effect is:
- this currently acts as configuration/report metadata rather than a proven waveform-changing input

## Testing Requirements

Directly affects:
- no verified direct signal in the current templates

Specific outputs affected:
- `results/issue-xxxx/logs/SUMMARY.md`
- `results/issue-xxxx/code/spi_config.json`

And the effect is:
- this is currently reflected in reporting/config metadata, not in a specific waveform signal

## Clock Jitter Testing

Directly affects:
- no verified direct signal in the current templates

Specific outputs affected:
- `results/issue-xxxx/code/spi_config.json`
- `results/issue-xxxx/logs/SUMMARY.md`

And the effect is:
- this is currently reflected in configuration/report metadata, not in a specific waveform signal

## Waveform Capture

Directly affects:
- existence of waveform analysis outputs at the workflow level

Specific outputs affected:
- `results/issue-xxxx/data/spi_waveform.vcd`
- `results/issue-xxxx/data/spi_timing_data.csv`
- `results/issue-xxxx/data/spi_signal_summary.csv`
- `results/issue-xxxx/data/spi_consolidated_signals.csv`
- all `results/issue-xxxx/data/spi_*_data.csv` files
- all `results/issue-xxxx/graphs/*.png`
- `results/issue-xxxx/logs/spi_timing_diagram.txt`
- `results/issue-xxxx/logs/spi_signal_analysis.txt`

And the effect is:
- this controls whether waveform-derived artifacts are expected as a category
- it does not directly change one specific signal shape like `SS_N` or `DATA`

## SPI Role

Directly affects:
- which core is generated
- which testbench is generated
- which signals exist and what `DATA` represents

Specific outputs affected:
- `results/issue-xxxx/code/spi_master_modeX_Ybit.v` or role-equivalent generated RTL
- `results/issue-xxxx/code/spi_master_tb.v`, `spi_slave_tb.v`, or `spi_dual_tb.v`
- `results/issue-xxxx/data/spi_DATA_data.csv`
- `results/issue-xxxx/data/spi_SCLK_data.csv`
- `results/issue-xxxx/data/spi_MOSI_data.csv`
- `results/issue-xxxx/data/spi_MISO_data.csv`
- `results/issue-xxxx/data/spi_SS_N_data.csv`
- `results/issue-xxxx/data/spi_BUSY_data.csv`
- `results/issue-xxxx/data/spi_IRQ_data.csv`
- all role-specific internal signal CSVs
- all waveform plots under `results/issue-xxxx/graphs/`
- all waveform summary logs under `results/issue-xxxx/logs/`

And the effect is:
- master role makes `DATA` represent master receive data
- slave role makes `DATA` represent slave receive data
- dual role changes both visible signals and internal master/slave mode behavior

## Default Data Storage

Directly affects:
- whether default-data logic is enabled
- whether transmitted/default path can use `default_data`

Specific outputs affected:
- `results/issue-xxxx/data/spi_MOSI_data.csv`
- `results/issue-xxxx/data/spi_signal_summary.csv` row for `DEFAULT_DATA_ENABLED`
- `results/issue-xxxx/data/spi_signal_summary.csv` row for `DEFAULT_DATA_VALUE`
- `results/issue-xxxx/data/spi_spi_*DEFAULT_DATA_ENABLED*_data.csv`
- `results/issue-xxxx/data/spi_spi_*DEFAULT_DATA_VALUE*_data.csv`
- `results/issue-xxxx/data/spi_spi_*default_data*_data.csv`
- `results/issue-xxxx/graphs/spi_mosi_individual.png`
- `results/issue-xxxx/graphs/spi_all_signals.png`
- `results/issue-xxxx/logs/spi_signal_analysis.txt`

And the effect is:
- enabled means transmit/default-data paths can use the generated default pattern
- disabled means user/testbench-provided `tx_data` is used instead

## Default Data Pattern

Directly affects:
- bit pattern loaded into `DEFAULT_DATA_VALUE` and `default_data`

Specific outputs affected:
- `results/issue-xxxx/data/spi_MOSI_data.csv`
- `results/issue-xxxx/data/spi_signal_summary.csv` row for `DEFAULT_DATA_VALUE`
- `results/issue-xxxx/data/spi_spi_*DEFAULT_DATA_VALUE*_data.csv`
- `results/issue-xxxx/data/spi_spi_*default_data*_data.csv`
- `results/issue-xxxx/graphs/spi_mosi_individual.png`
- `results/issue-xxxx/graphs/spi_all_signals.png`
- `results/issue-xxxx/logs/spi_signal_analysis.txt`

And the effect is:
- `A5A5` creates an alternating-style transmitted/default pattern
- `FFFF` creates an all-ones transmitted/default pattern
- `0000` creates an all-zeros transmitted/default pattern
- `5555` creates a `0101...` style transmitted/default pattern

## Custom Data Value (Hex)

Directly affects:
- custom bits used for `DEFAULT_DATA_VALUE` when the custom/default path is selected

Specific outputs affected:
- `results/issue-xxxx/data/spi_MOSI_data.csv`
- `results/issue-xxxx/data/spi_signal_summary.csv` row for `DEFAULT_DATA_VALUE`
- `results/issue-xxxx/data/spi_spi_*DEFAULT_DATA_VALUE*_data.csv`
- `results/issue-xxxx/data/spi_spi_*default_data*_data.csv`
- `results/issue-xxxx/graphs/spi_mosi_individual.png`
- `results/issue-xxxx/graphs/spi_all_signals.png`
- `results/issue-xxxx/logs/spi_signal_analysis.txt`

And the effect is:
- the specific custom hex value becomes the transmitted/default-data bit pattern after width scaling

## Clock Divider

Directly affects:
- timing and frequency of `SCLK`
- time spacing of `MOSI`, `MISO`, and `DATA` changes
- overall transaction duration

Specific outputs affected:
- `results/issue-xxxx/data/spi_SCLK_data.csv`
- `results/issue-xxxx/data/spi_MOSI_data.csv`
- `results/issue-xxxx/data/spi_MISO_data.csv`
- `results/issue-xxxx/data/spi_DATA_data.csv`
- `results/issue-xxxx/data/spi_timing_data.csv` columns `SCLK`, `MOSI`, `MISO`, `DATA`
- `results/issue-xxxx/data/spi_consolidated_signals.csv` columns `SCLK`, `MOSI`, `MISO`, `DATA`
- `results/issue-xxxx/data/spi_signal_summary.csv` row for `CLOCK_DIVIDER`
- `results/issue-xxxx/data/spi_spi_*CLOCK_DIVIDER*_data.csv`
- `results/issue-xxxx/data/spi_spi_*sclk_counter*_data.csv`
- `results/issue-xxxx/graphs/spi_sclk_individual.png`
- `results/issue-xxxx/graphs/spi_mosi_individual.png`
- `results/issue-xxxx/graphs/spi_miso_individual.png`
- `results/issue-xxxx/graphs/spi_data_individual.png`
- `results/issue-xxxx/graphs/spi_all_signals.png`
- `results/issue-xxxx/logs/spi_timing_diagram.txt`
- `results/issue-xxxx/logs/spi_signal_analysis.txt`

And the effect is:
- a larger divider makes `SCLK` slower
- signal transitions spread farther apart in time
- transfer duration increases

## FIFO Depth

Directly affects:
- `FIFO_DEPTH` parameter visibility
- FIFO-related internal behavior only if the generated RTL uses it behaviorally

Specific outputs affected:
- `results/issue-xxxx/data/spi_signal_summary.csv` row for `FIFO_DEPTH`
- `results/issue-xxxx/data/spi_spi_*FIFO_DEPTH*_data.csv`
- `results/issue-xxxx/data/spi_spi_*fifo*_data.csv` if FIFO internal signals exist
- `results/issue-xxxx/logs/spi_signal_analysis.txt`
- `results/issue-xxxx/logs/SUMMARY.md`

And the effect is:
- configured FIFO depth appears in parameter traces
- waveform effects depend on whether FIFO logic is active in that generated design

## Maximum Slaves

Directly affects:
- `MAX_SLAVES` parameter visibility in roles that expose it

Specific outputs affected:
- `results/issue-xxxx/data/spi_signal_summary.csv` row for `MAX_SLAVES`
- `results/issue-xxxx/data/spi_spi_*MAX_SLAVES*_data.csv`
- `results/issue-xxxx/logs/spi_signal_analysis.txt`
- `results/issue-xxxx/logs/SUMMARY.md`

And the effect is:
- configured maximum slave count appears in parameter traces
- waveform effects depend on whether the generated role uses this limit behaviorally

## Additional Notes

Directly affects:
- no direct waveform signal

Specific outputs affected:
- `results/issue-xxxx/code/spi_config.json`
- `results/issue-xxxx/logs/run_manifest.json`

And the effect is:
- this is stored as traceability/context metadata rather than a direct signal or plot driver
