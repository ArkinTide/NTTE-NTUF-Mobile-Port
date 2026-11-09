"""Read-only 2.0.5/internal103 same-VM review; no build or publication.

Retain the frozen build102 semantic reviewers and all72 historical cases,
then require all10 current cases on the same new VM/input. A diagnostic-only
Pirate observation cannot satisfy a repair acceptance claim.
"""
from pathlib import Path as _Path
import hashlib as _hashlib

_FROZEN_REVIEW = _Path(__file__).with_name("verify_204r2_repairs.py")
_FROZEN_REVIEW_SHA256 = "6cca1cef0fbfc5cbaba7f79891f324b6cfbbb4a46dcdeddcf318f24774ec9fd9"
_raw205 = _FROZEN_REVIEW.read_bytes()
assert _hashlib.sha256(_raw205).hexdigest() == _FROZEN_REVIEW_SHA256, "Frozen build102 reviewer changed"
_entry205 = '\nif __name__ == "__main__":\n    main()\n'
_source205 = _raw205.decode("utf-8-sig")
assert _source205.count(_entry205) == 1
exec(compile(_source205.replace(_entry205, "\n"), str(_FROZEN_REVIEW), "exec"), globals())
_retained205_identity = verify204_identity
_retained205_current = CURRENT204_CASES
_retained205_required = REQUIRED204_CASES
_retained205_tests = REVIEW_TESTS
_retained205_inputs = REVIEW_INPUTS

# The build102 wrapper exposes the hash-bound effective original reviewer.
# Rebind its orchestration to this release while retaining all binary/source,
# receipt/artifact, native-case identity and immutable-evidence checks.
_changes205 = (
    ('review/release204r2-cases.json', 'review/release205-cases.json'),
    ('selection["version"] == "2.0.4"', 'selection["version"] == "2.0.5"'),
    ('selection["internal"] == 102', 'selection["internal"] == 103'),
    ('evidence.get("version") == "2.0.4"', 'evidence.get("version") == "2.0.5"'),
    ('evidence["internal"] == 102', 'evidence["internal"] == 103'),
    ('mobile-release204-20261108/staged-source-manifest.json', 'mobile-release204r2-20261108/staged-source-manifest.json'),
    ('60a31c739c5fc52b3a953f3d5c549dcd7ba760de4d08615b91517ecae77f6b85', 'f99a88460173ec3a73a70d56a198f32d13386fc58fdd50d794dee64ffbd04737'),
    ('da2a770b768d84227bf415bc7b458b056612317b2ebf09820826b7889b9860b6', '369cc798ca60c93e0b09fb0f8f4938bc23f8a70a5d8eb22e0d386477bdc0f36e'),
    ('b8bc9c5d34f76840e0a849c072d01ea5c7f0d87759ab69688f70636335a0f2ad', '7c77b58dee311823f45aa6f16e310d0e63900f492a178f95ab533522136c769a'),
    ('#macro GAME_VERSION "2.0.4"', '#macro GAME_VERSION "2.0.5"'),
    ('NTTE_RELEASE_NUMBER\\s+102', 'NTTE_RELEASE_NUMBER\\s+103'),
    ('#macro NTTE_RELEASE_VERSION "2.0.4"', '#macro NTTE_RELEASE_VERSION "2.0.5"'),
    ('#macro NTTE_RELEASE_TAG "2.0.4"', '#macro NTTE_RELEASE_TAG "2.0.5"'),
    ('github-publish/release-2.0.4/publication-receipt.json', 'github-publish/release-2.0.4-r2/publication-receipt.json'),
    ('92c226fd1896472e2f8371ee2cd129ec63432b20b20a4ad68ce5cb0040ba6265', 'd0c63a24375a4fabc17077a7e74de4004caac43998430d18a252b2be997b85c5'),
    ('mobile-release204-20261108/deliverables/NuclearThrone.NTTE-NTUF-iOS-2.0.4.ipa', 'mobile-release204r2-20261108/deliverables/NuclearThrone.NTTE-NTUF-iOS-2.0.4-build102.ipa'),
    ('778a32cc4ee2aca2f06b3697a53966b8c1f5134b3f9876d891ba7f58d4fbbb32', '834f141f7bf926b0d28aeea29ab98c46fb570e8066ceeb246965dc888b1bd05b'),
    ('mobile-release204-20261108/deliverables/NuclearThrone.NTTE-NTUF-Android-2.0.4.apk', 'mobile-release204r2-20261108/deliverables/NuclearThrone.NTTE-NTUF-Android-2.0.4-build102.apk'),
    ('900745f4af346c585862d74a844573227386f1092087ef717e523e89f1df4ece', '75e65bc4400a15b9d7aa6a5920a9a14071b17e5ba60d64df738df8f2b810687d'),
    ('"version": "2.0.4", "internal": 102', '"version": "2.0.5", "internal": 103'),
    ('post204r2-development-review-', 'post205-development-review-'),
    ('both explicit reviewer test modules', 'all four explicit reviewer test modules'),
    ('CURRENT204_CASES', 'CURRENT205_CASES'),
    ('REQUIRED204_CASES', 'REQUIRED205_CASES'),
    ('current204', 'current205'),
)
for _old205, _new205 in _changes205:
    assert _text.count(_old205) >= 1, ("Frozen build102 review anchor changed", _old205)
    _text = _text.replace(_old205, _new205)
exec(compile(_text, str(_FROZEN_REVIEW), "exec"), globals())

NEW205_CASES = (
    "FrontierContinueAudio205Tests", "FrontierBubblesAttack205Tests", "FrontierVisual205Tests",
    "FrontierWallSurface205Tests", "FrontierQuestVault205Tests", "FrontierQuestContinue205Tests",
    "FrontierLairReturn205Tests", "FrontierLairReturnLinger205Tests", "FrontierPirateVisibility205Tests",
    "FrontierBloodlust205Tests",
)
CURRENT205_CASES = _retained205_current | set(NEW205_CASES)
REQUIRED205_CASES = frozenset(read(ROOT / "review/release204r2-cases.json")["cases"]) | set(NEW205_CASES)
REVIEW_TESTS = (*_retained205_tests, "review/test_review205.py")
REVIEW_INPUTS = (*_retained205_inputs, "review/verify_205_repairs.py", "review/capture205_python.py",
    "review/test_review205.py", "review/release205-cases.json", "review/release205-user-requirements.json",
    "review/inspect_release205_packages.py", "review/verify_release205_debug_font.py")


def load_cases():
    selection = read(CASE_SELECTION)
    prior_path = ROOT / "review/release204r2-cases.json"
    assert sha(prior_path) == "a62c40540b4924d96c94509b403799cf9fb702b90d02486723c9f7a6450fd857", "Frozen build102 selection changed"
    prior = read(prior_path)
    assert prior["version"] == "2.0.4" and prior["internal"] == 102 and len(prior["cases"]) == 72
    expected = [*NEW205_CASES, *prior["cases"]]
    assert selection["version"] == "2.0.5" and selection["internal"] == 103, "Wrong205 release case selection"
    assert selection["cases"] == expected and len(expected) == len(set(expected)) == 82, "All82 exact ordered current-VM cases are mandatory"
    assert set(expected) == REQUIRED205_CASES
    return tuple(expected)


FINAL_CASES = load_cases()


def _one_summary(smoke, summary):
    assert smoke.splitlines().count(summary) == 1, ("Native205 assertions did not complete exactly once", summary)
    return summary


def _artifact205(name, artifacts, directory):
    evidence = json_artifact(name, artifacts, directory)
    assert sha(directory / name) == artifacts[name], ("Native205 artifact changed", name)
    assert evidence.get("physical_device_tested") is False, "Native desktop evidence cannot claim phone validation"
    return evidence


def verify_audio205(smoke):
    for summary in (
        "NTUF AUDIO205 source loop + normal Destroy + Cleanup-only + reused sample + preview PASS",
        "PASS NTUF AUDIO205 actual source Bulwark voices, normal Destroy, Cleanup-only, reused sample, native preview/full loader + room_restart + async terrain",
    ):
        _one_summary(smoke, summary)
    return {"actual_native_checkpoint_loader": True, "source_voice_ownership_and_cleanup_asserted": True,
        "unrelated_voice_positive_control": True, "physical_device_tested": False,
        "scope": "Real source voice, ordinary Destroy, Cleanup-only, replaced voice, native preview/full Continue and asynchronous regeneration; no listening test or physical phone claim"}


def verify_bubbles205(smoke):
    prefix = "NTUF BUBBLES205 "
    rows = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    assert len(rows) == 2 and [row["rate"] for row in rows] == [30, 60]
    expected = {"rate", "actual_general", "controller_named_buttons", "touch_joystick_and_ability",
        "idle_no_spray", "release_stops", "weapon_excluded", "mode_off_fires", "preference_off_original_controls"}
    for row in rows:
        assert set(row) == expected
        for key in expected - {"rate"}: native_true(row[key], "Bubbles205 " + key)
    _one_summary(smoke, "PASS NTUF BUBBLES205 actual General + native controller + touch JoystickAttack/ButtonActive + real Player firing/source race EndStep at30/60Hz")
    return {"rows": rows, "physical_device_tested": False,
        "scope": "Actual native input producer, controller helper, JoystickAttack/ButtonActive, Player firing and source race EndStep at30/60; no physical controller claim"}


def verify_visual205(smoke, artifacts, directory):
    summaries = (
        "PASS FRONTIER visual205 real Video settings ON/OFF/AUTO, RGB/HEX black+pink+green persistence, local body/Pet/HUD color and remote color preservation, native Video/Profile color back navigation and Draw GUI screenshots",
        "PASS FRONTIER visual205 actual Player.Draw, black-art cardinal1px sprite-sized alpha outlines, nested screenshot targets, camera/draw state, source shader toggles, mirror/rotation, OFF and pause guards, context-loss recreation",
        "PASS FRONTIER visual205 six real B-skin rich-text locale/GUI bounds, dynamic progress, transparent source Storms silhouette and screenshot evidence; desktop only, mobile hardware not tested",
    )
    for summary in summaries: _one_summary(smoke, summary)
    prefix = "VISUAL205 TRANSFORM "
    transforms = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    expected = [(shader, mirror, angle) for shader in (0, 1) for mirror in (-1, 1) for angle in (0, 90)]
    assert [(row["shaders"], row["mirror"], row["angle"]) for row in transforms] == expected
    for row in transforms:
        assert row["different"] == 0 and row["first"] == [], "Outline pixels differ from independent native alpha reference"
        assert row["actual_ink"] == row["expected_ink"] == 21
        assert len(row["source_bounds"]) == 4
        for value in row["source_bounds"]: assert finite(value, "Native alpha source bounds", minimum=0) <= 64
    names = ("frontier-visual205-video-settings.png", "frontier-visual205-color-picker.png",
        "frontier-visual205-bubbles-unlock.png", "frontier-visual205-locked-storms.png",
        "frontier-visual205-player-outline.png", *("frontier-visual205-outline-s" + str(shader)
        + "-m" + str(mirror) + "-a" + str(angle) + ".png" for shader, mirror, angle in expected))
    for name in names:
        assert name in artifacts, ("Missing actual native205 GUI/Player screenshot", name)
        header = (directory / name).read_bytes()[:24]
        assert header[:8] == b"\x89PNG\r\n\x1a\n" and header[12:16] == b"IHDR"
        dimensions = (int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big"))
        assert dimensions == (64, 64) if "outline" in name else dimensions in {(320, 240), (360, 240), (426, 240), (480, 270)}
        assert sha(directory / name) == artifacts[name]
    return {"summaries": list(summaries), "transforms": transforms, "screenshots": list(names), "physical_device_tested": False,
        "scope": "Native Video/Profile callbacks, RGB/HEX persistence, true Player.Draw alpha outlines and actual rich-text tooltips; desktop GPU only"}


def verify_walls205(smoke, artifacts, directory):
    name = "frontier-wall-surface205.json"
    evidence = _artifact205(name, artifacts, directory)
    assert evidence["status"] == "PASS"
    expected = [0, 1, 2, 3, 4, 5, 6, 7, 100, 101, 102, 103, 104, 105, 106, 107,
        201, 202, 203, 204, 205, 206, 207, 301, 302, 303, 304, 305, 306]
    rows = evidence["rows"]
    assert isinstance(rows, list) and [row["area"] for row in rows] == expected
    for row in rows:
        assert len(row["source_clip"]) == 4
        for number in row["source_clip"]: finite(number, "Wall205 original art clipping")
        for key in ("actual_native_draw", "physical_collision_retained", "reference_pixels_equal"):
            native_true(row[key], key)
    for area in (0, 7, 206):
        for stem in ("frontier-wall-surface205-area", "frontier-wall-surface205-reference"):
            capture = stem + str(area) + ".png"
            assert capture in artifacts and sha(directory / capture) == artifacts[capture]
    _one_summary(smoke, "PASS WALL SURFACE205 actual native art/collision, all29 area styles and independent GPU reference")
    return {**evidence, "artifact": name, "scope": "All29 actual native art/collision styles with independent GPU reference, retained exterior collision and untouched save"}


def verify_vault205(smoke, artifacts, directory):
    name = "frontier-quest-vault205.json"
    evidence = _artifact205(name, artifacts, directory)
    assert evidence["schema"] == 1 and evidence["status"] == "PASS"
    rows = evidence["routes"]
    assert isinstance(rows, list) and [row["rate"] for row in rows] == [30, 60]
    for row in rows:
        native_true(row["actual_async_generator"], "Actual Vault205 asynchronous generator")
        assert len(row["statues_seen"]) == len(set(row["statues_seen"])) == 4
        assert len(row["guardians_seen"]) == len(set(row["guardians_seen"])) == 4
        for key, minimum in (("dormant_frames", 1), ("actual_shots", 5), ("corpse_attempts", 1), ("corpse_passes", 1)):
            _quest_integer(row[key], key, minimum)
        assert row["portal_type"] == 1
    prefix = "FR_QUEST_VAULT205 "
    assert [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)] == rows
    return {**evidence, "artifact": name, "scope": "Genuine generated ordinary Vault, real statue/guardian projectile deaths, dormant quest negative control and passing Corpse.Alarm0 exit at30/60"}


def verify_quest_continue205(smoke, artifacts, directory):
    name = "frontier-quest-continue205.json"
    evidence = _artifact205(name, artifacts, directory)
    assert evidence["schema"] == 1 and evidence["status"] == "PASS" and evidence["reason"] == ""
    for key in ("full_binary_native_continue", "actual_source_merges_and_combat"):
        native_true(evidence[key], key)
    rows = evidence["rows"]
    assert isinstance(rows, list) and [row["rate"] for row in rows] == [30, 60]
    for row in rows:
        assert len(row["actual_merges"]) == 3 and all(_mutation_flag(value, "native source merge") for value in row["actual_merges"])
        assert row["source_hearts"] == 8 and row["held_parts"] == 4
        for key in ("source_enemies", "source_shots"): _quest_integer(row[key], key, 1)
        _quest_integer(row["binary_bytes"], "Native binary Continue bytes", 129)
        finite(row["guarded_ticks"], "Guarded Continue logical ticks", minimum=90)
        assert row["room_ends"] == row["room_starts"] == 1
        assert row["loaded_player"] != row["source_initial_player"] and row["loaded_chest"] != row["source_initial_chest"]
        for key in ("before_guard", "continued", "active_after", "guard_after", "unlockable_after"):
            native_true(row[key], key)
        unlock = row["native_unlock"]
        assert not _mutation_flag(unlock["locked"], "native locked chest after UNLOCK")
        native_true(unlock["reward"], "native reward chest")
        assert not _mutation_flag(unlock["guard"], "quest guard after UNLOCK")
        assert not _mutation_flag(unlock["active"], "active claim after UNLOCK")
    logged = [json.loads(line[len("FR_QUEST_CONTINUE205 "):]) for line in smoke.splitlines() if line.startswith("FR_QUEST_CONTINUE205 ")]
    assert logged and logged[-1] == evidence and sum(row.get("status") == "PASS" for row in logged) == 1
    _one_summary(smoke, "PASS FRONTIER Quest205 genuine merges/held graph/full binary Vlambeer Continue/new Vault/eightDraw/90tick guard/native UNLOCK release x30/60")
    return {**evidence, "artifact": name, "scope": "Actual source merges/combat and native full binary Continue, generated Vault, eight real Draws,90tick locked guard and genuine UNLOCK release at30/60"}


def verify_lair205(case, smoke, artifacts, directory):
    name = "frontier-lair-return205.json"
    evidence = _artifact205(name, artifacts, directory)
    assert evidence["schema"] == 1 and evidence["status"] == "PASS" and evidence["reason"] == ""
    native_true(evidence["native_sampled_movement"], "Lair205 actual sampled movement")
    assert evidence["production_terrain_modified_by_test"] is False
    linger = case == "FrontierLairReturnLinger205Tests"
    expected = [(seed, rate) for seed in ((6123,) if linger else (6123, 41, 702643)) for rate in (30, 60)]
    rows = evidence["routes"]
    assert isinstance(rows, list) and [(row["seed"], row["rate"]) for row in rows] == expected
    common = {"entered-before-border", "returned-to-pizza-before-cavein", "real-crossing-triggered-cavein",
        "returned-during-cavein-countdown", "moved-away-after-cavein"}
    for row in rows:
        assert _mutation_flag(row["linger"], "Lair205 lingering branch") == linger
        for key in ("before_return", "during_return", "after_cavein"): native_true(row[key], key)
        _quest_integer(row["move_samples"], "native sampled traversal", 1)
        labels = [witness["label"] for witness in row["witnesses"]]
        assert common <= set(labels) and len(labels) == len(set(labels))
        assert "persistent-wall-overlap" not in labels and "native-route-stalled" not in labels
        # The fixed source releases a healthy edge Player before persistent-item
        # salvage. Capturing that Player is a diagnostic for the legacy saved
        # array fallback, not a prerequisite that would require the old bug.
        captured = "native-border-captured-live-player" in labels
        assert _mutation_flag(row["buried_witness"], "Lair205 optional native capture") == captured
        required = {"lingered-through-real-cavein", "eight-real-draws-after-lingering-cavein"} if linger else {"survived-real-cavein-clear-of-walls", "approached-closed-rubble-without-overlap"}
        assert required <= set(labels)
        indexed = {witness["label"]: witness for witness in row["witnesses"]}
        for witness in row["witnesses"]:
            assert finite(witness["hp"], "Lair205 native HP", minimum=0) > 0
            assert len(witness["xy"]) == 2
            for coordinate in witness["xy"]: finite(coordinate, "Lair205 actual native position")
            finite(witness["frame"], "Lair205 actual native frame", minimum=0)
            if witness["label"] in required or witness["label"] == "moved-away-after-cavein":
                native_true(witness["visible"], "Lair205 released player visible")
                assert not _mutation_flag(witness["saved_by_border"], "Lair205 retained in border")
                assert not _mutation_flag(witness["saved_by_rubble"], "Lair205 retained in rubble")
                assert not _mutation_flag(witness["in_wall"], "Lair205 final player in wall")
                assert finite(witness["cavein"], "Lair205 completed native cavein") < 0
        origin = indexed["eight-real-draws-after-lingering-cavein" if linger else "approached-closed-rubble-without-overlap"]
        moved = indexed["moved-away-after-cavein"]
        assert moved["frame"] > origin["frame"], "Lair205 actual retreat did not advance native frames"
        assert sum((a-b)**2 for a, b in zip(moved["xy"], origin["xy"])) >= 16**2, "Lair205 actual retreat did not move16px"
        if linger:
            begin = indexed["lingered-through-real-cavein"]
            assert origin["frame"]-begin["frame"] >= 8*30/row["rate"], "Lair205 omitted eight real Draws after collapse"
    assert evidence["active"] == {"completed": True}
    logged = [json.loads(line[len("FR_LAIR_RETURN205 "):]) for line in smoke.splitlines() if line.startswith("FR_LAIR_RETURN205 ")]
    assert logged and logged[-1] == evidence and sum(row.get("status") == "PASS" for row in logged) == 1
    _one_summary(smoke, "PASS FRONTIER Pizza-to-Lair205 real opening, native sampled entry/return before/during cavein, postcavein movement x3seeds x30/60")
    return {**evidence, "artifact": name, "scope": "Real generated Pizza/Lair opening and native sampled mask collision, entry/return/cave-in and post-collapse movement; no test wall removal"}


def verify_pirate205(smoke, artifacts, directory):
    name = "frontier-pirate-visibility205.json"
    evidence = _artifact205(name, artifacts, directory)
    assert evidence.get("diagnostic_only") is False, "A Pirate diagnostic observation is not repair acceptance"
    assert evidence["reported_area"] == "Cove L1"
    rows = evidence["cases"]
    assert isinstance(rows, list) and [(row["seed"], row["rate"]) for row in rows] == [(205091, 30), (205091, 60), (205151, 30), (205151, 60)]
    clusters = 0
    for row in rows:
        assert row["loops"] == row["subarea"] == 1
        _quest_integer(row["test_bullets"], "actual scheduled friendly collisions", 1)
        assert row["hitme_births"] and row["shots"] and row["samples"]
        final = row["samples"][-1]
        assert final["ticks"] >= 600 and final["counted_enemies"] == [], "Invisible or surviving counted enemies still prevent the genuine exit"
        natural = final["natural"]
        assert not _mutation_flag(natural["clear_check"], "Pirate205 final native clear check")
        assert not _mutation_flag(natural["portal_blocked"], "Pirate205 final portal blocker")
        assert natural["pending_police"] == 0 and natural["portals"] > 0
        for cluster in row["clusters"]:
            clusters += 1
            native_true(cluster["scheduled_bullet"], "Actual source-factory cluster received friendly collision")
            source, actor = cluster["source"], cluster["actor"]
            assert actor["object"] == source["object"] and actor["name"] == source["name"]
            assert actor["max_hp"] == source["max_hp"] and actor["max_hp"] > 1 and actor["hp"] > 0
            for key in ("sprite_exists", "factory_retained", "on_step", "on_draw", "on_hurt"):
                native_true(actor[key], "Initialized source-factory cluster " + key)
            assert not _mutation_flag(actor["fr_maxhealth_init"], "cluster cached pre-source maxhealth")
            assert actor["id"] not in [body["id"] for body in final["all_hitme"]], "Native cluster survived its real friendly collision"
            assert any(shot["target"]["id"] == actor["id"] for shot in row["shots"])
    assert clusters > 0, "Pirate205 did not exercise a genuine native loop cluster"
    prefix = "PIRATE VISIBILITY205 NATURAL OBSERVED "
    observed = [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    assert observed == [{"seed": row["seed"], "rate": row["rate"], "shots": row["test_bullets"], "final": row["samples"][-1]} for row in rows]
    return {**evidence, "artifact": name, "scope": "Two real generated L1 Cove seeds at30/60, observed hitme births/provenance and scheduled friendly collision deaths followed by genuine natural clear exit"}


def verify_bloodlust205(smoke, artifacts, directory):
    name = "frontier-bloodlust205.json"
    evidence = _artifact205(name, artifacts, directory)
    assert evidence["schema"] == 1 and evidence["status"] == "PASS" and evidence["reason"] == ""
    assert evidence["direct_effect_calls"] is False, "An injected heal or counter is not actual mutation acceptance"
    rows = evidence["routes"]
    assert isinstance(rows, list) and [(row["rate"], row["family"]) for row in rows] == [
        (rate, family) for rate in (30, 60) for family in ("native", "NTTE", "NTUF")]
    for row in rows:
        assert row["failures"] == [] and row["grant"] == "actual AugmentStation source step"
        native_true(row["station_opened"], "Actual source mutation station opened")
        assert row["unowned_counter"] == row["live_despawn_counter"] == 0
        assert (row["initial_hp"], row["injured_hp"], row["healed_hp"],
            row["counter_at_12"], row["counter_after_13"]) == (8, 5, 6, 12, 0)
        settled = row["settled"]
        assert isinstance(settled, list) and len(settled) == 13
        assert [(state["kills"], state["counter"], state["hp"], state["procs"]) for state in settled] == [
            (kill, kill if kill < 13 else 0, 5 if kill < 13 else 6, 0 if kill < 13 else 1) for kill in range(1, 14)]
        assert len(row["procs"]) == 1
        assert any("AugmentBloodlust" in str(frame) for frame in row["procs"][0]["callstack"]), "Heal bypassed real source mutation step"
        shots, deaths = row["shots"], row["deaths"]
        assert isinstance(shots, list) and len(shots) >= 15
        assert sum(shot["phase"] == 1 and shot["projectile"] == "Bullet1" for shot in shots) == 1
        assert sum(shot["phase"] == 3 and shot["projectile"] == "EnemyBullet1" and shot["damage"] == 3 for shot in shots) == 1
        kills = [shot for shot in shots if shot["phase"] == 5]
        assert len(kills) == 13 and [shot["kill_index"] for shot in kills] == list(range(13))
        assert all(shot["projectile"] == "Bullet1" and shot["damage"] > 0 for shot in kills)
        combat = [death for death in deaths if death["phase"] == 5 and death["hp"] <= 0]
        assert len(combat) == 13 and [death["kill_index"] for death in combat] == list(range(13))
        assert len({death["id"] for death in combat}) == 13
        assert {death["id"] for death in combat} == {shot["target"] for shot in kills}
        assert sum(death["phase"] == 1 and death["hp"] <= 0 for death in deaths) == 1
        assert sum(death["phase"] == 2 and death["hp"] > 0 for death in deaths) == 1
        assert all(death["callstack"] for death in combat)
        if row["family"] == "NTUF": native_true(row["held_dead_source_poll"], "Native held-dead source poll and ordinary Destroy deduplicate")
    prefix = "FR_BLOODLUST205 OBSERVED "
    assert [json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)] == rows
    _one_summary(smoke, "PASS Carnivorous Enzymes actual AugmentStation grant, native projectiles,12+1 deaths, deduplication and injured Player healing across native/NTTE/NTUF at30/60Hz")
    return {**evidence, "artifact": name, "scope": "Actual AugmentStation replacement, enemy projectile injury and13 real projectile kills through native/NTTE/NTUF ordinary lifecycles at30/60; unowned/live cleanup controls and source-poll deduplication, no direct mutation effect calls"}


def verify204_identity(case, smoke, artifacts, directory):
    if case == "FrontierContinueAudio205Tests": return verify_audio205(smoke)
    if case == "FrontierBubblesAttack205Tests": return verify_bubbles205(smoke)
    if case == "FrontierVisual205Tests": return verify_visual205(smoke, artifacts, directory)
    if case == "FrontierWallSurface205Tests": return verify_walls205(smoke, artifacts, directory)
    if case == "FrontierQuestVault205Tests": return verify_vault205(smoke, artifacts, directory)
    if case == "FrontierQuestContinue205Tests": return verify_quest_continue205(smoke, artifacts, directory)
    if case in {"FrontierLairReturn205Tests", "FrontierLairReturnLinger205Tests"}: return verify_lair205(case, smoke, artifacts, directory)
    if case == "FrontierPirateVisibility205Tests": return verify_pirate205(smoke, artifacts, directory)
    if case == "FrontierBloodlust205Tests": return verify_bloodlust205(smoke, artifacts, directory)
    return _retained205_identity(case, smoke, artifacts, directory)


if __name__ == "__main__":
    main()
