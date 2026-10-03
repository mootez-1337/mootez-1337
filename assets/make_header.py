#!/usr/bin/env python3
"""Generate assets/header.svg: an xxd-style hex dump that decodes into the intro text.

Edit LINES (each exactly 16 characters) and re-run: python3 assets/make_header.py
"""
import random
from pathlib import Path

LINES = [
    "hi, i'm mootez. ",
    "msc in cybersec.",
    "pentest + soc.  ",
    "learning ai/ml. ",
    "open to research",
]
COMMAND = "$ xxd mootez-1337.bin"

BG, RULE = "#1C2633", "#2E3B4C"
DIM, NOISE = "#6F8197", "#4A5A6E"
HEX, TEXT, AMBER = "#C9D1DB", "#EDE6D6", "#E9A23B"

FONT = 15
ADV = 9.4                 # fixed glyph advance; every glyph is placed explicitly
PAD = 32
LINE_H = 26
TOP = 82                  # baseline of the first dump row
COLS = 67                 # width of one xxd line in characters

ROW_START, ROW_GAP, CELL_GAP = 0.5, 0.55, 0.035
FRAMES, FRAME_T = 5, 0.07

rng = random.Random(1337)
HEXDIGITS = "0123456789abcdef"
NOISE_ASCII = "abcdefghijklmnopqrstuvwxyz0123456789.:/#%$@!?*+=-_~"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


def x(col):
    return round(PAD + col * ADV, 2)


def hex_col(b):
    return 10 + (b // 2) * 5 + (b % 2) * 2


def ascii_col(b):
    return 51 + b


def glyphs(chars, cols, y, cls, extra=""):
    xs = " ".join(str(x(c)) for c in cols)
    return f'<text x="{xs}" y="{y}" class="{cls}"{extra}>{esc("".join(chars))}</text>'


assert all(len(l) == 16 for l in LINES), "every line must be exactly 16 characters"

width = round(PAD * 2 + COLS * ADV)
last_y = TOP + (len(LINES) - 1) * LINE_H
prompt_y = last_y + LINE_H + 14
height = prompt_y + 30
done = ROW_START + (len(LINES) - 1) * ROW_GAP + 16 * CELL_GAP + 0.25

out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">')
out.append('<title id="t">mootez-1337</title>')
out.append(f'<desc id="d">A hex dump that decodes to: {esc(" ".join(l.strip() for l in LINES))}</desc>')
out.append(f"""<style>
text {{ font-family: 'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, 'DejaVu Sans Mono', monospace; font-size: {FONT}px; }}
.cmd {{ fill: {DIM}; }}
.off {{ fill: {DIM}; }}
.noise {{ fill: {NOISE}; opacity: 0; animation: flick {FRAMES * FRAME_T:.2f}s linear infinite; }}
.hex {{ fill: {HEX}; }}
.asc {{ fill: {TEXT}; }}
.cell {{ opacity: 0; animation: lock .12s ease-out forwards; }}
.done {{ opacity: 0; animation: lock .2s ease-out {done:.2f}s forwards; }}
.caret {{ fill: {AMBER}; animation: blink 1.06s steps(1) {done:.2f}s infinite; }}
@keyframes flick {{ 0%, 19.99% {{ opacity: 1; }} 20%, 100% {{ opacity: 0; }} }}
@keyframes lock {{ to {{ opacity: 1; }} }}
@keyframes blink {{ 0%, 50% {{ opacity: 1; }} 50.01%, 100% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{
  .noise {{ display: none; }}
  .cell, .done, .caret {{ animation: none; opacity: 1; }}
}}
</style>""")
out.append(f'<rect width="{width}" height="{height}" rx="10" fill="{BG}"/>')
out.append(f'<line x1="{PAD}" x2="{width - PAD}" y1="{TOP - 28}" y2="{TOP - 28}" stroke="{RULE}"/>')
out.append(glyphs(COMMAND, range(len(COMMAND)), TOP - 40, "cmd"))

for r, line in enumerate(LINES):
    y = TOP + r * LINE_H
    out.append(glyphs(f"{r * 16:08x}:", range(9), y, "off"))

    # noise layer: FRAMES full-row scrambles, each visible for one FRAME_T slot
    cols = [c for b in range(16) for c in (hex_col(b), hex_col(b) + 1)] + [ascii_col(b) for b in range(16)]
    for f in range(FRAMES):
        chars = [rng.choice(HEXDIGITS) for _ in range(32)] + [rng.choice(NOISE_ASCII) for _ in range(16)]
        out.append(glyphs(chars, cols, y, "noise", f' style="animation-delay:-{f * FRAME_T:.2f}s"'))

    # locked layer: each byte covers its noise with a background rect, left to right
    for b, ch in enumerate(line):
        delay = ROW_START + r * ROW_GAP + b * CELL_GAP
        top = y - FONT - 2
        hc, ac = hex_col(b), ascii_col(b)
        out.append(f'<g class="cell" style="animation-delay:{delay:.3f}s">')
        out.append(f'<rect x="{x(hc)}" y="{top}" width="{round(ADV * 2, 2)}" height="{LINE_H - 4}" fill="{BG}"/>')
        out.append(f'<rect x="{x(ac)}" y="{top}" width="{ADV}" height="{LINE_H - 4}" fill="{BG}"/>')
        out.append(glyphs(f"{ord(ch):02x}", (hc, hc + 1), y, "hex"))
        if ch != " ":
            out.append(glyphs(ch, (ac,), y, "asc"))
        out.append("</g>")

out.append(f'<g class="done">{glyphs("$", (0,), prompt_y, "cmd")}'
           f'<rect class="caret" x="{x(2)}" y="{prompt_y - FONT + 2}" width="{ADV}" height="{FONT + 2}"/></g>')
out.append("</svg>")

Path(__file__).with_name("header.svg").write_text("\n".join(out) + "\n")
print(f"wrote header.svg ({width}x{height}, decode finishes at {done:.2f}s)")
