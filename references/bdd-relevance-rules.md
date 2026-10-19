# BDD Relevance 判定规则（V1.1.3 + BDD-Specific Relevance Gate Patch）

**回答的问题**：这家公司 / 这个伙伴，是否存在 BDD 可切入的机会？

**不是**行业属不属于目标市场（那是 `bdd-fit-rules.md` 的 Industry Fit）。

> ⚠️ **本文件的核心作用：阻断"行业对口 → BDD 相关性高"的错误推导。**

> **BDD-Specific Relevance Gate Patch（2026-09-27）· Patch B**：
> 新增 **`BDD-Specific Relevance Evidence Gate`**（`Strong` / `Moderate` / `Weak` / `Unknown`），
> 作为 **End-user `BDD Opportunity = High` 的第 5 个硬门槛（条件 E）** —— 见第四节。
> **Patch A**（T3 定义收紧）见 `bdd-fit-rules.md` 第二节。
> **本 Gate 只作用于 End-user；Partner Path 规则不变。不新增 Internal Key、不新增 PDF 字段、不新增评分。**

---

## 一、V1.1 的两处关键修复

### 修复 1 · 废水证据拆成两类（删除封顶规则）

| 证据类 | 来源 | 说明 |
|---|---|---|
| **Public Wastewater Evidence（PWE）**<br>公开废水证据 | 官网 · 年报 / ESG / BRSR · 政府许可 · 环评 · 合规报告 · 公开案例 · 招聘 | 企业级**公开事实** |
| **Customer-stated Demand（CSD）**<br>客户侧需求陈述 | **询盘文字** · 客户自述 | 客户级**需求陈述** |

> ❌ **已删除规则**：「无询盘废水信号 → BDD Relevance 最高 `Medium`」。
>
> **删除原因**：该规则使「仅凭公司名 + 官网做背调」的场景**从定义上不可能达到 `High`**，即使已掌握官网环境政策、政府合规报告、完整排放数据。
> 在多次实跑中连续复现（多个制造业与工程类主体均被此规则封顶 `Medium`）。
>
> **V1.1 规则**：PWE **或** CSD 任一成立即可满足废水证据条件。两者分别记录、分别标注来源。

### 修复 2 · 按 Customer Type 使用不同的内部逻辑

`End-user Path` 与 `Partner Path` **判断对象不同**，不能用同一套判据：

| Path | BDD Relevance 回答的问题 | 主要依据 |
|---|---|---|
| **End-user Path** | 这家企业**是否产生 BDD 可切入的废水**？ | 制造业活动 + PWE（现有设施 / 排放 / 许可）+ 窗口信号 |
| **Partner Path** | 这个伙伴**是否会把 BDD 纳入其交付组合**？ | 能力确认 + 技术组合重叠 + 渠道 / 项目信号 |

> **Partner Path 不得以"它自己产生多少废水"为主要判断依据。**
> EPC / 集成商 / 分销商类主体，其价值在于渠道与交付能力，不在于自身排污。

---

## 二、8 项输入（分 Path 适用）

| # | 输入 | 来源 | End-user | Partner |
|---|---|---|---|---|
| 1 | **Industry** 行业 | 询盘 / 工商 / 官网 | 必须 | 必须 |
| 2 | **Company Business** 公司业务 | 工商 / 官网 | 必须 | 必须 |
| 3 | **Products** 产品 / 服务 | 官网 / 目录 | 必须 | 必须 |
| 4 | **Activity Confirmation** 活动确认<br>（End-user：制造业活动 / Partner：技术·集成·渠道能力） | 厂址 · 规模 · 设备招标 · 招聘 · 案例 · 资质 | **关键项** | **关键项** |
| 5 | **Process / Technology** 工艺或技术组合 | 公开可验证时 | 可选 | **建议** |
| 6 | **Public Wastewater Evidence（PWE）** | 官网 / 政府 / 年报 | **必须之一** | **必须之一** |
| 7 | **Environmental Evidence** 环境证据 | 处罚 / 许可 / 环评 | 强烈建议 | 建议 |
| 8 | **Project / EIA / Tender / ESG / Job signals** | 公开检索 | 强烈建议 | 强烈建议 |

**输入 6 与 7 的区别**：输入 6 描述**设施与排放现状**（有无处理、用什么），输入 7 描述**监管痕迹**（有无处罚 / 许可 / 环评）。

---

## 三、取值定义

### A. End-user Path

**`High` 的五个条件（Patch B 后 · 必须全部满足）**

| 条件 | 内容 |
|---|---|
| **A** | `Industry Fit = Target`（含 T3 已过 `bdd-fit-rules.md` 的 T3 证据门槛） |
| **B** | 制造业活动已确认（输入 4） |
| **C** | `PWE` **或** `CSD` 至少一项成立（输入 6） |
| **D** | 存在主体级相关证据：**≥ 2 项**（环境证据 / 项目信号 / 现有处理设施 / 窗口信号） |
| **E** | **`BDD-Specific Relevance Evidence = Strong`（新增硬门槛，见第四节）** |

> **Patch B 前**的 `High` 只需 A+B+C+D。**Patch B 后 A+B+C+D+E 全部满足才可判 `High`。**
> 理由：「行业对口 + 有制造 + 有废水证据 + 证据够多」**仍不能证明该主体的废水属 BDD 适用场景**。

**取值定义（Patch B 后）**

| 取值 | 判据 |
|---|---|
| `High` | A + B + C + D + **E（Gate = `Strong`）** 全部满足 |
| `Medium` | ① 行业对口 且 ② 制造业活动已确认，且满足下列任一：<br>· 主体级证据仅 1 项，或 `PWE` / `CSD` 均缺失（**原 Medium 定义**）<br>· **A+B+C+D 已满足但 Gate ∈ {`Moderate`, `Weak`}**（**Patch B 新增封顶路径**） |
| `Low` | 已确证**三项同时成立**：全厂区闭环 + 无扩产/加严/处罚 + 无遗留难降解段；**或** 主体确证为非制造业（纯研发 / 纯持有 / 无任何生产活动） |
| `Unknown` | ① 关键输入不足（主体未核实 / 无法确认是否有生产活动 / 无任何废水相关信息）；**或**<br>② **`Industry Fit = Unknown`**（不属目标市场地图的 Target / Adjacent，且未被正面确证为 `Outside`）→ **无目标市场归属即无机会判定依据**；**或**<br>③ **Gate = `Unknown`** |

**Gate 与取值的机械映射（**A+B+C+D 已满足时适用**，不得人工指定）**

| Gate | BDD Relevance |
|---|---|
| `Strong` | `High` |
| `Moderate` | `Medium` |
| `Weak` | `Medium` |
| `Unknown` | `Unknown` |

> **注意适用范围**：该映射**只处理"原本会判 High"的那条路径**。
> 若 A~D 本身不满足（缺活动确认 / 缺 PWE 与 CSD / 证据不足），**Gate 不参与**，按上表"原 Medium 定义"与 `Low` / `Unknown` 判据取值。
> `Industry Fit = Unknown` 时 **①（A 条件）即不成立** → 落 `Unknown`，与 Gate 无关。

### B. Partner Path

> **2026-09-27 Partner Cooperation Evidence Gate Patch**：`High` 增加两条硬门槛（条件 E / F）。完整规则见**第五节**。

| 取值 | 判据（需同时满足） |
|---|---|
| `High` | **A** Industry Fit ∈ {Target, Adjacent} **且 B** 技术 / 集成 / 分销能力已确认 **且 C** 其技术组合与 BDD 场景存在**公开可证的重叠** **且 D** **≥ 2 项渠道 / 项目证据**（公开项目案例 / 采购记录 / 合作方 / 在谈项目清单）**且 E** **`Partner Cooperation Evidence ∈ {Confirmed, Supported}`（新增硬门槛）** **且 F** **Conflict 控制通过**（无 Conflict，或存在 Conflict 但**同时**具备 `Confirmed` / 强 `Supported` 合作开放证据，且已解释竞争边界） |
| `Medium` | ① 行业对口 **且** ② 能力已确认 **且**（③ 重叠度或渠道证据仅 1 项 **或** ④ **A+B+C+D 已满足但 Gate 未过**） |
| `Low` | 确证其技术线与 BDD 场景**无任何重叠**，且明确不集成第三方工艺（工艺封闭 + 无渠道） |
| `Unknown` | 能力或技术组合无法确认 |

---

## 四、BDD-Specific Relevance Evidence Gate（Patch B · **仅作用于 End-user `High`**）

**回答的问题**：这家企业的废水，**是否与 BDD（电化学氧化 / 高级氧化）的适用场景存在明确关系**？

**这不是**：不是 Industry Fit（行业属性）· 不是 Demand Status（需求事实）· 不是 Technical Fit（技术可行性 —— 本 Skill 不输出）· **不是评分、不是 0–100、不是加权**。

**定位（硬约束）**

| # | 约束 |
|---|---|
| 1 | **不新增到 13 个 Internal Key**；不进主卡字段表 |
| 2 | **不新增任何 PDF 字段 / 卡片**；业务 PDF（Page 1 / 2 / 3）结构不变 |
| 3 | 不新增评分、不新增分数制、不新增 Technical Fit、不新增设备选型 |
| 4 | **只用于 `End-user Path` 的 `BDD Opportunity = High` 判定**；`Partner Path` 规则**完全不变** |
| 5 | 判定结果记录在 **Markdown 附录 B（审计信息）**，**不进业务 PDF** |

### 四.1 四档取值

| 档 | 判据（满足任一即该档；取**已命中的最高档**） |
|---|---|
| **`Strong`** | 存在至少一种**明确 BDD 相关处理信号**：<br>· High COD + difficult-to-treat context（高 COD 且明载难处理背景）<br>· refractory organic wastewater（难降解有机废水）<br>· hard-to-biodegrade organics（可生化性差的有机物）<br>· persistent organic pollutants（持久性有机污染物）<br>· API / pharmaceutical refractory wastewater（原料药 / 制药难降解废水）<br>· fine-chemical difficult organic wastewater（精细化工难处理有机废水）<br>· **AOP already in use**（已在用高级氧化）<br>· **AOP under evaluation**（在评估 / 可研高级氧化）<br>· advanced oxidation requirement（明载需高级氧化）<br>· electrochemical oxidation / electro-oxidation（电化学氧化 / 电氧化）<br>· conventional treatment failure / limitation（常规处理失效或受限）<br>· tertiary / deep polishing need for difficult pollutants（针对难处理污染物的三级 / 深度处理需求）<br>· documented treatment gap **clearly relevant to destructive oxidation**（明确载明的、与破坏性氧化相关的处理缺口） |
| **`Moderate`** | 存在**较强间接证据**：<br>· complex organic chemical manufacturing（复杂有机化学品制造）<br>· API / pharmaceutical synthesis（原料药 / 制药合成）<br>· fine chemical multi-step synthesis（精细化工多步合成）<br>· solvent-rich or organic-rich process（富溶剂 / 富有机工艺）<br>· known difficult liquid waste streams（已知的难处理液体废物流）<br>· battery / chemical production with meaningful wastewater evidence（电池 / 化工生产且有实质废水证据）<br>**但尚未确认** refractory / high COD / AOP / treatment limitation |
| **`Weak`** | 仅有：manufacturing · wastewater generation · treatment facility · discharge permit · water consumption · generic ESG water statement<br>**但没有明确的 BDD-specific 污染物或处理难点** |
| **`Unknown`** | 公开资料不足，**无法判断该废水是否与 BDD 适用场景存在明确关系** |

### 四.2 硬规则

| # | 规则 |
|---|---|
| 1 | **"有废水" ≠ Gate ≥ `Moderate`。** 废水相关性（有无废水 / 有无设施 / 有无许可 / 水量多大）**不构成 BDD 相关性**。 |
| 2 | `Strong` 必须有 **E# 级 FACT 证据**支撑；`Reason` 中应写明命中的信号。 |
| 3 | **不得用行业经验值升格**（"该行业通常难降解" → 不构成 `Strong`）。 |
| 4 | **不得由行业标签推出** —— `Industry Fit = Target` 不构成任何 Gate 证据。 |
| 5 | 取**已命中的最高档**；不得为凑档位把 `Moderate` 证据写成 `Strong`。 |
| 6 | Gate ∈ {`Moderate`, `Weak`, `Unknown`} 时**不得判 `High`**，且**不得人工指定**替代值 —— 按第三节映射表机械取值。 |
| 7 | 本 Gate **不适用于 `Partner Path`**（Partner Path 判"技术组合重叠 + 渠道 / 项目证据"，规则不变）。 |
| 8 | 本 Gate **不新增 Internal Key、不新增字段、不新增评分**；结果只记入 Markdown 附录 B。 |

### 四.3 与 Industry Fit 的关系（分离原则）

| | Industry Fit | Gate |
|---|---|---|
| 回答 | 这个**行业**是否属目标市场 | 这家**企业的废水**是否与 BDD 场景相关 |
| 层级 | 行业级 | 主体级 |
| 证据 | 行业 / 业务属性 +（T3）废水性质证据 | 主体级废水性质与处理难点证据 |
| 可否互相推导 | ❌ | ❌ |

> **`Industry Fit = Target` 不等于 `BDD Opportunity = High`。**
> 例：电池企业 → `Industry Fit = Target`（T1）；但若只有 manufacturing + wastewater + recycling，而没有 high COD / refractory / AOP / difficult pollutants → **Gate 最高 `Moderate`** → `BDD Opportunity` 最高 `Medium`。
> 例：精细化工企业 → 若有 complex synthesis + wastewater + **UV-AOP 在用** → Gate = `Strong` → 可支撑 `High`。

---

## 五、Partner Cooperation Evidence Gate（Partner Cooperation Evidence Gate Patch · 2026-09-27 · **仅作用于 Partner Path**）

**回答的问题**（只回答这一个）：

> 是否存在**公开证据**表明 **Boromond / 第三方 BDD 技术**有机会进入该 Partner 的**技术、采购或项目交付体系**？

**它不回答**：

- ❌ Partner 的技术强不强
- ❌ Partner 是否覆盖 BDD 应用场景
- ❌ Partner 的项目多不多

> ⚠️ **本 Gate 的存在，就是为了阻断「能力 / 场景强 → 机会高」这条错误推导。**
> 背景：在多个大型水处理 EPC 案例中，原 B 表（行业对口 + 能力确认 + 重叠 + ≥2 项目证据）**对任何大型水处理 EPC 都会自动成立** → 机会档位虚高。

### 5.1 四档取值

| 档 | 判据（满足任一即可，**必须 FACT + Source**） |
|---|---|
| `Confirmed` | ① 存在**落在 BDD / 高级氧化 / 电化学氧化 / 难降解氧化域**的**外部方技术被该主体集成或联合交付的具体案例**（**须点名技术 / 装置 / 项目**）；② 正在采购第三方电化学氧化设备 / 电极 / 模组；③ 招标或采购 BDD / diamond electrode / electro-oxidation 相关产品；④ 公开文件中出现外部电极 / 反应器 / 电化学技术供应商；⑤ 已存在**同一技术域内**「类似 Boromond 角色」的外部合作方 |
| `Supported` | **有明确的第三方技术合作 / 供应 / 集成机制，但证据不落在 BDD 域**：成熟 OEM / technology partner ecosystem · approved vendor / supplier qualification 机制 · 明确采用多家第三方核心工艺设备 · EPC 公开采购外部核心组件 · 官方长期与外部工艺公司联合交付 · 产品线非完全自研封闭 |
| `Unverified` | 只能确认 EPC 能力、技术组合、项目数量、场景重叠；**未发现**任何第三方技术集成 / 采购 / 合作机制证据 |
| `Conflict` | 出现**自有 BDD 竞争技术**信号，**且同时缺乏**合作开放证据：自有电化学氧化产品线 / 自研核心氧化破坏技术 / 自有专利电化学平台 / 明确封闭技术栈且与 BDD 同域 |

**V1.2 主体归属门槛（先于档位映射）**：每项 A～F 证据须标 `目标法人/业务主体`、`集团`、`关联公司` 或 `具体项目`。集团级合同、订单、装机、技术许可只证明集团能力；不得拆成两条子公司渠道证据，也不得直接证明子公司拥有外部技术采购/集成权。只有公开文件点名目标子公司、其实际交付/采购记录，或明确可核的集团授权链覆盖它，才可把该项计入子公司 A～F。否则保留 `Group-level context`，相应 Gate 不得判 `Confirmed`，子公司不得凭母公司证据判 `High`。母公司与子公司的同一交易/许可只算**一项独立证据**。

**V1.2 分销机制门槛**：销售外购化学品、贴牌、为外部品牌代工、集团多站点或产品目录规模，只能证明相应商品业务。`Supported` 须有**该目标主体**采购/代理/集成外部技术或设备的可核机制；仅有商品化学品进出货或母体代工时为 `Unverified`（可在附录记为渠道背景），不得写「BDD 设备进入渠道的机制明确存在」。

**判定顺序**：先看有无「**BDD 域内**」的外部集成证据 → `Confirmed`；再看有无「**BDD 域外**」的合作机制证据 → `Supported`；两者均无 → `Unverified`；**同时**存在自有同域竞争技术且无开放证据 → `Conflict`。

**`Conflict` 分层记录（沿用现有字段，在附录 B 写子类，不新增主卡字段）**：

| 子类 | 判据 | 机会处理 |
|---|---|---|
| `Direct competitor` 直接竞争 | 自有/独占的电化学氧化、BDD 或同工位专有氧化产品已对外销售，且目标客户/污染物场景重叠 | 标竞争关系；没有**已证实的非竞争合作或部件采购切面**时不得判 `High`，销售结论按 `sales-conclusion-rules.md` 的直接竞争步骤处理。缺少采购证据只表示未证实，不写成「绝不会采购」。 |
| `Integration overlap` 工程重叠 | EPC 可设计通用 AOP 或交付相邻氧化工段，但未证实拥有同域专有产品 | 说明工位边界；不得仅因通用工艺能力自动认定直接竞争者或自动否决。 |
| `Component procurement` 部件采购切面 | 有该主体从集团外采购电极/反应器/电化学核心单元的具体证据 | 可与 `Direct competitor` **同时存在**；分别写系统级竞争与部件级采购事实，核实 BDD 的替代/供货资格后再定机会，不自动否决也不自动升 `High`。 |

`Conflict = Yes/No` 仍作兼容标记；`Unknown` 的采购切面不能按 `No` 处理。若直接竞争和部件采购并存，两者的 E#、合同主体与技术域必须各自列出。

> **附录 B 标准行写法（防解析返工 · 2026-10-13）**：固定写 `| `Conflict` | **`Yes`**（`Integration overlap`） | 理由 + E# |` ——
> **值加粗 + 反引号**，**子类必须写在 `**Yes**` 之外**（全角括号括注）。写法规范见 `assets/output-card-template.md` 附录 B「`Conflict` 记录」。

**合作证据强度的两个维度**（仅在 `Confirmed` 与 `Conflict = Yes` 并存、需在 `High` / `Medium` 间定档时使用）：

| 维度 | 加分 | 减分 |
|---|---|---|
| **BDD 域相关性** | 证据落在高级氧化 / 电化学氧化 / 难降解氧化域 | 证据落在 BDD 域外（膜、分离、药剂、仪控等） |
| **机制外部性** | 相对方为**集团外**独立主体 | 相对方为**集团内**兄弟公司 / 网络成员 |

> **定档口径**：两个维度均为加分 → 可在 `Conflict = Yes` 下判 `High`；**任一维度为减分 → 落 `Medium`**（不得机械判 High）。

### 5.2 硬规则

| # | 规则 |
|---|---|
| 1 | **`Strong Technical Capability` ≠ `High Cooperation Opportunity`。** |
| 2 | **`Strong Scenario Overlap` ≠ `High Cooperation Opportunity`。** |
| 3 | **技术越 proprietary，不得解释为"越有吸引力的伙伴"。** 自研程度越高，对 Boromond 通常意味着**更难切入**。 |
| 4 | **`Unverified` 与 `Conflict` 一律不得判 `High`。** |
| 5 | 档位判定**必须逐条引用 E# 与 Source**；无 Source 不得计入。 |
| 5a | 集团/关联公司证据不得代替目标主体的 A～F；同一集团交易不得重复计数。`Supported` 的设备/技术机制不得由商品化学品分销或对外代工推出。 |
| 6 | **不得以行业经验或"大公司通常开放"补全机制证据。** |
| 7 | **本 Gate 只影响机会强度，不改机会类型** —— `Opportunity Type` 五值与复合规则完全不变。 |
| 8 | **`Demand Status` 与本 Gate 双向独立**：`Cooperation = Unverified` 不得导致 `Demand Status` 降档；`Cooperation = Confirmed` 不得导致其升档。 |
| 9 | **不新增 Internal Key、不新增 PDF 字段、不新增评分 / 0–100 分制**；档位只记入 **Markdown 附录 B（审计层）**。 |
| 10 | **本 Gate 只作用于 Partner Path。** End-user Path 与其 `BDD-Specific Relevance Gate`（第四节）完全不变，两个 Gate **不得混用**。 |

### 5.3 条件 A~F 与映射表

`High` 必须同时满足 A~F：

| 条件 | 内容 |
|---|---|
| **A** | `Industry Fit ∈ {Target, Adjacent}` |
| **B** | Partner 能力确认（技术 / 集成 / 分销） |
| **C** | 技术组合与 BDD 场景存在**明确重叠** |
| **D** | 存在 **≥ 2 项渠道 / 项目证据** |
| **E** | **`Partner Cooperation Evidence ∈ {Confirmed, Supported}`（新增硬门槛）** |
| **F** | **Conflict 控制**：有 `Conflict` → 必须**解释竞争边界**；**只有同时存在 `Confirmed` 或强 `Supported` 合作开放证据时**才允许 `High`；**只有技术重叠 + 自有路线 + 无合作开放证据 → 不得 `High`** |

**映射表（机械执行，禁止写死具体公司结果）**

| Cooperation | Conflict | `BDD Opportunity` |
|---|---|---|
| `Confirmed` | No / Low | `High` |
| `Confirmed` | Yes | `High` 或 `Medium` —— 按 5.1「合作证据强度」两维度重算，**不得机械 `High`** |
| `Supported` | No | `High` 或 `Medium` —— 按现有主体级证据重算 |
| `Supported` | Yes | **通常最高 `Medium`**，除非存在非常明确的第三方合作证据 |
| `Unverified` | No | **不得 `High`**，通常 `Medium` / `Unknown` |
| `Unverified` | Yes | **不得 `High`**，通常 `Medium` / `Unknown` |
| `Conflict` | Yes 且无开放合作证据 | **不得 `High`** |

### 5.4 Conflict 不是装饰性标签

只要出现 `Conflict`，**Partner 判 `High` 前必须额外检查以下 5 项**：

1. 技术路线是否**直接重叠**（自有技术即氧化破坏路线），还是**仅场景覆盖**；
2. 是否存在**自研 / proprietary** 技术；
3. **是否有第三方集成机制**；
4. **是否有外部核心组件采购证据**；
5. Boromond 可能是 **supplier / partner / competitor** 中的哪一类。

> ⚠️ **若第 3、4 项均为 `Unknown`（无合作机制、无外部采购证据），不得因为第 1、2 项成立、或因为"项目能力强"而继续判 `High`。**

### 5.5 与 End-user Gate 的区别（不得混用）

| | End-user `BDD-Specific Relevance Gate` | Partner `Cooperation Evidence Gate` |
|---|---|---|
| 问的是 | 它的**废水**是否与 BDD 场景有明确关系 | 第三方 BDD 技术能否**进入它的体系** |
| 四档 | `Strong` / `Moderate` / `Weak` / `Unknown` | `Confirmed` / `Supported` / `Unverified` / `Conflict` |
| 作用对象 | 仅 End-user `High` | 仅 Partner `High` |
| 记录位置 | Markdown 附录 B | Markdown 附录 B |

---

## 六、三条不可越过的红线

### 红线 1 · 行业对口 ≠ BDD Relevance 高

> ❌ `Industry Fit = Target` → **不得**推导 `BDD Relevance = High`。

**示例（必读）**：某 API 原料药企业
- `Industry Fit = Target`（行业属 T2）
- 但**未确认生产活动、无 PWE / CSD、无环境证据**
- → `BDD Relevance = Unknown`（**不得给 High**）

### 红线 2 · 领域吻合 ≠ 自动 High

> ❌ **不得因其行业属 Lithium Battery / Battery Materials 就直接给 `High`。**

**多厂区电池材料制造集团型主体**：
- 行业属 T1（Battery Materials）→ `Industry Fit = Target`
- **但这不构成 `High` 依据。** 必须逐项核验 ② 制造业活动、③ PWE / CSD、④ 主体级证据。
- 若主体级证据充分（如自有个位数量级厂区、政府合规报告、在建项目）→ `High` 是**由证据支撑**的，`Reason` 必须逐条列出证据编号。
- 若仅有"行业是电池" → 最高 `Medium`。

**强制写法**：给 `High` 时，`Reason` 必须显式写出 ≥ 2 项主体级证据及其编号。缺则视为无效。

### 红线 3 · 废水相关性 ≠ BDD 相关性（Patch 2026-09-27 新增）

> ❌ **不得由「有工业废水 / 有生产废水 / 有处理设施 / 有排污许可 / 有废水监测」推出 `BDD Relevance = High`。**
> ❌ **不得由「该行业通常产生难降解废水」推出 `Strong`。**

**判定顺序**：Industry Fit（含 T3 证据门槛）→ A~D 四条件 → **Gate** → 取值。
**两条链路必须分别取证**：`Industry Fit` 用行业属性（T3 另需废水性质证据）；`Gate` 用**主体级**废水性质与处理难点证据。
任一环节缺失 → 按封顶规则下落，**不得用另一环节的证据互相顶替**。

---

## 七、强制附注（缺任一 → 判定无效）

```
Reason            判定理由（已确认什么 / 缺什么）
Evidence          支撑证据编号（指向附录 A，如 E4 / E8 / E12）
Confidence        High / Medium / Low
Opportunity Type  End-user / Technology Partner / EPC·Integration / Distribution / Unknown
```

| 附注字段 | 写法要求 |
|---|---|
| `Reason` | 不得只写"行业对口"。必须写明已确认的主体级事实与缺失项；给 `High` 时必须列 ≥ 2 项证据编号 |
| `Evidence` | 引用附录 A 编号；无证据支撑写 `无`，不得留空 |
| `Confidence` | 官方来源 + 多源互证 = High；单一可信来源 = Medium；聚合站 / B2B 平台 = Low |
| `Opportunity Type` | 见 `opportunity-type-rules.md`，五值之一 |

---

## 八、判定流程

```
1. Path 确定？（见 customer-type-playbook.md 分流）
   ├─ Undetermined ─→ BDD Relevance = Unknown（先确认客户类型）
   ▼
2. 输入 1~3 可获取？
   ├─ 否 ─→ Unknown
   ▼是
3. 输入 4（活动 / 能力确认）
   ├─ End-user 无生产活动证据 ─→ 最高 Medium（或 Low，若确证非制造业）
   ├─ Partner 能力无法确认 ────→ 最高 Medium
   ▼
4. 输入 6（PWE 或 CSD）
   ├─ 两者均无 ─→ 最高 Medium        ← 注意：V1.1 起 PWE 单独成立即可
   ▼至少一项
5. 输入 5 / 7 / 8（工艺或技术组合 / 环境证据 / 项目信号）
   ├─ ≥ 2 项主体级证据 ─→ 进入第 6 步（**不再直接判 High**）
   ├─ 仅 1 项 ─────────→ Medium
   ▼
6. **BDD-Specific Relevance Gate（仅 End-user）** ← Patch B 新增
   ├─ Strong ───→ High
   ├─ Moderate ─→ Medium
   ├─ Weak ─────→ Medium
   └─ Unknown ──→ Unknown
   （Partner Path 跳过本步）
   ▼
7. **Partner Cooperation Evidence Gate（仅 Partner）** ← 2026-09-27 新增
   ├─ Confirmed + No Conflict ──→ High
   ├─ Confirmed + Conflict ─────→ High / Medium（按合作证据强度两维度重算）
   ├─ Supported + No Conflict ──→ High / Medium
   ├─ Supported + Conflict ─────→ 通常最高 Medium
   ├─ Unverified（无论 Conflict）→ **不得 High**（通常 Medium / Unknown）
   └─ Conflict 且无开放证据 ────→ **不得 High**
   （End-user Path 跳过本步）
   ▼
8. 判 Low 前必须核对"降级三条件"（见 current-treatment-rules.md 第四节）
```

**封顶规则速记（V1.1 更新）**

| 缺失项 | 封顶 |
|---|---|
| **Gate ∈ {Moderate, Weak}（End-user）** | **`Medium`** |
| **`Partner Cooperation Evidence = Unverified`（Partner）** | **`Medium`**（**不得 High**） |
| **`Partner Cooperation Evidence = Conflict` 且无开放证据（Partner）** | **`Medium`**（**不得 High**） |
| **`Supported` + Conflict = Yes（Partner）** | **通常最高 `Medium`** |
| **Gate = Unknown（End-user）** | **`Unknown`** |
| **Industry Fit = Unknown** | **`Unknown`** |
| 无活动 / 能力确认 | `Medium` |
| 无 PWE **且** 无 CSD | `Medium` |
| 主体级证据仅 1 项 | `Medium` |
| 主体未核实 | `Unknown` |
| Path 未定 | `Unknown` |

> ⚠️ **已不存在"无询盘 → 最高 Medium"这条封顶。** `PWE` 单独成立即可支撑 `High`。

---

## 九、常见错误对照（必读）

| # | 错误写法 | 问题 | 正确写法 |
|---|---|---|---|
| 1 | `Industry Fit = Target` → `High` | 禁止推导 | 逐项对照；仅行业对口 → 最高 `Medium` |
| 2 | "它是电池行业" → `High` | **红线 2** | 必须列 ≥ 2 项主体级证据 |
| 3 | 无询盘 → 封顶 `Medium` | **V1.1 已删除** | 有 PWE 即可支持 `High` |
| 4 | 有 ETP / ZLD → `Low` | 已有设施 ≠ 无机会 | 先核对窗口信号与降级三条件 |
| 5 | EPC 型主体按"自身废水"判 | Partner Path 口径错 | 判"是否会纳入交付组合 + 渠道 / 项目证据" |
| 6 | 写"该行业通常产生高浓度废水" → `High` | 行业经验值替代企业事实 | `Unknown`，或补主体级证据 |
| 7 | 采信非公开来源推断工艺 | 工艺属企业信息 | 仅采信公开可验证来源，否则跳过输入 5 |
| 8 | 缺 `Reason` / `Evidence` / `Confidence` / `Opportunity Type` | 判定无效 | 四项必填 |
| 9 | 字段留空 | 破坏主卡完整性 | 无法判断时也要输出 `Unknown` |
| 10 | 有工业废水 / 生产废水 → T3 `Target` | **Patch A 已收紧** | T3 须有高 COD / 难降解 / 难处理证据；否则 `Adjacent` / `Outside` / `Unknown` |
| 11 | 有废水处理设施 / 排污许可 → `High` | **红线 3**；废水相关性 ≠ BDD 相关性 | 先判 Gate；非 `Strong` 不得 `High` |
| 12 | 有制造 + 有废水 → Gate `Strong` | 档位虚高 | `Strong` 须命中 AOP / 难降解 / 高 COD / 处理受限等信号 |
| 13 | **Partner EPC 能力强 / 项目多 → `High`** | **本 Patch 修正** | 能力 ≠ 合作机会；须过 `Partner Cooperation Evidence Gate` |
| 14 | **Partner 技术组合与 BDD 场景重叠 → `High`** | **本 Patch 修正** | 场景重叠 ≠ 合作机会；须有第三方集成 / 采购 / 合作机制证据 |
| 15 | **Partner 自研程度越高越值得开发** | 方向性错误 | 自有路线越封闭，Boromond 越难切入；`proprietary` 是减分项 |
| 16 | `Cooperation = Unverified` → 顺手把 `Demand Status` 也降档 | 字段独立性被破坏 | 两者双向独立，不得互相迁移 |

---

## 十、与 Industry Fit 的关系

| | Industry Fit | BDD Relevance |
|---|---|---|
| 层级 | **行业级** | **公司 / 伙伴级** |
| 口径 | 商业定位 | 机会场景 |
| 输入 | 只要行业 / 业务属性 | 8 项输入 + Path |
| 主体差异 | 同行业取值相同 | **同行业内每家公司可不同** |
| 可否互相推导 | ❌ | ❌ |

> **同行业内取值可变**——这是 BDD Relevance 存在的全部意义。

---

## 十一、与其他文件的职责边界

| 文件 | 负责 |
|---|---|
| **本文件** | BDD Relevance 判定（分 Path 逻辑 → 四值 + 四项附注） |
| `bdd-fit-rules.md` | Industry Fit 判定（含最小目标市场地图） |
| `customer-type-playbook.md` | 客户类型 + Path 分流 |
| `current-treatment-rules.md` | 现有处理方案 / 技术组合的提取与判读 |
| `opportunity-type-rules.md` | Opportunity Type + Priority Site |
| `wastewater-signal-map.md` | 从文字识别 CSD 与特征信号 |
| `lead-signals.md` | 从外部来源检索 PWE 与环境证据 |
| `evidence-policy.md` | 标注 FACT / INFERENCE / UNKNOWN；Demand Status 与 Commercial Risk 定级 |

**本文件不做技术可行性判断，不输出任何技术参数与数值区间。**

---

## 十二、待校准项

| # | 待确认 | 归属 |
|---|---|---|
| 1 | `High` 要求"≥ 2 项主体级证据"是否过严 / 过松 | 销售 |
| 2 | `Low` 的"降级三条件"是否符合实际经验 | 销售 + 技术 |
| 3 | Partner Path 的"技术组合重叠"如何界定更可靠 | 技术 |
| 4 | 8 项输入是否需要增删 | 销售 + 技术 |
| 5 | **Gate 的 `Strong` 信号清单是否需要增删**；`Moderate` 与 `Strong` 的边界（「富溶剂工艺」vs「已明载难降解」）是否清晰 | 销售 + 技术 |
| 6 | **Gate 结果是否需要业务可视化位**（当前只进 Markdown 附录 B，业务 PDF 不可见） | 销售 |
| 7 | **T3 证据门槛是否导致目标市场召回损失**（需重跑历史客户评估） | 销售 |
| 8 | **`Partner Cooperation Evidence` 四档的 `Confirmed` / `Supported` 边界**（「集团内网络成员提供核心工艺」是否算 Confirmed） | 销售 + 技术 | Partner 档位偏差 |
| 9 | **合作证据强度两维度（BDD 域相关性 / 机制外部性）的定档权重**是否够用 | 销售 | High / Medium 边界 |
| 10 | **Partner Gate 是否导致 Partner 机会普遍下沉**（多例同时重算后档位普遍下降） | 销售 | 渠道开发优先级 |
