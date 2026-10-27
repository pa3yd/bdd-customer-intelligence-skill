# Sales Conclusion 判定规则（V1.1 新增）

**回答的问题**：**这个客户，我现在该投入多少？**

**新增原因**：此前 5 次实跑中，`Next Action` 只回答"做什么动作"，**不回答"值不值得投入"**。
同一个人在不同时间看同一张卡，会得出不同的投入决策。销售要的是一句可直接引用的结论。

---

## 一、五值枚举（只允许这五个）

| 取值 | 语义 | 颜色 |
|---|---|---|
| `建议重点开发` | 证据充分、无重大风险 → 应优先配置资源 | 🟢 |
| `建议开发` | 有明确机会，但需求或风险尚有未确认项 | 🟢 |
| `建议先验证` | 机会已识别，但关键信息缺失 → 先补信息再决定投入 | 🟡 |
| `暂不优先` | 机会低，或存在实质风险 / 财务警示 | 🔴 |
| `信息不足，暂缓判断` | 连"值不值得查"都还无法判断 | ⚪ |

**每条结论必须附 1~2 句原因**（引用字段与证据编号）。

---

## 二、判定输入（只用已有字段，不新增判断）

```
BDD Relevance           High / Medium / Low / Unknown
Demand Status           Public Wastewater Evidence + Customer-stated Demand 的组合
Commercial Risk         Low / Medium / High / Unknown
Financial Warning       Yes / No / Unknown   ← 只由财务困境证据触发（evidence-policy.md 6.1）
Business Change Signal  Yes / No / Unknown   ← Context / Watch Item，**不是判定输入**
Path                    End-user / Partner / Undetermined
Missing Critical Information  是否为空
```

**V1.2 前置核对**：`Demand Status` 必须先通过 `evidence-policy.md` 第四节的目标主体/需求对象门槛。集团订单、Partner 对外销售和通用目录不能直接抬高需求。Partner 有 `Conflict` 时读取 `bdd-relevance-rules.md` 5.1 的子类与非竞争切面证据；这属于现有 `BDD Relevance / Conflict` 的解释，不新增评分或主卡字段。

> **`Business Change Signal` 不是判定输入。** 它只用于解释企业当前经营变化，
> **不得参与任何档位判定**（见 `evidence-policy.md` 第七节硬规则 1~8）。
> 裁员、高管变化、组织架构调整、厂区亏损、降本计划 → 一律只进 Business Change Signal。

---

## 三、判定流程（一票否决优先，再按档次判定）

### 第 1 步 · 一票否决 → `暂不优先`

| 条件 | 理由写法 |
|---|---|
| `Commercial Risk = High` | 存在高商业风险信号，不建议投入技术资源 |
| `BDD Relevance = Low` | 已确证无 BDD 可切入场景 |

> **`Financial Warning = Yes` 不构成一票否决。** 它使结论**最高不超过 `建议先验证`**（见第 5 步），
> 除非通过第 4b 步的例外判定，且必须在该结论中**明示财务警示**。
> 理由：报表亏损但手上有项目 / 有渠道的伙伴仍具开发价值；直接判死会把有效渠道误杀。
> （此口径在实践中发现并修正。）
>
> **`Business Change Signal = Yes` 既不一票否决，也不降档。**

### 第 1b 步 · 已确证直接竞争的优先级

仅当目标主体的产品**直接替代BDD功能且服务同一采购需求**均有可核证据，并已定向核对外部核心部件采购、授权、联合研发或其他合作切面，仍无正面入口时，才可因“已证实的直接替代风险＋当前缺少可进入切面”取 `暂不优先`。`Conflict = Yes` 单独不构成一票否决。只有技术路线/污染物/行业重叠或未检索合作切面时，不触发本步。存在合作事实但尚无BDD需求时通常 `建议先验证`，同时保留直接竞争风险。不得把未发现采购证据写成不会采购。

V1.2.1-b Partner实际执行由 `scripts/decision_engine.py` 复算；BDD机会、开发优先级、采购意向与技术合作潜力分别输出。`Medium`机会而`Low`开发必须写明具体替代证据、检索覆盖和资源判断，不能靠Conflict布尔标签。

存在该主体**已证实的外部电极/反应器等部件采购**时，记录「系统级竞争 + 部件级潜在供应」并继续第 2～5 步；不能自动否决，也不能因采购行为自动升 `High`。通用 AOP 工程设计只属 `Integration overlap`，不触发本步。

### 第 2 步 · `信息不足，暂缓判断`

| 条件 |
|---|
| `BDD Relevance = Unknown` **且** `Demand Status` 无任何证据 |
| **或** `Path = Undetermined` **且** 无任何主体级证据 |

> `Path = Undetermined` 但有主体级证据时，不落入本档 → 落 `建议先验证`（先确认客户类型）。

### 第 3 步 · `建议重点开发`

**需同时满足**：

| # | 条件 |
|---|---|
| 1 | `BDD Relevance = High` |
| 2 | `Demand Status` 达 `Confirmed` 或 `Strong Signal`（PWE 或 CSD 任一构成） |
| 3 | `Commercial Risk ∈ {Low, Medium}` |
| 4 | `Financial Warning ≠ Yes` |
| 5 | `Missing Critical Information` 不含 Business 级缺项 |

> **说明（2026-10-16 · 未放开门槛）**：`Commercial Risk` 现已新增「公开可验证风险信号」路径（见 `evidence-policy.md` 5.6 / 5.7），
> 纯公开背调下 `Risk` **可以**通过"按允许渠道检索 + 无公开负面"拿到**可核查的 `Low`**（不再必然恒 `Unknown`）。
> 但**本步条件 3 的 `Risk ∈ {Low, Medium}` 门槛保持原样、未放宽** —— 拿 `Low` 的前提仍是"有可靠主体级覆盖且无负面"，
> 非上市 / 无公开财报渠道的主体仍为 `Unknown`，不满足本步。是否进一步调整门槛属后续独立决策，本 Patch 不动。

### 第 4 步 · `建议开发`

**满足任一**：

| # | 条件 |
|---|---|
| A | `BDD Relevance = High` **且** `Demand Status = Potential` **且** `Risk ≠ High` **且** `FW ≠ Yes` |
| B | `BDD Relevance = Medium` **且** `Demand Status ∈ {Confirmed, Strong Signal}` **且** `Risk ∈ {Low, Medium}` **且** `FW ≠ Yes` |

> **说明（2026-10-16 · 未放开门槛）**：A 项 `Risk ≠ High` 本已允许 `Unknown`（`Unknown` ≠ `High`，故 A 项在纯背调下**本就可达**）；
> B 项的 `Risk ∈ {Low, Medium}` 现因「公开可验证风险信号」路径（`evidence-policy.md` 5.6 / 5.7）而**具备拿 `Low` 的可能**，
> 但**门槛未放宽** —— 拿 `Low` 仍需"可靠主体级覆盖 + 无负面"。本 Patch 不联动第 3 步的结论门槛。

> 表中 `FW ≠ Yes` 的含义是 **"不存在财务困境"**。
> 若 `FW = Yes`，先走 **第 4b 步**判定是否影响本次采购与执行，再决定是否适用 A / B。

### 第 4b 步 · `Financial Warning = Yes` 的特殊判定（**不得机械降档**）

**`FW = Yes` ≠ 结论必须降一档。** 必须逐项回答下列四个问题，并把判断写进结论原因：

| # | 必须回答的问题 |
|---|---|
| 1 | **财务风险严重程度**：是破产 / 违约 / 持续经营重大疑虑，还是仅"连续亏损"？ |
| 2 | **风险主体层级**：是集团 / 母公司，还是某个厂区、子公司或非目标主体？ |
| 3 | **是否影响本次潜在采购与付款能力**：是否有公开证据显示仍在正常采购 / 正常重大投资 / 正常付款？ |
| 4 | **是否影响相关项目执行能力**：是否影响项目推进、交付或运维能力？ |

**判定规则（固定，不凭印象）**

| 情形 | 结论上限 |
|---|---|
| 四问中任一**指向影响本次目标采购主体 / 采购与付款能力 / 项目执行** | **`建议先验证`** |
| 风险主体**不是**本次目标采购主体或 `Priority Site`，**且**有公开证据显示采购、付款、项目执行均未受影响 | **可不降档**（回到第 3 / 4 步正常判定） |
| 无法判断上一行 | 取保守侧 → **`建议先验证`** |

> **输出强制要求**：只要 `FW = Yes`，结论原因中**必须**出现一句
> 「为什么该财务风险会影响（或不影响）本次 BDD 客户开发判断」的解释。

### 第 5 步 · `建议先验证`

**其余情况**，即：机会已识别（`BDD Relevance ∈ {High, Medium}`）但未达上述门槛。典型：

| 情形 | 先验证什么 |
|---|---|
| `Missing Critical Information` 含 Business / Project 级缺项 | 先确认业务与项目层面信息 |
| `Commercial Risk = Unknown` 且 `Demand Status ≤ Weak` | 先补需求证据与风险信号 |
| **`Financial Warning = Yes` 且经第 4b 步判定影响本次采购 / 执行** | **先复核财务口径与风险主体；结论中必须明示并解释财务警示** |
| `Path = Undetermined` 但有主体级证据 | 先确认客户类型 |
| `Demand Status` 无任何证据（含 `Unknown`） | 先确认是否存在需求 |

**输出时必须写明"先验证什么"**——指向 `What Is Missing` 的对应项。

---

## 三之二、Next Action 生成要求（**V1.1.6 新增 · 对全部档位生效**）

`Next Action` 只回答一件事：**「这家企业下一步最需要确认什么」。**

**必须包含两段内容：**

| 段 | 内容 | 来源（**单一来源，不得另立**） |
|---|---|---|
| **① 首轮加问** | 按客户类型取该类型的**加问项**：主卡只留**最关键 1 项**，完整清单进 Page 2 明细 | **`references/must-ask-params.md` 第六节**（A / B / C / D / E 组）—— **本文件不复写、不新造问题清单**，只引用 |
| **② 边界提示** | 当 `Conflict = Yes` 时，**`Next Action` 必须以该提示开头**：「先确认合作 / 竞争边界，再进入技术讨论。」 | `Conflict` 的定义与判定见 `references/bdd-relevance-rules.md` 5.1 / 5.4 与 `references/opportunity-type-rules.md` 第三节 —— **不在本文件重定义** |

**类型 → 加问组映射（复用 `must-ask-params.md` 第六节已有分组，不新增问题）**

| Path / 客户类型 | 加问组 |
|---|---|
| End-user | **B 组** |
| Partner·EPC | **C 组** |
| Partner·Distributor | **D 组** |
| Partner·Technology Partner | **E 组** |
| Partner·Integrator | **C 组 + E 组**（项目与采购形态 + 组合缺口；**沿用已有条目，不新增问题**） |
| Undetermined | **A 组（通用）** |

**`Conflict = Yes` 时 · 本阶段不主动释放（禁止范围一律复用现有规则的定义，不新增禁止项）**

| 不释放 | 依据（**现有规则**） |
|---|---|
| 核心技术参数 | `SKILL.md` 硬规则 17（不输出工艺参数） |
| 完整方案设计 | `SKILL.md` 硬规则 17（不做设备选型、不出技术方案） |
| 敏感工艺细节 | `SKILL.md` 硬规则 17 ＋ `references/current-treatment-rules.md`（只写单元名，禁止数值区间） |
| 非公开项目资料 | `references/evidence-policy.md`（FACT 必须有 Source；不得引用非公开来源） |

**明确不做**：不写开发信 · 不写话术 · 不写跟进节奏与时间节点 · 不做联系人评分 · 不进入 SDR 流程。
（以上均属 V1 Freeze 归档区与执行层职责，见 `SKILL.md` 第十三节。）

**Page 2 明细写法**：遵循 `assets/output-card-template.md` 的「**Page 2 明细写法纪律**」——
依据用 `E#` 引用不展开、加问项紧凑排版、检索路径一行平铺；**不得删除任何信息点**。
（原因：Page 2 显示字段完整原文，明细过长会把 Page 2 挤成两页 → 共 4 页。）

---

## 四、硬规则

| # | 规则 |
|---|---|
| 1 | **不得引入数值评分。** 无 100 分制、无权重求和、无 AI 打分。判定为**逐级规则匹配**，规则可完整打印、可人工复核。 |
| 2 | **保守优先。** 规则冲突时取更保守的一档（把 C 误判为 A 的代价远大于漏掉一个 A）。 |
| 3 | **`Unknown` 不得被当作负面信号。** `Risk = Unknown` 本身不导致 `暂不优先`，也不能冒充 `Low`；按第 3/4/5 步的明示条件落档。 |
| 3a | 第 1b 步是**直接竞争的资源优先级**判定，不把 `Risk = Unknown` 改成 `High`，也不把未发现采购证据写成「无采购可能」。 |
| 4 | **一票否决优先于所有加分项。** 风险高不因需求强而降档。 |
| 5 | 结论必须与 `Next Action` 一致。`建议先验证` → Next Action 必须是"去拿那个缺失信息"，不得是"推进小试"；**并须按「三之二 · Next Action 生成要求」给出该类型的首轮加问项**。 |
| 6 | **不得因某个字段看起来更好就跳档。** 逐条对照本文件，不凭整体印象。 |
| 7 | 不得输出金额、折扣、报价条件、产能承诺。 |
| 8 | **`Business Change Signal` 不得作为判定输入。** 它只作背景 / 观察项，不得导致任何档位变化。 |
| 9 | **`FW = Yes` 不得机械降档。** 必须先过第 4b 步四问，并在结论原因中解释。 |
| 10 | **不得用单条负面新闻覆盖更完整的集团财务事实。** 裁员 / 重组 / 厂区亏损属业务变化，不属财务困境。 |
| 11 | **`Next Action` 的加问项必须取自 `must-ask-params.md` 第六节对应组**（映射见「三之二」）；**不得在本文件另立问题清单** —— 单一来源，避免双重维护。 |
| 12 | **`Conflict = Yes` 时，`Next Action` 必须以「先确认合作 / 竞争边界，再进入技术讨论」开头**，并按「三之二」列出本阶段不主动释放范围；**禁止项一律复用现有规则编号，不得新造另一套 `Conflict` 判断标准**。 |
| 13 | **`Next Action` 不得扩展为开发信 / 话术 / 跟进节奏 / 时间节点 / 联系人评分 / SDR 流程** —— 它只回答"下一步最需要确认什么"。 |

### Evidence 标注要求（遵循 `evidence-policy.md`）

| 结论 | 类型 | 要求 |
|---|---|---|
| `Sales Conclusion` 的档位 | **INFERENCE** | 必须有 `Reason`（1~2 句，引用字段取值与规则路径） |
| 一票否决的触发依据 | **FACT** | 必须指向附录 A 的具体证据编号 |
| `Financial Warning = Yes` 的依据 | **FACT** | 必须有 Source（公开财报 / 上市公告 / 政府公示 / 监管披露），且属 `evidence-policy.md` 6.1 白名单类型；来源 `Confidence = Low` 时**必须注明需复核** |
| `Business Change Signal = Yes` 的依据 | **FACT** | 必须有 Source；且**必须**同时输出 `Reason`（见 `evidence-policy.md` 7.2） |
| 输入字段本身为 `Unknown` | **UNKNOWN** | 不得补全；`Unknown` 不导致降档，只影响档位上限判定 |

**禁止**：不得因"感觉这个客户不错"而跳档——本文件是逐条规则匹配，不是主观判断。

---

## 五、示例（对照写法）

### 示例 1 · 分销渠道型

```
输入：Path = Partner / Distributor；BDD Relevance = Medium（渠道覆盖 + 水处理药剂线）
      Demand Status = 无证据；Risk = Unknown；FW = Unknown
      Missing：需求性质、终端行业结构
判定：建议先验证
原因：其水处理药剂线与工业客户覆盖构成渠道机会，但"是自用项目还是渠道分销"未确认；
      先确认真实需求性质与终端行业结构，再决定是否投入。
```

### 示例 2 · 多厂区制造集团型

```
输入：Path = End-user；BDD Relevance = High（制造业确认 + PWE 充分 + 项目信号）
      Demand Status = Public Wastewater Evidence 充分 / Customer-stated Demand 无 → Potential
      Risk = Unknown；FW = No
      Missing：[Project] 目标厂区与项目主体、具体项目及目标工段 [Technical] 水质与水量
判定：建议开发
原因：主体级证据充分（含政府许可与合规文件、在建湿法冶金装置）、风险未观察到高风险信号、
      财务无警示；缺具体项目证据，故未达"重点开发"，需在接触中确认项目存在性。
```

### 示例 2b · 真实财务困境且影响采购（负向对照）

```
输入：Path = End-user；BDD Relevance = High（制造业确认 + PWE 充分）
      Demand Status = Potential
      Risk = Unknown
      FW = Yes（依据：集团公告进入法院主导的债务重组 + 审计报告持续经营重大疑虑，Source：公开财报/监管披露）
      Business Change Signal = Yes（重组中的人员与产能调整）
判定：建议先验证
原因：**财务警示已触发且经第 4b 步判定影响本次采购与付款能力**（风险主体即目标采购主体，
      债务重组直接削弱其签约与付款能力），上限降至本档；
      先复核财务口径与项目预算，再决定是否投入技术资源。
```

### 示例 2c · 业务变化 ≠ 财务警示（**本 Patch 修正的典型**）

```
输入：Path = End-user；BDD Relevance = High（制造业确认 + PWE 充分）
      Demand Status = Potential
      Risk = Unknown
      FW = **No**（集团最新财报盈利、现金流正常、上调业绩指引、分红与回购；无 6.1 白名单证据）
      Business Change Signal = **Yes**（全球裁员、组织架构重组、多套装置关闭、某基地连续亏损）
判定：建议开发
原因：主体级证据充分、行业属目标市场、需求为 Potential、无商业风险与财务困境证据；
      **业务变化信号（裁员 / 重组 / 单厂区亏损）已记录为背景与观察项，不作为降档依据**；
      缺具体项目证据，故未达"重点开发"。
```

### 示例 3 · 需求已确认且无风险

```
输入：Path = End-user；BDD Relevance = High；Demand Status = Confirmed（文件级）
      Risk = Low；FW = No；Missing = None（Business 级无缺项）
判定：建议重点开发
原因：需求有文件级证据、无风险信号、业务层面无缺项，可优先配置资源。
```

---

## 六、与其他文件的职责边界

| 文件 | 负责 |
|---|---|
| **本文件** | Sales Conclusion 五值判定 + 保守优先规则 |
| `bdd-relevance-rules.md` | 提供 BDD Relevance |
| `evidence-policy.md` | 提供 Demand Status · Commercial Risk · Financial Warning（6.1 白名单）· Business Change Signal（只作背景） |
| `must-ask-params.md` | 提供 Missing Critical Information 三级排序 |
| `customer-type-playbook.md` | 提供 Path |
| `output-visual-rules.md` | 颜色语义映射 |

**本文件不引入新判断维度，只做已有字段的规则化汇总。**

---

## 七、待业务方确认

| # | 待确认 | 归属 |
|---|---|---|
| 1 | 五档结论的措辞是否与实际销售口径一致 | 销售 |
| 2 | "建议重点开发"是否要求"Business 级无缺项"（当前设置） | 销售 |
| 3 | 是否需要对 `Distribution Opportunity` 单列一档判据 | 销售 |
| 4 | 一票否决项是否需要增删 | 销售 |
| 5 | `FW = Yes` 第 4b 步四问的判定顺序与权重是否够用 | 销售 / 财务 |
| 6 | `Business Change Signal` 是否需要在业务 PDF 有独立展示位（当前只进 Markdown + 结论原因） | 销售 |
