"""Check touch event hook boundaries and install encoding on copies only."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import fr_movement214_hooks as hooks


ROOT = Path(__file__).resolve().parents[1]


class Movement214HooksTests(unittest.TestCase):
    def test_current_event_is_reviewed_input_or_hook(self):
        source = (ROOT / 'staging/project/objects/JoystickMove/Other_10.gml').read_text('utf-8-sig')
        self.assertEqual(hooks.NEW, hooks.transform(source))

    def test_hook_preserves_editor_keyboard_and_gamepad_gates(self):
        transformed = hooks.transform(hooks.OLD)
        self.assertTrue(transformed.startswith('event_inherited()\n'))
        self.assertIn('if instance_exists(MenuOptions) or UberCont.opt_keyboard or UberCont.opt_gamepad\n\texit', transformed)
        self.assertEqual(1, transformed.count('scrFRMovementStick214();'))
        self.assertEqual(transformed, hooks.transform(transformed))

    def test_unreviewed_source_is_rejected_without_partial_rewrite(self):
        for source in (hooks.OLD.replace('KeyCont.moving[global.index] = 0', 'new_input();'),
                       hooks.NEW + 'unexpected_input();\n', hooks.OLD + hooks.NEW):
            with self.assertRaises(RuntimeError):
                hooks.transform(source)

    def test_copy_install_preserves_newlines_and_bom(self):
        for bom in (b'', b'\xef\xbb\xbf'):
            for newline in ('\n', '\r\n'):
                with self.subTest(bom=bool(bom), newline=newline), TemporaryDirectory() as folder:
                    project = Path(folder)
                    path = project / 'objects/JoystickMove/Other_10.gml'
                    path.parent.mkdir(parents=True)
                    path.write_bytes(bom + hooks.OLD.replace('\n', newline).encode('utf8'))
                    hooks.apply(project)
                    after = path.read_bytes()
                    self.assertEqual(bom + hooks.NEW.replace('\n', newline).encode('utf8'), after)
                    hooks.apply(project)
                    self.assertEqual(after, path.read_bytes())


if __name__ == '__main__':
    unittest.main()
