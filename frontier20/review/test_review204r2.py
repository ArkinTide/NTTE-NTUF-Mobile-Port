"""Temporary/inert checks for same-version build102 evidence and isolation."""
from contextlib import redirect_stdout
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
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


class Revision204Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.delivery = load('revision204r2_delivery_guard', 'tools/release204r2_delivery.py')
        cls.review = load('revision204r2_review_guard', 'review/verify_204r2_repairs.py')
        cls.capture = load('revision204r2_capture_guard', 'review/capture204r2_python.py')
        cls.packages = load('revision204r2_package_guard', 'review/inspect_release204r2_packages.py')
        cls.font = load('revision204r2_font_guard', 'review/verify_release204r2_debug_font.py')

    def test_filenames_and_writable_root_keep_published_bytes_separate(self):
        tool = self.delivery
        self.assertEqual(tool.INTERNAL, 102)
        self.assertEqual(tool.DISPLAY_VERSION, '2.0.4')
        self.assertEqual(tool.MOBILE.name, 'mobile-release204r2-20261108')
        self.assertEqual(tool.package_path('Android').name, 'NuclearThrone.NTTE-NTUF-Android-2.0.4-build102.apk')
        self.assertEqual(tool.package_path('iOS').name, 'NuclearThrone.NTTE-NTUF-iOS-2.0.4-build102.ipa')
        with self.assertRaisesRegex(AssertionError, 'escaped'):
            tool.local(ROOT / 'mobile-release204-20261108/native-acceptance.json')

    def test_plan_reads_only_and_cannot_enter_build_or_gate(self):
        tool = self.delivery
        output = io.StringIO()
        with patch.object(sys, 'argv', ['release204r2_delivery.py', 'plan']), \
                patch.object(tool, 'gate', side_effect=AssertionError('unexpected gate')), \
                patch.object(tool, 'run', side_effect=AssertionError('unexpected process')), \
                redirect_stdout(output):
            tool.main()
        record = json.loads(output.getvalue())
        self.assertEqual((record['version'], record['internal']), ('2.0.4', 102))
        self.assertFalse(record['executes_builds_in_plan'])
        self.assertFalse(record['promotes_or_publishes'])

    def test_revision_selection_retains_all_published_cases_and_new_case(self):
        old = json.loads((ROOT / 'review/release204-cases.json').read_text())['cases']
        current = self.delivery.FINAL_CASES
        self.assertEqual(tuple(current), tuple(['FrontierQuestPortal204Tests', 'FrontierBossArt204Tests', 'FrontierLoadoutArt204Tests', 'FrontierMutationPool204Tests', 'FrontierRedConnectivity204Tests'] + old))
        self.assertEqual(len(current), 72)
        self.assertEqual(tuple(self.review.FINAL_CASES), tuple(current))
        self.assertLessEqual(self.review.REQUIRED204_CASES, set(current))

    def test_old_vm_input_and_original_packages_are_the_protected_baseline(self):
        tool = self.delivery
        self.assertEqual(tool.PRIOR_VM_SHA256, 'da2a770b768d84227bf415bc7b458b056612317b2ebf09820826b7889b9860b6')
        self.assertEqual(tool.PRIOR_INPUT_SHA256, 'b8bc9c5d34f76840e0a849c072d01ea5c7f0d87759ab69688f70636335a0f2ad')
        self.assertEqual(self.review.PRIOR_MANIFEST.name, 'staged-source-manifest.json')
        self.assertEqual(self.review.PRIOR_MANIFEST.parent.name, 'mobile-release204-20261108')
        self.assertEqual(self.review.sha(self.review.PRIOR_MANIFEST), self.review.PRIOR_MANIFEST_SHA256)

    def test_capture_and_verifier_bind_actual_maintained_and_review_inputs(self):
        self.assertEqual(self.capture.REVIEW_TESTS, self.review.REVIEW_TESTS)
        self.assertEqual(self.capture.REVIEW_INPUTS, self.review.REVIEW_INPUTS)
        self.assertIn('review/test_review204r2.py', self.capture.REVIEW_TESTS)
        self.assertIn('review/verify_post203_repairs.py', self.capture.REVIEW_INPUTS)
        self.assertIn('review/verify_204r2_repairs.py', self.capture.REVIEW_INPUTS)
        actual = self.capture.inputs()
        self.assertIn('tools/release204r2_delivery.py', actual)
        self.assertIn('tools/release204_delivery.py', actual)
        self.assertEqual(self.capture.reviewer_inputs(), {
            name: self.review.sha(ROOT / name) for name in self.review.REVIEW_INPUTS})

    def test_independent_package_audit_recovers_the_exact_reviewed_selection(self):
        source = (ROOT / 'tools/release204r2_delivery.py').read_text(encoding='utf8')
        selection = json.loads((ROOT / 'review/release204r2-cases.json').read_text())
        self.assertEqual(self.packages.delivery_cases(source, selection), self.delivery.FINAL_CASES)
        self.assertEqual(self.packages.RELEASE, self.delivery.MOBILE)
        self.assertEqual(self.packages.package_path('Android'), self.delivery.package_path('Android'))
        self.assertEqual(self.packages.package_path('iOS'), self.delivery.package_path('iOS'))
        self.assertEqual(self.font.OUTPUT.name, 'dbg-font-full-range-coverage-204r2.json')

    def test_independent_package_audit_rejects_wrapper_side_effect_and_identity_edits(self):
        source = (ROOT / 'tools/release204r2_delivery.py').read_text(encoding='utf8')
        selection = json.loads((ROOT / 'review/release204r2-cases.json').read_text())
        for modified in (source + '\npublish()\n',
                         source.replace('INTERNAL = 102', 'INTERNAL = 103'),
                         source + '\n_BASE_TOOL_SHA256 = "0" * 64\n'):
            with self.subTest(modified=modified[-80:]), self.assertRaisesRegex(RuntimeError, 'wrapper changed'):
                self.packages.delivery_cases(modified, selection)


class QuestPortalEvidence204Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = load('revision204r2_quest_portal_guard', 'review/verify_204r2_repairs.py')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        witness = dict.fromkeys(('check_enemies', 'CrownPickup', 'VaultStatue', 'CrownGuardian', 'TutCont',
            'RadMaggotChest', 'BecomeScrapBoss', 'LevCont', 'GenCont', 'Menu', 'Cinematic', 'GameOver',
            'SitDown', 'special_final_area'), False)
        witness.update(recovery_allowed=True, eligible=True, player=True, locked=True, full_portal_blocked=True,
            active_portal_prevents=0, hearts=0)
        routes = []
        for rate in (30, 60):
            for route, stored, seed in (('QuestHubNatural', False, 702643), ('QuestStoredHubNatural', True, 41),
                    ('QuestStoredHubAltSeedNatural', True, 702643)):
                deaths = [dict(id=1001, object='Bandit', hp=0, frame=100), dict(id=1002, object='IDPD', hp=-3, frame=200)]
                alarms = [dict(kind=kind, corpse=2001, frame=250, forceportal=False, native_deaths_before=2,
                    eligibility=deepcopy(witness)) for kind in ('before', 'rejected')]
                routes.append(dict(route=route, stored=stored, seed=seed, rate=rate, runtime_fps=rate,
                    logic_scale=30 / rate, completed=True, frames=2000, logical_ticks=2000 * 30 / rate,
                    locked_frames=1800, unblocked_locked_frames=0, ordinary_portals=[], merges=[True] * 3,
                    native_deaths=deaths, actual_shots=2, generated_enemies_seen=2, hearts_seen=8,
                    heart_gate_intervals=3, enemy_gate_intervals=3, eligible_empty_frames=360,
                    eligible_empty_ticks=180, recovery_eligible_calls=4, corpse_eligible_attempts=1,
                    corpse_rejected_attempts=1, final_unlock_wait_ticks=90, eligible_empty_witness=deepcopy(witness),
                    final_unlock_wait_witness=deepcopy(witness), empty_gaps=[dict(before_merge=index, ticks=60,
                        native_deaths_before=0 if index == 0 else index, hearts_seen=(2, 4, 8)[index], frame=100 * index)
                        for index in range(3)], corpse_alarms=alarms, owner_release_seen=True,
                    owner_release=dict(locked_exists=False, reward_exists=True, full_portal_blocked=False,
                        remaining_floor_controllers=4, frame=1900), reward_opened=True, crown_created=True,
                    legal_crown_portal=dict(native_collision=True, type=3, id=3001, frame=1950)))
        controls = [dict(kind=kind, actor=4001 + index, live_actor=True, locked_exists=False, full_portal_blocked=False)
            for index, kind in enumerate(('FloorCont-only', 'CrownPed-only', 'HugeQuestChest-before-open', 'ordinary-HeartBullet'))]
        controls += [dict(kind='HugeQuestChest-after-open', genuine_contact=True, locked_exists=False, full_portal_blocked=False),
            dict(kind='normal-combat-release', enemy_id=5001, native_deaths=[dict(id=5001, object='Bandit', hp=0, frame=100)],
                corpse_attempts=1, corpse_passes=1, actual_shots=1, portal_type=1, full_portal_blocked=False)]
        self.evidence = dict(schema=1, status='PASS', reason='', physical_device_tested=False,
            actual_native_frames=True, actual_enemy_damage_and_deaths=True, ordinary_portals_deleted=False,
            routes=routes, controls=controls)

    def verify(self, evidence=None, *, log_change=None, diagnostic_change=None,
               hash_change=False, missing_artifact=False, dispatch=False):
        evidence = self.evidence if evidence is None else evidence
        target = self.directory / 'frontier-quest-portal204.json'
        target.write_text(json.dumps(evidence), encoding='utf8')
        diagnostics = []
        for index, row in enumerate(evidence['routes']):
            diagnostics.append({**evidence, 'status': 'IN_PROGRESS',
                'reason': 'native route reached final acceptance assertions',
                'routes': evidence['routes'][:index], 'controls': [],
                'active_route': {**row, 'completed': False}})
        if diagnostic_change == 'missing':
            diagnostics.pop()
        elif diagnostic_change == 'duplicate':
            diagnostics[1] = deepcopy(diagnostics[0])
        elif diagnostic_change == 'status':
            diagnostics[0]['status'] = 'FAIL'
        elif diagnostic_change == 'completed':
            diagnostics[0]['active_route']['completed'] = True
        elif diagnostic_change == 'counter':
            diagnostics[0]['active_route']['actual_shots'] += 1
        elif diagnostic_change == 'death':
            diagnostics[0]['active_route']['native_deaths'] = []
        elif diagnostic_change == 'merge':
            diagnostics[0]['active_route']['empty_gaps'] = []
        elif diagnostic_change == 'cumulative':
            diagnostics[1]['routes'] = []
        elif diagnostic_change == 'controls':
            diagnostics[0]['controls'] = deepcopy(evidence['controls'])
        elif diagnostic_change == 'reason':
            diagnostics[0]['reason'] = 'unverified checkpoint'
        lines = []
        for index, row in enumerate(evidence['routes']):
            if index < len(diagnostics):
                lines.append('FR_QUEST_PORTAL204 ' + json.dumps(diagnostics[index]))
            lines.append('FR_QUEST_PORTAL204 ROUTE PASS ' + json.dumps(row))
        lines.append('FR_QUEST_PORTAL204 ' + json.dumps(evidence))
        if log_change == 'missing-final':
            lines.pop()
        elif log_change == 'duplicate-final':
            lines.append(lines[-1])
        elif log_change == 'missing-route':
            lines.pop(1)
        elif log_change == 'changed-route':
            changed = deepcopy(evidence['routes'][0])
            changed['rate'] = 15
            lines[1] = 'FR_QUEST_PORTAL204 ROUTE PASS ' + json.dumps(changed)
        if diagnostic_change == 'extra':
            lines.insert(0, 'FR_QUEST_PORTAL204 ' + json.dumps(diagnostics[0]))
        elif diagnostic_change == 'detached':
            lines[0], lines[1] = lines[1], lines[0]
        elif diagnostic_change == 'only-progress':
            lines.pop()
        artifacts = {} if missing_artifact else {target.name: '0' * 64 if hash_change else self.review.sha(target)}
        verify = self.review.verify_quest_portal
        if dispatch:
            return self.review.verify204_identity('FrontierQuestPortal204Tests', '\n'.join(lines), artifacts, self.directory)
        return verify('\n'.join(lines), artifacts, self.directory)

    def test_accepts_all_six_real_routes_and_dispatches_mandatory_semantics(self):
        accepted = self.verify(dispatch=True)
        self.assertEqual(accepted['routes'], self.evidence['routes'])
        self.assertEqual(accepted['controls'], self.evidence['controls'])
        self.assertIn('FrontierQuestPortal204Tests', self.review.CURRENT204_CASES)
        self.assertIn('FrontierQuestPortal204Tests', self.review.REQUIRED204_CASES)

    def test_accepts_actual_60hz_half_tick_timestamps_without_weakening_counts(self):
        evidence = deepcopy(self.evidence)
        for row in evidence['routes']:
            for witness in [*row['native_deaths'], *row['empty_gaps'], *row['corpse_alarms'],
                    row['owner_release'], row['legal_crown_portal']]:
                witness['frame'] += 0.5
        self.verify(evidence)

    def test_rejects_unfinished_missing_duplicate_or_unbound_preassertion_diagnostics(self):
        for change in ('missing', 'duplicate', 'extra', 'status', 'completed', 'counter', 'death', 'merge',
                'cumulative', 'controls', 'reason', 'detached', 'only-progress'):
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(diagnostic_change=change)

    def test_rejects_missing_duplicate_reordered_or_wrong_source_route(self):
        for change in ('missing', 'duplicate', 'order', 'seed', 'stored', 'rate', 'runtime_fps', 'logic_scale'):
            evidence = deepcopy(self.evidence)
            rows = evidence['routes']
            if change == 'missing':
                rows.pop()
            elif change == 'duplicate':
                rows[1] = deepcopy(rows[0])
            elif change == 'order':
                rows.reverse()
            else:
                rows[0][change] = False if change == 'stored' else 12
                if change == 'stored':
                    rows[0][change] = True
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_unrelated_blockers_that_would_mask_premature_portal(self):
        false_flags = ('check_enemies', 'CrownPickup', 'VaultStatue', 'CrownGuardian', 'TutCont', 'RadMaggotChest',
            'BecomeScrapBoss', 'LevCont', 'GenCont', 'Menu', 'Cinematic', 'GameOver', 'SitDown', 'special_final_area')
        for witness in ('eligible_empty_witness', 'final_unlock_wait_witness'):
            for flag in false_flags:
                evidence = deepcopy(self.evidence)
                evidence['routes'][0][witness][flag] = True
                with self.subTest(witness=witness, flag=flag), self.assertRaises(AssertionError):
                    self.verify(evidence)
            for flag in ('recovery_allowed', 'eligible', 'player', 'locked', 'full_portal_blocked'):
                evidence = deepcopy(self.evidence)
                evidence['routes'][0][witness][flag] = False
                with self.subTest(witness=witness, flag=flag), self.assertRaises(AssertionError):
                    self.verify(evidence)
            for field in ('active_portal_prevents', 'hearts'):
                evidence = deepcopy(self.evidence)
                evidence['routes'][0][witness][field] = 1
                with self.subTest(witness=witness, field=field), self.assertRaises(AssertionError):
                    self.verify(evidence)

    def test_rejects_missing_short_wrong_order_or_predeath_merge_gaps(self):
        for change in ('missing', 'order', 'short', 'predeath', 'hearts', 'final-wait', 'merge', 'witness'):
            evidence = deepcopy(self.evidence)
            row = evidence['routes'][0]
            if change == 'missing':
                row['empty_gaps'].pop()
            elif change == 'order':
                row['empty_gaps'].reverse()
            elif change == 'short':
                row['empty_gaps'][1]['ticks'] = 29
            elif change == 'predeath':
                row['empty_gaps'][1]['native_deaths_before'] = 0
            elif change == 'hearts':
                row['hearts_seen'] = 7
            elif change == 'final-wait':
                row['final_unlock_wait_ticks'] = 89
            elif change == 'merge':
                row['merges'][2] = False
            else:
                row['final_unlock_wait_witness']['full_portal_blocked'] = False
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_unguarded_frames_early_portals_or_a_passed_forced_corpse_alarm(self):
        for change in ('unguarded', 'portal', 'passed', 'forced', 'no-alarm', 'count', 'alarm-blocker'):
            evidence = deepcopy(self.evidence)
            row = evidence['routes'][0]
            if change == 'unguarded':
                row['unblocked_locked_frames'] = 1
            elif change == 'portal':
                row['ordinary_portals'] = [dict(type=1)]
            elif change == 'passed':
                row['corpse_alarms'][0]['kind'] = 'passed'
            elif change == 'forced':
                row['corpse_alarms'][0]['forceportal'] = True
            elif change == 'no-alarm':
                row['corpse_alarms'] = []
            elif change == 'count':
                row['corpse_rejected_attempts'] += 1
            else:
                row['corpse_alarms'][0]['eligibility']['CrownPickup'] = True
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_absent_actual_combat_or_native_deaths(self):
        for change in ('actual_native_frames', 'actual_enemy_damage_and_deaths', 'deaths', 'hp', 'duplicate', 'shots', 'enemy_gate_intervals'):
            evidence = deepcopy(self.evidence)
            row = evidence['routes'][0]
            if change in ('actual_native_frames', 'actual_enemy_damage_and_deaths'):
                evidence[change] = False
            elif change == 'deaths':
                row['native_deaths'] = []
            elif change == 'hp':
                row['native_deaths'][0]['hp'] = 1
            elif change == 'duplicate':
                row['native_deaths'][1]['id'] = row['native_deaths'][0]['id']
            else:
                row['actual_shots' if change == 'shots' else change] = 0
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_persistent_owner_or_missing_real_reward_and_crown_exit(self):
        for change in ('owner_release_seen', 'locked_exists', 'reward_exists', 'full_portal_blocked',
                'remaining_floor_controllers', 'reward_opened', 'native_collision', 'portal_type'):
            evidence = deepcopy(self.evidence)
            row = evidence['routes'][0]
            if change in ('owner_release_seen', 'reward_opened'):
                row[change] = False
            elif change in ('locked_exists', 'full_portal_blocked'):
                row['owner_release'][change] = True
            elif change in ('reward_exists', 'remaining_floor_controllers'):
                row['owner_release'][change] = 0
            else:
                row['legal_crown_portal']['native_collision' if change == 'native_collision' else 'type'] = False if change == 'native_collision' else 1
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_omitted_or_overbroad_owner_negative_controls(self):
        for change in ('missing', 'order', 'blocked', 'owner', 'not-live', 'not-contact', 'ordinary-type', 'ordinary-shot', 'ordinary-pass', 'ordinary-death'):
            evidence = deepcopy(self.evidence)
            controls = evidence['controls']
            if change == 'missing':
                controls.pop()
            elif change == 'order':
                controls.reverse()
            elif change == 'blocked':
                controls[0]['full_portal_blocked'] = True
            elif change == 'owner':
                controls[0]['locked_exists'] = True
            elif change == 'not-live':
                controls[0]['live_actor'] = False
            elif change == 'not-contact':
                controls[4]['genuine_contact'] = False
            elif change == 'ordinary-type':
                controls[5]['portal_type'] = 3
            elif change == 'ordinary-shot':
                controls[5]['actual_shots'] = 0
            elif change == 'ordinary-pass':
                controls[5]['corpse_passes'] = 0
            else:
                controls[5]['native_deaths'] = []
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_phone_claims_deleted_portals_unfinished_routes_or_truthy_flags(self):
        for change in ('physical_device_tested', 'ordinary_portals_deleted', 'active_route', 'truthy', 'noninteger', 'infinite'):
            evidence = deepcopy(self.evidence)
            if change in ('physical_device_tested', 'ordinary_portals_deleted'):
                evidence[change] = True
            elif change == 'active_route':
                evidence[change] = deepcopy(evidence['routes'][0])
            elif change == 'truthy':
                evidence['actual_native_frames'] = 'yes'
            elif change == 'noninteger':
                evidence['routes'][0]['actual_shots'] = 1.5
            else:
                evidence['routes'][0]['logical_ticks'] = float('inf')
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_missing_mismatched_duplicated_or_unbound_native_artifact(self):
        for change in ('missing-final', 'duplicate-final', 'missing-route', 'changed-route'):
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(log_change=change)
        with self.assertRaises(AssertionError):
            self.verify(hash_change=True)
        with self.assertRaises(AssertionError):
            self.verify(missing_artifact=True)


class MutationEvidence204Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = load('revision204r2_mutation_guard', 'review/verify_204r2_repairs.py')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        mini = {'bat ears': 31, 'lead ribs': 33, 'magnetic pulse': 34, 'toad breath': 37}
        hidden = {'annihilation': 30, 'reroll': 35, 'silver tongue': 36}
        augments = ['AugmentBloodlust', 'AugmentBoilingVeins', 'AugmentCompassion', 'AugmentEagleEyes',
            'AugmentEuphoria', 'AugmentExtraFeet', 'AugmentGammaGuts', 'AugmentHeavyHeart',
            'AugmentImpactWrists', 'AugmentLaserBrain', 'AugmentLastWish', 'AugmentLongArms',
            'AugmentLuckyShot', 'AugmentOpenMind', 'AugmentRabbitPaw', 'AugmentScarierFace',
            'AugmentSecondStomach', 'AugmentSharpTeeth']
        named = {'mini': mini, 'hidden': hidden, 'augment': dict(zip(augments, range(38, 56))),
            'burden': dict(zip(['BurdenAutomotiveApocalypse', 'BurdenBlood', 'BurdenPelagicPredicament', 'BurdenPlagueOfFlesh'], range(56, 60))),
            'surgery': dict(zip(['SurgerySlot', 'SurgerySlot2', 'SurgerySlot3', 'SurgerySlot4'], range(60, 64)))}
        self.evidence = {'status': 'PASS', 'rates': [30, 60],
            'groups': {key: [{'name': name, 'id': value} for name, value in group.items()] for key, group in named.items()},
            'physical_device_tested': False, 'actual_levcont_draw_gui': True, 'actual_random_chooser': True,
            'actual_rat_reward_grants': True, 'actual_idpd_station_grants': True, 'rows': [], 'special': []}
        for rate in (30, 60):
            for main in (False, True):
                eligible = list(range(1, 30)) + (list(range(38, 56)) if main else [])
                self.evidence['rows'].append({'rate': rate, 'main_pool_augments': main,
                    'eligible_ids': eligible, 'pages': [eligible[index:index + 11] for index in range(0, len(eligible), 11)],
                    'ordinary_rolls': (eligible * 12)[:256], 'left_wrap': True, 'right_wrap': True})
            self.evidence['special'].append({'rate': rate, 'rat_ids': list(mini.values()),
                'rat_eligible': [True] * 4, 'rat_natural_grants_passed': True,
                'compassion_when_not_full': False, 'compassion_when_full': True,
                'heavy_heart_when_ready': True, 'heavy_heart_when_not_ready': False,
                'disabled_normal_excluded': True, 'idpd_station': {'grant_name': 'AugmentEuphoria',
                    'grant_id': 42, 'base_id': 12, 'opened': True, 'grant_count': 1, 'base_count': 0,
                    'base_deactivated': True, 'ordinary_available': False}})

    def verify(self, evidence=None, *, omit_log=False):
        evidence = self.evidence if evidence is None else evidence
        target = self.directory / 'frontier-mutation-pool204.json'
        target.write_text(json.dumps(evidence), encoding='utf8')
        smoke = '\n'.join(['NTUF MUTATION POOL204 ROW ' + json.dumps(row) for row in evidence['rows']]
            + ['NTUF MUTATION POOL204 SPECIAL ' + json.dumps(row) for row in evidence['special']]
            + ['PASS NTUF MUTATION POOL204 actual native pages,normal rolls,exclusive Rat and HQ grants30/60'])
        return self.review.verify_mutation_pool('' if omit_log else smoke,
            {target.name: self.review.sha(target)}, self.directory)

    def test_accepts_complete_ordinary_pages_and_real_exclusive_grants(self):
        accepted = self.verify()
        self.assertEqual(accepted['rows'], self.evidence['rows'])
        self.assertEqual(accepted['special'], self.evidence['special'])

    def test_rejects_mini_hidden_augment_surgery_and_burden_leaks(self):
        for key in ('mini', 'hidden', 'augment', 'surgery', 'burden'):
            evidence = deepcopy(self.evidence)
            evidence['rows'][0]['eligible_ids'].append(evidence['groups'][key][0]['id'])
            with self.subTest(key=key), self.assertRaisesRegex(AssertionError, 'Exclusive mutation'):
                self.verify(evidence)

    def test_rejects_missing_or_duplicate_page_coverage_and_incomplete_random_rolls(self):
        for failure in ('missing', 'duplicate', 'rolls', 'wrap'):
            evidence = deepcopy(self.evidence)
            row = evidence['rows'][0]
            if failure == 'missing':
                row['pages'][-1].pop()
            elif failure == 'duplicate':
                row['pages'][0][1] = row['pages'][0][0]
            elif failure == 'rolls':
                row['ordinary_rolls'].pop()
            else:
                row['left_wrap'] = False
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_weakened_source_groups_or_option_and_exclusive_grants(self):
        for failure in ('group', 'option', 'rat', 'hq', 'compassion', 'heavy', 'disabled'):
            evidence = deepcopy(self.evidence)
            if failure == 'group':
                evidence['groups']['mini'].pop()
            elif failure == 'option':
                evidence['rows'][1]['main_pool_augments'] = False
            elif failure == 'rat':
                evidence['special'][0]['rat_natural_grants_passed'] = False
            elif failure == 'hq':
                evidence['special'][0]['idpd_station']['ordinary_available'] = True
            elif failure == 'compassion':
                evidence['special'][0]['compassion_when_not_full'] = True
            elif failure == 'heavy':
                evidence['special'][0]['heavy_heart_when_ready'] = False
            else:
                evidence['special'][0]['disabled_normal_excluded'] = False
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_artifact_without_matching_native_rows_and_completion(self):
        with self.assertRaisesRegex(AssertionError, 'actual native rows'):
            self.verify(omit_log=True)


class RedEvidence204Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = load('revision204r2_red_guard', 'review/verify_204r2_repairs.py')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        helper = {'id': 123, 'creator': 124, 'x': 48, 'y': 0, 'bbox': [48, 0, 64, 16],
            'solid': True, 'creator_exists': True, 'creator_mask': 'mskWall',
            'normal_floor_overlap': False, 'floor_styles': [1]}
        pre = {'start_helper_overlap': False, 'start_ordinary_wall_overlap': False,
            'contact_real_wall': True, 'contact_fake_wall': True, 'fake_native_mask': True,
            'helper_exists': True, 'helper_closed': True, 'wall_object': 'Wall',
            'wall_id': 120, 'wall_bbox': [0, 0, 16, 16]}
        ordinary = {'mode': 'fake-and-helper-open', 'position': [20, 13], 'motion': [1, -1],
            'wall_survived': True, 'ordinary_contact_resolved': True}
        fake_open = {**ordinary, 'mode': 'fake-open', 'position': [19, 14]}
        authored = {**deepcopy(fake_open), 'mode': 'authored'}
        boundaries = [{'phase': phase, 'protected_points': 5, 'protected_styles': [2, 3],
            'changed': [], 'fake_overlap': 0, 'helper_overlap': 0,
            'helpers': [] if phase == 'secret-before' else [deepcopy(helper)]}
            for phase in ('secret-before', 'corridor-after', 'quest-after')]
        self.evidence = {'status': 'PASS', 'rates': [30, 60], 'physical_device_tested': False,
            'actual_gencont': True, 'actual_player_mask': True, 'actual_player_collision_event': True,
            'actual_helper_endstep': True, 'manual_collision_dispatch': True, 'manual_pixel_integration': True,
            'queries': [{'object': obj, 'solid': False, 'native_meeting': True, 'actual': expected,
                'expected': expected, 'fake_family': not expected}
                for obj, expected in (('NTTEFullWallFake', False), ('Wall', True), ('NTTESolidWall', True))],
            'seams': [], 'worlds': [], 'walks': []}
        for rate in (30, 60):
            self.evidence['seams'].append({'rate': rate, 'contact': [15, 15], 'start': [18, 18],
                'ordinary': deepcopy(ordinary), 'fake_open': deepcopy(fake_open), 'authored': deepcopy(authored),
                'preconditions': deepcopy(pre), 'fake_only': [15, 15], 'ordinary_contact_resolved': True,
                'authored_vs_fake_open_distance': 0, 'actual_player_collision_event': True,
                'actual_native_floor_and_wall_create': True, 'actual_wall_fake_create_and_helper': True,
                'manual_collision_dispatch': True, 'physical_device_tested': False})
        for seed in (1, 2, 3):
            for rate in (30, 60):
                self.evidence['worlds'].append({'seed': seed, 'rate': rate, 'generation_rate': 30,
                    'actual_gencont': True, 'actual_player_collision_event': True, 'actual_helper_endstep': True,
                    'boundaries': deepcopy(boundaries), 'seam': {'candidate': True, 'fixture': {
                        'invalid': False, 'start': [18, 18], 'contact': [15, 15], 'fake': [0, 16], 'wall': [0, 0],
                        'preconditions': deepcopy(pre), 'controls': [deepcopy(ordinary), deepcopy(fake_open)],
                        'authored': deepcopy(authored), 'actual_collision_event': True,
                        'manual_collision_dispatch': True, 'physical_device_tested': False}}})
        for rate in (30, 60):
            for index, kind in enumerate(('warp', 'twins')):
                self.evidence['walks'].append({'seed': 91, 'rate': rate, 'generation_rate': 30,
                    'target_index': index, 'target_count': 2, 'target': {'kind': kind, 'x': 32 + index * 32, 'y': 0},
                    'components': 1, 'nodes': 20, 'actual_gencont': True, 'pixel_swept_edges': True,
                    'helpers_after_walk': [deepcopy(helper)], 'walk': {'steps': 100, 'reached': True,
                        'returned': True, 'blocked': [], 'final': [0, 0], 'fake_collision_events': index * 10,
                        'peak_reveal': index, 'closed_overlapping_after_endstep': 0,
                        'orphan_helpers_after_endstep': 0, 'open_helpers_after_return': 0,
                        'reveal_after_return': 0, 'actual_wall_collision_events': True,
                        'actual_helper_endstep': True, 'manual_pixel_integration': True}})

    def verify(self, evidence=None, *, log_change=None):
        evidence = self.evidence if evidence is None else evidence
        target = self.directory / 'frontier-red-regression204.json'
        target.write_text(json.dumps(evidence), encoding='utf8')
        lines = ['NTUF RED QUERY204 ROW ' + json.dumps(evidence['queries'])]
        for key, prefix in (('seams', 'NTUF RED SEAM204 ROW '),
                            ('worlds', 'NTUF RED REGRESSION204 WORLD '),
                            ('walks', 'NTUF RED REGRESSION204 WALK ')):
            lines.extend(prefix + json.dumps(row) for row in evidence[key])
        lines.append('NTUF RED REGRESSION204 PASS generated seams, ordinary Warp paths and hidden-room round trips')
        if log_change == 'missing':
            lines.pop(1)
        elif log_change == 'duplicate':
            lines.append(lines[-1])
        return self.review.verify_red_connectivity('\n'.join(lines),
            {target.name: self.review.sha(target)}, self.directory)

    def test_accepts_generated_seams_and_complete_warp_secret_round_trips(self):
        accepted = self.verify()
        self.assertEqual(accepted['worlds'], self.evidence['worlds'])
        self.assertEqual(accepted['walks'], self.evidence['walks'])
        self.assertIn('no physical phone acceptance', accepted['scope'])

    def test_rejects_diagnostic_status_rate_seed_or_hardware_scope_substitution(self):
        for failure in ('diagnostic', 'rates', 'seed', 'generation_rate', 'physical'):
            evidence = deepcopy(self.evidence)
            if failure == 'diagnostic':
                evidence['status'] = 'DIAGNOSTIC'
            elif failure == 'rates':
                evidence['rates'] = [30]
            elif failure == 'seed':
                evidence['worlds'][0]['seed'] = 91
            elif failure == 'generation_rate':
                evidence['worlds'][1]['generation_rate'] = 60
            else:
                evidence['physical_device_tested'] = True
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_blanket_nonsolid_exclusion_or_retained_fake_query(self):
        for index in range(3):
            evidence = deepcopy(self.evidence)
            evidence['queries'][index]['actual'] = not evidence['queries'][index]['actual']
            with self.subTest(index=index), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_invalid_natural_seam_preconditions_and_damaged_walls(self):
        for failure in ('candidate', 'invalid', 'start_helper', 'start_wall', 'contact', 'mask', 'closed', 'destroyed', 'unresolved', 'position', 'motion'):
            evidence = deepcopy(self.evidence)
            seam = evidence['worlds'][0]['seam']
            fixture = seam['fixture']
            if failure == 'candidate':
                seam['candidate'] = False
            elif failure == 'invalid':
                fixture['invalid'] = True
            elif failure == 'start_helper':
                fixture['preconditions']['start_helper_overlap'] = True
            elif failure == 'start_wall':
                fixture['preconditions']['start_ordinary_wall_overlap'] = True
            elif failure in ('contact', 'mask', 'closed'):
                fixture['preconditions'][{'contact': 'contact_real_wall', 'mask': 'fake_native_mask', 'closed': 'helper_closed'}[failure]] = False
            elif failure == 'destroyed':
                fixture['authored']['wall_survived'] = False
            elif failure == 'unresolved':
                fixture['authored']['ordinary_contact_resolved'] = False
            else:
                fixture['authored'][failure][0] += 1
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_missing_ordinary_or_warp_road_protection_and_fake_only_block(self):
        for failure in ('style0', 'style1', 'changed', 'helper', 'phase', 'fake_only'):
            evidence = deepcopy(self.evidence)
            boundaries = evidence['worlds'][0]['boundaries']
            if failure in ('style0', 'style1'):
                boundaries[0]['protected_styles'][int(failure[-1])] = 0
            elif failure == 'changed':
                boundaries[1]['changed'] = [{'point': [0, 0]}]
            elif failure == 'helper':
                boundaries[2]['helper_overlap'] = 1
            elif failure == 'phase':
                boundaries[2]['phase'] = 'corridor-after'
            else:
                evidence['seams'][0]['fake_only'][0] += 1
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_incomplete_targets_blocked_walk_or_lost_reveal_and_restoration(self):
        for failure in ('missing', 'index', 'kind', 'target', 'returned', 'blocked', 'hidden', 'open', 'mask', 'orphan', 'final'):
            evidence = deepcopy(self.evidence)
            row = evidence['walks'][1]
            if failure == 'missing':
                evidence['walks'].pop()
            elif failure == 'index':
                row['target_index'] = 0
            elif failure == 'kind':
                row['target']['kind'] = 'warp'
            elif failure == 'target':
                evidence['walks'][3]['target']['x'] += 1
            elif failure == 'returned':
                row['walk']['returned'] = False
            elif failure == 'blocked':
                row['walk']['blocked'] = [{'at': [0, 0]}]
            elif failure == 'hidden':
                row['walk']['fake_collision_events'] = 0
            elif failure == 'open':
                row['walk']['open_helpers_after_return'] = 1
            elif failure == 'mask':
                row['helpers_after_walk'][0]['creator_mask'] = 'mskNone'
            elif failure == 'orphan':
                row['helpers_after_walk'][0]['creator_exists'] = False
            else:
                row['walk']['final'][0] += 1
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_missing_native_rows_or_duplicated_completion(self):
        for change in ('missing', 'duplicate'):
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(log_change=change)



class LoadoutArtwork204Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = load('revision204r2_loadout_guard', 'review/verify_204r2_repairs.py')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.evidence = {'status': 'PASS', 'control_coverage': 256, 'control_ink': 256,
            'empty_coverage': 0, 'refresh_and_native_rebuild_verified': True,
            'all_declared_callbacks_checked': True, 'rows': [], 'phases': []}
        for phase in range(3):
            self.evidence['phases'].append({'phase': phase, 'declared': 2, 'absent_callbacks': 75,
                'checked_weapons': 77, 'all_gameplay_sprites_unchanged': True,
                'ordinary_fallback_pixels_verified': True, 'ordinary_fallback_coverage': 30})
            for key, weapon, portrait in (
                ('weapon:FR_BubblesCutlass', 187, 'sprFR_sprBubblesCutlassLoadout_a3f9cae1b4d8'),
                ('weapon:FR_BubblesShovel', 188, 'sprFR_sprBubblesShovelLoadout_b0d98bdf1533')):
                self.evidence['rows'].append({'phase': phase, 'key': key, 'weapon': weapon,
                    'portrait': portrait, 'coverage': 128, 'ink': 64,
                    'exact_authored_pixels': True, 'gameplay_fallback_rejected': True})

    def verify(self, evidence=None, *, log_change=None, capture_change=None):
        evidence = self.evidence if evidence is None else evidence
        target = self.directory / 'frontier-loadout-art204.json'
        target.write_text(json.dumps(evidence), encoding='utf8')
        artifacts = {target.name: self.review.sha(target)}
        for weapon in (187, 188):
            capture = self.directory / f'frontier-loadout-art204-{weapon}.png'
            # The semantic gate binds the native consumer capture bytes; native GPU
            # pixel verification is established by the hash-bound native test.
            capture.write_bytes(b'artwork guard fixture')
            artifacts[capture.name] = self.review.sha(capture)
            if capture_change == 'missing' and weapon == 188:
                del artifacts[capture.name]
            elif capture_change == 'changed' and weapon == 188:
                capture.write_bytes(b'changed fixture')
        lines = ['LOADOUT ART204 ' + json.dumps(row) for row in evidence['phases']]
        lines.append('PASS FRONTIER authored loadout portraits: all source callbacks, genuine native consumer GPU pixels, refresh/rebuild and no-art fallback')
        if log_change == 'phase':
            lines.pop(0)
        elif log_change == 'done':
            lines.append(lines[-1])
        return self.review.verify_loadout_art('\n'.join(lines), artifacts, self.directory)

    def test_accepts_all_authored_callbacks_and_three_real_rebuild_phases(self):
        accepted = self.verify()
        self.assertEqual(accepted['rows'], self.evidence['rows'])
        self.assertIn('no physical phone acceptance', accepted['scope'])

    def test_rejects_empty_control_portrait_or_fallback(self):
        for failure in ('control', 'empty', 'coverage', 'ink', 'fallback'):
            evidence = deepcopy(self.evidence)
            if failure == 'control':
                evidence['control_coverage'] = 0
            elif failure == 'empty':
                evidence['empty_coverage'] = 1
            elif failure == 'fallback':
                evidence['phases'][2]['ordinary_fallback_coverage'] = 0
            else:
                evidence['rows'][0][failure] = 0
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_missing_or_duplicate_weapon_or_phase(self):
        for failure in ('weapon', 'row', 'phase', 'callback_count', 'absent_count', 'checked_count'):
            evidence = deepcopy(self.evidence)
            if failure == 'weapon':
                evidence['rows'][1]['key'] = evidence['rows'][0]['key']
            elif failure == 'row':
                evidence['rows'].pop()
            elif failure == 'phase':
                evidence['phases'][2]['phase'] = 1
            else:
                field = {'callback_count': 'declared', 'absent_count': 'absent_callbacks', 'checked_count': 'checked_weapons'}[failure]
                evidence['phases'][0][field] -= 1
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_gameplay_sprite_or_wrong_portrait_substitution(self):
        for failure in ('portrait', 'weapon', 'pixels', 'fallback', 'gameplay', 'ordinary', 'refresh'):
            evidence = deepcopy(self.evidence)
            if failure == 'portrait':
                evidence['rows'][0]['portrait'] = 'sprWeapon'
            elif failure == 'weapon':
                evidence['rows'][0]['weapon'] = 1
            elif failure in ('pixels', 'fallback'):
                evidence['rows'][0][{'pixels': 'exact_authored_pixels', 'fallback': 'gameplay_fallback_rejected'}[failure]] = False
            elif failure in ('gameplay', 'ordinary'):
                evidence['phases'][1][{'gameplay': 'all_gameplay_sprites_unchanged', 'ordinary': 'ordinary_fallback_pixels_verified'}[failure]] = False
            else:
                evidence['refresh_and_native_rebuild_verified'] = False
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_missing_native_logs_or_capture_and_changed_capture_bytes(self):
        for change in ('phase', 'done'):
            with self.subTest(log=change), self.assertRaises(AssertionError):
                self.verify(log_change=change)
        for change in ('missing', 'changed'):
            with self.subTest(capture=change), self.assertRaises(AssertionError):
                self.verify(capture_change=change)


class BossArtwork204Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = load('revision204r2_boss_art_guard', 'review/verify_204r2_repairs.py')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        bosses = ('CoveHyperCrystal', 'GraveyardBoss', 'LightningHyperCrystal', 'OurpleCursedHyperCrystal', 'RoboBoss')
        targets = {'Main': 'sprBossIntro', 'Back': 'sprBossIntroBackLayer', 'Name': 'sprBossName'}
        coverage = {'CoveHyperCrystal': (30337, 4915, 3492), 'GraveyardBoss': (0, 23032, 3492),
            'LightningHyperCrystal': (31234, 4915, 3492), 'OurpleCursedHyperCrystal': (30337, 4915, 3492),
            'RoboBoss': (12106, 54714, 4180)}
        palettes = {'CoveHyperCrystal': (8, 6, 1), 'GraveyardBoss': (0, 6, 1),
            'LightningHyperCrystal': (8, 6, 1), 'OurpleCursedHyperCrystal': (8, 6, 1), 'RoboBoss': (3, 11, 1)}
        inks = {'CoveHyperCrystal': (26139, 3538, 3492), 'GraveyardBoss': (0, 23032, 3492),
            'LightningHyperCrystal': (27037, 3538, 3492), 'OurpleCursedHyperCrystal': (26139, 3538, 3492),
            'RoboBoss': (12106, 45215, 4180)}
        self.manifest = {'schema': 'frontier-boss-art204-v1', 'resource_count': 15, 'alias_count': 30,
            'base_manifest_sha256': self.review.sha(ROOT / 'generated-assets/manifest.json'), 'assets': []}
        self.proof = {'status': 'PASS', 'resource_count': 15, 'alias_count': 30,
            'original_inventory_verified': True, 'rgba_preserved': True, 'target_origins_preserved': True,
            'native_execution_performed': False, 'physical_device_tested': False}
        self.evidence = {'status': 'PASS', 'physical_device_tested': False, 'resource_count': 15,
            'alias_count': 30, 'control_coverage': 1024, 'control_ink': 1024, 'empty_coverage': 0,
            'missing_alias_rejected': True, 'resources': [], 'intros': [],
            'native_name_path_unchanged': True, 'disabled_intro_guard_preserved': True,
            'destroyed_owner_rejected': True, 'ordinary_intro_replacement_isolated': True,
            'ntte_intro_replacement_isolated': True, 'destroyed_owner_pixels_restored': True,
            'rejected_start_guards': [{'kind': kind, 'refused': True, 'ntte_key_preserved': True,
                'state_preserved': True, 'artwork_preserved': True, 'actual_source_callback_rejected': True,
                'rejected_source_cleanup_preserved': True} for kind in ('disabled', 'coop', 'no-player')],
            'interrupted_intro_restoration': [{'kind': kind, 'actual_source_callback': True,
                'owner_destroyed': True, 'name_path_preserved': True, 'all_native_pixels_restored': True,
                'restored_before_active_query': True,
                'dirty_layers': [{'role': role, 'target': target, 'authored_pixels_match': True,
                    'changed_from_native': True} for role, target in targets.items()],
                'restored_layers': [{'role': role, 'target': target, 'restored_pixels_match': True,
                    'restored_origin_match': True} for role, target in targets.items()]}
                for kind in ('ordinary', 'ntte')]}
        for boss in bosses:
            for role, target in targets.items():
                role_index = ('Main', 'Back', 'Name').index(role)
                raw_coverage, raw_palette, raw_ink = coverage[boss][role_index], palettes[boss][role_index], inks[boss][role_index]
                path = f'Sprites/Menu/Intros/spr{boss}{role}.png'
                resource = f'spr{boss}{role}'
                self.manifest['assets'].append({'boss': boss, 'role': role, 'path': path,
                    'resource': resource, 'target': target, 'aliases': [path.lower(), '../' + path.lower()],
                    'width': 512, 'height': 256, 'origin': [16, 8], 'frames': 1,
                    'source_sha256': 'a' * 64, 'rgba_sha256': 'b' * 64, 'source_bytes': 100,
                    'alpha_coverage': raw_coverage, 'authored_transparent': False})
                self.evidence['resources'].append({'boss': boss, 'role': role, 'path': path.lower(),
                    'resource': resource, 'target': target, 'width': 512, 'height': 256, 'origin_x': 16,
                    'origin_y': 8, 'source_coverage': raw_coverage, 'source_ink': raw_ink, 'source_colours': raw_palette,
                    'expected_source_coverage': raw_coverage, 'expected_source_colours': raw_palette, 'expected_source_ink': raw_ink, 'authored_transparent': False,
                    'aliases_resolve': True, 'source_nonempty': True, 'replacement_pixels_match': True,
                    'replacement_origin_match': True, 'restored_pixels_match': True, 'restored_origin_match': True})
                if boss == 'GraveyardBoss' and role == 'Main':
                    self.manifest['assets'][-1].update(width=481, height=240, alpha_coverage=0, authored_transparent=True)
                    self.evidence['resources'][-1].update(width=481, height=240, expected_source_coverage=0,
                        source_coverage=0, source_ink=0, source_colours=0, source_nonempty=False, authored_transparent=True)
            self.evidence['intros'].append({'boss': boss, 'enabled': True, 'actual_source_callback': True,
                'artwork_applied': True, 'artwork_restored': True, 'state_preserved': True,
                'native_intro_started': True, 'artwork_retained_while_active': True,
                'native_intro_closed': True, 'frontend_name_png_selected': True,
                'actual_native_draw_visible': True, 'native_draw_changed_pixels': 500,
                'actual_pause_barrier': True, 'owner_inactive_at_barrier': True,
                'owner_remained_inactive': True, 'pause_artwork_retained': True})

    def verify(self, evidence=None, *, manifest=None, log_change=False, capture_change=None, restoration_capture_change=None):
        evidence = self.evidence if evidence is None else evidence
        target = self.directory / 'frontier-boss-art204.json'
        target.write_text(json.dumps(evidence), encoding='utf8')
        original_read = self.review.read
        def read(path):
            if Path(path) == ROOT / 'generated-assets/boss-art204/manifest.json':
                return self.manifest if manifest is None else manifest
            if Path(path) == ROOT / 'generated-assets/boss-art204/verification.json':
                return self.proof
            return original_read(path)
        smoke = '' if log_change else ('FR_BOSS_ART204 ' + json.dumps(evidence) + '\n'
            + 'PASS FRONTIER boss art204: all15 authored resources,30 aliases,5 enabled actual source intros, GPU pixels/origins and restoration')
        artifacts = {target.name: self.review.sha(target)}
        for row in self.evidence['resources']:
            capture = self.directory / f"frontier-boss-art204-{row['boss'].lower()}-{row['role'].lower()}.png"
            capture.write_bytes(b'boss artwork guard fixture')
            artifacts[capture.name] = self.review.sha(capture)
        for row in self.evidence['intros']:
            capture = self.directory / f"frontier-boss-art204-{row['boss'].lower()}-native-intro.png"
            capture.write_bytes(b'native boss intro Draw guard fixture')
            artifacts[capture.name] = self.review.sha(capture)
            if row['boss'] == 'RoboBoss':
                if capture_change == 'missing':
                    del artifacts[capture.name]
                elif capture_change == 'changed':
                    capture.write_bytes(b'changed native Draw capture')
        for route in ('ordinary', 'ntte', 'destroyed-owner'):
            for role in ('main', 'back', 'name'):
                capture = self.directory / f'frontier-boss-art204-interrupted-{route}-{role}.png'
                capture.write_bytes(b'interrupted native-layer guard fixture')
                artifacts[capture.name] = self.review.sha(capture)
                if restoration_capture_change is not None and restoration_capture_change[0] == route and role == 'main':
                    if restoration_capture_change[1] == 'missing':
                        del artifacts[capture.name]
                    else:
                        capture.write_bytes(b'changed interrupted native-layer fixture')
        with patch.object(self.review, 'read', side_effect=read):
            return self.review.verify_boss_art(smoke, artifacts, self.directory)

    def test_accepts_all_five_native_callbacks_and_fifteen_authored_triplet_resources(self):
        accepted = self.verify()
        self.assertEqual(accepted['resources'], self.evidence['resources'])
        self.assertIn('no physical phone acceptance', accepted['scope'])

    def test_rejects_inactive_native_intro_early_art_restoration_or_missing_visible_draw(self):
        flags = ('native_intro_started', 'artwork_retained_while_active', 'native_intro_closed',
            'frontend_name_png_selected', 'actual_native_draw_visible', 'actual_pause_barrier',
            'owner_inactive_at_barrier', 'owner_remained_inactive', 'pause_artwork_retained')
        for index in range(5):
            for flag in flags:
                evidence = deepcopy(self.evidence)
                evidence['intros'][index][flag] = False
                with self.subTest(index=index, flag=flag), self.assertRaises(AssertionError):
                    self.verify(evidence)
        for count in (0, 100, -1, True, 101.5, float('nan')):
            evidence = deepcopy(self.evidence)
            evidence['intros'][0]['native_draw_changed_pixels'] = count
            with self.subTest(count=count), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_changed_native_name_paths_stale_owner_or_same_tick_replacement_leaks(self):
        for flag in ('native_name_path_unchanged', 'disabled_intro_guard_preserved', 'destroyed_owner_rejected',
                     'ordinary_intro_replacement_isolated', 'ntte_intro_replacement_isolated', 'destroyed_owner_pixels_restored'):
            evidence = deepcopy(self.evidence)
            evidence[flag] = False
            with self.subTest(flag=flag), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_missing_or_incomplete_disabled_coop_and_no_player_start_guards(self):
        for change in ('missing', 'duplicate', 'order', 'kind'):
            evidence = deepcopy(self.evidence)
            if change == 'missing':
                evidence['rejected_start_guards'].pop()
            elif change == 'duplicate':
                evidence['rejected_start_guards'][1] = deepcopy(evidence['rejected_start_guards'][0])
            elif change == 'order':
                evidence['rejected_start_guards'].reverse()
            else:
                evidence['rejected_start_guards'][2]['kind'] = 'ordinary'
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(evidence)
        for index in range(3):
            for flag in ('refused', 'ntte_key_preserved', 'state_preserved', 'artwork_preserved',
                         'actual_source_callback_rejected', 'rejected_source_cleanup_preserved'):
                evidence = deepcopy(self.evidence)
                evidence['rejected_start_guards'][index][flag] = False
                with self.subTest(index=index, flag=flag), self.assertRaises(AssertionError):
                    self.verify(evidence)

    def test_rejects_missing_dirty_owner_routes_or_unproven_native_art_restoration(self):
        for change in ('missing', 'duplicate', 'order', 'kind'):
            evidence = deepcopy(self.evidence)
            rows = evidence['interrupted_intro_restoration']
            if change == 'missing':
                rows.pop()
            elif change == 'duplicate':
                rows[1] = deepcopy(rows[0])
            elif change == 'order':
                rows.reverse()
            else:
                rows[1]['kind'] = 'destroyed-owner'
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(evidence)
        for index in range(2):
            for flag in ('actual_source_callback', 'owner_destroyed', 'name_path_preserved', 'all_native_pixels_restored',
                         'restored_before_active_query'):
                evidence = deepcopy(self.evidence)
                evidence['interrupted_intro_restoration'][index][flag] = False
                with self.subTest(index=index, flag=flag), self.assertRaises(AssertionError):
                    self.verify(evidence)

    def test_rejects_missing_wrong_or_unproven_dirty_and_restored_native_layers(self):
        for index in range(2):
            for family, flags in (('dirty_layers', ('authored_pixels_match', 'changed_from_native')),
                                  ('restored_layers', ('restored_pixels_match', 'restored_origin_match'))):
                for change in ('missing', 'duplicate', 'order', 'target', *flags):
                    evidence = deepcopy(self.evidence)
                    layers = evidence['interrupted_intro_restoration'][index][family]
                    if change == 'missing':
                        layers.pop()
                    elif change == 'duplicate':
                        layers[1] = deepcopy(layers[0])
                    elif change == 'order':
                        layers.reverse()
                    elif change == 'target':
                        layers[0]['target'] = 'sprNativeWrongLayer'
                    else:
                        layers[0][change] = False
                    with self.subTest(index=index, family=family, change=change), self.assertRaises(AssertionError):
                        self.verify(evidence)

    def test_rejects_missing_or_changed_interrupted_owner_restoration_captures(self):
        for route in ('ordinary', 'ntte', 'destroyed-owner'):
            for change in ('missing', 'changed'):
                with self.subTest(route=route, change=change), self.assertRaises(AssertionError):
                    self.verify(restoration_capture_change=(route, change))

    def test_rejects_missing_or_changed_real_native_intro_draw_captures(self):
        for change in ('missing', 'changed'):
            with self.subTest(change=change), self.assertRaises(AssertionError):
                self.verify(capture_change=change)

    def test_accepts_original_single_colour_name_art_without_weakening_exact_counts(self):
        accepted = self.verify()
        names = [row for row in accepted['resources'] if row['role'] == 'Name']
        self.assertEqual(len(names), 5)
        self.assertTrue(all(row['source_colours'] == row['expected_source_colours'] == 1 for row in names))
        for field in ('source_colours', 'expected_source_colours', 'source_ink', 'expected_source_ink', 'source_coverage'):
            evidence = deepcopy(self.evidence)
            name = next(row for row in evidence['resources'] if row['role'] == 'Name')
            name[field] += 1
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_missing_boss_role_alias_or_native_callback(self):
        for failure in ('boss', 'role', 'row', 'alias', 'callback', 'intro'):
            evidence = deepcopy(self.evidence)
            if failure == 'boss':
                evidence['resources'][0]['boss'] = 'OtherBoss'
            elif failure == 'role':
                evidence['resources'][0]['role'] = 'Main2'
            elif failure == 'row':
                evidence['resources'].pop()
            elif failure == 'alias':
                evidence['alias_count'] = 29
            elif failure == 'callback':
                evidence['intros'][0]['actual_source_callback'] = False
            else:
                evidence['intros'][1] = deepcopy(evidence['intros'][0])
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_empty_pixels_wrong_target_origin_or_missing_restoration(self):
        for failure in ('source_coverage', 'source_ink', 'source_colours', 'target', 'origin_x',
                        'replacement_pixels_match', 'replacement_origin_match', 'restored_pixels_match',
                        'restored_origin_match', 'source_nonempty', 'aliases_resolve'):
            evidence = deepcopy(self.evidence)
            evidence['resources'][0][failure] = 'WrongTarget' if failure == 'target' else 0
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence)

    def test_rejects_unproven_artwork_or_hardware_claims_and_missing_native_logs(self):
        for failure in ('physical_device_tested', 'missing_alias_rejected', 'control_ink', 'empty_coverage'):
            evidence = deepcopy(self.evidence)
            evidence[failure] = True if failure == 'physical_device_tested' else (1 if failure == 'empty_coverage' else 0)
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence)
        with self.assertRaises(AssertionError):
            self.verify(log_change=True)

    def test_rejects_forged_transparent_source_or_changed_expected_pixel_coverage(self):
        for failure in ('other_empty', 'placeholder_nonempty', 'expected', 'placeholder_dimensions'):
            evidence = deepcopy(self.evidence)
            manifest = deepcopy(self.manifest)
            placeholder = next(row for row in evidence['resources'] if row['boss'] == 'GraveyardBoss' and row['role'] == 'Main')
            if failure == 'other_empty':
                evidence['resources'][0].update(source_nonempty=False, authored_transparent=True, source_coverage=0)
            elif failure == 'placeholder_nonempty':
                placeholder.update(source_nonempty=True, authored_transparent=False, source_coverage=128)
            elif failure == 'expected':
                evidence['resources'][0]['expected_source_coverage'] += 1
            else:
                row = next(row for row in manifest['assets'] if row['boss'] == 'GraveyardBoss' and row['role'] == 'Main')
                row['width'] += 1
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(evidence, manifest=manifest)

    def test_rejects_supplement_manifest_without_complete_source_aliases_and_preserved_origins(self):
        for failure in ('count', 'alias', 'path', 'origin', 'base', 'role'):
            manifest = deepcopy(self.manifest)
            if failure == 'count':
                manifest['resource_count'] = 14
            elif failure == 'alias':
                manifest['assets'][0]['aliases'].pop()
            elif failure == 'path':
                manifest['assets'][0]['path'] = 'Other.png'
            elif failure == 'origin':
                manifest['assets'][0]['origin'][0] += 1
            elif failure == 'base':
                manifest['base_manifest_sha256'] = '0' * 64
            else:
                manifest['assets'][1]['role'] = 'Main'
            with self.subTest(failure=failure), self.assertRaises(AssertionError):
                self.verify(manifest=manifest)

if __name__ == '__main__':
    unittest.main()
