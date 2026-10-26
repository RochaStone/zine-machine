#!/usr/bin/env python3
"""Zine Machine: five posts in, one fold-and-cut mini zine out.

  python3 zine.py build <posts...> --config zine.config.json --out out/
  python3 zine.py check

<posts> can be markdown or .txt files, a folder of them, one markdown file with --- page
breaks, or public Substack post links. Python 3.10+, standard library only; a browser
(Chrome, Chromium, Edge, Brave, or Playwright) turns the pages into PDF and PNG.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if sys.version_info < (3, 10):
    sys.exit("Zine Machine needs Python 3.10 or newer.")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from zinelib import inputs, layout, pages, style  # noqa: E402
from zinelib.browser import RenderError, find_chrome, get_renderer  # noqa: E402

STORY_W, STORY_H = 1080, 1920
PREVIEW_W, PREVIEW_H = 1600, 900
REQUIRED = ("zine_name",)


def load_config(path: Path | None, style_data: dict | None = None, style_words: bool = True) -> tuple[dict, list[str]]:
    cfg: dict = {}
    if path:
        try:
            cfg = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            sys.exit(f"config not found: {path}")
        except json.JSONDecodeError as err:
            sys.exit(f"config is not valid JSON ({path}): {err}")
    warnings = []
    style.apply_style(cfg, style_data or {}, style_words)
    cfg.setdefault("masthead", "newspaper")
    if cfg["masthead"] not in ("newspaper", "magazine"):
        warnings.append(f"masthead '{cfg['masthead']}' unknown, using newspaper")
        cfg["masthead"] = "newspaper"
    # the house mastheads, only when no personal style exists; a personal style never falls back to her words
    house = "THE ROCHEVERSE TIMES" if cfg["masthead"] == "newspaper" else "ROCHEVERSE"
    cfg.setdefault("zine_name", house if not style_words else style.NEUTRAL_MASTHEAD)
    cfg.setdefault("date", pages.default_date())
    cfg.setdefault("author", "")
    cfg.setdefault("handle", "")
    if cfg["handle"] and not cfg["handle"].startswith("@"):
        cfg["handle"] = "@" + cfg["handle"]
    return cfg, warnings


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def build(args) -> int:
    try:
        style_path = style.find_style(args.style)
    except FileNotFoundError as err:
        print(err)
        return 2
    style_data, warnings = style.load_style(style_path)
    if style_path != style.BUNDLED:
        example, _ = style.load_style(style.BUNDLED)
        style_data = style.inherit(style_data, example)
    cfg, w = load_config(Path(args.config) if args.config else None, style_data, style_path != style.BUNDLED)
    warnings += w
    style_css, cfg["_font_links"], w = style.css_and_fonts(style_data)
    warnings += w
    print(f"style: {style_path.name}" + (" (the bundled example)" if style_path == style.BUNDLED else ""))
    posts, w = inputs.collect(args.inputs)
    warnings += w
    if not posts:
        for line in warnings:
            print(f"! {line}")
        print("No posts to make a zine from.")
        return 2

    capacity = int(cfg.get("words_per_page", layout.CAPACITY))
    result, scale = layout.fit(posts, capacity)
    cfg["_type_scale"] = round(scale, 3)
    base_css, _ = pages.palette_vars({})
    override_css, w = pages.palette_vars(cfg.get("palette"), only_overrides=True)
    css_vars = base_css + style_css + override_css  # zine.config.json palette beats style.json
    warnings += w

    out = Path(args.out)
    html_dir = out / "html"
    built = pages.build_pages(cfg, posts, result)
    screen = write(html_dir / "zine-screen.html", pages.screen_doc(built, cfg, css_vars))
    sheet = write(html_dir / "zine-print.html", pages.print_doc(built, cfg, css_vars))
    preview = write(html_dir / "preview.html", pages.preview_doc(built[1], cfg, css_vars))
    stories = [write(html_dir / f"story-{n:02d}.html", pages.story_doc(n, built[n], cfg, css_vars))
               for n in range(1, layout.TOTAL_PAGES + 1)] if not args.no_stories else []

    print(f"{len(posts)} posts, {sum(len(p['items']) for p in result['pages'])} blocks on pages 2 to 7")
    size = round(100 / scale ** 0.5)
    if size != 100:
        print(f"type set at {size}% of normal size so the words fill the pages")
    if result["overflow_words"]:
        warnings.append(f"{result['overflow_words']} words did not fit and were left out. "
                        "Choose fewer or shorter posts, keeping whole sentences, and build again.")
    empty = [n for n, p in zip(layout.CONTENT_PAGES, result["pages"]) if not p["items"]]
    if empty:
        print(f"pages {', '.join(map(str, empty))} became Notes pages (not enough words to fill them)")

    renderer, message = get_renderer(args.renderer)
    if renderer is None:
        for line in warnings:
            print(f"! {line}")
        print(f"\nNo PDFs this time: {message}.")
        print(f"Your zine is ready as HTML in {html_dir}/")
        print("To print it: open zine-print.html in Chrome, Print, Save as PDF, Layout Landscape,")
        print("Margins None, Background graphics on. The pages are already in fold order.")
        return 0

    print(message)
    try:
        renderer.pdf(screen, out / "zine-screen.pdf")
        renderer.pdf(sheet, out / "zine-print.pdf")
        renderer.png(preview, out / "preview.png", PREVIEW_W, PREVIEW_H)
        for n, story in enumerate(stories, start=1):
            (out / "stories").mkdir(parents=True, exist_ok=True)
            renderer.png(story, out / "stories" / f"page-{n:02d}.png", STORY_W, STORY_H)
    except RenderError as err:
        print(f"! render failed: {err}")
        print(f"The HTML versions are in {html_dir}/ and print fine from any browser.")
        return 1
    finally:
        renderer.close()

    for line in warnings:
        print(f"! {line}")
    print(f"\nDone. In {out}/:")
    print("  zine-print.pdf    one A4 landscape sheet. Print it, cut the red line, fold (see FOLDING.md)")
    print("  zine-screen.pdf   the eight pages in reading order, for sending")
    if stories:
        print("  stories/          page-01.png to page-08.png, 1080 x 1920, for Instagram stories")
    print("  preview.png       a share image: your cover next to the folding sheet")
    return 0


def check(_args) -> int:
    print(f"Python {sys.version.split()[0]}: ok")
    renderer, message = get_renderer("auto")
    if renderer:
        renderer.close()
        print(f"Browser: ok, {message}")
        return 0
    chrome = find_chrome()
    print(f"Browser: missing ({message})." if not chrome else f"Browser: {chrome}")
    print("Without a browser you still get the HTML pages, ready to print from any browser.")
    return 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="zine.py", description="Five posts in, one fold-and-cut mini zine out.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="make the zine")
    b.add_argument("inputs", nargs="+", help="markdown or .txt files, a folder, or public Substack post links")
    b.add_argument("--config", help="zine.config.json")
    b.add_argument("--style", help="style.json (default: ./style.json, ~/.rocha-coded/style.json, then the bundled example)")
    b.add_argument("--out", default="out", help="output folder (default: out)")
    b.add_argument("--renderer", default="auto", choices=("auto", "playwright", "chrome", "html"))
    b.add_argument("--no-stories", action="store_true", help="skip the Instagram story PNGs")
    b.set_defaults(func=build)
    c = sub.add_parser("check", help="see whether this computer can render PDFs")
    c.set_defaults(func=check)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
