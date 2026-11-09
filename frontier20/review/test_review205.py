"""Inert205 evidence guards; no compiler, game, package, Git or cloud runs."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Review205Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = load("review205_guards", "review/verify_205_repairs.py")
        cls.capture = load("capture205_guards", "review/capture205_python.py")
        cls.packages = load("package205_guards", "review/inspect_release205_packages.py")
        cls.font = load("font205_guards", "review/verify_release205_debug_font.py")

    def test_all82_cases_retain_exact_frozen72_and_ten_current_routes(self):
        tool = self.review
        prior = json.loads((ROOT / "review/release204r2-cases.json").read_text("utf8"))
        self.assertEqual(len(tool.NEW205_CASES), 10)
        self.assertEqual(tool.FINAL_CASES, tuple([*tool.NEW205_CASES, *prior["cases"]]))
        self.assertEqual(len(tool.FINAL_CASES), 82)
        self.assertEqual(set(tool.FINAL_CASES), tool.REQUIRED205_CASES)
        selection = json.loads((ROOT / "review/release205-cases.json").read_text("utf8"))
        for change in ("missing-old", "missing-linger", "duplicate", "reordered", "old-version"):
            current = deepcopy(selection)
            if change == "missing-old": current["cases"].pop()
            elif change == "missing-linger": current["cases"].remove("FrontierLairReturnLinger205Tests")
            elif change == "duplicate": current["cases"][-1] = current["cases"][0]
            elif change == "reordered": current["cases"][0:2] = current["cases"][1::-1]
            else: current["internal"] = 102
            actual = tool.read
            with self.subTest(change=change), patch.object(tool, "read", side_effect=lambda path: current if path == tool.CASE_SELECTION else actual(path)):
                with self.assertRaises(AssertionError): tool.load_cases()

    def test_imports_cannot_build_write_or_publish(self):
        with patch.object(Path, "write_text", side_effect=AssertionError("unexpected writer")), \
                patch.object(Path, "write_bytes", side_effect=AssertionError("unexpected writer")), \
                patch.object(Path, "mkdir", side_effect=AssertionError("unexpected mkdir")), \
                patch.object(subprocess, "run", side_effect=AssertionError("unexpected process")), \
                patch.object(subprocess, "Popen", side_effect=AssertionError("unexpected process")):
            for index, name in enumerate(("verify_205_repairs", "capture205_python", "inspect_release205_packages", "verify_release205_debug_font")):
                load("inert205_" + str(index), "review/" + name + ".py")

    def test_new_baseline_is_published_build102_and_same_vm_is_mandatory(self):
        tool = self.review
        self.assertEqual(tool.PRIOR_MANIFEST.parent.name, "mobile-release204r2-20261108")
        self.assertEqual(tool.sha(tool.PRIOR_MANIFEST), tool.PRIOR_MANIFEST_SHA256)
        with self.assertRaisesRegex(AssertionError, "complete root-authored selection"):
            tool.check_run("20261109T000000000000Z", tool.FINAL_CASES[:-1])
        with self.assertRaisesRegex(AssertionError, "different release"):
            tool.verify_python_sources({"version": "2.0.4", "internal": 102})

    def test_capture_and_verifier_bind_current_and_retained_reviewers(self):
        self.assertEqual(self.review.REVIEW_TESTS, self.capture.REVIEW_TESTS)
        self.assertEqual(self.review.REVIEW_INPUTS, self.capture.REVIEW_INPUTS)
        self.assertIn("review/test_review205.py", self.capture.REVIEW_TESTS)
        self.assertIn("review/test_review204r2.py", self.capture.REVIEW_TESTS)
        self.assertEqual(self.capture.reviewer_inputs(), {name: self.review.sha(ROOT / name) for name in self.review.REVIEW_INPUTS})
        self.assertIn("native/visual205.gml", self.capture.inputs())
        self.assertIn("tools/release205_delivery.py", self.capture.inputs())

    def test_package_identity_paths_and_exact_delivery_wrapper(self):
        package = self.packages
        self.assertEqual((package.VERSION, package.INTERNAL), ("2.0.5", 103))
        self.assertEqual(package.RELEASE.name, "mobile-release205-20261109")
        self.assertEqual(package.package_path("Android").name, "NuclearThrone.NTTE-NTUF-Android-2.0.5.apk")
        self.assertEqual(package.package_path("iOS").name, "NuclearThrone.NTTE-NTUF-iOS-2.0.5.ipa")
        self.assertEqual(self.font.OUTPUT.name, "dbg-font-full-range-coverage-205.json")
        source = (ROOT / "tools/release205_delivery.py").read_text("utf8")
        selection = json.loads((ROOT / "review/release205-cases.json").read_text("utf8"))
        self.assertEqual(package.delivery_cases(source, selection), self.review.FINAL_CASES)
        for changed in (source + "\npublish()\n", source.replace("INTERNAL = 103", "INTERNAL = 104"), source + "\n_BASE_TOOL_SHA256='0'*64\n"):
            with self.subTest(change=changed[-55:]), self.assertRaisesRegex(RuntimeError, "wrapper changed"):
                package.delivery_cases(changed, selection)

    def test_audio_requires_complete_ownership_continue_and_regeneration_assertions(self):
        summaries = [
            "NTUF AUDIO205 source loop + normal Destroy + Cleanup-only + reused sample + preview PASS",
            "PASS NTUF AUDIO205 actual source Bulwark voices, normal Destroy, Cleanup-only, reused sample, native preview/full loader + room_restart + async terrain",
        ]
        self.review.verify_audio205("\n".join(summaries))
        for smoke in (summaries[0], summaries[1], "\n".join(summaries + [summaries[1]])):
            with self.assertRaises(AssertionError): self.review.verify_audio205(smoke)

    def test_bubbles_requires_real_attack_mapping_both_rates_and_all_controls(self):
        rows = [dict(rate=rate, actual_general=True, controller_named_buttons=True,
            touch_joystick_and_ability=True, idle_no_spray=True, release_stops=True,
            weapon_excluded=True, mode_off_fires=True, preference_off_original_controls=True) for rate in (30, 60)]
        summary = "PASS NTUF BUBBLES205 actual General + native controller + touch JoystickAttack/ButtonActive + real Player firing/source race EndStep at30/60Hz"

        def smoke(values): return "\n".join([*("NTUF BUBBLES205 " + json.dumps(row) for row in values), summary])
        self.review.verify_bubbles205(smoke(rows))
        for key in rows[0]:
            changed = deepcopy(rows)
            changed[0][key] = 60 if key == "rate" else False
            with self.subTest(key=key), self.assertRaises(AssertionError): self.review.verify_bubbles205(smoke(changed))

    def test_diagnostic_only_pirate_observation_can_never_claim_repair(self):
        evidence = dict(diagnostic_only=True, status="PASS", physical_device_tested=False, reported_area="Cove L1", cases=[])
        with patch.object(self.review, "_artifact205", return_value=evidence):
            with self.assertRaisesRegex(AssertionError, "diagnostic observation"):
                self.review.verify_pirate205("PASS", {}, ROOT)

    def test_normal_vault_requires_all_guardians_real_deaths_and_natural_alarm_exit(self):
        rows = [dict(rate=rate, actual_async_generator=True, statues_seen=[1, 2, 3, 4],
            guardians_seen=[5, 6, 7, 8], dormant_frames=100, actual_shots=5,
            corpse_attempts=1, corpse_passes=1, portal_type=1) for rate in (30, 60)]

        def verify(values):
            evidence = dict(schema=1, status="PASS", physical_device_tested=False, routes=values)
            smoke = "\n".join("FR_QUEST_VAULT205 " + json.dumps(row) for row in values)
            with patch.object(self.review, "_artifact205", return_value=evidence):
                return self.review.verify_vault205(smoke, {}, ROOT)
        verify(rows)
        for key, value in (("guardians_seen", [5, 6, 7]), ("actual_shots", 0), ("corpse_passes", 0), ("portal_type", 3), ("actual_async_generator", False)):
            changed = deepcopy(rows); changed[0][key] = value
            with self.subTest(key=key), self.assertRaises(AssertionError): verify(changed)

    def test_visual_and_wall_review_cannot_pass_without_actual_native_artifacts(self):
        with self.assertRaises(AssertionError): self.review.verify_visual205("PASS", {}, ROOT)
        with patch.object(self.review, "_artifact205", return_value=dict(status="PASS", physical_device_tested=False, rows=[])):
            with self.assertRaises(AssertionError): self.review.verify_walls205("PASS", {}, ROOT)

    def test_lair_linger_requires_safe_real_collapse_draws_and_retreat_without_old_bug_capture(self):
        labels = ["entered-before-border", "returned-to-pizza-before-cavein",
            "real-crossing-triggered-cavein", "returned-during-cavein-countdown",
            "lingered-through-real-cavein", "eight-real-draws-after-lingering-cavein",
            "moved-away-after-cavein"]
        rows = []
        for rate in (30, 60):
            frames = [1, 2, 3, 4, 30, 30+8*30/rate, 50]
            witnesses = [dict(label=label, frame=frame, xy=[32 if index == 6 else 0, 0],
                hp=8, visible=True, saved_by_border=False, saved_by_rubble=False,
                in_wall=False, cavein=-1 if index >= 4 else 1)
                for index, (label, frame) in enumerate(zip(labels, frames))]
            rows.append(dict(seed=6123, rate=rate, linger=True, before_return=True,
                during_return=True, after_cavein=True, move_samples=150,
                buried_witness=False, witnesses=witnesses))

        def verify(values):
            evidence = dict(schema=1, status="PASS", reason="", physical_device_tested=False,
                native_sampled_movement=True, production_terrain_modified_by_test=False,
                routes=values, active=dict(completed=True))
            smoke = "\n".join(["FR_LAIR_RETURN205 " + json.dumps(evidence),
                "PASS FRONTIER Pizza-to-Lair205 real opening, native sampled entry/return before/during cavein, postcavein movement x3seeds x30/60"])
            with patch.object(self.review, "_artifact205", return_value=evidence):
                return self.review.verify_lair205("FrontierLairReturnLinger205Tests", smoke, {}, ROOT)

        verify(rows)  # Proactive healthy Player release never enters item salvage.
        captured = deepcopy(rows)
        captured[0]["buried_witness"] = True
        captured[0]["witnesses"].insert(4, dict(captured[0]["witnesses"][3],
            label="native-border-captured-live-player", saved_by_border=True))
        verify(captured)  # The legacy saved-array fallback remains admissible.
        changed = deepcopy(rows); changed[0]["buried_witness"] = True
        with self.assertRaises(AssertionError): verify(changed)
        changed = deepcopy(captured); changed[0]["buried_witness"] = False
        with self.assertRaises(AssertionError): verify(changed)
        for label in labels[-3:]:
            for key, value in (("visible", False), ("saved_by_border", True),
                    ("saved_by_rubble", True), ("in_wall", True), ("hp", 0), ("cavein", 1)):
                changed = deepcopy(rows)
                next(w for w in changed[0]["witnesses"] if w["label"] == label)[key] = value
                with self.subTest(label=label, key=key), self.assertRaises(AssertionError): verify(changed)
        for label in labels[-3:]:
            changed = deepcopy(rows); changed[0]["witnesses"] = [w for w in changed[0]["witnesses"] if w["label"] != label]
            with self.subTest(missing=label), self.assertRaises(AssertionError): verify(changed)
        changed = deepcopy(rows); changed[0]["witnesses"][-2]["frame"] = 37
        with self.assertRaises(AssertionError): verify(changed)
        changed = deepcopy(rows); changed[0]["witnesses"][-1]["xy"] = [15, 0]
        with self.assertRaises(AssertionError): verify(changed)
        changed = deepcopy(rows); changed[0]["witnesses"][-1]["frame"] = 38
        with self.assertRaises(AssertionError): verify(changed)

    def test_bloodlust_requires_source_station_real_projectiles_thirteen_kills_and_one_heal(self):
        rows = []
        for rate in (30, 60):
            for family in ("native", "NTTE", "NTUF"):
                kills = [dict(phase=5, kill_index=kill, projectile="Bullet1", damage=10010, target=100+kill) for kill in range(13)]
                rows.append(dict(rate=rate, family=family, failures=[], grant="actual AugmentStation source step",
                    station_opened=True, unowned_counter=0, live_despawn_counter=0,
                    initial_hp=8, injured_hp=5, healed_hp=6, counter_at_12=12, counter_after_13=0,
                    held_dead_source_poll=family == "NTUF",
                    settled=[dict(kills=kill, counter=kill if kill < 13 else 0,
                        hp=5 if kill < 13 else 6, procs=0 if kill < 13 else 1) for kill in range(1, 14)],
                    procs=[dict(callstack=["fr_AugmentBloodlust_step"])],
                    shots=[dict(phase=1, projectile="Bullet1"), dict(phase=3, projectile="EnemyBullet1", damage=3), *kills],
                    deaths=[dict(phase=1, hp=0), dict(phase=2, hp=10), *[
                        dict(phase=5, hp=0, kill_index=kill, id=100+kill, callstack=["native actual Destroy"]) for kill in range(13)]]))

        def verify(values, direct=False):
            evidence = dict(schema=1, status="PASS", reason="", direct_effect_calls=direct,
                physical_device_tested=False, routes=values)
            smoke = "\n".join([*("FR_BLOODLUST205 OBSERVED " + json.dumps(row) for row in values),
                "PASS Carnivorous Enzymes actual AugmentStation grant, native projectiles,12+1 deaths, deduplication and injured Player healing across native/NTTE/NTUF at30/60Hz"])
            with patch.object(self.review, "_artifact205", return_value=evidence):
                return self.review.verify_bloodlust205(smoke, {}, ROOT)

        verify(rows)
        with self.assertRaises(AssertionError): verify(rows, direct=True)
        with self.assertRaises(AssertionError): verify(rows[:-1])
        for key, value in (("unowned_counter", 1), ("live_despawn_counter", 1), ("station_opened", False),
                ("counter_at_12", 0), ("healed_hp", 5), ("procs", []), ("shots", rows[0]["shots"][:-1])):
            changed = deepcopy(rows); changed[0][key] = value
            with self.subTest(key=key), self.assertRaises(AssertionError): verify(changed)
        changed = deepcopy(rows); changed[2]["held_dead_source_poll"] = False
        with self.assertRaises(AssertionError): verify(changed)
        changed = deepcopy(rows); changed[0]["settled"][0]["hp"] = 6
        with self.assertRaises(AssertionError): verify(changed)
        changed = deepcopy(rows); changed[0]["procs"][0]["callstack"] = ["injected_heal"]
        with self.assertRaises(AssertionError): verify(changed)


if __name__ == "__main__":
    unittest.main()
