"""Narrow Blizzard and menu-audio regression entry points."""
from pathlib import Path
from fr_content_hooks import patch


def optimize_aurora(project):
    paths=list((project/"scripts").glob("frCode_Frontier_Events_mod_*/*.gml"))
    assert len(paths)==1, "Frontier event module is ambiguous"
    path=paths[0]
    text=path.read_text(encoding="utf-8-sig")
    anchor="function fr_Frontier_Events_mod_gml_Aurora_applysprites() {"
    body="if(!scrFRWeatherSourceOracle()) {scrFRAuroraApplySprites();return;}"
    if body not in text:
        assert text.count(anchor)==1, "Aurora apply source entry changed"
        text=text.replace(anchor,anchor+"\n// FRONTIER AURORA DIRECT LIVE MARKERS\n"+body,1)
        path.write_text(text,encoding="utf8")


def apply(project):
    project = Path(project)
    optimize_aurora(project)
    # This case intentionally observes the real application intro instead of
    # the smoke world's synthetic GameCont. All other smoke cases still skip it.
    boot_path = project / "objects/Vlambeer/Create_0.gml"
    boot_text = boot_path.read_text(encoding="utf-8-sig")
    boot_old = 'if (global.ntte_smoke_active) { instance_destroy(); exit }'
    boot_new = 'if (global.ntte_smoke_active && !scrFRMenuAudioBootTestsSelected()) { instance_destroy(); exit }'
    if boot_new not in boot_text:
        assert boot_text.count(boot_old) == 1, "Cold-boot smoke guard changed"
        boot_path.write_text(boot_text.replace(boot_old, boot_new, 1), encoding="utf8")
    patch(project, "scripts/scrFrontier_tests/scrFrontier_tests.gml", "BLIZZARD TEST DRIVER",
          'if(fr_test_case=="blizzard-perf") {\n'
          '    if(!scrFRReadyTick()) return;\n'
          '    if(instance_exists(GenCont) || instance_exists(FloorMaker)) return;\n'
          '    if(++fr_test_ticks<45) return;\n'
          '    scrFRBlizzardPerformanceTests();\n'
          '    scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
          '    game_end();return;\n'
          '}', anchor="function scrFRIntegrationTestStep() {")
    patch(project, "scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml", "BLIZZARD TEST ENTRY",
          'if(scrNTTEFullSmokeAsyncCase("FrontierBlizzardTests")) {scrFRIntegrationTestStart("blizzard-perf");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', before=True)
    patch(project, "scripts/scrNTTESmoke/scrNTTESmoke.gml", "MENU AUDIO COLD BOOT",
          'if(scrFRMenuAudioBootTestsSelected()) {\n'
          '    scrFRMenuAudioBootTestsStep(id);return;\n'
          '}',anchor='    if (phase==0) {',before=True)
    patch(project, "scripts/scrFrontier_tests/scrFrontier_tests.gml", "MENU AUDIO COLD BOOT DRIVER",
          'if(fr_test_case=="menu_audio_boot") {scrFRMenuAudioBootTestsStep(id);return;}',
          anchor='function scrFRIntegrationTestStep() {')
    patch(project, "scripts/scrFrontier_tests/scrFrontier_tests.gml", "BLIZZARD LIVE TEST DRIVER",
          'if(fr_test_case=="blizzard-live") {\n'
          '    if(!variable_instance_exists(id,"fr_blizzard_live")) {\n'
          '        if(!scrFRReadyTick()) return;\n'
          '        if(++fr_test_ticks<45) return;\n'
          '        scrFRBlizzardLiveTestsStart(id);return;\n'
          '    }\n'
          '    if(scrFRBlizzardLiveTestsStep(id)) {\n'
          '        scrNTTESmokeLog("PASS FRONTIER actual live Blizzard component/count diagnostics");\n'
          '        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
          '        game_end();\n'
          '    }return;\n'
          '}',anchor='function scrFRIntegrationTestStep() {')
    patch(project, "scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml", "BLIZZARD LIVE TEST ENTRY",
          'if(scrNTTEFullSmokeAsyncCase("FrontierBlizzardLiveTests")) {scrFRIntegrationTestStart("blizzard-live");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))',before=True)
    patch(project,"scripts/scrFrontier_tests/scrFrontier_tests.gml","AURORA NATIVE TEST DRIVER",
          'if(fr_test_case=="aurora-native") {\n'
          '    if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;\n'
          '    if(++fr_test_ticks<45) return;\n'
          '    scrFRAuroraPerformanceTests();\n'
          '    scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
          '    game_end();return;\n'
          '}',anchor='function scrFRIntegrationTestStep() {')
    patch(project,"scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml","AURORA NATIVE TEST ENTRY",
          'if(scrNTTEFullSmokeAsyncCase("FrontierAuroraNativeTests")) {scrFRIntegrationTestStart("aurora-native");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))',before=True)
    return {"native_case": "FrontierBlizzardTests", "cold_boot_case":"FrontierMenuAudioBootTests",
            "live_case":"FrontierBlizzardLiveTests","production_weather_changed": "Aurora direct live-marker traversal"}
