"""Install only the populated Desert/Jungle native diagnostic driver."""
from pathlib import Path
from fr_content_hooks import patch


def apply(project):
    project = Path(project)
    patch(project, 'scripts/scrFrontier_tests/scrFrontier_tests.gml', 'BIOME CLEARANCE204 NATURAL DIAGNOSTIC DRIVER',
          'if(fr_test_case=="biome-clearance204-natural" || fr_test_case=="biome-clearance204-suspects") {\n'
          '    if(!variable_instance_exists(id,"fr_biome_clearance204_natural")) {\n'
          '        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;\n'
          '        if(++fr_test_ticks<45) return;\n'
          '        scrFRBiomeClearance204NaturalTestsStart(id,fr_test_case=="biome-clearance204-suspects");\n'
          '    }\n'
          '    if(scrFRBiomeClearance204NaturalTestsStep(id)) {\n'
          '        scrNTTESmokeLog("PASS populated biome clearance diagnostic completed; not proof of a repair");\n'
          '        game_end();\n'
          '    }\n'
          '    return;\n'
          '}', anchor='function scrFRIntegrationTestStep() {')
    patch(project, 'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', 'BIOME CLEARANCE204 NATURAL DIAGNOSTIC ENTRY',
          'if(scrNTTEFullSmokeAsyncCase("FrontierBiomeClearance204NaturalTests")) {scrFRIntegrationTestStart("biome-clearance204-natural");return;}\n'
          'if(scrNTTEFullSmokeAsyncCase("FrontierBiomeClearance204SuspectTests")) {scrFRIntegrationTestStart("biome-clearance204-suspects");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', before=True)
    observer = ('if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))\n'
                '    scrFRBiomeClearance204NaturalCreated(id);')
    for name in ['Gator', 'BuffGator', 'NTTEBabyGator', 'FRCustomEnemy',
                 'NTTEFullTopObject', 'NTTEFullPalankingToss']:
        patch(project, f'objects/{name}/Create_0.gml', 'BIOME CLEARANCE204 READONLY BIRTH', observer)
    lifecycle = 'if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))\n    '
    patch(project, 'scripts/scrNTTEFullPalankingToss/scrNTTEFullPalankingToss.gml',
          'BIOME CLEARANCE204 READONLY TOSS FIRST STEP',
          lifecycle+'scrFRBiomeClearance204NaturalLifecycle("Toss.first-step",id,true);',
          anchor='function scrNTTEFullPalankingTossEndStep() {')
    patch(project, 'scripts/scrNTTEFullPalankingToss/scrNTTEFullPalankingToss.gml',
          'BIOME CLEARANCE204 READONLY TOSS CLEANUP',
          lifecycle+'scrFRBiomeClearance204NaturalLifecycle("Toss.cleanup-before",id);',
          anchor='    ntte_toss_cleaned=true', before=True)
    patch(project, 'scripts/scrNTTEFullPalankingToss/scrNTTEFullPalankingToss.gml',
          'BIOME CLEARANCE204 READONLY TOSS RESTORED',
          lifecycle+'scrFRBiomeClearance204NaturalLifecycle("Toss.cleanup-after",id);',
          anchor='    scrNTTEFullPalankingTossCleanup()')
    patch(project, 'scripts/scrNTTEFullTop/scrNTTEFullTop.gml',
          'BIOME CLEARANCE204 READONLY TOP FIRST STEP',
          lifecycle+'scrFRBiomeClearance204NaturalLifecycle("Top.first-step",id,true);',
          anchor='function scrNTTEFullTopEndStep() {')
    patch(project, 'scripts/scrNTTEFullTop/scrNTTEFullTop.gml',
          'BIOME CLEARANCE204 READONLY TOP DESTROY',
          lifecycle+'scrFRBiomeClearance204NaturalLifecycle("Top.destroy-before",id);',
          anchor='function scrNTTEFullTopDestroy() {')
    return {'diagnostic_only': True, 'native_case': 'FrontierBiomeClearance204NaturalTests'}
