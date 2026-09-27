# Opportunity Type & Priority Site 判定规则（V1.1 新增）

**回答两个问题**：
1. **这个机会是什么类型？**（`Opportunity Type`）
2. **如果是多厂区集团，最该先研究哪个厂区？**（`Priority Site`）

---

## 第一部分 · Opportunity Type

### 一、五值枚举（只允许这五个）

| 取值 | 含义 | 典型主体 |
|---|---|---|
| `End-user Opportunity` | 客户自身产生废水，BDD 可用于其废水治理 / 提标 / 难降解段 | 终端业主（Target 四组的制造企业） |
| `Technology Partner Opportunity` | 客户自有工艺产品线，BDD 可与其组合互补或授权合作 | 技术公司 · 设计院 · 科研院所 |
| `EPC / Integration Opportunity` | 客户承接工程，可采购电极 / 模组用于其项目集成 | 环保工程公司 · 系统集成商 |
| `Distribution Opportunity` | 客户为渠道商，可代理 / 分销产品 | 工业化学品 / 水处理药剂分销代理 |
| `Unknown` | 以上均无法确证 | — |

### 二、判定流程

```
1. Path 确定？
   ├─ Undetermined ──→ Unknown（先确认客户类型）
   ▼
2. End-user Path？
   ├─ 是 ────────────→ End-user Opportunity
   ▼否（Partner Path）
3. 主体是工程 / 集成方（承接项目、做系统集成）？
   ├─ 是 ────────────→ EPC / Integration Opportunity
   ▼否
4. 主体是渠道 / 分销方（采购转售、代理、无自有交付）？
   ├─ 是 ────────────→ Distribution Opportunity
   ▼否
5. 主体自有工艺产品线 / 规格影响力（技术公司、设计院、院所）？
   ├─ 是 ────────────→ Technology Partner Opportunity
   └─ 否 ────────────→ Unknown
```

### 三、复合情形（重要）

**一个主体可同时符合多个类型。** 此时按以下规则处理：

| 情形 | 处理 |
|---|---|
| 既承接工程，又自有工艺产品线 | 输出**主类型** + `+| 副类型`，例如 `EPC / Integration Opportunity +| Technology Partner Opportunity`<br>并在 `Reason` 写明两者的证据 |
| 既做分销，又做少量集成 | 以**证据更强的能力**为主类型 |
| 自有工艺与 BDD 目标场景重叠 | 主类型照常输出，但**必须同时标注 `Conflict: 潜在竞争`**（红色语义），不得隐藏 |

> **EPC 兼自有工艺线型主体**：同时具备 EPC 承接、自有 AOP 产品线（UV/H₂O₂、臭氧）、自有生产制造 → 正确输出为
> `EPC / Integration Opportunity +| Technology Partner Opportunity`，并标注 `Conflict: 潜在竞争（自有 AOP 产品线）`。

> **2026-09-27 Partner Cooperation Evidence Gate Patch**：`Conflict` **不是装饰性标签**。
> 出现 `Conflict` 时，Partner `BDD Opportunity` 判 `High` 前必须额外检查 5 项（技术路线是否直接重叠 / 是否自研 proprietary / **是否有第三方集成机制** / **是否有外部核心组件采购证据** / Boromond 属 supplier·partner·competitor 哪一类）；
> **第 3、4 项均为 `Unknown` 时不得因能力或项目强而判 `High`**。完整规则见 `bdd-relevance-rules.md` **第五节**。
>
> ⚠️ 本 Patch **不改 `Opportunity Type` 五值与复合规则** —— `Conflict` 只影响**机会强度**，不影响**机会类型**。

### 四、硬规则

| # | 规则 |
|---|---|
| 1 | **`Opportunity Type` 不是评分，不参与优先级排序。** 它只回答"机会类型"，不回答"好坏"。 |
| 2 | 不得因 `End-user Opportunity` 就认为优于 `Distribution Opportunity`——不同类型走不同打法，价值量级由业务方判断。 |
| 3 | Path 未定 → `Opportunity Type = Unknown`，不得猜。 |
| 4 | 复合情形必须显式标注，不得只写主类型而隐藏副类型。 |
| 5 | **发现潜在竞争关系必须标注**，不得淡化。这是建立信任的前提。 |

### 五、Evidence 标注要求（遵循 `evidence-policy.md`）

| 结论 | 类型 | 要求 |
|---|---|---|
| `Opportunity Type` | **INFERENCE** | 必须有 `Reason`（引用了哪条客户类型 / 能力判据） |
| 复合类型中作为副类型的依据 | **INFERENCE** | 必须列出支撑证据编号 |
| `Conflict: 潜在竞争` | **INFERENCE** | 必须有 `Reason` + 证据（其自有工艺与 BDD 场景重叠的公开来源） |
| `Priority Site` 的厂区名与定位 | **FACT** | 必须有 `Source` |
| `Priority Site` 的"最值得优先研究"判断 | **INFERENCE** | 必须写明命中的权重项与证据编号 |
| 厂区无法确证 | **UNKNOWN** | 输出 `Group-level only`，**不得用集团数据填充厂区** |

**禁止**：不得因"这类客户通常走某条路线"而输出 `Opportunity Type`——类型级先验不构成 Source。

---

## 第二部分 · Priority Site

### 一、适用条件（**仅大型多工厂集团使用**）

| 条件 | 说明 |
|---|---|
| **触发** | 主体在**公开来源中可确认 ≥ 3 个制造厂区 / 工业站点**（跨国或跨区域） |
| **不适用** | 单一厂区、办公型主体、厂区数无法确认、厂区数 < 3 → 输出 `N/A` |

> **目的**：避免"集团级事实"与"厂区级事实"混在一起。
> 集团有 62 个站点不等于每个站点都有废水需求；**具体到厂区才能落地**。

### 二、选择依据（按公开证据加权，择优一处）

| 权重 | 信号 | 说明 |
|---|---|---|
| **1（最高）** | 近 12 个月环境执法 / 许可事件 | 处罚、整改令、许可修订 → 合规压力最直接 |
| **2** | 在建 / 规划中的环保或产能项目 | 有项目 = 有采购窗口 |
| **3** | 工艺单元涉水密度最高 | 湿法冶金、化学反应、精炼、合成等工艺密集处 |
| **4** | 公开披露现有处理设施且存在未闭环段 | 有设施 + 未闭环 = 提标窗口 |
| **5** | 公开披露环境管理岗位 / 独立监测 | 说明该厂区环保权重高 |

**评分方式**：**不做数值评分。** 按上表顺序**逐级否决**——先看权重 1，有多处命中再比权重 2，依此类推。命中最多者即为 `Priority Site`。

### 三、输出格式

```
Priority Site: {厂区名}（{国家 / 地区}）
  Why: {一句话，指向具体信号}
  Evidence: {编号}
```

**不适用时**：
```
Priority Site: N/A（单一厂区 / 厂区数不足 3）
```

### 四、硬规则

| # | 规则 |
|---|---|
| 1 | **必须区分集团级事实与厂区级事实。** 集团数据不得直接写成某厂区数据。 |
| 2 | 厂区级信息无法确证时，写 `Group-level only`，**不得用集团数据填充厂区**。 |
| 3 | `Priority Site` 只用于**研究优先级**，不构成任何项目判断，不承诺该厂区有需求。 |
| 4 | 若多个厂区证据强度相当，输出 1 个主选 + 可附 1 个备选，**最多 2 个**。 |
| 5 | 输出 `Priority Site` 时，`Next Action` 应同步指向该厂区。 |

### 五、多厂区制造集团型示例

```
Priority Site: <主基地城市>（国家 · 州 / 省）
  Why: 近 12 个月有环境许可条件修订申请与政府定期监测；官方披露现有废水处理设施（物化 + 生物）与雨水缓冲，且有大型装置处于许可申请准备阶段
  Evidence: E12 / E15 / E16 / E17
```

> 集团层其余站点 → 全部保留在附录，但主卡只指向优先厂区。

---

## 六、与其他文件的职责边界

| 文件 | 负责 |
|---|---|
| **本文件** | Opportunity Type（五值 + 复合情形）+ Priority Site（触发条件与选择依据） |
| `customer-type-playbook.md` | 客户类型与 Path 分流（决定 Opportunity Type 的第一层分支） |
| `bdd-relevance-rules.md` | BDD Relevance 四值判定 |
| `bdd-fit-rules.md` | Industry Fit |
| `current-treatment-rules.md` | 现有处理方案 / 技术组合提取 |
| `sales-conclusion-rules.md` | Sales Conclusion（消费 Opportunity Type，但不据此排序） |

**本文件不输出金额、不排序客户价值、不做技术判断。**

---

## 七、待业务方确认

| # | 待确认 | 归属 |
|---|---|---|
| 1 | 五类机会类型是否覆盖实际业务形态；是否需第 6 类 | 销售 |
| 2 | 四类机会的价值量级差异（是否需要内部口径说明） | 销售 |
| 3 | `Priority Site` 触发门槛（≥ 3 厂区）是否合适 | 销售 |
| 4 | 权重顺序是否符合实际判断习惯 | 技术 + 销售 |
