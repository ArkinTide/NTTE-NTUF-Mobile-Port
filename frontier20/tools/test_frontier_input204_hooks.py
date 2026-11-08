from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import fr_input204_hooks as hooks
import fr_input_hooks as old_hooks


class Input204HookTests(unittest.TestCase):
    def fixture(self, folder):
        project = Path(folder)
        texts = {}
        for hook in hooks.hook_specs():
            text = texts.get(hook["path"], "")
            if "end" in hook:
                text += (hook["scope"] + "\n" + hook["anchor"]
                         + "\nlegacy_eight_way_direction_and_backoff();\n}\n"
                         + hook["end"] + "\noriginal_arrival_particles_and_sound();\n}\n")
            else:
                text += hook["anchor"] + "\n"
            texts[hook["path"]] = text
        for relative, text in texts.items():
            path = project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, "utf8")
        return project

    def snapshot(self, project):
        return {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob("*.gml")}

    def test_replaces_only_dash_geometry_and_preserves_source_effects(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            hooks.apply(project)
            source = (project / hooks.source_script("Mutations/AugmentExtraFeet.skill.gml")).read_text("utf8")
            self.assertNotIn("legacy_eight_way_direction_and_backoff", source)
            self.assertIn("original_arrival_particles_and_sound", source)
            self.assertIn("scrFRPocketTeleporterStep204(); return;", source)
            self.assertIn("scrFRPocketTeleporterAngle204(index)", source)
            self.assertIn("scrFRPocketTeleporterDistance204", source)
            view = (project / "scripts/scrFrontier_view_input/scrFrontier_view_input.gml").read_text("utf8")
            self.assertEqual(view.count("scrFRMenuTouchPoll204(); return;"), 1)
            self.assertIn("// FRONTIER POINTER 204 STABLE HARDWARE FRAME", view)
            before = self.snapshot(project)
            for _ in range(3):
                hooks.apply(project)
                self.assertEqual(before, self.snapshot(project))

    def test_missing_scope_and_partial_markers_fail_without_writing(self):
        relative = hooks.source_script("Mutations/AugmentExtraFeet.skill.gml")
        variants = (
            lambda s: s.replace("lastx = x;", "lastx = broken;"),
            lambda s: s + "// FRONTIER CONTROLLER 204 CONNECTION\n",
            lambda s: s.replace("function fr_Mutations_AugmentExtraFeet_skill_gml_dash() {", "different_scope() {"),
        )
        for change in variants:
            with self.subTest(change=change), TemporaryDirectory() as folder:
                project = self.fixture(folder)
                path = project / relative
                if "CONNECTION" in change(""):
                    path = project / "scripts/InputHandling/InputHandling.gml"
                path.write_text(change(path.read_text("utf8")), "utf8")
                before = self.snapshot(project)
                with self.assertRaises(RuntimeError):
                    hooks.apply(project)
                self.assertEqual(before, self.snapshot(project))

    def test_legacy_blink_hooks_allow_incremental_new_mask_sweep(self):
        with TemporaryDirectory() as folder:
            project = Path(folder)
            for hook in old_hooks.hook_specs():
                path = project / hook["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                text = path.read_text("utf8") if path.exists() else ""
                if "// FRONTIER TOUCH DASH INITIAL " not in hook["marker"]:
                    text += hook["replacement"] + "\n"
                else:
                    text += "// FRONTIER POCKET 204 CONTINUOUS MASK SWEEP\n"
                path.write_text(text, "utf8")
            before = self.snapshot(project)
            report = old_hooks.apply(project)
            self.assertEqual(2, sum(r["status"] == "superseded-mask-sweep" for r in report))
            self.assertEqual(before, self.snapshot(project))


if __name__ == "__main__":
    unittest.main()
