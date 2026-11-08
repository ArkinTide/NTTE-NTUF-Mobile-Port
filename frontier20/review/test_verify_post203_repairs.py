"""Temporary-data gates for204 evidence semantics; no native game execution."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


PATH = Path(__file__).with_name("verify_post203_repairs.py")
SPEC = importlib.util.spec_from_file_location("review204_semantics_under_test", PATH)
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


class PythonCaptureBinding(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        paths = ("tools/build.py", "native/fixture.gml", *REVIEW.REVIEW_INPUTS)
        for name in paths:
            path = self.directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("temporary guarded input: " + name, encoding="utf8")
        self.evidence = {
            "version": "2.0.4", "internal": 100,
            "source_inputs": {name: REVIEW.sha(self.directory / name) for name in paths[:2]},
            "source_inputs_unchanged": True,
            "reviewer_inputs": {name: REVIEW.sha(self.directory / name) for name in REVIEW.REVIEW_INPUTS},
            "reviewer_inputs_unchanged": True,
            "review_test_modules": list(REVIEW.REVIEW_TESTS),
        }

    def verify(self, evidence=None):
        with patch.object(REVIEW, "ROOT", self.directory):
            return REVIEW.verify_python_sources(self.evidence if evidence is None else evidence)

    def test_accepts_exact_current_sources_and_explicit_review_inputs(self):
        self.assertEqual(self.verify(), self.evidence["source_inputs"])

    def test_rejects_stale_added_or_missing_maintained_source(self):
        for change in ("stale", "added", "missing"):
            with self.subTest(change=change):
                path = self.directory / "native/fixture.gml"
                original = path.read_bytes()
                extra = self.directory / "tools/additional.py"
                try:
                    if change == "stale":
                        path.write_text("changed after capture", encoding="utf8")
                    elif change == "added":
                        extra.write_text("not captured", encoding="utf8")
                    else:
                        path.unlink()
                    with self.assertRaisesRegex(AssertionError, "maintained inputs"):
                        self.verify()
                finally:
                    path.write_bytes(original)
                    extra.unlink(missing_ok=True)

    def test_rejects_missing_extra_or_stale_reviewer_digest(self):
        for change in ("missing", "extra", "stale"):
            value = deepcopy(self.evidence)
            if change == "missing":
                del value["reviewer_inputs"][REVIEW.REVIEW_INPUTS[0]]
            elif change == "extra":
                value["reviewer_inputs"]["review/unreviewed.py"] = "0" * 64
            else:
                value["reviewer_inputs"][REVIEW.REVIEW_INPUTS[1]] = "0" * 64
            with self.subTest(change=change), self.assertRaisesRegex(AssertionError, "reviewer inputs"):
                self.verify(value)

    def test_rejects_actual_reviewer_edit_after_capture(self):
        (self.directory / REVIEW.REVIEW_INPUTS[0]).write_text("changed capture logic", encoding="utf8")
        with self.assertRaisesRegex(AssertionError, "reviewer inputs"):
            self.verify()

    def test_rejects_changed_or_unreported_inputs_during_checks(self):
        for field in ("source_inputs_unchanged", "reviewer_inputs_unchanged"):
            for invalid in (False, None, 1):
                value = deepcopy(self.evidence)
                value[field] = invalid
                with self.subTest(field=field, invalid=invalid), self.assertRaisesRegex(AssertionError, "changed during checks"):
                    self.verify(value)

    def test_requires_exact_two_review_modules_in_aggregate_capture(self):
        for modules in ([], list(REVIEW.REVIEW_TESTS[:1]), list(reversed(REVIEW.REVIEW_TESTS)),
                        [*REVIEW.REVIEW_TESTS, "review/unrelated.py"]):
            value = deepcopy(self.evidence)
            value["review_test_modules"] = modules
            with self.subTest(modules=modules), self.assertRaisesRegex(AssertionError, "test modules"):
                self.verify(value)

    def test_rejects_wrong_or_loosely_typed_release_identity(self):
        for field, invalid in (("version", "2.0.3"), ("internal", 99), ("internal", 100.0),
                               ("internal", "100"), ("version", None)):
            value = deepcopy(self.evidence)
            value[field] = invalid
            with self.subTest(field=field, invalid=invalid), self.assertRaisesRegex(AssertionError, "different release"):
                self.verify(value)


class NaturalVisibilityLaunchSemantics(unittest.TestCase):
    @staticmethod
    def evidence():
        rows = []
        for index in range(12):
            for loops in (0, 1, 3):
                rows.append({"seed": 103038 + 97 * index, "loops": loops,
                             "subarea": 1 + index % 3, "rate": 30 if index % 2 == 0 else 60,
                             "samples": [{"source_ticks": 0, "actors": []}]})
        for row_index in (0, 3):
            row = rows[row_index]
            actor = 100000 + row_index * 10
            source = {"id": actor, "object": "SnowBot", "hp": 15, "team": 1,
                      "x": 100.4, "y": 200.6, "visible": 1.0, "alpha": 1,
                      "mask": 286, "canfly": False, "intro": None,
                      "top": -4, "top_exists": 0.0, "top_owns_target": False,
                      "floor_contact": 1.0, "wall_contact": 0.0}
            launch = {"source": source,
                      "floor": {"id": actor + 5, "x": 96, "y": 192, "bbox": [96, 192, 127, 223]},
                      "wrapper": [100, 209],
                      "ray": {"from": [100, 217], "to": [112, 208], "wall": -4, "top_small": -4}}
            row["samples"][0]["actors"] = [source]
            row["natural_clone"] = {"source": actor, "launch": launch,
                                    "before": {"id": actor + 1, "object": "SnowBot", "mask": 260}}
        return {"physical_device_tested": False, "clone_top_repair_tested": True,
                "clone_toss_repair_tested": True, "natural_city": rows,
                "possessed_host_deaths": [{"rate": 30}, {"rate": 60}]}

    @staticmethod
    def log(value):
        lines = []
        for row in value["natural_city"]:
            lines.append("FRONTIER ENEMY VISIBILITY CITY BEGIN " + json.dumps(
                {field: row[field] for field in ("seed", "loops", "subarea", "rate")}))
            if row.get("natural_clone") is not None:
                lines.append("FRONTIER ENEMY VISIBILITY NATURAL CLONE LAUNCH " + json.dumps(
                    row["natural_clone"]["launch"]))
            lines.append("FRONTIER ENEMY VISIBILITY CITY OBSERVED " + json.dumps(row))
        return "\n".join(lines)

    def verify(self, value, smoke=None):
        REVIEW.verify_enemy_visibility_launches(self.log(value) if smoke is None else smoke, value)

    def test_accepts_exact_rounded_native_rays_and_both_rate_witnesses(self):
        self.verify(self.evidence())

    def test_rejects_missing_duplicate_or_wrong_rate_and_native_case_identity(self):
        for field in ("missing", "duplicate", "rate", "seed", "loops", "subarea", "order"):
            value = self.evidence()
            rows = value["natural_city"]
            if field == "missing":
                del rows[3]["natural_clone"]
            elif field == "duplicate":
                rows[1]["natural_clone"] = deepcopy(rows[0]["natural_clone"])
            elif field == "order":
                rows[0], rows[1] = rows[1], rows[0]
            else:
                rows[3][field] += 1
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.verify(value)

    def test_rejects_ungrounded_hidden_flying_or_preowned_source(self):
        changes = {"hp": 11.999, "team": 2, "visible": 0, "alpha": 0, "canfly": True,
                   "intro": False, "top": 99, "top_exists": 1, "top_owns_target": True,
                   "floor_contact": 0, "wall_contact": 1, "mask": 260}
        for field, invalid in changes.items():
            value = self.evidence()
            value["natural_city"][0]["natural_clone"]["launch"]["source"][field] = invalid
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.verify(value)

    def test_rejects_wrong_source_identity_object_and_generated_snapshot(self):
        for field in ("identity", "copy-object", "copy-identity", "snapshot", "initial-tick"):
            value = self.evidence()
            row = value["natural_city"][0]
            trial = row["natural_clone"]
            if field == "identity":
                trial["source"] += 1
            elif field == "copy-object":
                trial["before"]["object"] = "Bandit"
            elif field == "copy-identity":
                trial["before"]["id"] = trial["source"]
            elif field == "snapshot":
                row["samples"][0]["actors"] = []
            else:
                row["samples"][0]["source_ticks"] = 1
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.verify(value)

    def test_rejects_rounded_wrapper_ray_or_floor_geometry_drift(self):
        for field in ("wrapper-x", "wrapper-y", "ray-start", "ray-end", "bbox", "floor-id", "nonfinite", "boolean"):
            value = self.evidence()
            launch = value["natural_city"][0]["natural_clone"]["launch"]
            if field.startswith("wrapper"):
                launch["wrapper"][int(field.endswith("y"))] += 1
            elif field == "ray-start":
                launch["ray"]["from"][1] -= 8
            elif field == "ray-end":
                launch["ray"]["to"][0] -= .5
            elif field == "bbox":
                launch["floor"]["bbox"][2] = 95
            elif field == "floor-id":
                launch["floor"]["id"] = -4
            elif field == "nonfinite":
                launch["source"]["x"] = float("nan")
            else:
                launch["wrapper"][0] = True
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.verify(value)

    def test_rejects_wall_or_topsmall_occlusion_and_non_native_noone(self):
        for field in ("wall", "top_small"):
            for invalid in (0, 100005):
                value = self.evidence()
                value["natural_city"][0]["natural_clone"]["launch"]["ray"][field] = invalid
                with self.subTest(field=field, invalid=invalid), self.assertRaises(AssertionError):
                    self.verify(value)

    def test_rejects_missing_or_stale_begin_launch_and_completed_trace(self):
        for prefix in ("CITY BEGIN ", "NATURAL CLONE LAUNCH ", "CITY OBSERVED "):
            value = self.evidence()
            smoke = self.log(value).replace("FRONTIER ENEMY VISIBILITY " + prefix, "OMITTED ", 1)
            with self.subTest(prefix=prefix), self.assertRaises(AssertionError):
                self.verify(value, smoke)
        value = self.evidence()
        smoke = self.log(value)
        value["natural_city"][0]["natural_clone"]["launch"]["floor"]["x"] += 1
        with self.assertRaises(AssertionError):
            self.verify(value, smoke)

    def test_release_visibility_dispatch_requires_launch_semantics(self):
        value = self.evidence()
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            name = "frontier-enemy-visibility-diagnostic.json"
            (directory / name).write_text(json.dumps(value), encoding="utf8")
            REVIEW.verify204_identity("FrontierEnemyVisibilityTests", self.log(value), {name: "outer hash"}, directory)
            value["natural_city"][0]["natural_clone"]["launch"]["ray"]["wall"] = 5
            (directory / name).write_text(json.dumps(value), encoding="utf8")
            with self.assertRaises(AssertionError):
                REVIEW.verify204_identity("FrontierEnemyVisibilityTests", self.log(value), {name: "outer hash"}, directory)


class BluescreenAdmissionSemantics(unittest.TestCase):
    """Synthetic temporary boundary data only; never native acceptance evidence."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    @staticmethod
    def fixture(choice="Yes", rate=30):
        eligible, accept = choice in {"Yes", "No"}, choice == "Yes"
        mode = "eligible" if eligible else choice.lower()
        def actor(actor_id, **fields):
            return {"id": actor_id, "exists": True, "object": "Player", "race": 8,
                    "x": 100, "y": 100, **fields}
        missing = {"id": -4, "exists": False}
        controller = actor(30, name="fr_bluescreenController", drawConnect=False)
        buttons = [actor(40 + int(yes), yes=yes, done=False, creator=30, creator_exists=True,
                         visible=True, alpha=1, box=[90, 90, 110, 110]) for yes in (False, True)]
        def snapshot(label, host):
            return {"label": label, "host": host, "frame": 46 + host * 30 / rate,
                    "serial": int(46 + host * 30 / rate), "area": 1, "subarea": 1,
                    "players": 1, "player": actor(10), "controller": deepcopy(missing),
                    "gameover": False, "buttons": [], "portals": [], "bindings": [],
                    "wibbly_managers": 1, "view": [0, 0, 426, 240], "gui": [426, 240],
                    "native": {"smoke_active": True, "floors": 100, "walls": 100,
                               "gen": 0, "floormakers": 0, "generation_screen": False}}
        rows = [snapshot("start", 0), snapshot("authentic-level-start", 70),
                snapshot("fatal-damage-requested", 78)]
        value = {"passed": True, "physical_device_tested": False, "phase": 7, "rate": rate,
                 "accept": accept, "entry_mode": mode, "eligible": eligible, "input_frames": [],
                 "observations": [], "actual_click": None, "stale_press": None, "draw_counts": {},
                 "connection_draws": 0, "denial_draws": 0,
                 "manager_before_death": {"id": 15, "slot": 0, "living": 1, "race": "robot", "x": 100, "y": 100}}
        if eligible:
            rows += [snapshot("natural-controller", 79), snapshot("natural-buttons", 200),
                     snapshot("drawn-before-input", 203), snapshot("after-touch-and-endstep", 206),
                     snapshot("postclick-later-frame", 209), snapshot("postclick-later-frame", 221)]
            for row in rows[3:]:
                row["player"] = actor(20)
                row["controller"] = deepcopy(controller)
            for row in rows[4:6]:
                row["buttons"] = deepcopy(buttons)
            value["stale_press"] = {"host": 180, "blueTime": 90}
            value["draw_counts"] = {"40": 2, "41": 2}
            selected = next(button for button in buttons if button["yes"] is accept)
            for host in (201, 202):
                for button in buttons:
                    value["observations"].append({"kind": "draw", "host": host, "self": button["id"]})
            for index in range(3):
                value["input_frames"].append({"host": 203 + index, "hardware_frame": 300 + index,
                    "frame": 46 + (203 + index) * 30 / rate, "ready": rate == 30 or index != 1,
                    "touch": 4, "button": selected["id"], "pressed": index == 1,
                    "held": index == 1, "released": index != 1, "x": 100, "y": 100, "view": [0, 0]})
            click_host = 204 if rate == 30 else 205
            click = {"kind": "step", "host": click_host, "self": selected["id"], "ready": True,
                     "click": 0, "actor": {**selected, "done": True},
                     "pointer": {"ready": True, "output": {"x": 100, "y": 100, "held": True},
                                 "samples": {"held": rate == 30}}}
            value["actual_click"] = click
            value["observations"].append(click)
            value["observations"] += [{"kind": "end-before", "host": click_host, "self": button["id"],
                                        "actor": {**button, "done": True}} for button in buttons]
            if accept:
                for row in rows[6:]:
                    row["area"], row["subarea"] = 302, 0
                    row["controller"]["drawConnect"] = True
                    row["portals"] = [{"id": 50, "type": 3, "endgame": 30}]
                rows += [snapshot("native-portal-room-handoff", 260), snapshot("accepted", 260 + rate)]
                for row in rows[-2:]:
                    row["area"], row["subarea"], row["player"] = 302, 1, actor(60)
                value["connection_draws"] = 3
            else:
                rows += [snapshot("accepted", 206 + rate)]
                for row in rows[6:]:
                    row.update(players=0, player=deepcopy(missing), controller=deepcopy(missing), gameover=True)
                rows[6]["bindings"] = [{"id": 55, "code": "denybluescreen_draw"}]
                value["observations"] += [{"kind": "deny-binding-draw", "self": 55,
                                           "creator": selected["id"]} for _ in range(2)]
                value["denial_draws"] = 2
        else:
            rows += [snapshot("ineligible-native-gameover", 79), snapshot("accepted", 79 + rate)]
            for row in rows[3:]:
                row.update(players=0, player=deepcopy(missing), gameover=True)
        value.update(snapshots=rows, final=rows[-1], host_frames=rows[-1]["host"])
        return value

    @staticmethod
    def smoke(value):
        lines = ["PASS scheduled Robot fatal damage, auto-created blue YES/NO, raw touch, delayed EndStep and native destination/death lifecycle"]
        for prefix, key in (("SNAPSHOT", "snapshots"), ("ACTOR", "observations"), ("RAW TOUCH", "input_frames")):
            lines += ["BLUESCREEN UI204 " + prefix + " " + json.dumps(row) for row in value[key]]
        if value["stale_press"] is not None:
            lines += ["BLUESCREEN UI204 PREEXISTING HELD TOUCH " + json.dumps(value["stale_press"])]
        lines += ["BLUESCREEN UI204 ACCEPTED " + json.dumps({"rate": value["rate"], "accept": value["accept"],
                   "frames": value["host_frames"], "input": value["input_frames"], "final": value["final"]})]
        return "\n".join(lines)

    def check(self, value, choice="Yes", rate=30, smoke=None):
        name = "frontier-bluescreen-ui204.json"
        (self.directory / name).write_text(json.dumps(value), encoding="utf8")
        artifacts = {name: "synthetic-unit-data"}
        for suffix in ("before", "after"):
            png = "frontier-bluescreen-ui204-" + suffix + ".png"
            (self.directory / png).write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 4 + b"IHDR" +
                                              (426).to_bytes(4, "big") + (240).to_bytes(4, "big"))
            artifacts[png] = "synthetic-unit-data"
        return REVIEW.verify204_identity("FrontierBluescreenUI204" + choice + str(rate) + "Tests",
            self.smoke(value) if smoke is None else smoke, artifacts, self.directory)

    def test_accepts_all_eight_scheduled_semantic_paths(self):
        for choice in ("Yes", "No", "Disabled", "Visited"):
            for rate in (30, 60):
                with self.subTest(choice=choice, rate=rate):
                    self.assertEqual(self.check(self.fixture(choice, rate), choice, rate)["rate"], rate)

    def test_rejects_wrong_case_rate_and_eligibility(self):
        for key, bad in (("rate", 60), ("entry_mode", "visited"), ("eligible", False), ("accept", False)):
            value = self.fixture(); value[key] = bad
            with self.subTest(key=key), self.assertRaises(AssertionError): self.check(value)

    def test_rejects_missing_authentic_manager_and_terrain(self):
        for key in ("living", "race"):
            value = self.fixture(); value["manager_before_death"][key] = 0
            with self.subTest(key=key), self.assertRaises(AssertionError): self.check(value)
        value = self.fixture(); value["snapshots"][1]["native"]["floors"] = 0
        with self.assertRaises(AssertionError): self.check(value)

    def test_rejects_premature_gameover_even_with_successful_destination(self):
        value = self.fixture(); value["snapshots"][3]["gameover"] = True
        with self.assertRaisesRegex(AssertionError, "Premature"): self.check(value)

    def test_rejects_pointer_shortcuts_and_lost_60hz_queued_press(self):
        value = self.fixture(); value["input_frames"][1]["pressed"] = False
        with self.assertRaises(AssertionError): self.check(value)
        value = self.fixture(); value["actual_click"]["click"] = -1
        with self.assertRaises(AssertionError): self.check(value)
        value = self.fixture("Yes", 60); value["actual_click"]["pointer"]["output"]["held"] = False
        with self.assertRaises(AssertionError): self.check(value, rate=60)

    def test_rejects_missing_stale_press_guard_real_draw_and_deferred_cleanup(self):
        value = self.fixture(); value["snapshots"][5]["buttons"][0]["done"] = True
        with self.assertRaises(AssertionError): self.check(value)
        value = self.fixture(); value["observations"] = [row for row in value["observations"] if row["kind"] != "draw"]
        with self.assertRaises(AssertionError): self.check(value)
        value = self.fixture(); value["observations"] = [row for row in value["observations"] if row["kind"] != "end-before"]
        with self.assertRaises(AssertionError): self.check(value)

    def test_rejects_fake_destination_and_missing_real_portal_or_connection_draw(self):
        for native_key in ("floors", "walls"):
            value = self.fixture(); value["final"]["native"][native_key] = 0
            with self.subTest(key=native_key), self.assertRaises(AssertionError): self.check(value)
        value = self.fixture(); value["snapshots"][6]["portals"] = []
        with self.assertRaises(AssertionError): self.check(value)
        value = self.fixture(); value["connection_draws"] = 0
        with self.assertRaises(AssertionError): self.check(value)

    def test_rejects_no_without_denial_draw_or_ordinary_gameover(self):
        value = self.fixture("No"); value["denial_draws"] = 0
        with self.assertRaises(AssertionError): self.check(value, "No")
        value = self.fixture("No"); value["final"]["gameover"] = False
        with self.assertRaises(AssertionError): self.check(value, "No")

    def test_rejects_disabled_or_visited_revival_and_artifact_log_mismatch(self):
        for choice in ("Disabled", "Visited"):
            value = self.fixture(choice); value["final"]["players"] = 1
            with self.subTest(choice=choice), self.assertRaises(AssertionError): self.check(value, choice)
        value = self.fixture(); smoke = self.smoke(value); value["snapshots"][4]["host"] += 1
        with self.assertRaisesRegex(AssertionError, "differs"): self.check(value, smoke=smoke)


class MenuInputOwnershipSemantics(unittest.TestCase):
    """Synthetic temporary boundary data only; never native acceptance evidence."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    @staticmethod
    def fixture(rate=30):
        observations = []
        def observe(label, scenario, phase, host, race=0, owners=0, selection=0, controller=False):
            return {"label": label, "scenario": scenario, "phase": phase, "host": host,
                    "frame": 10 + (host - 1) * 30 / rate, "input_frame": 100 + host - 1,
                    "race": race, "selection": selection, "owners": owners, "menus": 1,
                    "characters": 20, "touch": not controller, "keyboard": False, "gamepad": controller,
                    "direction": {"east": scenario != 1, "west": scenario == 1, "north": False, "south": False}}
        for scenario in range(3):
            host = scenario * 2 * rate + 1
            fresh = observe("real-joystick-fresh-edge", scenario, 1, host, owners=1,
                            race=2 if scenario == 0 else 0)
            observations += [fresh, observe("native-menu-entered-with-stale-edge", scenario, 2, host)]
            observations += [observe("idle", scenario, 2, host + index + 1) for index in range(2 * rate)]
        observations += [observe("controller-before-touch-mode-boundary", 3, 6, 6 * rate + 52,
                                 race=6, selection=6, controller=True),
                         observe("real-joystick-fresh-edge", 3, 7, 7 * rate + 52,
                                 race=6, owners=1, selection=6)]
        observations[-1]["direction"] = {"east": False, "west": False, "north": True, "south": False}
        phases = sum(([1] + [2] * (2 * rate - 1) for _ in range(3)), [])
        phases += [3] * 8 + [4] * 21 + [5] * 21 + [6] * (rate + 1) + [7]
        inputs = [{"phase": phase, "host": index + 1, "frame": 100 + index,
                   "touch": {"held": False, "pressed": False, "released": False, "x": 0, "y": 0},
                   "keyboard": {"held": -1, "pressed": -1, "released": -1},
                   "pad": {"x": 0, "button": -1}}
                  for index, phase in enumerate(phases)]
        for scenario in range(3):
            raw = inputs[scenario * 2 * rate:(scenario + 1) * 2 * rate]
            for index, row in enumerate(raw):
                row["touch"].update(x=100 + (20 if scenario != 1 else -20), y=150,
                    held=index == 0 or (scenario == 1 and index < 10), pressed=index == 0,
                    released=(scenario == 0 and index == 1) or (scenario == 1 and index == 10))
        for phase in (3, 4, 5, 6):
            for index, row in enumerate(item for item in inputs if item["phase"] == phase):
                if phase == 3:
                    row["touch"].update(x=50, y=50, held=index == 0, pressed=index == 0, released=index == 1)
                elif phase == 4:
                    row["keyboard"] = {"held": 39 if 2 <= index <= 6 or 10 <= index <= 14 else -1,
                        "pressed": 39 if index in (2, 10) else -1, "released": 39 if index in (7, 15) else -1}
                elif phase == 5:
                    row["pad"] = {"x": .8 if 2 <= index <= 6 else 0, "button": 1 if 10 <= index <= 14 else -1}
                else:
                    row["pad"] = {"x": .8 if index == 0 else 0, "button": -1}
        inputs[-1]["touch"].update(held=True, pressed=True, x=100, y=150)
        return {"passed": True, "failure": None, "rate": rate, "phase": 8, "scenario": 3,
                "physical_device_tested": False, "os_mouse_dispatch_emulated": True,
                "host_frames": len(inputs) + 8, "source_pointer_checks": 18,
                "inputs": inputs, "observations": observations,
                "transitions": [row for previous, row in zip(observations, observations[1:])
                                if previous["race"] != row["race"]],
                "positive": [{"kind": "raw-touch-native-mouse4", "race": 1},
                             {"kind": "keyboard-native-general", "fresh_edges": 2, "held_repeats": 0, "neutral_repeats": 0},
                             {"kind": "analogue+dpad-native-general", "fresh_edges": 2, "held_repeats": 0, "neutral_repeats": 0},
                             {"kind": "controller-to-touch-mode", "repeats": 0}],
                "options_observations": [{"host": len(inputs) + index + 1, "kh": 0, "kv": 0,
                    "touch": True, "keyboard": False, "gamepad": False, "pointed": 0 if index == 0 else -1}
                    for index in range(7)]}

    @staticmethod
    def smoke(value):
        rate = value["rate"]
        rows, logged = value["observations"], []
        for scenario in range(3):
            group = rows[scenario * (2 + 2 * rate):(scenario + 1) * (2 + 2 * rate)]
            logged += group[:2] + [row for index, row in enumerate(group[2:]) if index % rate == 0]
        logged += rows[-2:]
        return "\n".join(["MENU INPUT204 START rate=" + str(rate),
            *["MENU INPUT204 OBSERVE " + json.dumps(row) for row in logged],
            "PASS FRONTIER INPUT204 real libMenu30/60Hz short press, same-host early/late polls, once-only later source ticks, stale pre-button hold, local hitbox/slot and release: 18",
            "MENU INPUT204 SEPARATE TOUCH OPTIONS OBSERVATION " + json.dumps(value["options_observations"]),
            "MENU INPUT204 ACCEPTED " + json.dumps({"rate": rate, "scenarios": 3,
                "positive": value["positive"], "source_pointer_checks": 18, "physical_device_tested": False,
                "options_reader_input_ownership_checked": True}),
            "PASS scheduled raw JoystickMove owner removal, native menu idle, touch/keyboard/controller/mode positive controls"])

    def check(self, value, rate=30, smoke=None, omit=None):
        name = "frontier-menu-input204.json"
        (self.directory / name).write_text(json.dumps(value), encoding="utf8")
        artifacts = {name: "synthetic-unit-data"}
        for suffix in ("idle-0", "idle-1", "idle-2", "after"):
            png = "frontier-menu-input204-" + suffix + ".png"
            (self.directory / png).write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 4 + b"IHDR" +
                                              (426).to_bytes(4, "big") + (240).to_bytes(4, "big"))
            artifacts[png] = "synthetic-unit-data"
        if omit is not None:
            artifacts.pop(omit)
        return REVIEW.verify204_identity("FrontierMenuInput204" + str(rate) + "Tests",
            self.smoke(value) if smoke is None else smoke, artifacts, self.directory)

    def test_accepts_both_scheduled_rates_with_real_positive_input_shapes(self):
        for rate in (30, 60):
            with self.subTest(rate=rate):
                result = self.check(self.fixture(rate), rate)
                self.assertEqual(result["raw_input_frames"], 7 * rate + 52)
                self.assertIn("OS Mouse4 delivery emulated", result["scope"])

    def test_rejects_wrong_identity_completion_and_physical_claim(self):
        for key, bad in (("passed", False), ("failure", "native failure"), ("rate", 60), ("phase", 9),
                         ("scenario", 2), ("physical_device_tested", True), ("os_mouse_dispatch_emulated", False)):
            value = self.fixture(); smoke = self.smoke(value); value[key] = bad
            with self.subTest(key=key), self.assertRaises(AssertionError): self.check(value, smoke=smoke)

    def test_rejects_missing_artifact_and_any_native_screenshot(self):
        for name in ("frontier-menu-input204.json", "frontier-menu-input204-idle-0.png",
                     "frontier-menu-input204-idle-1.png", "frontier-menu-input204-idle-2.png",
                     "frontier-menu-input204-after.png"):
            with self.subTest(name=name), self.assertRaisesRegex(AssertionError, "Missing hash-bound"):
                self.check(self.fixture(), omit=name)

    def test_rejects_missing_real_owner_removal_and_touch_menu_population(self):
        for index, key, bad in ((0, "owners", 0), (1, "owners", 1), (1, "menus", 0),
                                (1, "characters", 1), (2, "touch", False), (2, "keyboard", True)):
            value = self.fixture(); value["observations"][index][key] = bad
            with self.subTest(index=index, key=key), self.assertRaises(AssertionError): self.check(value)

    def test_rejects_idle_drift_missing_stale_edge_or_simulation_progress(self):
        for key, bad in (("race", 7), ("selection", 7), ("owners", 1), ("frame", 10)):
            value = self.fixture(); value["observations"][12][key] = bad
            with self.subTest(key=key), self.assertRaises(AssertionError): self.check(value)
        value = self.fixture(); value["observations"][12]["direction"]["east"] = False
        with self.assertRaises(AssertionError): self.check(value)
        value = self.fixture(); value["observations"].pop(12)
        with self.assertRaises(AssertionError): self.check(value)

    def test_rejects_positive_summary_without_actual_raw_keyboard_pad_and_touch_edges(self):
        changes = ((3, 0, "touch", "pressed", False), (3, 1, "touch", "released", False),
                   (3, 0, "touch", "x", 900), (4, 2, "keyboard", "pressed", -1),
                   (4, 3, "keyboard", "pressed", 39), (4, 7, "keyboard", "released", -1),
                   (5, 2, "pad", "x", 0), (5, 10, "pad", "button", -1),
                   (6, 0, "pad", "x", 0), (6, 1, "pad", "x", .8))
        for phase, index, part, key, bad in changes:
            value = self.fixture(); row = [row for row in value["inputs"] if row["phase"] == phase][index]
            row[part][key] = bad
            with self.subTest(phase=phase, index=index, key=key), self.assertRaises(AssertionError): self.check(value)

    def test_rejects_replayed_touch_release_loss_and_missing_raw_frames(self):
        for index, key, bad in ((1, "released", False), (10, "pressed", True),
                                (61, "held", False), (70, "released", False), (121, "held", True)):
            value = self.fixture(); value["inputs"][index]["touch"][key] = bad
            with self.subTest(index=index, key=key), self.assertRaises(AssertionError): self.check(value)
        value = self.fixture(); value["inputs"].pop(10)
        with self.assertRaises(AssertionError): self.check(value)

    def test_rejects_missing_positive_control_or_remaining_repeat(self):
        for index, key, bad in ((0, "race", 0), (1, "fresh_edges", 1), (1, "held_repeats", 1),
                                (2, "neutral_repeats", 1), (3, "repeats", 1)):
            value = self.fixture(); value["positive"][index][key] = bad
            with self.subTest(index=index, key=key), self.assertRaises(AssertionError): self.check(value)

    def test_rejects_options_direction_leak_and_wrong_input_mode_but_allows_hover(self):
        value = self.fixture()
        for index, row in enumerate(value["options_observations"]): row["pointed"] = index % 3
        self.check(value)
        for key, bad in (("kh", 1), ("kv", -1), ("touch", False), ("gamepad", True)):
            value = self.fixture(); value["options_observations"][2][key] = bad
            with self.subTest(key=key), self.assertRaises(AssertionError): self.check(value)

    def test_rejects_artifact_log_history_and_pointer_binding_changes(self):
        value = self.fixture(); smoke = self.smoke(value); value["options_observations"][0]["pointed"] = 1
        with self.assertRaises(AssertionError): self.check(value, smoke=smoke)
        value = self.fixture(); value["transitions"] = []
        with self.assertRaises(AssertionError): self.check(value)
        value = self.fixture(); value["source_pointer_checks"] = 17
        with self.assertRaises(AssertionError): self.check(value)
        value = self.fixture(); smoke = self.smoke(value).replace("PASS scheduled raw", "OMITTED scheduled raw")
        with self.assertRaises(AssertionError): self.check(value, smoke=smoke)

    def test_requires_both_rates_in_explicit_current_semantic_selection(self):
        for case in ("FrontierMenuInput20430Tests", "FrontierMenuInput20460Tests"):
            self.assertIn(case, REVIEW.CURRENT204_CASES)
            path = self.directory / "selection.json"
            path.write_text(json.dumps({"version": "2.0.4", "internal": 100,
                "cases": [name for name in REVIEW.FINAL_CASES if name != case]}), encoding="utf8")
            with self.subTest(case=case), patch.object(REVIEW, "CASE_SELECTION", path), self.assertRaisesRegex(AssertionError, "mandatory"):
                REVIEW.load_cases()


class CurrentSemantics(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def check_artifact(self, case, name, value, smoke):
        (self.directory / name).write_text(json.dumps(value), encoding="utf8")
        return REVIEW.verify204_identity(case, smoke, {name: "hash bound by outer receipt gate"}, self.directory)

    @staticmethod
    def possession():
        rows = []
        for rate in (30, 60):
            for kind in ("native-host-death", "native-car-pickup", "native-parrot-charm", "living-host-control"):
                row = {"rate": rate, "kind": kind, "source_constructor": "Frontier_Events::HauntedCity_create",
                       "attempts": 1, "initial": {"id": 100001, "hp": 17, "alpha": 0,
                           "possessing": True, "possess_target_exists": True, "mask": 5,
                           "possess_target": 100002, "possess_target_hp": 16.8,
                           "possess_target_object": "SnowBot" if kind == "native-car-pickup" else "Wolf",
                           "possess_target_possessed": True, "possess_target_possessor": 100001,
                           "possess_target_team": 1},
                       "detached": kind != "living-host-control", "restored_hittable": kind != "living-host-control",
                       "samples": [{"source_ticks": 60}], "host_action": {"collision_dispatched_by_engine": True}}
                row["host_type"] = row["initial"]["possess_target_object"]
                row["before_action"] = deepcopy(row["initial"])
                if kind == "living-host-control":
                    row.update(host_action={"unchanged_living_host": True},
                               ghost_after={"possessing": True, "alpha": 0})
                else:
                    row.update(detached_at=1,
                               restored={"id": 100001, "alpha": 1, "possessing": False, "mask": 6},
                               actual_bullet_collision={"target": 100001, "damage": 3, "bullet_consumed": True},
                               guardian_hit={"target": 100001, "damage": 15, "punches": 1})
                    if kind == "native-parrot-charm":
                        row["host_action"] = {"native_charm": True}
                rows.append(row)
        return {"reported_area": "City 5-1", "loops": 1, "screenshot_hp": 17,
                "regression": True, "physical_device_tested": False, "cases": rows}

    @staticmethod
    def possession_log(value):
        return "\n".join("FRONTIER ENEMY POSSESSION ACCEPTED " + json.dumps(row) for row in value["cases"])

    def test_possession_requires_eight_real_observations_and_records_scope(self):
        value = self.possession()
        actual = self.check_artifact("FrontierEnemyPossessionTests", "frontier-enemy-possession-diagnostic.json",
                                     value, self.possession_log(value))
        self.assertEqual(len(actual["cases"]), 8)
        self.assertFalse(actual["physical_device_tested"])
        self.assertIn("not physical phone acceptance", actual["scope"])

    def test_possession_accepts_actual_vm_numeric_exists_with_live_reciprocal_host(self):
        value = self.possession()
        # Exact relevant fields from the immutable full64 first native record;
        # this remains temporary unit boundary data, not native evidence.
        row = value["cases"][0]
        row["initial"].update(id=100970.0, possess_target=100949.0,
            possess_target_exists=1.0, possess_target_hp=16.8,
            possess_target_object="Wolf", possess_target_possessed=True,
            possess_target_possessor=100970.0, possess_target_team=1.0)
        row["before_action"] = deepcopy(row["initial"])
        row["restored"]["id"] = row["actual_bullet_collision"]["target"] = row["guardian_hit"]["target"] = 100970.0
        self.check_artifact("FrontierEnemyPossessionTests", "frontier-enemy-possession-diagnostic.json",
                            value, self.possession_log(value))
        for accepted in (True, 1, 1.0):
            self.assertTrue(REVIEW.native_true(accepted, "native true encoding"))

    def test_possession_rejects_noncanonical_exists_encoding(self):
        for invalid in (False, 0, 0.0, -1, 2, "1", "true", None, [], {}, float("nan"), float("inf")):
            value = self.possession(); value["cases"][0]["initial"]["possess_target_exists"] = invalid
            with self.subTest(value=invalid), self.assertRaises(AssertionError):
                self.check_artifact("FrontierEnemyPossessionTests", "frontier-enemy-possession-diagnostic.json",
                                    value, self.possession_log(value))

    def test_possession_rejects_missing_hp_wrong_pair_or_lost_ownership_at_either_boundary(self):
        for boundary in ("initial", "before_action"):
            for key, invalid in (("possess_target_exists", 0), ("possess_target_hp", 0),
                                 ("possess_target", 100003), ("possess_target_possessor", 100003),
                                 ("possess_target_possessed", False), ("possess_target_object", "Bandit"),
                                 ("possess_target_team", 2)):
                value = self.possession(); value["cases"][0][boundary][key] = invalid
                with self.subTest(boundary=boundary, key=key), self.assertRaises(AssertionError):
                    self.check_artifact("FrontierEnemyPossessionTests", "frontier-enemy-possession-diagnostic.json",
                                        value, self.possession_log(value))

    def test_possession_rejects_missing_rate_wrong_damage_and_changed_control(self):
        for field in ("missing-rate", "bullet", "guardian", "late", "control", "artifact-log"):
            value = self.possession()
            smoke = None
            if field == "missing-rate":
                value["cases"] = value["cases"][:4]
            elif field == "bullet":
                value["cases"][0]["actual_bullet_collision"]["damage"] = 0
            elif field == "guardian":
                value["cases"][0]["guardian_hit"]["damage"] = 0
            elif field == "late":
                value["cases"][0]["detached_at"] = 10
            elif field == "control":
                value["cases"][3]["ghost_after"]["alpha"] = 1
            else:
                smoke = self.possession_log(value)
                value["cases"][0]["attempts"] = 2
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.check_artifact("FrontierEnemyPossessionTests", "frontier-enemy-possession-diagnostic.json",
                                    value, smoke if smoke is not None else self.possession_log(value))

    def test_input_requires_current_touch_controller_and_hardware_limit_marker(self):
        summary = ("PASS FRONTIER INPUT204 continuous actual touch double taps 30/60Hz; native+packed wall mask; "
                   "nonzero controller/reversal/D-pad/right-stick/confirm/hot-plug; physical Android/iOS controller untested")
        result = REVIEW.verify204_identity("FrontierPromptTests", summary, {}, self.directory)
        self.assertFalse(result["physical_device_tested"])
        for fragment in ("actual touch double taps 30/60Hz", "native+packed wall mask", "physical Android/iOS controller untested"):
            with self.subTest(fragment=fragment), self.assertRaises(AssertionError):
                REVIEW.verify204_identity("FrontierPromptTests", summary.replace(fragment, "omitted"), {}, self.directory)

    @staticmethod
    def biome():
        rows = []
        for index, (rate, wall) in enumerate(((30, True), (60, True), (30, False), (60, False))):
            actor = 110000 + index * 100
            awake = {"exists": True, "id": actor, "object": "JungleAssassin", "hp": 16,
                     "visible": True, "alpha": 1, "mask": 260 if wall else 12,
                     "depth": -9 if wall else 0, "in_wall": wall, "on_floor": not wall,
                     "top": actor + 1 if wall else -4}
            dormant = {**awake, "id": actor - 1, "object": "JungleAssassinHide",
                       "top": actor - 2 if wall else -4}
            landed = {**awake, "mask": 12, "depth": 0, "in_wall": False, "on_floor": True, "top": -4}
            nonlethal = {"target": actor, "bullet": actor + 2, "damage": 3,
                        "before": 16, "after": 13, "phase": 3, "consumed": True}
            lethal = {"target": actor, "bullet": actor + 3, "damage": 113,
                      "before": 13, "after": -100, "phase": 5, "consumed": True}
            rows.append({"rate": rate, "wall": wall, "dormant": dormant, "awake": awake,
                         "samples": [awake] if wall else [], "landed": landed,
                         "nonlethal": nonlethal, "lethal": lethal, "death_ticks": 150,
                         "portal": {"id": actor + 4, "type": 1, "x": 943064, "y": 943064, "ticks": 151}})
        return {"physical_device_tested": False, "cases": rows}

    @staticmethod
    def biome_log(value):
        lines = []
        for row in value["cases"]:
            start = {"rate": row["rate"], "wall": row["wall"], "dormant": row["dormant"], "samples": []}
            lines.append("BIOME CLEARANCE204 ACCEPTANCE BEGIN " + json.dumps(start))
            for shot in (row["nonlethal"], row["lethal"]):
                lines.append("BIOME CLEARANCE204 ACTUAL BULLET " + json.dumps(shot))
            lines.append("BIOME CLEARANCE204 ACCEPTED " + json.dumps(row))
        return "\n".join(lines)

    def check_biome(self, value, smoke=None):
        return self.check_artifact("FrontierBiomeClearance204AcceptanceTests",
                                   "frontier-biome-clearance204-acceptance.json", value,
                                   self.biome_log(value) if smoke is None else smoke)

    def test_biome_accepts_four_independent_native_wall_ground_combat_exits(self):
        value = self.biome()
        for row in value["cases"]:
            row["landed"].update(visible=1.0, in_wall=0.0, on_floor=1.0)
        result = self.check_biome(value)
        self.assertEqual(len(result["cases"]), 4)
        self.assertIn("not physical phone or every hidden-enemy acceptance", result["scope"])

    def test_biome_rejects_missing_control_and_hidden_or_unrestored_landing(self):
        for field in ("missing", "rate", "hidden", "wall", "floor", "owner", "mask", "depth"):
            value = self.biome()
            landed = value["cases"][0]["landed"]
            if field == "missing":
                value["cases"].pop()
            elif field == "rate":
                value["cases"][0]["rate"] = 60
            elif field == "hidden":
                landed["alpha"] = 0
            elif field == "wall":
                landed["in_wall"] = True
            elif field == "floor":
                landed["on_floor"] = False
            elif field == "owner":
                landed["top"] = value["cases"][0]["awake"]["top"]
            else:
                landed[field] = value["cases"][0]["awake"][field]
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.check_biome(value)

    def test_biome_rejects_missing_real_damage_death_or_original_exit(self):
        for field in ("damage", "target", "consumed", "survives", "portal-type", "portal-delay", "scene-reuse"):
            value = self.biome()
            row = value["cases"][0]
            if field == "damage":
                row["nonlethal"]["after"] = 16
            elif field == "target":
                row["nonlethal"]["target"] += 1
            elif field == "consumed":
                row["lethal"]["consumed"] = False
            elif field == "survives":
                row["lethal"]["after"] = 1
            elif field == "portal-type":
                row["portal"]["type"] = 2
            elif field == "portal-delay":
                row["portal"]["ticks"] = row["death_ticks"] + 180
            else:
                value["cases"][1] = {**deepcopy(row), "rate": 60}
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.check_biome(value)

    def test_biome_rejects_artifact_or_native_lifecycle_log_mismatch(self):
        for field in ("artifact", "begin", "shot", "completed"):
            value = self.biome()
            smoke = self.biome_log(value)
            if field == "artifact":
                value["cases"][0]["portal"]["x"] += 1
            else:
                prefix = {"begin": "BIOME CLEARANCE204 ACCEPTANCE BEGIN ",
                          "shot": "BIOME CLEARANCE204 ACTUAL BULLET ",
                          "completed": "BIOME CLEARANCE204 ACCEPTED "}[field]
                smoke = smoke.replace(prefix, "OMITTED ", 1)
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.check_biome(value, smoke)

    @staticmethod
    def drone():
        benchmarks = []
        for rate in (30, 60):
            for shock in (False, True):
                old = {"rate": rate, "shock": shock, "reference": True, "projectiles": 512,
                       "hostile_intercepted": 320, "allied_neutral_typ0_passed": 192,
                       "query_checks": 16, "query_iterations": 96, "query_us": 1000, "missing_typ_ignored": True,
                       "callback_us": 2000, "null_effects": 320, "sound_requests": 320,
                       "native_rng_next": [.1, .2, .3, .4, .5], "source_rng_next": [.2, .3, .4, .5, .6]}
                new = {**deepcopy(old), "reference": False, "query_us": 500, "callback_us": 1000,
                       "null_effects": 32, "sound_requests": 1}
                benchmarks.append({"reference": old, "optimized": new, "query_ratio": .5, "callback_ratio": .5})
        moving = [{"rate": rate, "reference": reference, "host_frames": 16 * rate / 30,
                   "source_ticks": 16, "projectiles": 512, "hostile_intercepted": 256,
                   "allied_neutral_passed": 256, "elapsed_us": 1000}
                  for rate in (30, 60) for reference in (True, False)]
        destroyed = [{"rate": rate, "shock": shock, "projectile": projectile, "reference": reference,
                      "native_explosions": {"Grenade": 1, "StickyGrenade": 3, "FRCustomProjectile": 0}[projectile],
                      "source_destroy_calls": int(projectile == "FRCustomProjectile"), "source_destroy_id_matches": True}
                     for rate in (30, 60) for shock in (False, True)
                     for projectile in ("Grenade", "StickyGrenade", "FRCustomProjectile") for reference in (True, False)]
        return {"physical_device_tested": False, "production_rules_unchanged": True,
                "benchmarks": benchmarks, "natural_collision": moving, "destroy_callbacks": destroyed}

    @staticmethod
    def drone_log(value):
        return ("NTUF HYPERION real source drone/shock: native projectile/grenade callbacks, current-team reflection, "
                "player/allied explosives/lasers and hostile pursuit PASS\n" +
                "PASS NTUF Hyperion dense real native collision at30/60Hz, live nearest parity and both RNG ladders " +
                json.dumps(value["benchmarks"]) + "\nFRONTIER DRONE204 ACCEPTED " + json.dumps(value))

    def check_drone(self, value, smoke=None):
        return self.check_artifact("FrontierDronePerformance204Tests", "frontier-drone-performance204.json", value,
                                   self.drone_log(value) if smoke is None else smoke)

    def test_drone_accepts_dense_source_parity_and_real_moving_native_collisions(self):
        result = self.check_drone(self.drone())
        self.assertEqual(len(result["benchmarks"]), 4)
        self.assertIn("no universal FPS or phone hardware acceptance", result["scope"])

    def test_drone_rejects_changed_rules_rng_allegiance_or_cosmetic_budget(self):
        for field in ("rules", "native-rng", "source-rng", "hostile", "friendly", "queries", "missing-typ", "effects", "sounds", "ratio"):
            value = self.drone()
            row = value["benchmarks"][0]
            new = row["optimized"]
            if field == "rules":
                value["production_rules_unchanged"] = False
            elif field.endswith("rng"):
                new[field.replace("-", "_") + "_next"][0] = .99
            elif field == "hostile":
                new["hostile_intercepted"] = 319
            elif field == "friendly":
                new["allied_neutral_typ0_passed"] = 191
            elif field == "queries":
                new["query_checks"] = 0
            elif field == "missing-typ":
                new["missing_typ_ignored"] = False
            elif field == "effects":
                new["null_effects"] = 0
            elif field == "sounds":
                new["sound_requests"] = 320
            else:
                row["callback_ratio"] = .1
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.check_drone(value)

    def test_drone_rejects_missing_moving_control_wrong_source_progress_or_output_mismatch(self):
        for field in ("missing", "frames", "ticks", "allied", "artifact", "matrix"):
            value = self.drone()
            smoke = None
            if field == "missing":
                value["natural_collision"].pop()
            elif field == "frames":
                value["natural_collision"][2]["host_frames"] = 16
            elif field == "ticks":
                value["natural_collision"][0]["source_ticks"] = 8
            elif field == "allied":
                value["natural_collision"][1]["allied_neutral_passed"] = 255
            elif field == "artifact":
                smoke = self.drone_log(value)
                value["natural_collision"][1]["elapsed_us"] = 2000
            else:
                smoke = self.drone_log(value).replace("hostile pursuit PASS", "hostile pursuit OMITTED")
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.check_drone(value, smoke)

    def test_drone_rejects_lost_or_duplicate_native_source_destroy_callbacks(self):
        for field in ("missing", "grenade", "sticky", "source-calls", "source-owner"):
            value = self.drone()
            destroyed = value["destroy_callbacks"]
            if field == "missing":
                destroyed.pop()
            elif field == "grenade":
                destroyed[1]["native_explosions"] = 0
            elif field == "sticky":
                destroyed[3]["native_explosions"] = 1
            elif field == "source-calls":
                destroyed[5]["source_destroy_calls"] = 2
            else:
                destroyed[5]["source_destroy_id_matches"] = False
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.check_drone(value)

    @staticmethod
    def biome_maps():
        rows = []
        for loops in (0, 1, 3):
            for area, subarea, seed, rate in ((1, 2, 100005, 30), (1, 2, 100006, 60),
                                             (105, 1, 204071, 30), (105, 1, 204086, 60)):
                actor = 200000 + len(rows) * 100
                pipe = actor + 1
                initial = {"ticks": 0, "enemies": 1, "actors": [{"id": actor, "object": "Bandit"}],
                           "big_pipes": [{"id": pipe}], "wall_crates": []}
                hits = [{"bullet": actor + 2, "requested": actor, "target": actor, "damage": 116,
                         "ticks": 15, "team": 2, "consumed": True, "hp": 16, "after": -100, "object": "Bandit"},
                        {"bullet": actor + 3, "requested": pipe, "target": pipe, "damage": 210,
                         "ticks": 15, "team": 2, "consumed": True, "hp": 110, "after": -100, "object": "NTTEFullBigPipe"}]
                rows.append({"area": area, "subarea": subarea, "loops": loops, "seed": seed, "rate": rate,
                             "result": "passed", "floors": 256, "initial_enemies": 1, "initial_pipes": 1,
                             "baseline_ids": [100001, 100002], "baseline_skills": [], "births": [], "lifecycle": [], "approaches": [],
                             "samples": [initial], "hits": hits, "test_bullets": 2, "crate_attacks": [],
                             "portal": {"id": actor + 4, "type": 1, "x": 10000, "y": 10000, "ticks": 30},
                             "final": {"ticks": 30, "enemies": 0, "clear_check": False, "portals": 1,
                                       "big_pipes": [], "dormant": [], "pending_police": 0, "wall_crates": []}})
        row = rows[-1]
        actor = row["samples"][0]["actors"][0]["id"]
        walls = [actor + offset for offset in (11, 12, 13, 14)]
        row["samples"][0]["actors"][0]["object"] = row["hits"][0]["object"] = "Mimic"
        row["samples"][0]["wall_crates"] = [{"id": actor + 10, "x": 10000, "y": 10000,
            "loot": actor, "loot_exists": True, "loot_object": "Mimic",
            "walls": [{"id": identity, "exists": True, "object": "Wall"} for identity in walls]}]
        row["crate_attacks"] = [{"ticks": 15, "crate": actor + 10, "loot": actor,
            "loot_object": "Mimic", "loot_hp": 16, "loot_enemy": True, "loot_team": 1,
            "walls": walls, "attack": actor + 15, "object": "Explosion", "damage": 5, "team": 2,
            "creator": 100003, "creator_object": "Player", "x": 10000, "y": 10000, "mask": 20}]
        return {"passed": True, "physical_device_tested": False, "cases": rows}

    @staticmethod
    def biome_maps_log(value):
        fields = ("area", "subarea", "loops", "seed", "rate")
        lines = []
        for row in value["cases"]:
            lines.append("BIOME CLEARANCE204 MAP BEGIN " + json.dumps({field: row[field] for field in fields}))
            lines.append("BIOME CLEARANCE204 MAP ACCEPTED " + json.dumps(row))
        return "\n".join(lines)

    def check_biome_maps(self, value, smoke=None):
        return self.check_artifact("FrontierBiomeClearance204MapTests", "frontier-biome-clearance204-maps.json", value,
                                   self.biome_maps_log(value) if smoke is None else smoke)

    def test_biome_maps_accept_twelve_populated_profiles_with_real_spawner_combat(self):
        result = self.check_biome_maps(self.biome_maps())
        self.assertEqual(result["actual_bigpipe_combat_deaths"], 12)
        self.assertEqual(result["actual_hostile_crate_explosions"], 1)
        self.assertIn("not every seed or physical phone acceptance", result["scope"])

    def test_biome_maps_bind_default_crate_explosions_to_hostile_loot_and_native_wall_opening(self):
        for field in ("missing", "object", "damage", "team", "creator", "creator_object", "loot_enemy",
                      "loot_team", "loot", "wall", "position", "ownership", "observed-hostile",
                      "still-closed", "duplicate", "late", "baseline", "artifact-log"):
            value = self.biome_maps()
            row = value["cases"][-1]
            attack = row["crate_attacks"][0]
            smoke = None
            if field == "missing":
                row["crate_attacks"] = []
            elif field == "object":
                attack["object"] = "SmallExplosion"
            elif field in ("damage", "team", "creator"):
                attack[field] = 0
            elif field == "creator_object":
                attack[field] = "Bandit"
            elif field == "loot_enemy":
                attack[field] = False
            elif field == "loot_team":
                attack[field] = 2
            elif field == "loot":
                attack[field] += 1
            elif field == "wall":
                attack["walls"][0] += 100
            elif field == "position":
                attack["x"] += 2.0001
            elif field == "ownership":
                row["samples"][0]["wall_crates"] = []
            elif field == "observed-hostile":
                row["samples"][0]["actors"][0]["object"] = "Bandit"
            elif field == "still-closed":
                row["final"]["wall_crates"] = deepcopy(row["samples"][0]["wall_crates"])
            elif field == "duplicate":
                row["crate_attacks"].append(deepcopy(attack))
            elif field == "late":
                attack["ticks"] = 31
            elif field == "baseline":
                row["baseline_ids"].append(attack["crate"])
            else:
                smoke = self.biome_maps_log(value)
                attack["loot_hp"] += 1
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.check_biome_maps(value, smoke)

    def test_biome_crate_blast_coordinates_accept_only_finite_native_two_pixel_jitter(self):
        for dx, dy in ((-2, -2), (-2, 2), (2, -2), (2, 2), (-0.919921875, 1.5234375)):
            value = self.biome_maps()
            attack = value["cases"][-1]["crate_attacks"][0]
            attack["x"] += dx
            attack["y"] += dy
            with self.subTest(dx=dx, dy=dy):
                self.assertEqual(self.check_biome_maps(value)["actual_hostile_crate_explosions"], 1)
        for axis in ("x", "y"):
            for invalid in (9997.9999, 10002.0001, float("inf"), float("-inf"), float("nan"), True):
                value = self.biome_maps()
                value["cases"][-1]["crate_attacks"][0][axis] = invalid
                with self.subTest(axis=axis, invalid=invalid), self.assertRaises(AssertionError):
                    self.check_biome_maps(value)

    def test_biome_maps_accept_scheduled_crate_wall_cleanup_without_requiring_loot_bullet_death(self):
        value = self.biome_maps()
        row = value["cases"][-1]
        crate = deepcopy(row["samples"][0]["wall_crates"][0])
        for wall in crate["walls"]:
            wall["exists"] = 0.0
        row["final"]["wall_crates"] = [crate]
        row["hits"][0].update(requested=300000, target=300000, object="Bandit")
        self.assertEqual(self.check_biome_maps(value)["actual_hostile_crate_explosions"], 1)

    def test_biome_maps_preserve_original_nonblocking_neutral_and_dormant_prop_semantics(self):
        value = self.biome_maps()
        for row in value["cases"]:
            row["hits"].pop()
            row["final"].update(big_pipes=row["samples"][0]["big_pipes"], dormant=[{"id": 50}], enemies=1, pending_police=1)
        result = self.check_biome_maps(value)
        self.assertEqual(result["actual_bigpipe_combat_deaths"], 0)
        self.assertEqual(result["initial_bigpipe_instances"], 12)

    def test_biome_maps_reject_missing_loop_profiles_parked_actors_and_no_real_enemy_damage(self):
        for field in ("profile", "baseline", "enemy-damage", "no-pipes"):
            value = self.biome_maps()
            row = value["cases"][0]
            if field == "profile":
                row["loops"] = 2
            elif field == "baseline":
                row["baseline_ids"].append(row["samples"][0]["actors"][0]["id"])
            elif field == "enemy-damage":
                row["hits"][0]["after"] = 16
            else:
                for item in value["cases"]:
                    item["samples"][0]["big_pipes"] = []
                    item["initial_pipes"] = 0
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.check_biome_maps(value)

    def test_biome_maps_reject_remaining_blockers_wrong_exit_or_changed_observations(self):
        for field in ("clear", "portal", "late", "artifact", "failed-log"):
            value = self.biome_maps()
            row = value["cases"][0]
            smoke = None
            if field == "clear":
                row["final"]["clear_check"] = True
            elif field == "portal":
                row["portal"]["type"] = 2
            elif field == "late":
                row["portal"]["ticks"] = row["final"]["ticks"] = 901
            elif field == "artifact":
                smoke = self.biome_maps_log(value)
                row["portal"]["x"] += 1
            else:
                smoke = self.biome_maps_log(value) + "\nBIOME CLEARANCE204 MAP FAILED {}"
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.check_biome_maps(value, smoke)

    def test_selection_accepts_added_case_without_frozen_count(self):
        value = {"version": "2.0.4", "internal": 100, "cases": list(REVIEW.FINAL_CASES) + ["AdditionalReviewedCase"]}
        path = self.directory / "selection.json"
        path.write_text(json.dumps(value), encoding="utf8")
        with patch.object(REVIEW, "CASE_SELECTION", path):
            self.assertEqual(REVIEW.load_cases(), tuple(value["cases"]))
            value["cases"].remove("FrontierEnemyPossessionTests")
            path.write_text(json.dumps(value), encoding="utf8")
            with self.assertRaisesRegex(AssertionError, "mandatory"):
                REVIEW.load_cases()

    def test_selection_requires_clearance_and_native_world_generation_regressions(self):
        for case in ("FrontierBiomeClearance204AcceptanceTests", "FrontierDronePerformance204Tests", "FrontierBiomeClearance204MapTests", "DesertLevelNativeTests", "JungleLevelNativeTests",
                     "WorldFinalizeNativeTests", "WorldCompletionNativeTests"):
            value = {"version": "2.0.4", "internal": 100, "cases": [name for name in REVIEW.FINAL_CASES if name != case]}
            path = self.directory / "selection.json"
            path.write_text(json.dumps(value), encoding="utf8")
            with self.subTest(case=case), patch.object(REVIEW, "CASE_SELECTION", path), self.assertRaisesRegex(AssertionError, "mandatory"):
                REVIEW.load_cases()

    def test_selection_requires_each_authentic_bluescreen_choice_and_rate_case(self):
        cases = {"FrontierBluescreenUI204Yes30Tests", "FrontierBluescreenUI204Yes60Tests",
                 "FrontierBluescreenUI204No30Tests", "FrontierBluescreenUI204No60Tests",
                 "FrontierBluescreenUI204Disabled30Tests", "FrontierBluescreenUI204Disabled60Tests",
                 "FrontierBluescreenUI204Visited30Tests", "FrontierBluescreenUI204Visited60Tests"}
        self.assertLessEqual(cases, REVIEW.CURRENT204_CASES)
        self.assertLessEqual(cases, REVIEW.REQUIRED204_CASES)
        for case in cases:
            value = {"version": "2.0.4", "internal": 100,
                     "cases": [name for name in REVIEW.FINAL_CASES if name != case]}
            path = self.directory / "selection.json"
            path.write_text(json.dumps(value), encoding="utf8")
            with self.subTest(case=case), patch.object(REVIEW, "CASE_SELECTION", path), \
                    self.assertRaisesRegex(AssertionError, "mandatory"):
                REVIEW.load_cases()

    @staticmethod
    def performance():
        areas = [1, 2, 3, 4, 5, 6, 7, 301, 302, 303, 304, 305, 306, 1, 2]
        return {"physical_device_tested": False,
                "rows": [{"scene": {"rate": 30 if index % 2 else 60, "area": area},
                          "source_ticks": 120, "actor_ticks": 120, "simulation_seconds": 4,
                          "seconds": 5, "simulation_per_second": .8,
                          "floors": 21, "walls": 1, "invisible_walls": 0, "enemies": 1}
                         for index, area in enumerate(areas)]}

    @staticmethod
    def performance_log(value):
        return "\n".join("FRONTIER PERFORMANCE RESULT " + json.dumps(row) for row in value["rows"])

    def test_performance_records_measured_progress_without_fps_claim(self):
        value = self.performance()
        result = self.check_artifact("FrontierPerformanceTests", "frontier-performance.json", value, self.performance_log(value))
        self.assertEqual(len(result["rows"]), 15)
        self.assertIn("no universal60FPS", result["scope"])

    def test_performance_rejects_complete_pass_logs_without_its_hash_bound_artifact(self):
        value = self.performance()
        with self.assertRaisesRegex(AssertionError, "Missing hash-bound native artifact"):
            REVIEW.verify204_identity("FrontierPerformanceTests", self.performance_log(value), {}, self.directory)

    def test_performance_rejects_wrong_simulation_missing_population_and_log_mismatch(self):
        for field in ("source_ticks", "floors", "enemies", "simulation_per_second", "artifact-log"):
            value = self.performance()
            smoke = None
            if field == "artifact-log":
                smoke = self.performance_log(value)
                value["rows"][0]["scene"]["rate"] = 30
            else:
                value["rows"][0][field] = 0
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.check_artifact("FrontierPerformanceTests", "frontier-performance.json", value,
                                    smoke if smoke is not None else self.performance_log(value))


if __name__ == "__main__":
    unittest.main()
