"""Transactional guards for a narrow collision-query installer.

Actual native seam, movement and real-wall behavior are verified by the Runner;
these checks protect registration, exact scope and failure atomicity.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

import fr_red_wall_query204_hooks as hooks


EVENT = """// native direct-Fake guard remains
if(instance_is(other.id,NTTEFullWallFake)) exit;
if(scrFRPalacePlayerWallCollision(other.id)) exit;
if(hammerhead && hammering>6) {scrWallDestroy(other.id);exit;}
if !roll && race != Race.Frog {
	if (instance_exists(Floor)) while (place_meeting(x, y, Wall)) {
		if(++_iteration>100) {scrWallDestroy(other.id);break;}
		if (!place_meeting(x, y, Wall)) break
	}
	move_contact_solid(direction,clamp(speed,1,maxspeed));
	if place_meeting(x + hspeed, y, Wall) {
		hspeed/=2;
		if place_meeting(x + hspeed, y, Wall) {hspeed=0;}
	}
	if place_meeting(x, y + vspeed, Wall) {
		vspeed/=2;
		if place_meeting(x, y + vspeed, Wall) {vspeed=0;}
	}
	x+=hspeed;y+=vspeed;
} else {move_bounce_solid(true);angle+=720;x+=hspeed;y+=vspeed;}
"""


class RedWallQuery204HookTests(unittest.TestCase):
    def fixture(self, folder):
        project = Path(folder)
        files = {
            hooks.EVENT: EVENT,
            "nuclearthronemobile.yyp": json.dumps({"resources": [], "keep": "untouched"}),
            "scripts/scrNTTEFullAreas/scrNTTEFullAreas.yy": json.dumps({
                "%Name": "scrNTTEFullAreas", "name": "scrNTTEFullAreas", "resourceType": "GMScript"}),
            "objects/Pickup/Collision_Wall.gml": "unchanged pickup movement\n",
        }
        for relative, text in files.items():
            path = project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, "utf8")
        return project

    def snapshot(self, project):
        return {p.relative_to(project).as_posix(): p.read_bytes()
                for p in project.rglob("*") if p.is_file()}

    def test_only_six_player_queries_change_and_native_response_is_retained(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            hooks.apply(project)
            event = (project / hooks.EVENT).read_text("utf8")
            restored = event
            for before, after, count in hooks.PATCHES:
                restored = restored.replace(after, before)
            self.assertEqual(EVENT, restored)
            self.assertEqual(6, event.count(hooks.FUNCTION + "("))
            self.assertNotIn("place_meeting(", event)
            self.assertEqual("unchanged pickup movement\n", (project / "objects/Pickup/Collision_Wall.gml").read_text("utf8"))
            self.assertEqual((hooks.ROOT / "native/red_wall_query204.gml").read_bytes(),
                             (project / f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.gml").read_bytes())
            resources = json.loads((project / "nuclearthronemobile.yyp").read_text("utf8"))["resources"]
            self.assertEqual([{"id": {"name": hooks.SCRIPT, "path": f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.yy"}}], resources)

    def test_repeat_apply_preserves_exact_bytes(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            hooks.apply(project)
            expected = self.snapshot(project)
            for _ in range(3):
                hooks.apply(project)
                self.assertEqual(expected, self.snapshot(project))

    def test_missing_duplicate_or_partial_queries_fail_without_writes(self):
        variants = [EVENT.replace(hooks.PATCHES[0][0], "changed-loop"),
                    EVENT + hooks.PATCHES[-1][0],
                    EVENT.replace(hooks.PATCHES[-1][0], hooks.PATCHES[-1][1], 1),
                    EVENT + "\n" + hooks.MARKER]
        for value in variants:
            with self.subTest(value=value), TemporaryDirectory() as folder:
                project = self.fixture(folder)
                (project / hooks.EVENT).write_text(value, "utf8")
                expected = self.snapshot(project)
                with self.assertRaises(RuntimeError):
                    hooks.apply(project)
                self.assertEqual(expected, self.snapshot(project))

    def test_duplicate_or_mismatched_resource_fails_before_player_write(self):
        resource = {"id": {"name": hooks.SCRIPT, "path": f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.yy"}}
        for resources in [[resource, resource], [{"id": {"name": hooks.SCRIPT, "path": "scripts/wrong.yy"}}]]:
            with self.subTest(resources=resources), TemporaryDirectory() as folder:
                project = self.fixture(folder)
                (project / "nuclearthronemobile.yyp").write_text(json.dumps({"resources": resources}), "utf8")
                expected = self.snapshot(project)
                with self.assertRaises(RuntimeError):
                    hooks.apply(project)
                self.assertEqual(expected, self.snapshot(project))

    def test_existing_modified_helper_or_metadata_fails_without_writes(self):
        for relative in [f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.gml", f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.yy"]:
            with self.subTest(relative=relative), TemporaryDirectory() as folder:
                project = self.fixture(folder)
                hooks.apply(project)
                path = project / relative
                value = "function scrNTTEFullPlayerWallMeeting(){return false;}" if path.suffix == ".gml" else '{}'
                path.write_text(value, "utf8")
                expected = self.snapshot(project)
                with self.assertRaises(RuntimeError):
                    hooks.apply(project)
                self.assertEqual(expected, self.snapshot(project))

    def test_partial_write_failure_restores_original_bytes_and_created_directories(self):
        with TemporaryDirectory() as folder:
            project = self.fixture(folder)
            expected = self.snapshot(project)
            directories = {p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_dir()}
            write_bytes, calls = Path.write_bytes, 0

            def fail_third(path, data):
                nonlocal calls
                calls += 1
                if calls == 3:
                    write_bytes(path, b"partial")
                    raise OSError("simulated partial write")
                return write_bytes(path, data)

            with patch.object(Path, "write_bytes", fail_third):
                with self.assertRaisesRegex(OSError, "simulated partial write"):
                    hooks.apply(project)
            self.assertEqual(expected, self.snapshot(project))
            self.assertEqual(directories, {p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_dir()})

    def test_helper_retains_all_nonfake_wall_families_and_avoids_normal_allocation(self):
        source = (hooks.ROOT / "native/red_wall_query204.gml").read_text("utf8")
        body = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("//"))
        self.assertNotIn(".solid", body)
        self.assertNotIn("instance_destroy", body)
        self.assertNotIn("mask_index", body)
        self.assertNotIn("NTTESolidWall", body)
        self.assertEqual(2, body.count("instance_is("))
        self.assertLess(body.index("if(_wall==noone) return false;"), body.index("ds_list_create()"))
        self.assertLess(body.index("if(!instance_is(_wall,NTTEFullWallFake)) return true;"), body.index("ds_list_create()"))
        self.assertIn("finally {ds_list_destroy(_walls);}", body)


if __name__ == "__main__":
    unittest.main()
