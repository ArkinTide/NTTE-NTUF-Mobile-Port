"""Content-wide activation gates, independent of source metadata availability."""
from pathlib import Path
from apply_release210_repairs import ROOT, PROJECT, change
from install_native205 import apply as install


def both(name, before, after, stage=None):
    paths=[ROOT/'native'/f'{name}.gml',PROJECT/'scripts'/(stage or 'scrFrontier_'+name)/((stage or 'scrFrontier_'+name)+'.gml')]
    for path in paths:
        change(path,before,after)


def main():
    both('offline_lib',
         'return variable_global_exists("fr_enabled") && global.fr_enabled && instance_exists(FRWorld);',
         'return scrFRContent210RuntimeReady() && scrFRContent210Active("ntuf");')
    both('offline_lib','    scrFRRuntimeInit();',
         '    global.fr_content210_ntuf=true; // Bootstrap source settings before applying the saved content switch.\n    scrFRRuntimeInit();')
    both('offline_lib','function scrFRWorldStep() {',
         'function scrFRWorldStep() {\n    scrFRContent210Sync(); // FRONTIER210 CONTENT LIFECYCLE')
    both('options','    if(!scrFREnabled()) return;\n    scrOptionsMenuCategoryBegin(OptionCategory.Frontier);',
         '    if(!scrFRContent210RuntimeReady()) return;\n    scrOptionsMenuCategoryBegin(OptionCategory.Frontier);')
    both('options','    scrOptionsMenuCategoryEnd();\n    var _main=options[OptionCategory.Main]',
         '    scrOptionsMenuCategoryEnd();\n    scrFRContent210Options(); // FRONTIER210 CONTENT SETTINGS\n    var _main=options[OptionCategory.Main]')
    both('skills','function scrFRSkillAvailable(_skill) {',
         'function scrFRSkillAvailable(_skill) {\n    if(!scrFREnabled()) return false; // FRONTIER210 CONTENT POOL')
    both('skills','    if(is_undefined(_key)) return scr_skill_get(_skill);',
         '    if(is_undefined(_key)) return scr_skill_get(_skill);\n    if(!scrFRContent210Active("ntuf")) return 0; // FRONTIER210 OWNED SKILL GATE')
    both('crowns','return variable_global_exists("fr_enabled") && global.fr_enabled\n',
         'return scrFREnabled()\n')
    for name,ret in [('scrFRNTTESpriteOverride','undefined'),('scrFRNTTENativeSprite','_sprite'),
                     ('scrFRNTTEWeaponSprite','undefined'),('scrFRNTTEStatueSprites','undefined'),
                     ('scrFRNTTEScorchSprites','undefined')]:
        import re
        path=ROOT/'native/ntte_compat.gml'
        text=path.read_text('utf-8-sig')
        signature=re.search(r'function '+name+r'\([^\n]*?\) \{',text).group()
        both('ntte_compat',signature,signature+'\n    if(!scrFRContent210Active("ntuf")) return '+ret+'; // FRONTIER210 NTTE RESTORE')
    both('ntte_compat','function scrFRNTTEExists(_type,_module) {return scrFRNTTEHandles(_type,_module);}',
         'function scrFRNTTEExists(_type,_module) {\n    if(!scrFRContent210Active("undergrowth") && (_module=="undergrowth" || string_pos("fossil ",string(_module))==1)) return false;\n    return scrFRNTTEHandles(_type,_module);\n}')
    both('legacy_api','function scrFRSoundResolve(_sound) {',
         'function scrFRSoundResolve(_sound) {\n    if(!scrFRContent210Active("ntuf")) return _sound; // FRONTIER210 ORIGINAL SOUND')
    both('menu_repairs','            array_push(groups[group_count-1],_weapon);continue;',
         '            if(scrFRContent210Active("ntuf")) array_push(groups[group_count-1],_weapon);continue;')
    both('menu_repairs','    for(var _weapon=1;_weapon<=maxwep;++_weapon) {',
         '    for(var _weapon=1;_weapon<=maxwep;++_weapon) {\n        if(!scrFRContent210WeaponEnabled(_weapon)) continue;')
    # NTTE's own Undergrowth remains independent from the Frontier runtime.
    for func in ['scrUGRoomStart','scrUGAfterGeneration']:
        path=PROJECT/'scripts/scrUndergrowthArea/scrUndergrowthArea.gml'
        change(path,'function '+func+'() {','function '+func+'() {\n    if(!scrFRContent210Active("undergrowth")) return; // FRONTIER210 CONTENT GATE')
    path=PROJECT/'scripts/scr_weapon_get_type/scr_weapon_get_type.gml'
    change(path,'function scr_weapon_is_valid(_weapon) {',
           'function scr_weapon_is_valid(_weapon) {\n    if(!scrFRContent210WeaponEnabled(_weapon)) return false; // FRONTIER210 CONTENT GATE')
    change(path,'function scr_weapon_get_area(_weapon) {',
           'function scr_weapon_get_area(_weapon) {\n    if(!scrFRContent210WeaponEnabled(_weapon)) return -1; // FRONTIER210 CONTENT GATE')
    path=PROJECT/'scripts/scrNTTEFullWeaponDrop/scrNTTEFullWeaponDrop.gml'
    change(path,'function scrNTTEFullWeaponDropArea(_raw,_context) {',
           'function scrNTTEFullWeaponDropArea(_raw,_context) {\n    if(!scrFRContent210Active("undergrowth") && array_contains(["fossil pistol","fossil gun","fossil cannon","fossil hammer","mega grenade launcher",174,175,176,177,178],_raw)) return -1; // FRONTIER210 CONTENT GATE')
    # Always remember achievement exclusion while a game is active, including
    # pause options and console opening on a non-award frame.
    path=PROJECT/'objects/GameCont/Step_0.gml'
    text=path.read_text('utf-8-sig')
    marker='scrFRAchievementsAllowed210(); // FRONTIER210 RUN ELIGIBILITY\n'
    if marker not in text: path.write_text(marker+text,encoding='utf8')
    install(PROJECT,{'content210.gml':'scrFrontier_content210'})


if __name__=='__main__': main()
