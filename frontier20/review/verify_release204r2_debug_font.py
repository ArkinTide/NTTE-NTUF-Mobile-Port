"""Fresh build102 static font evidence; preserve the frozen build100 audit."""
from pathlib import Path as _Path
import hashlib as _hashlib

_BASE = _Path(__file__).with_name("verify_release204_debug_font.py")
_raw = _BASE.read_bytes()
assert _hashlib.sha256(_raw).hexdigest() == "5197ca1587d2217b0d1f6b6e5aea93c89ab715a8ec80ba350721a901f4721a00"
_text = _raw.decode("utf-8-sig")
for _old, _new in (
    ("dbg-font-full-range-coverage-204.json", "dbg-font-full-range-coverage-204r2.json"),
    ('"internal":100', '"internal":102'),
):
    assert _text.count(_old) == 1, _old
    _text = _text.replace(_old, _new)
_entry = '\nif __name__=="__main__":main()\n'
assert _text.count(_entry) == 1
_text = _text.replace(_entry, "\n")
exec(compile(_text, str(_BASE), "exec"), globals())


if __name__ == "__main__":
    main()
