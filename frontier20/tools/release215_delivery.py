"""Source-bound NTTE + NTUF 2.1.5/build110 mobile delivery.

Only named packaging definitions are reused from the pinned historical tool.
Its globals, acceptance, CLI and old test results are never executed. The
current source/VM/native-case gate below owns this release's evidence.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

FRONTIER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FRONTIER / "dependencies/packaging-python"))
WORKSPACE = FRONTIER.parents[1]
HOST = WORKSPACE / "work/ntte-complete"
STAGED = FRONTIER / "staging/project"
MOBILE = FRONTIER / "mobile-release215-build110-20261122"
ANDROID = MOBILE / "android-delivery"
ANDROID_SOURCE = ANDROID / "project"
ANDROID_REFERENCE = HOST / "android-delivery"
IOS_BUILD = MOBILE / "build-ios"
IOS_SOURCE = MOBILE / "ios-project"
ANDROID_BUILD = ANDROID / "build-android"
RUNTIME = Path("C:/ProgramData/GameMakerStudio2-LTS2026/Cache/runtimes/runtime-2026.0.0.23")
USER = Path("C:/Users/ArkinTide/AppData/Roaming/GameMakerStudio2-LTS2026/liutianhao683_5123854")
BASE_IPA = WORKSPACE / "analysis/hardmode-restore-20261112/recovered/qi/outputs/NuclearThroneIOS.ipa"
TOOLCHAIN = WORKSPACE / "analysis/ntultra-20261119/android-toolchain"
ANDROID_JDK = TOOLCHAIN / "jdk-17.0.2"
ANDROID_SDK = TOOLCHAIN / "sdk"
ANDROID_NDK = ANDROID_SDK / "ndk/28.2.13676358"
GRADLE_BIN = WORKSPACE / "analysis/hardmode-restore-20261112/recovered/qi/work/ntte-complete/android-delivery/toolchain/gradle-8.9/bin/gradle.bat"
CANONICAL_PLATFORM_VERSION = DISPLAY_VERSION = COMPILER_VERSION = UPDATE_VERSION = RELEASE_TAG = FILENAME_VERSION = "2.1.5"
INTERNAL = 110
PACKAGE = "com.arkintide.nuclearthronentte"
DISPLAY_NAME = "Nuclear Throne :Territorial Expansion"
CERTIFICATE = "bbf4736b3ccdbc822ffd46d148780a05fec6a20a19d00f67afc3808f596bbe81"
ANDROID_SUPPORT = ("prepare_ntte_chinese_glyphs_20261023.py",)
CONFIG = FRONTIER / "review/release215-config.json"
FROZEN_TOOL = FRONTIER / "tools/release204_delivery.py"
FROZEN_TOOL_SHA256 = "8bf26a83abd3a6f3398e08fe03f6cc821cc5814a9254a363dda95297a3d81b71"
FINAL_CASES = (
    "NewCharacterUnlockTests", "CustomCharacterTests", "SkeletonRevivalTests",
    "RaceNativeLifecycleTests", "RaceProgressionNativeTests",
    "WeaponLoadoutNativeTests", "CrownLoadoutNativeTests", "PetSalamanderTests",
    "FrontierFollowup210Tests", "FrontierUnlockTests",
)
REUSED_FUNCTIONS = (
    "io_path", "copy_tree", "read", "sha", "utc", "local", "write", "snapshot",
    "package_path", "load", "metadata", "compiler_options", "android_package_path",
    "compiler_source_binding", "ios_source_gate", "idle_runner", "run", "compiler_args",
    "ios_build", "zip_member_sha", "ios_build_evidence", "font_inputs", "ipa",
    "android_prepare", "android_source_gate", "aliases", "android_env", "android_build",
    "android_build_evidence", "native_layout", "verify_android", "apk",
    "android_audit_evidence", "alias_evidence", "verify_delivery", "validate_delivery",
)


def _install_packaging_definitions():
    raw = FROZEN_TOOL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == FROZEN_TOOL_SHA256, "Pinned packaging definitions changed"
    text = raw.decode("utf-8-sig")
    replacements = (
        ('#macro GAME_VERSION "2.0.4"', '#macro GAME_VERSION "2.1.5"'),
        ('assert set(deltas) == {option_path}, "iOS compiler copy must change only its version field"',
         'assert set(deltas) == set(), "Canonical iOS compiler input must match source bytes"'),
        ("versionName='2.0.4'", "versionName='2.1.5'"),
        ("versionCode='3000100'", "versionCode='3000110'"),
        ("NTTE+NTUF2.0.4/internal100", "NTTE+NTUF2.1.5/internal110"),
        ('yield Path("R:/toolchain"), Path("N:/android-delivery")',
         'yield TOOLCHAIN, Path("N:/android-delivery")'),
        ('gradle = toolchain / "gradle-8.9/bin/gradle.bat"',
         'gradle = GRADLE_BIN'),
        ('(user / "local_settings.json").write_text(json.dumps(settings, indent=2), encoding="utf8")',
         'settings = android_user_settings(settings)\n    (user / "local_settings.json").write_text(json.dumps(settings, indent=2), encoding="utf8")'),
    )
    for before, after in replacements:
        assert before in text, ("Pinned packaging boundary changed", before)
        text = text.replace(before, after)
    tree = ast.parse(text, str(FROZEN_TOOL))
    definitions = {node.name: node for node in tree.body
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert set(REUSED_FUNCTIONS) <= definitions.keys()
    imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    safe = ast.Module(body=imports + [definitions[name] for name in REUSED_FUNCTIONS], type_ignores=[])
    exec(compile(ast.fix_missing_locations(safe), str(Path(__file__)), "exec"), globals())


_install_packaging_definitions()


def android_user_settings(settings):
    """Rewrite only compiler paths in the private copy; retain signing values."""
    settings = dict(settings)
    paths = {"jdk_location": ANDROID_JDK, "sdk_location": ANDROID_SDK, "ndk_location": ANDROID_NDK}
    for key, path in paths.items():
        full = "machine.Platform Settings.Android.Paths." + key
        assert full in settings, "Retained Android compiler path setting missing"
        settings[full] = path.as_posix()
    return settings


def toolchain_pins():
    """Bind the reused official tools without copying or linking the SDK tree."""
    paths = [ANDROID_JDK / name for name in ("release", "bin/java.exe", "bin/javac.exe")]
    paths += [ANDROID_SDK / name for name in (
        "build-tools/34.0.0/aapt.exe", "build-tools/34.0.0/aapt2.exe",
        "build-tools/34.0.0/zipalign.exe", "build-tools/34.0.0/lib/apksigner.jar",
        "platforms/android-36/android.jar", "ndk/28.2.13676358/source.properties")]
    paths += [GRADLE_BIN, GRADLE_BIN.parent.parent / "lib/gradle-launcher-8.9.jar"]
    assert all(path.is_file() and not path.is_symlink() for path in paths), "Reused Android toolchain is incomplete"
    return {path.relative_to(WORKSPACE).as_posix(): sha(path) for path in paths}


def relative_input(value, prefix=None):
    path = Path(value)
    assert not path.is_absolute() and path.parts and ".." not in path.parts
    if prefix is not None:
        assert path.parts[0] == prefix
    target = (FRONTIER / path).resolve()
    assert target.is_relative_to(FRONTIER.resolve())
    return target


def configured_evidence():
    config = read(CONFIG)
    assert config.get("status") == "READY", "Finalize current 2.1.5 evidence before packaging"
    assert config.get("version") == DISPLAY_VERSION and config.get("internal") == INTERNAL
    for key in ("vm_sha256", "input_sha256", "compile_receipt_sha256", "silent_vm_sha256"):
        assert isinstance(config.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", config[key]), key
    rows = config.get("native_cases")
    assert isinstance(rows, list) and len(rows) == len(FINAL_CASES)
    assert [row["case"] for row in rows] == list(FINAL_CASES)
    for row in rows:
        path = relative_input(row["receipt"], "tests")
        assert path.name == "receipt.json" and path.parent.name == row["case"]
        assert len(path.relative_to(FRONTIER).parts) == 4
        assert re.fullmatch(r"\d{8}T\d+Z", path.parent.parent.name)
        assert sha(path) == row["receipt_sha256"], "Configured native evidence changed"
    assert sha(FRONTIER / "build-windows/last-success.json") == config["compile_receipt_sha256"]
    assert sha(FRONTIER / "build-windows/frontier-silent.win") == config["silent_vm_sha256"]
    if config.get("python_evidence"):
        python = config["python_evidence"]
        path = relative_input(python["path"], "review")
        assert sha(path) == python["sha256"]
        evidence = read(path)
        assert evidence["exit"] == 0 and type(evidence["tests"]) is int and evidence["tests"] > 0
        log = relative_input(evidence["log"], "review")
        assert sha(log) == evidence["log_sha256"]
        output = log.read_text("utf8")
        assert re.search(r"^Ran " + str(evidence["tests"]) + r" tests in ", output, re.MULTILINE)
        assert re.search(r"\nOK\s*$", output) and not re.search(r"^(FAILED|ERROR:|FAIL:)", output, re.MULTILINE)
    return config


def input_state():
    manifest = load("ntuf215_exact_input_manifest", FRONTIER / "tools/build_input_manifest.py")
    current = manifest.snapshot()
    compiled = read(FRONTIER / "build-windows/last-success.json")
    config = configured_evidence()
    assert compiled["status"] == "COMPILED_NOT_PLAYABLE_VERIFIED"
    assert current["input_sha256"] == compiled["input_sha256"] == config["input_sha256"]
    assert sha(FRONTIER / "build-windows/nuclearthronemobile.win") == compiled["vm_sha256"] == config["vm_sha256"]
    assert sha(FRONTIER / "build-windows/compile.log") == compiled["log_sha256"]
    capture = relative_input(compiled["input_manifest"], "analysis")
    before = read(capture)
    assert before["input_sha256"] == current["input_sha256"]
    # snapshot() above has freshly hashed every canonical byte. Reuse that
    # exact result instead of immediately reading the same tree a second time.
    assert before["staged_files"] == current["staged_files"]
    return current, compiled


def required_cases():
    dispatch = (STAGED / "scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml").read_text("utf-8-sig")
    implemented = set(re.findall(
        r'(?m)^[ \t]*if\s*\(\s*scrNTTEFullSmoke(?:Async)?Case\s*\(\s*"([A-Za-z]\w+Tests)"\s*\)\s*\)', dispatch))
    assert set(FINAL_CASES) <= implemented, "Selected case lacks its compiled native harness"
    return list(FINAL_CASES)


def verify_case(path, case, compiled):
    record = read(path)
    assert record["case"] == case and record["status"] == "PASS" and record["exit"] == 0
    assert record["termination_reason"] is None and path.parent.name == case
    assert record["vm_sha256"] == compiled["vm_sha256"] and record["input_sha256"] == compiled["input_sha256"]
    assert record["muted_resources"] > 100 and record["physical_device_tested"] is False
    assert record["desktop"] == "private, never activated"
    assert record["silent_vm_sha256"] == configured_evidence()["silent_vm_sha256"]
    smoke = (path.parent / "smoke.txt").read_text("utf8")
    log = (path.parent / "runner.log").read_text("utf8", errors="replace")
    assert "PASS full internal selected implemented branches" in smoke
    assert "ERROR!!!" not in log and "ERROR!!!" not in smoke and "###game_end###0" in log
    assert not re.search(r"^ERROR(?:\s|$)", smoke, re.MULTILINE)
    # Synchronous cases explicitly identify both logical-rate passes. The two
    # Frontier asynchronous cases own their internal logical-rate coverage.
    if case not in {"FrontierFollowup210Tests", "FrontierUnlockTests"}:
        for rate in (30, 60):
            assert "FULL INTERNAL BEGIN @" + str(rate) in smoke
            assert "CASE " + case in smoke
            assert "FULL INTERNAL END @" + str(rate) in smoke
    assert read(path.parent.parent / "compiled-build.json") == compiled
    assert (path.parent.parent / "compile.log").read_bytes() == (FRONTIER / "build-windows/compile.log").read_bytes()
    artifacts = record["artifacts_sha256"]
    actual = {p.name for p in path.parent.iterdir() if p.is_file()
              and p.name.startswith(("frontier-", "ntuf-")) and p.suffix.lower() in {".png", ".json"}}
    assert isinstance(artifacts, dict) and set(artifacts) == actual
    for name, digest in artifacts.items():
        target = path.parent / name
        assert target.resolve().parent == path.parent.resolve() and sha(target) == digest
    return {"case": case, "receipt": path.relative_to(FRONTIER).as_posix(), "files": snapshot(path.parent)}


def development_regression_binding(current, compiled):
    config = configured_evidence()
    results = []
    for row in config["native_cases"]:
        path = relative_input(row["receipt"], "tests")
        results.append(verify_case(path, row["case"], compiled))
    return {"config": CONFIG.relative_to(FRONTIER).as_posix(), "config_sha256": sha(CONFIG),
            "total": len(results), "cases": required_cases(), "results": results,
            "vm_sha256": compiled["vm_sha256"], "silent_vm_sha256": config["silent_vm_sha256"],
            "input_sha256": current["input_sha256"], "historical_pass_evidence_reused": False,
            "python_evidence": config.get("python_evidence"),
            "evidence_scope": "Ten selected current-VM native cases; multiple runs accepted only for identical source, compile receipt, VM, muted VM and compile log. No historical PASS results contribute.",
            "request_status": {"1": "NOT_REPRODUCED_PENDING_CONTEXT", "2": "VERIFIED_FIXED", "3": "VERIFIED_FIXED"},
            "physical_device_tested": False}


def support_pins():
    names = ("package_ntte_final.py", "final_package_support.py", "final-package-support-provenance.json",
             "audit_ios_vm_builtins.py", "prepare_ntte_chinese_glyphs_20261023.py", "final_special_thanks.py",
             "ntte_icon_assets.py", "android-delivery/prepare_gradle.py", "android-delivery/patch_assets.py",
             "android-delivery/verify_apk.py", "android-delivery/native-controller/Gamepad.java",
             "android-delivery/native-project-receipt.json", "android-delivery/mirrors.init.gradle")
    paths = [HOST / name for name in names]
    paths += [HOST.parent / name for name in ("patch_followup_compat.py", "restore_ipa_fonts.py", "inspect_native_timing.py",
                                             "inspect_timing_bytecode.py", "patch_crisp_credits.py", "render_small_credits.py")]
    icon_root = HOST / "packaging-inputs/icon-20261025-assets"
    catalog = read(icon_root / "manifest.json")
    paths += [HOST / "packaging-inputs/icon-20261025-user-final.png", icon_root / "manifest.json"]
    for item in [*catalog["images"].values(), catalog["windows_ico"]]:
        path = (icon_root / item["file"]).resolve()
        assert path.is_relative_to(icon_root.resolve())
        paths.append(path)
    paths += [BASE_IPA, Path(__file__).resolve(), FROZEN_TOOL, FRONTIER / "tools/build_input_manifest.py", CONFIG]
    config = configured_evidence()
    if config.get("python_evidence"):
        paths.append(relative_input(config["python_evidence"]["path"], "review"))
    assert all(path.is_file() and not path.is_symlink() for path in paths), "Incomplete retained packaging support"
    return {**{path.relative_to(WORKSPACE).as_posix(): sha(path) for path in paths}, **toolchain_pins()}


def accept():
    current, compiled = input_state()
    metadata(STAGED)
    assets = read(FRONTIER / "generated-assets/verification.json")
    assert assets["status"] == "PASS"
    regression = development_regression_binding(current, compiled)
    write(MOBILE / "staged-source-manifest.json", {"utc": utc(), "files": current["staged_files"]})
    write(MOBILE / "native-acceptance.json", {"status": "PASS", "utc": utc(), "version": DISPLAY_VERSION,
          "update_version": UPDATE_VERSION, "internal": INTERNAL, "input_sha256": current["input_sha256"],
          "vm_sha256": compiled["vm_sha256"], "windows_compile_receipt_sha256": sha(FRONTIER / "build-windows/last-success.json"),
          "source_manifest_sha256": sha(MOBILE / "staged-source-manifest.json"),
          "asset_verification_sha256": sha(FRONTIER / "generated-assets/verification.json"),
          "reviewed_support": support_pins(), "development_regression": regression,
          "required_cases": required_cases(), "cases": regression["results"],
          "mobile_device_tested": False, "physical_device_tested": False,
          "requirement_status": {"1": "NOT_REPRODUCED", "2": "VERIFIED_FIXED", "3": "VERIFIED_FIXED"},
          "full_campaign_acceptance_claimed": False})
    print("PASS: current 2.1.5 source, compiled VM and ten native cases bound; packaging eligible.")


def gate():
    accepted = read(MOBILE / "native-acceptance.json")
    current, compiled = input_state()
    assert accepted["status"] == "PASS" and accepted["required_cases"] == required_cases()
    assert accepted["version"] == DISPLAY_VERSION and accepted["update_version"] == UPDATE_VERSION and accepted["internal"] == INTERNAL
    assert accepted["mobile_device_tested"] is False and accepted["full_campaign_acceptance_claimed"] is False
    assert accepted["physical_device_tested"] is False
    assert accepted["requirement_status"] == {"1": "NOT_REPRODUCED", "2": "VERIFIED_FIXED", "3": "VERIFIED_FIXED"}
    assert accepted["input_sha256"] == current["input_sha256"] and accepted["vm_sha256"] == compiled["vm_sha256"]
    assert accepted["development_regression"] == development_regression_binding(current, compiled)
    assert accepted["windows_compile_receipt_sha256"] == sha(FRONTIER / "build-windows/last-success.json")
    assert accepted["source_manifest_sha256"] == sha(MOBILE / "staged-source-manifest.json")
    assert read(MOBILE / "staged-source-manifest.json")["files"] == current["staged_files"]
    assert accepted["asset_verification_sha256"] == sha(FRONTIER / "generated-assets/verification.json")
    assert accepted["reviewed_support"] == support_pins(), "Packaging support changed after acceptance"
    assert accepted["cases"] == accepted["development_regression"]["results"]
    metadata(STAGED)
    return accepted


def plan():
    return {"source": str(STAGED), "host": str(HOST), "workspace": str(WORKSPACE), "writable_root": str(MOBILE),
            "version": DISPLAY_VERSION, "internal": INTERNAL, "android_version_code": 3000000 + INTERNAL,
            "package": PACKAGE, "required_cases": list(FINAL_CASES), "config": str(CONFIG),
            "android_toolchain": str(TOOLCHAIN), "gradle": str(GRADLE_BIN),
            "reused_definition_sha256": FROZEN_TOOL_SHA256, "historical_acceptance_reused": False,
            "executes_builds_in_plan": False, "publishes": False,
            "phases": ["accept", "ios-build", "ipa", "android-prepare", "android-build", "apk", "verify"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("plan", "accept", "ios-build", "ipa", "android-prepare", "android-build", "apk", "verify"))
    phase = parser.parse_args().phase
    if phase == "plan":
        print(json.dumps(plan(), indent=2)); return
    {"accept": accept, "ios-build": ios_build, "ipa": ipa, "android-prepare": android_prepare,
     "android-build": android_build, "apk": apk, "verify": verify_delivery}[phase]()


if __name__ == "__main__":
    main()
