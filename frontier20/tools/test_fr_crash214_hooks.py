"""Exercise214 source boundaries on copies; no build or source reimport."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import fr_crash214_hooks as hooks


ROOT = Path(__file__).resolve().parents[1]


class Crash214HooksTests(unittest.TestCase):
    def test_gold_exchange_uses_its_own_branch_index(self):
        original = '// retained\n' + hooks.GOLD_OLD + '\nretained_tail();\n'
        patched = hooks.transform_main(original)
        self.assertIn('if ((_frl__goldStationIndex >= 0))', patched)
        self.assertNotIn('_frl__statueIndex', patched)
        self.assertIn('_frl__goldStationIndex--', patched)
        self.assertEqual(patched, hooks.transform_main(patched))
        self.assertTrue(patched.startswith('// retained\n'))
        self.assertTrue(patched.endswith('retained_tail();\n'))

    def test_preheat_has_finally_and_only_visual_events(self):
        patched = hooks.transform_warmup('prefix\n' + hooks.WARM_OLD + '\nsuffix')
        self.assertIn('scrFRSpiralWarmCount214(timescale)', patched)
        self.assertIn('finally {global.time_scale=_fr_spiral_saved_dt214;}', patched)
        self.assertEqual(4, patched.count('event_perform(ev_step, 0)'))
        self.assertEqual(patched, hooks.transform_warmup(patched))
        self.assertNotIn('150 / timescale', patched)

    def test_native_scale_updates_are_validated_before_assignment(self):
        native = (ROOT / 'native/crash214.gml').read_text('utf8')
        self.assertLess(native.index('if(!(_sx>=0'), native.index('image_xscale=_sx'))
        self.assertLess(native.index('if(!(grow>=0'), native.index('var _grow='))
        self.assertIn('clamp(round(150/scrFRSpiralDelta214(_dt)),150,600)', native)
        patched = hooks.transform_step(hooks.STEP_OLD + '\nlanim += random(1);')
        self.assertIn('if(!scrFRSpiralAdvance214(_dt,_controller))', patched)
        self.assertNotIn('image_xscale +=', patched)
        self.assertTrue(patched.endswith('lanim += random(1);'))
        self.assertEqual(patched, hooks.transform_step(patched))

    def test_existing_screenshot_guards_are_present(self):
        self.assertEqual(4, len(hooks.audit_prior_guards(ROOT / 'staging/project')))

    def test_current_live_patches_are_complete_and_stable(self):
        project = ROOT / 'staging/project'
        paths = {
            next(project.glob('scripts/frCode_Frontier_Main_mod_*/*.gml')): hooks.transform_main,
            project / 'objects/SpiralCont/Create_0.gml': hooks.transform_warmup,
            project / 'objects/Spiral/Step_0.gml': hooks.transform_step,
        }
        for path, transform in paths.items():
            source = path.read_text('utf-8-sig')
            self.assertEqual(source, transform(source))

    def test_copy_install_preserves_encoding_and_is_atomic_on_anchor_mismatch(self):
        live = ROOT / 'staging/project'
        relatives = [next(live.glob('scripts/frCode_Frontier_Main_mod_*/*.gml')).relative_to(live),
                     Path('objects/SpiralCont/Create_0.gml'), Path('objects/Spiral/Step_0.gml'),
                     Path('scripts/scrFRActors/scrFRActors.gml'),
                     Path('scripts/scrOptionsUpdate/scrOptionsUpdate.gml'),
                     next(live.glob('scripts/frCode_Frontier_Projectiles2_mod_*/*.gml')).relative_to(live),
                     Path('scripts/scrNTTESolidWalls/scrNTTESolidWalls.gml')]
        for bom in (b'', b'\xef\xbb\xbf'):
            for newline in ('\n', '\r\n'):
                with self.subTest(bom=bool(bom), newline=newline), TemporaryDirectory() as folder:
                    project = Path(folder)
                    for relative in relatives:
                        path = project / relative
                        path.parent.mkdir(parents=True, exist_ok=True)
                        source = (live / relative).read_text('utf-8-sig')
                        for before, after in ((hooks.GOLD_OLD, hooks.GOLD_NEW),
                                              (hooks.WARM_OLD, hooks.WARM_NEW),
                                              (hooks.STEP_OLD, hooks.STEP_NEW)):
                            source = source.replace(after, before)
                        path.write_bytes(bom+source.replace('\n', newline).encode('utf8'))
                    hooks.apply(project)
                    snapshot = {rel: (project / rel).read_bytes() for rel in relatives}
                    hooks.apply(project)
                    self.assertEqual(snapshot, {rel: (project / rel).read_bytes() for rel in relatives})
                    for data in snapshot.values():
                        self.assertEqual(bool(bom), data.startswith(b'\xef\xbb\xbf'))
                        if newline == '\r\n':
                            self.assertNotIn(b'\n', data.replace(b'\r\n', b''))
                    bad = project / 'objects/Spiral/Step_0.gml'
                    bad.write_bytes(bad.read_bytes().replace(b'scrFRSpiralAdvance214', b'renamed_callback'))
                    before = {rel: (project / rel).read_bytes() for rel in relatives}
                    with self.assertRaises(RuntimeError):
                        hooks.apply(project)
                    self.assertEqual(before, {rel: (project / rel).read_bytes() for rel in relatives})


if __name__ == '__main__':
    unittest.main()
