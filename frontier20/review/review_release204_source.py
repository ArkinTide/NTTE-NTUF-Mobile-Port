"""Independently review the concrete, finalized 2.0.4 source payload.

The default plan never emits a PASS or writes files. The explicit review reads
the actual source/package/evidence bytes and runs only the public offline source
restoration helper in a temporary directory. It never builds, executes a game,
changes Git or accesses the network. A completed review receipt is immutable.
"""
from __future__ import annotations

import argparse
import ast
import base64
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile

FRONTIER = Path(__file__).resolve().parents[1]
PUBLISH = FRONTIER.parents[2] / "github-publish"
RELEASE = PUBLISH / "release-2.0.4"
PAYLOAD = PUBLISH / "ntuf204-src"
REPO = PUBLISH / "ntte-mobile-port"
MOBILE = FRONTIER / "mobile-release204-20261108"
RECEIPT = RELEASE / "source-payload-receipt.json"
REPORT = RELEASE / "final-source-review.json"
BASE = "bce57723c9b341b74313947553e80d0de087025f"
VERSION, INTERNAL = "2.0.4", 100
ARCHIVE_SHA = "921cec16f63ed36c95ef97ed5bdd644e142a209965f430b9e0cf47500adcfeea"
REFERENCE_ROOTS = ("native", "tools", "dependencies", "generated-code", "generated-assets", "base-assets", "localization", "original/Frontier", "review")
PUBLIC_REVIEW = {"review/verify_post203_repairs.py", "review/release204-cases.json",
                 "review/release204-config.json", "review/release204-config.template.json",
                 "review/release204-cases.template.json", "review/test_verify_post203_repairs.py",
                 "review/inspect_release204_packages.py", "review/review_release204_source.py",
                 "review/capture204_python.py", "review/verify_release204_debug_font.py", "review/inspect_release20_packages.py",
                 "review/test_release204_reviewers.py"}
OMIT_TOOLS = {"mobile_delivery.py", "release200_delivery.py", "release201_delivery.py", "release202_delivery.py", "release203_delivery.py", "release204_delivery.py", "MOBILE_DELIVERY.md", "build_windows.ps1"}
OMIT_RAW = {"original/Frontier/LibLoader.mod.gml"}
OVERLAYS = ("objects/MakeGame/Alarm_0.gml", "options/android/options_android.yy")
SUPPORT = {
    "frontier20/tools/restore_source_inputs.py": RELEASE / "restore_source_inputs.py",
    "frontier20/SOURCE_REPRODUCTION.md": RELEASE / "SOURCE_REPRODUCTION.md",
    "tools/source_only_policy.py": PUBLISH / "source_only_policy.py",
}
UPSTREAM_ROUTE = {"file": "project/README.md", "target": "../../graphs/contributors", "reason": "preserved canonical upstream web route; not a local file"}
SOURCE_EXTS = set("gml yy yyp resource_order vsh fsh ini json md js loc txt java gitignore gitattributes mit csv tsv py xml cpp bat nsi ext sh yml yaml h hpp c css html lock toml ps1 patch license".split())
SOURCE_NAMES = {"LICENSE", "COPYING", "NOTICE", "Makefile", "CMakeLists.txt", ".gitkeep", ".gitignore", ".gitattributes", "pre-push"}
PRIVATE_NAMES = {"local.properties", "key.properties", "keystore.properties", "signing.properties", ".env"}
PNG = re.compile(rb"iVBORw0KGgo[A-Za-z0-9+/=]{100,}")
SECRET = re.compile(rb"(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{25,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")
AUTH = re.compile(rb"(?i)(?:Authorization|oauth_token).{0,100}(?:token|bearer)")
HOST_USER = re.compile(rb"(?i)[A-Z]:[\\/]+Users[\\/]")
ENCODED_MEDIA = re.compile(rb"data:(?:image|audio)/[^;]+;base64,", re.I)
CASE_SELECTION = FRONTIER / "review/release204-cases.json"
PLAN = RELEASE / "PUBLICATION_PLAN.json"
PUBLICATION_TOOLS = ("prepare_source.py", "finalize_docs.py", "publication_adapter.py", "restore_source_inputs.py", "publication_plan.py")
FINAL_CASES = tuple(json.loads(CASE_SELECTION.read_text(encoding="utf-8-sig"))["cases"])
PYTHON_REVIEW_INPUTS = ("review/capture204_python.py", "review/inspect_release204_packages.py",
    "review/review_release204_source.py", "review/verify_release204_debug_font.py",
    "review/test_release204_reviewers.py", "review/verify_post203_repairs.py",
    "review/test_verify_post203_repairs.py")
CURRENT204_SEMANTIC_CASES = {"FrontierPost203CompatTests", "FrontierPost203WeatherWallTests",
    "FrontierPromptTests", "FrontierEnemyVisibilityTests", "FrontierEnemyPossessionTests", "FrontierPerformanceTests",
    "FrontierBiomeClearance204AcceptanceTests", "FrontierDronePerformance204Tests", "FrontierBiomeClearance204MapTests",
    "FrontierBluescreenUI204Yes30Tests", "FrontierBluescreenUI204Yes60Tests",
    "FrontierBluescreenUI204No30Tests", "FrontierBluescreenUI204No60Tests",
    "FrontierBluescreenUI204Disabled30Tests", "FrontierBluescreenUI204Disabled60Tests",
    "FrontierBluescreenUI204Visited30Tests", "FrontierBluescreenUI204Visited60Tests",
    "FrontierMenuInput20430Tests", "FrontierMenuInput20460Tests"}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def delivery_cases(source, selection):
    """Read dynamic case scope without executing or importing a publisher."""
    tree = ast.parse(source)
    declarations = [node.value for node in tree.body if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "FINAL_CASES" for target in node.targets)]
    assert len(declarations) == 1, "Delivery case declaration is ambiguous"
    declaration = declarations[0]
    assert isinstance(declaration, ast.Call) and isinstance(declaration.func, ast.Name) \
        and declaration.func.id == "selected_cases" and not declaration.args and not declaration.keywords, \
        "Delivery must use the reviewed dynamic case selection"
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
    assert len(functions) == 1 and ast.dump(functions[0]) == ast.dump(expected), \
        "Delivery selected_cases implementation differs from the reviewed read-only validator"
    return tuple(selection["cases"])


def publication_binding():
    """Read formal root-reviewed claims; never populate pins or execute a publisher."""
    assert PLAN.is_file() and not PLAN.is_symlink(), "Formal publication plan is absent or a link"
    plan = read(PLAN)
    assert plan["status"] == "READY", "Formal publication plan is still DRAFT"
    assert plan["version"] == VERSION and plan["internal"] == INTERNAL and plan["base_commit"] == BASE
    assert plan["product"] == "ntuf204" and plan["mobile_folder"] == MOBILE.name and plan["payload_folder"] == PAYLOAD.name
    assert plan["physical_device_tested"] is False
    for name in ("persistent_menu_audio_noise", "invisible_enemies"):
        assert isinstance(plan[name], str) and plan[name].strip(), "Missing reviewed claim: " + name
    pins = plan["reviewed_sha256"]
    for key, path in (("delivery_tool", FRONTIER / "tools/release204_delivery.py"),
            ("case_selection", CASE_SELECTION), ("release_content", RELEASE / "RELEASE_CONTENT.json"),
            ("release_notes", RELEASE / "RELEASE_NOTES.md"),
            ("acceptance_config", FRONTIER / "review/release204-config.json"),
            ("review_verifier", FRONTIER / "review/verify_post203_repairs.py")):
        assert re.fullmatch(r"[0-9a-f]{64}", pins[key]) and not path.is_symlink() and sha(path) == pins[key], key
    selection = read(CASE_SELECTION)
    assert selection["version"] == VERSION and selection["internal"] == INTERNAL
    assert list(FINAL_CASES) == selection["cases"] == plan["selected_cases"]
    assert FINAL_CASES and len(FINAL_CASES) == len(set(FINAL_CASES))
    assert all(isinstance(case,str) and re.fullmatch(r"[A-Za-z0-9_]+",case) for case in FINAL_CASES)
    config = read(FRONTIER / "review/release204-config.json")
    assert config["status"] == "READY" and config["version"] == VERSION and config["internal"] == INTERNAL
    wording = read(RELEASE / "RELEASE_CONTENT.json")
    assert wording["status"] == "READY" and wording["version"] == VERSION and wording["internal"] == INTERNAL
    assert "DRAFT" not in (RELEASE / "RELEASE_NOTES.md").read_text(encoding="utf-8-sig")
    return plan


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf8")


def allowed_path(name):
    path = PurePosixPath(name)
    return path.suffix.lower().lstrip(".") in SOURCE_EXTS or path.name in SOURCE_NAMES


def checked_name(name):
    assert isinstance(name, str) and name and "\\" not in name and ":" not in name, name
    assert not PurePosixPath(name).is_absolute() and all(part not in {"", ".", ".."} for part in name.split("/")), name
    assert allowed_path(name) and PurePosixPath(name).name not in PRIVATE_NAMES, name
    assert not any(part in {".git", ".auth", "gradle-home", "node_modules", "__pycache__"} for part in name.split("/")), name
    return name


def decoded_text(data, name):
    try:
        text = data.decode("utf16") if data.startswith((b"\xff\xfe", b"\xfe\xff")) else data.decode("utf-8-sig")
    except UnicodeError:
        assert name.lower().endswith("/license.txt"), "Non-UTF text: " + name
        text = data.decode("cp1252")
        assert all(ord(c) >= 32 or c in "\r\n\t\f" for c in text), name
    assert "\0" not in text, "Binary/NUL content: " + name
    return text


def scan(name, data):
    checked_name(name)
    text = decoded_text(data, name)
    for value in (data, text.encode("utf8")):
        assert not SECRET.search(value) and not AUTH.search(value), "Credential pattern: " + name
        assert not HOST_USER.search(value), "Machine-local user path: " + name
        assert not PNG.search(value) and not ENCODED_MEDIA.search(value), "Encoded media: " + name
    return text


def regular_files(root):
    root = Path(root).resolve(strict=True)
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    assert root.is_dir() and not root.is_symlink() and not root.stat().st_file_attributes & reparse, root
    files = {}
    for current, directories, names in os.walk(root, followlinks=False):
        for name in directories + names:
            path = Path(current) / name
            mode = path.lstat()
            assert not stat.S_ISLNK(mode.st_mode) and not getattr(mode, "st_file_attributes", 0) & reparse, "Link/reparse point: " + str(path)
            assert path.resolve(strict=True).is_relative_to(root), "Path escaped root"
            if path.is_file():
                relative = path.relative_to(root).as_posix()
                assert relative not in files, relative
                files[relative] = path
    return files


def git(*args):
    return subprocess.check_output(["git", "--no-optional-locks", "-c", "core.longpaths=true", "-c", "safe.directory=" + REPO.as_posix(), *args], cwd=REPO)


def checkout_state():
    index = Path(git("rev-parse", "--git-path", "index").decode("utf8").strip())
    if not index.is_absolute():
        index = REPO / index
    return {"head": git("rev-parse", "HEAD").decode("ascii").strip(),
            "status_sha256": sha_bytes(git("status", "--porcelain=v1", "-z", "--untracked-files=all")),
            "index_sha256": sha(index) if index.exists() else None,
            "cached_diff_sha256": sha_bytes(git("diff", "--cached", "--binary"))}


def payload_inventory(receipt):
    paths = regular_files(PAYLOAD)
    assert set(paths) == set(receipt["files"]), "Concrete payload path set differs from final receipt"
    hashes, sizes, fragments = {}, {}, {}
    for name, path in paths.items():
        data = path.read_bytes()
        scan(name, data)
        hashes[name], sizes[name] = sha_bytes(data), len(data)
        assert hashes[name] == receipt["files"][name]["sha256"], "Payload hash mismatch: " + name
        if name.endswith(".source.json"):
            record = json.loads(data)
            assert record["format"] == "NTUF-source-fragments-1", name
            checked_name(record["original_path"])
            images = 0
            for segment in record["segments"]:
                if "text_base64" in segment:
                    assert set(segment) == {"text_base64"}, name
                    scan(record["original_path"], base64.b64decode(segment["text_base64"], validate=True))
                else:
                    assert set(segment) == {"external_png_base64_sha256", "encoded_bytes", "png_sha256", "png_bytes"}, name
                    assert all(re.fullmatch(r"[0-9a-f]{64}", segment[key]) for key in ("external_png_base64_sha256", "png_sha256")), name
                    assert all(isinstance(segment[key], int) and segment[key] > 0 for key in ("encoded_bytes", "png_bytes")), name
                    images += 1
            fragments[name] = (record, images)
    assert len(fragments) == 5 and sum(count for _, count in fragments.values()) == 24, "Unexpected source-fragment/image inventory"
    return paths, hashes, sizes, fragments


def canonical_project(paths, hashes):
    manifest = read(MOBILE / "staged-source-manifest.json")
    expected = {"project/" + name: pin for name, pin in manifest["files"].items() if allowed_path(name)}
    observed = {name: pin for name, pin in hashes.items() if name.startswith("project/")}
    assert observed == expected, "Published canonical project differs from accepted text-source manifest"
    for name, pin in expected.items():
        current = FRONTIER / "staging" / name
        assert sha(current) == pin, "Accepted staged text source changed: " + name
    android = read(MOBILE / "android-source-manifest.json")
    prefix = "platforms/android/project/"
    overlay = {prefix + name: android["files"]["project/" + name] for name in OVERLAYS}
    assert {name: pin for name, pin in hashes.items() if name.startswith(prefix)} == overlay, "Android overlay must be exactly the two reviewed files"
    for name in OVERLAYS:
        assert sha(MOBILE / "android-delivery/project" / name) == overlay[prefix + name], name
    assert android["native_acceptance_sha256"] == sha(MOBILE / "native-acceptance.json")
    return len(expected)


def references(paths, hashes, fragments, receipt):
    expected, excluded = {}, []
    for directory in REFERENCE_ROOTS:
        for relative, path in regular_files(FRONTIER / directory).items():
            original = directory + "/" + relative
            if directory == "review" and original not in PUBLIC_REVIEW:
                continue
            if not allowed_path(original) or path.name in OMIT_TOOLS or original in OMIT_RAW or "__pycache__" in path.parts:
                continue
            name = "frontier20/" + original
            data = path.read_bytes()
            if HOST_USER.search(data):
                excluded.append({"path": name, "sha256": sha_bytes(data)})
                assert name not in paths, "Private local tool/receipt leaked: " + name
                continue
            matches = list(PNG.finditer(data))
            if matches:
                target = name + ".source.json"
                record, count = fragments[target]
                assert record["original_path"] == original and record["original_sha256"] == sha_bytes(data) and record["original_bytes"] == len(data), name
                assert count == len(matches), name
                chunks, offset = [], 0
                for segment in record["segments"]:
                    if "text_base64" in segment:
                        chunk = base64.b64decode(segment["text_base64"], validate=True)
                    else:
                        chunk = data[offset:offset + segment["encoded_bytes"]]
                        assert sha_bytes(chunk) == segment["external_png_base64_sha256"], name
                        image = base64.b64decode(chunk, validate=True)
                        assert image.startswith(b"\x89PNG\r\n\x1a\n") and len(image) == segment["png_bytes"] and sha_bytes(image) == segment["png_sha256"], name
                    assert data[offset:offset + len(chunk)] == chunk, name
                    chunks.append(chunk)
                    offset += len(chunk)
                assert b"".join(chunks) == data and offset == len(data), name
                expected[target] = hashes[target]
            else:
                expected[name] = sha_bytes(data)
    for name, path in SUPPORT.items():
        expected[name] = sha(path)
    relevant = {name: pin for name, pin in hashes.items() if any(name.startswith("frontier20/" + directory + "/") for directory in REFERENCE_ROOTS) or name in SUPPORT}
    assert relevant == expected, "Current public reference source differs from local canonical inputs"
    declared_exclusions = {row["path"]: row["sha256"] for row in receipt["externalized_or_excluded_references"] if "excluded" in row}
    assert declared_exclusions == {row["path"]: row["sha256"] for row in excluded}, "Private-source omission inventory differs"
    inventory = read(FRONTIER / "input-manifest.json")
    inventory["source"] = "Frontier 1.0.3.3.zip (obtained separately from author)"
    assert paths["frontier20/input-manifest.json"].read_bytes() == encoded(inventory)
    return len(expected)


def inherited_baseline(paths, hashes, receipt):
    inherited = {name for name, row in receipt["files"].items() if row["kind"] == "public_baseline"}
    seen = set()
    proc = subprocess.Popen(["git", "--no-optional-locks", "-c", "safe.directory=" + REPO.as_posix(), "archive", "--format=tar", BASE], cwd=REPO, stdout=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=proc.stdout, mode="r|") as archive:
            for member in archive:
                assert member.isdir() or member.isfile(), "Unexpected baseline archive member"
                if member.name not in inherited:
                    continue
                assert member.isfile() and member.name not in seen
                assert sha_bytes(archive.extractfile(member).read()) == hashes[member.name], "Inherited baseline source changed: " + member.name
                seen.add(member.name)
        assert proc.wait() == 0
    finally:
        if proc.poll() is None:
            proc.kill()
    assert seen == inherited
    return len(seen)


def restoration(fragments):
    inventory = read(FRONTIER / "input-manifest.json")
    archive = Path(inventory["source"]).resolve(strict=True)
    assert inventory["archive_sha256"] == sha(archive) == ARCHIVE_SHA, "Author archive hash differs"
    assert ARCHIVE_SHA in (PAYLOAD / "frontier20/SOURCE_REPRODUCTION.md").read_text(encoding="utf8"), "Reproduction documentation archive hash differs"
    rows = []
    with tempfile.TemporaryDirectory(prefix="source204-review-", dir=FRONTIER / "review") as temporary:
        base = Path(temporary).resolve(strict=True)
        assert base.parent == (FRONTIER / "review").resolve()
        output = base / "restored"
        proc = subprocess.run([sys.executable, str(PAYLOAD / "frontier20/tools/restore_source_inputs.py"),
            "--source-root", str(PAYLOAD / "frontier20"), "--frontier-archive", str(archive),
            "--dependency-inputs", str(FRONTIER / "dependencies"), "--output", str(output)], capture_output=True, text=True, encoding="utf8", timeout=120)
        assert proc.returncode == 0, "Published offline restoration helper failed"
        result = json.loads(proc.stdout)
        assert result["status"] == "PASS" and result["network_used"] is False
        actual = regular_files(output)
        assert set(actual) == {record["original_path"] for record, _ in fragments.values()}
        with zipfile.ZipFile(archive) as own_archive:
            for name, (record, count) in sorted(fragments.items()):
                original = PurePosixPath(record["original_path"])
                if original.parts[:2] == ("original", "Frontier"):
                    own = own_archive.read(PurePosixPath("Frontier", *original.parts[2:]).as_posix())
                else:
                    assert original.parts[0] == "dependencies"
                    own = (FRONTIER / Path(*original.parts)).read_bytes()
                restored = actual[original.as_posix()].read_bytes()
                assert restored == own and sha_bytes(restored) == record["original_sha256"]
                assert {"path": original.as_posix(), "sha256": record["original_sha256"], "bytes": len(restored)} in result["restored"]
                rows.append({"path": name, "images": count, "original_sha256": record["original_sha256"], "published_sha256": sha(PAYLOAD / name)})
        assert len(result["restored"]) == len(rows) == 5
    return rows


def relative_markdown_links(paths):
    names = sorted(name for name in paths if (name.startswith("docs/") or "/" not in name) and name.endswith(".md"))
    names += ["frontier20/SOURCE_REPRODUCTION.md", "project/README.md"]
    count, routes = 0, []
    for name in names:
        text = paths[name].read_text(encoding="utf-8-sig")
        # Markdown syntax only; upstream HTML artwork is intentionally external
        # to this text-only checkout, and not a publication-documentation link.
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        targets = re.findall(r"(?<!!)\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", text)
        targets += re.findall(r"(?m)^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", text)
        for raw in targets:
            target = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            if name == UPSTREAM_ROUTE["file"] and target == UPSTREAM_ROUTE["target"]:
                routes.append(UPSTREAM_ROUTE)
                continue
            target_path = (paths[name].parent / unquote(parsed.path)).resolve()
            assert target_path.is_relative_to(PAYLOAD.resolve()) and target_path.exists(), ("Broken relative Markdown link", name, target)
            count += 1
    assert routes == [UPSTREAM_ROUTE], "Canonical upstream contributor route must be preserved once"
    return count


def cold_boot_native_evidence(smoke, artifact):
    """Validate the cold-boot observer's dedicated entry, without inventing CASE."""
    start = "NTUF MENU AUDIO true cold-boot observer started without synthetic GameCont"
    summary = "PASS FRONTIER actual cold-boot Logo, mode menu, character selection and Back audio lifecycle"
    completion = "PASS full internal selected implemented branches; not complete MOD coverage"
    prefix = "NTUF MENU AUDIO native idle "
    lines = [line for line in smoke.splitlines() if line]
    assert not re.search(r"(?m)^CASE(?:\s|$)", smoke), "Cold-boot observer must not claim a synthetic CASE"
    assert lines.count(start) == lines.count(summary) == 1, "Missing or repeated cold-boot boundary"
    idle = [line for line in lines if line.startswith(prefix)]
    assert len(idle) == 2 and lines == [start, *idle, summary, completion], "Unexpected cold-boot smoke sequence"
    assert "FULL INTERNAL BEGIN" not in smoke, "Synthetic gameplay replaced cold boot"
    assert artifact["kind"] == "actual application cold-boot menu voice lifecycle"
    assert artifact["physical_device_tested"] is False and artifact["audio_output_captured"] is False
    rows = [json.loads(line[len(prefix):]) for line in idle]
    assert rows == artifact["rows"], "Cold-boot smoke and artifact idle rows differ"
    assert [row["phase"] for row in rows] == ["actual-cold-boot-mode-menu", "actual-cold-boot-after-character-back"]
    for row in rows:
        assert row["rate"] == 60 and row["live_portal_voices"] == 1 and row["new_portal_plays"] == 0
        assert row["old_source_stopped"] is True
        assert row["pitch"] == row["voice_gain"] == 1 and row["sample_gain"] == .5
        for key in ("portal_voice", "track_advance", "wall_seconds", "voice_gain", "sample_gain", "pitch"):
            assert isinstance(row[key], (int, float)) and not isinstance(row[key], bool) and math.isfinite(row[key]) and row[key] > 0, key
    assert rows[0]["portal_voice"] != rows[1]["portal_voice"], "Character Back did not replace the portal source"
    assert isinstance(artifact["voices"], list) and artifact["voices"]
    assert isinstance(artifact["snapshots"], list) and artifact["snapshots"]


def selected_native_binding(native, receipt):
    expected = list(FINAL_CASES)
    assert expected and len(expected) == len(set(expected))
    selection = read(FRONTIER / "review/release204-cases.json")
    declared = delivery_cases((FRONTIER / "tools/release204_delivery.py").read_text(encoding="utf8"), selection)
    assert tuple(declared) == FINAL_CASES
    assert selection["version"] == VERSION and selection["internal"] == INTERNAL and selection["cases"] == expected
    assert native["required_cases"] == expected and [row["case"] for row in native["cases"]] == expected
    regression = native["development_regression"]
    assert regression["cases"] == expected and regression["total"] == len(expected)
    run_name = regression["run"]
    assert re.fullmatch(r"tests/\d{8}T\d+Z", run_name), "Unexpected native evidence path"
    run = FRONTIER / run_name
    compiled = read(run / "compiled-build.json")
    assert compiled["status"] == "COMPILED_NOT_PLAYABLE_VERIFIED" and sha(run / "compile.log") == compiled["log_sha256"]
    assert compiled["vm_sha256"] == native["vm_sha256"] == receipt["vm_sha256"] == regression["vm_sha256"]
    assert compiled["input_sha256"] == native["input_sha256"] == receipt["input_sha256"] == regression["input_sha256"]
    assert sha(FRONTIER / "build-windows/nuclearthronemobile.win") == compiled["vm_sha256"]
    assert sha(FRONTIER / "build-windows/frontier-silent.win") == regression["silent_vm_sha256"]
    assert {p.name for p in run.iterdir() if p.is_dir()} == set(expected)
    for selected in native["cases"]:
        directory = run / selected["case"]
        assert selected["receipt"] == directory.relative_to(FRONTIER).as_posix() + "/receipt.json"
        files = regular_files(directory)
        assert {name: sha(path) for name, path in files.items()} == selected["files"], "Native accepted evidence changed"
        row = read(directory / "receipt.json")
        assert row["case"] == selected["case"] and row["status"] == "PASS" and row["exit"] == 0 and row["termination_reason"] is None
        assert row["vm_sha256"] == compiled["vm_sha256"] and row["input_sha256"] == compiled["input_sha256"]
        assert row["silent_vm_sha256"] == regression["silent_vm_sha256"] and row["muted_resources"] > 100
        assert row["desktop"] == "private, never activated" and row["physical_device_tested"] is False
        assert isinstance(row["elapsed_seconds"], (int, float)) and math.isfinite(row["elapsed_seconds"]) and row["elapsed_seconds"] > 0
        smoke = (directory / "smoke.txt").read_text(encoding="utf8")
        log = (directory / "runner.log").read_text(encoding="utf8", errors="replace")
        if selected["case"] == "FrontierMenuAudioBootTests":
            artifact = directory / "ntuf-menu-audio-cold-boot.json"
            assert artifact.is_file(), "Actual cold-boot artifact is absent"
            cold_boot_native_evidence(smoke, read(artifact))
        else:
            assert set(re.findall(r"(?m)^CASE (.+)$", smoke)) == {selected["case"]}
            assert "PASS full internal selected implemented branches" in smoke
        assert not re.search(r"(?m)^ERROR(?:\s|$)", smoke)
        assert "ERROR!!!" not in smoke and "ERROR!!!" not in log and "###game_end###0" in log
        artifacts = {name for name in files if name.startswith(("frontier-", "ntuf-")) and Path(name).suffix in {".png", ".json"}}
        assert set(row["artifacts_sha256"]) == artifacts
        for name, pin in row["artifacts_sha256"].items():
            assert sha(files[name]) == pin
    for field, path in (("config_sha256", regression["config"]), ("report_sha256", regression["report"]), ("case_selection_sha256", regression["case_selection"])):
        checked_name(path)
        assert sha(FRONTIER / path) == regression[field]
    development = read(FRONTIER / regression["report"])
    assert development["status"] == "SELECTED_DEVELOPMENT_CHECKS_VERIFIED" and development["prior_vm_runs"] == []
    assert development["current_native_run"]["count"] == len(expected) and development["current_native_run"]["expected_cases"] == expected
    assert development["current_native_run"]["compiled_build"] == compiled
    current_semantics = development["current_native_run"]["current204_semantics"]
    assert set(current_semantics) == CURRENT204_SEMANTIC_CASES
    python = development["python"]
    assert python["exit"] == 0 and python["tests"] == regression["python_tests"] >= 110
    assert sha(FRONTIER / python["log"]) == python["log_sha256"]
    text = (FRONTIER / python["log"]).read_text(encoding="utf8")
    assert re.search(r"(?m)^Ran " + str(python["tests"]) + r" tests in ", text) and re.search(r"\nOK\s*$", text)
    assert not re.search(r"(?m)^(?:FAILED|ERROR:|FAIL:)", text)
    # The current capture includes before/after maintained-input maps and
    # separately binds the explicit review guard suite.
    # Earlier runs lack that history; do not conflate them with this new map.
    current_inputs={path.relative_to(FRONTIER).as_posix():sha(path)
        for path in sorted([*(FRONTIER/"tools").glob("*.py"),*(FRONTIER/"native").glob("*.gml")])}
    assert python["source_inputs_unchanged"] is True and python["source_inputs"]==current_inputs, "Current Python maintained-source capture differs"
    review_inputs={name:sha(FRONTIER/name) for name in PYTHON_REVIEW_INPUTS}
    assert python["reviewer_inputs_unchanged"] is True and python["reviewer_inputs"]==review_inputs, \
        "Current Python reviewer/verifier guard input capture differs"
    assert python["review_test_modules"]==["review/test_verify_post203_repairs.py", "review/test_release204_reviewers.py"]
    source_binding={"current_source_inputs_bound":True,"source_inputs_unchanged":True,
        "files":len(current_inputs),"source_input_map_sha256":sha_bytes(json.dumps(current_inputs,sort_keys=True,separators=(",",":")).encode("utf8")),
        "reviewer_inputs_bound":True,"reviewer_files":len(review_inputs),
        "reviewer_input_map_sha256":sha_bytes(json.dumps(review_inputs,sort_keys=True,separators=(",",":")).encode("utf8")),
        "earlier_run_historical_source_binding_claimed":False}
    return len(expected), python["tests"], source_binding


def package_binding(receipt):
    plan = publication_binding()
    delivery_path = MOBILE / "delivery-verification.json"
    native_path = MOBILE / "native-acceptance.json"
    manifest_path = MOBILE / "staged-source-manifest.json"
    audit_path = FRONTIER / "review/release204-independent-package-audit.json"
    delivery, native, audit = read(delivery_path), read(native_path), read(audit_path)
    for row in (delivery, native, audit):
        assert row["status"] == "PASS" and row["version"] == VERSION and row["internal"] == INTERNAL
    assert receipt["delivery_receipt_sha256"] == sha(delivery_path) == audit["delivery_receipt_sha256"]
    assert receipt["native_acceptance_sha256"] == sha(native_path) == delivery["native_acceptance_sha256"] == audit["native_acceptance_sha256"]
    assert receipt["source_manifest_sha256"] == sha(manifest_path) == native["source_manifest_sha256"] == audit["source_manifest_sha256"]
    assert receipt["independent_package_audit_sha256"] == sha(audit_path)
    assert delivery["update_version"] == delivery["release_tag"] == VERSION
    assert delivery["physical_device_tested"] is False and delivery["ios_requires_resigning"] is True
    assert delivery["development_regression"] == native["development_regression"] and delivery["packages"] == audit["packages"]
    public_audit = PAYLOAD / "docs/validation/2.0.4-independent-package-audit.json"
    assert sha(public_audit) == receipt["independent_package_audit_public_summary_sha256"]
    public = read(public_audit)
    assert public["original_audit_sha256"] == sha(audit_path)
    for key in ("status", "version", "internal", "scope", "delivery_receipt_sha256", "packages", "native_acceptance_sha256", "source_manifest_sha256", "development_evidence", "ios_actual_checks", "android_actual_checks", "save_compatibility_checks", "limitations", "physical_device_tested", "full_campaign_acceptance_claimed", "publication_performed_by_this_reviewer"):
        assert public[key] == audit[key], key
    packages = {}
    assert set(delivery["packages"]) == {"Android", "iOS"}
    for label, extension in (("Android", "apk"), ("iOS", "ipa")):
        row = delivery["packages"][label]
        path = (FRONTIER / row["path"]).resolve(strict=True)
        assert path == (MOBILE / "deliverables" / f"NuclearThrone.NTTE-NTUF-{label}-{VERSION}.{extension}").resolve()
        assert path.stat().st_size == row["bytes"] and sha(path) == row["sha256"]
        assert sha(path.with_suffix(".validation.json")) == row["validation_sha256"]
        packages[label.lower()] = {"name": path.name, "bytes": row["bytes"], "sha256": row["sha256"]}
    assert packages == receipt["packages"]
    baseline = read(PAYLOAD / "docs/SOURCE_BASELINE.json")
    assert baseline["publication_plan_sha256"] == receipt["publication_plan_sha256"] == sha(PLAN)
    for key, expected in (("version", VERSION), ("internal", INTERNAL), ("base_commit", BASE), ("installers", packages), ("assets_included", False), ("upload_installers_to_github", False), ("game_build_save_protocol", 3004), ("new_vm_regression_claimed", True), ("platform_versions_normalized_only", False), ("persistent_mobile_audio_noise", plan["persistent_menu_audio_noise"]), ("invisible_enemies", plan["invisible_enemies"])):
        assert baseline[key] == expected, key
    assert baseline["preserved_upstream_markdown_web_routes"] == [UPSTREAM_ROUTE]
    current_cases, python_checks, python_binding = selected_native_binding(native, receipt)
    return {"delivery_tool_sha256": sha(FRONTIER / "tools/release204_delivery.py"), "delivery_receipt_sha256": sha(delivery_path),
            "native_acceptance_sha256": sha(native_path), "source_manifest_sha256": sha(manifest_path),
            "independent_package_audit_sha256": sha(audit_path), "independent_package_audit_public_summary_sha256": sha(public_audit),
            "package_hashes_and_bytes_match_independent_actual_audit": True, "packages": packages,
            "current_native_cases": current_cases, "python_checks": python_checks, "python_source_binding": python_binding,
            "vm_sha256": native["vm_sha256"], "input_sha256": native["input_sha256"]}


def review():
    plan = publication_binding()
    plan_pin = sha(PLAN)
    tools = {name: sha(RELEASE / name) for name in PUBLICATION_TOOLS}
    assert not REPORT.exists(), "Preserve completed final-source review receipt"
    receipt = read(RECEIPT)
    assert receipt["status"] == "FINAL_SOURCE_PAYLOAD_READY_NOT_PUBLISHED", "Source payload documentation/package gate is not finalized"
    assert receipt["version"] == VERSION and receipt["internal"] == INTERNAL and receipt["base_commit"] == BASE
    assert receipt["final_documentation_and_package_gate_pending"] is False and receipt["game_assets_in_git"] is False
    assert receipt["publication_plan_sha256"] == plan_pin
    receipt_pin = sha(RECEIPT)
    before = checkout_state()
    assert before["head"] == BASE and git("status", "--porcelain").strip() == b"", "Publication checkout must be clean at the reviewed baseline"
    print("Reading and scanning the concrete finalized source payload", flush=True)
    paths, hashes, sizes, fragments = payload_inventory(receipt)
    canonical = canonical_project(paths, hashes)
    reference_count = references(paths, hashes, fragments, receipt)
    inherited_count = inherited_baseline(paths, hashes, receipt)
    print("Checking offline source restoration, documentation and bound delivery evidence", flush=True)
    restored = restoration(fragments)
    links = relative_markdown_links(paths)
    binding = package_binding(receipt)
    assert tools == {name: sha(RELEASE / name) for name in PUBLICATION_TOOLS}, "Publication tools changed during review"
    assert sha(PLAN) == plan_pin and sha(RECEIPT) == receipt_pin and {name: sha(path) for name, path in regular_files(PAYLOAD).items()} == hashes, "Payload changed during independent review"
    after = checkout_state()
    assert after == before, "Publication checkout/index changed during independent review"
    result = {"status": "PASS", "scope": "concrete-final-source-payload", "version": VERSION, "internal": INTERNAL,
        "reviewer": "independent-final-source-review", "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
        "review_script_sha256": sha(__file__), "source_payload_receipt_sha256": receipt_pin,
        "files": len(paths), "bytes": sum(sizes.values()), "canonical_project_matched": True, "canonical_text_files": canonical,
        "android_overlay_exactly": ["platforms/android/project/" + name for name in OVERLAYS], "text_only": True,
        "credential_scan_passed": True, "credential_scan_scope": "Every final payload file plus decoded text-source fragment; path/text/private-name/token/key/authorization/machine-local-user checks.",
        "encoded_artwork_absent": True, "restoration_roundtrip_passed": True, "fragment_sources": restored,
        "reference_exact_files_prechecked": reference_count, "inherited_baseline_files_byte_checked": inherited_count,
        "source_path_hash_map_sha256": sha_bytes(json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode("utf8")),
        "publication_documentation_relative_links_valid": True, "relative_markdown_links_checked": links,
        "preserved_upstream_markdown_web_routes": [UPSTREAM_ROUTE], "upstream_route_actual_reachability_claimed": False,
        "reviewed_publication_tools": tools, "publication_plan_sha256": plan_pin, **binding,
        "new_vm_regression_claimed": True, "platform_versions_normalized_only": False, "python_historical_source_binding": False,
        "persistent_mobile_audio_noise": plan["persistent_menu_audio_noise"],
        "invisible_enemies": plan["invisible_enemies"], "physical_device_tested": False, "native_xcode_compilation_performed": False,
        "full_random_campaign_tested": False, "universal_fps_claimed": False, "ios_requires_resigning": True,
        "full_delivery_gate_rerun_by_this_reviewer": False, "source_git_network_publication_mutated_by_this_reviewer": False,
        "public_checkout_changed_by_reviewer": False, "public_index_changed_by_reviewer": False, "published": False}
    with REPORT.open("xb") as output:
        output.write(encoded(result))
    print(json.dumps({"status": "PASS", "files": len(paths), "canonical_text_files": canonical, "restored_sources": len(restored), "current_native_cases": binding["current_native_cases"], "public_checkout_changed": False}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", nargs="?", choices=("plan", "review"), default="plan")
    args = parser.parse_args()
    if args.operation == "review":
        review()
    else:
        required = [RECEIPT, MOBILE / "native-acceptance.json", MOBILE / "delivery-verification.json", FRONTIER / "review/release204-independent-package-audit.json"]
        status = read(RECEIPT).get("status") if RECEIPT.is_file() else "absent"
        print(json.dumps({"status": "NOT_REVIEWED", "version": VERSION, "internal": INTERNAL,
            "payload_exists": PAYLOAD.is_dir(), "source_payload_status": status,
            "prerequisite_files_present": {path.name: path.is_file() for path in required},
            "expected_native_cases": len(FINAL_CASES), "publication_plan_status": read(PLAN).get("status") if PLAN.is_file() else "absent",
            "completed_review_exists": REPORT.exists(),
            "writes": "Only explicit review writes its immutable final-source receipt and a temporary restoration output", "git_or_network_mutated": False}, indent=2))


if __name__ == "__main__":
    main()
