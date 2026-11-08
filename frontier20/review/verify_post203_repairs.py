"""Verify selected current-VM development evidence without executing tests.

Writes one immutable review report. Does not stage, build, package, commit,
publish or upload. Prior 2.0.3 release bytes are protected and prior VM passes
never contribute to this release's native acceptance.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_input_manifest
from verify_development_regression import verify_bubbles_startup

CASE_SELECTION = ROOT / "review/release204-cases.json"
PRIOR_MANIFEST = ROOT / "mobile-release203-20261107/staged-source-manifest.json"
PRIOR_MANIFEST_SHA256 = "803d0b4fab96d42f1e853a1db33bc2af95c54bba4ad0f5d814677d6716fb8176"
REVIEW_TESTS = ("review/test_verify_post203_repairs.py", "review/test_release204_reviewers.py")
REVIEW_INPUTS = ("review/capture204_python.py", "review/inspect_release204_packages.py",
                "review/review_release204_source.py", "review/verify_release204_debug_font.py",
                "review/test_release204_reviewers.py", "review/verify_post203_repairs.py",
                "review/test_verify_post203_repairs.py")
CURRENT204_CASES = frozenset({"FrontierPost203CompatTests", "FrontierPost203WeatherWallTests", "FrontierPromptTests",
                             "FrontierEnemyVisibilityTests", "FrontierEnemyPossessionTests", "FrontierPerformanceTests",
                             "FrontierBiomeClearance204AcceptanceTests", "FrontierDronePerformance204Tests",
                             "FrontierBiomeClearance204MapTests", "FrontierBluescreenUI204Yes30Tests",
                             "FrontierBluescreenUI204Yes60Tests", "FrontierBluescreenUI204No30Tests",
                             "FrontierBluescreenUI204No60Tests", "FrontierBluescreenUI204Disabled30Tests",
                             "FrontierBluescreenUI204Disabled60Tests", "FrontierBluescreenUI204Visited30Tests",
                             "FrontierBluescreenUI204Visited60Tests", "FrontierMenuInput20430Tests",
                             "FrontierMenuInput20460Tests"})
REQUIRED204_CASES = CURRENT204_CASES | {"DesertLevelNativeTests", "JungleLevelNativeTests",
                                     "WorldFinalizeNativeTests", "WorldCompletionNativeTests"}


def read(path):
    return json.loads(path.read_text("utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_cases():
    selection = read(CASE_SELECTION)
    assert selection["version"] == "2.0.4" and selection["internal"] == 100, "Wrong release case selection"
    cases = selection["cases"]
    assert isinstance(cases, list) and cases, "Root must finalize the selected current-VM cases"
    assert all(isinstance(case, str) and re.fullmatch(r"[A-Za-z0-9_]+", case) for case in cases), "Invalid native case identity"
    assert len(cases) == len(set(cases)), "Duplicate selected native case"
    required = {"FrontierBubblesStartupATests", "FrontierBubblesStartupBTests", "FrontierBubblesRandomTests",
                "FrontierWeatherPerformanceTests", "FrontierFlyWallTests", "FrontierPalaceBlockTests", "FrontierMenuRepairTests"}
    assert required <= set(cases), "Required current repair cases are absent from the root-authored selection"
    assert REQUIRED204_CASES <= set(cases), "Current204 repair and performance cases are mandatory"
    return tuple(cases)


# The root-authored explicit selection is authoritative; receipt counts cannot
# silently define or reduce the acceptance scope.
FINAL_CASES = load_cases()


def verify_random_bubbles(smoke, artifacts, directory):
    """Check the real random-selection path in addition to its starter gameplay."""
    result = verify_bubbles_startup(smoke, artifacts, directory, 0)
    prefix = "NTUF BUBBLES STARTUP real new-run acceptance PASS "
    rows = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    assert all(row.get("random") is True for row in rows), "Random Bubbles case did not exercise genuine random selection"
    return {**result, "random_selection": True,
            "scope": "Native random CharSelect selection, real new-run/death-menu Retry, touch producer and Slash HP loss; not physical Android/iOS validation"}


def json_log(smoke, prefix):
    rows = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    assert len(rows) == 1, ("Expected exactly one native summary", prefix)
    return rows[0]


def finite(value, label, *, minimum=None):
    assert isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value), label
    if minimum is not None:
        assert value >= minimum, label
    return value


def native_true(value, label):
    """GM VM builtins may encode true as numeric1; reject generic truthiness."""
    assert value is True or (type(value) in (int, float) and value == 1), label
    return True


def json_artifact(name, artifacts, directory):
    assert name in artifacts, ("Missing hash-bound native artifact", name)
    return read(directory / name)


def png_artifact(name, artifacts, directory, *, dimensions):
    assert name in artifacts, ("Missing hash-bound native screenshot", name)
    with (directory / name).open("rb") as handle:
        header = handle.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n" and header[12:16] == b"IHDR", name
    assert (int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")) == dimensions, name
    return name


def verify_weather(smoke, artifacts, directory):
    evidence = json_artifact("frontier-weather-performance.json", artifacts, directory)
    assert json_log(smoke, "PASS NTUF FRESH WEATHER FILTER ") == evidence, "Weather artifact differs from the actual native summary"
    assert smoke.splitlines().count("PASS NTUF actual Aurora/Meteor/Scrapyards nested actor callbacks use live native background colour") == 1
    assert evidence["kind"] == "native Windows weather query/callback comparison"
    assert evidence["physical_device_tested"] is False
    assert evidence["parity_comparisons"] == 162
    assert evidence["actual_source_callback_calls"] == 120
    duration = finite(evidence["actual_source_callback_us"], "Weather source callback duration", minimum=1)
    mean = finite(evidence["source_callback_mean_us"], "Weather source callback mean", minimum=0)
    assert math.isclose(mean, duration / 120, rel_tol=1e-12, abs_tol=1e-12)
    rows = evidence["rows"]
    assert isinstance(rows, list) and len(rows) == 3 and [row["round"] for row in rows] == [0, 1, 2]
    for row in rows:
        assert row["terrain"] == 1601 and row["queries"] == 60 and row["same_result_total"] == 0
        old = finite(row["original_snapshot_us"], "Weather original snapshot duration", minimum=1)
        new = finite(row["fresh_native_us"], "Weather fresh native duration", minimum=1)
        ratio = finite(row["ratio"], "Weather paired duration ratio", minimum=0)
        assert math.isclose(ratio, new / old, rel_tol=1e-12, abs_tol=1e-12)
        assert new < old, "Fresh weather filter did not improve its same-workload native sample"
    return {**evidence, "artifact": "frontier-weather-performance.json",
            "scope": "Paired native Windows query/callback samples with old-oracle parity; not mobile FPS or universal speed guarantees"}


def verify_fly_wall(smoke, artifacts, directory):
    evidence = json_artifact("frontier-fly-wall-landing.json", artifacts, directory)
    assert evidence["physical_device_tested"] is False
    rows = evidence["rows"]
    assert json_log(smoke, "PASS NTUF actual JungleFly wall-top landing/restored collision at30/60Hz ") == rows
    assert isinstance(rows, list) and len(rows) == 2 and [row["rate"] for row in rows] == [30, 60]
    for index, row in enumerate(rows):
        assert smoke.splitlines().count("NTUF FLY LANDING real native start rate=" + str(int(row["rate"]))) == 1
        assert 40 <= finite(row["real_source_ticks"], "Fly landing actual native ticks") < 180
        assert row["landed"] == 4 and row["ordinary_fly_alive"] == 1
        assert row["anchors"] == [[186176 + index * 4000, 186016]] * 4
    return {**evidence, "artifact": "frontier-fly-wall-landing.json",
            "scope": "Actual native wall-top descent, restored collision and ordinary fly control at30/60Hz"}


def verify_palace(smoke):
    prefix = "NTUF PALACE BLOCK "
    rows = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    expected = [(rate, scene) for rate in (30, 60) for scene in ("open", "wall-prop", "corner-enemy")]
    assert len(rows) == 6 and [(row["rate"], row["scene"]) for row in rows] == expected
    summary = json_log(smoke, "PASS NTUF PALACE authored detection, 6px source velocity, real wall/prop/enemy collision and per-frame solid-wall synchronization at30/60Hz ")
    assert summary == rows, "Palace final summary differs from its six actual scheduled scenes"
    for row in rows:
        for field in ("launched", "proxy_alive", "proxy_synced", "prop_destroyed"):
            assert row[field] is True, ("Palace actual native observation failed", field, row)
        assert row["alive"] == 1
        duration = 30 if row["scene"] == "open" else 60
        assert finite(row["physical_frames"], "Palace physical frames", minimum=1) >= duration * row["rate"] / 30
        for field in ("start_x", "start_y", "maximum_x", "displacement", "enemy_hp"):
            finite(row[field], "Palace " + field)
        assert row["start_y"] == 824992
        if row["scene"] == "open":
            assert abs(row["displacement"] - 180) <= 12
        else:
            assert row["start_x"] + 24 < row["maximum_x"] < row["start_x"] + 144
            # A genuine smush reverses the source block; its final position
            # may be behind its start even though its measured peak reached
            # the front wall. Bound real source travel, not a stopped pose.
            assert abs(row["displacement"]) <= duration * 6 + 16
            assert row["displacement"] <= row["maximum_x"] - row["start_x"]
        if row["scene"] == "corner-enemy":
            assert row["enemy_hp"] == 970 and row["smush_hits"] == 1 and row["smush_damage"] == 30, "Palace contact did not deliver the authored native enemy damage exactly once"
            assert row["smush_created"] >= 1 and row["smush_target_overlap"] is True
        else:
            assert row["enemy_hp"] == 1000
    return {"rows": rows, "scope": "Actual authored player detection, source-speed movement, wall/prop/enemy contact and every-host-frame moving-wall synchronization at30/60Hz"}


def verify_menu(smoke, artifacts, directory):
    prefix = "PASS FRONTIER menu repairs: "
    rows = [line for line in smoke.splitlines() if line.startswith(prefix)]
    assert len(rows) == 1, "Native menu repair assertions did not complete exactly once"
    for fragment in ("locked Storms", "statistics22/credits16 rows", "77 NTUF weapon menu metadata without GameCont", "13 Unicode Goto labels and debug glyphs"):
        assert fragment in rows[0], ("Native menu repair coverage omitted", fragment)
    loadouts = "PASS FRONTIER Bubbles saved loadout: missing A/B, legacy false/0/negative/out-of-range, saved skin, valid alternate/fusion identity and actual Custom NONE menu selection"
    assert smoke.splitlines().count(loadouts) == 1, "Native Bubbles invalid/stored loadout and actual Custom NONE assertions did not complete"
    screenshots = [png_artifact(name, artifacts, directory, dimensions=(360, 240))
                   for name in ("frontier-menu-statistics.png", "frontier-menu-credits.png")]
    return {"native_assertion_summary": rows[0], "bubbles_saved_loadout_summary": loadouts,
            "screenshots": screenshots,
            "scope": "Actual native locked crown/menu rows/custom weapon selector/CJK console assertions and rendered stats/credits artifacts"}


def verify_case_identity(case, smoke, artifacts, directory):
    """Check normal dispatch or the deliberate pre-game cold-boot entry."""
    selected = [line[5:] for line in smoke.splitlines() if line.startswith("CASE ")]
    if case != "FrontierMenuAudioBootTests":
        assert selected and set(selected) == {case}, (directory, "smoke case", selected)
        return verify204_identity(case, smoke, artifacts, directory)
    # This observer runs before synthetic GameCont initializes the ordinary
    # async selector. Its exact raw argument is checked by the compiled native
    # fixture; require its distinct lifecycle output rather than invent CASE.
    assert selected == [], "Cold boot must retain its genuine pre-game entry"
    start = "NTUF MENU AUDIO true cold-boot observer started without synthetic GameCont"
    end = "PASS FRONTIER actual cold-boot Logo, mode menu, character selection and Back audio lifecycle"
    assert smoke.splitlines().count(start) == smoke.splitlines().count(end) == 1, "Cold boot entry/completion missing or duplicated"
    assert "FULL INTERNAL BEGIN" not in smoke, "Synthetic gameplay replaced cold boot"
    name = "ntuf-menu-audio-cold-boot.json"
    evidence = json_artifact(name, artifacts, directory)
    assert sha(directory / name) == artifacts[name], "Cold boot artifact changed"
    assert evidence["kind"] == "actual application cold-boot menu voice lifecycle"
    assert evidence["physical_device_tested"] is False and evidence["audio_output_captured"] is False
    prefix = "NTUF MENU AUDIO native idle "
    rows = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    assert rows == evidence["rows"] and len(rows) == 2, "Cold boot actual idle rows differ"
    assert [row["phase"] for row in rows] == ["actual-cold-boot-mode-menu", "actual-cold-boot-after-character-back"]
    for row in rows:
        assert row["rate"] in (30, 60) and row["live_portal_voices"] == 1 and row["new_portal_plays"] == 0
        assert row["old_source_stopped"] is True and row["pitch"] == row["voice_gain"] == 1 and row["sample_gain"] == .5
        finite(row["wall_seconds"], "Cold boot real idle duration", minimum=1)
        finite(row["track_advance"], "Cold boot real audio-clock advance", minimum=1)
    assert isinstance(evidence["voices"], list) and evidence["voices"]
    assert isinstance(evidence["snapshots"], list) and evidence["snapshots"]


def verify_enemy_visibility_launches(smoke, evidence):
    """Bind each natural clone race to the native constructor's real launch ray."""
    rows = evidence["natural_city"]
    expected = [(103038 + 97 * index, loops, 1 + index % 3, 30 if index % 2 == 0 else 60)
                for index in range(12) for loops in (0, 1, 3)]
    fields = ("seed", "loops", "subarea", "rate")
    assert isinstance(rows, list) and [tuple(row[field] for field in fields) for row in rows] == expected, \
        "Natural City visibility lost its seeded Loop/subarea/rate identity"
    observed = "FRONTIER ENEMY VISIBILITY CITY OBSERVED "
    assert [json.loads(line[len(observed):]) for line in smoke.splitlines() if line.startswith(observed)] == rows, \
        "Natural City visibility artifact differs from its actual map observations"
    begin = "FRONTIER ENEMY VISIBILITY CITY BEGIN "
    assert [json.loads(line[len(begin):]) for line in smoke.splitlines() if line.startswith(begin)] == [
        {field: row[field] for field in fields} for row in rows], \
        "Natural City visibility launch lost its scheduled native case identity"
    witnesses = [row for row in rows if row.get("natural_clone") is not None]
    assert len(witnesses) == 2 and {row["rate"] for row in witnesses} == {30, 60}, \
        "Natural City clone launch requires one real witness at each native rate"
    prefix = "FRONTIER ENEMY VISIBILITY NATURAL CLONE LAUNCH "
    assert [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)] == [
        row["natural_clone"]["launch"] for row in witnesses], \
        "Natural City clone launch trace differs from its completed native witness"
    for row in witnesses:
        trial = row["natural_clone"]
        launch, source = trial["launch"], trial["launch"]["source"]
        actor = finite(source["id"], "Natural City launch source identity", minimum=1)
        assert actor == trial["source"], "Natural City launch changed its actual source identity"
        assert row["samples"] and row["samples"][0]["source_ticks"] == 0
        matches = [candidate for candidate in row["samples"][0]["actors"] if candidate["id"] == actor]
        assert matches == [source], "Natural City launch source differs from its generated actor snapshot"
        assert source["top_exists"] == 0 and source["top_owns_target"] == 0 and source["top"] == -4, \
            "Natural City falling race reused an existing Top controller"
        assert source["visible"] == 1 and finite(source["alpha"], "Natural City launch source alpha") > 0
        assert source["canfly"] == 0 and source.get("intro") != False
        assert source["floor_contact"] == 1 and source["wall_contact"] == 0, \
            "Natural City launch source was not a grounded wall-free native candidate"
        assert finite(source["team"], "Natural City launch source team", minimum=0) != 2
        finite(source["hp"], "Natural City launch source HP", minimum=12)
        assert source["mask"] != trial["before"]["mask"], "Natural City candidate was already suspended"
        assert source["object"] == trial["before"]["object"] and actor != trial["before"]["id"]
        x = finite(source["x"], "Natural City launch source x")
        y = finite(source["y"], "Natural City launch source y")
        wrapper = launch["wrapper"]
        assert isinstance(wrapper, list) and len(wrapper) == 2
        for coordinate in wrapper:
            finite(coordinate, "Natural City launch wrapper coordinate")
        assert wrapper == [round(x), round(y + 8)], "Natural City launch changed the native rounded wrapper"
        floor = launch["floor"]
        finite(floor["id"], "Natural City launch Floor identity", minimum=1)
        finite(floor["x"], "Natural City launch Floor x"); finite(floor["y"], "Natural City launch Floor y")
        bbox = floor["bbox"]
        assert isinstance(bbox, list) and len(bbox) == 4
        left, top, right, bottom = [finite(coordinate, "Natural City launch Floor bbox") for coordinate in bbox]
        assert left <= right and top <= bottom, "Natural City launch Floor has reversed native bounds"
        ray = launch["ray"]
        assert ray["from"] == [wrapper[0], wrapper[1] + 8] \
            and ray["to"] == [(left + right + 1) / 2, (top + bottom + 1) / 2], \
            "Natural City launch ray differs from the native Top constructor endpoints"
        assert ray["wall"] == ray["top_small"] == -4, \
            "Natural City falling race used an obstructed native launch ray"


def verify_possession(smoke, artifacts, directory):
    """Require real host transitions and restored native damage at both rates."""
    name = "frontier-enemy-possession-diagnostic.json"
    evidence = json_artifact(name, artifacts, directory)
    assert evidence["reported_area"] == "City 5-1" and evidence["loops"] == 1
    assert evidence["screenshot_hp"] == 17 and evidence["regression"] is True
    assert evidence["physical_device_tested"] is False
    rows = evidence["cases"]
    kinds = ("native-host-death", "native-car-pickup", "native-parrot-charm", "living-host-control")
    assert isinstance(rows, list) and [(row["rate"], row["kind"]) for row in rows] == [
        (rate, kind) for rate in (30, 60) for kind in kinds]
    prefix = "FRONTIER ENEMY POSSESSION ACCEPTED "
    actual = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    assert actual == rows, "Possession artifact differs from the eight native observations"
    for row in rows:
        assert row["source_constructor"] == "Frontier_Events::HauntedCity_create"
        assert 1 <= row["attempts"] <= 4
        initial = row["initial"]
        assert initial["hp"] == 17 and initial["alpha"] == 0 and initial["possessing"] is True
        native_true(initial["possess_target_exists"], "Possession lacks its actual living native host")
        ghost = finite(initial["id"], "Possession spirit identity", minimum=1)
        host = finite(initial["possess_target"], "Possession host identity", minimum=1)
        assert ghost != host and row["host_type"] == ("SnowBot" if row["kind"] == "native-car-pickup" else "Wolf")
        for sample in (initial, row["before_action"]):
            native_true(sample["possess_target_exists"], "Possession host vanished before its native action")
            assert sample["id"] == ghost and sample["possess_target"] == host
            assert sample["hp"] == 17 and sample["alpha"] == 0 and sample["possessing"] is True
            finite(sample["possess_target_hp"], "Possession living host HP", minimum=.000001)
            assert sample["possess_target_object"] == row["host_type"] \
                and sample["possess_target_possessed"] is True \
                and sample["possess_target_possessor"] == ghost, "Possession lost its reciprocal native host ownership"
            assert finite(sample["possess_target_team"], "Possession hostile host team", minimum=0) != 2
        if row["kind"] == "living-host-control":
            assert row["detached"] is False and row["restored_hittable"] is False
            assert row["host_action"]["unchanged_living_host"] is True
            assert row["ghost_after"]["possessing"] is True and row["ghost_after"]["alpha"] == 0
            assert any(sample["source_ticks"] >= 60 for sample in row["samples"])
            continue
        assert row["detached"] is True and row["restored_hittable"] is True
        assert 0 < finite(row["detached_at"], "Possession detachment source ticks") < 10
        restored = row["restored"]
        assert restored["id"] == initial["id"] and restored["alpha"] == 1
        assert restored["possessing"] is False and restored["mask"] != initial["mask"]
        shot, guardian = row["actual_bullet_collision"], row["guardian_hit"]
        assert shot["target"] == guardian["target"] == initial["id"]
        assert shot["damage"] == 3 and shot["bullet_consumed"] is True
        assert guardian["damage"] == 15 and guardian["punches"] >= 1
        if row["kind"] in {"native-host-death", "native-car-pickup"}:
            assert row["host_action"]["collision_dispatched_by_engine"] is True
        else:
            assert row["host_action"]["native_charm"] is True
    return {**evidence, "artifact": name,
            "scope": "Actual source HauntedCity possession, native death/car/charm transitions, Bullet1 and Guardian damage, plus untouched living-host controls at30/60Hz; not physical phone acceptance"}


def verify_biome_clearance(smoke, artifacts, directory):
    """Require natural assassin wake/landing, combat death and the original exit."""
    name = "frontier-biome-clearance204-acceptance.json"
    evidence = json_artifact(name, artifacts, directory)
    assert evidence["physical_device_tested"] is False
    rows = evidence["cases"]
    assert isinstance(rows, list) and [(row["rate"], row["wall"]) for row in rows] == [
        (30, True), (60, True), (30, False), (60, False)], "Biome acceptance lost a wall/ground30/60Hz control"
    for row in rows:
        assert type(row["wall"]) is bool, "Biome wall control must be explicit"
    accepted = "BIOME CLEARANCE204 ACCEPTED "
    logged = [json.loads(line[len(accepted):]) for line in smoke.splitlines() if line.startswith(accepted)]
    assert logged == rows, "Biome artifact differs from its four actual native completed observations"
    begin = "BIOME CLEARANCE204 ACCEPTANCE BEGIN "
    starts = [json.loads(line[len(begin):]) for line in smoke.splitlines() if line.startswith(begin)]
    assert starts == [{"rate": row["rate"], "wall": row["wall"], "dormant": row["dormant"], "samples": []}
                      for row in rows], "Biome beginning snapshots differ from the scheduled native scenes"
    prefix = "BIOME CLEARANCE204 ACTUAL BULLET "
    shots = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    assert shots == [shot for row in rows for shot in (row["nonlethal"], row["lethal"])], \
        "Biome real native Bullet1 collision log differs from its damage evidence"
    actors = []
    for row in rows:
        dormant, awake, landed = (row[key] for key in ("dormant", "awake", "landed"))
        assert dormant["exists"] is True and dormant["object"] == "JungleAssassinHide"
        assert awake["exists"] is landed["exists"] is True
        assert awake["object"] == landed["object"] == "JungleAssassin"
        actor = finite(awake["id"], "Awakened native actor identity", minimum=1)
        assert landed["id"] == actor and dormant["id"] != actor
        actors.append(actor)
        # Engine collision/visibility builtins serialize as numeric0/1 in
        # GameMaker VM snapshots; fixture-authored flags above stay booleans.
        assert landed["visible"] == 1 and landed["alpha"] == 1
        assert landed["in_wall"] == 0 and landed["on_floor"] == 1
        assert finite(landed["top"], "Landed native Top ownership") < 0
        if row["wall"]:
            assert finite(dormant["top"], "Dormant native wall Top identity", minimum=1) != awake["top"]
            assert finite(awake["top"], "Awakened native wall Top identity", minimum=1)
            assert landed["mask"] != awake["mask"] and landed["depth"] != awake["depth"], \
                "Wall landing did not restore its own native collision/depth"
        else:
            assert dormant["top"] < 0 and awake["top"] < 0
            assert landed["mask"] == awake["mask"], "Ground control unexpectedly changed its native collision mask"
        assert isinstance(row["samples"], list)
        assert all(sample["id"] == actor and sample["object"] == "JungleAssassin" for sample in row["samples"])
        nonlethal, lethal = row["nonlethal"], row["lethal"]
        assert nonlethal["phase"] == 3 and lethal["phase"] == 5
        assert nonlethal["target"] == lethal["target"] == actor
        assert nonlethal["consumed"] is lethal["consumed"] is True
        assert finite(nonlethal["bullet"], "Nonlethal actual Bullet1 identity", minimum=1) != \
            finite(lethal["bullet"], "Lethal actual Bullet1 identity", minimum=1)
        assert nonlethal["damage"] == 3 and nonlethal["before"] == landed["hp"] > 3
        assert nonlethal["after"] == nonlethal["before"] - 3 == lethal["before"]
        assert lethal["damage"] == lethal["before"] + 100
        if lethal.get("after") is not None:
            assert finite(lethal["after"], "Lethal actual Bullet1 remaining HP") <= 0
        death = finite(row["death_ticks"], "Native assassin death source ticks", minimum=1)
        portal = row["portal"]
        assert finite(portal["id"], "Original native Portal identity", minimum=1) != actor
        assert portal["type"] == 1, "Ordinary Jungle combat did not open its original Portal"
        assert 0 <= finite(portal["ticks"], "Original native Portal source ticks") - death < 180
        finite(portal["x"], "Original native Portal x"); finite(portal["y"], "Original native Portal y")
    assert len(set(actors)) == 4, "Biome acceptance reused one actor across independent scenes"
    return {**evidence, "artifact": name,
            "scope": "Actual native JungleAssassinHide wake, independent wall/ground controls, scheduled Top landing, real Bullet1 damage/death and ordinary Portal at30/60Hz; not physical phone or every hidden-enemy acceptance"}


def verify_drone_performance(smoke, artifacts, directory):
    """Bind dense drone optimization to full collision/allegiance/RNG parity."""
    name = "frontier-drone-performance204.json"
    evidence = json_artifact(name, artifacts, directory)
    assert evidence["physical_device_tested"] is False and evidence["production_rules_unchanged"] is True
    assert json_log(smoke, "FRONTIER DRONE204 ACCEPTED ") == evidence, \
        "Drone artifact differs from actual dense native acceptance"
    matrix = "NTUF HYPERION real source drone/shock: native projectile/grenade callbacks, current-team reflection, player/allied explosives/lasers and hostile pursuit PASS"
    assert smoke.splitlines().count(matrix) == 1, "Dense optimization omitted the actual native source collision matrix"
    rows = evidence["benchmarks"]
    assert isinstance(rows, list) and len(rows) == 4
    assert [(row["reference"]["rate"], row["reference"]["shock"]) for row in rows] == [
        (30, False), (30, True), (60, False), (60, True)]
    prefix = "PASS NTUF Hyperion dense real native collision at30/60Hz, live nearest parity and both RNG ladders "
    assert json_log(smoke, prefix) == rows, "Drone paired callback benchmark differs from the native summary"
    for row in rows:
        old, new = row["reference"], row["optimized"]
        assert old["reference"] is True and new["reference"] is False
        assert type(old["shock"]) is bool and new["shock"] is old["shock"]
        assert old["rate"] == new["rate"]
        for sample in (old, new):
            assert sample["projectiles"] == 512
            assert sample["hostile_intercepted"] == 320 and sample["allied_neutral_typ0_passed"] == 192
            assert sample["query_checks"] == 16 and sample["query_iterations"] == 96
            assert sample["missing_typ_ignored"] is True, "Dense nearest lookup did not exclude the genuine no-typ projectile"
            finite(sample["query_us"], "Dense actual nearest-query microseconds", minimum=1)
            finite(sample["callback_us"], "Dense actual collision callback microseconds", minimum=1)
            for ladder in ("native_rng_next", "source_rng_next"):
                assert isinstance(sample[ladder], list) and len(sample[ladder]) == 5
                assert all(0 <= finite(value, "Dense actual RNG continuation") < 1 for value in sample[ladder])
        assert old["native_rng_next"] == new["native_rng_next"] and old["source_rng_next"] == new["source_rng_next"], \
            "Drone optimization altered native/source combat RNG continuation"
        assert old["null_effects"] == old["sound_requests"] == 320
        assert 32 <= new["null_effects"] <= 64 and new["sound_requests"] == 1, \
            "Dense drone budget changed interception instead of overlapping cosmetics"
        assert math.isclose(finite(row["query_ratio"], "Dense query ratio", minimum=0),
                            new["query_us"] / old["query_us"], rel_tol=1e-12, abs_tol=1e-12)
        assert math.isclose(finite(row["callback_ratio"], "Dense callback ratio", minimum=0),
                            new["callback_us"] / old["callback_us"], rel_tol=1e-12, abs_tol=1e-12)
    moving = evidence["natural_collision"]
    assert isinstance(moving, list) and [(row["rate"], row["reference"]) for row in moving] == [
        (30, True), (30, False), (60, True), (60, False)]
    for row in moving:
        assert type(row["reference"]) is bool
        assert row["host_frames"] == 16 * row["rate"] / 30 and row["source_ticks"] == 16
        assert row["projectiles"] == 512 and row["hostile_intercepted"] == row["allied_neutral_passed"] == 256
        finite(row["elapsed_us"], "Dense actual moving native collision microseconds", minimum=1)
    destroyed = evidence["destroy_callbacks"]
    assert isinstance(destroyed, list) and [(row["rate"], row["shock"], row["projectile"], row["reference"])
                                          for row in destroyed] == [
        (rate, shock, projectile, reference) for rate in (30, 60) for shock in (False, True)
        for projectile in ("Grenade", "StickyGrenade", "FRCustomProjectile") for reference in (True, False)]
    for row in destroyed:
        assert type(row["reference"]) is type(row["shock"]) is bool
        assert row["native_explosions"] == {"Grenade": 1, "StickyGrenade": 3, "FRCustomProjectile": 0}[row["projectile"]]
        assert row["source_destroy_calls"] == (1 if row["projectile"] == "FRCustomProjectile" else 0)
        assert row["source_destroy_id_matches"] is True, "Intercepted source projectile lost or duplicated its own Destroy callback"
    return {**evidence, "artifact": name,
            "scope": "Paired dense real source drone/shock callbacks, live nearest parity, unchanged RNG, genuine moving native collisions and24 native/source Destroy controls at30/60Hz; cosmetic coalescing only, no universal FPS or phone hardware acceptance"}


def verify_biome_crate_attacks(row, ticks):
    """Bind ordinary hostile-crate blasts to actual before/after ownership."""
    attacks = row["crate_attacks"]
    samples = [*row["samples"], row["final"]]
    assert isinstance(attacks, list)
    for sample in samples:
        assert isinstance(sample["wall_crates"], list)
        assert len({crate["id"] for crate in sample["wall_crates"]}) == len(sample["wall_crates"])
    assert len({attack["crate"] for attack in attacks}) == len(attacks), "Natural hostile crate attacked more than once"
    assert len({attack["attack"] for attack in attacks}) == len(attacks), "Natural hostile crates reused an Explosion identity"
    for attack in attacks:
        when = finite(attack["ticks"], "Natural crate attack source ticks", minimum=1)
        assert when <= ticks
        for field in ("crate", "loot", "attack", "creator"):
            finite(attack[field], "Natural crate attack " + field, minimum=1)
        assert attack["object"] == "Explosion" and attack["damage"] == 5 and attack["team"] == 2, \
            "Natural crate requires an ordinary default-damage friendly Explosion"
        assert attack["creator_object"] == "Player" and attack["loot_enemy"] == 1 \
            and finite(attack["loot_team"], "Natural hostile crate loot team", minimum=0) != 2, \
            "Natural crate attack must have a real player creator and hostile enemy loot"
        finite(attack["loot_hp"], "Natural hostile crate loot HP", minimum=0.000001)
        walls = attack["walls"]
        assert isinstance(walls, list) and walls and len(set(walls)) == len(walls)
        for identity in (attack["crate"], attack["loot"], *walls):
            finite(identity, "Natural crate owned identity", minimum=1)
            assert identity not in row["baseline_ids"], "Natural crate reused a parked baseline identity"
        before = [sample for sample in samples if sample["ticks"] <= when]
        assert before, "Natural crate attack lacks its prior ownership snapshot"
        prior = max(before, key=lambda sample: sample["ticks"])
        owned = [crate for crate in prior["wall_crates"] if crate["id"] == attack["crate"]]
        assert len(owned) == 1, "Natural crate attack lacks its actual crate owner"
        crate = owned[0]
        assert crate["loot_exists"] == 1 and crate["loot"] == attack["loot"] \
            and crate["loot_object"] == attack["loot_object"], "Natural crate loot ownership differs"
        # Explosion.Create retains its native independent orandom(2) offsets.
        # Bind the resulting centre to that exact constructor allowance.
        assert all(abs(finite(attack[axis], "Natural crate blast " + axis)
                       - finite(crate[axis], "Natural crate centre " + axis)) <= 2
                   for axis in ("x", "y")), "Natural crate blast left its native constructor jitter bounds"
        assert {wall["id"] for wall in crate["walls"] if wall["exists"] == 1} == set(walls), \
            "Natural crate attack changed its owned live wall set"
        assert any(actor["id"] == attack["loot"] and actor["object"] == attack["loot_object"]
                   for actor in prior["actors"]), "Natural crate loot was not an observed hostile enemy"
        after = [sample for sample in samples if sample["ticks"] > when]
        assert after and any(not any(crate["id"] == attack["crate"] and
            any(wall["exists"] == 1 and wall["id"] in walls for wall in crate["walls"])
            for crate in sample["wall_crates"]) for sample in after), \
            "Natural Explosion never opened its recorded hostile crate walls"
    return len(attacks)


def verify_biome_maps(smoke, artifacts, directory):
    """Require populated asynchronous Desert/Jungle maps to clear through combat."""
    name = "frontier-biome-clearance204-maps.json"
    evidence = json_artifact(name, artifacts, directory)
    assert evidence["passed"] is True and evidence["physical_device_tested"] is False
    rows = evidence["cases"]
    expected = [(area, subarea, loops, seed, rate) for loops in (0, 1, 3)
                for area, subarea, seed, rate in ((1, 2, 100005, 30), (1, 2, 100006, 60),
                                                (105, 1, 204071, 30), (105, 1, 204086, 60))]
    fields = ("area", "subarea", "loops", "seed", "rate")
    assert isinstance(rows, list) and [tuple(row[field] for field in fields) for row in rows] == expected, \
        "Biome map acceptance lost a seeded area/Loop/rate profile"
    accepted = "BIOME CLEARANCE204 MAP ACCEPTED "
    assert [json.loads(line[len(accepted):]) for line in smoke.splitlines() if line.startswith(accepted)] == rows, \
        "Biome map artifact differs from the twelve actual native completed maps"
    begin = "BIOME CLEARANCE204 MAP BEGIN "
    assert [json.loads(line[len(begin):]) for line in smoke.splitlines() if line.startswith(begin)] == [
        {field: row[field] for field in fields} for row in rows], "Biome map native generation profiles differ"
    assert not any(line.startswith("BIOME CLEARANCE204 MAP FAILED ") for line in smoke.splitlines())
    pipe_kills = 0
    initial_spawners = 0
    crate_attacks = 0
    for row in rows:
        assert row["result"] == "passed"
        assert finite(row["floors"], "Populated native map floor count", minimum=21)
        finite(row["initial_enemies"], "Populated native map enemy count", minimum=1)
        initial_pipes = finite(row["initial_pipes"], "Populated native map pipe count", minimum=0)
        initial_spawners += initial_pipes
        assert isinstance(row["baseline_ids"], list) and len(set(row["baseline_ids"])) == len(row["baseline_ids"])
        assert isinstance(row["baseline_skills"], list)
        for field in ("births", "lifecycle", "approaches"):
            assert isinstance(row[field], list)
        samples, final, portal = row["samples"], row["final"], row["portal"]
        assert isinstance(samples, list) and samples and samples[0]["ticks"] == 0
        assert samples[0]["enemies"] == row["initial_enemies"]
        pipes = samples[0]["big_pipes"]
        assert len(pipes) == initial_pipes and len({pipe["id"] for pipe in pipes}) == initial_pipes
        for actor in [*samples[0]["actors"], *pipes]:
            assert actor["id"] not in row["baseline_ids"], "Natural map retained a parked baseline actor/spawner"
        # Ordinary source clearance excludes neutral BigPipes and dormant
        # ambush props. A type1 Portal may legitimately coexist with them;
        # retain their snapshots without inventing a stronger win condition.
        assert final["clear_check"] is False and final["portals"] >= 1
        finite(final["enemies"], "Native final enemy instance count", minimum=0)
        finite(final["pending_police"], "Native final pending police count", minimum=0)
        assert isinstance(final["big_pipes"], list) and isinstance(final["dormant"], list)
        ticks = finite(portal["ticks"], "Natural map original exit source ticks", minimum=1)
        assert ticks <= 900 and final["ticks"] == ticks
        assert portal["type"] == 1 and finite(portal["id"], "Natural map original Portal identity", minimum=1)
        finite(portal["x"], "Natural map original Portal x"); finite(portal["y"], "Natural map original Portal y")
        sampled_ticks = [finite(sample["ticks"], "Natural map sample source ticks", minimum=0) for sample in samples]
        assert sampled_ticks == sorted(set(sampled_ticks)) and sampled_ticks[-1] <= ticks
        crate_attacks += verify_biome_crate_attacks(row, ticks)
        hits = row["hits"]
        assert isinstance(hits, list) and hits, "Natural map has no actual native Bullet1 combat evidence"
        damaging = []
        for hit in hits:
            assert hit["team"] == 2 and type(hit["consumed"]) is bool
            for field in ("bullet", "requested", "target", "damage"):
                finite(hit[field], "Natural actual Bullet1 " + field, minimum=1)
            assert hit["target"] not in row["baseline_ids"]
            assert 0 < finite(hit["ticks"], "Natural actual Bullet1 source ticks") <= ticks
            hp = finite(hit["hp"], "Natural actual Bullet1 target HP")
            after = hit.get("after")
            if after is not None:
                finite(after, "Natural actual Bullet1 remaining target HP")
            if hp > 0 and (after is None or after < hp):
                damaging.append(hit)
        assert any(hit["object"] != "NTTEFullBigPipe" for hit in damaging), "Natural map was not cleared through real enemy damage"
        assert finite(row["test_bullets"], "Natural map actual Bullet1 emissions", minimum=1) >= len({hit["bullet"] for hit in hits})
        for pipe in pipes:
            pipe_kills += any(hit["target"] == pipe["id"] and hit["object"] == "NTTEFullBigPipe"
                              and hit["consumed"] is True and hit["damage"] >= hit["hp"]
                              and (hit.get("after") is None or hit["after"] <= 0) for hit in damaging)
    assert initial_spawners > 0, "Natural map acceptance never included a live BigPipe spawner"
    assert crate_attacks > 0, "Natural map acceptance never exercised an authored hostile WallCrate"
    return {**evidence, "artifact": name, "actual_bigpipe_combat_deaths": pipe_kills,
            "initial_bigpipe_instances": initial_spawners,
            "actual_hostile_crate_explosions": crate_attacks,
            "scope": "Twelve seeded asynchronous Desert/Jungle maps atLoop0/1/3 and30/60Hz, real Bullet1 combat and source scr_check_enemies/type1 exits, preserving nonblocking neutral/dormant props; not every seed or physical phone acceptance"}



def verify_bluescreen_ui(case, smoke, artifacts, directory):
    """Bind the admission outcome to its real input, actors and native lifecycle."""
    match = re.fullmatch(r"FrontierBluescreenUI204(Yes|No|Disabled|Visited)(30|60)Tests", case)
    assert match, "Unknown Blue admission identity"
    choice, rate_text = match.groups()
    rate, accept = int(rate_text), choice == "Yes"
    mode = choice.lower() if choice in {"Disabled", "Visited"} else "eligible"
    eligible = mode == "eligible"
    name = "frontier-bluescreen-ui204.json"
    evidence = json_artifact(name, artifacts, directory)
    assert evidence["passed"] is True and evidence["physical_device_tested"] is False
    assert evidence["phase"] == 7 and evidence["rate"] == rate, "Blue rate/final phase mismatch"
    assert evidence["accept"] is accept and evidence["entry_mode"] == mode \
        and evidence["eligible"] is eligible, "Blue choice/admission eligibility mismatch"
    completion = "PASS scheduled Robot fatal damage, auto-created blue YES/NO, raw touch, delayed EndStep and native destination/death lifecycle"
    assert smoke.splitlines().count(completion) == 1, "Missing actual native death/admission assertions"
    snapshots, observations, inputs = (evidence[key] for key in ("snapshots", "observations", "input_frames"))
    for prefix, expected in (("BLUESCREEN UI204 SNAPSHOT ", snapshots),
                             ("BLUESCREEN UI204 ACTOR ", observations),
                             ("BLUESCREEN UI204 RAW TOUCH ", inputs)):
        actual = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
        assert actual == expected, ("Blue artifact differs from scheduled native observations", prefix)
    final = evidence["final"]
    assert snapshots and final == snapshots[-1] and final["label"] == "accepted"
    assert json_log(smoke, "BLUESCREEN UI204 ACCEPTED ") == {
        "rate": rate, "accept": accept, "frames": evidence["host_frames"], "input": inputs, "final": final}
    assert evidence["host_frames"] == final["host"] < rate * 70
    labels = [row["label"] for row in snapshots]
    expected = ["start", "authentic-level-start", "fatal-damage-requested"]
    expected += (["natural-controller", "natural-buttons", "drawn-before-input", "after-touch-and-endstep",
                  "postclick-later-frame", "postclick-later-frame"] +
                 (["native-portal-room-handoff"] if accept else [])) if eligible else ["ineligible-native-gameover"]
    assert labels == expected + ["accepted"], "Blue lifecycle omitted/reordered native boundaries"
    for index, row in enumerate(snapshots):
        for key in ("host", "frame", "serial"):
            finite(row[key], "Blue native " + key, minimum=0)
            if index:
                assert (row[key] >= snapshots[index - 1][key] if key == "serial" else
                        row[key] > snapshots[index - 1][key]), "Blue native lifecycle did not advance"
        assert row["native"]["smoke_active"] is True, "Blue lost isolated smoke/save mode"
    start, alive, fatal = snapshots[:3]
    assert start["host"] == 0 and alive["players"] == 1 and alive["player"]["exists"] is True
    assert alive["player"]["object"] == "Player" and alive["player"]["race"] == 8
    assert alive["wibbly_managers"] == 1 and alive["native"]["floors"] > 0 \
        and alive["native"]["walls"] > 0, "Blue did not start a genuine populated native level/manager"
    manager = evidence["manager_before_death"]
    assert manager["id"] > 0 and manager["living"] == 1 and manager["race"] == "robot"
    slot = finite(manager["slot"], "Blue native player slot", minimum=0)
    assert slot == int(slot) and slot < 4
    assert [manager["x"], manager["y"]] == [alive["player"]["x"], alive["player"]["y"]]
    assert fatal["players"] == 1 and fatal["player"]["id"] == alive["player"]["id"]
    assert fatal["host"] > alive["host"] and not alive["gameover"] and not fatal["gameover"]
    png_artifact("frontier-bluescreen-ui204-after.png", artifacts, directory, dimensions=(426, 240))
    if not eligible:
        assert inputs == observations == [] and evidence["actual_click"] is None
        assert evidence["stale_press"] is None and evidence["draw_counts"] == {}
        assert evidence["connection_draws"] == evidence["denial_draws"] == 0
        for row in snapshots:
            assert not row["controller"]["exists"] and row["buttons"] == [] and row["portals"] == []
        for row in snapshots[3:]:
            assert row["players"] == 0 and not row["player"]["exists"] and row["gameover"]
        assert final["host"] - snapshots[3]["host"] >= rate, "Ineligible ordinary death was not stable for one second"
    else:
        png_artifact("frontier-bluescreen-ui204-before.png", artifacts, directory, dimensions=(426, 240))
        natural, buttons, drawn, cleaned = snapshots[3:7]
        controller = natural["controller"]
        assert controller["exists"] is True and controller["name"] == "fr_bluescreenController"
        assert natural["players"] == 1 and natural["player"]["exists"] is True
        assert natural["player"]["id"] != fatal["player"]["id"], "Admission did not revive the actually killed Robot"
        assert all(not row["gameover"] for row in snapshots[:6]), "Premature native GameOver bypassed Blue admission"
        assert len(buttons["buttons"]) == len(drawn["buttons"]) == 2
        ids = {row["id"] for row in buttons["buttons"]}
        assert len(ids) == 2 and {row["yes"] for row in buttons["buttons"]} == {True, False}
        for row in (buttons, drawn):
            assert row["controller"]["id"] == controller["id"] and row["controller"]["exists"]
            assert {button["id"] for button in row["buttons"]} == ids
            for button in row["buttons"]:
                assert button["exists"] and button["creator"] == controller["id"] and button["creator_exists"]
                assert button["done"] is False and button["visible"] and button["alpha"] > 0
        stale = evidence["stale_press"]
        assert json_log(smoke, "BLUESCREEN UI204 PREEXISTING HELD TOUCH ") == stale
        assert 90 <= stale["blueTime"] < 115 and stale["host"] < buttons["host"] < drawn["host"]
        for actor_id in ids:
            key = str(int(actor_id))
            assert evidence["draw_counts"][key] >= 2
            actual_draws = [row for row in observations if row["kind"] == "draw" and row["self"] == actor_id]
            assert len(actual_draws) >= 2 and actual_draws[0]["host"] < actual_draws[1]["host"] <= drawn["host"]
        selected = next(button for button in drawn["buttons"] if button["yes"] is accept)
        assert len(inputs) == 3 and [row["pressed"] for row in inputs] == [False, True, False]
        for index, row in enumerate(inputs):
            assert row["touch"] == 4 and row["button"] == selected["id"]
            assert row["held"] is (index == 1) and row["released"] is (index != 1)
            if index:
                assert row["host"] == inputs[index - 1]["host"] + 1 \
                    and row["hardware_frame"] == inputs[index - 1]["hardware_frame"] + 1
                assert math.isclose(row["frame"] - inputs[index - 1]["frame"], 30 / rate)
            wx = row["view"][0] + row["x"] * drawn["view"][2] / drawn["gui"][0]
            wy = row["view"][1] + row["y"] * drawn["view"][3] / drawn["gui"][1]
            left, top, right, bottom = selected["box"]
            assert left <= wx <= right and top <= wy <= bottom, "Raw touch missed its actual visible admission button"
        assert inputs[0]["host"] == drawn["host"]
        click = evidence["actual_click"]
        assert click in observations and click["kind"] == "step" and click["ready"] is True
        assert click["self"] == selected["id"] and click["click"] == slot
        assert click["actor"]["done"] is True and click["actor"]["yes"] is accept
        assert inputs[1]["host"] <= click["host"] <= inputs[2]["host"]
        pointer = click["pointer"]
        assert pointer["ready"] is True and pointer["output"]["held"] is True
        assert [pointer["output"][key] for key in ("x", "y")] == [inputs[1][key] for key in ("x", "y")]
        if rate == 60:
            assert inputs[1]["ready"] is False and inputs[2]["ready"] is True
            assert pointer["samples"]["held"] is False, "60Hz test did not carry a one-frame raw press into the next source tick"
        ends = [row for row in observations if row["kind"] == "end-before"]
        assert len(ends) == 2 and {row["self"] for row in ends} == ids
        assert all(row["actor"]["done"] is True and row["host"] == click["host"] for row in ends)
        assert observations.index(click) < min(observations.index(row) for row in ends)
        assert cleaned["host"] > click["host"] and cleaned["buttons"] == [], "Missing deferred native EndStep cleanup"
        if accept:
            assert all(not row["gameover"] for row in snapshots), "YES retained premature native GameOver"
            for row in snapshots[6:9]:
                assert [row["area"], row["subarea"]] == [302, 0] and row["players"] == 1
                assert row["controller"]["exists"] and row["controller"]["drawConnect"] is True
                assert len(row["portals"]) == 1 and row["portals"][0]["id"] == cleaned["portals"][0]["id"]
            assert cleaned["portals"][0]["type"] == 3 and cleaned["portals"][0]["endgame"] > 0
            handoff = snapshots[-2]
            assert [handoff["area"], handoff["subarea"]] == [302, 1] and not handoff["controller"]["exists"]
            assert [final["area"], final["subarea"]] == [302, 1] and final["players"] == 1 and final["player"]["exists"]
            assert final["native"]["floors"] > 0 and final["native"]["walls"] > 0 \
                and final["native"]["gen"] == final["native"]["floormakers"] == 0 \
                and not final["native"]["generation_screen"], "YES faked destination without actual generated Cyberspace terrain"
            assert final["host"] - handoff["host"] >= rate and final["buttons"] == []
            assert evidence["connection_draws"] >= 2 and evidence["denial_draws"] == 0
        else:
            assert all(row["players"] == 0 and not row["player"]["exists"] and row["gameover"]
                       and not row["controller"]["exists"] and row["buttons"] == [] for row in snapshots[6:])
            assert [final["area"], final["subarea"]] == [fatal["area"], fatal["subarea"]]
            assert final["host"] - cleaned["host"] >= rate
            denied = [row for row in observations if row["kind"] == "deny-binding-draw"]
            assert evidence["denial_draws"] >= 2 and len(denied) >= 2 and evidence["connection_draws"] == 0
            binding = next(row for row in cleaned["bindings"] if "denybluescreen_draw" in row["code"])
            assert all(row["self"] == binding["id"] and row["creator"] == selected["id"] for row in denied)
    return {"artifact": name, "rate": rate, "accept": accept, "entry_mode": mode,
            "raw_input_frames": len(inputs), "scheduled_observations": len(observations),
            "scope": "Actual scheduled Robot death, manager/admission gate, raw touch, deferred EndStep and native destination/death assertions (including preserved deathcause); no physical device validation"}


def verify_menu_input(case, smoke, artifacts, directory):
    """Require the scheduled owner loss and working native input positive controls."""
    match = re.fullmatch(r"FrontierMenuInput204(30|60)Tests", case)
    assert match, "Unknown native menu input identity"
    rate = int(match.group(1))
    name = "frontier-menu-input204.json"
    evidence = json_artifact(name, artifacts, directory)
    assert evidence["passed"] is True and evidence.get("failure") is None
    assert evidence["rate"] == rate and evidence["phase"] == 8 and evidence["scenario"] == 3
    assert evidence["physical_device_tested"] is False and evidence["os_mouse_dispatch_emulated"] is True
    completion = "PASS scheduled raw JoystickMove owner removal, native menu idle, touch/keyboard/controller/mode positive controls"
    assert smoke.splitlines().count(completion) == 1, "Missing completed native input lifecycle assertions"
    assert smoke.splitlines().count("MENU INPUT204 START rate=" + str(rate)) == 1
    pointer = "PASS FRONTIER INPUT204 real libMenu30/60Hz short press, same-host early/late polls, once-only later source ticks, stale pre-button hold, local hitbox/slot and release: 18"
    assert evidence["source_pointer_checks"] == 18 and smoke.splitlines().count(pointer) == 1
    positive = evidence["positive"]
    assert len(positive) == 4
    assert positive[0]["kind"] == "raw-touch-native-mouse4"
    finite(positive[0]["race"], "Native touch selection race", minimum=0)
    assert positive[1:] == [
        {"kind": kind, "fresh_edges": 2, "held_repeats": 0, "neutral_repeats": 0}
        for kind in ("keyboard-native-general", "analogue+dpad-native-general")
    ] + [{"kind": "controller-to-touch-mode", "repeats": 0}], "Native menu positive controls were incomplete"
    assert json_log(smoke, "MENU INPUT204 ACCEPTED ") == {
        "rate": rate, "scenarios": 3, "positive": positive, "source_pointer_checks": 18,
        "physical_device_tested": False, "options_reader_input_ownership_checked": True}

    def touch_mode(row):
        assert row["touch"] is True and row["keyboard"] is False and row["gamepad"] is False, "Expected real touch input mode"

    observations = evidence["observations"]
    assert len(observations) == 3 * (2 + 2 * rate) + 2, "Incomplete native menu observations"
    logged = []
    for scenario in range(3):
        rows = observations[scenario * (2 + 2 * rate):(scenario + 1) * (2 + 2 * rate)]
        fresh, entered, *idle = rows
        direction = {"east": scenario != 1, "west": scenario == 1, "north": False, "south": False}
        assert fresh["label"] == "real-joystick-fresh-edge" and fresh["phase"] == 1 and fresh["owners"] == 1
        assert entered["label"] == "native-menu-entered-with-stale-edge" and entered["phase"] == 2
        assert fresh["host"] == entered["host"] and fresh["input_frame"] == entered["input_frame"]
        assert entered["owners"] == 0 and entered["menus"] == 1 and entered["characters"] >= 2
        logged += [fresh, entered]
        for row in rows:
            touch_mode(row)
            assert row["scenario"] == scenario and row["direction"] == direction, "Missing real stale joystick direction"
            for key in ("host", "input_frame", "frame", "selection", "race"):
                finite(row[key], "Native menu " + key, minimum=0)
        for index, row in enumerate(idle):
            assert row["label"] == "idle" and row["phase"] == 2
            assert row["owners"] == 0 and row["menus"] == 1 and row["characters"] == entered["characters"]
            assert row["race"] == entered["race"] and row["selection"] == entered["selection"], "Stale touch changed native character selection"
            assert row["host"] == entered["host"] + index + 1
            assert math.isclose(row["frame"] - entered["frame"], (index + 1) * 30 / rate)
            if index % rate == 0:
                logged.append(row)
        png_artifact("frontier-menu-input204-idle-" + str(scenario) + ".png", artifacts, directory, dimensions=(426, 240))
    controller, options_edge = observations[-2:]
    assert controller["label"] == "controller-before-touch-mode-boundary" and controller["phase"] == 6
    assert controller["keyboard"] is False and controller["gamepad"] is True and controller["touch"] is False
    assert controller["owners"] == 0 and controller["menus"] == 1 and controller["characters"] >= 2
    assert options_edge["label"] == "real-joystick-fresh-edge" and options_edge["phase"] == 7 and options_edge["owners"] == 1
    touch_mode(options_edge)
    assert options_edge["direction"] == {"east": False, "west": False, "north": True, "south": False}
    assert options_edge["race"] == controller["race"] and options_edge["selection"] == controller["selection"]
    assert controller["scenario"] == options_edge["scenario"] == 3
    assert positive[0]["race"] != entered["race"], "Touch positive control did not change the selected character"
    logged += [controller, options_edge]
    actual = [json.loads(line[len("MENU INPUT204 OBSERVE "):]) for line in smoke.splitlines()
              if line.startswith("MENU INPUT204 OBSERVE ")]
    assert actual == logged, "Menu artifact differs from native scheduled observations"
    assert evidence["transitions"] == [row for previous, row in zip(observations, observations[1:])
                                       if previous["race"] != row["race"]], "Native selection transition history differs"

    inputs = evidence["inputs"]
    phases = sum(([1] + [2] * (2 * rate - 1) for _ in range(3)), [])
    phases += [3] * 8 + [4] * 21 + [5] * 21 + [6] * (rate + 1) + [7]
    assert [row["phase"] for row in inputs] == phases, "Missing/reordered raw native input frames"
    for index, row in enumerate(inputs):
        for key in ("host", "frame"):
            finite(row[key], "Raw native input " + key, minimum=0)
            if index:
                assert row[key] == inputs[index - 1][key] + 1, "Raw native hardware frames did not advance"
        sample = row["touch"]
        for key in ("held", "pressed", "released"):
            assert type(sample[key]) is bool, "Raw touch flag is not an actual boolean"
        for key in ("x", "y"):
            finite(sample[key], "Raw native touch coordinate")
        if row["phase"] not in {1, 2, 3, 7}:
            assert not any(sample[key] for key in ("held", "pressed", "released"))
        if row["phase"] != 4:
            assert row["keyboard"] == {"held": -1, "pressed": -1, "released": -1}
        if row["phase"] not in {5, 6}:
            assert row["pad"] == {"x": 0, "button": -1}
    for scenario in range(3):
        raw = inputs[scenario * 2 * rate:(scenario + 1) * 2 * rate]
        fresh, *idle = raw
        assert fresh["touch"]["held"] and fresh["touch"]["pressed"] and not fresh["touch"]["released"]
        observed = observations[scenario * (2 + 2 * rate)]
        assert fresh["host"] == observed["host"] and fresh["frame"] == observed["input_frame"]
        for index, row in enumerate(idle):
            sample = row["touch"]
            assert [sample[key] for key in ("x", "y")] == [fresh["touch"][key] for key in ("x", "y")]
            assert sample["pressed"] is False
            assert sample["held"] is (scenario == 1 and index < 9)
            assert sample["released"] is ((scenario == 0 and index == 0) or (scenario == 1 and index == 9))
    touch = [row["touch"] for row in inputs if row["phase"] == 3]
    assert [row["pressed"] for row in touch] == [True] + [False] * 7
    assert [row["held"] for row in touch] == [True] + [False] * 7
    assert [row["released"] for row in touch] == [False, True] + [False] * 6
    assert 0 <= touch[0]["x"] < 426 and 0 <= touch[0]["y"] < 240, "Native character touch was not in GUI space"
    keyboard = [row["keyboard"] for row in inputs if row["phase"] == 4]
    key = finite(keyboard[2]["pressed"], "Raw native right key", minimum=1)
    for index, row in enumerate(keyboard):
        assert row == {"held": key if 2 <= index <= 6 or 10 <= index <= 14 else -1,
                       "pressed": key if index in {2, 10} else -1,
                       "released": key if index in {7, 15} else -1}
    pad = [row["pad"] for row in inputs if row["phase"] == 5]
    button = finite(pad[10]["button"], "Raw native D-pad key", minimum=1)
    for index, row in enumerate(pad):
        assert row == {"x": .8 if 2 <= index <= 6 else 0,
                       "button": button if 10 <= index <= 14 else -1}
    boundary = [row["pad"] for row in inputs if row["phase"] == 6]
    assert boundary == [{"x": .8, "button": -1}] + [{"x": 0, "button": -1}] * rate
    assert inputs[-1]["touch"]["held"] and inputs[-1]["touch"]["pressed"] and not inputs[-1]["touch"]["released"]

    options = evidence["options_observations"]
    assert len(options) == 7 and json_log(smoke, "MENU INPUT204 SEPARATE TOUCH OPTIONS OBSERVATION ") == options
    for index, row in enumerate(options):
        touch_mode(row)
        assert row["kh"] == row["kv"] == 0, "Stale touch navigated the independent native options reader"
        assert row["host"] == inputs[-1]["host"] + index + 1
        finite(row["pointed"], "Native options pointed diagnostic", minimum=-1)
    assert evidence["host_frames"] == inputs[-1]["host"] + 8 < rate * 35
    png_artifact("frontier-menu-input204-after.png", artifacts, directory, dimensions=(426, 240))
    return {"artifact": name, "rate": rate, "idle_scenarios": 3, "idle_host_frames": 6 * rate,
            "raw_input_frames": len(inputs), "positive_controls": positive,
            "source_pointer_checks": 18, "physical_device_tested": False, "os_mouse_dispatch_emulated": True,
            "scope": "Scheduled native JoystickMove owner loss, three two-second touch-mode character idles, raw touch/keyboard/analogue/D-pad/mode positive controls and independent options input ownership; OS Mouse4 delivery emulated, no physical phone/controller validation"}


def verify204_identity(case, smoke, artifacts, directory):
    """Require the new204 branches, beyond a generic current-VM PASS marker."""
    if case == "FrontierPost203CompatTests":
        evidence = json_artifact("frontier-post203-compat.json", artifacts, directory)
        assert evidence["native_area_forms"] == 21 and evidence["ntuf_areas"] == 6
        assert evidence["source_main_steps"] == 7 and evidence["display_only_lightring"] is True
        assert len(evidence["module_normalization"]) == 5
        for pair in evidence["module_normalization"]:
            assert len(pair) == 2 and {row["oracle"] for row in pair} == {True, False}
            assert pair[0]["checksum"] == pair[1]["checksum"]
            for row in pair: finite(row["microseconds"], "Normalization callback duration", minimum=1)
        assert smoke.splitlines().count("PASS FRONTIER native area207 optional dispatch, all native area predicates, LIGHTRING display and live-alias cached module normalization") == 1
        return {**evidence, "artifact": "frontier-post203-compat.json"}
    elif case == "FrontierPost203WeatherWallTests":
        evidence = json_artifact("ntuf-post203-weather-wall.json", artifacts, directory)
        assert evidence["physical_device_tested"] is False and evidence["source_rng_unchanged"] is True
        assert evidence["chamber_areas"] == [6, 106]
        rows = evidence["rendered_join_cases"]
        assert len(rows) == 12 and all(row["seam_pixels_checked"] >= 50 for row in rows)
        assert smoke.splitlines().count("PASS NTUF Labs/HQ chamber side/out ownership and 12 rendered wide-view Blizzard join cases") == 1
        return {**evidence, "artifact": "ntuf-post203-weather-wall.json"}
    elif case == "FrontierPromptTests":
        rows = [line for line in smoke.splitlines() if line.startswith("PASS FRONTIER INPUT204 continuous ")]
        assert len(rows) == 1 and "actual touch double taps 30/60Hz" in rows[0]
        assert "native+packed wall mask" in rows[0] and "nonzero controller/reversal/D-pad/right-stick/confirm/hot-plug" in rows[0]
        assert "physical Android/iOS controller untested" in rows[0]
        return {"native_assertion_summary": rows[0], "physical_device_tested": False,
                "scope": "Native touch producer, analog direction/mask sweep and controller helpers; no physical Android/iOS or controller connectivity acceptance"}
    elif case == "FrontierEnemyVisibilityTests":
        evidence = json_artifact("frontier-enemy-visibility-diagnostic.json", artifacts, directory)
        assert evidence["physical_device_tested"] is False
        deaths = evidence["possessed_host_deaths"]
        assert len(deaths) >= 2 and all(row["rate"] in {30, 60} for row in deaths)
        assert evidence["clone_top_repair_tested"] is True and evidence["clone_toss_repair_tested"] is True
        verify_enemy_visibility_launches(smoke, evidence)
        return {**evidence, "artifact": "frontier-enemy-visibility-diagnostic.json"}
    elif case == "FrontierEnemyPossessionTests":
        return verify_possession(smoke, artifacts, directory)
    elif case == "FrontierBiomeClearance204AcceptanceTests":
        return verify_biome_clearance(smoke, artifacts, directory)
    elif case == "FrontierDronePerformance204Tests":
        return verify_drone_performance(smoke, artifacts, directory)
    elif case == "FrontierBiomeClearance204MapTests":
        return verify_biome_maps(smoke, artifacts, directory)
    elif re.fullmatch(r"FrontierBluescreenUI204(Yes|No|Disabled|Visited)(30|60)Tests", case):
        return verify_bluescreen_ui(case, smoke, artifacts, directory)
    elif re.fullmatch(r"FrontierMenuInput204(30|60)Tests", case):
        return verify_menu_input(case, smoke, artifacts, directory)
    elif case == "FrontierPerformanceTests":
        evidence = json_artifact("frontier-performance.json", artifacts, directory)
        assert evidence["physical_device_tested"] is False
        rows = evidence["rows"]
        assert len(rows) >= 15 and {row["scene"]["rate"] for row in rows} == {30, 60}
        assert {1, 2, 3, 4, 5, 6, 7, 301, 302, 303, 304, 305, 306} <= {row["scene"]["area"] for row in rows}
        for row in rows:
            assert row["source_ticks"] == 120 and abs(row["actor_ticks"] - 120) <= 1
            assert abs(row["simulation_seconds"] - 4) < .04
            elapsed = finite(row["seconds"], "Performance wall duration", minimum=.001)
            ratio = finite(row["simulation_per_second"], "Performance simulation/wall ratio", minimum=.001)
            assert math.isclose(ratio, row["simulation_seconds"] / elapsed, rel_tol=1e-12, abs_tol=1e-12)
            assert row["floors"] > 20 and row["walls"] + row["invisible_walls"] > 0 and row["enemies"] > 0
        prefix = "FRONTIER PERFORMANCE RESULT "
        logged = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
        assert logged == rows, "Performance artifact differs from the actual native samples"
        return {**evidence, "artifact": "frontier-performance.json",
                "scope": "Populated selected native Windows scenes and measured simulation progress; no universal60FPS or physical phone acceptance"}


def check_run(value, expected_cases, vm=None):
    assert isinstance(value, str) and re.fullmatch(r"\d{8}T\d+Z", value), "Invalid native run identity"
    assert tuple(expected_cases) == FINAL_CASES, "Run must verify the complete root-authored selection"
    run = ROOT / "tests" / value
    compiled = read(run / "compiled-build.json")
    assert compiled["status"] == "COMPILED_NOT_PLAYABLE_VERIFIED", run
    assert sha(run / "compile.log") == compiled["log_sha256"], run
    if vm is not None:
        assert compiled == vm, (run, "different compiled build")
    expected = set(expected_cases)
    assert len(expected) == len(expected_cases), (run, "duplicate expected case")
    directories = {path.name for path in run.iterdir() if path.is_dir()}
    assert directories == expected, (run, "case directories", sorted(directories), sorted(expected))
    paths = {path.parent.name: path for path in run.glob("*/receipt.json")}
    assert set(paths) == expected, (run, "case receipts", sorted(paths), sorted(expected))
    rows = []
    bubbles = {}
    repairs = {}
    current204 = {}
    for case in expected_cases:
        path = paths[case]
        row = read(path)
        assert row["case"] == case == path.parent.name, path
        assert row["status"] == "PASS" and row["exit"] == 0, path
        assert row["termination_reason"] is None, path
        assert row["vm_sha256"] == compiled["vm_sha256"], path
        assert row["input_sha256"] == compiled["input_sha256"], path
        assert row["physical_device_tested"] is False, path
        assert row["muted_resources"] > 100 and row["desktop"] == "private, never activated", path
        elapsed = row["elapsed_seconds"]
        assert isinstance(elapsed, (int, float)) and not isinstance(elapsed, bool) and math.isfinite(elapsed) and elapsed > 0, path
        smoke_path, runner_path = path.parent / "smoke.txt", path.parent / "runner.log"
        smoke = smoke_path.read_text("utf8")
        log = runner_path.read_text("utf8", errors="replace")
        assert "PASS full internal selected implemented branches" in smoke, path
        assert not re.search(r"^ERROR(?:\s|$)", smoke, re.MULTILINE), path
        assert "ERROR!!!" not in smoke and "ERROR!!!" not in log, path
        assert "###game_end###0" in log, path
        artifacts = row["artifacts_sha256"]
        assert isinstance(artifacts, dict), path
        actual_artifacts = {
            artifact.name for artifact in path.parent.iterdir()
            if artifact.is_file() and artifact.name.startswith(("frontier-", "ntuf-"))
            and artifact.suffix.lower() in {".png", ".json"}
        }
        assert set(artifacts) == actual_artifacts, (path, "artifact set", sorted(artifacts), sorted(actual_artifacts))
        for name, digest in artifacts.items():
            assert isinstance(name, str) and Path(name).name == name and name not in {".", ".."}, (path, name)
            assert isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest), (path, name)
            assert sha(path.parent / name) == digest, (path, name)
        semantics = verify_case_identity(case, smoke, artifacts, path.parent)
        if semantics is not None:
            current204[case] = semantics
        if case in {"FrontierBubblesStartupATests", "FrontierBubblesStartupBTests"}:
            skin = 0 if case == "FrontierBubblesStartupATests" else 1
            bubbles[case] = verify_bubbles_startup(smoke, artifacts, path.parent, skin)
        elif case == "FrontierBubblesRandomTests":
            bubbles[case] = verify_random_bubbles(smoke, artifacts, path.parent)
        elif case == "FrontierWeatherPerformanceTests":
            repairs[case] = verify_weather(smoke, artifacts, path.parent)
        elif case == "FrontierFlyWallTests":
            repairs[case] = verify_fly_wall(smoke, artifacts, path.parent)
        elif case == "FrontierPalaceBlockTests":
            repairs[case] = verify_palace(smoke)
        elif case == "FrontierMenuRepairTests":
            repairs[case] = verify_menu(smoke, artifacts, path.parent)
        rows.append({**row, "receipt": path.relative_to(ROOT).as_posix(),
                     "receipt_sha256": sha(path), "smoke_sha256": sha(smoke_path),
                     "runner_log_sha256": sha(runner_path)})
    assert set(bubbles) == {"FrontierBubblesStartupATests", "FrontierBubblesStartupBTests", "FrontierBubblesRandomTests"}, run
    assert set(repairs) == {"FrontierWeatherPerformanceTests", "FrontierFlyWallTests", "FrontierPalaceBlockTests", "FrontierMenuRepairTests"}, run
    assert set(current204) == CURRENT204_CASES, run
    assert len({row["silent_vm_sha256"] for row in rows}) == 1, (run, "different silent VM")
    return {"run": run.relative_to(ROOT).as_posix(), "compiled_build": compiled,
            "expected_cases": list(expected_cases), "count": len(rows), "results": rows,
            "bubbles_startup": bubbles, "repair_semantics": repairs,
            "current204_semantics": current204}


def verify_python_sources(evidence):
    """Bind the aggregate capture to its maintained code and reviewer inputs."""
    assert evidence.get("version") == "2.0.4" and type(evidence.get("internal")) is int \
        and evidence["internal"] == 100, "Python capture belongs to a different release"
    paths = sorted([*ROOT.joinpath("tools").glob("*.py"),
                    *ROOT.joinpath("native").glob("*.gml")])
    current = {path.relative_to(ROOT).as_posix(): sha(path) for path in paths}
    assert evidence.get("source_inputs_unchanged") is True, "Python capture inputs changed during checks"
    assert evidence.get("source_inputs") == current, "Python capture does not match current maintained inputs"
    reviewers = {name: sha(ROOT / name) for name in REVIEW_INPUTS}
    assert evidence.get("reviewer_inputs_unchanged") is True, "Reviewer capture inputs changed during checks"
    assert evidence.get("reviewer_inputs") == reviewers, "Python capture does not match current reviewer inputs"
    assert evidence.get("review_test_modules") == list(REVIEW_TESTS), "Python capture omitted or changed the explicit reviewer test modules"
    return current


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run")
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--python-evidence", type=Path, required=True)
    args = ap.parse_args()
    assert args.count == len(FINAL_CASES), ("Final selection is explicitly fixed", args.count, len(FINAL_CASES))
    current = read(ROOT / "build-windows/last-success.json")
    assert current["status"] == "COMPILED_NOT_PLAYABLE_VERIFIED"
    assert current["vm_sha256"] != "4bc772621c054e3f4a66003bac75f900d75ae99d8aeb8847359b33f5bb8c0545", "Do not inherit2.0.3 VM acceptance"
    assert current["input_sha256"] != "6849309290b02d96c9c558e730f4e56fb2bd159ba86f7915e9bb6c0160911d13", "Do not inherit2.0.3 input acceptance"
    game = (ROOT / "staging/project/objects/UberCont/Create_0.gml").read_text("utf-8-sig")
    assert '#macro GAME_VERSION "2.0.4"' in game and '#macro GAME_BUILD 3004' in game
    update = (ROOT / "staging/project/scripts/scrNTTEUpdate/scrNTTEUpdate.gml").read_text("utf-8-sig")
    assert re.search(r'#macro\s+NTTE_RELEASE_NUMBER\s+100(?:\s|$)', update)
    assert '#macro NTTE_RELEASE_VERSION "2.0.4"' in update and '#macro NTTE_RELEASE_TAG "2.0.4"' in update
    assert sha(ROOT / "build-windows/nuclearthronemobile.win") == current["vm_sha256"]
    assert sha(ROOT / "build-windows/compile.log") == current["log_sha256"]
    snapshot = build_input_manifest.snapshot()
    assert snapshot["input_sha256"] == current["input_sha256"]
    archived_path = (ROOT / current["input_manifest"]).resolve()
    assert archived_path.is_relative_to((ROOT / "analysis/build-inputs").resolve())
    archived = read(archived_path)
    assert archived["input_sha256"] == snapshot["input_sha256"]
    assert archived["staged_files"] == snapshot["staged_files"]
    assert sha(PRIOR_MANIFEST) == PRIOR_MANIFEST_SHA256, "Prior release source manifest changed"
    old_files, new_files = read(PRIOR_MANIFEST)["files"], snapshot["staged_files"]
    changed = [{"path": name, "before": old_files.get(name), "after": new_files.get(name)}
               for name in sorted(old_files.keys() | new_files.keys())
               if old_files.get(name) != new_files.get(name)]
    final = check_run(args.run, FINAL_CASES, current)
    silent_digest = sha(ROOT / "build-windows/frontier-silent.win")
    assert all(row["silent_vm_sha256"] == silent_digest for row in final["results"])
    python_evidence = args.python_evidence.resolve()
    assert python_evidence.is_relative_to((ROOT / "review").resolve()), "Python evidence must remain under review"
    py = read(python_evidence)
    verify_python_sources(py)
    assert py["exit"] == 0
    assert isinstance(py["tests"], int) and not isinstance(py["tests"], bool) and py["tests"] >= 110
    py_log = (ROOT / py["log"]).resolve()
    assert py_log.is_relative_to((ROOT / "review").resolve()), "Python output escaped review"
    assert sha(py_log) == py["log_sha256"]
    text = py_log.read_text("utf8")
    assert re.search(r"^Ran " + str(py["tests"]) + r" tests? in ", text, re.MULTILINE)
    assert re.search(r"\nOK\s*$", text)
    assert not re.search(r"^(?:FAILED|ERROR:|FAIL:)", text, re.MULTILINE)
    protected = {
        ROOT.parents[2] / 'github-publish/release-2.0.3/publication-receipt.json': '0d3318d58c857baafb7e66acc902d810344c2ddb1f760a3b8c74cd15fb0c3622',
        ROOT / 'mobile-release203-20261107/deliverables/NuclearThrone.NTTE-NTUF-iOS-2.0.3.ipa': '500ae550763281f59bd9fd1bb8efa9a31be10db24ee9eb0536dbf0afc05e491c',
        ROOT / 'mobile-release203-20261107/deliverables/NuclearThrone.NTTE-NTUF-Android-2.0.3.apk': 'b09d7404d451f81a1fa0155b694c17290a1b58ea41ccc03aafddc4a003aa575e',
    }
    with ThreadPoolExecutor(max_workers=3) as pool:
        actual = dict(zip(protected, pool.map(sha, protected)))
    assert actual == protected, "Previously published bytes changed"
    report = {"status": "SELECTED_DEVELOPMENT_CHECKS_VERIFIED", "version": "2.0.4", "internal": 100,
              "utc": datetime.now(timezone.utc).isoformat(),
              "case_selection": CASE_SELECTION.relative_to(ROOT).as_posix(),
              "case_selection_sha256": sha(CASE_SELECTION),
              "prior_source_manifest_sha256": PRIOR_MANIFEST_SHA256,
              "current_compiled_build": current, "current_native_run": final,
              "prior_vm_runs": [], "changed_inputs_since_prior_vm": changed,
              "python": {**py, "evidence_scope": "Verified the passing aggregate log/count, both explicit reviewer test modules, and exact current maintained Python/native/reviewer inputs; inputs stayed unchanged during this capture. Historical VM passes do not contribute."},
              "staged_files": len(snapshot["staged_files"]),
              "published_files_unchanged": {str(p): digest for p, digest in actual.items()},
              "physical_device_tested": False,
              "packaging_commit_publication_upload_performed": False,
              "limits": "Selected native cases belong to this current VM only; historical VM passes do not contribute. No physical Android/iOS acceptance or universal mobile FPS guarantee."}
    target = ROOT / "review" / ("post203-development-review-" + args.run + ".json")
    assert not target.exists(), "Never overwrite accepted evidence"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    print(json.dumps({"report": str(target), "sha256": sha(target),
                      "current_cases": args.count, "previous_cases": 0,
                      "python_tests": py["tests"], "changed_inputs": len(changed)}))


if __name__ == "__main__":
    main()
