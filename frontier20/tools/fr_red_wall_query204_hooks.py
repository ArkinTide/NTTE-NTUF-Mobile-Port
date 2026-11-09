"""Install only the Player's real-wall query at Red secret-wall seams.

No source import, terrain regeneration, sprite/mask mutation or collision-
response replacement. Validation precedes all writes; failed writes roll back
the exact original bytes. Repeated application is byte-identical.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EVENT = "objects/Player/Collision_Wall.gml"
SCRIPT = "scrFrontier_red_wall_query204"
FUNCTION = "scrNTTEFullPlayerWallMeeting"
MARKER = "// FRONTIER RED WALL QUERY204 REAL WALL CONTACT"
PATCHES = (
    ("\tif (instance_exists(Floor)) while (place_meeting(x, y, Wall)) {",
     "\t" + MARKER + "\n\tif (instance_exists(Floor)) while (scrNTTEFullPlayerWallMeeting(x, y)) {", 1),
    ("\t\tif (!place_meeting(x, y, Wall)) break",
     "\t\tif (!scrNTTEFullPlayerWallMeeting(x, y)) break", 1),
    ("if place_meeting(x + hspeed, y, Wall) {",
     "if scrNTTEFullPlayerWallMeeting(x + hspeed, y) {", 2),
    ("if place_meeting(x, y + vspeed, Wall) {",
     "if scrNTTEFullPlayerWallMeeting(x, y + vspeed) {", 2),
)


def read_json(raw):
    return json.loads(re.sub(r",(?=\s*[}\]])", "", raw.decode("utf-8-sig")))


def event_source(raw):
    text = raw.decode("utf-8-sig").replace("\r\n", "\n")
    installed = MARKER in text or FUNCTION in text
    if installed:
        if text.count(MARKER) != 1 or text.count(FUNCTION + "(") != 6:
            raise RuntimeError("Red wall query204 partial or duplicate installed Player event")
        for before, after, count in PATCHES:
            if text.count(before) or text.count(after) != count:
                raise RuntimeError("Red wall query204 installed Player anchor changed: " + before)
        return raw, "already-applied"
    if text.count("place_meeting(") != 6:
        raise RuntimeError("Red wall query204 unexpected Player collision queries")
    for before, after, count in PATCHES:
        if text.count(before) != count:
            raise RuntimeError("Red wall query204 Player anchor changed: " + before)
    for before, after, count in PATCHES:
        text = text.replace(before, after)
    return text.encode("utf8"), "patched"


def apply(project):
    project = Path(project).resolve()
    originals, planned, report = {}, {}, []

    def read(relative, optional=False):
        path = project / relative
        if path.is_symlink() or not path.resolve().is_relative_to(project):
            raise RuntimeError("Red wall query204 consumer escapes project: " + relative)
        value = path.read_bytes() if path.exists() else None
        if value is None and not optional:
            raise RuntimeError("Red wall query204 missing consumer: " + relative)
        originals[path] = value
        return path, value

    event, raw = read(EVENT)
    planned[event], state = event_source(raw)
    report.append({"path": EVENT, "status": state})

    yyp, raw = read("nuclearthronemobile.yyp")
    model = read_json(raw)
    relative = f"scripts/{SCRIPT}/{SCRIPT}.yy"
    matching = [value for value in model["resources"]
                if value["id"]["path"] == relative or value["id"]["name"] == SCRIPT]
    if len(matching) > 1 or (matching and matching[0]["id"] != {"name": SCRIPT, "path": relative}):
        raise RuntimeError("Red wall query204 duplicate or mismatched script registration")
    if not matching:
        model["resources"].append({"id": {"name": SCRIPT, "path": relative}})
        planned[yyp] = (json.dumps(model, ensure_ascii=False, indent=2) + "\n").encode("utf8")
    template_path, template_raw = read("scripts/scrNTTEFullAreas/scrNTTEFullAreas.yy")
    template = deepcopy(read_json(template_raw))
    template["name"] = template["%Name"] = SCRIPT
    script_yy, previous_yy = read(relative, optional=True)
    expected_yy = (json.dumps(template, ensure_ascii=False, indent=2) + "\n").encode("utf8")
    if previous_yy is not None and read_json(previous_yy) != template:
        raise RuntimeError("Red wall query204 existing script metadata differs")
    # An existing valid resource retains its original formatting, as does yyp.
    if previous_yy is None:
        planned[script_yy] = expected_yy
    script_gml, previous_gml = read(f"scripts/{SCRIPT}/{SCRIPT}.gml", optional=True)
    expected_gml = (ROOT / "native/red_wall_query204.gml").read_bytes()
    if expected_gml.decode("utf8").count("function " + FUNCTION + "(") != 1:
        raise RuntimeError("Red wall query204 maintained helper is ambiguous")
    if previous_gml is not None and previous_gml != expected_gml:
        raise RuntimeError("Red wall query204 installed helper differs from maintained source")
    planned[script_gml] = expected_gml
    report.append({"path": relative, "status": "already-applied" if matching else "registered"})

    for path, original in originals.items():
        if (path.read_bytes() if path.exists() else None) != original:
            raise RuntimeError("Red wall query204 consumer changed during preflight: " + str(path))
    written, new_directories = [], []
    try:
        for path, data in planned.items():
            if data == originals[path]:
                continue
            missing = []
            parent = path.parent
            while not parent.exists():
                missing.append(parent)
                parent = parent.parent
            for parent in reversed(missing):
                parent.mkdir()
                new_directories.append(parent)
            # Add before writing so even a partial write is restored.
            written.append(path)
            path.write_bytes(data)
    except Exception:
        for path in reversed(written):
            if originals[path] is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(originals[path])
        for directory in reversed(new_directories):
            directory.rmdir()
        raise
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", type=Path, required=True)
    print(json.dumps(apply(parser.parse_args().apply), indent=2))
