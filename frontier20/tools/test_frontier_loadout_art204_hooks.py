"""Guard a one-field metadata repair and atomic isolated test registration."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re
import unittest
from unittest.mock import patch

import fr_loadout_art204_hooks as hooks


class LoadoutArt204HookTests(unittest.TestCase):
    def fixture(self, folder):
        project = Path(folder)
        source = (hooks.ROOT / "native/weapons.gml").read_bytes()
        old = source.replace(hooks.NEW.encode(), hooks.OLD.encode(), 1)
        files = {
            hooks.WEAPONS: old,
            "nuclearthronemobile.yyp": json.dumps({"resources": [], "keep": "preserved"}).encode(),
            "scripts/scrNTTEFullAreas/scrNTTEFullAreas.yy": json.dumps({
                "%Name": "scrNTTEFullAreas", "name": "scrNTTEFullAreas", "resourceType": "GMScript"}).encode(),
            "scripts/scr_weapon_get_type/scr_weapon_get_type.gml": b"unchanged metadata consumers\n",
            "scripts/scrCampfireMenuCreate/scrCampfireMenuCreate.gml": b"unchanged selection drawing\n",
            "scripts/scrFire/scrFire.gml": b"unchanged gameplay firing\n",
        }
        for relative, raw in files.items():
            path = project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        return project

    @staticmethod
    def snapshot(project):
        return {p.relative_to(project).as_posix(): p.read_bytes()
                for p in project.rglob("*") if p.is_file()}

    def test_repair_changes_only_loadout_field_and_registers_separate_regression(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            before = self.snapshot(project)
            hooks.apply(project)
            after = self.snapshot(project)
            self.assertEqual(before[hooks.WEAPONS], after[hooks.WEAPONS].replace(hooks.NEW.encode(), hooks.OLD.encode(), 1))
            for name in before:
                if name not in (hooks.WEAPONS, "nuclearthronemobile.yyp"):
                    self.assertEqual(before[name], after[name], name)
            relative = f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.yy"
            self.assertEqual([{"id": {"name": hooks.SCRIPT, "path": relative}}],
                             json.loads(after["nuclearthronemobile.yyp"])["resources"])
            self.assertEqual((hooks.ROOT / "native/loadout_art204_tests.gml").read_bytes(),
                             after[f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.gml"])

    def test_repeated_application_is_byte_identical(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            hooks.apply(project)
            expected = self.snapshot(project)
            for _ in range(3):
                hooks.apply(project)
                self.assertEqual(expected, self.snapshot(project))

    def test_unrelated_staged_weapon_changes_are_rejected_without_writes(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            path = project / hooks.WEAPONS
            path.write_bytes(path.read_bytes() + b"\n// unrelated local change\n")
            expected = self.snapshot(project)
            with self.assertRaisesRegex(RuntimeError, "unrelated changes"):
                hooks.apply(project)
            self.assertEqual(expected, self.snapshot(project))

    def test_ambiguous_registration_or_modified_regression_fails_atomically(self):
        resource = {"id": {"name": hooks.SCRIPT, "path": f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.yy"}}
        variants = [[resource, resource], [{"id": {"name": hooks.SCRIPT, "path": "wrong.yy"}}]]
        for resources in variants:
            with self.subTest(resources=resources), TemporaryDirectory() as folder:
                project = self.fixture(folder)
                (project / "nuclearthronemobile.yyp").write_text(json.dumps({"resources": resources}), "utf8")
                expected = self.snapshot(project)
                with self.assertRaises(RuntimeError):
                    hooks.apply(project)
                self.assertEqual(expected, self.snapshot(project))
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            hooks.apply(project)
            path = project / f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.gml"
            path.write_text("modified test", "utf8")
            expected = self.snapshot(project)
            with self.assertRaisesRegex(RuntimeError, "regression differs"):
                hooks.apply(project)
            self.assertEqual(expected, self.snapshot(project))

    def test_partial_write_restores_exact_bytes_and_directories(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            expected = self.snapshot(project)
            directories = {p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_dir()}
            write_bytes, calls = Path.write_bytes, 0

            def fail_third(path, raw):
                nonlocal calls
                calls += 1
                if calls == 3:
                    write_bytes(path, b"partial")
                    raise OSError("simulated partial write")
                return write_bytes(path, raw)

            with patch.object(Path, "write_bytes", fail_third):
                with self.assertRaisesRegex(OSError, "simulated partial write"):
                    hooks.apply(project)
            self.assertEqual(expected, self.snapshot(project))
            self.assertEqual(directories, {p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_dir()})

    def test_all_authored_loadout_callbacks_have_native_packaged_art(self):
        # The source corpus is the independent inventory: do not just ask the
        # repaired native table which two Bubbles IDs it knows about.
        authored = []
        for path in (hooks.ROOT / "original/Frontier/Weapons").glob("*.wep.gml"):
            source = path.read_text("utf-8-sig")
            if not re.search(r"^#define\s+weapon_loadout\b", source, re.M):
                continue
            match = re.search(r'sprite_add_weapon\("([^\"]+Loadout[^\"]+\.png)"', source, re.I)
            self.assertIsNotNone(match, path.name)
            authored.append((path.stem.removesuffix(".wep"), match.group(1).removeprefix("../").lower()))
        self.assertEqual({"FR_BubblesCutlass", "FR_BubblesShovel"}, {name for name, _ in authored})
        lookup = json.loads((hooks.ROOT / "generated-assets/path-lookup.json").read_text("utf-8-sig"))
        resources = {entry["id"]["name"] for entry in hooks.read_json(
            (hooks.ROOT / "staging/project/nuclearthronemobile.yyp").read_bytes())["resources"]}
        for name, path in authored:
            with self.subTest(weapon=name):
                variants = lookup[path]
                self.assertTrue(variants)
                self.assertIn(variants[0]["resource"], resources)
                generated = (hooks.ROOT / f"generated-code/Weapons_{name}_wep_gml.gml").read_text("utf-8-sig")
                self.assertIn(f"function fr_Weapons_{name}_wep_gml_weapon_loadout()", generated)
                self.assertIn(variants[0]["resource"], generated)


if __name__ == "__main__":
    unittest.main()
