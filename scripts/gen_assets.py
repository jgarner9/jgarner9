"""Generates the profile SVGs. Usage: python3 scripts/gen_assets.py assets"""
import sys, os

OUT = sys.argv[1]
MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace'
SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Helvetica, Arial, sans-serif'
GO = "#00add8"

# ---------------------------------------------------------------- header
W, H = 900, 270
CX, CY = 718, 135          # chip centre
BODY = 120                 # chip body size
NPIN = 12                  # pins per side
PITCH = 8.0
PIN_L, PIN_W = 9, 4

def pins_and_traces():
    pins, traces, vias, pulses = [], [], [], []
    half = BODY / 2
    start = -PITCH * (NPIN - 1) / 2
    for side in range(4):
        for i in range(NPIN):
            o = start + i * PITCH
            # local coords: pin sticks out to +x from right edge, offset o along y
            # rotate per side
            def rot(x, y):
                return {0: (x, y), 1: (-y, x), 2: (-x, -y), 3: (y, -x)}[side]
            px0, py0 = rot(half, o)
            px1, py1 = rot(half + PIN_L, o)
            pins.append((px0, py0, px1, py1))
            # trace: straight out, 45deg fan, then straight to a via
            fan = (i - (NPIN - 1) / 2) * 3.2
            l1 = half + PIN_L + 6 + abs(i - (NPIN - 1) / 2) * 1.5
            l2 = l1 + abs(fan)
            reach = 38 if side in (1, 3) else 74
            stag = 10 if i % 2 else 0
            l3 = half + PIN_L + reach - stag - (8 if side in (1, 3) and i % 3 == 0 else 0)
            pts = [rot(half + PIN_L, o), rot(l1, o), rot(l2, o + fan), rot(l3, o + fan)]
            traces.append(pts)
            vias.append(rot(l3, o + fan))
            if (side * NPIN + i) % 4 == 1:
                pulses.append(pts)
    return pins, traces, vias, pulses

def path(pts):
    return "M" + " L".join(f"{CX+x:.1f},{CY+y:.1f}" for x, y in pts)


def components():
    """A few passives in the free corners of the board, plus silkscreen."""
    h = BODY / 2
    out = []
    def cap(x, y, rot, name):
        out.append(f'<g transform="translate({CX+x:.1f},{CY+y:.1f}) rotate({rot})">'
                   f'<rect x="-10" y="-5.5" width="20" height="11" rx="1.5" fill="none" stroke="#2c3e57"/>'
                   f'<rect x="-8" y="-4" width="16" height="8" rx="1" fill="#a8875a"/>'
                   f'<rect x="-8" y="-4" width="4" height="8" rx="1" fill="url(#pin)"/>'
                   f'<rect x="4" y="-4" width="4" height="8" rx="1" fill="url(#pin)"/></g>')
        out.append(f'<text x="{CX+x:.1f}" y="{CY+y-10:.1f}" text-anchor="middle" class="silk">{name}</text>')
    cap(h + 32, -h - 30, -45, "C1")
    cap(h + 48, -h - 14, -45, "C2")
    cap(-h - 34, h + 32, -45, "C3")
    # crystal oscillator, bottom-right corner
    x, y = CX + h + 36, CY + h + 30
    out.append(f'<g transform="translate({x:.1f},{y:.1f}) rotate(-45)">'
               f'<rect x="-17" y="-8" width="34" height="16" rx="8" fill="url(#pin)" stroke="#5d6b80"/>'
               f'<rect x="-13" y="-4.5" width="26" height="9" rx="4.5" fill="none" stroke="#9aa6b8" stroke-width=".8"/>'
               f'<text x="0" y="2.4" text-anchor="middle" font-family=\'{MONO}\' font-size="6" fill="#3b4656">16MHz</text></g>')
    out.append(f'<text x="{x+16:.1f}" y="{y+18:.1f}" class="silk">Y1</text>')
    out.append(f'<text x="{CX-h-26:.1f}" y="{CY-h-22:.1f}" class="silk">U1</text>')
    return "\n  ".join(out)

def header():
    pins, traces, vias, pulses = pins_and_traces()
    tr = "\n      ".join(f'<path d="{path(p)}"/>' for p in traces)
    vi = "\n      ".join(f'<circle cx="{CX+x:.1f}" cy="{CY+y:.1f}" r="2.6"/>' for x, y in vias)
    pu = "\n      ".join(
        f'<path class="pulse" style="animation-delay:{(k*0.37)%3:.2f}s" d="{path(p)}"/>'
        for k, p in enumerate(pulses))
    pn = "\n      ".join(
        f'<line x1="{CX+a:.1f}" y1="{CY+b:.1f}" x2="{CX+c:.1f}" y2="{CY+d:.1f}"/>'
        for a, b, c, d in pins)
    h = BODY / 2
    bx, by = CX - h, CY - h

    # die grid inside a window
    dw = 50
    dx, dy = CX - dw / 2, CY - dw / 2 + 8
    cells = []
    for r in range(6):
        for c in range(6):
            cls = ' class="cell"' if (r * 6 + c) % 7 == 3 else ""
            cells.append(f'<rect{cls} x="{dx+3+c*7.6:.1f}" y="{dy+3+r*7.6:.1f}" width="5.6" height="5.6" rx="1" style="animation-delay:{((r*6+c)*0.29)%2.5:.2f}s"/>')
    cells = "\n      ".join(cells)

    tag = [("i", "#ff7b72"), ("like", "#d2a8ff"), ("pretty", "#ffa657"),
           ("colored", "#7ee787"), ("words", "#79c0ff")]
    text = " ".join(t for t, _ in tag)
    n = len(text)
    tl = round(n * 13.2)
    tspans = " ".join(f'<tspan fill="{c}">{t}</tspan>' for t, c in tag)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Hi, I'm Jason. i like pretty colored words. Always learning, currently building.">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0b1220"/>
      <stop offset="1" stop-color="#101a2c"/>
    </linearGradient>
    <radialGradient id="glow" cx="{CX/W:.3f}" cy="0.5" r="0.4">
      <stop offset="0" stop-color="{GO}" stop-opacity="0.20"/>
      <stop offset="1" stop-color="{GO}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="body" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1e2738"/>
      <stop offset="1" stop-color="#121926"/>
    </linearGradient>
    <linearGradient id="pin" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#d7dee8"/>
      <stop offset="1" stop-color="#7f8ba0"/>
    </linearGradient>
    <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="#ffffff" fill-opacity="0.045"/>
    </pattern>
    <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.6"/></filter>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
    <clipPath id="type"><rect class="typer" x="60" y="158" width="{tl+2}" height="34"/></clipPath>
    <style>
      .rise {{ opacity: 0; animation: rise .8s ease-out forwards; }}
      .d1 {{ animation-delay: .1s; }} .d2 {{ animation-delay: .4s; }} .d3 {{ animation-delay: 3.6s; }}
      @keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
      .typer {{ transform-box: fill-box; transform-origin: left; transform: scaleX(0);
               animation: type {n*0.075:.2f}s steps({n}) 1.1s forwards; }}
      @keyframes type {{ to {{ transform: scaleX(1); }} }}
      .cursor {{ animation: move {n*0.075:.2f}s steps({n}) 1.1s forwards, blink 1s step-end infinite; }}
      @keyframes move {{ to {{ transform: translateX({tl+4}px); }} }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
      .pulse {{ fill: none; stroke: {GO}; stroke-width: 2; stroke-linecap: round;
               stroke-dasharray: 10 140; stroke-dashoffset: 150; animation: flow 3s linear infinite; }}
      @keyframes flow {{ to {{ stroke-dashoffset: 0; }} }}
      .cell {{ animation: cell 2.5s ease-in-out infinite; }}
      @keyframes cell {{ 0%, 100% {{ fill: #1b2a40; }} 50% {{ fill: {GO}; }} }}
      .silk {{ font-family: {MONO}; font-size: 8px; fill: #4a5d78; letter-spacing: 1px; }}
      .led {{ animation: led 1.6s ease-in-out infinite; }}
      @keyframes led {{ 50% {{ opacity: .25; }} }}
    </style>
  </defs>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#dots)"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>

    <!-- circuit traces -->
    <g fill="none" stroke="#22344d" stroke-width="1.6" stroke-linejoin="round">
      {tr}
    </g>
    <g fill="#0b1220" stroke="#3a5172" stroke-width="1.4">
      {vi}
    </g>
    <g filter="url(#blur)" opacity=".9">
      {pu}
    </g>
    <g>
      {pu}
    </g>
  </g>

  <!-- left: intro -->
  <text class="rise d1" x="60" y="88" font-family='{MONO}' font-size="16" fill="#7ee787">$ whoami</text>
  <text class="rise d2" x="58" y="140" font-family='{SANS}' font-size="46" font-weight="700" fill="#e6edf3">Hi, I'm Jason<tspan fill="{GO}">.</tspan></text>
  <g clip-path="url(#type)">
    <text x="60" y="182" font-family='{MONO}' font-size="22" textLength="{tl}" lengthAdjust="spacingAndGlyphs">{tspans}</text>
  </g>
  <rect class="cursor" x="62" y="164" width="11" height="24" fill="{GO}"/>
  <text class="rise d3" x="60" y="218" font-family='{MONO}' font-size="14" fill="#5b6b82">// always learning, currently building</text>

  <!-- right: microchip -->
  {components()}
  <g stroke="url(#pin)" stroke-width="{PIN_W}" stroke-linecap="butt">
      {pn}
  </g>
  <rect x="{bx+3}" y="{by+4}" width="{BODY}" height="{BODY}" rx="7" fill="#000" opacity=".35"/>
  <rect x="{bx}" y="{by}" width="{BODY}" height="{BODY}" rx="7" fill="url(#body)" stroke="#33445f" stroke-width="1.5"/>
  <rect x="{bx+6}" y="{by+6}" width="{BODY-12}" height="{BODY-12}" rx="4" fill="none" stroke="#2a3850" stroke-width="1"/>
  <path d="M{bx+BODY-16},{by} L{bx+BODY},{by+16}" stroke="#33445f" stroke-width="1.5"/>
  <circle cx="{bx+14}" cy="{by+14}" r="3.5" fill="#0b1220" stroke="#3a5172"/>
  <circle class="led" cx="{bx+BODY-14}" cy="{by+BODY-14}" r="2.4" fill="#3fb950"/>
  <text x="{CX}" y="{by+27}" text-anchor="middle" font-family='{MONO}' font-size="11" font-weight="700" fill="#9fb3c8" letter-spacing="1.5">JG-9</text>
  <rect x="{dx}" y="{dy}" width="{dw}" height="{dw}" rx="3" fill="#0d1626" stroke="#2a3850"/>
  <g fill="#1b2a40">
      {cells}
  </g>
  <text x="{CX}" y="{by+BODY-9}" text-anchor="middle" font-family='{MONO}' font-size="6.5" fill="#56677f" letter-spacing="1">REV.2026 · GO</text>
</svg>
'''

# ---------------------------------------------------------- section titles
def section(num, label):
    w, h = 900, 44
    lab = f"{num}"
    x0 = 34 + (len(label) + 2) * 12.65 + 4  # monospace advance at 21px
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
  <text x="0" y="29" font-family='{MONO}' font-size="15" fill="{GO}">{lab}</text>
  <text x="34" y="29" font-family='{MONO}' font-size="21" font-weight="700" fill="#8b949e"><tspan fill="#6e7681">~/</tspan>{label}</text>
  <g fill="none" stroke="#6e7681" stroke-opacity=".45" stroke-width="1.5">
    <path d="M{x0+16:.0f},22 L{w-90},22 L{w-76},10 L{w-14},10"/>
  </g>
  <circle cx="{x0+12:.0f}" cy="22" r="3.5" fill="none" stroke="{GO}" stroke-width="1.5"/>
  <circle cx="{w-10}" cy="10" r="3.5" fill="none" stroke="{GO}" stroke-width="1.5"/>
</svg>
'''

SECTIONS = [("01", "about"), ("02", "toolbox"), ("03", "always-learning"),
            ("04", "currently-building"), ("05", "say-hi")]

os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/header.svg", "w").write(header())
for num, label in SECTIONS:
    open(f"{OUT}/section-{label}.svg", "w").write(section(num, label))
print("ok")
