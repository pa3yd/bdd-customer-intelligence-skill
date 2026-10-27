"""Evidence-led Partner judgment and report preflight, V1.2.1-b.

The caller researches and labels evidence; this module applies reproducible
rules. It does not search, call a model, score numerically or alter old cards.
"""
from __future__ import annotations
import argparse
import json
import re
from urllib.parse import urlsplit

RULE_VERSION = "partner-decision/1"
CONCLUSIONS = {"High": "建议重点开发", "Develop": "建议开发", "Medium": "建议先验证",
               "Low": "暂不优先", "Unknown": "信息不足，暂缓判断"}


def _sourced_fact(e):
    return (e.get("type") == "FACT" and bool(e.get("quote"))
            and urlsplit(str(e.get("source_url", ""))).scheme in {"https", "http"}
            and bool(urlsplit(str(e.get("source_url", ""))).hostname)
            and bool(e.get("retrieved_at")) and e.get("subject_scope") in {"target", "group", "related", "project"})


def _fact(e):
    return _sourced_fact(e) and e.get("subject_scope") == "target"


def evaluate(data):
    if not isinstance(data, dict):
        raise ValueError("结构化判断输入必须为JSON对象")
    if data.get("path") != "Partner":
        raise ValueError("此引擎仅处理Partner；End-user继续执行原有独立门槛")
    evidence = data.get("evidence") or []
    if not isinstance(evidence, list) or not all(isinstance(e, dict) for e in evidence):
        raise ValueError("evidence必须为证据对象列表")
    if not isinstance(data.get("contacts") or {}, dict) or not isinstance(data.get("cooperation_search") or {}, dict):
        raise ValueError("contacts及cooperation_search必须为对象")
    ids = [e.get("id") for e in evidence]
    if any(not isinstance(eid, str) or not eid.strip() for eid in ids) or len(ids) != len(set(ids)):
        raise ValueError("证据ID缺失或重复")
    errors = []
    for e in evidence:
        if e.get("type") not in {"FACT", "INFERENCE", "UNKNOWN"}:
            errors.append(f"{e.get('id')}: 非法证据类型")
        if e.get("type") == "FACT" and not _sourced_fact(e):
            errors.append(f"{e.get('id')}: FACT缺少主体/原文/可核验链接/时间")
        if e.get("type") == "INFERENCE" and not (e.get("reason") and e.get("basis_ids") and e.get("confidence")):
            errors.append(f"{e.get('id')}: 推断必须注明依据与置信度")
        if e.get("type") == "UNKNOWN" and e.get("search_status") not in {"not_searched", "searched_not_found", "unavailable", "no_source"}:
            errors.append(f"{e.get('id')}: UNKNOWN缺少检索状态")
    facts = [e for e in evidence if _fact(e)]
    fact_ids = {e["id"] for e in evidence if _sourced_fact(e)}
    for e in evidence:
        if e.get("type") == "INFERENCE" and not set(e.get("basis_ids", [])).issubset(fact_ids):
            errors.append(f"{e['id']}: 推断依据没有对应可核验FACT")
    if errors:
        raise ValueError("；".join(errors))
    def of(kind):
        return [e for e in facts if e.get("kind") == kind]
    def refs(items):
        return [e["id"] for e in items]
    identity, capability, application = of("identity"), of("capability"), of("application")
    cooperation = [e for e in of("cooperation") if e.get("external_party") and e.get("mechanism")]
    bdd_cooperation = [e for e in cooperation if e.get("technology_domain") in {"BDD", "electrochemical", "refractory_oxidation", "AOP"}]
    substitution = [e for e in of("direct_substitution") if all(
        e.get("comparison", {}).get(k) for k in ("offering", "alternative", "procurement_need", "functional_equivalence"))]
    complementary = [e for e in of("complementary_integration") if e.get("technology_domain") == "BDD"]
    procurement = [e for e in of("purchase") if e.get("purchase_object") and e.get("project") and e.get("current") is True
                   and e.get("technology_domain") in {"BDD", "electrochemical", "refractory_oxidation", "AOP"}]
    mixed = bool(substitution and (cooperation or complementary or procurement))
    if mixed:
        conflict, conflict_type, confidence = "Partial / Use-case dependent", "Competition and cooperation", "Medium"
    elif substitution:
        conflict, conflict_type, confidence = "Yes", "Direct competitor", "High"
    elif complementary:
        conflict, conflict_type, confidence = "No", "Complementary Opportunity", "High"
    elif application and cooperation and capability:
        conflict, conflict_type, confidence = "Partial / Use-case dependent", "Application overlap; potential integration", "Medium"
    else:
        conflict, conflict_type, confidence = "Unknown", "Insufficient substitution evidence", "Low"
    competition = {"status": conflict, "type": conflict_type, "confidence": confidence,
        "legacy_conflict": "Yes" if substitution else "No" if complementary else "Unknown",
        "application_overlap": bool(application), "direct_substitution": bool(substitution),
        "direct_substitution_evidence": "Confirmed" if substitution else "Unknown",
        "same_procurement_need": "Confirmed" if substitution else "Unknown", "evidence_ids": refs(substitution + complementary + cooperation + application),
        "complementary_opportunity": "Supported" if complementary else "Potential · INFERENCE" if cooperation and application else "Unknown",
        "reason": "同一污染物或应用领域不证明功能可直接替代；竞争与合作切面分别取证。"}
    negative = of("negative_fit")
    relevant = bool(identity and capability and application and data.get("industry_fit") in {"Target", "Adjacent"})
    # Same transaction/announcement counts once, even when copied into many facts.
    channels = {e.get("transaction_id") or e["source_url"] for e in of("project") + cooperation}
    opportunity = ("Low" if negative else "High" if relevant and len(channels) >= 2 and bdd_cooperation
                   else "Medium" if relevant else "Unknown")
    technology_partner = ("High" if bdd_cooperation and capability else "Medium" if cooperation and capability
                          else "Unknown")
    demand_levels = ("Unknown", "Weak", "Potential", "Strong Signal", "Confirmed")
    demand_signals = [e for e in of("demand_signal") if e.get("current") is True
                      and e.get("demand_object") and e.get("signal_type") in {"PWE", "CSD"}
                      and e.get("technology_domain") in {"BDD", "electrochemical", "refractory_oxidation", "AOP"}
                      and e.get("strength") in demand_levels]
    demand = ("Confirmed" if procurement else max(
        (e["strength"] for e in demand_signals), key=demand_levels.index, default="Unknown"))
    requested_risk = data.get("commercial_risk", "Unknown")
    if requested_risk not in {"High", "Medium", "Low", "Unknown"}:
        raise ValueError("商业风险枚举无效")
    risk_evidence = of("commercial_risk")
    risk = ("High" if any(e.get("severity") == "High" for e in risk_evidence) else
            requested_risk if requested_risk in {"Low", "Medium"} and any(
                e.get("severity") == requested_risk for e in risk_evidence) else "Unknown")
    financial = any(e.get("affects_target_purchase") is not False for e in of("financial_warning"))
    searched = data.get("cooperation_search", {})
    searched_closed = searched.get("status") == "searched_not_found" and bool(searched.get("checked_urls"))
    reasons = []
    if risk == "High" or opportunity == "Low":
        priority = "Low"; reasons.append("已核实高商业风险或缺乏可进入场景的明确负面证据")
    elif substitution and searched_closed and not cooperation and not procurement and not complementary:
        priority = "Low"; reasons.append("直接替代关系有证据；已定向检索采购/集成切面但未找到正面入口，当前资源优先级低；不等于没有采购可能")
    elif opportunity == "Unknown":
        priority = "Unknown"; reasons.append("主体、能力或具体应用证据不足，尚无法判断")
    elif opportunity == "High" and demand in {"Confirmed", "Strong Signal"} and risk in {"Low", "Medium"} and not financial and not data.get("missing_business"):
        priority = "High"; reasons.append("BDD域外部集成机制、项目/采购及风险依据满足重点开发条件")
    elif opportunity == "High" and demand == "Potential" and risk != "High" and not financial:
        priority = "Develop"; reasons.append("BDD机会High且有相关需求间接正面信号；尚无明确采购意向，按原规则建议开发")
    elif opportunity == "Medium" and demand in {"Confirmed", "Strong Signal"} and risk in {"Low", "Medium"} and not financial:
        priority = "Develop"; reasons.append("有主体级采购项目及相关业务证据，仍需确认具体合作切面")
    else:
        priority = "Medium"; reasons.append("有技术或应用关联，但未核实BDD外购项目、采购意向或合作入口，先验证")
    if substitution:
        reasons.append("保留直接竞争证据；逐项目区分系统替代与部件供货/联合研发")
    if financial:
        priority = "Medium" if priority in {"High", "Develop"} else priority
        reasons.append("存在目标采购/执行能力的财务警示，需先核实影响")
    company_claims = refs(of("performance_claim"))
    independent = refs([e for e in of("independent_validation") if all(
        e.get(k) for k in ("test_organization", "test_scope", "independence_basis"))])
    return {"rule_version": RULE_VERSION, "competition": competition,
        "bdd_opportunity": opportunity, "technology_partner_opportunity": technology_partner,
        "demand_status": demand, "purchase_intent": "Confirmed" if procurement else "Unknown",
        "development_priority": priority, "sales_conclusion": CONCLUSIONS[priority],
        "commercial_risk": risk,
        "priority_reasons": reasons, "cooperation_gate": "Confirmed" if bdd_cooperation else "Supported" if cooperation else "Unverified",
        "decision_confidence": "Medium" if relevant else "Low",
        "performance_evidence": {"company_stated_claims": company_claims, "independent_validation": independent,
                                 "status": "Independent evidence available; inspect scope" if independent else "Company-stated claim; not independently validated"},
        "evidence_ids": refs(facts), "unknowns": [e["id"] for e in evidence if e.get("type") == "UNKNOWN"],
        "next_action": "核实具体项目是否考虑外部BDD电极、模组或联合方案，并确认技术/采购负责人"}


BLOCK = re.compile(r"```bdd-decision\s*\n(.*?)\n```", re.S)


def check_report(md, fields):
    """Recompute new Partner cards at the actual rendering boundary. Never rewrite."""
    blocks = BLOCK.findall(md)
    if not blocks:
        if "V1.2.1-b" in md and "Partner" in fields.get("Customer Type", ""):
            return False, ["V1.2.1-b Partner报告缺少bdd-decision输入，无法复算"], None
        return True, ["LEGACY: 旧报告按原规则展示，未声称完成新判定"], None
    if len(blocks) != 1:
        return False, ["结构化判断输入须且只能出现一次"], None
    try:
        data = json.loads(blocks[0]); result = evaluate(data)
    except (ValueError, TypeError, KeyError) as exc:
        return False, ["结构化证据错误：" + str(exc)], None
    problems = []
    clean = lambda s: re.sub(r"[*`_]", "", str(s))
    expected = {"BDD Opportunity": result["bdd_opportunity"], "Sales Conclusion": result["sales_conclusion"],
                "Demand Status": result["demand_status"]}
    for key, value in expected.items():
        field = clean(fields.get(key, ""))
        choices = "|".join(CONCLUSIONS.values()) if key == "Sales Conclusion" else "High|Medium|Low|Unknown" if key == "BDD Opportunity" else "Confirmed|Strong Signal|Potential|Weak|Unknown"
        found = re.search(choices, field)
        if not found or found.group(0) != value:
            problems.append(f"{key}与证据引擎不一致；应为{value}")
    for label, key in (("Technology Partner Opportunity", "technology_partner_opportunity"),
                       ("Development Priority", "development_priority"), ("Purchase Intent", "purchase_intent")):
        match = re.search(re.escape(label) + r"\s*[:：]\s*(High|Medium|Low|Unknown|Develop|Confirmed)", clean(md.split("```bdd-decision", 1)[0]))
        if not match or match.group(1) != result[key]:
            problems.append(label + "须独立展示且与证据复算一致")
    if result["competition"]["status"] not in clean(fields.get("BDD Opportunity", "")):
        problems.append("主卡须显示本次独立竞争状态，不可省略或沿用旧标签")
    contact = clean(fields.get("Who to Contact", ""))
    # Renderer uses Contact as its canonical internal key.
    if not contact:
        contact = clean(fields.get("Contact", ""))
    contacts = data.get("contacts") or {}
    observed = {e.get("email", "").lower() for e in contacts.get("emails", []) if e.get("sources") and not e.get("template_hint")}
    published = set(re.findall(r"[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}", contact))
    if observed and (not published or re.search(r"未列示公开邮箱|官网无联系方式|未找到任何邮箱|无公开邮箱", contact)):
        problems.append("已提取公开邮箱，联系人主卡仍缺失或否认官方渠道")
    if any(e.lower() not in observed for e in published):
        problems.append("主卡邮箱没有公开原文来源，不得标作已核实")
    named = contacts.get("named_contacts") or []
    if named and (not any(p.get("name") in contact for p in named) or re.search(r"未发现组织|无团队页|没有任何具名联系人", contact)):
        problems.append("官方具名联系人证据与联系人主卡不一致")
    business_md = md.split("## 附录 B", 1)[0]
    for label, value in (("BDD Opportunity", result["bdd_opportunity"]),
                         ("Commercial Risk", result["commercial_risk"]),
                         ("Conflict", result["competition"]["status"])):
        values = re.findall(r"(?:^|\n)\s*(?:-\s*)?" + re.escape(label) + r"\s*[:=：]\s*(Partial / Use-case dependent|High|Medium|Low|Unknown|Yes|No)", clean(business_md))
        if any(v != value for v in values):
            problems.append(label + "在主卡/销售情报/风险之间存在矛盾")
    if result["competition"]["status"] != "Yes" and re.search(r"(?:已确认|明确)(?:的)?直接竞争|Conflict\s*=\s*Yes.{0,20}一票否决", business_md):
        problems.append("主卡/销售情报把未证实或部分竞争写成明确直接竞争")
    if re.search(r"(?:自有工厂|自身废水|厂内).{0,18}(?:使用|采用|运行)", fields.get("Current Wastewater Treatment / Technology", "")) and not any(
            e.get("kind") == "own_plant" and _fact(e) for e in data.get("evidence", [])):
        problems.append("把设备产品误写成该公司的自身工厂处理工艺")
    if re.search(r"经独立测试证明|已获独立验证|独立验证通过", business_md) and not result["performance_evidence"]["independent_validation"]:
        problems.append("公司宣传性能被写成独立验证结果")
    if result["performance_evidence"]["company_stated_claims"] and "Company-stated claim" not in md:
        problems.append("性能宣传缺少Company-stated claim限定")
    for e in data.get("evidence", []):
        if e["id"] not in md[:BLOCK.search(md).start()]:
            problems.append(f"{e['id']}没有进入业务/审计证据表")
        if _sourced_fact(e) and e["source_url"] not in md[:BLOCK.search(md).start()]:
            problems.append(f"{e['id']}的完整来源链接未进入报告证据表")
    return not problems, problems, result


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("input"); ap.add_argument("--out", required=True)
    args = ap.parse_args()
    from pathlib import Path
    result = evaluate(json.loads(Path(args.input).read_text(encoding="utf-8")))
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(result["rule_version"], result["competition"]["status"], result["bdd_opportunity"], result["sales_conclusion"])


if __name__ == "__main__":
    main()
