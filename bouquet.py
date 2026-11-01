"""İsme özel kasımpatı buketi üreten SVG çizici (aynı isim → aynı buket)."""
import hashlib
import html
import random

from markupsafe import Markup

# (dış yaprak rengi, merkeze yakın yaprak rengi)
PALETTES = [
    {"petals": [("#fbe3ea", "#e58fb0"), ("#f7cadb", "#d86f9d"), ("#fdeef2", "#efa6c0")],
     "paper": "#efe3d3", "ribbon": "#c0587f"},   # pudra pembe
    {"petals": [("#f6bfd2", "#c85a8c"), ("#f9d2e0", "#d9709f"), ("#eeaac6", "#b24a80")],
     "paper": "#efe3d3", "ribbon": "#9b3f6c"},   # gül pembe
    {"petals": [("#eadcf7", "#a67fd0"), ("#f1e8fa", "#b896dc"), ("#dcc8f1", "#8d63bd")],
     "paper": "#e6dcf0", "ribbon": "#7f58a6"},   # lila
    {"petals": [("#e3cdf3", "#9a62c4"), ("#efdcfa", "#ad7ad2"), ("#d6b5ee", "#8149ae")],
     "paper": "#efe3d3", "ribbon": "#c0587f"},   # orkide
    {"petals": [("#fff0b8", "#f2c14e"), ("#fdf3c8", "#e8b23a"), ("#ffe79a", "#e0a526")],
     "paper": "#efe3d3", "ribbon": "#a8477f"},   # sarı
    {"petals": [("#ffe0cc", "#f29b6b"), ("#ffd2b8", "#e8814f"), ("#fff0e4", "#f5b48a")],
     "paper": "#e6dcf0", "ribbon": "#a8477f"},   # şeftali
    {"petals": [("#ffffff", "#efe1cf"), ("#fffaf4", "#f0d9c2"), ("#fdf6ee", "#e8d3bd")],
     "paper": "#e6dcf0", "ribbon": "#c0587f"},   # beyaz-krem
    {"petals": [("#f3a6b4", "#b5253f"), ("#e98a9c", "#9c1f3a"), ("#f7c0ca", "#c23552")],
     "paper": "#efe3d3", "ribbon": "#7a1f3d"},   # bordo
    {"petals": [("#ffc9c2", "#ef6f6c"), ("#ffd9d3", "#e5605e"), ("#ffb8ae", "#d9534f")],
     "paper": "#efe3d3", "ribbon": "#8c3b63"},   # mercan
]
# Her palet için yanında en güzel duran ikinci palet
COMPANION = [2, 3, 0, 1, 6, 6, 5, 6, 6]
GREENS = ["#7fa27a", "#6b9170", "#93b58a"]
BIG = [(300, 175, 112), (185, 255, 100), (415, 255, 100), (105, 380, 88),
       (495, 380, 88), (255, 345, 92), (350, 360, 92)]
SMALL = [(210, 150, 50), (400, 145, 46)]
PLUM = "#5a1f4a"
LEAF = ("M0,0 C5,-6 9,-12 17,-13 C19,-8 24,-9 27,-15 C33,-17 36,-10 41,-12 C47,-13 53,-6 62,0 "
        "C53,6 47,13 41,12 C36,10 33,17 27,15 C24,9 19,8 17,13 C9,12 5,6 0,0Z")
SHADOW = (f'<radialGradient id="shd"><stop offset="0" stop-color="{PLUM}" stop-opacity=".30"/>'
          f'<stop offset=".7" stop-color="{PLUM}" stop-opacity=".18"/>'
          f'<stop offset="1" stop-color="{PLUM}" stop-opacity="0"/></radialGradient>')


def _seed(name):
    return int(hashlib.sha256(name.casefold().encode()).hexdigest(), 16)


def _mix(a, b, t):
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(pa, pb))


def _petal(L, w, b):
    """Dibi dar, ucu yuvarlak, kaşık biçimli kasımpatı yaprağı."""
    return (f"M0,{-b:.1f} C{w * .45:.1f},{-L * .22:.1f} {w:.1f},{-L * .5:.1f} {w * .9:.1f},{-L * .82:.1f} "
            f"C{w * .75:.1f},{-L:.1f} {-w * .75:.1f},{-L:.1f} {-w * .9:.1f},{-L * .82:.1f} "
            f"C{-w:.1f},{-L * .5:.1f} {-w * .45:.1f},{-L * .22:.1f} 0,{-b:.1f}Z")


def _flower(rng, fid, x, y, size, colors, delay, layers):
    outer, inner = colors
    defs = [f'<radialGradient id="h{fid}" cx=".38" cy=".32" r=".7">'
            f'<stop offset="0" stop-color="#fff" stop-opacity=".38"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>']
    uses = []
    for i in range(layers):
        t = i / (layers - 1)
        length = size * (1 - 0.8 * t)
        width = length * 0.11 + 1.5
        count = max(6, 24 - 2 * i)
        col = _mix(outer, inner, t ** 0.8)
        tip, root = _mix(col, "#ffffff", .3), _mix(col, PLUM, .35)
        gid, pid = f"g{fid}_{i}", f"p{fid}_{i}"
        defs.append(f'<linearGradient id="{gid}" x1="0" y1="1" x2="0" y2="0">'
                    f'<stop offset="0" stop-color="{root}"/><stop offset="1" stop-color="{tip}"/></linearGradient>')
        defs.append(f'<g id="{pid}"><path d="{_petal(length, width, length * .08)}" fill="url(#{gid})" '
                    f'stroke="{root}" stroke-opacity=".45" stroke-width=".6"/>'
                    f'<path d="M0,{-length * .12:.1f} L0,{-length * .8:.1f}" stroke="#fff" '
                    f'stroke-opacity=".28" stroke-width=".7" fill="none"/></g>')
        step = 360 / count
        offset = (i % 2) * step / 2 + rng.uniform(0, step / 2)
        for k in range(count):
            a = offset + k * step + rng.uniform(-3, 3)
            sx, sy = rng.uniform(.9, 1.1), rng.uniform(.9, 1.08)
            uses.append(f'<use href="#{pid}" transform="rotate({a:.1f}) scale({sx:.2f} {sy:.2f})"/>')
    core = f'<circle r="{size * .06:.1f}" fill="{_mix(inner, PLUM, .4)}"/>'
    shine = f'<circle r="{size * .85:.1f}" fill="url(#h{fid})"/>'
    tilt, squash = rng.uniform(0, 360), rng.uniform(.88, .97)
    return (f'<g transform="translate({x} {y})"><g class="bloom" style="--d:{delay:.2f}s">'
            f'<circle cx="4" cy="9" r="{size * 1.02:.1f}" fill="url(#shd)"/>'
            f'<g transform="rotate({tilt:.0f}) scale(1 {squash:.2f})"><defs>{"".join(defs)}</defs>'
            f'{"".join(uses)}{core}{shine}</g></g></g>')


def _stem(rng, x, y):
    gx, gy = 300 + rng.uniform(-14, 14), 655
    cx = x + (gx - x) * .25 + rng.uniform(-18, 18)
    cy = y + (gy - y) * .55
    t = rng.uniform(.5, .66)
    px = (1 - t) ** 2 * x + 2 * (1 - t) * t * cx + t * t * gx
    py = (1 - t) ** 2 * y + 2 * (1 - t) * t * cy + t * t * gy
    angle = -90 + rng.choice((-1, 1)) * rng.uniform(35, 65)
    leaf = (f'<g transform="translate({px:.1f} {py:.1f}) rotate({angle:.0f}) scale({rng.uniform(.9, 1.3):.2f})">'
            f'<path d="{LEAF}" fill="{rng.choice(GREENS)}"/>'
            f'<path d="M0,0 L56,0" stroke="#fff" stroke-opacity=".3" stroke-width="1" fill="none"/></g>')
    stem = (f'<path d="M{x},{y} Q{cx:.1f},{cy:.1f} {gx:.1f},{gy}" fill="none" '
            f'stroke="#6f9a6c" stroke-width="4.5" stroke-linecap="round"/>')
    return stem + leaf


def _wrap(palette):
    paper, ribbon = palette["paper"], palette["ribbon"]
    return f'''
<path d="M150,565 Q300,535 450,565 L322,752 Q300,764 278,752Z" fill="{paper}"/>
<path d="M150,565 Q300,535 450,565 L330,640 Q300,600 270,640Z" fill="#fff" opacity=".3"/>
<path d="M278,752 L300,600 L322,752" fill="none" stroke="#000" stroke-opacity=".1"/>
<path d="M208,648 Q300,672 392,648 L386,672 Q300,696 214,672Z" fill="{ribbon}"/>
<path d="M300,664 C262,628 232,650 258,676 C270,684 290,676 300,664Z" fill="{ribbon}"/>
<path d="M300,664 C338,628 368,650 342,676 C330,684 310,676 300,664Z" fill="{ribbon}"/>
<path d="M296,670 L280,712 L292,706 L298,718 L304,674Z" fill="{ribbon}"/>
<path d="M304,670 L320,712 L308,706 L302,718 L296,674Z" fill="{ribbon}"/>
<circle cx="300" cy="666" r="7" fill="{_mix(ribbon, '#000000', .2)}"/>'''


def build_bouquet(name, animate=False, seed=None):
    """Buket SVG'si üretir. seed verilmezse isimden türetilir (aynı isim → aynı buket)."""
    seed = _seed(name) if seed is None else seed
    rng = random.Random(seed)
    idx = seed % len(PALETTES)
    main, accent = PALETTES[idx], PALETTES[COMPANION[idx]]

    spots = [(x + rng.uniform(-10, 10), y + rng.uniform(-8, 8), s * rng.uniform(.92, 1.08), s < 60)
             for x, y, s in SMALL + BIG]
    spots.sort(key=lambda p: p[1])

    stems = "".join(_stem(rng, round(x), round(y)) for x, y, _, _ in spots)
    flowers = []
    for i, (x, y, s, small) in enumerate(spots):
        pal = accent if i % 3 == 2 else main
        layers = 6 if small else rng.randint(9, 11)
        flowers.append(_flower(rng, i, round(x), round(y), s, rng.choice(pal["petals"]), .5 + i * .16, layers))

    cls = ' class="animate"' if animate else ""
    label = html.escape(f"{name} için kasımpatı buketi")
    return Markup(f'<svg id="buket"{cls} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 780" '
                  f'width="600" height="780" role="img" aria-label="{label}"><defs>{SHADOW}</defs>'
                  f'<g class="stems">{stems}</g>{_wrap(main)}{"".join(flowers)}</svg>')


def build_stamp(name, seed=None):
    """Mesaj kartının üstünde duran tek bir küçük kasımpatı."""
    seed = _seed(name) if seed is None else seed
    rng = random.Random(seed ^ 0x5EED)
    pal = PALETTES[seed % len(PALETTES)]
    flower = _flower(rng, "s", 0, 0, 50, pal["petals"][0], 0, 9)
    return Markup(f'<svg class="stamp" viewBox="-62 -62 124 124" width="84" height="84" '
                  f'aria-hidden="true"><defs>{SHADOW}</defs>{flower}</svg>')