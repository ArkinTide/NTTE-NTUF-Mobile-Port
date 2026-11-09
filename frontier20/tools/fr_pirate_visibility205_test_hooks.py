"""Opt-in Cove L1 loop-cluster and ordinary-collision acceptance."""
from pathlib import Path
from fr_content_hooks import patch


def apply(project):
    project = Path(project)
    patch(project, 'scripts/scrFrontier_tests/scrFrontier_tests.gml',
          'PIRATE VISIBILITY205 DIAGNOSTIC DRIVER',
          'if(fr_test_case=="pirate-visibility205") {\n'
          '    if(!variable_instance_exists(id,"fr_pirate_visibility205")) {\n'
          '        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;\n'
          '        if(++fr_test_ticks<45) return;\n'
          '        scrFRPirateVisibility205TestsStart(id);return;\n'
          '    }\n'
          '    if(scrFRPirateVisibility205TestsStep(id)) {\n'
          '        scrNTTESmokeLog("PASS real Cove L1 source-factory loop clusters at 30/60Hz: initialized species/HP/callbacks/masks, native scatter, scheduled Bullet1 deaths and natural exits");\n'
          '        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
          '        game_end();\n'
          '    }\n'
          '    return;\n'
          '}', anchor='function scrFRIntegrationTestStep() {')
    patch(project, 'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml',
          'PIRATE VISIBILITY205 DIAGNOSTIC ENTRY',
          'if(scrNTTEFullSmokeAsyncCase("FrontierPirateVisibility205Tests")) '
          '{scrFRIntegrationTestStart("pirate-visibility205");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', before=True)
    patch(project, 'objects/hitme/Create_0.gml', 'PIRATE VISIBILITY205 READONLY HITME BIRTH',
          'if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))\n'
          '    scrFRPirateVisibility205Created(id);')
    return {'diagnostic_only': False, 'native_case': 'FrontierPirateVisibility205Tests'}
