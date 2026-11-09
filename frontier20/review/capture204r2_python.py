"""Capture the real current build102 Python suite with exact source bindings."""
from pathlib import Path as _Path
import hashlib as _hashlib

_BASE_CAPTURE = _Path(__file__).with_name("capture204_python.py")
_raw = _BASE_CAPTURE.read_bytes()
assert _hashlib.sha256(_raw).hexdigest() == "9cd22ec882d52808007f1c128ded2023f026737107468a6cda42aadaf0ff6132", "Frozen build100 capture changed"
_text = _raw.decode("utf-8-sig")
for _old, _new, _count in (
    ('"internal": 100', '"internal": 102', 1),
    ('post203-python-regression', 'post204r2-python-regression', 2),
):
    assert _text.count(_old) == _count, ("Frozen capture anchor changed", _old)
    _text = _text.replace(_old, _new)
_entry = '\nif __name__ == "__main__":\n    main()\n'
assert _text.count(_entry) == 1
_text = _text.replace(_entry, "\n")
exec(compile(_text, str(_BASE_CAPTURE), "exec"), globals())
REVIEW_TESTS = (*REVIEW_TESTS, "review/test_review204r2.py")
REVIEW_INPUTS = (*REVIEW_INPUTS, "review/verify_204r2_repairs.py", "review/capture204r2_python.py",
                 "review/test_review204r2.py", "review/release204r2-cases.json",
                 "review/inspect_release204r2_packages.py", "review/verify_release204r2_debug_font.py",
                 "generated-assets/boss-art204/manifest.json", "generated-assets/boss-art204/verification.json")


if __name__ == "__main__":
    main()
