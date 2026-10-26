"""How words flow onto pages 2 to 7."""
import unittest

from zinelib.layout import (CAPACITY, CONTENT_PAGES, MAX_SCALE, MIN_SCALE, MIN_SPLIT, SPLIT_FROM, TITLE_COST,
                            Block, Post, fit, paginate, word_count)


def words(n, sentence=8):
    out = []
    for i in range(n):
        w = f"w{i}"
        out.append(w + "." if (i + 1) % sentence == 0 else w)
    return " ".join(out)


def post(title, *sizes, kind="p"):
    return Post(title, [Block(kind, words(n)) for n in sizes])


def placed_words(layout):
    return sum(word_count(it["text"].replace(" …", "")) for p in layout["pages"] for it in p["items"] if it["kind"] != "title")


class PaginateTest(unittest.TestCase):
    def test_six_content_pages(self):
        res = paginate([post("A", 20)], 100)
        self.assertEqual(len(res["pages"]), len(CONTENT_PAGES))

    def test_short_post_fits_on_one_page(self):
        res = paginate([post("A", 30, 30)], 100)
        self.assertEqual(len(res["pages"][0]["items"]), 3)
        self.assertEqual(res["overflow_words"], 0)
        self.assertFalse(any(p["items"] for p in res["pages"][1:]))

    def test_no_words_lost_or_duplicated(self):
        posts = [post("A", 60, 45, 70), post("B", 40, 90), post("C", 25)]
        res = paginate(posts, 80)
        self.assertEqual(res["overflow_words"], 0)
        self.assertEqual(placed_words(res), 60 + 45 + 70 + 40 + 90 + 25)

    def test_budget_respected(self):
        res = paginate([post("A", 60, 45, 70), post("B", 40, 90)], 80)
        for page in res["pages"]:
            cost = sum(TITLE_COST if it["kind"] == "title" else len(it["text"].split()) for it in page["items"])
            self.assertLessEqual(cost, 80)

    def test_long_paragraph_splits_with_continued_markers(self):
        res = paginate([post("A", 150)], 80)
        first, second = res["pages"][0], res["pages"][1]
        self.assertTrue(first["continues"])
        self.assertTrue(second["continued_from"])
        self.assertTrue(second["items"][0]["cont"])
        self.assertEqual(placed_words(res), 150)

    def test_split_prefers_sentence_end(self):
        res = paginate([post("A", 150)], 80)
        self.assertTrue(res["pages"][0]["items"][-1]["text"].endswith("."))

    def test_split_never_leaves_tiny_scraps(self):
        res = paginate([post("A", 150)], 80)
        for page in res["pages"]:
            for it in page["items"]:
                if it["kind"] == "p":
                    self.assertGreaterEqual(len(it["text"].split()), MIN_SPLIT // 2)

    def test_short_paragraph_moves_whole(self):
        res = paginate([post("A", 60), post("B", SPLIT_FROM - 2)], 80)
        texts = [it for p in res["pages"] for it in p["items"] if it["kind"] == "p"]
        self.assertFalse(any(it["cont"] for it in texts))

    def test_title_never_stranded_at_page_bottom(self):
        res = paginate([post("A", 50), post("B", 30)], 80)
        for page in res["pages"]:
            if page["items"]:
                self.assertNotEqual(page["items"][-1]["kind"], "title")

    def test_new_post_on_next_page_is_not_marked_continued(self):
        res = paginate([post("A", 60), post("B", 60)], 80)
        self.assertEqual(res["pages"][1]["items"][0]["kind"], "title")
        self.assertFalse(res["pages"][1]["continued_from"])
        self.assertFalse(res["pages"][0]["continues"])

    def test_quotes_cost_more(self):
        res = paginate([Post("A", [Block("quote", words(40)), Block("p", words(40))])], 80)
        self.assertEqual(res["pages"][0]["items"][1]["kind"], "quote")
        self.assertTrue(res["pages"][1]["items"])

    def test_overflow_is_counted_and_marked(self):
        res = paginate([post("A", *([60] * 12))], 80)
        self.assertGreater(res["overflow_words"], 0)
        self.assertTrue(res["pages"][-1]["items"][-1]["text"].endswith("…"))
        self.assertEqual(placed_words(res) + res["overflow_words"], 720)

    def test_empty_input(self):
        res = paginate([], 80)
        self.assertEqual(res["overflow_words"], 0)
        self.assertFalse(any(p["items"] for p in res["pages"]))


class FitTest(unittest.TestCase):
    def test_few_words_get_bigger_type(self):
        res, scale = fit([post("A", 40), post("B", 40)])
        self.assertEqual(scale, round(int(CAPACITY * MIN_SCALE) / CAPACITY, 3))
        self.assertLess(scale, 1)
        self.assertEqual(res["overflow_words"], 0)

    def test_five_posts_spread_over_all_pages(self):
        posts = [post(t, 50, 40) for t in "ABCDE"]
        res, scale = fit(posts)
        self.assertEqual(res["overflow_words"], 0)
        self.assertTrue(all(p["items"] for p in res["pages"]), "every content page has words")

    def test_many_words_get_smaller_type(self):
        posts = [post(t, 80, 80) for t in "ABCDE"]
        res, scale = fit(posts)
        self.assertGreater(scale, 1)
        self.assertEqual(res["overflow_words"], 0)

    def test_too_many_words_reports_overflow(self):
        posts = [post(t, 200, 200) for t in "ABCDEFGH"]
        res, scale = fit(posts)
        self.assertEqual(scale, round(int(CAPACITY * MAX_SCALE) / CAPACITY, 3))
        self.assertGreater(res["overflow_words"], 0)


if __name__ == "__main__":
    unittest.main()
