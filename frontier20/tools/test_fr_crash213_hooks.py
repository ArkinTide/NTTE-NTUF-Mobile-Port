"""Lifecycle repair installer checks on copies; never alter the live project."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import fr_crash213_hooks as hooks


ROOT = Path(__file__).resolve().parents[1]
MODULE = "scripts/frCode_Frontier_Projectiles2_mod_fixture/module.gml"
IMPACT = "scripts/frCode_AugmentImpactWrists_skill_fixture/module.gml"
ACTORS = "scripts/scrFRActors/scrFRActors.gml"
MENU = "scripts/scrOptionsUpdate/scrOptionsUpdate.gml"


def projectile_fixture():
    text = "// unrelated preserved prefix\n"
    for name, target in hooks.HOMING_FUNCTIONS.items():
        text += ("// Original fixture\nfunction fr_Objects_Frontier_Projectiles2_mod_gml_" + name + "() {\n"
                 "if (scrFRInstanceExists(enemy)) {\n{\nvar " + target + " = instance_nearest(x, y, enemy);\n;\n"
                 "direction = point_direction(x, y, " + target + ".x, " + target + ".y);\n}\n}\n"
                 "preserved_callback_tail();\n}\n\n")
    return text + "// Original unrelated suffix\nfunction preserved() {}\n"


class Crash213HooksTests(unittest.TestCase):
    def test_actor_id_read_is_inside_instance_scope_and_real_type_branch(self):
        result = hooks.transform_actor("// before\n" + hooks.ACTOR_OLD + "\n// after\n")
        self.assertIn('if(_type==IceFlower) {\n        if(!is_struct(self)) {\n            if(scrFRPromptIs(id))', result)
        self.assertNotIn('&& scrFRPromptIs(id)', result)
        self.assertIn('_proxy.fr_prompt_proxy=true', result)
        self.assertTrue(result.startswith("// before\n"))
        self.assertTrue(result.endswith("\n// after\n"))
        self.assertEqual(result, hooks.transform_actor(result))

    def test_every_homing_guard_uses_the_returned_handle_not_family_count(self):
        original = projectile_fixture()
        patched = hooks.transform_projectiles(original)
        self.assertEqual(4, patched.count("FRONTIER213 VALIDATE SELECTED HOMING TARGET"))
        self.assertNotIn("scrFRInstanceExists(enemy)", patched)
        self.assertEqual(4, patched.count("preserved_callback_tail();"))
        self.assertEqual(4, patched.count("direction = point_direction"))
        for target in set(hooks.HOMING_FUNCTIONS.values()):
            self.assertIn("if (instance_exists(" + target + "))", patched)
        self.assertTrue(patched.startswith("// unrelated preserved prefix\n"))
        self.assertTrue(patched.endswith("function preserved() {}\n"))
        self.assertEqual(patched, hooks.transform_projectiles(patched))

    def test_menu_reset_reaches_type_aware_key_eraser_once(self):
        original = "function scrOptionsEraseSettings() {\n" + hooks.MENU_OLD + "\nkept_tail();\n}"
        result = hooks.transform_menu(original)
        self.assertIn("scrOptionsEraseKeys213(options,UberCont.saveData)", result)
        self.assertIn("kept_tail();", result)
        self.assertNotIn("array_foreach", result)
        self.assertEqual(result, hooks.transform_menu(result))

    def test_orphan_hitbox_keeps_live_owner_handoff_and_native_destroy(self):
        original = "preserved_prefix();\n" + hooks.IMPACT_OLD + "\npreserved_tail();\n"
        result = hooks.transform_impact(original)
        self.assertIn('if (scrFRInstanceExists(creator)) {\ncreator.droneHitbox = noone;', result)
        self.assertEqual(1, result.count("creator.droneHitbox = noone;"))
        self.assertTrue(result.startswith("preserved_prefix();\n"))
        self.assertTrue(result.endswith("\npreserved_tail();\n"))
        self.assertEqual(result, hooks.transform_impact(result))

    def make_project(self, folder, newline="\n", bom=b""):
        project = Path(folder)
        texts = {ACTORS: hooks.ACTOR_OLD, MENU: hooks.MENU_OLD,
                 MODULE: projectile_fixture(), IMPACT: hooks.IMPACT_OLD}
        for relative, source in texts.items():
            path = project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(bom + source.replace("\n", newline).encode("utf8"))
        return project

    def test_apply_preserves_bom_newlines_and_repeated_apply_is_stable(self):
        native_before = (ROOT / "native/actors.gml").read_bytes()
        for newline in ("\n", "\r\n"):
            for bom in (b"", b"\xef\xbb\xbf"):
                with self.subTest(newline=newline, bom=bool(bom)), TemporaryDirectory() as folder:
                    project = self.make_project(folder, newline, bom)
                    hooks.apply(project)
                    first = {p: (project / p).read_bytes() for p in (ACTORS, MENU, MODULE, IMPACT)}
                    hooks.apply(project)
                    self.assertEqual(first, {p: (project / p).read_bytes() for p in first})
                    for data in first.values():
                        self.assertEqual(bool(bom), data.startswith(b"\xef\xbb\xbf"))
                        if newline == "\r\n":
                            self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
                        else:
                            self.assertNotIn(b"\r\n", data)
        self.assertEqual(native_before, (ROOT / "native/actors.gml").read_bytes(),
                         "Installing a copied project must not alter maintained native source")

    def test_changed_or_partial_source_fails_before_any_write(self):
        for relative, before, after in (
            (ACTORS, "scrFRPromptIs(id)", "other_prompt(id)"),
            (MENU, "array_foreach(_categories", "another_foreach(_categories"),
            (MODULE, "var _frl_myTarget =", "var renamed_target ="),
            (IMPACT, "creator.droneHitbox = noone;", "creator.otherHitbox = noone;"),
        ):
            with self.subTest(path=relative), TemporaryDirectory() as folder:
                project = self.make_project(folder)
                path = project / relative
                path.write_text(path.read_text("utf8").replace(before, after, 1), "utf8")
                snapshot = {p: (project / p).read_bytes() for p in (ACTORS, MENU, MODULE, IMPACT)}
                with self.assertRaises(RuntimeError):
                    hooks.apply(project)
                self.assertEqual(snapshot, {p: (project / p).read_bytes() for p in snapshot})

    def test_live_actor_mirror_and_all_audited_production_hooks_are_current(self):
        project = ROOT / "staging/project"
        actor = (ROOT / "native/actors.gml").read_text("utf-8-sig")
        self.assertEqual(actor, (project / ACTORS).read_text("utf-8-sig"))
        self.assertEqual(actor, hooks.transform_actor(actor))
        menu = (project / MENU).read_text("utf-8-sig")
        self.assertEqual(menu, hooks.transform_menu(menu))
        module = next(project.glob("scripts/frCode_Frontier_Projectiles2_mod_*/*.gml")).read_text("utf-8-sig")
        self.assertEqual(module, hooks.transform_projectiles(module))
        impact = next(project.glob("scripts/frCode_AugmentImpactWrists_skill_*/*.gml")).read_text("utf-8-sig")
        self.assertEqual(impact, hooks.transform_impact(impact))


if __name__ == "__main__":
    unittest.main()
