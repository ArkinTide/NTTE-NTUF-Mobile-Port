from pathlib import Path
import unittest

import fr_perf214_hooks as hooks


class Performance214HooksTests(unittest.TestCase):
    def test_hooks_preserve_fallback_and_are_idempotent(self):
        text = ('function scrFRInstanceExists(_target) {\n    return original_exists(_target);\n}\n'
                'function scrFRInstanceNumber(_target) {\n    return original_number(_target);\n}\n'
                'function scrFRInstanceIs(_target,_type) {\n    return original_is(_target,_type);\n}\n')
        actual = hooks.transform(text)
        self.assertEqual(hooks.transform(actual), actual)
        for fallback in ('original_exists(_target)', 'original_number(_target)', 'original_is(_target,_type)'):
            self.assertIn(fallback, actual)
        self.assertEqual(actual.count('if(!is_undefined(_fast214)) return _fast214;'), 3)

    def test_unreviewed_boundary_is_rejected_before_write(self):
        with self.assertRaises(AssertionError):
            hooks.transform('function scrFRInstanceExists(different_signature) {}')

    def test_maintained_and_staged_predicates_match(self):
        native = (hooks.ROOT / 'native/actors.gml').read_text('utf-8-sig')
        staged = (hooks.ROOT / 'staging/project/scripts/scrFRActors/scrFRActors.gml').read_text('utf-8-sig')
        for name in ('scrFRInstanceExists', 'scrFRInstanceNumber', 'scrFRInstanceIs'):
            for text in (native, staged):
                start = text.index('function ' + name + '(')
                end = text.index('\n}', start) + 2
                self.assertIn('FRONTIER214 FRESH PROJECTILE FAMILY QUERY', text[start:end])
        # The implementation deliberately retains fresh native ancestry and
        # live pickup mask/creator checks instead of any frame membership cache.
        source = (hooks.ROOT / 'native/performance214.gml').read_text('utf8')
        self.assertIn('scrFRIsThrownWeapon', source)
        self.assertNotIn('current_frame', source)


if __name__ == '__main__':
    unittest.main()
