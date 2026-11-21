"""Refresh the generated blocks of index.html from darkroom.json and build.py.

  <!--SEGS-->...<!--/SEGS-->   seven-segment symbols used by the hero timer
  <!--PAL-->...<!--/PAL-->     palette rows (hexes read straight from darkroom.json)
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location("build", os.path.join(HERE, "build.py"))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

theme = json.load(open(os.path.join(HERE, "..", "darkroom.json")))
c = theme["colors"]

ROWS = [
    ("canvas", "Canvas", "the room"),
    ("sidebar", "Sidebar", "further from the lamp"),
    ("surface", "Surface", "composer, cards"),
    ("surfaceRaised", "Raised", "menus, hover"),
    ("border", "Border", "tray rims"),
    ("text", "Text", "paper under safelight"),
    ("textMuted", "Muted", "captions, meta"),
    ("accent", "Safelight", "accent and focus"),
    ("accentForeground", "On safelight", "text on accent"),
    ("messageSurface", "Print paper", "your messages"),
    ("messageForeground", "Print ink", "text on paper"),
    ("warning", "Lamp amber", "warnings, links"),
    ("update", "Fixer silver", "updates"),
    ("error", "Error pink", "never the accent"),
    ("codeBackground", "Deep tray", "code blocks"),
]


def pal():
    out = []
    for k, name, note in ROWS:
        hx = c[k].upper()
        out.append(
            f"<li><button type='button' class='sw' data-hex='{hx}' aria-label='Copy {name} {hx}'>"
            f"<i style='background:{hx}'></i><b>{name}</b><span>{note}</span><code>{hx}</code><em>copied</em></button></li>")
    return "\n".join(out)


def segs():
    out = ["<svg width='0' height='0' style='position:absolute' aria-hidden='true'><defs>"]
    out.append(f"<symbol id='dg' viewBox='0 0 {b.DW} {b.DH}'>{b.GHOST}</symbol>")
    for i in range(10):
        out.append(f"<symbol id='d{i}' viewBox='0 0 {b.DW} {b.DH}'>{b.glyph(i)}</symbol>")
    out.append("</defs></svg>")
    return "".join(out)


p = os.path.join(HERE, "..", "index.html")
h = open(p).read()
for tag, body in (("SEGS", segs()), ("PAL", pal())):
    h, n = re.subn(rf"(<!--{tag}-->).*?(<!--/{tag}-->)", lambda m: m.group(1) + body + m.group(2), h, flags=re.S)
    assert n == 1, tag
open(p, "w").write(h)
print("index.html refreshed")
