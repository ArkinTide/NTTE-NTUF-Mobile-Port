"""Retain the authored constructor when native loop clusters use a shared shell."""
from pathlib import Path
from tempfile import TemporaryDirectory
import re

from fr_content_hooks import patch


FUNCTION = re.compile(r"^function (?P<name>\w+)\((?P<params>[^\n]*)\)\s*\{", re.M)


def _arguments(text, opening):
    """Read a compiled call without confusing nested expressions or strings."""
    level = 1
    quote = None
    escaped = False
    start = opening + 1
    result = []
    for index in range(start, len(text)):
        char = text[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
        elif char in "([{":
            level += 1
        elif char in ")]}":
            level -= 1
            if level == 0:
                result.append(text[start:index].strip())
                return result, index + 1
        elif char == "," and level == 1:
            result.append(text[start:index].strip())
            start = index + 1
    raise AssertionError("Unclosed compiled Frontier constructor")


def retain_factories(text):
    headers = list(FUNCTION.finditer(text))
    changes = []
    total = 0
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        body = text[header.end():end]
        params = [item.split("=", 1)[0].strip()
                  for item in header.group("params").split(",") if item.strip()]
        for call in re.finditer(r"\bscrFRInstanceCreate\(", body):
            args, finish = _arguments(body, call.end() - 1)
            if len(args) != 3 or args[2] != "FRCustomEnemy":
                continue
            name = header.group("name")
            assert name.endswith("_create") and len(params) >= 2, name
            replacement = (f"scrFRClusterEnemyCreate({args[0]}, {args[1]}, {name}, "
                           f"[{', '.join(params)}])")
            changes.append((header.end() + call.start(), header.end() + finish, replacement))
            total += 1
    for start, end, replacement in reversed(changes):
        text = text[:start] + replacement + text[end:]
    return text, total


def apply(project):
    project = Path(project)
    count = 0
    updates = []
    for path in sorted((project / "scripts").glob("frCode_*/*.gml")):
        raw = path.read_bytes()
        bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
        text, changed = retain_factories(raw.decode("utf-8-sig"))
        count += changed
        if changed:
            updates.append((path, bom + text.encode("utf-8")))
    # Validate every generated constructor and the native anchor before any
    # project file changes. A stale base must leave the stage byte-for-byte.
    relative = "scripts/scrUndergrowthNative/scrUndergrowthNative.gml"
    original = project / relative
    with TemporaryDirectory(prefix="fr-cluster205-") as folder:
        probe = Path(folder)
        target = probe / relative
        target.parent.mkdir(parents=True)
        target.write_bytes(original.read_bytes())
        patch(probe, relative, "LOOP CLUSTER SOURCE FACTORY",
              "if(_object==FRCustomEnemy && instance_exists(_source))\n"
              "    return scrFRClusterCreate(_x,_y,_source);",
              anchor="function scrUGClusterCreate(_x,_y,_object,_source) {")
        updates.append((original, target.read_bytes()))
    for path, content in updates:
        if path.read_bytes() != content:
            path.write_bytes(content)
    return {"source_factories_retained": count,
            "shared_shell_cluster_repair": True,
            "native_case": "FrontierPirateVisibility205Tests"}
