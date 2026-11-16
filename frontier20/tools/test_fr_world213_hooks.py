"""Check exact world-consumer patching, repeat application and fail-closed writes."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import fr_world213_hooks as hook


class World213HooksTests(unittest.TestCase):
    def fixture(self, root, newline='\n', bom=b''):
        sources = {}
        for relative, before, _ in hook.SITES:
            sources.setdefault(relative, []).append(before)
        for relative, pieces in sources.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            source = '\n// unrelated preserved consumer\n'.join(pieces) + '\n'
            path.write_bytes(bom + source.replace('\n', newline).encode('utf8'))

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*.gml')}

    def test_apply_is_exact_byte_stable_and_preserves_format(self):
        for newline, bom in (('\n', b''), ('\r\n', b'\xef\xbb\xbf')):
            with self.subTest(newline=newline), TemporaryDirectory() as temp:
                root = Path(temp)
                self.fixture(root, newline, bom)
                report = hook.apply(root)
                self.assertEqual(len(report['changed_paths']), 7)
                once = self.snapshot(root)
                for relative, _, after in hook.SITES:
                    raw = once[relative]
                    self.assertEqual(raw.startswith(b'\xef\xbb\xbf'), bool(bom))
                    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
                    self.assertEqual(text.count(after), 1)
                self.assertEqual(hook.apply(root)['changed_paths'], [])
                self.assertEqual(self.snapshot(root), once)

    def test_changed_and_duplicate_late_anchor_write_nothing(self):
        for kind in ('changed', 'duplicate', 'installed-and-original'):
            with self.subTest(kind=kind), TemporaryDirectory() as temp:
                root = Path(temp)
                self.fixture(root)
                relative, before, after = hook.SITES[-1]
                path = root / relative
                source = path.read_text('utf8')
                if kind == 'changed':
                    source = source.replace(before, 'a different native call();')
                elif kind == 'duplicate':
                    source += before + '\n'
                else:
                    source = source.replace(before, after) + before + '\n'
                path.write_text(source, encoding='utf8')
                before_files = self.snapshot(root)
                with self.assertRaises(RuntimeError):
                    hook.apply(root)
                self.assertEqual(self.snapshot(root), before_files)


if __name__ == '__main__':
    unittest.main()
