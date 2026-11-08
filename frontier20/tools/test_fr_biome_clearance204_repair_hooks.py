"""The wakeup repair is exact, bounded and reproducible across staging."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest

import fr_biome_clearance204_repair_hooks as hook


ROOT = Path(__file__).resolve().parents[1]


class BiomeClearance204RepairTests(unittest.TestCase):
    def test_wake_and_collision_hooks_preserve_native_lifecycle(self):
        with TemporaryDirectory() as folder:
            project = Path(folder)
            relatives = ['objects/MeleeFake/Step_0.gml',
                         'objects/Bullet1/Collision_hitme.gml',
                         'scripts/scrFrontier_tests/scrFrontier_tests.gml',
                         'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml']
            for relative in relatives:
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / 'staging/project' / relative, target)
            report = hook.apply(project)
            self.assertTrue(report['dormant_replacement_own_top'])
            first = {str(p.relative_to(project)): p.read_bytes() for p in project.rglob('*.gml')}
            hook.apply(project)
            self.assertEqual(first, {str(p.relative_to(project)): p.read_bytes()
                                     for p in project.rglob('*.gml')})
            wake = (project / relatives[0]).read_text('utf-8-sig')
            self.assertEqual(wake.count('scrFRBiomeAwakenOwnTop(id,_awake);'), 1)
            self.assertLess(wake.index('_awake.team = team'), wake.index('scrFRBiomeAwakenOwnTop'))
            self.assertLess(wake.index('scrFRBiomeAwakenOwnTop'), wake.index('instance_destroy(id, false)'))
            self.assertEqual(wake.count('instance_create(x, y, _object)'), 1)
            collision = (project / relatives[1]).read_text('utf-8-sig')
            self.assertLess(collision.index('scrFRBiomeClearance204BulletBefore'),
                            collision.index('scr_projectile_generic_bullet_hit()'))
            self.assertGreater(collision.index('scrFRBiomeClearance204BulletAfter'),
                               collision.index('scr_projectile_generic_bullet_hit()'))
            self.assertEqual(collision.count('scr_projectile_generic_bullet_hit()'), 1)


if __name__ == '__main__':
    unittest.main()
