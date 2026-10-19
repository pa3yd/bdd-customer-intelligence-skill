#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
archive_report.py — BDD Customer Intelligence Skill V1.1.5 归档层

职责：把一份已完成的客户背调报告（.md + .pdf）归档到本机「客户档案库」
      —— **档案库是唯一存放地**：归档成功后清理工作区根目录的那一份（V1.1.5）
============================================================

【归档层隔离要求 — 硬要求，不可绕过】
  本脚本**只做文件归位**：
    · 不解析、不生成、不改写报告内容
    · 不新增结论、不推断字段、不补全 Unknown
    · **不覆盖任何已有文件**（同名一律改期为时间 / 版本后缀）
    · 不联网
  Markdown 与 PDF 在归档前后逐字节一致（脚本内以 sha256 自校验）。

【V1.1.4 Customer Archive Patch（仅新增归档层）】
    · 归档根目录（**解析顺序固定**）：
        ① `--archive-root`
        ② **环境变量 `BDD_ARCHIVE_ROOT`**（推荐：一次设定，永久生效，不依赖对话记忆）
        ③ 回退：**当前工作区根** 下的 `customer-archive/`
           （工作区根 = 从 cwd / 报告目录向上找到的第一个含 `.workbuddy/` 或 `.git/` 的目录；
             跳过用户主目录；找不到则退回报告所在目录）
    · **归档根绝不允许落在 Skill 源码目录内** —— 命中即报错退出（exit 6），
      避免客户档案被误随 Skill 源码提交 / 推送。
    · 每个客户一个子目录，目录名 = 规范化公司名称
    · 客户识别：**官网域名优先 → 公司名精确 → 登记别名 → 名称核心词前缀**
      （最后一条专门解决「全称建档后再用缩写查询导致重复建档」；
        必须**整体前缀**成立，仅「共享首词」不合并，只提示人工确认）
    · 同客户 → 复用原目录，历史报告保留；同名冲突 → `_HHMM` → `_HHMM_v2` 递增
    · 每个客户目录内维护一个轻量标识文件 `_customer.json`（**保留**：客户名 / 别名 /
      域名 / 报告清单；非数据库、非业务模块；丢失可从目录内既有报告自动重建）
  **本层不参与任何判断。** 13 字段 / Path 规则 / Evidence Policy / 三页 PDF 全部未改。

【V1.1.5 Single-Home Patch —— 档案库为唯一存放地】
    · 归档成功后**清理源文件**（工作区根目录那一份），消除「根目录 + 档案库」两份重复；
    · **安全性质（四条，不可绕过）**：
        ① 只有**归档成功且逐字节 sha256 校验通过**之后，才允许删除源文件；
        ② 归档失败 / 目标已存在 / 校验不一致 → **一个源文件都不删**（除非已确认档案副本一致）；
        ③ 源文件本身位于档案库内 → **不删**（否则会毁掉档案副本）；
        ④ `--dry-run` 与 `--keep-source` → **不删**；
    · `--keep-source` 可退回旧行为（保留源文件，供调试 / 需要平铺视图时使用）；
    · 交付地址随之变更：**交付物在档案库客户目录内**，不再另留一份在工作区根。
    · 本 Patch **只改归档层**，渲染层（`render_pdf.py`）与判断层零改动。

用法：
  python archive_report.py <report.md> [--pdf <report.pdf>] [--archive-root <dir>]
                           [--company "<登记全称>"] [--domain <域名>] [--date YYYY-MM-DD]
                           [--time HHMM] [--force-new] [--keep-source] [--list] [--dry-run]

  默认：
    · `--pdf`  省略时取 `<report>.pdf`
    · `--company` 省略时从 Markdown 主卡「公司 Company」读取
    · `--domain`  省略时从 Markdown 内引用域名自动推断（标注 auto，可人工覆盖）
    · `--date`    省略时取报告文件名中的日期，取不到用当天
    · 归档成功后**清理源文件**；`--keep-source` 则不清理（退回 V1.1.4 行为）

退出码：0 正常（含 --list 与 --dry-run）/ 2 输入不存在 / 3 主卡读不出公司名
        / 4 归档失败 / 6 归档根落在 Skill 源码目录内（已拒绝）
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

# ------------------------------------------------------------------ 常量

ARCHIVE_DIRNAME = "customer-archive"
ARCHIVE_ENV = "BDD_ARCHIVE_ROOT"
INDEX_NAME = "_customer.json"
INDEX_SCHEMA = "bdd-customer-archive/1"
REPORT_SUFFIX = "_BDD_Intelligence_"

# Skill 包根目录（本脚本位于 <skill>/scripts/）—— 归档根**绝不允许**落在其内部
SKILL_ROOT = Path(__file__).resolve().parents[1]

# 工作区根标记：从 cwd / 报告目录向上找到的第一个含这些目录的父级即工作区根
WORKSPACE_MARKERS = (".workbuddy", ".git")
USER_HOME = Path.home().resolve()

# 公司名中的法务后缀 / 连接词 —— 仅用于**名称比对**，不用于目录命名
LEGAL_TOKENS = {
    "llc", "ltd", "limited", "inc", "incorporated", "corp", "corporation",
    "co", "company", "plc", "pvt", "private", "gmbh", "ag", "bv", "nv",
    "sa", "sas", "srl", "spa", "as", "asa", "ab", "oy", "oyj", "a", "s",
    "pte", "sdn", "bhd", "jsc", "ojsc", "cjsc", "kk", "group", "holdings",
    "holding", "international", "intl", "the", "and", "of", "for", "und",
}

# 域名黑名单：社交 / 媒体 / 聚合 / 工商查询 / 监管 / 学术 —— 不作为客户身份依据
BLOCK_DOMAINS = {
    "google.com", "google.co.in", "google.co.uk", "google.de", "google.ae",
    "bing.com", "baidu.com", "yahoo.com", "duckduckgo.com",
    "linkedin.com", "facebook.com", "instagram.com", "twitter.com", "x.com",
    "youtube.com", "tiktok.com", "medium.com", "reddit.com", "pinterest.com",
    "wikipedia.org", "wikimedia.org", "wikidata.org",
    "archive.org", "web.archive.org", "archive.ph",
    "bloomberg.com", "reuters.com", "ft.com", "wsj.com", "forbes.com",
    "economictimes.indiatimes.com", "timesofindia.indiatimes.com",
    "business-standard.com", "moneycontrol.com", "livemint.com",
    "thenationalnews.com", "gulfnews.com", "khaleejtimes.com", "arabianbusiness.com",
    "zawya.com", "constructionweekonline.com", "arabiantrade.com",
    "zaubacorp.com", "tofler.in", "thecompanycheck.com", "indiafilings.com",
    "dnb.com", "zoominfo.com", "crunchbase.com", "glassdoor.com", "indeed.com",
    "owler.com", "pitchbook.com", "apollo.io", "rocketreach.co",
    "amazon.com", "alibaba.com", "made-in-china.com", "europages.com",
    "tradeindia.com", "exportersindia.com", "indiamart.com", "globalspec.com",
    "researchgate.net", "sciencedirect.com", "springer.com", "mdpi.com",
    "ieee.org", "acs.org", "nature.com", "arxiv.org",
    "un.org", "worldbank.org", "unep.org", "who.int", "imf.org",
    "ec.europa.eu", "eea.europa.eu", "epa.gov", "osha.gov", "usgs.gov",
    "w3.org", "schema.org", "example.com",
    # 展会 / 贸易目录站：它们**托管多家公司的档案页**，一旦被当作客户身份键，
    # 会把同页出现的两家不同公司误判为同一客户 —— 必须排除。
    "globalwaterexpo.me", "globalwaterexpo.com", "10times.com",
    "expocheck.com", "eventseye.com", "tradefairdates.com",
}

# 监管 / 教育类域名后缀（正则，命中即排除）
BLOCK_DOMAIN_RE = re.compile(
    r"(?:^|\.)(?:gov|gob|gouv|govt|mil|edu|ac|sch|k12)\.[a-z]{2,}$"
    r"|\.(?:gov|mil|edu)$"
)

ILLEGAL_FS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED_NAMES = {
    "con", "prn", "aux", "nul",
    *[f"com{i}" for i in range(1, 10)],
    *[f"lpt{i}" for i in range(1, 10)],
}

MAX_FOLDER_LEN = 80
MAX_PATH_WARN = 235

UNKNOWN_COMPANY = {"", "unknown", "n/a", "none", "未知", "—", "-"}


# ------------------------------------------------------------------ 小工具

def log(msg=""):
    print(msg)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_domain(raw: str) -> str:
    """域名归一：去协议 / 路径 / 查询 / 账号 / 端口 / www。"""
    s = (raw or "").strip().lower()
    s = re.sub(r"^[a-z][a-z0-9+.\-]*://", "", s)
    s = re.split(r"[/?#]", s)[0]
    s = s.split("@")[-1]
    s = s.split(":")[0]
    s = s.strip().rstrip(".")
    if s.startswith("www."):
        s = s[4:]
    return s


def is_blocked_domain(d: str) -> bool:
    if not d or "." not in d:
        return True
    if d in BLOCK_DOMAINS:
        return True
    if BLOCK_DOMAIN_RE.search(d):
        return True
    for b in BLOCK_DOMAINS:
        if b and (d == b or d.endswith("." + b)):
            return True
    return False


def tokenize(name: str):
    return re.findall(r"[a-z0-9]+", (name or "").lower())


def core_tokens(name: str):
    """去掉法务后缀 / 连接词后的核心词列表（保序）。全为后缀时退回原 token。"""
    ts = tokenize(name)
    core = [t for t in ts if t not in LEGAL_TOKENS]
    return core or ts


def company_key(name: str) -> str:
    return " ".join(core_tokens(name))


def normalize_folder_name(name: str) -> str:
    """规范化公司名称 → 合法目录名。只做清洗，不改词、不删词。"""
    s = (name or "").strip()
    s = ILLEGAL_FS.sub("-", s)
    s = re.sub(r"\s+", " ", s)
    s = s.strip(" .-")
    if len(s) > MAX_FOLDER_LEN:
        cut = s[:MAX_FOLDER_LEN]
        if " " in cut:
            cut = cut[: cut.rfind(" ")]
        s = cut.strip(" .-")
    if s.lower() in RESERVED_NAMES:
        s += "_co"
    return s


def safe_base_from_stem(stem: str) -> str:
    s = ILLEGAL_FS.sub("-", stem)
    return re.sub(r"\s+", " ", s).strip(" .-")


# ------------------------------------------------------------------ Markdown 解析

CARD_ROW_RE = re.compile(r"^\|\s*\**\s*([^|*]+?)\s*\**\s*\|(.*)\|\s*$")
URL_RE = re.compile(r"https?://[^\s\)\]\>\"'，。；、]+", re.I)
VER_RE = re.compile(r"执行版本\s*[:：]\s*(.+?)\s*$", re.M)


def parse_md_company(md_text: str) -> str:
    """取主卡「公司 Company」登记全称（Display Label 或 Internal Key 均可）。"""
    for raw in md_text.splitlines():
        s = raw.strip()
        if not s.startswith("|"):
            continue
        m = CARD_ROW_RE.match(s)
        if not m:
            continue
        label = m.group(1).strip().strip("*").strip()
        if label in ("公司 Company", "公司", "Company", "Company Name"):
            val = m.group(2).strip().strip("*").strip()
            if not val:
                continue
            # 去掉**尾部**的（国家 / 地区）· 核实三态
            # ⚠️ 不得用「在第一个括号处切分」—— 登记全称本身可能含括号：
            #    「某集团公司全称（印度）· Verified」会被截成首段简称（实证 bug，
            #    且截断后的短名可能成为其它客户规范名的前缀 → 触发误并风险）。
            # 规则：① 先剥离尾部「（…）· <核实三态>」；② 否则仅剥离尾部**全角**括号组
            #      （报告约定用全角括号标国别；半角括号多为登记名的一部分）；③ 再按「·」「|」截断。
            _m = re.search(r"[（(][^（()）]*[)）]\s*(?:·\s*)?\**\s*"
                           r"(?:Partially\s+Verified|Verified|Unverified)",
                           val, re.I)
            if _m:
                val = val[: _m.start()]
            else:
                val = re.sub(r"\s*[（][^（）]*[）]\s*$", "", val)
            for sep in ("·", "|"):
                if sep in val:
                    val = val.split(sep)[0]
            val = val.strip().strip("*").strip()
            if val and val.lower() not in UNKNOWN_COMPANY:
                return val
    # 兜底：一级标题 `# {Company} · BDD Customer Intelligence`
    for raw in md_text.splitlines():
        s = raw.strip()
        if s.startswith("# "):
            t = s[2:].strip()
            t = re.split(r"\s*[·|｜]\s*", t)[0].strip()
            if t and "BDD" not in t:
                return t
    return ""


def parse_md_domains(md_text: str):
    """从报告内引用的 URL 推断客户官网域名（按出现次数排序，剔除聚合 / 监管站）。"""
    counts = {}
    for u in URL_RE.findall(md_text):
        d = norm_domain(u)
        if is_blocked_domain(d):
            continue
        counts[d] = counts.get(d, 0) + 1
    if not counts:
        return []
    return [d for d, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))][:3]


def parse_md_version(md_text: str) -> str:
    m = VER_RE.search(md_text)
    if not m:
        return ""
    v = re.search(r"V\d+(?:\.\d+)*", m.group(1))
    return v.group(0) if v else ""


def parse_md_date(name: str):
    m = re.search(r"(20\d{2})-(\d{2})-(\d{2})", name or "")
    return m.group(0) if m else ""


# ------------------------------------------------------------------ 档案索引

def load_index(folder: Path) -> dict:
    """读取 `_customer.json`；缺失 / 损坏则从目录内既有报告重建（自愈）。"""
    p = folder / INDEX_NAME
    if p.is_file():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("reports") is not None:
                return data
        except Exception:  # noqa: BLE001
            pass
    return rebuild_index(folder)


def rebuild_index(folder: Path) -> dict:
    """从目录内最新一份报告重建最小索引（不解析判断内容，只取公司名 / 域名 / 版本）。"""
    mds = sorted(folder.glob("*" + REPORT_SUFFIX + "*.md"),
                 key=lambda f: f.stat().st_mtime, reverse=True)
    if not mds:
        return {}
    newest = mds[0]
    text = newest.read_text(encoding="utf-8", errors="replace")
    company = parse_md_company(text) or folder.name
    reports = []
    for md in sorted(folder.glob("*" + REPORT_SUFFIX + "*.md")):
        pdf = md.with_suffix(".pdf")
        reports.append({
            "date": parse_md_date(md.name),
            "file": md.name,
            "pdf": pdf.name if pdf.is_file() else "",
            "sha256": "",
            "version": parse_md_version(text),
            "archived_at": "",
        })
    return {
        "schema": INDEX_SCHEMA,
        "company": company,
        "canonical_name": company,
        "aliases": [],
        "domains": parse_md_domains(text),
        "domain_source": "rebuilt",
        "folder": folder.name,
        "created": "",
        "updated": "",
        "reports": reports,
        "_rebuilt": True,
    }


def entry_identity(entry: dict, folder: Path):
    """索引 → 比对用身份（容错：字段缺失时用目录名 / 目录内报告兜底）。"""
    e = dict(entry or {})
    name = e.get("canonical_name") or e.get("company") or folder.name
    aliases = e.get("aliases") or []
    domains = e.get("domains") or []
    names = [name] + [a for a in aliases if a]
    cores = [core_tokens(n) for n in names]
    cores = [c for c in cores if c]
    return {
        "folder": folder,
        "name": name,
        "names": names,
        "domains": {norm_domain(d) for d in domains if norm_domain(d)},
        "cores": cores,
        # 规则④只用**规范名**核心词：别名（尤其 1 词缩写别名）不参与前缀比对，
        # 否则 "Acme" 这个别名会让 "Acme Green Water Ltd" 等异主体误并入。
        "canonical_core": core_tokens(name),
        "primary_core": cores[0] if cores else [],
        "entry": e,
    }


def scan_archive(root: Path):
    """扫描档案库里所有客户目录（跳过 `_` / `.` 开头的内部目录）。"""
    out = []
    if not root.is_dir():
        return out
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        if d.name.startswith("_") or d.name.startswith("."):
            continue
        out.append(entry_identity(load_index(d), d))
    return out


STRONG_MIN_CORE = 4


def match_customer(new_name: str, new_domains, entries):
    """客户身份比对。返回 (entry | None, matched_by, note)。

    优先级：domain > name（核心词全等）> alias > token-subset
    """
    nd = {norm_domain(d) for d in (new_domains or []) if norm_domain(d)}
    n_core = core_tokens(new_name)

    # ① 域名命中（最强）
    for e in entries:
        hit = nd & e["domains"]
        if hit:
            return e, "domain", "命中域名 " + ", ".join(sorted(hit))

    # ② 公司名核心词全等
    for e in entries:
        if company_key(new_name) and company_key(new_name) == company_key(e["name"]):
            return e, "name", "公司名一致"

    # ③ 登记别名命中
    for e in entries:
        for alias in e["names"]:
            if company_key(alias) and company_key(alias) == company_key(new_name):
                return e, "alias", f"命中别名「{alias}」"

    # ④ 核心词**前缀**包含（专治「全称建档 → 缩写再查」）
    #    ① 必须整体为前缀（Acme ⊂ Acme Waste Water Treatment），
    #       不得用「包含」—— 否则 "Dryrun Acme Ltd" 会被误并入 "Acme …" 档案；
    #    ② 只用**规范名**核心词比对，别名不参与（见 entry_identity 注释）。
    cands, near = [], []
    for e in entries:
        c = e["canonical_core"]
        if not c or not n_core:
            continue
        a, b = n_core, c
        if len(a) > len(b):
            a, b = b, a
        if len(a[0]) < STRONG_MIN_CORE:
            continue
        if b[:len(a)] == a:
            cands.append(e)
        elif a[0] == b[0]:
            near.append(e)
    if cands:
        cands.sort(key=lambda e: (-len(e["entry"].get("reports") or []), e["folder"].name))
        e = cands[0]
        c = e["canonical_core"]
        short, long_ = (n_core, c) if len(n_core) <= len(c) else (c, n_core)
        note = "核心词前缀：" + " ".join(short) + " ⊂ " + " ".join(long_)
        if len(cands) > 1:
            note += "（另有 " + str(len(cands) - 1) + " 个前缀相近档案，已取报告数最多者）"
        return e, "token-prefix", note

    if near:
        names = sorted({e["folder"].name for e in near})
        return None, "new", ("存在**共享首词**但不构成前缀的近似档案：" + "、".join(names)
                             + " —— 未自动合并，请人工确认是否同一客户")

    return None, "new", ""


# ------------------------------------------------------------------ 归档

def find_workspace_root(md_dir: Path):
    """定位「当前工作区」根：从 cwd → 报告目录向上找第一个含 `.workbuddy/` 或 `.git/` 的目录。

    跳过用户主目录（`~` 下也有 `.workbuddy/`，会误判）；找不到则退回报告所在目录。
    不扫描、不猜测既有 `customer-archive/` —— 路径来源必须确定。
    """
    for start in (Path.cwd().resolve(), md_dir.resolve()):
        for p in [start, *start.parents]:
            if p == USER_HOME:
                continue
            if any((p / m).exists() for m in WORKSPACE_MARKERS):
                return p
    return md_dir.resolve()


def inside_skill(p: Path) -> bool:
    r = p.resolve()
    return r == SKILL_ROOT or SKILL_ROOT in r.parents


def resolve_archive_root(cli_root, md_dir: Path):
    """归档根解析：`--archive-root` > `$BDD_ARCHIVE_ROOT` > 当前工作区 `customer-archive/`。

    **任何来源命中 Skill 源码目录一律拒绝**（返回 None + 原因），
    防止客户档案被误随 Skill 源码提交 / 推送。
    返回 (root | None, 来源说明 | 拒绝原因)。
    """
    if cli_root:
        root, src = Path(cli_root).expanduser(), "--archive-root 参数"
    else:
        env = os.environ.get(ARCHIVE_ENV, "").strip()
        if env:
            root, src = Path(env).expanduser(), "$" + ARCHIVE_ENV + " 环境变量"
        else:
            root = find_workspace_root(md_dir) / ARCHIVE_DIRNAME
            src = "当前工作区（未设 $" + ARCHIVE_ENV + "）"
    root = root.resolve()
    if inside_skill(root):
        return None, (f"归档根「{root}」落在 Skill 源码目录内（{SKILL_ROOT}）—— 已拒绝。\n"
                      f"       请设置环境变量 {ARCHIVE_ENV} 或改用 --archive-root 指向 Skill 目录之外。")
    return root, src


def unique_folder(root: Path, name: str):
    """客户目录名唯一化 —— 绝不写进既有客户目录。"""
    f = root / name
    if not f.exists():
        return f, False
    try:
        if not any(f.iterdir()):
            return f, False
    except OSError:
        pass
    n = 2
    while True:
        cand = root / f"{name} ({n})"
        if not cand.exists():
            return cand, True
        n += 1
        if n > 99:
            raise RuntimeError("同名客户目录过多（>99），请人工整理档案库。")


def unique_pair(folder: Path, base: str, hhmm: str):
    """为 .md / .pdf 计算**成对**的不冲突基名。永不覆盖已有文件。"""
    def taken(b):
        return any((folder / (b + ext)).exists() for ext in (".md", ".pdf"))

    if not taken(base):
        return base, "original"
    cand = f"{base}_{hhmm}"
    if not taken(cand):
        return cand, "time"
    n = 2
    while True:
        cand = f"{base}_{hhmm}_v{n}"
        if not taken(cand):
            return cand, "version"
        n += 1
        if n > 99:
            raise RuntimeError("同名版本过多（>99），请人工整理档案目录。")


def safe_cleanup_source(src: Path, archive_root: Path, keep: bool):
    """归档成功后的源文件清理（V1.1.5）。

    **调用方必须先确认：该内容已存在于档案库、且逐字节一致。**

    四条护栏（不可绕过）：
      ① `keep=True`（--keep-source）→ 不删
      ② 源文件位于档案库内 → 不删（否则会毁掉档案副本）
      ③ 源文件不存在 → 什么都不做
      ④ 删除失败 → 只告警，不影响归档结果

    返回 (是否已删除, 说明)。
    """
    if keep:
        return False, "保留（--keep-source）"
    if not src.is_file():
        return False, "源文件已不存在"
    try:
        r = src.resolve()
        if r == archive_root or archive_root in r.parents:
            return False, "源文件位于档案库内，未删除"
    except OSError:
        pass
    try:
        src.unlink()
        return True, "已清理"
    except OSError as e:  # noqa: BLE001
        return False, f"清理失败：{e}"


def archive(md_path: Path, pdf_path, cli_company, cli_domain, cli_date,
            cli_time, cli_root, force_new, dry_run, keep_source=False):
    if not md_path.is_file():
        log(f"[FAIL] 报告不存在：{md_path}")
        return 2

    md_text = md_path.read_text(encoding="utf-8", errors="replace")

    # ---- 客户身份
    company = (cli_company or "").strip() or parse_md_company(md_text)
    if not company or company.lower() in UNKNOWN_COMPANY:
        log("[FAIL] 读不到公司名（主卡「公司 Company」为空或 Unknown）。")
        log("       请用 --company \"<登记全称>\" 显式指定后重试。")
        return 3
    if cli_domain:
        domains = [norm_domain(cli_domain)]
        domain_src = "manual"
    else:
        domains = parse_md_domains(md_text)
        domain_src = "auto" if domains else "none"

    # ---- 日期 / 时间
    date = (cli_date or "").strip() or parse_md_date(md_path.name) \
        or dt.date.today().isoformat()
    hhmm = (cli_time or "").strip() or dt.datetime.now().strftime("%H%M")

    # ---- PDF 侧
    if pdf_path is None:
        pdf_path = md_path.with_suffix(".pdf")
    pdf_path = Path(pdf_path)
    pdf_ok = pdf_path.is_file()

    # ---- 归档根 + 客户比对
    root, root_src = resolve_archive_root(cli_root, md_path.parent)
    if root is None:
        log("=" * 66)
        log("BDD Customer Intelligence · 客户档案归档（V1.1.5）")
        log("=" * 66)
        log(f"[FAIL] {root_src}")
        log("STATUS             : FAIL（未写入任何文件）")
        return 6
    entries = scan_archive(root)
    hit, matched_by, note = (None, "new", "") if force_new \
        else match_customer(company, domains, entries)

    log("=" * 66)
    log("BDD Customer Intelligence · 客户档案归档（V1.1.5）")
    log("=" * 66)
    log(f"输入报告           : {md_path.name}")
    log(f"客户（登记全称）   : {company}")
    log(f"官网域名           : {', '.join(domains) if domains else '—'}"
        + (f"  [{domain_src}]" if domains else ""))
    log(f"报告日期           : {date}")
    log(f"归档根目录         : {root}")
    log(f"归档根来源         : {root_src}")
    log(f"匹配方式           : {matched_by}" + (f" —— {note}" if note else ""))
    log(f"源文件处理         : " + ("保留（--keep-source）" if keep_source
                                    else "归档成功后清理（档案库为唯一存放地）"))

    if hit is None:
        wanted = normalize_folder_name(company)
        folder, renamed = unique_folder(root, wanted)
        new_folder = True
        entry = {}
        existing_reports = []
        log("客户身份           : 新客户 → 新建档案目录")
        if note:
            log(f"[HINT] {note}")
        if renamed:
            log(f"[WARN] 目录名「{wanted}」已被占用，本次改用「{folder.name}」"
                "（若非同一客户请忽略；若为同一客户，请检查既有档案索引）")
    else:
        folder = hit["folder"]
        new_folder = False
        entry = hit["entry"]
        existing_reports = entry.get("reports") or []
        log(f"客户身份           : 已有档案 → 复用 {folder.name}")
        log(f"历史报告           : {len(existing_reports)} 份")

    # ---- 同内容去重（幂等：重复归档不产生冗余）
    md_sha = sha256_file(md_path)
    dup = next((r for r in existing_reports if r.get("sha256") == md_sha), None)
    if dup:
        pdf_name = dup.get("pdf") or ""
        if pdf_name and not (folder / pdf_name).is_file() and pdf_ok:
            if not dry_run:
                folder.mkdir(parents=True, exist_ok=True)
                shutil.copy2(pdf_path, folder / pdf_name)
            log(f"内容去重           : 报告已归档（{dup.get('file')}），补入缺失的 PDF")
        else:
            log(f"内容去重           : 报告已归档（{dup.get('file')}），跳过，不重复入库")
        if dry_run:
            log("DRY-RUN            : 未写入任何文件")
        else:
            # V1.1.5：源文件清理 —— 仅当档案库副本**逐字节一致**时才删
            twins = [(md_path, folder / (dup.get("file") or ""))]
            if pdf_name:
                twins.append((pdf_path, folder / pdf_name))
            for src, twin in twins:
                if not src.is_file():
                    continue
                if not twin.is_file() or sha256_file(src) != sha256_file(twin):
                    log(f"[WARN] 档案副本未通过一致性校验，保留源文件：{src.name}")
                    continue
                done, why = safe_cleanup_source(src, root, keep_source)
                log(f"源文件处理         : {src.name} → {'已清理' if done else why}")
        log(f"档案保存位置       : {folder}")
        log("STATUS             : PASS（无新增文件）")
        return 0

    # ---- 成对命名（永不覆盖）
    if REPORT_SUFFIX in md_path.stem:
        base = safe_base_from_stem(md_path.stem)
    else:
        base = f"{safe_base_from_stem(normalize_folder_name(company))}{REPORT_SUFFIX}{date}"
    base, suffix_kind = unique_pair(folder, base, hhmm)

    md_dst = folder / (base + ".md")
    pdf_dst = folder / (base + ".pdf")

    long_path = len(str(md_dst)) > MAX_PATH_WARN

    log(f"归档文件名         : {base}.md" + (" / " + base + ".pdf" if pdf_ok else "")
        + (f"  [{suffix_kind}]" if suffix_kind != "original" else "  [首份]"))
    if long_path:
        log("[WARN] 归档路径较长，Windows 上可能触及 260 字符上限。")

    if dry_run:
        log("DRY-RUN            : 未写入任何文件")
        log(f"档案保存位置       : {folder}")
        log("STATUS             : PASS（试运行）")
        return 0

    # ---- 写入（先建目录，再逐文件复制 + 校验）
    #     注意：任何一条 return 4 都发生在清理之前 —— 归档没成功就一个源文件都不删
    copied = []
    try:
        folder.mkdir(parents=True, exist_ok=True)
        for src, dst in ((md_path, md_dst), (pdf_path, pdf_dst)):
            if not src.is_file():
                continue
            if dst.exists():
                log(f"[FAIL] 目标已存在，拒绝覆盖：{dst}")
                log("       源文件未做任何改动。")
                return 4
            shutil.copy2(src, dst)
            if sha256_file(src) != sha256_file(dst):
                log(f"[FAIL] 复制后校验失败：{dst}")
                log("       源文件未做任何改动。")
                return 4
            copied.append(src)
    except OSError as e:
        log(f"[FAIL] 归档写入失败：{e}")
        log("       源文件未做任何改动。")
        return 4

    # ---- 更新客户标识文件
    now = dt.datetime.now().replace(microsecond=0).isoformat()
    entry.setdefault("schema", INDEX_SCHEMA)
    entry["folder"] = folder.name
    entry["reports"] = existing_reports
    entry["created"] = entry.get("created") or now
    entry["updated"] = now
    entry["company"] = entry.get("company") or company

    # 规范名：取核心词更多的那一个（目录名不动，避免破坏既有路径）
    canon = entry.get("canonical_name") or company
    if len(core_tokens(company)) > len(core_tokens(canon)):
        canon = company
    entry["canonical_name"] = canon

    # 别名：核心词与规范名 / 既有别名都不同的写法，登记为别名（专治缩写重复建档）
    known_keys = {company_key(canon)} | {company_key(a) for a in (entry.get("aliases") or [])}
    if company_key(company) not in known_keys and company not in (entry.get("aliases") or []):
        entry.setdefault("aliases", []).append(company)
    for d in domains:
        if d and d not in entry.setdefault("domains", []):
            entry["domains"].append(d)
    if cli_domain:
        entry["domain_source"] = "manual"
    else:
        entry.setdefault("domain_source", domain_src)
    entry["reports"].append({
        "date": date,
        "file": md_dst.name,
        "pdf": pdf_dst.name if pdf_dst.is_file() else "",
        "sha256": md_sha,
        "version": parse_md_version(md_text),
        "archived_at": now,
    })
    entry.pop("_rebuilt", None)
    try:
        (folder / INDEX_NAME).write_text(
            json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as e:
        log(f"[WARN] 客户标识文件写入失败（不影响报告归档）：{e}")

    # ---- V1.1.5：归档成功 + 逐字节校验通过 → 清理源文件（档案库为唯一存放地）
    cleaned, kept = 0, []
    for src in copied:
        done, why = safe_cleanup_source(src, root, keep_source)
        if done:
            cleaned += 1
        else:
            kept.append((src.name, why))
        log(f"源文件处理         : {src.name} → {'已清理' if done else why}")

    # ---- 结果
    log("-" * 66)
    log("归档文件           :")
    for f in sorted(folder.iterdir()):
        if f.is_file():
            mark = "  ← 本次" if f.name in (md_dst.name, pdf_dst.name) else ""
            log(f"  {f.name}  ({f.stat().st_size / 1024:.1f} KB){mark}")
    log("-" * 66)
    log(f"本次新增           : {md_dst.name}" + (f" + {pdf_dst.name}" if pdf_dst.is_file() else "（未找到 PDF）"))
    if not pdf_ok:
        log("[WARN] 未找到配套 PDF，本次只归档了 Markdown。")
    log(f"历史 + 本次总计    : {len(entry['reports'])} 份报告")
    log(f"源文件清理         : {cleaned} 个"
        + ("（工作区根目录已无重复文件）" if cleaned and not kept else ""))
    for nm, why in kept:
        log(f"                     · {nm} 未清理：{why}")
    log(f"交付位置           : {folder}" + ("（档案库为唯一存放地）" if cleaned and not keep_source else ""))
    log(f"档案保存位置       : {folder}")
    log("STATUS             : PASS")
    if new_folder:
        log("说明               : 已新建客户档案目录（规范化公司名称命名）")
    return 0


# ------------------------------------------------------------------ 列出档案库

def list_archive(root: Path, root_src: str = ""):
    entries = scan_archive(root)
    log("=" * 66)
    log("BDD 客户档案库 · 目录清单")
    log("=" * 66)
    log(f"归档根目录         : {root}")
    if root_src:
        log(f"归档根来源         : {root_src}")
    if not entries:
        log("（空）")
        return 0
    log(f"客户数             : {len(entries)}")
    log("-" * 66)
    total = 0
    for e in entries:
        reps = e["entry"].get("reports") or []
        total += len(reps)
        log(f"· {e['name']}")
        log(f"    目录 : {e['folder'].name}"
            + ("  [索引缺失，已由报告重建]" if e["entry"].get("_rebuilt") else ""))
        log(f"    域名 : {', '.join(sorted(e['domains'])) or '—'}")
        log(f"    报告 : {len(reps)} 份"
            + ("　" + ", ".join(r.get('date') or '?' for r in reps) if reps else ""))
    log("-" * 66)
    log(f"报告总数           : {total}")
    return 0


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(
        description="BDD Customer Intelligence — 客户档案归档（V1.1.4）")
    ap.add_argument("input", nargs="?", help="报告 Markdown 路径")
    ap.add_argument("--pdf", help="配套 PDF 路径（默认同名 .pdf）")
    ap.add_argument("--archive-root", help="归档根目录（默认 customer-archive/）")
    ap.add_argument("--company", help="客户登记全称（默认从主卡读取）")
    ap.add_argument("--domain", help="客户官网域名（默认从报告内引用推断）")
    ap.add_argument("--date", help="报告日期 YYYY-MM-DD（默认取文件名 / 当天）")
    ap.add_argument("--time", help="同名冲突时的时间后缀 HHMM（默认当前时间）")
    ap.add_argument("--force-new", action="store_true", help="忽略既有档案，强制新建客户目录")
    ap.add_argument("--keep-source", action="store_true",
                    help="归档后保留源文件（退回 V1.1.4 行为；默认归档成功后清理源文件）")
    ap.add_argument("--list", action="store_true", help="列出档案库目录后退出")
    ap.add_argument("--dry-run", action="store_true", help="只演算不写文件")
    args = ap.parse_args()

    if args.list:
        root, src = resolve_archive_root(args.archive_root, Path.cwd())
        if root is None:
            log(f"[FAIL] {src}")
            return 6
        return list_archive(root, src)

    if not args.input:
        ap.print_help()
        return 2

    return archive(
        md_path=Path(args.input).expanduser().resolve(),
        pdf_path=Path(args.pdf).expanduser().resolve() if args.pdf else None,
        cli_company=args.company,
        cli_domain=args.domain,
        cli_date=args.date,
        cli_time=args.time,
        cli_root=args.archive_root,
        force_new=args.force_new,
        dry_run=args.dry_run,
        keep_source=args.keep_source,
    )


if __name__ == "__main__":
    sys.exit(main())
