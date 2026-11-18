"""A restage must retain the requested Scythe-only decoration change."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fr_melee214_hooks import apply


class Melee214HookTests(unittest.TestCase):
    def test_scythe_arrow_removal_preserves_mode_icon_and_input(self):
        with TemporaryDirectory() as temporary:
            project = Path(temporary)
            path = project / "scripts/scrNTTEFullScythe/scrNTTEFullScythe.gml"
            path.parent.mkdir(parents=True)
            before = (
                "function scrNTTEFullScytheControlPress(_player,_touch,_pressed) {\n"
                "    _player.ntte_scythe_touch_frame=current_frame;\n}\n"
                "function scrNTTEFullScytheControlDraw(_player,_scale,_simplified) {\n"
                "    draw_sprite_ext(_sprite,0,x,y,_scale,_scale,0,c_white,_alpha);\n"
                "    draw_sprite_ext(sprLoadoutArrow,0,x+12*_scale,y-12*_scale,"
                "0.65*_scale,0.65*_scale,90,c_white,_alpha);\n"
                "    draw_set_color(c_white);draw_set_alpha(1);\n}\n"
                "function unrelated_arrow() {draw_sprite(sprLoadoutArrow,0,0,0);}\n")
            path.write_text(before, encoding="utf8")
            apply(project)
            first = path.read_bytes()
            apply(project)
            self.assertEqual(first, path.read_bytes())
            after = first.decode("utf8")
            self.assertIn("_player.ntte_scythe_touch_frame=current_frame;", after)
            self.assertIn("draw_sprite_ext(_sprite,0,x,y,_scale,_scale,0,c_white,_alpha);", after)
            self.assertIn("function unrelated_arrow() {draw_sprite(sprLoadoutArrow,0,0,0);}", after)
            self.assertNotIn("x+12*_scale,y-12*_scale", after)
            self.assertEqual(after.count("FRONTIER214"), 1)

    def test_missing_anchor_fails_instead_of_changing_another_arrow(self):
        with TemporaryDirectory() as temporary:
            project = Path(temporary)
            path = project / "scripts/scrNTTEFullScythe/scrNTTEFullScythe.gml"
            path.parent.mkdir(parents=True)
            before = "function other() {draw_sprite(sprLoadoutArrow,0,0,0);}\n"
            path.write_text(before, encoding="utf8")
            with self.assertRaises(AssertionError):
                apply(project)
            self.assertEqual(path.read_text("utf8"), before)

    def test_stale_marker_does_not_hide_a_reintroduced_arrow(self):
        with TemporaryDirectory() as temporary:
            project = Path(temporary)
            path = project / "scripts/scrNTTEFullScythe/scrNTTEFullScythe.gml"
            path.parent.mkdir(parents=True)
            before = (
                "    // FRONTIER214 Scythe mode control keeps its weapon icon without a corner arrow.\n"
                "    draw_sprite_ext(sprLoadoutArrow,0,x+12*_scale,y-12*_scale,"
                "0.65*_scale,0.65*_scale,90,c_white,_alpha);\n")
            path.write_text(before, encoding="utf8")
            with self.assertRaisesRegex(AssertionError, "contradicts"):
                apply(project)
            self.assertEqual(path.read_text("utf8"), before)


if __name__ == "__main__":
    unittest.main()
