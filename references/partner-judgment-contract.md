# Partner判断契约 · V1.2.1-b

本补丁替代旧规则中“自有AOP+同污染物/同工位即可直接竞争”的推导。
保持13主卡字段、五值Sales Conclusion和非数值判定。End-user继续原有规则。

## 实际执行顺序

1. 按现有证据政策检索企业、产品、项目和官方联系方式。联系人检索先于最终优先级，不能因先判Low而跳过。记录原网页、时间、逐字原文、主体及证据类型。
2. 模型/人工从原文整理结构化Partner输入，不把技术路线或宣传效果当成替代关系。
3. `python scripts/decision_engine.py input.json --out decision.json`。根据返回值填写13字段，禁止预设特定公司的结果。
4. Markdown附录B嵌入唯一的 `bdd-decision` JSON代码块，内容是上述input。`render_pdf.py`在真正导出前重新计算，矛盾则停止，不自动重写评级。
5. 按原归档流程保存新版本；历史文件保留。邮件生成/发送规则不在此补丁范围。

## 输入结构

顶层：`path: Partner`、`industry_fit: Target/Adjacent/Unknown`、`commercial_risk`、`missing_business`、`evidence`、`contacts`、`cooperation_search`。

每条证据：`id`、`type: FACT/INFERENCE/UNKNOWN`、`kind`、`quote`、`source_url`、`retrieved_at`、`subject_scope: target/group/related/project`。目标主体事实须有完整HTTP(S)链接、原文、时间；集团资料不可冒充target。推断须`reason/basis_ids/confidence`；UNKNOWN须`search_status: not_searched/searched_not_found/unavailable/no_source`。

`kind`及追加信息：

- `identity`：主体及主营业务；`capability`：设备开发/系统集成/交付能力；`application`：企业实际提供的具体处理场景。泛科普不是企业项目。
- `owned_product`：自售产品，不证明其自身工厂使用；自身工艺另有`own_plant`事实才可描述。
- `cooperation`：必须有`external_party`和`mechanism`；`technology_domain`明确标BDD/electrochemical/refractory_oxidation/AOP（外部核心氧化技术）或其他技术域。模块工程能力不等于外部氧化核心技术；只记Supported。不同网页转载同一交易须用同一`transaction_id`，不重复计数。
- `direct_substitution`：除可核事实外，`comparison`必须写明`offering/alternative/procurement_need/functional_equivalence`，由原文支撑两产品功能可直接替代及同一采购需求。仅“同类污染物”“同为AOP”不能使用该类型。
- `complementary_integration`：明确证据支持与BDD/电化学组合，`technology_domain: BDD`。尚未实现的组合只是INFERENCE。
- `purchase`：`purchase_object/project/current`三项有明确依据才算当前采购；既有研发合作不自动构成BDD采购意向。
- `demand_signal`：保留现有Weak/Potential/Strong Signal/Confirmed需求档位，需`strength/current/signal_type(PWE或CSD)/demand_object/technology_domain`，必须是目标主体与外部相关技术有关的事实。需求证据不自动等于采购意向；例如文件级技术评估可以构成需求证据，仍须另找采购证据。
- `project`：真实交付/项目证据，与cooperation按交易去重。
- `performance_claim`：Company-stated claim；`independent_validation`：独立机构对对应样品/参数的测试，必须标适用范围，不能用奖项替代测试。
- `commercial_risk`：按原政策核验，High须证据且`severity: High`；`financial_warning`沿用原白名单，附`affects_target_purchase`。`negative_fit`只能由“确证无可进入场景”使用，缺证据不能使用。

`contacts`保留脚本输出的邮箱及来源；具名联系人由Team原文人工核对后另记，个人邮箱不得构造。`cooperation_search`记录状态、checked_urls与时间，不得把未检索写成无合作入口。

## 相互独立的输出

- 竞争：Yes / Partial · Use-case dependent / Unknown / No，另附type、evidence_ids、confidence和legacy_conflict。明确直接竞争与合作并存时保留两侧证据。No仅由已证实互补支持，缺证据为Unknown。
- BDD Opportunity：沿用A～F证据门槛；有能力/应用而缺外部机制时通常Medium，不自动High。相同交易/新闻/产品目录不凑多个项目证据。
- Technology Partner Opportunity：技术合作机制，与BDD采购分开；非BDD联合研发通常Medium，不能直接证明会买BDD。
- Purchase Intent：真实当前采购证据独立判断，没有则Unknown；Demand Status保留原有五档，分别从PWE/CSD及采购证据判定，不因业务活跃或有邮箱而升档。
- Development Priority及Sales Conclusion：结合机会、需求、商业风险、财务影响、直接替代证据和已核合作切面。Conflict本身不是一票否决。Low若由直接竞争触发，必须同时有充分替代证据、定向检索覆盖且无正面可进入切面，并解释资源判断；尚未检索则先验证。

所有派生结论属于INFERENCE；官网真实性、性能独立验证和商业机会不是同一个置信度。

## 报告检查

主卡、Sales Intelligence和附录必须使用同一次计算值。主卡已找到邮箱就不能写“无公开联系方式”；有姓名但无个人邮箱时分开写；公司宣传参数在业务摘要和证据表均保留Company-stated claim。技术合作潜力、BDD机会、开发优先级不同档时解释缺少的证据。竞争/采购未知不能转写成确定否定。

旧报告无结构化输入时渲染输出LEGACY，表示仅保留历史规则，不宣称完成本次新逻辑验收；重评必须新建报告和证据，不改原历史文件。
