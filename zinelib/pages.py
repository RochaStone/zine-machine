"""Build the HTML for each of the eight pages and for every output document."""
from __future__ import annotations

import base64
import html
import random
import re
import struct
import zlib
from datetime import date
from pathlib import Path

from . import stickers
from .layout import CONTENT_PAGES, TOTAL_PAGES, imposition

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
FONTS = ("https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@500;700"
         "&family=Bodoni+Moda:ital,wght@0,400..900;1,400..900&family=Fraunces:ital,wght@0,400..900;1,400..900"
         "&family=Newsreader:ital,wght@0,400;0,600;1,400&family=Permanent+Marker&family=Caveat:wght@700&display=swap")

PALETTE = {
    "hot": "#FF2D8A", "candy": "#FFB3D1", "pink-paper": "#FFE1EC", "cream": "#F6EFE4", "ink": "#111111",
    "red": "#E0202E", "plum": "#4A1033", "gold": "#D4A64A", "blue": "#BFD4EA", "white": "#FFFFFF",
}
PALETTE_ALIASES = {
    "hot_pink": "hot", "candy_pink": "candy", "pale_pink": "pink-paper", "pink_paper": "pink-paper",
    "cream_paper": "cream", "marker_red": "red", "gold_sparkle": "gold", "pale_blue": "blue",
}
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def grain_png(size: int = 96, seed: int = 7) -> str:
    """A small tile of ink-coloured noise as a PNG data URI. One tile repeats across every page,
    so the PDF stays small (an SVG noise filter gets rasterised per page and bloats it)."""
    rng = random.Random(seed)
    rows = b"".join(b"\x00" + bytes(v for _ in range(size) for v in (17, 10, 14, rng.choice((0, 0, 0, 6, 12, 20)))) for _ in range(size))
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")
    return "data:image/png;base64," + base64.b64encode(png).decode()


# Runs inside the browser before printing: if a page's words spill past the bottom margin
# (the word budget is an estimate), shrink that page's type a step at a time until it fits.
AUTOFIT_JS = """<script>
(function(){
  function fitAll(){
    document.querySelectorAll('.page.inner').forEach(function(pg){
      var s = parseFloat(getComputedStyle(pg).getPropertyValue('--type-scale')) || 1, n = 0;
      while (pg.scrollHeight > pg.clientHeight + 1 && n < 14) { s = s * 1.07; pg.style.setProperty('--type-scale', s); n++; }
      if (n) pg.setAttribute('data-autofit', n);
    });
  }
  if (document.fonts && document.fonts.ready) { document.fonts.ready.then(fitAll); } else { fitAll(); }
  window.addEventListener('load', fitAll);
})();
</script>"""


def esc(text: str) -> str:
    """Escape, then turn **bold** and *em* / _em_ into tags."""
    out = html.escape(text, quote=True)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", out)
    out = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", out)
    return out.replace("**", "")


def plain(text: str) -> str:
    return html.escape(re.sub(r"(\*\*|\*|__|_)", "", text), quote=True)


def palette_vars(overrides: dict | None, only_overrides: bool = False) -> tuple[str, list[str]]:
    pal, warnings, changed = dict(PALETTE), [], {}
    for key, value in (overrides or {}).items():
        name = PALETTE_ALIASES.get(key.replace("-", "_"), key.replace("_", "-"))
        if name not in pal:
            warnings.append(f"palette: unknown colour '{key}', ignored (known: {', '.join(PALETTE)})")
        elif not isinstance(value, str) or not HEX.match(value):
            warnings.append(f"palette: '{key}' must look like #FF2D8A, ignored")
        else:
            pal[name] = changed[name] = value
    if only_overrides:
        return (":root{" + "".join(f"--{k}:{v};" for k, v in changed.items()) + "}") if changed else "", warnings
    css = ":root{" + "".join(f"--{k}:{v};" for k, v in pal.items()) + f'--grain:url("{grain_png()}");' + "}"
    return css, warnings


def _fit_size(text: str, sizes: tuple[tuple[int, str], ...]) -> str:
    n = len(text)
    for limit, size in sizes:
        if n <= limit:
            return size
    return sizes[-1][1]


# ---------------------------------------------------------------- the eight pages

def cover_newspaper(cfg: dict, posts, layout: dict) -> str:
    name = cfg["zine_name"]
    headline = cfg.get("cover_line") or (posts[0].title if posts else name)
    first_text = next((b.text for b in (posts[0].blocks if posts else []) if b.kind == "p"), "")
    words = re.sub(r"(\*\*|\*|__|_)", "", first_text).split()
    teaser = " ".join(words[:60]) + (" …" if len(words) > 60 else "")
    quote = cfg.get("cover_quote") or next((b.text for p in posts for b in p.blocks if b.kind == "quote"), "")
    quote_box = (f'<div class="qotd"><span class="inside-h">Quote of the day</span><p>{plain(quote)}</p></div>'
                 if quote else "")
    inside = "".join(f"<li><b>{p}</b><span>{plain(t)}</span></li>" for p, t in contents(posts, layout)[:6])
    mast = _fit_size(name, ((14, "44pt"), (18, "34pt"), (22, "29pt"), (30, "24pt"), (999, "20pt")))
    head = _fit_size(headline, ((30, "32pt"), (55, "26pt"), (90, "21pt"), (999, "18pt")))
    byline = " · ".join(x for x in (cfg.get("author"), cfg.get("handle")) if x)
    dateline = ", ".join(x for x in (cfg.get("place"), cfg["date"]) if x)
    return f"""<section class="page cover news" style="--mast-size:{mast};--head-size:{head}">
<div class="ear"><span>Vol. 1 · No. {html.escape(str(cfg.get('issue', 1)))}</span><span>Free · Pass it on</span></div>
<h1 class="masthead">{plain(name)}</h1>
<div class="dateline"><span>{html.escape(dateline)}</span><span>{html.escape(byline)}</span></div>
<div class="kicker">BREAKING NEWS</div>
<h2 class="headline">{plain(headline)}</h2>
<div class="cols"><div><p class="teaser">{plain(teaser)}</p><p class="more">read it all on page 2</p></div>
<div><p class="inside-h">Inside</p><ul class="inside">{inside}</ul></div></div>
{quote_box}
{stickers.SEVENS}{stickers.HEART}
</section>"""


def cover_magazine(cfg: dict, posts, layout: dict) -> str:
    name = cfg["zine_name"]
    titles = contents(posts, layout)
    scrawl = cfg.get("scrawl") or (titles[0][1].lower() if titles else name.lower())
    spine = cfg.get("spine") or [t for _, t in titles[:4]]
    lead = cfg.get("cover_line") or (posts[0].title if posts else "")
    rest = titles[1:4]
    lines = f'<div class="line lead">{plain(lead)}</div>' if lead else ""
    lines += "".join(f'<div class="line">{plain(t)}<small>page {p}</small></div>' for p, t in rest)
    mast = _fit_size(name, ((6, "72pt"), (8, "56pt"), (10, "48pt"), (14, "38pt"), (20, "28pt"), (999, "22pt")))
    scrawl_size = _fit_size(scrawl, ((16, "40pt"), (26, "32pt"), (40, "25pt"), (999, "20pt")))
    spine_html = " / ".join(plain(x) for x in spine)
    return f"""<section class="page cover mag" style="--mast-size:{mast};--scrawl-size:{scrawl_size}">
<div class="spine"><span>{spine_html}</span></div>
<div class="issue"><span>Issue {html.escape(str(cfg.get('issue', 1)).zfill(2))}</span><span>{html.escape(cfg['date'])}</span></div>
<h1 class="title">{plain(name)}</h1>
<div class="art">{stickers.HEART}{stickers.BUTTERFLY}{stickers.EVIL_EYE}{stickers.SEVENS}{stickers.SPARKLE}</div>
<div class="scrawl">{plain(scrawl)}</div>
<div class="lines">{lines}</div>
<div class="handle">{html.escape(cfg.get('handle', ''))}</div>
</section>"""


def contents(posts, layout: dict) -> list[tuple[int, str]]:
    """(page number, title) for every post title that made it into the zine."""
    found = []
    for n, page in zip(CONTENT_PAGES, layout["pages"]):
        for item in page["items"]:
            if item["kind"] == "title":
                found.append((n, item["text"]))
    return found


def inner_page(n: int, page: dict, cfg: dict) -> str:
    paper = cfg.get("paper", "alternate")
    tone = {"pink": "paper-pink", "cream": "paper-cream"}.get(paper, "paper-pink" if n % 2 == 0 else "paper-cream")
    head = f'<div class="tag-row"><span class="tag">{plain(cfg["zine_name"])}</span><span class="tag hot">P. {n}</span></div>'
    if not page["items"]:
        body = ('<p class="notes-sub">your page</p><p class="notes-head">Notes</p>'
                '<ul class="todo"><li>make art</li><li>call the girls</li><li>be hot</li><li>pass this on</li></ul>')
        return f'<section class="page inner {tone}">{head}{body}{stickers.for_page(n)}<div class="folio">{n}</div></section>'
    parts = []
    if page["continued_from"]:
        parts.append('<p class="cont-from">continued</p>')
    in_list = False
    for item in page["items"]:
        if item["kind"] == "li" and not in_list:
            parts.append("<ul>")
            in_list = True
        if item["kind"] != "li" and in_list:
            parts.append("</ul>")
            in_list = False
        if item["kind"] == "title":
            parts.append(f'<h2 class="post-title">{plain(item["text"])}</h2>')
        elif item["kind"] == "quote":
            parts.append(f'<blockquote class="pull">{esc(item["text"])}</blockquote>')
        elif item["kind"] == "li":
            parts.append(f'<li>{esc(item["text"])}</li>')
        else:
            parts.append(f'<p>{esc(item["text"])}</p>')
    if in_list:
        parts.append("</ul>")
    if page["continues"]:
        parts.append(f'<p class="cont-to">continued on page {n + 1}</p>')
    return f'<section class="page inner {tone}">{head}{"".join(parts)}{stickers.for_page(n)}<div class="folio">{n}</div></section>'


def back_cover(cfg: dict, posts) -> str:
    note = cfg.get("back_note")
    if not note:
        quote = next((b.text for p in posts for b in p.blocks if b.kind == "quote"), "")
        note = quote or "Made by hand, folded by hand, passed hand to hand."
    handle = cfg.get("handle", "")
    return f"""<section class="page back">
<p class="tag hot pass">Pass it on</p>
<p class="thanks">thank you for reading</p>
<p class="note">{plain(note)}</p>
<div class="who"><p class="handle">{html.escape(handle)}</p><p class="name">{html.escape(cfg.get('author', ''))}</p></div>
<p class="made">made with Zine Machine</p>
{stickers.LUCKY}{stickers.BUTTERFLY}{stickers.SPARKLE}{stickers.EVIL_EYE}
</section>"""


def build_pages(cfg: dict, posts, layout: dict) -> dict[int, str]:
    """All eight pages as HTML fragments, keyed by page number."""
    cover = cover_magazine if cfg.get("masthead") == "magazine" else cover_newspaper
    pages = {1: cover(cfg, posts, layout), TOTAL_PAGES: back_cover(cfg, posts)}
    for n, page in zip(CONTENT_PAGES, layout["pages"]):
        pages[n] = inner_page(n, page, cfg)
    return pages


# ---------------------------------------------------------------- documents

def document(body: str, title: str, cfg: dict, css_vars: str, body_class: str = "") -> str:
    css = (TEMPLATES / "zine.css").read_text(encoding="utf-8")
    scale = cfg.get("_type_scale", 1)
    extra_fonts = "".join('<link rel="stylesheet" href="%s">' % html.escape(u) for u in cfg.get("_font_links", []))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{plain(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">{extra_fonts}
<style>{css}
{css_vars}
:root{{--type-scale:{scale};}}</style></head>
<body class="{body_class}">{body}{AUTOFIT_JS}</body></html>"""


def screen_doc(pages: dict[int, str], cfg: dict, css_vars: str) -> str:
    body = "".join(pages[n] for n in range(1, TOTAL_PAGES + 1))
    return document(body, cfg["zine_name"], cfg, css_vars, "doc-screen")


def print_doc(pages: dict[int, str], cfg: dict, css_vars: str) -> str:
    slots = []
    for s in imposition():
        left, top = s["col"] * 74.25, s["row"] * 105
        flip = " flip" if s["rotate"] == 180 else ""
        slots.append(f'<div class="slot{flip}" style="left:{left}mm;top:{top}mm">{pages[s["page"]]}</div>')
    guides = "".join(f'<div class="guide fold-v" style="left:{c * 74.25}mm"></div>' for c in (1, 2, 3))
    guides += '<div class="guide fold-h"></div><div class="guide cut"></div><div class="cut-label">CUT</div>'
    return document(f'<div class="sheet">{"".join(slots)}{guides}</div>', cfg["zine_name"] + " print sheet", cfg, css_vars)


def story_doc(n: int, page_html: str, cfg: dict, css_vars: str) -> str:
    tilt = ("-1.6deg", "1.4deg", "-0.8deg", "1.8deg")[n % 4]
    body = f"""<div class="story">
<div class="top"><span class="tag">{plain(cfg['zine_name'])}</span><span class="tag hot">{n} / {TOTAL_PAGES}</span></div>
<div class="card" style="--tilt:{tilt}">{page_html}</div>
{stickers.SPARKLE if n % 2 else stickers.HEART}
<div class="bottom">{'swipe for the next page' if n < TOTAL_PAGES else html.escape(cfg.get('handle') or 'pass it on')}</div>
</div>"""
    return document(body, f"{cfg['zine_name']} story {n}", cfg, css_vars)


def sheet_diagram_svg() -> str:
    """The fold-one-sheet layout as a drawing, for the preview image and the folding guide."""
    w, h, cells = 180, 250, []
    for s in imposition():
        x, y = 10 + s["col"] * w, 10 + s["row"] * h
        fill = "var(--hot)" if s["page"] == 1 else ("var(--candy)" if s["page"] == 8 else "var(--white)")
        label_y = y + h / 2 + 30
        rot = f' transform="rotate(180 {x + w / 2} {y + h / 2})"' if s["rotate"] else ""
        name = {1: "COVER", 8: "BACK"}.get(s["page"], f"PAGE {s['page']}")
        cells.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="var(--ink)" stroke-width="4"/>'
                     f'<g{rot}><text x="{x + w / 2}" y="{label_y - 40}" text-anchor="middle" font-family="Bodoni Moda, Didot, serif" '
                     f'font-weight="800" font-size="84" fill="var(--ink)">{s["page"]}</text>'
                     f'<text x="{x + w / 2}" y="{label_y + 20}" text-anchor="middle" font-family="Archivo Narrow, Arial Narrow, sans-serif" '
                     f'font-weight="700" font-size="22" letter-spacing="4" fill="var(--ink)">{name}</text></g>')
    cut = (f'<line x1="{10 + w}" y1="{10 + h}" x2="{10 + 3 * w}" y2="{10 + h}" stroke="var(--red)" stroke-width="9" stroke-linecap="round"/>'
           f'<text x="{10 + 2 * w}" y="{h - 6}" text-anchor="middle" font-family="Permanent Marker, Marker Felt, cursive" font-size="34" '
           f'fill="var(--red)">cut here</text>')
    return f'<svg viewBox="0 0 {20 + 4 * w} {20 + 2 * h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Fold one sheet layout">{"".join(cells)}{cut}</svg>'


def preview_doc(cover_html: str, cfg: dict, css_vars: str) -> str:
    body = f"""<div class="preview">
<div class="card">{cover_html}</div>
<h1>One sheet. Eight pages.</h1>
<div class="scrawl">fold it!</div>
<div class="diagram">{sheet_diagram_svg()}</div>
<p class="caption">Print on one A4 sheet. Cut the red line. Fold. Hand it to someone.</p>
</div>"""
    return document(body, f"{cfg['zine_name']} preview", cfg, css_vars)


def default_date() -> str:
    d = date.today()
    return f"{d:%A}, {d:%B} {d.day}, {d.year}"
