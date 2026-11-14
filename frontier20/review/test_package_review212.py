"""Current independent package/font reviewers stay inert and reject stale scope."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def load(name):
    path = HERE / (name + ".py")
    spec = importlib.util.spec_from_file_location("ntuf212_test_" + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PackageReview212Tests(unittest.TestCase):
    def test_import_does_not_execute_build_network_or_historical_gate(self):
        with patch("subprocess.run", side_effect=AssertionError("Unexpected process")), \
                patch("subprocess.check_output", side_effect=AssertionError("Unexpected process")):
            inspector = load("inspect_release212_packages")
            font = load("verify_release212_debug_font")
        self.assertEqual((inspector.VERSION, inspector.INTERNAL), ("2.1.2", 107))
        self.assertEqual(inspector.HOST, inspector.ROOT.parent / "ntte-complete")
        self.assertEqual(inspector.BASE_IPA, inspector.WORKSPACE / "outputs/NuclearThroneIOS.ipa")
        self.assertEqual(font.HOST, inspector.HOST)
        self.assertEqual(font.OUTPUT.name, "dbg-font-full-range-coverage-212.json")
        self.assertNotIn("main", inspector.REUSED)
        self.assertNotIn("delivery_cases", inspector.REUSED)
        self.assertEqual(inspector.package_path("Android").name, "NuclearThrone.NTTE-NTUF-Android-2.1.2.apk")

    def test_binary_reader_has_no_historical_acceptance_or_globals(self):
        module = load("inspect_release212_packages")
        with patch("subprocess.run", side_effect=AssertionError("Reader executed process")):
            reader = module.reader()
        self.assertEqual(reader.ROOT, module.ROOT)
        self.assertTrue(callable(reader.VM))
        for name in ("main", "package", "EXPECTED_VM", "OLD_PACKAGES", "RELEASE", "android_native"):
            self.assertFalse(hasattr(reader, name), name)

    def test_current_selector_requires_ready_212_21_case_identity(self):
        module = load("inspect_release212_packages")
        source = (module.ROOT / "tools/release212_delivery.py").read_text("utf8")
        selection = module.read(module.SELECTION)
        selection["status"] = "READY"
        self.assertEqual(len(module.delivery_cases(source, selection)), 21)
        for key, value in (("version", "2.1.1"), ("internal", 106), ("status", "DRAFT")):
            wrong = dict(selection, **{key: value})
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                module.delivery_cases(source, wrong)
        for altered in (source.replace("FINAL_CASES=selected_cases()", "FINAL_CASES=selected_cases(1)"),
                        source.replace("selection=read(CASE_SELECTION)", "selection=untrusted_load(CASE_SELECTION)")):
            self.assertNotEqual(altered, source)
            with self.assertRaises(RuntimeError):
                module.delivery_cases(altered, selection)
        duplicate = dict(selection, cases=selection["cases"][:-1] + [selection["cases"][0]])
        with self.assertRaises(RuntimeError):
            module.delivery_cases(source, duplicate)

    def test_missing_real_packages_cannot_write_audit(self):
        module = load("inspect_release212_packages")
        with TemporaryDirectory() as temporary:
            module.RELEASE = Path(temporary) / "unbuilt-release"
            module.OUTPUT = Path(temporary) / "audit.json"
            with self.assertRaisesRegex(RuntimeError, "not complete"):
                module.audit()
            self.assertFalse(module.OUTPUT.exists())

    def test_resolved_evidence_cannot_escape_scoped_root(self):
        module = load("inspect_release212_packages")
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            for value in ("../escape.json", "/escape.json", "folder\\escape.json"):
                with self.subTest(value=value), self.assertRaises(RuntimeError):
                    module.child(root, value)


if __name__ == "__main__":
    unittest.main()
