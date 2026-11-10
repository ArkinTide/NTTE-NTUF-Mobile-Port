"""Narrow Visual205 hooks and original-alpha asset derivation in scratch copies."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from PIL import Image, ImageChops

from fr_gml_frontend import tokenize
from fr_visual205_hooks import ROOT, SITES, apply
from generate_frontier_menu_art import LOCKED_SHAPE, RESOURCE, SOURCE, TEMPLATE, generate


class Visual205Tests(unittest.TestCase):
    def fixture(self, project):
        """Back out this installer only; keep every other current staging hook."""
        paths = dict.fromkeys(relative for relative, _, _ in SITES)
        for relative in paths:
            text = (ROOT / 'staging/project' / relative).read_text('utf8')
            for site, before, after in reversed(SITES):
                if site == relative and after in text:
                    self.assertEqual(text.count(after), 1)
                    text = text.replace(after, before, 1)
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, 'utf8')
        identity = project / 'unchanged.yyp'
        identity.write_text('{"resources":["stable"]}', 'utf8')
        ledger = project / 'identity-ledger.json'
        ledger.write_text('{"stable":205}', 'utf8')
        return {identity: identity.read_bytes(), ledger: ledger.read_bytes()}

    def test_install_is_exact_idempotent_and_keeps_identity(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            protected = self.fixture(project)
            report = apply(project, crown=False)
            self.assertEqual(len(report['files_changed']), 8)
            self.assertFalse(report['public_test_entry_changed'])
            self.assertEqual(report['native_registration']['visual205.gml'], 'scrFrontier_visual205')
            before = {path: path.read_bytes() for path in project.rglob('*') if path.is_file()}
            for _ in range(3):
                self.assertEqual(apply(project, crown=False)['files_changed'], [])
                self.assertEqual(before, {path: path.read_bytes() for path in project.rglob('*') if path.is_file()})
            for path, contents in protected.items():
                self.assertEqual(path.read_bytes(), contents)
            for relative, _, after in SITES:
                self.assertEqual((project / relative).read_text('utf8').count(after), 1)
            outline = (project / 'scripts/scrNTTEFullOutlineOptionsNative/scrNTTEFullOutlineOptionsNative.gml').read_text('utf8')
            staged = (ROOT / 'staging/project/scripts/scrNTTEFullOutlineOptionsNative/scrNTTEFullOutlineOptionsNative.gml').read_text('utf8')
            self.assertEqual(outline, staged)

    def test_missing_anchor_preflight_writes_nothing(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            self.fixture(project)
            relative, before, _ = SITES[-1]
            path = project / relative
            path.write_text(path.read_text('utf8').replace(before, 'changed upstream anchor', 1), 'utf8')
            originals = {path: path.read_bytes() for path in project.rglob('*') if path.is_file()}
            with self.assertRaisesRegex(RuntimeError, 'changed or ambiguous anchor'):
                apply(project, crown=False)
            self.assertEqual(originals, {path: path.read_bytes() for path in project.rglob('*') if path.is_file()})

    def test_original_alpha_silhouette_and_unchanged_unlocked_frame(self):
        metadata = json.loads((TEMPLATE / (RESOURCE + '.yy')).read_text('utf8'))
        with TemporaryDirectory() as directory:
            output = Path(directory)
            generate(output=output)
            generate(output=output, check=True)
            locked = Image.open(output / (metadata['frames'][1]['name'] + '.png')).convert('RGBA')
            expected_alpha = Image.open(LOCKED_SHAPE).getchannel('A').resize((32, 32), Image.Resampling.NEAREST)
            self.assertIsNone(ImageChops.difference(locked.getchannel('A'), expected_alpha).getbbox())
            self.assertEqual(sum(value > 0 for value in expected_alpha.getdata()), 396)
            self.assertTrue(all(locked.getpixel(point)[3] == 0 for point in ((0, 0), (31, 0), (0, 31), (31, 31))))
            self.assertTrue(all(pixel[:3] == (66, 66, 66) for pixel in locked.getdata()))
            unlocked = Image.open(output / (metadata['frames'][0]['name'] + '.png')).convert('RGBA')
            source = Image.open(SOURCE).convert('RGBA')
            self.assertIsNone(ImageChops.difference(unlocked.crop((4, 0, 28, 32)), source).getbbox())
            self.assertEqual(unlocked.getchannel('A').crop((0, 0, 4, 32)).getbbox(), None)

    def test_native_sources_are_balanced_and_production_uses_no_test_override(self):
        for name in ('visual205.gml', 'visual205_tests.gml'):
            path = ROOT / 'native' / name
            stack = []
            for token in tokenize(path.read_text('utf8')):
                if token.text in ('(', '[', '{'):
                    stack.append(token.text)
                elif token.text in (')', ']', '}'):
                    self.assertTrue(stack, str(path))
                    self.assertEqual(stack.pop(), {')': '(', ']': '[', '}': '{'}[token.text])
            self.assertEqual(stack, [], str(path))
        production = (ROOT / 'native/visual205.gml').read_text('utf8')
        self.assertNotIn('SmokeEnabled', production)
        self.assertNotIn('Tests', production)
        self.assertNotIn('os_type', production)
        self.assertNotIn('event_perform', production)
        self.assertNotIn('gpu_set_fog(true', production)
        self.assertIn('gpu_set_colorwriteenable(true,true,true,false)', production)
        self.assertIn('my_player.color=global.player_color', production)
        self.assertIn('_owner==my_player', production)
        self.assertIn('render_parse_text(_message)', production)
        self.assertNotIn('string_upper(_text)', production)


if __name__ == '__main__':
    unittest.main()
