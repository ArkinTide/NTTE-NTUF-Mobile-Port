"""Read-only2.0.5 APK/IPA audit retaining every frozen binary/source check.

Preparation is inert. Only explicit audit may write its one new report, and
only after complete current acceptance and actual packages exist.
"""
from pathlib import Path as _Path
import hashlib as _hashlib

_BASE205 = _Path(__file__).with_name("inspect_release204_packages.py")
_raw205 = _BASE205.read_bytes()
assert _hashlib.sha256(_raw205).hexdigest() == "10093e9a810482c6d5ed3a784484fb4dadc4f7a5b2b75c83c6933494008d5c3e", "Frozen package inspector changed"
_text205 = _raw205.decode("utf-8-sig")
for _old205, _new205, _count205 in (
    ("internal100", "internal103", 1),
    ("mobile-release204-20261108", "mobile-release205-20261109", 1),
    ("release204-independent-package-audit.json", "release205-independent-package-audit.json", 1),
    ("release204-cases.json", "release205-cases.json", 1),
    ('VERSION, INTERNAL = "2.0.4", 100', 'VERSION, INTERNAL = "2.0.4", 103', 1),
    ('tools/release204_delivery.py', 'tools/release205_delivery.py', 1),
    ('("NTTE_RELEASE_NUMBER", "100")', '("NTTE_RELEASE_NUMBER", "103")', 1),
    ("3000100", "3000103", 2),
    ('== "100"', '== "103"', 1),
    ('"bundle_version": "100"', '"bundle_version": "103"', 1),
    (r"""r'("option_ios_version"\s*:\s*)"2\.0"'""",
     r"""r'("option_ios_version"\s*:\s*)"2\.0\.5"'""", 1),
    ("dbg-font-full-range-coverage-204.json", "dbg-font-full-range-coverage-205.json", 1),
):
    assert _text205.count(_old205) == _count205, ("Frozen audit anchor changed", _old205)
    _text205 = _text205.replace(_old205, _new205)
assert _text205.count("2.0.4") == 8, "Frozen audit version anchors changed"
_text205 = _text205.replace("2.0.4", "2.0.5")
_entry205 = '\nif __name__ == "__main__":\n    main()\n'
assert _text205.count(_entry205) == 1
exec(compile(_text205.replace(_entry205, "\n"), str(_BASE205), "exec"), globals())
_base205_delivery_cases = delivery_cases
REVIEWED205_DELIVERY_SHA256 = "ec4c340fc970705b825d6af83d91a869db64696f60e92c51fb2fd7ff4d03df97"


def delivery_cases(source, selection):
    """Validate the exact reviewed inert wrapper, then its effective declaration."""
    require(sha(source.encode("utf8")) == REVIEWED205_DELIVERY_SHA256,
            "Reviewed205 delivery wrapper changed; independent review must be refreshed")
    tree = ast.parse(source)
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in {"_BASE_TOOL_SHA256", "_REPLACEMENTS"}:
                require(name not in values, "Duplicate205 delivery declaration")
                values[name] = ast.literal_eval(node.value)
    require(set(values) == {"_BASE_TOOL_SHA256", "_REPLACEMENTS"}, "205 wrapper lacks frozen declarations")
    base = ROOT / "tools/release204_delivery.py"
    bound(base, values["_BASE_TOOL_SHA256"], "Frozen delivery implementation")
    require(values["_BASE_TOOL_SHA256"] == "8bf26a83abd3a6f3398e08fe03f6cc821cc5814a9254a363dda95297a3d81b71",
            "Unexpected frozen205 delivery base")
    effective = base.read_text(encoding="utf-8-sig")
    for old, new in values["_REPLACEMENTS"]:
        expected = 2 if old == '"versionCode=\'3000100\'"' else (3 if old == "internal100" else None)
        require(effective.count(old) == expected if expected is not None else effective.count(old) >= 1,
                "205 delivery substitution anchor changed")
        effective = effective.replace(old, new)
    require(selection["version"] == VERSION and selection["internal"] == INTERNAL,
            "Independent205 selection identity differs")
    result = _base205_delivery_cases(effective, selection)
    require(len(result) == len(set(result)) == 82, "Independent205 scope must contain exactly82 reviewed native cases")
    return result


if __name__ == "__main__":
    main()
