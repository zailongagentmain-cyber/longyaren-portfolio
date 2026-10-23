#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Round 4 (2026-10-23): linkify table-format source attributions "Source (Date)"
in march-2026-core-update.html.

Rules
-----
* Only ONE content file is touched: march-2026-core-update.html
* Idempotent: an already-linked attribution is never re-wrapped.
* Text is preserved except for the annotation format:
      Source (Date)   ->   (<a href="URL" ...>Source, Date</a>)
  (the parenthesis moves outside the anchor, the comma is added inside)
* "via X" attributions link to the origin of the NUMBER, not the re-publisher.
* Never guess a URL: only URLs verified in this round / round 3 are used.
"""
import re
import sys

FILE = "march-2026-core-update.html"

URL = {
    "SEO Handbook":   "https://seohandbook.co.uk/seo-news-updates/google-march-2026-core-update/",
    "Jamtech":        "https://www.jamtechtechnologies.com/index.php/insights/blog/google-march-2026-update-seo-impact-recovery-tips",
    "Script Walker":  "https://scriptwalker.app/en/blog/google-march-2026-core-update-ga4-impression-trust-engineering",
    "CrawlRaven":     "https://crawlraven.com/blog/google-march-2026-core-update",
    "Marwick":        "https://www.marwickmarketing.co.uk/blog/google-march-2026-core-update/",
    "Searchflex":     "https://searchflex.com/blog/the-march-2026-google-core-update-what-actually-changed-for-ecommerce-brands/",
    "Alpative":       "https://alpative.com/en/blog/google-core-update-march-2026",
    "TechDrifting":   "https://techdrifting.com/articles/google-ai-overviews-traffic-seo-2026",
    "Something":      "https://somethinginc.com/blog/ai-overviews-43-percent-citations-gap/",
    "SomethingAug19": "https://somethinginc.com/blog/google-august-2026-update-unconfirmed",
    "eCorpIT":        "https://ecorpit.com/google-search-volatility-august-2026-traffic-drop-diagnosis/",
    "Obsurfable":     "https://obsurfable.com/resources/articles/three-citation-rulebooks-citelens-study-2026",
    "BizScoreAI":     "https://bizscoreai.com/blog/google-search-ranking-volatility-continues-after-august-2026-spam-update",
    "FirstRanker":    "https://www.thefirstranker.com/blog/google-core-update",
    "GeoAura":        "https://geoaura.world/blog/what-is-geo-generative-engine-optimization",
    "RaisingSun":     "https://r-sun.ai/insights/generative-engine-optimization-2026",
    "ZzbaiKe":        "https://www.zzbaike.com/53228.html",
    "Auspia":         "https://auspia.ai/blog/google-ai-mode-citations-2026-6a6961b3-2",
    "StatusDash":     "https://status.search.google.com/",
}

# (label exactly as it appears in the article, date, url key)
# Longer labels first so that "Obsurfable, publishing the CiteLens study" wins
# over the bare "Obsurfable".
TARGETS = [
    ("The Searchflex analysis of the March 2026 update", "26 May 2026", "Searchflex"),
    ("Obsurfable, publishing the CiteLens study",       "27 Jul 2026", "Obsurfable"),
    ("Alpative's contemporaneous analysis",             "29 Mar 2026", "Alpative"),
    ("The SEO Handbook",        "17 Aug 2026", "SEO Handbook"),
    ("Jamtech Technologies",    "1 Apr 2026",  "Jamtech"),
    ("Script Walker",           "27 Apr 2026", "Script Walker"),
    ("CrawlRaven",              "10 Apr 2026", "CrawlRaven"),
    ("Marwick Marketing",       "11 May 2026", "Marwick"),
    ("Searchflex",              "26 May 2026", "Searchflex"),
    ("Alpative",                "29 Mar 2026", "Alpative"),
    ("TechDrifting",            "29 Jun 2026", "TechDrifting"),
    ("Something Inc",           "1 Aug 2026",  "Something"),
    ("Something Inc",           "19 Aug 2026", "SomethingAug19"),
    ("eCorpIT",                 "7 Aug 2026",  "eCorpIT"),
    ("CorpIT",                  "7 Aug 2026",  "eCorpIT"),
    ("Obsurfable",              "27 Jul 2026", "Obsurfable"),
    ("BizScoreAI",              "16 Sep 2026", "BizScoreAI"),
    ("TheFirstRanker",          "27 Aug 2026", "FirstRanker"),
    ("GeoAura",                 "7 Oct 2026",  "GeoAura"),
    ("R[AI]SING SUN",           "4 Jun 2026",  "RaisingSun"),
    ("站长百科",                  "19 Aug 2026", "ZzbaiKe"),
    ("Auspia",                  "29 Jul 2026", "Auspia"),
]

ANCHOR = ('<a href="{url}" rel="nofollow noopener" target="_blank">'
          '{label}, {date}</a>')


def main():
    with open(FILE, encoding="utf-8") as fh:
        html = fh.read()

    # protect already-linked regions: any <a ...>...</a> block
    protected = []

    def protect(m):
        protected.append(m.group(0))
        return "\x00P%d\x00" % (len(protected) - 1)

    html = re.sub(r"<a\b[^>]*>.*?</a>", protect, html, flags=re.S)

    stats = {}

    for label, date, key in TARGETS:
        url = URL[key]
        pat = re.compile(re.escape(label) + r"\s*\(\s*" + re.escape(date) + r"\s*\)")

        def repl(m):
            return "(" + ANCHOR.format(url=url, label=label, date=date) + ")"

        html, n = pat.subn(repl, html)
        stats[label + " | " + date] = n

    # plain (date-less) source names that still deserve a link
    for label, key in [("Google Search Status Dashboard", "StatusDash")]:
        url = URL[key]
        pat = re.compile(re.escape(label) + r"(?![\"'<])")
        html, n = pat.subn(
            '<a href="%s" rel="nofollow noopener" target="_blank">%s</a>' % (url, label),
            html)
        stats[label + " (plain)"] = n

    # "cited by X on <date>" style attributions in running text
    PLAIN = [
        (r"cited by (Marwick Marketing)(?= on 11 May 2026)", "Marwick"),
        (r"and (eCorpIT)(?= on 7 Aug 2026)", "eCorpIT"),
        (r"As (eCorpIT)(?= noted on 7 August 2026)", "eCorpIT"),
        (r"reported by (Obsurfable)(?= on 27 July 2026)", "Obsurfable"),
        (r"reported via (GeoAura)(?= on 7 Oct 2026)", "GeoAura"),
        (r"reported by (Something Inc)(?= on 1 Aug 2026)", "Something"),
        # source names without a date in the aggregators row
        (r"via (Marwick Marketing)(?= and The SEO Handbook)", "Marwick"),
        (r"(The SEO Handbook)(?=</td>)", "SEO Handbook"),
    ]
    for rx, key in PLAIN:
        url = URL[key]
        pat = re.compile(rx)
        html, n = pat.subn(
            lambda m: m.group(0).replace(m.group(1), '<a href="%s" rel="nofollow noopener" target="_blank">%s</a>' % (url, m.group(1))),
            html)
        stats["plain: " + rx] = n

    # restore protected regions
    for i, block in enumerate(protected):
        html = html.replace("\x00P%d\x00" % i, block)

    with open(FILE, "w", encoding="utf-8") as fh:
        fh.write(html)

    for k in sorted(stats):
        print("%-70s %d" % (k, stats[k]))
    print("total replacements:", sum(stats.values()))


if __name__ == "__main__":
    sys.exit(main())
