"""Inert204 audit guards with no packages, Git, games or publisher execution."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location("guard_" + name, ROOT / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


SELECTION_SOURCE = '''def selected_cases():
    if not CASE_SELECTION.is_file():
        return ()
    selection = json.loads(CASE_SELECTION.read_text(encoding="utf-8-sig"))
    assert selection.get("version") == DISPLAY_VERSION and selection.get("internal") == INTERNAL
    cases = selection.get("cases", [])
    assert isinstance(cases, list) and all(isinstance(case, str) and re.fullmatch(r"[A-Za-z0-9_]+", case) for case in cases)
    assert len(cases) == len(set(cases)), "Duplicate native case"
    return tuple(cases)
FINAL_CASES = selected_cases()
'''


class ReviewerGuards204(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages = module("inspect_release204_packages")
        cls.source = module("review_release204_source")
        cls.capture = module("capture204_python")
        cls.font = module("verify_release204_debug_font")

    def plan(self, target, name, **changes):
        with patch.object(sys, "argv", [name]), patch.multiple(target, **changes), \
                patch.object(Path, "is_file", return_value=False), patch.object(Path, "exists", return_value=False):
            output = io.StringIO()
            with redirect_stdout(output):
                target.main()
        return json.loads(output.getvalue())

    def test_default_package_plan_cannot_enter_actual_audit(self):
        value = self.plan(self.packages, "inspect_release204_packages.py",
            read=lambda _: {"cases": ["FutureReviewedCase"]},
            preflight=lambda: self.fail("Actual audit entered"), reader=lambda: self.fail("Binary reader entered"))
        self.assertEqual((value["version"], value["internal"]), ("2.0.4", 100))
        self.assertEqual(value["status"], "NOT_REVIEWED")
        self.assertFalse(value["build_game_network_or_publication_performed"])

    def test_independent_semantic_scope_and_capture_catalogues_match_current_verifier(self):
        verifier = module("verify_post203_repairs")
        self.assertEqual(self.source.CURRENT204_SEMANTIC_CASES, verifier.CURRENT204_CASES)
        self.assertEqual(self.capture.REVIEW_INPUTS, self.source.PYTHON_REVIEW_INPUTS)
        self.assertEqual(self.capture.REVIEW_INPUTS, verifier.REVIEW_INPUTS)
        self.assertEqual(self.capture.REVIEW_TESTS, verifier.REVIEW_TESTS)
        self.assertLessEqual(verifier.REQUIRED204_CASES, set(self.source.FINAL_CASES))

    def test_default_source_plan_cannot_enter_review(self):
        value = self.plan(self.source, "review_release204_source.py",
                          review=lambda: self.fail("Actual source review entered"))
        self.assertEqual((value["version"], value["internal"]), ("2.0.4", 100))
        self.assertEqual(value["status"], "NOT_REVIEWED")
        self.assertFalse(value["git_or_network_mutated"])

    def test_default_debug_font_plan_cannot_enter_audit(self):
        value = self.plan(self.font, "verify_release204_debug_font.py",
                          audit=lambda: self.fail("Actual native inspection entered"))
        self.assertEqual(value["status"], "NOT_REVIEWED")
        self.assertFalse(value["game_build_or_network"])
        self.assertEqual(self.font.OUTPUT.name, "dbg-font-full-range-coverage-204.json")

    def test_dynamic_selection_is_read_statically_without_freezing_case_count(self):
        for reviewer in (self.packages, self.source):
            for cases in (["SelectedNativeCase"], ["SelectedNativeCase", "NewlyReviewedCase"]):
                with self.subTest(reviewer=reviewer.__name__, cases=cases):
                    self.assertEqual(reviewer.delivery_cases(SELECTION_SOURCE, {"cases": cases}), tuple(cases))

    def test_dynamic_selection_rejects_publisher_import_or_mutating_validator(self):
        for reviewer in (self.packages, self.source):
            for changed in (SELECTION_SOURCE.replace("FINAL_CASES = selected_cases()", "FINAL_CASES = run_publisher()"),
                            SELECTION_SOURCE.replace("return tuple(cases)", 'publish(); return tuple(cases)'),
                            SELECTION_SOURCE + "\nFINAL_CASES = selected_cases()\n"):
                with self.subTest(reviewer=reviewer.__name__), self.assertRaises((AssertionError, RuntimeError)):
                    reviewer.delivery_cases(changed, {"cases": ["SelectedNativeCase"]})

    def fixture(self):
        cases, pin = ["SelectedNativeCase"], "a" * 64
        plan = {"status": "READY", "version": "2.0.4", "internal": 100, "base_commit": self.source.BASE,
            "product": "ntuf204", "mobile_folder": "mobile-release204-20261108", "payload_folder": "ntuf204-src",
            "physical_device_tested": False, "persistent_menu_audio_noise": "unresolved", "invisible_enemies": "unverified",
            "selected_cases": cases, "reviewed_sha256": {key: pin for key in
                ("delivery_tool", "case_selection", "release_content", "release_notes", "acceptance_config", "review_verifier")}}
        def read(path):
            return {"PUBLICATION_PLAN.json": plan,
                "release204-cases.json": {"version": "2.0.4", "internal": 100, "cases": cases},
                "release204-config.json": {"status": "READY", "version": "2.0.4", "internal": 100},
                "RELEASE_CONTENT.json": {"status": "READY", "version": "2.0.4", "internal": 100}}[Path(path).name]
        return plan, {"read": read, "sha": lambda _: pin, "FINAL_CASES": tuple(cases)}

    def test_publication_binding_reads_all_six_pins_and_current_identity(self):
        plan, changes = self.fixture()
        with patch.multiple(self.source, **changes), patch.object(Path, "is_file", return_value=True), \
                patch.object(Path, "is_symlink", return_value=False), patch.object(Path, "read_text", return_value="2.0.4\nReviewed scope.\n"):
            self.assertEqual(self.source.publication_binding(), plan)

    def test_changed_acceptance_config_or_verifier_pin_rejects_before_git(self):
        for name in ("release204-config.json", "verify_post203_repairs.py"):
            _, changes = self.fixture()
            changes["sha"] = lambda path: "b" * 64 if Path(path).name == name else "a" * 64
            with self.subTest(name=name), patch.multiple(self.source, **changes), \
                    patch.object(Path, "is_file", return_value=True), patch.object(Path, "is_symlink", return_value=False), \
                    patch.object(self.source, "checkout_state", side_effect=AssertionError("Git entered")):
                with self.assertRaisesRegex(AssertionError, "acceptance_config|review_verifier"):
                    self.source.review()

    def test_draft_plan_rejects_before_git_or_packages(self):
        plan, changes = self.fixture()
        plan["status"] = "DRAFT"
        with patch.multiple(self.source, **changes), patch.object(Path, "is_file", return_value=True), \
                patch.object(Path, "is_symlink", return_value=False), \
                patch.object(self.source, "checkout_state", side_effect=AssertionError("Git entered")), \
                patch.object(self.source, "package_binding", side_effect=AssertionError("Packages entered")):
            with self.assertRaisesRegex(AssertionError, "DRAFT"):
                self.source.review()

    def test_aggregate_capture_is_one_inert_command_and_binds_its_review_modules(self):
        with patch.object(self.capture.subprocess, "run", side_effect=AssertionError("Subprocess entered")):
            command = self.capture.suite_command()
        self.assertEqual(command[1:3], ["-B", "-c"])
        compile(command[3], "aggregate204-guard", "exec")
        self.assertEqual(set(self.capture.REVIEW_INPUTS), set(self.source.PYTHON_REVIEW_INPUTS))
        self.assertTrue(set(self.capture.REVIEW_TESTS).issubset(self.capture.REVIEW_INPUTS))

    def test_current_review_reference_allowlist_and_publisher_tools_are_exact(self):
        self.assertTrue({"review/capture204_python.py", "review/test_release204_reviewers.py",
                        "review/verify_release204_debug_font.py"}.issubset(self.source.PUBLIC_REVIEW))
        self.assertIn("release203_delivery.py", self.source.OMIT_TOOLS)
        self.assertIn("release204_delivery.py", self.source.OMIT_TOOLS)
        self.assertEqual(set(self.source.PUBLICATION_TOOLS), {"prepare_source.py", "finalize_docs.py",
            "publication_adapter.py", "restore_source_inputs.py", "publication_plan.py"})


if __name__ == "__main__":
    unittest.main()
