"""Exercise the production clone hook against the real native stage source."""
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from fr_enemy_visibility_hooks import apply


class EnemyVisibilityHooks(unittest.TestCase):
    def test_real_native_clone_path_anchor_and_idempotence(self):
        paths = [
            "objects/Bullet1/Collision_hitme.gml",
            "scripts/scrNTTEFullCrystalCloneNative/scrNTTEFullCrystalCloneNative.gml",
            "scripts/scrFrontier_tests/scrFrontier_tests.gml",
            "scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml",
        ]
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            for relative in paths:
                source = ROOT / "staging/project" / relative
                self.assertTrue(source.is_file(), f"Real native hook source missing: {source}")
                destination = target / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
            apply(target)
            once = {path: (target / path).read_bytes() for path in paths}
            apply(target)
            self.assertEqual(once, {path: (target / path).read_bytes() for path in paths})
            clone = (target / paths[1]).read_text(encoding="utf-8-sig")
            self.assertEqual(1, clone.count("scrFREnemyCloneOwnTop(_source,target);"))
            self.assertEqual(1, clone.count("scrFREnemyCloneOwnToss(_source,target);"))
            self.assertLess(clone.index("scrFREnemyCloneOwnTop(_source,target);"),
                            clone.index("scrNTTEFullCrystalCloneEffect(x,y,target.x,target.y)"))
            self.assertLess(clone.index("scrFREnemyCloneOwnToss(_source,target);"),
                            clone.index("scrNTTEFullCrystalCloneEffect(x,y,target.x,target.y)"))


if __name__ == "__main__":
    unittest.main()
