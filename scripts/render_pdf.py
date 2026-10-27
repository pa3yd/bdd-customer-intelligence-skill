#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_pdf.py — BDD Customer Intelligence Skill V1.1.4 渲染层

职责：Markdown → HTML → PDF（业务员版三页）
============================================================

【渲染层隔离要求 — 硬要求，不可绕过】
  本脚本**只做格式转换**：
    · 不新增结论
    · 不推断缺失字段
    · 不改写 / 润色任何文字
    · 不重新计算任何等级或颜色
    · 不补全 Unknown
  颜色映射为**查表**（映射表来源：references/output-visual-rules.md），
  表内无匹配时输出中性色，**不得猜测**。
  Markdown 为权威版本；两者冲突时以 Markdown 为准。

【V1.1.1 Presentation Patch】
  仅改展示：13 个 Internal Key 不变，新增 Display Label 别名表（仅用于还原内部标识）；
  主卡按四组 WHO / WHY / WHERE·WHO / ACTION 呈现；
  `Sales Conclusion` 渲染为第一页结论卡。

【V1.1.2 UI Refinement Patch】
  仅改 Presentation / PDF Rendering / Output Visual Layer：
    · 字段列浅灰蓝底 + 固定 20% 宽 + 垂直居中；短状态渲染为 Badge（不整行染色）
    · Section Header 带编号（01~04）
    · 长字段 `⟪P2⟫` 拆分：Page 1 只显示摘要，完整内容进 Page 2
    · 结论卡强化（中文大号 + 英文副标题 + 左侧色条）
    · Page 3 由 7 列表格改为 **Evidence Card**（只展示 High / Medium 前 6~10 条）
  **本层不参与任何判断。** 完整 Evidence 仍保留在 Markdown，不删除。

【V1.1.3 Sales Usability Patch】
  仅改 PDF 第 2 / 3 页，**Page 1 完全不变**：
    · Page 2：`字段详细内容` 表 → **SALES INTELLIGENCE ｜开发情报**（5 张销售信息卡：
      Why BDD / Current Treatment / Priority Site / Who to Contact / What to Verify）
    · Page 3：Evidence 卡片改为 **KEY EVIDENCE ｜关键依据**（6~8 条，主题 / 简洁事实 / Source；
      **不在 PDF 显示 FACT·INFERENCE·Confidence·Decision Impact 等审计术语**）
    · 审计 / 边界信息（可溯源率 · 类型定义 · 实体排除 · 来源冲突 · 边界声明等）
      只在 Markdown 的「附录 B」保留，**不进入业务 PDF**
    · Markdown 附录 A 的完整 Evidence **一字不删**（含 FACT/INFERENCE/UNKNOWN/Confidence/
      Decision Impact/Source）
  渲染层仍**只做版式转换与字段搬运**，不新增、不推断、不改写、不润色任何内容。

【V1.1.4 Customer Archive Patch】
  本 Patch **未修改渲染层任何逻辑**：客户档案归档由独立脚本 `scripts/archive_report.py` 承担，
  不并入本脚本（保持「渲染层只做格式转换」的隔离声明）。
  三页版式、颜色映射表、字段搬运规则与 V1.1.3 **完全一致**。

  渲染前必须通过**主卡 13 字段完整性校验**；缺任一字段 → 报错退出，不生成 PDF。

用法：
  python render_pdf.py <input.md> [--out <output.pdf>] [--html <output.html>] [--single]
    --single   输出完整单页版（不分页），用于内部复核

依赖：Google Chrome / Microsoft Edge（headless）
"""

import argparse
import html as html_mod
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import decision_engine

# ---------------------------------------------------------------- 主卡 13 字段
# 来源：assets/output-card-template.md（V1.1 / V1.1.1）
# **Internal Key，保持不变。Display Label 见 FIELD_ALIASES。**
REQUIRED_FIELDS = [
    "Company",
    "Country",
    "What They Do",
    "Customer Type",
    "Industry Match",
    "Current Wastewater Treatment / Technology",
    "BDD Opportunity",
    "Demand Status",
    "Priority Site",
    "Who to Contact",
    "What Is Missing",
    "Next Action",
    "Sales Conclusion",
]

# --------------------------------------------- V1.1.1 Display Label → Internal Key
# 仅用于把主卡显示标签还原为内部标识。Internal Key 为唯一权威标识。
FIELD_ALIASES = {
    "公司 Company": "Company",
    "国家 Country": "Country",
    "主营业务 Business": "What They Do",
    "客户类型 Customer Type": "Customer Type",
    "行业匹配 Industry Match": "Industry Match",
    "现有废水处理 Current Treatment": "Current Wastewater Treatment / Technology",
    "BDD机会 BDD Opportunity": "BDD Opportunity",
    "需求状态 Demand Status": "Demand Status",
    "优先厂区 Priority Site": "Priority Site",
    "关键联系人 Contact": "Who to Contact",
    "待确认信息 Missing Info": "What Is Missing",
    "下一步 Next Action": "Next Action",
    "开发建议 Sales Conclusion": "Sales Conclusion",
}

# 结论卡标记（marker 原文属该字段显示标签，不改写）
CONCLUSION_MARK = "开发建议 Sales Conclusion"

# 四组标题识别（版式识别，非内容规则）
GROUP_TITLE_RE = re.compile(
    r"^(?:\d{2}\s+)?(WHO|WHY|WHERE\s*/\s*WHO|ACTION)\s*[·｜]")

# --------------------------------------- Current Treatment 四态（查表，不推断）
# 来源：references/output-visual-rules.md 第二部分第三节 / 第三部分第三节
CURRENT_TREATMENT_STATES = ("Confirmed", "Partial", "Planned", "Unknown")

# ------------------------------------------ V1.1.2 Badge 映射（查表，不推断）
# 来源：references/output-visual-rules.md 第三部分第二节
# 仅**精确匹配**短状态词才渲染 Badge；未命中一律原样输出纯文本。
BADGE_WORDS = {
    # 绿 · 正面
    "High": "badge-ok",
    "Target": "badge-ok",
    "Confirmed": "badge-ok",
    "Strong Signal": "badge-ok",
    "建议开发": "badge-ok",
    "建议重点开发": "badge-ok",
    # 黄 · 待验证
    "Medium": "badge-warn",
    "Potential": "badge-warn",
    "Partial": "badge-warn",
    "建议先验证": "badge-warn",
    # 红 · 风险 / 负面（**只用于风险、冲突、负面**）
    "Risk": "badge-bad",
    "Conflict": "badge-bad",
    "Low": "badge-bad",
    "Weak": "badge-bad",
    "Outside": "badge-bad",
    "暂不优先": "badge-bad",
    # 灰 · 未知
    "Unknown": "badge-unk",
    "信息不足": "badge-unk",
    # 蓝 · 中性事实
    "Adjacent": "badge-info",
    "Planned": "badge-info",
    "Neutral Facts": "badge-info",
}

# Current Treatment 四态中文显示（状态仍由 Evidence 支撑，本表只加中文）
CT_CN_STATES = (
    ("🟢 已确认 Confirmed", "badge-ok"),
    ("🟡 部分确认 Partial", "badge-warn"),
    ("🔵 规划中 Planned", "badge-info"),
    ("⚪ 未知 Unknown", "badge-unk"),
)

# 五色点 → Badge 类（用于 `{色点} {状态词}` 形式）
DOT_TO_BADGE = {
    "🟢": "badge-ok",
    "🟡": "badge-warn",
    "🔴": "badge-bad",
    "⚪": "badge-unk",
    "🔵": "badge-info",
}

# Sales Conclusion 英文副标题（展示层映射，不改变判断结果）
CONCL_EN = {
    "建议重点开发": "Recommended — Priority Development",
    "建议开发": "Recommended to Develop",
    "建议先验证": "Verify Before Pursuing",
    "暂不优先": "Low Priority",
    "信息不足，暂缓判断": "Insufficient Information",
}

# 中文结论 → 卡片语义类
CONCL_CLS = {
    "建议重点开发": "ok",
    "建议开发": "ok",
    "建议先验证": "warn",
    "暂不优先": "bad",
    "信息不足，暂缓判断": "unk",
}

# Page 1 → Page 2 的版式标记（不是判断标记）
P2_MARK = "⟪P2⟫"

# 长字段（会被 `⟪P2⟫` 拆分压缩的字段）—— Internal Key
# 说明：V1.1.3 起 Page 2 显示字段**完整原文**，本表仅作参考登记（供审计对照）。
LONG_FIELDS = [
    "Current Wastewater Treatment / Technology",
    "Priority Site",
    "Who to Contact",
    "What Is Missing",
]

# ---- V1.2.1-layout（2026-10-19）：Page 1 确定性自动摘要 --------------------
# 背景：`⟪P2⟫` 依赖模型手工放置 + 字数试错（实测 Technoacque 重跑 5 渲 4 溢出）。
# 本补丁把「P1 摘要放多少字」从模型判断改为**渲染器确定性规则**：
#   渲染 → 测 P1 是否溢出 → 按预算档位自动收紧长字段摘要 → 重渲（本地循环，
#   零模型调用、零积分）。MD 原文一字不删（P2 卡仍显示完整原文）。
# 仅对 AUTO_SPLIT_FIELDS 白名单生效；评级 / 身份 / 结论字段**永不切分**。
AUTO_SPLIT_FIELDS = {
    "Current Wastewater Treatment / Technology",
    "Priority Site",
    "Who to Contact",
    "What Is Missing",
    "Next Action",
    "What They Do",
}
# 预算档位（P1 摘要字符数）：None=不干预（尊重手工 ⟪P2⟫）→ 逐档收紧
AUTO_SUMMARY_TIERS = (120, 88, 60)
MIN_SUMMARY_KEEP = 40          # 最短保留（保护 🟢/🟡 等评级头 + 字段类型）
AUTO_CUT_CHARS = ("；", "。", "！", "？", "　", "）", "，", " ")
AUTO_SUMMARY_BUDGET = None      # main() 溢出循环写入；None = 不干预
AUTO_CUT_LOG = []               # 本轮渲染实际被自动收紧的字段（报告用）


def auto_summary(text: str, keep: int) -> str:
    """确定性截短：在 [MIN_SUMMARY_KEEP, keep] 窗口内找最后一个**优选标点**切开。

    不在标点边界时硬切并加「……」。纯字符串操作，无模型参与。
    """
    if len(text) <= keep:
        return text
    lo = MIN_SUMMARY_KEEP
    for cc in AUTO_CUT_CHARS:
        idx = text.rfind(cc, lo, keep)
        if idx is not None and idx > lo:
            return text[: idx + 1].rstrip()
    return text[:keep].rstrip() + "……"

# Key Evidence 展示条数与上限（V1.1.3：要求 6 ~ 8 条）
EVIDENCE_CARD_MIN = 6
EVIDENCE_CARD_LIMIT = 8

# ---- V1.1.3：业务 PDF / Markdown 审计区的切分标记 ----
# 以下章节属**开发 / 审计信息**，只在 Markdown 保留，不进入业务 PDF：
#   附录 B（可溯源率 / 类型定义 / 实体排除 / 来源冲突 …）、边界声明
AUDIT_SECTION_RE = re.compile(r"^#{1,6}\s+(?:附录 B|边界声明)\b", re.M)

# ---- V1.1.3：Page 2「SALES INTELLIGENCE｜开发情报」五张销售信息卡 ----
# (卡片标题, 数据来源)
#   数据来源为 Internal Key → 取该字段**完整原文**（Page 1 摘要 + 被压缩部分）
#   数据来源为 None    → 取 Markdown「BDD Opportunity 判定依据 + Demand Status 明细」两块
PAGE2_CARDS = (
    ("Why BDD｜为什么和 BDD 有关", None),
    ("Current Treatment｜目前怎么处理", "Current Wastewater Treatment / Technology"),
    ("Priority Site｜优先厂区", "Priority Site"),
    ("Who to Contact｜找谁", "Who to Contact"),
    ("What to Verify｜还要确认什么", "What Is Missing"),
    # V1.2.1-audit（2026-10-19）：风险块此前不上业务 PDF ⇒ 补第 6 张卡（纯搬运「**风险**」小节）
    ("Risk & Watch｜风险与观察", "__SECTION__:风险"),
)

# Page 2 信息卡的数据来源小节（Markdown 加粗小标题 → 原样搬运）
PAGE2_SOURCES = ("BDD Opportunity 判定依据", "Demand Status 明细")

# Internal Key → Display Label（Page 2「字段完整内容」用）
KEY_TO_LABEL = {v: k for k, v in FIELD_ALIASES.items()}

# Display Label → (中文, 英文) 展示拆分（V1.1.2 字段名分字重；文字不改）
LABEL_SPLIT = {
    "公司 Company": ("公司", "Company"),
    "国家 Country": ("国家", "Country"),
    "主营业务 Business": ("主营业务", "Business"),
    "客户类型 Customer Type": ("客户类型", "Customer Type"),
    "行业匹配 Industry Match": ("行业匹配", "Industry Match"),
    "BDD机会 BDD Opportunity": ("BDD机会", "BDD Opportunity"),
    "需求状态 Demand Status": ("需求状态", "Demand Status"),
    "现有废水处理 Current Treatment": ("现有废水处理", "Current Treatment"),
    "优先厂区 Priority Site": ("优先厂区", "Priority Site"),
    "关键联系人 Contact": ("关键联系人", "Contact"),
    "待确认信息 Missing Info": ("待确认信息", "Missing Info"),
    "下一步 Next Action": ("下一步", "Next Action"),
    "开发建议 Sales Conclusion": ("开发建议", "Sales Conclusion"),
}

# ------------------------------------------------- 颜色语义映射表（查表，不推断）
# 来源：references/output-visual-rules.md
COLOR_TABLE = {
    "🟢": "ok",      # Confirmed / Positive / High relevance
    "🟡": "warn",    # Potential / Needs validation
    "🔴": "bad",     # Risk / Negative / Conflict
    "⚪": "unk",     # Unknown
    "🔵": "info",    # Neutral facts
}

COLOR_LEGEND = (
    ("ok", "🟢 已确认 / 正面 / 高相关"),
    ("warn", "🟡 待验证 / 潜力"),
    ("bad", "🔴 风险 / 负面 / 冲突"),
    ("unk", "⚪ 未知"),
    ("info", "🔵 中性事实"),
)

# ---------------------------------------------------------------- Markdown 子集解析


def esc(t: str) -> str:
    return html_mod.escape(t, quote=False)


def normalize_field(label: str) -> str:
    """Display Label → Internal Key。映射失败返回原文（兼容 V1.1 旧格式）。"""
    t = re.sub(r"\*\*", "", label).strip()
    return FIELD_ALIASES.get(t, t)


def colorize(text: str) -> str:
    """把五色 emoji 替换为色块 span。仅查表，不推断。"""
    out = esc(text)
    for emoji, cls in COLOR_TABLE.items():
        if emoji in out:
            out = out.replace(emoji, f'<span class="dot {cls}"></span>')
    return out


def inline(text: str) -> str:
    """行内元素：颜色 → 显式换行 → 粗体 → 行内代码 → 链接。顺序不可颠倒。"""
    t = colorize(text)
    # V1.1.1：Markdown 中显式书写的 `<br>` / `<br/>` 生效为换行（纯格式转换）
    t = t.replace("&lt;br&gt;", "<br/>").replace("&lt;br/&gt;", "<br/>")
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


# ------------------------------------------------------------- V1.1.2 Badge

def _badge_hold(badges, cls, txt, tail=""):
    badges.append((cls, txt))
    return f"\x01{len(badges) - 1}\x01" + tail


def extract_badges(value: str, badges):
    """把单元格开头的短状态渲染为占位符。**只查表，未命中即原样返回。**

    匹配优先级：
      ① Current Treatment 四态中文（`🟢 已确认 Confirmed`）
      ② `{色点} {状态词}`（`🟢 High · …`）
      ③ 整串即状态词（`Potential`）
    """
    v = value.strip()

    # ① 四态
    for state, cls in CT_CN_STATES:
        if v.startswith(state):
            return _badge_hold(badges, cls, state, v[len(state):])

    # ② `{色点} {状态词}`
    m = re.match(r"^(🟢|🟡|🔴|⚪|🔵)\s*(.+)$", v)
    if m:
        dot, rest = m.group(1), m.group(2).strip()
        for word in sorted(BADGE_WORDS, key=len, reverse=True):
            if rest == word or re.match(
                r"^" + re.escape(word) + r"(?![A-Za-z])", rest
            ):
                cls = BADGE_WORDS[word] or DOT_TO_BADGE[dot]
                # 状态词后若紧接 `（…）`，括号内容属补充说明，留在 Badge 外
                return _badge_hold(badges, cls, word, rest[len(word):])

    # ③ 整串即状态词（无颜色点）
    plain = re.sub(r"\*\*", "", v).strip()
    if plain in BADGE_WORDS:
        return _badge_hold(badges, BADGE_WORDS[plain], plain)

    return value


def cell_html(value: str) -> str:
    """表格单元格渲染：Badge 提取 → 行内格式 → Badge 还原。"""
    badges = []
    staged = extract_badges(value, badges)
    t = inline(staged)
    for i, (cls, txt) in enumerate(badges):
        t = t.replace(f"\x01{i}\x01",
                      f'<span class="badge {cls}">{esc(txt)}</span>')
    return t


def field_label_html(label: str) -> str:
    """字段名渲染：**中文加粗、英文正常字重**（V1.1.2 展示层拆分，文字不改）。"""
    t = re.sub(r"\*\*", "", label).strip()
    if t in LABEL_SPLIT:
        cn, en = LABEL_SPLIT[t]
        out = f'<span class="fld-cn">{esc(cn)}</span>'
        if en:
            out += f' <span class="fld-en">{esc(en)}</span>'
        return out
    return f'<span class="fld-cn">{esc(t)}</span>'


CELL_PIPE_PROT = "\x00P\x00"


def split_row(line: str):
    """拆分表格行。

    V1.1.1：先保护转义竖线 `\\|`，避免 `+|`（复合机会类型分隔符）被误拆成两列 ——
    这是纯排版修复，不改变任何单元格文本。
    """
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    s = s.replace("\\|", CELL_PIPE_PROT)
    return [c.strip().replace(CELL_PIPE_PROT, "|") for c in s.split("|")]


def is_table_sep(line: str) -> bool:
    s = line.strip()
    if not s.startswith("|"):
        return False
    return bool(re.fullmatch(r"\|[\s:\-|]+\|", s))


def render_conclusion(buf, field_full=None):
    """结论卡渲染：中文结论（大号）+ 英文副标题 + 原因。**取值与原因逐字不改。**

    V1.1.2：原因支持 `⟪P2⟫` 拆分 —— 第一页显示摘要，完整原因进 Page 2。
    V1.1.3：Page 2 改为销售信息卡后，此处仅登记完整原因（供需要时取用）。
    """
    label = buf[0] if buf else ""
    verdict_raw = buf[1] if len(buf) > 1 else ""
    reason_raw = " ".join(buf[2:]) if len(buf) > 2 else ""

    v_plain = re.sub(r"\*\*", "", verdict_raw).strip()
    key = next((k for k in CONCL_EN if k in v_plain), None)
    cls = CONCL_CLS.get(key, "unk")
    en = CONCL_EN.get(key, "")
    v_text = re.sub(r"^(🟢|🟡|🔴|⚪|🔵)\s*", "", v_plain).strip()

    if P2_MARK in reason_raw:
        head, _, tail = reason_raw.partition(P2_MARK)
        if field_full is not None:
            # 登记**完整原文**（摘要 + 其余），供需要时展示；一词不改
            field_full["Sales Conclusion"] = reason_raw.replace(P2_MARK, "")
        reason_raw = head.strip()

    parts = [f'<div class="concl-label">{inline(label)}</div>',
             f'<div class="concl-verdict">{esc(v_text)}</div>']
    if en:
        parts.append(f'<div class="concl-sub">{esc(en)}</div>')
    if reason_raw:
        parts.append(f'<div class="concl-reason">{inline(reason_raw)}</div>')
    return f'<blockquote class="conclusion concl-{cls}">' + "".join(parts) + "</blockquote>"


def md_to_html_body(lines):
    """返回 (html_blocks, page_breaks, field_full)。

    field_full：主卡每个字段的**完整原文**（`⟪P2⟫` 前后拼接，去标记）。
    Page 1 显示 `⟪P2⟫` 之前的摘要；V1.1.3 的 Page 2 信息卡显示完整原文。
    """
    out = []
    i = 0
    n = len(lines)
    page_break_before = set()
    block_idx = 0
    field_full = {}

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # 分页指令（版式规则，非内容规则）
        if stripped == "<!-- PAGEBREAK -->":
            page_break_before.add(block_idx)
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        # 分隔线
        if re.fullmatch(r"-{3,}|\*{3,}", stripped):
            out.append('<hr class="sep"/>')
            block_idx += 1
            i += 1
            continue

        # 表格
        if stripped.startswith("|") and i + 1 < n and is_table_sep(lines[i + 1]):
            header = split_row(stripped)
            is_card = bool(header) and header[0] in ("字段", "Field")
            body_rows = []
            j = i + 2
            while j < n and lines[j].strip().startswith("|"):
                body_rows.append(split_row(lines[j]))
                j += 1
            t = [f'<table class="{"card-table" if is_card else "data-table"}">',
                 "<thead><tr>"]
            t += [f"<th>{inline(c)}</th>" for c in header]
            t.append("</tr></thead><tbody>")
            for r in body_rows:
                field_key = normalize_field(r[0]) if is_card and r else ""
                row_attr = f' data-field="{html_mod.escape(field_key, quote=True)}"' if field_key else ""
                t.append(f"<tr{row_attr}>")
                for ci, c in enumerate(r):
                    # V1.1.2/V1.1.3：主卡长字段 `⟪P2⟫` 拆分 —— Page 1 只显示摘要，
                    # 完整原文登记到 field_full 供 Page 2 信息卡展示（**一字不删**）。
                    if is_card and ci == 1:
                        fname = normalize_field(r[0]) if r else ""
                        if fname and P2_MARK in c:
                            field_full[fname] = c.replace(P2_MARK, "")
                            c = c.partition(P2_MARK)[0].strip()
                        elif fname:
                            field_full[fname] = c
                        # V1.2.1-layout：确定性自动摘要 —— 仅白名单长字段、
                        # 仅在 main() 溢出循环设置了预算时生效；只改 P1 显示，
                        # field_full（P2 完整原文）不变。
                        if (fname in AUTO_SPLIT_FIELDS
                                and AUTO_SUMMARY_BUDGET
                                and len(c) > AUTO_SUMMARY_BUDGET):
                            c = auto_summary(c, AUTO_SUMMARY_BUDGET)
                            AUTO_CUT_LOG.append(fname)
                    if is_card and ci == 0:
                        t.append(f"<td>{field_label_html(c)}</td>")
                    else:
                        t.append(f"<td>{cell_html(c) if is_card else inline(c)}</td>")
                t.append("</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            block_idx += 1
            i = j
            continue

        # details / summary
        if stripped.startswith("<details>"):
            out.append('<div class="fold">')
            block_idx += 1
            i += 1
            continue
        if stripped.startswith("</details>"):
            out.append("</div>")
            block_idx += 1
            i += 1
            continue
        if stripped.startswith("<summary>"):
            txt = re.sub(r"</?summary>", "", stripped)
            out.append(f'<div class="fold-title">{inline(txt)}</div>')
            block_idx += 1
            i += 1
            continue

        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            lvl = len(m.group(1))
            txt = m.group(2)
            # V1.1.1：四组标题加样式类（识别 WHO / WHY / WHERE·WHO / ACTION）
            cls = ' class="group-title"' if GROUP_TITLE_RE.match(txt) else ""
            out.append(f"<h{lvl}{cls}>{inline(txt)}</h{lvl}>")
            block_idx += 1
            i += 1
            continue

        # 引用（V1.1.1：含结论卡标记的引用块 → 结论卡样式）
        if stripped.startswith(">"):
            buf = []
            is_conclusion = False
            while i < n:
                cur = lines[i].strip()
                if cur.startswith(">"):
                    raw = cur.lstrip(">").strip()
                    if raw:
                        buf.append(raw)
                        if CONCLUSION_MARK in raw:
                            is_conclusion = True
                    i += 1
                elif (not cur) and i + 1 < n and lines[i + 1].strip().startswith(">"):
                    i += 1  # 空行分隔的同一引用块（结论卡可能分行书写）
                else:
                    break
            if is_conclusion:
                out.append(render_conclusion(buf, field_full))
            else:
                out.append("<blockquote>"
                           + "<br/>".join(inline(b) for b in buf) + "</blockquote>")
            block_idx += 1
            continue

        # 代码块
        if stripped.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append("<pre>" + esc("\n".join(buf)) + "</pre>")
            block_idx += 1
            continue

        # 列表
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            tag = "ol" if ordered else "ul"
            items = []
            while i < n and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                txt = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])
                items.append(f"<li>{inline(txt)}</li>")
                i += 1
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            block_idx += 1
            continue

        # 段落（连续非空行合并）
        buf = []
        while i < n:
            s = lines[i].strip()
            if (not s) or s.startswith("#") or s.startswith("|") or s.startswith(">") \
               or s.startswith("```") or s.startswith("<details>") or s.startswith("</details>") \
               or s.startswith("<summary>") or re.fullmatch(r"-{3,}", s) \
               or re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]) \
               or s == "<!-- PAGEBREAK -->":
                break
            buf.append(lines[i].strip())
            i += 1
        if buf:
            out.append("<p>" + "<br/>".join(inline(b) for b in buf) + "</p>")
            block_idx += 1

    return out, page_break_before, field_full


# ---------------------------------------------------------------- 校验


def extract_main_card_fields(md_text: str):
    """提取主卡字段，返回 **Internal Key** 列表。

    V1.1.1：主卡按 WHO / WHY / WHERE·WHO / ACTION **四组分表**，
    因此需遍历**全部**以「字段 / Field」为表头的表格并累加（不再遇首个即停）。
    第一列为 Display Label 时，经 `normalize_field` 还原为 Internal Key。
    `Sales Conclusion` 为独立结论卡（引用块），单独识别后计入。
    """
    lines = md_text.splitlines()
    fields = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("|") and i + 1 < len(lines) and is_table_sep(lines[i + 1]):
            header = [h.strip() for h in split_row(s)]
            if header and header[0] in ("字段", "Field"):
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith("|"):
                    row = split_row(lines[j])
                    if row:
                        name = normalize_field(row[0])
                        if name and name not in fields:
                            fields.append(name)
                    j += 1
                i = j
                continue
        i += 1

    # 结论卡（V1.1.1）：Sales Conclusion 已移出主卡表格
    if CONCLUSION_MARK in md_text and "Sales Conclusion" not in fields:
        fields.append("Sales Conclusion")
    return fields


def validate(md_text: str):
    """主卡 13 字段完整性校验。返回 (ok, missing, found)。"""
    found = extract_main_card_fields(md_text)
    missing = [f for f in REQUIRED_FIELDS if f not in found]
    return (len(missing) == 0), missing, found


# ---------------- V1.2.1-audit：证据导出门禁（2026-10-19 审计案例） ----------------
# 修复缺陷：附录 A 表头若不含 `Decision Impact`，渲染器绑不到证据表 ⇒ Page 3 只剩图例，
# 而旧检查仅 WARN 不阻断。本函数把证据完整性升级为**硬门禁**：
#   ① 附录 A 存在且表头含 Decision Impact 列（渲染绑定契约）
#   ② 证据表至少 1 条数据行（禁止空白证据附录导出）
#   ③ 全文引用的 E# 必须在证据表中存在（禁止悬空引用）
#   ④ 每条证据的 Source 非空（影响决策的事实必须有来源）
#   ⑤ 每条证据的 类型 ∈ {FACT, INFERENCE, UNKNOWN*}（F/I/U 分类明确）
# 纯校验：不改写任何内容；不通过则不出 PDF。
EV_FIU_RE = re.compile(r"^(FACT|INFERENCE|UNKNOWN)\b")


def check_evidence(md_text: str):
    """证据导出门禁。返回 (ok, problems)。"""
    problems: list = []

    # 附录 A 证据段（次序无关，V1.2.1-fix：可在附录 B 之前或之后；
    # 与 build_html 的 extract_evidence_table_html 抽取口径一致）。
    a_match = re.search(r"(?:<summary>|#{1,6}\s+)附录 A\b", md_text)
    if not a_match:
        return False, ["缺少 附录 A 证据段；证据不会进入 PDF"]
    a_start = a_match.end()
    end_match = re.search(r"(?:<summary>|#{1,6}\s+)(附录 B|边界声明)\b", md_text[a_start:])
    evidence_section = md_text[a_start: a_start + end_match.start()] if end_match else md_text[a_start:]

    # ---- 定位证据表（Markdown 管道表，表头含 Decision Impact）----
    header = None
    rows_md = None
    for m in re.finditer(
        r"^\|(.+)\|\s*\n\|[\s:|-]+\|\s*\n((?:\|.*\|\s*\n?)+)", evidence_section, re.M
    ):
        cells = [c.strip() for c in m.group(1).split("|")]
        if "Decision Impact" in cells:
            header = cells
            rows_md = m.group(2)
            break

    if header is None:
        return False, ["附录 A 表头缺 `Decision Impact` 列 ⇒ 渲染器无法绑定证据表"
                       "（Page 3 将只剩图例）。请使用标准表头："
                       "| # | 主题 | 类型 | 结论 | Source | Reason | Confidence | Decision Impact |"]

    rows = [ln for ln in (rows_md or "").splitlines() if ln.strip().startswith("|")]
    if not rows:
        return False, ["证据表为空（0 条数据行）—— 禁止空白证据附录导出"]

    idx = {name: k for k, name in enumerate(header)}

    def cells_of(ln):
        return [c.strip() for c in ln.strip().strip("|").split("|")]

    # ---- 表内完整性（对齐 evidence-policy：FACT 必须有 Source；INFERENCE 必须有
    #      Reason + Confidence；UNKNOWN 必须带三态后缀 —— UNKNOWN 行回测校准 2026-10-19）----
    table_ids, problems_rows = [], []
    for ln in rows:
        cells = cells_of(ln)
        eid = cells[0] if cells else ""
        if not re.match(r"E\d+$", eid):
            problems_rows.append(f"行 ID 异常：{eid!r}（应为 E<数字>）")
            continue
        table_ids.append(eid)

        def get(col):
            k = idx.get(col)
            return cells[k] if k is not None and k < len(cells) else ""

        fiu = get("类型")
        m_fiu = EV_FIU_RE.match(fiu)
        if not m_fiu:
            problems_rows.append(f"{eid}：类型 {fiu!r} 不属 FACT / INFERENCE / UNKNOWN")
            continue
        kind = m_fiu.group(1)
        if kind == "FACT" and get("Source").strip(" *`—-") == "":
            problems_rows.append(f"{eid}：FACT 但 Source 为空（影响决策的事实必须有来源）")
        if kind == "INFERENCE":
            if get("Reason").strip(" *`—-") == "" or get("Confidence").strip(" *`—-") == "":
                problems_rows.append(f"{eid}：INFERENCE 但 Reason / Confidence 为空")
        if kind == "UNKNOWN" and not re.search(
            r"(searched|no source|not searched)", fiu
        ):
            problems_rows.append(f"{eid}：UNKNOWN 未带三态后缀（searched / no source / not searched）")

    # ---- 悬空引用（全文引用的 E# 必须在表中）----
    cited = {f"E{n}" for n in re.findall(r"\bE(\d{1,3})\b", md_text)}
    missing = sorted(cited - set(table_ids), key=lambda x: int(x[1:]))

    problems.extend(problems_rows)
    if missing:
        problems.append("悬空引用（引用了证据表不存在的编号）："
                        + "、".join(missing) + " —— 不得引用不存在的证据")
    return (not problems), problems


def split_audit_sections(md_text):
    """V1.1.3：把 Markdown 切成「业务 PDF 区」与「审计区」。

    审计区 = 从 `## 附录 B`（可溯源率 / 类型定义 / 实体排除 / 来源冲突 …）
             或 `## 边界声明` 起，直到文末。
    审计区**只在 Markdown 保留**，不进入业务 PDF；切分不改动任何文字。
    """
    lines = md_text.splitlines(keepends=True)
    cut = len(lines)
    for k, ln in enumerate(lines):
        if AUDIT_SECTION_RE.match(ln.strip()):
            cut = k
            break
    return "".join(lines[:cut]), "".join(lines[cut:])


def extract_evidence_table_html(md_text: str):
    """附录 A 证据表 → HTML data-table（次序无关，V1.2.1-fix）。

    无论附录 A 位于附录 B 之前或之后，都能从全文本定位附录 A 区段、
    抽取带 `Decision Impact` 列的管道表，并转为与 `md_to_html_body` 完全一致的
    `<table class="data-table">` 格式。修复「附录 A 在附录 B 之后时证据被截断、
    KEY EVIDENCE 页空白」的潜伏缺陷（原 build_html 仅在 pdf_md 内找证据表）。
    纯版式抽取，不改写任何字段值，不新增 / 推断任何结论。
    """
    a_match = re.search(r"(?:<summary>|#{1,6}\s+)附录 A\b", md_text)
    if not a_match:
        return None
    start = a_match.end()
    end_match = re.search(r"(?:<summary>|#{1,6}\s+)(附录 B|边界声明)\b", md_text[start:])
    seg = md_text[start: start + end_match.start()] if end_match else md_text[start:]
    lines = seg.splitlines()
    n = len(lines)
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("|") and i + 1 < n and is_table_sep(lines[i + 1]):
            header = split_row(s)
            if "Decision Impact" in header:
                body_rows = []
                j = i + 2
                while j < n and lines[j].strip().startswith("|"):
                    body_rows.append(split_row(lines[j].strip()))
                    j += 1
                t = ['<table class="data-table">', "<thead><tr>"]
                t += [f"<th>{inline(c)}</th>" for c in header]
                t.append("</tr></thead><tbody>")
                for r in body_rows:
                    t.append("<tr>")
                    for c in r:
                        t.append(f"<td>{inline(c)}</td>")
                    t.append("</tr>")
                t.append("</tbody></table>")
                return "".join(t)
    return None


BOLD_HEAD_RE = re.compile(r"^\*\*(.+?)\*\*\s*$")


def parse_bold_sections(md_text):
    """取「独立成行的加粗小标题」下的小节正文。纯搬运，不改写。"""
    out, cur = {}, None
    for raw in md_text.splitlines():
        s = raw.strip()
        m = BOLD_HEAD_RE.match(s)
        if m:
            cur = m.group(1).strip()
            out.setdefault(cur, [])
            continue
        if cur is None:
            continue
        if s.startswith("#") or s == "---" or s.startswith("<"):
            cur = None
            continue
        if s:
            out[cur].append(s)
    return out


def render_si_card(title, body_html):
    """Page 2 销售信息卡（V1.1.3）。标题为固定版式标签，正文为字段原文搬运。"""
    return (f'<div class="si-card"><div class="si-h">{esc(title)}</div>'
            f'<div class="si-body">{body_html}</div></div>')


def page2_cards_html(md_text, field_full):
    """Page 2 · SALES INTELLIGENCE｜开发情报 —— 5 张销售信息卡（V1.1.3）。

    **纯搬运**：内容全部取自 Markdown 既有字段与小节，不新增、不推断、不改写。
    不再使用「大型字段表」；不使用 FACT / Confidence / Decision Impact 等审计术语。
    """
    secs = parse_bold_sections(md_text)
    cards = []

    for title, key in PAGE2_CARDS:
        if key is None or (isinstance(key, str) and key.startswith("__SECTION__:")):
            # ① Why BDD —— 由「BDD Opportunity 判定依据」+「Demand Status 明细」组成
            # ⑥ Risk & Watch（V1.2.1-audit）—— 搬运「**风险**」小节
            body = []
            if isinstance(key, str) and key.startswith("__SECTION__:"):
                sec = key.split(":", 1)[1]
                for ln in secs.get(sec, []):
                    t = ln.strip()
                    if not t:
                        continue
                    if re.match(r"^[-*]\s+", t):
                        t = re.sub(r"^[-*]\s+", "", t)
                    body.append(f'<div class="si-kv">{inline(t)}</div>')
            else:
                for name in PAGE2_SOURCES:
                    for ln in secs.get(name, []):
                        t = ln.strip()
                        if not t:
                            continue
                        if re.match(r"^[-*]\s+", t):
                            t = re.sub(r"^[-*]\s+", "", t)
                        body.append(f'<div class="si-kv">{inline(t)}</div>')
            cards.append(render_si_card(title, "".join(body) or "<div class='si-kv'>—</div>"))
            continue

        # ② ③ ④ ⑤ —— 取该字段的**完整原文**（Page 1 摘要 + 被压缩部分）
        val = field_full.get(key) or ""
        cards.append(render_si_card(title, f'<div class="si-p">{cell_html(val)}</div>'))
    return cards


# ---------------------------------------------------------------- 三页切分


def split_pdf_pages(blocks):
    """业务三页的素材切分（纯版式操作，不改内容）。

    Page 1  客户快照 —— 决策 / 行动模块优先，其后为 WHO / WHY / WHERE 三组
    Page 2  SALES INTELLIGENCE —— 由 `page2_cards_html()` 现场生成，不取这里的块
    Page 3  KEY EVIDENCE      —— 取 Markdown 附录 A 的 Evidence 表（转为卡片）

    返回 (page1_blocks, evidence_table_block or None)。
    """
    page1, ev_table = [], None
    for b in blocks:
        plain = re.sub(r"<[^>]+>", "", b)
        if "BDD Opportunity 判定依据" in plain:
            break
        page1.append(b)
    for b in blocks:
        if re.match(r'<table class="data-table">', b) and "Decision Impact" in b:
            ev_table = b
            break
    return page1, ev_table


def decision_first_page(blocks):
    """Reorder existing card fields into a decision-first Page 1.

    Presentation only: every existing Internal Key is rendered once, and all
    field text and conclusion wording are copied from the parsed source blocks.
    If the expected 13 keyed rows or conclusion card are missing, preserve the
    legacy page blocks unchanged.
    """
    rows = {}
    title = None
    metadata = []
    conclusion = None
    for block in blocks:
        if block.startswith("<h1>") and title is None:
            title = block
            continue
        if 'class="card-table"' in block:
            for key, row_html in re.findall(
                r'<tr data-field="([^"]+)">(.*?)</tr>', block, re.S
            ):
                rows[key] = f"<tr data-field=\"{key}\">{row_html}</tr>"
        elif 'class="conclusion ' in block:
            conclusion = block
        elif not re.search(r"<h3[^>]*class=\"group-title\"", block):
            if not re.search(r"<table class=\"card-table\"", block):
                metadata.append(block)

    required_rows = [k for k in REQUIRED_FIELDS if k != "Sales Conclusion"]
    if title is None or conclusion is None or any(k not in rows for k in required_rows):
        return blocks

    def table(keys, extra_class="", with_head=True):
        body = "".join(rows[k] for k in keys)
        # V1.2.1-fix：恢复原主卡表格的「字段 / 判定」表头行（重排时曾丢失）
        head = ("<thead><tr><th>字段</th><th>判定</th></tr></thead>"
                if with_head else "")
        return (f'<table class="card-table {extra_class}">{head}<tbody>{body}'
                f'</tbody></table>')

    action_keys = ["Next Action", "Who to Contact", "What Is Missing"]
    info_groups = (
        ("01 WHO ｜客户是谁", ["Company", "Country", "What They Do", "Customer Type"]),
        ("02 WHY ｜为什么值得看", ["Industry Match", "BDD Opportunity", "Demand Status"]),
        ("03 WHERE / WHO ｜从哪里切入", [
            "Current Wastewater Treatment / Technology", "Priority Site"
        ]),
    )
    action_module = (
        '<div class="decision-action">'
        '<div class="decision-verdict">' + conclusion + '</div>'
        '<div class="decision-next">' + table(["Next Action"], "next-action-table") + '</div>'
        '<div class="decision-support">' + table(
            ["Who to Contact", "What Is Missing"], "support-action-table"
        ) + '</div></div>'
    )
    out = [title] + metadata + [action_module]
    for heading, keys in info_groups:
        out.append(f'<h3 class="group-title">{esc(heading)}</h3>')
        out.append(table(keys))
    return out


def _plain(h: str) -> str:
    return re.sub(r"<[^>]+>", "", h or "").strip()


# ---------------- V1.2.1-audit：Page 1 决策条（2026-10-19） ----------------
# 用户要求 Page 1 一屏突出：评级 / Gate / 风险 / 下一步 / 测试报价状态。
# 评级（结论卡）与下一步（Next Action）已在决策模块置顶；本条补 **Gate / Commercial Risk /
# 测试报价** 三个摘要值 —— 全部**机械抽取自 Markdown 原文**，取不到即整段省略，不新增不推断。
def decision_strip_html(md_text: str):
    items = []

    m = re.search(r"(?:Gate|Guard)[^=＝\n]{0,6}[=＝]\s*[`*]*\s*([A-Z][a-z]+)", md_text)
    if m:
        items.append(f"<span>Gate: <b>{esc(m.group(1))}</b></span>")

    m = re.search(r"Commercial Risk[^\n]*?[：:]", md_text)
    if m:
        tail = md_text[m.end():m.end() + 80]
        m2 = re.search(
            r"[`*]*\s*(?:⚪|🟢|🟡|🔴)?\s*[`*]*\s*"
            r"((?:Unknown|Low|Medium|High)(?:\s*·\s*(?:searched|no source|not searched))?)",
            tail,
        )
        if m2:
            items.append(f"<span>Commercial Risk: <b>{esc(m2.group(1))}</b></span>")

    if re.search(r"按范围冻结", md_text):
        items.append("<span>技术测试 / 报价: <b>按范围冻结（未输出）</b></span>")

    if not items:
        return ""
    return ('<div class="decision-strip">' + "".join(items) + "</div>")


def evidence_to_cards(blocks):
    """附录 A 表格 → **KEY EVIDENCE 卡片**（V1.1.3）。

    纯版式转换：按 Markdown 既有的 `Decision Impact` 排序取前 6~8 条，
    每条只呈现 **主题 / 简洁事实 / Source** 三段。
    **PDF 不显示 FACT · INFERENCE · Confidence · Decision Impact 等审计术语**
    （这些仍完整保留在 Markdown 附录 A）。
    **不新增、不推断、不改写**任何字段值。
    """
    out = []
    for b in blocks:
        if not re.match(r'<table class="data-table">', b):
            out.append(b)
            continue
        rows = re.findall(r"<tr>(.*?)</tr>", b, re.S)
        if not rows or "Decision Impact" not in rows[0]:
            out.append(b)
            continue

        cols = [_plain(c) for c in re.findall(r"<th>(.*?)</th>", rows[0])]
        idx = {name: k for k, name in enumerate(cols)}
        if "Decision Impact" not in idx:
            out.append(b)
            continue

        def cell(cells, name):
            k = idx.get(name)
            return cells[k] if k is not None and k < len(cells) else ""

        def rank(cells):
            low = _plain(cell(cells, "Decision Impact")).lower()
            for key, v in (("high", 0), ("medium", 1), ("low", 2)):
                if key in low:
                    return v
            return 3

        body = [c for c in (re.findall(r"<td>(.*?)</td>", r, re.S) for r in rows[1:]) if c]
        body.sort(key=rank)
        picked = [c for c in body if rank(c) <= 1][:EVIDENCE_CARD_LIMIT]
        if not picked:
            picked = body[:EVIDENCE_CARD_LIMIT]

        cards = []
        for c in picked:
            eid = _plain(cell(c, "#"))
            topic = _plain(cell(c, "主题"))
            fact = cell(c, "结论")
            src_cell = cell(c, "Source")
            src = re.sub(r"^<td>(.*)</td>$", r"\1", src_cell, flags=re.S)
            # ⚠️ 仅当来源是**不含任何 HTML 标签的纯文本**时才按 Markdown 处理。
            #    已含标签（<a> / <code> / <strong> …）的一律原样保留 —— 否则 inline()
            #    会把标签二次转义成 &lt;code&gt; 并以**字面文本**印进 PDF（实测缺陷）。
            if src and not re.search(r"<\s*/?\s*[A-Za-z]", src):
                src = inline(src)
            src_plain = _plain(src)
            heading = eid if not topic else f"{eid} · {topic}"
            lines = [f'<div class="ev-topic">{esc(heading)}</div>',
                     f'<div class="ev-fact">{fact}</div>']
            if src_plain not in ("", "—", "-"):
                lines.append(f'<div class="ev-src">来源：{src}</div>')
            cards.append('<div class="ev-card">' + "".join(lines) + "</div>")

        out.append(f'<div class="ev-list">共 {len(cards)} 条关键依据'
                   f'（全量 F/I/U 证据表附后）</div>'
                   + "".join(cards))
    return out


# ---------------------------------------------------------------- HTML 组装

CSS = """
@page { size: A4; margin: 12mm 11mm; }
* { box-sizing: border-box; }
body {
  font-family: "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
  color: #1c1f23; background: #ffffff; font-size: 10pt; line-height: 1.5;
  margin: 0; padding: 0;
}
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
.page-head {
  border-bottom: 2px solid #1c1f23; padding-bottom: 3px; margin: 0 0 8px 0;
  font-size: 9pt; letter-spacing: .12em; text-transform: uppercase; color: #5a626b;
  display: flex; justify-content: space-between;
}
/* V1.1.3：Page 2 / 3 的页眉即业务区标题，加重呈现（Page 1 完全不变） */
section.page:nth-of-type(n+2) .page-head {
  font-size: 11pt; font-weight: 700; color: #1f2b3a;
  letter-spacing: .03em; text-transform: none; margin-bottom: 7px;
}

/* ---- 字体层级（V1.1.2）---- */
h1 { font-size: 16pt; font-weight: 700; margin: 1px 0 3px 0; letter-spacing: -.01em; }
h2 { font-size: 11.5pt; font-weight: 700; margin: 9px 0 5px 0; padding-left: 7px;
     border-left: 3px solid #1c1f23; }
h3 { font-size: 10pt; font-weight: 700; margin: 8px 0 3px 0; color: #33383e; }
p { margin: 3px 0; }

/* ---- V1.1.2 Section Header（四组统一浅灰蓝底、深色加粗）---- */
h3.group-title {
  font-size: 9.5pt; font-weight: 700; letter-spacing: .03em;
  color: #1f2b3a; background: #e8eef5;
  margin: 8px 0 3px 0; padding: 4px 8px; break-after: avoid;
  border-left: 0; border-bottom: 0; border-radius: 2px;
}
h3.group-title.sub { background: #f2f5f9; color: #47566b; font-size: 9.8pt; }

/* ---- 表格基础 ---- */
table { border-collapse: collapse; width: 100%; margin: 6px 0; font-size: 9.6pt; }
th, td { border: 1px solid #d6dae0; padding: 5px 7px;
         text-align: left; vertical-align: middle; }
th { background: #f2f4f6; font-weight: 600; }
table.data-table td:first-child { white-space: nowrap; }

/* ---- V1.2.1 主卡：决策与行动优先；不改变字段值或判断 ---- */
.decision-action {
  border: 1px solid #d6dae0; border-radius: 3px; background: #f8fafc;
  padding: 7px 9px; margin: 6px 0 8px 0; break-inside: avoid;
  display: grid; grid-template-columns: 1.05fr 1.25fr; gap: 6px 10px;
}
.decision-verdict { grid-column: 1 / -1; }
.decision-verdict blockquote.conclusion { margin: 0; padding: 6px 10px; }
.decision-verdict .concl-verdict { font-size: 14pt; }
.decision-next { grid-column: 1 / -1; border-left: 4px solid #2f6fb5;
  background: #edf4fb; padding: 5px 8px; }
.decision-support { grid-column: 1 / -1; }
table.card-table.next-action-table { margin: 0; }
table.card-table.next-action-table td { padding: 4px 6px; }
table.card-table.next-action-table td:last-child { font-size: 10.5pt; font-weight: 700; }
/* support 表原为 8.7pt（偏小）；按「不靠缩字号压页」的口径提到 9.2pt */
table.card-table.support-action-table { margin: 0; font-size: 9.2pt; }
table.card-table.support-action-table td { padding: 3px 6px; }
table.card-table.support-action-table td:first-child { width: 20%; }
table.card-table.next-action-table thead th,
table.card-table.support-action-table thead th { padding: 2px 6px; }
/* ---- 主卡：字段列浅灰蓝 + 固定 20%；判定列白底 ---- */
/* V1.2.1-fix：恢复表头行后，用「自动换行 + 内边距 + 行高」抵消高度，
   **不缩小正文字号**（保持 9.8pt 可读性）。
   ⚠️ 不加 `table-layout: fixed` —— 实测它会强制列宽、令单元格换行变高，
      使 3 个样本从 3 页涨到 4 页（变体实验 V0=4页 / V4=3页）。 */
table.card-table { font-size: 9.8pt; margin: 4px 0; width: 100%; line-height: 1.3; }
table.card-table thead th { background: #e8eef5; color: #1f2b3a;
                            font-weight: 700; padding: 3px 7px;
                            text-align: left; vertical-align: middle; }
table.card-table td { background: #ffffff; padding: 4px 7px;
                      overflow-wrap: anywhere; word-break: break-word; }
table.card-table tr { break-inside: avoid; }
table.card-table td:first-child {
  width: 20%; background: #eef2f7; white-space: normal;
  text-align: left; vertical-align: middle;
}
.fld-cn { font-weight: 700; color: #1c1f23; }
.fld-en { font-weight: 400; color: #6b7480; font-size: 9pt; }

/* ---- V1.1.2 Badge（短状态；不整行染色）---- */
.badge {
  display: inline-block; padding: 1px 7px; border-radius: 9px;
  font-size: 9pt; font-weight: 700; line-height: 1.5; white-space: nowrap;
}
.badge-ok   { background: #e3f4ea; color: #1f7a45; border: 1px solid #b7e0c8; }
.badge-warn { background: #fdf3dc; color: #8a6100; border: 1px solid #f0dca6; }
.badge-bad  { background: #fdeaea; color: #ab2222; border: 1px solid #f2c4c4; }
.badge-unk  { background: #f0f2f4; color: #5f6874; border: 1px solid #d9dee3; }
.badge-info { background: #e7f0fa; color: #215d9e; border: 1px solid #bed8f0; }
td .badge { vertical-align: middle; }

/* ---- V1.1.2 结论卡（左色条 + 浅色语义背景）---- */
blockquote.conclusion {
  margin: 9px 0 3px 0; padding: 9px 13px 9px 13px;
  border: 1px solid #d6dae0; border-left: 6px solid #9aa1a9;
  background: #f7f9fb; border-radius: 3px;
}
blockquote.conclusion.concl-ok   { background: #f2faf5; border-color: #cbe7d7;
                                   border-left-color: #1f9d55; }
blockquote.conclusion.concl-warn { background: #fdfaf2; border-color: #f0e2c0;
                                   border-left-color: #d99a04; }
blockquote.conclusion.concl-bad  { background: #fdf4f4; border-color: #f0cccc;
                                   border-left-color: #cf2e2e; }
blockquote.conclusion.concl-unk  { background: #f7f8fa; border-color: #d9dee3;
                                   border-left-color: #9aa1a9; }
.concl-label { font-size: 7.8pt; letter-spacing: .14em; text-transform: uppercase;
               color: #5a626b; font-weight: 700; margin-bottom: 2px; }
.concl-verdict { font-size: 16pt; font-weight: 700; line-height: 1.18; }
.concl-sub { font-size: 9pt; color: #5a626b; margin-top: 0; }
.concl-reason { font-size: 9.2pt; line-height: 1.4; color: #33383e;
                margin-top: 3px; text-align: left; }

/* ---- V1.1.3 Page 2 · SALES INTELLIGENCE 销售信息卡 ---- */
.si-card {
  border: 1px solid #dde2e8; border-left: 3px solid #2f6fb5;
  background: #fbfcfd; border-radius: 2px;
  padding: 5px 9px 6px 9px; margin: 0 0 5px 0;
}
.si-card:last-child { margin-bottom: 0; }
.si-h { font-size: 9.6pt; font-weight: 700; color: #1f2b3a;
        margin-bottom: 3px; letter-spacing: .01em; }
.si-body { font-size: 8.8pt; line-height: 1.42; }
.si-kv { margin: 1px 0; text-align: left; }
.si-p { margin: 0; text-align: left; }

/* ---- V1.1.3 Page 3 · KEY EVIDENCE 卡片（主题 / 简洁事实 / Source）---- */
.ev-list { font-size: 8.2pt; color: #6b7480; margin: 3px 0 4px 0; }
.ev-card {
  border: 1px solid #dde2e8; border-left: 3px solid #2f6fb5;
  background: #fbfcfd; border-radius: 2px;
  padding: 4px 8px 5px 8px; margin: 0 0 3px 0;
}
.ev-topic { font-size: 8.8pt; font-weight: 700; color: #2f6fb5;
            margin-bottom: 1px; text-align: left; }
.ev-fact { font-size: 8.2pt; line-height: 1.36; color: #1c1f23; text-align: left; }
.ev-src { font-size: 7.8pt; line-height: 1.3; color: #526170;
          margin-top: 1px; text-align: left; }
.ev-src a { color: #215d9e; text-decoration: underline; text-underline-offset: 1px; }

/* ---- V1.2.1-audit（2026-10-19）---- */
/* Page 1 决策条：Gate / Commercial Risk / 测试报价 摘要 */
.decision-strip {
  grid-column: 1 / -1;
  display: flex; flex-wrap: wrap; gap: 2px 14px;
  border-top: 1px solid #dbe1e8; margin-top: 2px; padding: 3px 2px 0 2px;
  font-size: 8.2pt; color: #33404e;
  break-inside: avoid;
}
.decision-strip b { color: #14202c; }
/* 分页卫生：卡片 / 表格行 / 小节标题不跨页截断 */
.ev-card, .si-card, .decision-action, .decision-strip,
.conclusion, tr { break-inside: avoid; }
thead { display: table-header-group; }
/* Page 3 起全量证据表（自然分页）：压缩行距保证信息密度 */
table.data-table { font-size: 8.4pt; }
table.data-table td, table.data-table th { padding: 3px 5px; }

/* ---- V1.1.2 Page 2/3 正文密度容器 ---- */
.body-dense { font-size: 9pt; line-height: 1.38; }
.body-dense p { margin: 2.5px 0; }
.body-dense li { margin: 1px 0; }
.body-dense h2 { font-size: 11pt; margin: 7px 0 4px 0; }
.body-dense h3 { font-size: 9.5pt; margin: 6px 0 2px 0; }

code { background: #f2f4f6; padding: 0 3px; border-radius: 2px;
       font-family: Consolas, "Courier New", monospace; font-size: 9pt; }
blockquote { margin: 6px 0; padding: 5px 9px; background: #f7f8fa;
             border-left: 3px solid #b9c0c8; color: #3d444c; font-size: 9.6pt; }
pre { background: #f7f8fa; border: 1px solid #e3e7eb; padding: 7px 9px;
      font-family: Consolas, monospace; font-size: 8.8pt; white-space: pre-wrap; }
ul, ol { margin: 3px 0 3px 16px; padding: 0; }
li { margin: 1px 0; }
hr.sep { border: 0; border-top: 1px solid #e3e7eb; margin: 9px 0; }
.fold { margin: 6px 0; }
.fold-title { font-weight: 700; font-size: 9.8pt; margin: 8px 0 3px 0; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%;
       margin-right: 3px; vertical-align: baseline; }
.dot.ok { background: #1f9d55; }
.dot.warn { background: #d99a04; }
.dot.bad { background: #cf2e2e; }
.dot.unk { background: #9aa1a9; }
.dot.info { background: #2f6fb5; }
.legend { margin-top: 10px; font-size: 8.6pt; color: #5a626b;
          border-top: 1px solid #e3e7eb; padding-top: 5px; }
.legend span.item { margin-right: 12px; }
.pagenum { font-size: 8.6pt; color: #8a9099; }
"""


def build_html(md_text: str, single: bool) -> str:
    """Markdown → 业务 PDF 的 HTML。

    V1.1.3：Markdown 先按「业务区 / 审计区」切分 —— 审计区不进入 PDF。
    V1.2.1：第一页将现有结论、下一步、联系人、缺项组成决策/行动模块置顶；
    其后仅显示 WHO / WHY / WHERE 事实分组，13 个 Internal Key 各显示一次。
    """
    consistent, problems, _ = check_decision_consistency(md_text)
    if not consistent:
        raise ValueError("报告判断不一致：" + "；".join(problems))
    pdf_md, _audit_md = split_audit_sections(md_text)
    lines = pdf_md.splitlines()
    blocks, _, field_full = md_to_html_body(lines)

    p1_blocks, ev_table = split_pdf_pages(blocks)
    p1_blocks = decision_first_page(p1_blocks)

    # V1.2.1-fix：证据表次序无关抽取（修复「附录 A 在附录 B 之后时证据被截断、
    # KEY EVIDENCE 页空白」的潜伏缺陷）。split_pdf_pages 仅在 pdf_md 内找证据表，
    # 附录 A 落在审计区（pdf_md 之外）时回退到全文本抽取。
    if ev_table is None:
        ev_table = extract_evidence_table_html(md_text)

    # V1.2.1-audit：Page 1 决策条（Gate / Commercial Risk / 测试报价状态 —— 机械抽取，取不到则省略）
    # 注：置于决策模块**内部**（末行），避免外挂块把 Page 1 顶出一屏（实测 2026-10-19 缺陷）。
    strip = decision_strip_html(md_text)
    if strip:
        for k, b in enumerate(p1_blocks):
            if b.startswith('<div class="decision-action">') and b.rstrip().endswith("</div>"):
                p1_blocks[k] = b.rstrip()[: -len("</div>")] + strip + "</div>"
                break

    # Page 2 · SALES INTELLIGENCE（销售信息卡，内容取自 Markdown 字段原文）
    page2 = page2_cards_html(pdf_md, field_full)
    # Page 3 · KEY EVIDENCE（6~8 条卡片）+ **全量 F/I/U 证据表**（V1.2.1-audit：
    # 完整证据随 PDF 交付，第 3 页起按内容自然分页；表格跨页时 Chrome 自动重复表头）
    page3 = evidence_to_cards([ev_table]) if ev_table else []
    if ev_table is not None:
        page3 = page3 + [ev_table]

    # 抽取标题（第一个 h1）
    title = ""
    for b in p1_blocks:
        if b.startswith("<h1>"):
            title = b
            break

    if single:
        body1 = [b for b in p1_blocks if b != title]
        pages = [[("h1", title)] + [("b", b) for b in body1]
                 + [("b", b) for b in page2] + [("b", b) for b in page3]]
        page_names = ["Full"]
    else:
        pages = [
            [("h1", title)] + [("b", b) for b in p1_blocks if b != title],
            [("b", b) for b in page2],
            [("b", b) for b in page3],
        ]
        page_names = ["Customer Snapshot",
                      "SALES INTELLIGENCE ｜开发情报",
                      "KEY EVIDENCE ｜关键依据"]

    html_parts = [
        "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>",
        f"<title>{esc(title)}</title><style>{CSS}</style></head><body>",
    ]

    for idx, page in enumerate(pages):
        name = page_names[idx]
        # V1.2.1-audit：P3 起全量证据自然分页 ⇒ 物理页数可能 > 3；页码改用节号（P1/P2/P3），
        # 不再标「n / 3」以免与实际页数不符。
        html_parts.append("<section class='page'>")
        html_parts.append(
            f"<div class='page-head'><span>{esc(name)}</span>"
            f"<span class='pagenum'>P{idx + 1}</span></div>"
        )
        if not single and idx >= 1:
            html_parts.append("<div class='body-dense'>")
        for kind, b in page:
            html_parts.append(b)
        if not single and idx >= 1:
            html_parts.append("</div>")
        if idx == len(pages) - 1:
            legend = "".join(
                f"<span class='item'><span class='dot {c}'></span>{esc(t)}</span>"
                for c, t in COLOR_LEGEND
            )
            html_parts.append(f"<div class='legend'>{legend}</div>")
        html_parts.append("</section>")

    html_parts.append("</body></html>")
    return "\n".join(html_parts)


# ---------------------------------------------------------------- Chrome 打印


def find_browser():
    cands = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in cands:
        if os.path.isfile(c):
            return c
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    return None


def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    browser = find_browser()
    if not browser:
        raise RuntimeError(
            "未找到 Chrome / Edge。请安装 Google Chrome 或 Microsoft Edge 后重试。"
        )
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_profile = tempfile.mkdtemp(prefix="bdd_pdf_")
    render_dir = Path(tempfile.mkdtemp(prefix=".bdd_pdf_render_", dir=str(pdf_path.parent)))
    staged_pdf = render_dir / pdf_path.name
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={tmp_profile}",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={str(staged_pdf)}",
        html_path.as_uri(),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode != 0 or not staged_pdf.exists() or staged_pdf.stat().st_size == 0:
            raise RuntimeError(
                "PDF 生成失败。\n"
                f"exit={proc.returncode}\nstdout={proc.stdout[-1500:]}\nstderr={proc.stderr[-1500:]}"
            )
        # Replace atomically only after Chrome produced a fresh, non-empty PDF.
        os.replace(staged_pdf, pdf_path)
    finally:
        shutil.rmtree(tmp_profile, ignore_errors=True)
        shutil.rmtree(render_dir, ignore_errors=True)


def check_page_flow(pdf_path: Path):
    """P1/P2 溢出检测（V1.2.1-audit · 2026-10-19）。

    物理第 2 页应以「SALES INTELLIGENCE」开头、第 3 页以「KEY EVIDENCE」开头；
    否则说明第 1 / 2 节内容溢出（典型症状：几十字符的孤立页）。
    优先 pymupdf，缺失时用 pypdf 读取文本；两者均不可用时返回 None。
    """
    try:
        import pymupdf  # type: ignore
        with pymupdf.open(str(pdf_path)) as doc:
            pages = [pg.get_text().strip() for pg in doc]
    except Exception:
        try:
            from pypdf import PdfReader  # type: ignore
            pages = [(pg.extract_text() or "").strip()
                     for pg in PdfReader(str(pdf_path)).pages]
        except Exception:
            return None
    problems = []
    if len(pages) >= 2 and not pages[1].startswith("SALES INTELLIGENCE"):
        problems.append(f"P1 溢出：物理第 2 页仅 {len(pages[1])} 字符且非 P2 节头"
                        "（主卡超一屏，请按「Page 1 摘要纪律」压缩字段）")
    if len(pages) >= 3 and not pages[2].startswith("KEY EVIDENCE"):
        problems.append(f"P2 溢出：物理第 3 页非 KEY EVIDENCE 节头（P2 卡片超一屏）")
    return problems


def count_pdf_pages(pdf_path: Path):
    """读取 PDF 页数 —— 优先 pymupdf，否则纯 stdlib 扫描（**零强制依赖**）。

    合并说明（2026-10-13 成本优化 Patch 2）：原先「渲染后再由调用方另跑一次
    pymupdf 查页数」属于**重复的机械性检查**（同一次渲染的结论要跑两遍）。
    现并入渲染层输出 CHECK_pages，调用方以本行输出为准，不再另行核对。
    本函数**只读取页数，不参与任何判断**（渲染层隔离要求不变）。
    """
    try:                                    # ① pymupdf（若环境已装）
        import pymupdf  # type: ignore
        with pymupdf.open(str(pdf_path)) as doc:
            return doc.page_count
    except Exception:
        pass
    try:                                    # ② stdlib 回退：数 /Type /Page 对象
        raw = pdf_path.read_bytes()
    except Exception:
        return None
    pages = len(re.findall(rb"/Type\s*/Page(?![s])", raw))
    if pages:
        return pages
    counts = [int(n) for n in re.findall(rb"/Count\s+(\d+)", raw)]
    return max(counts) if counts else None


def check_pdf_content(pdf_path: Path):
    """核对业务 PDF 的节顺序、证据内容和近乎空白的续页（V1.2.1-fix：与物理页数无关）。

    证据表自第 3 页起自然分页（可延续到 4、5 页），且第 1 页偶发溢出时第 2 页
    未必是 SALES INTELLIGENCE。故不再把「第 i 页 = 第 i 节」作为硬约束，改为在
    合理范围内检索三节标题与关键证据 E#，并防止末页近乎空白。保留对「证据缺失 /
    空白证据页」的阻断能力。
    """
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return ["缺少 pypdf，无法自动核对 PDF 内容；请安装 requirements.txt"]

    try:
        pages = [(page.extract_text() or "").strip()
                 for page in PdfReader(str(pdf_path)).pages]
    except Exception as exc:  # noqa: BLE001
        return [f"PDF 文本读取失败：{exc}"]

    if not pages:
        return ["PDF 无任何页面"]

    problems = []
    expected = ("CUSTOMER SNAPSHOT", "SALES INTELLIGENCE", "KEY EVIDENCE")
    if len(pages) < len(expected):
        return [f"仅 {len(pages)} 页，缺少业务 PDF 的固定三节"]

    # 第 1 页固定为客户快照（CSS 已 uppercase；pypdf 抽取亦为大写，统一 .upper 比对）
    if expected[0] not in pages[0].upper()[:250]:
        problems.append("第 1 页不是 CUSTOMER SNAPSHOT，可能发生跨页溢出")

    # SALES INTELLIGENCE / KEY EVIDENCE 在证据自然分页下可能不在第 2/3 页；
    # 在合理范围内检索即可（KEY EVIDENCE 必在第 3 页或之后）。
    if not any(expected[1] in p.upper() for p in pages[:4]):
        problems.append("前 4 页未出现 SALES INTELLIGENCE 节标题，可能发生跨页溢出")
    if not any(expected[2] in p.upper() for p in pages[:6]):
        problems.append("前 6 页未出现 KEY EVIDENCE 节标题，证据可能未渲染")

    # 核心：全篇必须存在 E# 关键证据（确认证据表已写入 PDF，而非空白页）
    if not any(re.search(r"\bE\d+\b", p) for p in pages):
        problems.append("全篇缺少 E# 关键证据；请检查附录 A 的绑定与位置")

    # 末页近乎空白（证据分页收尾的表尾 / 图例行不计）：仅当末页 < 80 字符且无 E# 才告警
    if len(pages) > 3 and len(pages[-1]) < 80 and not re.search(r"\bE\d+\b", pages[-1]):
        problems.append("末页近乎空白；请检查证据表分页")
    return problems


# ---------------------------------------------------------------- main


def check_decision_consistency(md_text):
    business, _ = split_audit_sections(md_text)
    _, _, fields = md_to_html_body(business.splitlines())
    match = re.search(r">[^\n]*Sales Conclusion[^\n]*\n((?:>[^\n]*(?:\n|$))+)", business)
    if match:
        fields["Sales Conclusion"] = match.group(1)
    return decision_engine.check_report(md_text, fields)


def main():
    ap = argparse.ArgumentParser(description="BDD Customer Intelligence — MD → HTML → PDF")
    ap.add_argument("input", help="输入 Markdown 文件")
    ap.add_argument("--out", help="输出 PDF 路径（默认与输入同名）")
    ap.add_argument("--html", help="同时保留 HTML 的路径")
    ap.add_argument("--single", action="store_true", help="输出完整单页版（内部复核用）")
    args = ap.parse_args()

    md_path = Path(args.input).resolve()
    if not md_path.is_file():
        print(f"[FAIL] 输入文件不存在：{md_path}")
        return 2

    md_text = md_path.read_text(encoding="utf-8")
    consistent, decision_problems, decision = check_decision_consistency(md_text)
    if not consistent:
        print("CHECK_decision     : FAIL — " + "；".join(decision_problems))
        return 6
    print("CHECK_decision     : " + ("PASS — " + decision["rule_version"] if decision else "LEGACY — 保留历史规则，未执行新Partner重评"))

    # ---- 校验（硬门禁：缺字段不出 PDF）
    ok, missing, found = validate(md_text)
    print("=" * 66)
    print("BDD Customer Intelligence · 渲染前校验")
    print("=" * 66)
    print(f"输入文件           : {md_path}")
    print(f"主卡字段数         : {len(found)} / {len(REQUIRED_FIELDS)}")
    if not ok:
        print(f"CHECK_main_card    : FAIL — 缺 {len(missing)} 项：{', '.join(missing)}")
        print("\n[FAIL] 主卡字段不完整，按渲染层隔离要求**不生成 PDF**。")
        print("       请先补齐 Markdown 主卡后再渲染。")
        return 3
    print("CHECK_main_card    : PASS")
    # ---- V1.2.1-audit：证据导出门禁（硬门禁，FAIL 不出 PDF）----
    ev_ok, ev_problems = check_evidence(md_text)
    if ev_ok:
        print("CHECK_evidence     : PASS — 证据表绑定 / 引用完整性 / Source / F-I-U 全量核对通过")
    else:
        print("CHECK_evidence     : FAIL —")
        for p in ev_problems:
            print(f"    · {p}")
        print("\n[FAIL] 证据校验未通过，按导出门禁**不生成 PDF**。请先修复 Markdown 附录 A / 引用。")
        return 5

    # ---- HTML + PDF（V1.2.1-layout：P1 溢出 → 确定性自动收紧 → 本地重渲）
    # 背景：此前 P1 溢出靠模型逐字段试错压缩（实测单卡最多 5 渲 4 溢出 + 13 次 Edit）。
    # 现改为渲染器本地循环：测量（pymupdf，零积分）→ 按档位收紧白名单长字段摘要
    # → 重渲。MD 原文一字不动；P2 卡仍显示完整原文。
    pdf_path = Path(args.out).resolve() if args.out else md_path.with_suffix(".pdf")
    global AUTO_SUMMARY_BUDGET, AUTO_CUT_LOG

    def _render_once():
        html_doc = build_html(md_text, args.single)
        html_path = Path(args.html).resolve() if args.html else \
            Path(tempfile.gettempdir()) / (md_path.stem + ".render.html")
        html_path.write_text(html_doc, encoding="utf-8")
        html_to_pdf(html_path, pdf_path)

    flow = None
    try:
        _render_once()
    except Exception as e:  # noqa: BLE001
        print(f"CHECK_pdf          : FAIL — {e}")
        print("\n[FAIL] PDF 生成失败。**Markdown 保留不变**，请检查浏览器可用性后重试。")
        return 4

    if not args.single:
        for tier in AUTO_SUMMARY_TIERS:
            flow = check_page_flow(pdf_path)
            if not flow:                      # 无溢出（或 pymupdf 不可用）→ 收手
                break
            if not any(p.startswith("P1 溢出") for p in flow):
                break                         # 仅 P2 溢出不归本循环管
            # 收紧：重置切割日志 → 设预算 → 本地重渲（零模型调用）
            AUTO_CUT_LOG = []
            AUTO_SUMMARY_BUDGET = tier
            try:
                _render_once()
            except Exception as e:  # noqa: BLE001
                print(f"CHECK_pdf          : FAIL — 自动收紧重渲失败：{e}")
                return 4

    size_kb = pdf_path.stat().st_size / 1024
    print(f"CHECK_pdf          : PASS — {pdf_path} ({size_kb:.1f} KB)")
    if AUTO_CUT_LOG:
        uniq = sorted(set(AUTO_CUT_LOG))
        print(f"CHECK_page_auto    : PASS — 确定性自动摘要生效（预算 {AUTO_SUMMARY_BUDGET} 字符；"
              f"收紧 {len(uniq)} 字段：{'、'.join(uniq)}）；完整原文仍在 P2 卡与 MD")

    # ---- 页数核对（V1.2.1-audit：第 3 页起全量证据自然分页 ⇒ 目标改为「≥ 3 页」；只报告、不阻断）
    if not args.single:
        n_pages = count_pdf_pages(pdf_path)
        if n_pages is None:
            print("CHECK_pages        : MANUAL — 未能自动读取页数，请人工确认（≥ 3 页）")
        elif n_pages >= 3:
            print(f"CHECK_pages        : PASS — {n_pages} 页（P1 快照 / P2 开发情报 / "
                  "P3 起关键依据 + 全量证据自然分页）")
        else:
            print(f"CHECK_pages        : FAIL — 仅 {n_pages} 页（目标 ≥ 3 页）；"
                  "证据表可能未渲染，请核对附录 A")
            return 6

        content_problems = check_pdf_content(pdf_path)
        if content_problems:
            print("CHECK_pdf_content  : FAIL —")
            for problem in content_problems:
                print(f"    · {problem}")
            return 6
        print("CHECK_pdf_content  : PASS — 固定三节、E# 证据与末页内容已核对")

    # ---- V1.2.1-audit：P1/P2 溢出检测（只报告、不阻断）
    if not args.single:
        flow = check_page_flow(pdf_path)
        if flow is None:
            print("CHECK_page_flow    : MANUAL — pymupdf 不可用，请人工核对 P1/P2 是否溢出")
        elif flow:
            print("CHECK_page_flow    : WARN —")
            for p in flow:
                print(f"    · {p}")
        else:
            print("CHECK_page_flow    : PASS — P1/P2 各自一屏内，无孤立溢出页")

    print("=" * 66)
    print("渲染层声明：本次仅做格式转换，未新增 / 推断 / 改写任何结论；")
    print("           颜色由映射表机械查得；Markdown 为权威版本。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
