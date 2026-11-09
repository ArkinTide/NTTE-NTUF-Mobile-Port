"""Read-only build102 package audit, retaining every frozen build100 binary check."""
from pathlib import Path as _Path
import hashlib as _hashlib

_BASE = _Path(__file__).with_name("inspect_release204_packages.py")
_raw = _BASE.read_bytes()
assert _hashlib.sha256(_raw).hexdigest() == "10093e9a810482c6d5ed3a784484fb4dadc4f7a5b2b75c83c6933494008d5c3e"
_text = _raw.decode("utf-8-sig")
for _old, _new, _count in (
    ("internal100", "internal102", 1),
    ("mobile-release204-20261108", "mobile-release204r2-20261108", 1),
    ("release204-independent-package-audit.json", "release204r2-independent-package-audit.json", 1),
    ("release204-cases.json", "release204r2-cases.json", 1),
    ('VERSION, INTERNAL = "2.0.4", 100', 'VERSION, INTERNAL = "2.0.4", 102', 1),
    ('{platform}-{VERSION}.{suffix}', '{platform}-2.0.4-build102.{suffix}', 1),
    ('tools/release204_delivery.py', 'tools/release204r2_delivery.py', 1),
    ('("NTTE_RELEASE_NUMBER", "100")', '("NTTE_RELEASE_NUMBER", "102")', 1),
    ("3000100", "3000102", 2),
    ('== "100"', '== "102"', 1),
    ('"bundle_version": "100"', '"bundle_version": "102"', 1),
    ("dbg-font-full-range-coverage-204.json", "dbg-font-full-range-coverage-204r2.json", 1),
):
    assert _text.count(_old) == _count, ("Frozen audit anchor changed", _old)
    _text = _text.replace(_old, _new)
_entry = '\nif __name__ == "__main__":\n    main()\n'
assert _text.count(_entry) == 1
_text = _text.replace(_entry, "\n")
exec(compile(_text, str(_BASE), "exec"), globals())
_base_delivery_cases = delivery_cases


def delivery_cases(source, selection):
    """Validate the revision wrapper's exact frozen base and literal substitutions."""
    require(sha(source.encode("utf8")) == "4d4a95b3b6295de65d22d214b56d99fde33e30018f99ae041d6fa7a80202845c",
            "Reviewed build102 delivery wrapper changed")
    tree = ast.parse(source)
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in {"_BASE_TOOL_SHA256", "_REPLACEMENTS"}:
                require(name not in values, "Duplicate revision delivery declaration")
                values[name] = ast.literal_eval(node.value)
    require(set(values) == {"_BASE_TOOL_SHA256", "_REPLACEMENTS"}, "Revision wrapper lacks frozen declarations")
    base = ROOT / "tools/release204_delivery.py"
    bound(base, values["_BASE_TOOL_SHA256"], "Frozen delivery implementation")
    require(values["_BASE_TOOL_SHA256"] == "8bf26a83abd3a6f3398e08fe03f6cc821cc5814a9254a363dda95297a3d81b71",
            "Unexpected frozen delivery base")
    effective = base.read_text(encoding="utf-8-sig")
    for old, new in values["_REPLACEMENTS"]:
        count = 2 if old == '"versionCode=\'3000100\'"' else (3 if old == "internal100" else 1)
        require(effective.count(old) == count, "Revision delivery substitution anchor changed")
        effective = effective.replace(old, new)
    return _base_delivery_cases(effective, selection)


if __name__ == "__main__":
    main()
