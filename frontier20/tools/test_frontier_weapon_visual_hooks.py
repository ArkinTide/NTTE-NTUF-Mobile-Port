"""Disposable source fragments exercise the actual retained stage installer."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fr_content_hooks import patch
from fr_weapon_visual_hooks import apply


class WeaponVisualHookTests(unittest.TestCase):
    def fixture(self, folder):
        project = Path(folder)
        fragments = {
            "scripts/scrFire/scrFire.gml": "if (!_is_melee) {}\nelse wepangle *= -1\n",
            "scripts/scrUndergrowthNative/scrUndergrowthNative.gml": (
                "function scrUGWeaponPost(_kick,_reloadkick,_shake) {scr_weapon_post(gunangle,_kick,_reloadkick,_shake);}\n"),
            "scripts/scrNTTEFullScythe/scrNTTEFullScythe.gml": (
                "scr_weapon_post(gunangle,_heavy?-5:5,2,6+10*_heavy);\n"
                "scr_weapon_post(gunangle,12,15,17);\n"
                "scr_weapon_post(gunangle,6,7,3);\n"),
            "objects/Player/Step_0.gml": (
                "if (reload <= 0) {\n"
                "if(!scrNTTEFullMergedRuntimeStateReloaded(true) && !scrNTTEFullRedWeaponReloaded(true)) {}\n}\n"
                "if (breload <= 0) {\n"
                "if(!scrNTTEFullMergedRuntimeStateReloaded(false) && !scrNTTEFullRedWeaponReloaded(false)) {\n"
                "scrPlayerGunReloadFX(bwep);\n\t\t\t\twepflip *= -1;\n}\n}\n"),
            "scripts/scrNTTEFullMergedRuntimeState/scrNTTEFullMergedRuntimeState.gml": (
                "function scrNTTEFullMergedRuntimeStateReloadOne(_actor,_part,_primary) {\n native();\n}\n"),
            "scripts/scrWeapons/scrWeapons.gml": "function scrWeapons() {\n\tscrAmmoInit()\n}\n",
            "scripts/scrDrawPlayerHUD/scrDrawPlayerHUD.gml": (
                "function scrDrawPlayerHUD(_player) {\n\tscrNTTEFullParrotHUD(_player);\n"
                "scrNTTEFullDrawText(110, 7, string(_txt))\n}\n"),
            "scripts/frCode_Frontier_CharHuds_mod_fixture/hud.gml": (
                "// Original Characters/Frontier_CharHuds.mod.gml:16\n"
                "function fr_Characters_Frontier_CharHuds_mod_gml_player_hud() {\n"
                "var _frl__hudX = (scrFRPlayerIsActive(1) ? (_frl__hudSide ? (- 7) : 102) : 102);\n"
                "authored_charge_fill();\n}\n"
                "// Original Characters/Frontier_CharHuds.mod.gml:101\n"
                "function fr_Characters_Frontier_CharHuds_mod_gml_draw_gui() {\nold_projection();\n}\n"
                "// Original Characters/Frontier_CharHuds.mod.gml:189\n"
                "function fr_Characters_Frontier_CharHuds_mod_gml_draw_pause() {\nold_pause_snapshot();\n}\n"),
        }
        for relative, text in fragments.items():
            path = project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf8")
        patch(project, "objects/Player/Step_0.gml", "WEAPON PRIMARY RELOAD",
              "var _fr_reloaded=scrFRWeaponReloaded(true);", anchor="if (reload <= 0) {")
        patch(project, "objects/Player/Step_0.gml", "WEAPON SECONDARY RELOAD",
              "var _fr_breloaded=scrFRWeaponReloaded(false);", anchor="if (breload <= 0) {")
        return project

    def test_repeat_stage_keeps_exactly_one_source_swing_and_reload_owner(self):
        with TemporaryDirectory() as temporary:
            project = self.fixture(temporary)
            apply(project)
            once = {p.relative_to(project): p.read_bytes() for p in project.rglob("*.gml")}
            for _ in range(3):
                apply(project)
                self.assertEqual(once, {p.relative_to(project): p.read_bytes() for p in project.rglob("*.gml")})
            fire = (project / "scripts/scrFire/scrFire.gml").read_text("utf8")
            self.assertEqual(fire.count("wepangle *= -1"), 1)
            self.assertIn("!scrFRWeaponOwnsSwing(_wep)", fire)
            step = (project / "objects/Player/Step_0.gml").read_text("utf8")
            self.assertEqual(step.count("scrFRWeaponReloaded(true)"), 1)
            self.assertEqual(step.count("scrFRWeaponReloaded(false)"), 1)
            self.assertIn("if(!_fr_reloaded && !scrNTTEFullMergedRuntimeStateReloaded(true)", step)
            self.assertIn("if(!_fr_breloaded && !scrNTTEFullMergedRuntimeStateReloaded(false)", step)
            self.assertIn("scrPlayerGunReloadFX(bwep);\n\t\t\t\tbwepflip *= -1;", step)
            reload = (project / "scripts/scrNTTEFullMergedRuntimeState/scrNTTEFullMergedRuntimeState.gml").read_text("utf8")
            self.assertEqual(reload.count('scrFRWeaponMergedCallback(_actor,_part,_primary,"weapon_reloaded")'), 1)
            self.assertLess(reload.index("scrFRWeaponMergedCallback"), reload.index("native();"))

    def test_undergrowth_and_scythe_keep_source_kick_shift_shake_order(self):
        with TemporaryDirectory() as temporary:
            project = self.fixture(temporary)
            apply(project)
            source = (project / "scripts/scrUndergrowthNative/scrUndergrowthNative.gml").read_text("utf8")
            self.assertIn("scr_weapon_post(gunangle,_reloadkick,_shake,_kick)", source)
            source = (project / "scripts/scrNTTEFullScythe/scrNTTEFullScythe.gml").read_text("utf8")
            self.assertIn("scr_weapon_post(gunangle,6+10*_heavy,2,_heavy?-5:5)", source)
            self.assertIn("scr_weapon_post(gunangle,17,15,12)", source)
            self.assertIn("scr_weapon_post(gunangle,3,7,6)", source)

    def test_native_table_rebuild_restores_metadata_after_ammo_init(self):
        with TemporaryDirectory() as temporary:
            project = self.fixture(temporary)
            apply(project)
            source = (project / "scripts/scrWeapons/scrWeapons.gml").read_text("utf8")
            self.assertLess(source.index("scrAmmoInit()"), source.index("scrFRWeaponTablesRestore()"))

    def test_native_health_consumer_retains_authored_meter_and_retires_old_projection(self):
        with TemporaryDirectory() as temporary:
            project = self.fixture(temporary)
            apply(project)
            source = next((project / "scripts").glob("frCode_Frontier_CharHuds_mod_*/*.gml")).read_text("utf8")
            self.assertIn("var _frl__hudX = 119;", source)
            self.assertIn("authored_charge_fill();", source)
            self.assertNotIn("old_projection();", source)
            self.assertNotIn("old_pause_snapshot();", source)
            native = (project / "scripts/scrDrawPlayerHUD/scrDrawPlayerHUD.gml").read_text("utf8")
            self.assertEqual(native.count("scrFRBubblesHUD(_player)"), 1)
            self.assertIn("scrFREnabled() && scrFRRaceIs(_race) ? 132 : 110", native)


if __name__ == "__main__":
    unittest.main()
