"""Small project fixtures prove the supplemental importer fails closed."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

import fr_boss_art204_hooks as hook


class BossArt204Tests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="frontier-boss-art204-test-")
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.source = self.root / "original"
        self.output = self.root / "supplement"
        self.base = self.root / "manifest.json"
        real = hook.ROOT / "staging/project"
        for relative in ("sprites/mskBandit/mskBandit.yy",
                         "sprites/sprBossIntro/sprBossIntro.yy",
                         "sprites/sprBossIntroBackLayer/sprBossIntroBackLayer.yy",
                         "sprites/sprBossName/sprBossName.yy",
                         "scripts/scrNTTEFullAreas/scrNTTEFullAreas.yy",
                         "objects/UberCont/Draw_0.gml",
                         "scripts/scrBossIntro/scrBossIntro.gml"):
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(real / relative, target)
        registry = self.project / hook.REGISTRY
        registry.parent.mkdir(parents=True, exist_ok=True)
        registry.write_text("function scrFRRegisterAssets() {\n    // unrelated existing registrations\n}\n", encoding="utf8")
        (self.project / "nuclearthronemobile.yyp").write_text(json.dumps({"resources": []}), encoding="utf8")
        self.callback = "scripts/frCode_Frontier_Bosses_mod_fixture/frCode_Frontier_Bosses_mod_fixture.gml"
        target = self.project / self.callback
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(hook.CALLBACK + "\nintro = false;\n;\n" + hook.SOURCE_GUARD + "\n"
                          + "\n".join(f"scrFRSpriteReplaceImage({native}, spr_{role.lower()}, 0);" for role, native in hook.TARGETS.items())
                          + "\nevent_perform(ev_alarm, 6);\n}\n"
                          + "scrFRSpriteRestore(sprBossIntro);\n;\nscrFRSpriteRestore(sprBossIntroBackLayer);\n;\nscrFRSpriteRestore(sprBossName);\n;\nscrFRInstanceDestroy();\n}\n"
                          + hook.NEXT_CALLBACK + "_hp) {return _hp;}\n", encoding="utf8")
        media = []
        for boss in hook.BOSSES:
            for role in hook.TARGETS:
                relative = f"Sprites/Menu/Intros/spr{boss}{role}.png"
                target = self.source / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(hook.SOURCE / relative, target)
                raw = target.read_bytes()
                media.append({"path": relative, "bytes": len(raw), "sha256": hook.sha(raw)})
        self.base.write_bytes(hook.json_bytes({"original_media": media}))

    def tearDown(self):
        self.temporary.cleanup()

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}

    def emit(self):
        return hook.emit(self.project, self.output, self.source, self.base)

    def apply(self):
        return hook.apply(self.project, self.output, self.source, self.base)

    def verify(self):
        return hook.verify(self.project, self.output, self.source, self.base)

    def test_all_authored_triplets_exact_and_emit_leaves_project_and_base_untouched(self):
        before, base = self.snapshot(self.project), self.base.read_bytes()
        manifest = self.emit()
        self.assertEqual(before, self.snapshot(self.project))
        self.assertEqual(base, self.base.read_bytes())
        self.assertEqual(15, len(manifest["assets"]))
        self.assertEqual(45, len(manifest["files"]))
        self.assertEqual(30, sum(len(row["aliases"]) for row in manifest["assets"]))
        for row in manifest["assets"]:
            self.assertEqual([40, 37] if row["role"] == "Name" else [246, 0], row["origin"])
            self.assertEqual(181 if row["role"] == "Name" else 481 if row["boss"] == "GraveyardBoss" and row["role"] == "Main" else 492, row["width"])
            sprite = hook.importer.load_yy(self.output / f'sprites/{row["resource"]}/{row["resource"]}.yy')
            frame = sprite["frames"][0]["name"]
            with Image.open(self.output / f'sprites/{row["resource"]}/{frame}.png') as image:
                self.assertEqual(row["rgba_sha256"], hook.sha(image.convert("RGBA").tobytes()))
        generated = self.snapshot(self.output)
        self.emit()
        self.assertEqual(generated, self.snapshot(self.output))

    def test_apply_is_idempotent_and_has_exactly_one_registration_per_alias(self):
        self.emit()
        result = self.apply()
        self.assertTrue(result["changed_paths"])
        before = self.snapshot(self.project)
        self.assertEqual([], self.apply()["changed_paths"])
        self.assertEqual(before, self.snapshot(self.project))
        self.assertEqual("PASS", self.verify()["status"])
        registry = (self.project / hook.REGISTRY).read_text(encoding="utf8")
        self.assertEqual(30, registry.count("global.fr_asset_sources"))
        model = hook.importer.load_yy(self.project / "nuclearthronemobile.yyp")
        self.assertEqual(17, len(model["resources"]))

    def test_changed_original_is_rejected_before_any_output(self):
        original = self.source / "Sprites/Menu/Intros/sprRoboBossMain.png"
        original.write_bytes(original.read_bytes() + b"changed")
        before = self.snapshot(self.project)
        with self.assertRaisesRegex(RuntimeError, "frozen archive"):
            self.emit()
        self.assertFalse(self.output.exists())
        self.assertEqual(before, self.snapshot(self.project))

    def test_partial_marker_rejects_apply_before_project_writes(self):
        self.emit()
        registry = self.project / hook.REGISTRY
        registry.write_text(registry.read_text(encoding="utf8") + hook.BEGIN, encoding="utf8")
        before = self.snapshot(self.project)
        with self.assertRaisesRegex(RuntimeError, "partial, duplicate"):
            self.apply()
        self.assertEqual(before, self.snapshot(self.project))

    def test_duplicate_alias_outside_marker_is_rejected(self):
        manifest = self.emit()
        self.apply()
        registry = self.project / hook.REGISTRY
        row = manifest["assets"][0]
        with registry.open("a", encoding="utf8") as stream:
            stream.write(f'\nglobal.fr_asset_sources[$ "{row["aliases"][0]}"]={row["resource"]};\n')
        before = self.snapshot(self.project)
        with self.assertRaisesRegex(RuntimeError, "duplicate/mismatched path alias"):
            self.apply()
        self.assertEqual(before, self.snapshot(self.project))

    def test_existing_resource_conflict_does_not_overwrite(self):
        manifest = self.emit()
        relative = next(iter(manifest["files"]))
        target = self.project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"unrelated existing data")
        before = self.snapshot(self.project)
        with self.assertRaisesRegex(RuntimeError, "existing resource differs"):
            self.apply()
        self.assertEqual(before, self.snapshot(self.project))

    def test_verify_rejects_staged_pixels_and_missing_alias(self):
        manifest = self.emit()
        self.apply()
        relative = next(path for path in manifest["files"] if path.endswith(".png"))
        target = self.project / relative
        raw = target.read_bytes()
        target.write_bytes(raw + b"tampered")
        with self.assertRaisesRegex(RuntimeError, "staged resource mismatch"):
            self.verify()
        target.write_bytes(raw)
        registry = self.project / hook.REGISTRY
        registry.write_text(registry.read_text(encoding="utf8").replace(manifest["assets"][0]["aliases"][0], "wrong/path", 1), encoding="utf8")
        with self.assertRaisesRegex(RuntimeError, "changed registry block"):
            self.verify()

    def test_verify_rejects_changed_target_origin(self):
        self.emit()
        self.apply()
        target = self.project / "sprites/sprBossIntro/sprBossIntro.yy"
        data = hook.importer.load_yy(target)
        data["sequence"]["xorigin"] = 240
        target.write_bytes(hook.json_bytes(data))
        with self.assertRaisesRegex(RuntimeError, "source/origin mismatch"):
            self.verify()

    def test_write_failure_rolls_back_partial_project_transaction(self):
        self.emit()
        before = self.snapshot(self.project)
        write_bytes = Path.write_bytes
        counter = [0]

        def fail_once(path, data):
            if path.is_relative_to(self.project):
                counter[0] += 1
                if counter[0] == 4:
                    raise OSError("injected fixture write failure")
            return write_bytes(path, data)

        with patch.object(Path, "write_bytes", fail_once):
            with self.assertRaisesRegex(OSError, "injected fixture"):
                self.apply()
        self.assertEqual(before, self.snapshot(self.project))

    def test_supplement_descriptor_tampering_is_rejected_before_apply(self):
        manifest = self.emit()
        row = manifest["assets"][0]
        target = self.output / f'sprites/{row["resource"]}/{row["resource"]}.yy'
        data = hook.importer.load_yy(target)
        data["sequence"]["yorigin"] = 17
        target.write_bytes(hook.json_bytes(data))
        before = self.snapshot(self.project)
        with self.assertRaisesRegex(RuntimeError, "descriptor mismatch"):
            self.apply()
        self.assertEqual(before, self.snapshot(self.project))

    def test_postwrite_verification_failure_also_rolls_back(self):
        self.emit()
        before = self.snapshot(self.project)
        with patch.object(hook, "verify", side_effect=RuntimeError("injected final verification failure")):
            with self.assertRaisesRegex(RuntimeError, "injected final verification"):
                self.apply()
        self.assertEqual(before, self.snapshot(self.project))

    def test_emitter_failure_leaves_no_partial_supplement(self):
        before = self.snapshot(self.project)
        emitter = hook.importer.emit_sprite
        counter = [0]

        def fail_once(*args):
            counter[0] += 1
            if counter[0] == 3:
                raise OSError("injected sprite emission failure")
            return emitter(*args)

        with patch.object(hook.importer, "emit_sprite", fail_once):
            with self.assertRaisesRegex(OSError, "injected sprite emission"):
                self.emit()
        self.assertFalse(self.output.exists())
        self.assertEqual(before, self.snapshot(self.project))

    def test_native_bridge_is_scoped_to_exact_frontier_callback(self):
        original = (self.project / self.callback).read_text(encoding="utf8")
        unrelated = "\nfunction unrelated() { event_perform(ev_alarm, 6); scrFRSpriteReplaceImage(sprBossIntro, other_asset, 0); }\n"
        result = hook.callback_transform(original + unrelated)
        self.assertTrue(result.endswith(unrelated))
        self.assertEqual(1, result.count("scrFRBossArt204IntroStart(_fr_boss_art204_owner)"))
        self.assertEqual(3, result.count("scrFRBossArt204Replace("))
        self.assertEqual(result, hook.callback_transform(result))

    def test_partial_native_callback_rejects_entire_transaction(self):
        self.emit()
        target = self.project / self.callback
        target.write_text(target.read_text(encoding="utf8").replace("event_perform(ev_alarm, 6);", "scrFRBossArt204IntroStart(_fr_boss_art204_owner); // FRONTIER BOSS ART204 NATIVE START"), encoding="utf8")
        before = self.snapshot(self.project)
        with self.assertRaisesRegex(RuntimeError, "partially installed source callback"):
            self.apply()
        self.assertEqual(before, self.snapshot(self.project))

    def test_native_clear_preserves_original_guards_and_order(self):
        text = (self.project / "scripts/scrBossIntro/scrBossIntro.gml").read_text(encoding="utf8").replace("\r\n", "\n")
        result = hook.native_intro_transform(text)
        self.assertEqual(1, result.count(hook.INTRO_FIXED))
        self.assertLess(result.index(hook.INTRO_GUARD), result.index(hook.INTRO_FIXED))
        self.assertEqual(result, hook.native_intro_transform(result))
        self.assertEqual(text.replace(hook.INTRO_FIXED, hook.INTRO_ANCHOR).replace(hook.INTRO_LEGACY_FIXED, hook.INTRO_ANCHOR),
                         result.replace(hook.INTRO_FIXED, hook.INTRO_ANCHOR))

    def test_old_native_clear_upgrades_to_owned_art_restoration(self):
        text = (self.project / "scripts/scrBossIntro/scrBossIntro.gml").read_text(encoding="utf8").replace("\r\n", "\n")
        text = text.replace(hook.INTRO_FIXED, hook.INTRO_ANCHOR).replace(hook.INTRO_LEGACY_FIXED, hook.INTRO_ANCHOR)
        old = text.replace(hook.INTRO_ANCHOR, hook.INTRO_LEGACY_FIXED)
        result = hook.native_intro_transform(old)
        self.assertEqual(1, result.count("scrFRBossArt204NativeStart()"))
        self.assertNotIn(hook.INTRO_LEGACY_FIXED, result)
        self.assertLess(result.index(hook.INTRO_GUARD), result.index(hook.INTRO_FIXED))

    def test_rejected_source_callback_cleanup_cannot_restore_live_art(self):
        result = hook.callback_transform((self.project / self.callback).read_text(encoding="utf8"))
        self.assertEqual(1, result.count(hook.SOURCE_GUARD_FIXED))
        self.assertLess(result.index("scrFRBossArt204IntroPrepare("), result.index("scrFRBossArt204Replace("))
        self.assertLess(result.index("if(!fr_boss_art204_prepared)"), result.index("scrFRSpriteRestore("))
        self.assertEqual(1, result.count("fr_boss_art204_prepared=false;"))


if __name__ == "__main__":
    unittest.main()
