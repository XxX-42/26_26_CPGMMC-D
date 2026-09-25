# Q1 独立 Validator

Q1_VALID = TRUE

| 指标 | 数值 |
|---|---:|
| boxes_total | 80 |
| boxes_assigned | 80 |
| boxes_missing | 0 |
| boxes_duplicated | 0 |
| cross_service_batch | 0 |
| mass_violations | 0 |
| volume_violations | 0 |
| safe_payload_violations | 0 |
| energy_reserve_violations | 0 |
| invalid_aircraft_type | 0 |
| invalid_service | 0 |
| unknown_boxes | 0 |
| stored_value_mismatches | 0 |
| Q1_VALID | True |
| official_template_export | PASS |
| excel_roundtrip_check | PASS |
| sortie_rows | 18 |
| unique_boxes | 80 |
| other_sheets_unchanged | True |

原始货箱、机型、DEM 和节点重新读取；逐架次重算质量、容积、飞行时间、能耗与 SOC。
官方模板回读：PASS，其他 Sheet 值保持原样。
