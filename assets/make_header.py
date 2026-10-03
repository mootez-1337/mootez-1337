#!/usr/bin/env python3
"""Generate assets/header.svg: a typed `whoami` on the left, a radar sweep on the right.

Colours come from the kitty theme (~/.config/kitty/dark-theme.auto.conf), and each
colour has exactly one job; hierarchy comes from size, weight and position.
Edit the settings below and re-run: python3 assets/make_header.py
"""
import math
from pathlib import Path

NAME, HANDLE = "mootez", "-1337"
COMMAND = "whoami"
SUBTITLE = "cybersecurity msc / pentest / soc / ai-ml"
STATUS = "open to research collaborations"
# (label, angle in degrees clockwise from east, distance from centre 0..1)
BLIPS = [("soc", 30, 0.55), ("ai / ml", 110, 0.75), ("ctf", 200, 0.45),
         ("research", 250, 0.8), ("pentest", 300, 0.7)]

BG, DOT = "#222D31", "#2D3B40"
NAME_FG = "#f8f8f8"    # the name
TEXT = "#d8d8d8"       # normal text, cursor
DIM = "#8D8F8D"        # secondary text
RADAR = "#1ABB9B"      # the radar instrument
PING = "#f7ca88"       # a detection
STATUS_FG = "#7cafc2"  # availability
MONO = "'JetBrainsMono Nerd Font', 'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, 'DejaVu Sans Mono', monospace"

W, H = 900, 300
LEFT = 48
SMALL, SMALL_ADV = 15, 9.2
NAME_SIZE, NAME_ADV = 56, 34
CX, CY, R = 735, 150, 118
SWEEP = 4.0

Y_CMD, Y_NAME, Y_SUB, Y_STATUS, Y_PROMPT = 64, 132, 172, 210, 252
TYPE_START, TYPE_STEP = 0.6, 0.11
ENTER = TYPE_START + len(COMMAND) * TYPE_STEP + 0.35


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


def polar(deg, dist):
    a = math.radians(deg)
    return round(CX + math.cos(a) * dist, 2), round(CY + math.sin(a) * dist, 2)


def xs(start, n, adv):
    return " ".join(str(round(start + i * adv, 1)) for i in range(n))


out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'role="img" aria-labelledby="t d">',
       f'<title id="t">{NAME}{HANDLE}</title>',
       f'<desc id="d">{esc(NAME + HANDLE)}: {esc(SUBTITLE)}. {esc(STATUS)}.</desc>',
       f'''<defs>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{DOT}"/></pattern>
<radialGradient id="scope"><stop offset="0" stop-color="{RADAR}" stop-opacity=".08"/><stop offset="1" stop-color="{RADAR}" stop-opacity="0"/></radialGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath>
</defs>''',
       f"""<style>
text {{ font-family: {MONO}; font-size: {SMALL}px; }}
.dim {{ fill: {DIM}; }} .text {{ fill: {TEXT}; }}
.name {{ fill: {NAME_FG}; font-size: {NAME_SIZE}px; font-weight: 800; }}
.handle {{ fill: {DIM}; font-size: {NAME_SIZE}px; font-weight: 400; }}
.label {{ fill: {TEXT}; font-size: 12px; }}
.key {{ opacity: 0; animation: show 0s forwards; }}
.out {{ opacity: 0; animation: show 0s {ENTER:.2f}s forwards; }}
.cur1 {{ fill: {TEXT}; animation: travel {len(COMMAND) * TYPE_STEP:.2f}s steps({len(COMMAND)}, end) {TYPE_START:.2f}s forwards, gone 0s {ENTER:.2f}s forwards; }}
.cur2 {{ fill: {TEXT}; opacity: 0; animation: blink 1.06s steps(1) {ENTER + 0.1:.2f}s infinite; }}
.pulse {{ fill: {STATUS_FG}; animation: pulse 2s ease-in-out infinite; }}
@keyframes show {{ to {{ opacity: 1; }} }}
@keyframes gone {{ to {{ visibility: hidden; }} }}
@keyframes blink {{ 0%, 50% {{ opacity: 1; }} 50.01%, 100% {{ opacity: 0; }} }}
@keyframes travel {{ to {{ transform: translateX({len(COMMAND) * SMALL_ADV:.1f}px); }} }}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}
@media (prefers-reduced-motion: reduce) {{
  .key, .out {{ animation: none; opacity: 1; }}
  .cur1 {{ animation: none; visibility: hidden; }}
  .cur2 {{ animation: none; opacity: 1; }}
  .pulse {{ animation: none; }}
}}
</style>""",
       '<g clip-path="url(#card)">',
       f'<rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>']

# radar
out.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#scope)"/>')
for f in (1, 0.66, 0.33):
    out.append(f'<circle cx="{CX}" cy="{CY}" r="{round(R * f, 1)}" fill="none" stroke="{RADAR}" stroke-opacity=".2"/>')
out.append(f'<path d="M{CX - R} {CY}H{CX + R}M{CX} {CY - R}V{CY + R}" stroke="{RADAR}" stroke-opacity=".2"/>')
out.append('<g>')
for i in range(14):                            # trailing wedge: thin slices fading out behind the beam
    x0, y0 = polar(-(i + 1) * 4, R)
    x1, y1 = polar(-i * 4, R)
    out.append(f'<path d="M{CX} {CY}L{x0} {y0}A{R} {R} 0 0 1 {x1} {y1}Z" fill="{RADAR}" '
               f'fill-opacity="{round(0.28 * (1 - i / 14) ** 1.6, 3)}"/>')
ex, ey = polar(0, R)
out.append(f'<line x1="{CX}" y1="{CY}" x2="{ex}" y2="{ey}" stroke="{RADAR}" stroke-width="2"/>'
           f'<animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" '
           f'to="360 {CX} {CY}" dur="{SWEEP}s" repeatCount="indefinite"/></g>')
out.append(f'<circle cx="{CX}" cy="{CY}" r="3" fill="{RADAR}"/>')
for label, deg, dist in BLIPS:
    # blips share the beam's SMIL clock, so each ping lands exactly as the beam crosses it
    bx, by = polar(deg, R * dist)
    t = f'begin="{deg / 360 * SWEEP:.2f}s" dur="{SWEEP}s" repeatCount="indefinite"'
    left = math.cos(math.radians(deg)) < -0.2
    lx = bx - 10 if left else bx + 10
    anchor = ' text-anchor="end"' if left else ""
    out.append(f'<circle cx="{bx}" cy="{by}" r="3" fill="none" stroke="{PING}" stroke-width=".8" opacity="0">'
               f'<animate attributeName="r" values="3;14;14" keyTimes="0;.3;1" {t}/>'
               f'<animate attributeName="opacity" values=".9;0;0" keyTimes="0;.3;1" {t}/></circle>')
    out.append(f'<circle cx="{bx}" cy="{by}" r="3.5" fill="{PING}" opacity=".25">'
               f'<animate attributeName="opacity" values="1;.25;.25" keyTimes="0;.6;1" {t}/></circle>')
    out.append(f'<text class="label" x="{lx}" y="{by + 4}"{anchor} opacity=".45">{esc(label)}'
               f'<animate attributeName="opacity" values="1;.45;.45" keyTimes="0;.6;1" {t}/></text>')

# terminal column
out.append(f'<text class="dim" x="{LEFT}" y="{Y_CMD}">~$</text>')
cmd_x = LEFT + 3 * SMALL_ADV
for i, ch in enumerate(COMMAND):
    out.append(f'<text class="text key" x="{round(cmd_x + i * SMALL_ADV, 1)}" y="{Y_CMD}" '
               f'style="animation-delay:{TYPE_START + (i + 1) * TYPE_STEP - 0.01:.2f}s">{esc(ch)}</text>')
out.append(f'<rect class="cur1" x="{cmd_x}" y="{Y_CMD - SMALL + 2}" width="{SMALL_ADV - 1}" height="{SMALL + 3}"/>')

out.append('<g class="out">')
out.append(f'<text class="name" x="{xs(LEFT, len(NAME), NAME_ADV)}" y="{Y_NAME}">{esc(NAME)}</text>')
out.append(f'<text class="handle" x="{xs(LEFT + len(NAME) * NAME_ADV, len(HANDLE), NAME_ADV)}" y="{Y_NAME}">{esc(HANDLE)}</text>')
out.append(f'<text class="text" x="{xs(LEFT, len(SUBTITLE), SMALL_ADV)}" y="{Y_SUB}">{esc(SUBTITLE)}</text>')
out.append(f'<circle class="pulse" cx="{LEFT + 4}" cy="{Y_STATUS - 5}" r="4"/>')
out.append(f'<text class="dim" x="{LEFT + 18}" y="{Y_STATUS}">{esc(STATUS)}</text>')
out.append(f'<text class="dim" x="{LEFT}" y="{Y_PROMPT}">~$</text>')
out.append(f'<rect class="cur2" x="{cmd_x}" y="{Y_PROMPT - SMALL + 2}" width="{SMALL_ADV - 1}" height="{SMALL + 3}"/>')
out.append('</g></g></svg>')

Path(__file__).with_name("header.svg").write_text("\n".join(out) + "\n")
print(f"wrote header.svg ({W}x{H}); output prints at {ENTER:.2f}s")
