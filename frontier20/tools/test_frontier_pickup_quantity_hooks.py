"""Disposable exact-source anchors for all three authored ammo augments."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fr_pickup_quantity_hooks import apply


class PickupQuantityHookTests(unittest.TestCase):
    def fixture(self, folder):
        project = Path(folder)
        for name in ("AugmentSecondStomach", "AugmentRabbitPaw", "AugmentOpenMind"):
            path = project / "scripts" / ("frCode_" + name + "_skill_fixture") / "source.gml"
            path.parent.mkdir(parents=True)
            path.write_text('fr_checked = true;\nnum += 0.5;\n'
                            'num += 1; // separate HP path stays authored\n'
                            'resprite();\n', encoding="utf8")
        path = project / "objects/AmmoPickup/Collision_Player.gml"
        path.parent.mkdir(parents=True)
        path.write_text('if(variable_instance_exists(id,"ntte_full_ammo_num")) {\n'
                        '    scrNTTEFullBackpackAmmoCollect(other.id); exit;\n}\n'
                        'with (scr_ultra_get(Race.CoopUltra, 1) ? Player : _player) {\n'
                        '\tvar _ammo_type = scrAmmoDecideType(id, false),\n'
                        '\t\t_give_amount = scrFRAmmoRead(id,"typ_ammo",_ammo_type)\n\t\n'
                        '\tif instance_is(other, CursedPickup) {\n'
                        '\t\t_give_amount = round(_give_amount * 1.5)\n\t}\n'
                        '\tif scrCrownCheck(crwn_haste) { _give_amount ++ }\n'
                        '\tscrPlayerGiveAmmo(id, _ammo_type, _give_amount, true)\n}\n', encoding="utf8")
        return project

    def test_exactly_three_source_quantity_writes_keep_flags_hp_and_visuals(self):
        with TemporaryDirectory() as temporary:
            project = self.fixture(temporary)
            apply(project)
            for path in (project / "scripts").glob("*/*.gml"):
                text = path.read_text("utf8")
                self.assertEqual(text.count("scrFRAmmoPickupUpgrade(id,0.5);"), 1)
                self.assertNotIn("num += 0.5;", text)
                self.assertIn("fr_checked = true;", text)
                self.assertIn("num += 1;", text)
                self.assertIn("resprite();", text)

    def test_native_consumer_keeps_configured_coop_live_recipient_and_haste(self):
        with TemporaryDirectory() as temporary:
            project = self.fixture(temporary)
            apply(project)
            text = (project / "objects/AmmoPickup/Collision_Player.gml").read_text("utf8")
            self.assertIn("scrNTTEFullBackpackAmmoCollect(other.id); exit;", text)
            self.assertIn("scr_ultra_get(Race.CoopUltra, 1) ? Player : _player", text)
            self.assertIn('round(scrFRAmmoRead(id,"typ_ammo",_ammo_type) * scrFRAmmoPickupQuantity(other.id))', text)
            self.assertNotIn("_give_amount * 1.5", text)
            self.assertLess(text.index("scrFRAmmoPickupQuantity"), text.index("_give_amount ++"))

    def test_repeat_stage_is_byte_identical(self):
        with TemporaryDirectory() as temporary:
            project = self.fixture(temporary)
            apply(project)
            before = {p.relative_to(project): p.read_bytes() for p in project.rglob("*.gml")}
            for _ in range(3):
                apply(project)
                self.assertEqual(before, {p.relative_to(project): p.read_bytes() for p in project.rglob("*.gml")})


if __name__ == "__main__":
    unittest.main()
