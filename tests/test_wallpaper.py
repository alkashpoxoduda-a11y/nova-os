"""
Unit tests for NOVA OS Wallpaper Manager
"""

import unittest
import tempfile
from pathlib import Path
from nova_os.wallpaper import WallpaperManager

class TestWallpaperManager(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.wm = WallpaperManager(is_live_session=True)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_custom_wallpaper_selection(self):
        img = Path(self.tmp_dir.name) / "my_photo.jpg"
        img.write_bytes(b"fake image bytes")

        res = self.wm.select_custom_wallpaper(str(img), theme="dark", mode="fill")
        self.assertTrue(res["success"])
        self.assertIn("Live-сессии", res["message"])

    def test_missing_wallpaper_fallback(self):
        res = self.wm.select_custom_wallpaper("/nonexistent/path.png")
        self.assertFalse(res["success"])
        self.assertIn("не найден", res["message"])

    def test_reset(self):
        res = self.wm.reset_to_default()
        self.assertTrue(res["success"])

if __name__ == "__main__":
    unittest.main()
