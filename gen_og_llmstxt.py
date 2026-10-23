#!/usr/bin/env python3
"""OG card for llms-txt-ai-crawler-discovery-2026.html — reuses gen_og_new.py layout."""
import os, re, textwrap
from PIL import Image, ImageDraw, ImageFont

OUT = "/Users/clawbot/projects/longyaren-portfolio/og"
os.makedirs(OUT, exist_ok=True)
W, H = 1200, 630
BG = (11, 18, 32)
ACCENT = (56, 132, 255)
ACCENT2 = (34, 197, 94)
TEXT = (245, 247, 250)
MUTED = (148, 163, 184)
FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FR = "/System/Library/Fonts/Supplemental/Arial.ttf"
FBK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"

def font(path, size): return ImageFont.truetype(path, size)

def fit_font(draw, text, path, max_size, min_size, max_w, max_lines):
    for size in range(max_size, min_size - 1, -2):
        f = font(path, size)
        lines = textwrap.wrap(text, width=max(1, int(max_w / (size * 0.52))))[:max_lines]
        wmax = max((draw.textlength(l, font=f) for l in lines), default=0)
        if wmax <= max_w: return f, lines
    f = font(path, min_size)
    return f, textwrap.wrap(text, width=max(1, int(max_w / (min_size * 0.52))))[:max_lines]

def grid(draw):
    for x in range(0, W, 60): draw.line([(x, 0), (x, H)], fill=(19, 30, 50), width=1)
    for y in range(0, H, 60): draw.line([(0, y), (W, y)], fill=(19, 30, 50), width=1)

def cluster(draw, x0, y0, w, h):
    draw.rounded_rectangle([x0, y0, x0+w, y0+h], radius=10, fill=(15, 25, 44), outline=(40, 62, 98))
    rows = [("# llms.txt", ACCENT2), ("# /llms.txt", TEXT), ("- [ref](url): note", (180,196,220)),
            ("## Section", ACCENT), ("- [Link](url)", MUTED)]
    yy = y0 + 16
    for txt, col in rows:
        draw.text((x0+16, yy), txt, font=font(FR, 19), fill=col)
        yy += 26

def make_card(title, subtitle, out_png):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    grid(d)
    d.rectangle([0, 0, W, 8], fill=ACCENT)
    d.text((70, 52), "LONGYAREN", font=font(FB, 26), fill=TEXT)
    xoff = 70 + d.textlength("LONGYAREN", font=font(FB, 26))
    d.text((xoff + 14, 56), "|", font=font(FR, 24), fill=(90, 105, 130))
    d.text((xoff + 30, 52), "SEO & GEO CONSULTANT", font=font(FR, 24), fill=MUTED)
    cluster(d, 800, 60, 330, 150)
    tf, lines = fit_font(d, title, FBK, 72, 34, 1060, 3)
    y = 190
    for ln in lines:
        d.text((70, y), ln, font=tf, fill=TEXT); y += tf.size + 12
    d.rectangle([70, y + 14, 190, y + 18], fill=ACCENT)
    sf, slines = fit_font(d, subtitle, FR, 34, 22, 1060, 3)
    y2 = y + 48
    for ln in slines:
        d.text((70, y2), ln, font=sf, fill=(180, 196, 220)); y2 += sf.size + 12
    d.rectangle([0, H - 74, W, H], fill=(8, 13, 24))
    d.text((70, H - 52), "longyaren-portfolio  |  2026", font=font(FR, 24), fill=MUTED)
    tag = "GEO / AI CRAWLERS"
    tw = d.textlength(tag, font=font(FB, 22))
    d.text((W - 70 - tw, H - 54), tag, font=font(FB, 22), fill=ACCENT2)
    img.save(out_png, "PNG", optimize=True)
    return out_png

out = f"{OUT}/llms-txt-ai-crawler-discovery-2026.png"
make_card("llms.txt in 2026: Does It Actually Work for AI Crawlers?",
          "Measured adoption, blocking rates, six failure modes and the 8-command self-test - discovery, not a citation lever",
          out)
print(out, os.path.getsize(out), "bytes")
from PIL import Image as I
im = I.open(out); print("size:", im.size)
