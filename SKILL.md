---
name: bdd-inquiry-analyzer
description: |
  BDD（掺硼金刚石）/ 电化学氧化工业废水处理业务的客户情报与企业背调工具，服务 Boromond（波乐美）业务口径。
  【自动触发】无需用户点名本 Skill。只要意图是查清一家工业企业是什么、是不是 BDD 潜在客户、值不值得开发，就应主动调用——即使对话中完全没有出现 BDD / 波乐美 / 废水字样。
  【触发意图】1) 背调某家公司；2) 分析某家公司；3) 查这家公司什么来头 / 是做什么的；4) 判断这家公司是不是 BDD 潜在客户 / 值不值得开发 / 该不该跟；5) 调查企业主营业务 · 产品 · 工厂 · 产线 · 行业 · 规模；6) 调查企业环保与废水情况（是否排污、有无污水站、环评公示、排污许可、环保处罚）；7) 调查企业与 BDD 的相关性；8) 查找企业潜在需求信号；9) 查找应该联系的部门或职位；10) 判断该走终端客户还是渠道 / 工程合作伙伴路线；11) 用户仅提供公司名 / 官网 / 域名 / 名片 / 询盘原文 / 邮件 / 聊天记录就要求分析客户。
  【输入门槛】只要给出公司名或网址即可启动；信息缺失时输出 Unknown，不得编造。
  【输出】两层客户情报卡：一页主卡（13 字段：公司 / 国家 / 做什么 / 客户类型与路径 / 行业匹配 / 现有废水处理或技术组合 / BDD 机会与机会类型 / 需求状态 / 优先厂区 / 该联系谁 / 缺什么 / 下一步 / 销售结论）+ Evidence 附录（每条标注 FACT / INFERENCE / UNKNOWN + Source + Reason + Confidence + Decision Impact）。同时输出 Markdown 与 PDF（业务员版三页：客户快照 / 为什么是这个客户 / 关键证据）；最终交付只有这两个文件，HTML · 截图 · comparison · debug 等中间产物一律不交付。
  【适用范围】仅用于工业废水治理相关业务的潜在客户——化工、制药、印染、焦化、电镀、半导体、新能源电池、危废、垃圾渗滤液、工业园区污水等领域，含终端业主、环保工程公司、系统集成商、设计院、科研院所、贸易分销商。
  【排除】不做方案设计、选型、工程计算、项目跟进与报价类交付，不代写邮件，不进入小试流程。体育用品 / 泳帽泳镜等消费品外贸询盘 → 改用 ai-inquiry-analysis；纯财务 · 股价 · 投融资分析、纯工商信息查询、招聘求职背调、供应商验厂、非工业类公司分析 → 不用本 Skill。
agent_created: true
---

# BDD 客户情报与背调 · V1.2.1-b

针对 BDD 电极 / 电化学氧化废水处理业务（Boromond / 波乐美）的客户情报工具。

> **V1.2.1-b · 判断一致性修复（2026-10-26）**：这是当前生效补丁。Partner报告先读 `references/partner-judgment-contract.md`；应用重叠不等于直接替代；竞争、BDD机会、开发优先级、采购意向、技术合作潜力分别判断。先完成官网导航/页脚/团队/合作检索再评级，不因预先评低而跳过联系人检索。性能宣传须标 Company-stated claim，独立验证另取证。Partner证据以 `scripts/decision_engine.py` 复算，输入放在附录B的 `bdd-decision` JSON代码块；真正出PDF的 `scripts/render_pdf.py` 会强制核对。保留13主卡字段、五值结论和End-user原有规则；不改发送权限，不重评历史档案。


**唯一职责：对潜在客户进行完整企业背调，输出客户开发判断依据。**

**产出不是一份漂亮的背调报告，而是一页情报卡：这家公司是什么、机会在哪、值不值得投入、缺什么、该找谁、下一步做什么。**

> **V1.2.1-a · 联系人字段四要素写法（2026-10-21 · 最小质量修复）**：`关键联系人 Contact` 字段凡同时含「官方角色信箱 / 具名联系人 / 非目标岗具名」，**必须按四要素分段明示**——① 官方渠道（角色信箱＋来源）② 具名（Verified）＋职务照录 ③ 岗位相关性（目标岗 / 非目标岗，非目标岗标 Known / Escalation）④ 决策权一律写 `未知`。**具名个人邮箱不得混入官方渠道、媒体/市场联系人不得作 Primary**。触发案例：某环境工程客户（已背调样例；具名媒体联系人邮箱被下游执行器误判为通用渠道首位）。详见 `references/contact-role-map.md` 情况 B′ 写法补充。**不新增 Internal Key、不改渠道 4 态判定逻辑、不改任何评级**。

> **V1.2.0 · 证据边界修订（2026-10-10）**：① Partner 的销售/订单与**外部 BDD 相关需求**分开；② 母公司证据不得直接抬高子公司机会或需求；③ `Conflict` 在审计层区分直接竞争、工程重叠和部件采购切面；④ `Financial Warning` 的 `No/Unknown` 按检索覆盖与主体层级统一。具体规则以 `references/evidence-policy.md` 第四、六节、`references/bdd-relevance-rules.md` 第五节、`references/sales-conclusion-rules.md` 第 1b 步为准。13 个主卡字段、五值结论和 PDF 三页结构保持不变；历史档案不自动改判。
> **出卡回归**：边界例见 `references/v12-calibration-cases.md`；必须重核当次证据，不能按公司名套档位。
> **V1.2.1 · 业务员首屏优化（2026-10-12，仅展示层）**：PDF 第一页改为「决策 / 行动优先」—— Sales Conclusion 原结论卡置顶，紧接 Next Action，随后 Who to Contact 与 What Is Missing；其后为 `01 WHO` / `02 WHY` / `03 WHERE` 三组事实。**13 个 Internal Key 全部保留且每项只显示一次**（12 个字段行 + 1 张结论卡）；主卡表格保留「字段 / 判定」表头行。字段含义、判定值、颜色映射、Page 2 / Page 3 结构、Markdown 输出与归档规则**一律不变**。渲染层只搬运 Markdown 已有字段，不生成新内容、不新增分数或优先等级。详见 `references/output-visual-rules.md` 第九部分。

> **V1.1 相对 V1 的四处升级**（详见第十一节）：
> ① **客户分流**：新增 End-user Path / Partner Path —— 渠道与工程型客户不再按"自身废水"评判；
> ② **废水证据分类**：拆为 `PWE`（公开废水证据）/ `CSD`（客户侧需求陈述），**删除"无询盘 → 最高 Medium"封顶**；
> ③ **字段扩充**：新增 `Current Wastewater Treatment / Technology`、`Opportunity Type`、`Priority Site`、`Financial Warning`、`Sales Conclusion`；
> ④ **输出形态**：颜色语义 + 一页主卡（大白话）+ 三页业务员 PDF。

> **V1.1.1 Presentation Patch（仅展示层）**：
> ① 13 个 **Internal Key 完全不变**，仅新增中英文 **Display Label**（公司 Company / 国家 Country / …）；
> ② 第一页按 **WHO → WHY → WHERE/WHO → ACTION** 四组呈现；
> ③ `Current Treatment` 增加**显示状态**：`Confirmed` / `Partial` / `Planned` / `Unknown`，**只能来自现有证据，不得推断**；
> ④ `Sales Conclusion` 改为第一页**结论卡**（五色 + 1~2 句原因）；
> ⑤ Markdown 完整 Evidence 结构不变；PDF 仍约 3 页。
>
> **本 Patch 不修改任何判断规则**（Evidence Policy / Customer Path / Industry Map / BDD Opportunity / Demand Status / Commercial Risk / Opportunity Type / Priority Site 逻辑全部原样），
> **不新增字段、不新增 Skill、不新增评分、不新增 CRM 功能**。展示层规则见 `references/output-visual-rules.md` 第二部分。

> **V1.1.2 UI Refinement Patch（仅展示层）**：
> ① 字段列浅灰蓝底 + 固定 20% 宽 + 垂直居中；短状态渲染为 **Badge**（不整行染色，红色只用于风险/冲突/负面）；
> ② Section Header 加编号：`01 WHO ｜客户是谁` / `02 WHY ｜为什么值得看` / `03 WHERE / WHO ｜从哪里切入` / `04 ACTION ｜现在怎么办`；
> ③ `Current Treatment` 四态中文显示（已确认 / 部分确认 / 规划中 / 未知），**判据与状态来源不变**；
> ④ 第一页长字段压缩：`摘要⟪P2⟫其余` —— 摘要为**原文精确前缀**，其余进 Page 2「字段详细内容」，**一字不删**；
> ⑤ 结论卡强化：中文结论 16pt 加粗 + 英文副标题 + 左侧色条；
> ⑥ Page 3 由 7 列表格改为 **Evidence Card**（默认 6 条 High/Medium，**完整 Evidence 仍保留在 Markdown**）。
>
> 展示层规则见 `references/output-visual-rules.md` 第三部分。

> **V1.1.3 Sales Usability Patch（仅展示层 + 默认调用协议）**：
> ① **新增「零、Default Invocation Protocol」** —— 日常只给公司名 / 网址 + 表达背调意图即自动跑完整流程，**不需要用户复述版本号、13 字段、禁止预设、输出格式**；
> ② **Page 1 完全不变**；
> ③ **Page 2** 由「字段详细内容」表 → **`SALES INTELLIGENCE ｜开发情报`**，改为 5 张销售信息卡：Why BDD / Current Treatment / Priority Site / Who to Contact / What to Verify（**不再使用大型字段表**）；
> ④ **Page 3** 由 Evidence 明细 → **`KEY EVIDENCE ｜关键依据`**，6~8 条，每条只写 **主题 / 简洁事实 / Source**，**PDF 不显示 FACT · INFERENCE · Confidence · Decision Impact 等审计术语**；
> ⑤ **审计与边界信息**（可溯源率 / 类型定义 / 实体排除 / 来源冲突 / 边界声明 / Technical Fit 与 Quotation Readiness 冻结说明）**移入 Markdown 附录 B，不进入业务 PDF**；Markdown 附录 A 的完整 Evidence **一字不删**。
>
> **本 Patch 不修改任何客户判断逻辑**（Evidence Policy / Customer Path / Industry Map / BDD Opportunity / Demand Status / Financial Warning / Commercial Risk / Priority Site / Sales Conclusion 全部原样），
> **不新增字段、不新增 Skill、不新增评分、不新增 CRM 功能**。版式规则见 `references/output-visual-rules.md` 第五部分。

> **V1.1.3 · Financial Warning Rule Patch（2026-09-27，规则修订）**：
> ① **`Financial Warning = Yes` 收窄为"财务困境证据"**（资不抵债 / 破产 / 流动性危机 / 债务违约 / 持续经营疑虑 / 法院或债务层面财务重组 / 集团层面重大亏损且有明确财务压力 / 官方披露重大财务困难），必须附可靠公开 Source；
> ② **新增 `Business Change Signal`**（`Yes / No / Unknown`）—— 裁员 / 高管变化 / 组织架构调整 / 业务单元调整 / 工厂整合 / 产能调整 / 业务组合调整 / 战略转型 / **单一厂区经营亏损** / 降本计划，**从 Financial Warning 移出**；
> ③ **`Business Change Signal = Yes` 不得单独触发** `FW = Yes`、`Commercial Risk = High`、`Sales Conclusion` 降档、`BDD Opportunity` 降档、`Demand Status` 降档 —— 只作 **Context / Watch Item**；
> ④ **`FW = Yes` 不得机械降档** —— 必须经四问（严重程度 / 主体层级 / 采购与付款能力 / 项目执行能力），并在结论原因中**解释为什么该财务风险影响或不影响本次判断**；
> ⑤ **集团与厂区风险分开**；证据冲突时**不得用单条负面新闻覆盖更完整的集团财务事实**。
> 详细规则见 `references/evidence-policy.md` 第六、七节与 `references/sales-conclusion-rules.md` 第 4b 步。

> **BDD-Specific Relevance Gate Patch（2026-09-27，规则修订）**：
> ① **Patch A · T3 定义收紧** —— `T3` 必须由**废水性质证据**（高 COD / 难降解 / 难处理 / 深度处理 / AOP 需求 / 明确复杂污染物）成立；
> **只存在工业废水 / 生产废水 / 阳极氧化废水 / 机加工废水 / 压铸废水 / 普通表面处理废水 / 一般排污许可 / 废水处理设施 / 废水量数据时，一律不得判 T3 `Target`** —— 改落 `Adjacent` / `Outside` / `Unknown`（`bdd-fit-rules.md` 第二节）；
> ② **Patch B · 新增 `BDD-Specific Relevance Evidence Gate`**（`Strong` / `Moderate` / `Weak` / `Unknown`），作为 **End-user `BDD Opportunity = High` 的第 5 个硬门槛**；
> `Strong` → `High`；`Moderate` / `Weak` → 上限 `Medium`；`Unknown` → `Unknown`（`bdd-relevance-rules.md` 第四节）；
> ③ **只作用于 End-user**；Partner Path 规则、Demand Status、Financial Warning、Priority Site、Current Treatment、Opportunity Type、Sales Conclusion 五值体系**全部未改**；
> ④ **不新增 Internal Key、不新增 PDF 字段、不新增评分、不新增 Skill**；Gate 结果只记入 **Markdown 附录 B**。
>
> 详细规则见 `references/bdd-fit-rules.md` 第二节与 `references/bdd-relevance-rules.md` 第四、五节。

> **Partner Cooperation Evidence Gate Patch（2026-09-27，规则修订 · 仅 Partner Path）**：
> ① **新增 `Partner Cooperation Evidence` 内部 Gate**（`Confirmed` / `Supported` / `Unverified` / `Conflict`），回答**唯一问题**：
> **是否存在公开证据表明 Boromond / 第三方 BDD 技术有机会进入该 Partner 的技术、采购或项目交付体系？**
> ② **Partner `BDD Opportunity = High` 增加两条硬门槛**：**E** `Partner Cooperation Evidence ∈ {Confirmed, Supported}`；**F** **Conflict 控制**（有 `Conflict` 必须解释竞争边界，且**仅当同时具备 `Confirmed` / 强 `Supported` 合作开放证据时**才允许 `High`）；
> ③ **三条分离硬规则**：`Strong Technical Capability` ≠ `High Cooperation Opportunity`；`Strong Scenario Overlap` ≠ `High Cooperation Opportunity`；**技术越 proprietary 不得解释为越有吸引力**（对 Boromond 意味着更难切入）；
> ④ **`Conflict` 不再是装饰性标签** —— 出现 `Conflict` 时判 `High` 前必须检查 5 项，**其中「第三方集成机制」与「外部核心组件采购证据」均 `Unknown` 时不得判 `High`**；
> ⑤ **只作用于 Partner Path** —— End-user Path、`BDD-Specific Relevance Gate`、T3、`Demand Status`、`Financial Warning`、`Priority Site`、`Current Treatment`、`Opportunity Type`、`Sales Conclusion` 五值体系、PDF 结构与 13 个 Internal Key **全部未改**；
> ⑥ **不新增字段 / 评分 / 0–100 分制 / PDF 字段**；档位只记入 **Markdown 附录 B（审计层）**。
>
> 详细规则见 `references/bdd-relevance-rules.md` **第五节**，`Conflict` 边界见 `references/opportunity-type-rules.md` 第三节。

> **Delivery Scope Rule（2026-09-27，输出规则 · 不改版本号）**：
> ① **日常客户背调模式的最终交付只有两个文件**：`{Company}_BDD_Intelligence_{YYYY-MM-DD}.md` + 同名 `.pdf`；
> ② **Page PNG、截图、HTML、`_*-comparison`、debug 输出、临时提取文件，一律只是内部渲染 / 回归测试的中间产物**，**不得作为最终交付展示**，**任务结束后不列入用户产物、不进入交付清单**；
> ③ **仅当用户明确要求**「视觉检查 / PDF 回归 / Before-After 对比」时，才输出图片类测试产物；
> ④ **本规则只约束交付范围**，**不修改** PDF / MD 内容、判断规则、13 个 Internal Key、三页结构、`render_pdf.py` 与输出机制。
>
> 详见 `references/output-visual-rules.md` 第四部分与第六部分第 9 条。

> **V1.1.4 Customer Archive Patch（2026-09-28，新增归档层 · 不触碰判断层）**：
> ① **新增 `scripts/archive_report.py`（归档层）** —— 背调完成后把 `.md` + `.pdf` **复制**一份到本机客户档案库
> `customer-archive/<规范化公司名称>/`，逐步沉淀可长期复用的 BDD 客户档案；
> **（V1.1.5 起改为「归入 + 清理源文件」——档案库为唯一存放地，见下方 Single-Home Patch）**
> **归档根解析顺序固定**：`--archive-root` → **环境变量 `BDD_ARCHIVE_ROOT`** → **当前工作区根下的 `customer-archive/`**
> （工作区根 = 从 cwd / 报告目录向上找到的第一个含 `.workbuddy/` 或 `.git/` 的目录，跳过用户主目录）；
> **归档根绝不允许落在 Skill 源码目录内**（命中即拒绝，exit 6）—— 档案只在本机，不随源码入库；
> ② **客户识别优先级**：**官网域名 → 公司名核心词全等 → 登记别名 → 名称核心词前缀**
> —— 最后一条专治「首次用全称建档、后续用缩写再查」导致的重复建档；
> **必须是整体前缀**（`Acme` ⊂ `Acme Waste Water Treatment`），
> **仅共享首词一律不合并**（如 `Acme Green Water Ltd` ≠ `Acme Water Solutions Pte Ltd`），只输出人工确认提示；
> ③ **同名冲突永不覆盖**：`{原名}_{YYYY-MM-DD}.md` → 已存在则 `_HHMM` → 再冲突则 `_HHMM_v2` / `_v3` 递增，历史报告全部保留；
> ④ **同内容幂等**：以报告 sha256 去重，同一份报告重复归档不产生冗余文件；
> ⑤ **每个客户目录内维护 `_customer.json`（保留）** —— 客户标识 + 报告清单（客户名 / 别名 / 域名 / 报告清单）；
> **是目录标识文件，不是数据库、不是 CRM、不是业务模块**；丢失 / 损坏时脚本可从目录内既有报告自动重建；
> ⑥ **只复制、不移动、不删除、不覆盖、不联网**；归档前后报告逐字节一致（脚本内 sha256 自校验）；
> ⑦ **归档产物不进交付清单** —— 交付仍只有 `.md` + `.pdf` 两个文件，归档是**本机留档动作**，
> 且必须向用户报出**档案保存位置**。
>
> **本 Patch 不修改任何判断与呈现**：13 个 Internal Key、`Partner / End-user` 规则、Evidence Policy、
> Financial Warning 白名单、`Demand Status`、`Priority Site`、`Sales Conclusion`、
> 三页 PDF 版式、`render_pdf.py` 全部**原样未动**；
> **不新增字段 / 不新增评分 / 不新增 Skill / 不新增数据库与 CRM 界面**。
> 注：`references/` 各文件内的版本标注沿用其**规则所属版本**（V1.1.3 及更早），本 Patch 未改动其中任何规则。

> **V1.1.5 Single-Home Patch（2026-09-28，归档层 · 消除重复文件）**：
> ① **档案库成为报告的唯一存放地** —— 归档成功后**清理工作区根目录的那一份**，不再同时留两份；
> ② **安全性质（四条，不可绕过）**：
> **ⓐ** 只有**归档成功且逐字节 sha256 校验通过**之后，才允许删除源文件；
> **ⓑ** 归档失败 / 目标已存在 / 校验不一致 / 归档根被拒 → **一个源文件都不删**；
> **ⓒ** 源文件本身位于档案库内 → **不删**（否则会毁掉档案副本）；
> **ⓓ** `--dry-run` 与 `--keep-source` → **不删**；
> ③ **交付位置随之变更**：交付物在 **档案库客户目录内**（`customer-archive/<公司>/…`），
> 工作区根目录**不再保留副本**；回复中报出的「交付位置」即为该目录；
> ④ `--keep-source` 可退回旧行为（保留源文件），供调试或需要平铺视图时使用；
> ⑤ **只改归档层**：渲染层 `render_pdf.py` 与判断层**零改动**（归档层自己做清理，不污染渲染层）。
>
> **起草理由**：V1.1.4 会在工作区根与档案库各留一份，两份之间**没有同步机制** ——
> 改动任一份都会造成静默漂移，且每完成一家客户就向根目录堆积 2 个文件。
> 这与「同一 Skill 存在两份副本会漂移」是同一类缺陷。

> **V1.1.6 Contact / Next Action Usability Patch（2026-09-29，仅改写法与字段内部结构 · 不触碰判断层）**：
> ① **`关键联系人` 改为「主体（法人 / 业务主体）→（职能单位 →）目标岗位」** ——
> **职能单位必须有公开来源**；无来源时**退化为「主体 → 岗位」，不得为凑齐三段而推测部门名称**；
> 主体一律按**法人口径**（品牌 ≠ 登记主体时写实际经营主体）。
> ② **`关键联系人` 在 `No verified contact found` 时不得停住** —— 必须附「**建议检索路径**」（固定六项，见 `references/contact-role-map.md` 第三节情况 C），
> **只回答"下一步去哪里找这个角色"，不生成人名 / 邮箱 / 电话、不推断邮箱格式、不采信第三方聚合站数据**；
> **该「建议检索路径」不属于证据来源白名单**（白名单仅约束"展示真人"），不得据路径推断任何人名。
> ③ **新增「部分具名联系人」规则**（`references/contact-role-map.md` 第三节情况 B′）——
> 公开来源存在具名、但该具名**不是当前 Primary Contact 岗位**时：**可以**展示该具名及来源（标为 Known / Escalation / Secondary），
> **但不得把 Primary Contact 标记为「已找到」**，Primary Contact **仍须**输出目标角色 ＋ `No verified contact found`；
> **不得因为存在一个公开姓名就推断其能负责当前技术项目**。**不新增 Internal Key。**
> ④ **`下一步` 接入 `must-ask-params.md` 第六节的类型加问项**（**唯一来源，只引用不另立清单**）——
> 主卡只留最关键 1 项，完整清单进 Page 2；`类型 → 组` 映射见 `references/sales-conclusion-rules.md` 三之二。
> ⑤ **`Conflict = Yes` 时 `Next Action` 必须以「先确认合作 / 竞争边界，再进入技术讨论」开头**，并列明本阶段不主动释放范围——
> **禁止范围逐项复用现有规则定义（硬规则 17 / `current-treatment-rules.md` / `evidence-policy.md`），不新造禁止项、不新造 `Conflict` 判断标准**。
> ⑥ **新增「Page 2 明细写法纪律」**（`assets/output-card-template.md`）——
> Page 2 显示字段**完整原文**，明细过长会把 Page 2 挤成两页（共 4 页）；此时**压缩 Page 1 摘要无效**（实测三种改法全部失败）。
> 写法：**依据用 `E#` 引用不展开 · 加问项紧凑排版 · 检索路径一行平铺**；**不得删除任何信息点**。
> **篇幅预算（当前模板经验预算 · 非绝对物理上限）**：Page 2 明细合计（12 字段 `⟪P2⟫` 之后字符数之和）——
> **≤ 3,800 字符：正常**；**3,801 – 4,000 字符：警戒区，必须执行 PDF 渲染检查**；**> 4,000 字符：高溢出风险，优先紧凑化处理**。
> 实测依据：4,012 字符 → 3 页（通过）、4,862 字符 → 4 页（溢出）；**是否溢出最终以实际 PDF 渲染结果为准**。
> ⑦ **明确不做**：`Next Action` 不扩展为开发信 / 话术 / 跟进节奏 / 时间节点 / 联系人评分 / SDR 流程。
>
> **本 Patch 不修改任何判断逻辑**：13 个 Internal Key、`Customer Type / Path`、`Industry Fit`、`BDD Opportunity`、
> `Partner Cooperation Evidence Gate`、`Demand Status`、`Commercial Risk`、`Financial Warning`、`Business Change Signal`、
> `Current Treatment`、`Priority Site`、`Sales Conclusion`、`Contact Strategy Matrix`、三页 PDF 结构、`render_pdf.py`
> **全部原样未动**；**不新增字段 / 不新增评分 / 不新增 Skill / 不新增联系人自动搜索**。
> 注：`references/` 各文件内的既有规则条款内容未改，仅在 `contact-role-map.md` 与 `sales-conclusion-rules.md` 中**新增**本 Patch 对应条款。

> **历史已知缺口（V1.2.1 状态）**：
> ① **`Commercial Risk` 判据与背调场景不相容** —— `evidence-policy.md` 5.1 的危险信号**全部为「互动行为型」**，而「仅给网址」的背调必然无互动事实 → `Risk` 恒为 `Unknown`；
> 由此纯公开背调的第 3 步（要求 `Risk ∈ {Low, Medium}`）通常不可达；`contact-role-map.md` 的矩阵也缺少互动输入。**本次不把「可核查度」冒充商业风险，不为增加档位而放宽第 3/4 步**；先用 V1.2.0 的需求与主体门槛复核新样本，再用真实互动记录校准该联动。
> ② **Partner Gate 的 `Supported` 与 `Unverified` 封顶值相同**，导致"是否具备第三方集成机制"这一核心判据在档位上无差别（累计 5 例 `Medium`；`Confirmed + Conflict` 两路径已验证可落 `High`）。
> ③ **`Next Action` 三段式**（信息动作 / 推进动作 / 本轮不做）暂缓，待观察 ①②③④ 的实际使用效果。

---

## 零、Default Invocation Protocol（默认调用协议 · V1.1.3 新增）

**日常使用直接调用，用户不需要复述任何固定规则。**

只要用户提供 **Company（公司名）** 或 **Website（官网 / 域名）**，并表达下列任一意图，**默认自动执行完整的 BDD Customer Intelligence Workflow（14 步）**，**不追问、不要求确认**：

| 触发意图 | 示例输入（原样即可触发完整流程） |
|---|---|
| 背调 | `背调 <公司全称>，<官网域名>` |
| 客户分析 | `分析客户：<公司全称>，<官网域名>` |
| 是否值得开发 | `<公司全称> 是否值得作为 BDD 客户开发？` |
| 其他同义表达 | 查一下这家公司 / 这家公司什么来头 / 判断一下是不是 BDD 客户 / 帮我看看 `<官网域名>` |

### 默认行为（用户无需重复输入）

| 项 | 默认 |
|---|---|
| 执行范围 | **完整 14 步工作流**（公司核实 → 证据收集 → … → 销售结论 → 证据附录） |
| 输出形态 | **最终只交付两个文件**：`{Company}_BDD_Intelligence_{YYYY-MM-DD}.md` + 同名 `.pdf`；渲染后**归档**到 `customer-archive/<规范化公司名称>/`（V1.1.4），**归档成功后清理工作区根的那一份（V1.1.5）** → **档案库即交付位置**，并须报出该位置 |
| 交付边界 | **渲染中间产物不进交付** —— HTML / Page PNG / 截图 / comparison 目录 / debug 输出 / 临时提取文件仅作内部渲染与回归用，**任务结束后不列入用户产物**（详见下节） |
| 版本号 | 自动使用**当前版本**，无需用户声明 |
| 13 个 Internal Key | 自动按模板逐字段输出，**无需用户逐字段列出** |
| 预设禁令 | 自动执行：**不得预设** Customer Type / Industry Match / BDD Opportunity / Demand Status / Financial Warning / Business Change Signal / Commercial Risk / Priority Site / Sales Conclusion 中的任何结论；集团证据与目标主体证据先分层 |
| 缺失信息 | 自动写 `Unknown`（含三态后缀），**不得编造、不得为凑齐字段而反问** |
| 检索要求 | 自动执行证据检索优先级（处罚 / 许可 / 环评 / PWE / 招投标 / 厂区级 / 集团级） |

### 最终交付边界（Delivery Scope · 2026-09-27 新增 · 2026-09-28 更新存放位置）

**日常客户背调模式下，交付清单永远只有两个文件：**

```
customer-archive/<规范化公司名称>/{Company}_BDD_Intelligence_{YYYY-MM-DD}.md    ← 权威版本（含附录 A 完整 Evidence + 附录 B 审计信息）
customer-archive/<规范化公司名称>/{Company}_BDD_Intelligence_{YYYY-MM-DD}.pdf   ← 业务员版（三页）
```

> **V1.1.5 起，这两个文件存放于档案库客户目录内，工作区根目录不再保留副本。**
> 渲染时源文件先落在工作区根（`render_pdf.py` 的默认行为不变），归档成功后由归档层清理 ——
> 因此**任务结束时工作区根不应残留任何 `*_BDD_Intelligence_*` 文件**；若仍在，说明归档没跑完或失败了。
> 这是一条**可见的自检信号**。

**以下全部为内部中间产物，不得作为最终交付展示、不得列入用户产物：**

| 类型 | 示例 |
|---|---|
| 渲染中间态 | `*.html`（含内联 CSS 的中间 HTML）、单页分解 HTML |
| 视觉产物 | `*_Page1.png` / `*_Page3.png` 等页面截图、Before / After 对比图 |
| 对比目录 | `_*-comparison/`、`_*-preview/`、`_shot_*/` |
| 调试输出 | 逐页 / 逐块诊断 PDF、`_dg_*` / `_chk_*` 临时文件、临时 profile 目录 |
| 临时提取 | 从 PDF 抽取的中间文本（如 `*_text.txt`）、下载的原始 PDF 缓存 |

**唯一例外 —— 仅当用户明确要求时才输出图片类测试产物：**

| 触发条件（用户显式提出） | 允许输出 |
|---|---|
| 视觉检查 / 看看排版 | 页面 PNG |
| PDF 回归 / 逐页检查 | 逐页 PNG 或单页 PDF |
| Before / After 对比 | 对比截图 |

> **本规则是交付范围规则，不是内容规则。** 禁止因此修改 PDF / MD 内容、判断规则、13 个 Internal Key 或现有三页结构 —— 中间产物再多，产出的 `.md` / `.pdf` 仍必须完全一致。

### 仅两种情形才需要向用户追问

1. **既没有公司名、也没有网址** —— 无法核实主体；
2. 公司名存在**多个完全不同的同名主体**，且上下文无法判断指的是哪一个（不得"选最像的一家"）。

### 严格回归测试 Prompt 保留（不得删除）

需要逐项核对规则时，用户仍可使用**显式规格句式**（重申版本号 + 禁止预设 + 逐字段要求 + 输出格式），
例如：「严格按照当前 V1.2.1 规则执行。不预设 BDD Opportunity、Demand Status、Priority Site 或 Sales Conclusion。按标准格式输出 Markdown + PDF。」

**本协议不覆盖、不简化、不替代该用法** —— 显式规格仍然逐条生效。

---



### ✅ 本 Skill 只负责

1. **BDD 客户完整企业背调** —— 公司核实 + 公司概况 + 外部证据检索（含公开废水证据）
2. **客户开发判断** —— 客户类型与路径 / 行业匹配 / BDD 机会与机会类型 / 需求状态 / 商业风险 / 缺失信息 / 联系策略 / 下一步 / 销售结论

### ❌ 本 Skill 不负责（明确排除）

| 不做 | 归属 |
|---|---|
| Technical Fit（技术匹配度） | 平台计算层 / 工程师（阈值见归档区） |
| Current 处理方案的**技术可行性判断** | 工程师（本 Skill 只记录"现在用什么"，不判"够不够"） |
| 项目报价 / 报价状态 | 商务系统 |
| 设备选型 | 工程师 |
| 小试技术方案 / **小试流程** | 工程师 |
| 工程计算 | 工程师 / 平台计算层 |
| 正式技术方案 | 工程师 |
| 正式项目跟进流程 | 销售 CRM / 人工 |
| 自动邮件 / 回复 | 独立"回复执行" Skill（如需要，另建） |
| 案例数据库 | 平台 |

> **为什么划这条线**：背调只依赖公开信息，不被"数据资产化"瓶颈卡住，能立刻见效。技术判断与报价需要案例库、计算引擎与工程师签字，硬塞进本 Skill 会退化成"LLM 凭常识编参数"，对外使用有真实风险。

### 三类不可越界的输出禁令

1. **不输出工艺参数**（电流密度、停留时间、功耗、电极面积）
2. **不承诺处理效果 / 不承诺达标 / 不承诺通过验收**
3. **不做设备选型、不出技术方案、不出金额与报价状态**

### V1.1 删除的越界规则（务必不要再执行）

| 已删除 | 替代 |
|---|---|
| ~~输出必含"建议小试"~~ | 已删除。小试属执行，不在本 Skill 权限内 |
| ~~固定输出"寄 5~10 L 水样"~~ | 已删除。同上 |
| ~~自动进入小试流程~~ | 已删除。同上 |
| 已确认存在具体项目时 | **只允许输出「转交技术评估流程」** |

> 备注：不生成未经公开来源验证的具体人名 / 电话 / 邮箱（详见 `contact-role-map.md`）。
> 已归档内容路径与回收条件见第十三节。

---

## 二、单向决策链（本 Skill 的骨架，不可跳步）

```
Input（询盘 / 公司名 / 名片 / 聊天记录）
        │
        ▼
Company Verification            公司核实
        │
        ▼
Evidence Collection             证据收集（FACT / INFERENCE / UNKNOWN）
        │
        ▼
Company Profile                 公司概况
        │
        ▼
Customer Type                   客户类型 ──→ Path 分流（End-user / Partner / Undetermined）
        │
        ▼
Industry Fit                    行业匹配        ←── 最小目标市场地图
        │
        ▼
BDD Relevance                   BDD 机会        ←── 按 Path 分支 + Opportunity Type
        │                                          （End-user 另过 BDD-Specific Relevance Gate；
        │                                            Partner 另过 Partner Cooperation Evidence Gate）
        │
        ▼
Current Wastewater Treatment / Technology      ←── 现有方案 / 技术组合（V1.1 新增）
        │
        ▼
Demand Status                   需求状态        ←── PWE + CSD 两类证据
        │
        ▼
Commercial Risk + Financial Warning            ←── 商业风险 + 财务警示（财务困境口径）
        │
        ▼
Business Change Signal                         ←── 业务变化信号（Context / Watch Item，**非判定项**）
        │
        ▼
Missing Critical Information    缺失关键信息    ←── Business → Project → Technical
        │
        ▼
Contact Strategy                联系策略
        │
        ▼
Next Action + Sales Conclusion  下一步 + 销售结论
        │
        ▼
Evidence Appendix               证据附录（呈现，非新判定）
```

### 硬规则

| # | 规则 |
|---|---|
| 1 | **严格单向。** 上游未判定，下游不得先行判定。 |
| 2 | **不得多模块分别调用 LLM 得出互相冲突的结论。** 整张卡由同一次推理产出。 |
| 3 | **不得反向回推。** Next Action 不得倒过来影响上游任何字段。 |
| 4 | **Evidence 前置采集、末尾呈现。** 物理上先产出证据（第 3 步），最后才作为附录展示。**"排在末尾"是输出顺序，不是判定顺序。** |
| 5 | **不做任何自动串联推导。** 每个字段独立依据证据判定。`Demand Status` 在 End-user 与 Partner 两条 Path 均先按 `evidence-policy.md` 的主体/需求对象门槛分别定 `PWE` 与 `CSD`，再取较高者；集团订单与一般产品目录不得自动升档。 |
| 6 | **Path 优先。** Path 未定 → `BDD Relevance = Unknown`、`Opportunity Type = Unknown`、`Sales Conclusion = 信息不足，暂缓判断`。 |
| 7 | **`Industry Fit` 与 `BDD-Specific Relevance Gate` 必须分别取证。** 前者用行业属性（T3 另需废水性质证据），后者用主体级废水性质与处理难点证据；**不得用一方证据顶替另一方**。 |
| 8 | **Partner Path：能力证据与「合作机会」证据必须分别取证。** A~D 属能力 / 场景 / 项目证据；**E（`Partner Cooperation Evidence`）必须另有第三方集成 / 采购 / 合作机制证据**。**不得用 A~D 顶替 E。** |
| 9 | **主体层级优先。** 集团/母公司事实只有在目标主体参与、执行或获明确授权的证据下才计入其合作机会与需求；同一交易不得跨主体重复计数。 |

---

## 三、四个概念必须严格区分

这四个词最容易互相污染，是判断失真的最大来源。

| 概念 | 回答的问题 | 取值 | 数据要求 |
|---|---|---|---|
| **Industry Fit** | 这个**行业 / 业务属性**是否属 Boromond 目标市场？ | Target / Adjacent / Outside / Unknown | 只需行业属性 |
| **BDD Relevance** | 这家公司 / 这个伙伴**是否存在 BDD 可切入的机会**？ | High / Medium / Low / Unknown | 8 项输入 + Path |
| **Opportunity Type** | 这个机会**是什么类型**？ | End-user / Technology Partner / EPC·Integration / Distribution / Unknown | 由客户类型与能力推导 |
| **Demand Status** | 目标主体是否存在与 BDD 可切入场景相关的项目评估 / 外部采购 / 治理需求**证据**？ | Confirmed / Strong Signal / Potential / Weak / Unknown | PWE + CSD；Partner 对外销售仅作背景 |

> Industry Fit 是**行业属性**，BDD Relevance 是**主体级机会判断**，Opportunity Type 是**机会分类**，Demand Status 是**需求事实**。四者证据来源不同，不能互相替代。

### 四条禁止推导（本 Skill 最重要的一组）

> ❌ **Industry Fit = Target → 不得自动推导 BDD Relevance = High。**
>
> ❌ **行业属 Lithium Battery / Battery Materials → 不得自动给 High。** 必须由主体级证据支撑（详见 `bdd-relevance-rules.md` 红线 2）。
>
> ❌ **BDD Relevance = High → 不得推导 Demand Status = High。** 有应用场景 ≠ 这家公司现在有采购需求。
>
> ❌ **不得因"已建 ETP / ZLD"直接判 `Low`。** 已有设施 ≠ 无机会（详见 `current-treatment-rules.md` 第四节）。

### 两条新增禁止推导（BDD-Specific Relevance Gate Patch · 2026-09-27）

> ❌ **"有工业废水 / 生产废水" → 不得自动推导 `Industry Fit = Target`（T3）。**
> T3 需**废水性质证据**（高 COD / 难降解 / 难处理 / 深度处理 / AOP 需求）。详见 `bdd-fit-rules.md` 第二节「T3 证据门槛」。
>
> ❌ **"废水相关性" → 不得自动推导 "BDD 相关性"。**
> 有废水、有处理设施、有排污许可、有水量数据，**只能证明存在废水**；End-user `High` 另需 Gate = `Strong`（详见 `bdd-relevance-rules.md` 第四节）。

**示例（必读）**：某 API 原料药企业
- `Industry Fit = Target`（T2 制药 / 原料药）
- 但**未确认生产活动、无 PWE / CSD、无环境证据**
- → `BDD Relevance = Unknown`（**不得给 High**）

**示例 2**：某电池材料集团
- `Industry Fit = Target`（T1 锂电池材料）
- 若**主体级证据 < 2 项** → 最高 `Medium`。**"它是电池行业"本身不构成任何升级依据。**
- 若主体级证据 ≥ 2 项但**无 refractory / high COD / AOP / 处理受限证据** → Gate ≤ `Moderate` → 最高仍为 `Medium`。

**示例 3**：某工业自动化设备制造商（含阳极氧化线）
- 有制造、有生产废水、有持证处理设施、有废水监测 → 但**只有"普通表面处理废水"**
- → `Industry Fit` **不判 `Target`**（T3 证据门槛未过），落 `Unknown`；→ `BDD Relevance = Unknown`。**不得给 High。**

### 三条新增禁止推导（Partner Cooperation Evidence Gate Patch · 2026-09-27）

> ❌ **`Strong Technical Capability` → 不得推导 `High Cooperation Opportunity`。** EPC 能力强、项目多，**不等于** Boromond 有切入点。
>
> ❌ **`Strong Scenario Overlap` → 不得推导 `High Cooperation Opportunity`。** 技术组合覆盖 BDD 应用场景，**不等于**它会把第三方 BDD 技术装进自己的交付体系。
>
> ❌ **技术越 `proprietary` → 不得解释为"越有吸引力的伙伴"。** 自有路线越封闭，Boromond 越难切入 —— 这是**减分项**。

**示例（必读）**：某大型水处理 EPC
- `Industry Fit = Adjacent`、能力确认、技术组合与 BDD 场景高度重叠、项目与渠道证据充分
- 但**未找到任何第三方技术集成 / 采购 / 合作机制证据**
- → `Partner Cooperation Evidence = Unverified` → **`BDD Opportunity` 不得判 `High`**（通常 `Medium`）

---

## 四、客户类型分流（V1.1 新增）

**先定 Path，再判一切。**

| Path | 客户类型 | Sub-type |
|---|---|---|
| **End-user Path** | 终端业主 | — |
| **Partner Path** | 环保工程公司 | `EPC` |
| | 系统集成商 | `Integrator` |
| | 贸易商 / 中间商 / 分销代理 | `Distributor` |
| | 设计院 · 科研院所高校 · 自有工艺产品线的技术公司 | `Technology Partner` |
| **Undetermined** | Unconfirmed | — |

### 两条路径的判断对象完全不同

| | End-user Path | Partner Path |
|---|---|---|
| 判断对象 | 它自己产生什么废水 | 它能否把 BDD 纳入交付组合 / 渠道 |
| BDD Relevance 依据 | 制造业活动 + PWE / CSD + 窗口信号 | 能力确认 + 技术组合重叠 + 渠道 / 项目信号 |
| 主要机会类型 | `End-user Opportunity` | `EPC / Integration` · `Distribution` · `Technology Partner` |

> ⚠️ **Partner Path 不得以"自身产生多少废水"为主要判断依据。**

**分流规则详见 `customer-type-playbook.md`。**

---

## 五、BDD Relevance 判定（按 Path 分支）

**必须综合 8 类输入，并按 Path 使用不同内部逻辑。**

| # | 输入 | End-user | Partner |
|---|---|---|---|
| 1 | Industry 行业 | 必须 | 必须 |
| 2 | Company Business 公司业务 | 必须 | 必须 |
| 3 | Products / Services 产品服务 | 必须 | 必须 |
| 4 | Activity Confirmation 活动 / 能力确认 | **关键项** | **关键项** |
| 5 | Process / Technology 工艺或技术组合 | 可选 | 建议 |
| 6 | **PWE 或 CSD** 废水证据 | **必须之一** | **必须之一** |
| 7 | Environmental Evidence 环境证据 | 强烈建议 | 建议 |
| 8 | Project / EIA / Permit / Tender / ESG / Job signals | 强烈建议 | 强烈建议 |

### 取值定义（摘要，完整见 `bdd-relevance-rules.md`）

| 取值 | End-user Path | Partner Path |
|---|---|---|
| `High` | **A** Industry Fit = Target **+ B** 制造业确认 **+ C** PWE/CSD 之一成立 **+ D** ≥ 2 项主体级证据 **+ E** **`BDD-Specific Relevance Gate = Strong`（新增硬门槛）** | **A** 行业对口 **+ B** 能力确认 **+ C** 技术组合重叠 **+ D** ≥ 2 项渠道 / 项目证据 **+ E** **`Partner Cooperation Evidence ∈ {Confirmed, Supported}`（新增硬门槛）** **+ F** **Conflict 控制通过** |
| `Medium` | 行业对口 + 制造业确认，但主体级证据仅 1 项或 PWE/CSD 均缺；**或 A+B+C+D 已满足但 Gate ∈ {`Moderate`, `Weak`}** | ① 行业对口 **且** ② 能力已确认 **且**（③ 重叠度或渠道证据仅 1 项 **或** ④ **A+B+C+D 已满足但 Partner Gate 未过**） |
| `Low` | 确证全厂区闭环 + 无扩产/加严/处罚 + 无遗留难降解段；**或**确证非制造业 | 确证技术线与 BDD 场景无重叠且工艺封闭 |
| `Unknown` | 关键输入不足；**或 `Industry Fit = Unknown`；或 Gate = `Unknown`** | 能力或技术组合无法确认；**或 Partner Gate = `Unverified` / `Conflict` 且无开放证据、以致机会强度无法判定** |

> ⚠️ **Patch 2026-09-27 起，End-user `High` 多一道硬门槛（条件 E）**：
> 「行业对口 + 有制造 + 有废水证据 + 证据够多」**仍不足以判 `High`** ——
> 必须另证该主体的废水与 BDD 场景存在**明确关系**（Gate = `Strong`）。详见 `bdd-relevance-rules.md` 第四节。
> **本 Gate 只作用于 End-user；Partner Path 规则完全不变。** 不新增 Internal Key、不新增 PDF 字段、不新增评分；
> Gate 结果记录在 **Markdown 附录 B（审计信息）**。

### 强制附注（缺任一 → 判定无效）

```
Reason            判定理由（已确认什么 / 缺什么）
Evidence          支撑证据编号（E# …）；给 High 时必须列 ≥ 2 项主体级证据
Confidence        High / Medium / Low
Opportunity Type  五值之一（复合时用 " +| " 连接）
```

### 硬规则

- 不得因 Industry Fit 高直接给 BDD Relevance 高。
- **V1.1 起不存在"无询盘 → 最高 Medium"这条封顶。** `PWE` 单独成立即可支撑 `High`（但仍须过条件 E）。
- **Patch 2026-09-27 新增**：**「有废水」不等于「有 BDD 相关性」。** 有制造、有废水、有处理设施、有排污许可、有水量数据，**均不构成 Gate 证据**；非 `Strong` 不得判 `High`。
- **Patch 2026-09-27 新增**：`Industry Fit = Unknown` 时，BDD Relevance **不得高于 `Unknown`**（无目标市场归属即无机会判定依据）。
- **Partner Gate Patch 2026-09-27 新增**：**Partner Path 判 `High` 必须先过 `Partner Cooperation Evidence Gate`（条件 E）并满足 Conflict 控制（条件 F）。** 能力 / 场景 / 项目数量**均不构成 E 或 F 的证据**。
- **Partner Gate Patch 2026-09-27 新增**：`Partner Cooperation Evidence = Unverified` 或 `Conflict`（无开放证据）→ **一律不得 `High`**；**不得用"大公司通常开放"等行业经验补全机制证据。**
- **Partner Gate Patch 2026-09-27 新增**：**Gate 只影响机会强度，不改机会类型**；且 **`Demand Status` 与之双向独立**（不得互相迁移档位）。
- 判定依据不足时输出 `Unknown`，**不得用"该行业通常有废水"升格**。
- `Process / Technology` 只能在**公开可验证**时使用。不得靠行业常识推断。
- BDD Relevance 高**不代表**技术可行——本 Skill 不做技术判断。

---

## 六、废水证据两类（V1.1 新增）

| 证据类 | 来源 | 记录位置 |
|---|---|---|
| **Public Wastewater Evidence（PWE）** | 官网 · 年报 / ESG / BRSR · 政府许可 / 环评 · 合规报告 · 公开案例 · 招聘 | `Demand Status` 第一行 · `BDD Relevance` 输入 6 · `Current Treatment` |
| **Customer-stated Demand（CSD）** | **询盘文字** · 客户自述 | `Demand Status` 第二行 · `BDD Relevance` 输入 6 |

- **两者分别记录、分别标注来源，不得合并。**
- 主卡 `Demand Status` 取**较低者之外**的规则：取较高者（详见 `evidence-policy.md` 4.3）。
- 检索路径见 `lead-signals.md` 第一节·补；识别规则见 `wastewater-signal-map.md`。

---

## 七、Evidence Policy（证据政策）

**适用范围：所有关键结论。**

| 类型 | 定义 | 强制字段 |
|---|---|---|
| **FACT** | 可追溯到公开来源，或客户明确陈述 | **必须**有 `Source` |
| **INFERENCE** | 基于 FACT 的合理推断 | **必须**有 `Reason` + `Confidence` |
| **UNKNOWN** | 未查到 / 无法判断 | **不得自行补全**，且**必须带三态后缀** |

### UNKNOWN 三态（V1.1 新增，不可省略）

| 写法 | 含义 |
|---|---|
| `UNKNOWN · searched` | 已按允许渠道检索，未查到 |
| `UNKNOWN · no source` | 该地区 / 场景**不存在**公开检索渠道 |
| `UNKNOWN · not searched` | 本次未检索 |

> **为什么要三态**：「我查了 5 个渠道都没有」与「这个国家根本没有公开渠道」**含义完全不同**。
> 后者被误读为"这家很干净"，会产生**错误安全感**。

### Decision Impact（V1.1 新增）

每条 Evidence 增加 `Decision Impact = High / Medium / Low`。
**只影响展示优先级，不影响真实性判断。** 与类型、Confidence 完全正交。

### 三条铁律

1. **FACT 无 Source = 不得标为 FACT**，降级为 INFERENCE 或 UNKNOWN。
2. **INFERENCE 无 Reason 或无 Confidence = 不得输出**。
3. **UNKNOWN 保持空白 + 三态后缀。** 不允许用行业经验值、同类客户类比、"通常来说"填充。

详细分级见 `references/evidence-policy.md`。

---

## 八、工作流（14 步，严格按决策链顺序）

### 第 1 步 · Input 输入

接收：询盘原文 / 公司名 / 联系人 / 名片 / 邮件 / 聊天记录 / 展会信息。

**完整保留原文**，不做改写、不做摘要、不做判断。**无询盘原文时须显式记录"本次无询盘文字"。**

### 第 2 步 · Company Verification 公司核实

**确认"这家公司真实存在、主体唯一、名称准确"。**

| 核实项 | 来源 |
|---|---|
| 登记全称（与客户自述比对） | 企业信用公示 / 商业登记 / 官方注册信息 |
| 注册号 / 税号 / CIN | 同上 |
| 存续状态 | 同上 |
| 成立时间 | 同上 |
| 注册地址 | 同上 |
| 名称歧义 / 重名排查 | 多源交叉 |
| **同集团同名近似主体排查** | 多源交叉（**误关联会翻转结论**） |

**核实结果三态**：`Verified` / `Partially Verified` / `Unverified`

**硬规则**：名称有歧义时**不得选择最像的一家**。输出 `Unverified`，并在 `What Is Missing`（Business 级）列出"需客户提供登记全称"。

### 第 3 步 · Evidence Collection 证据收集

用 WebSearch / WebFetch 检索。**每条产出必须标注 FACT / INFERENCE / UNKNOWN + Decision Impact。**

**缺席证据检查（出卡前人工复核）**：官网菜单、产品目录或项目展示中「未见某技术」只能写成 `UNKNOWN · searched`，并列明检索范围；不得改写成「该主体没有该技术 / 不存在竞争 / 必然互补」。只有来源明确否认且指向目标主体时，才可把否定事实写为 FACT。此检查不改变任何评级、合作闸门或发送条件。

检索优先级（详见 `references/lead-signals.md`）：

| 优先级 | 查什么 |
|---|---|
| ★★★ | 环保处罚记录 |
| ★★★ | 环评公示 / 排污许可 / 合规报告 |
| ★★★ | **PWE：官网环境栏 / 年报 ESG / 公开项目案例** |
| ★★☆ | 招投标信息 |
| ★★☆ | 主体信息（成立时间、员工数、是否实体工厂、登记业务） |
| ★★☆ | 行业与产污类型 |
| ★★☆ | **厂区级信息（服务 Priority Site）** |
| ★☆☆ | 集团 / 子公司关系、新闻、招聘 |

**注意**：本步只产出证据，**不产出任何等级判定**。

### 第 4 步 · Company Profile 公司概况

**回答"这家公司是什么"。**

| 字段 | 查不到时 |
|---|---|
| 登记全称 · 成立时间 · 注册资本 | `Unknown` |
| 员工数（**须注明口径与来源**） | `Unknown` |
| 所在地 · 主营范围 · 主营产品 | `Unknown` |
| 是否实体工厂 | `Unknown` |
| 企业性质 · 集团 / 子公司关系 | `Unknown` |
| **厂区清单（≥ 3 个时逐列）** | 标注 `Group-level only` |

**硬规则**：
- 查不到的字段**直接写 `Unknown`**，不得用"估计""约""大概"填充。
- **集团级数据不得直接写成目标子公司或某厂区数据。**

### 第 5 步 · Customer Type + Path 客户类型与路径

按 `references/customer-type-playbook.md` 判定类型，**并输出 Path**：

```
End-user  /  Partner·EPC  /  Partner·Integrator  /  Partner·Distributor  /  Partner·Technology Partner  /  Undetermined
```

判据必须来自第 3 步的证据。**Path 未定 → 下游三个字段直接 `Unknown`。**

### 第 6 步 · Industry Fit 行业匹配

对照 `references/bdd-fit-rules.md` 的**最小目标市场地图**（T1~T4 / A1~A3）。

| 取值 | 含义 |
|---|---|
| `Target` | T1 锂电池 / T2 制药·原料药 / **T3 高 COD·难降解·难处理（**须过证据门槛**）** / T4 精细化工·农药·染料 |
| `Adjacent` | A1 工业废水 EPC·AOP·集成 / A2 工业化学品·水处理药剂分销 / A3 设计院·院所 |
| `Outside` | 已**正面确证**不属上述（市政污水、纯消费品、非涉水行业等） |
| `Unknown` | 行业 / 业务属性无法确认，或落在定义边界外 |

**硬规则**：

1. **不得因"清单没写"就判 `Outside`**。
2. **T3 必须过「T3 证据门槛」**（`bdd-fit-rules.md` 第二节）：至少命中 1 项**废水性质**证据（高 COD / 难降解 / 难处理 / 深度处理 / AOP 需求 / 明确复杂污染物）。**焦化、印染、电镀、半导体、危废、渗滤液、造纸、冷轧等仅为性质举例，行业标签本身不构成证据。**
3. **只存在工业废水 / 生产废水 / 阳极氧化废水 / 机加工废水 / 压铸废水 / 普通表面处理废水 / 一般排污许可 / 废水处理设施 / 废水量数据时，一律不得判 T3 `Target`** —— 按流程落 `Adjacent` / `Outside` / `Unknown`。

### 第 7 步 · BDD Relevance + Opportunity Type

**按第五节规则 + `bdd-relevance-rules.md`，分 Path 判定。** 同时按 `opportunity-type-rules.md` 判定 `Opportunity Type`。

**End-user 专用顺序（Patch 2026-09-27 起）**：条件 A（Industry Fit = Target）→ B（制造业确认）→ C（PWE/CSD）→ D（≥ 2 项主体级证据）→ **E（`BDD-Specific Relevance Gate = Strong`）**；**A~E 全满足才可判 `High`**。Gate ∈ {`Moderate`, `Weak`} → 上限 `Medium`；Gate = `Unknown` → `Unknown`。

- 必须附 `Reason` + `Evidence` + `Confidence` + `Opportunity Type`
- **给 `High` 时必须列出 ≥ 2 项主体级证据编号**，且 Gate 必须为 `Strong`（`Reason` 中写明命中的 BDD-specific 信号）
- **Gate 结果记入 Markdown 附录 B（审计信息）**，不进业务 PDF、不新增字段
- **禁止输出任何技术参数与数值区间**
- 若伙伴方自有工艺与 BDD 场景重叠 → **记录 Application overlap；直接替代证据不足时 Conflict = Unknown；有可核互补/集成切面时 Partial / Use-case dependent**
- **Partner 专用顺序（Partner Gate Patch 2026-09-27 起）**：条件 A（Industry Fit ∈ {Target, Adjacent}）→ B（能力确认）→ C（技术组合重叠）→ D（≥ 2 项渠道 / 项目证据）→ **E（`Partner Cooperation Evidence ∈ {Confirmed, Supported}`）** → **F（Conflict 控制）**；**A~F 全满足才可判 `High`**。
- **`Partner Cooperation Evidence` = `Unverified` / `Conflict`（无开放证据）→ 不得 `High`**（通常 `Medium`）；`Supported` + `Conflict = Yes` → **通常最高 `Medium`**；`Confirmed` + `Conflict = Yes` → 按「BDD 域相关性 / 机制外部性」两维度重算 `High` 或 `Medium`
- **V1.2.0 主体归属门槛**：A～F 分别记录证据所指的法律主体；母公司技术许可/订单不得直接计为子公司 `Confirmed` 或 `High`。化学品分销/代工不能单独证明外部 BDD 设备代理机制。
- `Conflict` 在附录 B 分 `Direct competitor` / `Integration overlap` / `Component procurement`；同一主体可同时竞争和采购部件。直接竞争但未检索部件切面 → 先验证；已定向检索仍无正面切面 → 按销售结论第 1b 步暂不优先。
- **Partner Path 不走 End-user 的 `BDD-Specific Relevance Gate`**（两者不得混用）
- **`Conflict` 出现时判 `High` 前必须检查 5 项**：技术路线重叠层级 / 是否自研 proprietary / **是否有第三方集成机制** / **是否有外部核心组件采购证据** / Boromond 属 supplier·partner·competitor 哪一类 —— **第 3、4 项均为 `Unknown` 时不得判 `High`**
- Gate 结果记入 **Markdown 附录 B（审计层）**，**不进业务 PDF、不新增字段**

### 第 8 步 · Current Wastewater Treatment / Technology

按 `references/current-treatment-rules.md` 提取：

- **End-user**：企业公开披露的**现有废水处理方案**（按工艺单元归类）
- **Partner**：其**当前可提供的水处理技术组合**（含自有 / 集成 / 代理，及工艺开放度）
- **只能使用公开证据**；查不到 → `Unknown`
- **只写单元名，禁止数值区间**
- **不得因"已有 ETP / ZLD"判 `Low`**——须同时核对窗口信号与降级三条件

### 第 9 步 · Demand Status 需求状态

按 `references/evidence-policy.md` 第四节：

- **`PWE` 与 `CSD` 分别定级**，主卡只输出较高者
- **先过主体与需求对象门槛**：Partner 的通用订单、营业规模、目录与已交付项目只证明业务活动；没有相关外部技术需求或未覆盖的工艺位时 `Demand Status = Unknown`。母公司证据未覆盖目标子公司时只作 `Group-level context`。
- **只能依据第 3 步的证据**——不依据行业好坏，不依据 BDD Relevance 高低，**也不依据最终是否成交**
- 无询盘文字时，`CSD = UNKNOWN · not searched`（**这不影响 `PWE` 独立定级**）

### 第 10 步 · Commercial Risk + Financial Warning + Business Change Signal（**含 FW Rule Patch**）

**Commercial Risk**（`Low / Medium / High / Unknown`）按 `evidence-policy.md` 第五节，**只用询盘当时可观察的事实**。

> **`Unknown` ≠ `High`。** 「没观察到风险信号」与「观察到高风险信号」是两件事。
> 类型级先验（如"工程公司通常风险高"）**不参与定级**，只能作为 `Risk Note` 附注。

**Financial Warning**（`Yes / No / Unknown`）按 `evidence-policy.md` 第六节：**只有财务困境证据**（资不抵债 / 破产 / 流动性危机 / 债务违约 / 持续经营重大疑虑 / 法院或债务层面财务重组 / 集团层面重大亏损且有明确财务压力 / 官方披露重大财务困难）才可判 `Yes`，必须附可靠公开 Source。
`No` 只表示近期可靠的**目标主体级**检索覆盖下未见白名单警示；无财报/登记渠道、只查普通网页或只有集团资料时为 `Unknown`。两者都不构成财务健康评级。
**裁员 / 重组 / 高管变化 / 厂区亏损 / 降本计划 → 一律不得触发 `Yes`。**
**不得扩展为完整财务评级。** `FW = Yes` 也不得机械降档（见第 13 步）。

**Business Change Signal**（`Yes / No / Unknown`）按 `evidence-policy.md` 第七节：记录**企业经营层面正在发生的变化**，判 `Yes` 时必须输出 `Reason` + `Source`。
> **它只是 Context / Watch Item：** 不得单独触发 `FW = Yes`、`Commercial Risk = High`，也不得导致 `Sales Conclusion` / `BDD Opportunity` / `Demand Status` 降档。

### 第 11 步 · Missing Critical Information 缺失关键信息

按 `references/must-ask-params.md`，**排列顺序固定为 Business → Project → Technical**，最多 5 项。

```
[Business]  ① … ② …
[Project]   ③ …
[Technical] ④ ⑤ …
```

**硬规则**：**不得跳过 Business 级直接列 Technical 级**——"这家到底是不是真实需求方"比"COD 是多少"重要得多。

### 第 12 步 · Contact Strategy 联系策略

按 `references/contact-role-map.md`：

- 按 **Path / 客户类型**推荐**岗位角色**；集团型优先接触 `Priority Site` 对应厂区
- 公开来源确实查到真人时可展示 `Name + Position + Source`
- 个人联系人未找到时写 `No verified named contact found`；公司邮箱/电话/合作表单独立列出，岗位角色仍输出；区分未检索、已检索未发现与无法访问
- **禁止生成人名 / 电话 / 邮箱 / 微信**
- 按 `Demand Status` + `Commercial Risk` 组合选择接触策略（矩阵已补齐全部单元格，`Risk = Unknown` **按中等处理**）

### 第 13 步 · Next Action + Sales Conclusion

**Next Action**：一句话，与决策链末端一致。**不得写"邀请寄样小试"。** 已确认存在具体项目时，**只写"转交技术评估流程"**。

**Sales Conclusion**：按 `references/sales-conclusion-rules.md` 判定五值之一 + 1~2 句原因。
**一票否决优先**（`Risk = High` / `BDD Relevance = Low` → `暂不优先`）。
**`FW = Yes` 不是一票否决，也不机械降档** —— 必须先过第 4b 步四问（严重程度 / 主体层级 / 采购与付款能力 / 项目执行能力），并在原因中解释。
**`Business Change Signal` 不参与档位判定。**

### 第 14 步 · Evidence Appendix + 输出 + 归档

按 `assets/output-card-template.md` 输出两层结构，并按 `references/output-visual-rules.md`：

1. 生成 `{Company}_BDD_Intelligence_{YYYY-MM-DD}.md`（落在工作区根，`render_pdf.py` 默认行为不变）
2. 调用 `scripts/render_pdf.py` 生成同名 `.pdf`
3. 确认 `CHECK_evidence`、`CHECK_pdf_content` 和 `CHECK_page_flow` 均为 `PASS`；任一 `FAIL` 时先修报告或版式，不归档该次 PDF。
4. **调用 `scripts/archive_report.py` 归档到客户档案库（V1.1.4 → V1.1.5：归档成功后清理工作区根的那一份）** —— 见下

**PDF 为业务员版；前两页固定，第三页起为关键依据与完整证据表，可自然续页。仅做格式转换，不得反向影响任何判断。**

| PDF 页 | 内容（V1.1.3） |
|---|---|
| Page 1 | `Customer Snapshot ｜客户快照` —— 主卡四组 + 结论卡（**自 V1.1.2 起完全不变**） |
| Page 2 | `SALES INTELLIGENCE ｜开发情报` —— 5 张销售信息卡（Why BDD / Current Treatment / Priority Site / Who to Contact / What to Verify） |
| Page 3 起 | `KEY EVIDENCE ｜关键依据` —— 6~8 条摘要卡，随后为完整证据表；续页须有实际内容 |

> 审计与边界信息（可溯源率 / 类型定义 / 实体排除 / 来源冲突 / 边界声明）**不进业务 PDF**，只保留在 Markdown 附录 B。

#### 第 14 步之三 · 客户档案归档（V1.1.5 · 档案库为唯一存放地）

**背调收尾的固定动作：把这两个文件归入本机客户档案库，并清理工作区根的那一份。**

```bash
python scripts/archive_report.py "{Company}_BDD_Intelligence_{YYYY-MM-DD}.md"
```

| 项 | 规则 |
|---|---|
| 归档根 | 解析顺序**固定**：① `--archive-root` → ② **环境变量 `BDD_ARCHIVE_ROOT`**（推荐，一次设定永久生效）→ ③ **当前工作区根**下的 `customer-archive/`（工作区根 = 从 cwd / 报告目录向上找到的第一个含 `.workbuddy/` 或 `.git/` 的目录；跳过用户主目录） |
| 归档根禁区 | **绝不允许落在 Skill 源码目录内** —— 命中即拒绝并退出（exit 6），防止客户档案被误随 Skill 源码提交 / 推送 |
| 客户目录 | `customer-archive/<规范化公司名称>/` —— 只做非法字符清洗、空白折叠与 Windows 保留字规避，**不改词、不删词**；目录名已被占用时自动唯一化（` (2)`），**绝不写进既有客户目录** |
| 客户识别 | ① **官网域名**（最强）→ ② 公司名核心词全等 → ③ 登记别名 → ④ 名称核心词**前缀**（解决缩写重复建档；仅共享首词不合并，只出 HINT） |
| 域名来源 | 优先 `--domain` 显式指定；否则从报告内引用 URL 自动推断（剔除社交 / 媒体 / 工商查询 / 监管站 / **展会名录站**）并标注 `auto` |
| 同名冲突 | `_HHMM` → `_HHMM_v2` / `_v3` 递增，**永不覆盖** |
| 同内容 | sha256 去重，重复归档不产生冗余文件（幂等）；**同内容分支同样清理源文件** |
| 客户标识 | 目录内 `_customer.json`（客户名 / 别名 / 域名 / 报告清单）—— 丢失可自动重建 |
| **源文件清理（V1.1.5）** | 归档成功 → 清理工作区根的那一份 → **档案库即唯一存放地**；`--keep-source` 可退回保留 |
| **输出要求** | **必须向用户报出「交付位置 / 档案保存位置」**（完整路径）+ 本次是新建还是复用既有档案 |

**硬规则**

1. **归档即归宿（V1.1.5 起）。** 归档成功**且逐字节 sha256 校验通过**之后，清理工作区根的那一份；工作区根**不留副本**。
2. **绝不丢件（V1.1.5 四条护栏）。** 归档失败 / 目标已存在 / 校验不一致 / 归档根被拒 / `--dry-run` / `--keep-source` → **一个源文件都不删**；**源文件本身位于档案库内也绝不删**。
3. **永不覆盖。** 目标同名一律改期后缀，历史报告一份不许丢。
4. **归档不参与判断。** 归档失败**不影响**报告交付；失败时报错并继续，不得因此重判任何字段。
   > **副作用（有益）**：V1.1.5 起，若归档未成功，源文件会**留在工作区根** → 归档失败变成**肉眼可见**的信号（工作区根本不该残留 `*_BDD_Intelligence_*` 文件）。
5. **客户识别不确定时不猜。** 脚本输出 `[HINT]` / `[WARN]`（共享首词但非前缀、目录名被占用、多档案前缀相近）时，**必须在回复里提示用户确认**；必要时用 `--force-new` 或人工改名。**不得**用别名强行合并两个不同主体。
6. **报出位置。** 归档完成后必须告知「交付位置 / 档案保存位置」与历史报告份数。
7. **交付物在档案库内。** 交付仍只有 `.md` + `.pdf` 两个文件，但**位置是档案库客户目录**；`customer-archive/` 整体**不上传、不提交 Git**。
8. **单客户多厂区 / 多主体**（如集团与子公司分属不同主体）按**独立客户目录**处理，**不得**用别名强行合并。


---

## 九、硬性约束（违反即视为分析无效）

| # | 约束 | 原因 |
|---|---|---|
| 1 | 决策链严格单向，不跳步、不回推 | 防止各模块独立判断互相冲突 |
| 2 | **Path 未定 → 下游三个字段必须 `Unknown`** | 口径错则全错 |
| 3 | **Industry Fit 高 → 不得推导 BDD Relevance 高** | 行业对口 ≠ 这家公司有场景 |
| 4 | **行业属锂电池 / 电池材料 → 不得自动给 `High`** | 必须由主体级证据支撑 |
| 5 | **BDD Relevance 高 → 不得推导 Demand Status 高** | 有场景 ≠ 有采购需求 |
| 6 | **Partner Path 不得以"自身废水"为主要判断依据** | 口径错 |
| 7 | **不得因"已建 ETP / ZLD"判 `Low`** | 已有设施 ≠ 无机会 |
| 8 | BDD Relevance 必须附 `Reason` + `Evidence` + `Confidence` + `Opportunity Type` | 判定可追溯 |
| 9 | **给 `High` 时 `Reason` 必须列 ≥ 2 项主体级证据编号** | 防行业经验值升格 |
| 10 | **`Commercial Risk = Unknown` 不得写成 `High`** | 无事实 ≠ 有风险 |
| 11 | FACT 必须有 Source；INFERENCE 必须有 Reason + Confidence；UNKNOWN 必须带三态后缀且不得补全 | 幻觉防线 |
| 12 | **集团级数据不得写成目标子公司或厂区级数据** | 主体 / 层级错位 |
| 13 | 同名近似主体未排除前，不得计入 Demand Status 与 Commercial Risk | 误关联会翻转结论 |
| 14 | Company Verification 名称有歧义时输出 `Unverified`，不得选最像的一家 | 主体错 = 全盘错 |
| 15 | Company Profile 查不到字段**留 `Unknown`**，不得填"估计值" | 制造虚假完整度 |
| 16 | 主卡不承载 Evidence 明细；主卡不出现内部术语 | 1 页 + 30 秒可读 |
| 17 | **不输出工艺参数、设备选型、达标承诺、技术方案、金额、报价状态** | 安全边界 |
| 18 | **不输出 Technical Fit / Quotation Readiness** | 已移出职责范围 |
| 19 | **不得输出"建议小试"、不得固定"寄 5~10 L 水样"、不得自动进入小试流程** | V1.1 删除的越界规则 |
| 20 | 只推荐 Contact Role；无公开来源证据不得生成具体人名 / 电话 / 邮箱 | 合规风险点 |
| 21 | Commercial Risk 判据不得使用"是否成交" | 结果论会污染规则且无法验证 |
| 22 | **不得引入数值评分 / 100 分制 / 加权总分** | Sales Conclusion 为逐级规则匹配 |
| 23 | 颜色由字段取值机械映射，不得人工调整，不得表达程度 | 横向可比 |
| 24 | **PDF 渲染层不得新增、推断、改写任何结论** | 渲染与判断隔离 |
| 25 | `What Is Missing` 必须按 Business → Project → Technical 排列 | 决策优先级 |
| 26 | **`Business Change Signal = Yes` 不得单独触发 `FW = Yes` / `Commercial Risk = High`，不得单独导致任何字段降档** | 业务变化 ≠ 财务困境 |
| 27 | **`FW = Yes` 不得机械降档** —— 必须经四问判定并解释理由；不得用单条负面新闻覆盖更完整的集团财务事实 | 防误报与机械降档 |
| 28 | **`T3` 判 `Target` 必须附至少 1 项废水性质证据（高 COD / 难降解 / 难处理 / 深度处理 / AOP 需求 / 明确复杂污染物）；"有工业废水"一律不构成 T3 证据** | 废水相关性 ≠ T3 Target |
| 29 | **End-user 判 `High` 必须 `BDD-Specific Relevance Gate = Strong`；Gate ∈ {Moderate, Weak} 上限 `Medium`，Gate = Unknown 则为 `Unknown`；`Industry Fit = Unknown` 时 BDD Relevance 不得高于 `Unknown`** | 废水相关性 ≠ BDD 相关性 |
| 30 | **最终交付只有 `.md` + `.pdf` 两个文件**；HTML、Page PNG、截图、comparison 目录、debug 输出、临时提取文件**仅作内部渲染与回归测试的中间产物**，不得作为交付展示、不得列入用户产物 —— **仅当用户明确要求视觉检查 / PDF 回归 / Before-After 对比时**才输出图片类产物 | 交付纪律（不改内容与判断） |
| 31 | **Partner 判 `High` 必须 `Partner Cooperation Evidence ∈ {Confirmed, Supported}`；`Unverified` / `Conflict`（无开放证据）一律不得 `High`；`Supported` + Conflict 通常最高 `Medium`** | 能力 / 场景 ≠ 合作机会 |
| 32 | **`Conflict` 出现时，若「第三方集成机制」与「外部核心组件采购证据」均为 `Unknown`，不得因技术重叠或项目能力强而判 Partner `High`** | Conflict 不是装饰性标签 |
| 33 | **归档即归宿（V1.1.5）** —— 归档成功**且逐字节 sha256 校验通过**后才清理源文件；归档失败 / 目标已存在 / 校验不一致 / 归档根被拒 / `--dry-run` / `--keep-source` → **一个源文件都不删**；**源文件本身位于档案库内也绝不删**；目标同名一律加 `_HHMM` / `_v2` 后缀，历史报告一份不许丢 | 消除重复副本造成的静默漂移，同时绝不丢件 |
| 34 | **归档不参与判断** —— 归档失败不得影响报告交付，不得因此重判任何字段；交付物只有 `.md` + `.pdf` 两个文件（**位于档案库客户目录内**），且必须向用户报出**交付位置** | 归档层与判断层隔离 |
| 35 | Partner 仅有通用订单/目录/对外销售时 `Demand Status = Unknown`；须先证明目标主体的相关外部技术或项目需求再升档 | 业务活动 ≠ BDD 需求 |
| 36 | 母公司交易/许可不得代替子公司 A～F、`Demand Status` 或 `Financial Warning` 的主体级证据；同一交易只计一次 | 防集团证据重复升档 |
| 37 | `Conflict` 须区分直接竞争、工程重叠和部件采购；竞争者有部件采购事实时不得自动否决 | 防误杀可供货切面 |
| 38 | `FW = No` 须记近期可靠的目标主体级检索来源、时段；覆盖不足取 `Unknown` | 防「没查到」写成「无财务问题」 |

---

## 十、输出结构（两层）

### 第一层 · 主判断卡（**1 页，固定 13 字段 · 四组呈现**）

**V1.1.1 起按四组排列**（顺序固定，不得调换）：

```
WHO · 客户是谁
  公司 Company                                 登记全称（国家）· 核实三态
  国家 Country                                 国家 · 主要运营地区
  主营业务 Business                            一句话（业务员能转述）
  客户类型 Customer Type                       类型 · Path

WHY · 为什么值得看
  行业匹配 Industry Match                      Target / Adjacent / Outside / Unknown（带颜色）
  BDD机会 BDD Opportunity                      High / Medium / Low / Unknown · Opportunity Type
  需求状态 Demand Status                       五值（较高者）

WHERE / WHO · 从哪里切入
  现有废水处理 Current Treatment               状态徽标（Confirmed / Partial / Planned / Unknown）· 技术组合（只写单元名）
  优先厂区 Priority Site                       厂区（国家）· 理由 / N/A
  关键联系人 Contact                           岗位角色（+ 具名 / No verified contact found）

ACTION · 现在怎么办
  待确认信息 Missing Info                      [Business] … [Project] … [Technical] …
  下一步 Next Action                           一句话

  ┌ 开发建议 Sales Conclusion（结论卡 · 第一页最醒目）────────┐
  │  五值之一 + 1~2 句原因                                    │
  └──────────────────────────────────────────────────────┘
```

> **Display Label 仅用于显示**；脚本校验与规则引用一律使用 **Internal Key**（对照表见 `assets/output-card-template.md` 与 `references/output-visual-rules.md` 第二部分）。

主卡下方附三个固定小块（不计入 13 字段，但必填）：

```
BDD Opportunity 判定依据    Reason / Evidence / Confidence / Opportunity Type
Demand Status 明细          Public Wastewater Evidence: … / Customer-stated Demand: … / → 取较高者
风险                        Commercial Risk / Risk Note（可选）/ Financial Warning（财务困境口径）
业务变化                    Business Change Signal（Yes / No / Unknown + Reason + Source，Context / Watch Item）
```

**主卡不写内部术语，不放 Evidence 明细。** `Unknown` 的字段**直接留 `Unknown`**。

**`Current Treatment` 状态硬规则（V1.1.1）**

| # | 规则 |
|---|---|
| 1 | 状态必须有 E# 支撑；无 E# → `Unknown` |
| 2 | 证据为规划 / 拟建 / 在建 → **只能** `Planned` |
| 3 | 覆盖不完整 → `Partial`，不得升为 `Confirmed` |
| 4 | **状态不参与任何判断字段**，不与 `BDD Opportunity` 联动 |

### 第二层 · 附录（折叠区）

**附录 A · Evidence 明细**（**完整证据层，一字不删**）

```
| # | 主题 | 类型 | 结论 | Source | Reason | Confidence | Decision Impact |
```

- `主题`：该条证据的**展示短标题**（V1.1.3 新增的展示标签，**非判断字段**），供业务 PDF 的 Key Evidence 卡片使用。
- `类型` / `Confidence` / `Decision Impact` / `Reason` 等**审计字段只在 Markdown 保留**，不进入业务 PDF。

**附录 B · 审计信息（仅 Markdown，不进入业务 PDF）**

固定附：可溯源率 · 类型定义 · Decision Impact 说明 · 集团级 vs 目标主体/厂区级说明 · 同名主体排除 · 来源冲突项 · UNKNOWN 三态汇总。Partner 另记 A～F 证据的主体层级、需求证据与一般业务活动的界线；有 `Conflict` 时记子类及部件采购切面。

**边界声明**（仅 Markdown）：不输出技术方案 / 设备选型 / 工艺参数 / 达标承诺 / 金额 / 报价状态；Technical Fit 与 Quotation Readiness 按范围冻结不输出；未输出"建议小试"、未固定"寄 5~10 L 水样"。

> 渲染层以 `## 附录 B` / `## 边界声明` 为切分点：**其后的内容不进入 PDF**（内容仍完整保留在 Markdown）。

详见 `assets/output-card-template.md` 与 `references/output-visual-rules.md`。

### 交付展示与汇报（2026-10-13 **展示层精简** · 只改"展示什么 / 报什么"，不改任何交付物与判断）

**默认可视交付只有 2 项**；其余一律**后台留存、不主动展示、不列入附件**：

| 默认展示 | 条件 |
|---|---|
| ① **客户背调资料卡 PDF**（业务员版 3 页） | 始终 |
| ② **英文开发信 MD**（`drafts/<公司>/<公司>_开发信_<日期>.md`） | **仅当符合 §十六 生成条件**（已归档 PASS 且结论 ∈ {`建议重点开发`, `建议开发`, `建议先验证`} 且 G1–G5 放行） |

> **不符合邮件生成条件时**：**只展示 ①**，并**说明阻断原因**（结论为 `暂不优先` / `信息不足，暂缓判断` / `CONTACT_NONE` / 台账 `SENT` 或 `UNKNOWN_NEEDS_REVIEW` / 归档未 PASS）。

**按需展示（仅当用户明确提出「要富通天下排版 / 复制 HTML / 准备发件」时）**：邮件 **HTML 排版版** 与 **纯文本版**。
> ⚠️ **两者必须继续生成与保存，不得延迟** —— `bdd-sales-outreach/scripts/quality_check.py` 的**入口校验**（缺 `.html` 或 `.txt` 即 `[ERR]` 退出）与**第 7 项**（HTML / 纯文本词元一致性）**强依赖**它们。归档、台账、去重**不依赖**它们，但质检依赖 ⇒ **只隐藏展示**。

**后台保留（正常保存，不作为交付附件展示）**：客户背调 **MD**（权威版，含附录 A 证据来源 / 附录 B 审计）· **Handoff JSON** · 开发信状态与去重**台账** · **质检日志** · **成本遥测记录** · `README` / `tools/telemetry.py` 等程序文件。

**汇报只输出四段**（其余一律不写）：

| 段 | 内容 | 要求 |
|---|---|---|
| ① **客户结论** | `Sales Conclusion` · `BDD Opportunity`（相关性）· 开发建议 | **各 1 句，尽量简短**；需要细节时由用户展开后台资料 |
| ② **联系渠道** | 可验证邮箱 / 官方联系表单 | 只列已核实的官方渠道；无则写明 |
| ③ **交付文件** | PDF ＋（如有）开发信 MD 的**档案库完整路径** | 须注明新建 / 复用既有档案 |
| ④ **异常提示** | **仅在有异常时出现**：证据不足 / 质检 `MANUAL` 项 / 归档异常 / `[HINT]` `[WARN]` / 页数 ≠ 3 / 邮件阻断原因 | 有则逐条列，无则写「无」 |

> **不因精简而省略**：交付位置（必报）· 归档异常（必报）· 机械核对失败项（必报）· 邮件阻断原因（必报）。
> **不再重复**：脚本已输出的 CHECK 逐项、Evidence 明细、13 字段全文（这些都在交付文件里，无需在对话中复述）。

---

## 十一、V1.1 变更对照（相对 V1）

| 项 | V1 | V1.1 |
|---|---|---|
| 客户分流 | 六类客户，统一判据 | **End-user Path / Partner Path（含 4 个 Sub-type）** |
| 行业清单 | 骨架，恒 `Unknown` | **最小目标市场地图已填（T1~T4 / A1~A3）** |
| 废水证据 | 单一"废水信号"（限询盘） | **PWE（公开）+ CSD（客户自述），分别定级** |
| 封顶规则 | 无废水信号 → 最高 `Medium` | **已删除** |
| 现有处理 | 无 | **`Current Wastewater Treatment / Technology`** |
| 机会分类 | 无 | **`Opportunity Type`（五值 + 复合 + 冲突标注）** |
| 厂区优先级 | 无 | **`Priority Site`（≥ 3 厂区集团）** |
| 缺失数据 | `Missing Critical Data` | **`Missing Critical Information`，Business → Project → Technical** |
| 商业风险 | `Unknown` / `High` 易混 | **明确 `Unknown` ≠ `High`；补齐矩阵空格；新增 `Financial Warning`** |
| 结论 | 只有 `Next Action` | **`Sales Conclusion`（五值 + 原因）** |
| 输出 | 1 屏主卡 10 字段，无颜色 | **1 页主卡 13 字段，大白话，五色语义** |
| 交付 | 仅 Markdown | **Markdown + PDF（三页业务员版）** —— **最终交付只有这两个文件**，HTML / PNG / 截图 / 对比 / debug / 临时提取文件仅为内部中间产物 |
| 越界规则 | 含"输出必含建议小试"、固定"寄 5~10 L 水样" | **已删除；改为"转交技术评估流程"** |

> V1 全量快照与已删除规则的完整记录见第十三节归档区。

---

## 十二、文件说明（V1.1.5 + Single-Home Patch）

```
SKILL.md                                   本文件：默认调用协议 + 职责边界 + 决策链 + 概念区分 + 分流
                                           + BDD Relevance 规则 + 证据政策（含 Financial Warning 白名单 + Business Change Signal） + 工作流 14 步（第 14 步含客户档案归档） + 38 条硬性约束
references/
  evidence-policy.md                       证据政策：三类型 + UNKNOWN 三态 + Demand Status（PWE/CSD）
                                           + Commercial Risk（唯一定级来源）
                                           + Financial Warning（**财务困境白名单口径**）+ Business Change Signal（Context / Watch Item）
                                           + Decision Impact
  lead-signals.md                          检索指引：三件套 + PWE 检索 + 集团/厂区区分 + 同名主体排除
  bdd-fit-rules.md                         Industry Fit 判定 + 最小目标市场地图（T1~T4 / A1~A3）
                                           + **T3 证据门槛与 T3 硬规则（Patch A 收紧）**
  bdd-relevance-rules.md                   BDD Relevance 判定：8 项输入 + 分 Path 逻辑 + 强制附注
                                           + **BDD-Specific Relevance Evidence Gate（Patch B · 仅 End-user High）**
                                           + **Partner Cooperation Evidence Gate（2026-09-27 · 仅 Partner High）**
  current-treatment-rules.md               Current Wastewater Treatment / Technology 提取与判读
  opportunity-type-rules.md                Opportunity Type 五值 + 复合情形 + Priority Site
  customer-type-playbook.md                客户类型判定 + 双路径分流 + 路径速查矩阵
  contact-role-map.md                      联系策略：Path/类型 → 岗位 + 接触战略矩阵 + 触发信号
  must-ask-params.md                       Missing Critical Information 三级优先级 + 加问清单 + 参数自检
  wastewater-signal-map.md                 从文字识别 CSD 与特征信号（骨架，待填）
  sales-conclusion-rules.md                Sales Conclusion 五值 + 保守优先规则
  output-visual-rules.md                   颜色语义（唯一来源）+ **展示层（Display Label / 四组导航 / Badge / 四态 / 第一页压缩 / 结论卡）** + 命名规范 + **PDF 三页模板（Page 2 Sales Intelligence ／ Page 3 Key Evidence）** + 渲染隔离
assets/
  output-card-template.md                  两层输出模板（主卡 13 字段 + 附录 A 含主题/Decision Impact + 附录 B 审计信息）
scripts/
  render_pdf.py                            MD → HTML → PDF（纯格式转换，无判断逻辑）
  archive_report.py                        **客户档案归档（V1.1.4 → V1.1.5）**：报告 .md/.pdf → `customer-archive/<公司名>/`
                                           （域名/公司名/别名/核心词四级识别 · 同名永不覆盖 · sha256 幂等
                                            · **归档成功后清理源文件 → 档案库为唯一存放地** · 四条防丢件护栏）
```

**共 16 个文件**（V1 为 10 个，V1.1 新增 5 个，V1.1.4 新增 1 个）。

**本机档案库（不在 Skill 包内、不入库）—— V1.1.5 起即「交付位置」**

```
customer-archive/                          客户档案库根 —— 由 $BDD_ARCHIVE_ROOT 指定；
                                           未设则该环境变量时回退到「当前工作区根」下的 customer-archive/
  <规范化公司名称>/                         一个客户一个目录（**报告的唯一存放地**）
    _customer.json                         客户标识 + 报告清单（保留；可自动重建，非数据库）
    {Company}_BDD_Intelligence_{日期}.md    历史报告，逐份保留 ← 权威版本
    {Company}_BDD_Intelligence_{日期}.pdf                                        ← 业务员版（三页）
```

**交付与自检约定（V1.1.5）**

- **交付物在档案库客户目录内**；工作区根目录**不再保留副本**（归档成功后清理）。
- **可见自检信号**：任务结束时工作区根**不应**残留任何 `*_BDD_Intelligence_*` 文件 ——
  若仍在，说明归档未成功（此时源文件被完整保留，**未丢件**）。

**机械核对单一来源（2026-10-13 成本优化 Patch 2 · 合并重复检查，不删检查项）**

为避免同一次结论被核对两遍，机械性检查一律**以脚本一次输出为准**，调用方**不再另跑命令复核**：

| 检查项 | 单一来源（脚本输出行） | 说明 |
|---|---|---|
| 主卡 13 字段完整性 | `render_pdf.py` → `主卡字段数 : 13 / 13` | **不要**再自己 `grep -c` 数 |
| PDF 页数 = 3 | `render_pdf.py` → `CHECK_pages` | **已合并**原先另跑的 `pymupdf` 页数核对 |
| PDF 生成成功 | `render_pdf.py` → `CHECK_pdf` | — |
| 附录 Decision Impact 列 | `render_pdf.py` → `CHECK_evidence_col` | — |
| 归档位置 / 份数 / sha256 | `archive_report.py` 输出 | 归档结论以它为准 |
| 开发信质检 13 项 | `quality_check.py` 输出 | 归 outreach 侧 |

> **保留原则**：上述**检查项一个都不删**，只把「脚本已算 + 人工再算」合并为「只算一次」。
> 脚本输出为 `MANUAL` / `FAIL` 时，仍须按异常提示处置（不得因自动化而忽略）。

**部署约定**：档案库位置由 **`BDD_ARCHIVE_ROOT` 环境变量**指定（部署方按本机实际目录设定，形如 `<工作区目录>\customer-archive`）。
路径来源**只依赖环境变量与工作区结构判断**，**不写入文档、不依赖任何对话记忆**。

> `customer-archive/` 已写入 `.gitignore`（Skill 仓库 + 工作区），**客户档案只保存在本机，不随 Skill 源码 Push 到 GitHub**；
> 归档脚本另有硬门禁：归档根若落在 Skill 源码目录内直接拒绝执行（exit 6）。

---

## 十三、已归档内容

### V1.0 Freeze 归档

**位置**：内部工作区归档区（不随本分发版发布）

| 归档件 | 内容 | 回收条件 |
|---|---|---|
| `reply-playbook.md` | 8 场景回复话术 + 跟进节奏 Day 0~30 | 需要独立"回复执行" Skill 时 |
| `disclosure-policy.md` | 资料开放三档 + 应对话术 + 可交换原则 | 需对外发布"资料开放 SOP"时 |
| `bdd-fit-rules.technical.md` | Technical Fit 阈值 + 判定流程 + 否决条件 | Boromond 技术确认阈值后 → 平台 L3 |
| `must-ask-params.quotation.md` | Quotation Readiness 四态 + 报价流程归属 | Skill 扩展至商务流程时 |
| `customer-type-playbook.strategy-columns.md` | 决策周期 / 报价路径 / 资料开放 / 价格敏感度 | 平台 L4 推理层需要销售策略输出时 |
| `output-card-template.appendix-B-C.md` | 附录 B 回复草稿 + 附录 C 推进节奏 | 恢复回复草稿与跟进节奏输出时 |
| `*.pre-freeze.md`（6 个） | 冻结前全量快照 | 供 diff 对照 |

### V1.0 Freeze 全量备份（V1.1 升级前）

**位置**：内部工作区归档区（不随本分发版发布）
**内容**：V1 冻结版全部 10 个文件（字节数与源文件一致校验通过），**可完整回退**。

### V1.1 变更归档

**位置**：内部工作区归档区（不随本分发版发布）

| 归档件 | 内容 |
|---|---|
| `V1.1-removed-rules.md` | V1.1 删除的越界规则原文 + 删除原因 + 替代写法 + 回退方式 |
| `V1.1-diff-summary.md` | V1 → V1.1 字段级变更对照 |

> **注意**：归档区在 Skill 目录之外，不会被 Skill 机制加载。

---

## 十四、TBD · 需向 Boromond 技术 / 销售确认

未经确认前 Skill 会输出 `Unknown` / `Unverified` / `N/A`，不会自行推断。

| # | TBD 项 | 归属 | 不填的后果 |
|---|---|---|---|
| 1 | **T3「T3 证据门槛」9 项证据清单是否需增删**；"高 COD"是否需给出浓度口径（当前不设阈值） | 销售 | 边界案例归类偏差 |
| 1b | **是否需新增一类 Target（如 T5「复杂有机合成类制造业」）** 以收纳"有复杂有机工艺但未公开载明难降解"的主体 —— 未定前输出 `Unknown` | 销售 | 召回损失 |
| 2 | **`Outside` 界定是否需补充** | 销售 | 目前需正面确证，偏保守 |
| 3 | A2 分销商是否确认为目标渠道 | 销售 | `Distribution Opportunity` 是否成立 |
| 4 | `Adjacent` 的判定边界 | 销售 | 粒度 |
| 5 | `High` 要求"≥ 2 项主体级证据"是否过严 / 过松 | 销售 | 等级偏差 |
| 6 | `Low` 的"降级三条件"是否符合实际 | 销售 + 技术 | 误判"无机会" |
| 7 | 五类 Opportunity Type 是否覆盖实际业务形态 | 销售 | 分类缺口 |
| 8 | `Priority Site` 触发门槛（≥ 3 厂区）与权重顺序 | 销售 + 技术 | 优先级偏差 |
| 9 | 三级优先级的项是否需增删 | 销售 + 技术 | 缺项排序 |
| 10 | 五档 Sales Conclusion 措辞是否符合销售口径 | 销售 | 结论不可直接引用 |
| 11 | `Financial Warning` 白名单（evidence-policy 6.1）是否覆盖实际遇到的财务困境形态 | 销售 / 财务 |
| 12 | `Business Change Signal` 是否需要更显眼的展示位（当前只在 Markdown + 结论原因中提一句，PDF 无独立卡片） | 销售 |
| 12 | Demand Status 的 `PWE` / `CSD` 分级是否需要分别设口径 | 销售 | 等级偏差 |
| 13 | 环保处罚时效窗口（现设 12 个月） | 销售 | 信号时效误判 |
| 14 | 检测报告时效窗口（现设 6 个月） | 技术 | 同上 |
| 15 | **「转交技术评估流程」的接收方与 SLA** | 技术 + 销售 | 结论无法落地 |
| 16 | 各类客户岗位序列是否符合实际接触经验 | 销售 | 联系角色不准 |
| 17 | 五色语义是否符合内部习惯 | 销售 | 呈现偏差 |
| 18 | 行业 → 废水特征关键词表（`wastewater-signal-map.md` 骨架） | 技术 + 销售 | 特征识别能力受限 |
| 19 | 是否需中文 / 英文双语输出 | 销售 | 对外可用性 |
| 20 | 是否存在"必须拒绝"的行业 | 销售 | 无筛除能力 |
| 21 | **`BDD-Specific Relevance Gate` 的 `Strong` 信号清单是否需增删**；`Moderate` / `Strong` 边界（富溶剂工艺 vs 已明载难降解）是否清晰 | 销售 + 技术 | 档位偏差 |
| 22 | **Gate 结果是否需要在业务 PDF 有可视化位**（当前只进 Markdown 附录 B，业务员看不到） | 销售 | 可解释性 |
| 23 | **T3 证据门槛收紧后是否需要重跑历史客户**（部分历史主体曾按旧口径判 Target） | 销售 | 历史结论不一致 |
| 24 | **`Partner Cooperation Evidence` 的 `Confirmed` / `Supported` 边界** —— 「集团内网络成员提供核心工艺装置」是否算 `Confirmed` | 销售 + 技术 | Partner 档位偏差 |
| 25 | **合作证据强度两维度（BDD 域相关性 / 机制外部性）的定档权重**是否够用 | 销售 | `High` / `Medium` 边界 |
| 26 | **Partner Gate 是否导致 Partner 机会普遍下沉**（多例同时重算后机会档位普遍下降） | 销售 | 渠道开发优先级 |

---

## 十五、与其他 Skill 的边界

| 场景 | 用哪个 Skill |
|---|---|
| BDD / 工业废水客户背调与开发判断 | **本 Skill** |
| 体育用品 / 泳具等消费品外贸询盘 | `ai-inquiry-analysis` |
| 开发信生成（首触 / 跟进草稿） | **`bdd-sales-outreach`**（已建成 · 本 Skill 归档后自动衔接，见 §十六） |

**不适用**：具体技术方案设计、设备选型计算、报价核价、工程参数输出、小试方案 → 属人工工程师职责。

---

## 十六、与 `bdd-sales-outreach` 的自动衔接（2026-10-12 · MVP-2）

### ⛔ 硬性动作 —— 阶段 ② 是默认动作，不是可选项

**本 Skill 的交付流程包含两个阶段：**

| 阶段 | 动作 |
|---|---|
| **① 背调** | 出客户情报卡 → 渲染 PDF → **归档** |
| **② 衔接（默认必须做）** | **归档 STATUS PASS 后，立即衔接 `bdd-sales-outreach` 生成首触开发信草稿** |

> **不要等用户再说一次「生成开发信」。** 归档成功后按下列顺序执行：
> ```bash
> # 1) 准入判定（客户级 · 跨版本）
> python "<skill_dir>\bdd-sales-outreach\scripts\outreach_log.py" --admit "<客户键>"
> # 2) 放行则生成交接数据
> python "<skill_dir>\bdd-sales-outreach\scripts\handoff_from_card.py" "<归档报告.md>"
> # 3) 按 references/angle-library.md 撰写正文 → make_email.py → quality_check.py
> # 4) 登记：outreach_log.py --add "<handoff.json>" --action-type first_touch --review-state <质检结论>
> ```
> **唯一例外**：用户明确说「只要背调 / 不要开发信」。

**继续生成的条件（四个全满足）**
1. 报告**已归档且 STATUS PASS**（未成功归档 ⇒ 不生成）
2. 结论 ∈ {`建议重点开发`, `建议开发`, `建议先验证`}
3. 客户卡至少有 **1 条主体级 FACT**
4. 台账准入放行（`outreach_log.py --admit`）

**一律不生成**：`暂不优先` / `信息不足，暂缓判断` / 无对口岗位（`CONTACT_NONE`）；
以及台账状态为 `SENT`（**已发送，永久禁止重发首封**）、`DRAFT_OPEN`（已有草稿，改走 `draft_update`）、
`UNKNOWN_NEEDS_REVIEW`（**发送状态无证据 ⇒ 必须人工核查，不得默认未发送**）。

**边界**：本 Skill **只提供判断依据** —— 邮件撰写、质检、台账、发送准备全部由 `bdd-sales-outreach` 负责。
本 Skill **不写**邮件内容、**不改** 13 个 Internal Key、**不改**归档与 PDF / MD 规则。
归档完成后，本 Skill 的产物（客户卡 `.md`）**保持不变**，Outreach 只**读**不写。

> ### 架构说明（事实陈述，不影响上面的执行指令）
>
> 本节是**指令层衔接**：`archive_report.py` **零改动**，没有 hook / 监听 / 回调，因此**不是操作系统级的事件驱动**。
> 阶段 ② 由遵循本节指令的调用方在归档成功后执行，命令已在上方给出。
>
> **兜底（若某次背调未执行阶段 ②）**：
> ```bash
> python "<skill_dir>\bdd-sales-outreach\scripts\outreach_scan.py" --json-out "<log>\queue.json"
> python "<skill_dir>\bdd-sales-outreach\scripts\outreach_worker.py" --customer "<客户键>"
> ```
> `outreach_scan.py` 输出「**已归档但未生成开发信**」的待办队列（含阻断原因与人工处置命令），幂等、按 sha256 缓存结论；
> `outreach_worker.py` 单客户执行器完成「生成 → 质检 → 更新状态」，任务可恢复、重复执行不重复创建首草。
> 已配置**每周一定时扫描**（automation「BDD 开发信待办扫描（每周）」）作为兜底。
