# Zine Machine

**Rocha Coded.** *Free tools from the Rocheverse.*

Paste five posts or voice notes. Get a mini zine you can print on one sheet, fold, and hand to someone.

<p align="center"><img src="docs/img/hero.png" width="760" alt="A newspaper style zine cover next to the one-sheet layout: eight numbered panels and a red cut line"></p>

## What you get
- **A zine on one sheet of paper.** Print it, cut one line, fold it. Eight little pages, in the right order, every time.
- **A cover with attitude.** A newspaper front page ("BREAKING NEWS", dateline, two columns) or a magazine cover with a big serif masthead and a pink scrawl running up the side.
- **Pink lined paper, cream paper, ink and stickers.** Hearts, an evil eye, 777, butterflies. Drawn in, nothing borrowed.
- **The same zine for screens.** An eight page PDF to email or DM, and eight Instagram stories, one per page.
- **Your words, exactly as you wrote them.** It never rewrites a sentence. If there is too much, it asks which whole sentences to keep.

Make one as a lead magnet. A retreat handout. The thing on every chair at your workshop. The thing you leave in a cafe.

<p align="center">
<img src="examples/output/stories/page-01.png" width="150" alt="Story 1: the cover">
<img src="examples/output/stories/page-02.png" width="150" alt="Story 2: a pink lined page">
<img src="examples/output/stories/page-04.png" width="150" alt="Story 4: a list page">
<img src="examples/output/stories/page-08.png" width="150" alt="Story 8: the back cover">
<img src="examples/output/magazine/story-cover.png" width="150" alt="The magazine cover style">
</p>

## Install
It runs on your own computer: a Mac or Linux with Python 3.10+ and Google Chrome (or Chromium, Edge or Brave).
No accounts, no servers, nothing to sign up for. Run `python3 zine.py check` to see that it can make PDFs.

| Where you use it | Install it | Start it |
|---|---|---|
| [Claude Code](#claude-code) (recommended) | clone into `~/.claude/skills` | ask for a zine, or `/zine-machine` |
| [Claude Cowork](#claude-cowork) | upload `zine-machine.zip` as a skill | ask for a zine in a Cowork task |

Tested on macOS with Chrome, both through Playwright and by calling Chrome directly. Linux and the Cowork sandbox
run the same steps but have not been tested yet.

### Claude Code
```sh
git clone https://github.com/RochaStone/zine-machine ~/.claude/skills/zine-machine
python3 ~/.claude/skills/zine-machine/zine.py check
```
Then start Claude Code and say "make a zine from my last five posts". To update later:
`git -C ~/.claude/skills/zine-machine pull`.

### Claude Cowork
Cowork (the Claude desktop app) runs tasks in a Linux sandbox on your computer that can only reach the folders you
give it.
1. Download `zine-machine.zip` from the [latest release](https://github.com/RochaStone/zine-machine/releases/latest).
2. In the Claude desktop app: Customize > Skills, then + > Create skill > Upload a skill, and pick the zip.
3. In Settings > Capabilities, turn on code execution and file creation.
4. Make a folder for your zine, put your posts in it (or have your Substack links ready), start a Cowork task, give
   it access to that folder, and ask: "Use Zine Machine to make a zine from these posts."
5. The sandbox may not have a browser. The skill installs one if it can (`pip install playwright`, then
   `python3 -m playwright install chromium`, a few minutes, once). If it can't, you still get the finished pages as
   HTML in your folder: open `zine-print.html` in Chrome, Print, Save as PDF, Landscape, Margins none, Background
   graphics on.

If the sandbox can't install software or reach the internet on your setup, use Claude Code instead.

## Make a zine
1. Give it your words. Any of these, up to eight posts:
   - markdown or `.txt` files (voice note transcripts are perfect), or a folder of them
   - one markdown file with `---` on its own line between posts
   - links to public Substack posts
   - or just paste them into the chat
2. It asks for the zine's name, the cover style, your name and handle, and anything optional (a cover line, the
   scrawl, a line for the back, your colours).
3. It builds everything into `out/`:

| File | What it is |
|---|---|
| `zine-print.pdf` | one A4 landscape sheet, pages already in fold order |
| `zine-screen.pdf` | the eight pages in reading order, A5, for sending |
| `stories/page-01.png` to `page-08.png` | 1080 x 1920 Instagram stories |
| `preview.png` | your cover next to the folding sheet, for showing it off |
| `html/` | the source pages, to tweak a word and print from any browser |

4. Print, cut, fold. The steps are in [templates/FOLDING.md](templates/FOLDING.md).

<p align="center"><img src="docs/img/print-sheet.png" width="760" alt="The printed sheet: the top row upside down, the bottom row upright, a red cut line in the middle"></p>

Five short posts of 60 to 120 words each is the sweet spot. Short zines get bigger type. Long ones get slightly
smaller type. If it still doesn't fit, it tells you how many words are over and you choose what stays.

### By hand
```sh
python3 zine.py build my-posts/ --config zine.config.json --out out/
python3 zine.py build https://yourname.substack.com/p/a-post https://yourname.substack.com/p/another --config zine.config.json
```
Copy [examples/zine.config.json](examples/zine.config.json) to start your config. `masthead` is `newspaper` or
`magazine`. `palette` takes hex colours for `hot_pink`, `candy_pink`, `pale_pink`, `cream`, `ink`, `marker_red`,
`plum`, `gold`, `pale_blue` and `white`.

`--renderer` picks how pages become PDFs: `auto` (Playwright if it is installed, else Chrome directly), `chrome`,
`playwright`, or `html` for no browser at all. If Chrome lives somewhere unusual, set `ZINE_CHROME` to its path.

## Make it yours
One `style.json` holds your colours, fonts, cover style and the lines you say a lot. Put it in your zine folder, or in `~/.rocha-coded/` to use it everywhere. Your Claude can make it with you from a few references.
Two examples ship with it: [examples/style.rocha-coded.json](examples/style.rocha-coded.json) is Rocha's own look, and [style.example.json](style.example.json) is the blank one to fill in. [STYLE.md](STYLE.md) explains every key.
The same file works across every Rocha Coded tool, so you make your look once.

## What's inside
- `SKILL.md`: the steps your Claude follows.
- `style.example.json` and `STYLE.md`: your look, in one file.
- `zine.py`: the one command. Python standard library only.
- `zinelib/`: reading posts (markdown, text, Substack pages), flowing words onto pages, the fold order, the pages
  themselves, the stickers, and the browser that prints them.
- `templates/zine.css`: the whole look. Fonts come from Google Fonts with system fallbacks.
- `templates/FOLDING.md`: how to cut and fold.
- `examples/`: five posts by a made-up potter, Rocha's style file, and the zine they make in both cover styles.
- `tests/`: the page flow and fold order tests, plus a full build. See [tests/TESTING.md](tests/TESTING.md).

## Licence
MIT. Copyright (c) 2026 Rochelle Livingstone / Thriving Era Studio. See [LICENSE](LICENSE).

## Made by Rocha

Rocha \
Brand Alchemist & AI Architect \
Author of *Brand Alchemy in the Thriving Era* \
Creator of [Conscious Founder OS](https://founders.thrivingera.com) \
Founder, [Thriving Era Studio](https://thrivingera.com)

I take female founders AI native in 7 days, and I build what they need next. \
Start with the audit: [thrivingera.com/audit](https://thrivingera.com/audit). \
Or book an exploratory call: [calendly.com/rochelle-thrivingera/exploratory-call](https://calendly.com/rochelle-thrivingera/exploratory-call). It is where we decide if we work together.

[Instagram @rocheverse](https://instagram.com/rocheverse) · [Substack](https://rochastone.substack.com) · [LinkedIn](https://www.linkedin.com/in/rochellelivingstonecosmic) · [More free tools](https://thrivingera.com/free) · [All tools on GitHub](https://github.com/RochaStone)
