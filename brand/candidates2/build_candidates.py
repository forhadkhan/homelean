#!/usr/bin/env python3
"""Build the three Homelean wordmark candidates (round 2) and their comparison sheet from named parameters.

    uv run --no-project --with pillow --with numpy --with fonttools --with uharfbuzz --with skia-pathops \
        python brand/candidates2/build_candidates.py [--report]

Each candidate sets "homelean" in a real typeface (shaped with HarfBuzz, so the font's own spacing and kerning
apply), outlines it, and replaces only the h with the Homelean h: the font's own h with its counter recut as a
gabled doorway, so stem, shoulder, leg, x-height and overshoot stay the font's. The full right leg is the font's
own leg, untouched. The icon is that same outline on the mint plate; the favicon is the same outline warped onto
the 32 grid (every straight edge on an even unit) so it lands on whole pixels at 16 px.

Fonts are read in place from ~/karkhana/library/fonts and never copied: the SVGs hold outlines only.
--report prints the measured gaps between letters (white area in the x-height band) for the kerning check.
"""

import argparse
import pathlib
import shutil
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
FONTS = pathlib.Path.home() / "karkhana/library/fonts"

INK, ACCENT, MINT, PAGE, BUTTER = "#0e2b22", "#1f7a55", "#d9f0e3", "#f6faf7", "#fbefc4"
WORD, SPLIT = "homelean", 4  # "home" in ink | "lean" in accent

# ---- the candidates -------------------------------------------------------------------------------------------
# tracking: font units added after every letter (negative = tighter). kern: extra font units between a named pair,
# set by eye from the --report numbers and the 240 px / 22 px renders. apex_k: how far the doorway's apex sits
# under the inside of the arch, in arch thicknesses. pitch: roof rise over half the door width (1.0 = 45 degrees).
CANDIDATES = {
    "a": dict(
        label="A  Outfit SemiBold (geometric, OFL)",
        font="outfit/OTF/Outfit-SemiBold.otf",
        tracking=-6,
        kern={"el": -15},
        apex_k=0.05,
        pitch=1.0,
    ),
    "b": dict(
        label="B  Switzer Medium (neo-grotesque)",
        font="switzer/OTF/Switzer-Medium.otf",
        tracking=-8,
        kern={"el": -10, "ea": -15},
        apex_k=0.05,
        pitch=1.0,
    ),
    "c": dict(
        label="C  Zodiak Bold (high-contrast serif)",
        font="zodiak/OTF/Zodiak-Bold.otf",
        tracking=-4,
        kern={"el": -12, "le": -10, "an": -8},
        apex_k=0.05,
        pitch=1.0,
    ),
}

SCALE_H = 100.0  # the wordmark's h is drawn SCALE_H units tall (ascender to baseline) in the SVGs
PAD = 2  # hairline margin inside each viewBox; clear space is extra
ICON_H = 60  # the h's height on the 100-unit icon plate
FAV = dict(H=24, BASE=28, MIN_STEM=4, MIN_COUNTER=8)  # favicon on the 32 grid (y down)


# ---- geometry helpers -----------------------------------------------------------------------------------------
def rect(x0, y0, x1, y1):
    import pathops

    p = pathops.Path()
    p.moveTo(x0, y0)
    p.lineTo(x1, y0)
    p.lineTo(x1, y1)
    p.lineTo(x0, y1)
    p.close()
    return p


def poly(points):
    import pathops

    p = pathops.Path()
    p.moveTo(*points[0])
    for pt in points[1:]:
        p.lineTo(*pt)
    p.close()
    return p


def op(a, b, how):
    import pathops

    return pathops.op(a, b, getattr(pathops.PathOp, how))


def union_all(paths):
    import pathops

    out = pathops.Path()
    for p in paths:
        out = op(out, p, "UNION")
    return out


def fmt(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class MapPen:
    """Writes every point through f((x, y)) into a pathops path (affine moves, flips and the favicon's warp)."""

    def __init__(self, path, f):
        self.p, self.f = path.getPen(), f

    def moveTo(self, pt):
        self.p.moveTo(self.f(pt))

    def lineTo(self, pt):
        self.p.lineTo(self.f(pt))

    def curveTo(self, *pts):
        self.p.curveTo(*[self.f(q) for q in pts])

    def qCurveTo(self, *pts):
        self.p.qCurveTo(*[self.f(q) if q is not None else None for q in pts])

    def closePath(self):
        self.p.closePath()

    def endPath(self):
        self.p.endPath()


def mapped(path, f):
    import pathops

    out = pathops.Path()
    path.draw(MapPen(out, f))
    return out


def path_d(path, f=lambda pt: pt):
    """SVG path data with every point mapped by f, two decimals."""
    from fontTools.pens.svgPathPen import SVGPathPen

    pen = SVGPathPen(None, ntos=fmt)
    mapped(path, f).draw(pen)
    return pen.getCommands()


def intervals_x(path, y):
    """Ink intervals [(x0, x1)] where the horizontal line at y crosses the path."""
    hit = op(path, rect(-1e5, y - 0.25, 1e5, y + 0.25), "INTERSECTION")
    return sorted((c.bounds[0], c.bounds[2]) for c in hit.contours)


def intervals_y(path, x):
    hit = op(path, rect(x - 0.25, -1e5, x + 0.25, 1e5), "INTERSECTION")
    return sorted((c.bounds[1], c.bounds[3]) for c in hit.contours)


# ---- font loading and shaping ---------------------------------------------------------------------------------
class Face:
    def __init__(self, rel):
        import uharfbuzz as hb
        from fontTools.ttLib import TTFont

        self.file = FONTS / rel
        self.tt = TTFont(self.file)
        self.gs, self.order = self.tt.getGlyphSet(), self.tt.getGlyphOrder()
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(str(self.file))))
        self.upm = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()

    def glyph(self, name):
        import pathops

        p = pathops.Path()
        self.gs[name].draw(p.getPen())
        p.simplify()
        return p

    def shape(self, text, tracking=0, kern=None):
        """[(char, glyph name, x)] with the font's kerning, plus tracking and extra pair kerning."""
        import uharfbuzz as hb

        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": False})
        x, out = 0, []
        for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions, strict=True)):
            if i:
                x += (kern or {}).get(text[i - 1] + text[i], 0)
            out.append((text[i], self.order[info.codepoint], x + pos.x_offset))
            x += pos.x_advance + tracking
        return out


# ---- the Homelean h -------------------------------------------------------------------------------------------
def homelean_h(face, apex_k, pitch):
    """The font's h with its counter recut as a gabled doorway. Returns (path, measures), font units, y up."""
    h = face.glyph(face.cmap[ord("h")])
    xh = face.glyph(face.cmap[ord("x")]).bounds[3]
    ink = intervals_x(h, 0.3 * xh)
    (_, x1), (x2, x3) = ink[0], ink[-1]  # stem's right edge, leg's left edge (measured at 30% of x-height)
    xm = (x1 + x2) / 2
    col = [iv for iv in intervals_y(h, xm) if iv[0] > 0.2 * xh]
    inner, outer = col[0]  # the arch above the counter: its inside and its top
    t = outer - inner
    # the counter: the white under the arch that reaches the baseline
    box = rect(x1, -0.5 * xh, x2, inner + 0.5 * t)
    counter = union_all(c for c in op(box, h, "DIFFERENCE").contours if c.bounds[1] < 1)
    half = (x2 - x1) / 2
    apex = inner - apex_k * t
    eave = apex - half * pitch
    m = 0.25 * (x2 - x1)  # walls run past the counter so the roof line, not a sliver, meets the stem and leg
    door = poly([(x1 - m, -xh), (x1 - m, eave - m * pitch), (xm, apex), (x2 + m, eave - m * pitch), (x2 + m, -xh)])
    wedge = op(counter, door, "DIFFERENCE")
    out = op(h, wedge, "UNION")
    out.simplify()
    stem = ink[0][1] - ink[0][0]
    return out, dict(xh=xh, x0=ink[0][0], x1=x1, x2=x2, x3=x3, inner=inner, top=h.bounds[3], arch=outer,
                     t=t, apex=apex, eave=eave, stem=stem, leg=x3 - x2)


def word(face, c):
    """[(char, path)] for the word, font units, y up, the Homelean h in place of the font's h."""
    hh, meas = homelean_h(face, c["apex_k"], c["pitch"])
    out = []
    for ch, name, x in face.shape(WORD, c["tracking"], c["kern"]):
        g = hh if ch == "h" else face.glyph(name)
        out.append((ch, mapped(g, lambda pt, x=x: (pt[0] + x, pt[1]))))
    return out, hh, meas


# ---- SVG writers ----------------------------------------------------------------------------------------------
def svg(view, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}">{body}</svg>\n'


REVERSE_THIN = 0.02


def thinned(path, d):
    """The path with d taken off every edge (a stroke of width 2d, subtracted)."""
    import pathops

    edge = pathops.Path()
    path.draw(edge.getPen())
    edge.stroke(2 * d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    edge.convertConicsToQuads()
    out = op(path, edge, "DIFFERENCE")
    out.simplify()
    return out


def wordmark_svgs(glyphs, meas):
    s = SCALE_H / meas["top"]
    xs = [g.bounds for _, g in glyphs]
    x0, y0 = min(b[0] for b in xs), min(b[1] for b in xs)
    x1, y1 = max(b[2] for b in xs), max(b[3] for b in xs)

    def f(pt):
        return ((pt[0] - x0) * s + PAD, (y1 - pt[1]) * s + PAD)

    hm = "".join(path_d(g, f) for _, g in glyphs[:SPLIT])
    ln = "".join(path_d(g, f) for _, g in glyphs[SPLIT:])
    # light on dark reads heavier: the reversed word loses REVERSE_THIN of a stem on every edge
    d = REVERSE_THIN * meas["stem"]
    hm_r = "".join(path_d(thinned(g, d), f) for _, g in glyphs[:SPLIT])
    ln_r = "".join(path_d(thinned(g, d), f) for _, g in glyphs[SPLIT:])
    view = f"0 0 {fmt((x1 - x0) * s + 2 * PAD)} {fmt((y1 - y0) * s + 2 * PAD)}"
    return {
        "wordmark.svg": svg(view, f'<path fill="{INK}" d="{hm}"/><path fill="{ACCENT}" d="{ln}"/>'),
        "wordmark-reversed.svg": svg(view, f'<path fill="{PAGE}" d="{hm_r}"/><path fill="{BUTTER}" d="{ln_r}"/>'),
        "wordmark-mono.svg": svg(view, f'<path fill="currentColor" d="{hm}{ln}"/>'),
    }


def icon_svg(hh, meas):
    """The same h outline on the mint plate, centred on its box horizontally and on its height vertically."""
    bx0, by0, bx1, by1 = hh.bounds
    s = ICON_H / (by1 - by0)
    cx = (bx0 + bx1) / 2

    def f(pt):
        return (50 + (pt[0] - cx) * s, 50 + ICON_H / 2 - (pt[1] - by0) * s)

    return svg("0 0 100 100", f'<rect width="100" height="100" rx="22" fill="{MINT}"/>'
                              f'<path fill="{INK}" d="{path_d(hh, f)}"/>')


def _even(v):
    return 2 * round(v / 2)


def favicon_svg(hh, meas):
    """The same h, warped piecewise-linearly so each stem, the leg, the baseline, eave, x-height and top land on even
    units of the 32 grid (whole pixels at 16 px). Stems and the counter keep a minimum width so 16 px stays open."""
    bx0, by0, bx1, by1 = hh.bounds
    s = FAV["H"] / (by1 - by0)
    # x keys: outer left, stem right, leg left, leg right (outer right), each width snapped to even and minimums
    stem = max(FAV["MIN_STEM"], _even((meas["x1"] - meas["x0"]) * s))
    counter = max(FAV["MIN_COUNTER"], 4 * round((meas["x2"] - meas["x1"]) * s / 4))  # half stays even: apex on grid
    leg = max(FAV["MIN_STEM"], _even((meas["x3"] - meas["x2"]) * s))
    left_extra = _even((meas["x0"] - bx0) * s)  # serif or spur left of the stem
    right_extra = _even((bx1 - meas["x3"]) * s)
    width = left_extra + stem + counter + leg + right_extra
    left = _even(16 - width / 2)
    kx = [bx0, meas["x0"], meas["x1"], meas["x2"], meas["x3"], bx1]
    tx = [left, left + left_extra, left + left_extra + stem, left + left_extra + stem + counter,
          left + left_extra + stem + counter + leg, left + width]
    if left_extra == 0:
        kx, tx = kx[1:], tx[1:]
    if right_extra == 0:
        kx, tx = kx[:-1], tx[:-1]
    # y keys (svg y down): baseline, eave, apex, x-height (arch top), top
    base = FAV["BASE"]
    top = base - FAV["H"]
    archtop = base - _even(meas["arch"] * s)
    eave = base - _even(meas["eave"] * s)
    apex = eave - counter / 2 * (meas["apex"] - meas["eave"]) / ((meas["x2"] - meas["x1"]) / 2)
    inner = min(apex - 2, archtop + max(2, _even(meas["t"] * s)))  # arch at least 1 px thick, apex below it
    ky = [0, meas["eave"], meas["apex"], meas["inner"], meas["arch"], by1]
    ty = [base, eave, apex, inner, archtop, top]
    if by0 < 0:  # overshoot below the baseline keeps its scale
        ky, ty = [by0] + ky, [base - by0 * s] + ty
    if left_extra:  # serifs: the foot serif's top and the head serif's underside also land on the grid, 1 px thick
        for lo, hi in intervals_y(hh, (bx0 + meas["x0"]) / 2):
            if lo < 0.5 * meas["xh"]:
                ky.append(hi)
                ty.append(base - max(2, _even(hi * s)))
            else:
                ky.append(lo)
                ty.append(top + max(2, _even((by1 - lo) * s)))
    pairs = sorted(zip(ky, ty))

    def lerp(keys, vals, v):
        if v <= keys[0]:
            return vals[0] + (v - keys[0]) * (vals[1] - vals[0]) / (keys[1] - keys[0])
        for i in range(1, len(keys)):
            if v <= keys[i]:
                return vals[i - 1] + (v - keys[i - 1]) * (vals[i] - vals[i - 1]) / (keys[i] - keys[i - 1])
        return vals[-1] + (v - keys[-1]) * (vals[-1] - vals[-2]) / (keys[-1] - keys[-2])

    yk, yv = [p[0] for p in pairs], [p[1] for p in pairs]

    def f(pt):
        return (lerp(kx, tx, pt[0]), lerp(yk, yv, pt[1]))

    return svg("0 0 32 32", f'<rect width="32" height="32" rx="7" fill="{MINT}"/>'
                            f'<path fill="{INK}" d="{path_d(hh, f)}"/>')


# ---- spacing report -------------------------------------------------------------------------------------------
def report(face, c, glyphs, meas):
    """White area between neighbours inside the x-height band, per pair, as a share of x-height squared."""
    import numpy as np
    from PIL import Image, ImageDraw

    xh = meas["xh"]
    sc = 400 / xh
    print(f"  stem {meas['stem']:.0f}  leg {meas['leg']:.0f}  arch {meas['t']:.0f}  x-height {xh:.0f}  "
          f"apex {meas['apex']:.0f}  eave {meas['eave']:.0f}")
    for (a, ga), (b, gb) in zip(glyphs, glyphs[1:]):
        lo, hi = ga.bounds[0], gb.bounds[2]
        w = int((hi - lo) * sc) + 4
        im = Image.new("L", (w, 400), 0)
        for g in (ga, gb):
            d = ImageDraw.Draw(im)
            for cont in g.contours:
                pts = [((x - lo) * sc, (xh - y) * sc) for x, y in cont.points]
                if len(pts) > 2:
                    d.polygon(pts, fill=255)
        arr = np.array(im) > 0
        # per row: white run between the last ink of a and the first ink of b (only the gap between the two)
        ra, rb = int((ga.bounds[2] - lo) * sc), int((gb.bounds[0] - lo) * sc)
        area = 0
        for row in arr:
            left = row[: ra + 1].nonzero()[0]
            right = row[rb:].nonzero()[0]
            if len(left) and len(right):
                gap = rb + right[0] - left[-1]
                area += min(max(gap, 0), 400 * 0.35)  # cap deep round gaps (the eye fills them only so far)
        print(f"  {a}{b}: {area / (400 * 400):.3f}")


# ---- comparison sheet -----------------------------------------------------------------------------------------
def sheet(out_png):
    """One headless-Chrome screenshot of an HTML page that places every SVG at its true size, so what you see is what
    a browser draws: 1200 px, 240 px and 22 px tall wordmarks, the icon at 180 px and the favicon at 32 and 16 px,
    on the page colour and on ink green."""
    rows = []
    for key, c in CANDIDATES.items():
        d = (HERE / key).resolve().as_uri()
        rows.append(f"""
<section><h2>{c['label']}</h2>
<div class="light big"><img src="{d}/wordmark.svg" width="1200"></div>
<div class="pair">
 <div class="light"><img src="{d}/wordmark.svg" width="240"></div>
 <div class="dark"><img src="{d}/wordmark-reversed.svg" width="240"></div>
 <div class="light hdr"><img src="{d}/wordmark.svg" style="height:22px"><span>header 22 px</span></div>
 <div class="dark hdr"><img src="{d}/wordmark-reversed.svg" style="height:22px"></div>
</div>
<div class="pair icons">
 <div class="light"><img src="{d}/icon.svg" width="180"><img src="{d}/favicon.svg" width="32"><img src="{d}/favicon.svg" width="16"></div>
 <div class="dark"><img src="{d}/icon.svg" width="180"><img src="{d}/favicon.svg" width="32"><img src="{d}/favicon.svg" width="16"></div>
</div></section>""")
    html = f"""<!doctype html><html><head><style>
body{{margin:0;padding:24px;background:#fff;font:14px/1.3 sans-serif;color:#333;width:1300px}}
section{{margin:0 0 40px}} h2{{font-size:15px;margin:0 0 8px;font-weight:600}}
.light{{background:{PAGE}}} .dark{{background:{INK}}}
.big{{padding:24px;margin-bottom:8px}}
.pair{{display:flex;gap:8px;margin-bottom:8px;align-items:stretch}}
.pair>div{{padding:20px;display:flex;align-items:center;gap:24px}}
.hdr span{{font-size:11px;color:#888}}
img{{display:block}}
</style></head><body>{''.join(rows)}</body></html>"""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="homelean-sheet-"))
    try:
        page = tmp / "sheet.html"
        page.write_text(html)
        height = 24 * 2 + len(CANDIDATES) * 620
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                        "--allow-file-access-from-files", f"--window-size=1348,{height}",
                        f"--screenshot={out_png}", page.as_uri()], capture_output=True, timeout=120)
        (HERE / "sheet.html").write_text(html)  # kept so the sheet can be opened and zoomed in a browser
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="print the measured letter gaps per pair")
    ap.add_argument("--no-sheet", action="store_true")
    a = ap.parse_args()
    for key, c in CANDIDATES.items():
        face = Face(c["font"])
        glyphs, hh, meas = word(face, c)
        files = wordmark_svgs(glyphs, meas)
        files["icon.svg"] = icon_svg(hh, meas)
        files["favicon.svg"] = favicon_svg(hh, meas)
        (HERE / key).mkdir(exist_ok=True)
        for name, text in files.items():
            (HERE / key / name).write_text(text)
        print(f"{key}: {c['label']}  ({len(files)} files)")
        if a.report:
            report(face, c, glyphs, meas)
    if not a.no_sheet:
        sheet(HERE / "sheet.png")
        print("sheet.png")


if __name__ == "__main__":
    main()
