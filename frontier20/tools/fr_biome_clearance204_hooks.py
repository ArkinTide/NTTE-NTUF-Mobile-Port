"""Install only an isolated native diagnostic entry, with no gameplay hooks."""
from pathlib import Path
from fr_content_hooks import patch


def apply(project):
    project = Path(project)
    patch(project, 'scripts/scrFrontier_tests/scrFrontier_tests.gml', 'BIOME CLEARANCE204 DIAGNOSTIC DRIVER',
          'if(fr_test_case=="biome-clearance204") {\n'
          '    if(!variable_instance_exists(id,"fr_biome_clearance204")) {\n'
          '        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;\n'
          '        if(++fr_test_ticks<45) return;\n'
          '        scrFRBiomeClearance204TestsStart(id);\n'
          '    }\n'
          '    if(scrFRBiomeClearance204TestsStep(id)) {\n'
          '        scrNTTESmokeLog("PASS biome clearance read-only native diagnostic completed; not proof of a repair");\n'
          '        game_end();\n'
          '    }\n'
          '    return;\n'
          '}', anchor='function scrFRIntegrationTestStep() {')
    patch(project, 'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', 'BIOME CLEARANCE204 DIAGNOSTIC ENTRY',
          'if(scrNTTEFullSmokeAsyncCase("FrontierBiomeClearance204Tests")) {scrFRIntegrationTestStart("biome-clearance204");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', before=True)
    return {'diagnostic_only': True, 'native_case': 'FrontierBiomeClearance204Tests'}
