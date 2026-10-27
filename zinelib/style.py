"""The shared Rocha Coded style file: one style.json styles every tool.

Lookup order: --style path, ./style.json, ~/.rocha-coded/style.json, then the bundled
examples/style.rocha-coded.json (Rocha's own look, shipped as the example).
"""
from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLED = ROOT / "examples" / "style.rocha-coded.json"
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")

# style.json palette key -> the zine's CSS colour name. "hero" is the GROUND colour (plum), not an accent.
PALETTE_MAP = {
    "hero": "ground", "accent": "accent", "paper": "cream", "paper_pink": "blush", "ink": "ink",
    "marker": "marker", "plum": "plum", "wine": "wine", "gold": "gold", "cool": "cool",
}
# style.json font key -> CSS font variables it drives, with system fallbacks kept behind it
FONT_MAP = {
    "masthead": (("--f-display", 'Georgia, "Times New Roman", serif'),),
    "label": (("--f-label", '"Helvetica Neue", Arial, sans-serif'),),
    "body": (("--f-body", 'Georgia, "Times New Roman", serif'),),
    "scrawl": (("--f-marker", '"Marker Felt", cursive'),),
    "script": (("--f-script", '"Snell Roundhand", "Apple Chancery", cursive'),),
    "mono": (("--f-mono", 'Menlo, Consolas, monospace'),),
}
FONT_NAME = re.compile(r"^[A-Za-z0-9 ]{2,40}$")


def find_style(explicit: str | None = None, cwd: Path | None = None) -> Path:
    if explicit:
        p = Path(explicit).expanduser()
        if not p.is_file():
            raise FileNotFoundError(f"style file not found: {p}")
        return p
    for p in ((cwd or Path.cwd()) / "style.json", Path.home() / ".rocha-coded" / "style.json"):
        if p.is_file():
            return p
    return BUNDLED


def load_style(path: Path) -> tuple[dict, list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        return {}, [f"style file {path.name} is not valid JSON ({err}), using no style"]
    return (data if isinstance(data, dict) else {}), []


NEUTRAL_MASTHEAD = "YOUR WORDS HERE"


def inherit(user: dict, example: dict) -> dict:
    """A user's style borrows only missing palette colours and fonts from the example.
    Lines, owner, handle, name, references and notes never fall back to Rocha's."""
    merged = {k: v for k, v in user.items() if k not in ("palette", "fonts")}
    for key in ("palette", "fonts"):
        mine = {k: v for k, v in (user.get(key) or {}).items() if v}
        merged[key] = {**(example.get(key) or {}), **mine}
    return merged


def apply_style(cfg: dict, style: dict, words: bool = True) -> dict:
    """Fill zine settings from the style. Anything set in zine.config.json wins.

    words=False (the bundled example) keeps the look but never puts Rocha's name,
    handle or lines on someone else's zine.
    """
    lines = style.get("lines") or {}
    # magazine-scrawl makes the magazine cover; every other motif (or none) the newspaper
    cfg.setdefault("masthead", "magazine" if style.get("motif") == "magazine-scrawl" else "newspaper")
    if not words:
        return cfg
    if cfg["masthead"] == "magazine" and lines.get("magazine"):
        cfg.setdefault("zine_name", lines["magazine"])
    for key, value in (("zine_name", lines.get("masthead")), ("cover_line", lines.get("headline")),
                       ("scrawl", lines.get("scrawl")), ("author", style.get("owner")), ("handle", style.get("handle"))):
        if value:
            cfg.setdefault(key, value)
    return cfg


def css_and_fonts(style: dict) -> tuple[str, list[str], list[str]]:
    """CSS variables for the style's colours and fonts, Google Fonts links, and warnings."""
    warnings, decls, families = [], [], []
    for key, value in (style.get("palette") or {}).items():
        name = PALETTE_MAP.get(key)
        if not name or not value:
            continue
        if isinstance(value, str) and HEX.match(value):
            decls.append(f"--{name}:{value};")
        else:
            warnings.append(f"style palette '{key}' must look like #50163C, ignored")
    for key, value in (style.get("fonts") or {}).items():
        if key not in FONT_MAP or not value:
            continue
        if not isinstance(value, str) or not FONT_NAME.match(value):
            warnings.append(f"style font '{key}' is not a plain font name, ignored")
            continue
        families.append(value)
        for var, fallback in FONT_MAP[key]:
            decls.append(f'{var}:"{value}", {fallback};')
    links = []
    for fam in dict.fromkeys(families):
        q = urllib.parse.quote_plus(fam)
        # plain family always loads if Google has it; the weighted request adds bold/italic where they exist
        links.append(f"https://fonts.googleapis.com/css2?family={q}&display=swap")
        links.append(f"https://fonts.googleapis.com/css2?family={q}:ital,wght@0,400;0,700;1,400&display=swap")
    css = (":root{" + "".join(decls) + "}") if decls else ""
    return css, links, warnings
