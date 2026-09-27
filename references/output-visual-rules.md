# Output Visual Rules · 颜色语义与 PDF 导出（V1.1 / V1.1.1）

**回答的问题**：情报卡怎么呈现，业务员能 30 秒读懂；存档版 PDF 长什么样。

> **V1.1.1 Presentation Patch**：本文件新增第二部分「展示层（Presentation Layer）」。
> 该部分**只定义展示**：显示标签、分组、状态徽标、结论卡样式。
> **不修改任何判断规则**，不新增字段，不新增评分。
> Internal Key 与全部判断逻辑保持 V1.1 原样。

---

## 第一部分 · 固定颜色语义

### 一、五色定义（**唯一来源，不得扩展**）

| 颜色 | 语义 | 用于 | 标记 |
|---|---|---|---|
| 🟢 **绿** | Confirmed / Positive / High relevance | 已确认的事实 · 高相关性 · 无风险的正面结论 | `🟢` |
| 🟡 **黄** | Potential / Needs validation | 待验证 · 潜力型 · 需先补信息 | `🟡` |
| 🔴 **红** | Risk / Negative / Conflict | 风险 · 负面 · 冲突（含潜在竞争） | `🔴` |
| ⚪ **灰** | Unknown | 未查到 / 无法判断 | `⚪` |
| 🔵 **蓝** | Neutral facts | 中性事实（描述性、不表态） | `🔵` |

### 二、字段 → 颜色映射

| 字段 | 取值 → 颜色 |
|---|---|
| **Customer Type** | End-user / Partner → 🔵；`Unconfirmed` → ⚪ |
| **Industry Match** | `Target` → 🟢；`Adjacent` → 🔵；`Outside` → 🔴；`Unknown` → ⚪ |
| **Current Wastewater Treatment / Technology** | **状态徽标（V1.1.1 四态）**：`Confirmed` → 🟢；`Partial` → 🟡；`Planned` → 🔵；`Unknown` → ⚪<br>**正文技术组合**：中性描述 → 🔵（与徽标解耦） |
| **BDD Opportunity**（四档） | `High` → 🟢；`Medium` → 🟡；`Low` → 🔴；`Unknown` → ⚪ |
| **BDD Opportunity**（Opportunity Type） | 有明确类型 → 🔵；`Unknown` → ⚪；含 `Conflict` → 🔴 |
| **Demand Status** | `Confirmed` / `Strong Signal` → 🟢；`Potential` → 🟡；`Weak` → 🔴；`Unknown` → ⚪ |
| **Commercial Risk** | `Low` → 🟢；`Medium` → 🟡；`High` → 🔴；`Unknown` → ⚪ |
| **Financial Warning** | `No` → 🟢；`Unknown` → ⚪；`Yes` → 🔴（**不设黄色档**） |
| **Priority Site** | 有 → 🟢；`N/A` → ⚪ |
| **What Is Missing** | 按级：Business → 🔴；Project → 🟡；Technical → 🔵 |
| **Who to Contact** | `No verified contact found` → ⚪；有具名 → 🟢 |
| **Sales Conclusion** | 建议重点开发 / 建议开发 → 🟢；建议先验证 → 🟡；暂不优先 → 🔴；信息不足 → ⚪ |
| **Evidence 类型** | FACT → 🔵；INFERENCE → 🟡；UNKNOWN → ⚪ |

### 三、硬规则

| # | 规则 |
|---|---|
| 1 | **禁止 100 分制、AI 评分、星级、加权总分。** 颜色只表达**类别语义**，不表达程度。 |
| 2 | **禁止渐变、阴影、拟物化。** 只用纯色块 + 文字标签。 |
| 3 | **颜色不是唯一信息载体。** 每个色块必须同时带文字（如 `🟢 High`），保证打印 / 色盲可读。 |
| 4 | **不得为"看起来更好"而改色。** 颜色由字段取值机械映射，不人工调整。 |
| 5 | 同一取值在所有公司卡上颜色必须一致——**保证横向可比**。 |

---

## 第二部分 · 展示层 Presentation Layer（V1.1.1 新增）

> **范围声明**：本部分只规定**怎么显示**。
> **13 个 Internal Key 完全不变**，判断结论一字不改。展示层**不得**产生任何新的判断结果。

### 一、Display Label 映射（**Internal Key 不变，仅新增显示标签**）

| # | Internal Key（**保持不变，勿改**） | Display Label（新增显示） | 所属组 |
|---|---|---|---|
| 1 | `Company` | **公司 Company** | WHO |
| 2 | `Country` | **国家 Country** | WHO |
| 3 | `What They Do` | **主营业务 Business** | WHO |
| 4 | `Customer Type` | **客户类型 Customer Type** | WHO |
| 5 | `Industry Match` | **行业匹配 Industry Match** | WHY |
| 6 | `BDD Opportunity` | **BDD机会 BDD Opportunity** | WHY |
| 7 | `Demand Status` | **需求状态 Demand Status** | WHY |
| 8 | `Current Wastewater Treatment / Technology` | **现有废水处理 Current Treatment** | WHERE / WHO |
| 9 | `Priority Site` | **优先厂区 Priority Site** | WHERE / WHO |
| 10 | `Who to Contact` | **关键联系人 Contact** | WHERE / WHO |
| 11 | `What Is Missing` | **待确认信息 Missing Info** | ACTION |
| 12 | `Next Action` | **下一步 Next Action** | ACTION |
| 13 | `Sales Conclusion` | **开发建议 Sales Conclusion** | ACTION（**结论卡**） |

**硬规则**

| # | 规则 |
|---|---|
| 1 | Display Label 只用于**显示**。脚本校验、字段引用、规则判据一律使用 Internal Key。 |
| 2 | **不得**因改显示名而改变字段语义、取值范围或判定逻辑。 |
| 3 | Display Label 为**固定字符串**，不得自由改写或增删中英文部分。 |
| 4 | 渲染脚本通过**别名表**把 Display Label 映射回 Internal Key；映射失败 → 按原文处理，不报错。 |

### 二、第一页四组分组（WHO → WHY → WHERE/WHO → ACTION）

主卡 13 字段按**决策阅读顺序**分四组。分组只改**呈现顺序与标题**，不改字段内容。

| 组 | 标题 | 回答 | 含字段 |
|---|---|---|---|
| **WHO** | `WHO · 客户是谁` | 这家公司是什么？ | 公司 / 国家 / 主营业务 / 客户类型 |
| **WHY** | `WHY · 为什么值得看` | 有没有机会？需求多强？ | 行业匹配 / BDD机会 / 需求状态 |
| **WHERE / WHO** | `WHERE / WHO · 从哪里切入` | 从哪个厂区、找谁？ | 现有废水处理 / 优先厂区 / 关键联系人 |
| **ACTION** | `ACTION · 现在怎么办` | 缺什么、下一步、值不值得投入？ | 待确认信息 / 下一步 / **开发建议（结论卡）** |

**硬规则**

| # | 规则 |
|---|---|
| 1 | 四组顺序固定，**不得调换**（阅读链路：认识 → 判断 → 切入 → 行动）。 |
| 2 | 分组**不改变字段归属语义**，也不表示字段间存在推导关系。 |
| 3 | **13 个字段一个都不能少**，也不得出现第 14 个字段。 |
| 4 | 三个固定小块（BDD Opportunity 判定依据 / Demand Status 明细 / 风险）**不属四组**，仍按原位置展示。 |

### 三、`Current Treatment` 显示状态（四态）

**状态只能来自现有证据，不得推断。**

| 显示状态 | 判据（**必须由一个具体 E# 支撑**） | 颜色 |
|---|---|---|
| `Confirmed` | 证据明确载明**已建成 / 在运行 / 在售交付**的处理单元或工艺组合 | 🟢 |
| `Partial` | 证据只覆盖**部分环节**：仅载明单个单元、工艺组合不完整，或原文本身含"部分厂区 / 部分工艺"限定 | 🟡 |
| `Planned` | 证据明确表述为**规划 / 拟建 / 在建**，尚未投运 | 🔵 |
| `Unknown` | 无任何相关证据（**不得据"这类厂应该有"填**） | ⚪ |

**显示格式**

```
🟢 Confirmed · {技术组合原文}
```

**硬规则**

| # | 规则 |
|---|---|
| 1 | 状态**必须有 E# 支撑**；无 E# → `Unknown`。 |
| 2 | 证据表述为计划 / 拟建 / 在建 → **只能** `Planned`，**不得**写 `Confirmed`。 |
| 3 | 覆盖不完整 → `Partial`，**不得**升为 `Confirmed`。 |
| 4 | **状态与 `BDD Opportunity` 不联动**：既有 ETP / ZLD ≠ 无机会；规划中 ≠ `High`。 |
| 5 | 状态**不参与任何判断字段**，仅为展示。判定依据仍在 `Current Wastewater Treatment / Technology` 字段本身。 |
| 6 | Partner Path 下，状态描述的是"**可提供 / 在交付**的技术组合"，不适用"自身废水"口径。 |

### 四、`Sales Conclusion` 结论卡（第一页最醒目）

`Sales Conclusion` **从主卡表格中移出**，渲染为第一页（Page 1）的独立结论卡，置于四组之后。

```
┌────────────────────────────────────────────┐
│  开发建议 SALES CONCLUSION                 │
│                                            │
│  🟢 建议开发                                │
│  主体级证据充分（…），属目标市场，无财务警示；  │
│  尚无具体项目文件级证据，故未达"重点开发"      │
└────────────────────────────────────────────┘
```

**硬规则**

| # | 规则 |
|---|---|
| 1 | 结论**取值与原因文字一字不改**，只改变位置与视觉权重。 |
| 2 | 五色语义沿用第一部分映射；**不得**为醒目而改色。 |
| 3 | 结论卡**不得**新增建议、行动项、评分或后续话术。 |
| 4 | 结论卡必须在 Page 1 内，**不得**被挤到第 2 页。 |
| 5 | Markdown 源中该字段仍属主卡 13 字段之一，校验照常计入。 |

### 五、展示层边界（**不得越界**）

| # | 禁止 |
|---|---|
| 1 | 修改任何判断规则（Evidence Policy / Customer Path / Industry Map / BDD Opportunity / Demand Status / Commercial Risk / Opportunity Type / Priority Site） |
| 2 | 新增字段、新增 Skill、新增评分、新增 CRM 功能 |
| 3 | 因"更好看"调整任何取值、颜色或结论 |
| 4 | 在渲染层推断、补全、润色任何内容 |
| 5 | 改动 Markdown 的**完整 Evidence 结构**（附录 A 原样保留） |

---

## 第三部分 · UI Refinement（V1.1.2 新增）

> **范围**：仅 Presentation / PDF Rendering / Output Visual Layer。
> **不修改任何判断逻辑**，不新增字段，不新增评分，不新增功能。
> 13 个 Internal Key、Sales Conclusion 五值与判定逻辑、32 条硬性约束均保持原样。

### 一、主卡字段列样式

| 项 | 规范 |
|---|---|
| 字段列背景 | **浅灰蓝** `#eef2f7` |
| 字段列宽度 | **固定 18% ~ 22%**（取 20%） |
| 中文名 | **加粗** |
| 英文名 | 正常字重、字色略淡 |
| 字段名对齐 | **左对齐** |
| 判定列背景 | **白色为主** |
| 判定列对齐 | 长文本**左对齐**；短 Badge 可**水平居中**；多行内容（联系人 / 项目描述 / Evidence）**禁止水平居中** |
| 所有单元格 | **垂直居中** |

### 二、状态值 → Badge（**不做整行染色**）

**只有下列短状态使用 Badge**（值必须**精确匹配**才替换）：

| 语义 | 颜色 | 取值 |
|---|---|---|
| 正面 | 🟢 绿 | `High` · `Target` · `Confirmed` · `建议开发` · `建议重点开发` |
| 待验证 | 🟡 黄 | `Medium` · `Potential` · `Partial` · `建议先验证` |
| 风险 | 🔴 红 | `Risk` · `Conflict` · `暂不优先` |
| 未知 | ⚪ 灰 | `Unknown` · `信息不足` |
| 中性事实 | 🔵 蓝 | `Adjacent` · `Planned` · `Neutral Facts` |

**硬规则**

| # | 规则 |
|---|---|
| 1 | 颜色**只表达业务语义**，不表达"重要"。 |
| 2 | "重要"只通过**加粗 / 字号 / 位置**体现。 |
| 3 | **不得把普通重点信息统一改成红色。** |
| 4 | **红色只用于风险、冲突、负面。** |
| 5 | Badge **不是新的判断**：只做取值 → 样式的机械映射，未命中即原样输出纯文本。 |
| 6 | 同一取值在所有卡上颜色一致（沿用第一部分规则）。 |

### 三、`Current Treatment` 四态中文显示

| 显示 | 颜色 |
|---|---|
| `🟢 已确认 Confirmed` | 绿 |
| `🟡 部分确认 Partial` | 黄 |
| `🔵 规划中 Planned` | 蓝 |
| `⚪ 未知 Unknown` | 灰 |

**状态必须继续由现有 Evidence 支撑，不得推断。** 判据与硬规则见第二部分第三节（不变）。

### 四、第一页长字段压缩（**只压缩展示，不删内容**）

**第一页只保留业务员 30 秒判断所需信息。**

**必压字段（用户指定）**：

| 字段 | 第一页保留 | 移入 Page 2 |
|---|---|---|
| `Current Treatment` | 核心技术组合（单元名） | 官网描述、雨水缓冲、监测数据、集团目标 |
| `Priority Site` | 厂区 + 最关键理由 | 许可申请细节、备选厂区说明、日期 |
| `Who to Contact` | 岗位角色（+ 是否需要走集团层） | 具名、职位、Source、时效说明 |
| `What Is Missing` | 各级最关键的 1 项 | 完整三级清单 |
| `Sales Conclusion` 原因 | 结论 + 1 句最关键原因（≤ 3 行） | 完整原因、证据编号、数字 |

**建议同压字段**（过长即压，保证 Page 1 落在 1 页内）：

| 字段 | 第一页保留 | 移入 Page 2 |
|---|---|---|
| `Country` | 国家 + 主要运营地 | 站点数、子公司国别清单 |
| `What They Do` | 主营业务一句话 | 工艺细节、板块构成 |
| `Industry Match` | 状态值（Badge） | 目标市场分组编号与性质口径说明 |
| `Next Action` | 核心动作 | 前置条件、附加确认项 |

**描述控制在 1~3 行核心内容**（实测阈值：摘要 ≤ 130 字）。

> **摘要 = 原文的精确前缀**（切分处插入 `⟪P2⟫`）。这样 `摘要 + Page 2 其余` 恒等于**完整原文**，
> 做到"压缩展示、不删一字"。

**实现约定（Markdown 侧）**：长字段值写成

```
{第一页摘要}⟪P2⟫{完整内容的其余部分}
```

- `⟪P2⟫` 之前 = Page 1 摘要
- `⟪P2⟫` 之后 = 仅 Page 2 显示
- Page 2 顶部生成「字段完整内容」区块，显示 `摘要 + ⟪P2⟫ 后续` 的**完整原文**

**硬规则**

| # | 规则 |
|---|---|
| 1 | **禁止删除底层完整内容。** Markdown 里一字不删。 |
| 2 | 摘要**必须逐字取自原文**，不得新增、不得改写、不得概括成新句子。 |
| 3 | 只改变 **PDF 第一页**的展示摘要；Markdown 与附录不受影响。 |
| 4 | `⟪P2⟫` 是**版式标记**，不是判断标记，**不得**影响任何字段取值。 |

### 五、Section Header 统一格式

```
01 WHO ｜客户是谁
02 WHY ｜为什么值得看
03 WHERE / WHO ｜从哪里切入
04 ACTION ｜现在怎么办
```

| 项 | 规范 |
|---|---|
| 编号 | `01` ~ `04`，两位数字 |
| 分隔符 | 全角竖线 `｜` |
| 背景 | **统一浅灰蓝** `#e8eef5` |
| 文字 | 深色 + **加粗** |
| 四组配色 | **同一种颜色**（不使用不同彩色背景） |
| 禁止 | 渐变、投影、拟物 |

### 六、Sales Conclusion 结论卡强化

```
┌─ 左侧色条 ─┬────────────────────────────────────────┐
│            │  开发建议 SALES CONCLUSION             │
│            │                                        │
│            │  🟢 建议开发            ← 中文 16~18pt Bold
│            │  Recommended to Develop ← 英文小一号副标题
│            │  主体级证据充分，属于目标市场；目前尚未   ← 深灰，左对齐
│            │  发现明确 BDD 项目需求。                 │
└────────────┴────────────────────────────────────────┘
```

| 项 | 规范 |
|---|---|
| 中文结论 | **最大、加粗**（16~18pt） |
| 英文副标题 | 小一号（9~10pt），字色略淡 |
| 结论颜色 | 按**现有五色语义**（不新增色） |
| 卡片 | 浅色语义背景 + **左侧色条** |
| 原因 | **黑色 / 深灰**，左对齐 |
| 位置 | 仍在第一页，独立卡片 |

**五值英文副标题对照**

| 中文 | 英文 |
|---|---|
| 建议重点开发 | Recommended — Priority Development |
| 建议开发 | Recommended to Develop |
| 建议先验证 | Verify Before Pursuing |
| 暂不优先 | Low Priority |
| 信息不足，暂缓判断 | Insufficient Information |

> **不得修改 Sales Conclusion 的判断结果或原因内容**，只允许展示层压缩与排版。

### 七、对齐规则（统一执行）

| 对象 | 对齐 |
|---|---|
| 所有单元格 | **垂直居中** |
| 字段名 | 左对齐 |
| 长文本 | 左对齐 |
| 短状态 Badge | 水平居中 |
| 数值 / 单个状态 | 可水平居中 |
| 多行联系人 / 项目描述 / Evidence | **禁止水平居中** |

### 八、第三页 Evidence Card（替代 7 列表格）

> **V1.1.3 已改写**：卡片格式由「E# · FACT · HIGH IMPACT + 结论/来源/置信度」改为
> **「编号 · 主题 / 简洁事实 / 来源」**，并移除审计术语。本节为 V1.1.2 记录，
> **现行规则以第五部分「Page 3 · KEY EVIDENCE ｜关键依据」为准**。

**原来的渲染方式（V1.1.2）：**

```
E12 · FACT · HIGH IMPACT
结论 Conclusion：`<厂区名>` 废水处理采用物化处理 + 微生物生物处理
来源 Source：官网 `<厂区名>` 环境专栏 Water
置信度 Confidence：High
```

| 类型 | 追加字段 |
|---|---|
| `INFERENCE` | `Reason：…` |
| `UNKNOWN` | `Status：Unknown · searched / not searched` |

**展示范围**：只展示 `Decision Impact = High / Medium` 的**最关键的 6 ~ 10 条**（High 优先）。
默认取 **6 条**（脚本常量 `EVIDENCE_CARD_LIMIT`），以保证 Page 3 稳定落在 1 页内。

| # | 硬规则 |
|---|---|
| 1 | **完整 Evidence 仍保留在 Markdown，不得删除。** |
| 2 | 卡片**不是新判断逻辑**：只把表格行转成卡片版式 + 按既有 Impact 排序取前 N 条。 |
| 3 | 不新增、不推断、不改写任何字段值。 |
| 4 | **不再出现过窄竖列**（卡片为单列流式布局）。 |

### 九、字体层级

| 元素 | 字号 |
|---|---|
| 公司标题 | **16 ~ 18 pt Bold** |
| Section Header | **10 ~ 11 pt Bold** |
| 字段名 | **9 ~ 10 pt Bold** |
| 主内容 | 9 ~ 10 pt |
| Evidence / Source | 8 ~ 9 pt |
| Sales Conclusion 中文结论 | **16 ~ 18 pt Bold** |

> **不得通过无限缩小字体来塞内容。**

---

## 第四部分 · 交付文件命名与交付边界（2026-09-27 新增交付范围规则）

### 一、最终交付 = 2 个文件

```
{Company}_BDD_Intelligence_{YYYY-MM-DD}.md      ← 权威版本（附录 A 完整 Evidence + 附录 B 审计信息）
{Company}_BDD_Intelligence_{YYYY-MM-DD}.pdf     ← 业务员版（三页）
```

**日常客户背调模式下，交付清单永远只有这两个文件 —— 不多、不少。**

| 项 | 规则 |
|---|---|
| `{Company}` | 主体简称，**不含空格与特殊字符**（如 `AcmeChemicals` / `AcmeEPC`） |
| `{YYYY-MM-DD}` | 生成日期 |
| 存放位置 | 工作区根目录 |

### 二、内部中间产物（**不进交付**）

以下全部只属于渲染 / 回归流程的内部文件，**不得作为最终交付展示，任务结束后不列入用户产物、不写进交付清单**：

| 类型 | 常见形态 |
|---|---|
| 渲染中间态 | 内联 CSS 的 `*.html`、单页分解 HTML |
| 视觉产物 | 页面截图 `*_Page1.png` / `*_Page3.png`、Before-After 对比图 |
| 对比 / 预览目录 | `_*-comparison/`、`_*-preview/`、`_shot_*/` |
| 调试输出 | 逐页 / 逐块诊断 PDF、`_dg_*` / `_chk_*` 临时文件、临时 Chrome profile |
| 临时提取 | 从 PDF 抽取的中间文本、下载的原始 PDF 缓存 |

### 三、唯一例外：用户明确要求时才输出图片类产物

| 用户显式提出的需求 | 允许输出 |
|---|---|
| 视觉检查 / 看看排版 | 页面 PNG |
| PDF 回归 / 逐页检查 | 逐页 PNG 或单页 PDF |
| Before / After 对比 | 对比截图 |

**未获明确要求时，一律不输出、不提及、不列入交付。**

### 四、硬边界

> **本规则是交付范围规则，不是内容规则。**
> 禁止因此修改 PDF / MD 内容、判断规则、13 个 Internal Key 或现有三页结构。
> 中间产物无论多少，最终 `.md` / `.pdf` 的内容必须完全一致（渲染层仍只做格式转换，见第六部分）。

---

## 第五部分 · PDF 三页模板（业务员版）

**Markdown 保留完整 Evidence；PDF 为业务员版本，约 3 页。**

> **V1.1.3 Sales Usability**：Page 1 **完全不变**；Page 2 / Page 3 改为销售向版式（详见本节）。
> 审计与边界信息移入 Markdown 附录 B，**不进入业务 PDF**。

| PDF 页 | 页眉（即业务区标题） |
|---|---|
| Page 1 | `Customer Snapshot \| 客户快照` |
| Page 2 | `SALES INTELLIGENCE ｜开发情报` |
| Page 3 | `KEY EVIDENCE ｜关键依据` |

（Page 2 / 3 的页眉按 V1.1.3 加重呈现：11pt 加粗深色；Page 1 页眉样式不变。）

### Page 1 · Customer Snapshot（客户快照）

内容：**主判断卡全部 13 字段**（原样搬运，不改写结论），按四组呈现，末尾为结论卡。

**V1.1.2**：长字段只展示**摘要**（`⟪P2⟫` 之前），完整内容进 Page 2；短状态渲染为 **Badge**。

```
┌─ Page 1 · Customer Snapshot ─────────────────────────────┐
│  {Company} · {Country}                     16~18pt Bold   │
│  {日期} | 来源：{输入形式}                                  │
│                                                          │
│  ▌01 WHO ｜客户是谁                     ← 浅灰蓝底 · 加粗    │
│    公司 Company              {全称}（{国家}）· {核实三态}    │
│    国家 Country              {国家 · 主要运营地区}           │
│    主营业务 Business         {一句话}                       │
│    客户类型 Customer Type    [🔵 Partner·EPC]              │
│                                                          │
│  ▌02 WHY ｜为什么值得看                                    │
│    行业匹配 Industry Match   [🔵 Adjacent]                 │
│    BDD机会 BDD Opportunity   [🟢 High] · {Opportunity Type}│
│    需求状态 Demand Status    [🟡 Potential]                │
│                                                          │
│  ▌03 WHERE / WHO ｜从哪里切入                              │
│    现有废水处理 Current       [🟢 已确认 Confirmed] · {摘要} │
│      Treatment                                            │
│    优先厂区 Priority Site    {厂区} · {最关键理由}           │
│    关键联系人 Contact        {岗位（摘要）}                  │
│                                                          │
│  ▌04 ACTION ｜现在怎么办                                   │
│    待确认信息 Missing Info   {各级最关键 1 项}               │
│    下一步 Next Action        {一句话}                       │
│                                                          │
│  ┃ 开发建议 SALES CONCLUSION                              │
│  ┃ [🟢] 建议开发                     ← 16~18pt Bold        │
│  ┃ Recommended to Develop           ← 9~10pt 副标题        │
│  ┃ {结论 + 1 句最关键原因，≤3 行，左对齐}                     │
└──────────────────────────────────────────────────────────┘
```

**限制**：**1 页内**。超页则进一步压缩长字段摘要，**不得删字段、不得删结论卡、不得把结论卡移到第 2 页**。

> 三个固定小块（`BDD Opportunity 判定依据` / `Demand Status 明细` / `风险`）**不放在 Page 1**，归入 Page 2。

### Page 2 · SALES INTELLIGENCE ｜开发情报（V1.1.3）

**由「字段详细内容」大表改为 5 张销售信息卡。不使用大型字段表。**

| # | 卡片标题 | 数据来源（**纯搬运**） |
|---|---|---|
| 1 | `Why BDD｜为什么和 BDD 有关` | Markdown「BDD Opportunity 判定依据」+「Demand Status 明细」两块逐行搬运 |
| 2 | `Current Treatment｜目前怎么处理` | `Current Wastewater Treatment / Technology` **完整原文**（Page 1 摘要 + 被压缩部分） |
| 3 | `Priority Site｜优先厂区` | `Priority Site` **完整原文** |
| 4 | `Who to Contact｜找谁` | `Who to Contact` **完整原文** |
| 5 | `What to Verify｜还要确认什么` | `What Is Missing` **完整原文** |

```
┌─ Page 2 · SALES INTELLIGENCE ｜开发情报 ─────────────────────────┐
│  ┌ Why BDD｜为什么和 BDD 有关 ──────────────────────────────┐   │
│  │  Reason：…                    ← 逐行搬运，不改写          │   │
│  │  Evidence：E4 / E7 / …                                    │   │
│  │  Confidence：High ／ Opportunity Type：…                  │   │
│  │  Public Wastewater Evidence：… ／ Customer-stated Demand：…│   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌ Current Treatment｜目前怎么处理 ─────────────────────────┐   │
│  │  {字段完整原文，短段落}                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌ Priority Site｜优先厂区 ────────────────────────────────┐   │
│  │  {字段完整原文，短段落}                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌ Who to Contact｜找谁 ──────────────────────────────────┐   │
│  │  {字段完整原文，短段落}                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌ What to Verify｜还要确认什么 ───────────────────────────┐   │
│  │  {字段完整原文，短段落}                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

**硬规则**

| # | 规则 |
|---|---|
| 1 | **只用这 5 张卡**，不得新增卡片、不得改标题文字 |
| 2 | 正文为**字段原文搬运**，不得改写、润色、缩写 |
| 3 | **不使用大型字段表**；卡片为单列流式版式 |
| 4 | Page 1 摘要 + 本页完整原文 = 字段完整原文，**不丢内容** |
| 5 | 旧版的 `字段详细内容 · Field Details` 表与 `风险` 段**不再出现在 PDF**（内容仍在 Markdown） |

**限制**：**1 页内**。

### Page 3 · KEY EVIDENCE ｜关键依据（V1.1.3）

**只展示 6 ~ 8 条真正影响销售判断的关键证据**（按 Markdown 既有 `Decision Impact` 取 High 优先）。

每条只写三段：

```
{Evidence 编号} · {主题}
{简洁事实}
来源：{Source}
```

| 要素 | 来源 | 说明 |
|---|---|---|
| 编号 | 附录 A 的 `#` | 便于与 Markdown 对照 |
| 主题 | 附录 A 的 `主题` 列（V1.1.3 新增展示标签） | 缺失时只显示编号 |
| 简洁事实 | 附录 A 的 `结论` 列 | 逐字搬运 |
| Source | 附录 A 的 `Source` 列 | 空 / `—` 时**不显示该行** |

**硬规则**

| # | 规则 |
|---|---|
| 1 | **PDF 不显示** `FACT` / `INFERENCE` / `UNKNOWN` / `Confidence` / `Decision Impact` 等**审计术语** |
| 2 | **完整 Evidence 一字不删**，仍保留在 Markdown 附录 A（含全部审计列） |
| 3 | 卡片只做**版式转换 + 按既有 Impact 排序取前 6~8 条**，不新增判断 |
| 4 | 不再出现过窄竖列；无 7 列表格 |
| 5 | 只取 `Decision Impact = High / Medium`；不足 6 条时按原顺序补足 |

**限制**：**1 页内**。

### 不进 PDF 的内容（V1.1.3）

以下内容**只在 Markdown 保留**，业务 PDF 中不出现：

- `## 附录 B` 全部内容：可溯源率 · 类型定义 · Decision Impact 说明 · 集团级 vs 厂区级说明 · 同名主体排除 · 来源冲突项 · UNKNOWN 三态汇总
- `## 边界声明` 全部内容：未输出工艺参数 / 设备选型 / 技术方案 / 达标承诺 / 金额 / 报价状态；`Technical Fit` 与 `Quotation Readiness` 冻结说明；未输出"建议小试"说明

> 渲染层以 `## 附录 B` / `## 边界声明` 为切分点，其后一律不进入 PDF。**切分不删除任何 Markdown 文字。**

---

## 第六部分 · 渲染管线与隔离要求

### 一、管线

```
Markdown（唯一判断产出）
    │
    ▼  纯格式转换（无判断）
HTML（内联 CSS，五色语义）      ← 内部中间态，**不交付**
    │
    ▼  Chrome headless --print-to-pdf
PDF（业务员版）                  ← 交付物之一（另一个为 Markdown 原文）
```

**工具**：`scripts/render_pdf.py`

### 二、渲染层隔离（**硬要求**）

> **PDF 渲染层不得反向影响 Customer Intelligence 判断逻辑。**

| # | 规则 |
|---|---|
| 1 | 渲染脚本**只做格式转换**：解析 Markdown → 输出 HTML → 打印 PDF。**不得新增、推断、改写、润色任何结论。** |
| 2 | **不得在渲染层做判断**：不重新计算等级、不推断缺失字段、不补全 `Unknown`。 |
| 3 | **一致性校验**：渲染前必须校验 Markdown 主卡 **13 字段齐全**；缺任一字段 → **报错退出，不生成 PDF**。 |
| 4 | **颜色映射在渲染层实现**，但映射表**来源于本文件**（单一事实来源），脚本内只做查表。 |
| 5 | 渲染失败时**保留 Markdown**，并明确报错；**不得用简化版 PDF 替代**。 |
| 6 | **Markdown 为权威版本。** 两者冲突时以 Markdown 为准。 |
| 7 | **V1.1.3 审计区隔离**：渲染前按 `## 附录 B` / `## 边界声明` 切分，**其后内容不进入 PDF**（仅版式取舍，Markdown 原文不动）。 |
| 8 | **V1.1.3 Page 2/3 素材仍来自 Markdown**：Page 2 取主卡字段原文与两个判定小节；Page 3 取附录 A 表格。**渲染层不得自行补写任何文字。** |
| 9 | **渲染中间产物不进交付（2026-09-27）**：管线中的 `HTML`、诊断 PDF、截图与临时提取文件**仅作内部中间态**，**最终交付只有 `.md` + `.pdf` 两个文件**；**仅当用户明确要求视觉检查 / PDF 回归 / Before-After 对比时**才输出图片类产物。**该条只约束交付范围，不得据此改动渲染逻辑或内容。** |

### 三、Page 切分实现

用 CSS 分页强制切页：

```css
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
```

**V1.1.3 起不再依赖 Markdown 内的 `## Page N` 标记切页**，改为在渲染层装配三页：

| 页 | 素材来源 |
|---|---|
| Page 1 | Markdown 主卡区（到「BDD Opportunity 判定依据」之前） |
| Page 2 | 渲染层由主卡字段**完整原文** + 两个判定小节现场拼装 5 张信息卡 |
| Page 3 | Markdown 附录 A 的 Evidence 表 → 6~8 张关键依据卡片 |

（Page 切分属**版式规则**，不增删任何 Markdown 内容。）

### 四、V1.1.1 排版修复（**纯格式，不改内容**）

| # | 缺陷 | 修复 |
|---|---|---|
| 1 | 主卡值中显式书写的 `<br>` 被转义为字面文本 `&lt;br&gt;` | `inline()` 将 `&lt;br&gt;` 还原为 `<br/>`，正常换行 |
| 2 | 值中含转义竖线 `\|`（复合机会类型 `+\|`）时表格被误拆成两列 | `split_row()` 先保护 `\|` 再按 `|` 拆分，单元格不裂开 |

> 两项均为**排版修复**：单元格文本逐字不变，仅纠正 HTML 结构与列数。
> 修复后必须复核 **PDF 仍为 3 页**（`<br>` 生效会增高内容）。

---

## 第七部分 · 与其他文件的职责边界

| 文件 | 负责 |
|---|---|
| **本文件** | 颜色语义（唯一来源）+ 命名规范 + PDF 三页模板 + 渲染隔离要求 |
| `assets/output-card-template.md` | Markdown 输出模板（主卡 13 字段 + 附录 A 完整证据 + 附录 B 审计信息） |
| `sales-conclusion-rules.md` | Sales Conclusion 的**取值**（本文件只负责它的颜色） |
| `evidence-policy.md` | Evidence 类型与 Decision Impact 的定义 |
| `scripts/render_pdf.py` | 本文件的**实现**，不含判断逻辑 |

---

## 第八部分 · 待业务方确认

| # | 待确认 | 归属 |
|---|---|---|
| 1 | 五色语义是否与内部习惯一致（尤其红色用于"冲突"） | 销售 |
| 2 | PDF 三页的字段取舍是否符合业务员阅读习惯 | 销售 |
| 3 | 是否需要中文 / 英文双语输出 | 销售 |
| 4 | 是否需要在 PDF 页脚加公司标识与免责声明 | 公司 |
| 5 | **V1.1.1 四组阅读顺序（WHO → WHY → WHERE/WHO → ACTION）是否符合业务员实际翻查习惯** | 销售 |
| 6 | **`Current Treatment` 四态徽标是否需要加中文（已确认 / 部分 / 规划中 / 未知）** | 销售 |
