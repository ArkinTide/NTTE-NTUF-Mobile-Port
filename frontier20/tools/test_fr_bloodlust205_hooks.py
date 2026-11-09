from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest

import fr_bloodlust205_hooks as hook


class Bloodlust205HookTests(unittest.TestCase):
    def fixture(self, project):
        root = Path(__file__).resolve().parents[1]
        relatives = [relative for relative, *_ in hook.DEATHS] + [
            "scripts/scrFrontier_tests/scrFrontier_tests.gml",
            "scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml",
            "objects/NTTEFullBloodLust/Create_0.gml",
        ]
        for relative in relatives:
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / "staging/project" / relative, target)
        return relatives

    def test_production_and_real_combat_driver_are_idempotent(self):
        with TemporaryDirectory() as folder:
            project = Path(folder)
            relatives = self.fixture(project)
            report = hook.apply(project)
            hook.apply_tests(project)
            first = {r: (project / r).read_bytes() for r in relatives}
            hook.apply(project)
            hook.apply_tests(project)
            self.assertEqual(first, {r: (project / r).read_bytes() for r in relatives})
            self.assertTrue(report["authored_threshold_and_healing_retained"])
            enemy = (project / "objects/enemy/Destroy_0.gml").read_text("utf-8-sig")
            self.assertLess(enemy.index("scrFRBloodlust205TestsDeath();"),
                            enemy.index("scrFRBloodlust205EnemyDeath();"))
            self.assertLess(enemy.index("scrFRBloodlust205EnemyDeath();"), enemy.index("if hp > 0 exit"))

    def test_missing_final_anchor_has_no_partial_writes(self):
        with TemporaryDirectory() as folder:
            project = Path(folder)
            relatives = self.fixture(project)
            nothing = project / "objects/Nothing2/Destroy_0.gml"
            nothing.write_text("// incompatible native base\n", encoding="utf-8")
            original = {r: (project / r).read_bytes() for r in relatives}
            with self.assertRaises(AssertionError):
                hook.apply(project)
            self.assertEqual(original, {r: (project / r).read_bytes() for r in relatives})

    def test_acceptance_uses_engine_combat_and_original_source_effect(self):
        root = Path(__file__).resolve().parents[1]
        native = (root / "native/bloodlust205_tests.gml").read_text("utf-8")
        self.assertIn("fr_Objects_Frontier_IDPD_mod_gml_AugmentStation_create", native)
        self.assertIn("scr_projectile_create(_target.x,_target.y,Bullet1,0,0)", native)
        self.assertIn("instance_create(_target.x,_target.y,EnemyBullet1)", native)
        self.assertIn("counter_at_12", native)
        self.assertIn("_p.hp==5", native)
        self.assertIn("held_dead_source_poll", native)
        for forbidden in ("scrFRBloodlust205EnemyDeath(", "scrFRSkillHooks(",
                          "fr_Mutations_AugmentBloodlust_skill_gml_step(", "_target.hp=", "_target.hp ="):
            self.assertNotIn(forbidden, native)
        production = (root / "native/bloodlust205.gml").read_text("utf-8")
        self.assertIn('!is_undefined(self[$ "fr_AugmentBloodlust"])', production)
        self.assertIn('scrFRGetSkill("AugmentBloodlust")<=0', production)
        for forbidden in ("hp+=", "hp +=", "instance_destroy", ">=13", "BloodLust)"):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
