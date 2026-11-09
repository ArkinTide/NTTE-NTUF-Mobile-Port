"""Prove test hooks are independent, bounded, idempotent and transactional."""
from pathlib import Path
import shutil
import re
import tempfile
import unittest
from unittest.mock import patch

import fr_quest_portal204_test_hooks as hook
import fr_quest_portal204_hooks as production
import fr_quest_portal205_test_hooks as vault205
import fr_quest_continue205_test_hooks as continue205


ROOT = Path(__file__).resolve().parents[1]


class QuestPortal204TestHooks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='frontier-quest-portal204-hooks-')
        self.project = Path(self.temporary.name) / 'project'
        self.paths = [row[0] for row in hook.SITES] + [hook.NATURAL, hook.CORPSE, hook.RECOVERY, hook.ENEMY, hook.CROWN, hook.LOCKED]
        self.paths.append('scripts/scrNTTEFullLairWorld/scrNTTEFullLairWorld.gml')
        for relative in self.paths:
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / 'staging/project' / relative, target)
            # Unit fixtures stay a pristine baseline even after root applies
            # production and test hooks to the real staging project.
            text = target.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
            # 2.0.5 readonly probes can nest inside the 2.0.4 owned blocks.
            # Unwrap their exact additions first so this installer unit test
            # still starts from its original source boundary.
            for module in (continue205, vault205):
                for path, before, after in reversed(module.SITES):
                    if relative != path:
                        continue
                    if after.startswith(before):
                        text = text.replace(after[len(before):], '')
                    elif after.endswith(before):
                        text = text.replace(after[:-len(before)], '')
                    else:
                        text = text.replace(after, before)
            for path, before, after, _ in hook.SITES:
                if relative == path:
                    if after.startswith(before):
                        text = text.replace(after[len(before):], '')
                    elif after.endswith(before):
                        text = text.replace(after[:-len(before)], '')
                    else:
                        text = text.replace(after, before)
            if relative == hook.NATURAL:
                for before, insertion, identity in reversed(hook.NATURAL_SITES):
                    after = (before + '\n' + hook.call_block(insertion, identity).rstrip('\n')
                             if identity in ('BEGIN', 'STEP', 'FINISH')
                             else hook.call_block(insertion, identity).rstrip('\n'))
                    text = text.replace(after, before)
            for call, identity in (
                ('scrFRQuestPortal204CorpseProbe("before");', 'CORPSE BEFORE'),
                ('scrFRQuestPortal204CorpseProbe("rejected");', 'CORPSE REJECT'),
                ('scrFRQuestPortal204CorpseProbe("passed");', 'CORPSE PASS'),
                ('    scrFRQuestPortal204RecoveryProbe();', 'RECOVERY'),
                ('scrFRQuestPortal204EnemyDeathProbe();', 'ENEMY DEATH'),
                ('scrFRQuestPortal204CrownCollisionProbe();', 'CROWN COLLISION'),
                ('    scrFRQuestPortal204UnlockedProbe();', 'NATIVE UNLOCK'),
            ):
                text = text.replace(hook.call_block(call, identity), '')
            text = re.sub(r'(?ms)^    // BEGIN FRONTIER QUEST PORTAL204 RECOVERY SCHEDULER\n.*?^    // END FRONTIER QUEST PORTAL204 RECOVERY SCHEDULER\n', '', text)
            text = re.sub(r'(?ms)^    // BEGIN FRONTIER QUEST PORTAL204 ORDINARY EXIT\n.*?^    // END FRONTIER QUEST PORTAL204 ORDINARY EXIT\n', '', text)
            target.write_text(text, encoding='utf8')

    def tearDown(self):
        self.temporary.cleanup()

    def snapshot(self):
        return {p.relative_to(self.project).as_posix(): p.read_bytes()
                for p in self.project.rglob('*') if p.is_file()}

    def test_independent_of_new_production_guard_and_idempotent(self):
        for path in self.project.rglob('*.gml'):
            text = path.read_text(encoding='utf-8-sig')
            # Baseline fixtures intentionally have neither consumer guard.
            self.assertNotIn('scrFRQuestPortal204Blocked()', text)
        result = hook.apply(self.project)
        self.assertEqual(8, len(result['changed_paths']))
        self.assertFalse(result['production_helper_required'])
        before = self.snapshot()
        self.assertEqual([], hook.apply(self.project)['changed_paths'])
        self.assertEqual(before, self.snapshot())
        for path in self.project.rglob('*.gml'):
            self.assertNotIn('scrFRQuestPortal204Blocked()', path.read_text(encoding='utf8'))

    def test_natural_test_changes_only_instrumentation_and_fixture_input_wait(self):
        target = self.project / hook.NATURAL
        original = target.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
        fixed = hook.natural_transform(original)
        for before, insertion, identity in reversed(hook.NATURAL_SITES):
            if identity in ('BEGIN', 'STEP', 'FINISH'):
                after = before + '\n' + hook.call_block(insertion, identity).rstrip('\n')
            else:
                after = hook.call_block(insertion, identity).rstrip('\n')
            fixed = fixed.replace(after, before, 1)
        self.assertEqual(original, fixed)

    def test_native_probes_do_not_replace_original_corpse_guard_or_portal_creation(self):
        original = (self.project / hook.CORPSE).read_text(encoding='utf-8-sig').replace('\r\n', '\n')
        fixed = hook.corpse_transform(original)
        self.assertEqual(1, fixed.count('scrFRQuestPortal204CorpseProbe("before")'))
        self.assertEqual(1, fixed.count('scrFRQuestPortal204CorpseProbe("rejected")'))
        self.assertEqual(1, fixed.count('scrFRQuestPortal204CorpseProbe("passed")'))
        self.assertEqual(original.count('instance_create(_portal_x, _portal_y, Portal)'),
                         fixed.count('instance_create(_portal_x, _portal_y, Portal)'))
        self.assertLess(fixed.index('scrFRQuestPortal204CorpseProbe("before")'), fixed.index(hook.CORPSE_BEFORE))
        self.assertLess(fixed.index('type = 1'), fixed.index('scrFRQuestPortal204CorpseProbe("passed")'))
        self.assertEqual(fixed, hook.corpse_transform(fixed))

    def test_changed_late_anchor_preflights_all_files_before_any_write(self):
        path = self.project / hook.CROWN
        path.write_text(path.read_text(encoding='utf8').replace('instance_destroy()', 'instance_destroy(id)'), encoding='utf8')
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, 'changed/partial'):
            hook.apply(self.project)
        self.assertEqual(before, self.snapshot())

    def test_duplicate_or_partial_markers_are_rejected(self):
        path = self.project / hook.NATURAL
        path.write_text(path.read_text(encoding='utf8') + '\n// FRONTIER QUEST PORTAL204 TEST BEGIN\n', encoding='utf8')
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, 'changed/partial'):
            hook.apply(self.project)
        self.assertEqual(before, self.snapshot())

    def test_write_failure_rolls_back_the_complete_project_transaction(self):
        before = self.snapshot()
        write_bytes = Path.write_bytes
        writes = [0]

        def fail_once(path, data):
            writes[0] += 1
            if writes[0] == 4:
                raise OSError('injected quest probe write failure')
            return write_bytes(path, data)

        with patch.object(Path, 'write_bytes', fail_once):
            with self.assertRaisesRegex(OSError, 'injected quest probe'):
                hook.apply(self.project)
        self.assertEqual(before, self.snapshot())

    def test_native_acceptance_observes_real_routes_and_activated_lifecycle(self):
        text = (ROOT / 'native/quest_portal204_tests.gml').read_text(encoding='utf8')
        self.assertIn('if(!scrFRQuestPortal204Blocked()) return;', text)
        self.assertIn('if(scrNTTEFullValue(GameCont,"fr_quest_portal205_active",false))', text)
        self.assertIn('_r.active_frames++;', text)
        self.assertIn('else _r.dormant_frames++;', text)
        self.assertIn('_r.active_frames>0 && _r.unblocked_locked_frames==0', text)
        self.assertIn('scrNTTEFullQuestStoredHubNaturalTests(_case.seed)', text)
        self.assertIn('scrNTTEFullQuestHubNaturalTests()', text)
        self.assertEqual(3, text.count('rate:30}'))
        self.assertEqual(3, text.count('rate:60}'))
        self.assertIn('scrNTTEPortalRecoveryAllowed()', text)
        self.assertIn('scrNTTEFullPortalBlocked()', text)
        self.assertIn('game_get_speed(gamespeed_fps)', text)
        self.assertIn('_r.final_unlock_wait_ticks>=90', text)
        self.assertIn('_observer.phase==6 && scrFRQuestPortal204HasHeldArtifact(_observer)', text)
        self.assertIn('_observer.want_pick=false;', text)
        self.assertLess(text.index('scrFRQuestPortal204Write(_s,"IN_PROGRESS"'),
                        text.index('assert(_r.locked_frames>0'))
        self.assertIn('Ordinary portal interrupted an activated Ultimate Quest', text)
        self.assertNotIn('instance_destroy(', text)

    def test_empty_witness_samples_active_claim_without_dropping_dormant_gaps(self):
        text = (ROOT / 'native/quest_portal204_tests.gml').read_text(encoding='utf8')
        self.assertIn('active_claim:scrNTTEFullValue(GameCont,"fr_quest_portal205_active",false)', text)
        start = text.index('if(_observer.phase==5 && _e.eligible && _e.hearts==0) {')
        stop = text.index('        } else if(_r.empty_run>0)', start)
        empty = text[start:stop]
        self.assertIn('_r.empty_run+=timescale;_r.eligible_empty_ticks+=timescale;', empty)
        self.assertIn('_r.eligible_empty_frames++;', empty)
        self.assertIn('if(_e.active_claim && is_undefined(_r.eligible_empty_witness))', empty)
        self.assertEqual(1, empty.count('_r.eligible_empty_witness=_e;'))
        self.assertIn('array_push(_r.empty_gaps,{before_merge:_i,', text)
        self.assertIn('ticks:max(_r.empty_run,_r.last_empty_run)', text)
        self.assertIn('_r.active_frames>0 && _r.unblocked_locked_frames==0', text)

    def test_dormant_vault_acceptance_retains_guardian_combat_and_ordinary_exit(self):
        production = (ROOT / 'native/quest_portal204.gml').read_text(encoding='utf8')
        begin = production.index('function scrFRQuestPortal204Blocked() {')
        end = production.index('\nfunction ', begin + 1)
        guard = production[begin:end]
        self.assertIn('return instance_exists(NTTEFullLockedHugeQuestChest)', guard)
        self.assertIn('&& instance_exists(GameCont)', guard)
        self.assertIn('&& scrNTTEFullValue(GameCont,"fr_quest_portal205_active",false)', guard)
        dormant = (ROOT / 'native/quest_portal205_tests.gml').read_text(encoding='utf8')
        self.assertIn('instance_exists(NTTEFullLockedHugeQuestChest) && !scrFRQuestPortal204Blocked()', dormant)
        self.assertIn('&& !scrNTTEFullValue(GameCont,"fr_quest_portal205_active",false)', dormant)
        self.assertIn('_s.row.dormant_frames++;', dormant)
        self.assertIn('array_length(_s.row.guardians_seen)==4', dormant)
        self.assertIn('_s.row.actual_shots>=5 && _s.row.corpse_attempts>0 && _s.row.corpse_passes>0', dormant)
        self.assertIn('with(Portal) if(type==1)', dormant)
        self.assertNotIn('instance_destroy(', dormant)

    def test_final_wait_keeps_source_combat_and_strict_eligible_gate_with_bounded_diagnostics(self):
        text = (ROOT / 'native/quest_portal204_tests.gml').read_text(encoding='utf8')
        start = text.index('if(_observer.phase==6 && scrFRQuestPortal204HasHeldArtifact(_observer)')
        stop = text.index('    if(_observer.phase!=9) return false;', start)
        wait = text[start:stop]
        self.assertIn('_r.final_wait_diagnostic_next+=30;', wait)
        self.assertIn('_r.final_wait_elapsed>=600 && _r.final_unlock_wait_ticks<90', wait)
        self.assertIn('scrFRQuestPortal204Fail(_s,', wait)
        self.assertIn('FR_QUEST_PORTAL204_WAIT ', wait)
        for key in ('eligibility:', 'heldpart_count:', 'player_chest_distance:',
                    'wait_elapsed:', 'eligible_wait_ticks:', 'pending_police:', 'enemy_count:',
                    'spawn_count:', 'source_combat_shots:', 'enemies:', 'spawns:', 'prevents:'):
            self.assertIn(key, wait)
        self.assertNotIn('instance_destroy(', wait)
        self.assertNotIn('alarm[', wait)
        self.assertEqual(1, wait.count('with(_observer) scrNTTEFullQuestHubNaturalShootEnemies();'))
        self.assertLess(wait.index('scrNTTEFullQuestHubNaturalShootEnemies();'),
                        wait.index('pending_police:scrFRPendingPoliceCount()'))
        self.assertNotIn('.hp=', wait)
        self.assertNotIn('final_unlock_wait_ticks+=', wait)

    def test_actual_unlock_probe_follows_real_owner_destruction_and_preserves_source(self):
        source = (self.project / hook.LOCKED).read_text(encoding='utf8')
        sources = {relative: (self.project / relative).read_text(encoding='utf8')
                   for relative in [row[0] for row in hook.SITES]
                   + [hook.NATURAL, hook.CORPSE, hook.RECOVERY, hook.ENEMY, hook.CROWN, hook.LOCKED]}
        fixed = hook.transforms(sources)[hook.LOCKED]
        probe = hook.call_block('    scrFRQuestPortal204UnlockedProbe();', 'NATIVE UNLOCK')
        self.assertEqual(source, fixed.replace(probe, '', 1))
        start = fixed.index('function scrNTTEFullLockedQuestUnlock(')
        stop = fixed.index('function scrNTTEFullLockedQuestStep()', start)
        unlock = fixed[start:stop]
        self.assertLess(unlock.index('instance_create(x,y,NTTEFullHugeQuestChest)'), unlock.index(probe))
        self.assertLess(unlock.index('instance_destroy(id,false)'), unlock.index(probe))
        self.assertLess(unlock.index(probe), unlock.index('return true'))

    def test_test_and_production_hooks_keep_probe_before_early_return_and_are_idempotent(self):
        hook.apply(self.project)
        production.apply(self.project)
        before = self.snapshot()
        self.assertEqual([], hook.apply(self.project)['changed_paths'])
        self.assertEqual([], production.apply(self.project)['changed_paths'])
        self.assertEqual(before, self.snapshot())
        text = (self.project / hook.RECOVERY).read_text(encoding='utf8')
        start = text.index('function scrNTTEAllyPortalStep() {')
        stop = text.index('// BEGIN FOLLOWUP73', start)
        recovery = text[start:stop]
        self.assertLess(recovery.index('scrFRQuestPortal204RecoveryProbe()'),
                        recovery.index('scrFRQuestPortal204Blocked()'))
        self.assertLess(recovery.index('scrFRQuestPortal204Blocked()'),
                        recovery.index('if (!global.is_server'))


if __name__ == '__main__':
    unittest.main()
