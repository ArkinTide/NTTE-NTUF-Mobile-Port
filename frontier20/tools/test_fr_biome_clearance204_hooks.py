"""The diagnostic installer must not install a production clearance bypass."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest

import fr_biome_clearance204_hooks as hook


ROOT = Path(__file__).resolve().parents[1]


class BiomeClearance204DiagnosticTests(unittest.TestCase):
    def test_entry_only_and_idempotent(self):
        with TemporaryDirectory() as folder:
            project = Path(folder)
            relatives = [Path('scripts/scrFrontier_tests/scrFrontier_tests.gml'),
                         Path('scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml')]
            for relative in relatives:
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / 'staging/project' / relative, target)
            report = hook.apply(project)
            self.assertTrue(report['diagnostic_only'])
            first = {str(p.relative_to(project)): p.read_bytes() for p in project.rglob('*.gml')}
            hook.apply(project)
            self.assertEqual(first, {str(p.relative_to(project)): p.read_bytes()
                                     for p in project.rglob('*.gml')})
            self.assertEqual(set(first), {str(p) for p in relatives})
            driver = (project / relatives[0]).read_text('utf-8-sig')
            self.assertEqual(driver.count('if(fr_test_case=="biome-clearance204")'), 1)
            self.assertNotIn('scrFRBiomeClearance204TestsStep',
                             (project / relatives[1]).read_text('utf-8-sig'))


if __name__ == '__main__':
    unittest.main()
