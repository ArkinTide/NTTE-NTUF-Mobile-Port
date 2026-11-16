import json
import tempfile
import unittest
from pathlib import Path

import fr_perf213_hooks as hooks


class Performance213HooksTests(unittest.TestCase):
    def make_objects(self, rows):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for name, parent, slots in rows:
            path = root / 'objects' / name / (name + '.yy')
            path.parent.mkdir(parents=True)
            obj = {'name': name, 'parentObjectId': {'name': parent} if parent else None,
                   'eventList': [{'eventType': 2, 'eventNum': i} for i in slots]}
            path.write_text(json.dumps(obj), 'utf8')
        return root

    def test_timer_slots_include_transitive_inheritance_and_no_duplicates(self):
        root = self.make_objects([('Base', None, [0, 10]), ('Child', 'Base', [0, 4]),
                                  ('Leaf', 'Child', []), ('Floor', None, [])])
        self.assertEqual(hooks.alarm_slots(root),
                         {'Base': [0, 10], 'Child': [0, 4, 10], 'Floor': [], 'Leaf': [0, 4, 10]})
        generated = hooks.alarm_source(root)
        self.assertIn('_slots[Floor]=[];', generated)
        self.assertIn('_slots[Leaf]=[0,4,10];', generated)
        self.assertEqual(generated, hooks.alarm_source(root))

    def test_cycle_and_invalid_alarm_rejected(self):
        root = self.make_objects([('A', 'B', []), ('B', 'A', [])])
        with self.assertRaises(AssertionError):
            hooks.alarm_slots(root)
        root = self.make_objects([('Bad', None, [12])])
        with self.assertRaises(AssertionError):
            hooks.alarm_source(root)

    def test_exact_transformation_is_idempotent_and_rejects_drift(self):
        before = 'before\nneedle\nafter'
        output = hooks.replace_once(before, 'needle', 'repaired')
        self.assertEqual(output, 'before\nrepaired\nafter')
        self.assertEqual(hooks.replace_once(output, 'needle', 'repaired'), output)
        with self.assertRaises(AssertionError):
            hooks.replace_once('drift', 'needle', 'repaired')

    def test_staged_alarm_table_matches_every_exact_native_event(self):
        source = hooks.alarm_source(hooks.PROJECT)
        self.assertEqual(source, (hooks.ROOT / 'native/alarms213.gml').read_text('utf8'))
        rows = hooks.alarm_slots(hooks.PROJECT)
        self.assertIn(10, rows['Player'])
        self.assertNotIn(11, rows['Player'])
        self.assertEqual(rows['Floor'], [])
        self.assertEqual(rows['FRCustomObject'], [])


if __name__ == '__main__':
    unittest.main()
