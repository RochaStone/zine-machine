# Testing

Run everything from the repo folder:
```sh
python3 -m unittest discover -s tests -t . -v
```
Standard library only. No pytest needed.

## What the tests cover
- `test_imposition.py`: the fold order. Every page appears once, the top row is upside down, cover and back share the outside, the reading spreads 2|3, 4|5 and 6|7 sit side by side, the end columns back onto consecutive pages, and the cut runs between the middle columns.
- `test_pagination.py`: words flowing onto pages 2 to 7. No words lost or doubled, budgets respected, long paragraphs split at a sentence end with "continued" markers, short paragraphs move whole, titles never stranded at the bottom of a page, overflow counted and marked, and type grows for short zines and shrinks for long ones.
- `test_inputs.py`: markdown, voice-note text, frontmatter, `---` page breaks, folders, missing files, a saved Substack page (title, body, bold and italics, quotes, lists, line breaks, and skipping nav, scripts, figures and subscribe boxes), fetch failures, non-http links, HTML escaping of post text and config, and hex-only palette values.
- `test_style.py`: the shared style.json. A second style (other masthead, colours, fonts, handle) renders a cover where the masthead text, colour variables and font links all change. Also the lookup order, zine.config.json winning over style.json, the bundled example never putting Rocha's name or lines on someone else's zine, unsafe values ignored, and the blank example file being harmless.
- `test_render_smoke.py`: a full build of the example into a temp folder, checking 8 pages in the screen PDF, 1 page in the print PDF, eight 1080 x 1920 story PNGs and a 1600 x 900 preview. Skipped with a clear reason when no browser is found. The HTML-only build runs everywhere.

## What was run (26 Oct 2026, macOS, Python 3.12.8, Google Chrome 156)
- Full suite: 51 tests, all passing, about 20 to 45 seconds.
- Smoke test with the browser faked as missing: skipped with its reason, the HTML-only test still passed.
- Example built with `--renderer playwright` (Playwright driving the installed Chrome) and with `--renderer chrome` (Chrome's own headless print and screenshot). Both gave:

| Output | Result |
|---|---|
| `zine-screen.pdf` | 8 pages, A5 (420.96 x 594.96 pt) |
| `zine-print.pdf` | 1 page, A4 landscape (841.92 x 594.96 pt) |
| `stories/page-01.png` to `page-08.png` | 1080 x 1920 each |
| `preview.png` | 1600 x 900 |

- Fonts checked with `pdffonts`: with the bundled style, Playfair Display, Newsreader, Archivo Narrow and Permanent Marker are embedded from Google Fonts.
- Every page of both PDFs, the preview and the stories were looked at by eye, in both cover styles (THE ROCHEVERSE TIMES front page and the ROCHEVERSE magazine cover).
- Two live public Substack posts were read with the Substack reader (titles and body text came out clean). Not part of the suite, because tests stay offline.

## Not tested yet
- A real print, cut and fold of `zine-print.pdf` on paper. The fold order is checked by the tests above against the standard one-sheet layout, not by hand.
- Linux, and the Claude Cowork sandbox.
- US Letter paper with "Fit to page".
