"""Keep Hyperion's projectile interception restricted to hostile shots."""
from pathlib import Path


PATTERN = "scripts/frCode_AugmentCompassion_skill_*/*.gml"
CALLBACK = "fr_Mutations_AugmentCompassion_skill_gml_DroneShock_nullify"
QUERY = ('scrFRMatchingNE(scrFRMatchingNE(projectile, "typ", 0), '
         '"team", team)')
QUERY_NEW = 'scrFRHyperionEnemyProjectiles() /* FRONTIER HYPERION HOSTILE TARGETS */'
ENTRY = f"function {CALLBACK}() {{"
ENTRY_NEW = (ENTRY + '\n// BEGIN FRONTIER HYPERION HOSTILE COLLISION\n'
             'if(!scrFRHyperionEnemyProjectile(scrFROther(other))) return;\n'
             '// END FRONTIER HYPERION HOSTILE COLLISION')
ASSIGN = f"on_projectile = {CALLBACK};"
ASSIGN_NEW = (ASSIGN + '\n// BEGIN FRONTIER HYPERION GRENADE COLLISION\n'
              f'on_grenade = {CALLBACK};\n'
              '// END FRONTIER HYPERION GRENADE COLLISION')


def apply(project):
    project = Path(project)
    matches = sorted(project.glob(PATTERN))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one Hyperion source module, found {len(matches)}")
    path = matches[0]
    raw = path.read_bytes()
    source = raw.decode("utf-8-sig").replace("\r\n", "\n")
    replacements = (
        (QUERY, QUERY_NEW, "/* FRONTIER HYPERION HOSTILE TARGETS */", 1),
        (ENTRY, ENTRY_NEW, "// BEGIN FRONTIER HYPERION HOSTILE COLLISION", 1),
        (ASSIGN, ASSIGN_NEW, "// BEGIN FRONTIER HYPERION GRENADE COLLISION", 2),
    )
    # Validate every boundary before writing the module. Both the physical
    # drone and its expanding shock use exactly this source callback.
    for anchor, replacement, marker, count in replacements:
        if replacement in source:
            if source.count(replacement) != count or source.count(marker) != count:
                raise RuntimeError("Duplicate/partial Hyperion hook: " + marker)
            if source.count(anchor) != count * replacement.count(anchor):
                raise RuntimeError("Extra Hyperion source anchor: " + marker)
            continue
        if marker in source or source.count(anchor) != count:
            raise RuntimeError("Changed Hyperion source anchor: " + marker)
        source = source.replace(anchor, replacement)
    # A truncated end marker must not silently make a partial install valid.
    for label, count in (("HOSTILE COLLISION", 1), ("GRENADE COLLISION", 2)):
        if source.count("// BEGIN FRONTIER HYPERION " + label) != count \
                or source.count("// END FRONTIER HYPERION " + label) != count:
            raise RuntimeError("Partial Hyperion hook: " + label)
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    newline = "\r\n" if b"\r\n" in raw else "\n"
    updated = bom + source.replace("\n", newline).encode("utf8")
    if updated != raw:
        path.write_bytes(updated)
    return {"file": path.relative_to(project).as_posix(),
            "kind": "Hyperion hostile-only target and native projectile/grenade collision"}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    print(json.dumps(apply(parser.parse_args().project), indent=2))
