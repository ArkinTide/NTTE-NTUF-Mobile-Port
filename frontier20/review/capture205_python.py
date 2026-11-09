"""Capture one aggregate current205 suite with exact maintained/reviewer inputs.

Import is inert. The explicit capture command runs only the Python suite and
writes a new immutable205 log/receipt; no build, game, Git or network action.
"""
from pathlib import Path as _Path
import hashlib as _hashlib

_BASE205 = _Path(__file__).with_name("capture204_python.py")
_raw205 = _BASE205.read_bytes()
assert _hashlib.sha256(_raw205).hexdigest() == "9cd22ec882d52808007f1c128ded2023f026737107468a6cda42aadaf0ff6132", "Frozen capture changed"
_text205 = _raw205.decode("utf-8-sig")
for _old205, _new205, _count205 in (
    ('"version": "2.0.4", "internal": 100', '"version": "2.0.5", "internal": 103', 1),
    ("post203-python-regression", "post205-python-regression", 2),
    ("tools/test_*.py plus the two explicit204 reviewer/verifier guard modules in one aggregate suite",
     "tools/test_*.py plus all four explicit retained/current205 reviewer guard modules in one aggregate suite", 1),
):
    assert _text205.count(_old205) == _count205, ("Frozen capture anchor changed", _old205)
    _text205 = _text205.replace(_old205, _new205)
_entry205 = '\nif __name__ == "__main__":\n    main()\n'
assert _text205.count(_entry205) == 1
exec(compile(_text205.replace(_entry205, "\n"), str(_BASE205), "exec"), globals())
REVIEW_TESTS = (*REVIEW_TESTS, "review/test_review204r2.py", "review/test_review205.py")
REVIEW_INPUTS = (*REVIEW_INPUTS, "review/verify_204r2_repairs.py", "review/capture204r2_python.py",
    "review/test_review204r2.py", "review/release204r2-cases.json",
    "review/inspect_release204r2_packages.py", "review/verify_release204r2_debug_font.py",
    "generated-assets/boss-art204/manifest.json", "generated-assets/boss-art204/verification.json",
    "review/verify_205_repairs.py", "review/capture205_python.py", "review/test_review205.py",
    "review/release205-cases.json", "review/release205-user-requirements.json",
    "review/inspect_release205_packages.py", "review/verify_release205_debug_font.py")


if __name__ == "__main__":
    main()
