"""Transactional selection-hook safety; native gameplay supplies behavior proof."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import fr_mutation_pool204_hooks as hooks


class MutationPool204HookTests(unittest.TestCase):
    def fixture(self, folder):
        project = Path(folder)
        texts = {}
        for relative, before, after, marker in hooks.specs():
            texts[relative] = texts.get(relative, "") + before + "\n"
        texts[hooks.DRAW] += "// original alignment and HUD remain\nevent_user(0)\n"
        for relative, text in texts.items():
            path = project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, "utf8")
        template = project / "scripts/scrNTTEFullAreas/scrNTTEFullAreas.yy"
        template.parent.mkdir(parents=True, exist_ok=True)
        template.write_text(json.dumps({"name":"scrNTTEFullAreas","%Name":"scrNTTEFullAreas","resourceType":"GMScript"}), "utf8")
        (project / "nuclearthronemobile.yyp").write_text(json.dumps({"resources":[]}), "utf8")
        return project

    def snapshot(self, project):
        return {p.relative_to(project).as_posix():p.read_bytes() for p in project.rglob("*") if p.is_file()}

    def test_hook_keeps_native_alignment_and_earned_reward_and_registers_one_test(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            hooks.apply(project)
            draw = (project / hooks.DRAW).read_text("utf8")
            self.assertNotIn("until skill > 0 && !scr_skill_get", draw)
            self.assertIn("scr_skill_can_appear(_candidate)", draw)
            self.assertIn("GameCont.heavyheart>=3", draw)
            self.assertIn("skill=_pool[_at]", draw)
            self.assertIn("event_user(0)", draw)
            self.assertIn("skill = mut_last_wish", draw)
            self.assertNotIn("mut = mut_last_wish", draw)
            yyp = json.loads((project / "nuclearthronemobile.yyp").read_text("utf8"))
            self.assertEqual([hooks.SCRIPT], [r["id"]["name"] for r in yyp["resources"]])
            staged = project / f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.gml"
            self.assertEqual((hooks.ROOT / "native/mutation_pool204_tests.gml").read_bytes(), staged.read_bytes())

    def test_repeat_apply_is_byte_identical(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            hooks.apply(project)
            before = self.snapshot(project)
            for _ in range(3):
                hooks.apply(project)
                self.assertEqual(before, self.snapshot(project))

    def test_late_missing_or_duplicate_or_partial_anchor_does_not_write(self):
        last = hooks.specs()[-1]
        changes = [lambda s:s.replace(last[1], "unrelated-entry"),
                   lambda s:s+last[1], lambda s:s+last[3]]
        for change in changes:
            with self.subTest(change=change), TemporaryDirectory() as folder:
                project = self.fixture(folder)
                path = project / last[0]
                path.write_text(change(path.read_text("utf8")), "utf8")
                before = self.snapshot(project)
                with self.assertRaises(RuntimeError):
                    hooks.apply(project)
                self.assertEqual(before, self.snapshot(project))

    def test_duplicate_resource_is_rejected_without_partial_hooks(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            resource = {"id":{"name":hooks.SCRIPT,"path":f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.yy"}}
            (project / "nuclearthronemobile.yyp").write_text(json.dumps({"resources":[resource,resource]}), "utf8")
            before = self.snapshot(project)
            with self.assertRaises(RuntimeError):
                hooks.apply(project)
            self.assertEqual(before, self.snapshot(project))

    def test_does_not_patch_exclusive_content_or_random_chooser(self):
        paths = {r[0] for r in hooks.specs()}
        self.assertEqual({hooks.DRAW,"scripts/scrFrontier_tests/scrFrontier_tests.gml",
                          "scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml"}, paths)
        source = (hooks.ROOT / "native/mutation_pool204_tests.gml").read_text("utf8")
        self.assertIn("event_perform(ev_draw,64)", source)
        self.assertIn("scrDecideSkill(true)", source)
        self.assertIn("scrNTTEFullRatRewardNaturalTests()", source)
        self.assertIn("event_perform(ev_step,ev_step_normal)", source)
        self.assertIn("fr_Objects_Frontier_IDPD_mod_gml_AugmentStation_create", source)


if __name__ == "__main__":
    unittest.main()
