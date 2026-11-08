"""Install real-map normal-clearance acceptance and read-only bullet evidence."""
from pathlib import Path
from fr_content_hooks import patch


def apply(project):
    project = Path(project)
    patch(project, 'objects/Bullet1/Collision_hitme.gml', 'BIOME CLEARANCE204 MAP HIT BEFORE',
          'var _fr_biome_map_hit=undefined;\n'
          'if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))\n'
          '    _fr_biome_map_hit=scrFRBiomeClearance204MapBulletBefore(id,other.id);',
          anchor='scr_projectile_generic_bullet_hit()', before=True)
    patch(project, 'objects/Bullet1/Collision_hitme.gml', 'BIOME CLEARANCE204 MAP HIT AFTER',
          'if(!is_undefined(_fr_biome_map_hit)) scrFRBiomeClearance204MapBulletAfter(_fr_biome_map_hit);',
          anchor='scr_projectile_generic_bullet_hit()')
    patch(project, 'scripts/scrFrontier_tests/scrFrontier_tests.gml', 'BIOME CLEARANCE204 MAP DRIVER',
          'if(fr_test_case=="biome-clearance204-maps") {\n'
          '    if(!variable_instance_exists(id,"fr_biome_clearance204_maps")) {\n'
          '        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;\n'
          '        if(++fr_test_ticks<45) return;\n'
          '        scrFRBiomeClearance204MapTestsStart(id);\n'
          '    }\n'
          '    if(scrFRBiomeClearance204MapTestsStep(id)) {\n'
          '        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
          '        game_end();\n'
          '    }\n'
          '    return;\n'
          '}', anchor='function scrFRIntegrationTestStep() {')
    patch(project, 'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', 'BIOME CLEARANCE204 MAP ENTRY',
          'if(scrNTTEFullSmokeAsyncCase("FrontierBiomeClearance204MapTests")) {scrFRIntegrationTestStart("biome-clearance204-maps");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', before=True)
    return {'native_case': 'FrontierBiomeClearance204MapTests', 'natural_maps': 12,
            'rates': [30, 60], 'loops': [0, 1, 3], 'normal_exit_required': True}
