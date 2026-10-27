> **当前V1.2.1-b**：Partner使用references/partner-judgment-contract.md。保持13字段；竞争状态/合作潜力在BDD机会与结论原因内说明，独立采购意向写Demand明细；附录B嵌入唯一bdd-decision输入，render_pdf实际复算。模板中的旧Conflict示例不能替代证据判断。

# 客户情报卡输出模板（V1.2.1）

> **V1.2.1**：**仅展示层**。PDF 第一页改为「决策 / 行动优先」—— 结论卡 + Next Action + Who to Contact + What Is Missing 置顶，其后为 `01 WHO` / `02 WHY` / `03 WHERE` 三组事实；主卡表格保留「字段 / 判定」表头行。**13 个 Internal Key 全部保留、每项只显示一次（12 个字段行 + 1 张结论卡）**；字段含义、判定值、颜色映射、Page 2 / Page 3 结构、Markdown 输出与归档规则一律不变。Markdown 模板本身**未改动**，详见 `references/output-visual-rules.md` 第九部分。

> **V1.2.0**：13 个主卡字段不变。Partner 的 `Demand Status` 须区别「对外业务活动」与「外部技术/项目需求」；集团证据在附录 B 标主体层级；`Conflict` 分层并说明部件采购切面；`Financial Warning = No` 须注明近期主体级检索覆盖，不足则 `Unknown`。判据见对应 references，模板不另立规则。

> **V1.1.6 · Contact / Next Action Usability Patch（仅改写法与字段内部结构）**
> ① **`关键联系人`** 统一为 `主体（法人 / 业务主体）→（职能单位 →）目标岗位`；**职能单位无公开来源时退化为二段式，不得推测**（`references/contact-role-map.md` 第一节约束 1 / 8 / 9）。
> ② **`关键联系人` 在 `No verified contact found` 时不得停住**，必须附「**建议检索路径**」——只回答"去哪里找这个角色"，**不生成任何人名 / 邮箱 / 电话**（同上第三节情况 C）。
> ③ **`下一步`** 必须接入 `references/must-ask-params.md` **第六节**的类型加问项（**只引用，不另立清单**），主卡留最关键 1 项；`Conflict = Yes` 时**以「先确认合作 / 竞争边界，再进入技术讨论」开头**，并列明本阶段不主动释放范围（**禁止项复用现有规则定义**）。
> ④ **`下一步` 不得**扩展为开发信 / 话术 / 跟进节奏 / 时间节点 / 联系人评分 / SDR 流程。
> **本 Patch 不新增字段、不改 13 个 Internal Key、不改任何判断逻辑**（`BDD Opportunity` / `Demand Status` / `Commercial Risk` / `Sales Conclusion` / `Industry Fit` 全部原样）。

## 结构总览

| 层 | 内容 | 长度上限 | 写给谁 |
|---|---|---|---|
| **第一层** | 主判断卡（**13 固定字段**） | **1 页** | 业务员（30 秒读懂） |
| **第二层 · 附录 A** | Evidence 明细（含 `主题` 展示列） | 不限，折叠 | 复核者 / 存档 / PDF Key Evidence |
| **第二层 · 附录 B** | 审计信息 | 不限，折叠 | 复核者 / 存档 · **不进业务 PDF** |

> **V1.1 设计原则**：**主卡用大白话，专业规则放后层。**
> 主卡不出现"8 项输入""封顶规则"这类内部术语；它们全部在附录与参考文件中。
>
> **V1.1.3**：审计与边界信息集中到 **附录 B**，渲染时**不进业务 PDF**；Markdown 中原文一字不删。

**颜色语义见 `references/output-visual-rules.md`（唯一来源）。**

### Markdown → 业务 PDF 三页对应（V1.1.3）

| PDF 页 | 取自 Markdown |
|---|---|
| Page 1 `Customer Snapshot ｜客户快照` | 主卡四组 + 结论卡（**与 V1.1.2 完全一致，未改动**） |
| Page 2 `SALES INTELLIGENCE ｜开发情报` | 5 张销售信息卡：Why BDD ← 「BDD Opportunity 判定依据 + Demand Status 明细」；Current Treatment / Priority Site / Who to Contact / What to Verify ← 对应字段**完整原文** |
| Page 3 `KEY EVIDENCE ｜关键依据` | 附录 A 表格 → 取 `Decision Impact` 前 6~8 条，每条只呈现 **编号 · 主题 / 简洁事实 / Source** |
| **不进 PDF** | 附录 B（审计信息）与 `## 边界声明` |

---

## 第一层 · 主判断卡（13 字段 · 四组呈现）

> **V1.1.1**：13 个 Internal Key **完全不变**，新增中英文 Display Label；字段按
> **WHO → WHY → WHERE/WHO → ACTION** 四组排列；`Sales Conclusion` 移出表格成为结论卡。
> 分组只改**呈现顺序与标题**，不改任何判定。

```markdown
# {Company} · BDD Customer Intelligence

{YYYY-MM-DD} | 来源：{输入形式：询盘原文 / 公司名 / 官网 / 名片}
执行版本：BDD Customer Intelligence Skill V1.2.1

## 第一层 · 主判断卡

### WHO · 客户是谁

| 字段 | 判定 |
|---|---|
| **公司 Company** | {登记全称}（{国家 / 地区}）· {Verified / Partially Verified / Unverified} |
| **国家 Country** | {国家} · {主要运营地区} |
| **主营业务 Business** | {一句话：这家公司是做什么的，用业务员能转述的话} |
| **客户类型 Customer Type** | {类型} · {Path: End-user / Partner·子类型 / Undetermined} |

### WHY · 为什么值得看

| 字段 | 判定 |
|---|---|
| **行业匹配 Industry Match** | {🟢 Target / 🔵 Adjacent / 🔴 Outside / ⚪ Unknown} |
| **BDD机会 BDD Opportunity** | {🟢 High / 🟡 Medium / 🔴 Low / ⚪ Unknown} · {Opportunity Type} |
| **需求状态 Demand Status** | {🟢 Confirmed / 🟢 Strong Signal / 🟡 Potential / 🔴 Weak / ⚪ Unknown} |

### WHERE / WHO · 从哪里切入

| 字段 | 判定 |
|---|---|
| **现有废水处理 Current Treatment** | {🟢 已确认 Confirmed / 🟡 部分确认 Partial / 🔵 规划中 Planned / ⚪ 未知 Unknown} · {End-user：现有处理方案单元 / Partner：可提供的技术组合}⟪P2⟫{移到 Page 2 的细节} |
| **优先厂区 Priority Site** | {厂区名（国家）· 一句话理由 / N/A} |
| **关键联系人 Contact** | {主体（法人 / 业务主体）} → {职能单位（无公开来源则省略，**不得推测**）} → {目标岗位} {/ 具名 + 职位 + Source} {/ No verified contact found ＋ 建议检索路径} |

### ACTION · 现在怎么办

| 字段 | 判定 |
|---|---|
| **待确认信息 Missing Info** | [Business] {…}　[Project] {…}　[Technical] {…}　/ None |
| **下一步 Next Action** | {核心动作一句话}＋{该类型首轮最关键加问 1 项}；{`Conflict = Yes` 时以「先确认合作 / 竞争边界，再进入技术讨论」开头} |

> **开发建议 Sales Conclusion**
>
> {🟢 | 🟡 | 🔴 | ⚪} **{建议重点开发 / 建议开发 / 建议先验证 / 暂不优先 / 信息不足，暂缓判断}**
>
> {1~2 句原因}

**BDD Opportunity 判定依据**

- Reason: {已确认什么 / 缺什么}
- Evidence: {E# / E# …}
- Confidence: {High / Medium / Low}
- Opportunity Type: {五值之一，复合时用 " +| " 连接}

**Demand Status 明细**

- Public Wastewater Evidence: {等级} — {一句话；Partner 须写明是外部技术需求还是一般业务活动；集团证据注明层级}（E#）
- Customer-stated Demand: {等级} — {一句话}（客户自述 / E#）
- → 取较高者：{等级}

**风险**

- Commercial Risk: {🟢 Low / 🟡 Medium / 🔴 High / ⚪ Unknown}
- Risk Note: {可选，一句话}
- Financial Warning: {🟢 No / 🔴 Yes / ⚪ Unknown}　← {主体层级、检索渠道与时间；`No` 仅表示足够覆盖下未见白名单警示}

**业务变化（Context / Watch Item，不参与降档）**

- Business Change Signal: {🟢 No / 🟡 Yes / ⚪ Unknown}
- Reason: {发生了什么变化，一句话；`Yes` 时必填}
- Source: {公开来源；`Yes` 时必填}
```

---

## Display Label 对照（**Internal Key 不变**）

| # | Internal Key（保持不变） | Display Label（主卡显示） | 组 |
|---|---|---|---|
| 1 | `Company` | 公司 Company | WHO |
| 2 | `Country` | 国家 Country | WHO |
| 3 | `What They Do` | 主营业务 Business | WHO |
| 4 | `Customer Type` | 客户类型 Customer Type | WHO |
| 5 | `Industry Match` | 行业匹配 Industry Match | WHY |
| 6 | `BDD Opportunity` | BDD机会 BDD Opportunity | WHY |
| 7 | `Demand Status` | 需求状态 Demand Status | WHY |
| 8 | `Current Wastewater Treatment / Technology` | 现有废水处理 Current Treatment | WHERE / WHO |
| 9 | `Priority Site` | 优先厂区 Priority Site | WHERE / WHO |
| 10 | `Who to Contact` | 关键联系人 Contact | WHERE / WHO |
| 11 | `What Is Missing` | 待确认信息 Missing Info | ACTION |
| 12 | `Next Action` | 下一步 Next Action | ACTION |
| 13 | `Sales Conclusion` | 开发建议 Sales Conclusion（**结论卡**） | ACTION |

> Display Label 只用于显示；脚本校验与规则引用一律用 Internal Key。
> 完整规则见 `references/output-visual-rules.md` 第二部分。

---

## 字段填写规则（大白话要求）

> 下表用 **Display Label** 指代，规则中的字段名仍以 Internal Key 为准（见上方对照表）。

| 字段（Display Label） | 规则 |
|---|---|
| **公司 Company** | 登记全称 + 核实三态。名称有歧义 → `Unverified`，**不得选最像的一家** |
| **国家 Country** | 只写国家 + 主要运营地区。跨国集团写"总部所在国 + 主要制造分布" |
| **主营业务 Business** | **一句话，用业务员能转述的话。** 不堆术语。例如："德国水处理设备公司，自己造设备、也自己生产水处理药剂" |
| **客户类型 Customer Type** | 类型 + **Path**。Path 必须显式写出：`End-user` / `Partner·EPC` / `Partner·Integrator` / `Partner·Distributor` / `Partner·Technology Partner` / `Undetermined` |
| **行业匹配 Industry Match** | 对照 `bdd-fit-rules.md` 最小目标市场地图。带颜色 |
| **现有废水处理 Current Treatment** | **必须带状态徽标**（四态，见下）。End-user 写"现在用什么处理"；Partner 写"能提供哪些技术"。**只写单元名，不写数值。** 查不到 → `⚪ Unknown · Unknown` |
| **BDD机会 BDD Opportunity** | 四档 + **Opportunity Type**。复合类型写 `主 +| 副`。已证实直接替代才标 `Conflict = Yes`；应用重叠标Unknown/Partial并解释 |
| **需求状态 Demand Status** | 主卡只写**较高者**；两类的明细写在下方"Demand Status 明细" |
| **优先厂区 Priority Site** | **仅 ≥ 3 个公开厂区的集团使用**；否则写 `N/A` |
| **关键联系人 Contact** | **`主体（法人 / 业务主体）→（职能单位 →）目标岗位`** —— 三段式首选；**职能单位无公开来源 → 退化为二段式，不得推测部门名称**。可选具名 + 职位 + Source。**查不到真人时不得停住**：输出 `No verified contact found` ＋「**建议检索路径**」（**只回答去哪里找，不生成任何人名 / 邮箱 / 电话**）。**存在具名但非目标岗位时**按「**部分具名**」处理：具名者标为 Known / Escalation，**Primary Contact 仍须显示目标角色 + `No verified contact found`**。规则见 `references/contact-role-map.md` 第一、三节（情况 A / A′ / B / B′ / C） |
| **待确认信息 Missing Info** | **按 Business → Project → Technical 排列**，最多 5 项，前缀标级别。齐全 → `None` |
| **下一步 Next Action** | ① **核心动作一句话**（**不得写"邀请寄样小试"**；已确认具体项目时写"转交技术评估流程"）② **该类型最关键的首轮加问项 1 项**（取自 `references/must-ask-params.md` 第六节，**只引用、不另立清单**）③ **`Conflict = Yes` 时必须以「先确认合作 / 竞争边界，再进入技术讨论」开头**。**不得**写成开发信 / 话术 / 跟进节奏 / 时间节点 / 联系人评分 |
| **开发建议 Sales Conclusion** | 五值之一 + 1~2 句原因。取值规则见 `sales-conclusion-rules.md`。**渲染为结论卡，置于第一页四组之后** |

### 风险块与业务变化块（主卡下方固定小块）

| 项 | 规则 |
|---|---|
| **Commercial Risk** | `Low / Medium / High / Unknown`。**只用可观察事实**；`Unknown` ≠ `High`；类型级先验只作 `Risk Note` |
| **Financial Warning** | `Yes / No / Unknown`。`Yes` 只认财务困境白名单；`No` 须有近期可靠的目标主体级检索覆盖；无财报/登记渠道或只查普通网页为 `Unknown`。`No` 不是财务健康评级；裁员 / 重组 / 高管变化 / 厂区亏损 / 降本计划不触发 `Yes` |
| **Business Change Signal** | `Yes / No / Unknown`。纳入裁员 / 高管变化 / 组织架构调整 / 业务单元调整 / 工厂整合 / 产能调整 / 业务组合调整 / 战略转型 / 单一厂区经营亏损 / 降本计划。**判 `Yes` 必须写 `Reason` + `Source`** |
| **两者的关系** | **业务变化 ≠ 财务困境。** `Business Change Signal = Yes` 不得单独触发 `FW = Yes` / `Commercial Risk = High`，也不得导致任何字段降档 —— 只作 **Context / Watch Item** |
| **集团 vs 厂区** | 厂区 / 业务单元的亏损、裁员、产能调整 → 归 `Business Change Signal`，**不得**推出集团 `FW = Yes` |
| **证据冲突** | 同时存在「裁员 / 重组 / 厂区亏损」与「集团盈利 / 正常现金流 / 上调指引 / 分红 / 回购」时：**优先判 `Business Change Signal = Yes`**，`FW` 按主体级检索覆盖与白名单定级；**不得用单条负面新闻覆盖集团财务事实** |

### `Current Treatment` 状态徽标（四态 · **只能来自现有证据**）

| 徽标（V1.1.2 中文显示） | 判据（**必须有一个 E# 支撑**） |
|---|---|
| `🟢 已确认 Confirmed` | 证据明确载明**已建成 / 在运行 / 在售交付**的处理单元或工艺组合 |
| `🟡 部分确认 Partial` | 证据只覆盖**部分环节**（仅单个单元、工艺组合不完整），或原文含"部分厂区 / 部分工艺"限定 |
| `🔵 规划中 Planned` | 证据明确表述为**规划 / 拟建 / 在建**，尚未投运 |
| `⚪ 未知 Unknown` | 无相关证据（**不得据"这类厂应该有"填**） |

**四态硬规则**

| # | 规则 |
|---|---|
| 1 | 无 E# 支撑 → `Unknown` |
| 2 | 证据为计划 / 拟建 / 在建 → **只能** `Planned`，不得写 `Confirmed` |
| 3 | 覆盖不完整 → `Partial`，不得升为 `Confirmed` |
| 4 | **状态不参与任何判断字段**，也不与 `BDD Opportunity` 联动 |
| 5 | Partner Path 下状态指"可提供 / 在交付"的能力，不适用"自身废水"口径 |

### 第一页长字段压缩标记 `⟪P2⟫`（V1.1.2）

对下列 **5 个长字段**，在 Markdown 中写成：

```
{第一页摘要}⟪P2⟫{完整内容的其余部分}
```

| 字段（Display Label） | 第一页保留 | 移到 Page 2 |
|---|---|---|
| 现有废水处理 Current Treatment | 核心技术组合（单元名） | 官网描述、监测数据、集团目标 |
| 优先厂区 Priority Site | 厂区 + 最关键理由 | 许可细节、备选厂区、日期 |
| 关键联系人 Contact | `主体 →（职能单位 →）目标岗位` | 具名 / 职位 / Source、**建议检索路径**、职能单位退化的说明 |
| 待确认信息 Missing Info | 各级最关键的 1 项 | 完整三级清单 |
| 开发建议 Sales Conclusion（原因） | 结论 + 1 句最关键原因（≤3 行） | 完整原因、证据编号、数字 |
| 国家 Country | 国家 + 主要运营地 | 站点数、子公司国别 |
| 主营业务 Business | 主营业务一句话 | 工艺细节、板块构成 |
| 行业匹配 Industry Match | 状态值 | 目标市场分组与口径说明 |
| 下一步 Next Action | 核心动作 ＋ 首轮加问 1 项 | **完整加问项**（引用 `must-ask-params.md` 第六节对应组）、`Conflict = Yes` 时边界提示的完整表述与本阶段不释放范围、前置条件 |

> **摘要是原文的精确前缀**：`⟪P2⟫` 之后的内容进 Page 2，两者相加 = 完整原文。

**硬规则**

| # | 规则 |
|---|---|
| 1 | **禁止删除底层完整内容** —— Markdown 里一字不删。 |
| 2 | 摘要**必须逐字取自原文**，不得新增或改写。 |
| 3 | 只影响 **PDF 第一页** 展示；Markdown 与 Page 2 保留完整原文。 |
| 4 | `⟪P2⟫` 是**版式标记**，不是判断标记，不得影响任何取值。 |
| 5 | **V1.1.3**：PDF Page 2 的对应信息卡显示该字段**完整原文**（摘要 + 其余），因此 Page 2 可独立读懂，不依赖 Page 1。 |

---

### Page 2 明细写法纪律（**V1.1.6 新增 · 只压缩排版与引用方式，不删信息点**）

> **为什么需要**：Page 2 显示的是字段**完整原文**，所以**字段明细过长会把 Page 2 本身挤成两页** ——
> 4 页的结构表现为 `p1 客户快照 / p2 开发情报 / p3 开发情报（续） / p4 关键依据`。
> **此时压缩 Page 1 摘要完全无效**（已实测三种改法全部失败），**必须压缩 Page 2 明细**。

| # | 纪律 |
|---|---|
| 1 | **依据用引用，不展开**：引用 `E#` 证据编号或「`文件名` ＋ 小节」，**不整段复述来源原文**，**也不逐项重复罗列同一依据的规则编号**（同一组依据只在末尾引用一次） |
| 2 | **加问项紧凑排版**：同组加问项在**同一行**内以全角空格分隔，**不逐项换行** |
| 3 | **检索路径一行平铺**：六项固定路径用 ` ｜ ` 串成一行，**不逐条编号换行** |
| 4 | **不删信息点**：允许压缩表述、合并重复引用；**不得删除事实、编号、限定条件与判断口径括注**（如"按规则退化为二段式"） |
| 5 | **不变量**：Page 1 结构、13 个 Internal Key 与**所有判断结果不受本纪律影响** |
| 6 | **适用对象**：`⟪P2⟫` 之后的所有字段明细，重点为 `关键联系人` / `下一步` / `现有废水处理` / `优先厂区` |

**篇幅预算（**当前模板的经验预算** · 2026-09-29 实测 —— 非绝对物理上限）**

> 计量口径：12 个主卡字段 `⟪P2⟫` **之后**的字符数之和（不含摘要、不含附录）。
> **该预算只用于提前预警与排序压缩优先级；是否溢出，最终判定始终以实际 PDF 渲染结果为准。**

| 区间 | 判定 | 动作 |
|---|---|---|
| **≤ 3,800 字符** | 正常 | 按常规写法出卡，渲染后确认页数即可 |
| **3,801 – 4,000 字符** | **警戒区** | **必须执行 PDF 渲染检查**，确认是否为 3 页；若已溢出，按以下纪律压缩 |
| **> 4,000 字符** | **高溢出风险** | **优先进行紧凑化处理**，再渲染确认 |

| 项 | 内容 |
|---|---|
| 实测依据 | **4,012 字符 → 3 页（通过）**；**4,862 字符 → 4 页（溢出）** |
| 压缩顺序 | **按上表纪律压缩最长的字段**，通常依次为 `现有废水处理` ≈ `主营业务` ≈ `关键联系人` ≈ `公司` > `优先厂区` ≈ `待确认信息`；**不得删除信息点** |
| **无效做法（已实测三种全部失败）** | 只压缩 **Page 1 摘要** —— 因为 Page 2 显示的是字段**完整原文**，摘要长短不影响 Page 2 高度 |
| 判断方法 | 渲染后若为 4 页，且结构为 `p1 客户快照 / p2 开发情报 / p3 开发情报（续） / p4 关键依据` → **根因在 Page 2，按本表处置** |

---

## 主卡禁止项（V1.1）

| 禁止 | 原因 |
|---|---|
| 出现"8 项输入""封顶规则""判据①"等内部术语 | 主卡写给业务员，不写给规则维护者 |
| 主卡超过 1 页 | 30 秒可读约束 |
| 用 `Unknown` 的推测内容填满模板 | 制造虚假完整度 |
| 把 FACT 与 INFERENCE 混在同一格 | 幻觉主要来源 |
| 因 Industry Match = Target 直接给 BDD Opportunity = High | 最重要的一条禁止 |
| 因行业是 Lithium Battery 就自动给 `High` | 必须由主体级证据支撑 |
| 有 ETP / ZLD 就判 `Low` | 已有设施 ≠ 无机会 |
| Partner Path 按"自身废水"评判 | 口径错 |
| `Commercial Risk = Unknown` 写成 `High` | 修复项 |
| 输出工艺参数 / 设备选型 / 技术方案 / 达标承诺 / 金额 | 安全边界 |
| 输出 Technical Fit / Quotation Readiness | 已移出职责 |
| **输出"建议小试" / 固定"寄 5~10 L 水样" / 自动进入小试流程** | **V1.1 已删除，属越界** |
| 输出回复草稿 / 跟进节奏 | 已移出职责 |
| 生成未经公开来源验证的具体人名 / 电话 / 邮箱 | 合规风险 |
| 颜色与取值不一致，或用颜色表达程度 | 破坏横向可比 |
| `UNKNOWN` 不带三态后缀 | 无法区分"查了没有"与"没渠道可查" |
| **「有裁员 / 重组 / 高管变化 / 厂区亏损」→ 直接判 `Financial Warning = Yes`** | **业务变化 ≠ 财务困境（FW Rule Patch）** |
| **`FW = Yes` → 机械把 `Sales Conclusion` 降一档** | 必须经四问并解释为什么影响本次判断 |
| **用 `Business Change Signal = Yes` 单独把任何字段降档** | 它只是 Context / Watch Item |
| **用单条负面新闻覆盖更完整的集团财务事实** | 证据冲突处理规则 |

### 展示层禁止项（V1.1.1）

| 禁止 | 原因 |
|---|---|
| 调换四组顺序（WHO → WHY → WHERE/WHO → ACTION） | 阅读链路固定，为业务员翻查习惯而设 |
| 删除结论卡，或把结论卡移到第 2 页 | 第一眼要看的就是"值不值得投入" |
| 结论卡新增建议 / 行动项 / 评分 / 话术 | 展示层不产生判断 |
| 给 `Current Treatment` 填无 E# 支撑的状态 | 状态只能来自现有证据，不得推断 |
| 把"规划 / 在建"写成 `Confirmed` | 未投运 ≠ 已建成 |
| 用 Display Label 替代 Internal Key 做校验或规则引用 | Internal Key 是唯一权威标识 |
| 在展示层改写、润色、补全任何字段内容 | 渲染层只做格式转换 |
| 新增第 14 个字段 / 新增评分 / 新增 CRM 功能 | 越界 |

### 展示层禁止项（V1.1.3 Sales Usability）

| 禁止 | 原因 |
|---|---|
| 改动 PDF Page 1 的任何内容或样式 | 本次 Patch 明确要求 Page 1 完全不变 |
| Page 2 使用大型字段表，或新增第 6 张信息卡 | 只保留 5 张销售信息卡 |
| 修改 Page 2 五张卡的标题文字 | 标题为固定版式标签 |
| 改写字段正文（缩写、润色、合并） | 正文为字段原文搬运 |
| Page 3 显示 `FACT` / `INFERENCE` / `UNKNOWN` / `Confidence` / `Decision Impact` | 审计术语不进业务 PDF |
| Page 3 超出 8 条关键依据 | 一页内 + 只列真正影响销售的 |
| 把审计 / 边界信息（附录 B 内容）渲染进业务 PDF | 审计信息只在 Markdown 保留 |
| 因删除 PDF 展示而删除 Markdown 中的底层 Evidence | 底层证据一字不删 |

---

## 第二层 · 附录 A · Evidence 明细（折叠区）

```markdown
<details>
<summary>附录 A · Evidence 明细（{N} 条）</summary>

| # | 主题 | 类型 | 结论 | Source | Reason | Confidence | Decision Impact |
|---|---|---|---|---|---|---|---|
| E1 | {展示短标题} | FACT | {内容} | {URL / 客户自述} | — | High | High |
| E2 | {展示短标题} | INFERENCE | {内容} | — | {推断理由} | Medium | Medium |
| E3 | {展示短标题} | UNKNOWN · searched | {未查到的项} | — | — | — | Low |

</details>
```

影响主体身份、需求、Partner Gate、竞争或结论的 FACT，`Source` 写具体页面/文件标题、URL（或官方文号/登记号）、发布/访问日期和所指主体；仅填「官网」「多源检索」不合格。PDF 可缩写来源，完整信息保留在本附录。

**否定事实复核**：仅从目录或项目页没有看到 BDD/AOP 等技术时，写 `UNKNOWN · searched` 并说明查过的页面；不要写成「没有该技术」「无竞争」「可直接互补」。渲染器只能核对结构，不能替代人工核验来源的实际含义。

**`主题` 列（V1.1.3 新增的展示标签，非判断字段）**

| 规则 | 说明 |
|---|---|
| 作用 | 供业务 PDF 的 **Key Evidence 卡片** 做标题行；**不参与任何判断** |
| 写法 | ≤ 20 字的**中性短标题**（如「废水处理设施与运行沿革」），不得写结论、不得写评价 |
| 缺失时 | 渲染层只显示证据编号，**不得推断补写** |
| 编号 | `E1`、`E2`… 顺序编号；主卡 `Evidence` 字段与 `Priority Site` 引用这些编号 |

---

## 第二层 · 附录 B · 审计信息（**仅 Markdown，不进入业务 PDF**）

```markdown
---

## 附录 B · 审计信息（仅 Markdown，不进入业务 PDF）

**可溯源率**：{已标注 Source 的 FACT 数} / {FACT 总数}　目标 100%

**类型定义**：FACT 必须有 Source；INFERENCE 必须有 Reason + Confidence；
UNKNOWN 必须带三态后缀（`searched` / `no source` / `not searched`），不得补全。

**Decision Impact**：High / Medium / Low —— 只影响展示优先级，不影响真实性判断，与类型、Confidence 正交。

**集团级 vs 目标主体/厂区级说明**：{A～F、需求与财务证据分别属于谁；集团合同/技术许可是否点名或授权目标主体；同一交易只计一次}

**Partner 需求与业务活动**：{哪些事实只证明对外销售/目录/订单，哪些证据指向目标主体当前相关外部技术需求；只有前者时 Demand Status = Unknown}

**`Conflict` 记录（固定小节 · 唯一写法）**

| 项 | 值 | 理由 |
|---|---|---|
| `Conflict` | **`Unknown`**（`Integration overlap; substitution not verified`） | {一句话理由 + E#；子类未证实时写「未证实同域专有产品」} |

> **写法硬约束（防解析返工 · 2026-10-13 成本优化 Patch 1）**：
> ① **值只写 `**`Yes`**` / `**`No`**` / `**`Unknown`**`** —— 加粗 + 反引号，三值之一；
> ② **子类写在状态值之外**，用全角括号括注：`**`Unknown`**（`Integration overlap; substitution not verified`）`；
> ❌ 错例：`**`Yes`（Integration overlap）**`（子类写进加粗内）· `**Yes（Integration overlap）**`；
> ③ 子类按本次证据填写：`Direct competitor` / `Integration overlap` / `Component procurement` / `Competition and cooperation` / `Complementary Opportunity` / `Insufficient substitution evidence`；无子类写 `（无）` 或省略括注；
> ④ **一张卡只写一条 `Conflict` 标准行**；「与历史版本差异」对比表另起一行，**首格改写 `Conflict 取值`**（不要再用 `Conflict`，避免与标准行同格名）。
> ⑤ 本节**只记事实与子类**，不改变 `BDD Opportunity` / `Sales Conclusion` 的任何判定（判据见 `references/bdd-relevance-rules.md` 第五节）。

**Conflict 子类与采购切面**：{Direct competitor / Integration overlap / Component procurement；各自 E#；未检索写 not searched，不把未见写成无可能}

**同名主体排除**：{排除过程；无则写"未发现需排除的无关同名主体"}

**来源冲突项**：{冲突字段两条都列，照录未择一}

**UNKNOWN 三态汇总**：`searched` {N} 条 / `not searched` {N} 条 / `no source` {N} 条

## 边界声明

本次执行未输出：工艺参数、设备选型、技术方案、达标承诺、金额、报价状态、回复草稿、跟进节奏。
`Technical Fit` 与 `Quotation Readiness` 按范围冻结规定**不输出**。
**未输出"建议小试"，未固定"寄 5~10 L 水样"**（V1.1 已删除该越界规则）。
```

**渲染层切分规则**：从 `## 附录 B` 或 `## 边界声明` 起，直至文末 —— **不进入业务 PDF**，Markdown 中原文一字不删。

**附录 B 不得省略的固定段**

| 段 | 内容 |
|---|---|
| 可溯源率 | 已标注 Source 的 FACT 数 / FACT 总数 |
| 排除项 | 同名主体排除的核实过程（若有） |
| 冲突项 | 来源冲突的字段（两条都列） |
| UNKNOWN 汇总 | 三态分类，说明"查了没有"≠"没有" |
| 边界声明 | 本卡不输出什么 |

---

## 分组输出（按输入信息量自动调整）

| 用户提供了什么 | 输出什么 |
|---|---|
| 完整询盘原文 + 公司名 | 完整两层结构（13 字段全填，可含 CSD） |
| 只有公司名 / 官网 | 完整两层结构；`Demand Status` 主要来自 PWE；`What Is Missing` 优先 Business 级 |
| 只有询盘原文，无公司名 | 主卡（`Company` 标客户自述 + `Unverified`）+ 附录 A 标注"需公司名方可检索" |
| 只有官网网址，无公司名 | 先做主体识别；能唯一确定 → 正常输出；不能 → `Unverified` + Business 级缺项 |
| 信息极少 | 主卡如实填 `⚪ Unknown`，`Sales Conclusion = ⚪ 信息不足，暂缓判断`。**不硬凑分析** |

---

## 填写示例（说明大白话风格）

> 以下为**虚构示例**：公司名、厂区、数据均为占位内容，仅用于示范字段写法与大白话风格。

```markdown
# Sample Chemicals · BDD Customer Intelligence

YYYY-MM-DD | 来源：公司名 + 官网
执行版本：BDD Customer Intelligence Skill <当前版本>

## 第一层 · 主判断卡

### WHO · 客户是谁

| 字段 | 判定 |
|---|---|
| **公司 Company** | SAMPLE CHEMICALS LTD（示例国）· Verified |
| **国家 Country** | 示例国 · 某州注册，总部位于某市 |
| **主营业务 Business** | 精细化学品制造商，做有机中间体，多个制造基地，出口占比较高 |
| **客户类型 Customer Type** | 终端业主 · End-user |

### WHY · 为什么值得看

| 字段 | 判定 |
|---|---|
| **行业匹配 Industry Match** | 🟢 Target（T4 精细化工，且产生高 COD 难降解废水） |
| **BDD机会 BDD Opportunity** | 🟢 High · End-user Opportunity |
| **需求状态 Demand Status** | 🟡 Potential |

### WHERE / WHO · 从哪里切入

| 字段 | 判定 |
|---|---|
| **现有废水处理 Current Treatment** | 🔵 Planned · 物化 + 生化 + 膜 + 多效蒸发；部分厂区已 ZLD、其余在推进（**部分厂区仍在推进，属规划口径**） |
| **优先厂区 Priority Site** | `<厂区名>`（示例国 · 某州）· 有政府合规报告载明废水设施与月废水产生量，且废水回用项目在该厂区推进 |
| **关键联系人 Contact** | SAMPLE CHEMICALS LTD → 环保负责人 / EHS 负责人（首选）<br>（本例**无公开来源可确认职能单位** → 按规则退化为二段式，**不推测部门名**）<br>`<岗位名称>`｜Source: 官网 |

> **联系人写法纪律（V1.1.6）**：输出**主体 →（职能单位 →）岗位**，职能单位**必须有公开来源**，否则退化为二段式。人名**仅可**来自官网 / 政府公示 / 招投标 / 上市公告 / 官方媒体；第三方聚合站（人才库 / 数据聚合站）人名**一律弃用**。
> **查不到具名时不得停住** —— 必须附「**建议检索路径**」（官网组织页 / 官方公告年报 / 招投标公开联系人 / 行业协会名录 / 展会参展商资料 / LinkedIn 等公开职业信息），**只给路径，不给姓名、邮箱、电话**。详见 `references/contact-role-map.md` 第三节情况 C。

### ACTION · 现在怎么办

| 字段 | 判定 |
|---|---|
| **待确认信息 Missing Info** | [Business] ① 是否存在具体废水治理项目的需求方与决策链　[Project] ② 目标工段（新建 / 提标 / 高浓母液）③ 项目阶段与时间节点　[Technical] ④ 目标污染物浓度与水量 |
| **下一步 Next Action** | 先向 EHS 负责人确认是否存在具体提标或高浓母液处理项目及目标工段；若确认存在项目，转交技术评估流程。**首轮加问（B 组）**：目标工段（新建 / 提标 / 高浓母液 / 水回用）？ |

> **开发建议 Sales Conclusion**
>
> 🟡 **建议先验证**
>
> 　企业级废水证据充分、行业属目标市场，但尚无具体项目证据、需求方未确认；先补 Business / Project 级信息再决定投入

**BDD Opportunity 判定依据**

- Reason: 主体级证据充分——多个制造单元已确认、官网载明主导工艺段、已建 ZLD 与未闭环厂区并存、政府合规报告含废水分析、环境改善专项资本开支、EHS / ETP 岗位持续招聘；缺具体项目证据
- Evidence: E4 / E5 / E6 / E8 / E12 / E13 / E14 / E15 / E16
- Confidence: High
- Opportunity Type: End-user Opportunity

**Demand Status 明细**

- Public Wastewater Evidence: Potential — 官网与政府合规报告载明现有设施与运行数据，但无具体项目
- Customer-stated Demand: Unknown — 本次无询盘文字
- → 取较高者：Potential

**风险**

- Commercial Risk: ⚪ Unknown
- Risk Note: 无往来内容可供观察；类型级先验不参与定级
- Financial Warning: 🟢 No（上市公司公告显示盈利，无白名单财务困境证据）

**业务变化（Context / Watch Item，不参与降档）**

- Business Change Signal: 🟡 Yes
- Reason: 全集团组织架构调整与人员优化计划，个别厂区连续亏损
- Source: 公司公告 / 官方新闻稿
```

> **说明**：`Industry Match` 输出 `Target`（V1.1 起地图已填）；
> `BDD Opportunity` 输出 `High`——**不再因"无询盘"封顶 `Medium`**（该封顶规则 V1.1 已删除）。
> 示例中 `Current Treatment` 状态标 `🔵 Planned`：因证据含"部分厂区仍在推进、尚未全部投运"——**部分未投运 → 属规划口径，不得标 `Confirmed`**。
> 若证据全部为已建成、且覆盖完整，则标 `🟢 Confirmed`；仅覆盖部分环节则标 `🟡 Partial`。
