"""GML treats an undeclared harness function as a late instance-field lookup.

Keep registered regression drivers bound to real maintained functions; Igor
alone does not reject a lost entry point when one test file is replaced.
"""
from pathlib import Path
import re
import tempfile
import unittest

import fr_audio_bubbles205_hooks


ROOT = Path(__file__).resolve().parents[1]


def dispatch_block(source, case):
    """Read a real case body, ignoring braces inside GML strings/comments."""
    match = re.search(r'if\s*\(\s*fr_test_case\s*==\s*"' + re.escape(case) + r'"\s*\)\s*\{', source)
    if not match:
        return ""
    masked = re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/',
                    lambda token: " " * len(token.group()), source, flags=re.S)
    start = match.end() - 1
    depth = 0
    for index in range(start, len(source)):
        depth += (masked[index] == "{") - (masked[index] == "}")
        if depth == 0:
            return source[start + 1:index]
    raise AssertionError("Unclosed native test dispatch: " + case)


class FrontierNativeTestEntrypoints(unittest.TestCase):
    def test_registered_test_functions_are_maintained(self):
        declarations = set()
        for path in (ROOT / "native").glob("*.gml"):
            declarations.update(re.findall(r"\bfunction\s+(\w+)\s*\(",
                                           path.read_text(encoding="utf-8-sig")))
        drivers = [ROOT / "native/tests.gml", *sorted((ROOT / "tools").glob("fr_*hooks.py"))]
        references = {}
        for path in drivers:
            for function in re.findall(r"\b(scrFR\w*Tests(?:Start|Step)?)\s*\(",
                                       path.read_text(encoding="utf-8-sig")):
                references.setdefault(function, []).append(path.name)
        self.assertGreater(len(references), 30, "No regression driver registrations were inspected")
        missing = {function: paths for function, paths in references.items()
                   if function not in declarations}
        self.assertEqual({}, missing, f"Registered native test functions are missing: {missing}")

    def assert_bubbles212_dispatch(self, source):
        body = dispatch_block(source, "bubbles_attack212")
        self.assertTrue(body, "Bubbles212 smoke entry has no integration dispatch")
        self.assertIn('variable_instance_exists(id,"fr_bubbles_attack212")', body)
        self.assertRegex(body, r'\bscrFRBubblesAttack212TestsStart\(id\)')
        self.assertRegex(body, r'\bif\(scrFRBubblesAttack212TestsStep\(id\)\)')
        self.assertIn("game_end()", body)
        return body

    def test_bubbles212_smoke_reaches_real_start_step_and_input(self):
        project = ROOT / "staging/project"
        smoke = (project / "scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml").read_text("utf-8-sig")
        self.assertRegex(smoke, r'scrNTTEFullSmokeAsyncCase\("FrontierBubblesAttack212Tests"\)\)\s*\{\s*scrFRIntegrationTestStart\("bubbles_attack212"\)')
        native = (ROOT / "native/tests.gml").read_text("utf-8-sig")
        staged = (project / "scripts/scrFrontier_tests/scrFrontier_tests.gml").read_text("utf-8-sig")
        body = self.assert_bubbles212_dispatch(native)
        self.assertEqual(body, self.assert_bubbles212_dispatch(staged))
        # These negative controls fail for the exact omission that used to
        # pass the declaration-only check, and for a partially wired driver.
        for broken in (native.replace(body, "", 1),
                       native.replace("scrFRBubblesAttack212TestsStart(id)", "", 1),
                       native.replace("scrFRBubblesAttack212TestsStep(id)", "", 1)):
            with self.assertRaises(AssertionError):
                self.assert_bubbles212_dispatch(broken)
        uber = (project / "objects/UberCont/Step_0.gml").read_text("utf-8-sig")
        self.assertLess(uber.index("scrFRBubblesAttack212TestsBeforeInput();"),
                        uber.index("scrHandleInputsGeneral(global.index)"))
        self.assertGreater(uber.index("scrFRBubblesAttack212TestsAfterInput();"),
                           uber.index("scrHandleInputsGeneral(global.index)"))
        for path in (ROOT / "native/bubbles_startup_tests.gml",
                     project / "scripts/scrFrontier_bubbles_startup_tests/scrFrontier_bubbles_startup_tests.gml"):
            self.assertIn("var _fr205=scrFRBubblesAttack212TouchState();", path.read_text("utf-8-sig"))

    def test_bubbles212_routes_survive_native_mirror_and_legacy_test_hooks(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            grouped = {}
            for hook in fr_audio_bubbles205_hooks.hook_specs(tests=True):
                grouped.setdefault(hook["path"], []).append(hook["replacement"])
            for relative, fragments in grouped.items():
                path = project / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("\n".join(fragments), encoding="utf8")
            # Model the maintained build's canonical native -> stage copy.
            for native, script in (("tests", "scrFrontier_tests"),
                                   ("bubbles_startup_tests", "scrFrontier_bubbles_startup_tests")):
                (project / f"scripts/{script}/{script}.gml").write_bytes(
                    (ROOT / f"native/{native}.gml").read_bytes())
            marker = project / "scripts/scrFrontier_bubbles_attack212_tests/scrFrontier_bubbles_attack212_tests.gml"
            marker.parent.mkdir(parents=True)
            marker.write_bytes((ROOT / "native/bubbles_attack212_tests.gml").read_bytes())
            fr_audio_bubbles205_hooks.apply(project, tests=True)
            self.assert_bubbles212_dispatch((project / "scripts/scrFrontier_tests/scrFrontier_tests.gml").read_text("utf-8-sig"))
            self.assertIn("scrFRBubblesAttack212TouchState();", (project / "scripts/scrFrontier_bubbles_startup_tests/scrFrontier_bubbles_startup_tests.gml").read_text("utf-8-sig"))
            uber = (project / "objects/UberCont/Step_0.gml").read_text("utf-8-sig")
            self.assertIn("scrFRBubblesAttack212TestsBeforeInput();", uber)
            self.assertIn("scrFRBubblesAttack212TestsAfterInput();", uber)
            before = {path: path.read_bytes() for path in project.rglob("*.gml")}
            fr_audio_bubbles205_hooks.apply(project, tests=True)
            self.assertEqual(before, {path: path.read_bytes() for path in project.rglob("*.gml")})


if __name__ == "__main__":
    unittest.main()
