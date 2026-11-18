"""Independent 2.1.4/build109 APK/IPA byte, metadata, font and signature audit.

Import and plan are inert. Only explicit audit writes its new report after both
real packages pass. Frozen binary inspection functions are loaded as AST
definitions; historical globals, acceptance gates and CLIs are never executed.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import plistlib
import re
import struct
import subprocess
import sys
from types import SimpleNamespace
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
HOST = ROOT.parent / "ntte-complete"
RELEASE = ROOT / "mobile-release214-build109-20261118"
STAGED = ROOT / "staging/project"
REFERENCE = HOST / "android-delivery"
BASE_IPA = WORKSPACE / "outputs/NuclearThroneIOS.ipa"
OUTPUT = ROOT / "review/release214-independent-package-audit.json"
SELECTION = ROOT / "review/release214-cases.json"
VERSION, INTERNAL = "2.1.4", 109
PACKAGE = "com.arkintide.nuclearthronentte"
CERTIFICATE = "bbf4736b3ccdbc822ffd46d148780a05fec6a20a19d00f67afc3808f596bbe81"
READER = ROOT / "review/inspect_release20_packages.py"
READER_SHA = "537bfbb8d1f76b85107f07f1acf56a199e6a884217d737613da8dfa2eb2c966f"
FROZEN = ROOT / "review/inspect_release204_packages.py"
FROZEN_SHA = "10093e9a810482c6d5ed3a784484fb4dadc4f7a5b2b75c83c6933494008d5c3e"
HELPERS = {"assets/.gitignore": "cb2e2a6deb5577f7640e2c6563b647058269b1cdf842139c4a9f01f49e7c5af7"}
# Independent scope: package inspection must not accept a same-count selector
# substitution merely because its mutable JSON still contains32 entries.
EXPECTED214_CASES = (
    'FrontierMelee214Tests','FrontierCrash214Tests','FrontierMenus214Tests','FrontierPerformance214Tests','FrontierMovement214Tests',
    'FrontierBubbles213Tests','FrontierCrash213Tests','FrontierWorld213Tests',
    'FrontierPerformance213Tests','FrontierReticle213Tests','FrontierRed212ScheduledTests',
    'FrontierCollision212Tests','FrontierMenus212Tests','FrontierClock212Tests',
    'FrontierClock212LiveTests','FrontierBubblesAttack212Tests',
    'FrontierBluescreenUI204Yes30Tests','FrontierBluescreenUI204No30Tests',
    'FrontierBluescreenUI204Yes60Tests','FrontierBluescreenUI204No60Tests',
    'FrontierPlayerWallTests','FrontierRedConnectivity204Tests','FrontierWallSurface205Tests',
    'FrontierWeaponTests','FrontierWeaponVisualTests','FrontierContinueWriteTests',
    'FrontierContinueReadTests','FrontierLifecycleTests','FrontierWeatherPerformanceTests',
    'VisualOptionsDrawTests','IOSRenderSurfaceTests','QuestLockedNativeTests',
    'QuestFloorNativeTests','QuestTeleporterNativeTests','QuestHubNativeTests',
    'FrontierBubblesStartupATests','FrontierBubblesStartupBTests',
)

REUSED = (
    "require", "sha", "file_sha", "read", "relative", "child", "bound",
    "package_path", "preflight", "acceptance_chain", "source_chain",
    "native_android", "compiled_assets", "debugger_font_evidence", "audit_package",
)


def inspection_definitions():
    raw = FROZEN.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == FROZEN_SHA, "Frozen inspection definitions changed"
    text = raw.decode("utf-8-sig")
    substitutions = (
        ("tools/release204_delivery.py", "tools/release214_delivery.py"),
        ("dbg-font-full-range-coverage-204.json", "dbg-font-full-range-coverage-214.json"),
        ('("NTTE_RELEASE_NUMBER", "100")', '("NTTE_RELEASE_NUMBER", "109")'),
        ("3000100", "3000109"),
        ('== "100"', '== "109"'),
        ('"bundle_version": "100"', '"bundle_version": "109"'),
        ("2.0.4", "2.1.4"),
    )
    for before, after in substitutions:
        assert before in text, ("Frozen inspection anchor changed", before)
        text = text.replace(before, after)
    # The accepted 212 common project already has the canonical iOS version.
    # Its iOS compiler copy must preserve all bytes, including that declaration.
    before = '''        changed, count = re.subn(r'("option_ios_version"\\s*:\\s*)"2\\.0"', r'\\g<1>"2.1.4"', raw.decode("utf8"))
        require(count == 1, "Canonical iOS version anchor differs")
        expected[option] = sha(changed.encode("utf8"))'''
    after = '''        require(json.loads(raw)["option_ios_version"] == VERSION, "Canonical iOS version differs")'''
    assert text.count(before) == 1, "Canonical iOS inspection boundary changed"
    text = text.replace(before, after)
    tree = ast.parse(text, str(FROZEN))
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert set(REUSED) <= functions.keys()
    return ast.Module(body=[functions[name] for name in REUSED], type_ignores=[])


exec(compile(ast.fix_missing_locations(inspection_definitions()), str(__file__), "exec"), globals())
_base_acceptance_chain = acceptance_chain
_base_source_chain = source_chain


def delivery_cases(source, selection):
    """Inspect the current explicit selector without importing delivery code."""
    tree = ast.parse(source)
    declarations = [node.value for node in tree.body if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "FINAL_CASES" for target in node.targets)]
    require(len(declarations) == 1, "Ambiguous current case declaration")
    call = declarations[0]
    require(isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            and call.func.id == "selected_cases" and not call.args and not call.keywords,
            "Current delivery must use its explicit read-only selector")
    expected = ast.parse('''def selected_cases():
    if not CASE_SELECTION.is_file():return ()
    selection=read(CASE_SELECTION)
    assert selection.get('version')==DISPLAY_VERSION and selection.get('internal')==INTERNAL
    cases=selection.get('cases',[])
    assert isinstance(cases,list) and all(isinstance(c,str) and re.fullmatch(r'[A-Za-z0-9_]+',c) for c in cases)
    assert len(cases)==len(set(cases)),'Duplicate current native case'
    return tuple(cases)
''').body[0]
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "selected_cases"]
    require(len(functions) == 1 and ast.dump(functions[0]) == ast.dump(expected), "Unreviewed current case selector")
    require(selection["version"] == VERSION and selection["internal"] == INTERNAL
            and selection["status"] == "READY", "Current selection is not finalized")
    cases = selection["cases"]
    require(isinstance(cases, list) and tuple(cases) == EXPECTED214_CASES,
            "Current reviewed37-case scope differs")
    return tuple(cases)


def acceptance_chain():
    delivery, accepted, canonical = _base_acceptance_chain()
    tool = ROOT / "tools/release214_delivery.py"
    key = tool.relative_to(WORKSPACE).as_posix()
    bound(tool, accepted["reviewed_support"][key], "Current delivery source")
    require(read(ROOT / "review/release214-config.json")["status"] == "READY",
            "Current repair evidence is not finalized")
    return delivery, accepted, canonical


def source_chain(platform, accepted, canonical):
    result = _base_source_chain(platform, accepted, canonical)
    source_root = RELEASE / ("android-delivery/project" if platform == "Android" else "ios-project")
    current = (
        "scripts/scrFrontier_performance214/scrFrontier_performance214.gml",
        "scripts/scrFrontier_crash214/scrFrontier_crash214.gml",
        "scripts/scrFrontier_menus214/scrFrontier_menus214.gml",
        "scripts/scrFrontier_movement214/scrFrontier_movement214.gml",
        "scripts/scrFrontier_world213/scrFrontier_world213.gml",
        "scripts/scrFrontier_crash213/scrFrontier_crash213.gml",
        "scripts/scrFrontier_reticle213/scrFrontier_reticle213.gml",
        "scripts/scrFrontier_bubbles213/scrFrontier_bubbles213.gml",
        "scripts/scrFrontier_performance213/scrFrontier_performance213.gml",
        "scripts/scrFrontier_alarms213/scrFrontier_alarms213.gml",
        "scripts/scrFrontier_clock212/scrFrontier_clock212.gml",
        "scripts/scrFRActors/scrFRActors.gml",
        "scripts/scrOptionsUpdate/scrOptionsUpdate.gml",
        "scripts/frCode_Frontier_Projectiles2_mod_3605a3e6c8/frCode_Frontier_Projectiles2_mod_3605a3e6c8.gml",
        "scripts/frCode_AugmentImpactWrists_skill_19a3fdffe9/frCode_AugmentImpactWrists_skill_19a3fdffe9.gml",
        "scripts/scrNTTEFullBaseFrameNative/scrNTTEFullBaseFrameNative.gml",
        "scripts/scrNTTEFullMergedMotion/scrNTTEFullMergedMotion.gml",
        "scripts/scrDrawSpiral/scrDrawSpiral.gml",
        "objects/UberCont/Draw_75.gml",
        "objects/JoystickAttack/Other_10.gml",
        "objects/MenuOptions/Other_20.gml",
        "objects/TopCont/Draw_0.gml",
        "scripts/scrDrawMobileControls/scrDrawMobileControls.gml",
        "scripts/scrSave/scrSave.gml",
        "objects/FiredMaggot/Collision_Player.gml",
        "objects/FiredMaggot/Collision_Wall.gml",
        "scripts/scrNTTEFullWeaponDrop/scrNTTEFullWeaponDrop.gml",
        "scripts/scrNTTEFullQuestHubNative/scrNTTEFullQuestHubNative.gml",
        "scripts/scrNTTEFullQuestFloorNative/scrNTTEFullQuestFloorNative.gml",
        "scripts/scrNTTEFullQuestTeleporterNative/scrNTTEFullQuestTeleporterNative.gml",
        "scripts/scrNTTEFullCrystalHeart/scrNTTEFullCrystalHeart.gml",
        "scripts/scrFrontier_menus212/scrFrontier_menus212.gml",
        "scripts/scrFrontier_bubbles_preferences/scrFrontier_bubbles_preferences.gml",
        "scripts/scrNTTESolidWalls/scrNTTESolidWalls.gml",
        "objects/Slash/Collision_Wall.gml",
        "scripts/scrNTTEFullRedAreaNative/scrNTTEFullRedAreaNative.gml",
    )
    for name in current:
        bound(child(STAGED, name), canonical[name], "Current targeted repair source")
        bound(child(source_root, name), canonical[name], "Current compiler repair source")
    result["current_repair_source_files_verified"] = list(current)
    return result


def reader():
    """Load only pure bounded reader definitions, never old acceptance globals."""
    bound(READER, READER_SHA, "Frozen binary reader")
    tree = ast.parse(READER.read_text("utf-8-sig"), str(READER))
    wanted = {"require", "sha", "file_sha", "read", "safe_archive", "gameplay", "cjk_and_titles"}
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted
                   or isinstance(node, ast.ClassDef) and node.name == "VM"]
    require({node.name for node in definitions} == wanted | {"VM"}, "Frozen binary reader lacks definitions")
    imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    namespace = {"__name__": "ntuf213_bounded_binary_reader", "__file__": str(READER), "ROOT": ROOT}
    exec(compile(ast.fix_missing_locations(ast.Module(body=imports + definitions, type_ignores=[])),
                 str(READER), "exec"), namespace)
    return SimpleNamespace(**namespace)


def audit():
    preflight()
    binary = reader()
    delivery, accepted, canonical = acceptance_chain()
    results = {platform: audit_package(platform, delivery, accepted, canonical, binary)
               for platform in ("iOS", "Android")}
    debugger = debugger_font_evidence(results["iOS"]["actual"]["native_sha256"])
    regression = accepted["development_regression"]
    report = {"status": "PASS", "utc": datetime.now(timezone.utc).isoformat(),
              "version": VERSION, "internal": INTERNAL, "scope": __doc__.strip(),
              "audit_tool_sha256": file_sha(Path(__file__)), "binary_reader_sha256": READER_SHA,
              "frozen_inspection_definitions_sha256": FROZEN_SHA,
              "delivery_receipt": relative(RELEASE / "delivery-verification.json"),
              "delivery_receipt_sha256": file_sha(RELEASE / "delivery-verification.json"),
              "native_acceptance_sha256": file_sha(RELEASE / "native-acceptance.json"),
              "source_manifest_sha256": accepted["source_manifest_sha256"],
              "development_evidence": {"report": regression["report"], "report_sha256": regression["report_sha256"],
                  "native_selected_cases": regression["total"], "native_run": regression["run"],
                  "vm_sha256": regression["vm_sha256"], "input_sha256": regression["input_sha256"],
                  "python_tests": regression["python_tests"],
                  "scope": "37 selected current native VM cases and current source-bound Python log; prior VMs do not contribute."},
              "packages": delivery["packages"], "detailed_package_audit": results,
              "ios_actual_checks": results["iOS"]["actual"], "android_actual_checks": results["Android"]["actual"],
              "save_compatibility_checks": {"canonical_and_both_compiler_version_sources_bound_to_manifests": True,
                  "targeted_source_files_checked_per_platform": results["iOS"]["source_chain"]["targeted_source_files_verified"],
                  "public_update_tag_version": VERSION, "internal": INTERNAL, "game_build_save_protocol": 3004,
                  "android_app_id_and_certificate_retained": True, "ios_app_id_retained": True,
                  "physical_device_save_migration_tested": False},
              "debugger_font_checks": debugger,
              "limitations": ["No physical Android/iOS, full random campaign, phone FPS or save migration acceptance.",
                  "Native font ranges and current glyph resources are checked; phone overlay rendering is not tested.",
                  "iOS requires re-signing; no new native Xcode executable is built."],
              "physical_device_tested": False, "full_campaign_acceptance_claimed": False,
              "publication_performed_by_this_reviewer": False,
              "limits": {"full_root_validator_called": False, "stage_tree_rehashed": False,
                         "historical_globals_or_gate_executed": False,
                         "build_game_network_or_publication_performed": False}}
    with OUTPUT.open("x", encoding="utf8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print("PASS independent 2.1.4 APK/IPA audit: " + str(OUTPUT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("plan", "audit"), default="plan", nargs="?")
    args = parser.parse_args()
    if args.operation == "audit":
        audit()
    else:
        print(json.dumps({"status": "NOT_REVIEWED", "version": VERSION, "internal": INTERNAL,
                          "selected_native_cases": len(read(SELECTION)["cases"]),
                          "completed_audit_exists": OUTPUT.exists(),
                          "actual_package_presence": {platform: package_path(platform).is_file()
                                                      for platform in ("Android", "iOS")},
                          "writes": "Explicit audit writes only its new JSON after all real checks pass",
                          "build_game_network_or_publication_performed": False}, indent=2))


if __name__ == "__main__":
    main()
