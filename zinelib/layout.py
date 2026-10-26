"""Pure layout logic: how the words flow onto pages, and where each page sits on the sheet.

Nothing in here touches the disk or a browser, so every function is easy to test.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

TOTAL_PAGES = 8           # page 1 cover, pages 2 to 7 content, page 8 back cover
CONTENT_PAGES = (2, 3, 4, 5, 6, 7)
CAPACITY = 140            # words a content page holds at the default type size (scale 1)
TITLE_COST = 12           # a post title takes the room of about twelve words
QUOTE_FACTOR = 1.6        # pull quotes are set bigger, so each word costs more
MIN_SPLIT = 14            # never leave a scrap of fewer words than this when splitting
SPLIT_FROM = 38           # paragraphs shorter than this move to the next page whole
MIN_SCALE = 0.6           # type grows up to 1/sqrt(0.6), about 1.3x, when there are few words
MAX_SCALE = 1.45          # type shrinks down to 1/sqrt(1.45), about 0.83x, when there are many


@dataclass
class Block:
    kind: str   # "p", "quote" or "li"
    text: str


@dataclass
class Post:
    title: str
    blocks: list[Block] = field(default_factory=list)
    source: str = ""


def word_count(text: str) -> int:
    return len(strip_marks(text).split())


def strip_marks(text: str) -> str:
    """Remove the light markdown we support (**bold**, *em*, _em_) for counting."""
    return re.sub(r"(\*\*|\*|__|_)", "", text)


def block_cost(kind: str, words: int) -> float:
    return words * (QUOTE_FACTOR if kind == "quote" else 1.0)


def _split_point(words: list[str], capacity: int) -> int:
    """Where to cut a paragraph that does not fit. Prefer the end of a sentence."""
    capacity = min(capacity, len(words) - MIN_SPLIT // 2)
    for i in range(capacity, MIN_SPLIT - 1, -1):
        if re.search(r"[.!?\"')]$", words[i - 1]):
            return i
    return capacity


def paginate(posts: list[Post], budget: int = CAPACITY, pages: int = len(CONTENT_PAGES)) -> dict:
    """Flow posts onto `pages` content pages with a word budget per page.

    Returns {"pages": [{"items": [...], "continued_from": bool, "continues": bool}, ...],
             "overflow_words": int, "budget": int}
    Each item is {"kind": "title"|"p"|"quote"|"li", "text": str, "post": int, "cont": bool}.
    `cont` is True when the text is the tail of a paragraph split across pages.
    """
    out = [{"items": [], "continued_from": False, "continues": False} for _ in range(pages)]
    page, remaining, overflow = 0, float(budget), 0
    queue: list[dict] = []
    for i, post in enumerate(posts):
        queue.append({"kind": "title", "text": post.title, "post": i, "cont": False})
        for b in post.blocks:
            if b.text.strip():
                queue.append({"kind": b.kind, "text": b.text.strip(), "post": i, "cont": False})

    def next_page() -> bool:
        nonlocal page, remaining
        if page + 1 >= pages:
            return False
        page += 1
        remaining = float(budget)
        return True

    idx = 0
    while idx < len(queue):
        item = queue[idx]
        items = out[page]["items"]
        if item["kind"] == "title":
            # keep a title with its first lines: need room for the title plus the opening
            # block (all of it if that block is too short to split)
            nxt = queue[idx + 1] if idx + 1 < len(queue) else None
            need = TITLE_COST + MIN_SPLIT
            if nxt and nxt["post"] == item["post"] and nxt["kind"] != "title":
                n = len(nxt["text"].split())
                need = TITLE_COST + (block_cost(nxt["kind"], MIN_SPLIT) if n >= SPLIT_FROM else block_cost(nxt["kind"], n))
            if items and remaining < need:
                if not next_page():
                    break
                continue
            items.append(item)
            remaining -= TITLE_COST
            idx += 1
            continue

        words = item["text"].split()
        cost = block_cost(item["kind"], len(words))
        if cost <= remaining:
            items.append(item)
            remaining -= cost
            idx += 1
            continue

        factor = QUOTE_FACTOR if item["kind"] == "quote" else 1.0
        capacity = int(remaining / factor)
        splittable = len(words) >= SPLIT_FROM
        if splittable and capacity >= MIN_SPLIT:
            cut = _split_point(words, capacity)
            items.append({**item, "text": " ".join(words[:cut])})
            queue[idx] = {**item, "text": " ".join(words[cut:]), "cont": True}
            if not next_page():
                idx += 1  # the tail we just queued is the overflow
                overflow += len(words) - cut
                break
            continue

        if not items:  # a single block bigger than a whole page: place it and move on
            items.append(item)
            remaining = 0
            idx += 1
            continue
        if not next_page():
            break

    for rest in queue[idx:]:
        overflow += 0 if rest["kind"] == "title" else len(rest["text"].split())

    if overflow and out[-1]["items"]:
        last = out[-1]["items"][-1]
        if last["kind"] != "title" and not last["text"].endswith("…"):
            last["text"] = last["text"].rstrip(" .") + " …"

    for k in range(pages - 1):
        a, b = out[k]["items"], out[k + 1]["items"]
        if a and b and a[-1]["post"] == b[0]["post"] and b[0]["kind"] != "title":
            out[k]["continues"] = True
            out[k + 1]["continued_from"] = True

    return {"pages": out, "overflow_words": overflow, "budget": budget}


def total_cost(posts: list[Post]) -> float:
    return sum(TITLE_COST + sum(block_cost(b.kind, word_count(b.text)) for b in p.blocks) for p in posts)


def fit(posts: list[Post], capacity: int = CAPACITY, pages: int = len(CONTENT_PAGES)) -> tuple[dict, float]:
    """Choose a word budget per page and a matching type size so the posts fill pages 2 to 7.

    Starts from an even share of the words per page. Few words means bigger type
    (scale < 1), many words means smaller type (scale > 1), within MIN_SCALE..MAX_SCALE.
    The budget grows in small steps until everything fits.
    Returns (layout, scale); font sizes are divided by sqrt(scale).
    If nothing fits at MAX_SCALE, the overflow is trimmed and reported in the layout.
    """
    lo, hi = int(capacity * MIN_SCALE), int(capacity * MAX_SCALE)
    budget = max(lo, min(hi, int(total_cost(posts) / pages * 1.1) + 1))
    while True:
        result = paginate(posts, budget, pages)
        if result["overflow_words"] == 0 or budget >= hi:
            return result, round(budget / capacity, 3)
        budget = min(hi, int(budget * 1.06) + 1)


# ---------------------------------------------------------------- imposition

# The classic one-sheet, eight-page mini zine. Looking at the printed side of a
# landscape sheet: the top row is upside down, the bottom row is upright.
SHEET_TOP = (5, 4, 3, 2)
SHEET_BOTTOM = (6, 7, 8, 1)


def imposition() -> list[dict]:
    """Where each page goes on the sheet, left to right, top row first.

    Each slot is {"row": 0|1, "col": 0..3, "page": 1..8, "rotate": 180|0}.
    """
    slots = []
    for col, page in enumerate(SHEET_TOP):
        slots.append({"row": 0, "col": col, "page": page, "rotate": 180})
    for col, page in enumerate(SHEET_BOTTOM):
        slots.append({"row": 1, "col": col, "page": page, "rotate": 0})
    return slots


def slot_for(page: int) -> dict:
    for slot in imposition():
        if slot["page"] == page:
            return slot
    raise ValueError(f"page must be 1 to {TOTAL_PAGES}, got {page}")
