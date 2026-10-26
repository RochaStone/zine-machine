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
| `palette.hero` | your loudest colour | kicker, page tags, magazine spine, script scrawl |
| `palette.accent` | a softer partner to the hero | back cover, stickers |
| `palette.paper` | your main paper colour | newspaper cover and cream pages |
| `palette.paper_pink` | your second paper | lined pages and the preview |
| `palette.ink` | text colour | all text and outlines |
| `palette.marker` | your marker pen colour | "continued" notes, cut line, pull quotes |
| `palette.plum` | a deep shade | post titles |
| `palette.gold` | a metallic accent | the 777 and sparkle stickers |
| `palette.cool` | a rare cool accent | the evil eye sticker |
| `fonts.masthead` | a big editorial serif | mastheads and titles |
| `fonts.label` | a condensed sans | tags and labels |
| `fonts.body` | a readable text face | the posts |
| `fonts.scrawl` | a marker or handwriting face | scrawls, pull quotes, notes |
| `fonts.mono` | a typewriter face | not used by the zine |
| `motif` | your signature look | `front-page` makes newspaper covers, `magazine-scrawl` makes magazine covers; anything else keeps the newspaper |
| `lines.masthead` | the name across the top | the zine name, unless you give one |
| `lines.headline` | your big line | the cover headline, unless you give one |
| `lines.scrawl` | your handwritten line | the magazine scrawl, unless you give one |
| `lines.todo`, `stamp`, `celebrate`, `affirm` | more of your lines | used by other tools |
| `references` | images or links that show your taste | your Claude looks at these when making your style file |
| `notes` | your look in a sentence | your Claude reads this |

Colours are hex, like `#FF2D8A`. Fonts are Google Fonts names, like `Playfair Display`. If a font is not on Google Fonts, the page falls back to a similar system font.
