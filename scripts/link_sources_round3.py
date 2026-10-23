#!/usr/bin/env python3
"""
link_sources_round3.py — 大循环第 3 轮 · D 角色：来源外链落地

把 3 篇文章里的「带日期来源标注」纯文本括号变成可点击外链，并各加一个 <h2>Sources</h2> 区块。

设计约束（来自规格文件 memory/projects/loop-round-2026-10-23-1400-d.md）：
  * 只用 re.sub + 函数回调做替换，绝不用偏移切片拼字符串
  * 同一段落 / 同一表格单元格内，同一来源只链接第一次
  * 日期必须落在 <a> 内部 —— 验收脚本会剥掉 <a> 内容再数「裸标注」，
    日期留在外面会被当成未链接
  * 除规格允许的 3 处标注修正外，正文措辞零改动

用法：python3 scripts/link_sources_round3.py [--dry-run]
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REL = 'rel="nofollow noopener" target="_blank"'

# ---------------------------------------------------------------- 来源 URL
# 每条都经过：HTTP 200 + 页面可见日期 == 文中标注日期 + 站内关键词/数字命中 + Wayback 快照核实
URL = {
    "seo_handbook": "https://seohandbook.co.uk/seo-news-updates/google-march-2026-core-update/",
    "marwick": "https://www.marwickmarketing.co.uk/blog/google-march-2026-core-update/",
    "crawlraven": "https://crawlraven.com/blog/google-march-2026-core-update",
    "zzbaike": "https://www.zzbaike.com/53228.html",
    "ecorpit": "https://ecorpit.com/google-search-volatility-august-2026-traffic-drop-diagnosis/",
    "searchflex": "https://searchflex.com/blog/the-march-2026-google-core-update-what-actually-changed-for-ecommerce-brands/",
    "techdrifting": "https://techdrifting.com/articles/google-ai-overviews-traffic-seo-2026",
    "nexvolu": "https://nexvolu.com/google-update-august-2026/",
    "scriptwalker": "https://scriptwalker.app/en/blog/google-march-2026-core-update-ga4-impression-trust-engineering",
    "alpative": "https://alpative.com/en/blog/google-core-update-march-2026",
    "obsurfable": "https://obsurfable.com/resources/articles/three-citation-rulebooks-citelens-study-2026",
    "geoaura": "https://geoaura.world/blog/what-is-geo-generative-engine-optimization",
    "auspia": "https://auspia.ai/blog/google-ai-mode-citations-2026-6a6961b3-2",
    "somethinginc": "https://somethinginc.com/blog/ai-overviews-43-percent-citations-gap/",
    "awr": "https://www.advancedwebranking.com/free-seo-tools/google-ai-overview",
    "arxiv": "https://arxiv.org/abs/2609.07559",
}

# 标注原文 -> (括号内留在链接外的文字, 链接文字, URL key, 日期改写 or None)
# 链接文字后面会接上日期，日期整体落在 <a> 里面。
ATTR = {
    "The SEO Handbook": ("", "The SEO Handbook", "seo_handbook", None),
    # "reported by" 留在链接外，来源名 + 日期进链接
    "reported by Marwick Marketing": ("reported by ", "Marwick Marketing", "marwick", None),
    "CrawlRaven": ("", "CrawlRaven", "crawlraven", None),
    "站长百科": ("", "站长百科", "zzbaike", None),
    "eCorpIT": ("", "eCorpIT", "ecorpit", None),
    "Searchflex": ("", "Searchflex", "searchflex", None),
    '"parasitic SEO decoupling", CrawlRaven': ('"parasitic SEO decoupling", ', "CrawlRaven", "crawlraven", None),
    "TechDrifting": ("", "TechDrifting", "techdrifting", None),
    # A-1：页面 datePublished = 2026-10-15，原文 23 Aug 在页面上找不到出处
    "Nexvolu": ("", "Nexvolu", "nexvolu", "15 Oct 2026"),
    "Script Walker": ("", "Script Walker", "scriptwalker", None),
    "Auspia": ("", "Auspia", "auspia", None),
    "Something Inc": ("", "Something Inc", "somethinginc", None),
    "Alpative": ("", "Alpative", "alpative", None),
    # CiteLens 研究由 Obsurfable 发布，同一 URL；原文照留
    "CiteLens, via Obsurfable": ("", "CiteLens, via Obsurfable", "obsurfable", None),
    "GeoAura": ("", "GeoAura", "geoaura", None),
    # 论文本体日期为 arXiv 提交日 7 Sep 2026；文中 7 Oct 2026 是 GeoAura 的发稿日，
    # 正文按原文保留「via GeoAura」并链 GeoAura（日期一致），arXiv 放进 Sources A 组
    "Bajemon &amp; Rochet preprint, via GeoAura": ("", "Bajemon &amp; Rochet preprint, via GeoAura", "geoaura", None),
    # AWR 工具页是动态看板，静态 HTML 里没有该数字；数字可核验的落点是 GeoAura
    "Advanced Web Ranking, via GeoAura": ("", "Advanced Web Ranking, via GeoAura", "geoaura", None),
    "Obsurfable": ("", "Obsurfable", "obsurfable", None),
    # A-2：via 链反向 —— 60–80% / 71% 两个数字实际出自 Script Walker，ALM 原帖不含
    "ALM Corp, via Script Walker": ("", "Script Walker", "scriptwalker", None),
}

# ------------------------------------------------------------- 正文标注匹配
# 形如 (Source, 17 Aug 2026) —— 括号内不含右括号，日期在末尾
ATTR_PAT = re.compile(r"\(([^()\n]{3,120}?),\s*(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})\)")

# 分段边界：段落 / 表格单元格 / 列表项 / 小标题 —— 每个单元格里同源只链第一次
BLOCK_SPLIT = re.compile(r"(</p>|</td>|</li>|</h3>|</h4>|</blockquote>|</div>)", re.I)
DELIMS = {"</p>", "</td>", "</li>", "</h3>", "</h4>", "</blockquote>", "</div>"}


def a(url_key, text):
    return '<a href="%s" %s>%s</a>' % (URL[url_key], REL, text)


def link_blocks(text, stats):
    """按 BLOCK_SPLIT 切块，每块内维护已链接来源集合。"""
    parts = BLOCK_SPLIT.split(text)
    out = []
    for part in parts:
        if part.lower() in DELIMS:
            out.append(part)
            continue
        # 每个段落 / 单元格独立去重：同源只链第一次
        linked = set()

        def repl(m):
            inner, date = m.group(1), m.group(2)
            key = inner.strip()
            if key not in ATTR:
                stats["unmapped"].append(m.group(0))
                return m.group(0)
            prefix, link_text, url_key, new_date = ATTR[key]
            if url_key in linked:
                stats["dedup"].append(m.group(0))
                return m.group(0)
            linked.add(url_key)
            stats["linked"].append(m.group(0))
            return "(%s%s)" % (prefix, a(url_key, "%s, %s" % (link_text, new_date or date)))

        out.append(ATTR_PAT.sub(repl, part))
    return "".join(out)


# ------------------------------------------------------------------ Sources
SOURCES_CORE = """
    <h2>Sources</h2>
    <p><strong>Primary sources and original research</strong></p>
    <ul>
        <li><a href="https://seohandbook.co.uk/seo-news-updates/google-march-2026-core-update/" rel="nofollow noopener" target="_blank">The SEO Handbook (updated 17 Aug 2026)</a> — the rollout record and Google's own framing of the March 2026 core update; supports the timeline of the 27 March to 8 April rollout and the argument that the update was a comparative recalibration rather than a domain-level penalty</li>
        <li><a href="https://arxiv.org/abs/2609.07559" rel="nofollow noopener" target="_blank">Bajemon &amp; Rochet, arXiv preprint 2609.07559 (submitted 7 Sep 2026)</a> — the one-hand replication study behind the finding that volume-controlled quotation, statistics and citation edits produced no positive pooled effect while query relevance lifted citation correlation from 0.114 to roughly 0.37</li>
    </ul>
    <p><strong>Industry analysis and tracker data</strong></p>
    <ul>
        <li><a href="https://www.marwickmarketing.co.uk/blog/google-march-2026-core-update/" rel="nofollow noopener" target="_blank">Marwick Marketing (11 May 2026)</a> — Amsive's winner and loser data: brand-owned media such as IMDb, Amazon and Spotify gained while aggregators such as TripAdvisor, Yelp and eBay lost; supports the claim that the update redistributed visibility toward first-party and brand-owned properties</li>
        <li><a href="https://crawlraven.com/blog/google-march-2026-core-update" rel="nofollow noopener" target="_blank">CrawlRaven (10 Apr 2026)</a> — the "parasitic SEO decoupling" framing, the 22% average visibility gain for proprietary data and first-hand case studies, and Danny Sullivan's statement that Google focuses on content quality rather than how content is produced</li>
        <li><a href="https://ecorpit.com/google-search-volatility-august-2026-traffic-drop-diagnosis/" rel="nofollow noopener" target="_blank">eCorpIT (7 Aug 2026)</a> — diagnostic criteria for separating a core update from a technical incident, including reversals inside single days in August 2026 and the rule that a dip concentrated in Discover while web Search held is not a core update signature</li>
        <li><a href="https://searchflex.com/blog/the-march-2026-google-core-update-what-actually-changed-for-ecommerce-brands/" rel="nofollow noopener" target="_blank">Searchflex (26 May 2026)</a> — the e-commerce reading of the update as a relative recalibration across pages rather than a site-wide penalty; supports the "comparative recalibration" argument</li>
        <li><a href="https://techdrifting.com/articles/google-ai-overviews-traffic-seo-2026" rel="nofollow noopener" target="_blank">TechDrifting (29 Jun 2026)</a> — passage-level extractability data: content broken into 100 to 150 word sections is most likely to be lifted and cited, a 1.13 second LCP carries about 1.6 times higher odds of selection, and pages updated within two months are roughly 28% more likely to be cited</li>
        <li><a href="https://scriptwalker.app/en/blog/google-march-2026-core-update-ga4-impression-trust-engineering" rel="nofollow noopener" target="_blank">Script Walker (27 Apr 2026)</a> — the measured traffic impact by site type: AI-generated content farms losing 60 to 80% of traffic, affiliate sites reporting 71% visibility loss, and the GA4 attribution blind spot for AI-assisted visits</li>
        <li><a href="https://alpative.com/en/blog/google-core-update-march-2026" rel="nofollow noopener" target="_blank">Alpative (29 Mar 2026)</a> — Google's March 2026 documentation change adding a specific warning about structured data that does not match visible page content; supports the structured-data-parity requirement</li>
        <li><a href="https://obsurfable.com/resources/articles/three-citation-rulebooks-citelens-study-2026" rel="nofollow noopener" target="_blank">Obsurfable, publishing the CiteLens study (27 Jul 2026)</a> — 320 buyer queries across four engines showing Google AI Mode citing 93% of its sources from the top ten while ChatGPT cites 30%; supports the engine-by-engine citation split</li>
        <li><a href="https://auspia.ai/blog/google-ai-mode-citations-2026-6a6961b3-2" rel="nofollow noopener" target="_blank">Auspia (29 Jul 2026)</a> — freshness data from AI Mode citation measurement: pages updated within 30 days receive roughly 3.2 times more citations; supports the case that a refresh must change evidence rather than a timestamp</li>
        <li><a href="https://somethinginc.com/blog/ai-overviews-43-percent-citations-gap/" rel="nofollow noopener" target="_blank">Something Inc (1 Aug 2026)</a> — the citation gap between a forty-word and a longer version of the same question, and the 43% AI Overview coverage figure cited here</li>
        <li><a href="https://www.advancedwebranking.com/free-seo-tools/google-ai-overview" rel="nofollow noopener" target="_blank">Advanced Web Ranking (live dashboard, read 7 Oct 2026)</a> — the tracker series behind the AI-generated answer share of personalised and non-personalised US results</li>
    </ul>
    <p><strong>Aggregated and secondary reporting</strong></p>
    <ul>
        <li><a href="https://geoaura.world/blog/what-is-geo-generative-engine-optimization" rel="nofollow noopener" target="_blank">GeoAura (7 Oct 2026)</a> — the compilation this article draws on for the llms.txt coverage probe (36% serving a valid file, 17% blocking PerplexityBot at root against 6% blocking OAI-SearchBot) and for the 75.24% personalised AI answer share; also the reporting path for the arXiv preprint</li>
        <li><a href="https://www.zzbaike.com/53228.html" rel="nofollow noopener" target="_blank">站长百科 (19 Aug 2026)</a> — the 15 May 2026 confirmation that existing spam content policy also applies to attempts to manipulate generative AI search results, including AI Overviews and AI Mode</li>
    </ul>
"""

SOURCES_GEO = """
    <h2>Sources</h2>
    <p><strong>Primary sources and original research</strong></p>
    <ul>
        <li><a href="https://seohandbook.co.uk/seo-news-updates/google-march-2026-core-update/" rel="nofollow noopener" target="_blank">The SEO Handbook (updated 17 Aug 2026)</a> — Google's own description of the March 2026 core update as a regular update designed to better surface relevant, satisfying content for searchers from all types of sites; supports the framing of this guide around intent satisfaction rather than keyword coverage</li>
    </ul>
    <p><strong>Industry analysis and tracker data</strong></p>
    <ul>
        <li><a href="https://scriptwalker.app/en/blog/google-march-2026-core-update-ga4-impression-trust-engineering" rel="nofollow noopener" target="_blank">Script Walker (27 Apr 2026)</a> — the measurement behind the 60 to 80% traffic loss reported for AI content farms running scaled rewrites, and the explanation of why AI-assisted sessions never reach a standard GEO report</li>
    </ul>
"""

SOURCES_DEEP = """
    <h2>Sources</h2>
    <p><strong>Industry analysis and tracker data</strong></p>
    <ul>
        <li><a href="https://techdrifting.com/articles/google-ai-overviews-traffic-seo-2026" rel="nofollow noopener" target="_blank">TechDrifting (29 Jun 2026)</a> — the AI citation measurement behind the claim that AI-generated pages carry the lowest measured citation odds of any category, and the passage-length and Core Web Vitals thresholds that decide whether a page gets extracted and cited</li>
    </ul>
"""

# Sources 区块插入点（正文最后一个内容块之后）
INSERT = {
    "march-2026-core-update.html": (
        '\n<div class="related-reading">',
        SOURCES_CORE,
    ),
    "geo-guide-2026.html": (
        '\n<div class="author-card">',
        SOURCES_GEO,
    ),
    "march-2026-core-update-deep-dive-2026.html": (
        '\n<div class="related-reading">',
        SOURCES_DEEP,
    ),
}

FILES = list(INSERT.keys())


def main():
    dry = "--dry-run" in sys.argv
    for fn in FILES:
        path = os.path.join(ROOT, fn)
        src = open(path, encoding="utf-8").read()
        before = src

        stats = {"linked": [], "dedup": [], "unmapped": []}
        src = link_blocks(src, stats)

        anchor, block = INSERT[fn]
        if "<h2>Sources</h2>" not in src:
            if anchor not in src:
                print("!! insert anchor not found in %s" % fn)
                continue
            src = src.replace(anchor, block.rstrip() + "\n" + anchor, 1)

        print("== %s linked=%d dedup=%d unmapped=%d" %
              (fn, len(stats["linked"]), len(stats["dedup"]), len(stats["unmapped"])))
        if stats["dedup"]:
            print("   dedup:", stats["dedup"])
        if stats["unmapped"]:
            print("   unmapped:", stats["unmapped"])

        if src != before and not dry:
            open(path, "w", encoding="utf-8").write(src)
            print("   written")


if __name__ == "__main__":
    main()
