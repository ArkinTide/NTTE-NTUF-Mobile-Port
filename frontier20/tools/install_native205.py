"""Register only explicitly maintained 2.0.5 native scripts in current stage.

This is a narrow installer, never a reimport of generated source or assets.
Missing files are rejected before any write, and imports are inert.
"""
from copy import deepcopy
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = {
    "wall_surface205.gml": "scrFrontier_wall_surface205",
    "wall_surface205_tests.gml": "scrFrontier_wall_surface205_tests",
}


def load(path):
    return json.loads(re.sub(r",(?=\s*[}\]])", "", path.read_text("utf-8-sig")))


def apply(project, mapping):
    project = Path(project).resolve()
    sources = {name: (ROOT / "native" / name).read_bytes() for name in mapping}
    yyp_path = project / "nuclearthronemobile.yyp"
    yyp_raw = yyp_path.read_bytes()
    yyp = load(yyp_path)
    template = load(project / "scripts/scrFrontier_wall_fixes/scrFrontier_wall_fixes.yy")
    resources = {row["id"]["path"]: row for row in yyp["resources"]}
    for filename, name in mapping.items():
        if not re.fullmatch(r"scrFrontier_[A-Za-z0-9_]+", name):
            raise RuntimeError("Unexpected native205 script identity")
        folder = project / "scripts" / name
        folder.mkdir(parents=True, exist_ok=True)
        rel = f"scripts/{name}/{name}.yy"
        meta = deepcopy(template)
        meta["name"] = meta["%Name"] = name
        meta_bytes = (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        data_path = folder / (name + ".gml")
        meta_path = folder / (name + ".yy")
        if not data_path.is_file() or data_path.read_bytes() != sources[filename]:
            data_path.write_bytes(sources[filename])
        if not meta_path.is_file() or meta_path.read_bytes() != meta_bytes:
            meta_path.write_bytes(meta_bytes)
        resources[rel] = {"id": {"name": name, "path": rel}}
    yyp["resources"] = list(resources.values())
    if yyp_path.read_bytes() != yyp_raw:
        raise RuntimeError("Project resource index changed during native205 registration")
    data = (json.dumps(yyp, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if data != yyp_raw:
        yyp_path.write_bytes(data)
    return {"registered": mapping}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT / "staging/project")
    parser.add_argument("--mapping", type=Path, help="Explicit reviewed native filename to script-name JSON map")
    args = parser.parse_args()
    mapping = load(args.mapping) if args.mapping else SCRIPTS
    print(json.dumps(apply(args.project, mapping), indent=2))
