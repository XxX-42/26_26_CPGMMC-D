# 问题四求解结果

## 1. Q3 冻结
Q3 Final 任务、时刻和通信保障关系未变；全部资源占用使用固定快照。

## 2. 依赖图
运输同架次及固定中继保障连接后有 3 个不可拆分量。

- C01: S001, S002, S003, S004, S007, S008, S009, S010, S011, S012, S013, S014, S015
- C02: S005
- C03: S006

## 3. K=2 结果

- 组 1: S001, S002, S003, S004, S005, S007, S008, S009, S010, S011, S012, S013, S014, S015；箱 74；质量 699.000 kg；运输 23 架次；中继 5 架次；工作量 58583.507 resource-s；资源 {'A_UAV': 4, 'B_UAV': 2, 'C_UAV': 2, 'A_BATTERY': 6, 'B_BATTERY': 4, 'C_BATTERY': 4, 'RELAY_UAV': 2, 'RELAY_COMPONENT': 3}。
- 组 2: S006；箱 6；质量 59.000 kg；运输 1 架次；中继 0 架次；工作量 1561.560 resource-s；资源 {'A_UAV': 0, 'B_UAV': 0, 'C_UAV': 1, 'A_BATTERY': 0, 'B_BATTERY': 0, 'C_BATTERY': 1, 'RELAY_UAV': 0, 'RELAY_COMPONENT': 0}。
- 资源缺口 {'A_UAV': 0, 'B_UAV': 0, 'C_UAV': 1, 'A_BATTERY': 0, 'B_BATTERY': 0, 'C_BATTERY': 1, 'RELAY_UAV': 0, 'RELAY_COMPONENT': 0}；隔离冗余 {'A_UAV': 0, 'B_UAV': 0, 'C_UAV': 1, 'A_BATTERY': 0, 'B_BATTERY': 0, 'C_BATTERY': 1, 'RELAY_UAV': 0, 'RELAY_COMPONENT': 0}；F1/F2/F3 = 3/4, 3/4, 570219471268950049/601450661787756989。

## 3. K=3 结果

- 组 1: S001, S002, S003, S004, S007, S008, S009, S010, S011, S012, S013, S014, S015；箱 68；质量 640.000 kg；运输 22 架次；中继 4 架次；工作量 54200.372 resource-s；资源 {'A_UAV': 4, 'B_UAV': 2, 'C_UAV': 2, 'A_BATTERY': 6, 'B_BATTERY': 4, 'C_BATTERY': 4, 'RELAY_UAV': 2, 'RELAY_COMPONENT': 3}。
- 组 2: S005；箱 6；质量 59.000 kg；运输 1 架次；中继 1 架次；工作量 4383.135 resource-s；资源 {'A_UAV': 0, 'B_UAV': 0, 'C_UAV': 1, 'A_BATTERY': 0, 'B_BATTERY': 0, 'C_BATTERY': 1, 'RELAY_UAV': 1, 'RELAY_COMPONENT': 1}。
- 组 3: S006；箱 6；质量 59.000 kg；运输 1 架次；中继 0 架次；工作量 1561.560 resource-s；资源 {'A_UAV': 0, 'B_UAV': 0, 'C_UAV': 1, 'A_BATTERY': 0, 'B_BATTERY': 0, 'C_BATTERY': 1, 'RELAY_UAV': 0, 'RELAY_COMPONENT': 0}。
- 资源缺口 {'A_UAV': 0, 'B_UAV': 0, 'C_UAV': 2, 'A_BATTERY': 0, 'B_BATTERY': 0, 'C_BATTERY': 2, 'RELAY_UAV': 1, 'RELAY_COMPONENT': 0}；隔离冗余 {'A_UAV': 0, 'B_UAV': 0, 'C_UAV': 2, 'A_BATTERY': 0, 'B_BATTERY': 0, 'C_BATTERY': 2, 'RELAY_UAV': 1, 'RELAY_COMPONENT': 1}；F1/F2/F3 = 2/1, 13/6, 526388120439447439/601450661787756989。

## 5. K=2 vs K=3
K2 枚举 3，K3 枚举 1；资源缺口分别 2、5。

## 6. 精确性
在固定 Q3 任务和本文 must-link 定义下，两组和三组全部无标签分区均已完整枚举；资源需求由半开区间峰值与达到峰值的着色证实。

## 7. Validator
15 个服务区各恰好分配一次；依赖、固定任务、资源着色及 Excel 回读违规为 0。库存缺口是分析指标，不是分区违规。
