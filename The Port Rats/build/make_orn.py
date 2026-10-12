"""Ornaments for THE PORT RATS. All hand-built SVG, single ink colour."""
import math, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
INK = "#1d1a17"


def rope(x0, x1, y, amp=2.4, period=9.0, w=1.1):
    """Twisted-rope line: two interleaved sine strands plus lay strokes."""
    paths = []
    for phase in (0, math.pi):
        pts = []
        x = x0
        while x <= x1 + 0.01:
            t = (x - x0) / period * 2 * math.pi + phase
            pts.append(f"{x:.2f},{y + amp * math.sin(t):.2f}")
            x += 0.5
        paths.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round"/>')
    # the lay: short slanted strokes where strands cross
    x = x0 + period / 4
    while x < x1:
        paths.append(f'<line x1="{x-1.3:.2f}" y1="{y+amp:.2f}" x2="{x+1.3:.2f}" y2="{y-amp:.2f}" stroke="{INK}" stroke-width="{w*0.8}" stroke-linecap="round"/>')
        x += period / 2
    return "\n".join(paths)


def anchor(cx, top, s=1.0, w=1.6):
    """Fouled-free anchor, ring at top. s = scale (1.0 ≈ 30 units tall)."""
    def p(x, y):
        return f"{cx + x*s:.2f},{top + y*s:.2f}"
    return f'''
<circle cx="{cx}" cy="{top+3.2*s:.2f}" r="{3.0*s:.2f}" fill="none" stroke="{INK}" stroke-width="{w}"/>
<line x1="{cx-8*s:.2f}" y1="{top+9*s:.2f}" x2="{cx+8*s:.2f}" y2="{top+9*s:.2f}" stroke="{INK}" stroke-width="{w*1.3}" stroke-linecap="round"/>
<circle cx="{cx-8.6*s:.2f}" cy="{top+9*s:.2f}" r="{1.3*s:.2f}" fill="{INK}"/>
<circle cx="{cx+8.6*s:.2f}" cy="{top+9*s:.2f}" r="{1.3*s:.2f}" fill="{INK}"/>
<line x1="{cx}" y1="{top+6.2*s:.2f}" x2="{cx}" y2="{top+30*s:.2f}" stroke="{INK}" stroke-width="{w*1.4}" stroke-linecap="round"/>
<path d="M {p(-12,21)} Q {p(-11,31)} {p(0,31)} Q {p(11,31)} {p(12,21)}" fill="none" stroke="{INK}" stroke-width="{w*1.3}" stroke-linecap="round"/>
<path d="M {p(-12,17.5)} L {p(-15.5,23.5)} L {p(-9.5,23)} Z" fill="{INK}"/>
<path d="M {p(12,17.5)} L {p(15.5,23.5)} L {p(9.5,23)} Z" fill="{INK}"/>
<circle cx="{cx}" cy="{top+30.5*s:.2f}" r="{1.6*s:.2f}" fill="{INK}"/>'''


def rat(ox, oy, s=1.0, flip=False):
    """Side-profile dock rat, nose right, tail curling into a hook. ~110x40 units."""
    tr = f'translate({ox},{oy}) scale({-s if flip else s},{s})'
    return f'''<g transform="{tr}">
<path d="M 30 33 C 28 20, 44 11, 62 12 C 74 13, 82 17, 90 22 C 96 25, 102 28, 107 30.5
         C 108.5 31.3, 108 33, 106 33.2 C 100 33.8, 94 34.2, 88 35 C 80 37.5, 70 38, 56 38
         C 44 38, 32 38, 30 33 Z" fill="{INK}"/>
<path d="M 84 19 C 82 12, 87 8.5, 91 10.5 C 94 12.5, 92 18, 88 20.5 Z" fill="{INK}"/>
<path d="M 85.8 17.6 C 85.5 13.5, 88 11.8, 89.8 12.6 C 91 13.4, 90 16.5, 88 18.4 Z" fill="#f4efe6"/>
<circle cx="95" cy="25.2" r="1.25" fill="#f4efe6"/>
<path d="M 107 31.2 L 116 28.5 M 107 31.8 L 116 32.6 M 106.5 32.4 L 114 35.5" stroke="{INK}" stroke-width="0.45" stroke-linecap="round"/>
<path d="M 48 37 L 46 42 L 51 42 M 76 36.5 L 79 42 L 83 42 M 60 37.5 L 58 42 M 89 34.5 L 92 41 L 95 41"
      fill="none" stroke="{INK}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 31 33 C 18 36, 6 38, -4 34 C -12 31, -13 23, -7 20.5 C -2.5 18.8, 1 22.5, -2 25"
      fill="none" stroke="{INK}" stroke-width="1.7" stroke-linecap="round"/>
</g>'''


def ash_leaf(cx, cy, s=1.0, rot=0):
    """Pinnate ash leaf: rachis + 3 leaflet pairs + terminal leaflet. Points up."""
    g = [f'<g transform="translate({cx},{cy}) rotate({rot}) scale({s})">',
         f'<path d="M 0 22 L 0 -12" stroke="{INK}" stroke-width="1.1" stroke-linecap="round"/>']
    leaflet = "M 0 0 C 4 -3.2, 12 -3.4, 17 0 C 12 3.4, 4 3.2, 0 0 Z"
    for i, y in enumerate((12, 2, -8)):
        ln = 1.0 - i * 0.06
        for side in (1, -1):
            ang = -22 if side == 1 else -158
            g.append(f'<path d="{leaflet}" transform="translate(0,{y}) rotate({ang}) scale({ln})" fill="{INK}"/>')
    g.append(f'<path d="{leaflet}" transform="translate(0,-11) rotate(-90) scale(0.95)" fill="{INK}"/>')
    g.append('</g>')
    return "\n".join(g)


def svg(w, h, body, name):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n{body}\n</svg>\n'
    open(os.path.join(OUT, name), "w").write(s)
    return s


# 1. Scene break — "The Mooring": anchor riding a twisted hawser, eyelets at each end
mid = 120
body = rope(22, mid - 18, 20) + rope(mid + 18, 218, 20) + anchor(mid, 4, s=1.0)
body += f'<circle cx="17" cy="20" r="4" fill="none" stroke="{INK}" stroke-width="1.2"/>'
body += f'<circle cx="223" cy="20" r="4" fill="none" stroke="{INK}" stroke-width="1.2"/>'
body += f'<circle cx="8" cy="20" r="1.4" fill="{INK}"/><circle cx="232" cy="20" r="1.4" fill="{INK}"/>'
svg(240, 40, body, "mooring.svg")

# 2. Chapter head — "Rat on the Line": a rat walking the mooring line
body = rope(4, 236, 46, amp=2.2, period=8.5, w=1.0)
body += f'<circle cx="2" cy="46" r="1.6" fill="{INK}"/><circle cx="238" cy="46" r="1.6" fill="{INK}"/>'
body += rat(70, 4.6, s=0.95)
svg(240, 52, body, "ratline.svg")

# 3. Tailpiece — the Ashburn ash leaf between two short rules
body = ash_leaf(60, 28, s=0.85)
body += f'<path d="M 4 26 L 40 26" stroke="{INK}" stroke-width="0.9"/><path d="M 80 26 L 116 26" stroke="{INK}" stroke-width="0.9"/>'
body += f'<path d="M 40 26 l 4 -2.5 l 0 5 z" fill="{INK}"/><path d="M 80 26 l -4 -2.5 l 0 5 z" fill="{INK}"/>'
svg(120, 52, body, "ashleaf.svg")

# 4. Title emblem — two rats nose to nose over a crossed anchor, rope underline
body = anchor(150, 4, s=1.45, w=1.9)
body += rat(16, 19.5, s=0.88)
body += rat(284, 19.5, s=0.88, flip=True)
body += rope(12, 288, 58, amp=2.2, period=8.5, w=1.0)
body += f'<circle cx="7" cy="58" r="2" fill="{INK}"/><circle cx="293" cy="58" r="2" fill="{INK}"/>'
svg(300, 66, body, "emblem.svg")

print("ok")
