"""Read-only actual-package audit; never build, run the game, scan stage, or upload.

Only this audit's JSON report is written, after both actual installers pass.
The full canonical stage gates belong to the root delivery process.
"""
from __future__ import annotations

import bisect
from collections import OrderedDict
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import plistlib
import re
import struct
import subprocess
import sys
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT.parent
RELEASE = ROOT / "mobile-release20-20261106"
PACKAGE = "com.arkintide.nuclearthronentte"
BASE_IPA = HOST.parents[1] / "outputs/NuclearThroneIOS.ipa"
REFERENCE = HOST / "android-delivery"
EXPECTED_VM = "49053e0ea4c46790a1acf26216de624a76ec134ce4ba381da91f317c367a568f"
EXPECTED_INPUT = "8c316bb80b353c6ade0e151cac35b09f29db92d70478dd5b737c9963e2625e1c"
EXPECTED_REPORT = "387565b672be19cf305cb1e90a4e2384b3d43f3220fdee693844625c6551f8fe"
CERTIFICATE = "bbf4736b3ccdbc822ffd46d148780a05fec6a20a19d00f67afc3808f596bbe81"
OLD_PACKAGES = {
    "Android": "f7c38ac38698e76b5627b2ad8cff19599c936d5258ce9f942a2f2787acd4d475",
    "iOS": "00a948e485dc3dbdd21880f16bb2c2b501fddef4c718d6b2f5989b36e572f46f",
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


class VM:
    """Minimal independent bounded IFF/CODE/resource reader; no mutators."""

    def __init__(self, data):
        self.data = data
        require(data[:4] == b"FORM" and self.u32(4) == len(data) - 8, "Invalid VM FORM")
        self.parts = {}
        position = 8
        while position < len(data):
            require(position + 8 <= len(data), "Truncated VM chunk header")
            tag, size = data[position:position + 4], self.u32(position + 4)
            require(tag not in self.parts and position + 8 + size <= len(data), "Invalid/duplicate VM chunk")
            self.parts[tag] = (position + 8, size)
            position += size + 8
        require(position == len(data), "Invalid final VM boundary")
        self.codes = {}
        start = self.parts[b"CODE"][0]
        for index in range(self.u32(start)):
            pointer = self.u32(start + 4 + index * 4)
            name = self.string(self.u32(pointer))
            extent = (pointer + 12 + self.i32(pointer + 12), self.u32(pointer + 4))
            require(name not in self.codes and 0 <= extent[0] <= extent[0] + extent[1] <= len(data), "Invalid CODE record")
            self.codes[name] = extent
        self.references = {}
        start = self.parts[b"FUNC"][0]
        for index in range(self.u32(start)):
            pointer = start + 4 + index * 12
            name, count, reference = self.string(self.u32(pointer)), self.u32(pointer + 4), self.u32(pointer + 8)
            for _ in range(count):
                self.references[reference] = ("function", name)
                reference += self.u32(reference)
        start, size = self.parts[b"VARI"]
        for pointer in range(start + 12, start + size - 19, 20):
            if not self.u32(pointer):
                break
            name, reference = self.string(self.u32(pointer)), self.u32(pointer + 16) + 4
            for _ in range(self.u32(pointer + 12)):
                self.references[reference] = ("variable", name)
                delta = self.u32(reference) & 0xfffffff
                reference += delta - 0x10000000 if delta & 0x8000000 else delta
        self.reference_positions = sorted(self.references)
        start = self.parts[b"STRG"][0]
        self.strings = {self.string(self.u32(start + 4 + index * 4) + 4) for index in range(self.u32(start))}
        self.pages = OrderedDict()

    def u32(self, position):
        require(0 <= position <= len(self.data) - 4, "VM pointer outside data")
        return struct.unpack_from("<I", self.data, position)[0]

    def i32(self, position):
        require(0 <= position <= len(self.data) - 4, "VM signed pointer outside data")
        return struct.unpack_from("<i", self.data, position)[0]

    def string(self, position):
        require(0 <= position < len(self.data), "VM string pointer outside data")
        return self.data[position:self.data.index(0, position)].decode("utf8")

    def chunk(self, tag):
        start, size = self.parts[tag]
        return self.data[start:start + size]

    def table(self, tag):
        start = self.parts[tag][0]
        rows = {}
        for index in range(self.u32(start)):
            pointer = self.u32(start + 4 + index * 4)
            name = self.string(self.u32(pointer))
            require(name not in rows, "Duplicate VM resource name")
            rows[name] = pointer
        return rows

    def image(self, page):
        if page in self.pages:
            self.pages.move_to_end(page)
            return self.pages[page]
        start = self.parts[b"TXTR"][0]
        require(0 <= page < self.u32(start), "Invalid texture page")
        record = self.u32(start + 4 + page * 4)
        size, width, height = struct.unpack_from("<III", self.data, record + 8)
        pointer = self.u32(record + 24)
        require(0 < size and pointer + size <= len(self.data), "Invalid texture bytes")
        image = Image.open(io.BytesIO(self.data[pointer:pointer + size])).convert("RGBA")
        require(image.size == (width, height), "Texture dimensions disagree")
        self.pages[page] = image
        if len(self.pages) > 4:
            self.pages.popitem(last=False)
        return image

    def texture(self, pointer):
        return struct.unpack_from("<10Hh", self.data, pointer)

    def sprite_frame(self, pointer):
        sx, sy, sw, sh, tx, ty, tw, th, bw, bh, page = self.texture(pointer)
        require(0 <= tx <= tx + tw <= bw and 0 <= ty <= ty + th <= bh, "Invalid sprite target crop")
        crop = self.image(page).crop((sx, sy, sx + sw, sy + sh))
        if crop.size != (tw, th):
            crop = crop.resize((tw, th), Image.Resampling.NEAREST)
        return (tx, ty, tw, th, bw, bh), crop.tobytes()


def safe_archive(archive):
    names = archive.namelist()
    require(len(names) == len(set(names)) and archive.testzip() is None, "ZIP duplicates or CRC failure")
    for name in names:
        path = PurePosixPath(name)
        require(not path.is_absolute() and ".." not in path.parts and "\\" not in name, "Unsafe archive path")
        lower = name.lower()
        require(not lower.endswith((".p12", ".pfx", ".jks", ".keystore", ".key", ".pem", ".gml", ".yyp", ".mobileprovision")),
                "Unexpected private/source material in installer")
        require(not any(part in {"signing", "gradle-home", "toolchain"} for part in path.parts), "Private build directory in installer")
        require(path.name.lower() not in {"identity.json", "local_settings.json", "gradle.properties", "key.properties", "signing.properties", "licence.plist", "devices.json"},
                "Unexpected private build configuration in installer")
    return len(names)


def gameplay(before, after, validation, platform):
    require(before.parts == after.parts and before.codes == after.codes, "Packaged VM resource/CODE layout differs")
    for tag in (b"EXTN", b"OBJT", b"SCPT", b"GLOB", b"SOND", b"AUDO", b"STRG"):
        require(before.chunk(tag) == after.chunk(tag), "Packaged VM changed gameplay resource chunk " + tag.decode())
    changed = {"gml_Object_ButtonDiscord_Draw_0", "gml_Object_ButtonDiscord_Step_0",
               "gml_Object_ButtonDiscord_Other_10", "gml_Script_scrNTTEFullMenuDefine"}
    timing = validation["timing_and_title_alignment"]
    sites = [timing["cjk_anchor_operand"]]
    if platform == "iOS":
        changed |= {"gml_Object_MenuOptions_Other_20", "gml_Script_scrDrawMobileControls", "gml_Object_Console_Other_10"}
        sites += [timing["vsync_timing_operand"], validation["volume_controls"]["hud_hint_guard"]]
    changed.update(name for name, (start, size) in before.codes.items() if any(start <= site < start + size for site in sites))
    ignored = {before.codes[name] for name in changed}
    verified, records, references = set(), 0, 0
    for name, (start, size) in before.codes.items():
        if (start, size) in ignored:
            continue
        records += 1
        if (start, size) in verified:
            continue
        left, right = bytearray(before.data[start:start + size]), bytearray(after.data[start:start + size])
        positions = before.reference_positions[bisect.bisect_left(before.reference_positions, start):bisect.bisect_left(before.reference_positions, start + size)]
        for position in positions:
            require(before.references[position] == after.references.get(position), "Gameplay reference identity changed: " + name)
            left[position - start:position - start + 4] = right[position - start:position - start + 4]
            references += 1
        require(left == right, "Non-UI gameplay bytecode changed: " + name)
        verified.add((start, size))
    first, second = before.table(b"SPRT"), after.table(b"SPRT")
    require(first == second, "Packaged sprite identities changed")
    sprites = sorted(name for name in first if name.startswith("sprFR"))
    require(len(sprites) >= 1868, "NTUF sprite resource set incomplete")
    sounds = [name for name in before.table(b"SOND") if name.startswith("sndFR_")]
    require(len(sounds) == 160, "NTUF native sound resource set incomplete")
    frame_jobs = []
    for name in sprites:
        pointer = first[name]
        count = before.u32(pointer + 84)
        require(count == after.u32(pointer + 84) and count > 0, "NTUF sprite frames changed")
        for index in range(count):
            a = before.u32(pointer + 88 + index * 4)
            b = after.u32(pointer + 88 + index * 4)
            frame_jobs.append((before.texture(a)[-1], after.texture(b)[-1], name, a, b))
    # Group by actual texture page so this read-only audit decodes each packed
    # PNG once without retaining every 4096px atlas while root is compiling.
    for _, _, name, a, b in sorted(frame_jobs):
        require(before.sprite_frame(a) == after.sprite_frame(b), "NTUF sprite rendered pixels changed: " + name)
    return {"non_ui_code_records": records, "unique_code_extents": len(verified),
            "semantic_reference_operands": references, "unchanged_gameplay_chunks": ["EXTN", "OBJT", "SCPT", "GLOB", "SOND", "AUDO", "STRG"],
            "ntuf_sprites": len(sprites), "ntuf_frames_rendered_pixels_verified": len(frame_jobs),
            "ntuf_native_sound_resources_in_unchanged_SOND_AUDO": len(sounds)}


def cjk_and_titles(game, source_manifest):
    source = ROOT / "staging/project"
    font_table = game.table(b"FONT")
    dictionary_text = (ROOT / "native/localization_data.gml").read_text(encoding="utf8")
    match = re.search(r"static _data=(\{.*?\});\s*return", dictionary_text, re.DOTALL)
    require(match is not None, "Cannot read current NTUF localization dictionary")
    dictionary = json.loads(match[1])
    require(len(dictionary) == 1174 and set(dictionary.values()).issubset(game.strings), "Actual NTUF Chinese dictionary strings absent")
    needed = {ord(character) for value in dictionary.values() for character in value if ord(character) > 127 and not character.isspace()}
    def bound(relative):
        path = source / relative
        require(file_sha(path) == source_manifest[relative], "Targeted font/title source hash changed: " + relative)
        return path
    fonts = []
    for name, minimum in (("fntCJK", 5483), ("fntCJKBig", 5457)):
        pointer = font_table[name]
        require(struct.unpack_from("<ff", game.data, pointer + 32) == (1.0, 1.0), "CJK font remains scaled")
        raw = bound(f"fonts/{name}/{name}.yy").read_text(encoding="utf-8-sig")
        expected = {}
        for candidate in re.finditer(r'"(\d+)"\s*:\s*(?=\{)', raw):
            expected[int(candidate[1])] = json.loads(re.sub(r",\s*}", "}", raw[candidate.end():raw.index("}", candidate.end()) + 1]))
        require(len(expected) >= minimum and needed.issubset(expected), "CJK glyph coverage incomplete")
        image = Image.open(bound(f"fonts/{name}/{name}.png")).convert("RGBA")
        sx, sy, sw, sh, tx, ty, tw, th, bw, bh, page = game.texture(game.u32(pointer + 28))
        require((sw, sh) == (tw, th) == image.size and (tx, ty) == (0, 0), "CJK atlas is not full resolution")
        require(game.u32(pointer + 56) == len(expected), "CJK glyph count changed")
        actual_image = game.image(page)
        for index in range(len(expected)):
            item = game.u32(pointer + 60 + index * 4)
            char, x, y, width, height, shift, offset, kerning = struct.unpack_from("<5H2hH", game.data, item)
            glyph = expected[char]
            require(kerning == 0 and (x, y, width, height, shift, offset) == tuple(glyph[key] for key in ("x", "y", "w", "h", "shift", "offset")), "CJK glyph geometry changed")
            require(actual_image.crop((sx + x, sy + y, sx + x + width, sy + y + height)).tobytes()
                    == image.crop((x, y, x + width, y + height)).tobytes(), "CJK glyph pixels changed")
        fonts.append({"font": name, "glyphs": len(expected), "scale": 1, "all_glyph_geometry_and_pixels_match": True})
    relative = "sprites/sprBignameAtlas/sprBignameAtlas.yy"
    frames = re.findall(r'"\$GMSpriteFrame":"v1","%Name":"([^"]+)"', bound(relative).read_text(encoding="utf-8-sig"))
    sprite = game.table(b"SPRT")["sprBignameAtlas"]
    require(len(frames) == game.u32(sprite + 84) == 3, "Boss title atlas count changed")
    for index, frame in enumerate(frames):
        bounds, pixels = game.sprite_frame(game.u32(sprite + 88 + index * 4))
        x, y, width, height, _, _ = bounds
        image = Image.open(bound(f"sprites/sprBignameAtlas/{frame}.png")).convert("RGBA")
        require(pixels == image.crop((x, y, x + width, y + height)).tobytes(), "Boss title atlas pixels differ")
    return {"fonts": fonts, "ntuf_dictionary_phrases": len(dictionary), "required_non_ascii_characters": len(needed), "actual_vm_dictionary_present": True, "boss_title_frames_pixels_verified": 3}


def compiled_assets(compiled, packaged, prefix, game_name):
    count, sounds = 0, 0
    for item in compiled.infolist():
        if item.is_dir() or not item.filename.startswith("assets/"):
            continue
        name = item.filename[len("assets/"):]
        if name == game_name:
            continue
        require(compiled.read(item) == packaged.read(prefix + name), "Compiled external resource differs: " + name)
        count += 1
        sounds += name.startswith("sndFR_") and name.endswith(".ogg")
    return {"all_non_game_compiled_assets_exact": count, "ntuf_streamed_sounds_exact": sounds}


def run_tool(name, command, env):
    result = subprocess.run([str(part) for part in command], env=env, capture_output=True, timeout=120)
    require(result.returncode == 0, name + " independent verification failed (" + str(result.returncode) + ")")
    return (result.stdout + result.stderr).decode("utf8", errors="replace")


def android_native(path, archive, validation, build):
    toolchain = REFERENCE / "toolchain"
    jdk = next(toolchain.glob("jdk-17*"))
    tools = toolchain / "sdk/build-tools/34.0.0"
    env = os.environ.copy()
    env.update(JAVA_HOME=str(jdk), PATH=str(jdk / "bin") + os.pathsep + env["PATH"])
    env.pop("JAVA_TOOL_OPTIONS", None)
    signature = run_tool("apksigner", [jdk / "bin/java.exe", "-jar", tools / "lib/apksigner.jar", "verify", "--verbose", "--print-certs", path], env)
    require("Verified using v1 scheme (JAR signing): true" in signature, "APK v1 signature missing for Android 21")
    require("Verified using v2 scheme (APK Signature Scheme v2): true" in signature, "APK v2 signature missing")
    certs = re.findall(r"Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]+)", signature)
    require(len(certs) == 1 and certs[0].lower() == CERTIFICATE == validation["signing_certificate_sha256"], "APK signing identity changed")
    badging = run_tool("aapt", [tools / "aapt.exe", "dump", "badging", path], env)
    require("package: name='" + PACKAGE + "' versionCode='3000096' versionName='2.0'" in badging, "Actual APK version/identity incorrect")
    require("sdkVersion:'21'" in badging and "targetSdkVersion:'36'" in badging and "application-debuggable" not in badging, "Unexpected Android platform metadata")
    run_tool("zipalign", [tools / "zipalign.exe", "-c", "-p", "-v", "4", path], env)
    retained = read(REFERENCE / "native-project-receipt.json")["native_library_sha256"]
    prepared = read(RELEASE / "android-delivery/native-project-receipt.json")["native_library_sha256"]
    require(retained == prepared and set(retained) == {"arm64-v8a", "armeabi-v7a"}, "Retained Android native ABI set differs")
    offsets, alignments = {}, {}
    for abi, digest in retained.items():
        entry = archive.getinfo("lib/" + abi + "/libyoyo.so")
        require(entry.compress_type == zipfile.ZIP_STORED, "Native library is compressed")
        with path.open("rb") as handle:
            handle.seek(entry.header_offset)
            header = handle.read(30)
        require(header[:4] == b"PK\x03\x04", "Invalid local ZIP header")
        first, second = struct.unpack_from("<HH", header, 26)
        offsets[abi] = entry.header_offset + 30 + first + second
        require(offsets[abi] % 16384 == 0, "Native ZIP data is not 16KB aligned")
        data = archive.read(entry)
        require(data[:4] == b"\x7fELF" and sha(data) == digest, "Actual Android native runner differs")
        is64 = data[4] == 2
        table = struct.unpack_from("<Q" if is64 else "<I", data, 32 if is64 else 28)[0]
        size, count = struct.unpack_from("<HH", data, 54 if is64 else 42)
        alignments[abi] = [struct.unpack_from("<Q" if is64 else "<I", data, table + index * size + (48 if is64 else 28))[0]
                           for index in range(count) if struct.unpack_from("<I", data, table + index * size)[0] == 1]
    require(min(alignments["arm64-v8a"]) >= 16384, "ARM64 ELF load alignment below 16KB")
    return {"aapt_identity_version_verified": True, "version_code": 3000096, "display_version": "2.0", "signature_v1_verified": True, "signature_v2_verified": True,
            "public_certificate_sha256": CERTIFICATE, "retained_native_hashes": retained, "native_zip_offsets": offsets,
            "elf_load_alignments": alignments, "independent_zipalign_pass": True}


def package(platform, delivery, acceptance, source_manifest):
    ext = "apk" if platform == "Android" else "ipa"
    path = RELEASE / "deliverables" / f"NuclearThrone.NTTE-NTUF-{platform}-2.0.{ext}"
    require(path.resolve() == (ROOT / delivery["packages"][platform]["path"]).resolve(), "Unexpected final package path")
    digest = file_sha(path)
    require(digest == delivery["packages"][platform]["sha256"] and digest != OLD_PACKAGES[platform], "New actual package is stale or differs from final receipt")
    old = ROOT / "mobile/deliverables" / path.name
    require(file_sha(old) == OLD_PACKAGES[platform], "Original package preservation failed")
    validation_path = path.with_suffix(".validation.json")
    validation = read(validation_path)
    receipt_path = RELEASE / (ext + "-package-receipt.json")
    receipt = read(receipt_path)
    require(file_sha(validation_path) == delivery["packages"][platform]["validation_sha256"] == receipt["validation_sha256"], "Validation receipt binding changed")
    require(file_sha(receipt_path) == delivery["packages"][platform]["receipt_sha256"] and receipt["status"] == "PASS", "Package receipt binding changed")
    require(digest == validation["sha256"] == receipt["package_sha256"] and path.stat().st_size == validation.get("bytes", validation.get("output_bytes")), "Actual package size/hash mismatch")
    require(receipt["native_acceptance_sha256"] == delivery["native_acceptance_sha256"], "Package native acceptance mismatch")
    target = "android" if ext == "apk" else "ios"
    build_path = RELEASE / (target + "-build-receipt.json")
    build = read(build_path)
    require(file_sha(build_path) == receipt[target + "_build_receipt_sha256"] and build["native_acceptance_sha256"] == delivery["native_acceptance_sha256"], "Build receipt mismatch")
    require(build["compiler_input_sha256"] == receipt["compiler_input_sha256"], "Compiler input mismatch")
    manifest = RELEASE / (target + "-source-manifest.json")
    manifest_record = read(manifest)
    require(file_sha(manifest) == receipt[target + "_source_manifest_sha256"] == build[target + "_source_manifest_sha256"]
            and manifest_record["compiler_input"]["canonical_source_manifest_sha256"] == acceptance["source_manifest_sha256"]
            and manifest_record["compiler_input"]["compiler_input_sha256"] == build["compiler_input_sha256"]
            and manifest_record["compiler_input"]["native_acceptance_sha256"] == delivery["native_acceptance_sha256"], "Compiler source manifest mismatch")
    compiled_path = RELEASE / ("android-delivery/build-android/nuclearthronemobile.zip" if ext == "apk" else "build-ios/nuclearthronemobile.zip")
    require(file_sha(compiled_path) == build["archive_sha256"], "Compiled platform archive mismatch")
    with zipfile.ZipFile(path) as archive, zipfile.ZipFile(compiled_path) as compiled:
        count = safe_archive(archive)
        require(compiled.testzip() is None, "Compiled asset archive CRC failure")
        if ext == "ipa":
            matches = [name for name in archive.namelist() if name.startswith("Payload/") and name.endswith(".app/games/game.ios")]
            require(len(matches) == 1, "Ambiguous IPA game payload")
            prefix = matches[0][:-len("games/game.ios")]
            packaged_game = archive.read(matches[0])
            source_game = compiled.read("assets/game.ios")
            require(sha(packaged_game) == validation["merged_game_sha256"] and sha(source_game) == validation["source_game_sha256"] == build["game_sha256"], "IPA game binding failed")
            info = plistlib.loads(archive.read(prefix + "Info.plist"))
            require(info["CFBundleIdentifier"] == PACKAGE and info["CFBundleVersion"] == "96" and info["CFBundleShortVersionString"] == "2.0", "Actual IPA identity/version changed")
            require(info["UIFileSharingEnabled"] and info["LSSupportsOpeningDocumentsInPlace"], "IPA editable Documents support lost")
            require(archive.getinfo(prefix + "nuclearthronemobile").external_attr >> 16 & 0o111 == 0o111, "IPA executable mode lost")
            require(not any("/_CodeSignature/" in name for name in archive.namelist()) and validation["requires_resigning"] is True, "IPA re-signing limitation inconsistent")
            with zipfile.ZipFile(BASE_IPA) as baseline:
                old_names = [name for name in baseline.namelist() if name.startswith("Payload/") and name.endswith(".app/nuclearthronemobile")]
                require(len(old_names) == 1 and archive.read(prefix + "nuclearthronemobile") == baseline.read(old_names[0]), "Actual retained iOS runner differs")
            compatibility_path = RELEASE / "ios-native-compatibility.json"
            compatibility = read(compatibility_path)
            require(file_sha(compatibility_path) == build["compatibility_sha256"] and compatibility["compatible_added_functions_and_extensions"]
                    and not compatibility["missing_native_registrations"] and compatibility["extension_chunk_identical"]
                    and compatibility["old_extension_count"] == compatibility["new_extension_count"] == 0
                    and compatibility["verified_additional_functions"] == compatibility["additional_vm_functions"], "iOS retained runner API compatibility evidence failed")
            native = {"plist_identity_version_verified": True, "display_version": "2.0", "internal": "96", "retained_native_sha256": sha(archive.read(prefix + "nuclearthronemobile")), "requires_resigning": True, "signed": False, "editable_documents_enabled": True,
                      "hash_bound_additional_builtin_registrations_verified": compatibility["verified_additional_functions"], "native_extensions_unchanged": True}
            asset_report = compiled_assets(compiled, archive, prefix + "games/", "game.ios")
            patches = validation
        else:
            patches = read(RELEASE / "android-delivery/assets-validation.json")
            require(file_sha(RELEASE / "android-delivery/assets-validation.json") == receipt["assets_validation_sha256"], "Android asset patch receipt mismatch")
            packaged_game, source_game = archive.read("assets/game.droid"), compiled.read("assets/game.droid")
            require(sha(packaged_game) == validation["game_sha256"] == patches["patched_game_sha256"] and sha(source_game) == patches["source_game_sha256"] == build["game_sha256"], "Android game binding failed")
            native = android_native(path, archive, validation, build)
            asset_report = compiled_assets(compiled, archive, "assets/", "game.droid")
        before, after = VM(source_game), VM(packaged_game)
        gameplay_report = gameplay(before, after, patches, platform)
        fonts = cjk_and_titles(after, source_manifest)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": digest, "bytes": path.stat().st_size,
            "different_from_old_package": True, "original_package_preserved": True, "archive_members_crc_and_paths_verified": count,
            "current_native_acceptance_and_platform_build_receipts_bound": True, "compiled_game_sha256": sha(source_game), "packaged_game_sha256": sha(packaged_game),
            "native": native, "compiled_assets": asset_report, "gameplay": gameplay_report, "cjk_and_titles": fonts,
            "package_receipt_sha256": file_sha(receipt_path), "validation_sha256": file_sha(validation_path)}


def main():
    delivery_path = RELEASE / "delivery-verification.json"
    delivery = read(delivery_path)
    require(delivery["status"] == "PASS" and delivery["version"] == "2.0" and delivery["internal"] == 96
            and delivery["update_version"] == "2.0.0" and delivery["release_tag"] == "2.0"
            and delivery["game_build_save_protocol"] == 3004 and delivery["physical_device_tested"] is False
            and delivery["ios_requires_resigning"] is True, "Final repaired delivery incomplete")
    require(set(delivery["packages"]) == {"Android", "iOS"}, "Final delivery package set incomplete")
    require(file_sha(RELEASE / "native-acceptance.json") == delivery["native_acceptance_sha256"], "Final native receipt changed")
    acceptance = read(RELEASE / "native-acceptance.json")
    selected = read(ROOT / "review/final-regression-cases.json")["cases"]
    require(acceptance["status"] == "PASS" and len(set(selected)) == len(acceptance["cases"]) == 88
            and acceptance["required_cases"] == selected == [row["case"] for row in acceptance["cases"]], "Final 88-case acceptance incomplete")
    require(acceptance["vm_sha256"] == EXPECTED_VM and acceptance["input_sha256"] == EXPECTED_INPUT, "Final native VM/input differs")
    require(file_sha(ROOT / "build-windows/last-success.json") == acceptance["windows_compile_receipt_sha256"], "Current successful native compiler receipt changed")
    tool_key = "work/ntte-complete/frontier20/tools/mobile_delivery.py"
    require(file_sha(ROOT / "tools/mobile_delivery.py") == acceptance["reviewed_support"][tool_key], "Accepted mobile delivery tool changed")
    require(acceptance["development_regression"] == delivery["development_regression"] and acceptance["development_regression"]["report_sha256"] == EXPECTED_REPORT, "Final regression report binding differs")
    require(file_sha(ROOT / "review/development-regression.json") == EXPECTED_REPORT, "Final development evidence changed")
    require(file_sha(RELEASE / "staged-source-manifest.json") == acceptance["source_manifest_sha256"], "Canonical source manifest changed")
    source_manifest = read(RELEASE / "staged-source-manifest.json")["files"]
    results = {platform: package(platform, delivery, acceptance, source_manifest) for platform in ("iOS", "Android")}
    report = {"status": "PASS", "reviewed_utc": datetime.now(timezone.utc).isoformat(), "method": __doc__.strip(),
              "version": "2.0", "internal": 96, "native_acceptance_sha256": delivery["native_acceptance_sha256"],
              "delivery_verification_sha256": file_sha(delivery_path), "development_regression": delivery["development_regression"],
              "packages": results, "limits": {"full_stage_gate_repeated": False, "runner_used": False, "physical_device_tested": False,
              "mobile_fps_guaranteed": False, "ios_requires_resigning": True, "publication_or_upload_performed": False}}
    output = ROOT / "review/release20-package-independent-review.json"
    require(not output.exists(), "Preserve earlier successful independent package evidence")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("PASS independent actual repaired APK/IPA audit: " + str(output))


if __name__ == "__main__":
    main()
