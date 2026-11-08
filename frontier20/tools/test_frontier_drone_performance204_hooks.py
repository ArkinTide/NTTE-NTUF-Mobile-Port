"""Guard Hyperion204 hooks using the frozen real generated source."""
from pathlib import Path
import tempfile
import unittest

from fr_drone_performance204_hooks import apply, NEAREST_NEW, COLLISION_NEW
from fr_hyperion_projectile_hooks import apply as apply_allegiance


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("scripts/frCode_AugmentCompassion_skill_fixture/source.gml")
DRIVER = Path("scripts/scrFrontier_tests/scrFrontier_tests.gml")
SMOKE = Path("scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml")


class DronePerformance204Hooks(unittest.TestCase):
    def fixture(self, root, crlf=False, bom=False):
        data = {
            SOURCE: (ROOT/"generated-code/Mutations_AugmentCompassion_skill_gml.gml").read_text("utf-8-sig"),
            DRIVER: "function scrFRIntegrationTestStep() {\n}\n",
            SMOKE: 'function smoke() {\n        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests")) {}\n}\n',
        }
        for relative, text in data.items():
            path = root/relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((b"\xef\xbb\xbf" if bom else b"")
                             + text.replace("\n", "\r\n" if crlf else "\n").encode())
        apply_allegiance(root)

    def test_actual_source_idempotence_and_previous_installer_compatibility(self):
        for crlf, bom in ((False, False), (True, True)):
            with self.subTest(crlf=crlf), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.fixture(root, crlf, bom)
                apply(root)
                once = {path: (root/path).read_bytes() for path in (SOURCE, DRIVER, SMOKE)}
                for _ in range(3):
                    apply_allegiance(root)
                    apply(root)
                    self.assertEqual(once, {path: (root/path).read_bytes() for path in once})
                text = (root/SOURCE).read_text("utf-8-sig")
                self.assertEqual(1, text.count(NEAREST_NEW))
                self.assertEqual(1, text.count(COLLISION_NEW))
                # Original native callbacks and exact source reference remain
                # available to the isolated parity fixture, never saved mode.
                self.assertEqual(2, text.count("on_grenade = fr_Mutations_AugmentCompassion_skill_gml_DroneShock_nullify;"))
                self.assertIn("scrFRSoundPitchVolume(sndPickupDisappear", text)
                self.assertIn("scrFRInstanceDestroy();", text)
                self.assertEqual(once[SOURCE].startswith(b"\xef\xbb\xbf"), bom)
                self.assertEqual(b"\r\n" in once[SOURCE], crlf)

    def test_missing_duplicate_partial_and_late_failure_are_transactional(self):
        variations = [
            (SOURCE, lambda text: text.replace(".instance_nearest_array, x, y,", ".changed_query, x, y,")),
            (SOURCE, lambda text: text + "\n" + NEAREST_NEW),
            (SOURCE, lambda text: text + "\n// FRONTIER DRONE204 DIRECT INTERCEPT"),
            (DRIVER, lambda text: text.replace("scrFRIntegrationTestStep", "changed_driver")),
            (SMOKE, lambda text: text.replace("Release127PerfTests", "changed_entry")),
        ]
        for relative, mutate in variations:
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.fixture(root)
                (root/relative).write_text(mutate((root/relative).read_text()), "utf8")
                before = {path: (root/path).read_bytes() for path in (SOURCE, DRIVER, SMOKE)}
                with self.assertRaises(AssertionError):
                    apply(root)
                self.assertEqual(before, {path: (root/path).read_bytes() for path in before})

    def test_duplicate_module_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            other = root/str(SOURCE).replace("_fixture", "_duplicate")
            other.parent.mkdir(parents=True)
            other.write_bytes((root/SOURCE).read_bytes())
            before = (root/SOURCE).read_bytes()
            with self.assertRaises(AssertionError):
                apply(root)
            self.assertEqual(before, (root/SOURCE).read_bytes())


if __name__ == "__main__":
    unittest.main()
