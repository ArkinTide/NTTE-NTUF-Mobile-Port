"""Bounded Ultimate Quest exit hooks fail closed and preserve native consumers."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import fr_quest_portal204_hooks as hook


ROOT = Path(__file__).resolve().parents[1]


class QuestPortal204HookTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory(prefix="frontier-quest-portal204-")
        self.project = Path(self.temporary.name)
        self.originals = {}
        for relative, signature, _, _, before in hook.SITES:
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            source = ("function scrNTTEAllyPortalStep() {\n" if before else "") + signature + "\n    native_body();\n}\nfunction unrelated() {native_other();}\n"
            target.write_bytes(source.replace("\n", "\r\n").encode("utf8"))
            self.originals[relative] = target.read_bytes()
        self.unrelated = self.project / "objects/CrownPickup/Collision_Player.gml"
        self.unrelated.parent.mkdir(parents=True)
        self.unrelated.write_bytes(b"with(instance_create(x,y,Portal)) type=3;\r\n")

    def tearDown(self):
        self.temporary.cleanup()

    def snapshot(self):
        return {path.relative_to(self.project).as_posix(): path.read_bytes()
                for path in self.project.rglob("*") if path.is_file()}

    def test_exact_two_function_entries_preserve_native_bodies_and_explicit_exit(self):
        before = self.snapshot()
        report = hook.apply(self.project)
        self.assertEqual([row[0] for row in hook.SITES], report["changed_paths"])
        self.assertEqual(2, report["consumer_count"])
        self.assertEqual("NTTEFullLockedHugeQuestChest", report["owner"])
        self.assertEqual(before[self.unrelated.relative_to(self.project).as_posix()], self.unrelated.read_bytes())
        for relative, signature, guard, identity, before_guard in hook.SITES:
            source = (self.project / relative).read_text("utf8")
            self.assertEqual(1, source.count("scrFRQuestPortal204Blocked()"))
            marker = "    // BEGIN FRONTIER QUEST PORTAL204 " + identity + "\n" + guard
            self.assertIn(marker, source)
            self.assertLess(source.index(guard), source.index(signature)) if before_guard else self.assertLess(source.index(signature), source.index(guard))
            self.assertEqual(1, source.count("native_body();"))
            self.assertEqual(1, source.count("function unrelated() {native_other();}"))

    def test_apply_is_byte_idempotent(self):
        hook.apply(self.project)
        before = self.snapshot()
        self.assertEqual([], hook.apply(self.project)["changed_paths"])
        self.assertEqual(before, self.snapshot())

    def test_second_anchor_failure_preflights_before_first_script_write(self):
        relative = hook.SITES[1][0]
        (self.project / relative).write_bytes(b"function changed() {}\n")
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, "identity is ambiguous"):
            hook.apply(self.project)
        self.assertEqual(before, self.snapshot())

    def test_duplicate_function_entry_is_rejected_without_writes(self):
        relative, signature, _, _, _ = hook.SITES[0]
        target = self.project / relative
        target.write_text(target.read_text("utf8") + signature + "\n}\n", encoding="utf8")
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, "identity is ambiguous"):
            hook.apply(self.project)
        self.assertEqual(before, self.snapshot())

    def test_partial_duplicate_and_moved_markers_are_rejected(self):
        relative, signature, guard, identity, before = hook.SITES[0]
        target = self.project / relative
        pristine = target.read_bytes()
        installed = hook.transform(pristine.decode("utf8"), signature, guard, identity, before)
        variants = [
            installed.replace("    // END FRONTIER QUEST PORTAL204 " + identity + "\n", "", 1),
            installed + guard + "\n",
            installed.replace(signature + "\n", signature + "\n    native_before_guard();\n", 1),
        ]
        for variant in variants:
            with self.subTest(variant=variant):
                target.write_text(variant, encoding="utf8")
                before = self.snapshot()
                with self.assertRaisesRegex(RuntimeError, "partial, duplicated or moved"):
                    hook.apply(self.project)
                self.assertEqual(before, self.snapshot())
        target.write_bytes(pristine)

    def test_unowned_guard_is_rejected_without_writes(self):
        relative, _, guard, _, _ = hook.SITES[0]
        target = self.project / relative
        target.write_text(target.read_text("utf8") + guard + "\n", encoding="utf8")
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, "unowned guard"):
            hook.apply(self.project)
        self.assertEqual(before, self.snapshot())

    def test_readonly_recovery_probe_precedes_guard_and_both_hooks_reapply_cleanly(self):
        import fr_quest_portal204_test_hooks as test_hook
        relative, native_anchor, guard, _, _ = hook.SITES[1]
        target = self.project / relative
        pristine = target.read_text("utf8")
        source_entry = "function scrNTTEAllyPortalStep() {"
        probe = test_hook.call_block("    scrFRQuestPortal204RecoveryProbe();", "RECOVERY").rstrip("\n")
        after_probe = test_hook.replace_exact(pristine, source_entry, source_entry + "\n" + probe, "RECOVERY")
        target.write_text(after_probe, encoding="utf8")
        hook.apply(self.project)
        installed = target.read_text("utf8")
        self.assertLess(installed.index("scrFRQuestPortal204RecoveryProbe();"), installed.index(guard))
        self.assertLess(installed.index(guard), installed.index(native_anchor))
        repeated = test_hook.replace_exact(installed, source_entry, source_entry + "\n" + probe, "RECOVERY")
        self.assertEqual(installed, repeated)
        self.assertEqual([], hook.apply(self.project)["changed_paths"])

    def test_second_write_failure_rolls_back_both_original_byte_streams(self):
        before = self.snapshot()
        write_bytes = Path.write_bytes
        calls = [0]

        def fail_once(path, data):
            calls[0] += 1
            if calls[0] == 2:
                # Simulate a partial OS write before the raised error.
                write_bytes(path, data[:11])
                raise OSError("injected second write failure")
            return write_bytes(path, data)

        with patch.object(Path, "write_bytes", fail_once):
            with self.assertRaisesRegex(OSError, "injected second write failure"):
                hook.apply(self.project)
        self.assertEqual(before, self.snapshot())

    def test_live_activated_owner_excludes_dormant_chest_and_synthetic_enemies(self):
        source = (ROOT / "native/quest_portal204.gml").read_text("utf8")
        blocked = source.split("function scrFRQuestPortal204Blocked() {", 1)[1].split("function ", 1)[0]
        self.assertIn("return instance_exists(NTTEFullLockedHugeQuestChest)", blocked)
        self.assertIn("&& instance_exists(GameCont)", blocked)
        self.assertIn('scrNTTEFullValue(GameCont,"fr_quest_portal205_active",false)', blocked)
        self.assertNotIn("instance_create", blocked)
        self.assertNotIn("global.", source)
        self.assertNotIn("scr_check_enemies", source)
        self.assertNotIn("QuestFloorCont", source)
        activate = source.split("function scrFRQuestPortal205Activate() {", 1)[1].split("function ", 1)[0]
        self.assertIn("GameCont.fr_quest_portal205_active=true;", activate)
        self.assertIn("with(Portal) if(type==1 || type==2)", activate)
        self.assertIn("instance_create(x,y,PortalClear);", activate)
        self.assertNotIn("type==3", activate)
        release = source.split("function scrFRQuestPortal205Release() {", 1)[1].split("function ", 1)[0]
        self.assertIn("GameCont.fr_quest_portal205_active=false;", release)
        restore = source.split("function scrFRQuestPortal205RestoreChest(_chest) {", 1)[1]
        self.assertIn('!scrNTTEFullValue(GameCont,"fr_quest_portal205_active",false)', restore)
        self.assertIn("array_length(_held)>=4 || array_length(_back)>=4", restore)
        self.assertIn("_chest.is_unlockable=true;", restore)


if __name__ == "__main__":
    unittest.main()
