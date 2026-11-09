"""Keep source wall edge artwork independent of compact exterior collision.

Only explicitly selected project files are changed. No stage importer runs.
"""
from pathlib import Path
import argparse
import json

MACRO = "scripts/macros_general/macros_general.gml"
TOP = "objects/SubTopCont/Draw_0.gml"


def transform_macro(source):
    start = source.index("#macro mcr_wall_update_lrwh {")
    end = source.index("\n\n", start)
    body = source[start:end]
    marker = "/* FRONTIER WALL ART205 */"
    if marker in body:
        if body.count(marker) != 1 or body.count("scrFRWallArtFree205(") != 4 or "place_free(" in body:
            raise RuntimeError("Partial wall-art205 macro")
        return source
    if body.count("place_free(") != 4:
        raise RuntimeError("Wall-art205 macro anchor changed")
    body = body.replace("{ \\", "{ " + marker + " \\", 1)
    body = body.replace("place_free(", "scrFRWallArtFree205(")
    return source[:start] + body + source[end:]


def transform_top(source):
    anchor = "var _list = global.lis_walls_visible,"
    fill = "scrNTTESolidWallDraw();"
    marker = "// FRONTIER WALL ART205 FILL BEFORE SOURCE EDGES"
    if marker in source:
        if source.count(marker) != 1 or source.count(fill) != 1 or source.index(fill) > source.index(anchor):
            raise RuntimeError("Partial wall-art205 draw order")
        return source
    if source.count(anchor) != 1 or source.count(fill) != 1:
        raise RuntimeError("Wall-art205 draw anchor changed")
    source = source.replace(fill + "\n", "", 1)
    return source.replace(anchor, marker + "\n" + fill + "\n\n" + anchor, 1)


def apply(project):
    project = Path(project).resolve()
    rows = []
    for rel, transform in ((MACRO, transform_macro), (TOP, transform_top)):
        path = project / rel
        raw = path.read_bytes()
        source = raw.decode("utf-8-sig").replace("\r\n", "\n")
        updated = transform(source)
        if updated != source:
            rows.append((path, raw, updated.encode("utf-8")))
    for path, raw, _ in rows:
        if path.read_bytes() != raw:
            raise RuntimeError("Wall-art205 consumer changed during preflight")
    written = []
    try:
        for path, raw, data in rows:
            written.append((path, raw))
            path.write_bytes(data)
    except BaseException:
        for path, raw in reversed(written):
            path.write_bytes(raw)
        raise
    return {"changed": [p.relative_to(project).as_posix() for p, _, _ in rows]}


def apply_tests(project):
    project = Path(project).resolve()
    specs = (
        ("scripts/scrFrontier_tests/scrFrontier_tests.gml", "function scrFRIntegrationTestStep() {",
         '''
    // FRONTIER WALL SURFACE205 TEST DRIVER
    if(fr_test_case=="wall-surface205") {
        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;
        if(++fr_test_ticks<45) return;
        scrFRWallSurface205Tests();
        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");
        game_end();return;
    }
''', False),
        ("scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml",
         '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))',
         '// FRONTIER WALL SURFACE205 TEST ENTRY\n'
         'if(scrNTTEFullSmokeAsyncCase("FrontierWallSurface205Tests")) {scrFRIntegrationTestStart("wall-surface205");return;}\n', True),
    )
    changed = []
    for rel, anchor, block, before in specs:
        path = project / rel
        source = path.read_text("utf-8-sig").replace("\r\n", "\n")
        if block in source:
            if source.count(block) != 1:
                raise RuntimeError("Duplicate wall205 test entry")
            continue
        if source.count(anchor) != 1:
            raise RuntimeError("Wall205 test anchor changed")
        replacement = block + anchor if before else anchor + block
        path.write_text(source.replace(anchor, replacement, 1), "utf-8", newline="\n")
        changed.append(rel)
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", required=True, type=Path)
    print(json.dumps(apply(parser.parse_args().apply), indent=2))
