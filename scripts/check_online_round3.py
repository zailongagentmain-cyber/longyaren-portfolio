#!/usr/bin/env python3
"""E4：线上复验（GitHub Pages）"""
import re, subprocess, collections

BASE = "https://zailongagentmain-cyber.github.io/longyaren-portfolio/"
FILES = ["march-2026-core-update.html", "geo-guide-2026.html", "march-2026-core-update-deep-dive-2026.html"]
PROXY = "http://127.0.0.1:10080"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"

def get(url):
    cmd = ["curl", "-s", "-L", "-x", PROXY, "--max-time", "40", "-A", UA, "-w", "\n@@%{http_code}", url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    o = r.stdout
    m = re.search(r"@@(\d+)$", o)
    return (int(m.group(1)) if m else 0), (o[:m.start()] if m else o)

for f in FILES:
    code, s = get(BASE + f)
    n_sources = s.count("<h2>Sources</h2>")
    i = s.find("<h2>Sources</h2>")
    body = s[:i] if i > 0 else s
    ext = re.findall(r'<a href="https?://[^"]+"[^>]*>', body)
    opens = len(re.findall(r"<a\b", s)); closes = len(re.findall(r"</a>", s))
    paras = [p.strip() for p in re.findall(r"<p[^>]*>(.*?)</p>", s, re.S) if len(p.strip()) > 120]
    dup = [p for p, n in collections.Counter(paras).items() if n > 1]
    print(f"{f}: HTTP={code} h2Sources={n_sources} bodyExtAnchors={len(ext)} a_open={opens} a_close={closes} dupLongParas={len(dup)}")
    if dup:
        for d in dup[:3]:
            print("   DUP:", re.sub(r"<[^>]+>", "", d)[:120])

print()
for f in ["index.html", "ai-citation-volatility-2026.html", "ai-search-platform-comparison-2026.html"]:
    code, _ = get(BASE + f)
    print(f"other article {f}: HTTP={code}")
