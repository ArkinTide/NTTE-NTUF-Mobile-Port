from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import fr_menu_input204_hooks as hooks


class MenuInput204HookTests(unittest.TestCase):
    def fixture(self, folder):
        project = Path(folder)
        texts = {}
        for row in hooks.hook_specs():
            texts[row["path"]] = texts.get(row["path"], "") + row["anchor"] + "\n"
        for name, text in texts.items():
            path = project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf8")
        return project

    def snapshot(self, project):
        return {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob("*.gml")}

    def test_mode_guard_is_local_and_repeat_application_is_identical(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            result = hooks.apply(project)
            text = (project / "scripts/scrGamepadUIControl/scrGamepadUIControl.gml").read_text("utf8")
            self.assertIn("!KeyCont.keyboard[global.index] && !KeyCont.gamepad[global.index]", text)
            self.assertIn("gamepad_h=0;gamepad_v=0;return;", text)
            self.assertNotIn("pending", text)
            self.assertFalse(result["pointer_or_movement_queues_changed"])
            before = self.snapshot(project)
            for _ in range(3):
                hooks.apply(project)
                self.assertEqual(before, self.snapshot(project))

    def test_unfixed_candidate_installs_identical_observers_without_mode_guard(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            before = (project / "scripts/scrGamepadUIControl/scrGamepadUIControl.gml").read_bytes()
            result = hooks.apply(project, production_fix=False)
            self.assertEqual(before, (project / "scripts/scrGamepadUIControl/scrGamepadUIControl.gml").read_bytes())
            self.assertFalse(result["production_fix"])
            driver = (project / "scripts/scrFrontier_tests/scrFrontier_tests.gml").read_text("utf8")
            self.assertIn("scrFRMenuInput204Start", driver)
            self.assertIn("scrFRMenuInput204Step", driver)

    def test_missing_anchor_and_partial_marker_fail_before_writes(self):
        for partial in (False, True):
            with self.subTest(partial=partial), TemporaryDirectory() as folder:
                project = self.fixture(folder)
                row = hooks.hook_specs()[-1]
                path = project / row["path"]
                text = path.read_text("utf8")
                text += "// BEGIN FRONTIER " + row["label"] + "\n" if partial else ""
                if not partial:
                    text = text.replace(row["anchor"], "anchor_changed()")
                path.write_text(text, encoding="utf8")
                before = self.snapshot(project)
                with self.assertRaises(RuntimeError):
                    hooks.apply(project)
                self.assertEqual(before, self.snapshot(project))


if __name__ == "__main__":
    unittest.main()
