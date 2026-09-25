# 2026“华为杯”D题《山区洪涝灾害下无人机运输与通信协同优化》Deep Research 技术路线研究报告

## 执行摘要与题目数据审计

**第一章｜执行摘要**

【官方确定】我已完整读取你上传的赛题 DOCX、官方数据集与核心文件审计报告，并实际打开检查结果提交模板 XLSX。赛题的本质不是“四个彼此独立的问题”，而是一条逐步加约束、最终冻结方案再分区的决策链：

\[
\text{统一物理模型}
\rightarrow Q1\text{单点能力/组批}
\rightarrow Q2\text{运输路径+资源时序}
\rightarrow Q3\text{运输-通信联合调度}
\rightarrow Q4\text{固定Q3方案后的资源隔离分区}.
\]

尤其要纠正一个容易导致整篇论文架构错误的理解：**Q1 的组批结果不应机械冻结给 Q2；Q2 的运输路线也不应机械冻结给 Q3。** Q1 是能力分析和候选组批/下界来源；Q2 是不考虑通信的最优或高质量基准；Q3 题面明确要求“联合确定”运输与中继，因此允许、而且必要时应当重新调整 Q2 的运输决策。真正必须严格冻结的是 **Q3 → Q4**。fileciteturn0file0

【研究推断】这道题最危险的地方不是 VRP 本身，而是四类同步关系同时存在：

1. 箱子—路线—载荷随投递逐段下降；
2. 实体无人机—共享电池—充电之间的时间资源同步；
3. 运输轨迹—DEM—三维 LOS—双向链路预算—中继服务区间同步；
4. Q3 固定任务—Q4 must-link—各分组峰值资源需求同步。

因此，**把全题写成一个巨大 MINLP/MILP 不是“更高级”，而是比赛剩余时间内高概率自杀**；反过来，仅做“VRP + 最近中继点 + K-means”又会漏掉题目的核心难点。

【研究结论】综合题意完整性、剩余约 91 小时的竞赛时间、可实现性、求解器稳定性、论文深度和一等奖增量创新空间，最终前三为：

| 排名 | 完整技术路线 | 获奖适配评分 | 核心定位 |
|---|---|---:|---|
| **TOP 1** | **候选运输架次生成 + MILP/CP-SAT 资源排程 + DEM 中继候选离散化 + 通信子问题 + 迭代修复** | **93.0/100** | 最稳，兼顾一等奖深度 |
| **TOP 2** | **运输 sortie 与 relay coverage pattern 联合生成 + Set-Partitioning Master MILP** | **89.5/100** | 理论最完整，上限最高但开发风险明显更高 |
| **TOP 3** | **可行性优先 ALNS/LNS Matheuristic + 精确子问题修复** | **85.0/100** | anytime 性最好，适合时间失控后的高质量备用路线 |

这里的“获奖适配评分”仅是你指定的启发式决策指标，**不是获奖概率**。

TOP 1 的关键不是“用了 MILP + CP-SAT”这个标签，而是一个非常具体的架构：

> **连续几何和物理计算全部前置为统一预处理 → 把大量连续飞行行为压缩成有限的可行 sortie / relay option → 离散优化负责组合选择和资源同步 → 最后由独立 validator 对原始 DEM、原始公式、全轨迹通信重新计算。**

这正好符合近年无人机路径、应急物流和同步资源调度研究中反复出现的“数学模型 + 分解/启发式 + 小规模精确验证”范式。2024 年 Omega 的灾后直升机—卡车—无人机研究使用 MIP 加两阶段启发式，并用 Gurobi 在小规模实例验证；2025 年 ESWA 的动态 truck–drone 调度则直接采用 matheuristic 处理复杂同步关系。citeturn21search0turn23search2

**真正值得冲一等奖的创新点应限制为三处：**

第一，**DEM 驱动的 relay candidate reduction + adaptive refinement**；第二，**transportation–relay iterative coupling**，而不是简单运输后处理；第三，**Q4 基于 fixed-Q3 dependency graph 的 must-link 精确分区**。这些创新都来自题目结构，不需要训练神经网络，也不会把工程风险拉爆。

【官方确定】本次检索时北京时间约为 2026 年 9 月 23 日 16:37；竞赛自 9 月 23 日 8:00 开始，9 月 27 日 12:00 截止，因此此时距离竞赛截止约 **91 小时 23 分钟**。组委会信息还建议最迟约 9 月 27 日 11:00 前锁定论文并提交 MD5，意味着真正可自由研发的时间应再预留至少一小时安全缓冲。citeturn19time0turn19search0turn26search3

**结论先说死：现在不应该尝试 branch-and-price、Benders、连续 3D MINLP、RL/GNN 或大规模 NSGA-II 作为主体。** 如果团队当前还没有统一 DEM/能耗/充电/通信计算模块，继续讨论更花哨的算法是在逃避真正风险。

**第二章｜题目与数据审计**

### 文件读取结论

【官方确定】赛题 DOCX 明确给出了四问关系、飞行/能源统一计算规则以及通信判定口径，是最高优先级规则源。fileciteturn0file0

【官方确定】你上传的《官方数据集与核心文件报告.md》说明，原始完整赛题目录应包含赛题、结果模板、五份基础参数 XLSX、地理说明文件、DEM GeoTIFF、地理 CSV/MAT 和交互地图等 19 个文件。当前本对话直接上传给我的只有三份文件，因此我能够独立逐文件检查的是 **DOCX、审计报告、结果模板**；五份原始参数 XLSX 和原始 DEM 本身没有作为独立附件上传。因此，下述 A/B/C 数量、电池数量、通信数值等已经完成“题面—审计报告一致性核查”，但我不能虚构成“重新逐单元格读取了那五份未上传 XLSX”。fileciteturn0file1

### 核心规模复核

| 数据对象 | 核验结果 | 状态 |
|---|---:|---|
| 临时调度中心 | O01，1 个 | 【官方确定】 |
| 服务区 | S001–S015，共 15 个 | 【官方确定】 |
| 货箱 | 80 箱，不可拆 | 【官方确定】 |
| 首批保障箱 | 30 箱 | 【官方确定】 |
| 医疗物资 | 16 箱 | 【审计报告确定】 |
| 饮用水 | 36 箱 | 【审计报告确定】 |
| 应急食品 | 19 箱 | 【审计报告确定】 |
| 生活卫生用品 | 9 箱 | 【审计报告确定】 |
| 总质量 | 约 758 kg | 【审计报告确定】 |
| 总体积 | 约 2.011 m³ | 【审计报告确定】 |
| 运输机型 | A/B/C | 【官方确定】 |
| 额定载质量 | 25/30/80 kg | 【审计报告确定】 |
| 实体运输无人机 | 8 架，约 4/2/2 | 【审计报告确定】 |
| 共享电池 | A/B/C 分别 6/4/4 组 | 【审计报告确定】 |
| 中继无人机 | R 型 2 架 | 【审计报告确定】 |
| 中继能源组件 | 6 组 | 【审计报告确定】 |
| 中继组件可用能量 | 3.2 kWh | 【审计报告确定】 |
| 中继返航 SOC 下限 | 20% | 【审计报告确定】 |
| 最大中继 AGL | 300 m | 【审计报告确定】 |
| DEM | Copernicus GLO-30，约 30 m | 【官方确定】 |
| 标准测试人口 | 3422 人 | 【审计报告确定】 |
| 背景新闻受困人口 | 约 8000 人，**不得替代标准数据** | 【官方确定】 |

这些数据与审计报告一致。fileciteturn0file0 fileciteturn0file1

【官方确定】首批 30 箱的截止时间分布在审计报告中为：3600 s 的 16 箱、7200 s 的 7 箱、10800 s 的 7 箱。fileciteturn0file1

### Hard Constraints Checklist

| 类别 | 必须满足的约束 | 最容易犯的错误 |
|---|---|---|
| 货箱 | 每箱不可拆、恰好交付一次 | 用连续需求量替代箱级决策 |
| Q1 | 每 sortie 仅 O01→Si→O01 | 跨服务区组批 |
| 重量 | 任一架次起飞载荷不超过机型限制 | 只检查平均载荷 |
| 体积 | 任一架次总体积不超舱容 | 只做重量 bin packing |
| 航迹 | 节点间水平直线 | 自行绕山缩短/优化航迹 |
| DEM | 巡航海拔 = 所穿 DEM 像元最高地形 + 50 m | 用端点高程 |
| 服务区高度 | 地面 + 30 m | 从巡航高度直接连接下一点 |
| 多点架次 | 每投送后从该点 +30 m 重新爬升 | 忽略重复爬升 |
| 载荷 | 投送后逐段降低 | 全程按初始载荷或空载计算 |
| 能耗 | 按题面统一公式 | Q1/Q2/Q3 三套算法 |
| 安全余量 | 整个 sortie 能耗满足 reserve | 仅检查最后一段 |
| 实体无人机 | 同一实体机任务不能重叠 | 把机型数量当无限 |
| 电池 | 同机型共享，不同机型不可混用 | 一个“总电池池” |
| SOC | 任务后按真实能耗下降 | 飞完直接变成满电 |
| 复用 | 再投入前必须充至 100% | 允许部分充电直接复飞 |
| 充电 | 0–90%、90–100% 两阶段速率 | 全程单一线性速率 |
| 电池时间 | 任务占用、充电不能重叠 | 只做能量约束 |
| 医疗 | 应满足附件给定期望送达要求 | 与普通物资同权 |
| 首批保障 | 必须在硬截止前交付 | 当成软惩罚 |
| Q3 通信 | 爬升、巡航、下降、交接全过程 | 只检查节点 |
| 中继 | 单架 relay 两跳；禁止 relay-relay 多跳 | 构造多级中继 |
| LOS | 实际 3D 点 + DEM | 纯二维距离 |
| 链路预算 | 双向门限 | 只验下行 |
| Relay | access 与 backhaul 同时可用 | 分开时段判断 |
| Relay 能源 | 任务、悬停、通信、返航、充电 | 只算悬停 |
| Q4 | 不能重新优化 Q3 路线/任务/保障关系 | 每组重新跑 VRP |
| Q4 must-link | 同一 transport sortie 中服务区必须同组 | 直接 K-means |

这些均来自题面及附录。fileciteturn0file0

### 统一飞行与能源物理口径

【官方确定】对于节点 \(i,j\)，先由水平直线穿过的 DEM 像元确定最大地形高程 \(H^{\max}_{ij}\)，巡航海拔为

\[
H^{c}_{ij}=H^{\max}_{ij}+50.
\]

O01 起降作业高度为其地面海拔，服务区作业高度为

\[
H^{op}_{S_i}=H^{ground}_{S_i}+30.
\]

每段均为“爬升—水平—下降”。fileciteturn0file0

题面给出的载荷相关等效航程可写成：

\[
L_g(q)=L_g^0-
\left(L_g^0-L_g^F\right)
\left(\frac{q}{Q_g}\right)^{3/2},
\qquad 0\le q\le Q_g.
\]

航段飞行时间结构为：

\[
t_{gij}
=
\frac{h^+_{ij}}{v_g^\uparrow}
+
\frac{d_{ij}}{v_g^c}
+
\frac{h^-_{ij}}{v_g^\downarrow}.
\]

航段能耗为：

\[
E_{gij}(q)
=
E^{hor}_{gij}(q)+E^{up}_{gij}(q),
\]

下降不单独计算附加能耗。一个 sortie \(p\) 必须满足：

\[
E_p^T
=
\sum_{(i,j)\in p}E_{gij}(q_{pij})
\le
(1-\rho_g)E_g^{use}.
\]

这里真正关键的是 \(q_{pij}\) 必须随着投递下降，而不是一个 sortie 使用单一载荷。fileciteturn0file0

### 两阶段充电

对于任务后 SOC \(s\)，统一实现：

\[
t^{chg}(s)=
\begin{cases}
T^{full}
\left[
0.65\frac{0.90-s}{0.90}+0.35
\right],
&0\le s<0.90,\\[4pt]
T^{full}
\left[
0.35\frac{1-s}{0.10}
\right],
&0.90\le s\le1.
\end{cases}
\]

【官方确定】同一能源资源的任务占用和充电区间不得重叠；不同能源资源可以并行。fileciteturn0file0

### 通信统一计算

\[
P^{th}_b=P^{sens}_b+M_b,
\]

\[
L^{\max}_{a\to b}
=
P_{t,a}+G_{t,a}+G_{r,b}
-L_{sys}-P^{th}_b.
\]

双向链路采用两个通信方向允许损耗的较小值：

\[
L_{ab}^{bi}=
\min\{L^{\max}_{a\to b},L^{\max}_{b\to a}\}.
\]

自由空间传播损耗：

\[
FSPL=32.45+
20\log_{10}(f_{\rm MHz})
+
20\log_{10}(D_{\rm km}),
\]

地形遮挡后：

\[
L^{tot}=FSPL+b\,L_{obs}.
\]

仅当

\[
L^{tot}\le L_{ab}^{bi}
\]

链路才可用。运输机在时刻 \(t\) 的状态必须属于“G01 直连”或“通过一架 relay 的两段链路同时可用”，否则就是通信中断。fileciteturn0file0

审计报告列出的标准通信数值包括 2400 MHz、系统损耗 3 dB、遮挡附加损耗 10 dB、灵敏度 −98 dBm、衰落裕量 8 dB；正式实现仍应从原始 `通信链路参数.xlsx` 读入，禁止硬编码。fileciteturn0file1

### 结果模板对建模的反向约束

我实际打开了 `结果提交模板.xlsx`。模板不是装饰，它已经告诉我们最终代码的最低输出接口：

| Sheet | 必须输出的核心字段 |
|---|---|
| Q1_单点组批 | 架次、服务区、机型、货箱列表、质量、体积、往返时间、能耗、返航 SOC |
| Q2_运输架次 | sortie、实体无人机、机型、电池、开始时刻、访问顺序、返回时刻、能耗 |
| Q2_逐箱交付 | 每箱 sortie、服务区、交付完成时刻 |
| Q3_中继架次 | relay sortie、relay UAV、组件、开始、经纬度、海拔、建链完成、服务结束、返回、能耗 |
| Q3_通信保障 | transport sortie、通信阶段、开始/结束时间、直连/中继、relay sortie |
| Q4_分区配置 | \(K=2/3\)、组、服务区、A/B/C UAV、电池、中继 UAV、能源组件数量 |

审计报告也确认模板共六张工作表且为空白提交模板。fileciteturn0file1

一个非常有价值的反推是：**Q3 官方模板本身就是“通信阶段 + 时间区间”表达，而不是要求每秒一行通信状态。** 因此，“轨迹连续验证 → 压缩成 maximal communication intervals → 输出区间”是非常自然的工程架构。

## 数学结构识别与最新文献综述

**第三章｜数学结构识别**

### Q1：不是普通 Bin Packing

Q1 同时包含三层结构：

\[
\text{连续安全载荷}
\rightarrow
\text{不可拆货箱 feasible subset}
\rightarrow
\text{set partitioning}.
\]

传统 bin packing 假定箱体容量是固定的，但本题“容量”除了重量和体积，还受服务区地形、往返能耗以及安全余量影响。因此，对机型 \(g\)、服务区 \(i\)，真正的有效容量应写成：

\[
\mathcal F_{ig}
=
\left\{
S\subseteq K_i:
\sum_{k\in S}w_k\le Q_g,\;
\sum_{k\in S}v_k\le V_g,\;
E_{ig}(S)\le (1-\rho_g)E_g^{use}
\right\}.
\]

之后才是在所有 \(S\in\mathcal F_{ig}\) 中找一个集合划分。

【研究推断】15 个服务区、80 箱，平均每区只有约 5.3 箱，因此 **“枚举 feasible subsets + set partitioning”明显比 generic GA 更值得优先尝试**。但不能假定每区都只有 5 箱；正式程序应先读取 \(n_i\)，若某服务区 \(2^{n_i}\) 过大，再切换 DFS branch-and-bound 或直接 bin-packing MILP。

最大安全载荷也不是“额定载重 × 某个安全系数”。对直接往返，

\[
E_{O,i}(q)+E_{i,O}(0)
\le (1-\rho_g)E_g^{use}.
\]

应在

\[
0\le q\le Q_g
\]

上通过题面统一能耗函数求最大的可行 \(q\)。在确认能耗关于 \(q\) 单调后可以二分；若实现公式存在非单调细节，则直接做一维精确搜索/分段求根。

### Q2：Heterogeneous Multi-Trip VRP + RCPSP/Job Shop

它并不是“一个 VRPTW”能够概括的。

路径层同时决定：

\[
\text{boxes}
+\text{batch}
+\text{visit sequence}
+\text{drone type}.
\]

排程层决定：

\[
\text{physical UAV}
+\text{battery}
+\text{start time}
+\text{charging}.
\]

因此更准确的数学结构是：

> **异构、多架次、载荷依赖能耗的 VRP + 并行可替代机器调度 + 能源资源周转调度。**

一条 sortie 本质上是一个需要**同时占用一个实体 UAV 和一个兼容电池**的非抢占 job；电池在 job 后还要继续进入确定时长的 charging job。

这使 CP-SAT 的 interval/no-overlap 建模非常有吸引力。OR-Tools 官方文档明确把 interval variable、precedence 和 `NoOverlap` 作为 job-shop scheduling 的核心建模工具；但 CP-SAT 仅使用整数，因此连续能耗/时间需要预先计算并缩放或作为 route 参数输入。citeturn16search0turn16search1

### Q3：几何可行域 + Set Cover + 双资源同步调度

把一条 transport sortie 的完整三维轨迹写成

\[
\mathbf p_p(t),\quad t\in[\tau_p,\tau_p+T_p].
\]

对于直连不可用时刻集合：

\[
\mathcal U_p
=
\{t:
A(\mathbf p_p(t),G01)=0\}.
\]

对于候选 relay \(r\)：

\[
C_{pr}(t)
=
A(\mathbf p_p(t),r)
\land A(r,G01).
\]

Q3 的通信部分就是：

> 对所有 \((p,t)\) 的 uncovered demand，在 relay 空间位置、relay sortie 时间和能源资源约束下进行连续覆盖。

离散化后，它兼具：

- set covering；
- interval covering；
- scheduling；
- alternative resource assignment；
- terrain-aware relay placement。

所以“最近可行中继点”根本不足以解决 Q3。

### Q4：固定任务依赖图上的 constrained partition

由 Q3 最终 sortie 构造服务区图：

\[
G=(S,E),
\]

若 \(i,j\) 同属某一 transport sortie，则加入 must-link 边

\[
(i,j)\in E.
\]

题面明确要求这些服务区同组，因此其 connected components 可以安全收缩成 supernodes。fileciteturn0file0

之后才是对最多 15 个原节点、通常更少 supernodes 的 2-way/3-way partition。

这意味着：

**K-means 是错误的第一反应。**

它既不能自然表达 must-link，也不直接优化电池峰值、中继峰值、库存缺口。

2024/2025 的 connected graph partition 文献已经采用 mixed-integer programming 处理固定组数和连接/规模约束；对于本题至多 15 个服务区，问题规模远小于那些研究场景，因此穷举/精确 MILP 反而比复杂图启发式更合理。citeturn27search0turn27search3

**第四章｜最新研究证据及其对本题的真正启示**

### Q1 与载荷能耗

Zhang 等在 *Transportation Research Part D* 2021 的综述系统比较了无人机配送能耗模型，并指出不同模型给出的能耗差异可能很大，payload 和 speed 对续航都有显著影响。DOI: `10.1016/j.trd.2020.102668`。citeturn21search1

**可借鉴：** payload 不能粗暴忽略；灵敏度分析必须做。

**不能照搬：** 本题已经强制给出了统一能耗规则，所以不能为了“更真实”擅自用论文中的物理功率模型覆盖题面模型。

这点非常重要：**文献是证明建模意识，不是获得修改官方公式的许可。**

### Q2 路径、时间窗和多架次

Kuo 等 2022 年研究 VRP with Drones + Time Windows，提出 MIP，并以 VNS 求解较大实例，还拿精确 MIP 和 ALNS 做比较。DOI: `10.1016/j.eswa.2021.116264`。citeturn21search3

对本题的启示不是“应该用 VNS”，而是：

> **小规模用 exact model 定义问题和校验，大规模/复杂组合用 problem-specific neighborhood 加速。**

2024 年 Omega 的灾后应急物资研究建立 truck–helicopter–drone MIP，并对大规模实例采用两阶段启发式，同时用 Gurobi 在小实例上验证算法有效性。DOI: `10.1016/j.omega.2024.103104`。citeturn21search0

2025 年 Zhao 等针对动态 truck–drone collaboration，专门用 matheuristic 处理复杂同步关系，并提供不同精度/效率版本。DOI: `10.1016/j.eswa.2024.126218`。citeturn23search2

2026 年最新的 GRV–UAV emergency delivery 研究允许 UAV 一次访问多个任务节点，并使用带同步机制的 hybrid heuristic。DOI: `10.1016/j.seps.2026.102487`。citeturn23search0

这些研究共同指向：**route + synchronization 分解是成熟路线，不是为了比赛临时拼凑。**

### 电池与能源调度

2023 年 *Applied Soft Computing* 的 UAV routing with recharging 建立 MINLP，并使用改进 ALNS；其场景同样说明一旦路径与充电耦合，纯 exact formulation 很快会变重。DOI: `10.1016/j.asoc.2023.110831`。citeturn23search4

2023 年 *Computers & Operations Research* 针对 EVRPTW 与同步移动充电/换电采用 VNS-based matheuristic。DOI: `10.1016/j.cor.2023.106310`。citeturn23search1

2023 年 *Applied Energy* 的移动充电系统甚至显式跟踪每块电池，并把车辆 routing 与 battery scheduling 分层。DOI: `10.1016/j.apenergy.2023.120845`。citeturn23search20

更值得注意的是，2026 年 *Computers & Operations Research* 专门发表了一篇 note，指出 battery-swapping policy 中一个假设差异就可能导致结果解释错误。DOI: `10.1016/j.cor.2025.107277`。citeturn23search6

这直接支持本题的工程原则：

> **电池不能做“架次能耗总量 ≤ 电池总能量”的聚合资源。必须逐块跟踪时间占用、SOC 和充电。**

### Q3 terrain-aware relay

Zheng 与 Chen 在 IEEE TWC 2024 的 *Geography-Aware Optimal UAV 3D Placement for LOS Relaying* 直接研究实际传播环境下的 LOS relay placement，并证明可以显著收缩三维搜索空间，而不是依赖抽象概率 LOS。DOI: `10.1109/TWC.2023.3301613`。citeturn22search0

它与本题非常匹配的思想是：

> **先利用真实地理环境做 geometry reduction，再优化 relay position。**

但论文研究的是两地面端点、城市环境；本题是**移动运输机 + 山区 DEM + 时变服务需求**，所以不能直接套它的最优性结论。

IEEE T-ITS 2023 的 connectivity-aware UAV path planning 强调的是**沿完整轨迹保持连续 backhaul connectivity**，而不是只保证起终点通信。DOI: `10.1109/TITS.2023.3280995`。citeturn22search1

这与本题附录三“全过程连续通信”的核心要求高度一致。

2026 年出现了更多 emergency UAV communication 研究。例如 CIE 2026 的 UAV emergency communication relay planning 把灾区通信恢复和 UAV cooperative planning 结合；Drones 2026 也出现了 QoS-aware emergency UAV deployment 研究。DOI 分别为 `10.1016/j.cie.2026.111844` 和 `10.3390/drones10070544`。citeturn23search16turn22search2

这些工作证明 relay placement/scheduling 是活跃方向，但很多研究追求网络容量、SINR 或动态基站恢复；**本题的硬判据更简单，也更适合提前预计算成 0–1 coverage matrix。**

### 为什么不推荐 RL / GNN

2025–2026 的确有多智能体强化学习用于 UAV 中继、任务分配和灾后任务规划的研究，例如 multi-hop UAV relay covert communication 使用 MARL，2026 年灾后 victim localisation 也出现 federated MARL。citeturn22search17turn22search5

但它们解决的是：

- 动态未知环境；
- 长期在线决策；
- 多跳/无线资源连续控制；
- 大量重复 scenario 下的策略泛化。

本题则是：

- 单个确定性标准实例；
- 只有 15 个服务区、80 箱；
- 官方 DEM 和设备参数已给；
- 不要求策略泛化；
- 剩余比赛时间约四天。

【研究结论】在这种情况下训练 RL/GNN，没有合理的数据来源，也没有必要的泛化对象，更无法在有限时间内提供强于 MILP/ALNS 的可验证性。

因此纯 RL/GNN 不进入前三。

### 多目标策略

2026 年 humanitarian truck–drone 多目标研究同时比较 NSGA-II 与 \(\varepsilon\)-constraint，说明进化算法适合展示大规模 Pareto trade-off，而 \(\varepsilon\)-constraint 提供更明确的数学约束式权衡。DOI: `10.1016/j.cie.2025.111786`。citeturn23search14

对本题，我不建议直接采用 NSGA-II 作为主求解器。

最适合的是：

\[
\boxed{\text{Lexicographic 主方案}
+
\varepsilon\text{-constraint 敏感性/权衡实验}}
\]

理由是灾害救援目标天然存在优先级：

1. 硬可行性；
2. 医疗和首批保障；
3. 普通物资及时性；
4. makespan；
5. 能耗；
6. sortie 数量。

Gurobi 当前官方文档原生支持 hierarchical multi-objective，通过不同 priority 逐级求解；这比人为写 \(0.25F_1+0.25F_2+\cdots\) 更容易解释。citeturn15search2turn15search11

其中建议：

- 首批保障截止：**硬约束**；
- “医疗物资应满足期望送达时间”中的“应满足”，保守解释为**硬约束**；
- 普通物资期望时间：软及时性指标；
- 如果医疗期望时间确实导致整体不可行，应由 solver/validator 明确报告，而不是暗中软化。

后一点属于【研究推断】，最终仍应以原始配送时限 XLSX 的字段语义核实。

## 优秀竞赛论文经验与额外数据审查

**第五章｜优秀论文结构研究**

这里必须先揭露一个信息源风险。

【研究结果】我确实定位到了公开的 2004–2023 中国研究生数学建模优秀论文集合以及 GitHub 中的部分优秀论文 PDF，例如 2021、2023 年若干编号论文，但这些是公开整理库，不是一个可以逐篇稳定检索全文章节的组委会官方 HTML 档案。当前公开搜索接口也无法可靠抽取这些 PDF 的完整文本。因此，**我不会为了满足“5–10 篇”这个形式要求，凭文件编号编造论文摘要和章节结构。**

公开库中能够定位到 2021 D、2023 D 等优秀论文 PDF 文件。citeturn17search4turn17search12

当前能够高可信核验、且与本题结构非常近的案例中，最重要的是 2022 年研究生赛 B 题。

### 高相关样本

| 样本 | 可核验信息 | 与本题关系 | 可借鉴点 |
|---|---|---|---|
| 2022 研赛 B | 《方形件组批优化问题》；大连理工全国一等奖论文题名为《基于混合整数规划模型的方形件组批优化问题研究》 | Q1 高度相关 | 组批问题直接用 MIP 并不“低级” |
| 2022 研赛 C | 汽车制造公司涂装—总装缓存区调序调度优化 | Q2 电池/无人机时序相关 | 调序、资源同步、阶段继承 |
| 2021 研赛 F | 航空公司机组优化排班问题 | Q2 实体 UAV+资源排程相关 | assignment + scheduling 的工程论文组织 |
| 2024 研赛 A | 风电场有功功率优化调度 | 多阶段工程优化相关 | 统一物理模型 + 优化调度 |
| 2018 国赛 B 类 RGV 动态调度 | 0-1规划/动态调度公开优秀论文较多 | Q2 资源排程近似 | 决策变量—约束—仿真验证叙事 |
| 2023/2024 graph partition 优化研究 | 并非竞赛论文，但结构可补 Q4 | Q4 高相关 | 先图结构、后 MILP/枚举 |

2022 B 的一等奖论文题名和奖项由大连理工大学官方新闻明确公布。citeturn24search15 2022 年官方赛题页面确认 B 为方形件组批、C 为汽车涂装—总装调序优化。citeturn24search11 2021 F 为航空公司机组优化排班，且华东理工/上海理工相关专家讲座专门将它作为“优化模型”案例剖析。citeturn25search1

【优秀论文经验】从这些可核验工程优化赛题和获奖案例中，真正应吸收到 D 题的不是某个固定算法，而是以下叙事方式：

**第一，公共机理一次定义。**  
坐标、DEM、飞行、能耗、SOC、通信不能在 Q1/Q2/Q3 重复三遍。

**第二，每问都保持“问题分析 → 数学模型 → 求解方法 → 结果 → 校验”的闭环。**

**第三，继承关系要在章首明确。**

例如：

> Q2 继承 Q1 的统一飞行与能源计算模块，但重新优化多点组批；Q3 以 Q2 为基准方案并允许运输方案在通信约束下调整；Q4 完全冻结 Q3 的任务和通信关系。

**第四，优化论文的摘要不是算法清单。**

差的摘要：

> “本文采用 MILP、ALNS、CP-SAT、K-means……”

好的摘要：

> “针对山区灾害中运输资源、能源周转与通信保障相互耦合的问题，建立统一三维飞行—能耗—通信模型；针对不同规模和耦合程度，分别采用集合划分、候选架次调度和基于地形候选中继点的分解协调方法……”

**第五，结果图必须承担证明任务。**

甘特图要证明无资源冲突；SOC 图证明充电可行；通信图证明全过程覆盖；Q4 图证明 must-link 分区，而不是为“漂亮”而画。

### 对优秀论文研究的诚实边界

你要求“至少 5–10 篇逐篇说明摘要、章节结构”。当前能够公开定位到多个优秀论文 PDF，但无法可靠读取它们的全文目录和正文。依据你自己规定的“不得虚构”，本报告**不假装已经对无法读取的 PDF 做逐章内容分析**。

这个缺口不影响技术路线决策；在比赛剩余 91 小时时，继续花数小时下载和整理十年前优秀论文的章节标题，其机会成本已经高于收益。

这正是需要冷酷止损的地方。

**第六章｜额外数据集必要性审查**

结论非常明确：

> **本题不建议增加额外业务数据集。**

理由：

官方已经规定了：

- 需求；
- 80 箱；
- 时限；
- UAV；
- 电池；
- 中继；
- 通信参数；
- Copernicus DEM；
- 节点坐标。

而题面特别强调标准测试场景的需求、时限、装备和资源参数以附件为准。fileciteturn0file0

额外下载：

- 真实横州市人口；
- OpenStreetMap 道路；
- 气象；
- 其他 DEM；
- 真实 8000 人需求；

都不会提高官方测试解的正确性，反而可能造成坐标、需求和口径冲突。

Copernicus DEM 也没有必要重新下载。题目已经提供了 GLO-30 场景裁剪数据；其官方数据产品 DOI 在题面中已经给出为 `10.5270/ESA-c5d3d65`。fileciteturn0file0

**唯一合理的“额外数据”不是业务数据，而是自行生成的验证实例：**

- 2–3 服务区 toy instance；
- 5–10 箱手算 instance；
- 单中继盲区 instance；
- 人工制造的电池充电冲突 instance。

它们用于 unit test，不参与最终决策。

如果赛后要做算法 benchmark，可以考虑 Solomon VRPTW/CVRPLIB，但**本次比赛现在不值得做**。

## 候选技术路线、淘汰与评分

**第七章｜方法空间发散**

本轮共保留 12 个合理候选架构。

| 编号 | 技术路线 | 核心思想 | 预计实现风险 |
|---|---|---|---|
| A | Monolithic MINLP | 连续 relay 3D + 路径+电池+时序一次求 | 极高 |
| B | Giant time-expanded MILP | 时间×位置×资源全面离散 | 极高 |
| C | Node-arc integrated MILP | 节点弧路径+离散 relay grid 一体化 | 高 |
| D | Route generation + MILP/CP-SAT + relay decomposition | 先构造可行 sortie，再做资源和通信协调 | 中 |
| E | Joint route-relay pattern + set partitioning | 联合列/模式一次选择 | 高 |
| F | CP-SAT-centric finite-route model | 路径池+所有时序统一 CP-SAT | 中高 |
| G | End-to-end ALNS | route/schedule/relay 都在 ALNS 中搜索 | 中 |
| H | ALNS/LNS matheuristic + exact repair | 启发式主搜索+MILP/CP子问题修复 | 中高 |
| I | Column generation / branch-and-price | 动态产生 sortie columns | 极高 |
| J | Benders/decomposition | transport master + relay/battery subproblem cuts | 极高 |
| K | Pure GA/NSGA-II | 染色体编码全方案 | 中高 |
| L | RL/GNN/neural optimization | 训练策略生成路径/中继 | 极高 |

### Monolithic MINLP

优点是理论上最“联合”。

但 Q3 同时包含：

- 离散箱子；
- 离散路线；
- 离散 UAV/battery；
- 连续时间；
- 连续 relay 位置；
- DEM LOS 的非光滑判定；
- log-distance FSPL；
- SOC；
- 两阶段充电。

这几乎就是为求解器制造最坏环境。

**淘汰。**

### Giant time-expanded MILP

如果按秒或较细时间步离散：

\[
|T|\times |R|\times |P|
\]

很快爆炸。

更糟的是，本题其实只有少量任务区间，完全没必要用巨大时间网格。

**淘汰。**

### Node-arc 一体化 MILP

比 MINLP 好，因为 relay 可以离散化，但 routing 的 subtour、box assignment、time synchronization、battery sequencing、communication coverage 全堆一起后 Big-M 很多。

可以当理论模型，但不建议直接作为正式生产 solver。

### Route generation + resource scheduling + relay decomposition

核心是先把物理复杂度“编译”为可行 route/sortie：

\[
p\in\mathcal P.
\]

每个 \(p\) 已经包含：

- 箱子集合；
- 顺序；
- 机型；
- 分段载荷；
- 飞行时间；
- 能耗；
- 每箱相对交付时间。

之后 master 只选择和排程。

这是 TOP 1。

### Joint route-relay pattern

进一步生成：

\[
\omega=
(\text{transport sortie},
\text{relay placement},
\text{coverage pattern}).
\]

Master 一次联合选 transport 和 relay。

数学上更完整，但 pattern 数量可能爆炸。

这是 TOP 2。

### CP-SAT-centric

CP-SAT 对 interval/no-overlap 很适合，特别适合：

- UAV；
- battery；
- relay UAV；
- energy component。

但所有连续量必须整数化；另一方面 route 本身仍需外部生成。citeturn16search0turn16search1

因此 CP-SAT **非常适合作为 TOP 1 的 scheduler，却没有足够理由让它成为整个建模故事的核心。**

### Pure ALNS

ALNS 在 UAV routing/recharging 等问题中已经有成功应用。citeturn23search4turn23search11

问题是本题硬约束太多。一个纯 ALNS chromosome 很容易出现：

- 箱子重复；
- 电池冲突；
- 充电不足；
- 通信断链；
- relay component 冲突。

如果 penalty 参数处理不好，会花大量时间调参。

不进入前三。

### Matheuristic

让 ALNS 只负责“适合启发式搜索的部分”，把硬资源调度和 relay feasibility 交给 exact subsolver，则明显更可靠。

例如：

\[
\text{ALNS route destroy/repair}
\rightarrow
\text{MILP/CP-SAT schedule repair}.
\]

这是 TOP 3。

### Column Generation

理论上特别漂亮：

\[
\min \sum_{p\in\mathcal P}c_p y_p,
\]

从 pricing problem 中动态生成 routes。

但本题 pricing 本身要考虑：

- box subset；
- sequence；
- load-dependent energy；
- deadlines；
- 甚至 communication。

做成真正可靠的 branch-and-price，剩余四天不值得。

**放弃。**

### Benders

理想：

- master：运输；
- subproblem：relay/communication。

但 Q3 relay 子问题的 infeasibility 来源包含离散 LOS/candidate 和时序，不容易形成有力的 Benders cut。

最后很可能变成“每次 infeasible 就加一个 no-good cut”，理论高级、计算并不高级。

**放弃。**

### GA / NSGA-II

2026 年应急物流中仍有大量 NSGA-II 研究。citeturn23search17turn23search14

但论文规模大、多目标 exploratory study 与四天比赛的要求不同。

本题要的是一个**确定、完全可验证的提交表格**。

纯 NSGA-II 不进入前三。

### RL/GNN

不再重复。

没有训练集、没有反复 deployment、没有足够规模、没有时间。

**直接砍。**

**第八章｜淘汰评分**

评分仍按：

\[
70\% \text{稳二等奖}
+
30\% \text{一等奖上限}.
\]

| 方案 | 保二稳健性 /70 | 冲一上限 /30 | 数据难度 | 模型难度 | 算法难度 | 代码难度 | 调试风险 | 论文潜力 | 总分 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| D Route pool + decomposition | **66.0** | **27.0** | 2 | 7 | 7 | 7 | 6 | 9 | **93.0** |
| E Joint route-relay patterns | 61.0 | **28.5** | 2 | 9 | 9 | 9 | 8 | 10 | **89.5** |
| H Matheuristic + exact repair | 60.0 | 25.0 | 2 | 7 | 8 | 8 | 7 | 9 | **85.0** |
| F CP-SAT-centric | 61.0 | 21.5 | 2 | 7 | 7 | 7 | 6 | 7 | 82.5 |
| G Pure ALNS | 57.0 | 24.0 | 2 | 7 | 8 | 8 | 8 | 8 | 81.0 |
| I Column generation | 50.0 | 29.0 | 2 | 9 | 10 | 10 | 9 | 10 | 79.0 |
| C Integrated node-arc MILP | 55.0 | 23.0 | 2 | 9 | 7 | 9 | 9 | 9 | 78.0 |
| J Benders | 47.0 | 28.0 | 2 | 9 | 10 | 10 | 10 | 10 | 75.0 |
| B Time-expanded MILP | 47.0 | 21.0 | 2 | 9 | 8 | 9 | 9 | 8 | 68.0 |
| K Pure GA/NSGA-II | 47.0 | 18.0 | 2 | 6 | 7 | 7 | 8 | 7 | 65.0 |
| A Monolithic MINLP | 38.0 | 23.0 | 2 | 10 | 10 | 10 | 10 | 9 | 61.0 |
| L RL/GNN | 29.0 | 14.0 | 9 | 9 | 10 | 10 | 10 | 7 | 43.0 |

这里的数据难度低分表示容易，高分表示困难。

**最需要注意的淘汰结论是：**

- CP-SAT 没被否定；它只是**更适合成为 scheduler 子模块**。
- ALNS 没被否定；它更适合成为**route improvement / destroy-repair 模块**。
- Column generation 和 Benders 不是能力不足，而是**机会成本过高**。
- NSGA-II 不是“落后”，而是**当前问题和剩余时间不匹配**。
- RL/GNN 是最不应该被“AI 高级感”诱惑的方向。

## 最终前三完整方案与正面对比

**第九章｜最终 TOP 3**

### TOP 1：候选架次生成 + 分层精确调度 + DEM Relay Decomposition

**获奖适配评分：93.0/100**

- 保二等奖稳健性：66/70
- 冲一等奖上限：27/30

#### 为什么第一

因为它把难度最大的几个连续/组合问题切在了正确边界上：

\[
\boxed{
\text{Physics/GIS}
\rightarrow
\text{Feasible objects}
\rightarrow
\text{Discrete optimization}
\rightarrow
\text{Independent verification}
}
\]

而不是让求解器重新“发现”物理规律。

最大风险：Q3 relay candidate 和 transport adjustment 之间可能需要数轮迭代。

#### Q1

**模型：Feasible-subset enumeration + Set Partitioning MILP**

集合：

\[
I=\{1,\ldots,15\},\quad
K_i=\text{服务区 }i\text{ 的箱子},
\quad
G=\{A,B,C\}.
\]

对于每个 \(i,g\) 枚举：

\[
S\subseteq K_i.
\]

若同时满足重量、体积、energy reserve，则产生一个 column \(c=(i,g,S)\)。

变量：

\[
x_c\in\{0,1\}.
\]

箱子唯一覆盖：

\[
\sum_{c:k\in S_c}x_c=1
\qquad\forall k.
\]

Lexicographic：

\[
\min F_1=\sum_c x_c
\]

\[
\min F_2=\sum_c E_cx_c
\]

\[
\min F_3=\sum_c T_cx_c.
\]

最大安全载荷则独立求：

\[
q^*_{ig}
=
\max\{q:
E_{Oi}(q)+E_{iO}(0)
\le(1-\rho_g)E_g^{use}\}.
\]

**算法：**

- 连续载荷：一维 root/bisection；
- subset：DFS enumeration；
- master：Gurobi MILP；
- 若 \(n_i\) 大，剪枝或直接 DP/MILP。

**输出：**模板 Q1 全部字段。

**Baseline：**weight-first First Fit / Best Fit。

**Sensitivity：**

\[
\rho_g
\]

为题目明确要求的必做参数。

建议至少展示：

- \(q^*_{ig}(\rho)\)；
- sorties 数；
- energy；
- model mix。

#### Q2

**模型：Feasible sortie pool + Set Partitioning + Resource Scheduling**

候选 sortie：

\[
p=
(g,\,
K_p,\,
(i_1,\ldots,i_m)).
\]

为每条 sortie 预计算：

\[
T_p,\quad E_p,\quad
\delta_{pk},
\]

其中 \(\delta_{pk}\) 是箱 \(k\) 从 sortie 开始到交付完成的相对时间。

选择变量：

\[
y_p\in\{0,1\}.
\]

箱子覆盖：

\[
\sum_{p:k\in K_p}y_p=1.
\]

开始时间：

\[
s_p\ge0.
\]

逐箱送达：

\[
D_k=s_p+\delta_{pk}.
\]

医疗/首批硬时间约束：

\[
D_k\le d_k^{hard}.
\]

普通物资 tardiness：

\[
T_k^{late}\ge D_k-d_k^{exp},
\]

\[
T_k^{late}\ge0.
\]

每个选中 sortie 分配：

\[
a_{pu}\in\{0,1\},
\quad
b_{pb}\in\{0,1\}.
\]

实体无人机：

\[
\sum_{u\in U_g}a_{pu}=y_p.
\]

电池：

\[
\sum_{b\in B_g}b_{pb}=y_p.
\]

然后把每条任务生成 interval：

\[
I_p=[s_p,s_p+T_p].
\]

同一 physical UAV 上：

\[
NoOverlap(I_p:a_{pu}=1).
\]

对电池 \(b\)，其不可复用区间应扩展为：

\[
I^{battery}_p
=
[s_p,\;e_p+t^{chg}(SOC^{end}_p)].
\]

同一电池：

\[
NoOverlap(I^{battery}_p:b_{pb}=1).
\]

**研究建议：**route selection 用 Gurobi，资源时序用 CP-SAT；若希望减少接口复杂度，可以先全部 Gurobi，CP-SAT 作为 infeasibility repair。

OR-Tools 的 interval/no-overlap 与这一资源结构高度匹配。citeturn16search0

多目标：

第一层：

\[
\min
\sum_{k\in K^{ordinary}}
\alpha_k
\frac{T_k^{late}}{d_k^{exp}}
\]

第二层：

\[
\min C_{\max},
\quad
C_{\max}\ge s_p+T_p.
\]

第三层：

\[
\min \sum_pE_py_p.
\]

第四层：

\[
\min \sum_py_p.
\]

【研究推断】不要把“架次数最少”置于及时性前面。灾害物流里，为了减少一次 sortie 而让救援物资明显晚到，没有合理现实解释。

#### Q3

这里是 TOP 1 最有竞争力的部分。

**先从 Q2 方案作为 warm start，而不是冻结它。**

第一步，得到每条 transport trajectory：

\[
\mathbf x_p(t).
\]

第二步，直接对 G01 计算：

\[
A_{p0}(t)\in\{0,1\}.
\]

提取 maximal uncovered intervals：

\[
\mathcal U_p
=
\{[a_{p1},b_{p1}],\ldots\}.
\]

第三步，生成 relay candidate set：

\[
R^c=
R_{\rm grid}
\cup
R_{\rm ridge}
\cup
R_{\rm shadow}
\cup
R_{\rm service}
\cup
R_{\rm refined}.
\]

建议候选来源：

- coarse DEM grid；
- 服务区附近；
- transport shadow interval 中点附近；
- LOS blocker 对应山脊/高点；
- direct-link feasible/infeasible boundary；
- 被选候选周围局部细化。

海拔候选：

\[
z_r=H_{\rm DEM}(x_r,y_r)+h_r,
\quad
0<h_r\le300m.
\]

不要一开始把所有 DEM 像元 × 所有高度全部作为候选。

第四步，预计算 sparse coverage matrix：

\[
A_{pr\ell}
=
1
\]

表示 relay candidate \(r\) 在 transport interval/sample \(\ell\) 同时满足：

\[
\text{Transport}\leftrightarrow r
\]

和

\[
r\leftrightarrow G01.
\]

第五步，生成 relay sortie option

\[
\omega=(r,t^{start},t^{serve-start},t^{serve-end}),
\]

包含：

- 出发；
- 飞抵；
- 建链；
- hover/service；
- return；
- energy。

变量：

\[
z_\omega\in\{0,1\}.
\]

对每个通信需求 interval element：

\[
A_{p0\ell}
+
\sum_\omega A_{p\ell\omega}z_\omega
\ge1.
\]

再对 relay UAV 和 energy component 建 NoOverlap / recharge 约束。

若 relay subproblem 不可行或代价很高：

\[
\text{conflict interval}
\rightarrow
\text{Q2 route/start-time repair}.
\]

修复邻域包括：

- shift sortie start time；
- swap service sequence；
- split multi-stop sortie；
- merge compatible boxes；
- replace route with alternative pool member。

这就实现了：

\[
Q2
\rightarrow
Q3\ relay
\rightarrow
transport\ repair
\rightarrow
relay
\]

的 **transportation-relay iterative joint optimization**。

它比“Q2 冻结后补中继”强得多，又比 monolithic joint MINLP 稳得多。

#### 连续通信最终 Validator

禁止仅检查轨迹节点。

正式 checker 应：

1. 对 climb/cruise/descent/handover 分段；
2. 插入所有 phase boundary；
3. 对通信射线穿过的 DEM cells 做 raster traversal；
4. 检查 line altitude 与 terrain；
5. 对 transport motion 做 adaptive subdivision；
6. 对任何 link margin 接近 0 的区间继续细分；
7. 最后独立重新计算双向 FSPL + obstruction。

【待实验验证】优化阶段可以用较粗采样；最终 verifier 推荐把水平采样尺度压到明显小于 30 m DEM 像元，例如 5–10 m 等级，并在通信状态变化附近递归细化。这个数值不是官方规定，因此最终论文应写成“验证精度设置”，并做 sampling-density convergence experiment，而不能声称其有官方含义。

更漂亮的做法是同时报告：

\[
\Delta_{\min}^{link}
=
\min_t
\left(
L^{bi}_{max}-L^{tot}(t)
\right),
\]

作为最小链路余量。

如果只报告“通信率 100%”，评审不知道你离断链有多近。

#### Q4

构造 must-link graph。

若 transport sortie \(p\) 服务集合

\[
S_p=\{i_1,\ldots,i_m\},
\]

则：

\[
g(i_1)=\cdots=g(i_m).
\]

先用 union-find 收缩成 components：

\[
C_1,\ldots,C_M.
\]

由于

\[
M\le15,
\]

对于 \(K=2,3\)，完全可以枚举可行 component assignments，并使用 symmetry breaking：

- 固定 \(C_1\) 在 group 1；
- group labels 按最小服务区编号排序。

对每个 partition \(P\)，**不重新优化 Q3 任务**，只 replay 对应 group 的 fixed task timeline，然后求：

\[
R^{transport}_{Pg},
R^{battery}_{Pg},
R^{relay}_P,
R^{component}_P.
\]

目标优先级：

\[
\min F_1=\text{inventory deficit},
\]

\[
\min F_2=\text{total duplicated resources},
\]

\[
\min F_3=\text{workload imbalance}.
\]

资源缺口：

\[
Gap_m
=
\max
\left(
0,\;
\sum_{j=1}^{K}R_{jm}-Inventory_m
\right).
\]

**Q4 一个需要 GPT-6 Pro 最终裁决的语义点：**

题面显式规定了“同一 transport sortie 内服务区必须同组”，但如果**同一固定 relay sortie 同时/连续保障了属于不同 transport sorties 的多个服务区**，是否也应把它们视为隐含 must-link？

从“保持中继任务和通信保障关系不变、组间资源不得调配”看，我倾向于：

> 建立第二层 task-dependency hypergraph，把共享同一不可拆 relay task 的运输任务也绑定。

这是【研究推断】，不是题面直接写出的 must-link。正式代码应把这一规则做成配置开关，并在论文解释。

#### TOP 1 风险评分

| 风险项 | 分数 /10 | 原因 |
|---|---:|---|
| 模型难度 | 7 | 四层模型，但边界清楚 |
| 算法难度 | 7 | route generation + 两种 solver + repair |
| 代码难度 | 7 | 模块多但可拆分测试 |
| 数据处理难度 | 6 | DEM/坐标是主要工作 |
| 外部数据查找难度 | **1** | 不需要 |
| GIS 难度 | 7 | raster traversal + LOS |
| 调试风险 | 6 | validator 能显著压风险 |
| 求解时间风险 | 5 | 可控制 candidate pool |
| 论文写作难度 | 6 | 叙事自然 |

### TOP 2：Route–Relay Pattern 联合集合划分

**获奖适配评分：89.5/100**

- 保二等奖：61/70
- 冲一等奖：28.5/30

TOP 2 的思想更激进：

> 不先选 transport route 再寻找 relay，而是在生成 transport route 时直接产生与它兼容的一组通信保障 pattern。

定义：

\[
p\in\mathcal P
\]

运输架次；

\[
\omega\in\Omega_p
\]

是其一套通信保障方案：

\[
\omega=
(\text{direct intervals},
\text{relay candidate(s)},
\text{relay service intervals},
\text{energy}).
\]

联合 column：

\[
c=(p,\omega).
\]

变量：

\[
x_{p\omega}\in\{0,1\}.
\]

箱覆盖：

\[
\sum_{p,\omega:k\in K_p}
x_{p\omega}=1.
\]

从而 Q3 的“运输 + 通信”在 master 中天然联合。

资源排程仍对：

- transport UAV；
- transport battery；
- relay UAV；
- relay energy component

进行同步。

#### Q1

与 TOP 1 相同，仍采用 enumeration + set partitioning。

不要为了“方案不同”故意把已经正确的 Q1 换成较差算法。

#### Q2

预先生成 pure transport columns，master set-partitioning。

#### Q3

从 pure route columns 扩展成 joint columns。

最大的理论优势是：

\[
c_{p\omega}
=
c_p^{transport}
+
c_\omega^{relay},
\]

master 可以直接在运输代价和通信代价之间权衡，而不是迭代 repair。

这比 TOP 1 更接近真正的联合有限优化。

#### Q4

仍然从最终 joint columns 恢复 transport/relay dependency graph，并精确枚举分区。

#### 为什么不排第一

因为 pattern 数可能从：

\[
|\mathcal P|
\]

膨胀成：

\[
\sum_{p\in\mathcal P}|\Omega_p|.
\]

如果一条 transport route 有多个盲区，每个盲区有多个 relay candidate，组合数会快速增长。

必须进行 dominance：

若两个 relay pattern \(\omega_1,\omega_2\) 覆盖完全相同，而：

\[
E_{\omega_1}\le E_{\omega_2},\quad
T_{\omega_1}\le T_{\omega_2},
\]

则删除 \(\omega_2\)。

还可以限制每个 uncovered interval 只保留 top-\(k\) relay alternatives。

#### 算法

- DFS / LNS transport route generation；
- DEM relay candidate preprocessing；
- pattern generation；
- dominance pruning；
- Gurobi Set Partitioning MILP；
- CP-SAT optional interval 做资源排程。

如果进一步上 column generation，理论深度更强，但我明确**不建议比赛中现在再实现 pricing**。

#### TOP 2 风险评分

| 风险项 | 分数 /10 | 原因 |
|---|---:|---|
| 模型难度 | 9 | route-relay column 设计复杂 |
| 算法难度 | 9 | pattern generation/pruning |
| 代码难度 | 9 | 数据结构复杂 |
| 数据难度 | 6 | 与 TOP1 相同 |
| 外部数据 | 1 | 无需 |
| GIS | 8 | preprocessing 更重 |
| 调试风险 | 8 | pattern correctness 难查 |
| 求解时间风险 | 8 | column explosion |
| 论文难度 | 8 | 写好很强，写坏很乱 |

**最大价值：**如果 TOP 1 已经跑通，TOP 2 的“joint pattern”思想可以作为一等奖增强，而不是整套重写。

### TOP 3：ALNS/LNS Matheuristic + Exact Repair

**获奖适配评分：85.0/100**

- 保二等奖：60/70
- 冲一等奖：25/30

这个架构更偏 anytime：

方案编码保存：

\[
X=
(\text{box batching},
\text{routes},
\text{start-order}).
\]

ALNS 采用 destroy operators：

- random boxes；
- worst-tardiness boxes；
- one service area；
- one route；
- communication-critical route；
- energy-critical route；
- battery-conflict routes。

Repair operators：

- cheapest insertion；
- EDF insertion；
- energy-aware insertion；
- communication-aware insertion；
- regret-2 / regret-3；
- route split；
- route merge。

但每一次候选方案**不由 penalty 判断是否满足所有硬约束**，而是调用 exact feasibility oracle：

\[
\text{Route solution}
\rightarrow
\text{CP-SAT battery/UAV schedule}
\rightarrow
\text{relay MILP}.
\]

无法修复就拒绝。

这就是它和“pure ALNS”的本质区别。

2025 年 ESWA 的动态 truck–drone matheuristic 正是因为同步约束复杂而采用数学规划和启发式结合，这为这种架构提供了较强文献依据。citeturn23search2

#### Q1

仍用 exact subset enumeration。

#### Q2

ALNS 搜索 route/batch；CP-SAT 精确分配 physical UAV / battery / start time。

#### Q3

通信-aware destroy/repair：

- 优先拆掉盲区时间最长的 route；
- 改变 route sequence；
- 移动开始时间；
- 把通信困难点拆成单点 sortie。

每次 route 变化后只增量重算相关通信轨迹。

Relay assignment 仍为小 MILP/CP-SAT。

#### Q4

Q4 不用启发式。

15 个节点太小，仍精确枚举。

#### 优势

它可以随时停止并返回当前 best feasible solution。

这在比赛现场极其重要。

#### 缺点

无法像 MILP master 那样自然给出全局 lower bound/gap。

所以论文中必须加入：

- Q1 exact baseline；
- 小型 Q2 restricted MILP；
- TOP1-style exact schedule comparison；

证明 ALNS 的方案质量不是拍脑袋。

#### TOP 3 风险评分

| 风险项 | 分数 /10 | 原因 |
|---|---:|---|
| 模型难度 | 7 | exact backbone 仍清晰 |
| 算法难度 | 8 | neighborhoods 较多 |
| 代码难度 | 8 | incremental evaluation 容易 bug |
| 数据难度 | 6 | GIS 相同 |
| 外部数据 | 1 | 无需 |
| GIS | 7 | 同 TOP1 |
| 调试风险 | 7 | operator 交互复杂 |
| 求解时间风险 | **4** | anytime |
| 论文难度 | 7 | 必须充分做 algorithm comparison |

**第十章｜Top 3 正面对比**

| 指标 | TOP 1 | TOP 2 | TOP 3 |
|---|---|---|---|
| Q1 | subset enumeration + SP-MILP | 同 TOP1 | 同 TOP1 |
| Q2 | route pool + MILP/CP schedule | route-column master | ALNS + exact scheduler |
| Q3 | candidate relay + iterative coupling | joint route-relay pattern master | communication-aware ALNS + relay subsolver |
| Q4 | must-link supernode enumeration | dependency-graph enumeration | dependency-graph enumeration |
| 理论深度 | 高 | **最高** | 高 |
| 可解释性 | **最高** | 高 | 中高 |
| 最优性信息 | 有 restricted gap/bounds | **最好** | 较弱 |
| 开发时间 | 中 | **最长** | 中高 |
| Debug 风险 | **最低** | 最高 | 中高 |
| GIS 难度 | 高 | 高 | 高 |
| 求解时间风险 | 中 | 高 | **较低/anytime** |
| 保二稳健性 | **最高** | 中高 | 高 |
| 冲一上限 | 高 | **最高** | 高 |
| 适合当前时间 | **是** | 仅已有强代码底座时 | 是，适合作备用 |
| 推荐角色 | **主方案** | 增强方案 | 紧急/高质量备用 |

我的最终判断没有歧义：

> **实际参赛应先做 TOP 1。**

然后从 TOP 2 吸收“joint route-relay pattern / dominance”思想，从 TOP 3 吸收 ALNS repair operators。

这比选一个纯粹路线更强：

\[
\boxed{
\text{TOP1 backbone}
+
\text{TOP2 joint-pattern insight}
+
\text{TOP3 LNS repair}
}
\]

但论文中仍应讲成一套统一方法，不能写成算法大杂烩。

## 论文骨架与代码工程

**第十一章｜推荐论文骨架**

该目录不是你原始模板的复制，而是按照工程优化题应有的论证结构重新组织。

**摘要**

写：

- 核心冲突；
- 每问模型；
- 核心算法；
- 最主要结果指标；
- 验证方式；
- 一到两个创新点。

不能写：

- Python 库列表；
- 大段背景；
- “建立若干模型取得良好效果”这种空话。

**问题重述与建模目标**

- 场景；
- 四问逻辑；
- 输出目标。

**问题分析与总体技术路线**

这里先画一张全题框图：

\[
\text{数据}
\rightarrow
\text{统一物理}
\rightarrow
Q1
\rightarrow
Q2
\rightarrow
Q3
\rightarrow
Q4
\rightarrow
Validator.
\]

单独强调：

- Q1 不是 Q2 的硬冻结前驱；
- Q3 可以修改 Q2；
- Q4 完全继承 Q3。

**模型假设与符号**

只保留真正需要的假设。

不要写“假设数据真实可靠”这种废话。

**场景数据处理与统一物理模型**

建议细分：

- 地理坐标与 DEM 栅格；
- 航段地形净空与三阶段飞行；
- 载荷递减与能耗；
- 作业/周转时间；
- SOC 与两阶段充电；
- 三维 LOS；
- 双向链路预算；
- 公共可行性计算接口。

这是整篇论文最应该前置统一的一章。

**单点运输能力与精确组批**

- 最大安全载荷；
- feasible subset；
- set partitioning；
- 结果；
- reserve sensitivity。

**异构多架次运输与能源资源协同调度**

- candidate sortie 定义；
- route feasibility；
- master model；
- physical UAV/battery schedule；
- 多目标优先级；
- final routes；
- Gantt/SOC；
- baseline。

**地形约束下运输—中继协同调度**

这一章是论文核心。

结构建议：

- 直连盲区识别；
- 中继候选点生成；
- trajectory-to-relay coverage matrix；
- relay sortie model；
- transport-relay decomposition；
- iterative repair；
- continuous communication verification；
- final joint solution。

**固定任务条件下的任务分区与独立资源配置**

- dependency graph；
- must-link connected components；
- 2-way/3-way exact partition；
- group resource replay；
- deficit/redundancy/balance；
- comparison。

**模型检验与算法实验**

不要放一堆无关敏感性。

重点：

- physics unit validation；
- feasibility validator；
- baseline；
- route generation ablation；
- relay candidate density；
- communication sampling convergence；
- battery number；
- reserve；
- objective trade-off；
- runtime/gap。

**模型评价与推广**

优点：

- 统一物理；
- 强可验证；
- 分解降低组合规模；
- DEM-aware；
- Q4 exact。

不足：

- relay continuous placement 离散化；
- 默认确定性天气；
- DEM 分辨率限制；
- 未考虑风场；
- 通信只按题面 FSPL+terrain loss。

不要声称不存在的“现实全局最优”。

**参考文献**

优先放：

- 题面官方参考；
- IEEE；
- Transportation Research；
- Omega；
- C&OR；
- ESWA；
- OR-Tools/Gurobi 文档仅在需要说明软件机制时引用。

**附录**

放：

- 算法伪代码；
- 参数表；
- validator 输出；
- 完整结果表；
- AI/程序来源声明。

【官方确定】2026 开赛公告要求引用程序、AI 工具和文献必须明确注明来源，并会进行查重；附件可在规定时段上传，压缩包大小限制 50 MB。citeturn26search0

### 真正值得画的图

不建议把 19 张候选图全部塞进去。

优先级最高的是：

1. **DEM + O01 + 服务区 + Q2/Q3 路径总图**
2. **Q1 最大安全载荷 vs 服务区/机型**
3. **返航安全余量 sensitivity**
4. **Q2 physical UAV 甘特图**
5. **Q2 battery/charging 甘特图**
6. **关键电池 SOC 曲线**
7. **逐箱交付时刻 / deadline 图**
8. **Q3 直连盲区 + relay positions**
9. **transport-relay 协同甘特图**
10. **communication status timeline**
11. **Q4 2-group / 3-group 地图**
12. **资源配置/缺口比较图**
13. **1 张核心 Pareto/ε-constraint trade-off 图**

可以砍掉：

- 与模型无关的 3D 炫图；
- 每个服务区单独一张路线；
- 大量重复 SOC 图；
- 无结论的散点图。

**第十二章｜代码工程建议**

建议代码树：

```text
project/
├── config/
│   ├── constants.py
│   └── paths.py
├── data/
│   ├── loader.py
│   ├── schemas.py
│   └── integrity_check.py
├── geo/
│   ├── terrain.py
│   ├── raster_trace.py
│   └── coordinates.py
├── physics/
│   ├── flight.py
│   ├── energy.py
│   ├── charging.py
│   └── communication.py
├── precompute/
│   ├── segment_cache.py
│   ├── trajectory.py
│   ├── relay_candidates.py
│   └── coverage_matrix.py
├── q1/
│   ├── payload.py
│   ├── subsets.py
│   └── model.py
├── q2/
│   ├── route_generation.py
│   ├── master.py
│   └── scheduler.py
├── q3/
│   ├── direct_coverage.py
│   ├── relay_options.py
│   ├── relay_model.py
│   └── transport_repair.py
├── q4/
│   ├── dependency_graph.py
│   ├── resource_replay.py
│   └── partition.py
├── validators/
│   ├── q1_validator.py
│   ├── q2_validator.py
│   ├── q3_validator.py
│   └── q4_validator.py
├── visualization/
├── export/
│   └── result_template.py
├── tests/
└── main.py
```

### 最重要的工程原则

**只有一套 `physics/`。**

禁止：

```text
q1_energy()
q2_energy()
q3_energy()
```

分别各写一次公式。

必须：

```text
physics.energy.evaluate_segment(...)
physics.flight.evaluate_route(...)
```

所有问题调用同一函数。

### Optimizer 与 Validator 相对独立

不是复制两遍物理公式，而是：

- optimizer 可以用 cached matrices；
- validator 从 raw objects 重新调用 canonical physics；
- validator 不信任 optimizer 的 `feasible=True` 标志。

例如优化器输出：

```text
route_id = P138
energy = 2.31
```

validator 应重新从：

```text
box list
route nodes
DEM
aircraft type
```

计算 2.31，而不是读取缓存的 2.31。

### Q1 Validator

检查：

\[
\text{each box count}=1
\]

以及：

- 服务区对应；
- weight；
- volume；
- exact route energy；
- return reserve。

### Q2 Validator

检查：

- 全部 80 箱且唯一；
- route sequence；
- delivery time；
- hard deadlines；
- UAV intervals；
- battery compatibility；
- battery task overlap；
- charging overlap；
- recharge-to-100；
- sortie energy；
- makespan。

### Q3 Validator

在 Q2 基础上加入：

- full trajectory；
- direct link；
- relay access；
- relay backhaul；
- simultaneous availability；
- relay UAV occupation；
- relay component occupation；
- relay energy/SOC；
- hover AGL；
- DEM extent；
- communication intervals；
- minimum link margin。

### Q4 Validator

检查：

- 15 服务区唯一分组；
- 非空组；
- transport sortie must-link；
- relay dependency interpretation；
- fixed Q3 tasks；
- group isolation；
- resource peak；
- inventory gap。

### 软件选择

**推荐主栈：**

- Python；
- pandas / numpy；
- rasterio；
- pyproj；
- shapely；
- networkx；
- Gurobi；
- OR-Tools CP-SAT；
- matplotlib。

Gurobi 支持 hierarchical multi-objective 和 IIS infeasibility diagnosis，非常适合 master MILP 和 debug。citeturn15search2turn15search5

CP-SAT 适合 interval scheduling，但需要整数化。citeturn15search8turn16search0

HiGHS 能解决 LP/MILP，采用 branch-and-cut，并且开源 MIT；可以作为 Q1/set-partitioning 和部分 Q2 master 的无 Gurobi 备用，但它没有 CP-SAT 那种专门的 scheduling interval 表达。citeturn15search0

**无 Gurobi 备用：**

\[
\text{HiGHS}
+
\text{OR-Tools CP-SAT}.
\]

**GPU：不需要。**

这题的瓶颈是：

- combinatorial optimization；
- DEM raster operations；
- MILP/CP；
- LOS preprocessing。

现代多核 CPU 足够。GPU 不应该成为默认工程依赖。

## 实验设计、时间方案与止损条件

**第十三章｜实验设计**

### Baselines

**Q1**

FFD/BFD：

- weight descending；
- first/best feasible sortie。

对比：

- sorties；
- energy；
- time。

**Q2**

Greedy baseline：

\[
\text{EDF}
+
\text{nearest next service}
+
\text{earliest available compatible UAV/battery}.
\]

对比：

- hard deadline violations；
- ordinary tardiness；
- makespan；
- energy；
- sorties；
- battery utilization。

**Q3**

Baseline：

> Q2 完全冻结 + 对每个 uncovered interval 选择最近/最低能耗 feasible relay。

正式方案则允许 transport repair。

这会直接展示“联合优化”的价值。

**Q4**

baseline：

- 先满足 must-link；
- 再按 service centroid / workload greedy balance。

与 exact enumeration 比：

- deficit；
- duplicated resources；
- workload imbalance。

### Ablation

最值得做的只有四个：

**Ablation A**

无 payload-dependent energy  
vs  
完整载荷递减。

用于证明官方物理规则的重要性。

**Ablation B**

transport-first frozen  
vs  
transport-relay iterative repair。

这是一等奖创新最重要的实验。

**Ablation C**

uniform relay grid  
vs  
DEM/shadow adaptive candidates。

证明 candidate reduction 不是拍脑袋。

**Ablation D**

不建模 battery charging  
vs  
完整共享电池/SOC scheduling。

这能展示一个“看起来可行、实际上资源不可行”的方案。

### 必做敏感性

题目明确要求：

\[
\rho=\text{return reserve}.
\]

额外最值得做：

- battery quantity；
- relay component quantity；
- relay candidate density；
- communication margin；
- relay altitude；
- ordinary timeliness priority；
- \(\varepsilon\)-constraint makespan/energy bound。

不值得大量做：

- GA mutation rate；
- 15 个 ALNS 参数逐个敏感性；
- 与题意无关的 DEM 平滑系数。

### 多目标实验

正式解用 lexicographic。

另外围绕最佳及时性 \(F_1^*\) 做：

\[
F_1\le F_1^*(1+\epsilon),
\]

分别取若干 \(\epsilon\)，优化 energy/makespan。

这样可以画一张：

\[
\text{timeliness vs energy}
\]

或

\[
\text{makespan vs energy}
\]

的 frontier。

它比权重从 0.1 调到 0.9 更容易解释。

### 运行时间与规模预算

以下不是虚构实测值，而是【工程预算/止损阈值】。

**Q1**

目标：

- feasible subset 数量控制在 \(10^3\)–\(10^4\) 量级；
- 5 分钟内应完成。

如果单服务区：

\[
n_i>18
\]

或 subset 数超过约 \(10^5\)，立即停止全枚举，切换 branch-and-bound/DP。

**Q2**

建议最终 pool：

\[
2\times10^3
\sim
2\times10^4
\]

条 dominated-pruned sorties。

Restricted master 单轮求解给 30–60 min time limit 即可，不需要为了 0.00% gap 卡几个小时。

**Q3**

relay 3D candidates 初始尽量控制在：

\[
200\sim800
\]

量级。

如果超过约 1500，先做：

- backhaul infeasibility pruning；
- route relevance pruning；
- dominance pruning；
- adaptive refinement。

不要直接把 DEM 的全部约两百万像元 × 多个高度塞进去。审计报告显示原始 DEM 约为 \(1486\times1309\) 栅格，直接全空间候选化显然不合理。fileciteturn0file1

**Q4**

至多 15 个服务区，2-way 全二元组合数量本来就很小；3-way 若以 labeled group 粗算也只是 \(3^{15}\) 级别，在 must-link、非空和 symmetry breaking 后会大幅减少。

因此 Q4 没有任何理由上 GA。

### Feasibility 报告

建议程序最后自动生成：

```text
Q1_VALID = TRUE
Q2_VALID = TRUE
Q3_VALID = TRUE
Q4_K2_VALID = TRUE
Q4_K3_VALID = TRUE
```

并输出：

```text
boxes_missing = 0
boxes_duplicated = 0
deadline_violations = 0
drone_overlap = 0
battery_overlap = 0
charging_conflicts = 0
communication_outage_duration = 0
relay_resource_conflicts = 0
q4_mustlink_violations = 0
```

这种附录对“保二”价值远大于再加一个算法名称。

**第十四章｜剩余比赛时间执行方案**

【官方确定】竞赛 9 月 27 日 12:00 截止，组委会建议不要卡最后时刻提交 MD5。citeturn19search0turn26search3

以本次检索时刻计算，剩余约 91 小时。

### P0：必须完成

**现在起约 8 小时**

只做：

- 数据加载；
- schema；
- DEM 查询；
- raster segment；
- flight；
- energy；
- charging；
- communication；
- template exporter；
- unit tests。

如果这个阶段没有完成，后面所有优化都不可信。

### P0：随后约 10 小时

完成 Q1：

- safe payload；
- exact batching；
- reserve sensitivity；
- Q1 validator；
- Q1 图表。

Q1 不应该拖一天。

### P0：随后约 20 小时

完成 Q2 **第一个完整可行方案**。

优先级：

\[
\text{Feasible}
>
\text{Good}
>
\text{Optimal}.
\]

必须先得到：

- 80 箱全送达；
- hard deadlines；
- UAV；
- battery；
- charging 全可行。

此时不要追 0.1% energy 改善。

### P0：随后约 20 小时

完成 Q3：

先做：

1. Q2 全轨迹 direct check；
2. 找 blind intervals；
3. coarse relay candidates；
4. 一定要获得一个完整 relay-feasible solution；
5. q3 validator。

只有在出现第一份 **communication outage = 0** 的结果后，才允许优化。

### P0：随后约 8 小时

完成 Q4：

- must-link components；
- exact 2/3 group enumeration；
- resources；
- gaps；
- validator。

### P1：随后约 12 小时

提升：

- transport-relay repair；
- better route pool；
- battery schedule；
- relay candidate refinement；
- baselines。

### P1：随后约 8 小时

实验：

- reserve；
- battery；
- relay density；
- objective trade-off；
- ablation。

### P0：最后至少 5 小时

只做：

- independent validation；
- 表格；
- template；
- figures；
- PDF；
- 引用；
- AI 声明；
- MD5 freeze。

**最后数小时绝对禁止重构核心代码。**

### 三人分工建议

**成员 A：物理/GIS/Validator**

负责：

- DEM；
- flight；
- energy；
- comm；
- validator。

**成员 B：Optimization**

负责：

- Q1；
- Q2 route/master；
- Q3 relay；
- Q4。

**成员 C：论文/实验/Exporter**

不是“只写论文”。

应同时负责：

- result consistency；
- baseline；
- sensitivity；
- figures；
- Excel；
- 文献；
- 主动审查逻辑漏洞。

**第十五章｜Stop-Loss**

### TOP 1 止损

**Q1**

如果 2 小时后还没有可信的 safe-payload 表：

> 立即停止任何 Q2 开发，修物理模型。

因为错误会向后污染三问。

**Q2**

如果开始写 Q2 后 **4 小时仍得不到一个 80 箱完整可行 route set**：

立即缩减问题：

- 先允许单点/双点 sortie；
- greedy 生成 route；
- CP-SAT 调度；
- 暂停 sophisticated route search。

如果仍无解，重点查：

- 医疗 deadline；
- service time；
- energy formula；
- battery recharge；
- 时间单位。

不要第一反应是“算法不够高级”。

**Q2 route pool**

若：

\[
|\mathcal P|>20,000
\]

且 master 明显变慢：

- dominance；
- 每箱/服务区只保留 top alternatives；
- 截断高代价 route；
- incremental generation。

**Q3**

如果 relay candidates 超过约 1500：

> 停止增点，先 prune。

如果 coverage matrix 达到数百万以上 dense entries：

> 改 sparse interval representation。

如果 **3 小时后还没有 communication-feasible Q3**：

按以下顺序降级：

1. 冻结当前 Q2；
2. 对盲区直接配置 relay；
3. 允许 route start shift；
4. split communication-hard routes；
5. 再求 relay。

不要继续调 MILP 参数。

如果两个 transport-relay repair cycle 后没有明显改善：

> 停止迭代，保留当前 best feasible solution。

### TOP 2 止损

如果 route-relay patterns：

\[
>100,000
\]

或生成超过约 2 小时：

> **立即退回 TOP 1。**

如果 joint master 30 分钟没有高质量 incumbent：

> 不再调 branch strategy，退回 TOP1。

如果你们此刻还没写 pattern generator：

> **现在不要选 TOP 2 主线。**

### TOP 3 止损

如果 ALNS：

- 一小时内没有稳定优于 greedy baseline；
- feasible solution ratio 很低；
- repair solver 成为绝大部分运行时间；

则停止调 neighborhood weights。

退回：

\[
\text{deterministic route pool + MILP/CP}.
\]

如果跑一万个 neighborhood moves 仍频繁出现资源 infeasibility：

> 问题不是“ALNS 迭代不够”，而是编码与 repair architecture 有问题。

### 最终总止损

比赛剩余约 **24 小时时**：

> 禁止引入任何新的算法体系。

剩余约 **12 小时时**：

> 禁止改变物理口径和核心数据 schema。

剩余约 **6 小时时**：

> 只允许 validator 修 bug、输出修复、论文一致性修正。

剩余约 **2 小时时**：

> 禁止优化结果，锁定版本。

这是稳住全国二等奖最重要的工程纪律之一。

## GPT-6 Pro 技术路线决策输入

**第十六章｜《GPT-6 Pro 技术路线决策输入》**

### 题目核心

确定性山区灾害无人机优化问题。

核心不是单独 VRP，而是：

\[
\boxed{
\text{indivisible cargo}
+
\text{heterogeneous multi-trip routing}
+
\text{physical UAV scheduling}
+
\text{battery charging}
+
\text{DEM-based flight}
+
\text{continuous communication}
+
\text{relay placement/scheduling}
+
\text{fixed-plan partition}
}
\]

### 官方硬约束

【官方确定】

- O01 + 15 服务区；
- 80 不可拆箱；
- Q1 sortie 只能 O01→Si→O01；
- Q2/Q3 可多服务区；
- 航段水平直线；
- cruise altitude = max traversed DEM +50 m；
- 服务区 +30 m 作业；
- 多点每次重新爬升；
- payload-dependent energy；
- return reserve；
- 8 physical transport UAV；
- shared compatible batteries；
- battery SOC + two-stage charging；
- medical expected time；
- first-batch hard deadlines；
- continuous communication；
- direct G01 or single relay；
- no relay-relay multihop；
- 3D terrain LOS；
- bidirectional link budget；
- relay UAV + component + charging；
- Q4 freezes Q3 tasks/relations；
- same transport sortie service zones must be same group。fileciteturn0file0

### 数据规模

【审计报告确定】

\[
|S|=15,\quad|K|=80.
\]

Transport UAV：

\[
A/B/C=4/2/2.
\]

Battery：

\[
6/4/4.
\]

Relay：

\[
2.
\]

Relay components：

\[
6.
\]

DEM：

\[
1486\times1309
\]

约 30 m resolution。fileciteturn0file1

### TOP 1

**架构**

\[
\text{Unified Physics}
\rightarrow
Q1\ Enumeration+SP
\rightarrow
Q2\ RoutePool+MILP/CP
\rightarrow
Q3\ RelayDecomposition+IterativeRepair
\rightarrow
Q4\ ExactPartition.
\]

**评分**

\[
93/100.
\]

**Q1**

Feasible subset enumeration + set partitioning.

**Q2**

Candidate feasible sorties + Gurobi master + CP-SAT physical UAV/battery scheduling.

**Q3**

DEM-aware relay candidate discretization + coverage matrix + relay MILP/CP-SAT + transport repair loop.

**Q4**

Transport-sortie must-link components + exact 2/3-way enumeration.

**核心创新**

- relay candidate reduction；
- route-level communication matrix；
- iterative transportation-relay coupling；
- exact Q4 must-link resource partition。

**代码难度**

7/10。

**数据需求**

只需官方数据。

**最大风险**

Q3 candidate discretization/repair convergence。

### TOP 2

**架构**

\[
\text{Transport route column}
+
\text{relay coverage pattern}
\rightarrow
\text{joint set-partitioning master}.
\]

**评分**

\[
89.5/100.
\]

**优势**

transport-relay coupling 最完整。

**缺点**

pattern explosion。

**代码难度**

9/10。

**使用条件**

只有 TOP1 底层物理和 route generator 已稳定后才考虑。

### TOP 3

**架构**

\[
\text{ALNS/LNS route search}
+
\text{CP/MILP exact resource repair}
+
\text{relay subsolver}.
\]

**评分**

\[
85/100.
\]

**优势**

anytime、快速得到较好可行解。

**缺点**

global gap 弱，operator debug 较多。

**代码难度**

8/10。

### 多目标决策

推荐：

\[
\boxed{\text{Lexicographic}}
\]

而不是 equal weighted sum。

建议：

**Priority 0**

所有 hard constraints。

**Priority 1**

医疗/首批保障。

**Priority 2**

普通物资 normalized tardiness。

**Priority 3**

makespan。

**Priority 4**

energy。

**Priority 5**

sorties。

实验时再用：

\[
\varepsilon\text{-constraint}
\]

展示 trade-off。

Gurobi 官方原生支持 hierarchical multi-objective。citeturn15search2

### Solver 决策

推荐：

**Gurobi**

用于：

- set partitioning；
- MILP master；
- relay set cover；
- Q4 if MILP；
- MIP gap / IIS。

**CP-SAT**

用于：

- UAV interval；
- battery interval；
- relay interval；
- charging；
- alternative-machine scheduling。

**HiGHS**

无 Gurobi 时作为 linear MILP backup。citeturn15search0turn16search0

GPU：

**不需要。**

### Relay candidate 最终建议

先产生：

\[
R_0=
\text{coarse DEM grid}
+
\text{service vicinity}
+
\text{shadow critical areas}
+
\text{terrain ridges}.
\]

过滤：

1. relay→G01 永远不可行；
2. 对所有 transport blind intervals 都不可行；
3. 被其他候选完全 dominance。

然后：

\[
R_1
=
R_0
+
\text{local refinement around selected candidates}.
\]

最后做 grid-density convergence。

### 连续通信最终建议

Optimizer：

- sparse adaptive samples；
- coverage intervals；
- 小安全 buffer。

Validator：

- phase boundaries；
- dense/adaptive motion sampling；
- DEM raster traversal；
- exact official FSPL；
- exact terrain blockage；
- bidirectional margin；
- access/backhaul simultaneous；
- no communication gap。

论文报告：

\[
\min_t\text{LinkMargin}(t)
\]

而不只是“100% coverage”。

### Q4 最终建议

明确建：

\[
\text{service must-link graph}
\]

并 union-find 成 supernodes。

对 2/3 groups 精确枚举。

不要 K-means。

待 GPT-6 Pro 裁决：

> 一个 relay sortie 若保障多个 transport sorties，是否应额外形成跨 transport sortie 的隐含 must-link。

### 最关键研究证据

- Zhang et al., TRD 2021：payload/energy sensitivity。DOI `10.1016/j.trd.2020.102668`。citeturn21search1
- Rottondi et al., Computer Networks 2021：灾后 multi-service UAV joint planning。DOI `10.1016/j.comnet.2020.107644`。citeturn21search2
- Kuo et al., ESWA 2022：VRP-D + time windows，MIP + VNS。DOI `10.1016/j.eswa.2021.116264`。citeturn21search3
- Shi et al., Omega 2024：灾后 multi-modal emergency scheduling，MIP + two-stage heuristic。DOI `10.1016/j.omega.2024.103104`。citeturn21search0
- Zheng & Chen, IEEE TWC 2024：geography-aware relay 3D placement。DOI `10.1109/TWC.2023.3301613`。citeturn22search0
- Connectivity-aware UAV path planning, IEEE T-ITS 2023：连续 connectivity。DOI `10.1109/TITS.2023.3280995`。citeturn22search1
- Zhao et al., ESWA 2025：truck–drone synchronization matheuristic。DOI `10.1016/j.eswa.2024.126218`。citeturn23search2
- UAV routing with recharging, ASC 2023：MINLP + ALNS。DOI `10.1016/j.asoc.2023.110831`。citeturn23search4
- EVRPTW synchronized charging/swapping, C&OR 2023：VNS matheuristic。DOI `10.1016/j.cor.2023.106310`。citeturn23search1
- Emergency supply GRV–UAV, SEPS 2026：dynamic cooperation + hybrid heuristic。DOI `10.1016/j.seps.2026.102487`。citeturn23search0
- Humanitarian truck–drone multiobjective 2026：NSGA-II + \(\varepsilon\)-constraint。DOI `10.1016/j.cie.2025.111786`。citeturn23search14
- Connected graph partition 2024/2025：MIP/partition exact methods。DOI `10.1002/net.22257`。citeturn27search0

### 仍未解决、必须由下一阶段确认的问题

**其一：**原始五份参数 XLSX 与 DEM 未直接上传到本轮对话，因此需要正式代码重新逐字段读取并生成 `data_audit.json`。

**其二：**医疗“期望送达时间”到底是绝对硬 deadline，还是比普通物资更高优先级的 soft target，应根据原始配送时限表字段和赛题措辞最终确定。当前稳健方案按 hard requirement 处理。

**其三：**Q4 relay-task 跨组依赖的严格语义。

**其四：**Q4 是否允许在固定任务时间不变的条件下重新编号同型号资源，还是必须保留 Q3 的具体 UAV/battery ID。

**其五：**relay altitude candidate 应采用固定 AGL levels、critical-height generation，还是二者混合。

**其六：**continuous communication validator 的最终采样/自适应收敛阈值。

**其七：**TOP 1 的 route pool 应仅采用 enumeration/DFS，还是加入 ALNS 增量生成。

### 需要 GPT-6 Pro 最终做出的决策

请 GPT-6 Pro **不要重新从几十种算法发散**，而应围绕以下有限决策做最终技术冻结：

**核心决策：**

\[
\boxed{\text{是否正式采用 TOP 1 作为主骨架}}
\]

我的研究结论是：**应该。**

然后只需要决定：

**Q1**

是否正式采用：

\[
\text{feasible subset enumeration}
+
\text{set partitioning MILP}.
\]

建议：**是。**

**Q2**

决定：

\[
\text{Gurobi master + CP-SAT scheduler}
\]

还是全部 Gurobi。

建议：先 Gurobi master + CP-SAT scheduling；若接口时间不够，全 Gurobi。

**Q3**

决定：

\[
\text{transport-relay iterative decomposition}
\]

是否作为正式核心创新。

建议：**是。**

再决定：

- candidate XY 生成规则；
- altitude candidate 规则；
- sparse coverage interval 表示；
- transport repair operators。

**Q4**

决定是否采用：

\[
\text{must-link components}
+
\text{exact enumeration}.
\]

建议：**明确采用，禁止 K-means 主解。**

**多目标**

决定：

\[
\text{lexicographic}
+
\varepsilon\text{-constraint experiment}.
\]

建议：**采用。**

**代码落地顺序必须冻结为：**

\[
\boxed{
\text{Data Audit}
\rightarrow
\text{Unified Physics}
\rightarrow
\text{Validators Skeleton}
\rightarrow
Q1
\rightarrow
Q2\ Feasible
\rightarrow
Q3\ Feasible
\rightarrow
Q4
\rightarrow
\text{Improve}
\rightarrow
\text{Experiments}
\rightarrow
\text{Paper/Export}
}
\]

而不是：

\[
\text{先写一个复杂 ALNS}
\rightarrow
\text{最后再检查物理公式}.
\]

最终战略判断是：

> **稳二等奖的底座不是“找到更聪明的优化算法”，而是统一物理口径、得到四问完整可行解、独立 validator 零违规、模板零缺字段。一等奖上限则来自在这个底座之上增加 DEM-aware relay candidate reduction、transport-relay iterative coupling 与 Q4 dependency-graph exact partition。**

在当前约四天窗口里，任何迫使团队牺牲这四件事去换算法炫技的技术路线，都不应该被采用。