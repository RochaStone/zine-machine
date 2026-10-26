"""Read posts from markdown files, plain-text voice notes, or public Substack post URLs."""
from __future__ import annotations

import re
import shutil
import ssl
import subprocess
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from .layout import Block, Post

MAX_POSTS = 8
MAX_FETCH_BYTES = 5 * 1024 * 1024
TEXT_SUFFIXES = {".md", ".markdown", ".txt"}


# ---------------------------------------------------------------- markdown / text

def _strip_frontmatter(text: str) -> tuple[str, dict]:
    meta: dict = {}
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        head = text[4:end] if end != -1 else ""
        lines = [ln for ln in head.splitlines() if ln.strip()]
        if end != -1 and lines and all(re.match(r"^[A-Za-z_][\w-]*\s*:", ln) for ln in lines):
            for ln in lines:
                k, _, v = ln.partition(":")
                meta[k.strip().lower()] = v.strip().strip("\"'")
            text = text[end + 4:].lstrip("\n")
    return text, meta


def parse_markdown(text: str, fallback_title: str = "") -> Post:
    """One post from markdown. The first heading (or first short line) is the title."""
    text, meta = _strip_frontmatter(text.replace("\r\n", "\n"))
    title = meta.get("title", "")
    blocks: list[Block] = []
    para: list[str] = []
    quote: list[str] = []

    def flush():
        if para:
            blocks.append(Block("p", " ".join(para)))
            para.clear()
        if quote:
            blocks.append(Block("quote", " ".join(quote)))
            quote.clear()

    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            flush()
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush()
            if not title:
                title = heading.group(2).strip()
            else:
                blocks.append(Block("p", f"**{heading.group(2).strip()}**"))
            continue
        if line.startswith(">"):
            if para:
                flush()
            quote.append(line.lstrip("> ").strip())
            continue
        item = re.match(r"^([-*+]|\d+[.)])\s+(.*)$", line)
        if item:
            flush()
            blocks.append(Block("li", item.group(2).strip()))
            continue
        if quote:
            flush()
        para.append(line)
    flush()

    if not title:
        first = next((b for b in blocks if b.kind == "p"), None)
        if first and len(first.text.split()) <= 12:
            title = first.text.strip("* ")
            blocks.remove(first)
        else:
            title = fallback_title
    return Post(title=title.strip() or "Untitled", blocks=blocks)


def split_pages(text: str) -> list[str]:
    """Split one markdown file into posts on lines that are exactly '---'."""
    body, _ = _strip_frontmatter(text.replace("\r\n", "\n"))
    parts = re.split(r"(?m)^\s*---\s*$", body)
    return [p.strip() for p in parts if p.strip()]


def _title_from_name(path: Path) -> str:
    name = re.sub(r"^\d+[-_ ]*", "", path.stem)
    return name.replace("-", " ").replace("_", " ").strip().capitalize()


def read_file(path: Path) -> list[Post]:
    text = path.read_text(encoding="utf-8")
    chunks = split_pages(text)
    if len(chunks) > 1:
        return [parse_markdown(c, f"{_title_from_name(path)} {i + 1}") for i, c in enumerate(chunks)]
    post = parse_markdown(text, _title_from_name(path))
    post.source = path.name
    return [post]


# ---------------------------------------------------------------- substack

class _SubstackParser(HTMLParser):
    """Pull the title and the post body out of a public Substack post page."""

    VOID = {"br", "img", "hr", "input", "meta", "link", "source", "wbr", "area", "col", "embed", "track"}
    SKIP_CLASSES = ("subscription-widget", "button-wrapper", "captioned-button", "footnote", "share", "image")
    BLOCK_TAGS = {"p": "p", "li": "li", "h2": "h", "h3": "h", "h4": "h"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.og_title = ""
        self.h1_title = ""
        self.post_title = ""
        self._h1_is_post = False
        self._first_h1_done = False
        self.blocks: list[Block] = []
        self.loose: list[Block] = []
        self._depth = 0
        self._body_depth = None
        self._skip_depth = None
        self._quote_depth = None
        self._in_h1 = False
        self._ignore_depth = None  # script/style/figure
        self._cur: list[str] | None = None
        self._cur_kind = ""
        self._cur_in_body = False
        self._marks: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        if tag == "meta" and a.get("property") == "og:title":
            self.og_title = a.get("content") or ""
        if tag in self.VOID:
            if tag == "br" and self._cur is not None:
                self._cur.append(" ")
            return
        self._depth += 1
        if self._ignore_depth is None and tag in ("script", "style", "figure", "svg", "noscript", "button", "form"):
            self._ignore_depth = self._depth
        if self._skip_depth is None and any(s in cls for s in self.SKIP_CLASSES):
            self._skip_depth = self._depth
        if self._body_depth is None and "body" in cls.split() and "markup" in cls.split():
            self._body_depth = self._depth
        if tag == "h1":
            self._in_h1 = True
            self._h1_is_post = "post-title" in cls
        if tag == "blockquote" and self._quote_depth is None:
            self._quote_depth = self._depth
        if tag in self.BLOCK_TAGS and self._cur is None:
            self._cur = []
            self._cur_kind = self.BLOCK_TAGS[tag]
            self._cur_in_body = self._body_depth is not None
        if tag in ("strong", "b") and self._cur is not None:
            self._cur.append("**")
        if tag in ("em", "i") and self._cur is not None:
            self._cur.append("*")

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if tag in ("strong", "b") and self._cur is not None:
            self._cur.append("**")
        if tag in ("em", "i") and self._cur is not None:
            self._cur.append("*")
        if tag == "h1":
            if not self._h1_is_post and self.h1_title.strip():
                self._first_h1_done = True
            self._in_h1 = False
            self._h1_is_post = False
        if tag in self.BLOCK_TAGS and self._cur is not None:
            text = re.sub(r"\s+", " ", "".join(self._cur)).strip()
            text = re.sub(r"\*\*\s*\*\*|(?<!\*)\*\s+\*(?!\*)", " ", text)  # empty bold/italic marks
            text = re.sub(r"\s+", " ", text).strip()
            if text and self._ignore_depth is None and self._skip_depth is None:
                kind = self._cur_kind
                if self._quote_depth is not None:
                    kind = "quote"
                elif kind == "h":
                    kind, text = "p", f"**{text.strip('*')}**"
                (self.blocks if self._cur_in_body else self.loose).append(Block(kind, text))
            self._cur = None
        if self._ignore_depth == self._depth:
            self._ignore_depth = None
        if self._skip_depth == self._depth:
            self._skip_depth = None
        if self._quote_depth == self._depth:
            self._quote_depth = None
        if self._body_depth == self._depth:
            self._body_depth = None
        self._depth = max(0, self._depth - 1)

    def handle_data(self, data):
        if self._ignore_depth is not None:
            return
        if self._in_h1:
            if self._h1_is_post:
                self.post_title += data
            elif not self._first_h1_done:
                self.h1_title += data
        if self._cur is not None:
            self._cur.append(data)


def parse_substack_html(html: str, url: str = "") -> Post:
    parser = _SubstackParser()
    parser.feed(html)
    parser.close()
    clean = lambda t: re.sub(r"\s+", " ", t).strip()
    title = clean(parser.post_title) or clean(parser.og_title) or clean(parser.h1_title) or "Untitled"
    blocks = parser.blocks or parser.loose
    return Post(title=title, blocks=blocks, source=url)


def _urlopen(url: str, timeout: int, context=None) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (zine-machine; +public post reader)"})
    with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
        data = resp.read(MAX_FETCH_BYTES + 1)
        if len(data) > MAX_FETCH_BYTES:
            raise ValueError(f"page too large to read: {url}")
        charset = resp.headers.get_content_charset() or "utf-8"
    return data.decode(charset, errors="replace")


def _curl(url: str, timeout: int) -> str:
    curl = shutil.which("curl")
    if not curl:
        raise OSError("certificate check failed and curl is not available")
    proc = subprocess.run([curl, "-sSL", "--fail", "--proto", "=http,https", "--max-time", str(timeout),
                           "--max-filesize", str(MAX_FETCH_BYTES), "-A", "Mozilla/5.0 (zine-machine)", url],
                          capture_output=True, timeout=timeout + 5)
    if proc.returncode != 0:
        raise OSError(proc.stderr.decode(errors="replace").strip() or f"curl exited {proc.returncode}")
    return proc.stdout.decode("utf-8", errors="replace")


def fetch_url(url: str, timeout: int = 20) -> str:
    """Read a public page. Certificates are always checked. Some Python installs on macOS ship
    without a certificate bundle, so if the check cannot run we try certifi, then the system curl."""
    if not re.match(r"^https?://", url):
        raise ValueError(f"only http and https links are supported: {url}")
    try:
        return _urlopen(url, timeout)
    except urllib.error.URLError as err:
        if not isinstance(err.reason, ssl.SSLCertVerificationError):
            raise
    try:
        import certifi  # optional
        return _urlopen(url, timeout, ssl.create_default_context(cafile=certifi.where()))
    except ImportError:
        return _curl(url, timeout)


# ---------------------------------------------------------------- collect

def collect(inputs: list[str], fetch=fetch_url) -> tuple[list[Post], list[str]]:
    """Turn the command-line inputs into posts. Returns (posts, warnings)."""
    posts: list[Post] = []
    warnings: list[str] = []
    for raw in inputs:
        if re.match(r"^https?://", raw):
            try:
                post = parse_substack_html(fetch(raw), raw)
            except (OSError, ValueError) as err:
                warnings.append(f"could not read {raw}: {err}")
                continue
            if not post.blocks:
                warnings.append(f"no post text found at {raw} (is it public?)")
                continue
            posts.append(post)
            continue
        path = Path(raw).expanduser()
        if path.is_dir():
            files = sorted(p for p in path.iterdir() if p.suffix.lower() in TEXT_SUFFIXES and not p.name.startswith("."))
            if not files:
                warnings.append(f"no .md or .txt files in {path}")
            for f in files:
                posts.extend(read_file(f))
        elif path.is_file():
            posts.extend(read_file(path))
        else:
            warnings.append(f"not found: {raw}")
    if len(posts) > MAX_POSTS:
        warnings.append(f"{len(posts)} posts given, using the first {MAX_POSTS}")
        posts = posts[:MAX_POSTS]
    return posts, warnings
