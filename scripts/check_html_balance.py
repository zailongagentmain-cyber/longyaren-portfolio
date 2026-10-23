#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robust HTML tag-balance checker for the portfolio.

Why this exists (2026-10-23):
  The A9 spec script (re.findall over r'<(/?)([a-zA-Z0-9]+)[^>]*?(/?)>') produced
  FALSE POSITIVES on prose like "load <2s" (matched as a tag named "2s"), which
  then cascaded into 7 phantom mismatches, and it could not report WHERE a real
  mismatch happened.

This version:
  - only accepts tag names starting with a letter (so "<2s" in prose is ignored)
  - tracks void elements + self-closing tags
  - on mismatch, reports line number + context and pops the nearest matching open tag
  - prints per-file results and a TOTAL line (mismatches / unclosed / files)

Usage:  python3 scripts/check_html_balance.py [dir]
Exit code 0 = all balanced, 1 = at least one imbalance.
"""
import glob
import os
import re
import sys

VOID = {'meta', 'link', 'br', 'hr', 'img', 'input', 'source', 'area',
        'base', 'col', 'embed', 'param', 'track', 'wbr'}
TAG = re.compile(r'<(/?)([A-Za-z][A-Za-z0-9]*)([^>]*?)(/?)>')
SCRIPT_STYLE = re.compile(r'<(script|style)\b.*?</\1>', re.S | re.I)


def check(path):
    raw = open(path, encoding='utf-8').read()
    s = SCRIPT_STYLE.sub(lambda m: ' ' * len(m.group(0)), raw)  # ignore script/style bodies
    stack = []
    mismatches = []
    for m in TAG.finditer(s):
        close, name, attrs, selfclose = m.groups()
        n = name.lower()
        if n in VOID or selfclose == '/':
            continue
        line = raw.count('\n', 0, m.start()) + 1
        if close:
            if stack and stack[-1][0] == n:
                stack.pop()
            else:
                mismatches.append((line, n, stack[-1][0] if stack else None))
                for i in range(len(stack) - 1, -1, -1):
                    if stack[i][0] == n:
                        del stack[i:]
                        break
        else:
            stack.append((n, line))
    return mismatches, stack


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else '.'
    files = sorted(glob.glob(os.path.join(d, '*.html')))
    tm = tu = 0
    for f in files:
        mism, stack = check(f)
        tm += len(mism)
        tu += len(stack)
        name = os.path.basename(f)
        if mism or stack:
            print('  %-48s mismatches=%d unclosed=%s' % (name, len(mism), [s[0] for s in stack]))
            for line, n, top in mism[:5]:
                print('        line %-6d unexpected </%s> (open top: %s)' % (line, n, top))
    print('TOTAL mismatches=%d unclosed=%d files=%d' % (tm, tu, len(files)))
    sys.exit(1 if (tm or tu) else 0)


main()
