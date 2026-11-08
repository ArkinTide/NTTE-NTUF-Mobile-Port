"""Check the Heart-only hook boundary, byte-stable restaging and fail-closed edits."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fr_orb_wall_hooks import (ANCHOR, RELATIVE, TOP_RELATIVE, TOP_ANCHOR, TOP_REPLACEMENT,
                               MERGE_RELATIVE, MERGE_ANCHOR, MERGE_REPLACEMENT, apply)


class OrbWallInstallerTests(unittest.TestCase):
    def fixture(self, directory, source):
        root = Path(directory)
        path = root / RELATIVE
        path.parent.mkdir(parents=True)
        path.write_bytes(source)
        newline = '\r\n' if b'\r\n' in source else '\n'
        bom = b'\xef\xbb\xbf' if source.startswith(b'\xef\xbb\xbf') else b''
        for relative, text in ((TOP_RELATIVE,
                                'if (' + TOP_ANCHOR + ' || position_meeting(x, y, Floor)) {\n'
                                '    instance_destroy();exit;\n}\n'),
                               (MERGE_RELATIVE, 'with (_new) { ' + MERGE_ANCHOR + ' }\n')):
            other = root / relative
            other.parent.mkdir(parents=True, exist_ok=True)
            other.write_bytes(bom + text.replace('\n', newline).encode())
        return root, path

    def test_hook_runs_after_decoration_before_reveal_and_restages_exactly(self):
        source = ('function scrNTTEFullCrystalHeartBulletDestroy() {\n'
                  '    var _generation=actual_native_generation();\n'
                  '    for(var _i=0;_i<4;++_i) instance_create(x,y,Top)\n'
                  + ANCHOR + '\n    show_reveal(_reveal);\n}\n'
                  'function unrelated() { instance_create(x,y,Top) }\n')
        for newline, bom in (("\n", b""), ("\r\n", b"\xef\xbb\xbf")):
            with self.subTest(newline=newline), TemporaryDirectory() as directory:
                root, path = self.fixture(directory, bom + source.replace('\n', newline).encode())
                report = apply(root)
                result = path.read_bytes()
                self.assertEqual(report['file'], RELATIVE)
                text = result.decode('utf-8-sig').replace('\r\n', '\n')
                self.assertLess(text.index('for(var _i'), text.index('scrFROrbWallPruneTops'))
                self.assertLess(text.index('scrFROrbWallPruneTops'), text.index(ANCHOR))
                self.assertTrue(text.endswith('function unrelated() { instance_create(x,y,Top) }\n'))
                self.assertEqual(result.startswith(b'\xef\xbb\xbf'), bool(bom))
                self.assertEqual(result.count(b'scrFROrbWallPruneTops(_generation);'), 1)
                top = (root / TOP_RELATIVE).read_text('utf-8-sig')
                merge = (root / MERGE_RELATIVE).read_text('utf-8-sig')
                self.assertIn(TOP_REPLACEMENT, top)
                self.assertIn('position_meeting(x, y, Floor)', top)
                self.assertIn(MERGE_REPLACEMENT, merge)
                once = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*.gml')}
                apply(root)
                self.assertEqual(once, {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*.gml')})

    def test_changed_duplicate_or_partial_markers_do_not_write(self):
        for source in (ANCHOR.replace('var _reveal', 'var _different'),
                       ANCHOR + '\n' + ANCHOR,
                       '// BEGIN FRONTIER HEART AUTHORED EDGE TOPS\n' + ANCHOR,
                       ANCHOR + '\n// END FRONTIER HEART AUTHORED EDGE TOPS'):
            with self.subTest(source=source), TemporaryDirectory() as directory:
                root, path = self.fixture(directory, source.encode())
                original = path.read_bytes()
                with self.assertRaises(AssertionError):
                    apply(root)
                self.assertEqual(original, path.read_bytes())

    def test_layout_and_merge_changed_duplicate_or_partial_hooks_are_transactional(self):
        cases = ((TOP_RELATIVE, TOP_ANCHOR, TOP_REPLACEMENT, '/* FRONTIER PACKED CAP LAYOUT */'),
                 (MERGE_RELATIVE, MERGE_ANCHOR, MERGE_REPLACEMENT, '/* FRONTIER PACKED CAP MERGE */'))
        for relative, anchor, replacement, marker in cases:
            for kind in ('changed', 'duplicate', 'partial', 'installed-and-original'):
                with self.subTest(relative=relative, kind=kind), TemporaryDirectory() as directory:
                    root, _ = self.fixture(directory, (ANCHOR + '\n').encode())
                    target = root / relative
                    source = target.read_text('utf-8')
                    if kind == 'changed':
                        source = source.replace(anchor, anchor.replace('Wall', 'Floor').replace('_old_list', '_other_list'))
                    elif kind == 'duplicate':
                        source += '\n' + anchor
                    elif kind == 'partial':
                        source += '\n' + marker
                    else:
                        source = source.replace(anchor, replacement) + '\n' + anchor
                    target.write_text(source, 'utf-8')
                    once = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*.gml')}
                    with self.assertRaises(AssertionError):
                        apply(root)
                    self.assertEqual(once, {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*.gml')})


if __name__ == '__main__':
    unittest.main()
