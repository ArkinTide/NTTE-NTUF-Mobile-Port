"""GML treats an undeclared harness function as a late instance-field lookup.

Keep registered regression drivers bound to real maintained functions; Igor
alone does not reject a lost entry point when one test file is replaced.
"""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


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


if __name__ == "__main__":
    unittest.main()
