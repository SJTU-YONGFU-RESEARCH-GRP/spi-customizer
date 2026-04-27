# SPI Replay Validation Report

- Cases evaluated: **109**
- Passed all gates: **94**
- Failed at least one gate: **15**
- Modern cases (post-fix replay set): **94**, pass: **94**
- Legacy cases (historical artifacts): **15**, pass: **0**

## Policy Verdict

- `release_gate_modern`: **PASS**
- `coverage_gap`: **none**
- `conformance_gate`: **PASS**
- `negative_suite_ok`: **PASS**
- `signoff_gate`: **PASS**

## Gate Definitions

- `compile_ok`: compilation log indicates success
- `sim_ok`: simulation log has return code 0 and no `FATAL:`
- `vcd_ok`: non-empty `spi_waveform.vcd` exists
- `compliance_ok`: compliance report exists, has check table, and no `FAIL`/`NOT_RUN` checks
- `summary_ok`: summary exists with key metrics
- `consistency_ok`: summary metrics match CSV/log-derived values
- `spec_oracle_ok`: compliance/log evidence satisfies issue-derived verification spec
- `rtl_tb_semantic_ok`: generated RTL/TB structure and semantic checks match spec
- `transaction_oracle_ok`: decoded busy-window SCLK sampling activity satisfies minimum frame bit-count expectation
- `selected_slave_oracle_ok`: SS_N evidence matches configured one-hot selected slave during busy (master/dual)

## Requirement Traceability

| Requirement | Title | Covered Modern Cases | Status |
|---|---|---:|:---:|
| SPI-CONF-001 | SCLK idle level shall match CPOL during idle windows. | 94 | PASS |
| SPI-CONF-002 | Slave select shall be active while busy and inactive while not busy. | 94 | PASS |
| SPI-CONF-003 | MOSI shall remain stable on sampling edges for active transactions. | 66 | PASS |
| SPI-CONF-004 | SCLK activity shall be present while transactions are active. | 66 | PASS |
| SPI-CONF-005 | MOSI setup/hold margin around sampling edges shall meet minimum timing window. | 66 | PASS |

## Negative Suite (Fault Injection)

| Case | Expected Fail Checks | Status |
|---|---:|:---:|
| negative-001-ss-framing-and-mosi-edge | 2 | PASS |

## Per-Issue Results

| Issue | Overall | compile_ok | sim_ok | vcd_ok | compliance_ok | summary_ok | consistency_ok | spec_oracle_ok | rtl_tb_semantic_ok | transaction_oracle_ok | selected_slave_oracle_ok |
|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | FAIL | Y | Y | N | N | Y | N | N | N | N | N |
| 3 | FAIL | N | N | Y | Y | Y | Y | N | N | Y | Y |
| 36 | FAIL | Y | Y | Y | N | N | N | N | N | N | N |
| 37 | FAIL | Y | Y | Y | N | N | N | N | N | N | N |
| 38 | FAIL | Y | Y | Y | N | N | N | N | N | Y | Y |
| 39 | FAIL | Y | Y | Y | N | N | N | N | N | N | N |
| 42 | FAIL | Y | Y | Y | N | N | N | N | N | Y | Y |
| 43 | FAIL | Y | Y | Y | N | N | N | N | N | Y | Y |
| 44 | FAIL | Y | Y | Y | N | N | N | N | N | Y | Y |
| 45 | FAIL | Y | Y | Y | N | N | N | N | N | Y | Y |
| 46 | FAIL | Y | Y | Y | N | N | N | N | N | N | N |
| 48 | FAIL | Y | N | Y | N | N | N | N | N | N | N |
| 49 | FAIL | Y | N | Y | N | N | N | N | N | N | Y |
| 50 | FAIL | Y | Y | Y | N | N | N | N | N | Y | Y |
| 51 | FAIL | Y | Y | Y | N | N | N | N | N | N | Y |
| 1002 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1003 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1004 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1005 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1006 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1007 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1008 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1009 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1010 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1011 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1012 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1013 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1014 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1015 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1016 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1017 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1018 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1019 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1020 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1021 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1022 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1023 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1024 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1025 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1026 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1027 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1028 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1029 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1030 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1031 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1032 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1033 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1034 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1035 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1036 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1037 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1038 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1039 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1040 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1041 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1042 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1043 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1044 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1045 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1046 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1047 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1048 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1049 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1050 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1051 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1052 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1053 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1054 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1055 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1056 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1057 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1058 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1059 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1060 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1061 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1062 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1063 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1065 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1066 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1067 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1068 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1070 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1071 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1072 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1073 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1075 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1076 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1077 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1078 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1079 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1080 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1081 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1082 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1083 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1084 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1085 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1086 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1087 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1088 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1089 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1090 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1091 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1092 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1093 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1094 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1095 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1096 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1097 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1098 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |

## Coverage Matrix (Modern Cases)

| Mode | Role | Width Class | SS Polarity | Bit Order | Cases |
|---:|---|---|---|---|---:|
| 0 | dual | 1 | active_high | lsb_first | 1 |
| 0 | dual | 1 | active_high | msb_first | 1 |
| 0 | dual | 1 | active_low | lsb_first | 1 |
| 0 | dual | 1 | active_low | msb_first | 1 |
| 0 | dual | 16 | active_high | msb_first | 1 |
| 0 | dual | other | active_low | msb_first | 2 |
| 0 | master | 1 | active_high | lsb_first | 1 |
| 0 | master | 1 | active_high | msb_first | 1 |
| 0 | master | 1 | active_low | lsb_first | 1 |
| 0 | master | 1 | active_low | msb_first | 1 |
| 0 | master | 16 | active_low | lsb_first | 1 |
| 0 | master | 2 | active_low | msb_first | 1 |
| 0 | master | 32 | active_high | msb_first | 1 |
| 0 | master | 8 | active_low | lsb_first | 1 |
| 0 | master | other | active_low | msb_first | 2 |
| 0 | slave | 1 | active_high | lsb_first | 1 |
| 0 | slave | 1 | active_high | msb_first | 1 |
| 0 | slave | 1 | active_low | lsb_first | 1 |
| 0 | slave | 1 | active_low | msb_first | 1 |
| 0 | slave | 24 | active_high | lsb_first | 1 |
| 0 | slave | 24 | active_low | msb_first | 1 |
| 0 | slave | other | active_low | msb_first | 2 |
| 1 | dual | 1 | active_high | lsb_first | 1 |
| 1 | dual | 1 | active_high | msb_first | 1 |
| 1 | dual | 1 | active_low | lsb_first | 1 |
| 1 | dual | 1 | active_low | msb_first | 1 |
| 1 | dual | 16 | active_low | lsb_first | 1 |
| 1 | dual | 24 | active_high | lsb_first | 2 |
| 1 | dual | 32 | active_high | msb_first | 1 |
| 1 | dual | 9 | active_high | lsb_first | 1 |
| 1 | dual | other | active_high | lsb_first | 2 |
| 1 | master | 1 | active_high | lsb_first | 1 |
| 1 | master | 1 | active_high | msb_first | 1 |
| 1 | master | 1 | active_low | lsb_first | 1 |
| 1 | master | 1 | active_low | msb_first | 1 |
| 1 | master | 24 | active_low | lsb_first | 2 |
| 1 | master | other | active_high | lsb_first | 1 |
| 1 | slave | 1 | active_high | lsb_first | 1 |
| 1 | slave | 1 | active_high | msb_first | 1 |
| 1 | slave | 1 | active_low | lsb_first | 1 |
| 1 | slave | 1 | active_low | msb_first | 1 |
| 1 | slave | 24 | active_low | msb_first | 1 |
| 1 | slave | 3 | active_low | lsb_first | 1 |
| 1 | slave | 32 | active_high | msb_first | 1 |
| 1 | slave | other | active_high | lsb_first | 2 |
| 2 | dual | 1 | active_high | lsb_first | 1 |
| 2 | dual | 1 | active_high | msb_first | 1 |
| 2 | dual | 1 | active_low | lsb_first | 1 |
| 2 | dual | 1 | active_low | msb_first | 1 |
| 2 | dual | 16 | active_high | msb_first | 1 |
| 2 | dual | 16 | active_low | msb_first | 1 |
| 2 | dual | 24 | active_high | lsb_first | 1 |
| 2 | dual | 32 | active_low | msb_first | 4 |
| 2 | dual | other | active_low | msb_first | 2 |
| 2 | master | 1 | active_high | lsb_first | 1 |
| 2 | master | 1 | active_high | msb_first | 1 |
| 2 | master | 1 | active_low | lsb_first | 1 |
| 2 | master | 1 | active_low | msb_first | 1 |
| 2 | master | 24 | active_high | msb_first | 1 |
| 2 | master | 32 | active_low | lsb_first | 1 |
| 2 | master | other | active_low | msb_first | 2 |
| 2 | slave | 1 | active_high | lsb_first | 1 |
| 2 | slave | 1 | active_high | msb_first | 1 |
| 2 | slave | 1 | active_low | lsb_first | 1 |
| 2 | slave | 1 | active_low | msb_first | 1 |
| 2 | slave | 15 | active_high | msb_first | 1 |
| 2 | slave | 16 | active_high | lsb_first | 1 |
| 2 | slave | other | active_low | msb_first | 1 |
| 3 | dual | 1 | active_high | lsb_first | 1 |
| 3 | dual | 1 | active_high | msb_first | 1 |
| 3 | dual | 16 | active_high | lsb_first | 1 |
| 3 | dual | other | active_high | lsb_first | 1 |
| 3 | master | 24 | active_high | msb_first | 1 |
| 3 | master | 31 | active_low | lsb_first | 1 |
| 3 | master | 32 | active_low | msb_first | 1 |
| 3 | master | 7 | active_low | lsb_first | 1 |
| 3 | master | other | active_high | lsb_first | 2 |
| 3 | slave | 32 | active_low | msb_first | 1 |
| 3 | slave | 8 | active_low | msb_first | 1 |
| 3 | slave | other | active_high | lsb_first | 2 |

## Corner Coverage Closure

- Required width corners: `1, 2, 3, 7, 8, 9, 15, 16, 24, 31, 32`
- Covered width corners: `1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32`
- Missing width corners: `none`

| Corner Signature | Cases | Pass | Fail |
|---|---:|---:|---:|
| mode=0|role=dual|width=16|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=17|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=30|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=master|width=16|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=master|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=master|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=0|role=master|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=master|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=master|width=21|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=master|width=2|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=master|width=32|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=0|role=master|width=4|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=master|width=8|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=11|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=24|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=24|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=26|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=12|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=16|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=24|ss=active_high|order=lsb_first | 2 | 2 | 0 |
| mode=1|role=dual|width=27|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=32|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=9|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=master|width=18|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=master|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=master|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=1|role=master|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=master|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=1|role=master|width=24|ss=active_low|order=lsb_first | 2 | 2 | 0 |
| mode=1|role=slave|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=slave|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=1|role=slave|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=slave|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=1|role=slave|width=22|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=slave|width=24|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=1|role=slave|width=32|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=1|role=slave|width=3|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=slave|width=5|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=dual|width=16|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=2|role=dual|width=16|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=dual|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=dual|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=2|role=dual|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=dual|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=dual|width=23|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=dual|width=24|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=dual|width=32|ss=active_low|order=msb_first | 4 | 4 | 0 |
| mode=2|role=dual|width=6|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=13|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=master|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=master|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=24|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=28|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=32|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=15|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=16|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=19|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=3|role=dual|width=16|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=dual|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=dual|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=3|role=dual|width=20|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=master|width=10|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=master|width=24|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=3|role=master|width=25|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=master|width=31|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=master|width=32|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=3|role=master|width=7|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=slave|width=14|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=slave|width=29|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=slave|width=32|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=3|role=slave|width=8|ss=active_low|order=msb_first | 1 | 1 | 0 |

## Template Input Coverage (Modern Cases)

| Dimension | Covered Values | Required Values |
|---|---|---|
| bit_order | lsb_first, msb_first | lsb_first, msb_first |
| clock_jitter_test | False, True | False, True |
| data_width | 1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 4, 5, 6, 7, 8, 9 | 1, 15, 16, 2, 24, 3, 31, 32, 7, 8, 9 |
| default_data_enabled | False, True | False, True |
| default_data_pattern | 0000, 5555, a5a5, custom, ffff | 0000, 5555, a5a5, custom, ffff |
| dma_support | False, True | False, True |
| fifo_buffers | False, True | False, True |
| interrupts | False, True | False, True |
| mode | 0, 1, 2, 3 | 0, 1, 2, 3 |
| multi_master | False, True | False, True |
| role | dual, master, slave | dual, master, slave |
| selected_slave_bucket | nonzero, zero | nonzero, zero |
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
- issue-1012: PASS
- issue-1013: PASS
- issue-1014: PASS
- issue-1015: PASS
- issue-1016: PASS
- issue-1017: PASS
- issue-1018: PASS
- issue-1019: PASS
- issue-1020: PASS
- issue-1021: PASS
- issue-1022: PASS
- issue-1023: PASS
- issue-1024: PASS
- issue-1025: PASS
- issue-1026: PASS
- issue-1027: PASS
- issue-1028: PASS
- issue-1029: PASS
- issue-1030: PASS
- issue-1031: PASS
- issue-1032: PASS
- issue-1033: PASS
- issue-1034: PASS
- issue-1035: PASS
- issue-1036: PASS
- issue-1037: PASS
- issue-1038: PASS
- issue-1039: PASS
- issue-1040: PASS
- issue-1041: PASS
- issue-1042: PASS
- issue-1043: PASS
- issue-1044: PASS
- issue-1045: PASS
- issue-1046: PASS
- issue-1047: PASS
- issue-1048: PASS
- issue-1049: PASS
- issue-1050: PASS
- issue-1051: PASS
- issue-1052: PASS
- issue-1053: PASS
- issue-1054: PASS
- issue-1055: PASS
- issue-1056: PASS
- issue-1057: PASS
- issue-1058: PASS
- issue-1059: PASS
- issue-1060: PASS
- issue-1061: PASS
- issue-1062: PASS
- issue-1063: PASS
- issue-1065: PASS
- issue-1066: PASS
- issue-1067: PASS
- issue-1068: PASS
- issue-1070: PASS
- issue-1071: PASS
- issue-1072: PASS
- issue-1073: PASS
- issue-1075: PASS
- issue-1076: PASS
- issue-1077: PASS
- issue-1078: PASS
- issue-1079: PASS
- issue-1080: PASS
- issue-1081: PASS
- issue-1082: PASS
- issue-1083: PASS
- issue-1084: PASS
- issue-1085: PASS
- issue-1086: PASS
- issue-1087: PASS
- issue-1088: PASS
- issue-1089: PASS
- issue-1090: PASS
- issue-1091: PASS
- issue-1092: PASS
- issue-1093: PASS
- issue-1094: PASS
- issue-1095: PASS
- issue-1096: PASS
- issue-1097: PASS
- issue-1098: PASS

### Legacy Failures (Historical Artifacts)

- Count: 15
- Primary pattern: missing compliance/summary-consistency artifacts from older runs.

## Failure Signatures

| Gate | Corner Signature | Count | Issues |
|---|---|---:|---|
| (none) | (none) | 0 | (none) |
