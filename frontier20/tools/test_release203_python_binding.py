"""Reject stale or incomplete passing Python evidence before packaging."""
from pathlib import Path
import hashlib
import importlib.util
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("post202_binding_review", ROOT / "review/verify_post202_repairs.py")
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


class PythonSourceBinding(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name in ("tools/check.py", "native/actor.gml"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("original", encoding="utf8")
        self.evidence = {"source_inputs_unchanged": True, "source_inputs": {
            name: hashlib.sha256(b"original").hexdigest()
            for name in ("tools/check.py", "native/actor.gml")}}

    def verify(self):
        with patch.object(REVIEW, "ROOT", self.root):
            return REVIEW.verify_python_sources(self.evidence)

    def test_exact_capture_is_accepted(self):
        self.assertEqual(self.verify(), self.evidence["source_inputs"])

    def test_changed_source_rejects_old_success(self):
        (self.root / "native/actor.gml").write_text("changed", encoding="utf8")
        with self.assertRaisesRegex(AssertionError, "does not match"):
            self.verify()

    def test_new_source_rejects_old_success(self):
        (self.root / "tools/new.py").write_text("new", encoding="utf8")
        with self.assertRaisesRegex(AssertionError, "does not match"):
            self.verify()

    def test_deleted_source_rejects_old_success(self):
        (self.root / "native/actor.gml").unlink()
        with self.assertRaisesRegex(AssertionError, "does not match"):
            self.verify()

    def test_capture_mutation_is_rejected(self):
        self.evidence["source_inputs_unchanged"] = False
        with self.assertRaisesRegex(AssertionError, "changed during"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
