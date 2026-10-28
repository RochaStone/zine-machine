---
name: zine-machine
description: Turns five posts, voice notes or Substack links into a printable mini zine on one A4 sheet (cut, fold, hand it out), a page-by-page PDF to send, and eight 1080x1920 Instagram story images. Use when someone says "make a zine", "mini zine", "fold one sheet", "printable from my posts", "turn my posts into a handout", or wants a lead magnet, retreat handout or craft-night printable from their own writing.
---

# Zine Machine

Five posts in. One sheet out. Print it, cut one line, fold it, hand it to someone.

You guide her through this. She may never have opened a terminal, so be warm, certain and clear.
- **One question at a time.** Wait for her answer before the next one.
- **Reflect it back** in one sentence ("Lovely, the zine is called The Tide Line.").
- **Say what you are about to do** before you do it ("I'm going to save your posts into a folder called posts.").
- **End every step with what she can do next.**
- **If she needs to type something,** give her the exact line in a code block and tell her what she will see when it worked.
- **Her words stay hers.** Never paraphrase and never cut inside a sentence.

`<skill>` below means the folder this SKILL.md is in.

## 1. Check the computer can make PDFs
Say: "First I'm checking this computer can turn the pages into PDFs. It takes a few seconds."
```bash
python3 <skill>/zine.py check
```
When it worked, it prints `Python ...: ok` and `Browser: ok`. Tell her it's ready.
If it says the browser is missing, tell her kindly: "Your zine will still be made, as web pages you can print from Chrome or Safari. If you'd like PDFs made for you, install Google Chrome and I'll check again." Then carry on.

## 2. Her words
Ask: "Which posts or voice notes would you like in your zine? You can paste them here, point me to a folder of files, or send links to public Substack posts. Five is perfect, up to eight."

She can give:
- text pasted into the chat. Say you'll save each post as `posts/01-title.md`, `posts/02-title.md` and so on in the working folder, then do it.
- markdown or `.txt` files (voice note transcripts are perfect), or a folder of them
- one markdown file with `---` on its own line between posts
- links to public Substack posts. The script reads the public page, with no login.

Reflect back what you have: "I have five posts, about 500 words in all. That fills the zine nicely."
Five short posts of 60 to 120 words each is the sweet spot. Pages 2 to 7 hold roughly 500 to 900 words. The type grows a little for short zines and shrinks a little for long ones.
If there is too much, show her which whole sentences or paragraphs you suggest keeping, ask for her yes, and save the trimmed versions as new copies.

## 3. Her look
Look for `style.json` in the working folder, then in `~/.rocha-coded/style.json`. If you find one, say: "I found your style file, so your colours and fonts are ready." Its name, handle and lines also answer some of the questions below, so skip those.

If there is no style.json, ask: "Would you like the zine in your own colours and fonts? I can make a style file with you from a few pictures you love. Or I can use the house look for now."
- If yes, ask one at a time: 3 to 5 references (screenshots, links, a Pinterest board), then her palette if she has one, then the words and phrases she says a lot. Look at the references. Write `style.json` in the working folder with the keys in `<skill>/style.example.json` (explained in `<skill>/STYLE.md`). Build the zine once, show her the cover (`out/preview.png`), and adjust once if she wants. Never assume her taste is Rocha's.
- If no, the house look in `<skill>/examples/style.rocha-coded.json` is used. Only its colours and fonts carry over. Her name and words go on her zine.

## 4. A few details, one at a time
Ask each one, reflect it back, then ask the next. Skip any her style file already answers.
1. "What would you like to call your zine? This goes across the top of the cover." Example: THE ROCHEVERSE TIMES.
2. "Which look feels like you? **Analog** is paper you could hold. **Cyberpunk** is a girly plum terminal, with a cartridge label on the back. **Y2k-blog** is a 2003 blog page, with windows, a hit counter and a guestbook on the back." Skip this if her style file sets `motif`. Save her answer as `motif`: `analog`, `cyberpunk` or `y2k-blog`.
   If she picks analog, also ask: "A **newspaper front page** (big masthead, dateline, breaking news, two columns) or a **magazine cover** (huge serif title, a line in script running up the side)?"
3. "What name and handle should go on the cover and the back page?"
4. "Is there a line you'd love on the cover? If not, I'll use the title of your first post." For the magazine cover, also ask for the script line up the side.
5. "Anything for the back cover, like a line to readers or where to find you?" This one is optional.

## 5. Save the settings
Say: "I'm saving your choices in a small settings file called zine.config.json."
```json
{
  "zine_name": "THE ROCHEVERSE TIMES",
  "author": "Her Name",
  "handle": "@herhandle",
  "masthead": "newspaper",
  "motif": "analog",
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
- Leave out anything she did not give. `date` defaults to today.
- Settings here win over style.json for this one zine.
- `motif`: `analog`, `cyberpunk` or `y2k-blog`. `masthead` (analog only): `newspaper` or `magazine`. `paper`: `alternate` (blush lined and cream), `pink`, or `cream`.
- `palette` keys, all optional, hex only: `hero` (the dark ground), `accent`, `paper`, `paper_pink`, `ink`, `marker`, `plum`, `wine`, `gold`, `cool`.

## 6. Make the zine
Say: "Now I'm making your zine. This takes about a minute."
```bash
python3 <skill>/zine.py build <posts, folder or links> --config zine.config.json --out out/
```
Add `--style path/to/style.json` if her style file lives somewhere else. When it worked, it ends with `Done.` and a list of files.
What else it may say, and what to tell her:
- "type set at N%": the type was resized to fill the pages. Nothing to do.
- "N words did not fit": go back to step 2 together and choose whole sentences to leave out.
- "pages ... became Notes pages": there were fewer words than pages, so those pages became lined notes pages. Lovely for a handout, or add a post.
- "No PDFs this time": no browser was found. The pages are ready in `out/html/`. Tell her: open `zine-print.html` in Chrome or Safari, choose Print, then Save as PDF, Layout Landscape, Margins None, and Background graphics on. If she'd like PDFs made for her, she can install Google Chrome, or you can run `pip install playwright` then `python3 -m playwright install chromium`, and build again.

## 7. Hand it over
Show her `out/preview.png` and say where everything is:
- `out/zine-print.pdf`: the one sheet to print. The cut and fold steps are in `<skill>/templates/FOLDING.md`. Offer to walk her through them.
- `out/zine-screen.pdf`: the eight pages in reading order, for email or DMs.
- `out/stories/page-01.png` to `page-08.png`: Instagram stories, in order.
- `out/html/`: the pages as web pages, if she wants to change a word and print from the browser.

End with what she can do next: "Would you like to change a word, the cover line or the colours? I can rebuild it in a minute. Or print it, and I'll walk you through the fold."
