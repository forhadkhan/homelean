#!/usr/bin/env python3
"""Build the three Homelean icon-mark candidates (A, B, C) and their contact sheet from named parameters.

    uv run --no-project --with pillow --with numpy --with fonttools --with uharfbuzz --with skia-pathops \
        python brand/candidates/build_candidates.py

Drafts for Forhad's choice only; nothing here replaces the files in brand/. Every path comes from the geometry
below (no stock icon, no traced raster). The wordmark is Switzer Semibold, shaped with HarfBuzz and outlined with
fontTools; the font file is only read.

  A  Lean-to h    the h is a building: one solid block, a single-pitch roof falling from the stem, an arched door
                  as the counter.
  B  Roof & tick  two strokes of one weight and one angle: a gable roof over a tick whose arms run parallel to it.
  C  Home in h    a Switzer-like h with a round shoulder whose counter is a gabled doorway: the home inside the h.
"""

import math
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
FONT = pathlib.Path.home() / "karkhana/library/fonts/switzer/OTF/Switzer-Semibold.otf"
QA = pathlib.Path.home() / "karkhana/skills/brand-identity/scripts"

INK, ACCENT, MINT, PAGE, BUTTER = "#0e2b22", "#1f7a55", "#d9f0e3", "#f6faf7", "#fbefc4"
K = 0.5523  # cubic handle length for a quarter circle, times r


def fmt(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ---- path helpers (skia-pathops) ------------------------------------------------------------------------------
def poly(points):
    import pathops

    p = pathops.Path()
    p.moveTo(*points[0])
    for pt in points[1:]:
        p.lineTo(*pt)
    p.close()
    return p


def op(a, b, kind):
    import pathops

    return pathops.op(a, b, getattr(pathops.PathOp, kind))


def path_d(path, s=1.0, dx=0.0, dy=0.0):
    """SVG path data of a pathops path, scaled and moved, two decimals."""
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen

    pen = SVGPathPen(None, ntos=fmt)
    path.draw(TransformPen(pen, (s, 0, 0, s, dx, dy)))
    return pen.getCommands()


def outline_polyline(pts, t):
    """Outline of an open polyline of width t: mitre joins, butt caps, as one polygon."""
    def offset(p, q, d):
        vx, vy = q[0] - p[0], q[1] - p[1]
        n = math.hypot(vx, vy)
        nx, ny = -vy / n * d, vx / n * d
        return (p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny)

    def meet(a, b):
        (x1, y1), (x2, y2) = a
        (x3, y3), (x4, y4) = b
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        u = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        return (x1 + u * (x2 - x1), y1 + u * (y2 - y1))

    sides = []
    for d in (t / 2, -t / 2):
        segs = [offset(pts[i], pts[i + 1], d) for i in range(len(pts) - 1)]
        line = [segs[0][0]] + [meet(segs[i], segs[i + 1]) for i in range(len(segs) - 1)] + [segs[-1][1]]
        sides.append(line)
    return poly(sides[0] + sides[1][::-1])


# ---- A: lean-to h ---------------------------------------------------------------------------------------------
A = dict(
    STEM_L=16, STEM_W=22,   # the wall / stem
    TOP=8, BASE=92,         # ascender top, baseline
    RIGHT=84,               # far wall
    ROOF_Y=28,              # where the roof meets the wall: the wall stands ROOF_Y - TOP above it (the ascender)
    PITCH=0.42,             # roof slope, rise over run (about 23 degrees)
    DOOR_W=22,              # the arched counter (door) width; leg = RIGHT - STEM_R - DOOR_W
    ROOF_T=17,              # roof thickness measured square to the slope, above the door's arch
)


def mark_a():
    p = A
    sr = p["STEM_L"] + p["STEM_W"]
    roof = lambda x: p["ROOF_Y"] + p["PITCH"] * (x - sr)  # noqa: E731
    body = poly([(p["STEM_L"], p["TOP"]), (sr, p["TOP"]), (sr, p["ROOF_Y"]), (p["RIGHT"], roof(p["RIGHT"])),
                 (p["RIGHT"], p["BASE"]), (p["STEM_L"], p["BASE"])])
    r = p["DOOR_W"] / 2
    cx = sr + r
    # arch centre: roof-to-arch distance square to the slope equals ROOF_T
    yc = roof(cx) + (r + p["ROOF_T"]) * math.hypot(1, p["PITCH"])
    import pathops

    door = pathops.Path()
    x0, x1 = cx - r, cx + r
    door.moveTo(x0, p["BASE"] + 4)
    door.lineTo(x0, yc)
    door.cubicTo(x0, yc - K * r, cx - K * r, yc - r, cx, yc - r)
    door.cubicTo(cx + K * r, yc - r, x1, yc - K * r, x1, yc)
    door.lineTo(x1, p["BASE"] + 4)
    door.close()
    return {INK: op(body, door, "DIFFERENCE")}


# ---- B: roof and tick -----------------------------------------------------------------------------------------
B = dict(
    T=15,                    # one stroke weight for both parts
    PEAK=(50, 12), SPAN=38,  # roof: apex and half-span; arms at 45 degrees
    EAVE_Y=50,               # roof ends cut level here (eaves), not square to the stroke
    TICK=(43, 86),           # tick corner (centreline)
    SHORT=15, LONG=29,       # tick arm lengths along x (45 degrees, parallel to the roof arms)
)


def mark_b():
    p = B
    px, py = p["PEAK"]
    s = p["SPAN"] + 12  # draw the arms long, then cut them level at the eave line
    roof = outline_polyline([(px - s, py + s), (px, py), (px + s, py + s)], p["T"])
    roof = op(roof, poly([(0, -50), (100, -50), (100, p["EAVE_Y"]), (0, p["EAVE_Y"])]), "INTERSECTION")
    tx, ty = p["TICK"]
    tick = outline_polyline([(tx - p["SHORT"], ty - p["SHORT"]), (tx, ty), (tx + p["LONG"], ty - p["LONG"])], p["T"])
    return {INK: roof, ACCENT: tick}


# ---- C: home in the h ------------------------------------------------------------------------------------------
C = dict(
    STEM_L=16, STEM_W=23, TOP=8, BASE=92,
    XH=34,                   # shoulder top (x-height)
    RIGHT=84, R=30,          # far side and the shoulder's outer radius
    LEG_W=22,                # right leg
    EAVE=66, PITCH=1.0,      # doorway: wall top and roof pitch (45 degrees)
)


def mark_c():
    import pathops

    p = C
    sl, sr = p["STEM_L"], p["STEM_L"] + p["STEM_W"]
    r = p["R"]
    body = pathops.Path()
    body.moveTo(sl, p["TOP"])
    body.lineTo(sr, p["TOP"])
    body.lineTo(sr, p["XH"])
    body.lineTo(p["RIGHT"] - r, p["XH"])
    body.cubicTo(p["RIGHT"] - r + K * r, p["XH"], p["RIGHT"], p["XH"] + r - K * r, p["RIGHT"], p["XH"] + r)
    body.lineTo(p["RIGHT"], p["BASE"])
    body.lineTo(sl, p["BASE"])
    body.close()
    dl, dr = sr, p["RIGHT"] - p["LEG_W"]
    half = (dr - dl) / 2
    door = poly([(dl, p["BASE"] + 4), (dl, p["EAVE"]), (dl + half, p["EAVE"] - half * p["PITCH"]), (dr, p["EAVE"]),
                 (dr, p["BASE"] + 4)])
    return {INK: op(body, door, "DIFFERENCE")}


CANDIDATES = {
    "a": ("A  Lean-to h", "The h is the building: one block, a single-pitch roof, an arched door.", mark_a),
    "b": ("B  Roof & tick", "One weight, one angle: a gable over a tick that runs parallel to it.", mark_b),
    "c": ("C  Home in the h", "A friendly h whose counter is a gabled doorway: the home inside the name.", mark_c),
}


def bounds(parts):
    bs = [p.bounds for p in parts.values()]
    return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))


def reversed_colour(c):
    return {INK: PAGE, ACCENT: BUTTER}[c]


# ---- SVG writers ----------------------------------------------------------------------------------------------
def svg(view, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}">{body}</svg>\n'


def mark_svg(parts):
    x0, y0, x1, y1 = bounds(parts)
    pad = 1
    body = "".join(f'<path fill="{c}" d="{path_d(p)}"/>' for c, p in parts.items())
    return svg(f"{fmt(x0 - pad)} {fmt(y0 - pad)} {fmt(x1 - x0 + 2 * pad)} {fmt(y1 - y0 + 2 * pad)}", body)


ICON_FILL = 0.62  # the mark's larger side over the plate side


def icon_svg(parts):
    x0, y0, x1, y1 = bounds(parts)
    s = ICON_FILL * 100 / max(x1 - x0, y1 - y0)
    dx = 50 - (x0 + x1) / 2 * s
    dy = 50 - (y0 + y1) / 2 * s
    body = f'<rect width="100" height="100" rx="22" fill="{MINT}"/>'
    body += "".join(f'<path fill="{c}" d="{path_d(p, s, dx, dy)}"/>' for c, p in parts.items())
    return svg("0 0 100 100", body)


WORD, SPLIT = "homelean", 4
ASC = 62           # wordmark h ascender height, lock-up units
MARK_RATIO = 1.25  # mark height over the ascender
GAP_RATIO = 0.30   # mark-to-word gap over the ascender
PAD = 2


def word_glyphs():
    import uharfbuzz as hb
    from fontTools.ttLib import TTFont

    f = TTFont(FONT)
    gs, order = f.getGlyphSet(), f.getGlyphOrder()
    buf = hb.Buffer()
    buf.add_str(WORD)
    buf.guess_segment_properties()
    hb.shape(hb.Font(hb.Face(hb.Blob.from_file_path(str(FONT)))), buf, {"kern": True, "liga": True})
    x, glyphs = 0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions, strict=True):
        glyphs.append((order[info.codepoint], x + pos.x_offset, -pos.y_offset))
        x += pos.x_advance
    return glyphs, x, gs


def glyph_d(gs, name, gx, gy, scale, dx, dy):
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen

    pen = SVGPathPen(gs, ntos=fmt)
    gs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, dx + gx * scale, dy - gy * scale)))
    return pen.getCommands()


def logo_svg(parts, on_dark=False):
    from fontTools.pens.boundsPen import BoundsPen

    glyphs, adv, gs = word_glyphs()
    bp = BoundsPen(gs)
    gs["h"].draw(bp)
    scale = ASC / bp.bounds[3]
    x0, y0, x1, y1 = bounds(parts)
    ms = ASC * MARK_RATIO / (y1 - y0)
    base = PAD + (y1 - y0) * ms          # the mark stands on the word's baseline
    mdx, mdy = PAD - x0 * ms, base - y1 * ms
    wx = PAD + (x1 - x0) * ms + ASC * GAP_RATIO
    home_c, lean_c = (PAGE, BUTTER) if on_dark else (INK, ACCENT)
    paint = (lambda c: reversed_colour(c)) if on_dark else (lambda c: c)
    by_colour = {}
    for c, p in parts.items():
        by_colour.setdefault(paint(c), []).append(path_d(p, ms, mdx, mdy))
    by_colour.setdefault(home_c, []).append("".join(glyph_d(gs, n, gx, gy, scale, wx, base)
                                                    for n, gx, gy in glyphs[:SPLIT]))
    by_colour.setdefault(lean_c, []).append("".join(glyph_d(gs, n, gx, gy, scale, wx, base)
                                                    for n, gx, gy in glyphs[SPLIT:]))
    body = "".join(f'<path fill="{c}" d="{"".join(ds)}"/>' for c, ds in by_colour.items())
    return svg(f"0 0 {fmt(wx + adv * scale + PAD)} {fmt(base + PAD)}", body)


# ---- renders --------------------------------------------------------------------------------------------------
def render(svg_path, width, out_png):
    sys.path.insert(0, str(QA))
    from qa_logo import render as qa_render

    if not qa_render(svg_path, width, out_png):
        raise SystemExit(f"no renderer could draw {svg_path}")


def icon_pngs(folder, tmp):
    """512 from the renderer; 64, 32 and 16 drawn at their own size (an SVG favicon is rasterised at size)."""
    from PIL import Image

    for size in (512, 64, 32, 16):
        out = folder / f"icon-{size}.png"
        render(folder / "icon.svg", size, out)
        im = Image.open(out)
        if im.size != (size, size):  # a renderer with a minimum window: fall back to an area-averaged downsample
            big = tmp / f"{folder.name}-1024.png"
            render(folder / "icon.svg", 1024, big)
            Image.open(big).convert("RGBA").resize((size, size), Image.Resampling.BOX).save(out, optimize=True)
        else:
            im.save(out, optimize=True)


def contact_sheet(tmp):
    from PIL import Image, ImageDraw, ImageFont

    W, ROW, TOPH = 1600, 400, 92
    sheet = Image.new("RGB", (W, TOPH + ROW * len(CANDIDATES) + 24), PAGE)
    d = ImageDraw.Draw(sheet)
    head = ImageFont.truetype(str(FONT), 30)
    lab = ImageFont.truetype(str(FONT), 22)
    small = ImageFont.truetype(str(FONT), 16)
    d.text((40, 28), "Homelean icon mark: candidates A, B, C (drafts for Forhad's choice)", font=head, fill=INK)
    for i, (key, (name, idea, _)) in enumerate(CANDIDATES.items()):
        folder = HERE / key
        y = TOPH + i * ROW
        d.line([(40, y), (W - 40, y)], fill=MINT, width=2)
        d.text((40, y + 14), name, font=lab, fill=INK)
        d.text((260, y + 18), idea, font=small, fill=ACCENT)
        # big icon
        render(folder / "icon.svg", 300, tmp / f"{key}-300.png")
        big = Image.open(tmp / f"{key}-300.png").convert("RGBA")
        sheet.paste(big, (40, y + 60), big)
        # true sizes on page and on ink, plus a 4x pixel zoom of the 16 px render
        x = 370
        for ground, gy in ((PAGE, y + 60), (INK, y + 200)):
            d.rectangle([x - 10, gy, x + 250, gy + 120], fill=ground)
            cx = x + 6
            for size in (64, 32, 16):
                im = Image.open(folder / f"icon-{size}.png").convert("RGBA")
                sheet.paste(im, (cx, gy + 60 - size // 2), im)
                cx += size + 22
            z = Image.open(folder / "icon-16.png").convert("RGBA").resize((64, 64), Image.Resampling.NEAREST)
            sheet.paste(z, (cx + 6, gy + 28), z)
        d.text((370, y + 330), "64 / 32 / 16 px true size, then 16 px at 4x", font=small, fill=INK)
        # logos
        for j, (fname, ground) in enumerate((("logo.svg", PAGE), ("logo-on-ink.svg", INK))):
            ly = y + 60 + j * 160
            d.rectangle([680, ly, W - 40, ly + 140], fill=ground if j else "#ffffff")
            render(folder / fname, 600, tmp / f"{key}-{j}.png")
            lg = Image.open(tmp / f"{key}-{j}.png").convert("RGBA")
            sheet.paste(lg, (720, ly + (140 - lg.height) // 2), lg)
            render(folder / fname, 150, tmp / f"{key}-{j}-s.png")
            sm = Image.open(tmp / f"{key}-{j}-s.png").convert("RGBA")
            sheet.paste(sm, (W - 40 - 40 - sm.width, ly + (140 - sm.height) // 2), sm)
    sheet.save(HERE / "sheet.png", optimize=True)


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="homelean-cand-"))
    for key, (_, _, build) in CANDIDATES.items():
        parts = build()
        folder = HERE / key
        folder.mkdir(exist_ok=True)
        (folder / "mark.svg").write_text(mark_svg(parts))
        (folder / "icon.svg").write_text(icon_svg(parts))
        (folder / "logo.svg").write_text(logo_svg(parts))
        (folder / "logo-on-ink.svg").write_text(logo_svg(parts, on_dark=True))
        icon_pngs(folder, tmp)
        print(key, "ok")
    contact_sheet(tmp)
    print("sheet.png written; scratch renders in", tmp)


if __name__ == "__main__":
    main()
