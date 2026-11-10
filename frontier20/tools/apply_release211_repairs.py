"""Repeatable narrow2.1.1 changes; never re-import the Frontier stage."""
from pathlib import Path
import hashlib
import json
import re
from apply_release210_repairs import ROOT, PROJECT, change
from install_native205 import apply


def script(name):
    return PROJECT/'scripts'/name/(name+'.gml')


def native(name, stage=None):
    return [ROOT/'native'/(name+'.gml'), script(stage or 'scrFrontier_'+name)]


def each(paths, before, after, count=1):
    for path in paths:
        change(path,before,after,count)


def install_once():
    # Save the exact pre-change text receipts once; never rewrite old evidence.
    proof=ROOT/'review/release211-prepatch.json'
    if not proof.exists():
        files=[*sorted((ROOT/'native').glob('*.gml')),
               *sorted((PROJECT/'scripts').glob('*/*.gml')),
               *sorted((PROJECT/'objects').glob('*/*.gml'))]
        proof.write_text(json.dumps({str(p.relative_to(ROOT)).replace('\\','/'):
            hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2),'utf8')
    each(native('content210'),
         'function scrFRContent210WeaponEnabled(_weapon) {\n    var _part=scrNTTEFullWeaponModel(_weapon),_depth=0;',
         'function scrFRContent210WeaponEnabled(_weapon) {\n'
         '    var _ntuf=scrFRContent210Active("ntuf"),_ug=scrFRContent210Active("undergrowth");\n'
         '    if(_ntuf && _ug) return true; // FRONTIER211 COMMON CONTENT HOT PATH\n'
         '    var _part=scrNTTEFullWeaponModel(_weapon),_depth=0;')
    each(native('content210'),
         '        if(_raw>=174 && _raw<=178 && !scrFRContent210Active("undergrowth")) return false;\n'
         '        if(variable_global_exists("fr_weapon_keys") && !is_undefined(global.fr_weapon_keys[$ string(_raw)])\n'
         '            && !scrFRContent210Active("ntuf")) return false;',
         '        if(!scrFRContent211RawEnabled(_raw,_ntuf,_ug)) return false;')
    each(native('content210'),'if(!scrFRContent210WeaponEnabled(_p.cwep)) _p.cwep=wep_revolver;',
         'if(!scrFRContent210WeaponEnabled(_p.cwep)) _p.cwep=scrFRContent211Starter(_p.race,_p.skin);')
    each(native('content210'),'if(!scrFRContent210WeaponEnabled(_p.bwep)) _p.bwep=wep_none;',
         'if(!scrFRContent210WeaponEnabled(_p.bwep)) _p.bwep=scrFRContent211Starter(_p.race,_p.skin);')
    each(native('content210'),
         '    global.fr_content210_undergrowth=scrFRContent210Requested("undergrowth");\n'
         '    scrFRContent210Apply(scrFRContent210Requested("ntuf"));\n'
         '    scrFRContent210Selections();\n}',
         '    global.fr_content210_undergrowth=scrFRContent210Requested("undergrowth");\n'
         '    scrFRContent210Apply(scrFRContent210Requested("ntuf"));\n'
         '    scrFRContent211Presets();\n'
         '    scrFRContent210Selections();\n}',count=2)
    each(native('content210'),
         '    global.fr_content210_undergrowth=scrFRContent210Requested("undergrowth");\n'
         '    scrFRContent210Apply(scrFRContent210Requested("ntuf"));\n'
         '    scrFRContent211Presets();\n'
         '    scrFRContent210Selections();\n}\nfunction scrFRContent210Toggle',
         '    var _ntuf=scrFRContent210Requested("ntuf"),_ug=scrFRContent210Requested("undergrowth"),\n'
         '        _menu=instance_find(Menu,0),_custom=scrNTTEFullValue(UberCont,"custom_options",-1);\n'
         '    if(scrNTTEFullValue(FRWorld,"fr_sync211_menu",-1)==_menu\n'
         '        && scrNTTEFullValue(FRWorld,"fr_sync211_custom",-1)==_custom\n'
         '        && scrNTTEFullValue(FRWorld,"fr_sync211_ntuf",undefined)==_ntuf\n'
         '        && scrNTTEFullValue(FRWorld,"fr_sync211_ug",undefined)==_ug\n'
         '        && scrFRContent210Active("ntuf")==_ntuf && scrFRContent210Active("undergrowth")==_ug) return;\n'
         '    global.fr_content210_undergrowth=_ug;scrFRContent210Apply(_ntuf);\n'
         '    scrFRContent211Presets();scrFRContent210Selections();\n'
         '    if(instance_exists(Menu)) with(Menu) scrFRContent211BuildSelect();\n'
         '    FRWorld.fr_sync211_menu=_menu;FRWorld.fr_sync211_custom=_custom;\n'
         '    FRWorld.fr_sync211_ntuf=_ntuf;FRWorld.fr_sync211_ug=_ug;\n'
         '}\nfunction scrFRContent210Toggle')
    # Preserve the native layout and event consumers; add/remove pack-owned
    # entries instead of treating disabled content as another locked character.
    menu=PROJECT/'objects/Menu/Create_0.gml'
    text=menu.read_text('utf-8-sig')
    if 'scrFRContent211BuildSelect();' not in text:
        start=text.index('var _slot_index = 0,')
        stop=text.index('\n\n#endregion',start)
        body=text[start:stop]
        body=body.replace('for(var _race_id = Race.Random; _race_id < Race.NUM_ALL_RACE_TYPES; ++_race_id) {',
            'for(var _race_id = Race.Random; _race_id < Race.NUM_ALL_RACE_TYPES; ++_race_id) {\n'
            '    if(!scrFRContent211RaceVisible(_race_id)) continue;')
        source=ROOT/'native/content211.gml'
        source.write_text(source.read_text('utf8')+'\nfunction scrFRContent211BuildSelect() {\n'
            '    var _go=instance_find(GoButton,0),_show=instance_exists(_go) && _go.visible;\n'
            '    with(CharSelect) instance_destroy();\n    with(GoButton) instance_destroy();\n'
            +body+'\n    with(GoButton) visible=_show;\n'
            '    if(!scrFRContent211RaceVisible(race)) race=Race.Fish;\n}\n','utf8')
        change(menu,text[start:stop],'scrFRContent211BuildSelect();')
    change(PROJECT/'objects/DrawStats/Create_0.gml',
         'for(var _race_id = Race.Random; _race_id < Race.NUM_ALL_RACE_TYPES; ++_race_id) {',
         'for(var _race_id = Race.Random; _race_id < Race.NUM_ALL_RACE_TYPES; ++_race_id) {\n'
         '    if(!scrFRContent211RaceVisible(_race_id)) continue; // FRONTIER211 CONTENT STATISTICS')
    change(ROOT/'native/menu_repairs.gml','function scrFRMenuStatistics() {',
         'function scrFRMenuStatistics() {\n    if(!scrFRContent210Active("ntuf")) return; // FRONTIER211 HIDDEN PACK')
    # Both loaded presets and value readers protect menus opened before the
    # source library completes bootstrap. The fallback remains a race-default
    # sentinel, so Chicken, Rogue, Beetle and Random get their own starters.
    change(script('CustomMode'),'return variable_struct_get(UberCont.custom_options, _key)',
         'return scrFRContent211CustomWeapon(_key,variable_struct_get(UberCont.custom_options, _key))')
    change(PROJECT/'objects/MenuOptions/Other_20.gml',
         'var _weapon = scrCustomParam(_key), _sprite;',
         'var _weapon = scrCustomParam(_key), _sprite = sprCustomModeWeaponDefault; // FRONTIER211 TOTAL ICON FALLBACK')
    change(script('scrLoadoutMenuInit'),'\t\treturn _cwep\n',
         '\t\treturn scrFRContent210WeaponEnabled(_cwep)?_cwep:scrFRContent211Starter(_race_id)\n')
    # Stop the native Undergrowth factory itself, including source-module
    # direct calls, instead of relying solely on its optional-mod probes.
    change(script('scrUndergrowthNative'),'function scrUGCreate(_x,_y,_name) {',
         'function scrUGCreate(_x,_y,_name) {\n    if(!scrFRContent210Active("undergrowth")) return noone; // FRONTIER211 ALL UG FACTORIES')
    for signature in ['function scrUGDrawTop() {','function scrUGDark(_gray,_vx,_vy) {',
                      'function scrUGBloom() {','function scrUGShadows(_vx,_vy) {',
                      'function scrUGWeaponStep() {']:
        change(script('scrUndergrowthNative'),signature,signature+'\n    if(!scrFRContent210Active("undergrowth")) return; // FRONTIER211 UG RUNTIME')
    # Source room callbacks can also be called through registered modules.
    for signature in ['function scrUG_area_pop_extras() {','function scrUG_area_pop_enemies() {',
                      'function scrUG_area_pop_props() {']:
        change(script('scrUndergrowthCallbacks'),signature,
               signature+'\n    if(!scrFRContent210Active("undergrowth")) return; // FRONTIER211 SOURCE AREA GATE')
    # Keep actor captures at main quality through EVERY intermediate pass.
    # Minor quality remains available for water/foam/background caches.
    water=script('scrNTTEFullCoastSea')
    change(water,'var _sizes=[[2*(_w+32),2*(_h+32),_minor]',
         'var _actors=max(1,_main); // FRONTIER211 KEEP ACTOR TEXELS THROUGH COMPOSITOR\n'
         '    var _sizes=[[2*(_w+32),2*(_h+32),_minor]')
    change(water,'[_w+16,_h+16,_minor],[_w+16,_h+16,_minor],[_w,_h,_minor],[_w,_h,_main],[_w,_h,_main],[_w,_h,_minor]]',
         '[_w+16,_h+16,_minor],[_w+16,_h+16,_minor],[_w,_h,_actors],[_w,_h,_actors],[_w,_h,_actors],[_w,_h,_actors]]')
    # Blue controller Step/Draw and buttons now share their anchor. Drawing
    # runs even on 60Hz host frames with no30Hz source logic tick.
    cyber=script('frCode_cyberspace_area_68cf57f4f0')
    for signature in ['function fr_Areas_cyberspace_area_gml_bluescreen_step() {',
                      'function fr_Areas_cyberspace_area_gml_bluescreen_draw() {']:
        change(cyber,signature,signature+'\nscrFRBluescreen211Align();')
    change(cyber,'fr_Areas_cyberspace_area_gml_BluescreenButton_create((x - 87), (y + 51), __fr_other1,',
         'fr_Areas_cyberspace_area_gml_BluescreenButton_create((x - 87), (y + 51), id,')
    change(cyber,'fr_Areas_cyberspace_area_gml_BluescreenButton_create((x - 16), (y + 51), __fr_other2,',
         'fr_Areas_cyberspace_area_gml_BluescreenButton_create((x - 16), (y + 51), id,')
    # Native achievements were gated; authored NTTE/NTUF unlock notices were
    # still queuing independently after the rejected permanent save.
    change(script('scrNTTEFullUnlockPresentation'),
         'function scrNTTEFullUnlockSplat(_name,_text,_sprite,_sound) {',
         'function scrNTTEFullUnlockSplat(_name,_text,_sprite,_sound) {\n'
         '    if(!scrFRProgress210CanUnlock()) return {nam:["",""],txt:"",spr:-1,img:0,snd:-1}; // FRONTIER211 NO CHEAT NOTICES')
    source_saves=script('frCode_libSaves_mod_06c031bb7a')
    for function in ['unlock_popup','unlock_splat','unlock_splat_ext']:
        text=source_saves.read_text('utf-8-sig')
        signature=re.search(r'function fr_dependencies_libSaves_mod_gml_'+function+r'\([^\n]*\) \{',text).group()
        change(source_saves,signature,signature+'\nif(!scrFRProgress210CanUnlock()) return {nam:["",""],txt:"",spr:-1,img:0,snd:-1}; // FRONTIER211 NO CHEAT NOTICES')
    # Do not inherit a preceding object's black colour or partial alpha.
    change(script('scrNTTEFullUnlockPresentation'),
         'try {\n// Epsilon native UnlockScreen',
         'try {\nif(!scrFRProgress210CanUnlock()) return;\ndraw_set_color(c_white);draw_set_alpha(1);\n// Epsilon native UnlockScreen')
    change(ROOT/'native/unlock_hooks.gml','    try {\n        if(scrFRUnlockPresentationContext() && unlock_delay<=0',
         '    try {\n        if(!scrFRProgress210CanUnlock()) return;\n'
         '        draw_set_color(c_white);draw_set_alpha(1);\n'
         '        if(scrFRUnlockPresentationContext() && unlock_delay<=0')
    change(PROJECT/'objects/AchievementSplash/Other_10.gml',
         'if instance_exists(Spiral) || !(ok && index > 0.4) exit',
         'if(!scrFRAchievementsAllowed210()) exit // FRONTIER211 HIDE QUEUED CHEAT ACHIEVEMENT\n'
         'if instance_exists(Spiral) || !(ok && index > 0.4) exit')
    # Exercise the new production paths through a separate native case.
    change(script('scrNTTEFullSmoke'),'        if(scrNTTEFullSmokeAsyncCase("FrontierFollowup210Tests"))',
         '        if(scrNTTEFullSmokeAsyncCase("FrontierRepairs211Tests")) {scrFRIntegrationTestStart("repairs211");return;}\n'
         '        if(scrNTTEFullSmokeAsyncCase("FrontierFollowup210Tests"))')
    driver='''    if(fr_test_case=="repairs211") {
        if(!scrFRReadyTick() || ++fr_test_ticks<45) return;
        scrFRRepairs211Tests();
        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");
        game_end();return;
    }
'''
    each(native('tests'),'function scrFRIntegrationTestStep() {',
         'function scrFRIntegrationTestStep() {\n'+driver)
    apply(PROJECT,{'content210.gml':'scrFrontier_content210','content211.gml':'scrFrontier_content211',
                   'repairs211_tests.gml':'scrFrontier_repairs211_tests',
                   'menu_repairs.gml':'scrFrontier_menu_repairs','unlock_hooks.gml':'scrFrontier_unlock_hooks'})
    print(json.dumps({'version':'2.1.1','status':'installed; runtime verification pending'}))


def main():
    if not script('scrFrontier_repairs211_tests').is_file():
        install_once()
    # The baseline transformations compose (e.g. Sync replaces an earlier
    # NewRun-shaped anchor). Repeated installs verify the final boundary and
    # only synchronize explicitly maintained native scripts.
    assert 'FRONTIER211 TOTAL ICON FALLBACK' in (PROJECT/'objects/MenuOptions/Other_20.gml').read_text('utf-8-sig')
    change(script('scrNTTEFullSmoke'),'        if(scrNTTEFullSmokeAsyncCase("FrontierRepairs211Tests"))',
         '        if(scrNTTEFullSmokeAsyncCase("FrontierRender211Tests")) {scrFRIntegrationTestStart("render211");return;}\n'
         '        if(scrNTTEFullSmokeAsyncCase("FrontierRepairs211Tests"))')
    driver='''    if(fr_test_case=="render211") {
        if(!scrFRReadyTick() || ++fr_test_ticks<45) return;
        scrFRRender211Tests();
        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");
        game_end();return;
    }
'''
    each(native('tests'),'function scrFRIntegrationTestStep() {',
         'function scrFRIntegrationTestStep() {\n'+driver)
    # Existing test expectations follow the new required actor-quality
    # contract. Background/foam must still obey the minor-quality selector.
    visual=script('scrNTTEFullVisualOptionsNativeTests')
    change(visual,'_expected=(_i==5 || _i==6)?_main:_minor',
         '_expected=_i>=4?max(1,_main):_minor')
    change(visual,'assert(_sea.ntte_coast_surfaces[7].scale==5.25',
         'assert(_sea.ntte_coast_surfaces[7].scale==max(1,_main)')
    # Include the actual final icon's lower edge, instead of throwing away
    # overflow whenever the old partial-row height was shorter than the GUI.
    selector=PROJECT/'objects/CustomModeSkillSelector/Other_10.gml'
    change(selector,'\t_mx = gui_x,\n\t_my = gui_y,',
           '\t_mx = scrFRTouchX(0),\n\t_my = scrFRTouchY(0),')
    change(selector,'\t_ypos = 0,','\t_ypos = 0, _last_ypos211 = 0,')
    change(selector,'\tvar _dx = _drawx,','\t_last_ypos211 = _ypos;\n\tvar _dx = _drawx,')
    change(selector,'height = _ypos + LETTERBOX_SIZE + 16\nif ((height - _height) < 20) height = 0',
           'height = _start_y + _last_ypos211 + _half_h + 8; // FRONTIER211 COMPLETE LAST ROW')
    change(selector,'mouse_ui_clicked()','scrFRCustom211Clicked()',2)
    menu=PROJECT/'objects/MenuOptions/Other_10.gml'
    change(menu,'\t\tother.scroll_max = max(0, (height - (gui_h div 2) - LETTERBOX_SIZE) div 2)',
           '\t\tif(object_index==CustomModeSkillSelector)\n'
           '\t\t\tother.scroll_max = max(0, (height - (gui_h - LETTERBOX_SIZE - 8)) / 2); // FRONTIER211 SKILL SCROLL\n'
           '\t\telse other.scroll_max = max(0, (height - (gui_h div 2) - LETTERBOX_SIZE) div 2)')
    change(menu,'\t#region Slider element','\tif(instance_exists(CustomModeSkillSelector)) scroll=clamp(scroll,scroll_min,scroll_max);\n\t#region Slider element')
    # Same host slider artwork and drag dispatch. Touch helpers are identical
    # native calls in shipping; desktop-only smoke samples can exercise them.
    change(menu,'if is_undefined(slider) && mouse_check_button(mb_left) {',
           'if is_undefined(slider) && (instance_exists(CustomModeSkillSelector)?scrFRCustom211Held():mouse_check_button(mb_left)) {')
    change(menu,'if (!device_mouse_check_button(i, mb_left)) continue',
           'if (!scrFRTouchHeld(i)) continue')
    change(menu,'var mx = device_mouse_x_to_gui(i),\n\t\t\t\tmy = device_mouse_y_to_gui(i)',
           'var mx = scrFRTouchX(i),\n\t\t\t\tmy = scrFRTouchY(i)')
    change(menu,'var _slider_size = 80,\n\t\t_slider_bottom = view_height - _slider_size,',
           'var _slider_size = 80,\n'
           '\t\t_slider_w211 = instance_exists(CustomModeSkillSelector)?gui_w:view_width,\n'
           '\t\t_slider_h211 = instance_exists(CustomModeSkillSelector)?gui_h:view_height,\n'
           '\t\t_slider_bottom = _slider_h211 - _slider_size,')
    change(menu,'draw_sprite_ext(sprOptionSlider, 0, view_width - 16, 36,',
           'draw_sprite_ext(sprOptionSlider, 0, _slider_w211 - 16, 36,')
    change(menu,'view_width - 20 + (dragging > 0), 40 + _slider_bottom * _progress,',
           '_slider_w211 - 20 + (dragging > 0), 40 + _slider_bottom * _progress,')
    change(menu,'if (mx >= view_width - 32 && mx <= view_width) || dragging {',
           'if (mx >= _slider_w211 - 32 && mx <= _slider_w211) || dragging {')
    apply(PROJECT,{'content210.gml':'scrFrontier_content210','content211.gml':'scrFrontier_content211',
                   'repairs211_tests.gml':'scrFrontier_repairs211_tests','render211_tests.gml':'scrFrontier_render211_tests',
                   'menu_repairs.gml':'scrFrontier_menu_repairs','unlock_hooks.gml':'scrFrontier_unlock_hooks',
                   'tests.gml':'scrFrontier_tests','restart_tests.gml':'scrFrontier_restart_tests'})
    print(json.dumps({'version':'2.1.1','status':'narrow install complete; runtime verification pending'}))


if __name__=='__main__': main()
