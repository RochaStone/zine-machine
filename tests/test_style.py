"""The shared style.json: lookup order, and a second style really changes the cover."""
import json
import tempfile
import unittest
from pathlib import Path

import zine
from zinelib import inputs, pages, style
from zinelib.layout import fit

ROOT = Path(__file__).resolve().parent.parent
SECOND = {
    "name": "Sea Glass", "owner": "Mara Quill", "handle": "@maraquill",
    "palette": {"hero": "#0F7B6C", "paper": "#EEF4F0", "ink": "#1B2A2F"},
    "fonts": {"masthead": "Cormorant Garamond", "body": "Lora"},
    "motif": "front-page",
    "lines": {"masthead": "THE TIDE LINE", "headline": "Slow mornings, bright ideas"},
}


def cover_doc(style_data, words=True):
    cfg, _ = zine.load_config(None, style_data, words)
    style_css, cfg["_font_links"], _ = style.css_and_fonts(style_data)
    posts = [inputs.parse_markdown("# A post\n\nSome words for the cover teaser to use here.")]
    layout, _ = fit(posts)
    base, _ = pages.palette_vars({})
    return pages.document(pages.build_pages(cfg, posts, layout)[1], cfg["zine_name"], cfg, base + style_css)


class StyleTest(unittest.TestCase):
    def setUp(self):
        self.rocha = json.loads(style.BUNDLED.read_text(encoding="utf-8"))

    def test_second_style_changes_masthead_and_colours(self):
        a, b = cover_doc(self.rocha), cover_doc(SECOND)
        self.assertIn("THE ROCHEVERSE TIMES", a)
        self.assertIn("THE TIDE LINE", b)
        self.assertNotIn("THE ROCHEVERSE TIMES", b)
        self.assertIn("--hot:#0F7B6C", b)
        self.assertIn("--cream:#EEF4F0", b)
        self.assertNotIn("#0F7B6C", a)
        self.assertIn("Slow mornings, bright ideas", b)
        self.assertIn("@maraquill", b)
        self.assertIn("family=Cormorant+Garamond", b)
        self.assertIn('--f-mast:"Cormorant Garamond"', b)

    def test_bundled_example_never_puts_rochas_words_on_your_zine(self):
        cfg, _ = zine.load_config(None, self.rocha, style_words=False)
        self.assertNotEqual(cfg.get("handle"), "@rocheverse")
        self.assertNotIn("cover_line", cfg)
        self.assertEqual(cfg["zine_name"], "THE ROCHEVERSE TIMES")  # the house masthead, until you name yours

    def test_zine_config_wins_over_style(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "zine.config.json"
            p.write_text(json.dumps({"zine_name": "My Own Name"}), encoding="utf-8")
            cfg, _ = zine.load_config(p, SECOND)
        self.assertEqual(cfg["zine_name"], "My Own Name")
        self.assertEqual(cfg["handle"], "@maraquill")

    def test_user_style_inherits_only_palette_and_fonts(self):
        user = {"name": "", "owner": "", "handle": "", "palette": {"hero": "#0F7B6C", "ink": ""},
                "fonts": {"body": "Lora"}, "lines": {"masthead": "", "headline": ""}, "references": [], "notes": ""}
        merged = style.inherit(user, self.rocha)
        self.assertEqual(merged["palette"]["hero"], "#0F7B6C")             # hers kept
        self.assertEqual(merged["palette"]["ink"], self.rocha["palette"]["ink"])  # missing colour borrowed
        self.assertEqual(merged["fonts"]["body"], "Lora")
        self.assertEqual(merged["fonts"]["masthead"], self.rocha["fonts"]["masthead"])
        for key in ("name", "owner", "handle", "references", "notes"):
            self.assertEqual(merged[key], user[key], key)
        self.assertEqual(merged["lines"], user["lines"])
        cfg, _ = zine.load_config(None, merged, style_words=True)
        self.assertEqual(cfg["zine_name"], style.NEUTRAL_MASTHEAD)
        self.assertNotIn("cover_line", cfg)
        self.assertEqual(cfg["handle"], "")
        flat = json.dumps(cfg) + json.dumps(merged["lines"])
        for theirs in ("ROCHEVERSE", "FOUNDER WORLD", "@rocheverse", "Rocha"):
            self.assertNotIn(theirs, flat)

    def test_lookup_order(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            self.assertIn(style.find_style(None, d), (style.BUNDLED, Path.home() / ".rocha-coded" / "style.json"))
            (d / "style.json").write_text("{}", encoding="utf-8")
            self.assertEqual(style.find_style(None, d), d / "style.json")
            self.assertEqual(style.find_style(str(d / "style.json")), d / "style.json")
            with self.assertRaises(FileNotFoundError):
                style.find_style(str(d / "nope.json"))

    def test_bad_values_are_ignored(self):
        css, links, warnings = style.css_and_fonts({"palette": {"hero": "red;}</style>"}, "fonts": {"body": "x</style>"}})
        self.assertNotIn("</style>", css)
        self.assertEqual(links, [])
        self.assertEqual(len(warnings), 2)

    def test_blank_example_file_is_harmless(self):
        blank = json.loads((ROOT / "style.example.json").read_text(encoding="utf-8"))
        css, links, warnings = style.css_and_fonts(blank)
        self.assertEqual((css, links, warnings), ("", [], []))


if __name__ == "__main__":
    unittest.main()
