"""Keep the synchronous target background alive before authored area setup."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fr_area_hooks import _sync_background_before_setup


SOURCE = '''function scrNTTEFullAreaGenerateNative() {
    try {
        GameCont.area=_area; GameCont.subarea=_subarea; GameCont.loops=_loops
        global.ntte_full_sync_generation=true
        _generation=instance_create(0,0,GenCont)
        // Source setArea is independent of sync: false appends a submap only.
        // Store before setup/alarms; global sync is restored before Destroy.
        _generation.ntte_full_set_area=_set_area
        // The appended geometry must merge before a compact collar is
        // made. A temporary target collar can cover the entire old map.
        _generation.ntte_full_sync_compact_defer=true
        if(_set_area) with(_generation) scrFRContinueGenerationBegin(true);

        global.ntte_full_sync_generation=_old_sync
        if (!instance_exists(BackCont)) instance_create(0,0,BackCont)
        run_generation();
    } finally { restore_old_controllers(); }
    dispose_old_or_new_controllers(_set_area);
}
'''


class SyncBackgroundInstallerTests(unittest.TestCase):
    def test_setup_has_target_controller_and_restaging_is_exact(self):
        for newline, bom in (("\n", b""), ("\r\n", b"\xef\xbb\xbf")):
            with self.subTest(newline=newline), TemporaryDirectory() as directory:
                path = Path(directory) / "generation.gml"
                path.write_bytes(bom + SOURCE.replace("\n", newline).encode())
                report = []
                _sync_background_before_setup(path, report)
                result = path.read_bytes()
                source = result.decode("utf-8-sig")
                self.assertEqual(source.count("instance_create(0,0,BackCont)"), 1)
                self.assertLess(source.index("GameCont.area=_area"), source.index("instance_create(0,0,BackCont)"))
                self.assertLess(source.index("instance_create(0,0,BackCont)"), source.index("instance_create(0,0,GenCont)"))
                self.assertIn("finally { restore_old_controllers(); }", source)
                self.assertIn("dispose_old_or_new_controllers(_set_area);", source)
                _sync_background_before_setup(path, report)
                self.assertEqual(path.read_bytes(), result)
                self.assertEqual(report[-1]["status"], "already-applied")

    def test_changed_or_duplicate_boundary_fails_without_writing(self):
        for source in (SOURCE.replace("_generation=instance_create(0,0,GenCont)", "new_generation();"), SOURCE + SOURCE):
            with self.subTest(source=source[:70]), TemporaryDirectory() as directory:
                path = Path(directory) / "generation.gml"
                path.write_text(source, encoding="utf-8")
                original = path.read_bytes()
                with self.assertRaises(RuntimeError):
                    _sync_background_before_setup(path, [])
                self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
