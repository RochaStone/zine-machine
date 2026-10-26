"""The page mapping for the fold-one-sheet zine. If this is wrong, the printed zine reads out of order."""
import unittest

from zinelib.layout import TOTAL_PAGES, imposition, slot_for


def at(row, col):
    return next(s["page"] for s in imposition() if s["row"] == row and s["col"] == col)


class ImpositionTest(unittest.TestCase):
    def test_every_page_exactly_once(self):
        pages = sorted(s["page"] for s in imposition())
        self.assertEqual(pages, list(range(1, TOTAL_PAGES + 1)))

    def test_grid_is_four_by_two(self):
        cells = {(s["row"], s["col"]) for s in imposition()}
        self.assertEqual(cells, {(r, c) for r in (0, 1) for c in range(4)})

    def test_standard_layout(self):
        top = [at(0, c) for c in range(4)]
        bottom = [at(1, c) for c in range(4)]
        self.assertEqual(top, [5, 4, 3, 2])
        self.assertEqual(bottom, [6, 7, 8, 1])

    def test_top_row_upside_down_bottom_row_upright(self):
        for s in imposition():
            self.assertEqual(s["rotate"], 180 if s["row"] == 0 else 0)

    def test_cover_and_back_share_the_outside_spread(self):
        self.assertEqual(slot_for(1)["row"], slot_for(8)["row"])
        self.assertEqual(abs(slot_for(1)["col"] - slot_for(8)["col"]), 1)

    def test_reading_spreads_sit_side_by_side(self):
        # 2|3, 4|5 and 6|7 face each other when the zine is open, so they share a fold
        for left, right in ((2, 3), (4, 5), (6, 7)):
            a, b = slot_for(left), slot_for(right)
            self.assertEqual(a["row"], b["row"], (left, right))
            self.assertEqual(abs(a["col"] - b["col"]), 1, (left, right))

    def test_outer_leaves_back_onto_each_other(self):
        # the two end columns fold double: each is one leaf, front and back are consecutive pages
        for col in (0, 3):
            pair = sorted((at(0, col), at(1, col)))
            self.assertEqual(pair[1] - pair[0], 1)
            self.assertEqual(pair[0] % 2, 1, "a right-hand page backs onto the next left-hand page")

    def test_cut_line_runs_between_the_middle_columns(self):
        # the slit is cut between rows across columns 1 and 2: pages 4/7 and 3/8
        self.assertEqual({at(0, 1), at(1, 1)}, {4, 7})
        self.assertEqual({at(0, 2), at(1, 2)}, {3, 8})

    def test_slot_for_rejects_bad_pages(self):
        with self.assertRaises(ValueError):
            slot_for(9)

    def test_pure(self):
        self.assertEqual(imposition(), imposition())


if __name__ == "__main__":
    unittest.main()
