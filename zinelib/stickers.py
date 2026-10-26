"""Hand-drawn style stickers as inline SVG. No external images, all colours from the palette vars."""

HEART = """<svg viewBox="0 0 100 92" class="stk stk-heart" aria-hidden="true">
<path d="M50 88 C18 64 4 46 6 26 C8 10 22 2 34 4 C42 5 48 11 50 18 C52 11 58 5 66 4 C78 2 92 10 94 26 C96 46 82 64 50 88 Z"
 fill="var(--hot)" stroke="var(--ink)" stroke-width="4" stroke-linejoin="round"/>
<path d="M22 22 C24 15 30 12 36 13" fill="none" stroke="var(--white)" stroke-width="5" stroke-linecap="round"/>
</svg>"""

EVIL_EYE = """<svg viewBox="0 0 100 100" class="stk stk-eye" aria-hidden="true">
<circle cx="50" cy="50" r="45" fill="var(--plum)" stroke="var(--ink)" stroke-width="4"/>
<circle cx="50" cy="50" r="34" fill="var(--white)"/>
<circle cx="50" cy="50" r="22" fill="var(--blue)"/>
<circle cx="50" cy="50" r="11" fill="var(--ink)"/>
<circle cx="44" cy="44" r="4" fill="var(--white)"/>
</svg>"""

SEVENS = """<svg viewBox="0 0 120 64" class="stk stk-777" aria-hidden="true">
<rect x="3" y="3" width="114" height="58" rx="14" fill="var(--gold)" stroke="var(--ink)" stroke-width="4"/>
<text x="60" y="47" text-anchor="middle" font-family="'Archivo Narrow','Arial Narrow',Arial,sans-serif"
 font-weight="700" font-size="44" fill="var(--ink)" letter-spacing="2">777</text>
</svg>"""

BUTTERFLY = """<svg viewBox="0 0 120 100" class="stk stk-fly" aria-hidden="true">
<g stroke="var(--ink)" stroke-width="4" stroke-linejoin="round">
<path d="M58 48 C40 10 10 4 6 22 C2 40 26 50 58 50 Z" fill="var(--candy)"/>
<path d="M62 48 C80 10 110 4 114 22 C118 40 94 50 62 50 Z" fill="var(--candy)"/>
<path d="M58 54 C34 56 16 74 26 88 C36 98 52 80 58 58 Z" fill="var(--hot)"/>
<path d="M62 54 C86 56 104 74 94 88 C84 98 68 80 62 58 Z" fill="var(--hot)"/>
<rect x="55" y="34" width="10" height="46" rx="5" fill="var(--ink)"/>
<path d="M58 36 C54 26 50 20 44 16 M62 36 C66 26 70 20 76 16" fill="none" stroke-linecap="round"/>
</g>
<circle cx="24" cy="24" r="5" fill="var(--white)"/><circle cx="96" cy="24" r="5" fill="var(--white)"/>
</svg>"""

LUCKY = """<svg viewBox="0 0 140 140" class="stk stk-lucky" aria-hidden="true">
<defs><path id="lucky-arc" d="M70 70 m-46 0 a46 46 0 1 1 92 0 a46 46 0 1 1 -92 0"/></defs>
<circle cx="70" cy="70" r="64" fill="var(--candy)" stroke="var(--ink)" stroke-width="4"/>
<circle cx="70" cy="70" r="30" fill="var(--hot)" stroke="var(--ink)" stroke-width="3"/>
<text font-family="'Archivo Narrow','Arial Narrow',Arial,sans-serif" font-weight="700" font-size="17"
 letter-spacing="3" fill="var(--ink)"><textPath href="#lucky-arc">I AM SO LUCKY · I AM SO LUCKY ·</textPath></text>
<path d="M70 52 l5 12 13 1 -10 8 4 13 -12 -7 -12 7 4 -13 -10 -8 13 -1z" fill="var(--white)"/>
</svg>"""

SPARKLE = """<svg viewBox="0 0 60 60" class="stk stk-sparkle" aria-hidden="true">
<path d="M30 2 C33 22 38 27 58 30 C38 33 33 38 30 58 C27 38 22 33 2 30 C22 27 27 22 30 2 Z"
 fill="var(--gold)" stroke="var(--ink)" stroke-width="3" stroke-linejoin="round"/>
</svg>"""

ALL = {"heart": HEART, "eye": EVIL_EYE, "777": SEVENS, "butterfly": BUTTERFLY, "lucky": LUCKY, "sparkle": SPARKLE}

# One sticker per content page, picked by page number so the zine looks the same every build.
PAGE_ORDER = ("heart", "eye", "butterfly", "777", "sparkle", "lucky")


def for_page(page: int) -> str:
    return ALL[PAGE_ORDER[(page - 2) % len(PAGE_ORDER)]]
