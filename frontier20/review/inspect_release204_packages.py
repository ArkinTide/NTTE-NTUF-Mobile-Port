"""Independent concrete NTTE + NTUF 2.0.4/internal100 APK/IPA audit.

Read-only inspection of real packages, their exact compiler archives and the
root's completed acceptance/delivery receipts. No build, game, stage scan,
full delivery validator, drive mapping, network or publication is invoked.
Only this review's new JSON is written, after every check passes. The frozen
2.0 reader is reused solely for bounded binary/resource inspection, never its
historical acceptance constants or CLI. Phone performance is not tested.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import plistlib
import re
import struct
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT.parent
RELEASE = ROOT / "mobile-release204-20261108"
STAGED = ROOT / "staging/project"
REFERENCE = HOST / "android-delivery"
BASE_IPA = HOST.parents[1] / "outputs/NuclearThroneIOS.ipa"
OUTPUT = ROOT / "review/release204-independent-package-audit.json"
SELECTION = ROOT / "review/release204-cases.json"
VERSION, INTERNAL = "2.0.4", 100
PACKAGE = "com.arkintide.nuclearthronentte"
CERTIFICATE = "bbf4736b3ccdbc822ffd46d148780a05fec6a20a19d00f67afc3808f596bbe81"
READER = ROOT / "review/inspect_release20_packages.py"
READER_SHA = "537bfbb8d1f76b85107f07f1acf56a199e6a884217d737613da8dfa2eb2c966f"
HELPERS = {"assets/.gitignore": "cb2e2a6deb5577f7640e2c6563b647058269b1cdf842139c4a9f01f49e7c5af7"}


def delivery_cases(source, selection):
    """Read the dynamic case declaration without importing delivery tooling."""
    tree = ast.parse(source)
    declarations = [node.value for node in tree.body if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "FINAL_CASES" for target in node.targets)]
    require(len(declarations) == 1, "Delivery case declaration is ambiguous")
    declaration = declarations[0]
    require(isinstance(declaration, ast.Call) and isinstance(declaration.func, ast.Name)
        and declaration.func.id == "selected_cases" and not declaration.args and not declaration.keywords,
        "Delivery must use the reviewed dynamic case selection")
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "selected_cases"]
    expected = ast.parse('''def selected_cases():
    if not CASE_SELECTION.is_file():
        return ()
    selection = json.loads(CASE_SELECTION.read_text(encoding="utf-8-sig"))
    assert selection.get("version") == DISPLAY_VERSION and selection.get("internal") == INTERNAL
    cases = selection.get("cases", [])
    assert isinstance(cases, list) and all(isinstance(case, str) and re.fullmatch(r"[A-Za-z0-9_]+", case) for case in cases)
    assert len(cases) == len(set(cases)), "Duplicate native case"
    return tuple(cases)
''').body[0]
    require(len(functions) == 1 and ast.dump(functions[0]) == ast.dump(expected),
        "Delivery selected_cases implementation differs from the reviewed read-only validator")
    return tuple(selection["cases"])


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def relative(path):
    return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()


def child(base, name):
    require(isinstance(name, str) and name and "\\" not in name, "Invalid relative evidence path")
    value = PurePosixPath(name)
    require(not value.is_absolute() and ".." not in value.parts, "Evidence path escaped its scope")
    result = (base / name).resolve()
    require(result.is_relative_to(base.resolve()), "Evidence path escaped its scope")
    return result


def bound(path, digest, label):
    require(file_sha(path) == digest, label + " hash differs")


def reader():
    bound(READER, READER_SHA, "Frozen binary reader")
    spec = importlib.util.spec_from_file_location("release204_independent_vm_reader", READER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def package_path(platform):
    suffix = "apk" if platform == "Android" else "ipa"
    return RELEASE / "deliverables" / f"NuclearThrone.NTTE-NTUF-{platform}-{VERSION}.{suffix}"


def preflight():
    required = [RELEASE / name for name in (
        "native-acceptance.json", "delivery-verification.json", "staged-source-manifest.json",
        "ios-source-manifest.json", "android-source-manifest.json", "ios-build-receipt.json",
        "android-build-receipt.json", "ipa-package-receipt.json", "apk-package-receipt.json",
        "ios-native-compatibility.json")]
    required += [package_path(platform) for platform in ("Android", "iOS")]
    required += [path.with_suffix(".validation.json") for path in required[-2:]]
    require(all(path.is_file() for path in required), "Actual current packages/receipts are not complete; audit was not started")
    require(not OUTPUT.exists(), "Preserve the completed current independent package audit")


def acceptance_chain():
    delivery, accepted = read(RELEASE / "delivery-verification.json"), read(RELEASE / "native-acceptance.json")
    require(delivery["status"] == accepted["status"] == "PASS", "Root delivery/acceptance is not PASS")
    require(delivery["version"] == delivery["update_version"] == delivery["release_tag"] == VERSION
            and accepted["version"] == accepted["update_version"] == VERSION
            and delivery["internal"] == accepted["internal"] == INTERNAL, "Current release identity differs")
    require(set(delivery["packages"]) == {"Android", "iOS"}, "Current package set differs")
    require(delivery["game_build_save_protocol"] == 3004 and delivery["physical_device_tested"] is False
            and delivery["ios_requires_resigning"] is True and accepted["mobile_device_tested"] is False
            and accepted["full_campaign_acceptance_claimed"] is False, "Unsupported device/save/signing claim")
    bound(RELEASE / "native-acceptance.json", delivery["native_acceptance_sha256"], "Native acceptance")
    bound(RELEASE / "staged-source-manifest.json", accepted["source_manifest_sha256"], "Canonical source manifest")
    bound(ROOT / "build-windows/last-success.json", accepted["windows_compile_receipt_sha256"], "Current Windows compile receipt")
    compiled = read(ROOT / "build-windows/last-success.json")
    require(compiled["vm_sha256"] == accepted["vm_sha256"] and compiled["input_sha256"] == accepted["input_sha256"], "Current VM/input differs")
    bound(ROOT / "build-windows/nuclearthronemobile.win", compiled["vm_sha256"], "Current Windows VM")
    bound(ROOT / "build-windows/compile.log", compiled["log_sha256"], "Current compile log")
    captured = read(child(ROOT, compiled["input_manifest"]))
    canonical = read(RELEASE / "staged-source-manifest.json")["files"]
    require(captured["input_sha256"] == compiled["input_sha256"] and captured["staged_files"] == canonical,
            "Current captured compiler input/canonical file map differs")
    selection = read(SELECTION)
    cases = selection["cases"]
    declared = delivery_cases((ROOT / "tools/release204_delivery.py").read_text(encoding="utf8"), selection)
    require(isinstance(cases,list) and cases and tuple(cases)==tuple(declared), "Actual selected cases differ from delivery tool")
    require(selection["version"] == VERSION and selection["internal"] == INTERNAL
            and len(cases) == len(set(cases)) == len(cases) and accepted["required_cases"] == cases
            and [item["case"] for item in accepted["cases"]] == cases, "Current ordered selected-case scope differs")
    regression = accepted["development_regression"]
    require(regression == delivery["development_regression"] and regression["cases"] == cases
            and regression["total"] == len(cases) and regression["vm_sha256"] == compiled["vm_sha256"]
            and regression["input_sha256"] == compiled["input_sha256"], "Current same-VM evidence binding differs")
    bound(SELECTION, regression["case_selection_sha256"], "Current case selection")
    bound(child(ROOT, regression["report"]), regression["report_sha256"], "Root current development report")
    bound(child(ROOT, regression["config"]), regression["config_sha256"], "Current review config")
    report = read(child(ROOT, regression["report"]))
    require(report["prior_vm_runs"] == [] and report["current_compiled_build"] == compiled
            and report["case_selection_sha256"] == file_sha(SELECTION), "Historical or stale native acceptance contributed")
    run = child(ROOT, regression["run"])
    require(run.parent == (ROOT / "tests").resolve(), "Current native run escaped tests")
    for item in accepted["cases"]:
        receipt_path = child(ROOT, item["receipt"])
        require(receipt_path.parent == run / item["case"], "Native case belongs to another run")
        receipt = read(receipt_path)
        require(receipt["case"] == item["case"] and receipt["status"] == "PASS" and receipt["exit"] == 0
                and receipt["termination_reason"] is None and receipt["vm_sha256"] == compiled["vm_sha256"]
                and receipt["input_sha256"] == compiled["input_sha256"]
                and receipt["physical_device_tested"] is False, "Native case receipt differs")
        for name, digest in item["files"].items():
            bound(child(receipt_path.parent, name), digest, "Native case artifact")
    return delivery, accepted, canonical


def source_chain(platform, accepted, canonical):
    target = "android" if platform == "Android" else "ios"
    source_root = RELEASE / ("android-delivery/project" if target == "android" else "ios-project")
    manifest_path = RELEASE / (target + "-source-manifest.json")
    manifest = read(manifest_path)
    files = manifest["files"]
    if target == "android":
        require(all(name.startswith("project/") for name in files), "Android manifest escaped project")
        files = {name[len("project/"):]: digest for name, digest in files.items()}
    binding = manifest["compiler_input"]
    require(files.keys() == canonical.keys() and binding["platform"] == target
            and binding["canonical_source_manifest_sha256"] == accepted["source_manifest_sha256"]
            and binding["native_acceptance_sha256"] == file_sha(RELEASE / "native-acceptance.json"), "Compiler source chain differs")
    require(sha(json.dumps(files, sort_keys=True, separators=(",", ":")).encode("utf8")) == binding["compiler_input_sha256"],
            "Compiler file-map identity differs")
    differences = {name: {"canonical_sha256": canonical[name], "compiler_sha256": files[name]}
                   for name in sorted(canonical) if canonical[name] != files[name]}
    require(differences == binding["deltas"], "Compiler delta record differs")
    option = f"options/{target}/options_{target}.yy"
    expected = dict(canonical)
    raw = (STAGED / option).read_bytes()
    bound(STAGED / option, canonical[option], "Canonical platform options")
    if target == "ios":
        changed, count = re.subn(r'("option_ios_version"\s*:\s*)"2\.0"', r'\g<1>"2.0.4"', raw.decode("utf8"))
        require(count == 1, "Canonical iOS version anchor differs")
        expected[option] = sha(changed.encode("utf8"))
    else:
        options = json.loads(raw)
        options.update(option_android_display_name="Nuclear Throne :Territorial Expansion",
                       option_android_package_company="arkintide", option_android_package_domain="com",
                       option_android_package_product="nuclearthronentte", option_android_version=VERSION)
        expected[option] = sha((json.dumps(options, ensure_ascii=False, indent=2) + "\n").encode("utf8"))
        alarm = "objects/MakeGame/Alarm_0.gml"
        raw_alarm = (STAGED / alarm).read_bytes()
        bound(STAGED / alarm, canonical[alarm], "Canonical Android app-ID source")
        require(raw_alarm.count(b"com.toncho.nuclearthrone") == 1, "Canonical Android app-ID anchor differs")
        expected[alarm] = sha(raw_alarm.replace(b"com.toncho.nuclearthrone", PACKAGE.encode("ascii")))
        icons_path = RELEASE / "android-delivery/project-icon-receipt.json"
        bound(icons_path, manifest["project_icon_receipt_sha256"], "Android icon receipt")
        icons, catalog = read(icons_path), read(HOST / "packaging-inputs/icon-20261025-assets/manifest.json")
        require(icons["source_sha256"] == catalog["source_sha256"], "Approved icon source changed")
        require(len({row["path"] for row in icons["files"]}) == len(icons["files"]), "Duplicate compiler icon")
        for row in icons["files"]:
            name = row["path"]
            require(name in canonical and name.startswith("options/") and Path(name).suffix.lower() in {".png", ".ico"}, "Unexpected icon compiler delta")
            key = row["kind"] + ":" + "x".join(str(value) for value in row.get("dimensions", []))
            approved = catalog["windows_ico"] if row["kind"] == "ico" else catalog["images"][key]
            require(row["sha256"] == approved["sha256"], "Compiler icon differs from approved catalog")
            bound(child(source_root, name), row["sha256"], "Actual compiler icon")
            expected[name] = row["sha256"]
    require(files == expected, "Compiler source contains unapproved gameplay/resource deltas")
    targeted = ["objects/UberCont/Create_0.gml", "scripts/scrNTTEUpdate/scrNTTEUpdate.gml",
                "scripts/scrFrontier_core_api/scrFrontier_core_api.gml",
                "scripts/scrFrontier_legacy_api/scrFrontier_legacy_api.gml",
                "scripts/scrFrontier_fly_wall_fix/scrFrontier_fly_wall_fix.gml",
                "scripts/scrFrontier_palace_blocks/scrFrontier_palace_blocks.gml",
                "scripts/scrFrontier_menu_repairs/scrFrontier_menu_repairs.gml",
                "scripts/scrFrontier_ammo_compat/scrFrontier_ammo_compat.gml",
                "scripts/scrFrontier_hyperion_projectiles/scrFrontier_hyperion_projectiles.gml",
                "scripts/scrFrontier_registry/scrFrontier_registry.gml",
                "scripts/scrFrontier_post203_fixes/scrFrontier_post203_fixes.gml",
                "scripts/scrFrontier_post203_weather_wall/scrFrontier_post203_weather_wall.gml",
                "scripts/scrFrontier_input204/scrFrontier_input204.gml",
                "scripts/scrFrontier_enemy_visibility_fixes/scrFrontier_enemy_visibility_fixes.gml",
                "scripts/scrNTTEFullOutlineOptionsNative/scrNTTEFullOutlineOptionsNative.gml",
                "scripts/scrFrontier_palace_blocks/scrFrontier_palace_blocks.gml", option]
    targeted=list(dict.fromkeys(targeted))
    for name in targeted:
        bound(child(STAGED, name), canonical[name], "Targeted canonical source")
        bound(child(source_root, name), files[name], "Targeted compiler source")
    game = (source_root / targeted[0]).read_text(encoding="utf8")
    update = (source_root / targeted[1]).read_text(encoding="utf8")
    require('#macro GAME_VERSION "2.0.4"' in game and "#macro GAME_BUILD 3004" in game, "Runtime version/save protocol differs")
    for macro, value in (("NTTE_RELEASE_NUMBER", "100"), ("NTTE_RELEASE_VERSION", '"2.0.4"'), ("NTTE_RELEASE_TAG", '"2.0.4"')):
        require(re.search(r"#macro\s+" + macro + r"\s+" + re.escape(value) + r"(?:\s|$)", update), "Updater metadata differs")
    return {"manifest_sha256": file_sha(manifest_path), "compiler_input_sha256": binding["compiler_input_sha256"],
            "canonical_compiler_deltas": sorted(differences), "targeted_source_files_verified": len(targeted),
            "complete_manifest_map_compared": True, "full_source_tree_rehashed": False}


def native_android(path, archive):
    toolchain = REFERENCE / "toolchain"
    jdks = list(toolchain.glob("jdk-17*"))
    require(len(jdks) == 1, "Android audit JDK is ambiguous")
    jdk, tools = jdks[0], toolchain / "sdk/build-tools/34.0.0"
    env = os.environ.copy()
    env.update(JAVA_HOME=str(jdk), PATH=str(jdk / "bin") + os.pathsep + env.get("PATH", ""))
    env.pop("JAVA_TOOL_OPTIONS", None)
    commands = {
        "signature": [jdk / "bin/java.exe", "-jar", tools / "lib/apksigner.jar", "verify", "--verbose", "--print-certs", path],
        "badging": [tools / "aapt.exe", "dump", "badging", path],
        "alignment": [tools / "zipalign.exe", "-c", "-p", "-v", "4", path],
    }
    outputs = {}
    for name, command in commands.items():
        result = subprocess.run([str(part) for part in command], env=env, capture_output=True, timeout=180)
        require(result.returncode == 0, "Independent actual APK " + name + " verification failed")
        outputs[name] = (result.stdout + result.stderr).decode("utf8", errors="replace")
    require("Verified using v1 scheme (JAR signing): true" in outputs["signature"]
            and "Verified using v2 scheme (APK Signature Scheme v2): true" in outputs["signature"], "APK actual v1/v2 signatures missing")
    require([value.lower() for value in re.findall(r"Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]+)", outputs["signature"])] == [CERTIFICATE], "APK signing identity differs")
    require(f"package: name='{PACKAGE}' versionCode='3000100' versionName='2.0.4'" in outputs["badging"]
            and "sdkVersion:'21'" in outputs["badging"] and "targetSdkVersion:'36'" in outputs["badging"]
            and "application-debuggable" not in outputs["badging"], "Actual Android metadata differs")
    native = read(REFERENCE / "native-project-receipt.json")["native_library_sha256"]
    require(native == read(RELEASE / "android-delivery/native-project-receipt.json")["native_library_sha256"]
            and set(native) == {"arm64-v8a", "armeabi-v7a"}, "Retained Android ABI set differs")
    require({name for name in archive.namelist() if name.startswith("lib/") and name.endswith(".so")}
            == {f"lib/{abi}/libyoyo.so" for abi in native}, "Unexpected APK native library set")
    offsets, alignments = {}, {}
    for abi, digest in native.items():
        item = archive.getinfo(f"lib/{abi}/libyoyo.so")
        require(item.compress_type == zipfile.ZIP_STORED, "Android native library is compressed")
        with path.open("rb") as stream:
            stream.seek(item.header_offset)
            header = stream.read(30)
        require(header[:4] == b"PK\x03\x04", "Bad native ZIP local header")
        first, second = struct.unpack_from("<HH", header, 26)
        offsets[abi] = item.header_offset + 30 + first + second
        require(offsets[abi] % 16384 == 0, "Native ZIP offset is not 16KB aligned")
        data = archive.read(item)
        require(data[:4] == b"\x7fELF" and sha(data) == digest and data[5] == 1, "Actual retained ELF bytes differ")
        wide = data[4] == 2
        pointer = struct.unpack_from("<Q" if wide else "<I", data, 32 if wide else 28)[0]
        size, count = struct.unpack_from("<HH", data, 54 if wide else 42)
        require(pointer + size * count <= len(data), "ELF program header escaped file")
        alignments[abi] = [struct.unpack_from("<Q" if wide else "<I", data, pointer + index * size + (48 if wide else 28))[0]
                           for index in range(count) if struct.unpack_from("<I", data, pointer + index * size)[0] == 1]
    require(alignments["arm64-v8a"] and min(alignments["arm64-v8a"]) >= 16384, "ARM64 ELF LOAD alignment is below16KB")
    return {"package": PACKAGE, "version_name": VERSION, "version_code": 3000100, "min_sdk": 21, "target_sdk": 36,
            "debuggable": False, "fresh_apksigner_v1_v2": True, "fresh_aapt_badging": True, "fresh_zipalign": True,
            "certificate_sha256": CERTIFICATE, "native_libraries_match_retained_baseline": True,
            "native_zip_offsets": offsets, "elf_load_alignments": alignments,
            "fresh_tool_output_sha256": {name: sha(value.encode("utf8")) for name, value in outputs.items()}}


def compiled_assets(compiled, packaged, prefix, game_name, platform):
    helpers = dict(HELPERS)
    if platform == "Android":
        helpers["assets/lang/.gitkeep"] = sha(b"")
    seen, count, sounds = set(), 0, 0
    for item in compiled.infolist():
        if item.is_dir() or not item.filename.startswith("assets/"):
            continue
        name = item.filename[len("assets/"):]
        if item.filename in helpers:
            require(sha(compiled.read(item)) == helpers[item.filename] and prefix + name not in packaged.namelist(), "Explicit compiler helper filter differs")
            seen.add(item.filename)
        elif name != game_name:
            require(compiled.read(item) == packaged.read(prefix + name), "Packaged external compiler resource differs: " + name)
            count += 1
            sounds += name.startswith("sndFR_") and name.endswith(".ogg")
    require(seen == set(helpers), "Compiler helper inventory differs")
    return {"all_non_game_runtime_assets_exact": count, "ntuf_streamed_sounds_exact": sounds,
            "explicit_filtered_nonruntime_helpers": helpers}


def debugger_font_evidence(native_digest):
    path = ROOT / "review/dbg-font-full-range-coverage-204.json"
    evidence = read(path)
    require(evidence["status"] == "PASS" and evidence["range_id"] == 3
            and evidence["version"] == VERSION and evidence["internal"] == INTERNAL
            and evidence["range_name"] == "Chinese Full" and evidence["physical_device_tested"] is False
            and evidence["native_sha256"] == native_digest, "Debugger font native range evidence differs")
    bound(ROOT / "native/menu_repairs.gml", evidence["source_sha256"], "Current debugger glyph-range source")
    bound(STAGED / "datafiles/lang/Silver.ttf", evidence["silver_font_sha256"], "Current debugger Silver font")
    require(evidence["silver_font_cmap_coverage_verified"] is True, "Current debugger cmap was not checked")
    source = (STAGED / "scripts/scrFrontier_menu_repairs/scrFrontier_menu_repairs.gml").read_text(encoding="utf8")
    require('dbg_add_font_glyphs("lang/Silver.ttf",13,3)' in source
            and evidence["source_call"] == 'dbg_add_font_glyphs("lang/Silver.ttf",13,3)',
            "Current native debugger must select Chinese Full range3")
    characters = {ord(char) for row in evidence["labels"] for char in row["text"] if ord(char) > 127}
    require(len(characters) == evidence["all_cjk_characters"] and all(not row["missing"] for row in evidence["labels"])
            and all(any(first <= code <= last for first, last in evidence["ranges"]) for code in characters),
            "Localized Goto labels are not covered by the retained native glyph range")
    return {"evidence_sha256": file_sha(path), "range_id": 3, "range_name": "Chinese Full",
            "localized_labels": len(evidence["labels"]), "covered_cjk_characters": len(characters),
            "silver_font_sha256": evidence["silver_font_sha256"], "current_source_and_font_cmap_bound": True,
            "retained_native_sha256": native_digest, "physical_device_overlay_rendering_tested": False}


def audit_package(platform, delivery, accepted, canonical, binary):
    target, extension = ("android", "apk") if platform == "Android" else ("ios", "ipa")
    path = package_path(platform)
    record = delivery["packages"][platform]
    require(child(ROOT, record["path"]) == path.resolve(), "Unexpected current package path")
    validation_path, receipt_path = path.with_suffix(".validation.json"), RELEASE / (extension + "-package-receipt.json")
    validation, receipt = read(validation_path), read(receipt_path)
    digest = file_sha(path)
    validation_bytes = validation["bytes" if platform == "Android" else "output_bytes"]
    require(digest == record["sha256"] == validation["sha256"] == receipt["package_sha256"]
            and path.stat().st_size == record["bytes"] == validation_bytes, "Actual package size/hash differs")
    bound(validation_path, record["validation_sha256"], "Package validation")
    require(receipt["validation_sha256"] == record["validation_sha256"] and receipt["status"] == "PASS"
            and receipt["native_acceptance_sha256"] == delivery["native_acceptance_sha256"], "Package receipt chain differs")
    bound(receipt_path, record["receipt_sha256"], "Package receipt")
    build_path, source_path = RELEASE / (target + "-build-receipt.json"), RELEASE / (target + "-source-manifest.json")
    build, source = read(build_path), source_chain(platform, accepted, canonical)
    bound(build_path, receipt[target + "_build_receipt_sha256"], "Platform build receipt")
    bound(source_path, receipt[target + "_source_manifest_sha256"], "Platform source manifest")
    require(build["native_acceptance_sha256"] == delivery["native_acceptance_sha256"]
            and build["compiler_input_sha256"] == receipt["compiler_input_sha256"] == source["compiler_input_sha256"]
            and build[target + "_source_manifest_sha256"] == file_sha(source_path), "Fresh platform compiler chain differs")
    archive_path = RELEASE / ("android-delivery/build-android/nuclearthronemobile.zip" if platform == "Android" else "build-ios/nuclearthronemobile.zip")
    bound(archive_path, build["archive_sha256"], "Fresh compiler archive")
    log_path = RELEASE / ("android-delivery/igor-Package.log" if platform == "Android" else "build-ios/compile.log")
    bound(log_path, build["compile_log_sha256"], "Fresh platform compile log")
    with zipfile.ZipFile(path) as package, zipfile.ZipFile(archive_path) as compiler:
        members = binary.safe_archive(package)
        require(compiler.testzip() is None, "Compiler archive CRC differs")
        game_name = "game.droid" if platform == "Android" else "game.ios"
        before_bytes = compiler.read("assets/" + game_name)
        require(sha(before_bytes) == build["game_sha256"], "Fresh source gameplay VM differs")
        if platform == "Android":
            prefix, patches = "assets/", read(RELEASE / "android-delivery/assets-validation.json")
            bound(RELEASE / "android-delivery/assets-validation.json", receipt["assets_validation_sha256"], "Android VM patch receipt")
            bound(RELEASE / "android-delivery/native-project-receipt.json", receipt["native_project_receipt_sha256"], "Android native receipt")
            require(patches["source_game_sha256"] == build["game_sha256"] and validation["package"] == PACKAGE,
                    "Android source VM/app identity differs")
            actual = native_android(path, package)
        else:
            infos = [name for name in package.namelist() if re.fullmatch(r"Payload/[^/]+\.app/Info\.plist", name)]
            require(len(infos) == 1, "IPA application metadata is ambiguous")
            prefix = infos[0][:-len("Info.plist")]
            info = plistlib.loads(package.read(infos[0]))
            require(info["CFBundleIdentifier"] == PACKAGE and info["CFBundleShortVersionString"] == VERSION
                    and info["CFBundleVersion"] == "100" and info["UIFileSharingEnabled"] is True
                    and info["LSSupportsOpeningDocumentsInPlace"] is True, "Actual IPA metadata/Documents differs")
            native_name = prefix + info["CFBundleExecutable"]
            require(package.getinfo(native_name).external_attr >> 16 & 0o111 == 0o111, "IPA executable mode is missing")
            native = package.read(native_name)
            with zipfile.ZipFile(BASE_IPA) as retained:
                names = [name for name in retained.namelist() if name.startswith("Payload/") and name.endswith(".app/nuclearthronemobile")]
                require(len(names) == 1 and native == retained.read(names[0]), "IPA retained native executable differs")
            require(sha(native) == validation["native_sha256"] and not any("/_CodeSignature/" in name for name in package.namelist())
                    and receipt["requires_resigning"] is True and validation["signed"] is False, "IPA signing limitation/native hash differs")
            compatibility = read(RELEASE / "ios-native-compatibility.json")
            bound(RELEASE / "ios-native-compatibility.json", build["compatibility_sha256"], "iOS native API compatibility")
            require(compatibility["native_sha256"] == sha(native) and compatibility["compatible_added_functions_and_extensions"] is True
                    and not compatibility["missing_native_registrations"] and compatibility["extension_chunk_identical"] is True
                    and compatibility["old_extension_count"] == compatibility["new_extension_count"] == 0
                    and compatibility["verified_additional_functions"] == compatibility["additional_vm_functions"], "iOS native API compatibility differs")
            require(validation["source_game_sha256"] == build["game_sha256"]
                    and validation["final_build_receipt_sha256"] == file_sha(build_path), "IPA final compiler binding differs")
            actual = {"bundle_identifier": PACKAGE, "display_version": VERSION, "bundle_version": "100",
                      "native_executable_mode_preserved": True, "native_matches_retained_base_bytes": True,
                      "native_sha256": sha(native), "file_sharing_enabled": True, "opening_documents_in_place": True,
                      "requires_resigning": True, "signed": False,
                      "additional_native_builtins_hash_bound": compatibility["verified_additional_functions"]}
            prefix += "games/"
            patches = validation
        after_bytes = package.read(prefix + game_name)
        expected_game = validation["game_sha256"] if platform == "Android" else validation["merged_game_sha256"]
        require(sha(after_bytes) == expected_game, "Actual packaged VM differs")
        if platform == "Android":
            require(patches["patched_game_sha256"] == expected_game, "Android patched VM hash differs")
        before, after = binary.VM(before_bytes), binary.VM(after_bytes)
        require(VERSION in after.strings, "Current runtime version absent from packaged VM")
        gameplay = binary.gameplay(before, after, patches, platform)
        fonts = binary.cjk_and_titles(after, canonical)
        resources = compiled_assets(compiler, package, prefix, game_name, platform)
        actual.update(unique_safe_zip_members=members, fresh_source_game_sha256=sha(before_bytes),
                      packaged_game_sha256=sha(after_bytes), compiler_input_sha256=source["compiler_input_sha256"])
    return {"path": relative(path), "sha256": digest, "bytes": path.stat().st_size,
            "validation_sha256": file_sha(validation_path), "receipt_sha256": file_sha(receipt_path),
            "source_chain": source, "actual": actual, "gameplay_vm": gameplay, "fonts_and_titles": fonts,
            "runtime_resources": resources}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", nargs="?", choices=("plan", "audit"), default="plan")
    args = parser.parse_args()
    if args.operation == "plan":
        selection = read(SELECTION)
        print(json.dumps({"status": "NOT_REVIEWED", "version": VERSION, "internal": INTERNAL,
            "selected_native_cases": len(selection["cases"]), "completed_audit_exists": OUTPUT.exists(),
            "actual_package_presence": {platform: package_path(platform).is_file() for platform in ("Android", "iOS")},
            "writes": "Only explicit audit writes its immutable package-audit JSON after all checks pass",
            "build_game_network_or_publication_performed": False}, indent=2))
        return
    preflight()
    binary = reader()
    delivery, accepted, canonical = acceptance_chain()
    results = {platform: audit_package(platform, delivery, accepted, canonical, binary) for platform in ("iOS", "Android")}
    debugger = debugger_font_evidence(results["iOS"]["actual"]["native_sha256"])
    regression = accepted["development_regression"]
    # Publication consumes the same exact package-record projection as the
    # root's delivery receipt. Keep all detailed checks in a separate field;
    # the summary is derived only after the actual checks above complete.
    report = {"status": "PASS", "utc": datetime.now(timezone.utc).isoformat(), "version": VERSION, "internal": INTERNAL,
              "scope": __doc__.strip(), "audit_tool_sha256": file_sha(Path(__file__)), "binary_reader_sha256": READER_SHA,
              "delivery_receipt": relative(RELEASE / "delivery-verification.json"),
              "delivery_receipt_sha256": file_sha(RELEASE / "delivery-verification.json"),
              "native_acceptance_sha256": file_sha(RELEASE / "native-acceptance.json"),
              "source_manifest_sha256": accepted["source_manifest_sha256"],
              "development_evidence": {"report": regression["report"], "report_sha256": regression["report_sha256"],
                  "native_selected_cases": regression["total"], "native_run": regression["run"],
                  "vm_sha256": regression["vm_sha256"], "input_sha256": regression["input_sha256"],
                  "python_tests": regression["python_tests"],
                  "scope": str(regression["total"])+" selected current native VM cases and hash-bound Python log; earlier VMs do not contribute."},
              "packages": delivery["packages"], "detailed_package_audit": results,
              "ios_actual_checks": results["iOS"]["actual"], "android_actual_checks": results["Android"]["actual"],
              "save_compatibility_checks": {"canonical_and_both_compiler_version_sources_bound_to_manifests": True,
                  "targeted_source_files_checked_per_platform": results["iOS"]["source_chain"]["targeted_source_files_verified"],
                  "public_update_tag_version": VERSION, "internal": INTERNAL, "game_build_save_protocol": 3004,
                  "android_app_id_and_certificate_retained": True, "ios_app_id_retained": True,
                  "physical_device_save_migration_tested": False},
              "debugger_font_checks": debugger,
              "limitations": ["No Android/iOS physical-device, emulator, full random-campaign, phone FPS or save-migration acceptance.",
                  "The retained native debugger range and font resource are checked; phone overlay rendering is not tested.",
                  "iOS requires re-signing. Root full validation is bound through its receipt, never re-executed by this audit."],
              "physical_device_tested": False, "full_campaign_acceptance_claimed": False,
              "publication_performed_by_this_reviewer": False,
              "limits": {"full_root_validator_called": False, "stage_tree_rehashed": False,
                         "build_game_network_or_publication_performed": False}}
    # An exclusive write preserves successful evidence if two reviewers race.
    with OUTPUT.open("x", encoding="utf8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print("PASS independent current 2.0.4 APK/IPA audit: " + str(OUTPUT))


if __name__ == "__main__":
    main()
