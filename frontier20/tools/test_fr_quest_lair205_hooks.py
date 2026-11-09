"""Preflight/rollback and coexistence for the real-evidence quest/Lair repairs."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

import fr_quest_portal205_hooks as quest
import fr_lair_return205_hooks as lair
import fr_quest_portal205_test_hooks as vault_tests
import fr_lair_return205_test_hooks as lair_tests
import fr_quest_continue205_test_hooks as continue_tests

ROOT = Path(__file__).resolve().parents[1]
MODULES = (quest, lair, vault_tests, lair_tests, continue_tests)


class QuestLair205HooksTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix='frontier-quest-lair205-')
        self.project = Path(self.temp.name)
        self.relatives = sorted({row[0] for module in MODULES for row in module.SITES})
        for relative in self.relatives:
            text = (ROOT / 'staging/project' / relative).read_text('utf-8-sig').replace('\r\n', '\n')
            # Keep fixture valid whether the parent has already integrated the
            # production repair. Independent readonly test hooks may remain.
            for module in (lair, quest):
                for site, before, after in reversed(module.SITES):
                    if site == relative:
                        text = text.replace(after, before)
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, 'utf8')

    def tearDown(self):
        self.temp.cleanup()

    def snapshot(self):
        return {relative: (self.project / relative).read_bytes() for relative in self.relatives}

    def test_production_and_readonly_test_hooks_coexist_in_both_orders(self):
        for module in MODULES:
            module.apply(self.project)
        before = self.snapshot()
        for module in reversed(MODULES):
            self.assertEqual([], module.apply(self.project)['changed_paths'])
        self.assertEqual(before, self.snapshot())
        text = (self.project / quest.LOCKED).read_text('utf8')
        self.assertEqual(1, text.count('scrFRQuestPortal205RestoreChest(id);'))
        text = (self.project / lair.LAIR).read_text('utf8')
        self.assertEqual(1, text.count('scrFRLairReturn205ReleasePlayer(_v,x,y)) { }'))

    def test_late_changed_anchor_preflights_before_any_write(self):
        target = self.project / quest.ROOM_END
        target.write_text(target.read_text('utf8').replace(
            'scrNTTEFullGuardianEscapeRoomEndBegin();', 'changed_room_end_anchor();'), 'utf8')
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, 'anchor changed'):
            quest.apply(self.project)
        self.assertEqual(before, self.snapshot())

    def test_partial_owned_marker_is_rejected_before_any_write(self):
        target = self.project / lair.LAIR
        target.write_text(target.read_text('utf8') +
                          '\n// FRONTIER LAIR RETURN205 RELEASE PRIOR LIVE SALVAGE\n', 'utf8')
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, 'partial or moved'):
            lair.apply(self.project)
        self.assertEqual(before, self.snapshot())

    def test_second_file_write_failure_rolls_back_first_file(self):
        before = self.snapshot()
        original = Path.write_bytes
        writes = 0

        def fail_second(path, data):
            nonlocal writes
            writes += 1
            if writes == 2:
                raise OSError('injected second-file failure')
            return original(path, data)

        with patch.object(Path, 'write_bytes', fail_second):
            with self.assertRaisesRegex(OSError, 'injected second-file'):
                quest.apply(self.project)
        self.assertEqual(before, self.snapshot())

    def test_player_release_retains_native_deep_hazard_and_checks_real_masks(self):
        original = (self.project / lair.LAIR).read_text('utf8')
        lair.apply(self.project)
        fixed = (self.project / lair.LAIR).read_text('utf8')
        lethal = ('if (_v.y>y+64 && instance_is(_v,hitme) && _v.hp>0) {\n'
                  '                    _v.hp=0')
        self.assertIn(lethal, original)
        self.assertIn(lethal, fixed)
        self.assertLess(fixed.index(lethal), fixed.index('else if (scrFRLairReturn205ReleasePlayer(_v,x,y))'))
        for _, before, after in reversed(lair.SITES):
            fixed = fixed.replace(after, before, 1)
        self.assertEqual(original, fixed)
        native = (ROOT / 'native/lair_return205.gml').read_text('utf8')
        self.assertIn('with(Floor)', native)
        self.assertIn('!scrNTTEFullPlayerWallMeeting(_cx,_cy)', native)
        self.assertIn('!place_meeting(_cx,_cy,InvisiWall)', native)
        self.assertIn('if(_best==infinity) return false;', native)
        self.assertIn('_edge_y-24', native)
        self.assertNotIn('instance_create(', native)
        self.assertNotIn('instance_destroy(', native)


if __name__ == '__main__':
    unittest.main()
