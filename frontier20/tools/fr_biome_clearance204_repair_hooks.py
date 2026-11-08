"""Preserve the source Top lifecycle when a dormant native actor wakes."""
from pathlib import Path
from fr_content_hooks import patch


def apply(project):
    project = Path(project)
    patch(project, 'objects/MeleeFake/Step_0.gml', 'AWAKENED ENEMY OWNS WALL TOP',
          'scrFRBiomeAwakenOwnTop(id,_awake);', anchor='\t_awake.team = team')
    patch(project, 'objects/Bullet1/Collision_hitme.gml', 'BIOME CLEARANCE204 READONLY HIT BEFORE',
          'var _fr_biome_hit=undefined;\n'
          'if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))\n'
          '    _fr_biome_hit=scrFRBiomeClearance204BulletBefore(id,other.id);',
          anchor='scr_projectile_generic_bullet_hit()', before=True)
    patch(project, 'objects/Bullet1/Collision_hitme.gml', 'BIOME CLEARANCE204 READONLY HIT AFTER',
          'if(!is_undefined(_fr_biome_hit)) scrFRBiomeClearance204BulletAfter(_fr_biome_hit);',
          anchor='scr_projectile_generic_bullet_hit()')
    patch(project, 'scripts/scrFrontier_tests/scrFrontier_tests.gml', 'BIOME CLEARANCE204 ACCEPTANCE DRIVER',
          'if(fr_test_case=="biome-clearance204-acceptance") {\n'
          '    if(!variable_instance_exists(id,"fr_biome_clearance204_acceptance")) {\n'
          '        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;\n'
          '        if(++fr_test_ticks<45) return;\n'
          '        scrFRBiomeClearance204AcceptanceStart(id);\n'
          '    }\n'
          '    if(scrFRBiomeClearance204AcceptanceStep(id)) {\n'
          '        scrNTTESmokeLog("PASS biome clearance actual30/60Hz native wake, Top landing, Bullet1 damage/death and ordinary exit");\n'
          '        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
          '        game_end();\n'
          '    }\n'
          '    return;\n'
          '}', anchor='function scrFRIntegrationTestStep() {')
    patch(project, 'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', 'BIOME CLEARANCE204 ACCEPTANCE ENTRY',
          'if(scrNTTEFullSmokeAsyncCase("FrontierBiomeClearance204AcceptanceTests")) {scrFRIntegrationTestStart("biome-clearance204-acceptance");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', before=True)
    return {'dormant_replacement_own_top': True,
            'native_case': 'FrontierBiomeClearance204AcceptanceTests', 'rates': [30, 60]}
