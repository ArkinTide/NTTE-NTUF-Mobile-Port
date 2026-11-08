"""Capture one aggregate current204 Python suite and its exact maintained inputs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REVIEW_TESTS = ("review/test_verify_post203_repairs.py", "review/test_release204_reviewers.py")
REVIEW_INPUTS = ("review/capture204_python.py", "review/inspect_release204_packages.py",
    "review/review_release204_source.py", "review/verify_release204_debug_font.py",
    "review/test_release204_reviewers.py", "review/verify_post203_repairs.py",
    "review/test_verify_post203_repairs.py")


def inputs():
    paths = sorted([*ROOT.joinpath("tools").glob("*.py"),
                    *ROOT.joinpath("native").glob("*.gml")])
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths}


def reviewer_inputs():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in REVIEW_INPUTS}


def suite_command():
    # One aggregate runner yields exactly one Ran-N/OK boundary for the
    # acceptance verifier. Loading the explicit review tests never runs a
    # reviewer CLI, package audit, build, game, Git command or publisher.
    runner = '''import importlib.util
import pathlib
import sys
import unittest
suite=unittest.TestSuite([unittest.defaultTestLoader.discover("tools",pattern="test_*.py")])
for index,name in enumerate(REVIEW_TESTS):
    path=pathlib.Path(name)
    spec=importlib.util.spec_from_file_location("release204_review_tests_"+str(index),path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result=unittest.TextTestRunner(verbosity=1).run(suite)
sys.exit(not result.wasSuccessful())
'''
    return [sys.executable, "-B", "-c", "REVIEW_TESTS=" + repr(REVIEW_TESTS) + "\n" + runner]


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "post203-python-regression"
    assert re.fullmatch(r"post203-python-regression(?:-[a-z0-9]+)?", label)
    log = ROOT / "review" / (label + ".txt")
    receipt = log.with_suffix(".json")
    assert not log.exists() and not receipt.exists(), "Preserve captured evidence"
    before, review_before = inputs(), reviewer_inputs()
    result = subprocess.run(suite_command(), cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = result.stdout.decode("utf8", errors="replace")
    matches = re.findall(r"^Ran (\d+) tests in ", text, re.MULTILINE)
    count = int(matches[0]) if len(matches) == 1 else 0
    unchanged, review_unchanged = before == inputs(), review_before == reviewer_inputs()
    record = {"exit": result.returncode, "tests": count, "version": "2.0.4", "internal": 100,
              "log": log.relative_to(ROOT).as_posix(),
              "log_sha256": hashlib.sha256(result.stdout).hexdigest(),
              "source_inputs": before, "source_inputs_unchanged": unchanged,
              "reviewer_inputs": review_before, "reviewer_inputs_unchanged": review_unchanged,
              "review_test_modules": list(REVIEW_TESTS),
              "test_scope": "tools/test_*.py plus the two explicit204 reviewer/verifier guard modules in one aggregate suite",
              "utc": datetime.now(timezone.utc).isoformat()}
    with log.open("xb") as stream:
        stream.write(result.stdout)
    with receipt.open("x", encoding="utf8") as stream:
        json.dump(record, stream, indent=2)
        stream.write("\n")
    print(text[-2500:])
    assert unchanged and review_unchanged, "Maintained Python/native/reviewer inputs changed during checks"
    assert result.returncode == 0 and count >= 110 and re.search(r"\nOK\s*$", text)


if __name__ == "__main__":
    main()
