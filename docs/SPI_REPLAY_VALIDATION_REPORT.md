# SPI Replay Validation Report

- Cases evaluated: **120**
- Passed all gates: **120**
- Failed at least one gate: **0**
- Modern cases (post-fix replay set): **120**, pass: **120**
- Compact modern suite: **120** selected from **120** available (target=0)
- Practical compact size for full scoped closure: **45** (computed from actual coverage closure)

## Policy Verdict

- `release_gate_modern`: **PASS**
- `coverage_gap`: **none**
- `conformance_gate`: **PASS**
- `negative_suite_ok`: **PASS**
- `signoff_gate`: **PASS**

## Runtime Telemetry

- Cases with telemetry: **120 / 120**
- Duration seconds: min **3.308**, max **4.756**, mean **3.650**
- Percentiles: p50 **3.638**, p90 **3.878**

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
| SPI-CONF-001 | SCLK idle level shall match CPOL during idle windows. | 120 | PASS |
| SPI-CONF-002 | Slave select shall be active while busy and inactive while not busy. | 120 | PASS |
| SPI-CONF-003 | MOSI shall remain stable on sampling edges for active transactions. | 85 | PASS |
| SPI-CONF-004 | SCLK activity shall be present while transactions are active. | 85 | PASS |
| SPI-CONF-005 | MOSI setup/hold margin around sampling edges shall meet minimum timing window. | 85 | PASS |

## Negative Suite (Fault Injection)

| Case | Expected Fail Checks | Status |
|---|---:|:---:|
| negative-001-ss-framing-and-mosi-edge | 2 | PASS |

## Per-Issue Results

| Issue | Overall | compile_ok | sim_ok | vcd_ok | compliance_ok | summary_ok | consistency_ok | spec_oracle_ok | rtl_tb_semantic_ok | transaction_oracle_ok | selected_slave_oracle_ok |
|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
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
| 1099 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1100 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1101 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1102 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1103 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1104 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1105 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1106 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1107 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1108 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1109 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1110 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1111 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1112 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1113 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1114 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1115 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1116 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1117 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1118 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1119 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1120 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1121 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1122 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1123 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 1124 | PASS | Y | Y | Y | Y | Y | Y | Y | Y | Y | Y |

## Per-Issue Runtime

| Issue | Start (UTC) | End (UTC) | Duration (s) |
|---:|---|---|---:|
| 1002 | 2026-04-30T15:35:48.375809+00:00 | 2026-04-30T15:35:52.211776+00:00 | 3.836 |
| 1003 | 2026-04-30T15:35:52.479774+00:00 | 2026-04-30T15:35:56.247743+00:00 | 3.768 |
| 1004 | 2026-04-30T15:35:56.495740+00:00 | 2026-04-30T15:36:00.231709+00:00 | 3.736 |
| 1005 | 2026-04-30T13:59:48.215389+00:00 | 2026-04-30T13:59:52.035358+00:00 | 3.820 |
| 1006 | 2026-04-30T13:59:52.295356+00:00 | 2026-04-30T13:59:55.771321+00:00 | 3.476 |
| 1007 | 2026-04-30T13:59:56.011319+00:00 | 2026-04-30T14:00:00.087286+00:00 | 4.076 |
| 1008 | 2026-04-30T14:00:00.347284+00:00 | 2026-04-30T14:00:03.827256+00:00 | 3.480 |
| 1009 | 2026-04-30T15:36:00.487707+00:00 | 2026-04-30T15:36:04.175655+00:00 | 3.688 |
| 1010 | 2026-04-30T15:36:04.435653+00:00 | 2026-04-30T15:36:08.127622+00:00 | 3.692 |
| 1011 | 2026-04-30T14:00:12.039189+00:00 | 2026-04-30T14:00:15.551160+00:00 | 3.512 |
| 1012 | 2026-04-30T14:00:15.803158+00:00 | 2026-04-30T14:00:19.455128+00:00 | 3.652 |
| 1013 | 2026-04-30T14:00:19.711126+00:00 | 2026-04-30T14:00:23.415097+00:00 | 3.704 |
| 1014 | 2026-04-30T14:00:23.679095+00:00 | 2026-04-30T14:00:27.431065+00:00 | 3.752 |
| 1015 | 2026-04-30T14:00:27.687063+00:00 | 2026-04-30T14:00:31.431033+00:00 | 3.744 |
| 1016 | 2026-04-30T15:36:08.387619+00:00 | 2026-04-30T15:36:12.083591+00:00 | 3.696 |
| 1017 | 2026-04-30T14:00:43.598922+00:00 | 2026-04-30T14:00:47.054894+00:00 | 3.456 |
| 1018 | 2026-04-30T14:00:47.298892+00:00 | 2026-04-30T14:00:51.014862+00:00 | 3.716 |
| 1019 | 2026-04-30T14:00:51.270860+00:00 | 2026-04-30T14:00:54.706832+00:00 | 3.436 |
| 1020 | 2026-04-30T15:36:12.335589+00:00 | 2026-04-30T15:36:15.915562+00:00 | 3.580 |
| 1021 | 2026-04-30T14:00:58.722800+00:00 | 2026-04-30T14:01:02.286771+00:00 | 3.564 |
| 1022 | 2026-04-30T14:01:02.538769+00:00 | 2026-04-30T14:01:06.474738+00:00 | 3.936 |
| 1023 | 2026-04-30T15:36:16.155560+00:00 | 2026-04-30T15:36:19.895531+00:00 | 3.740 |
| 1024 | 2026-04-30T15:36:20.163528+00:00 | 2026-04-30T15:36:23.807499+00:00 | 3.644 |
| 1025 | 2026-04-30T15:36:24.083497+00:00 | 2026-04-30T15:36:27.795466+00:00 | 3.712 |
| 1026 | 2026-04-30T15:36:28.055464+00:00 | 2026-04-30T15:36:31.611435+00:00 | 3.556 |
| 1027 | 2026-04-30T14:01:22.542608+00:00 | 2026-04-30T14:01:26.526577+00:00 | 3.984 |
| 1028 | 2026-04-30T14:01:26.790575+00:00 | 2026-04-30T14:01:30.326546+00:00 | 3.536 |
| 1029 | 2026-04-30T15:36:31.851433+00:00 | 2026-04-30T15:36:35.539406+00:00 | 3.688 |
| 1030 | 2026-04-30T14:01:34.526512+00:00 | 2026-04-30T14:01:38.122483+00:00 | 3.596 |
| 1031 | 2026-04-30T14:01:38.386481+00:00 | 2026-04-30T14:01:42.190450+00:00 | 3.804 |
| 1032 | 2026-04-30T14:01:52.430368+00:00 | 2026-04-30T14:01:56.198329+00:00 | 3.768 |
| 1033 | 2026-04-30T15:36:35.819405+00:00 | 2026-04-30T15:36:39.259382+00:00 | 3.440 |
| 1034 | 2026-04-30T14:02:00.282296+00:00 | 2026-04-30T14:02:03.906267+00:00 | 3.624 |
| 1035 | 2026-04-30T14:02:04.154265+00:00 | 2026-04-30T14:02:08.106233+00:00 | 3.952 |
| 1036 | 2026-04-30T14:02:08.366230+00:00 | 2026-04-30T14:02:11.778203+00:00 | 3.412 |
| 1037 | 2026-04-30T14:02:12.042201+00:00 | 2026-04-30T14:02:15.790170+00:00 | 3.748 |
| 1038 | 2026-04-30T15:36:39.495380+00:00 | 2026-04-30T15:36:43.091353+00:00 | 3.596 |
| 1039 | 2026-04-30T14:02:19.950136+00:00 | 2026-04-30T14:02:23.446108+00:00 | 3.496 |
| 1040 | 2026-04-30T14:02:23.690106+00:00 | 2026-04-30T14:02:27.022079+00:00 | 3.332 |
| 1041 | 2026-04-30T15:36:43.331351+00:00 | 2026-04-30T15:36:46.663324+00:00 | 3.332 |
| 1042 | 2026-04-30T14:02:30.854049+00:00 | 2026-04-30T14:02:34.578016+00:00 | 3.724 |
| 1043 | 2026-04-30T14:02:34.842014+00:00 | 2026-04-30T14:02:38.325983+00:00 | 3.484 |
| 1044 | 2026-04-30T15:36:46.903322+00:00 | 2026-04-30T15:36:50.459290+00:00 | 3.556 |
| 1045 | 2026-04-30T14:02:42.481950+00:00 | 2026-04-30T14:02:46.225920+00:00 | 3.744 |
| 1046 | 2026-04-30T14:02:46.489918+00:00 | 2026-04-30T14:02:49.981888+00:00 | 3.492 |
| 1047 | 2026-04-30T15:36:50.715287+00:00 | 2026-04-30T15:36:54.171254+00:00 | 3.456 |
| 1048 | 2026-04-30T14:03:03.749773+00:00 | 2026-04-30T14:03:07.737741+00:00 | 3.988 |
| 1049 | 2026-04-30T14:03:08.009739+00:00 | 2026-04-30T14:03:11.733709+00:00 | 3.724 |
| 1050 | 2026-04-30T15:36:54.419252+00:00 | 2026-04-30T15:36:57.871223+00:00 | 3.452 |
| 1051 | 2026-04-30T14:03:15.693675+00:00 | 2026-04-30T14:03:19.277644+00:00 | 3.584 |
| 1052 | 2026-04-30T14:03:19.549642+00:00 | 2026-04-30T14:03:23.337611+00:00 | 3.788 |
| 1053 | 2026-04-30T15:36:58.111221+00:00 | 2026-04-30T15:37:01.651191+00:00 | 3.540 |
| 1054 | 2026-04-30T14:03:27.353579+00:00 | 2026-04-30T14:03:31.133549+00:00 | 3.780 |
| 1055 | 2026-04-30T14:03:31.393547+00:00 | 2026-04-30T14:03:34.853519+00:00 | 3.460 |
| 1056 | 2026-04-30T15:37:01.923188+00:00 | 2026-04-30T15:37:05.575157+00:00 | 3.652 |
| 1057 | 2026-04-30T14:03:39.041485+00:00 | 2026-04-30T14:03:42.917454+00:00 | 3.876 |
| 1058 | 2026-04-30T14:03:43.173452+00:00 | 2026-04-30T14:03:46.673424+00:00 | 3.500 |
| 1059 | 2026-04-30T15:37:05.835155+00:00 | 2026-04-30T15:37:09.499124+00:00 | 3.664 |
| 1060 | 2026-04-30T15:37:09.759121+00:00 | 2026-04-30T15:37:13.435090+00:00 | 3.676 |
| 1061 | 2026-04-30T15:37:13.695088+00:00 | 2026-04-30T15:37:17.307058+00:00 | 3.612 |
| 1062 | 2026-04-30T15:37:17.583055+00:00 | 2026-04-30T15:37:21.235020+00:00 | 3.652 |
| 1063 | 2026-04-30T15:37:21.499018+00:00 | 2026-04-30T15:37:25.070981+00:00 | 3.572 |
| 1065 | 2026-04-30T14:04:06.465260+00:00 | 2026-04-30T14:04:10.061230+00:00 | 3.596 |
| 1066 | 2026-04-30T14:04:10.321227+00:00 | 2026-04-30T14:04:13.921195+00:00 | 3.600 |
| 1067 | 2026-04-30T14:04:14.193192+00:00 | 2026-04-30T14:04:17.629165+00:00 | 3.436 |
| 1068 | 2026-04-30T14:04:17.885163+00:00 | 2026-04-30T14:04:21.253136+00:00 | 3.368 |
| 1070 | 2026-04-30T15:37:25.334978+00:00 | 2026-04-30T15:37:28.930941+00:00 | 3.596 |
| 1071 | 2026-04-30T15:37:29.186939+00:00 | 2026-04-30T15:37:32.878903+00:00 | 3.692 |
| 1072 | 2026-04-30T15:37:33.154900+00:00 | 2026-04-30T15:37:36.798865+00:00 | 3.644 |
| 1073 | 2026-04-30T15:37:37.070862+00:00 | 2026-04-30T15:37:40.798828+00:00 | 3.728 |
| 1075 | 2026-04-30T14:04:37.297003+00:00 | 2026-04-30T14:04:40.884973+00:00 | 3.588 |
| 1076 | 2026-04-30T14:04:41.140971+00:00 | 2026-04-30T14:04:44.660943+00:00 | 3.520 |
| 1077 | 2026-04-30T14:04:44.920941+00:00 | 2026-04-30T14:04:48.504912+00:00 | 3.584 |
| 1078 | 2026-04-30T14:04:48.804909+00:00 | 2026-04-30T14:04:52.252882+00:00 | 3.448 |
| 1079 | 2026-04-30T14:04:52.516880+00:00 | 2026-04-30T14:04:56.240849+00:00 | 3.724 |
| 1080 | 2026-04-30T14:04:56.504847+00:00 | 2026-04-30T14:04:59.876820+00:00 | 3.372 |
| 1081 | 2026-04-30T14:05:00.140818+00:00 | 2026-04-30T14:05:03.832788+00:00 | 3.692 |
| 1082 | 2026-04-30T14:05:04.084786+00:00 | 2026-04-30T14:05:07.496758+00:00 | 3.412 |
| 1083 | 2026-04-30T14:05:07.752756+00:00 | 2026-04-30T14:05:11.140727+00:00 | 3.388 |
| 1084 | 2026-04-30T14:05:11.380725+00:00 | 2026-04-30T14:05:14.764696+00:00 | 3.384 |
| 1085 | 2026-04-30T15:37:41.066825+00:00 | 2026-04-30T15:37:44.790790+00:00 | 3.724 |
| 1086 | 2026-04-30T15:37:45.058789+00:00 | 2026-04-30T15:37:48.654780+00:00 | 3.596 |
| 1087 | 2026-04-30T15:37:48.926777+00:00 | 2026-04-30T15:37:52.594740+00:00 | 3.668 |
| 1088 | 2026-04-30T15:37:52.866738+00:00 | 2026-04-30T15:37:56.466721+00:00 | 3.600 |
| 1089 | 2026-04-30T14:05:30.808563+00:00 | 2026-04-30T14:05:34.376534+00:00 | 3.568 |
| 1090 | 2026-04-30T14:05:34.648532+00:00 | 2026-04-30T14:05:38.296503+00:00 | 3.648 |
| 1091 | 2026-04-30T14:05:38.556501+00:00 | 2026-04-30T14:05:42.160471+00:00 | 3.604 |
| 1092 | 2026-04-30T14:05:42.432469+00:00 | 2026-04-30T14:05:46.064440+00:00 | 3.632 |
| 1093 | 2026-04-30T14:05:46.316438+00:00 | 2026-04-30T14:05:49.672411+00:00 | 3.356 |
| 1094 | 2026-04-30T14:05:49.916409+00:00 | 2026-04-30T14:05:53.236382+00:00 | 3.320 |
| 1095 | 2026-04-30T14:05:53.484380+00:00 | 2026-04-30T14:05:56.800351+00:00 | 3.316 |
| 1096 | 2026-04-30T14:05:57.040349+00:00 | 2026-04-30T14:06:00.348322+00:00 | 3.308 |
| 1097 | 2026-04-30T15:37:56.742718+00:00 | 2026-04-30T15:38:00.410684+00:00 | 3.668 |
| 1098 | 2026-04-30T15:38:00.686681+00:00 | 2026-04-30T15:38:04.318659+00:00 | 3.632 |
| 1099 | 2026-04-30T15:38:04.582657+00:00 | 2026-04-30T15:38:08.194626+00:00 | 3.612 |
| 1100 | 2026-04-30T14:35:37.757688+00:00 | 2026-04-30T14:35:41.497658+00:00 | 3.740 |
| 1101 | 2026-04-30T15:24:14.377673+00:00 | 2026-04-30T15:24:18.601625+00:00 | 4.224 |
| 1102 | 2026-04-30T15:38:08.458624+00:00 | 2026-04-30T15:38:12.182593+00:00 | 3.724 |
| 1103 | 2026-04-30T15:24:23.009589+00:00 | 2026-04-30T15:24:26.509560+00:00 | 3.500 |
| 1104 | 2026-04-30T15:24:26.761558+00:00 | 2026-04-30T15:24:30.473527+00:00 | 3.712 |
| 1105 | 2026-04-30T15:38:12.454591+00:00 | 2026-04-30T15:38:15.994562+00:00 | 3.540 |
| 1106 | 2026-04-30T15:24:30.913523+00:00 | 2026-04-30T15:24:35.669484+00:00 | 4.756 |
| 1107 | 2026-04-30T15:24:35.937482+00:00 | 2026-04-30T15:24:40.041448+00:00 | 4.104 |
| 1108 | 2026-04-30T15:38:16.298559+00:00 | 2026-04-30T15:38:20.082528+00:00 | 3.784 |
| 1109 | 2026-04-30T15:24:44.349407+00:00 | 2026-04-30T15:24:48.153375+00:00 | 3.804 |
| 1110 | 2026-04-30T15:24:48.445372+00:00 | 2026-04-30T15:24:52.441339+00:00 | 3.996 |
| 1111 | 2026-04-30T15:38:20.346525+00:00 | 2026-04-30T15:38:23.750497+00:00 | 3.404 |
| 1112 | 2026-04-30T15:24:56.473305+00:00 | 2026-04-30T15:25:00.365273+00:00 | 3.892 |
| 1113 | 2026-04-30T15:54:28.154364+00:00 | 2026-04-30T15:54:32.262330+00:00 | 4.108 |
| 1114 | 2026-04-30T15:54:32.554327+00:00 | 2026-04-30T15:54:36.378295+00:00 | 3.824 |
| 1115 | 2026-04-30T15:54:36.646293+00:00 | 2026-04-30T15:54:40.222263+00:00 | 3.576 |
| 1116 | 2026-04-30T15:54:40.490261+00:00 | 2026-04-30T15:54:44.062231+00:00 | 3.572 |
| 1117 | 2026-04-30T15:54:44.330229+00:00 | 2026-04-30T15:54:48.102197+00:00 | 3.772 |
| 1118 | 2026-04-30T15:54:48.370195+00:00 | 2026-04-30T15:54:51.902165+00:00 | 3.532 |
| 1119 | 2026-04-30T15:54:52.150163+00:00 | 2026-04-30T15:54:55.678133+00:00 | 3.528 |
| 1120 | 2026-04-30T15:54:55.934131+00:00 | 2026-04-30T15:54:59.686100+00:00 | 3.752 |
| 1121 | 2026-04-30T15:54:59.954097+00:00 | 2026-04-30T15:55:03.646065+00:00 | 3.692 |
| 1122 | 2026-04-30T15:55:03.914063+00:00 | 2026-04-30T15:55:07.698031+00:00 | 3.784 |
| 1123 | 2026-04-30T15:55:07.970029+00:00 | 2026-04-30T15:55:11.386000+00:00 | 3.416 |
| 1124 | 2026-04-30T15:55:11.625998+00:00 | 2026-04-30T15:55:15.601965+00:00 | 3.976 |

## Coverage Matrix (Modern Cases)

| Mode | Role | Width Class | SS Polarity | Bit Order | Cases |
|---:|---|---|---|---|---:|
| 0 | dual | 1 | active_high | lsb_first | 1 |
| 0 | dual | 1 | active_high | msb_first | 1 |
| 0 | dual | 1 | active_low | lsb_first | 1 |
| 0 | dual | 1 | active_low | msb_first | 1 |
| 0 | dual | 16 | active_high | msb_first | 1 |
| 0 | dual | other | active_low | lsb_first | 1 |
| 0 | dual | other | active_low | msb_first | 2 |
| 0 | master | 1 | active_high | lsb_first | 1 |
| 0 | master | 1 | active_high | msb_first | 1 |
| 0 | master | 1 | active_low | lsb_first | 1 |
| 0 | master | 1 | active_low | msb_first | 1 |
| 0 | master | 16 | active_low | lsb_first | 1 |
| 0 | master | 2 | active_low | msb_first | 1 |
| 0 | master | 32 | active_high | msb_first | 1 |
| 0 | master | 8 | active_low | lsb_first | 1 |
| 0 | master | 8 | active_low | msb_first | 1 |
| 0 | master | other | active_high | msb_first | 1 |
| 0 | master | other | active_low | msb_first | 2 |
| 0 | slave | 1 | active_high | lsb_first | 1 |
| 0 | slave | 1 | active_high | msb_first | 1 |
| 0 | slave | 1 | active_low | lsb_first | 1 |
| 0 | slave | 1 | active_low | msb_first | 1 |
| 0 | slave | 24 | active_high | lsb_first | 1 |
| 0 | slave | 24 | active_low | msb_first | 1 |
| 0 | slave | other | active_low | lsb_first | 1 |
| 0 | slave | other | active_low | msb_first | 2 |
| 1 | dual | 1 | active_high | lsb_first | 1 |
| 1 | dual | 1 | active_high | msb_first | 1 |
| 1 | dual | 1 | active_low | lsb_first | 1 |
| 1 | dual | 1 | active_low | msb_first | 1 |
| 1 | dual | 16 | active_high | msb_first | 1 |
| 1 | dual | 16 | active_low | lsb_first | 1 |
| 1 | dual | 24 | active_high | lsb_first | 2 |
| 1 | dual | 32 | active_high | msb_first | 1 |
| 1 | dual | 9 | active_high | lsb_first | 1 |
| 1 | dual | other | active_high | lsb_first | 2 |
| 1 | dual | other | active_low | msb_first | 2 |
| 1 | master | 1 | active_high | lsb_first | 1 |
| 1 | master | 1 | active_high | msb_first | 1 |
| 1 | master | 1 | active_low | lsb_first | 1 |
| 1 | master | 1 | active_low | msb_first | 1 |
| 1 | master | 24 | active_high | lsb_first | 1 |
| 1 | master | 24 | active_low | lsb_first | 2 |
| 1 | master | other | active_high | lsb_first | 1 |
| 1 | slave | 1 | active_high | lsb_first | 1 |
| 1 | slave | 1 | active_high | msb_first | 1 |
| 1 | slave | 1 | active_low | lsb_first | 1 |
| 1 | slave | 1 | active_low | msb_first | 1 |
| 1 | slave | 16 | active_low | lsb_first | 1 |
| 1 | slave | 24 | active_low | msb_first | 1 |
| 1 | slave | 3 | active_low | lsb_first | 1 |
| 1 | slave | 32 | active_high | msb_first | 1 |
| 1 | slave | other | active_high | lsb_first | 2 |
| 1 | slave | other | active_high | msb_first | 1 |
| 2 | dual | 1 | active_high | lsb_first | 1 |
| 2 | dual | 1 | active_high | msb_first | 1 |
| 2 | dual | 1 | active_low | lsb_first | 1 |
| 2 | dual | 1 | active_low | msb_first | 1 |
| 2 | dual | 16 | active_high | msb_first | 1 |
| 2 | dual | 16 | active_low | msb_first | 1 |
| 2 | dual | 24 | active_high | lsb_first | 1 |
| 2 | dual | 32 | active_high | msb_first | 1 |
| 2 | dual | 32 | active_low | msb_first | 4 |
| 2 | dual | other | active_low | msb_first | 2 |
| 2 | master | 1 | active_high | lsb_first | 1 |
| 2 | master | 1 | active_high | msb_first | 1 |
| 2 | master | 1 | active_low | lsb_first | 1 |
| 2 | master | 1 | active_low | msb_first | 1 |
| 2 | master | 16 | active_high | msb_first | 1 |
| 2 | master | 24 | active_high | msb_first | 1 |
| 2 | master | 32 | active_high | lsb_first | 1 |
| 2 | master | 32 | active_low | lsb_first | 1 |
| 2 | master | other | active_low | lsb_first | 1 |
| 2 | master | other | active_low | msb_first | 2 |
| 2 | slave | 1 | active_high | lsb_first | 1 |
| 2 | slave | 1 | active_high | msb_first | 1 |
| 2 | slave | 1 | active_low | lsb_first | 1 |
| 2 | slave | 1 | active_low | msb_first | 1 |
| 2 | slave | 15 | active_high | msb_first | 1 |
| 2 | slave | 16 | active_high | lsb_first | 1 |
| 2 | slave | other | active_high | lsb_first | 1 |
| 2 | slave | other | active_low | msb_first | 1 |
| 3 | dual | 1 | active_high | lsb_first | 1 |
| 3 | dual | 1 | active_high | msb_first | 1 |
| 3 | dual | 1 | active_low | lsb_first | 1 |
| 3 | dual | 16 | active_high | lsb_first | 3 |
| 3 | dual | 24 | active_low | lsb_first | 1 |
| 3 | dual | other | active_high | lsb_first | 1 |
| 3 | dual | other | active_low | msb_first | 1 |
| 3 | master | 24 | active_high | msb_first | 1 |
| 3 | master | 31 | active_low | lsb_first | 1 |
| 3 | master | 32 | active_high | lsb_first | 1 |
| 3 | master | 32 | active_low | msb_first | 1 |
| 3 | master | 7 | active_low | lsb_first | 1 |
| 3 | master | 8 | active_low | msb_first | 1 |
| 3 | master | other | active_high | lsb_first | 2 |
| 3 | master | other | active_low | lsb_first | 1 |
| 3 | slave | 24 | active_low | lsb_first | 1 |
| 3 | slave | 24 | active_low | msb_first | 1 |
| 3 | slave | 32 | active_high | lsb_first | 1 |
| 3 | slave | 32 | active_low | msb_first | 1 |
| 3 | slave | 8 | active_low | msb_first | 1 |
| 3 | slave | other | active_high | lsb_first | 2 |

## Corner Coverage Closure

- Required width corners: `1, 2, 3, 7, 8, 9, 15, 16, 24, 31, 32`
- Covered width corners: `1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32`
- Missing width corners: `none`

| Corner Signature | Cases | Pass | Fail |
|---|---:|---:|---:|
| mode=0|role=dual|width=14|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=16|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=17|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=dual|width=30|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=master|width=12|ss=active_high|order=msb_first | 1 | 1 | 0 |
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
| mode=0|role=master|width=8|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=11|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=22|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=24|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=24|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=0|role=slave|width=26|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=12|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=12|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=16|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=16|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=20|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=24|ss=active_high|order=lsb_first | 2 | 2 | 0 |
| mode=1|role=dual|width=27|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=32|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=1|role=dual|width=9|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=master|width=18|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=master|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=master|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=1|role=master|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=master|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=1|role=master|width=24|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=1|role=master|width=24|ss=active_low|order=lsb_first | 2 | 2 | 0 |
| mode=1|role=slave|width=10|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=1|role=slave|width=16|ss=active_low|order=lsb_first | 1 | 1 | 0 |
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
| mode=2|role=dual|width=32|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=2|role=dual|width=32|ss=active_low|order=msb_first | 4 | 4 | 0 |
| mode=2|role=dual|width=6|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=13|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=16|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=18|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=master|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=master|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=master|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=24|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=28|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=master|width=32|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=master|width=32|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=15|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=16|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=19|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=1|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=2|role=slave|width=28|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=dual|width=16|ss=active_high|order=lsb_first | 3 | 3 | 0 |
| mode=3|role=dual|width=1|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=dual|width=1|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=3|role=dual|width=1|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=dual|width=20|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=dual|width=24|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=dual|width=6|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=3|role=master|width=10|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=master|width=12|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=master|width=24|ss=active_high|order=msb_first | 1 | 1 | 0 |
| mode=3|role=master|width=25|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=master|width=31|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=master|width=32|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=master|width=32|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=3|role=master|width=7|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=master|width=8|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=3|role=slave|width=14|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=slave|width=24|ss=active_low|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=slave|width=24|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=3|role=slave|width=29|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=slave|width=32|ss=active_high|order=lsb_first | 1 | 1 | 0 |
| mode=3|role=slave|width=32|ss=active_low|order=msb_first | 1 | 1 | 0 |
| mode=3|role=slave|width=8|ss=active_low|order=msb_first | 1 | 1 | 0 |

## Compact Suite Representativeness

- Representativeness score: **100.0%** (70/70)
- Confidence claim: compact suite representativeness is based on coverage closure and stable gate outcomes, not raw case count.

| Dimension | Covered / Target | Missing Required Values |
|---|---:|---|
| bit_order | 2 / 2 | none |
| clock_jitter_test | 2 / 2 | none |
| data_width | 11 / 11 | none |
| default_data_enabled | 2 / 2 | none |
| default_data_pattern | 5 / 5 | none |
| dma_support | 2 / 2 | none |
| fifo_buffers | 2 / 2 | none |
| interrupts | 2 / 2 | none |
| mode | 4 / 4 | none |
| multi_master | 2 / 2 | none |
| role | 3 / 3 | none |
| selected_slave_bucket | 2 / 2 | none |
| ss_polarity | 2 / 2 | none |
| test_duration | 3 / 3 | none |
| waveform_capture | 2 / 2 | none |
| special_feature_pairs_2way | 24 / 24 | none |

## Special Feature Pairwise Coverage (2-way)

| Pair | Covered / Target | Missing Pairs |
|---|---:|---|
| interrupts x fifo_buffers | 4 / 4 | none |
| interrupts x dma_support | 4 / 4 | none |
| interrupts x multi_master | 4 / 4 | none |
| fifo_buffers x dma_support | 4 / 4 | none |
| fifo_buffers x multi_master | 4 / 4 | none |
| dma_support x multi_master | 4 / 4 | none |

## Balance Matrix (Modern Cases)

| Dimension | Value Counts | Min | Max | Max/Min Ratio |
|---|---|---:|---:|---:|
| bit_order | lsb_first:60, msb_first:60 | 60 | 60 | 1.00 |
| clock_jitter_test | False:53, True:67 | 53 | 67 | 1.26 |
| data_width | 1:39, 10:2, 11:1, 12:4, 13:1, 14:2, 15:1, 16:12, 17:1, 18:2, 19:1, 2:1, 20:2, 21:1, 22:2, 23:1, 24:14, 25:1, 26:1, 27:1, 28:2, 29:1, 3:1, 30:1, 31:1, 32:14, 4:1, 5:1, 6:2, 7:1, 8:4, 9:1 | 1 | 39 | 39.00 |
| default_data_enabled | False:25, True:95 | 25 | 95 | 3.80 |
| default_data_pattern | 0000:14, 5555:17, a5a5:60, custom:11, ffff:18 | 11 | 60 | 5.45 |
| dma_support | False:69, True:51 | 51 | 69 | 1.35 |
| fifo_buffers | False:56, True:64 | 56 | 64 | 1.14 |
| interrupts | False:30, True:90 | 30 | 90 | 3.00 |
| mode | 0:29, 1:33, 2:33, 3:25 | 25 | 33 | 1.32 |
| multi_master | False:81, True:39 | 39 | 81 | 2.08 |
| num_slaves | 1:4, 2:11, 3:29, 4:25, 5:39, 6:7, 8:5 | 4 | 39 | 9.75 |
| role | dual:45, master:40, slave:35 | 35 | 45 | 1.29 |
| ss_polarity | active_high:57, active_low:63 | 57 | 63 | 1.11 |
| waveform_capture | False:6, True:114 | 6 | 114 | 19.00 |

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
- issue-1099: PASS
- issue-1100: PASS
- issue-1101: PASS
- issue-1102: PASS
- issue-1103: PASS
- issue-1104: PASS
- issue-1105: PASS
- issue-1106: PASS
- issue-1107: PASS
- issue-1108: PASS
- issue-1109: PASS
- issue-1110: PASS
- issue-1111: PASS
- issue-1112: PASS
- issue-1113: PASS
- issue-1114: PASS
- issue-1115: PASS
- issue-1116: PASS
- issue-1117: PASS
- issue-1118: PASS
- issue-1119: PASS
- issue-1120: PASS
- issue-1121: PASS
- issue-1122: PASS
- issue-1123: PASS
- issue-1124: PASS
## Failure Signatures

| Gate | Corner Signature | Count | Issues |
|---|---|---:|---|
| (none) | (none) | 0 | (none) |
