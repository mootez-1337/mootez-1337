#!/usr/bin/env python3
"""Generate assets/header.svg: name decode on the left, radar sweep on the right.

Edit the settings below and re-run: python3 assets/make_header.py
"""
import math
import random
from pathlib import Path

NAME, HANDLE = "mootez", "-1337"
PROMPT = "~$ whoami"
SUBTITLE = "cybersecurity msc / pentest / soc / ai-ml"
STATUS = "open to research collaborations"
# (label, angle in degrees clockwise from east, distance from centre 0..1)
BLIPS = [("soc", 30, 0.55), ("ai / ml", 110, 0.75), ("ctf", 200, 0.45),
         ("research", 250, 0.8), ("pentest", 300, 0.7)]

W, H = 900, 300
BG1, BG2, DOT = "#0E1726", "#13283D", "#1E3450"
TEAL, TEAL_DIM, BONE, MUTED, AMBER = "#4FD1C5", "#2C7A7B", "#F1EBDD", "#8AA0B8", "#FFB547"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, 'DejaVu Sans Mono', monospace"

LEFT = 48
NAME_SIZE, NAME_ADV = 58, 35.6
SUB_SIZE, SUB_ADV = 16, 9.8
CX, CY, R = 735, 150, 118
SWEEP = 4.0                                    # seconds per radar revolution

rng = random.Random(1337)
NOISE = "abcdefghijklmnopqrstuvwxyz0123456789#%$@?*+=/<>"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


def polar(deg, dist):
    a = math.radians(deg)
    return round(CX + math.cos(a) * dist, 2), round(CY + math.sin(a) * dist, 2)


out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'role="img" aria-labelledby="t d">',
       f'<title id="t">{NAME}{HANDLE}</title>',
       f'<desc id="d">{esc(NAME + HANDLE)}: {esc(SUBTITLE)}. {esc(STATUS)}.</desc>']

out.append(f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{DOT}"/></pattern>
<radialGradient id="scope"><stop offset="0" stop-color="{TEAL}" stop-opacity=".10"/><stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>
<clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>""")

name_done = 0.3 + len(NAME + HANDLE) * 0.08 + 0.35
type_start, type_step = name_done + 0.15, 0.035
type_done = type_start + len(SUBTITLE) * type_step
status_at = type_done + 0.3

out.append(f"""<style>
text {{ font-family: {MONO}; }}
.prompt {{ fill: {MUTED}; font-size: 15px; }}
.name {{ font-size: {NAME_SIZE}px; font-weight: 800; }}
.bone {{ fill: {BONE}; }} .teal {{ fill: {TEAL}; }}
.noise {{ fill: {TEAL_DIM}; font-size: {NAME_SIZE}px; font-weight: 800; opacity: 0; animation: flick .32s linear infinite; }}
.nz {{ animation: hide 0s forwards; }}
.lock {{ opacity: 0; animation: show .15s ease-out forwards; }}
.sub {{ fill: {BONE}; font-size: {SUB_SIZE}px; opacity: .85; }}
.ch {{ opacity: 0; animation: show 0s forwards; }}
.caret {{ fill: {TEAL}; opacity: 0; animation: travel {type_done - type_start:.2f}s steps({len(SUBTITLE)}, end) {type_start:.2f}s forwards, blink 1.06s steps(1) {type_start:.2f}s infinite; }}
.status {{ opacity: 0; animation: show .4s ease-out {status_at:.2f}s forwards; }}
.status text {{ fill: {MUTED}; font-size: 14px; }}
.pulse {{ fill: {AMBER}; transform-box: fill-box; transform-origin: center; animation: pulse 2s ease-out infinite; }}
.label {{ fill: {MUTED}; font-size: 12px; }}
.ring {{ fill: none; stroke: {TEAL}; stroke-opacity: .22; }}
@keyframes flick {{ 0%, 24.99% {{ opacity: 1; }} 25%, 100% {{ opacity: 0; }} }}
@keyframes hide {{ to {{ visibility: hidden; }} }}
@keyframes show {{ to {{ opacity: 1; }} }}
@keyframes blink {{ 0%, 50% {{ opacity: 1; }} 50.01%, 100% {{ opacity: 0; }} }}
@keyframes travel {{ from {{ transform: translateX(0); }} to {{ transform: translateX({len(SUBTITLE) * SUB_ADV:.1f}px); }} }}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}
@media (prefers-reduced-motion: reduce) {{
  .noise {{ display: none; }}
  .lock, .ch, .status {{ animation: none; opacity: 1; }}
  .caret, .pulse {{ animation: none; }}
  .caret {{ opacity: 0; }}
}}
</style>""")

out.append('<g clip-path="url(#card)">')
out.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#dots)" opacity=".7"/>')

# radar
out.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#scope)"/>')
for f in (1, 0.66, 0.33):
    out.append(f'<circle class="ring" cx="{CX}" cy="{CY}" r="{round(R * f, 1)}"/>')
out.append(f'<path class="ring" d="M{CX - R} {CY}H{CX + R}M{CX} {CY - R}V{CY + R}"/>')
out.append('<g>')
for i in range(14):                            # trailing wedge: thin slices fading out behind the beam
    a0, a1 = -(i + 1) * 4, -i * 4
    x0, y0 = polar(a0, R)
    x1, y1 = polar(a1, R)
    out.append(f'<path d="M{CX} {CY}L{x0} {y0}A{R} {R} 0 0 1 {x1} {y1}Z" fill="{TEAL}" '
               f'fill-opacity="{round(0.30 * (1 - i / 14) ** 1.6, 3)}"/>')
ex, ey = polar(0, R)
out.append(f'<line x1="{CX}" y1="{CY}" x2="{ex}" y2="{ey}" stroke="{TEAL}" stroke-width="2"/>'
           f'<animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" '
           f'to="360 {CX} {CY}" dur="{SWEEP}s" repeatCount="indefinite"/></g>')
out.append(f'<circle cx="{CX}" cy="{CY}" r="3" fill="{TEAL}"/>')
for label, deg, dist in BLIPS:
    # blips share the beam's SMIL clock, so each ping lands exactly as the beam crosses it
    bx, by = polar(deg, R * dist)
    t = f'begin="{deg / 360 * SWEEP:.2f}s" dur="{SWEEP}s" repeatCount="indefinite"'
    fade = f'<animate attributeName="opacity" values="1;.3;.3" keyTimes="0;.6;1" {t}/>'
    left = math.cos(math.radians(deg)) < -0.2
    lx = bx - 10 if left else bx + 10
    anchor = ' text-anchor="end"' if left else ""
    out.append(f'<circle cx="{bx}" cy="{by}" r="3" fill="none" stroke="{AMBER}" stroke-width=".8" opacity="0">'
               f'<animate attributeName="r" values="3;14;14" keyTimes="0;.3;1" {t}/>'
               f'<animate attributeName="opacity" values=".9;0;0" keyTimes="0;.3;1" {t}/></circle>')
    out.append(f'<circle cx="{bx}" cy="{by}" r="3.5" fill="{AMBER}" opacity=".3">{fade}</circle>')
    out.append(f'<text class="label" x="{lx}" y="{by + 4}"{anchor} opacity=".45">{esc(label)}{fade}</text>')

# left column
out.append(f'<text class="prompt" x="{LEFT}" y="78">{esc(PROMPT)}</text>')
full = NAME + HANDLE
ny = 150
glow_xs = " ".join(str(round(LEFT + i * NAME_ADV, 1)) for i in range(len(full)))
out.append(f'<text class="name lock" x="{glow_xs}" y="{ny}" fill="{TEAL}" opacity=".5" filter="url(#glow)" '
           f'style="animation-delay:{name_done - 0.2:.2f}s">{esc(full)}</text>')
for i, ch in enumerate(full):
    x = round(LEFT + i * NAME_ADV, 1)
    lock = 0.3 + i * 0.08 + rng.uniform(0.1, 0.35)
    out.append(f'<g class="nz" style="animation-delay:{lock:.2f}s">')
    for f in range(4):
        out.append(f'<text class="noise" x="{x}" y="{ny}" style="animation-delay:-{f * 0.08:.2f}s">'
                   f'{esc(rng.choice(NOISE))}</text>')
    out.append('</g>')
    cls = "bone" if i < len(NAME) else "teal"
    out.append(f'<text class="name lock {cls}" x="{x}" y="{ny}" style="animation-delay:{lock:.2f}s">{esc(ch)}</text>')

sy = 192
for i, ch in enumerate(SUBTITLE):
    if ch != " ":
        out.append(f'<text class="sub ch" x="{round(LEFT + i * SUB_ADV, 1)}" y="{sy}" '
                   f'style="animation-delay:{type_start + i * type_step:.3f}s">{esc(ch)}</text>')
out.append(f'<rect class="caret" x="{LEFT}" y="{sy - SUB_SIZE + 2}" width="{SUB_ADV - 1}" height="{SUB_SIZE + 2}"/>')

out.append(f'<g class="status"><circle class="pulse" cx="{LEFT + 5}" cy="232" r="5"/>'
           f'<text x="{LEFT + 20}" y="237">{esc(STATUS)}</text></g>')
out.append('</g></svg>')

Path(__file__).with_name("header.svg").write_text("\n".join(out) + "\n")
print(f"wrote header.svg ({W}x{H}); intro finishes at {status_at + 0.4:.2f}s")
