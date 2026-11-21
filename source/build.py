"""Build the Darkroom theme for T3 Code: darkroom.json (+ SVG previews in assets/svg).

A red-safelight darkroom. While a turn runs, a print develops in the tray and a
seven-segment timer counts; wet prints hang on a line. At rest everything is
finished and still.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
MONO = "ui-monospace,Menlo,monospace"

RED = "#ff5a47"        # safelight
RED_RGB = "255,90,71"
PAPER = "#cdb2a6"      # print paper under red light
CANVAS = "#170b0c"


def f(x):
    s = f"{x:.1f}"
    return s[:-2] if s.endswith(".0") else s


def data_uri(svg):
    out = svg.replace("%", "%25").replace("#", "%23").replace('"', "'").replace("<", "%3C").replace(">", "%3E")
    return 'url("data:image/svg+xml,' + out + '")'


# ------------------------------------------------------------------ the photograph
# One scene in a 200x190 box: low sun behind a ridge, a lone tree on a hill.
SCENE_DEFS = (
    "<linearGradient id='sk' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#3a2827'/>"
    "<stop offset='.55' stop-color='#86695f'/><stop offset='.72' stop-color='#e8d3c8'/></linearGradient>"
    "<radialGradient id='hl'><stop offset='0' stop-color='#fff4ee' stop-opacity='.95'/>"
    "<stop offset='.4' stop-color='#fff4ee' stop-opacity='.35'/><stop offset='1' stop-color='#fff4ee' stop-opacity='0'/></radialGradient>"
    "<linearGradient id='gl' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#fff' stop-opacity='.26'/>"
    "<stop offset='.4' stop-color='#fff' stop-opacity='0'/></linearGradient>"
)


def scene(cls=True):
    c = (lambda n: f" class='{n}'") if cls else (lambda n: "")
    return (
        f"<g{c('l1')}><rect width='200' height='190' fill='url(#sk)'/>"
        "<circle cx='128' cy='126' r='74' fill='url(#hl)'/><circle cx='128' cy='126' r='15' fill='#fff7f1'/>"
        "<ellipse cx='56' cy='66' rx='50' ry='2.6' fill='#fff' fill-opacity='.16'/>"
        "<ellipse cx='150' cy='84' rx='38' ry='2.2' fill='#fff' fill-opacity='.14'/>"
        "<path d='M148 52l4-3 4 3M160 44l3-2.4 3 2.4M136 40l3-2.4 3 2.4' fill='none' stroke='#2a1816' stroke-width='1.3' stroke-linecap='round'/></g>"
        f"<g{c('l2')}><path d='M0 129C30 113 52 122 82 115S132 124 160 113S190 119 200 115V190H0Z' fill='#7a6159'/>"
        "<path d='M0 142C40 129 72 144 112 135S170 139 200 131V190H0Z' fill='#4b3834'/></g>"
        f"<g{c('l3')}><path d='M0 162C50 149 90 160 130 157S185 151 200 155V190H0Z' fill='#190e0d'/>"
        "<path d='M51 160C52 146 52 134 53 120L55 120C55 134 56 148 57 160Z' fill='#110908'/>"
        "<path d='M54 130L40 118M54 126L68 114' stroke='#110908' stroke-width='2' fill='none'/>"
        "<g fill='#110908'><circle cx='54' cy='106' r='14'/><circle cx='42' cy='113' r='9'/><circle cx='66' cy='112' r='10'/><circle cx='54' cy='96' r='9'/></g></g>"
        "<rect width='200' height='190' fill='url(#gl)'/>"
    )


def pitch_dark():  # not used; kept for symmetry of layers
    return ""


# ------------------------------------------------------------------ seven-segment digits
DW, DH, DT = 46, 66, 8
SEG = {"a": "abcdef"}  # placeholder replaced below
DIGITS = ["abcdef", "bc", "abged", "abgcd", "fgbc", "afgcd", "afgedc", "abc", "abcdefg", "abcdfg"]


def hseg(x0, x1, yc):
    t = DT / 2
    pts = [(x0, yc), (x0 + t, yc - t), (x1 - t, yc - t), (x1, yc), (x1 - t, yc + t), (x0 + t, yc + t)]
    return " ".join(f"{f(x)},{f(y)}" for x, y in pts)


def vseg(xc, y0, y1):
    t = DT / 2
    pts = [(xc, y0), (xc + t, y0 + t), (xc + t, y1 - t), (xc, y1), (xc - t, y1 - t), (xc - t, y0 + t)]
    return " ".join(f"{f(x)},{f(y)}" for x, y in pts)


def seg_poly(s):
    t, w, h, g = DT / 2, DW, DH, 1.6
    return {
        "a": hseg(t + g, w - t - g, t), "d": hseg(t + g, w - t - g, h - t), "g": hseg(t + g, w - t - g, h / 2),
        "b": vseg(w - t, t + g, h / 2 - g), "c": vseg(w - t, h / 2 + g, h - t - g),
        "f": vseg(t, t + g, h / 2 - g), "e": vseg(t, h / 2 + g, h - t - g),
    }[s]


def glyph(n):
    return "".join(f"<polygon points='{seg_poly(s)}'/>" for s in DIGITS[n])


GHOST = "".join(f"<polygon points='{seg_poly(s)}'/>" for s in "abcdefg")
PITCH = DH + 24


def digit_slot(x, y, count, dur, static, tens_static=False):
    """A digit window. Animated: a reel of `count` glyphs stepping once per `dur/count` seconds."""
    ghost = f"<g class='gh'>{GHOST}</g>"
    if static or tens_static:
        return f"<g transform='translate({x} {y})'>{ghost}<g class='lit'>{glyph(0)}</g></g>"
    reel = "".join(f"<g transform='translate(0 {i * PITCH})'>{glyph(i)}</g>" for i in range(count))
    name = f"r{count}x{int(dur)}"
    return (f"<g transform='translate({x} {y})'>{ghost}<svg width='{DW}' height='{DH}' viewBox='0 0 {DW} {DH}'>"
            f"<g class='lit reel' style='animation:{name} {dur}s steps({count}) infinite'>{reel}</g></svg></g>"), (
        f"@keyframes {name}{{to{{transform:translateY({-count * PITCH}px)}}}}")


# ------------------------------------------------------------------ tray + timer
def tray_svg(static, dock=False, fx=False):
    cx = 170
    css = [
        ".gh{fill:#ff5a47;fill-opacity:.075}.lit{fill:#e8402f}",
        f".pp{{fill:{PAPER}}}",
        "text{font:600 10px " + MONO + ";letter-spacing:.2em;fill:#c9a9a0}",
    ]
    slots = ""
    xs = [40, 94, 190, 244]  # m10 m1 : s10 s1
    if static:
        for x in xs:
            slots += digit_slot(x, 424, 0, 0, True)
        css.append(".lit{fill-opacity:.3}")
        if fx:
            css.append(""
                       ".fx{fill:#ffd9cf;fill-opacity:0;animation:fx 1.3s ease-in-out .15s 1}"
                       "@keyframes fx{0%{fill-opacity:0;transform:translateX(-150px)}35%{fill-opacity:.34}100%{fill-opacity:0;transform:translateX(150px)}}")
    else:
        kfs = []
        specs = [(xs[0], 1, 1, True), (xs[1], 10, 600, False), (xs[2], 6, 60, False), (xs[3], 10, 10, False)]
        for x, n, d, st in specs:
            r = digit_slot(x, 424, n, d, False, st)
            if isinstance(r, tuple):
                slots += r[0]; kfs.append(r[1])
            else:
                slots += r
        css += kfs
    colon_cls = ""
    colon = (f"<g class='lit{colon_cls}'><rect x='158' y='438' width='9' height='9' rx='1'/><rect x='158' y='462' width='9' height='9' rx='1'/></g>")
    if not static:
        css.append(
            ".lyr{opacity:0}.a1{animation:d1 30s steps(45) 1 forwards}.a2{animation:d2 30s steps(45) 1 forwards}.a3{animation:d3 30s steps(45) 1 forwards}"
            "@keyframes d1{0%,3%{opacity:0}40%{opacity:.88}100%{opacity:1}}"
            "@keyframes d2{0%,12%{opacity:0}55%{opacity:.9}100%{opacity:1}}"
            "@keyframes d3{0%,26%{opacity:0}75%,100%{opacity:1}}"
            ".sh{fill:#ff8a78;fill-opacity:0;animation:sh 9s steps(10) infinite}.sh.b{animation-delay:-4.5s;animation-duration:11s}"
            "@keyframes sh{0%,100%{fill-opacity:0;transform:translateX(-26px)}50%{fill-opacity:.2;transform:translateX(26px)}}"
            ".rk{transform-origin:170px 188px;animation:rk 8s steps(12) infinite}@keyframes rk{0%,100%{rotate:0deg}50%{rotate:.6deg}}"
            "@media (prefers-reduced-motion:reduce){*{animation:none!important}.lyr{opacity:1}}"
        )
    L = (lambda n: f"lyr a{n}") if not static else (lambda n: "")
    # scene is 200x190, drawn at (72,70) inside a 220x270 print
    photo = (
        "<g transform='rotate(-2.2 170 188)'>"
        f"<rect class='pp' x='60' y='58' width='220' height='250' rx='2'/>"
        "<rect x='60' y='58' width='220' height='250' rx='2' fill='none' stroke='#fff' stroke-opacity='.28'/>"
        "<svg x='72' y='70' width='196' height='186' viewBox='0 0 200 190' preserveAspectRatio='xMidYMid slice'>"
        + scene_layers(L) + "</svg>"
        "<rect x='72' y='70' width='196' height='186' fill='#170b0c' fill-opacity='.16'/>"
        + ("" if dock else "<text x='72' y='282' style='font:600 9px " + MONO + ";letter-spacing:.18em;fill:#5b3e38'>FRAME 07 · 8×10</text>"
        "<text x='72' y='296' style='font:500 8px " + MONO + ";letter-spacing:.14em;fill:#6f504a'>TREE ON HILL, LOW SUN</text>") + "</g>"
    )
    if static and fx:
        photo += "<clipPath id='pcl'><rect x='60' y='58' width='220' height='250'/></clipPath><g clip-path='url(#pcl)'><g transform='skewX(-12)'><rect class='fx' x='200' y='58' width='34' height='250'/></g></g>"
    if not static:
        photo = "<g class='rk'>" + photo + "</g>"
    rings = "" if static else (
        "<ellipse class='sh' cx='170' cy='318' rx='96' ry='5'/><ellipse class='sh b' cx='170' cy='34' rx='84' ry='4'/>"
        "")
    body = (
        "<defs>" + SCENE_DEFS +
        "<linearGradient id='tr' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#3b1a1c'/><stop offset='1' stop-color='#1e0e0f'/></linearGradient>"
        "<linearGradient id='lq' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#4a1d1d'/><stop offset='1' stop-color='#1a0a0b'/></linearGradient>"
        "<radialGradient id='lamp' cx='.5' cy='.45' r='.7'><stop offset='0' stop-color='#ff5a47' stop-opacity='.24'/><stop offset='1' stop-color='#ff5a47' stop-opacity='0'/></radialGradient></defs>"
        # tray
        "<rect x='4' y='6' width='332' height='364' rx='20' fill='#0a0505'/>"
        "<rect x='4' y='2' width='332' height='364' rx='20' fill='url(#tr)' stroke='#5b2a2c' stroke-width='2'/>"
        "<rect x='20' y='18' width='300' height='332' rx='12' fill='url(#lq)' stroke='#0c0505' stroke-width='3'/>"
        "<ellipse cx='170' cy='170' rx='140' ry='150' fill='url(#lamp)'/>"
        "<path d='M34 50C60 40 100 36 140 38' fill='none' stroke='#ff8a78' stroke-opacity='.16' stroke-width='2' stroke-linecap='round'/>"
        + rings + photo
        + ("" if dock else "<text x='34' y='346' style='font-size:9px'>DEVELOPER · 20°C</text>")
        +        # timer panel
        "<rect x='4' y='388' width='332' height='128' rx='14' fill='#0f0708' stroke='#4a2326' stroke-width='2'/>"
        "<rect x='20' y='408' width='300' height='92' rx='6' fill='#050202' stroke='#2a1213'/>"
        + ("" if dock else "<text x='22' y='402' style='font-size:9px'>TIMER</text><text x='318' y='402' text-anchor='end' style='font-size:9px'>MIN  SEC</text>")
        + slots + colon
    )
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 340 520'><style>{''.join(css)}</style>{body}</svg>"


def scene_layers(L):
    s = scene(cls=False)
    # tag the three tone layers so the develop animation can stagger them
    parts = s.split("<g>")
    out = parts[0]
    for i, p in enumerate(parts[1:], 1):
        out += f"<g class='{L(i)}'>" + p
    return out


# ------------------------------------------------------------------ the clothesline
def cord_pt(p0, p1, p2, t):
    return (
        (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1],
    )


def line_svg(static):
    cords = [((-10, 30), (170, 84), (350, 32)), ((-10, 292), (170, 340), (350, 290))]
    # (cord, t, print w, print h, tilt, crop viewBox, sway a, sway b, dur, delay)
    prints = [
        (0, .17, 86, 108, -2.0, "30 60 130 125", -2.6, 1.2, 7.5, 0.0),
        (0, .50, 90, 114, 1.2, "88 78 100 100", -1.0, 2.8, 6.0, -1.1),
        (0, .83, 82, 104, -1.0, "60 90 140 100", -2.2, 1.4, 10.0, -2.0),
        (1, .30, 92, 116, 1.6, "0 50 200 140", -0.8, 3.0, 7.5, -0.6),
        (1, .70, 86, 108, -1.6, "10 70 90 105", -2.8, 0.8, 6.0, -1.7),
    ]
    css = [
        "path.cd{fill:none;stroke:#b79a8c;stroke-opacity:.7;stroke-width:1.6}"
        ".pp{fill:#cdb2a6}.pg{fill:#c79a68}.pg2{fill:#8f6a47}.sp{fill:#9c8f8a}"
        "text{font:600 9px " + MONO + ";letter-spacing:.2em;fill:#c9a9a0}"
        ".dp{fill:#ff8a78;fill-opacity:0}"
    ]
    if not static:
        css.append(
            ".sw{animation:sw var(--d) steps(14,jump-none) infinite;animation-delay:var(--dl)}"
            "@keyframes sw{0%,100%{rotate:var(--a)}50%{rotate:var(--b)}}"
            ".dp{animation:dp 3s steps(18) infinite}.dp.b{animation-delay:-1.5s}"
            "@keyframes dp{0%{fill-opacity:0;translate:0 0}12%{fill-opacity:.8}78%{fill-opacity:.8;translate:0 46px}100%{fill-opacity:0;translate:0 52px}}"
            "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        )
    body = "<defs>" + SCENE_DEFS + "<g id='sc'>" + scene(cls=False) + "</g></defs>"
    for c in cords:
        body += f"<path class='cd' d='M{c[0][0]} {c[0][1]}Q{c[1][0]} {c[1][1]} {c[2][0]} {c[2][1]}'/>"
    drips = ""
    for ci, t, w, h, tilt, crop, a, b, dur, dl in prints:
        px, py = cord_pt(*cords[ci], t)
        x0, y0 = px - w / 2, py + 10
        sty = f"transform-origin:{f(px)}px {f(py + 6)}px;rotate:{tilt}deg"
        if not static:
            sty += f";--a:{a}deg;--b:{b}deg;--d:{dur}s;--dl:{dl}s"
        cls = "sw" if not static else ""
        mx = 7
        body += (
            f"<g class='{cls}' style='{sty}'>"
            f"<rect class='pp' x='{f(x0)}' y='{f(y0)}' width='{w}' height='{h}' rx='1.5'/>"
            f"<svg x='{f(x0 + mx)}' y='{f(y0 + mx)}' width='{w - 2 * mx}' height='{h - 2 * mx}' viewBox='{crop}' preserveAspectRatio='xMidYMid slice'><use href='#sc'/></svg>"
            f"<rect x='{f(x0 + mx)}' y='{f(y0 + mx)}' width='{w - 2 * mx}' height='{h - 2 * mx}' fill='url(#gl)'/>"
            f"<rect class='pg' x='{f(px - 5)}' y='{f(py - 3)}' width='4.6' height='19' rx='1.2'/><rect class='pg2' x='{f(px + 0.6)}' y='{f(py - 3)}' width='4.6' height='19' rx='1.2'/>"
            f"<rect class='sp' x='{f(px - 6)}' y='{f(py + 5)}' width='12' height='2.4' rx='1'/></g>"
        )
        if ci == 0 and t in (.50,):
            drips += f"<circle class='dp' cx='{f(x0 + 14)}' cy='{f(y0 + h + 3)}' r='2.4'/>"
        if ci == 1 and t == .30:
            drips += f"<circle class='dp b' cx='{f(x0 + w - 18)}' cy='{f(y0 + h + 3)}' r='2.2'/>"
    body += drips
    body += "<text x='24' y='470'>FIXED · WASHED · HUNG TO DRY</text>"
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 340 520'><style>{''.join(css)}</style>{body}</svg>"


def mini_line_svg():
    body = "<defs>" + SCENE_DEFS + "<g id='sc'>" + scene(cls=False) + "</g></defs>"
    body += "<path d='M-4 10Q95 34 194 10' fill='none' stroke='#b79a8c' stroke-opacity='.8' stroke-width='1.4'/>"
    for px, py, tilt, crop in ((52, 22, -3, "30 60 130 125"), (136, 22, 2.5, "88 78 100 100")):
        x0, y0, w, h = px - 21, py + 6, 42, 52
        body += (f"<g style='transform-origin:{px}px {py}px;rotate:{tilt}deg'>"
                 f"<rect fill='#cdb2a6' x='{x0}' y='{y0}' width='{w}' height='{h}' rx='1'/>"
                 f"<svg x='{x0 + 4}' y='{y0 + 4}' width='{w - 8}' height='{h - 8}' viewBox='{crop}' preserveAspectRatio='xMidYMid slice'><use href='#sc'/></svg>"
                 f"<rect fill='#c79a68' x='{px - 3}' y='{py - 3}' width='3' height='12' rx='.8'/><rect fill='#8f6a47' x='{px}' y='{py - 3}' width='3' height='12' rx='.8'/></g>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 190 90'>{body}</svg>"


# ------------------------------------------------------------------ small tiles
def grain_svg():
    return (
        "<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n' x='0' y='0' width='100%' height='100%'>"
        "<feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/>"
        "<feColorMatrix values='0 0 0 0 1  0 0 0 0 .42  0 0 0 0 .36  0 0 0 1.1 -.42'/></filter>"
        "<rect width='180' height='180' filter='url(#n)' opacity='.24'/></svg>"
    )


def sprocket(color, op):
    return (
        "<svg xmlns='http://www.w3.org/2000/svg' width='14' height='6'>"
        f"<rect x='3' y='1' width='8' height='4' rx='1.2' fill='{color}' fill-opacity='{op}'/></svg>"
    )


def peg_svg():
    return (
        "<svg xmlns='http://www.w3.org/2000/svg' width='12' height='20' viewBox='0 0 12 20'>"
        "<rect x='.5' y='0' width='5' height='19' rx='1.4' fill='#c79a68'/><rect x='6.5' y='0' width='5' height='19' rx='1.4' fill='#8f6a47'/>"
        "<rect x='0' y='6' width='12' height='2.6' rx='1' fill='#9c8f8a'/></svg>"
    )


# ------------------------------------------------------------------ colours
colors = {
    "canvas": CANVAS, "chrome": "#1d0e0f", "toolbar": "#1b0d0e", "toolbarForeground": "#f4e4dd",
    "toolbarBorder": "#3d1d1f", "toolbarControl": "#2b1416", "toolbarControlForeground": "#f4e4dd",
    "toolbarControlHover": "#3a1b1e", "surface": "#211011", "surfaceRaised": "#2c1517",
    "surfaceOverlay": "#341a1c", "text": "#f4e4dd", "textMuted": "#c9a9a0", "border": "#4a2326",
    "input": "#6b3438", "focus": RED, "accent": RED, "accentForeground": "#1a0707",
    "secondary": "#3a1d1f", "secondaryForeground": "#f4e4dd", "muted": "#2a1517",
    "mutedForeground": "#c9a9a0", "placeholder": "#a07d75", "secondaryLabel": "#c9a9a0",
    "iconMuted": "#b8958c", "error": "#ff8fa0", "errorForeground": "#ffb3bf", "errorSurface": "#42141d",
    "warning": "#ffb347", "warningForeground": "#ffd08a", "warningSurface": "#40290e",
    "update": "#a9cfd6", "updateForeground": "#d4eaee", "updateSurface": "#152a2e",
    "accentSurface": "#3d1514", "accentSurfaceForeground": "#ffc9bd", "messageSurface": "#dcc3b6",
    "messageForeground": "#1d0d0c", "messageAction": "#4a1c1c", "messageActionForeground": "#fbe3da",
    "messageActionHover": "#5e2424", "codeBackground": "#0d0607", "codeForeground": "#f0d9d0",
    "searchMatchBackground": "#5c3a12", "searchMatchForeground": "#ffe7c2",
    "searchMatchActiveBackground": "#ffb347", "searchMatchActiveForeground": "#1a0b02",
    "sidebar": "#110808", "sidebarForeground": "#f0dcd4", "sidebarMutedForeground": "#bf9d94",
    "sidebarControlSurface": "#231012", "sidebarRowHover": "#2a1315", "sidebarRowActive": "#3a1a1c",
    "sidebarRowSelected": "#431e20", "sidebarBorder": "#2e1618", "terminalBackground": "#0c0505",
    "terminalForeground": "#f0d9d0", "terminalCursor": RED, "terminalSelection": "#5a2224",
    "terminalScrollbar": "#3d1c1e", "terminalScrollbarHover": "#6b2f31",
}

CW = "var(--chat-content-max-width,46rem)"
G = f"(100% - {CW})/2"
BUSY = ('body:has([data-timeline-row-kind="working"])',
        'body:has([data-thread-item] [aria-busy="true"][aria-current]:not([aria-current="false"]))')
RM = "@media (prefers-reduced-motion:no-preference)"


def busy(sel):
    return ",".join(f"{b} {sel}" for b in BUSY)


def gutter_w(threshold, maxw):
    return f"min({maxw}px,clamp(0px,({G} - {threshold}px)*1000,{G} - 40px))"


GLOW = (f"radial-gradient(ellipse 70% 55% at 100% 0%,rgba({RED_RGB},.11),transparent 70%),"
        f"radial-gradient(ellipse 60% 45% at 0% 100%,rgba({RED_RGB},.07),transparent 70%)")
GRAIN = data_uri(grain_svg())
DIM = "linear-gradient(rgba(17,8,8,.12),rgba(17,8,8,.12))"
SCRIM = "linear-gradient(#110808 0%,rgba(17,8,8,.9) 16%,rgba(17,8,8,0) 52%)"
SCRIM2 = "linear-gradient(#110808 0%,#110808 5%,transparent 26%)"
SB_GLOW = f"radial-gradient(ellipse 120% 40% at 0% 0%,rgba({RED_RGB},.11),transparent 70%)"
SPR_DIM_T = data_uri(sprocket("#ff5a47", ".16"))
SPR_LIT_T = data_uri(sprocket("#ff5a47", ".7"))

css = (
    ":root{--dr-ts:" + data_uri(tray_svg(True)) + ";--dr-ta:" + data_uri(tray_svg(False))
    + ";--dr-ls:" + data_uri(line_svg(True)) + ";--dr-la:" + data_uri(line_svg(False))
    + ";--dr-tf:" + data_uri(tray_svg(True, False, True)) + ";--dr-df:" + data_uri(tray_svg(True, True, True)) + ";--dr-ds:" + data_uri(tray_svg(True, True)) + ";--dr-da:" + data_uri(tray_svg(False, True))
    + ";--dr-ml:" + data_uri(mini_line_svg()) + ";--dr-peg:" + data_uri(peg_svg()) + ";--dr-sd:" + SPR_DIM_T + ";--dr-sl:" + SPR_LIT_T + "}"
    "@property --dr-p{syntax:'<number>';inherits:false;initial-value:.9}"
    "@property --dr-dn{syntax:'<number>';inherits:false;initial-value:0}"
    ""
    # the room: a static glow + grain on the conversation; the moving art lives on two gutter-sized pseudo-elements
    "[data-workspace-area=\"conversation\"]{position:relative;background:"
    f"{GLOW},{GRAIN},{CANVAS}!important}}"
    "[data-workspace-area=\"conversation\"]::before,[data-workspace-area=\"conversation\"]::after{content:\"\";position:absolute;top:64px;"
    f"width:{gutter_w(216, 280)};aspect-ratio:340/520;background:center/100% 100% no-repeat;pointer-events:none;animation:dr-ia .9s ease-out 1}}"
    "[data-workspace-area=\"conversation\"]::before{left:12px;background-image:var(--dr-ts)}"
    + RM + "{[data-workspace-area=\"conversation\"]::before{background-image:var(--dr-tf)}}"
    "[data-workspace-area=\"conversation\"]::after{right:12px;background-image:var(--dr-ls)}"
    "@keyframes dr-ia{0%{opacity:.15;transform:translateY(-5px)}40%{opacity:1}100%{opacity:1;transform:none}}"
    "@keyframes dr-ib{0%{opacity:.15;transform:translateY(-5px)}40%{opacity:1}100%{opacity:1;transform:none}}"
    + RM + "{" + busy('[data-workspace-area="conversation"]::before') + "{background-image:var(--dr-ta);animation:dr-ib .7s ease-out 1}"
    + busy('[data-workspace-area="conversation"]::after') + "{background-image:var(--dr-la);animation:dr-ib .7s ease-out 1}}"
    # reading column scrim
    "[data-workspace-area=\"conversation\"] .messages-timeline-scroll{background:linear-gradient(90deg,transparent "
    f"calc(50% - {CW}/2 - 216px),rgba(23,11,12,.8) calc(50% - {CW}/2 - 16px),rgba(23,11,12,.8) calc(50% + {CW}/2 + 16px),transparent calc(50% + {CW}/2 + 216px))!important}}"
    f"[data-chat-composer-form]{{background:linear-gradient(90deg,transparent calc(50% - {CW}/2 - 216px),rgba(23,11,12,.8) calc(50% - {CW}/2 - 16px),rgba(23,11,12,.8) calc(50% + {CW}/2 + 16px),transparent calc(50% + {CW}/2 + 216px))}}"
    # header: a timer ruler along its foot; a bar fills while the turn runs; a ding when it ends
    "[data-chat-header]{background-color:rgba(27,13,14,.96)!important;background-image:"
    "repeating-linear-gradient(90deg,rgba(255,150,130,.3) 0 1px,transparent 1px 12px),"
    "linear-gradient(rgba(255,236,226,var(--dr-dn)),rgba(255,236,226,var(--dr-dn)))!important;"
    "background-repeat:repeat-x,no-repeat!important;background-size:100% 4px,100% 2px!important;background-position:0 100%,0 100%!important;"
    "border-bottom:1px solid #3d1d1f!important;animation:dr-done 1.8s ease-out 1;"
    "font-family:\"Avenir Next Condensed\",\"Helvetica Neue\",Arial,sans-serif;letter-spacing:.06em}"
    "@keyframes dr-done{from{--dr-dn:.95}to{--dr-dn:0}}"
    + RM + "{" + busy("[data-chat-header]") + "{background-image:repeating-linear-gradient(90deg,rgba(255,150,130,.3) 0 1px,transparent 1px 12px),"
    f"linear-gradient(90deg,transparent,{RED} 50%,transparent)!important;background-size:100% 4px,90px 2px!important;background-position:0 100%,-90px 100%!important;animation:dr-trav 2.6s linear infinite}}}}"
    "@keyframes dr-trav{from{background-position:0 100%,-90px 100%}to{background-position:0 100%,calc(100% + 90px) 100%}}"
    # live working row: a developer wash sweeps through; busy threads get a safelight dot
    + RM + "{[data-timeline-row-kind=\"working\"]{background-image:linear-gradient(90deg,transparent,"
    f"rgba({RED_RGB},.2),transparent);background-size:55% 100%;background-repeat:no-repeat;background-position:-80% 0;animation:dr-sweep 3s linear infinite}}}}"
    "@keyframes dr-sweep{from{background-position:-80% 0}to{background-position:180% 0}}"
    "[data-thread-item] [aria-busy=\"true\"]{background-image:radial-gradient(circle,"
    f"rgba({RED_RGB},var(--dr-p)) 0 2.6px,transparent 3.2px);background-position:1px 50%;background-size:7px 7px;background-repeat:no-repeat}}"
    + RM + "{[data-thread-item] [aria-busy=\"true\"]{animation:dr-pulse 1.5s ease-in-out infinite}}"
    "@keyframes dr-pulse{50%{--dr-p:.22}}"
    # sidebar: dim room light; thread rows hang from pegs
    f"[data-slot=\"sidebar-inner\"]{{background:{SB_GLOW},#110808!important}}"
    "[data-thread-item]{position:relative}"
    "[data-thread-item]::after{content:\"\";position:absolute;left:6px;top:-4px;width:10px;height:16px;background:var(--dr-peg) center/10px 16px no-repeat;"
    "opacity:0;transform:translateY(-3px);transition:opacity .2s,transform .25s cubic-bezier(.2,.7,.2,1);pointer-events:none}"
    "[data-thread-item]:hover::after,[data-thread-item]:has([aria-current]:not([aria-current=\"false\"]))::after{opacity:1;transform:none}"
    f"[data-thread-item] [aria-current]:not([aria-current=\"false\"]){{box-shadow:inset 2px 0 {RED}}}"
    "[data-slot=\"sidebar-inner\"]{font-family:\"Avenir Next Condensed\",\"Helvetica Neue\",Arial,sans-serif;letter-spacing:.035em}"
    # narrow windows: dock the tray at the foot of the sidebar
    "@media (max-width:1459px){[data-slot=\"sidebar-inner\"]{background:" + SB_GLOW + ",#110808!important;position:relative;isolation:isolate}"
    "[data-slot=\"sidebar-inner\"]::before{content:\"\";position:absolute;left:50%;bottom:40px;width:150px;height:230px;margin-left:-75px;opacity:.9;z-index:-1;pointer-events:none;-webkit-mask-image:linear-gradient(#000 calc(100% - 12px),transparent);mask-image:linear-gradient(#000 calc(100% - 12px),transparent);"
    f"background-image:{SCRIM2},var(--dr-ds);background-size:100% 100%;background-repeat:no-repeat;animation:dr-ia .9s ease-out 1}}"
    "[data-thread-item],:has(>[data-slot=\"project-monogram\"]){background-color:#110808;box-shadow:0 0 0 4px #110808}"
    ":has(>[data-slot=\"project-monogram\"]){box-shadow:0 0 0 12px #110808}"
    "[data-slot=\"sidebar-inner\"]::after{content:\"\";position:absolute;left:50%;bottom:274px;width:150px;height:71px;margin-left:-75px;z-index:-1;pointer-events:none;background:var(--dr-ml) center/100% 100% no-repeat}"
    "[data-workspace-area=\"conversation\"]::before,[data-workspace-area=\"conversation\"]::after{display:none}"
    + RM + "{[data-slot=\"sidebar-inner\"]::before{background-image:" + SCRIM2 + ",var(--dr-df)}"
    + busy('[data-slot="sidebar-inner"]::before') + f"{{background-image:{SCRIM2},var(--dr-da);animation:dr-ib .7s ease-out 1}}}}}}"
    # user bubble: a glossy print
    "[data-user-message-bubble]{background:linear-gradient(115deg,rgba(255,255,255,.3),transparent 38%),#dcc3b6!important;color:#1d0d0c;"
    "border:1px solid #f4e2d9!important;border-radius:2px!important;box-shadow:inset 0 -5px 0 rgba(120,66,56,.2),0 3px 0 rgba(0,0,0,.45)}"
    "[data-user-message-bubble] :is(a,code){color:#7a1e14!important;background:rgba(120,40,30,.12)}"
    # composer: a film frame; the safelight comes up on focus
    "[data-slot=\"composer-host\"]{background:var(--dr-sd) 0 3px/14px 6px repeat-x,var(--dr-sd) 0 calc(100% - 3px)/14px 6px repeat-x,#1c0d0e!important;"
    "border:1px solid #4a2326!important;border-radius:6px!important;transition:border-color .25s,box-shadow .35s}"
    "[data-slot=\"composer-host\"]:focus-within{background:var(--dr-sl) 0 3px/14px 6px repeat-x,var(--dr-sl) 0 calc(100% - 3px)/14px 6px repeat-x,#1c0d0e!important;"
    f"border-color:{RED}!important;box-shadow:0 0 0 3px rgba({RED_RGB},.15),0 0 26px rgba({RED_RGB},.2)}}"
    # assistant markdown
    ".chat-markdown :is(h1,h2,h3,h4){font-family:\"Avenir Next Condensed\",\"Helvetica Neue\",Arial,sans-serif;font-weight:600;letter-spacing:.07em;text-transform:uppercase}"
    ".chat-markdown :is(h1,h2,h3,h4) code{text-transform:none;letter-spacing:0}"
    f".chat-markdown :is(h1,h2,h3)::before{{content:\"\\25B6\";color:{RED};font-size:.55em;margin-right:.7em;vertical-align:.18em}}"
    ".chat-markdown :is(h1,h2){border-bottom:1px solid #3d1d1f;padding-bottom:.25em}"
    ".chat-markdown :not(pre)>code{color:#ffbfae;background:rgba(255,90,71,.11);padding:.05em .32em;border-radius:3px}"
    ".chat-markdown a{color:#ffb347!important;text-decoration-style:dotted;text-underline-offset:3px}"
    f".chat-markdown blockquote{{border-left:2px solid {RED};color:#c9a9a0}}"
    ".chat-markdown hr{border:0;height:6px;background:var(--dr-sd) 0 0/14px 6px repeat-x}"
    ".chat-markdown-codeblock{background:#0d0607!important;border:1px solid #3a1a1c!important;border-left:3px solid " + RED + "!important;border-radius:3px!important}"
    ".chat-markdown{counter-reset:drf 11}.chat-markdown-codeblock{counter-increment:drf}"
    ".chat-markdown-codeblock::before{content:\"\\25B6  \" counter(drf) \"A\";display:block;margin-bottom:6px;font:600 10px ui-monospace,Menlo,monospace;letter-spacing:.2em;color:#ffb347}"
    "::selection{background:rgba(255,90,71,.38)}"
    # overlays
    "[data-slot=\"popover-popup\"]{background-color:#2c1517!important;background-image:var(--dr-sd);background-size:14px 6px;background-position:0 4px;background-repeat:repeat-x;padding-top:6px}"
    "[data-slot=\"dialog-popup\"],[data-slot=\"popover-popup\"],[data-slot=\"menu-popup\"]{border:1px solid #5b2a2d!important;border-top:2px solid " + RED + "!important;border-radius:8px!important}"
    "[data-slot=\"tooltip-popup\"]{background:#ecd6cb!important;color:#1d0d0c!important;border-radius:3px!important;font-family:\"Avenir Next Condensed\",\"Helvetica Neue\",Arial,sans-serif;text-transform:uppercase;letter-spacing:.06em}"
    "[data-slot=\"button\"],[data-slot=\"input\"],[data-slot=\"select-trigger\"]{border-radius:6px!important}"
    "[data-slot=\"input\"],[data-slot=\"select-trigger\"]{background-color:#150a0b!important;border-color:#4a2326!important;transition:border-color .25s,box-shadow .3s}"
    f"[data-slot=\"input\"]:is(:hover,:focus,:focus-visible),[data-slot=\"select-trigger\"]:is(:hover,:focus-visible){{border-color:{RED}!important;box-shadow:0 0 0 3px rgba({RED_RGB},.14),0 0 18px rgba({RED_RGB},.16)}}"
    "[data-slot=\"button\"]{transition:transform .12s,box-shadow .2s,background-color .2s}"
    f"[data-slot=\"button\"]:hover{{box-shadow:0 0 14px rgba({RED_RGB},.22)}}[data-slot=\"button\"]:active{{transform:translateY(1px);box-shadow:none}}"
    f":focus-visible{{outline:2px solid {RED};outline-offset:2px}}"
    "[data-slot=\"composer-host\"] :focus-visible,.composer-tiptap:focus-visible{outline:none!important}"
    "[data-slot=\"switch\"]{background-color:#2a1517!important;border:1px solid #4a2326}"
    f"[data-slot=\"switch\"][aria-checked=\"true\"]{{background-color:#5a1f1c!important;border-color:{RED};box-shadow:0 0 12px rgba({RED_RGB},.4)}}"
    "[data-slot=\"switch\"]>*{background:#b8958c!important}"
    f"[data-slot=\"switch\"][aria-checked=\"true\"]>*{{background:{RED}!important;box-shadow:0 0 8px {RED}}}"
    f"[data-slot=\"menu-popup\"] :is([role=\"menuitem\"],[role=\"option\"]):is(:hover,:focus-visible,[aria-selected=\"true\"]){{background:linear-gradient(90deg,rgba({RED_RGB},.22),rgba({RED_RGB},.05))!important;box-shadow:inset 2px 0 {RED}}}"
    "[data-slot=\"dialog-popup\"]{background-image:var(--dr-sd);background-size:14px 6px;background-position:0 5px;background-repeat:repeat-x}"
    "[data-slot=\"project-monogram\"]{border-radius:2px!important;border:1px solid #4a2326;font-family:ui-monospace,Menlo,monospace;letter-spacing:.04em}"
    f"[data-thread-details-card]{{border:1px solid #3d1d1f!important;border-top:2px solid {RED}!important;border-radius:6px!important}}"
    f"[data-thread-terminal-drawer]{{border-top:2px solid {RED}!important;box-shadow:0 -8px 24px rgba(0,0,0,.4)}}"
    "[data-settings-page-scroll] :is(h1,h2,h3){font-family:\"Avenir Next Condensed\",\"Helvetica Neue\",Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;border-bottom:1px solid #3d1d1f;padding-bottom:.25em}"
    "[data-settings-page-scroll]{background-image:repeating-linear-gradient(90deg,rgba(255,150,130,.06) 0 1px,transparent 1px 12px);background-size:100% 4px;background-repeat:no-repeat}"
    ".chat-markdown table{border-collapse:collapse;border:1px solid #3d1d1f}"
    ".chat-markdown th{font-family:\"Avenir Next Condensed\",\"Helvetica Neue\",Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;border-bottom:2px solid #3d1d1f;background:#1c0d0e}"
    ".chat-markdown :is(th,td){border:1px solid #3d1d1f;padding:.35em .7em}"
    f".chat-markdown :is(ul,ol) li::marker{{color:{RED}}}"
    f"[data-timeline-row-kind=\"work\"]{{font-size:12px;letter-spacing:-.01em;border-left:2px solid #3d1d1f;padding-left:18px;position:relative}}"
    f"[data-timeline-row-kind=\"work\"]::before{{content:\"\\25B8\";position:absolute;left:5px;top:50%;transform:translateY(-50%);color:#ffb347;font-size:10px}}"
    "svg.lucide{stroke-width:1.7}"
    "::-webkit-scrollbar-track{background:#120909}::-webkit-scrollbar-thumb,[data-slot=\"scroll-area-thumb\"]{background:#4a2326!important;border-radius:6px!important}"
    f"::-webkit-scrollbar-thumb:hover{{background:rgba({RED_RGB},.6)!important}}"
    "@media (prefers-reduced-motion:reduce){[data-chat-header],[data-timeline-row-kind],[data-workspace-area=\"conversation\"]::before,[data-workspace-area=\"conversation\"]::after,[data-slot=\"sidebar-inner\"]::before,[data-thread-item] [aria-busy],[data-thread-item]::after,[data-slot=\"composer-host\"]{animation:none!important;transition:none!important}}"
)

theme = {"version": 1, "id": "darkroom", "name": "Darkroom", "appearance": "dark", "accent": RED, "canvas": CANVAS,
         "colors": colors, "css": css}

with open(os.path.join(HERE, "..", "darkroom.json"), "w") as fh:
    json.dump(theme, fh, ensure_ascii=False)
print("css chars:", len(css))
os.makedirs(os.path.join(HERE, "..", "assets", "svg"), exist_ok=True)
for n, s in (("tray", tray_svg(False)), ("tray-still", tray_svg(True)), ("line", line_svg(False)), ("line-still", line_svg(True))):
    with open(os.path.join(HERE, "..", "assets", "svg", f"{n}.svg"), "w") as fh:
        fh.write(s)
