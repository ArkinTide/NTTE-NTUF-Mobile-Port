"""Narrow menu hook installation on copies, including fail-before-write."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import fr_menus214_hooks as hooks


ROOT = Path(__file__).resolve().parents[1]
OBJECTS = 'scripts/frCode_Frontier_Objects_mod_fixture/module.gml'
CYBER = 'scripts/frCode_cyberspace_area_fixture/module.gml'
GUI = 'objects/UberCont/Draw_75.gml'
PREF = 'objects/MenuOptions/Other_10.gml'


class Menus214HooksTests(unittest.TestCase):
    def make_project(self, folder, newline='\n', bom=b''):
        project = Path(folder)
        texts = {OBJECTS: hooks.SURGERY_OLD,
                 CYBER: hooks.CONTROLLER_OLD + '\n' + hooks.CLICK_OLD + '\nauthored_accept_or_deny();\n}',
                 GUI: hooks.GUI_OLD, PREF: hooks.PREFERENCE_OLD}
        for relative, source in texts.items():
            path = project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(bom + ('// untouched before\n' + source + '\n// untouched after\n')
                             .replace('\n', newline).encode('utf8'))
        return project

    def test_surgery_replaces_fixed_latin_metrics_and_preserves_disposal(self):
        result = hooks.transform_surgery(hooks.SURGERY_OLD)
        self.assertIn('scrFRSurgery214Draw(_frl__x,_frl__y,_frl__surgeryName,_frl__description)', result)
        self.assertEqual(1, result.count('scrFRInstanceDestroy();'))
        self.assertNotIn('16 * round', result)
        self.assertEqual(result, hooks.transform_surgery(result))

    def test_robot_preserves_authored_decision_while_committing_once(self):
        original = hooks.CONTROLLER_OLD + '\n' + hooks.CLICK_OLD + '\nreal_authored_choice();\n}'
        result = hooks.transform_cyberspace(original)
        self.assertIn('on_step = scrFRBluescreen214ControllerStep', result)
        self.assertIn('if(!scrFRBluescreen214CommitChoice(creator)) return;', result)
        self.assertIn('if ((yesButton == true)) {\nreal_authored_choice();', result)
        self.assertEqual(result, hooks.transform_cyberspace(result))

    def test_preference_hook_keeps_the_native_value_column_and_click_lifecycle(self):
        original = ('native_mouse_and_toggle();\n' + hooks.PREFERENCE_OLD
                    + '\nnative_value_column();\nnative_switch_draw();')
        result = hooks.transform_preferences(original)
        self.assertIn(hooks.PREFERENCE_NEW, result)
        self.assertIn('native_mouse_and_toggle();', result)
        self.assertIn('native_value_column();\nnative_switch_draw();', result)
        self.assertEqual(result, hooks.transform_preferences(result))

    def test_apply_preserves_bom_newlines_and_is_idempotent(self):
        for newline in ('\n', '\r\n'):
            for bom in (b'', b'\xef\xbb\xbf'):
                with self.subTest(newline=newline, bom=bool(bom)), TemporaryDirectory() as folder:
                    project = self.make_project(folder, newline, bom)
                    hooks.apply(project)
                    first = {p: (project / p).read_bytes() for p in (OBJECTS, CYBER, GUI, PREF)}
                    hooks.apply(project)
                    self.assertEqual(first, {p: (project / p).read_bytes() for p in first})
                    for data in first.values():
                        self.assertEqual(bool(bom), data.startswith(b'\xef\xbb\xbf'))
                        if newline == '\r\n':
                            self.assertNotIn(b'\n', data.replace(b'\r\n', b''))
                        else:
                            self.assertNotIn(b'\r\n', data)
                        self.assertIn(b'// untouched before', data)
                        self.assertIn(b'// untouched after', data)

    def test_changed_source_and_partial_hooks_fail_before_any_write(self):
        for relative, before, after in (
            (OBJECTS, 'draw_set_font(fntSmall)', 'changed_font()'),
            (CYBER, 'if ((yesButton == true))', 'if (different_choice)'),
            (GUI, 'FRONTIER212', 'OTHER211'),
            (PREF, 'loc(_name)', 'different_name'),
        ):
            with self.subTest(path=relative), TemporaryDirectory() as folder:
                project = self.make_project(folder)
                path = project / relative
                path.write_text(path.read_text('utf8').replace(before, after, 1), 'utf8')
                saved = {p: (project / p).read_bytes() for p in (OBJECTS, CYBER, GUI, PREF)}
                with self.assertRaises(RuntimeError):
                    hooks.apply(project)
                self.assertEqual(saved, {p: (project / p).read_bytes() for p in saved})

    def test_native_sources_use_actual_cjk_metrics_and_complete_gui_matrix_scope(self):
        source = (ROOT / 'native/menus214.gml').read_text('utf8')
        self.assertIn('scrFROptionText(_description,"",false)', source)
        self.assertIn('render_parse_text(_wrapped_body)', source)
        self.assertIn('draw_set_font(_cjk?fntCJK:fntSmall)', source)
        self.assertIn('draw_set_halign(fa_center);draw_set_valign(fa_top)', source)
        self.assertIn('matrix_set(matrix_view,camera_get_view_mat(_camera))', source)
        self.assertIn('matrix_set(matrix_projection,camera_get_proj_mat(_camera))', source)
        self.assertIn('matrix_set(matrix_world,_world);matrix_set(matrix_view,_view)', source)
        self.assertIn('matrix_set(matrix_projection,_projection)', source)


if __name__ == '__main__':
    unittest.main()
