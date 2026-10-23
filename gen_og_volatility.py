#!/usr/bin/env python3
"""Generate the 1200x630 OG card for ai-citation-volatility-2026.html using PIL."""
import os, textwrap, math
from PIL import Image, ImageDraw, ImageFont

OUT = "/Users/clawbot/projects/longyaren-portfolio/og"
os.makedirs(OUT, exist_ok=True)

W, H = 1200, 630
BG = (11, 18, 32)
ACCENT = (167, 139, 250)      # violet
ACCENT2 = (34, 211, 238)      # cyan
TEXT = (245, 247, 250)
MUTED = (148, 163, 184)

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
        draw.line([(x, 0), (x, H)], fill=(19, 30, 50), width=1)
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=(19, 30, 50), width=1)


def waveform(draw, x0, y0, w, h):
    """Volatility sparkline: a stable band with one sharp drop and recovery."""
    mid = y0 + h * 0.45
    pts = []
    for i in range(0, 61):
        t = i / 60.0
        y = mid
        if 0.30 < t < 0.40:
            y = mid + h * 0.34 * (1 - abs(t - 0.35) / 0.05)
        elif 0.44 < t < 0.56:
            y = mid + h * 0.12 * math.sin((t - 0.44) / 0.12 * math.pi)
        else:
            y = mid + math.sin(t * 14) * h * 0.05
        pts.append((x0 + w * t, y))
    draw.line(pts, fill=ACCENT, width=4, joint="curve")
    for p in pts:
        draw.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=ACCENT2)
    band_top = mid - h * 0.22
    band_bot = mid + h * 0.22
    draw.rectangle([x0, band_top, x0 + w, band_bot], outline=(46, 68, 105), width=2)
    draw.text((x0, band_top - 26), "STABLE BAND", font=font(FB, 18), fill=MUTED)


def make_card(title, subtitle, out_png):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    grid(d)
    d.rectangle([0, 0, W, 8], fill=ACCENT)

    d.text((70, 52), "LONGYAREN", font=font(FB, 26), fill=TEXT)
    xoff = 70 + d.textlength("LONGYAREN", font=font(FB, 26))
    d.text((xoff + 14, 56), "|", font=font(FR, 24), fill=(90, 105, 130))
    d.text((xoff + 30, 52), "SEO & GEO CONSULTANT", font=font(FR, 24), fill=MUTED)

    waveform(d, 800, 60, 330, 150)

    tf, lines = fit_font(d, title, FBK, 76, 34, 1060, 3)
    y = 190
    for ln in lines:
        d.text((70, y), ln, font=tf, fill=TEXT)
        y += tf.size + 12

    d.rectangle([70, y + 14, 190, y + 18], fill=ACCENT)

    sf, slines = fit_font(d, subtitle, FR, 34, 22, 1060, 3)
    y2 = y + 48
    for ln in slines:
        d.text((70, y2), ln, font=sf, fill=(180, 196, 220))
        y2 += sf.size + 12

    d.rectangle([0, H - 74, W, H], fill=(8, 13, 24))
    d.text((70, H - 52), "longyaren-portfolio  |  2026", font=font(FR, 24), fill=MUTED)
    tag = "GEO / MEASUREMENT"
    tw = d.textlength(tag, font=font(FB, 22))
    d.text((W - 70 - tw, H - 54), tag, font=font(FB, 22), fill=ACCENT2)

    img.save(out_png, "PNG", optimize=True)
    return out_png


out = f"{OUT}/ai-citation-volatility-2026.png"
make_card("AI Citation Volatility in 2026",
          "Why the same prompt cites you today and not tomorrow \u2014 measurement, sampling and diagnosis",
          out)
print(out, os.path.getsize(out), "bytes")
from PIL import Image as I
im = I.open(out)
print("size:", im.size)
