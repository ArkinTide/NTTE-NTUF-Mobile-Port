from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest

import fr_pirate_visibility205_test_hooks as hook


class PirateVisibility205HookTests(unittest.TestCase):
    def test_opt_in_readonly_observer_installs_once(self):
        root = Path(__file__).resolve().parents[1]
        relatives = ['scripts/scrFrontier_tests/scrFrontier_tests.gml',
                     'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml',
                     'objects/hitme/Create_0.gml']
        with TemporaryDirectory() as folder:
            project = Path(folder)
            for relative in relatives:
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / 'staging/project' / relative, target)
            report = hook.apply(project)
            self.assertFalse(report['diagnostic_only'])
            first = {r: (project / r).read_bytes() for r in relatives}
            hook.apply(project)
            self.assertEqual(first, {r: (project / r).read_bytes() for r in relatives})
            birth = (project / relatives[2]).read_text('utf-8-sig')
            self.assertEqual(birth.count('scrFRPirateVisibility205Created(id);'), 1)
            self.assertIn('os_type==os_windows && scrNTTEFullSmokeEnabled()', birth)
            native = (root / 'native/pirate_visibility205_tests.gml').read_text('utf-8')
            self.assertNotIn('instance_destroy(', native)
            self.assertIn('_shot.damage=_a.hp+10000', native)
            self.assertIn('counted_hostile:', native)
            self.assertIn('top_owns_target:', native)
            self.assertIn('callstack:debug_get_callstack(99)', native)
            self.assertIn('_cluster.scheduled_bullet && !instance_exists(_cluster.actor.id)', native)
            self.assertIn('_final.natural.portals>0', native)


if __name__ == '__main__':
    unittest.main()
