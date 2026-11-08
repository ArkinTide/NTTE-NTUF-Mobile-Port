"""Real-map acceptance instrumentation must keep ordinary Bullet1 dispatch."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest

import fr_biome_clearance204_map_hooks as hook

ROOT = Path(__file__).resolve().parents[1]


class BiomeClearance204MapTests(unittest.TestCase):
    def test_exact_hooks_are_idempotent(self):
        relatives = ['objects/Bullet1/Collision_hitme.gml',
                     'scripts/scrFrontier_tests/scrFrontier_tests.gml',
                     'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml']
        with TemporaryDirectory() as folder:
            project = Path(folder)
            for relative in relatives:
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / 'staging/project' / relative, target)
            self.assertEqual(hook.apply(project)['natural_maps'], 12)
            first = {str(p.relative_to(project)): p.read_bytes() for p in project.rglob('*.gml')}
            hook.apply(project)
            self.assertEqual(first, {str(p.relative_to(project)): p.read_bytes()
                                     for p in project.rglob('*.gml')})
            text = (project / relatives[0]).read_text('utf-8-sig')
            self.assertEqual(text.count('scr_projectile_generic_bullet_hit()'), 1)
            self.assertLess(text.index('scrFRBiomeClearance204MapBulletBefore'),
                            text.index('scr_projectile_generic_bullet_hit()'))
            self.assertGreater(text.index('scrFRBiomeClearance204MapBulletAfter'),
                               text.index('scr_projectile_generic_bullet_hit()'))
            self.assertEqual((project / relatives[1]).read_text('utf-8-sig').count(
                'if(fr_test_case=="biome-clearance204-maps")'), 1)


if __name__ == '__main__':
    unittest.main()
