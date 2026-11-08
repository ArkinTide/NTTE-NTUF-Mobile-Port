from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fr_seal_audio_hooks import ANCHOR, MARKER, RELATIVE, REPLACEMENT, apply


SOURCE = '''function scrNTTEFullSealHeavyStep() {
if (current_frame_active) {
if (gunangle<abs(anchor_spin)) ''' + ANCHOR + '''
}
if(anchor_swap) snd_play(sndMeleeFlip);
}
'''


class SealAudioHookTests(unittest.TestCase):
    def fixture(self, root, source=SOURCE, bom=False, crlf=False):
        path = root / RELATIVE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + source.replace("\n", "\r\n" if crlf else "\n").encode())
        return path

    def test_one_swing_only_and_stable_restaging_with_original_encoding(self):
        for bom, crlf in ((False, False), (True, True)):
            with self.subTest(bom=bom), TemporaryDirectory() as temporary:
                root = Path(temporary)
                path = self.fixture(root, bom=bom, crlf=crlf)
                apply(root)
                after = path.read_bytes()
                self.assertEqual(after.startswith(b"\xef\xbb\xbf"), bom)
                self.assertEqual(b"\r\n" in after, crlf)
                self.assertEqual(after.decode("utf-8-sig").count(REPLACEMENT), 1)
                self.assertIn('if(anchor_swap) snd_play(sndMeleeFlip);', after.decode("utf-8-sig"))
                self.assertIn('if (gunangle<abs(anchor_spin))', after.decode("utf-8-sig"))
                for _ in range(3):
                    apply(root)
                    self.assertEqual(path.read_bytes(), after)

    def test_changed_duplicate_and_partial_source_rejected_without_write(self):
        for source in (SOURCE.replace(ANCHOR, 'snd_play(sndMeleeFlip,1,8)'),
                       SOURCE + SOURCE, SOURCE + MARKER,
                       SOURCE.replace(ANCHOR, REPLACEMENT) + ANCHOR,
                       SOURCE.replace(ANCHOR, REPLACEMENT + REPLACEMENT)):
            with self.subTest(source=source[:50]), TemporaryDirectory() as temporary:
                root = Path(temporary)
                path = self.fixture(root, source)
                before = path.read_bytes()
                with self.assertRaises(RuntimeError):
                    apply(root)
                self.assertEqual(before, path.read_bytes())


if __name__ == "__main__":
    unittest.main()
