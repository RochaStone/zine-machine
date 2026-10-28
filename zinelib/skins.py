"""The cyberpunk and y2k-blog motif families. Same content as analog (pages.page_content), new structure."""
from __future__ import annotations

import html
import re

from .layout import CONTENT_PAGES, TOTAL_PAGES
from .pages import _fit_size, contents, page_content, page_titles, plain

HIT_COUNTER = "000,777"

HEART = ("..XX.XX..", ".XXXXXXX.", ".XXXXXXX.", "..XXXXX..", "...XXX...", "....X....")
STAR = ("....X....", "...XXX...", "XXXXXXXXX", ".XXXXXXX.", "..XX.XX..", ".X.....X.")


def pixel_svg(pattern: tuple[str, ...], cls: str, colour: str = "var(--gold)") -> str:
    """A tiny pixel-art icon as inline SVG, one rect per lit pixel."""
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1"/>'
                    for y, row in enumerate(pattern) for x, c in enumerate(row) if c == "X")
    w, h = len(pattern[0]), len(pattern)
    return (f'<svg class="px-icon {cls}" viewBox="0 0 {w} {h}" shape-rendering="crispEdges" aria-hidden="true">'
            f'<g fill="{colour}">{rects}</g></svg>')


def prompt(cfg: dict) -> str:
    """The terminal prompt, built from her handle or zine name: e.g. rocheverse:~$"""
    who = (cfg.get("handle") or cfg.get("zine_name") or "zine").lstrip("@").lower()
    who = re.sub(r"[^a-z0-9._-]+", "", who)[:22] or "zine"
    return f"{html.escape(who)}:~$"


def blocks(filled: int, total: int = 12) -> str:
    return '<span class="blk">' + "█" * filled + '</span><span class="blk off">' + "░" * (total - filled) + "</span>"


# ---------------------------------------------------------------- cyberpunk: the girly terminal

def cyber_cover(cfg, posts, layout) -> str:
    name, p = cfg["zine_name"], prompt(cfg)
    headline = cfg.get("cover_line") or (posts[0].title if posts else name)
    toc = "".join(f'<li><b>{n:02d}</b> {plain(t)}</li>' for n, t in contents(posts, layout)[:6])
    mast = _fit_size(name, ((8, "42pt"), (12, "34pt"), (22, "28pt"), (30, "22pt"), (999, "18pt")))
    return f"""<section class="page cover cyber" style="--mast-size:{mast}">
<div class="cy-bar"><span class="px">issue {html.escape(str(cfg.get('issue', 1)).zfill(2))}</span><span class="leds"><i></i><i class="g"></i></span></div>
<p class="cy-prompt">{p} ./zine --open</p>
<h1 class="cy-mast px">{plain(name)}</h1>
<p class="cy-date">{html.escape(cfg['date'])}</p>
<p class="cy-load">loading {blocks(10)} 83%</p>
<h2 class="cy-head">{plain(headline)}</h2>
<p class="cy-prompt">{p} ls ./pages</p>
<ul class="cy-toc">{toc}</ul>
<p class="cy-prompt">{p} <span class="cursor"></span></p>
<p class="cy-by">{html.escape(' · '.join(x for x in (cfg.get('author'), cfg.get('handle')) if x))}</p>
</section>"""


def cyber_inner(n, page, cfg) -> str:
    p = prompt(cfg)
    head = (f'<div class="cy-bar"><span class="px">{plain(cfg["zine_name"])}</span>'
            f'<span class="px">p.{n:02d}</span></div><p class="cy-prompt">{p} cat page-{n:02d}.txt</p>')
    body = page_content(n, page) if page["items"] else (
        '<p class="cy-notes px">notes</p><div class="cy-lines"><i></i><i></i><i></i><i></i><i></i><i></i></div>')
    return (f'<section class="page inner cyber">{head}{body}'
            f'<div class="cy-progress">{blocks(round(12 * n / TOTAL_PAGES))} {n}/{TOTAL_PAGES}</div></section>')


def cyber_back(cfg, posts) -> str:
    note = cfg.get("back_note") or "thank you for reading"
    return f"""<section class="page back cyber">
<div class="cart">
  <i class="screw a"></i><i class="screw b"></i><i class="screw c"></i><i class="screw d"></i>
  <div class="cart-label">
    <p class="px cart-name">{plain(cfg['zine_name'])}</p>
    <p class="cart-note">{plain(note)}</p>
    <p class="cart-handle">{html.escape(cfg.get('handle', ''))}</p>
  </div>
  <div class="cart-grip"><i></i><i></i><i></i><i></i><i></i></div>
</div>
<p class="cy-prompt center">{prompt(cfg)} exit <span class="cursor"></span></p>
<p class="made px">made with zine machine</p>
</section>"""


# ---------------------------------------------------------------- y2k-blog: the 2003 blog page

def window(title: str, inner: str, cls: str = "") -> str:
    return (f'<div class="win {cls}"><div class="win-bar"><span class="btns"><i></i><i></i><i></i></span>'
            f'<span class="px win-title">{title}</span></div><div class="win-body">{inner}</div></div>')


def y2k_cover(cfg, posts, layout) -> str:
    name = cfg["zine_name"]
    headline = cfg.get("cover_line") or (posts[0].title if posts else "")
    toc = "".join(f'<li>{pixel_svg(HEART, "bullet")}<span>{plain(t)}</span><b>p.{n}</b></li>'
                  for n, t in contents(posts, layout)[:6])
    mast = _fit_size(name, ((10, "46pt"), (16, "38pt"), (22, "33pt"), (999, "26pt")))
    marquee = " ✧ ".join(x for x in (html.escape(cfg.get("handle", "")), plain(name), "pass it on") if x)
    inner = f"""<h1 class="y-mast" style="--mast-size:{mast}">{plain(name)}</h1>
<p class="y-head">{plain(headline)}</p>
<p class="marquee">✧ {marquee} ✧</p>
<ul class="y-toc">{toc}</ul>
<div class="y-meta"><span class="counter">you are visitor no. <b>{HIT_COUNTER}</b></span><span>mood: ✧</span>
<span>last updated {html.escape(cfg['date'])}</span></div>"""
    return (f'<section class="page cover y2k">{window("zine.exe", inner, "cover-win")}'
            f'{pixel_svg(HEART, "deco h1")}{pixel_svg(STAR, "deco s1")}{pixel_svg(HEART, "deco h2")}</section>')


def y2k_inner(n, page, cfg) -> str:
    titles = page_titles(page)
    reading = titles[0] if titles else "page " + str(n)
    side = f"""<aside class="y-side">
<p class="px side-h">about me</p><p>{html.escape(cfg.get('author') or cfg.get('handle') or '')}</p>
<p class="px side-h">currently reading</p><p>{plain(reading)}</p>
<p class="px side-h">mood</p><p>✧</p>
{pixel_svg(HEART, "side-heart")}
</aside>"""
    body = page_content(n, page) if page["items"] else (
        '<p class="y-notes">notes</p><div class="y-lines"><i></i><i></i><i></i><i></i><i></i><i></i></div>')
    return (f'<section class="page inner y2k"><div class="win-frame"></div>'
            f'<div class="win-bar fixed"><span class="btns"><i></i><i></i><i></i></span>'
            f'<span class="px win-title">page-{n:02d}.html</span></div>{side}'
            f'<div class="y-main">{body}</div><div class="folio">{n}</div></section>')


def y2k_back(cfg, posts) -> str:
    note = cfg.get("back_note") or next((b.text for p in posts for b in p.blocks if b.kind == "quote"), "")
    entry = f'<div class="entry"><p class="gb-who">{html.escape(cfg.get("handle", ""))}</p><p>{plain(note)}</p></div>' if note else ""
    inner = f"""<p class="px gb-h">sign my guestbook</p>
{entry}
<div class="entry blank"><p class="gb-who">your name</p><p class="line"></p><p class="line"></p></div>
<div class="entry blank"><p class="gb-who">your name</p><p class="line"></p><p class="line"></p></div>
<p class="counter">you are visitor no. <b>{HIT_COUNTER}</b></p>"""
    return (f'<section class="page back y2k">{window("guestbook.html", inner, "gb-win")}'
            f'{pixel_svg(STAR, "deco s2")}{pixel_svg(HEART, "deco h3")}'
            f'<p class="made px">made with zine machine</p></section>')


FAMILIES = {
    "cyberpunk": (cyber_cover, cyber_inner, cyber_back),
    "y2k-blog": (y2k_cover, y2k_inner, y2k_back),
}


def build(motif: str, cfg: dict, posts, layout: dict) -> dict[int, str]:
    cover, inner, back = FAMILIES[motif]
    pages = {1: cover(cfg, posts, layout), TOTAL_PAGES: back(cfg, posts)}
    for n, page in zip(CONTENT_PAGES, layout["pages"]):
        pages[n] = inner(n, page, cfg)
    return pages
