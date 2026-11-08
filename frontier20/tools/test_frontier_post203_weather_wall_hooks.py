"""Check the narrow installer without changing an actual stage or old release."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest

import fr_post203_weather_wall_hooks as hook


ROOT = Path(__file__).resolve().parents[1]


class Post203WeatherWallInstallerTests(unittest.TestCase):
    def fixture(self, folder):
        project = Path(folder)
        source = ROOT / 'staging/project'
        module = next((source / 'scripts').glob('frCode_Frontier_Events_mod_*/*.gml'))
        relatives = [module.relative_to(source),
                     Path('scripts/scrNTTEFullFreakChamberNative/scrNTTEFullFreakChamberNative.gml'),
                     Path('scripts/scrFrontier_tests/scrFrontier_tests.gml'),
                     Path('scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml')]
        for relative in relatives:
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, target)
        # The integration stage may already contain this installer. Normalize
        # only these temporary copies so mutation tests always start from the
        # pre-install anchors, independently of the parent's latest stage.
        for target, replacements in (
            (project / relatives[0], [(hook.OUTER_AFTER, hook.OUTER_BEFORE)]),
            (project / relatives[1], [(hook.TRANSITION_AFTER, hook.TRANSITION_BEFORE),
                                     (hook.TOP_AFTER, hook.TOP_BEFORE)]),
        ):
            text = target.read_text('utf-8-sig')
            for after, before in replacements:
                if after in text:
                    self.assertEqual(text.count(after), 1)
                    text = text.replace(after, before, 1)
                self.assertEqual(text.count(before), 1)
            target.write_text(text, 'utf-8')
        return project, project / relatives[0], project / relatives[1]

    def snapshot(self, project):
        return {str(p.relative_to(project)): p.read_bytes() for p in project.rglob('*.gml')}

    def test_actual_stage_and_repeat_install(self):
        with TemporaryDirectory() as folder:
            project, events, chambers = self.fixture(folder)
            report = hook.apply(project)
            self.assertEqual(report['native_case'], 'FrontierPost203WeatherWallTests')
            self.assertEqual(events.read_text('utf-8').count(hook.OUTER_AFTER), 1)
            self.assertIn(hook.TRANSITION_AFTER, chambers.read_text('utf-8'))
            self.assertIn(hook.TOP_AFTER, chambers.read_text('utf-8'))
            first = self.snapshot(project)
            hook.apply(project)
            self.assertEqual(first, self.snapshot(project))

    def test_changed_chamber_anchor_is_transactional(self):
        with TemporaryDirectory() as folder:
            project, events, chambers = self.fixture(folder)
            old = chambers.read_text('utf-8-sig')
            chambers.write_text(old.replace(hook.TOP_BEFORE, hook.TOP_BEFORE.replace('_top.x', '_top.other_x')), 'utf-8')
            before = self.snapshot(project)
            with self.assertRaisesRegex(RuntimeError, 'sliding top'):
                hook.apply(project)
            self.assertEqual(before, self.snapshot(project))

    def test_duplicate_outer_anchor_is_rejected(self):
        with TemporaryDirectory() as folder:
            project, events, chambers = self.fixture(folder)
            events.write_text(events.read_text('utf-8-sig') + '\n' + hook.OUTER_BEFORE, 'utf-8')
            before = self.snapshot(project)
            with self.assertRaisesRegex(RuntimeError, 'Blizzard outer mask'):
                hook.apply(project)
            self.assertEqual(before, self.snapshot(project))

    def test_duplicate_installed_style_anchor_is_rejected(self):
        with TemporaryDirectory() as folder:
            project, events, chambers = self.fixture(folder)
            hook.apply(project)
            chambers.write_text(chambers.read_text('utf-8') + '\n' + hook.TRANSITION_AFTER, 'utf-8')
            before = self.snapshot(project)
            with self.assertRaisesRegex(RuntimeError, 'duplicate anchor: chamber edge'):
                hook.apply(project)
            self.assertEqual(before, self.snapshot(project))

    def test_blizzard_border_overlap_is_inside_opaque_source_pixels(self):
        # The inset must never replace visible gradient pixels. Check the
        # actual source alpha around every pixel affected by the 2px overlap.
        from PIL import Image
        image = Image.open(ROOT / 'original/Frontier/Sprites/Particles/sprVignette.png').convert('RGBA')
        alpha = image.getchannel('A')
        self.assertEqual(image.size, (500, 500))
        # The smallest supported radius (0.6) produces the largest source inset.
        for x in range(495, 500):
            self.assertEqual(alpha.crop((x, 0, x + 1, 500)).getextrema(), (255, 255))
            self.assertEqual(alpha.crop((499 - x, 0, 500 - x, 500)).getextrema(), (255, 255))
        for y in range(495, 500):
            self.assertEqual(alpha.crop((0, y, 500, y + 1)).getextrema(), (255, 255))
            self.assertEqual(alpha.crop((0, 499 - y, 500, 500 - y)).getextrema(), (255, 255))


if __name__ == '__main__':
    unittest.main()
