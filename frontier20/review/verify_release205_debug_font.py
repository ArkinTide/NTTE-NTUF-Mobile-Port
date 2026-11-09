"""Fresh2.0.5 static font evidence, preserving frozen build102/b100 tools."""
from pathlib import Path as _Path
import hashlib as _hashlib

_BASE205 = _Path(__file__).with_name("verify_release204_debug_font.py")
_raw205 = _BASE205.read_bytes()
assert _hashlib.sha256(_raw205).hexdigest() == "5197ca1587d2217b0d1f6b6e5aea93c89ab715a8ec80ba350721a901f4721a00"
_text205 = _raw205.decode("utf-8-sig")
for _old205, _new205, _count205 in (
    ("dbg-font-full-range-coverage-204.json", "dbg-font-full-range-coverage-205.json", 1),
    ('"internal":100', '"internal":103', 1),
    ('"version":"2.0.4"', '"version":"2.0.5"', 1),
):
    assert _text205.count(_old205) == _count205, ("Frozen font anchor changed", _old205)
    _text205 = _text205.replace(_old205, _new205)
_entry205 = '\nif __name__=="__main__":main()\n'
assert _text205.count(_entry205) == 1
exec(compile(_text205.replace(_entry205, "\n"), str(_BASE205), "exec"), globals())


if __name__ == "__main__":
    main()
