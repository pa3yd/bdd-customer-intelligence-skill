# Evidence Policy · 证据政策（V1.1）

**适用范围：所有关键外部结论。** 每一个进入情报卡的结论都必须遵守本文件。

---

## 一、三种类型定义

| 类型 | 定义 | 强制字段 | 示例 |
|---|---|---|---|
| **FACT** | 可追溯到公开来源，或客户明确陈述 | **必须**有 `Source` | 「参保 320 人」← 来源：企业年报 |
| **INFERENCE** | 基于 FACT 的合理推断 | **必须**有 `Reason` + `Confidence` | 「废水以含酚为主」← 理由：公开载明工艺段；置信度：Medium |
| **UNKNOWN** | 未查到 / 无法判断 | 无 | 「未查到环评公示」 |

### 三条铁律

1. **FACT 无 Source → 不得标为 FACT。** 降级为 INFERENCE（补 Reason）或 UNKNOWN。
2. **INFERENCE 无 Reason 或无 Confidence → 不得输出。**
3. **UNKNOWN 保持空白。** 不允许用行业经验值、同类客户类比、"通常来说"填充。

---

## 二、Confidence 分级

**注意：Confidence 只描述 FACT 的可靠度，不描述推断强度。**

| 等级 | 定义 |
|---|---|
| **High** | 官方来源（企业信用公示、政府公示、排污许可平台、官网、上市公告）+ 多条互证 |
| **Medium** | 单一可信来源（权威媒体、行业协会、上市公司文件） |
| **Low** | 第三方聚合站、B2B 平台、无日期信息、来源不可追溯 |

**Source 写法**：优先写 URL 或来源全名。客户口述写 `客户自述`。

### V1.1 补充 · UNKNOWN 的三种状态（**必须区分**）

> **新增原因**：5 次实跑中，「我查了 5 个渠道都没有」与「这个国家根本没有公开渠道」在卡上**完全一样**，
> 对海外客户会被误读成"这家很干净"——**产生错误安全感**。

| 写法 | 含义 |
|---|---|
| `UNKNOWN · searched` | 已按允许渠道检索，未查到 |
| `UNKNOWN · no source` | 该主体所在地区 / 场景**不存在**公开检索渠道 |
| `UNKNOWN · not searched` | 本次未检索（如信息不足、超出范围） |

**硬规则**：`UNKNOWN · searched` 与 `UNKNOWN · no source` **不得互写**。前者说明"可能没有"，后者说明"无法得知"。

---

## 三、FACT / INFERENCE / UNKNOWN 判定流程

```
拿到一条信息
   │
   ├─ 有可验证来源？ ──── 否 ─→ 是客户明确陈述？ ── 否 ─→ UNKNOWN（标注三态）
   │         │是                        │是
   │         ▼                          ▼
   │       FACT                      FACT（Source: 客户自述）
   │
   └─ 无来源，但能说明推断理由？ ── 是 ─→ INFERENCE（Reason + Confidence）
                                └─ 否 ─→ UNKNOWN
```

---

## 四、Demand Status 定级映射表（V1.1 重构）

### 4.1 两类证据（V1.1 拆分）

| 证据类 | 来源 | 记录位置 |
|---|---|---|
| **Public Wastewater Evidence（PWE）**<br>公开废水证据 | 官网环境栏 · 年报 / ESG / BRSR · 政府许可 / 环评 · 半年度合规报告 · 公开发表的项目案例 · 招聘信息载明的设施 | 主卡 `Demand Status` 第一行 |
| **Customer-stated Demand（CSD）**<br>客户侧需求陈述 | **询盘文字** · 客户自述 | 主卡 `Demand Status` 第二行 |

**两者分别记录、分别标注来源，不得合并为一条。**

### 4.2 定级（对两类证据分别给出，主卡只输出较高者作为 `Demand Status`）

| 等级 | 判据（满足任一） | 典型证据 |
|---|---|---|
| **Confirmed** | 有**文件级**证据指向具体项目 / 采购计划 | 环评文件载明废水处理设施；客户提供招标文件；公开中标公告；客户提交的检测报告 |
| **Strong Signal** | 存在硬性外部信号，但无文件级项目证据 | 近 12 个月环保处罚记录；环评公示；排污许可变更；公开招标公告 |
| **Potential** | 只有间接信号 | 行业属目标市场；招聘环保工程师；新增产线公告；扩产新闻；官网环境披露 |
| **Weak** | 客户主动联系但无任何外部信号，且内容笼统 | 只问通用价格 / 只要资料；无具体水质、水量、时间节点 |
| **Unknown** | 无足够信息判断 | 信息极少；无法检索到主体信息 |

### 4.3 定级规则（V1.1 更新）

- **就低不就高。** 同时满足多个等级时取较低者。
- **`PWE` 与 `CSD` 各自独立定级**，主卡取较高者。**不得因为"没有询盘"就把整体压到 `Unknown`。**
- **不得跨级。** 只有行业对口 → 最高只能到 `Potential`。
- **不得用结果反推。** 「后来成交了」不构成 `Confirmed` 的依据；「后来没成交」也不构成 `Weak` 的依据。
- `Confirmed` 需要**文件级**证据。仅客户口述 → 最高 `Strong Signal`。

> ❌ **V1.1 已删除**：「无询盘废水信号 → BDD Relevance 最高 `Medium`」。
> 该规则在 5 次实跑中连续把有充分 PWE 的主体封顶，现已删除。详见 `bdd-relevance-rules.md` 第一节。

### 4.4 主卡写法

```
Demand Status:
  Public Wastewater Evidence: {等级} — {一句话}（Source：E#）
  Customer-stated Demand:      {等级} — {一句话}（Source：客户自述 / E#）
  → Demand Status（取较高）:   {等级}
```

---

## 五、Commercial Risk 危险信号（**Skill 内唯一定级来源**）

> **V1.1 修复**：此前 `customer-type-playbook.md` 载有"工程公司 Commercial Risk 通常为 High 或 Medium"的类型级先验，
> 与本节（自称唯一定级来源、且信号全为行为型）产生**双口径冲突**。
> **现已修复**：类型级先验降级为 `Risk Note`（附注），**不参与定级**。定级只用本节。

### 5.1 危险信号表（仅行为型，须在**询盘当时可观察**）

| 信号 | 风险指向 |
|---|---|
| 一上来就要技术方案和选型计算 | High |
| 反复追问电流密度、能耗、停留时间 | High |
| 拒绝提供水质数据但要求出方案 | High |
| 说"有很多项目"但拿不出具体项目 | High |
| 同时索要多份不同行业的脱敏案例 | High |
| 要求提供客户联系方式做"回访" | High |
| 邮箱域名是同行公司 | High |
| 拒绝签保密协议但坚持要案例 | High |
| 要求"先把方案发来看看，合适再谈" | Medium |
| 对价格不敏感，只对参数敏感 | Medium |
| 只问价格，不问技术 | Medium |
| 无异常信号 | Low |
| 信息不足无法判断 | **Unknown** |

### 5.2 定级规则（V1.1 修正）

```
出现任一 High 信号  → Commercial Risk = High
无 High 但有 Medium → Commercial Risk = Medium
无 High 无 Medium，且存在可观察的互动事实 → Low
无任何可观察的互动事实（如仅有官网网址、无往来内容） → Unknown
```

> ⚠️ **`Unknown` ≠ `High`。** 这条必须显式遵守。
> 「没观察到风险信号」与「观察到高风险信号」是两件事。
> **`Unknown` 只在缺少可观察事实时使用，不得因保守而升格为 `High`。**
> 反之也不得因"看起来是知名大公司"而降为 `Low`。

### 5.3 禁止

- **不得用"最终是否成交"定级。** 结果论会污染规则且无法验证。
- **不得用公司规模、知名度、上市状态定级。**
- **不得使用类型级先验定级**（如"工程公司通常高风险"）。类型先验只能作为 `Risk Note` 附注。

### 5.4 附注字段

```
Commercial Risk: {Low / Medium / High / Unknown}
  Risk Note:  {可选。类型级先验或未纳入定级的事实观察，一句话}
```

---

## 六、Financial Warning（V1.1 新增 · **FW Rule Patch 重定义触发条件**）

**回答的问题**：是否存在公开可见的**企业财务风险 / 财务困境**证据？

**取值：`Yes` / `No` / `Unknown`（只有三个值，不是评级、不是分数、不扩展为财务分析）。**

> ### ⚠️ 本 Patch 的核心修正
> **Business Change / Restructuring（业务变化 / 重组） ≠ Financial Distress / Financial Risk（财务困境）。**
>
> 裁员、高管变化、组织架构调整、厂区亏损、降本计划等**一律不得触发 `Yes`** ——
> 它们全部归入 **第七节 `Business Change Signal`**。
> 真实案例中已连续发生两例此类误报。

### 6.1 `Yes` 的可接受证据（**只能由下列类型触发**）

| # | 证据类型 | 说明 |
|---|---|---|
| 1 | **Insolvency / 资不抵债** | 公开披露资不抵债、净资产为负 |
| 2 | **Bankruptcy / 破产** | 破产申请、破产受理、清算 |
| 3 | **Liquidity crisis / 严重流动性危机** | 公开披露现金流断裂、无法偿付到期债务 |
| 4 | **Debt default / 债务违约** | 债券 / 贷款违约、交叉违约 |
| 5 | **Going-concern warning / 持续经营重大疑虑** | 审计报告的持续经营重大不确定性段落 |
| 6 | **Court-supervised financial restructuring / 法院或债务层面的财务重组** | 破产保护、法院主导的债务重组、债权人主导的重组 |
| 7 | **连续、重大且具有集团层面影响的亏损，并存在明确财务压力证据** | **四条同时满足**：连续性 + 重大性 + **集团层面影响** + 明确财务压力（评级下调 / 被列为被执行人 / 拖欠款项等） |
| 8 | **官方财报 / 审计报告 / 监管披露中明确指出的重大财务困难** | 原文须明确表述财务困难 |

**所有 `Yes` 必须附可靠公开 Source。**

### 6.2 不得触发 `Yes` 的信息（**一律归入 `Business Change Signal`**）

Layoffs / 裁员 · Management changes / 高管变化 · Organizational restructuring / 组织架构调整 ·
Business-unit restructuring / 业务单元调整 · Plant consolidation / 工厂整合 ·
Capacity reduction / 产能调整 · Portfolio adjustment / 业务组合调整 ·
Strategic transformation / 战略转型 · **Site-level operating loss / 单一厂区经营亏损** ·
Cost-cutting program / 降本计划

### 6.3 集团与厂区必须分开

| 情形 | 处理 |
|---|---|
| **厂区 / 业务单元**亏损、裁员、产能调整 | 归 `Business Change Signal`，**不得**推出集团 `FW = Yes` |
| 集团整体财务困境证据 | 才可 `FW = Yes` |
| 仅影响集团、不影响目标采购主体 | 须注明口径（集团 / 主体）；是否影响 Sales Conclusion 见 `sales-conclusion-rules.md` |

### 6.4 证据冲突处理

当**同时**存在「裁员 / 重组 / 厂区亏损」**与**「集团盈利 / 正常现金流 / 上调业绩指引 / 分红 / 回购 / 正常重大投资」时：

| 步骤 | 做法 |
|---|---|
| 1 | **优先判 `Business Change Signal = Yes`** |
| 2 | 依**真实财务证据**定 `Financial Warning` —— 无 6.1 白名单证据时 = **`No`** |
| 3 | **不得用单条负面新闻覆盖更完整的集团财务事实** |

### 6.5 硬规则

| # | 规则 |
|---|---|
| 1 | **不得扩展为完整财务评级系统。** 不评分、不分档、不预测。 |
| 2 | **`Unknown` 不得当作负面。** `FW = Unknown` 不导致降档。 |
| 3 | `Yes` 需有 FACT 级来源（公开财报 / 上市公司公告 / 政府公示 / 监管披露）。 |
| 4 | **不得用"公司是不是大公司"推断财务健康度。** |
| 5 | 集团亏损但目标主体独立盈利时，需注明口径（集团 / 主体），不得混用。 |
| 6 | **`FW = Yes` 不得机械导致 Sales Conclusion 降档** —— 必须结合财务风险严重程度、风险主体是集团还是厂区/子公司、是否影响采购与付款能力、是否影响项目执行能力，并在输出中**说明理由**（见 `sales-conclusion-rules.md`）。 |

**主卡写法**：
```
Financial Warning: Yes / No / Unknown
```

---

## 七、Business Change Signal（**本 Patch 新增**）

**回答的问题**：这家企业**当前正在发生哪些经营层面的变化**？

**定位**：**`Context / Watch Item`（背景与观察项）—— 不是风险定级，不参与降档。**
**取值：`Yes` / `No` / `Unknown`。**

### 7.1 纳入范围（从 Financial Warning 移出）

Layoffs / 裁员 · Management changes / 高管变化 · Organizational restructuring / 组织架构调整 ·
Business-unit restructuring / 业务单元调整 · Plant consolidation / 工厂整合 ·
Capacity reduction / 产能调整 · Portfolio adjustment / 业务组合调整 ·
Strategic transformation / 战略转型 · **Site-level operating loss / 单一厂区经营亏损** ·
Cost-cutting program / 降本计划

### 7.2 输出要求

`Yes` **必须**输出 `Reason` + `Source`：

```
Business Change Signal: Yes
  Reason: {发生了什么变化，一句话}
  Source: {公开来源}
```

### 7.3 硬规则（**不得单独降档**）

| # | 规则 |
|---|---|
| 1 | `Business Change Signal = Yes` **不得单独触发** `Financial Warning = Yes` |
| 2 | `Business Change Signal = Yes` **不得单独触发** `Commercial Risk = High` |
| 3 | `Business Change Signal = Yes` **不得单独导致** `Sales Conclusion` 降档 |
| 4 | `Business Change Signal = Yes` **不得导致** `BDD Opportunity` 降档 |
| 5 | `Business Change Signal = Yes` **不得导致** `Demand Status` 降档 |
| 6 | 它只作 **Context / Watch Item**：帮助业务员理解企业当前经营变化、判断接触时机与话术口径 |
| 7 | **不得把它写进任何"风险"字段的定级依据**（只能作为附注 / 背景说明） |
| 8 | 只有在**同时**具备白名单财务证据（6.1）时，才可升级为 `Financial Warning = Yes` |

**主卡写法**：
```
Business Change Signal: Yes / No / Unknown
  Reason: {…}
  Source: {…}
```

---

## 八、Evidence 附录 · Decision Impact（V1.1 新增）

**每条 Evidence 增加一列 `Decision Impact = High / Medium / Low`。**

| 取值 | 含义 |
|---|---|
| `High` | 直接影响主卡任一字段的判定 |
| `Medium` | 影响某个字段的置信度或补充说明 |
| `Low` | 背景信息，不参与判定 |

### 硬规则

| # | 规则 |
|---|---|
| 1 | **`Decision Impact` 只影响展示优先级，不影响真实性判断。** 它与 `类型`（FACT / INFERENCE / UNKNOWN）和 `Confidence` **完全正交**。 |
| 2 | 一条 `Low Impact` 的 FACT 仍是 FACT，可溯源率照样计入。 |
| 3 | **不得为了"让证据看起来有力"而抬高 `Decision Impact`。** |
| 4 | PDF 第 3 页优先展示 `Decision Impact = High` 的条目。 |

---

## 九、输出格式要求

### 附录 A 表格

```markdown
| # | 主题 | 类型 | 结论 | Source | Reason | Confidence | Decision Impact |
|---|---|---|---|---|---|---|---|
| E1 | 主体规模 | FACT | 参保 320 人 | 企业年报公示 | — | High | High |
| E2 | 废水性质 | INFERENCE | 废水以含酚为主 | — | 公开载明工艺段 | Medium | High |
| E3 | 环评公示 | UNKNOWN · searched | 环评公示（已检索未查到） | — | — | — | Low |
```

### 混排禁令

- FACT 行不填 `Reason`；INFERENCE 行不填 `Source`（除非推断基于某个特定来源）。
- **不得把 FACT 与 INFERENCE 写在同一行或同一格。**
- **不得把 UNKNOWN 写成"可能""或许"等模糊表述。**
- **UNKNOWN 必须带三态后缀**（`searched` / `no source` / `not searched`）。

### 可溯源率（回测指标）

```
可溯源率 = 已标注 Source 的 FACT 数 / FACT 总数
目标：100%
```

任何 FACT 缺 Source 即为不合格，回测直接判不通过。

---

## 十、常见错误对照

| 错误写法 | 问题 | 正确写法 |
|---|---|---|
| 「该公司年产 5 万吨」（无来源） | FACT 缺 Source | 补 Source，或降级为 INFERENCE |
| 「估计参保 100 人左右」 | 用推测冒充规模数据 | `UNKNOWN` |
| 「印染废水通常 COD 800~1500」 | 用行业经验值当客户数据 | `UNKNOWN`（列入 Missing Critical Information） |
| 「该行业都有废水，所以 BDD 相关性高」 | 行业经验值替代企业事实 | 逐项对照 BDD Relevance 输入，证据不足时 `Unknown` |
| 「未发现环保处罚」（无渠道） | 把"无渠道"写成"没问题" | `UNKNOWN · no source` |
| 「客户很有诚意」 | 主观判断 | 删除，或改为可观察事实 |
| 无互动却写 `Risk = High` | **`Unknown` 被升格** | `Unknown` + `Risk Note` |
| 「工程公司通常风险高」→ 直接定 High | 类型级先验定级 | `Unknown` + `Risk Note` |
| 把 FACT 与 INFERENCE 写同一格 | 幻觉主要来源 | 拆行 |
| 「有裁员 / 重组公告」→ 直接 `FW = Yes` | **业务变化 ≠ 财务困境（本 Patch 修正）** | 归 `Business Change Signal = Yes`；`FW` 依 6.1 白名单定级 |
| 「某厂区连续亏损」→ 推出集团 `FW = Yes` | **厂区级 ≠ 集团级** | 厂区亏损归 `Business Change Signal`；集团 `FW` 需集团级白名单证据 |
| 用 `Business Change Signal` 单独降 `Sales Conclusion` | **背景项被当风险用** | 只作 Context / Watch Item，不得单独降档 |

---

## 十一、待校准项

- [ ] Demand Status 五级判据是否与实际一致？
- [ ] `PWE` 与 `CSD` 的分级是否需要对 `PWE` 单独设更宽松口径？
- [ ] 环保处罚记录的时效窗口（现为 12 个月）是否需要调整？
- [ ] `Financial Warning` 白名单（6.1）是否覆盖实际遇到的财务困境形态？
- [ ] `Business Change Signal` 是否需要更强的展示位（当前仅 Markdown + 结论原因中提一句）？
- [ ] `Decision Impact` 的三档定义是否符合使用习惯？
