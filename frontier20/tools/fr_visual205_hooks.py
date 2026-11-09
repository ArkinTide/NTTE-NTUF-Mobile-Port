"""Bounded native video options, player outline and locked-crown repairs.

This module never regenerates the imported project or writes a project on
import. Native script resource registration is owned by the release driver.
"""
from pathlib import Path
import argparse
import json
import shutil

from fr_content_hooks import patch

ROOT = Path(__file__).resolve().parents[1]

OLD_PLAYER_OUTLINE = '''if instance_exists(CoopController) && UberCont.opt_outlines {
\tvar pinst = scr_playerinstance_find(index)
\t
\tif pinst {
\t\tgpu_set_fog(true, pinst.color, 0, 0)
\t\t
\t    draw_sprite_ext(sprite_index, image_index, x - 1, y, right, 1, _angle, c_white, 1)
\t    draw_sprite_ext(sprite_index, image_index, x + 1, y, right, 1, _angle, c_white, 1)
\t    draw_sprite_ext(sprite_index, image_index, x, y - 1, right, 1, _angle, c_white, 1)
\t    draw_sprite_ext(sprite_index, image_index, x, y + 1, right, 1, _angle, c_white, 1)
\t\t
\t    gpu_set_fog(0, 0, 0, 0)
\t}
}'''
PLAYER_OUTLINE = ('// FRONTIER VISUAL205 NATIVE PLAYER OUTLINE\n'
                  'scrFRVisual205PlayerOutline(sprite_index,image_index,x,y,right,1,_angle);')
OLD_UNLOCK_HINT = '''if string_length(unlock_hint) {
    var _message = string_hash_to_newline(loc(string_upper(unlock_hint)))
\t
\tdraw_align(fa_center, fa_middle)
\t
\tvar _width = string_width_pure(_message) * 0.5 + 8 + unlock_hint_pop,
\t\t_height = string_height_pure(_message) * 0.5 + 8,
\t\t_xpos = gui_w div 2, _ypos = gui_h - 30
\t
    draw_set_colour(c_tooltip)
    draw_roundrect_ext(
\t\t_xpos - _width, _ypos - _height,
\t\t_xpos + _width, _ypos + _height, 4, 4, 0)
\t
\tdraw_set_color(c_white)
\tdraw_text_nt(_xpos, _ypos + unlock_hint_pop, _message)
\t
\tdraw_align()
\t
\tunlock_hint_pop = approach(unlock_hint_pop, 0, timescale)
}'''
UNLOCK_HINT = '''if string_length(unlock_hint) {
    // FRONTIER VISUAL205 ACTUAL RICH-TEXT TOOLTIP
    scrFRVisual205UnlockDraw(unlock_hint,unlock_hint_pop);
    unlock_hint_pop = approach(unlock_hint_pop, 0, timescale)
}'''

SITES = (
    ('objects/Player/Draw_0.gml', OLD_PLAYER_OUTLINE, PLAYER_OUTLINE),
    ('objects/Menu/Draw_74.gml', OLD_UNLOCK_HINT, UNLOCK_HINT),
    ('objects/MenuOptions/Other_20.gml', 'scrNTTEFullMenuDefine();',
     'scrNTTEFullMenuDefine();\nscrFRVisual205Options(); // FRONTIER VISUAL205 VIDEO SETTINGS'),
    ('objects/MenuOptions/Other_20.gml', 'if global.player_color {',
     'if scrFRVisual205ColorConfigured() { // FRONTIER VISUAL205 EXPLICIT BLACK'),
    ('objects/MenuOptions/Other_20.gml', 'if !global.player_color {',
     'if !scrFRVisual205ColorConfigured() { // FRONTIER VISUAL205 PROFILE COLOR'),
    ('objects/MenuOptions/Create_0.gml', 'var _value = base_convert(real(_color), 10, 16)',
     'var _value = scrFRVisual205ColorHex(_color) // FRONTIER VISUAL205 SIX-DIGIT HEX'),
    ('scripts/scrOptionsUpdate/scrOptionsUpdate.gml',
     '\t\tif !opt_cursorcol\n\t\t\topt_cursorcol = c_white',
     '\t\tif !opt_cursorcol\n\t\t\topt_cursorcol = c_white\n'
     '\t\tscrFRVisual205ColorSync(); // FRONTIER VISUAL205 LOCAL LIVE COLOR'),
    ('scripts/scrDrawPlayerHUD/scrDrawPlayerHUD.gml',
     'var _healthbar_color = UberCont.opt_healthcol,',
     'var _healthbar_color = scrFRVisual205HealthColor(_player,UberCont.opt_healthcol), // FRONTIER VISUAL205 HUD COLOR'),
    ('scripts/scrNTTEFullOutlineOptionsNative/scrNTTEFullOutlineOptionsNative.gml',
     '    var _owner=scr_playerinstance_find(_index)\n    return is_struct(_owner)?_owner.color:c_white',
     '    return scrFRVisual205OwnerColor(_index) // FRONTIER VISUAL205 SHARED OWNER COLOR'),
    ('scripts/scrFRRaces/scrFRRaces.gml',
     'case "skin_lock":return scrFRRaceCall("race_skin_lock",[_value]);',
     'case "skin_lock":return _value==1?scrFRVisual205BubblesSkinLock():scrFRRaceCall("race_skin_lock",[_value]);'),
)


def rewrite(text, before, after, relative):
    text = text.replace('\r\n', '\n')
    if after in text:
        if text.count(after) != 1 or before in text.replace(after, '', 1):
            raise RuntimeError('Visual205 duplicated hook: ' + relative)
        return text
    if text.count(before) != 1:
        raise RuntimeError('Visual205 changed or ambiguous anchor: ' + relative)
    return text.replace(before, after, 1)


def apply(project, crown=True):
    project = Path(project).resolve()
    planned, originals = {}, {}
    for relative, before, after in SITES:
        path = project / relative
        if path.is_symlink() or not path.resolve().is_relative_to(project):
            raise RuntimeError('Visual205 path escapes project: ' + relative)
        original = path.read_bytes()
        originals.setdefault(path, original)
        text = planned.get(path, original.decode('utf-8-sig'))
        planned[path] = rewrite(text, before, after, relative)
    written = []
    try:
        for path, text in planned.items():
            if text != originals[path].decode('utf-8-sig').replace('\r\n', '\n'):
                written.append(path)
                path.write_text(text, 'utf8', newline='\n')
    except BaseException:
        for path in reversed(written):
            path.write_bytes(originals[path])
        raise
    if crown:
        from generate_frontier_menu_art import generate
        generate()
        resource = 'sprFRStormsLoadout'
        # This already-registered sprite retains its YY identity and origin.
        for png in (ROOT / 'native/menu-assets' / resource).rglob('*.png'):
            relative = png.relative_to(ROOT / 'native/menu-assets' / resource)
            target = project / 'sprites' / resource / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(png, target)
    return {'files_changed': [str(path.relative_to(project)) for path in written],
            'native_registration': {'visual205.gml': 'scrFrontier_visual205',
                                    'visual205_tests.gml': 'scrFrontier_visual205_tests'},
            'locked_crown_shape': 'transparent upstream StormsIdle nearest2x',
            'public_test_entry_changed': False}


def apply_tests(project):
    """Apply only after other agents' shared test-entry installers finish."""
    project = Path(project)
    patch(project, 'scripts/scrFrontier_tests/scrFrontier_tests.gml', 'VISUAL205 FOCUSED DRIVER',
          'if(fr_test_case=="visual205") {\n'
          '    if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;\n'
          '    if(++fr_test_ticks<45) return;\n'
          '    scrFRVisual205Tests();\n'
          '    scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
          '    game_end();return;\n'
          '}', anchor='function scrFRIntegrationTestStep() {')
    patch(project, 'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', 'VISUAL205 ENTRY',
          'if(scrNTTEFullSmokeAsyncCase("FrontierVisual205Tests")) '
          '{scrFRIntegrationTestStart("visual205");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', before=True)
    return {'case': 'FrontierVisual205Tests', 'kind': 'visual205'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--tests', action='store_true')
    args = parser.parse_args()
    print(json.dumps(apply_tests(args.project) if args.tests else apply(args.project), ensure_ascii=False, indent=2))
