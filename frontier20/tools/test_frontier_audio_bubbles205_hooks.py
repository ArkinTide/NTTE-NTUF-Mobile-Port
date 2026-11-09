from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fr_audio_bubbles205_hooks import apply, hook_specs


class AudioBubbles205HookTests(unittest.TestCase):
    def fixture(self, root, *, tests=False, crlf=False, bom=False):
        grouped = {}
        for hook in hook_specs(tests=tests):
            grouped.setdefault(hook["path"], []).append(hook["anchor"])
        for name, anchors in grouped.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            text = "\nfixture_separation();\n".join(anchors) + "\n"
            path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.replace("\n", "\r\n" if crlf else "\n").encode())

    def test_exact_stable_install_and_opt_in_test_dispatch(self):
        for tests in (False, True):
            for crlf, bom in ((False, False), (True, True)):
                with self.subTest(tests=tests, crlf=crlf), TemporaryDirectory() as temporary:
                    root = Path(temporary)
                    self.fixture(root, tests=tests, crlf=crlf, bom=bom)
                    apply(root, tests=tests)
                    once = {p.relative_to(root): p.read_bytes() for p in root.rglob("*.gml")}
                    for _ in range(3):
                        apply(root, tests=tests)
                        self.assertEqual(once, {p.relative_to(root): p.read_bytes() for p in root.rglob("*.gml")})
                    for raw in once.values():
                        self.assertEqual(raw.startswith(b"\xef\xbb\xbf"), bom)
                        self.assertEqual(b"\r\n" in raw, crlf)
                    source = "\n".join(raw.decode("utf-8-sig") for raw in once.values())
                    self.assertNotIn("audio_stop_all", source)
                    self.assertEqual("FrontierContinueAudio205Tests" in source, tests)
                    self.assertEqual("FrontierBubblesAttack205Tests" in source, tests)

    def test_bad_late_boundary_leaves_every_source_unchanged(self):
        hooks = hook_specs(tests=True)
        for mode in ("missing", "duplicate", "partial"):
            with self.subTest(mode=mode), TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.fixture(root, tests=True)
                hook = hooks[-1]
                path = root / hook["path"]
                text = path.read_text("utf8")
                if mode == "missing":
                    text = text.replace(hook["anchor"], "changed_boundary();")
                elif mode == "duplicate":
                    text += hook["anchor"]
                else:
                    text += hook["marker"]
                path.write_text(text, "utf8")
                before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*.gml")}
                with self.assertRaises(RuntimeError):
                    apply(root, tests=True)
                self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob("*.gml")})

    def test_other_modules_can_share_dispatcher_anchors(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root, tests=True)
            apply(root, tests=True)
            for hook in hook_specs(tests=True):
                if "TEST DISPATCH" not in hook["marker"] and "SMOKE ENTRY" not in hook["marker"]:
                    continue
                path = root / hook["path"]
                text = path.read_text("utf8")
                text = text.replace(hook["anchor"], hook["anchor"] + "\nother_module();\n", 1)
                path.write_text(text, "utf8")
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*.gml")}
            apply(root, tests=True)
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob("*.gml")})


if __name__ == "__main__":
    unittest.main()
