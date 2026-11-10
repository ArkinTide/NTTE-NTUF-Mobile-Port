"""Narrow fixes for feedback on the first 2.1.0 candidate; no source import."""
from apply_release210_repairs import ROOT, PROJECT, change
from install_native205 import apply


def script(name):
    return PROJECT / 'scripts' / name / (name+'.gml')


def inject_once(path, before, after, marker):
    if marker not in path.read_text('utf-8-sig'):
        change(path, before, after)


def main():
    change(ROOT/'native/content210.gml', 'click:scrFRContent210Toggle',
           'click:function(_opt){return scrFRContent210Toggle(_opt);}', count=2)
    # A neutral powder creep deliberately uses team1724 so fire can ignite it.
    # Preserve that mechanic while tracking which side launched the powder.
    powder=script('frCode_Frontier_Projectiles_mod_03d50e982e')
    change(powder, 'team = 1724;\n;\nhitid = [sprite_index, "GUNPOWDER"];',
           'team = 1724;\nfr_powder_team210 = other[$ "fr_powder_team210"]??(other[$ "team"]??team_none);\n;\nhitid = [sprite_index, "GUNPOWDER"];')
    change(ROOT/'native/hyperion_projectiles.gml',
           '    var _team=_shot[$ "team"]??team_none,_typ=_shot[$ "typ"]??0;',
           '    if(scrFRHyperionFriendly210(_shot)) return false;\n    var _team=_shot[$ "team"]??team_none,_typ=_shot[$ "typ"]??0;')
    change(ROOT/'native/hyperion_projectiles.gml',
           'return (_b[$ "team"]??team_none)==team_player;', 'return scrFRHyperionFriendly210(_b);')
    change(ROOT/'native/hyperion_projectiles.gml',
           'return (_a[$ "team"]??team_none)==team_player;', 'return scrFRHyperionFriendly210(_a);')
    change(ROOT/'native/hyperion_projectiles.gml',
           'function scrFRHyperionEnemyProjectile(_shot) {',
           'function scrFRHyperionFriendly210(_shot) {\n'
           '    var _team=_shot[$ "team"]??team_none;\n'
           '    return _team==team_player || (_team==1724\n'
           '        && (_shot[$ "fr_powder_team210"]??team_none)==team_player);\n'
           '}\nfunction scrFRHyperionEnemyProjectile(_shot) {')
    # Queue the authored area0 entry without overwriting the departing world.
    cyber=script('frCode_cyberspace_area_68cf57f4f0')
    change(cyber, 'area = scrFRAreaResolve("cyberspace");\n;\nsubarea = 0;',
           'fr_cyberspace_return210 = area;\nscrFRAreaSet("cyberspace",0);')
    old_return='return [scrNTTEFullValue(GameCont,"fr_cyberspace_return210",GameCont.lastarea), 1];'
    if old_return not in cyber.read_text('utf-8-sig'): old_return='return [GameCont.lastarea, 1];'
    change(cyber,old_return,'return [scrFRCyberspaceReturn210(), 1];')
    # Include the return area in the existing primitive GameCont continuation.
    change(script('scrNTTEFullSystems'),
           'return {schema:1,content210:',
           'return {schema:1,progress210:{blocked:scrFRProgress210Cheated(),slot:scrFRProgress210Slot(),cyberspace_return:scrNTTEFullValue(GameCont,"fr_cyberspace_return210",undefined)},content210:')
    change(script('scrNTTEFullSystems'), '    scrFRContent210Import(_state);',
           '    var _scope210=_state[$ "progress210"]??{};\n'
           '    GameCont.fr_progress210_blocked=scrNTTEFullValue(GameCont,"fr_progress210_blocked",false) || (_scope210[$ "blocked"]??false);\n'
           '    if((_scope210[$ "slot"]??-1)>=0) GameCont.fr_progress210_slot=_scope210.slot;\n'
           '    GameCont.fr_cyberspace_return210=_scope210[$ "cyberspace_return"]??undefined;\n'
           '    scrFRContent210Import(_state);')
    systems=script('scrNTTEFullSystems')
    change(systems, '    return scrNTTEFullValue(global.ntte_full_progress.unlocks,_key,_default)',
           '    return scrNTTEFullValue(scrFRProgress210State().unlocks,_key,_default)')
    change(systems, 'function scrNTTEFullUnlockSet(_key,_value=true) {',
           'function scrNTTEFullUnlockSet(_key,_value=true) {\n    if(!scrFRProgress210CanUnlock()) return false;')
    change(systems, '    variable_struct_set(global.ntte_full_progress.unlocks,_key,_value)',
           '    variable_struct_set(scrFRProgress210State().unlocks,_key,_value)')
    change(systems, '    return scrNTTEFullValue(global.ntte_full_progress.loadouts,_key,_default)',
           '    var _shared=string_pos("option:",_key)==1;\n'
           '    return scrNTTEFullValue(_shared?global.ntte_full_progress.loadouts:scrFRProgress210State().loadouts,_key,_default)')
    change(systems, '    variable_struct_set(global.ntte_full_progress.loadouts,_key,_value)',
           '    var _shared=string_pos("option:",_key)==1;\n'
           '    if(!_shared && !scrFRProgress210CanUnlock()) return false;\n'
           '    variable_struct_set(_shared?global.ntte_full_progress.loadouts:scrFRProgress210State().loadouts,_key,_value)')
    # All production direct stats accesses use the same progress domain.
    direct=['scrNTTEFullCrabbonePhysicalNative','scrNTTEFullCrabboneStackNative',
            'scrNTTEFullMenuNative','scrNTTEFullMenuStatsPresentationNative','scrNTTEFullPet',
            'scrNTTEFullPetCuz','scrNTTEFullRaceMenuDecorationNative','scrNTTEFullRace',
            'scrNTTEFullRaceProgressionNative','scrNTTEFullSkinNative']
    for name in direct:
        path=script(name)
        text=path.read_text('utf-8-sig')
        if 'global.ntte_full_progress.stats' in text:
            change(path,'global.ntte_full_progress.stats','scrFRProgress210State().stats',text.count('global.ntte_full_progress.stats'))
    # Achievement ledgers must not later promote slot-local content to normal.
    path=script('scrNTTEFullUnlockPresentation')
    text=path.read_text('utf-8-sig')
    before='global.ntte_full_progress'
    if before in text:
        change(path,before,'scrFRProgress210State()',text.count(before))
    # Source Frontier save getters/setters use separate per-slot data, while
    # options and unrelated libSaves modules keep their original behavior.
    path=script('frCode_libSaves_mod_06c031bb7a')
    inject_once(path,'function fr_dependencies_libSaves_mod_gml_save_get() {',
           'function fr_dependencies_libSaves_mod_gml_save_get() {\n'
           'if(scrFRProgress210SourceScoped(argument[0])) return scrFRProgress210SourceGet(argument[1],argument_count>2?argument[2]:noone);',
           'if(scrFRProgress210SourceScoped(argument[0]))')
    inject_once(path,'function fr_dependencies_libSaves_mod_gml_save_set(_frl__mod=undefined, _frl__name=undefined, _frl__value=undefined) {',
           'function fr_dependencies_libSaves_mod_gml_save_set(_frl__mod=undefined, _frl__name=undefined, _frl__value=undefined) {\n'
           'if(_frl__mod=="Frontier" && !scrFRProgress210CanUnlock()) return false;\n'
           'if(scrFRProgress210SourceScoped(_frl__mod)) return scrFRProgress210SourceSet(_frl__name,_frl__value);',
           'if(scrFRProgress210SourceScoped(_frl__mod)) return')
    inject_once(path,'function fr_dependencies_libSaves_mod_gml_save_reset(_frl__mod=undefined, _frl__lwo=undefined) {',
           'function fr_dependencies_libSaves_mod_gml_save_reset(_frl__mod=undefined, _frl__lwo=undefined) {\n'
           'if(scrFRProgress210SourceScoped(_frl__mod)) {\n'
           '    if(!scrFRProgress210CanUnlock()) return scrFRProgress210Frontier();\n'
           '    var _scope=scrFRProgress210State();_scope.frontier210=json_parse(json_stringify(_frl__lwo));\n'
           '    scrNTTEFullProgressSave();return _scope.frontier210;\n}',
           'if(scrFRProgress210SourceScoped(_frl__mod)) {')
    inject_once(ROOT/'native/legacy_api.gml','function scrFRSaveLoad(_module,_defaults=undefined,_merge_defaults=false) {',
           'function scrFRSaveLoad(_module,_defaults=undefined,_merge_defaults=false) {\n'
           '    if(scrFRProgress210SourceScoped(_module)) {\n'
           '        var _data=scrFRProgress210Frontier();\n'
           '        if(_merge_defaults) {\n'
           '            var _keys=variable_struct_get_names(_defaults);\n'
           '            for(var _i=0;_i<array_length(_keys);++_i)\n'
           '                if(!variable_struct_exists(_data,_keys[_i])) _data[$ _keys[_i]]=_defaults[$ _keys[_i]];\n'
           '        }\n'
           '        return _data;\n    }', 'if(scrFRProgress210SourceScoped(_module)) {')
    # Fishing discovers and records content in a second authored save module.
    # Scope both progress modules, while configuration modules remain shared.
    change(path,'scrFRProgress210SourceGet(argument[1],argument_count>2?argument[2]:noone);',
           'scrFRProgress210SourceGet(argument[1],argument_count>2?argument[2]:noone,argument[0]);')
    change(path,'if(_frl__mod=="Frontier" && !scrFRProgress210CanUnlock())',
           'if(scrFRProgress210ContentModule(_frl__mod) && !scrFRProgress210CanUnlock())')
    change(path,'scrFRProgress210SourceSet(_frl__name,_frl__value);',
           'scrFRProgress210SourceSet(_frl__name,_frl__value,_frl__mod);')
    change(path,'    if(!scrFRProgress210CanUnlock()) return scrFRProgress210Frontier();\n'
           '    var _scope=scrFRProgress210State();_scope.frontier210=json_parse(json_stringify(_frl__lwo));\n'
           '    scrNTTEFullProgressSave();return _scope.frontier210;',
           '    if(!scrFRProgress210CanUnlock()) return scrFRProgress210Frontier(_frl__mod);\n'
           '    var _scope=scrFRProgress210State(),_field=scrFRProgress210Field(_frl__mod);\n'
           '    _scope[$ _field]=json_parse(json_stringify(_frl__lwo));\n'
           '    scrNTTEFullProgressSave();return _scope[$ _field];')
    change(ROOT/'native/legacy_api.gml','var _data=scrFRProgress210Frontier();',
           'var _data=scrFRProgress210Frontier(_module);')
    # Guard both automatic gold storage and its lower-level native/source APIs.
    change(script('scrUnlocks'),'    if(scrGameIsCustomMode()) exit;',
           '    if(!scrFRProgress210CanStoreGold()) exit;')
    change(script('scrLoadoutMenuInit'),'function scr_loadout_race_set_stored_weapon(_race_id, _weapon_id) {',
           'function scr_loadout_race_set_stored_weapon(_race_id, _weapon_id) {\n    if(!scrFRProgress210CanStoreGold()) return false;')
    change(script('scrNTTEFullWeaponLoadoutNative'),'    if(scrGameIsCustomMode()) return false',
           '    if(!scrFRProgress210CanStoreGold()) return false')
    path=script('scrRaces')
    for signature in ['function scr_race_set_unlocked(_race, _unlocked = true) {',
                      'function scr_race_set_skin_unlocked(_race, _skin=SkinLetter.B, _unlock=true) {']:
        change(path,signature,signature+'\n    if(!scrFRProgress210CanUnlock()) return false;')
    change(path,'if(scrNTTEFullRaceNumeric(_race)>=0) scrNTTEFullUnlockSet(',
           'if(scrNTTEFullRaceNumeric(_race)>=0) return scrNTTEFullUnlockSet(')
    change(path,'if(scrNTTEFullRaceNumeric(_race)>=0 && _skin==1) scrNTTEFullUnlockSet(',
           'if(scrNTTEFullRaceNumeric(_race)>=0 && _skin==1) return scrNTTEFullUnlockSet(')
    change(path,'function scrRaceUnlock(_race) {\n\tif (scrGameIsCustomMode()) exit',
           'function scrRaceUnlock(_race) {\n'
           '    if(!scrFRProgress210CanUnlock()) return;\n'
           '    if(scrFRRaceIs(_race)) {scrFRRaceUnlockSet(true);return;}\n'
           '\tif (scrGameIsCustomMode() && scrNTTEFullRaceNumeric(_race)<0) exit')
    change(path,'function scrRaceUnlockSkin(_race, _skin_id) {\n\tif (scrGameIsCustomMode()) exit',
           'function scrRaceUnlockSkin(_race, _skin_id) {\n'
           '    if(!scrFRProgress210CanUnlock()) return;\n'
           '    if(scrFRRaceIs(_race)) {scrFRRaceUnlockSet(true,_skin_id);return;}\n'
           '\tif (scrGameIsCustomMode() && scrNTTEFullRaceNumeric(_race)<0 && _skin_id<200) exit')
    change(script('scrNTTEFullRace'),'case "lock":return "OPEN THE CHEST"',
           'case "lock":return scrNTTEUpdateText("OPEN THE SECRET CHEST","打开秘密宝箱")')
    change(PROJECT/'objects/Console/Step_0.gml','scrFRAchievementsAllowed210(); // FRONTIER210 CONSOLE RUN EXCLUSION',
           'scrFRAchievementsAllowed210();scrFRProgress210Cheated(); // FRONTIER210 CONSOLE RUN EXCLUSION')
    change(script('scrOptionsUpdate'),'scrFRAchievementsAllowed210(); // FRONTIER210 PRACTICE/CONSOLE EXCLUSION',
           'scrFRAchievementsAllowed210();scrFRProgress210Cheated(); // FRONTIER210 PRACTICE/CONSOLE EXCLUSION')
    change(script('scrNTTEFullSmoke'),'        if(scrNTTEFullSmokeAsyncCase("FrontierFeatures210Tests"))',
           '        if(scrNTTEFullSmokeAsyncCase("FrontierFollowup210Tests")) {scrFRIntegrationTestStart("followup210");return;}\n        if(scrNTTEFullSmokeAsyncCase("FrontierFeatures210Tests"))')
    driver='''    if(fr_test_case=="followup210") {
        if(!scrFRReadyTick() || ++fr_test_ticks<45) return;
        scrFRFollowup210Tests();
        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");
        game_end();return;
    }
'''
    for path in [ROOT/'native/tests.gml',script('scrFrontier_tests')]:
        change(path,'function scrFRIntegrationTestStep() {','function scrFRIntegrationTestStep() {\n'+driver)
    apply(PROJECT,{'progress210.gml':'scrFrontier_progress210',
                   'content210.gml':'scrFrontier_content210',
                   'hyperion_projectiles.gml':'scrFrontier_hyperion_projectiles',
                   'legacy_api.gml':'scrFrontier_legacy_api',
                   'cyberspace_revive.gml':'scrFrontier_cyberspace_revive',
                   'followup210_tests.gml':'scrFrontier_followup210_tests',
                   'menu_input204_tests.gml':'scrFrontier_menu_input204_tests',
                   'event_tests.gml':'scrFrontier_event_tests',
                   'content210_tests.gml':'scrFrontier_content210_tests',
                   'bluescreen_ui_tests.gml':'scrFrontier_bluescreen_ui_tests'})


if __name__=='__main__': main()
