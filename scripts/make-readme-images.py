#!/usr/bin/env python3
"""Makes every image in the README from the example zine, with the tool's own renderer.

  python3 scripts/make-readme-images.py

Writes docs/img/: hero.png (the zine inside a y2k-blog window), triptych.png (the same cover in
analog, cyberpunk and y2k-blog), stories.png, print-sheet.png, and the small pixel SVGs
(step-01.svg to step-05.svg, divider.svg, heart.svg). Needs Chrome or Playwright, like zine.py.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import zine  # noqa: E402
from zinelib import inputs, layout, pages, style  # noqa: E402
from zinelib.browser import get_renderer  # noqa: E402
from zinelib.skins import HEART, HIT_COUNTER, pixel_svg  # noqa: E402

IMG = ROOT / "docs" / "img"
EXAMPLE = ROOT / "examples"
MOTIFS = ("analog", "cyberpunk", "y2k-blog")

# 3x5 pixel digits for the step badges (no web fonts inside README SVGs, so they draw themselves)
DIGITS = {"0": ("XXX", "X.X", "X.X", "X.X", "XXX"), "1": (".X.", "XX.", ".X.", ".X.", "XXX"),
          "2": ("XXX", "..X", "XXX", "X..", "XXX"), "3": ("XXX", "..X", ".XX", "..X", "XXX"),
          "4": ("X.X", "X.X", "XXX", "..X", "..X"), "5": ("XXX", "X..", "XXX", "..X", "XXX")}
PLUM, GOLD = "#50163C", "#E9B949"


def step_badge(n: int) -> str:
    rects, x = [], 3
    for d in f"{n:02d}":
        for y, row in enumerate(DIGITS[d]):
            rects += [f'<rect x="{x + i}" y="{2 + y}" width="1" height="1"/>' for i, c in enumerate(row) if c == "X"]
        x += 4
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 13 9" width="39" height="27" shape-rendering="crispEdges">'
            f'<rect width="13" height="9" fill="{PLUM}"/><g fill="{GOLD}">{"".join(rects)}</g></svg>\n')


def divider() -> str:
    dots = "".join(f'<rect x="{x}" y="0" width="2" height="1"/>' for x in range(0, 160, 4))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 1" width="480" height="3" shape-rendering="crispEdges">'
            f'<g fill="{GOLD}">{dots}</g></svg>\n')


def heart() -> str:
    svg = pixel_svg(HEART, "", GOLD).replace('class="px-icon "', 'xmlns="http://www.w3.org/2000/svg" width="27" height="18"')
    return svg.replace(' aria-hidden="true"', "") + "\n"


def example_zine(motif: str):
    cfg_data = json.loads((EXAMPLE / "style.rocha-coded.json").read_text(encoding="utf-8"))
    cfg, _ = zine.load_config(EXAMPLE / "zine.config.json", cfg_data, style_words=False)
    cfg["motif"] = motif
    style_css, cfg["_font_links"], _ = style.css_and_fonts(cfg_data)
    posts, _ = inputs.collect([str(EXAMPLE / "input")])
    result, scale = layout.fit(posts, int(layout.CAPACITY * zine.MOTIF_CAPACITY[motif]))
    cfg["_type_scale"] = round(scale, 3)
    base, _ = pages.palette_vars({})
    return cfg, pages.build_pages(cfg, posts, result), base + style_css


EXTRA = """<style>
.frame { position: relative; overflow: hidden; }
.card { position: absolute; overflow: hidden; box-shadow: 0 22px 44px rgba(20,4,14,.45), 0 4px 10px rgba(20,4,14,.3); }
.card > .page { transform-origin: 0 0; }
.cap { position: absolute; font-family: var(--f-pixel); color: var(--cream); font-size: 26px; text-align: center; }
.hero-win { position: absolute; left: 60px; top: 50px; width: 1480px; height: 800px; background: var(--cream);
  border: 3px solid var(--plum); box-shadow: 14px 14px 0 var(--wine); }
.hero-win .bar { height: 46px; background: var(--plum); display: flex; align-items: center; gap: 14px; padding: 0 16px; }
.hero-win .bar i { width: 16px; height: 16px; border-radius: 50%; background: var(--gold); }
.hero-win .bar span { flex: 1; text-align: center; color: var(--cream); font-family: var(--f-pixel); font-size: 22px; margin-right: 80px; }
.status { position: absolute; left: 30px; right: 30px; bottom: 22px; display: flex; gap: 40px; font-family: var(--f-mono);
  font-size: 19px; color: var(--ink); border-top: 2px dotted var(--wine); padding-top: 14px; }
.status b { background: var(--plum); color: var(--gold); font-weight: 500; padding: 2px 8px; letter-spacing: .08em; }
.hero-title { position: absolute; left: 1010px; top: 110px; width: 470px; }
.hero-title h1 { font-family: var(--f-display); font-weight: 900; font-size: 64px; line-height: .95; letter-spacing: -.03em; color: var(--plum); }
.hero-title p { font-family: var(--f-label); font-size: 23px; line-height: 1.4; color: var(--ink); margin-top: 22px; }
.hero-title .px { font-family: var(--f-pixel); font-size: 17px; color: var(--cream); background: var(--wine); display: inline-block;
  padding: 4px 10px; margin-top: 26px; }
.strip img { position: absolute; top: 40px; width: 288px; box-shadow: 0 18px 36px rgba(20,4,14,.45); }
</style>"""


def card(page_html: str, left: int, top: int, width: int, rot: float = 0) -> str:
    scale = width / 561.3  # a page is 148.5 mm = 561.3 px wide
    return (f'<div class="card" style="left:{left}px;top:{top}px;width:{width}px;height:{width * 1.4141:.1f}px;'
            f'transform:rotate({rot}deg)"><div class="page-wrap" style="transform:scale({scale:.4f});transform-origin:0 0">'
            f'{page_html}</div></div>')


def main() -> int:
    renderer, message = get_renderer("auto")
    if renderer is None:
        print(f"Cannot make images: {message}")
        return 1
    IMG.mkdir(parents=True, exist_ok=True)
    for n in range(1, 6):
        (IMG / f"step-{n:02d}.svg").write_text(step_badge(n), encoding="utf-8")
    (IMG / "divider.svg").write_text(divider(), encoding="utf-8")
    (IMG / "heart.svg").write_text(heart(), encoding="utf-8")

    zines = {m: example_zine(m) for m in MOTIFS}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        def shoot(name: str, body: str, cfg: dict, css: str, w: int, h: int, out: Path) -> None:
            doc = pages.document(EXTRA + body, name, cfg, css)
            src = tmp / f"{name}.html"
            src.write_text(doc, encoding="utf-8")
            renderer.png(src, out, w, h)
            print(f"wrote {out.relative_to(ROOT)}")

        cfg, built, css = zines["y2k-blog"]
        hero = f"""<div class="frame y2k" style="width:1600px;height:900px">
<div class="hero-win"><div class="bar"><i></i><i></i><i></i><span>zine-machine.exe</span></div></div>
{card(built[1], 110, 130, 430, -2)}{card(built[3], 560, 150, 410, 2)}
<div class="hero-title"><h1>Five posts in. One sheet out.</h1>
<p>Print it, cut one line, fold it, hand it to someone. Or post the eight pages as stories.</p>
<span class="px">analog · cyberpunk · y2k-blog</span></div>
<div class="status" style="left:90px;right:90px;bottom:70px"><span>you are visitor no. <b>{HIT_COUNTER}</b></span><span>mood: ✧</span>
<span>last updated {cfg['date']}</span></div></div>"""
        shoot("hero", hero, cfg, css, 1600, 900, IMG / "hero.png")

        cfg_a, _, css_a = zines["analog"]
        trip = '<div class="frame" style="width:1600px;height:820px;background:var(--plum)">'
        for i, m in enumerate(MOTIFS):
            left = 90 + i * 490
            trip += card(zines[m][1][1], left, 50, 440) + f'<p class="cap" style="left:{left}px;width:440px;top:700px">{m}</p>'
        shoot("triptych", trip + "</div>", cfg_a, css_a, 1600, 820, IMG / "triptych.png")

        shots = []
        for m, n in (("analog", 1), ("analog", 4), ("cyberpunk", 1), ("y2k-blog", 3), ("analog", 8)):
            c, b, s = zines[m]
            src = tmp / f"story-{m}-{n}.html"
            src.write_text(pages.story_doc(n, b[n], c, s), encoding="utf-8")
            png = tmp / f"story-{m}-{n}.png"
            renderer.png(src, png, 1080, 1920)
            shots.append(png)
        strip = '<div class="frame strip" style="width:1600px;height:600px;background:var(--blush)">'
        strip += "".join(f'<img src="{p.name}" style="left:{60 + i * 300}px">' for i, p in enumerate(shots))
        shoot("stories", strip + "</div>", cfg_a, css_a, 1600, 600, IMG / "stories.png")

        sheet = tmp / "sheet.html"
        sheet.write_text(pages.print_doc(zines["analog"][1], cfg_a, css_a), encoding="utf-8")
        renderer.png(sheet, IMG / "print-sheet.png", 1123, 794)
        print("wrote docs/img/print-sheet.png")
    renderer.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
