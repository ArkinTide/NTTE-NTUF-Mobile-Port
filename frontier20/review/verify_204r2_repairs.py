"""Read-only build102 review retaining the complete frozen 2.0.4 semantics.

No historical PASS can satisfy this revision: all selected cases must use the
new final VM/input, and the prior build100 packages and publication stay intact.
"""
from pathlib import Path as _Path
import hashlib as _hashlib

_BASE_REVIEW = _Path(__file__).with_name("verify_post203_repairs.py")
_BASE_REVIEW_SHA256 = "96e72eb100062a585f1fd77c899c9cd782a0e7c95ec0a4b9d2d18bc408d8e703"
_raw = _BASE_REVIEW.read_bytes()
assert _hashlib.sha256(_raw).hexdigest() == _BASE_REVIEW_SHA256, "Frozen build100 reviewer changed"
_text = _raw.decode("utf-8-sig")
_REPLACEMENTS = (
    ('review/release204-cases.json', 'review/release204r2-cases.json'),
    ('mobile-release203-20261107/staged-source-manifest.json', 'mobile-release204-20261108/staged-source-manifest.json'),
    ('803d0b4fab96d42f1e853a1db33bc2af95c54bba4ad0f5d814677d6716fb8176', '60a31c739c5fc52b3a953f3d5c549dcd7ba760de4d08615b91517ecae77f6b85'),
    ('selection["internal"] == 100', 'selection["internal"] == 102'),
    ('evidence["internal"] == 100', 'evidence["internal"] == 102'),
    ('NTTE_RELEASE_NUMBER\\s+100', 'NTTE_RELEASE_NUMBER\\s+102'),
    ('"internal": 100', '"internal": 102'),
    ('4bc772621c054e3f4a66003bac75f900d75ae99d8aeb8847359b33f5bb8c0545', 'da2a770b768d84227bf415bc7b458b056612317b2ebf09820826b7889b9860b6'),
    ('6849309290b02d96c9c558e730f4e56fb2bd159ba86f7915e9bb6c0160911d13', 'b8bc9c5d34f76840e0a849c072d01ea5c7f0d87759ab69688f70636335a0f2ad'),
    ('github-publish/release-2.0.3/publication-receipt.json', 'github-publish/release-2.0.4/publication-receipt.json'),
    ('0d3318d58c857baafb7e66acc902d810344c2ddb1f760a3b8c74cd15fb0c3622', '92c226fd1896472e2f8371ee2cd129ec63432b20b20a4ad68ce5cb0040ba6265'),
    ('mobile-release203-20261107/deliverables/NuclearThrone.NTTE-NTUF-iOS-2.0.3.ipa', 'mobile-release204-20261108/deliverables/NuclearThrone.NTTE-NTUF-iOS-2.0.4.ipa'),
    ('500ae550763281f59bd9fd1bb8efa9a31be10db24ee9eb0536dbf0afc05e491c', '778a32cc4ee2aca2f06b3697a53966b8c1f5134b3f9876d891ba7f58d4fbbb32'),
    ('mobile-release203-20261107/deliverables/NuclearThrone.NTTE-NTUF-Android-2.0.3.apk', 'mobile-release204-20261108/deliverables/NuclearThrone.NTTE-NTUF-Android-2.0.4.apk'),
    ('b09d7404d451f81a1fa0155b694c17290a1b58ea41ccc03aafddc4a003aa575e', '900745f4af346c585862d74a844573227386f1092087ef717e523e89f1df4ece'),
    ('post203-development-review-', 'post204r2-development-review-'),
)
for _old, _new in _REPLACEMENTS:
    assert _text.count(_old) == 1, ("Frozen review anchor changed", _old)
    _text = _text.replace(_old, _new)
_entry = '\nif __name__ == "__main__":\n    main()\n'
assert _text.count(_entry) == 1
_text = _text.replace(_entry, "\n")
exec(compile(_text, str(_BASE_REVIEW), "exec"), globals())

REVIEW_TESTS = (*REVIEW_TESTS, "review/test_review204r2.py")
REVIEW_INPUTS = (*REVIEW_INPUTS, "review/verify_204r2_repairs.py", "review/capture204r2_python.py",
                 "review/test_review204r2.py", "review/release204r2-cases.json",
                 "review/inspect_release204r2_packages.py", "review/verify_release204r2_debug_font.py",
                 "generated-assets/boss-art204/manifest.json", "generated-assets/boss-art204/verification.json")
CURRENT204_CASES = CURRENT204_CASES | {"FrontierQuestPortal204Tests", "FrontierBossArt204Tests", "FrontierLoadoutArt204Tests", "FrontierMutationPool204Tests", "FrontierRedConnectivity204Tests"}
REQUIRED204_CASES = REQUIRED204_CASES | {"FrontierQuestPortal204Tests", "FrontierBossArt204Tests", "FrontierLoadoutArt204Tests", "FrontierMutationPool204Tests", "FrontierRedConnectivity204Tests"}
_base_verify204_identity = verify204_identity


def verify_mutation_pool(smoke, artifacts, directory):
    """Verify genuine ordinary-page coverage and preserved exclusive grants."""
    name = "frontier-mutation-pool204.json"
    evidence = json_artifact(name, artifacts, directory)
    assert evidence["status"] == "PASS" and evidence["physical_device_tested"] is False
    assert evidence["rates"] == [30, 60]
    for key in ("actual_levcont_draw_gui", "actual_random_chooser",
                "actual_rat_reward_grants", "actual_idpd_station_grants"):
        assert _mutation_flag(evidence[key], key)
    groups = evidence["groups"]
    assert set(groups) == {"mini", "hidden", "augment", "surgery", "burden"}
    fixed = {
        "mini": {"bat ears": 31, "lead ribs": 33, "magnetic pulse": 34, "toad breath": 37},
        "hidden": {"annihilation": 30, "reroll": 35, "silver tongue": 36},
    }
    augment_names = {
        "AugmentBloodlust", "AugmentBoilingVeins", "AugmentCompassion", "AugmentEagleEyes",
        "AugmentEuphoria", "AugmentExtraFeet", "AugmentGammaGuts", "AugmentHeavyHeart",
        "AugmentImpactWrists", "AugmentLaserBrain", "AugmentLastWish", "AugmentLongArms",
        "AugmentLuckyShot", "AugmentOpenMind", "AugmentRabbitPaw", "AugmentScarierFace",
        "AugmentSecondStomach", "AugmentSharpTeeth",
    }
    expected_names = {**{key: set(value) for key, value in fixed.items()}, "augment": augment_names,
        "surgery": {"SurgerySlot", "SurgerySlot2", "SurgerySlot3", "SurgerySlot4"},
        "burden": {"BurdenAutomotiveApocalypse", "BurdenBlood", "BurdenPelagicPredicament", "BurdenPlagueOfFlesh"}}
    ids, registry = {}, {}
    for group, expected in expected_names.items():
        rows = groups[group]
        assert isinstance(rows, list) and len(rows) == len(expected), ("Mutation group omitted", group)
        assert {row["name"] for row in rows} == expected, ("Mutation group identity differs", group)
        values = _mutation_ids([row["id"] for row in rows], "Mutation registry IDs")
        assert len(values) == len(set(values)), ("Duplicate mutation registry ID", group)
        ids[group] = set(values)
        registry[group] = dict(zip((row["name"] for row in rows), values))
        if group in fixed:
            assert registry[group] == fixed[group], ("Native NTTE mutation identity changed", group)
    flattened_ids = [value for group in ids.values() for value in group]
    assert len(flattened_ids) == len(set(flattened_ids)), "Exclusive groups share a mutation ID"
    assert registry["augment"] == dict(zip(sorted(augment_names), range(38, 56))), "Native IDPD augment registration changed"
    assert registry["burden"] == dict(zip(sorted(expected_names["burden"]), range(56, 60))), "Native burden registration changed"
    assert registry["surgery"] == dict(zip(sorted(expected_names["surgery"]), range(60, 64))), "Native surgery registration changed"
    rows = evidence["rows"]
    assert isinstance(rows, list) and len(rows) == 4
    combinations = []
    base_denied = ids["mini"] | ids["hidden"] | ids["surgery"] | ids["burden"]
    for row in rows:
        rate = row["rate"]
        assert type(rate) in (int, float) and rate in (30, 60)
        main = _mutation_flag(row["main_pool_augments"], "main-pool augment option")
        combinations.append((rate, main))
        eligible = _mutation_ids(row["eligible_ids"], "ordinary eligible IDs")
        assert len(eligible) > 20 and len(eligible) == len(set(eligible))
        denied = base_denied | (set() if main else ids["augment"])
        assert set(eligible).isdisjoint(denied), "Exclusive mutation is eligible in the ordinary pool"
        pages = row["pages"]
        assert isinstance(pages, list) and pages and all(isinstance(page, list) and page for page in pages)
        page_size = row.get("page_size", len(pages[0]))
        assert type(page_size) in (int, float) and page_size == int(page_size) and 1 <= page_size <= 32
        page_size = int(page_size)
        assert all(len(page) == page_size for page in pages[:-1]) and len(pages[-1]) <= page_size
        assert len(pages) == math.ceil(len(eligible) / page_size)
        displayed = _mutation_ids([item for page in pages for item in page], "actual ordinary Griller pages")
        assert displayed == eligible and len(displayed) == len(set(displayed)), "Actual Griller page coverage differs from eligibility"
        rolls = _mutation_ids(row["ordinary_rolls"], "actual ordinary random rolls")
        assert len(rolls) == 256 and set(rolls) <= set(eligible) and set(rolls).isdisjoint(denied)
        assert _mutation_flag(row["left_wrap"], "left page wrap") and _mutation_flag(row["right_wrap"], "right page wrap")
        if main:
            assert set(eligible) & ids["augment"], "Explicit main-pool augment setting lost its legal choices"
    assert combinations == [(30, False), (30, True), (60, False), (60, True)]
    prefix = "NTUF MUTATION POOL204 ROW "
    logged_rows = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    assert logged_rows == rows, "Mutation-page artifact differs from actual native rows"
    special = evidence["special"]
    assert isinstance(special, list) and [row["rate"] for row in special] == [30, 60]
    for row in special:
        rat_ids = _mutation_ids(row["rat_ids"], "Rat mini reward IDs")
        assert rat_ids == [registry["mini"][key] for key in ("bat ears", "lead ribs", "magnetic pulse", "toad breath")]
        assert len(row["rat_eligible"]) == 4 and all(_mutation_flag(value, "Rat eligibility") for value in row["rat_eligible"])
        for key in ("rat_natural_grants_passed", "compassion_when_full", "heavy_heart_when_ready", "disabled_normal_excluded"):
            assert _mutation_flag(row[key], key)
        for key in ("compassion_when_not_full", "heavy_heart_when_not_ready"):
            assert not _mutation_flag(row[key], key)
        station = row["idpd_station"]
        assert station["grant_name"] == "AugmentEuphoria"
        assert _mutation_ids([station["grant_id"]], "HQ grant ID") == [registry["augment"]["AugmentEuphoria"]]
        base_id = _mutation_ids([station["base_id"]], "HQ replaced base ID")[0]
        assert base_id == 12 and base_id not in set(flattened_ids)
        assert type(station["grant_count"]) in (int, float) and station["grant_count"] == 1
        assert type(station["base_count"]) in (int, float) and station["base_count"] == 0
        assert _mutation_flag(station["opened"], "HQ station opened")
        assert _mutation_flag(station["base_deactivated"], "HQ base deactivated")
        assert not _mutation_flag(station["ordinary_available"], "HQ grant ordinary eligibility")
    prefix = "NTUF MUTATION POOL204 SPECIAL "
    logged_special = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    assert logged_special == special, "Exclusive-grant artifact differs from actual native rows"
    summary = "PASS NTUF MUTATION POOL204 actual native pages,normal rolls,exclusive Rat and HQ grants30/60"
    assert smoke.splitlines().count(summary) == 1, "Native ordinary/exclusive mutation acceptance did not finish exactly once"
    return {**evidence, "artifact": name,
        "scope": "Actual native LevCont Draw GUI pages and scrDecideSkill, Rat shop reward lifecycle and HQ station grant at 30/60; no physical phone acceptance"}


def _mutation_flag(value, label):
    assert value is True or value is False or (type(value) in (int, float) and value in (0, 1)), ("Invalid native boolean", label)
    return bool(value)


def _mutation_ids(values, label):
    assert isinstance(values, list) and all(type(value) in (int, float) and math.isfinite(value)
        and value == int(value) and value > 0 for value in values), ("Invalid native mutation IDs", label)
    return [int(value) for value in values]


def _quest_integer(value, label, minimum=0):
    finite(value, label, minimum=minimum)
    assert value == int(value), ("Noninteger quest evidence", label)
    return int(value)


def _quest_deaths(rows):
    assert isinstance(rows, list) and rows, "Quest regression omitted native enemy deaths"
    identities = []
    for row in rows:
        identities.append(_quest_integer(row["id"], "native death identity", 1))
        assert isinstance(row["object"], str) and row["object"], "Quest native death object omitted"
        assert finite(row["hp"], "native death HP") <= 0, "Quest enemy was removed while alive"
        finite(row["frame"], "native death logical frame", minimum=0)
    assert len(identities) == len(set(identities)), "Quest native death identity was duplicated"


def _quest_eligible_witness(row):
    for key in ("recovery_allowed", "eligible", "player", "locked", "full_portal_blocked"):
        assert _mutation_flag(row[key], key), ("Missing eligible locked-quest witness", key)
    for key in ("check_enemies", "CrownPickup", "VaultStatue", "CrownGuardian", "TutCont",
                "RadMaggotChest", "BecomeScrapBoss", "LevCont", "GenCont", "Menu", "Cinematic",
                "GameOver", "SitDown", "special_final_area"):
        assert not _mutation_flag(row[key], key), ("Unrelated blocker masked quest portal regression", key)
    assert _quest_integer(row["active_portal_prevents"], "active unrelated portal prevents") == 0
    assert _quest_integer(row["hearts"], "live heart bullets during empty witness") == 0


def verify_quest_portal(smoke, artifacts, directory):
    """Require genuine source quest waves, empty gaps, reward and legal exits."""
    name = "frontier-quest-portal204.json"
    evidence = json_artifact(name, artifacts, directory)
    assert sha(directory / name) == artifacts[name], "Quest artifact differs from its native receipt hash"
    assert _quest_integer(evidence["schema"], "quest artifact schema", 1) == 1
    assert evidence["status"] == "PASS" and evidence["reason"] == ""
    assert evidence["physical_device_tested"] is False, "Quest regression is not physical-phone acceptance"
    assert evidence["ordinary_portals_deleted"] is False, "Quest regression removed an erroneous ordinary portal"
    assert "active_route" not in evidence, "Quest regression ended with an unfinished active route"
    for key in ("actual_native_frames", "actual_enemy_damage_and_deaths"):
        assert _mutation_flag(evidence[key], key)
    routes = evidence["routes"]
    expected = [(route, stored, seed, rate) for rate in (30, 60) for route, stored, seed in (
        ("QuestHubNatural", False, 702643), ("QuestStoredHubNatural", True, 41),
        ("QuestStoredHubAltSeedNatural", True, 702643))]
    assert isinstance(routes, list) and len(routes) == 6, "Quest regression omitted a source route or frame rate"
    assert [(row["route"], bool(_mutation_flag(row["stored"], "stored quest route")), row["seed"], row["rate"])
            for row in routes] == expected, "Quest regression route/seed/rate order changed"
    for row in routes:
        rate = row["rate"]
        assert _mutation_flag(row["completed"], "native quest route completed")
        assert row["runtime_fps"] == rate and abs(finite(row["logic_scale"], "quest logic scale") - 30 / rate) < 0.00001
        frames = _quest_integer(row["frames"], "actual quest frames", 1)
        assert finite(row["logical_ticks"], "actual quest logical ticks", minimum=1) > 0
        assert 0 < _quest_integer(row["locked_frames"], "live quest owner frames", 1) <= frames
        assert _quest_integer(row["unblocked_locked_frames"], "unguarded live quest frames") == 0
        assert row["ordinary_portals"] == [], "Ordinary clear portal interrupted the locked quest"
        assert isinstance(row["merges"], list) and len(row["merges"]) == 3
        assert all(_mutation_flag(value, "genuine quest merge") for value in row["merges"])
        _quest_deaths(row["native_deaths"])
        for key in ("actual_shots", "generated_enemies_seen", "heart_gate_intervals", "enemy_gate_intervals",
                    "eligible_empty_frames", "recovery_eligible_calls", "corpse_eligible_attempts", "corpse_rejected_attempts"):
            _quest_integer(row[key], key, 1)
        assert _quest_integer(row["hearts_seen"], "actual heart bullets") == 8
        assert finite(row["eligible_empty_ticks"], "eligible empty quest ticks", minimum=30) >= 30
        assert finite(row["final_unlock_wait_ticks"], "final unlockable wait", minimum=90) >= 90
        for key in ("eligible_empty_witness", "final_unlock_wait_witness"):
            _quest_eligible_witness(row[key])
        gaps = row["empty_gaps"]
        assert isinstance(gaps, list) and len(gaps) == 3
        assert [gap["before_merge"] for gap in gaps] == [0, 1, 2], "Quest regression omitted a between-wave merge gap"
        for index, gap in enumerate(gaps):
            finite(gap["ticks"], "eligible between-wave ticks", minimum=30)
            deaths = _quest_integer(gap["native_deaths_before"], "deaths before next merge", 0 if index == 0 else 1)
            assert deaths <= len(row["native_deaths"])
            assert _quest_integer(gap["hearts_seen"], "hearts before next merge") <= 8
            finite(gap["frame"], "next merge logical frame", minimum=0)
        alarms = row["corpse_alarms"]
        assert isinstance(alarms, list) and alarms, "Quest regression omitted the real corpse-alarm rejection path"
        counts = {kind: 0 for kind in ("before", "rejected")}
        for alarm in alarms:
            assert alarm["kind"] in counts, "A corpse alarm passed while the locked quest was live"
            counts[alarm["kind"]] += 1
            _quest_integer(alarm["corpse"], "native corpse identity", 1)
            finite(alarm["frame"], "native corpse-alarm logical frame", minimum=0)
            assert not _mutation_flag(alarm["forceportal"], "ordinary corpse alarm was forced")
            assert _quest_integer(alarm["native_deaths_before"], "deaths at corpse alarm") <= len(row["native_deaths"])
            _quest_eligible_witness(alarm["eligibility"])
        assert counts == {"before": row["corpse_eligible_attempts"], "rejected": row["corpse_rejected_attempts"]}
        assert _mutation_flag(row["owner_release_seen"], "quest owner released")
        release = row["owner_release"]
        assert not _mutation_flag(release["locked_exists"], "locked owner after genuine unlock")
        assert _mutation_flag(release["reward_exists"], "genuine reward chest exists")
        assert not _mutation_flag(release["full_portal_blocked"], "quest guard released after unlock")
        _quest_integer(release["remaining_floor_controllers"], "retained quest floor controllers", 1)
        finite(release["frame"], "quest owner-release logical frame", minimum=0)
        assert _mutation_flag(row["reward_opened"], "genuine ultimate reward opened")
        assert _mutation_flag(row["crown_created"], "legal crown fixture created")
        crown = row["legal_crown_portal"]
        assert _mutation_flag(crown["native_collision"], "genuine CrownPickup collision")
        assert crown["type"] == 3, "Quest guard changed the explicit native crown exit"
        _quest_integer(crown["id"], "genuine crown portal identity", 1)
        finite(crown["frame"], "genuine crown collision logical frame", minimum=0)
    controls = evidence["controls"]
    kinds = ["FloorCont-only", "CrownPed-only", "HugeQuestChest-before-open", "ordinary-HeartBullet",
             "HugeQuestChest-after-open", "normal-combat-release"]
    assert isinstance(controls, list) and [row["kind"] for row in controls] == kinds, "Quest owner-negative controls omitted"
    for index, row in enumerate(controls):
        assert not _mutation_flag(row["full_portal_blocked"], "unrelated object blocked ordinary exit")
        if index < 4:
            _quest_integer(row["actor"], "live owner-negative control actor", 1)
            assert _mutation_flag(row["live_actor"], "owner-negative control actor exists")
        if index < 5:
            assert not _mutation_flag(row["locked_exists"], "owner-negative control has locked quest chest")
    assert _mutation_flag(controls[4]["genuine_contact"], "ultimate reward negative-control contact")
    ordinary = controls[5]
    _quest_deaths(ordinary["native_deaths"])
    assert len(ordinary["native_deaths"]) == _quest_integer(ordinary["actual_shots"], "ordinary actual shot", 1) == 1
    for key in ("enemy_id", "corpse_attempts", "corpse_passes"):
        _quest_integer(ordinary[key], key, 1)
    assert ordinary["native_deaths"][0]["id"] == ordinary["enemy_id"]
    assert ordinary["portal_type"] == 1, "Quest guard suppressed the ordinary post-combat exit"
    summary_prefix = "FR_QUEST_PORTAL204 "
    summaries = [json.loads(line[len(summary_prefix):]) for line in smoke.splitlines()
                 if line.startswith(summary_prefix + "{")]
    assert len(summaries) == 7 and [row["status"] for row in summaries] == ["IN_PROGRESS"] * 6 + ["PASS"], \
        "Quest regression requires six ordered diagnostics and exactly one final PASS"
    assert summaries[-1] == evidence, "Quest artifact differs from its actual final native summary"
    for index, snapshot in enumerate(summaries[:-1]):
        expected_active = {**routes[index], "completed": False}
        expected_snapshot = {**evidence, "status": "IN_PROGRESS",
            "reason": "native route reached final acceptance assertions",
            "routes": routes[:index], "controls": [], "active_route": expected_active}
        assert snapshot == expected_snapshot, ("Quest pre-assertion diagnostic differs from its actual completed route", index)
    logged_routes = [json.loads(line[len("FR_QUEST_PORTAL204 ROUTE PASS "):]) for line in smoke.splitlines()
                     if line.startswith("FR_QUEST_PORTAL204 ROUTE PASS ")]
    assert logged_routes == routes, "Quest route artifact differs from actual native route completion"
    events = []
    for line in smoke.splitlines():
        if line.startswith(summary_prefix + "{"):
            events.append(json.loads(line[len(summary_prefix):])["status"])
        elif line.startswith("FR_QUEST_PORTAL204 ROUTE PASS "):
            events.append("ROUTE PASS")
    assert events == [event for _ in routes for event in ("IN_PROGRESS", "ROUTE PASS")] + ["PASS"], \
        "Quest diagnostics were detached from their genuine route completion boundaries"
    return {**evidence, "artifact": name,
            "scope": "Six genuine native Ultimate Quest source routes at actual 30/60 Hz, damage/deaths, three eligible merge gaps, delayed final UNLOCK, owner release, genuine crown exit and ordinary combat controls; no physical-phone acceptance"}


def verify204_identity(case, smoke, artifacts, directory):
    if case == "FrontierQuestPortal204Tests":
        return verify_quest_portal(smoke, artifacts, directory)
    if case == "FrontierBossArt204Tests":
        return verify_boss_art(smoke, artifacts, directory)
    if case == "FrontierLoadoutArt204Tests":
        return verify_loadout_art(smoke, artifacts, directory)
    if case == "FrontierMutationPool204Tests":
        return verify_mutation_pool(smoke, artifacts, directory)
    if case == "FrontierRedConnectivity204Tests":
        return verify_red_connectivity(smoke, artifacts, directory)
    return _base_verify204_identity(case, smoke, artifacts, directory)


def verify_red_connectivity(smoke, artifacts, directory):
    """Accept generated seam contacts and complete native-mask round trips."""
    name = "frontier-red-regression204.json"
    evidence = json_artifact(name, artifacts, directory)
    assert evidence["status"] == "PASS" and evidence["rates"] == [30, 60]
    assert evidence["physical_device_tested"] is False, "Red regression is not physical-device acceptance"
    for key in ("actual_gencont", "actual_player_mask", "actual_player_collision_event", "actual_helper_endstep",
                "manual_collision_dispatch", "manual_pixel_integration"):
        assert _mutation_flag(evidence[key], key)

    queries = evidence["queries"]
    assert isinstance(queries, list) and len(queries) == 3
    for row, obj, expected in zip(queries, ("NTTEFullWallFake", "Wall", "NTTESolidWall"), (False, True, True)):
        assert row["object"] == obj and not _mutation_flag(row["solid"], "query solid")
        assert _mutation_flag(row["native_meeting"], "native Wall-family query")
        assert _mutation_flag(row["actual"], "filtered Wall-family query") is expected
        assert _mutation_flag(row["expected"], "query expected") is expected
        assert _mutation_flag(row["fake_family"], "query Fake family") is (not expected)

    seams = evidence["seams"]
    assert isinstance(seams, list) and [row["rate"] for row in seams] == [30, 60]
    for row in seams:
        for key in ("actual_player_collision_event", "actual_native_floor_and_wall_create",
                    "actual_wall_fake_create_and_helper", "manual_collision_dispatch"):
            assert _mutation_flag(row[key], key)
        assert row["physical_device_tested"] is False
        _red_seam_preconditions(row["preconditions"])
        _red_seam_response(row["ordinary"], "fake-and-helper-open", row["contact"])
        _red_seam_response(row["fake_open"], "fake-open", row["contact"])
        _red_seam_response(row["authored"], "authored", row["contact"])
        _red_point(row["start"])
        assert _red_distance(row["start"], row["contact"]) > 0.01
        _red_same_response(row["authored"], row["fake_open"])
        assert _red_distance(row["fake_only"], row["contact"]) < 0.01, "Direct Fake collision blocked the player"
        distance = _red_number(row["authored_vs_fake_open_distance"])
        assert 0 <= distance < 0.01
        assert abs(distance - _red_distance(row["authored"]["position"], row["fake_open"]["position"])) < 0.001
        assert _mutation_flag(row["ordinary_contact_resolved"], "ordinary-only resolved")

    worlds = evidence["worlds"]
    assert isinstance(worlds, list) and len(worlds) == 6
    assert [(row["seed"], row["rate"]) for row in worlds] == [(seed, rate) for seed in (1, 2, 3) for rate in (30, 60)]
    for row in worlds:
        assert row["generation_rate"] == 30
        for key in ("actual_gencont", "actual_player_collision_event", "actual_helper_endstep"):
            assert _mutation_flag(row[key], key)
        seam = row["seam"]
        assert _mutation_flag(seam["candidate"], "generated natural seam found")
        fixture = seam["fixture"]
        assert not _mutation_flag(fixture["invalid"], "generated seam fixture invalid")
        assert fixture["physical_device_tested"] is False
        for key in ("actual_collision_event", "manual_collision_dispatch"):
            assert _mutation_flag(fixture[key], key)
        _red_seam_preconditions(fixture["preconditions"])
        for key in ("start", "contact", "fake", "wall"):
            _red_point(fixture[key])
        assert _red_distance(fixture["start"], fixture["contact"]) > 0.01
        controls = fixture["controls"]
        assert isinstance(controls, list) and len(controls) == 2
        for control, mode in zip(controls, ("fake-and-helper-open", "fake-open")):
            _red_seam_response(control, mode, fixture["contact"])
        _red_seam_response(fixture["authored"], "authored", fixture["contact"])
        _red_same_response(fixture["authored"], controls[1])
        _red_boundaries(row["boundaries"])
    for index in range(0, len(worlds), 2):
        assert worlds[index]["boundaries"] == worlds[index + 1]["boundaries"], "30/60 seam tests regenerated different witness roads"

    walks = evidence["walks"]
    assert isinstance(walks, list) and len(walks) >= 4 and len(walks) % 2 == 0
    count = _red_integer(walks[0]["target_count"], minimum=2)
    assert len(walks) == count * 2, "Native red walk target coverage is incomplete"
    assert [(row["rate"], row["target_index"]) for row in walks] == [(rate, index) for rate in (30, 60) for index in range(count)]
    targets = []
    final = None
    nodes = _red_integer(walks[0]["nodes"], minimum=1)
    for index, row in enumerate(walks):
        assert row["seed"] == 91 and row["generation_rate"] == 30 and row["target_count"] == count
        assert row["components"] == 1 and _red_integer(row["nodes"], minimum=1) == nodes
        assert _mutation_flag(row["actual_gencont"], "walk native generation")
        assert _mutation_flag(row["pixel_swept_edges"], "actual Player pixel-swept edges")
        target = row["target"]
        assert target["kind"] == ("twins" if row["target_index"] == count - 1 else "warp")
        _red_point([target["x"], target["y"]])
        if index < count:
            targets.append(target)
        else:
            assert target == targets[index - count], "30/60 walks did not cover the same native targets"
        walk = row["walk"]
        _red_integer(walk["steps"], minimum=1)
        for key in ("reached", "returned", "actual_wall_collision_events", "actual_helper_endstep", "manual_pixel_integration"):
            assert _mutation_flag(walk[key], key)
        assert walk["blocked"] == [], "Actual red collision blocked a round trip"
        for key in ("closed_overlapping_after_endstep", "orphan_helpers_after_endstep", "open_helpers_after_return", "reveal_after_return"):
            assert _red_number(walk[key]) == 0, ("Red helper lifecycle did not restore", key)
        fake_events = _red_integer(walk["fake_collision_events"], minimum=0)
        reveal = _red_number(walk["peak_reveal"])
        assert 0 <= reveal <= 1
        if target["kind"] == "twins":
            assert fake_events > 0 and reveal > 0, "Hidden-room walk skipped Fake collision and reveal"
        _red_point(walk["final"])
        if final is None:
            final = walk["final"]
        assert _red_distance(final, walk["final"]) < 0.01, "Round trips returned to different spawn positions"
        _red_helpers(row["helpers_after_walk"], required=True)
    assert len({(target["kind"], target["x"], target["y"]) for target in targets}) == count, "Duplicated native walk target"

    for prefix, expected in (("NTUF RED QUERY204 ROW ", [queries]), ("NTUF RED SEAM204 ROW ", seams),
                             ("NTUF RED REGRESSION204 WORLD ", worlds), ("NTUF RED REGRESSION204 WALK ", walks)):
        actual = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
        assert actual == expected, ("Red artifact differs from actual native rows", prefix)
    finish = "NTUF RED REGRESSION204 PASS generated seams, ordinary Warp paths and hidden-room round trips"
    assert smoke.splitlines().count(finish) == 1, "Native red regression did not finish exactly once"
    return {**evidence, "artifact": name,
        "scope": "Actual native GenCont seams at seeds1/2/3 and 30/60 collision; complete seed91 Warp and hidden Twins round trips with pixel-swept Player mask and real helper EndStep; manual dispatch/integration, no physical phone acceptance"}


def _red_number(value):
    assert type(value) in (int, float) and math.isfinite(value), "Invalid native red numeric value"
    return value


def _red_integer(value, minimum=0):
    value = _red_number(value)
    assert value == int(value) and value >= minimum, "Invalid native red counter"
    return int(value)


def _red_point(value):
    assert isinstance(value, list) and len(value) == 2, "Invalid native red point"
    return [_red_number(item) for item in value]


def _red_distance(first, second):
    first, second = _red_point(first), _red_point(second)
    return math.hypot(first[0] - second[0], first[1] - second[1])


def _red_seam_preconditions(row):
    for key in ("start_helper_overlap", "start_ordinary_wall_overlap"):
        assert not _mutation_flag(row[key], key), "Red seam started inside an already-opened route"
    for key in ("contact_real_wall", "contact_fake_wall", "fake_native_mask", "helper_exists", "helper_closed"):
        assert _mutation_flag(row[key], key), ("Red seam precondition absent", key)
    assert row["wall_object"] == "Wall"
    _red_integer(row["wall_id"], minimum=1)
    bbox = row["wall_bbox"]
    assert isinstance(bbox, list) and len(bbox) == 4
    for item in bbox:
        _red_number(item)
    assert bbox[0] < bbox[2] and bbox[1] < bbox[3]


def _red_seam_response(row, mode, contact):
    assert row["mode"] == mode
    _red_point(row["position"])
    _red_point(row["motion"])
    assert _mutation_flag(row["wall_survived"], "ordinary wall survived"), "Red seam destroyed the ordinary wall"
    assert _mutation_flag(row["ordinary_contact_resolved"], "ordinary wall contact resolved"), "Red seam remained in ordinary wall"
    assert _red_distance(row["position"], contact) > 0.01, "Red seam never resolved the actual ordinary contact"


def _red_same_response(authored, fake_open):
    assert _red_distance(authored["position"], fake_open["position"]) < 0.01, "Red response still includes Fake masks"
    assert _red_distance(authored["motion"], fake_open["motion"]) < 0.01, "Red motion still includes Fake masks"


def _red_helpers(rows, required=False):
    assert isinstance(rows, list) and (rows or not required), "Red helper restoration evidence omitted"
    ids, creators = [], []
    for row in rows:
        ids.append(_red_integer(row["id"], minimum=1))
        creators.append(_red_integer(row["creator"], minimum=1))
        assert _mutation_flag(row["creator_exists"], "helper creator exists")
        assert _mutation_flag(row["solid"], "helper restored solid")
        assert row["creator_mask"] == "mskWall", "Red Fake mask was not restored"
        assert not _mutation_flag(row["normal_floor_overlap"], "helper normal-floor overlap")
        _red_point([row["x"], row["y"]])
        bbox = row["bbox"]
        assert isinstance(bbox, list) and len(bbox) == 4
        for item in bbox:
            _red_number(item)
        assert bbox[0] < bbox[2] and bbox[1] < bbox[3]
        assert isinstance(row["floor_styles"], list)
        for style in row["floor_styles"]:
            _red_integer(style)
    assert len(ids) == len(set(ids)) and len(creators) == len(set(creators)), "Duplicate red helper or creator evidence"


def _red_boundaries(rows):
    assert isinstance(rows, list) and [row["phase"] for row in rows] == ["secret-before", "corridor-after", "quest-after"]
    protected = _red_integer(rows[0]["protected_points"], minimum=1)
    styles = rows[0]["protected_styles"]
    assert isinstance(styles, list) and len(styles) == 2
    assert sum(_red_integer(style, minimum=1) for style in styles) == protected, "Ordinary or Warp-road style coverage omitted"
    for row in rows:
        assert row["protected_points"] == protected and row["protected_styles"] == styles
        assert row["changed"] == [], "Hidden corridor construction occupied an existing road"
        assert _red_number(row["fake_overlap"]) == 0 and _red_number(row["helper_overlap"]) == 0
        _red_helpers(row["helpers"], required=row["phase"] != "secret-before")



def _art_rows(smoke, prefix):
    return [json.loads(line.split(prefix, 1)[1]) for line in smoke.splitlines() if prefix in line]


def _art_positive(value, minimum, label):
    assert type(value) in (int, float) and math.isfinite(value) and value > minimum, label
    return value


def verify_loadout_art(smoke, artifacts, directory):
    """Require native menu consumer GPU pixels through init, refresh and rebuild."""
    name = "frontier-loadout-art204.json"
    evidence = json_artifact(name, artifacts, directory)
    assert evidence["status"] == "PASS"
    for key in ("refresh_and_native_rebuild_verified", "all_declared_callbacks_checked"):
        assert _mutation_flag(evidence[key], key)
    assert evidence["control_coverage"] == evidence["control_ink"] == 256
    assert evidence["empty_coverage"] == 0, "Loadout GPU transparent control failed"
    phases = evidence["phases"]
    assert isinstance(phases, list) and [row["phase"] for row in phases] == [0, 1, 2]
    for phase in phases:
        assert phase["declared"] == 2 and phase["absent_callbacks"] == 75 and phase["checked_weapons"] == 77
        assert _mutation_flag(phase["all_gameplay_sprites_unchanged"], "gameplay sprite stability")
        assert _mutation_flag(phase["ordinary_fallback_pixels_verified"], "ordinary no-art fallback")
        _art_positive(phase["ordinary_fallback_coverage"], 5, "Ordinary loadout fallback is empty")
    rows = evidence["rows"]
    assert isinstance(rows, list) and len(rows) == 6
    expected = {"weapon:FR_BubblesCutlass": (187, "sprFR_sprBubblesCutlassLoadout_a3f9cae1b4d8"),
                "weapon:FR_BubblesShovel": (188, "sprFR_sprBubblesShovelLoadout_b0d98bdf1533")}
    identities = []
    for row in rows:
        assert row["phase"] in (0, 1, 2) and row["key"] in expected
        assert (row["weapon"], row["portrait"]) == expected[row["key"]], "Authored loadout identity changed"
        identities.append((row["phase"], row["key"]))
        _art_positive(row["coverage"], 20, "Authored menu portrait is empty")
        _art_positive(row["ink"], 10, "Authored menu portrait has no visible detail")
        assert _mutation_flag(row["exact_authored_pixels"], "exact authored consumer pixels")
        assert _mutation_flag(row["gameplay_fallback_rejected"], "gameplay fallback negative control")
    assert set(identities) == {(phase, key) for phase in (0, 1, 2) for key in expected} and len(set(identities)) == 6
    assert _art_rows(smoke, "LOADOUT ART204 ") == phases, "Missing actual loadout rebuild phase logs"
    done = "PASS FRONTIER authored loadout portraits: all source callbacks, genuine native consumer GPU pixels, refresh/rebuild and no-art fallback"
    assert smoke.count(done) == 1, "Missing or duplicated native loadout completion"
    for weapon in (187, 188):
        capture = f"frontier-loadout-art204-{weapon}.png"
        assert capture in artifacts and (directory / capture).is_file(), "Missing genuine loadout consumer capture"
        assert sha(directory / capture) == artifacts[capture], "Loadout consumer capture changed"
    return {**evidence, "artifact": name,
        "scope": "Actual desktop native selection consumer GPU pixels and metadata init/refresh/rebuild; no physical phone acceptance"}


def verify_boss_art(smoke, artifacts, directory):
    """Require every authored boss triplet through native apply and restore."""
    name = "frontier-boss-art204.json"
    evidence = json_artifact(name, artifacts, directory)
    assert evidence["status"] == "PASS" and evidence["physical_device_tested"] is False
    assert evidence["resource_count"] == 15 and evidence["alias_count"] == 30
    assert evidence["control_coverage"] == evidence["control_ink"] == 1024 and evidence["empty_coverage"] == 0
    assert _mutation_flag(evidence["missing_alias_rejected"], "missing boss-art alias negative control")
    for key in ("native_name_path_unchanged", "disabled_intro_guard_preserved", "destroyed_owner_rejected",
                "ordinary_intro_replacement_isolated", "ntte_intro_replacement_isolated", "destroyed_owner_pixels_restored"):
        assert _mutation_flag(evidence[key], key)
    guards = evidence["rejected_start_guards"]
    assert isinstance(guards, list) and [row["kind"] for row in guards] == ["disabled", "coop", "no-player"], "Missing rejected native intro start coverage"
    for row in guards:
        for key in ("refused", "ntte_key_preserved", "state_preserved", "artwork_preserved",
                    "actual_source_callback_rejected", "rejected_source_cleanup_preserved"):
            assert _mutation_flag(row[key], key)
    manifest = read(ROOT / "generated-assets/boss-art204/manifest.json")
    proof = read(ROOT / "generated-assets/boss-art204/verification.json")
    assert manifest["schema"] == "frontier-boss-art204-v1"
    assert manifest["resource_count"] == proof["resource_count"] == 15
    assert manifest["alias_count"] == proof["alias_count"] == 30
    assert proof["status"] == "PASS" and proof["native_execution_performed"] is False and proof["physical_device_tested"] is False
    for key in ("original_inventory_verified", "rgba_preserved", "target_origins_preserved"):
        assert _mutation_flag(proof[key], key)
    assert manifest["base_manifest_sha256"] == sha(ROOT / "generated-assets/manifest.json")
    bosses = {"CoveHyperCrystal", "GraveyardBoss", "LightningHyperCrystal", "OurpleCursedHyperCrystal", "RoboBoss"}
    targets = {"Main": "sprBossIntro", "Back": "sprBossIntroBackLayer", "Name": "sprBossName"}
    expected = {(boss, role) for boss in bosses for role in targets}
    interruptions = evidence["interrupted_intro_restoration"]
    assert isinstance(interruptions, list) and [row["kind"] for row in interruptions] == ["ordinary", "ntte"], "Missing dirty-owner replacement route coverage"
    for row in interruptions:
        for key in ("actual_source_callback", "owner_destroyed", "name_path_preserved", "all_native_pixels_restored",
                    "restored_before_active_query"):
            assert _mutation_flag(row[key], key)
        for family, flags in (("dirty_layers", ("authored_pixels_match", "changed_from_native")),
                              ("restored_layers", ("restored_pixels_match", "restored_origin_match"))):
            layers = row[family]
            assert isinstance(layers, list) and [layer["role"] for layer in layers] == list(targets), "Interrupted intro omitted a native layer"
            for layer in layers:
                assert layer["target"] == targets[layer["role"]], "Interrupted intro used the wrong native target"
                for key in flags:
                    assert _mutation_flag(layer[key], key)
    for route in ("ordinary", "ntte", "destroyed-owner"):
        for role in targets:
            capture = f"frontier-boss-art204-interrupted-{route}-{role.lower()}.png"
            assert capture in artifacts and (directory / capture).is_file(), "Missing interrupted intro native-layer capture"
            assert sha(directory / capture) == artifacts[capture], "Interrupted intro native-layer capture changed"
    # Independent counts from the frozen author PNGs; the Name layers are
    # deliberately white-only, so their visible palette contains one colour.
    palette = {"CoveHyperCrystal": (8, 6, 1), "GraveyardBoss": (0, 6, 1),
        "LightningHyperCrystal": (8, 6, 1), "OurpleCursedHyperCrystal": (8, 6, 1), "RoboBoss": (3, 11, 1)}
    ink = {"CoveHyperCrystal": (26139, 3538, 3492), "GraveyardBoss": (0, 23032, 3492),
        "LightningHyperCrystal": (27037, 3538, 3492), "OurpleCursedHyperCrystal": (26139, 3538, 3492),
        "RoboBoss": (12106, 45215, 4180)}
    source_rows = manifest["assets"]
    assert isinstance(source_rows, list) and len(source_rows) == 15
    source = {(row["boss"], row["role"]): row for row in source_rows}
    assert set(source) == expected and len(source) == len(source_rows)
    for (boss, role), row in source.items():
        path = f"Sprites/Menu/Intros/spr{boss}{role}.png"
        assert row["path"] == path and row["aliases"] == [path.lower(), "../" + path.lower()]
        assert row["target"] == targets[role] and row["frames"] == 1
        assert re.fullmatch(r"[0-9a-f]{64}", row["source_sha256"]) and re.fullmatch(r"[0-9a-f]{64}", row["rgba_sha256"])
        _art_positive(row["source_bytes"], 0, "Boss authored source omitted")
        transparent = boss == "GraveyardBoss" and role == "Main"
        assert _mutation_flag(row["authored_transparent"], "manifest authored transparency") == transparent, "Unexpected authored transparent boss artwork"
        if transparent:
            assert row["alpha_coverage"] == 0 and (row["width"], row["height"]) == (481, 240)
        else:
            _art_positive(row["alpha_coverage"], 0, "Visible authored boss art omitted")
    rows = evidence["resources"]
    assert isinstance(rows, list) and len(rows) == 15
    observed = []
    for row in rows:
        identity = (row["boss"], row["role"])
        assert identity in expected
        observed.append(identity)
        original = source[identity]
        assert row["path"] == original["path"].lower()
        assert row["resource"] == original["resource"] and row["target"] == original["target"]
        assert (row["width"], row["height"]) == (original["width"], original["height"])
        assert [row["origin_x"], row["origin_y"]] == original["origin"]
        transparent = identity == ("GraveyardBoss", "Main")
        assert _mutation_flag(row["authored_transparent"], "authored transparent placeholder") == transparent
        assert row["expected_source_coverage"] == original["alpha_coverage"]
        assert row["source_coverage"] == row["expected_source_coverage"], "Authored boss source pixel coverage changed"
        role_index = ("Main", "Back", "Name").index(row["role"])
        assert row["expected_source_colours"] == row["source_colours"] == palette[row["boss"]][role_index], "Authored boss source palette changed"
        assert row["expected_source_ink"] == row["source_ink"] == ink[row["boss"]][role_index], "Authored boss source visible ink changed"
        assert _mutation_flag(row["source_nonempty"], "authored source visibility") == (not transparent)
        if transparent:
            assert row["source_coverage"] == row["source_ink"] == row["source_colours"] == 0
        else:
            _art_positive(row["source_coverage"], 0, "Boss authored art is transparent")
            _art_positive(row["source_ink"], 0, "Boss authored art has no visible detail")
            _art_positive(row["source_colours"], 0, "Boss authored art lacks source colours")
        for key in ("aliases_resolve", "replacement_pixels_match", "replacement_origin_match",
                    "restored_pixels_match", "restored_origin_match"):
            assert _mutation_flag(row[key], key)
    assert set(observed) == expected and len(set(observed)) == len(rows), "Boss triplet coverage is incomplete"
    for boss in bosses:
        assert sum(row["source_coverage"] for row in rows if row["boss"] == boss) > 0, "Boss triplet is entirely transparent"
    intros = evidence["intros"]
    assert isinstance(intros, list) and len(intros) == 5 and {row["boss"] for row in intros} == bosses
    for row in intros:
        for key in ("enabled", "actual_source_callback", "artwork_applied", "artwork_restored", "state_preserved",
                    "native_intro_started", "artwork_retained_while_active", "native_intro_closed",
                    "frontend_name_png_selected", "actual_native_draw_visible", "actual_pause_barrier",
                    "owner_inactive_at_barrier", "owner_remained_inactive", "pause_artwork_retained"):
            assert _mutation_flag(row[key], key)
        _red_integer(row["native_draw_changed_pixels"], minimum=101)
        capture = f"frontier-boss-art204-{row['boss'].lower()}-native-intro.png"
        assert capture in artifacts and (directory / capture).is_file(), "Missing real native intro Draw capture"
        assert sha(directory / capture) == artifacts[capture], "Native intro Draw capture changed"
    assert _art_rows(smoke, "FR_BOSS_ART204 ") == [evidence], "Missing exact native boss-art resource/callback log"
    done = "PASS FRONTIER boss art204: all15 authored resources,30 aliases,5 enabled actual source intros, GPU pixels/origins and restoration"
    assert smoke.count(done) == 1, "Missing or duplicated native boss-art completion"
    for boss, role in expected:
        capture = f"frontier-boss-art204-{boss.lower()}-{role.lower()}.png"
        assert capture in artifacts and (directory / capture).is_file(), "Missing genuine boss-art consumer capture"
        assert sha(directory / capture) == artifacts[capture], "Boss-art consumer capture changed"
    return {**evidence, "artifact": name,
        "scope": "Actual desktop native authored boss triplets, enabled source callbacks, visible native Draw through the actual pause barrier, inactive-owner artwork retention, Alarm2 cleanup, refused callback/cleanup guards and dirty destroyed-owner three-layer restoration for ordinary/NTTE consumers; no physical phone acceptance"}

if __name__ == "__main__":
    main()
