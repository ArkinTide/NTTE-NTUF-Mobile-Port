"""Narrow content lifecycle boundary fixes; no source reimport."""
from apply_release210_repairs import ROOT, PROJECT, change
from install_native205 import apply


def main():
    for path in [ROOT/'native/offline_lib.gml', PROJECT/'scripts/scrFrontier_offline_lib/scrFrontier_offline_lib.gml']:
        change(path, 'function scrFRSessionPrepare() {\n    if(!scrFREnabled()) return;',
               'function scrFRSessionPrepare() {\n    if(!scrFRContent210RuntimeReady()) return;\n    scrFRContent210Wake();')
        change(path, 'function scrFRSessionRetired(_retain_game=false) {\n    if(!scrFREnabled()) return;',
               'function scrFRSessionRetired(_retain_game=false) {\n    if(!scrFRContent210RuntimeReady()) return;')
    path=PROJECT/'scripts/scrGamePause/scrGamePause.gml'
    change(path,'\tinstance_activate_all()','\tinstance_activate_all()\n    scrFRContent210Suspend(); // FRONTIER210 DISABLED CONTENT AFTER UNPAUSE')
    path=PROJECT/'scripts/scrRunStart/scrRunStart.gml'
    change(path,'function scrRunStart() {','function scrRunStart() {\n    scrFRContent210NewRun(); // FRONTIER210 RETRY AND NEW GAME')
    path=PROJECT/'scripts/PlayerInstance/PlayerInstance.gml'
    change(path,'        // FRONTIER SKIN STARTER:',
           '        scrFRContent210Selections(); // FRONTIER210 VALIDATE RANDOM LOADOUT TOO\n        // FRONTIER SKIN STARTER:')
    for path in [ROOT/'native/actors.gml',PROJECT/'scripts/scrFRActors/scrFRActors.gml']:
        change(path,'function scrFRActorDraw() {','function scrFRActorDraw() {\n    if(!scrFRContent210Active("ntuf")) return; // FRONTIER210 HIDDEN CONTENT')
    for path in [ROOT/'native/areas.gml',PROJECT/'scripts/scrFrontier_areas/scrFrontier_areas.gml']:
        change(path,'        var _found=false;\n        for(var _j=0;_j<array_length(_areas);++_j)',
               '        if((_extra[_i]>=301 && !scrFRContent210Active("ntuf"))\n            || (_extra[_i]==207 && !scrFRContent210Active("undergrowth"))) continue; // FRONTIER210 AREA POOL\n        var _found=false;\n        for(var _j=0;_j<array_length(_areas);++_j)')
    path=PROJECT/'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml'
    change(path,'        if(scrNTTEFullSmokeAsyncCase("FrontierFeatures210Tests"))',
           '        if(scrNTTEFullSmokeAsyncCase("FrontierContent210Tests")) {scrFRIntegrationTestStart("content210");return;}\n        if(scrNTTEFullSmokeAsyncCase("FrontierFeatures210Tests"))')
    for path in [ROOT/'native/tests.gml',PROJECT/'scripts/scrFrontier_tests/scrFrontier_tests.gml']:
        change(path,'function scrFRIntegrationTestStep() {',
               'function scrFRIntegrationTestStep() {\n    if(fr_test_case=="content210") {\n        if(scrFRContent210TestsStep(id)) {\n            scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n            game_end();\n        }\n        return;\n    }')
    path=PROJECT/'objects/UberCont/Step_0.gml'
    change(path,'    scrFRRestartTestsObserve();','    scrFRRestartTestsObserve();\n    scrFRContent210TestsObserve();')
    apply(PROJECT,{'content210.gml':'scrFrontier_content210',
                   'content210_tests.gml':'scrFrontier_content210_tests',
                   'features210_tests.gml':'scrFrontier_features210_tests'})


if __name__=='__main__': main()
