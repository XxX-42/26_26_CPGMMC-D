# 问题一求解结果

## 1. 数据与物理口径

官方原始数据包含 15 个服务区和 80 个不可拆货箱。每架次仅执行 O01→Si→O01；沿 DEM 像元最高值 +50m 巡航，服务区作业高度为地面 +30m；去程带货、返程空载。
水平能耗和爬升能耗的具体展开式继承 Gate-0，状态为 **DECLARED_MODEL_ASSUMPTION**，并非题面逐项给出的官方公式。
累计作业时间 = 工位固定准备 + 每箱装载 + 往返纯飞行 + 接收点基础交接 + 每箱增加交接。运输机参数表未列架次周转时间，Q1 不调度实体机，故未添加虚构周转常数；官方模板“往返时间”填写纯飞行往返时间。

## 2. 最大安全载荷

| 服务区 | A kg/限制 | B kg/限制 | C kg/限制 |
|---|---:|---:|---:|
| S001 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 80.000 / RATED_PAYLOAD_LIMITED |
| S002 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 68.860 / ENERGY_LIMITED |
| S003 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 68.206 / ENERGY_LIMITED |
| S004 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 63.698 / ENERGY_LIMITED |
| S005 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 80.000 / RATED_PAYLOAD_LIMITED |
| S006 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 80.000 / RATED_PAYLOAD_LIMITED |
| S007 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 80.000 / RATED_PAYLOAD_LIMITED |
| S008 | 25.000 / RATED_PAYLOAD_LIMITED | 28.801 / ENERGY_LIMITED | 58.904 / ENERGY_LIMITED |
| S009 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 80.000 / RATED_PAYLOAD_LIMITED |
| S010 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 80.000 / RATED_PAYLOAD_LIMITED |
| S011 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 80.000 / RATED_PAYLOAD_LIMITED |
| S012 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 68.118 / ENERGY_LIMITED |
| S013 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 80.000 / RATED_PAYLOAD_LIMITED |
| S014 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 80.000 / RATED_PAYLOAD_LIMITED |
| S015 | 25.000 / RATED_PAYLOAD_LIMITED | 30.000 / RATED_PAYLOAD_LIMITED | 80.000 / RATED_PAYLOAD_LIMITED |

共 45 项；限制因素计数：{'RATED_PAYLOAD_LIMITED': 39, 'ENERGY_LIMITED': 6}。

## 3. 最优货箱组批

| 服务区 | 箱数 | 架次 | 机型 | 总能耗 kWh | 累计作业 s |
|---|---:|---:|---|---:|---:|
| S001 | 15 | 2 | C | 5.913299 | 3186.341 |
| S002 | 8 | 2 | B,C | 8.434578 | 3858.506 |
| S003 | 8 | 2 | B,C | 8.544888 | 4450.654 |
| S004 | 6 | 1 | C | 6.152897 | 2301.061 |
| S005 | 6 | 1 | C | 4.222175 | 1877.195 |
| S006 | 6 | 1 | C | 2.597976 | 1561.560 |
| S007 | 5 | 1 | C | 3.410870 | 1907.575 |
| S008 | 5 | 1 | C | 5.836024 | 2199.712 |
| S009 | 3 | 1 | B | 2.096211 | 1558.442 |
| S010 | 3 | 1 | B | 1.823146 | 1555.377 |
| S011 | 3 | 1 | B | 1.073934 | 1188.424 |
| S012 | 3 | 1 | B | 2.752354 | 1922.735 |
| S013 | 3 | 1 | B | 1.824718 | 1510.470 |
| S014 | 3 | 1 | B | 2.140303 | 1869.752 |
| S015 | 3 | 1 | B | 2.307425 | 1828.289 |

## 4. 总体结果

- 总架次数：18；A/B/C：0/9/9。
- 总运输能耗：59.130796487 kWh。
- 累计作业时间：32776.092677 s。
- 最小返航 SOC：0.230887874；能量余量范围：0.247102992–3.802023614 kWh。

## 5. 最优性

15 个服务区独立完整枚举可行子集（同一子集仅保留能耗词典序占优机型），然后三阶段集合划分 MILP。第一、第二、第三层状态依次为 OPTIMAL、OPTIMAL、OPTIMAL；求解器：HiGHS (scipy.optimize.milp)。
第一层架次数为整数等式锁定；第二层能耗通过每区记录的极小容差锁定，详情见求解日志。

## 6. 返航余量敏感性

详见 `q1_sensitivity_summary.md`。各档均重新求最大安全载荷、候选与词典序最优解。

## 7. Validator

- boxes_missing=0；boxes_duplicated=0；cross_service_batch=0。
- mass_violations=0；volume_violations=0；safe_payload_violations=0；energy_reserve_violations=0。
- **Q1_VALID = TRUE**；官方 Excel 导出与回读：PASS。
