"""Three motif families from one render path: analog, cyberpunk, y2k-blog."""
import re
import unittest

import zine
from zinelib import inputs, pages, style
from zinelib.layout import fit, imposition

POSTS = [inputs.parse_markdown(f"# Post {i}\n\nSome words for post {i}. " * 3 + "\n\n> a quote to pull") for i in range(5)]
SIGNATURES = {
    "analog": ("breaking news", 'class="page cover news"'),
    "cyberpunk": (":~$", "cart-label", "cy-mast"),
    "y2k-blog": ("you are visitor no.", "zine.exe", "sign my guestbook", "currently reading"),
}


def render(motif, masthead="newspaper"):
    cfg, _ = zine.load_config(None, {}, style_words=False)
    cfg.update({"motif": motif, "masthead": masthead, "handle": "@someone"})
    layout, _ = fit(POSTS)
    built = pages.build_pages(cfg, POSTS, layout)
    return cfg, built


class MotifTest(unittest.TestCase):
    def test_each_family_renders_its_signature(self):
        for motif, markers in SIGNATURES.items():
            _, built = render(motif)
            html = "".join(built.values())
            self.assertEqual(sorted(built), list(range(1, 9)), motif)
            for m in markers:
                self.assertIn(m, html, f"{motif} is missing {m}")

    def test_families_do_not_borrow_each_others_signatures(self):
        self.assertNotIn("you are visitor no.", "".join(render("cyberpunk")[1].values()))
        self.assertNotIn(":~$", "".join(render("y2k-blog")[1].values()))
        self.assertNotIn("zine.exe", "".join(render("analog")[1].values()))

    def test_same_words_in_every_family(self):
        texts = []
        for motif in SIGNATURES:
            html = "".join(render(motif)[1][n] for n in range(2, 8))
            texts.append(sorted(set(re.findall(r"Some words for post \d", html))))
        self.assertEqual(texts[0], texts[1])
        self.assertEqual(texts[1], texts[2])

    def test_print_imposition_unchanged_by_motif(self):
        expected = [(s["page"], s["rotate"] == 180) for s in imposition()]
        for motif in SIGNATURES:
            cfg, built = render(motif)
            sheet = pages.print_doc(built, cfg, "")
            found = [(int(p), bool(f)) for f, p in re.findall(r'class="slot( flip)?" data-page="(\d)"', sheet)]
            self.assertEqual(found, expected, motif)

    def test_prompt_comes_from_her_handle(self):
        _, built = render("cyberpunk")
        self.assertIn("someone:~$", built[1])
        self.assertNotIn("rocheverse:~$", built[1])

    def test_style_motif_names_map_to_families(self):
        self.assertEqual(style.family("analog"), "analog")
        self.assertEqual(style.family("cyberpunk"), "cyberpunk")
        self.assertEqual(style.family("y2k-blog"), "y2k-blog")
        self.assertEqual(style.family("retro-tv"), "cyberpunk")
        self.assertEqual(style.family("guest-check"), "analog")
        self.assertEqual(style.family(None), "analog")
        cfg, _ = zine.load_config(None, {"motif": "y2k-blog"})
        self.assertEqual(cfg["motif"], "y2k-blog")

    def test_bundled_example_is_analog(self):
        import json
        self.assertEqual(json.loads(style.BUNDLED.read_text(encoding="utf-8"))["motif"], "analog")

    def test_magazine_cover_only_in_analog(self):
        self.assertIn('class="page cover mag"', render("analog", "magazine")[1][1])
        self.assertNotIn('class="page cover mag"', render("y2k-blog", "magazine")[1][1])


if __name__ == "__main__":
    unittest.main()
