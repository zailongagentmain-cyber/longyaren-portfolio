#!/usr/bin/env python3
"""E3：3 篇文章里所有外链逐条实测 HTTP 状态码"""
import re, os, subprocess, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
FILES = ["march-2026-core-update.html", "geo-guide-2026.html", "march-2026-core-update-deep-dive-2026.html"]
PROXY = "http://127.0.0.1:10080"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

links = []
for f in FILES:
    s = open(f, encoding="utf-8").read()
    for u in re.findall(r'<a href="(https?://[^"]+)"', s):
        links.append((f, u))

count = collections.Counter(u for _, u in links)
print(f"外链总数(含重复) {len(links)}，distinct {len(count)}\n")
bad = 0
for u, n in sorted(count.items()):
    code = 0
    for ua in (UA, "curl/8.4.0"):
        cmd = ["curl", "-s", "-L", "-o", "/dev/null", "-w", "%{http_code}", "-x", PROXY,
               "--max-time", "30", "-A", ua, u]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            code = int((r.stdout or "0").strip()[-3:] or 0)
        except Exception:
            code = 0
        if code == 200:
            break
    files = ",".join(sorted({f for f, uu in links if uu == u}))
    flag = ""
    if code != 200:
        flag = "  <-- NOT 200"
        if not (code == 403 and "zzbaike" in u):
            bad += 1
    print(f"{code}  x{n}  {u}   [{files}]{flag}")
print(f"\nBAD (非 200 且非 zzbaike 403 例外) = {bad}")
