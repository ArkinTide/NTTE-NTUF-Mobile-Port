"""Narrow, repeatable 2.1.0 repairs on the current maintained stage."""
from pathlib import Path
import json
import shutil
from install_native205 import apply as install

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'staging/project'


def change(path, before, after, count=1):
    path = Path(path)
    raw = path.read_bytes()
    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    if after in text:
        assert text.count(after) == count, 'Duplicate 210 patch: ' + str(path)
        return
    assert text.count(before) == count, 'Changed 210 anchor: ' + str(path)
    text = text.replace(before, after)
    nl = '\r\n' if b'\r\n' in raw else '\n'
    bom = b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b''
    path.write_bytes(bom + text.replace('\n', nl).encode('utf8'))


def main():
    change(PROJECT/'scripts/scrNTTEState/scrNTTEState.gml',
           'function scrNTTEDrawStatus() {',
           'function scrNTTEDrawStatus() {\n    scrFRChargeBars210Draw(); // FRONTIER210 SOURCE CHARGE HUD')
    change(PROJECT/'scripts/scrAchievementUnlock/scrAchievementUnlock.gml',
           'if (scrGameIsCustomMode()) exit', 'if (!scrFRAchievementsAllowed210()) exit // FRONTIER210 ACHIEVEMENTS')
    change(PROJECT/'scripts/scrNTTEFullUnlockPresentation/scrNTTEFullUnlockPresentation.gml',
           'if(scrGameIsCustomMode()) {', 'if(!scrFRAchievementsAllowed210()) { // FRONTIER210 ACHIEVEMENT EXCLUSION')
    change(PROJECT/'scripts/scrNTTEFullUnlockPresentation/scrNTTEFullUnlockPresentation.gml',
           '["OPEN THE CHEST", "打开宝箱"]', '["OPEN THE CHEST", "打开秘密宝箱"]')
    change(PROJECT/'scripts/scrNTTEFullSystems/scrNTTEFullSystems.gml',
           'return {schema:1,skills:GameCont.ntte_full_skills,',
           'return {schema:1,achievements_blocked210:!scrFRAchievementsAllowed210(),skills:GameCont.ntte_full_skills,')
    change(PROJECT/'scripts/scrNTTEFullSystems/scrNTTEFullSystems.gml',
           '    GameCont.ntte_full_skills=_state.skills',
           '    GameCont.fr_achievements_blocked210=scrNTTEFullValue(GameCont,"fr_achievements_blocked210",false) || (_state[$ "achievements_blocked210"]??false);\n    GameCont.ntte_full_skills=_state.skills')
    change(PROJECT/'objects/Console/Step_0.gml',
           'if (global.console_active && !prev_active) _ai_submit = false',
           'if (global.console_active && !prev_active) _ai_submit = false\nscrFRAchievementsAllowed210(); // FRONTIER210 CONSOLE RUN EXCLUSION')
    change(PROJECT/'scripts/scrOptionsUpdate/scrOptionsUpdate.gml',
           'if (opt_orig_console) opt_console = true',
           'if (opt_orig_console) opt_console = true\n        scrFRAchievementsAllowed210(); // FRONTIER210 PRACTICE/CONSOLE EXCLUSION')
    change(ROOT/'tools/generate_frontier_menu_art.py',
           "shade = Image.new('L', unlocked.size, 40)",
           "shade = Image.new('L', unlocked.size, 66) # Match sprLockedLoadoutCrown exactly")
    change(ROOT/'tools/generate_frontier_menu_art.py',
           'native RGB40 silhouette', 'native RGB66 silhouette')
    change(ROOT/'native/visual205_tests.gml',
           'make_color_rgb(40,40,40)', 'make_color_rgb(66,66,66)')
    driver='''    if(fr_test_case=="features210") {
        if(!scrFRReadyTick() || ++fr_test_ticks<45) return;
        scrFRFeatures210Tests();
        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");
        game_end();return;
    }
'''
    for path in (ROOT/'native/tests.gml', PROJECT/'scripts/scrFrontier_tests/scrFrontier_tests.gml'):
        change(path, 'function scrFRIntegrationTestStep() {',
               'function scrFRIntegrationTestStep() {\n'+driver)
    change(PROJECT/'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml',
           '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))',
           '        if(scrNTTEFullSmokeAsyncCase("FrontierFeatures210Tests")) {scrFRIntegrationTestStart("features210");return;}\n        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))')
    mapping={'features210.gml':'scrFrontier_features210', 'features210_tests.gml':'scrFrontier_features210_tests',
             'visual205_tests.gml':'scrFrontier_visual205_tests'}
    install(PROJECT, mapping)
    from generate_frontier_menu_art import generate
    generate()
    src=ROOT/'native/menu-assets/sprFRStormsLoadout'
    for file in src.rglob('*.png'):
        target=PROJECT/'sprites/sprFRStormsLoadout'/file.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file,target)
    print(json.dumps({'registered':mapping,'status':'partial implementation; tests pending'},indent=2))


if __name__ == '__main__':
    main()
