# -*- coding: utf-8 -*-
"""官方联系方式补查器（背调 Skill · 只读工具）

用途：当目标企业「值得开发但未找到邮箱」时，按固定阶梯抓取官网原始 HTML，
      提取并解码邮箱（**含 Cloudflare Email Protection**），输出带来源与核验日期的 JSON。

阶梯（按用户口径）：
    官网首页 → Contact 页面 → Impressum（德国常见法律信息页）→ 官网底部（全站页脚）→ 官方 PDF

设计要点：
  · **只提取网页中真实存在的邮箱**；不做任何猜测 / 拼接（如 firstname.lastname@ 构造）。
  · **解码 Cloudflare `data-cfemail`**（XOR-hex）—— 明文正则无法命中这类保护。
  · 提取 `mailto:` 链接与明文邮箱。
  · **不区分个人/部门时按事实输出**：只标注 `role_local`（本地部分是否为角色词）与
    `domain_match`（是否同站域），**分类结论由人（或上层规则）判定**。
  · 输出**每条来源 URL + HTTP 状态 + 核验日期**。
  · stdlib only；支持 `--proxy`，失败自动回退直连。

用法：
    python fetch_official_contacts.py --domain example.com
    python fetch_official_contacts.py --url https://example.com/contact-us
    python fetch_official_contacts.py --domain example.com --json-out contacts.json
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
from html import unescape
from html.parser import HTMLParser
import ssl
import sys
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlsplit, unquote, parse_qsl, urlencode, urlunsplit
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/153.0 Safari/537.36")

# 角色/公共邮箱本地部分（用于标注，不用于丢弃）
ROLE_LOCALS = ("info", "contact", "kontakt", "sales", "enquiry", "enquiries",
               "office", "admin", "service", "support", "export", "marketing",
               "ehs", "hse", "hr", "jobs", "career", "press", "media", "hello")

# 明显是模板/演示/表单占位 的邮箱（Framer/WordPress 模板残留）——只标注，不静默丢弃
TEMPLATE_HINTS = ("pawfect", "example.com", "yourdomain", "domain.com",
                  "email.com", "sentry.io", "wixpress")

# 阶梯候选路径（相对域名）
LADDER = ["/", "/contact-us", "/contact", "/kontakt", "/impressum", "/imprint",
          "/legal", "/en/contact-us", "/en/contact", "/about-us"]
DISCOVERY_HINTS = ("contact", "team", "about", "company", "news", "partner", "inquiry",
                   "management", "leadership", "문의", "회사", "조직", "团队", "联系")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAILTO_RE = re.compile(r"mailto:([^\"'\s>?]+)", re.I)
CF_RE = re.compile(r"data-cfemail=[\"']([0-9a-fA-F]+)[\"']")
PDF_RE = re.compile(r'href="([^"]+\.pdf)"', re.I)


def _opener(proxy: str | None):
    ctx = ssl.create_default_context()
    handlers = [urllib.request.HTTPSHandler(context=ctx)]
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    op = urllib.request.build_opener(*handlers)
    op.addheaders = [("User-Agent", UA)]
    return op


def fetch(url: str, proxy: str | None, timeout: int = 12) -> tuple[int, str]:
    """返回 (状态码, HTML 文本)；失败返回 (-1, 错误)。先试代理，再直连。"""
    for pr in ([proxy] if proxy else []) + [None]:
        try:
            with _opener(pr).open(url, timeout=timeout) as r:
                if _host(r.geturl()) != _host(url):
                    return -2, "跳转到其他域名，主体关系需另行核实：" + r.geturl()
                raw = r.read(4 * 1024 * 1024)
                enc = "utf-8"
                m = re.search(rb'charset=["\']?([\w-]+)', raw[:2048], re.I)
                if m:
                    enc = m.group(1).decode("ascii", "ignore")
                return r.status, raw.decode(enc, errors="ignore")
        except urllib.error.HTTPError as e:
            return e.code, ""          # 404 等：保留真实状态码（阶梯探测需要）
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
    return -1, last


def decode_cf(hexstr: str) -> str:
    """解码 Cloudflare Email Protection：首字节为 XOR 密钥。"""
    try:
        k = int(hexstr[:2], 16)
        return "".join(chr(int(hexstr[i:i + 2], 16) ^ k)
                       for i in range(2, len(hexstr), 2))
    except Exception:  # noqa: BLE001
        return ""


def extract(html: str) -> dict:
    """从原始 HTML 提取邮箱（明文 / mailto / Cloudflare 解码）与 PDF 链接。"""
    cf = {e for e in (decode_cf(h) for h in CF_RE.findall(html)) if e}
    html = unescape(html)
    mailto = {unquote(m).strip() for m in MAILTO_RE.findall(html) if "@" in unquote(m)}
    # Script/JSON/template assets can contain addresses that were never published
    # as contact information. Keep visible text + mailto + Cloudflare only.
    visible = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    plain = set(EMAIL_RE.findall(re.sub(r"<[^>]+>", " ", visible)))
    pdfs = sorted({p for p in PDF_RE.findall(html)})[:5]
    return {"cf": cf, "mailto": mailto, "plain": plain, "pdf": pdfs}


def classify(email: str, site_domain: str) -> dict:
    local, _, dom = email.partition("@")
    dom_l = dom.lower()
    return {
        "email": email,
        "domain": dom_l,
        "domain_match": bool(site_domain) and (dom_l == site_domain.lower().removeprefix("www.") or dom_l.endswith("." + site_domain.lower().removeprefix("www."))),
        "role_local": local.lower() in ROLE_LOCALS,
        "template_hint": any(h in dom_l for h in TEMPLATE_HINTS),
    }


def is_valid(email: str) -> bool:
    """基本形态校验；不构造、不补全。"""
    if not email or email.count("@") != 1:
        return False
    local, _, dom = email.partition("@")
    if not local or "." not in dom:
        return False
    if len(dom.split(".")[-1]) < 2:
        return False
    return True


class ContactPage(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.parts = []; self.skip = 0
        self.has_form = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "style", "noscript"}: self.skip += 1
        if tag == "a" and attrs.get("href"): self.links.append(attrs["href"])
        if tag == "form": self.has_form = True
    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"}: self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)


def _host(url):
    return (urlsplit(url).hostname or "").lower().removeprefix("www.")


def named_candidates(text, url, checked_at):
    """Adjacent role/name text is a candidate; never infer email or authority."""
    result = []
    for match in re.finditer(r"\b(Founder CEO|CEO|CTO|CAO|Senior Research Fellow)\s+([A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+){1,3})", text):
        parts = match.group(2).split()
        for index, part in enumerate(parts):
            if part in {"Master", "Senior", "Deputy", "Former", "Development", "President", "Ph"}:
                parts = parts[:index]; break
        if len(parts) >= 2:
            result.append({"name": " ".join(parts), "role": match.group(1), "source_url": url,
                           "checked_at": checked_at, "evidence_type": "OFFICIAL_TEAM_TEXT",
                           "verification_status": "requires_review", "personal_email": "Unknown",
                           "procurement_authority": "Unknown"})
    return result


def run(urls: list[str], proxy: str | None, site_domain: str, *, fetcher=None,
        discover=True, max_pages=16) -> dict:
    today = _dt.date.today().isoformat()
    found: dict[str, dict] = {}
    pages: list[dict] = []
    phones, forms, team_pages, people = [], [], [], []
    queue = list(dict.fromkeys(urls))
    reader = fetcher or fetch
    visited = set()
    while queue and len(pages) < max_pages:
        u = queue.pop(0)
        if u in visited: continue
        visited.add(u)
        status, html = reader(u, proxy)
        rec = {"url": u, "http": status, "checked_at": today,
               "cf": 0, "mailto": 0, "plain": 0, "pdf": [],
               "search_status": "searched_not_found" if status == 200 else "unavailable",
               "reason": "" if status == 200 else html[:500] or f"HTTP {status}"}
        if status == 200 and html:
            parsed = ContactPage(); parsed.feed(html)
            text = " ".join(" ".join(parsed.parts).split())
            rec["text"] = text[:40000]
            if any(x in u.lower() for x in ("team", "leadership", "management")):
                people.extend(named_candidates(text, u, today))
                team_pages.append({"url": u, "text": text[:20000], "checked_at": today,
                                   "evidence_type": "OFFICIAL_TEAM_PAGE", "status": "requires_name_role_review"})
            for number in re.findall(r"(?:tel:)([^\s\"'<>]+)", html, re.I):
                phones.append({"phone": unescape(number), "source_url": u, "checked_at": today, "evidence_type": "OFFICIAL_TEL_LINK"})
            for number in re.findall(r"(?:Tel(?:ephone)?|Phone|전화)\s*[:.]?\s*(\+?[\d() -]{7,24})", text, re.I):
                phones.append({"phone": number.strip(), "source_url": u, "checked_at": today, "evidence_type": "OFFICIAL_PAGE_TEXT"})
            if parsed.has_form and any(x in text.lower() for x in ("inquiry", "partnership", "문의", "contact us")):
                forms.append({"url": u, "checked_at": today, "evidence_type": "OFFICIAL_FORM",
                              "partnership": "partnership" in text.lower(), "submitted": False})
            if discover:
                discovered = []
                for link in parsed.links:
                    target = urljoin(u, unescape(link)).split("#")[0]
                    # Preserve the explicitly chosen language without inferring
                    # affiliation to another host after a locale redirect.
                    parsed_target = urlsplit(target)
                    query = dict(parse_qsl(parsed_target.query))
                    for key, value in parse_qsl(urlsplit(u).query):
                        if key in {"locale", "lang", "language"}:
                            query.setdefault(key, value)
                    target = urlunsplit(parsed_target._replace(query=urlencode(query)))
                    if urlsplit(target).scheme in {"http", "https"} and _host(target) == site_domain.lower().removeprefix("www.") and any(h in target.casefold() for h in DISCOVERY_HINTS):
                        if target not in visited and target not in discovered:
                            discovered.append(target)
                queue = list(dict.fromkeys(discovered + queue if not pages else queue + discovered))
            got = extract(html)
            rec["cf"] = len(got["cf"])
            rec["mailto"] = len(got["mailto"])
            rec["plain"] = len(got["plain"])
            rec["pdf"] = got["pdf"]
            for e in (got["cf"] | got["mailto"] | got["plain"]):
                if not is_valid(e):
                    continue
                key = e.lower()
                if key not in found:
                    c = classify(e, site_domain)
                    c.update(publication_status="observed_on_official_page", deliverability="Unknown",
                             evidence_type="PUBLIC_CONTACT", personal_owner="Unknown")
                    c["sources"] = [{"url": u, "via": (
                        "cloudflare" if e in got["cf"] else
                        "mailto" if e in got["mailto"] else "plaintext"),
                        "checked_at": today}]
                    found[key] = c
                else:
                    via = ("cloudflare" if e in got["cf"] else
                           "mailto" if e in got["mailto"] else "plaintext")
                    found[key]["sources"].append({"url": u, "via": via,
                                                  "checked_at": today})
        pages.append(rec)

    # 排序：同域优先 → 角色邮箱优先 → 字母序
    emails = sorted(found.values(),
                    key=lambda c: (not c["domain_match"], not c["role_local"],
                                   c["template_hint"], c["email"]))
    has_public = any(not e["template_hint"] for e in emails) or bool(phones or forms)
    status = ("not_searched" if not pages else "found" if has_public else
              "unavailable" if not any(p["http"] == 200 for p in pages) else "searched_not_found")
    return {
        "schema": "bdd-official-contacts/1",
        "site_domain": site_domain or None,
        "checked_at": today,
        "pages": pages,
        "emails": emails,
        "search_status": status, "coverage_complete": not queue,
        "unvisited_urls": queue, "phones": phones, "forms": forms, "team_pages": team_pages,
        "named_contact_candidates": people,
        "named_contacts_status": "requires_review" if team_pages else "unavailable" if any(
            any(t in p["url"] for t in ("team", "leadership", "management")) for p in pages) else "not_searched",
        "note": ("仅记录网页中真实出现（含 Cloudflare 解码）的邮箱；"
                 "未做任何猜测或拼接。个人 / 部门归属需人工按来源判定。"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", help="只给域名，按阶梯探测（如 example.com）")
    ap.add_argument("--url", help="只抓单个 URL（精确页）")
    ap.add_argument("--proxy", default=None, help="如 http://127.0.0.1:17891")
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--max-pages", type=int, default=16)
    args = ap.parse_args()

    if not args.domain and not args.url:
        print("[ERR] 需要 --domain 或 --url", file=sys.stderr)
        return 1

    if args.url:
        urls = [args.url]
        m = re.search(r"https?://([^/]+)", args.url)
        dom = m.group(1) if m else ""
    else:
        dom = args.domain.strip().lower().removeprefix("www.")
        base = f"https://{dom}"
        urls = [base + p for p in LADDER]

    res = run(urls, args.proxy, dom, max_pages=max(1, min(args.max_pages, 40)))

    print(f"站点域 : {res['site_domain']}　核验日期 : {res['checked_at']}")
    print("-" * 72)
    print(f"{'URL':<46}{'HTTP':<6}{'CF':<4}{'mailto':<7}{'明文'}")
    for p in res["pages"]:
        print(f"{p['url'][:45]:<46}{p['http']:<6}{p['cf']:<4}{p['mailto']:<7}{p['plain']}")
    print("-" * 72)
    if not res["emails"]:
        print("邮箱未发现；检索状态：" + res["search_status"] + "。仅在实际发现表单时记录表单，不推定存在。")
    else:
        print(f"找到 {len(res['emails'])} 个邮箱：")
        for c in res["emails"]:
            tags = []
            if c["domain_match"]:
                tags.append("同域")
            if c["role_local"]:
                tags.append("角色邮箱")
            if c["template_hint"]:
                tags.append("⚠️疑似模板")
            print(f"  · {c['email']:<34}{'/'.join(tags) or '—'}")
            for s in c["sources"][:3]:
                print(f"      ← {s['via']} · {s['url']} · {s['checked_at']}")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[JSON] {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
