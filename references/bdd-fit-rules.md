# Industry Fit 判定规则（V1.1.3 + BDD-Specific Relevance Gate Patch）

**回答的问题**：这个**行业 / 业务属性**是否属于 Boromond 目标市场？

**数据要求**：仅需行业与业务属性，**不需要水质数据、不需要客户需求**。

> **BDD-Specific Relevance Gate Patch（2026-09-27）· Patch A**：
> 收紧 `T3` 定义 —— `T3` 必须由**废水性质证据**（高 COD / 难降解 / 难处理）成立，
> **不得由"有工业废水 / 有生产废水 / 有表面处理废水"推出**。详见第二节「T3 证据门槛」与「T3 硬规则」。
> 同 Patch 的 Patch B（BDD-Specific Relevance Gate）见 `bdd-relevance-rules.md`，**只作用于 End-user `High`**。

> **V1.1 变化**：目标市场清单已补入（最小地图，由业务方提供）。此前"清单未填 → 一律 `Unknown`"的死锁已解除：
> 在此之前 5 次实跑中 `Industry Fit` 恒为 `Unknown`，连锁导致 `BDD Relevance` 从定义上不可达 `High`。

---

## 一、取值定义

| 取值 | 含义 |
|---|---|
| `Target` | 属 Boromond **核心目标市场**（④组之一） |
| `Adjacent` | 非核心，但属**可迁移场景 / 渠道**（工业废水治理链条上的伙伴型主体） |
| `Outside` | 已确证**不属**上述两类 |
| `Unknown` | 行业 / 业务属性无法确认，或落在下述定义的边界之外 |

---

## 二、Boromond 最小目标市场地图

> 来源：业务方 V1.1 Spec。**行业按"是否产生高 COD / 难降解工业废水"定义，不按国民经济门类。**
> 因此「化学品**制造**」与「化学品**分销**」分属不同档 —— 这是实际判定中出现过歧义的根源。

### `Target` · 核心目标市场（四组）

| 组 | 覆盖范围 |
|---|---|
| **T1** | Lithium Battery / Battery Materials / Battery Recycling<br>锂电池 · 电池材料 · 电池回收 |
| **T2** | Pharmaceutical / API<br>制药 · 原料药 |
| **T3** | High-COD / Refractory Industrial Wastewater<br>高 COD / 难降解工业废水（产生方） |
| **T4** | Fine Chemicals / Agrochemicals / Dyes<br>精细化工 · 农药 · 染料 |

**说明**：T3 是**性质口径**而非行业口径——它要求**废水性质**（高 COD / 难降解 / 难处理）成立，而不是"行业属制造业"成立。

> ⚠️ **Patch A（2026-09-27）· T3 定义收紧 —— 必读**
>
> **T3 = High-COD / refractory / difficult-to-treat industrial wastewater（高 COD / 难降解 / 难处理工业废水）。**
>
> ❌ **"有工业废水" ≠ T3。**「工业废水 / 制造业废水 / 生产废水」这类表述**本身不构成 T3 证据**。
> ❌ **"废水相关性" ≠ "BDD 相关性"。** 有废水、有处理设施、有排污许可，都只能证明**存在废水**，
> 不能证明**存在 BDD 适用场景**。
>
> **行业标签不构成证据。** 下方举例（焦化、印染、电镀…）只是**性质举例**，用于帮助识别；
> **不得因主体属于举例中的行业就直接判 `Target`** —— 必须另有该主体**自身的废水性质证据**（E# 级）。

### T3 证据门槛（**必须至少命中一项**）

| # | 可接受的 T3 证据（须为 FACT 级、附 Source） |
|---|---|
| 1 | high COD（高 COD） |
| 2 | refractory wastewater（难降解废水） |
| 3 | hard-to-biodegrade / poorly biodegradable wastewater（可生化性差） |
| 4 | persistent / recalcitrant organics（持久性 / 顽固性有机物） |
| 5 | difficult organic wastewater（难处理有机废水） |
| 6 | deep treatment / polishing requirement（深度处理 / 提标要求） |
| 7 | conventional biological treatment limitation（常规生化处理受限 / 不适用） |
| 8 | difficult industrial effluent requiring advanced treatment（需高级氧化等强化处理的工业废水） |
| 9 | explicitly documented difficult-to-treat pollutants（明确载明的难处理污染物，如卤代烃、难降解溶剂、高浓度母液等） |

### T3 硬规则（**以下证据单独存在时不得判 T3 `Target`**）

| # | 单独存在时**不足以**判 T3 |
|---|---|
| 1 | 只存在工业废水 |
| 2 | 只存在生产废水 |
| 3 | 只存在阳极氧化废水 |
| 4 | 只存在机加工废水 |
| 5 | 只存在压铸废水 |
| 6 | 只存在普通表面处理废水 |
| 7 | 只存在一般排污许可 |
| 8 | 只存在废水处理设施 |
| 9 | 只存在废水量 / 用水量数据 |

**除非同时存在上表「T3 证据门槛」中的至少一项**（高 COD / 难降解 / 难处理 / 深度处理 / AOP 需求 / 明确复杂污染物）。

**不满足时的落点**：按本文件第三节流程继续往下判 ——
属 A1~A3 → `Adjacent`；符合 Outside 界定 → `Outside`；**其余（含"普通制造业废水"，既非目标市场、亦非 A1~A3）→ `Unknown`**。
**一律不得因为"有工业废水"而判 `Target`。**

### `Adjacent` · 可迁移场景 / 渠道

| 组 | 覆盖范围 |
|---|---|
| **A1** | Industrial Wastewater EPC / AOP / Integrator<br>工业废水工程总包 · 高级氧化 · 系统集成 |
| **A2** | 工业化学品 / 水处理药剂**分销与代理**（服务工业客户） |
| **A3** | 工业废水领域设计院 · 科研院所（规格影响与技术验证节点） |

**说明**：`Adjacent` 是 `Partner Path` 的主要落点（见 `customer-type-playbook.md` 的双路径分流节）。
**Adjacent 不是"次等"，而是不同的机会类型**——对应 `EPC / Integration Opportunity`、`Distribution Opportunity`、`Technology Partner Opportunity`。

### `Outside` · 已确证不属上述

**界定式描述（非穷举）**，仅在能确证时使用：

| 类型 | 说明 |
|---|---|
| 市政 / 生活污水处理、给水厂运营 | 非工业废水治理链条 |
| 纯消费品 / 零售 / 餐饮 / 服务业 | 无工业废水场景 |
| 非涉水行业（软件、金融、贸易服务等） | 与目标市场无交集 |
| 明确对外声明仅做**非工业**客户的分销 | 渠道不覆盖工业客户 |

> ⚠️ **不得因"清单没写"就判 `Outside`。** 清单未列但符合 T3 性质口径的 → `Target`；无法归类 → `Unknown`。

---

## 三、判定流程

```
1. 行业 / 业务属性可确认？
   ├─ 否 ──────────────────────────→ Unknown
   ▼是
2. 属 Target 四组（T1~T4）？
   │   · T1 / T2 / T4 ──────────────→ 命中（行业口径）
   │   · T3 ── 须再过「T3 证据门槛」（第二节）：至少命中 1 项废水性质证据
   │            ├─ 命中 ───────────→ Target
   │            └─ 未命中 ─────────→ 不判 Target，继续第 3 步
   ├─ 是 ──────────────────────────→ Target
   ▼否
3. 属 Adjacent 三组（A1~A3）？
   ├─ 是 ──────────────────────────→ Adjacent
   ▼否
4. 符合 Outside 界定（第二节）？
   ├─ 是 ──────────────────────────→ Outside
   └─ 否（落在定义边界外）──────────→ Unknown
```

**第四步的保守性**：`Outside` 需要**正面确证**，不是默认值。这与 V1 相反（V1 中 Outside 因无清单而不可达）。

---

## 四、硬规则

| # | 规则 |
|---|---|
| 1 | **不得因行业不属于四个 Target 组就判 `Outside`。** 先查 `Adjacent`，再按 Outside 界定确证。 |
| 2 | **Industry Fit = Target/Adjacent 不得推导 BDD Relevance = High。** 它只是 BDD Relevance 的输入之一。 |
| 3 | 行业属性 ≠ 主体事实。「这个行业有废水」不等于「这家公司有废水」。 |
| 4 | 同一行业的所有公司 Industry Fit 取值相同——**这是它与 BDD Relevance 的根本区别**。 |
| 5 | **化学品制造 → T4（Target）**；**化学品分销 → A2（Adjacent）**。两者不得混判。 |
| 6 | Industry Fit 高不得推导 Demand Status 高。行业对口不代表这家公司真有项目。 |
| 7 | 海外主体按其**业务实质**归类，不依赖中国工商经营范围表述。 |
| 8 | **`T3` 判 `Target` 必须附至少 1 项「T3 证据门槛」中的废水性质证据（E# 级）。** 只有"制造业 + 废水"不得判 `Target`。 |
| 9 | **不得因主体行业落在 T3 的举例清单里（焦化 / 印染 / 电镀 / 表面处理…）就直接判 `Target`。** 举例是识别辅助，不是证据。 |
| 10 | **"有废水" ≠ "有 BDD 相关性"。** Industry Fit 只回答行业属性；废水是否属 BDD 适用场景由 `bdd-relevance-rules.md` 的 Gate 判定。 |

> 完整推导禁令见 `bdd-relevance-rules.md` 与 `SKILL.md` 第三节。

---

## 五、目标市场地图 → 机会类型对照

| Industry Fit | 典型主体 | 可能的机会类型 |
|---|---|---|
| `Target` | 锂电池 / 制药 / 高 COD 废水产生方 / 精细化工制造 | `End-user Opportunity` |
| `Adjacent` · A1 | 工业废水 EPC / AOP 供应商 / 系统集成商 | `EPC / Integration Opportunity` |
| `Adjacent` · A2 | 工业化学品 / 水处理药剂分销代理 | `Distribution Opportunity` |
| `Adjacent` · A3 | 设计院 / 科研院所 / 自有工艺产品线的技术公司 | `Technology Partner Opportunity` |
| `Outside` | — | `Unknown` |
| `Unknown` | — | `Unknown` |

> **注意**：本表是**倾向**而非换算公式。最终 `Opportunity Type` 由 `opportunity-type-rules.md` 依据主体级证据判定。

---

## 六、待业务方确认（不阻塞运行）

| # | 待确认 | 影响 |
|---|---|---|
| 1 | **T3「T3 证据门槛」的 9 项证据清单是否需要增删**；"高 COD"是否需给出浓度口径（当前**不设阈值**，只认"公开载明属高 COD / 难降解 / 难处理"） | 边界案例归类 |
| 1b | **是否需要新增一类 Target（如 T5「复杂有机合成类制造业」）以收纳"有复杂有机工艺但未公开载明难降解"的主体** —— 未定前这类主体输出 `Unknown` | 召回损失 |
| 2 | `Outside` 界定是否需要补充 | 目前需正面确证，偏保守 |
| 3 | A2 分销商是否确认为目标渠道（而非仅为贸易中间商） | `Distribution Opportunity` 是否成立 |
| 4 | 是否存在"必须拒绝"的行业（安全 / 合规 / 成本） | 无筛除能力 |

---

## 七、与其他文件的职责边界

| 文件 | 负责 |
|---|---|
| **本文件** | Industry Fit 判定（行业 / 业务属性 → 四值） |
| `bdd-relevance-rules.md` | BDD Relevance 判定（分 Path 内部逻辑 + 强制附注） |
| `customer-type-playbook.md` | 客户类型判定 + End-user / Partner 双路径分流 |
| `opportunity-type-rules.md` | Opportunity Type 判定 + Priority Site |
| `wastewater-signal-map.md` | 从文字识别信号（客户侧） |
| `lead-signals.md` | 从外部来源检索证据（公开侧） |
| `evidence-policy.md` | FACT / INFERENCE / UNKNOWN 标注；Demand Status 与 Commercial Risk 定级 |

**本文件不做任何技术判断，不输出任何技术参数与数值区间。**
