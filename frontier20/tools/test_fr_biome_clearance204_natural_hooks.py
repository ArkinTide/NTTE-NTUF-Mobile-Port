"""Read-only provenance stays dormant outside its explicit smoke driver."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest

import fr_biome_clearance204_natural_hooks as hook

ROOT = Path(__file__).resolve().parents[1]


class BiomeClearance204NaturalTests(unittest.TestCase):
    def test_provenance_installation_is_idempotent(self):
        relatives = ['scripts/scrFrontier_tests/scrFrontier_tests.gml',
                     'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml',
                     'scripts/scrNTTEFullPalankingToss/scrNTTEFullPalankingToss.gml',
                     'scripts/scrNTTEFullTop/scrNTTEFullTop.gml']
        relatives += [f'objects/{name}/Create_0.gml' for name in
                      ['Gator', 'BuffGator', 'NTTEBabyGator', 'FRCustomEnemy',
                       'NTTEFullTopObject', 'NTTEFullPalankingToss']]
        with TemporaryDirectory() as folder:
            project = Path(folder)
            for relative in relatives:
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / 'staging/project' / relative, target)
            hook.apply(project)
            first = {str(p.relative_to(project)): p.read_bytes() for p in project.rglob('*.gml')}
            hook.apply(project)
            self.assertEqual(first, {str(p.relative_to(project)): p.read_bytes()
                                     for p in project.rglob('*.gml')})
            for relative in relatives:
                text = (project / relative).read_text('utf-8-sig')
                self.assertIn('scrNTTEFullSmokeEnabled()', text)
            for relative in relatives[4:]:
                text = (project / relative).read_text('utf-8-sig')
                self.assertEqual(text.count('scrFRBiomeClearance204NaturalCreated(id);'), 1)


if __name__ == '__main__':
    unittest.main()
