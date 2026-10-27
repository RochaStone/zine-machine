"""Reading posts: markdown, plain voice-note text, page breaks, and Substack pages."""
import tempfile
import unittest
from pathlib import Path

from zinelib import inputs
from zinelib.pages import build_pages, esc, palette_vars
from zinelib.layout import fit

FIXTURES = Path(__file__).parent / "fixtures"


class MarkdownTest(unittest.TestCase):
    def test_heading_becomes_title(self):
        post = inputs.parse_markdown("# Hello\n\nFirst para\nstill first.\n\nSecond.")
        self.assertEqual(post.title, "Hello")
        self.assertEqual([b.text for b in post.blocks], ["First para still first.", "Second."])

    def test_quotes_and_lists(self):
        post = inputs.parse_markdown("# T\n\n> a quote\n> goes on\n\n- one\n- two\n\nend")
        self.assertEqual([(b.kind, b.text) for b in post.blocks],
                         [("quote", "a quote goes on"), ("li", "one"), ("li", "two"), ("p", "end")])

    def test_voice_note_without_heading_uses_short_first_line(self):
        post = inputs.parse_markdown("Morning thoughts\n\nI woke up and the kiln was still warm.")
        self.assertEqual(post.title, "Morning thoughts")
        self.assertEqual(len(post.blocks), 1)

    def test_long_first_line_falls_back_to_filename_title(self):
        text = "I woke up and the kiln was still warm and I sat with my coffee for an hour before work."
        post = inputs.parse_markdown(text, "Voice note 3")
        self.assertEqual(post.title, "Voice note 3")

    def test_frontmatter_title(self):
        post = inputs.parse_markdown("---\ntitle: From meta\ndate: 2026-10-01\n---\nBody here that is long enough to stay a paragraph for sure yes.")
        self.assertEqual(post.title, "From meta")

    def test_page_breaks_split_one_file_into_posts(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "all.md"
            f.write_text("# One\n\nA.\n\n---\n\n# Two\n\nB.\n\n---\n\n# Three\n\nC.\n", encoding="utf-8")
            posts = inputs.read_file(f)
        self.assertEqual([p.title for p in posts], ["One", "Two", "Three"])

    def test_collect_folder_sorted_and_capped(self):
        with tempfile.TemporaryDirectory() as d:
            for i in range(10):
                (Path(d) / f"{i:02d}-post.md").write_text(f"# Post {i}\n\nText {i}.", encoding="utf-8")
            (Path(d) / "notes.json").write_text("{}", encoding="utf-8")
            posts, warnings = inputs.collect([d])
        self.assertEqual(len(posts), inputs.MAX_POSTS)
        self.assertEqual(posts[0].title, "Post 0")
        self.assertTrue(any("first 8" in w for w in warnings))

    def test_missing_file_warns(self):
        posts, warnings = inputs.collect(["/nope/does-not-exist.md"])
        self.assertEqual(posts, [])
        self.assertTrue(warnings)


class SubstackTest(unittest.TestCase):
    def setUp(self):
        self.html = (FIXTURES / "substack-post.html").read_text(encoding="utf-8")

    def test_title_and_body(self):
        post = inputs.parse_substack_html(self.html, "https://example.substack.com/p/notes")
        self.assertEqual(post.title, "Notes from the wheel")
        kinds = [(b.kind, b.text) for b in post.blocks]
        self.assertEqual(kinds, [
            ("p", "This week I made **forty** cups and *loved* six of them."),
            ("p", "**The rule**"),
            ("p", "Keep the wonky ones. They have the best stories."),
            ("quote", "Done is a glaze colour."),
            ("li", "Clay"),
            ("li", "Water & patience"),
            ("p", "See you next Sunday."),
        ])

    def test_skips_nav_footer_widgets_scripts(self):
        text = " ".join(b.text for b in inputs.parse_substack_html(self.html).blocks)
        for junk in ("Subscribe", "Type your email", "footer", "ignore me", "a cup"):
            self.assertNotIn(junk, text)

    def test_collect_uses_fetcher_for_links(self):
        posts, warnings = inputs.collect(["https://example.substack.com/p/notes"], fetch=lambda url: self.html)
        self.assertEqual(len(posts), 1)
        self.assertEqual(warnings, [])

    def test_fetch_failure_is_a_warning(self):
        def boom(url):
            raise OSError("offline")
        posts, warnings = inputs.collect(["https://example.substack.com/p/x"], fetch=boom)
        self.assertEqual(posts, [])
        self.assertIn("offline", warnings[0])

    def test_rejects_non_http(self):
        with self.assertRaises(ValueError):
            inputs.fetch_url("file:///etc/passwd")


class SafetyTest(unittest.TestCase):
    def test_post_text_is_escaped(self):
        self.assertNotIn("<script>", esc("<script>alert(1)</script> **bold**"))
        self.assertIn("<strong>bold</strong>", esc("**bold**"))

    def test_pages_escape_titles_and_config(self):
        posts = [inputs.parse_markdown('# <img src=x onerror=alert(1)>\n\nHello <b>there</b>.')]
        layout, _ = fit(posts)
        cfg = {"zine_name": "<i>Zine</i>", "date": "today", "handle": "@<x>", "author": "A"}
        html = "".join(build_pages(cfg, posts, layout).values())
        self.assertNotIn("<img src=x", html)
        self.assertNotIn("<b>there", html)
        self.assertNotIn("<i>Zine", html)

    def test_palette_only_accepts_hex(self):
        css, warnings = palette_vars({"hot_pink": "#00FF00", "ink": "red;}</style><script>", "lilac": "#C8A2C8"})
        self.assertIn("--ground:#00FF00", css)
        self.assertNotIn("<script>", css)
        self.assertEqual(len(warnings), 2)


if __name__ == "__main__":
    unittest.main()
