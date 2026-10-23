#!/usr/bin/env python3
"""验收脚本 E1 / E2 / E5（本地部分）"""
import re, os, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
FILES = ["march-2026-core-update.html", "geo-guide-2026.html", "march-2026-core-update-deep-dive-2026.html"]
VOID = {"meta", "link", "br", "hr", "img", "input", "source", "area", "base", "col", "embed", "param", "track", "wbr"}

print("=== E1 未链接标注归零（剥掉 <a> 内容后统计） ===")
pat = re.compile(r"\(([^()]{3,90}?),\s*(\d{1,2}\s+\w+\s+\d{4})\)")
for f in FILES:
    s = open(f, encoding="utf-8").read()
    i = s.find("<h2>Sources</h2>")
    b = s[:i] if i > 0 else s
    st = re.sub(r"<a[^>]*>.*?</a>", "", b, flags=re.S)
    hits = pat.findall(st)
    print(f"  {f}: {len(hits)}  {hits if hits else ''}")

print("=== E1b 正文锚点数量 ===")
for f in FILES:
    s = open(f, encoding="utf-8").read()
    i = s.find("<h2>Sources</h2>")
    b = s[:i] if i > 0 else s
    ext = re.findall(r'<a href="(https?://[^"]+)"', b)
    print(f"  {f}: 正文外链锚点 {len(ext)}, distinct {len(set(ext))}")

print("=== E2 标签配平（栈式，void 排除） ===")
tag = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*?)(/?)>")
for f in FILES:
    s = open(f, encoding="utf-8").read()
    stack = []
    mis = 0
    unclosed = 0
    for m in tag.finditer(s):
        closing, name, attrs, selfclose = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        if name in VOID or selfclose:
            continue
        if closing:
            if stack and stack[-1][0] == name:
                stack.pop()
            else:
                mis += 1
                stack.append((name, m.start()))
                stack.pop()
        else:
            stack.append((name, m.start()))
    unclosed = len(stack)
    print(f"  {f}: mis={mis} unclosed={unclosed} {stack[:5]}")

print("=== E2b <h2>Sources</h2> 数量 & 位置 ===")
for f in FILES:
    s = open(f, encoding="utf-8").read()
    n = s.count("<h2>Sources</h2>")
    pos = s.find("<h2>Sources</h2>")
    print(f"  {f}: count={n} pos={pos} len={len(s)} footer_at={s.find('<footer>')}")

print("=== E5 datePublished 逐字对照 (git show HEAD:file) ===")
for f in FILES:
    old = subprocess.run(["git", "show", "HEAD:" + f], capture_output=True, text=True).stdout
    new = open(f, encoding="utf-8").read()
    o = re.findall(r'"datePublished"\s*:\s*"[^"]*"', old)
    n = re.findall(r'"datePublished"\s*:\s*"[^"]*"', new)
    print(f"  {f}: HEAD={o} NOW={n} SAME={o == n}")

print("=== E5b git status（其他文件是否被动过） ===")
print(subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout)
