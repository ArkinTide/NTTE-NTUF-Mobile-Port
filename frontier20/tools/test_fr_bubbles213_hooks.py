from pathlib import Path
import unittest

from fr_bubbles213_hooks import transform_fixture, transform_touch


class Bubbles213HooksTests(unittest.TestCase):
    def test_touch_preserves_existing_edges_and_cancel_boundary(self):
        current = (Path(__file__).resolve().parents[1] / "staging/project/objects/JoystickAttack/Other_10.gml").read_text("utf-8-sig")
        marker = "        // FRONTIER213 BUBBLES VALID GESTURE RELEASE\n"
        added = marker + "        scrFRBubblesManualRelease213(index,mx,my,dis,dir,\n" + "            scrFRBubblesStartupTestsTouchButton(\"pressed\",index,mb_left),\n" + "            scrFRBubblesStartupTestsTouchButton(\"held\",index,mb_left),\n" + "            scrFRBubblesStartupTestsTouchButton(\"released\",index,mb_left));\n"
        self.assertIn(added,current)
        original=current.replace("\t\t\n"+added, "", 1)
        self.assertEqual(transform_touch(original),current)
        self.assertEqual(transform_touch(current),current)
        self.assertIn("// note: press & release are swapped intentionally", current)
        self.assertIn("distance_to_point(mx, my) > rad * 3", current)

    def test_fixture_is_idempotent(self):
        current=(Path(__file__).resolve().parents[1]/"native/bubbles_startup_tests.gml").read_text("utf-8-sig")
        self.assertEqual(transform_fixture(current),current)
        self.assertIn('_state.touch[$ "dx"]??1',current)

    def test_missing_touch_boundary_rejected(self):
        with self.assertRaises(AssertionError):
            transform_touch("unrelated event")

    def test_missing_fixture_boundary_rejected(self):
        with self.assertRaises(AssertionError):
            transform_fixture("unrelated script")


if __name__ == "__main__":
    unittest.main()
