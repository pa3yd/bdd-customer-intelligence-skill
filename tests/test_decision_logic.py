import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import decision_engine as rules
import fetch_official_contacts as contacts
import render_pdf


def fact(eid, kind, **extra):
    return {"id": eid, "kind": kind, "type": "FACT", "quote": "Synthetic reviewed statement " + eid,
            "source_url": "https://example.org/" + eid, "retrieved_at": "2026-10-26",
            "subject_scope": "target", **extra}


def case():
    return {"path": "Partner", "industry_fit": "Adjacent", "commercial_risk": "Unknown",
            "evidence": [fact("E1", "identity"), fact("E2", "capability"), fact("E3", "application")],
            "contacts": {}, "cooperation_search": {"status": "not_searched"}}


def substitute():
    return fact("E4", "direct_substitution", comparison={"offering": "Oxidation unit A",
        "alternative": "BDD unit B", "procurement_need": "same buyer oxidation duty",
        "functional_equivalence": "documented direct substitution at specified duty"})


def report_input(data):
    result = rules.evaluate(data)
    fields = {"Customer Type": "Partner", "BDD Opportunity": result["bdd_opportunity"] + " · " + result["competition"]["status"],
              "Sales Conclusion": result["sales_conclusion"], "Demand Status": result["demand_status"],
              "Who to Contact": "未取得具名联系人", "Current Wastewater Treatment / Technology": "自售设备产品"}
    md = "V1.2.1-b\n" + " ".join(e["id"] + " " + e.get("source_url", "") for e in data["evidence"])
    md += "\nTechnology Partner Opportunity: " + result["technology_partner_opportunity"]
    md += "\nDevelopment Priority: " + result["development_priority"]
    md += "\nPurchase Intent: " + result["purchase_intent"]
    md += "\n## 附录 B\n```bdd-decision\n" + json.dumps(data) + "\n```\n"
    return md, fields


class DecisionTests(unittest.TestCase):
    def test_malformed_model_input_stops_with_clear_validation_error(self):
        for data in ([], {"path": "Partner", "evidence": "not a list"},
                     {"path": "Partner", "evidence": [{"id": {"bad": "id"}}]}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                rules.evaluate(data)

    def test_a_different_routes_overlap_is_not_confirmed_competition(self):
        data = case()
        self.assertEqual(rules.evaluate(data)["competition"]["status"], "Unknown")
        data["evidence"].append(fact("E4", "cooperation", external_party="Independent engineering firm", mechanism="joint modular system", technology_domain="engineering"))
        result = rules.evaluate(data)
        self.assertEqual(result["competition"]["status"], "Partial / Use-case dependent")
        self.assertEqual(result["competition"]["complementary_opportunity"], "Potential · INFERENCE")
        self.assertEqual(result["purchase_intent"], "Unknown")

    def test_b_substitution_needs_function_and_same_procurement_evidence(self):
        data = case(); data["evidence"].append(substitute())
        result = rules.evaluate(data)
        self.assertEqual(result["competition"]["status"], "Yes")
        self.assertEqual(result["sales_conclusion"], "建议先验证")
        data["cooperation_search"] = {"status": "searched_not_found", "checked_urls": ["https://example.org/partners"]}
        self.assertEqual(rules.evaluate(data)["development_priority"], "Low")
        data["evidence"][-1].pop("comparison")
        self.assertEqual(rules.evaluate(data)["competition"]["status"], "Unknown")

    def test_c_competition_and_cooperation_preserve_both(self):
        data = case(); data["evidence"] += [substitute(), fact("E5", "cooperation", external_party="Outside partner", mechanism="joint R&D", technology_domain="engineering")]
        result = rules.evaluate(data)
        self.assertTrue(result["competition"]["direct_substitution"])
        self.assertEqual(result["competition"]["status"], "Partial / Use-case dependent")
        self.assertEqual(result["competition"]["legacy_conflict"], "Yes")
        self.assertEqual(result["development_priority"], "Medium")

    def test_d_company_mail_without_person(self):
        result = contacts.run(["https://example.org/"], None, "example.org", fetcher=lambda *_: (200, "<p>sales@example.org</p>"))
        self.assertEqual(result["search_status"], "found")
        self.assertEqual(result["emails"][0]["deliverability"], "Unknown")
        data = case(); data["contacts"] = result
        md, fields = report_input(data)
        self.assertFalse(rules.check_report(md, fields)[0])
        fields["Who to Contact"] = "公司邮箱 sales@example.org；具名技术联系人未取得"
        self.assertTrue(rules.check_report(md, fields)[0])

    def test_e_team_name_does_not_generate_person_email(self):
        pages = {"https://example.org/": '<a href="/team">Team</a>',
                 "https://example.org/team": '<h2>CTO</h2><p>Jane Smith</p>'}
        result = contacts.run(["https://example.org/"], None, "example.org", fetcher=lambda u, p: (200, pages[u]))
        self.assertEqual(result["emails"], [])
        self.assertIn("Jane Smith", result["team_pages"][0]["text"])
        self.assertEqual(result["named_contact_candidates"][0]["name"], "Jane Smith")
        self.assertEqual(result["named_contact_candidates"][0]["personal_email"], "Unknown")

    def test_f_promotional_performance_is_not_independent_validation(self):
        data = case(); data["evidence"].append(fact("E4", "performance_claim"))
        result = rules.evaluate(data)
        self.assertEqual(result["performance_evidence"]["independent_validation"], [])
        md, fields = report_input(data)
        self.assertFalse(rules.check_report(md, fields)[0])
        self.assertTrue(rules.check_report(md + "\nCompany-stated claim", fields)[0])

    def test_g_no_projects_purchase_or_cooperation_does_not_become_high(self):
        result = rules.evaluate(case())
        self.assertEqual((result["bdd_opportunity"], result["development_priority"], result["demand_status"]), ("Medium", "Medium", "Unknown"))
        self.assertEqual(result["technology_partner_opportunity"], "Unknown")

    def test_missing_fact_source_rejected_and_inference_never_promoted(self):
        data = case(); data["evidence"][0].pop("source_url")
        with self.assertRaises(ValueError): rules.evaluate(data)
        data = case(); e = substitute(); e.update(type="INFERENCE", reason="possible substitutability", basis_ids=["E3"], confidence="Low")
        data["evidence"].append(e)
        self.assertEqual(rules.evaluate(data)["competition"]["status"], "Unknown")

    def test_same_transaction_is_not_two_projects(self):
        data = case()
        data["evidence"] += [fact("E4", "cooperation", external_party="Outside", mechanism="electrode integration", technology_domain="BDD", transaction_id="same"), fact("E5", "project", transaction_id="same")]
        self.assertEqual(rules.evaluate(data)["bdd_opportunity"], "Medium")
        data["evidence"][-1]["transaction_id"] = "different"
        self.assertEqual(rules.evaluate(data)["bdd_opportunity"], "High")

    def test_group_context_and_unrelated_purchase_do_not_upgrade_target(self):
        data = case()
        data["evidence"] += [fact("E4", "cooperation", subject_scope="group", external_party="Other", mechanism="R&D", technology_domain="BDD"),
                             fact("E5", "purchase", purchase_object="office stationery", project="office", current=True, technology_domain="office")]
        result = rules.evaluate(data)
        self.assertEqual(result["cooperation_gate"], "Unverified")
        self.assertEqual(result["purchase_intent"], "Unknown")

    def test_demand_signal_levels_survive_without_becoming_purchase_intent(self):
        for strength in ("Weak", "Potential", "Strong Signal", "Confirmed"):
            with self.subTest(strength=strength):
                data = case(); data["evidence"].append(fact("E4", "demand_signal", strength=strength,
                    current=True, signal_type="PWE", demand_object="external oxidation assessment", technology_domain="AOP"))
                result = rules.evaluate(data)
                self.assertEqual(result["demand_status"], strength)
                self.assertEqual(result["purchase_intent"], "Unknown")

    def test_high_opportunity_potential_demand_preserves_develop_rule(self):
        data = case(); data["evidence"] += [
            fact("E4", "cooperation", external_party="Outside", mechanism="electrode integration", technology_domain="BDD"),
            fact("E5", "project"), fact("E6", "demand_signal", strength="Potential", current=True,
                signal_type="PWE", demand_object="external oxidation assessment", technology_domain="BDD")]
        self.assertEqual(rules.evaluate(data)["sales_conclusion"], "建议开发")

    def test_risk_label_needs_matching_severity_evidence(self):
        data = case(); data["commercial_risk"] = "High"
        data["evidence"].append(fact("E4", "commercial_risk", severity="Low"))
        self.assertEqual(rules.evaluate(data)["commercial_risk"], "Unknown")

    def test_report_rejects_wrong_grade_and_self_factory(self):
        md, fields = report_input(case())
        fields["Sales Conclusion"] = "暂不优先"
        self.assertFalse(rules.check_report(md, fields)[0])
        fields["Sales Conclusion"] = "建议先验证"
        fields["Current Wastewater Treatment / Technology"] = "自身废水采用该氧化技术"
        ok, issues, _ = rules.check_report(md, fields)
        self.assertFalse(ok)
        self.assertTrue(any("自身工厂" in issue for issue in issues))

    def test_cross_section_conflict_and_fake_independent_validation_blocked(self):
        data = case(); data["evidence"].append(fact("E4", "independent_validation"))
        self.assertEqual(rules.evaluate(data)["performance_evidence"]["independent_validation"], [])
        md, fields = report_input(data)
        md = md.replace("## 附录 B", "- Conflict: Yes\n## 附录 B")
        self.assertFalse(rules.check_report(md, fields)[0])

    def test_renderer_real_entry_rejects_new_partner_without_input(self):
        md = "V1.2.1-b\n| 字段 | 判定 |\n|---|---|\n| Customer Type | Partner |\n"
        self.assertFalse(render_pdf.check_decision_consistency(md)[0])
        with self.assertRaises(ValueError): render_pdf.build_html(md, False)

    def test_legacy_renderer_compatibility(self):
        self.assertTrue(render_pdf.check_decision_consistency("# Legacy report\n")[0])


class ContactTests(unittest.TestCase):
    def test_navigation_discovers_php_and_preserves_language(self):
        pages = {"https://example.org/?locale=en_US": '<a href="/page/team.php">Team</a><a href="/bbs/write.php?bo_table=inquiry">Inquiry</a>',
            "https://example.org/page/team.php?locale=en_US": "<h2>CEO</h2><p>Jane Smith</p>",
            "https://example.org/bbs/write.php?bo_table=inquiry&locale=en_US": '<form><p>Partnership Inquiry</p></form><p>Tel +82 42 123 4567</p>'}
        result = contacts.run([next(iter(pages))], None, "example.org", fetcher=lambda u, p: (200, pages[u]))
        self.assertTrue(result["team_pages"])
        self.assertTrue(result["forms"][0]["partnership"])
        self.assertTrue(result["phones"])

    def test_states_and_templates_and_domain_boundary(self):
        self.assertEqual(contacts.run([], None, "example.org")["search_status"], "not_searched")
        self.assertEqual(contacts.run(["x"], None, "example.org", fetcher=lambda *_: (-1, "timeout"))["search_status"], "unavailable")
        self.assertEqual(contacts.run(["x"], None, "example.org", fetcher=lambda *_: (200, "no contacts"))["search_status"], "searched_not_found")
        self.assertFalse(contacts.classify("sales@notexample.org", "example.org")["domain_match"])
        self.assertTrue(contacts.classify("sales@dept.example.org", "example.org")["domain_match"])
        self.assertNotIn("track@example.org", contacts.extract('<script>"track@example.org"</script>')["plain"])

    def test_cloudflare_remains_supported(self):
        email = "sales@real.org"; key = 17
        encoded = f"{key:02x}" + "".join(f"{ord(c)^key:02x}" for c in email)
        self.assertIn(email, contacts.extract(f'<a data-cfemail="{encoded}"></a>')["cf"])


if __name__ == "__main__":
    unittest.main()
