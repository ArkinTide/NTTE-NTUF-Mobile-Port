"""Replay authored Frontier loadout artwork and install its isolated regression.

Only the weapon metadata script changes; ordinary world/HUD sprites, melee and
input code remain unchanged. Test entry points are registered by the owner.
Preflight completes before writes, and partial writes restore original bytes.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WEAPONS = "scripts/scrFrontier_weapons/scrFrontier_weapons.gml"
SCRIPT = "scrFrontier_loadout_art204_tests"
OLD = '        wep_lout[_weapon]=-1; wep_naim[_weapon]=false;'
NEW = '        wep_lout[_weapon]=scrFRWeaponProperty(_key,"weapon_loadout",-1); wep_naim[_weapon]=false;'


def read_json(raw):
    return json.loads(re.sub(r",(?=\s*[}\]])", "", raw.decode("utf-8-sig")))


def apply(project):
    project = Path(project).resolve()
    originals, planned = {}, {}

    def read(relative, optional=False):
        path = project / relative
        if path.is_symlink() or not path.resolve().is_relative_to(project):
            raise RuntimeError("Loadout art204 consumer escapes project: " + relative)
        raw = path.read_bytes() if path.exists() else None
        if raw is None and not optional:
            raise RuntimeError("Loadout art204 missing consumer: " + relative)
        originals[path] = raw
        return path, raw

    maintained = (ROOT / "native/weapons.gml").read_bytes()
    text = maintained.decode("utf-8-sig").replace("\r\n", "\n")
    if text.count(NEW) != 1 or OLD in text:
        raise RuntimeError("Loadout art204 maintained metadata declaration changed")
    target, raw = read(WEAPONS)
    current = raw.decode("utf-8-sig").replace("\r\n", "\n")
    if current not in (text, text.replace(NEW, OLD, 1)):
        raise RuntimeError("Loadout art204 staged weapon script has unrelated changes")
    planned[target] = raw if current == text else maintained

    yyp, raw = read("nuclearthronemobile.yyp")
    model = read_json(raw)
    relative = f"scripts/{SCRIPT}/{SCRIPT}.yy"
    matches = [r for r in model["resources"]
               if r["id"]["path"] == relative or r["id"]["name"] == SCRIPT]
    if len(matches) > 1 or (matches and matches[0]["id"] != {"name": SCRIPT, "path": relative}):
        raise RuntimeError("Loadout art204 duplicate or mismatched script registration")
    if not matches:
        model["resources"].append({"id": {"name": SCRIPT, "path": relative}})
        planned[yyp] = (json.dumps(model, ensure_ascii=False, indent=2) + "\n").encode("utf8")
    _, raw = read("scripts/scrNTTEFullAreas/scrNTTEFullAreas.yy")
    template = deepcopy(read_json(raw))
    template["name"] = template["%Name"] = SCRIPT
    target, raw = read(relative, optional=True)
    if raw is not None and read_json(raw) != template:
        raise RuntimeError("Loadout art204 existing test metadata differs")
    if raw is None:
        planned[target] = (json.dumps(template, ensure_ascii=False, indent=2) + "\n").encode("utf8")
    target, raw = read(f"scripts/{SCRIPT}/{SCRIPT}.gml", optional=True)
    tests = (ROOT / "native/loadout_art204_tests.gml").read_bytes()
    if raw is not None and raw != tests:
        raise RuntimeError("Loadout art204 existing regression differs")
    planned[target] = tests

    for path, raw in originals.items():
        if (path.read_bytes() if path.exists() else None) != raw:
            raise RuntimeError("Loadout art204 input changed during preflight")
    written, directories = [], []
    try:
        for path, raw in planned.items():
            if raw == originals[path]:
                continue
            missing, parent = [], path.parent
            while not parent.exists():
                missing.append(parent)
                parent = parent.parent
            for directory in reversed(missing):
                directory.mkdir()
                directories.append(directory)
            written.append(path)
            path.write_bytes(raw)
    except Exception:
        for path in reversed(written):
            if originals[path] is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(originals[path])
        for directory in reversed(directories):
            directory.rmdir()
        raise
    return {"weapon_loadout": "authored callback or original -1 fallback",
            "regression_script": SCRIPT, "test_entry_points": "owner registration required",
            "changed_paths": [p.relative_to(project).as_posix() for p in written]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", type=Path, required=True)
    print(json.dumps(apply(parser.parse_args().apply), indent=2))
