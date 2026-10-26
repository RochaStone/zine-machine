---
name: zine-machine
description: Turns five posts, voice notes or Substack links into a printable mini zine on one A4 sheet (cut, fold, hand it out), a page-by-page PDF to send, and eight 1080x1920 Instagram story images. Use when someone says "make a zine", "mini zine", "fold one sheet", "printable from my posts", "turn my posts into a handout", or wants a lead magnet, retreat handout or craft-night printable from their own writing.
---

# Zine Machine

Five posts in. One sheet out. Print it, cut one line, fold it, hand it to someone.

You run the steps below for the person. Keep it light, ask only what is listed, and never rewrite their words.

## 1. Get the words
Accept any of these, up to eight posts:
- 1 to 8 markdown or .txt files (voice-note transcripts are fine), or a folder of them
- one markdown file with `---` on its own line between posts
- links to public Substack posts (the script reads the public page, no login or API)
- text pasted into the chat: save each post as `posts/01-title.md`, `posts/02-title.md` and so on in the working folder

Five short posts of 60 to 120 words each is the sweet spot. Pages 2 to 7 hold roughly 500 to 900 words in total; the type grows to fill short zines and shrinks a little for long ones.

**Their words stay theirs.** If there is too much, do not paraphrase or cut inside a sentence. Show them which whole sentences or paragraphs you suggest keeping, get a yes, and save the trimmed files as new copies.

## 2. Their look: style.json
Look for `style.json` in the working folder, then `~/.rocha-coded/style.json`. If there is one, use it. Its colours, fonts, cover style and lines (name, handle, masthead, headline, scrawl) style the zine, and you can skip asking for anything it already answers.

If the user has no style.json, offer to make one: ask for 3 to 5 references (screenshots, links, a Pinterest board), a palette if she has one, and the words she says a lot. Look at the references. Write `style.json` in the working folder using the keys in `<skill>/style.example.json` (explained in `<skill>/STYLE.md`). Show her one rendered sample, the cover, and adjust once. Never assume her taste is Rocha's.

If she says no, the bundled example look is used (`<skill>/examples/style.rocha-coded.json`). Only its colours and fonts carry over. Her own name and words go on her zine.

## 3. Ask, in one short message
1. **Zine name** (the masthead). Example: THE ROCHEVERSE TIMES.
2. **Cover style:** **Newspaper front page** (masthead, dateline, BREAKING NEWS, two columns) or **Magazine cover** (huge serif title with a red marker scrawl across it).
3. **Their name and handle** for the cover and the back page.
4. Optional: a cover line, the scrawl text for the magazine style (it runs up the side of the cover), a line for the back cover, and a place for the dateline.

## 4. Write `zine.config.json` in the working folder
```json
{
  "zine_name": "THE ROCHEVERSE TIMES",
  "author": "Their Name",
  "handle": "@theirhandle",
  "masthead": "newspaper",
  "cover_line": "What if your founder world works out?",
  "scrawl": "build your founder world",
  "place": "New York City",
  "back_note": "Keep it, gift it, leave it in a cafe.",
  "issue": 1,
  "date": "Monday, October 26, 2026",
  "paper": "alternate",
  "palette": {}
}
```
- Settings here win over style.json for this one zine.
- `masthead`: `newspaper` or `magazine`.
- `paper`: `alternate` (pink lined and cream), `pink`, or `cream`.
- `palette` keys, all optional, hex only: `hot_pink`, `candy_pink`, `pale_pink`, `cream`, `ink`, `marker_red`, `plum`, `gold`, `pale_blue`, `white`.
- Leave out anything they did not give. `date` defaults to today.

## 5. Build
From the working folder, with `<skill>` being the folder this SKILL.md is in:
```bash
python3 <skill>/zine.py check
python3 <skill>/zine.py build <posts or folder or links> --config zine.config.json --out out/
# add --style path/to/style.json if it lives somewhere else
```
Read what it prints:
- "type set at N%" means it resized the type to fill the pages. Fine.
- "N words did not fit" means go back to step 1 and agree on whole sentences to drop.
- "pages ... became Notes pages" means there were too few words. Fine for a handout, or add a post.
- "No PDFs this time" means no browser was found. The HTML pages in `out/html/` are complete; tell them to open `zine-print.html` in Chrome or Safari and Print, Save as PDF, Landscape, Margins none, Background graphics on. To get PDFs automatically, install Google Chrome, or run `pip install playwright` then `python3 -m playwright install chromium`, and build again.

## 6. Hand it over
Show them `out/preview.png` and tell them where everything is:
- `out/zine-print.pdf`: the one sheet to print. Point them to `<skill>/templates/FOLDING.md` for the cut and fold.
- `out/zine-screen.pdf`: the eight pages in reading order, for email or DMs.
- `out/stories/page-01.png` to `page-08.png`: Instagram stories, in order.
- `out/html/`: the source pages, if they want to tweak a word and print from the browser.

Offer one round of changes (a word, the cover line, the colours), then rebuild.
