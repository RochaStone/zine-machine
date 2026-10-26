"""Turn HTML into PDF and PNG with a headless browser: Playwright if it works, else Chrome directly."""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

MAC_APPS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
)
LINUX_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser")


class RenderError(RuntimeError):
    pass


def find_chrome() -> str | None:
    env = os.environ.get("ZINE_CHROME")
    if env and Path(env).exists():
        return env
    if platform.system() == "Darwin":
        for app in MAC_APPS:
            for root in ("", str(Path.home())):
                p = root + app
                if Path(p).exists():
                    return p
    for name in LINUX_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


class ChromeRenderer:
    name = "chrome"

    def __init__(self, binary: str):
        self.binary = binary
        self.profile = tempfile.mkdtemp(prefix="zine-chrome-")

    def _run(self, args: list[str], target: Path) -> None:
        cmd = [self.binary, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
               "--no-default-browser-check", f"--user-data-dir={self.profile}", "--run-all-compositor-stages-before-draw",
               "--virtual-time-budget=10000", "--force-device-scale-factor=1"]
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            cmd.append("--no-sandbox")  # Chrome refuses to start as root otherwise (common in containers)
        target.unlink(missing_ok=True)
        try:
            proc = subprocess.run(cmd + args, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired as err:
            raise RenderError(f"Chrome took too long on {target.name}") from err
        if not target.exists() or target.stat().st_size == 0:
            raise RenderError(f"Chrome did not write {target.name}: {proc.stderr.strip()[-400:]}")

    def pdf(self, html_path: Path, pdf_path: Path) -> None:
        self._run(["--no-pdf-header-footer", "--print-to-pdf-no-header", f"--print-to-pdf={pdf_path}",
                   html_path.resolve().as_uri()], pdf_path)

    def png(self, html_path: Path, png_path: Path, width: int, height: int) -> None:
        self._run([f"--window-size={width},{height}", f"--screenshot={png_path}", html_path.resolve().as_uri()], png_path)

    def close(self) -> None:
        shutil.rmtree(self.profile, ignore_errors=True)


class PlaywrightRenderer:
    name = "playwright"

    def __init__(self):
        from playwright.sync_api import Error, sync_playwright  # optional dependency
        self._error = Error
        self._pw = sync_playwright().start()
        try:
            self._browser = self._pw.chromium.launch()
        except Error:
            try:  # no bundled browser downloaded: use the installed Chrome instead
                self._browser = self._pw.chromium.launch(channel="chrome")
            except Error as err:
                self._pw.stop()
                raise RenderError("Playwright is installed but has no browser") from err

    def _open(self, html_path: Path, width: int = 1200, height: int = 900):
        page = self._browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle", timeout=60000)
        page.evaluate("document.fonts.ready.then(() => true)")
        return page

    def pdf(self, html_path: Path, pdf_path: Path) -> None:
        page = self._open(html_path)
        try:
            page.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True)
        finally:
            page.close()

    def png(self, html_path: Path, png_path: Path, width: int, height: int) -> None:
        page = self._open(html_path, width, height)
        try:
            page.screenshot(path=str(png_path), clip={"x": 0, "y": 0, "width": width, "height": height})
        finally:
            page.close()

    def close(self) -> None:
        self._browser.close()
        self._pw.stop()


def get_renderer(choice: str = "auto"):
    """Returns (renderer or None, message). None means: HTML only."""
    if choice == "html":
        return None, "HTML only, as asked"
    if choice in ("auto", "playwright"):
        try:
            r = PlaywrightRenderer()
            return r, "rendering with Playwright"
        except ImportError:
            if choice == "playwright":
                return None, "Playwright is not installed (pip install playwright)"
        except RenderError as err:
            if choice == "playwright":
                return None, str(err)
    if choice in ("auto", "chrome"):
        binary = find_chrome()
        if binary:
            return ChromeRenderer(binary), f"rendering with {Path(binary).name}"
        return None, "no Chrome, Chromium, Edge or Brave found (set ZINE_CHROME to the browser's path)"
    return None, f"unknown renderer '{choice}'"
