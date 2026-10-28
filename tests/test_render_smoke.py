"""Builds the example zine end to end. Skipped cleanly when this computer has no browser."""
import re
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from zinelib.browser import get_renderer

ROOT = Path(__file__).resolve().parent.parent


def pdf_pages(path: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", path.read_bytes()))


def png_size(path: Path) -> tuple[int, int]:
    head = path.read_bytes()[:24]
    return struct.unpack(">II", head[16:24])


def browser_available() -> bool:
    renderer, _ = get_renderer("auto")
    if renderer:
        renderer.close()
        return True
    return False


@unittest.skipUnless(browser_available(), "no Chrome, Chromium, Edge, Brave or Playwright browser on this computer")
class RenderSmokeTest(unittest.TestCase):
    def test_build_example(self):
        with tempfile.TemporaryDirectory() as out:
            proc = subprocess.run(
                [sys.executable, str(ROOT / "zine.py"), "build", str(ROOT / "examples" / "input"),
                 "--config", str(ROOT / "examples" / "zine.config.json"), "--out", out],
                capture_output=True, text=True, timeout=600)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            out = Path(out)
            self.assertEqual(pdf_pages(out / "zine-screen.pdf"), 8)
            self.assertEqual(pdf_pages(out / "zine-print.pdf"), 1)
            for n in range(1, 9):
                self.assertEqual(png_size(out / "stories" / f"page-{n:02d}.png"), (1080, 1920))
            self.assertEqual(png_size(out / "preview.png"), (1600, 900))

    def test_build_every_motif(self):
        for motif in ("cyberpunk", "y2k-blog"):
            with tempfile.TemporaryDirectory() as out:
                proc = subprocess.run(
                    [sys.executable, str(ROOT / "zine.py"), "build", str(ROOT / "examples" / "input"),
                     "--config", str(ROOT / "examples" / "zine.config.json"), "--out", out, "--motif", motif, "--no-stories"],
                    capture_output=True, text=True, timeout=600)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertEqual(pdf_pages(Path(out) / "zine-screen.pdf"), 8, motif)
                self.assertEqual(pdf_pages(Path(out) / "zine-print.pdf"), 1, motif)


class HtmlOnlyTest(unittest.TestCase):
    def test_html_fallback_needs_no_browser(self):
        with tempfile.TemporaryDirectory() as out:
            proc = subprocess.run(
                [sys.executable, str(ROOT / "zine.py"), "build", str(ROOT / "examples" / "input"),
                 "--config", str(ROOT / "examples" / "zine.config.json"), "--out", out, "--renderer", "html"],
                capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("No PDFs this time", proc.stdout)
            sheet = (Path(out) / "html" / "zine-print.html").read_text(encoding="utf-8")
            self.assertEqual(sheet.count('class="slot'), 8)
            self.assertEqual(sheet.count('class="slot flip"'), 4)


if __name__ == "__main__":
    unittest.main()
