#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OG card for ai-shopping-agents-product-feeds-2026.html — 复用新版卡片样式（2026 PLAYBOOK）"""
import os, textwrap
from PIL import Image, ImageDraw, ImageFont

OUT = "/Users/clawbot/projects/longyaren-portfolio/og"
os.makedirs(OUT, exist_ok=True)

W, H = 1200, 630
BG = (9, 15, 28)
ACCENT = (56, 132, 255)
TEXT = (245, 247, 250)
MUTED = (138, 152, 176)
SUB = (176, 190, 212)
GRID = (16, 26, 45)

FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FR = "/System/Library/Fonts/Supplemental/Arial.ttf"
FBK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, max_size, min_size, max_w, max_lines):
    for size in range(max_size, min_size - 1, -2):
        f = font(path, size)
        lines = textwrap.wrap(text, width=max(1, int(max_w / (size * 0.52))))[:max_lines]
        wmax = max((draw.textlength(l, font=f) for l in lines), default=0)
        if wmax <= max_w:
            return f, lines
    f = font(path, min_size)
    return f, textwrap.wrap(text, width=max(1, int(max_w / (min_size * 0.52))))[:max_lines]


def grid(draw):
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill=GRID, width=1)
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=GRID, width=1)


def cart_icon(draw, x, y, s):
    """购物车 + feed 数据点：右上空视觉"""
    c = (30, 48, 80)
    draw.rounded_rectangle([x, y, x + s, y + s * 0.78], radius=10, outline=c, width=3)
    draw.rounded_rectangle([x + s * 0.12, y - s * 0.16, x + s * 0.34, y + s * 0.06], radius=4, outline=c, width=3)
    for i in range(3):
        yy = y + s * (0.2 + i * 0.22)
        draw.line([(x + s * 0.14, yy), (x + s * (0.5 - i * 0.08), yy)], fill=(30, 48, 80), width=3)
    for i, (dx, dy) in enumerate([(0.78, 0.18), (0.86, 0.42), (0.72, 0.62)]):
        r = 5
        cx, cy = x + s * dx, y + s * dy
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT if i == 1 else (44, 104, 200))
    draw.line([(x + s * 0.78, y + s * 0.18), (x + s * 0.86, y + s * 0.42)], fill=(44, 104, 200), width=3)
    draw.line([(x + s * 0.86, y + s * 0.42), (x + s * 0.72, y + s * 0.62)], fill=(44, 104, 200), width=3)


def make_card(title, subtitle, out_png):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    grid(d)

    # eyebrow
    d.rounded_rectangle([70, 58, 86, 74], radius=4, fill=ACCENT)
    d.text((100, 56), "2026 PLAYBOOK", font=font(FB, 22), fill=MUTED)

    # 右上视觉
    cart_icon(d, 930, 120, 200)

    # 标题
    tf, lines = fit_font(d, title, FBK, 60, 34, 800, 3)
    y = 160
    for ln in lines:
        d.text((70, y), ln, font=tf, fill=TEXT)
        y += tf.size + 10

    # 蓝色分隔线
    d.rectangle([70, y + 20, 220, y + 25], fill=ACCENT)

    # 副标题
    sf, slines = fit_font(d, subtitle, FR, 30, 20, 830, 3)
    y2 = y + 56
    for ln in slines:
        d.text((70, y2), ln, font=sf, fill=SUB)
        y2 += sf.size + 12

    # 底栏
    d.rectangle([0, H - 72, W, H], fill=(7, 11, 21))
    d.text((70, H - 50), "longyaren-portfolio  |  Oct 2026", font=font(FR, 22), fill=MUTED)
    tag = "LONGYAREN · SEO & GEO"
    tw = d.textlength(tag, font=font(FB, 21))
    d.text((W - 70 - tw, H - 52), tag, font=font(FB, 21), fill=ACCENT)

    img.save(out_png, "PNG", optimize=True)
    return out_png


p = make_card(
    "AI Shopping Agents in 2026",
    "Your product feed is the ranking layer: nine required fields, agent-readability and the 30-day checklist",
    f"{OUT}/ai-shopping-agents-product-feeds-2026.png",
)
from PIL import Image as I
im = I.open(p)
print("OUT", p, im.size, os.path.getsize(p) / 1024, "KB")
assert im.size == (1200, 630), "尺寸不对"
