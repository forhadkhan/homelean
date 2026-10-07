#!/usr/bin/env python3
"""Roll the chosen Homelean logo (candidate A, Outfit SemiBold) out to every file in brand/.

    uv run --no-project --with pillow --with numpy --with fonttools --with uharfbuzz --with skia-pathops \
        python brand/source/build_logo.py

The drawing itself comes from `brand/candidates2/build_candidates.py` (candidate "a"): "homelean" set in Outfit
Medium (read in place from the font library, never copied or modified, outlines only in the SVGs), with the h's
counter recut as a gabled doorway. The icon is that same h on a mint plate. This script writes the SVG masters and
exports the PNGs from them.
"""

import importlib.util
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
BRAND = HERE.parent
QA = pathlib.Path.home() / "karkhana/skills/brand-identity/scripts"
CHOSEN = "a"

INK, ACCENT, MINT, PAGE, BUTTER = "#0e2b22", "#1f7a55", "#d9f0e3", "#f6faf7", "#fbefc4"


def masters():
    spec = importlib.util.spec_from_file_location("cands", BRAND / "candidates2/build_candidates.py")
    cands = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cands)
    c = cands.CANDIDATES[CHOSEN]
    glyphs, hh, meas = cands.word(cands.Face(c["font"]), c)
    files = cands.wordmark_svgs(glyphs, meas)
    return {
        "logo.svg": files["wordmark.svg"],
        "logo-reversed.svg": files["wordmark-reversed.svg"],
        "logo-mono.svg": files["wordmark-mono.svg"],
        "icon.svg": cands.icon_svg(hh, meas),
        "favicon.svg": cands.favicon_svg(hh, meas),
    }


# ---- exports --------------------------------------------------------------------------------------------------
def render(svg_path, width, out_png):
    sys.path.insert(0, str(QA))
    from qa_logo import render as qa_render

    if not qa_render(svg_path, width, out_png):
        raise SystemExit(f"no renderer could draw {svg_path}")


def exports(tmp):
    from PIL import Image

    tmp.mkdir(parents=True, exist_ok=True)
    render(BRAND / "icon.svg", 512, BRAND / "icon-512.png")
    # the touch icon is solid: the plate already fills the square at 180 px; flatten onto mint so the corners
    # (transparent in the SVG's rounded plate) are filled too, since iOS applies its own mask
    render(BRAND / "icon.svg", 180, tmp / "touch.png")
    im = Image.open(tmp / "touch.png").convert("RGBA")
    flat = Image.new("RGBA", im.size, MINT)
    flat.alpha_composite(im)
    flat.convert("RGB").save(BRAND / "apple-touch-icon-180.png", optimize=True)
    render(BRAND / "logo.svg", 1200, BRAND / "logo-1200.png")
    # og image: the light lock-up 760 px wide, centred on the page colour, over a thin band of the mark's accent green
    render(BRAND / "logo.svg", 760, tmp / "og-logo.png")
    lg = Image.open(tmp / "og-logo.png").convert("RGBA")
    og = Image.new("RGBA", (1200, 630), PAGE)
    band = Image.new("RGBA", (1200, 18), ACCENT)
    og.alpha_composite(band, (0, 630 - 18))
    og.alpha_composite(lg, ((1200 - lg.width) // 2, (630 - 18 - lg.height) // 2))
    og.convert("RGB").save(BRAND / "og-1200x630.png", optimize=True)
    Image.open(BRAND / "icon-512.png").save(BRAND / "icon-512.png", optimize=True)
    Image.open(BRAND / "logo-1200.png").save(BRAND / "logo-1200.png", optimize=True)


def main():
    from PIL import Image  # noqa: F401  (fail early if missing)

    for name, text in masters().items():
        (BRAND / name).write_text(text)
        print(f"{name}: {len((BRAND / name).read_bytes())} bytes")
    exports(pathlib.Path(tempfile.mkdtemp(prefix="homelean-brand-")))
    for n in ("icon-512.png", "apple-touch-icon-180.png", "logo-1200.png", "og-1200x630.png"):
        print(f"{n}: {(BRAND / n).stat().st_size} bytes")


if __name__ == "__main__":
    main()
