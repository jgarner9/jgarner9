"""Generates the profile SVGs. Usage: python3 scripts/gen_assets.py assets"""
import os
import sys

W, H = 900, 270
MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, &quot;Liberation Mono&quot;, monospace'
SANS = '-apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Inter, Helvetica, Arial, sans-serif'
GO = "#00add8"
# The tagline, word by word, in its syntax-highlight colours. Also the rainbow palette.
TAG = [("i", "#ff7b72"), ("like", "#d2a8ff"), ("pretty", "#ffa657"), ("colored", "#7ee787"), ("words", "#79c0ff")]
ADV = 0.6  # monospace advance, in em


# ---------------------------------------------------------------- header
def intro():
    """$ whoami, the name, the typed tagline and the comment line.

    Every tagline character is placed at its own column and revealed in turn, so the
    typing effect never depends on the viewer's font (Safari ignores textLength on tspans).
    """
    size, x, y, step, d0 = 22, 60, 182, 0.075, 1.1
    text = " ".join(w for w, _ in TAG)
    colors = []
    for w, c in TAG:
        colors += [c] * len(w) + [None]
    chars = "".join(
        f'<text class="ch" style="animation-delay:{d0 + i*step:.3f}s" x="{x + i*size*ADV:.1f}" y="{y}" font-size="{size}" fill="{colors[i]}">{ch}</text>'
        for i, ch in enumerate(text) if ch != " ")
    n = len(text)
    return f'''<g font-family="{MONO}">
    <text class="rise d1" x="60" y="88" font-size="16" fill="#7ee787">$ whoami</text>
    {chars}
    <rect class="cursor" x="{x}" y="164" width="11" height="24" fill="{GO}"
      style="animation: move {n*step:.3f}s steps({n}, start) {d0}s forwards, blink 1s step-end infinite"/>
    <text class="rise d3" x="60" y="218" font-size="14" fill="#5b6b82">// always learning, currently building</text>
  </g>
  <text class="rise d2" x="58" y="140" font-family="{SANS}" font-size="46" font-weight="700" fill="#e6edf3">Hi, I'm Jason<tspan fill="{GO}">.</tspan></text>
  <style>@keyframes move {{ to {{ transform: translateX({n*size*ADV:.1f}px); }} }}</style>'''


def wafer():
    """A silicon wafer full of dies under a rainbow sheen, with one die (JG-9) highlighted."""
    cx, cy, r, pitch = 726, 135, 118, 19
    flat = f"M{cx-r*0.28:.1f},{cy+r*0.96:.1f} A{r},{r} 0 1 1 {cx+r*0.28:.1f},{cy+r*0.96:.1f} Z"
    dies, hl = [], None
    for gy in range(-7, 7):
        for gx in range(-7, 7):
            x, y = cx + gx*pitch + 1.5, cy + gy*pitch + 1.5
            corners = [(x, y), (x+pitch-3, y), (x, y+pitch-3), (x+pitch-3, y+pitch-3)]
            if all((a-cx)**2 + (b-cy)**2 < (r-6)**2 for a, b in corners):
                dies.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{pitch-3}" height="{pitch-3}" rx="1.5" fill="#1d2640"/>'
                            f'<rect x="{x+3:.1f}" y="{y+3:.1f}" width="{(pitch-9)/2:.1f}" height="{(pitch-9)/2:.1f}" fill="#fff" opacity=".07"/>')
                if (gx, gy) == (2, -2):
                    hl = (x, y)
    hx, hy = hl
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in
                    [(0, "#ff7b72"), (.25, "#ffa657"), (.45, "#7ee787"), (.65, "#79c0ff"), (.85, "#d2a8ff"), (1, "#ff7b72")])
    defs = f'''<clipPath id="wf"><path d="{flat}"/></clipPath>
    <linearGradient id="rb" x1="0" y1="0" x2="1" y2="1">{stops}</linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <filter id="hg" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5"/></filter>
    <radialGradient id="wg" cx="{cx/W:.3f}" cy=".5" r=".32"><stop offset="0" stop-color="#d2a8ff" stop-opacity=".18"/><stop offset="1" stop-color="#d2a8ff" stop-opacity="0"/></radialGradient>'''
    art = f'''<rect width="{W}" height="{H}" fill="url(#wg)"/>
    <g clip-path="url(#wf)">
      <rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" fill="#121a2c"/>
      {"".join(dies)}
      <rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" fill="url(#rb)" opacity=".26"/>
      <rect class="shine" x="{cx-r-160}" y="{cy-r-40}" width="90" height="{2*r+80}" fill="url(#shine)"/>
    </g>
    <path d="{flat}" fill="none" stroke="#5a6283" stroke-width="1.5"/>
    <rect class="hl" x="{hx-4:.1f}" y="{hy-4:.1f}" width="{pitch+5}" height="{pitch+5}" rx="4" fill="none" stroke="{GO}" stroke-width="3" opacity=".5" filter="url(#hg)"/>
    <rect x="{hx-1:.1f}" y="{hy-1:.1f}" width="{pitch-1}" height="{pitch-1}" rx="2" fill="{GO}" fill-opacity=".55" stroke="{GO}" stroke-width="1.5"/>
    <path d="M{hx+pitch-1:.1f},{hy-1:.1f} L{hx+pitch+22:.1f},{hy-24:.1f} H{hx+pitch+52:.1f}" fill="none" stroke="{GO}" stroke-width="1"/>
    <text x="{hx+pitch+56:.1f}" y="{hy-20:.1f}" font-family="{MONO}" font-size="11" fill="{GO}">JG-9</text>'''
    css = '''.shine { animation: shine 6s ease-in-out infinite; }
      @keyframes shine { 0% { transform: translateX(0); } 60%, 100% { transform: translateX(420px); } }
      .hl { animation: blink 1.6s ease-in-out infinite; }'''
    return defs, art, css


def header():
    defs, art, css = wafer()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Hi, I'm Jason. i like pretty colored words. Always learning, currently building.">
  <defs>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1220"/><stop offset="1" stop-color="#101a2c"/></linearGradient>
    <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#fff" fill-opacity=".045"/></pattern>
    {defs}
    <style>
      .rise {{ opacity: 0; animation: rise .8s ease-out forwards; }}
      .d1 {{ animation-delay: .1s; }} .d2 {{ animation-delay: .4s; }} .d3 {{ animation-delay: 3.4s; }}
      @keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
      .ch {{ opacity: 0; animation: show .01s forwards; }}
      @keyframes show {{ to {{ opacity: 1; }} }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
      {css}
    </style>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#dots)"/>
    {art}
  </g>
  {intro()}
</svg>
'''


# ---------------------------------------------------------- section titles
def section(num, label):
    """Numbered ~/label heading with a rainbow trace, in mid-tones that read on light and dark."""
    w, h = 900, 44
    x0 = 34 + (len(label) + 2) * 21 * ADV + 4
    stops = "".join(f'<stop offset="{i/(len(TAG)-1):.2f}" stop-color="{c}"/>' for i, (_, c) in enumerate(TAG))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
  <defs><linearGradient id="rb" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient></defs>
  <text x="0" y="29" font-family="{MONO}" font-size="15" fill="{GO}">{num}</text>
  <text x="34" y="29" font-family="{MONO}" font-size="21" font-weight="700" fill="#8b949e"><tspan fill="#6e7681">~/</tspan>{label}</text>
  <path d="M{x0+16:.0f},22 L{w-90},22 L{w-76},10 L{w-14},10" fill="none" stroke="url(#rb)" stroke-opacity=".9" stroke-width="1.5"/>
  <circle cx="{x0+12:.0f}" cy="22" r="3.5" fill="none" stroke="{TAG[0][1]}" stroke-width="1.5"/>
  <circle cx="{w-10}" cy="10" r="3.5" fill="none" stroke="{TAG[-1][1]}" stroke-width="1.5"/>
</svg>
'''


SECTIONS = [("01", "about"), ("02", "toolbox"), ("03", "always-learning"),
            ("04", "currently-building"), ("05", "say-hi")]

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    with open(f"{out}/header.svg", "w") as f:
        f.write(header())
    for num, label in SECTIONS:
        with open(f"{out}/section-{label}.svg", "w") as f:
            f.write(section(num, label))
    print("ok")
