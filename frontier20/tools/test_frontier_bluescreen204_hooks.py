"""Pending Robot death gate installs only at the native GameOver decision."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import fr_bluescreen204_hooks as hook
from fr_gml_frontend import tokenize


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "history/2.0-delivered-20261106/staging/project"


class Bluescreen204HookTests(unittest.TestCase):
    def test_frozen_consumer_is_the_only_edit_and_install_is_byte_stable(self):
        frozen = (FROZEN / hook.RELATIVE).read_text("utf-8-sig")
        for newline in ("\n", "\r\n"):
            for bom in (b"", b"\xef\xbb\xbf"):
                with self.subTest(newline=repr(newline), bom=bool(bom)), TemporaryDirectory() as temporary:
                    project = Path(temporary)
                    path = project / hook.RELATIVE
                    path.parent.mkdir(parents=True)
                    raw = bom + frozen.replace("\n", newline).encode("utf8")
                    path.write_bytes(raw)
                    sentinel = project / "objects/Player/Step_0.gml"
                    sentinel.parent.mkdir(parents=True)
                    sentinel.write_bytes(b"native_player_death();\r\n")
                    self.assertEqual(hook.apply(project)[0]["status"], "patched")
                    installed = path.read_bytes()
                    replacement = hook.REPLACEMENT.replace("\n", newline).encode("utf8")
                    self.assertEqual(installed.replace(replacement, hook.ANCHOR.encode(), 1), raw)
                    self.assertEqual(sentinel.read_bytes(), b"native_player_death();\r\n")
                    for _ in range(3):
                        self.assertEqual(hook.apply(project)[0]["status"], "already-applied")
                        self.assertEqual(path.read_bytes(), installed)

    def test_changed_duplicate_or_partial_gate_fails_without_writing(self):
        cases = ("native_other_gate();\n", hook.ANCHOR + "\n" + hook.ANCHOR,
                 hook.MARKER + "\n" + hook.ANCHOR,
                 hook.REPLACEMENT.replace("PendingAdmission204", "UnrelatedGate"),
                 hook.REPLACEMENT + "\n" + hook.REPLACEMENT,
                 hook.REPLACEMENT + "\n" + hook.ANCHOR)
        for text in cases:
            with self.subTest(text=text), TemporaryDirectory() as temporary:
                project = Path(temporary)
                path = project / hook.RELATIVE
                path.parent.mkdir(parents=True)
                original = text.encode("utf8")
                path.write_bytes(original)
                with self.assertRaisesRegex(RuntimeError, "Frontier bluescreen204"):
                    hook.apply(project)
                self.assertEqual(path.read_bytes(), original)

    def test_native_modules_have_balanced_tokens_and_no_test_override_in_production(self):
        for name in ("bluescreen204.gml", "bluescreen204_tests.gml"):
            source = (ROOT / "native" / name).read_text("utf8")
            stack = []
            for token in tokenize(source):
                if token.text in ("(", "[", "{"):
                    stack.append(token.text)
                elif token.text in (")", "]", "}"):
                    self.assertEqual(stack.pop(), {")": "(", "]": "[", "}": "{"}[token.text])
            self.assertEqual(stack, [])
        production = (ROOT / "native/bluescreen204.gml").read_text("utf8")
        for forbidden in ("os_type", "SmokeEnabled", "instance_create(", "instance_destroy(",
                          "scrFRBluescreenUITests", "cyberspace_revive(", "current_frame", "timer"):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
