"""Package the dynamic Frontier boss-intro triplets without reimporting assets.

The frozen importer inventories these originals but cannot infer concatenated
runtime paths. This supplement preserves their authored RGBA and the native
replacement targets' origins. Emission never writes the project; apply is a
separate, preflighted transaction owned by the release driver.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import tempfile

from PIL import Image

import import_frontier_assets as importer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "generated-assets/boss-art204"
SOURCE = ROOT / "original/Frontier"
BASE_MANIFEST = ROOT / "generated-assets/manifest.json"
SCRIPT = "scrFrontier_boss_art204_tests"
PRODUCTION = "scrFrontier_boss_art204"
REGISTRY = "scripts/scrFrontierAssets/scrFrontierAssets.gml"
BEGIN = "    // FRONTIER BOSS ART204 BEGIN"
END = "    // FRONTIER BOSS ART204 END"
BOSSES = ("CoveHyperCrystal", "GraveyardBoss", "LightningHyperCrystal",
          "OurpleCursedHyperCrystal", "RoboBoss")
TARGETS = {"Main": "sprBossIntro", "Back": "sprBossIntroBackLayer", "Name": "sprBossName"}
CALLBACK = "function fr_Objects_Frontier_Bosses_mod_gml_boss_intro_step() {"
NEXT_CALLBACK = "function fr_Objects_Frontier_Bosses_mod_gml_boss_hp("
DRAW_NAME = "scrNTTEFullBossIntroActive() ? scrNTTEFullBossIntroChineseName() : scrMenuButtonName(sprBossName, boss)"
DRAW_NAME_FIXED = "scrFRBossArt204IntroName(" + DRAW_NAME + ") // FRONTIER BOSS ART204 NATIVE NAME"
INTRO_GUARD = "if instance_exists(CoopController) || !opt_bossintro || !instance_exists(Player) exit"
INTRO_ANCHOR = "\t\tscrGetPauseImage()"
INTRO_LEGACY_FIXED = "\t\tfr_boss_art204_intro=false;fr_boss_art204_owner=noone; // FRONTIER BOSS ART204 ACCEPTED NATIVE INTRO\n" + INTRO_ANCHOR
INTRO_FIXED = "\t\tscrFRBossArt204NativeStart(); // FRONTIER BOSS ART204 ACCEPTED NATIVE INTRO\n" + INTRO_ANCHOR
SOURCE_GUARD = "if ((((! intro) && (UberCont.opt_bossintro == true)) && (GameCont.loops <= loops))) {"
SOURCE_GUARD_FIXED = "if (!intro && UberCont.opt_bossintro && GameCont.loops<=loops && scrFRBossArt204IntroPrepare(_fr_boss_art204_owner)) {"


def callback_transform(text):
    """Only the compiled source intro callback owns these five native calls."""
    text = text.replace("\r\n", "\n")
    if text.count(CALLBACK) != 1 or text.count(NEXT_CALLBACK) != 1:
        raise RuntimeError("Boss art204 source callback identity is ambiguous")
    start, stop = text.index(CALLBACK), text.index(NEXT_CALLBACK)
    if stop <= start:
        raise RuntimeError("Boss art204 source callback boundary changed")
    body = text[start:stop]
    cleanup = "scrFRSpriteRestore(sprBossIntro);\n;\nscrFRSpriteRestore(sprBossIntroBackLayer);\n;\nscrFRSpriteRestore(sprBossName);\n;\nscrFRInstanceDestroy();"
    fixed_cleanup = "if(scrFRBossArt204IntroActive()) return; // FRONTIER BOSS ART204 WAIT FOR NATIVE INTRO\n" + cleanup.replace("scrFRInstanceDestroy();", "scrFRBossArt204IntroFinish(); // FRONTIER BOSS ART204 NATIVE FINISH\nscrFRInstanceDestroy();")
    specs = [(f"scrFRSpriteReplaceImage({target}, spr_{role.lower()}, 0);",
              f"scrFRBossArt204Replace({target}, spr_{role.lower()}, 0); // FRONTIER BOSS ART204 EXACT {role.upper()}")
             for role, target in TARGETS.items()]
    specs += [("intro = false;\n;", "intro = false;\n;\nvar _fr_boss_art204_owner=real(id); // FRONTIER BOSS ART204 BINDING OWNER"),
              ("event_perform(ev_alarm, 6);", "scrFRBossArt204IntroStart(_fr_boss_art204_owner); // FRONTIER BOSS ART204 NATIVE START"),
              (cleanup, fixed_cleanup)]
    installed = [after in body for _, after in specs]
    if any(installed) and not all(installed):
        raise RuntimeError("Boss art204 partially installed source callback bridge")
    for before, after in specs:
        if after in body:
            if body.count(after) != 1 or before in body.replace(after, "", 1):
                raise RuntimeError("Boss art204 duplicated source callback bridge")
        else:
            if body.count(before) != 1:
                raise RuntimeError("Boss art204 source callback anchor changed: " + before)
            body = body.replace(before, after, 1)
    owner_line = "var _fr_boss_art204_owner=real(id); // FRONTIER BOSS ART204 BINDING OWNER"
    prepared_line = "fr_boss_art204_prepared=false; // FRONTIER BOSS ART204 PREPARATION OWNER"
    if prepared_line not in body:
        body = body.replace(owner_line, owner_line + "\n" + prepared_line, 1)
    elif body.count(prepared_line) != 1:
        raise RuntimeError("Boss art204 source preparation owner is duplicated")
    rejected_cleanup = "if(!fr_boss_art204_prepared) {scrFRInstanceDestroy();return;} // FRONTIER BOSS ART204 REJECTED CLEANUP\n"
    if rejected_cleanup not in body:
        body = body.replace(fixed_cleanup, rejected_cleanup + fixed_cleanup, 1)
    elif body.count(rejected_cleanup) != 1:
        raise RuntimeError("Boss art204 source rejected cleanup is duplicated")
    if SOURCE_GUARD_FIXED in body:
        if body.count(SOURCE_GUARD_FIXED) != 1 or SOURCE_GUARD in body:
            raise RuntimeError("Boss art204 source preparation guard is duplicated")
    else:
        if body.count(SOURCE_GUARD) != 1:
            raise RuntimeError("Boss art204 source preparation guard changed")
        body = body.replace(SOURCE_GUARD, SOURCE_GUARD_FIXED, 1)
    return text[:start] + body + text[stop:]


def maintain_generated(path=None):
    """Explicit source-maintenance step; project apply never edits this tree."""
    path = Path(path or ROOT / "generated-code/Objects_Frontier_Bosses_mod_gml.gml")
    original = path.read_bytes()
    text = original.decode("utf-8-sig")
    replacement = callback_transform(text)
    if replacement != text.replace("\r\n", "\n"):
        path.write_bytes(replacement.encode("utf8"))
    return {"path": str(path), "bridge_installed": True}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(raw):
    return json.loads(re.sub(r",(?=\s*[}\]])", "", raw.decode("utf-8-sig")))


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf8")


def inside(root, relative):
    path = root / relative
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise RuntimeError("Boss art204 path escapes its root: " + str(relative))
    return path


def source_rows(project, source=SOURCE, base_manifest=BASE_MANIFEST):
    """Read the archive inventory as provenance; reject changed originals."""
    project, source = Path(project).resolve(), Path(source).resolve()
    manifest = read_json(Path(base_manifest).read_bytes())
    originals = {row["path"]: row for row in manifest["original_media"]}
    rows = []
    for boss in BOSSES:
        for role, target in TARGETS.items():
            relative = f"Sprites/Menu/Intros/spr{boss}{role}.png"
            original = originals.get(relative)
            raw = inside(source, relative).read_bytes()
            if original is None or original["bytes"] != len(raw) or original["sha256"] != sha(raw):
                raise RuntimeError("Boss art204 original differs from frozen archive inventory: " + relative)
            descriptor = importer.load_yy(inside(project, f"sprites/{target}/{target}.yy"))
            origin = [descriptor["sequence"]["xorigin"], descriptor["sequence"]["yorigin"]]
            with Image.open(inside(source, relative)) as decoded:
                image = decoded.convert("RGBA")
            coverage = sum(image.getchannel("A").histogram()[1:])
            transparent = relative == "Sprites/Menu/Intros/sprGraveyardBossMain.png"
            if (coverage == 0) != transparent:
                raise RuntimeError("Boss art204 original is empty: " + relative)
            path = relative.lower()
            resource = importer.native_name("sprite", "boss-art204:" + path, relative)
            rows.append({"boss": boss, "role": role, "target": target, "path": relative,
                         "resource": resource, "aliases": [path, "../" + path],
                         "source_sha256": sha(raw), "source_bytes": len(raw),
                         "rgba_sha256": sha(image.tobytes()), "width": image.width,
                         "height": image.height, "frames": 1, "origin": origin,
                         "alpha_coverage": coverage, "authored_transparent": transparent})
    return rows


def emit(project, output=OUTPUT, source=SOURCE, base_manifest=BASE_MANIFEST):
    """Generate only a supplemental tree; never touch staging or base manifests."""
    project, output = Path(project).resolve(), Path(output).resolve()
    rows = source_rows(project, source, base_manifest)  # All provenance before writes.
    template = importer.load_yy(project / "sprites/mskBandit/mskBandit.yy")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="boss-art204-", dir=output.parent) as temporary:
        scratch = Path(temporary)
        old_output = importer.OUTPUT
        try:
            importer.OUTPUT = scratch
            for row in rows:
                with Image.open(Path(source) / row["path"]) as decoded:
                    image = decoded.convert("RGBA")
                emitted = importer.emit_sprite(row, [image], template)
                if emitted["rgba_sha256"] != [row["rgba_sha256"]]:
                    raise RuntimeError("Boss art204 emitter changed authored pixels")
        finally:
            importer.OUTPUT = old_output
        files = {p.relative_to(scratch).as_posix(): sha(p.read_bytes())
                 for p in sorted(scratch.rglob("*")) if p.is_file()}
        manifest = {"schema": "frontier-boss-art204-v1", "resource_count": 15,
                    "alias_count": 30, "base_manifest_sha256": sha(Path(base_manifest).read_bytes()),
                    "assets": rows, "files": files}
        proof = {"status": "PASS", "scope": "offline supplemental authored artwork packaging",
                 "resource_count": 15, "alias_count": 30, "original_inventory_verified": True,
                 "rgba_preserved": True, "target_origins_preserved": True,
                 "native_execution_performed": False, "physical_device_tested": False}
        (scratch / "manifest.json").write_bytes(json_bytes(manifest))
        (scratch / "verification.json").write_bytes(json_bytes(proof))
        planned = {p.relative_to(scratch).as_posix(): p.read_bytes()
                   for p in scratch.rglob("*") if p.is_file()}
        if output.exists():
            current = {p.relative_to(output).as_posix(): p.read_bytes()
                       for p in output.rglob("*") if p.is_file()}
            if current != planned:
                raise RuntimeError("Boss art204 existing supplement differs; inspect before replacing")
        else:
            # Rename a complete sibling tree, so a write failure cannot leave
            # a partial supplement that looks ready for a future release.
            scratch.replace(output)
    return verify_supplement(project, output, source, base_manifest)


def verify_supplement(project, output=OUTPUT, source=SOURCE, base_manifest=BASE_MANIFEST):
    output = Path(output).resolve()
    manifest = read_json(inside(output, "manifest.json").read_bytes())
    rows = source_rows(project, source, base_manifest)
    if manifest.get("schema") != "frontier-boss-art204-v1" or manifest.get("assets") != rows \
            or manifest.get("resource_count") != 15 or manifest.get("alias_count") != 30 \
            or manifest.get("base_manifest_sha256") != sha(Path(base_manifest).read_bytes()):
        raise RuntimeError("Boss art204 supplemental metadata/source/origin mismatch")
    expected_files = set()
    for row in rows:
        name = row["resource"]
        relative = f"sprites/{name}/{name}.yy"
        descriptor = importer.load_yy(inside(output, relative))
        if descriptor["name"] != name or descriptor["%Name"] != name \
                or descriptor["width"] != row["width"] or descriptor["height"] != row["height"] \
                or len(descriptor["frames"]) != 1 or descriptor["sequence"]["length"] != 1 \
                or [descriptor["sequence"]["xorigin"], descriptor["sequence"]["yorigin"]] != row["origin"]:
            raise RuntimeError("Boss art204 sprite descriptor mismatch: " + name)
        frame = descriptor["frames"][0]["name"]
        layer = descriptor["layers"][0]["name"]
        for png in (f"sprites/{name}/{frame}.png", f"sprites/{name}/layers/{frame}/{layer}.png"):
            with Image.open(inside(output, png)) as decoded:
                image = decoded.convert("RGBA")
            if image.size != (row["width"], row["height"]) or sha(image.tobytes()) != row["rgba_sha256"]:
                raise RuntimeError("Boss art204 emitted pixels differ from original: " + png)
            expected_files.add(png)
        expected_files.add(relative)
    if set(manifest.get("files", {})) != expected_files:
        raise RuntimeError("Boss art204 file inventory differs from all15 exact sprite resources")
    actual_files = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}
    if actual_files != expected_files | {"manifest.json", "verification.json"}:
        raise RuntimeError("Boss art204 supplement contains untracked/missing files")
    for relative, expected in manifest["files"].items():
        if sha(inside(output, relative).read_bytes()) != expected:
            raise RuntimeError("Boss art204 emitted file hash mismatch: " + relative)
    proof = read_json(inside(output, "verification.json").read_bytes())
    if proof.get("status") != "PASS" or proof.get("native_execution_performed") is not False \
            or proof.get("physical_device_tested") is not False:
        raise RuntimeError("Boss art204 offline proof misstates verification scope")
    return manifest


def registry_block(rows):
    lines = [BEGIN]
    for row in rows:
        for alias in row["aliases"]:
            lines.append(f'    global.fr_asset_sources[$ "{alias}"]={row["resource"]};')
    return "\n".join(lines + [END])


def installed_registry(text, rows, install):
    block = registry_block(rows)
    if BEGIN in text or END in text:
        if text.count(BEGIN) != 1 or text.count(END) != 1 or text.count(block) != 1:
            raise RuntimeError("Boss art204 partial, duplicate or changed registry block")
    else:
        if not install:
            raise RuntimeError("Boss art204 missing registry block")
        anchor = "function scrFRRegisterAssets() {"
        if text.count(anchor) != 1:
            raise RuntimeError("Boss art204 registry function anchor changed")
        text = text.replace(anchor, anchor + "\n" + block, 1)
    for row in rows:
        for alias in row["aliases"]:
            assignments = re.findall(r'global\.fr_asset_sources\[\$\s*"' + re.escape(alias) + r'"\]\s*=\s*([^;]+);', text)
            if assignments != [row["resource"]]:
                raise RuntimeError("Boss art204 duplicate/mismatched path alias: " + alias)
    return text


def registration(model, name, relative, install):
    matches = [row for row in model["resources"]
               if row["id"]["name"] == name or row["id"]["path"] == relative]
    correct = {"name": name, "path": relative}
    if len(matches) > 1 or (matches and matches[0]["id"] != correct):
        raise RuntimeError("Boss art204 duplicate/mismatched project resource: " + name)
    if not matches:
        if not install:
            raise RuntimeError("Boss art204 missing project resource: " + name)
        model["resources"].append({"id": correct})


def callback_path(project):
    candidates = list((project / "scripts").glob("frCode_Frontier_Bosses_mod_*/*.gml"))
    if len(candidates) != 1:
        raise RuntimeError("Boss art204 staged callback script is ambiguous")
    return candidates[0].relative_to(project).as_posix()


def draw_transform(text):
    if DRAW_NAME_FIXED in text:
        if text.count(DRAW_NAME_FIXED) != 1 or DRAW_NAME in text.replace(DRAW_NAME_FIXED, "", 1):
            raise RuntimeError("Boss art204 native name bridge is duplicated")
        return text
    if "FRONTIER BOSS ART204 NATIVE NAME" in text or text.count(DRAW_NAME) != 1:
        raise RuntimeError("Boss art204 native name consumer anchor changed")
    return text.replace(DRAW_NAME, DRAW_NAME_FIXED, 1)


def native_intro_transform(text):
    if text.count("function scrBossIntro(_boss_index) {") != 1 or text.count(INTRO_GUARD) != 1:
        raise RuntimeError("Boss art204 native intro guard identity changed")
    if INTRO_LEGACY_FIXED in text:
        if text.count(INTRO_LEGACY_FIXED) != 1:
            raise RuntimeError("Boss art204 legacy native intro bridge is duplicated")
        text = text.replace(INTRO_LEGACY_FIXED, INTRO_ANCHOR, 1)
    if INTRO_FIXED in text:
        if text.count(INTRO_FIXED) != 1 or INTRO_ANCHOR in text.replace(INTRO_FIXED, "", 1):
            raise RuntimeError("Boss art204 accepted native intro bridge is duplicated")
        if text.index(INTRO_GUARD) > text.index(INTRO_FIXED):
            raise RuntimeError("Boss art204 native intro flag clear moved before original guards")
        return text
    if "FRONTIER BOSS ART204 ACCEPTED NATIVE INTRO" in text or text.count(INTRO_ANCHOR) != 1 \
            or text.index(INTRO_GUARD) > text.index(INTRO_ANCHOR):
        raise RuntimeError("Boss art204 accepted native intro anchor changed")
    return text.replace(INTRO_ANCHOR, INTRO_FIXED, 1)


def apply(project, output=OUTPUT, source=SOURCE, base_manifest=BASE_MANIFEST):
    project = Path(project).resolve()
    manifest = verify_supplement(project, output, source, base_manifest)
    originals, planned = {}, {}

    def plan(relative, raw, required=False):
        path = inside(project, relative)
        original = path.read_bytes() if path.exists() else None
        if required and original is None:
            raise RuntimeError("Boss art204 missing project consumer: " + relative)
        originals[path] = original
        planned[path] = raw
        return original

    yyp = inside(project, "nuclearthronemobile.yyp")
    yyp_raw = yyp.read_bytes()
    model = read_json(yyp_raw)
    for row in manifest["assets"]:
        name = row["resource"]
        registration(model, name, f"sprites/{name}/{name}.yy", True)
    for relative in manifest["files"]:
        raw = inside(Path(output).resolve(), relative).read_bytes()
        current = plan(relative, raw)
        if current is not None and current != raw:
            raise RuntimeError("Boss art204 existing resource differs: " + relative)
    registry_raw = inside(project, REGISTRY).read_bytes()
    text = registry_raw.decode("utf-8-sig").replace("\r\n", "\n")
    rewritten = installed_registry(text, manifest["assets"], True)
    plan(REGISTRY, registry_raw if rewritten == text else rewritten.encode("utf8"), required=True)
    for relative, transform in ((callback_path(project), callback_transform),
                                ("objects/UberCont/Draw_0.gml", draw_transform),
                                ("scripts/scrBossIntro/scrBossIntro.gml", native_intro_transform)):
        raw = inside(project, relative).read_bytes()
        text = raw.decode("utf-8-sig").replace("\r\n", "\n")
        rewritten = transform(text)
        plan(relative, raw if rewritten == text else rewritten.encode("utf8"), required=True)
    for name, native in ((PRODUCTION, "boss_art204.gml"), (SCRIPT, "boss_art204_tests.gml")):
        relative = f"scripts/{name}/{name}.yy"
        registration(model, name, relative, True)
        template = deepcopy(importer.load_yy(project / "scripts/scrNTTEFullAreas/scrNTTEFullAreas.yy"))
        template["name"] = template["%Name"] = name
        current = plan(relative, json_bytes(template))
        if current is not None:
            if read_json(current) != template:
                raise RuntimeError("Boss art204 existing script metadata differs")
            planned[inside(project, relative)] = current
        maintained = (ROOT / "native" / native).read_bytes()
        current = plan(f"scripts/{name}/{name}.gml", maintained)
        if current is not None and current != maintained:
            raise RuntimeError("Boss art204 existing maintained script differs: " + native)
    plan("nuclearthronemobile.yyp", yyp_raw if model == read_json(yyp_raw) else json_bytes(model), required=True)
    for path, raw in originals.items():
        if (path.read_bytes() if path.exists() else None) != raw:
            raise RuntimeError("Boss art204 input changed during preflight")
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
        verify(project, output, source, base_manifest)
    except Exception:
        for path in reversed(written):
            if originals[path] is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(originals[path])
        for directory in reversed(directories):
            directory.rmdir()
        raise
    return {"resource_count": 15, "alias_count": 30, "regression_script": SCRIPT,
            "changed_paths": [p.relative_to(project).as_posix() for p in written]}


def verify(project, output=OUTPUT, source=SOURCE, base_manifest=BASE_MANIFEST):
    project = Path(project).resolve()
    manifest = verify_supplement(project, output, source, base_manifest)
    model = importer.load_yy(project / "nuclearthronemobile.yyp")
    for row in manifest["assets"]:
        name = row["resource"]
        registration(model, name, f"sprites/{name}/{name}.yy", False)
    for relative, expected in manifest["files"].items():
        if sha(inside(project, relative).read_bytes()) != expected:
            raise RuntimeError("Boss art204 staged resource mismatch: " + relative)
    installed_registry(inside(project, REGISTRY).read_text(encoding="utf-8-sig").replace("\r\n", "\n"),
                       manifest["assets"], False)
    for relative, transform in ((callback_path(project), callback_transform),
                                ("objects/UberCont/Draw_0.gml", draw_transform),
                                ("scripts/scrBossIntro/scrBossIntro.gml", native_intro_transform)):
        text = inside(project, relative).read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        if transform(text) != text:
            raise RuntimeError("Boss art204 missing native intro bridge: " + relative)
    for name, native in ((PRODUCTION, "boss_art204.gml"), (SCRIPT, "boss_art204_tests.gml")):
        registration(model, name, f"scripts/{name}/{name}.yy", False)
        if inside(project, f"scripts/{name}/{name}.gml").read_bytes() != (ROOT / "native" / native).read_bytes():
            raise RuntimeError("Boss art204 staged maintained script differs: " + native)
    return {"status": "PASS", "resource_count": 15, "alias_count": 30,
            "rgba_preserved": True, "origins_preserved": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--emit", type=Path)
    mode.add_argument("--apply", type=Path)
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    project = args.emit or args.apply or args.verify
    result = emit(project, args.output) if args.emit else apply(project, args.output) if args.apply else verify(project, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
