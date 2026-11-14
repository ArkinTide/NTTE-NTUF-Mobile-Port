import tempfile
import unittest
from pathlib import Path

import fr_red212_hooks as hooks


class Red212BoundaryTests(unittest.TestCase):
    def fixture(self, source):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        path = root / hooks.REL
        path.parent.mkdir(parents=True)
        path.write_text(source, encoding="utf-8")
        return root, path

    def test_exact_callback_only_and_idempotent(self):
        root, path = self.fixture("prefix\n" + hooks.BEFORE + "\nsuffix\n")
        hooks.apply(root)
        output = path.read_bytes()
        self.assertEqual(path.read_text(), "prefix\n" + hooks.AFTER + "\nsuffix\n")
        hooks.apply(root)
        self.assertEqual(path.read_bytes(), output)

    def test_drift_rejected_before_write(self):
        root, path = self.fixture("function scrNTTEFullRedPopulateNative() {scrPopulate();}")
        before = path.read_bytes()
        with self.assertRaises(RuntimeError):
            hooks.apply(root)
        self.assertEqual(path.read_bytes(), before)

    def test_current_generator_scope(self):
        self.assertIn("if(object_index==GenCont) safespawn=false;", hooks.AFTER)
        self.assertNotIn("with(GenCont)", hooks.AFTER)
        self.assertLess(hooks.AFTER.index("safespawn=false"), hooks.AFTER.index("scrPopulate();"))


if __name__ == "__main__":
    unittest.main()
