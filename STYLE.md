# Your style file

One `style.json` styles every Rocha Coded tool. Make it once, and your zines, receipts and cards all come out in your look.

Zine Machine looks for it in this order and uses the first it finds:
1. `--style path/to/style.json` on the command line
2. `style.json` in the folder you are working in
3. `~/.rocha-coded/style.json` (one file for every tool on this computer)
4. `examples/style.rocha-coded.json`, Rocha's own look, shipped as the example

Start from [style.example.json](style.example.json). A blank colour or font borrows the example's. Your words never do: a blank name, handle or line stays blank, and a zine with no name of its own says YOUR WORDS HERE until you give it one.
Anything you set in `zine.config.json` (zine name, cover line, palette) wins over the style file for that one zine.

| Key | What it is | How Zine Machine uses it |
|---|---|---|
| `name` | what you call your look | not shown |
| `owner` | your name | the byline and the back cover |
| `handle` | your Instagram or other handle | the cover and the back cover |
| `site` | your website | not shown in the zine |
| `palette.hero` | your dark ground | the back cover, story and preview backgrounds |
| `palette.accent` | your one accent | pills and the script on dark grounds |
| `palette.paper` | your main paper colour | covers and cream pages, and type on dark grounds |
| `palette.paper_pink` | your second paper | lined pages and the notes page |
| `palette.ink` | text colour | all text and outlines |
| `palette.marker` | your script and pen colour | the magazine scrawl, pull quotes, "continued" notes, the cut line |
| `palette.plum` | a deep shade | the magazine spine and back cover |
| `palette.wine` | a second deep shade | the kicker and page pills, quote of the day |
| `palette.gold` | a metallic accent | thin hairline rules |
| `palette.cool` | a rare cool accent | not used by the zine |
| `fonts.masthead` | a big editorial serif | mastheads and titles |
| `fonts.label` | a condensed sans | tags and labels |
| `fonts.body` | a readable text face | the posts |
| `fonts.scrawl` | a marker face | the hand-written notes page |
| `fonts.script` | a signature script | the magazine scrawl and the thank-you line |
| `fonts.mono` | a typewriter face | datelines, page numbers, small notes |
| `motif` | your structure: `analog`, `cyberpunk` or `y2k-blog` | which of the three looks the zine is built in. Older names still work (`magazine-scrawl` gives the analog magazine cover, `retro-tv` gives cyberpunk, the rest give analog). `motif` in zine.config.json or `--motif` overrides it |
| `lines.masthead` | the name across the top | the zine name, unless you give one |
| `lines.headline` | your big line | the cover headline, unless you give one |
| `lines.scrawl` | your handwritten line | the magazine scrawl, unless you give one |
| `lines.magazine` | your magazine masthead | the magazine cover name, unless you give one |
| `lines.todo`, `stamp`, `celebrate`, `affirm`, `invite` | more of your lines | used by other tools |
| `references` | images or links that show your taste | your Claude looks at these when making your style file |
| `notes` | your look in a sentence | your Claude reads this |

Colours are hex, like `#50163C`. Fonts are Google Fonts names, like `Fraunces`. If a font is not on Google Fonts, the page falls back to a similar system font.
