"""Preflight every post203 consumer using copies of the maintained native stage."""
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from fr_post203_hooks import apply, specs


class Post203Hooks(unittest.TestCase):
    def fixture(self, destination, installed=False):
        stage = ROOT / "staging/project"
        paths = list(dict.fromkeys(path.relative_to(stage) for path, _, _ in specs(stage)))
        paths += [Path("scripts/scrFrontier_tests/scrFrontier_tests.gml"),
                  Path("scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml")]
        for relative in paths:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(stage / relative, target)
        if not installed:
            # Undo only the maintained hooks; all surrounding native source,
            # including unrelated marker blocks, remains the real consumer.
            for path, before, after in reversed(specs(destination)):
                source = path.read_text("utf-8-sig")
                self.assertEqual(1, source.count(after), str(path))
                path.write_text(source.replace(after, before, 1), "utf-8", newline="\n")
            for relative, label in [(paths[-2], "POST203 COMPAT DRIVER"),
                                    (paths[-1], "POST203 COMPAT ENTRY")]:
                path = destination / relative
                source = path.read_text("utf-8-sig")
                pattern = (r"^[ \t]*// BEGIN FRONTIER " + label + r"\r?\n.*?"
                           r"^[ \t]*// END FRONTIER " + label + r"(?:\r?\n|$)")
                source, count = re.subn(pattern, "", source, flags=re.M | re.S)
                self.assertEqual(1, count, label)
                path.write_text(source, "utf-8", newline="\n")
        return paths

    @staticmethod
    def snapshot(destination, paths):
        return {str(path): (destination / path).read_bytes() for path in paths}

    def test_real_source_install_and_byte_idempotence(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            paths = self.fixture(target)
            report = apply(target)
            self.assertEqual(["patched"] * 3, [entry["status"] for entry in report])
            once = self.snapshot(target, paths)
            report = apply(target)
            self.assertEqual(["already-applied"] * 3, [entry["status"] for entry in report])
            self.assertEqual(once, self.snapshot(target, paths))

    def test_all_missing_and_duplicate_anchor_failures_leave_every_consumer_intact(self):
        # Fail at each actual content and late driver/smoke boundary. Prior
        # planned replacements must never leak into the real target project.
        for index in range(5):
            for duplicate in (False, True):
                with self.subTest(anchor=index, duplicate=duplicate), tempfile.TemporaryDirectory() as temporary:
                    target = Path(temporary)
                    paths = self.fixture(target)
                    anchors = [(path, before) for path, before, _ in specs(target)] + [
                        (target / paths[-2], "function scrFRIntegrationTestStep() {"),
                        (target / paths[-1], '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))'),
                    ]
                    path, anchor = anchors[index]
                    source = path.read_text("utf-8-sig")
                    self.assertEqual(1, source.count(anchor))
                    path.write_text(source.replace(anchor, anchor + anchor if duplicate else "MISSING HOOK", 1),
                                    "utf-8", newline="\n")
                    before = self.snapshot(target, paths)
                    with self.assertRaises(AssertionError):
                        apply(target)
                    self.assertEqual(before, self.snapshot(target, paths))

    def test_duplicate_installed_content_is_rejected_atomically(self):
        for index in range(3):
            with self.subTest(content=index), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary)
                paths = self.fixture(target, installed=True)
                path, _, after = specs(target)[index]
                source = path.read_text("utf-8-sig")
                path.write_text(source + "\n" + after, "utf-8", newline="\n")
                before = self.snapshot(target, paths)
                with self.assertRaises(AssertionError):
                    apply(target)
                self.assertEqual(before, self.snapshot(target, paths))


if __name__ == "__main__":
    unittest.main()
