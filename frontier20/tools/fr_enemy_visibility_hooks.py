"""Repair Crystal clone Top ownership and install native visibility acceptance."""
from pathlib import Path
from fr_content_hooks import patch


def apply(project):
    project = Path(project)
    patch(project, "scripts/scrNTTEFullCrystalCloneNative/scrNTTEFullCrystalCloneNative.gml", "CLONE OWNS WALL TOP RESTORATION",
          'scrFREnemyCloneOwnTop(_source,target);\n'
          'scrFREnemyCloneOwnToss(_source,target);',
          anchor='    scrNTTEFullCrystalCloneEffect(x,y,target.x,target.y)', before=True)
    patch(project, "objects/Bullet1/Collision_hitme.gml", "VISIBILITY TEST READONLY BULLET BEFORE",
          'var _fr_visibility_hit=undefined;\n'
          'if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))\n'
          '    _fr_visibility_hit=scrFREnemyVisibilityBulletBefore(id,other.id);',
          anchor='scr_projectile_generic_bullet_hit()', before=True)
    patch(project, "objects/Bullet1/Collision_hitme.gml", "VISIBILITY TEST READONLY BULLET AFTER",
          'if(!is_undefined(_fr_visibility_hit)) scrFREnemyVisibilityBulletAfter(_fr_visibility_hit);',
          anchor='scr_projectile_generic_bullet_hit()')
    patch(project, "scripts/scrFrontier_tests/scrFrontier_tests.gml", "ENEMY VISIBILITY DIAGNOSTIC DRIVER",
          'if(fr_test_case=="enemy-visibility" || fr_test_case=="enemy-visibility-clone"\n'
          '    || fr_test_case=="enemy-visibility-toss") {\n'
          '    if(!variable_instance_exists(id,"fr_enemy_visibility")) {\n'
          '        if(!scrFRReadyTick()) return;\n'
          '        if(++fr_test_ticks<45) return;\n'
          '        scrFREnemyVisibilityTestsStart(id,fr_test_case=="enemy-visibility-clone",\n'
          '            fr_test_case=="enemy-visibility-toss");\n'
          '    }\n'
          '    if(scrFREnemyVisibilityTestsStep(id)) {\n'
          '        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
          '        game_end();\n'
          '    }\n'
          '    return;\n'
          '}', anchor="function scrFRIntegrationTestStep() {")
    patch(project, "scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml", "ENEMY VISIBILITY DIAGNOSTIC ENTRY",
          'if(scrNTTEFullSmokeAsyncCase("FrontierEnemyVisibilityTests")) {scrFRIntegrationTestStart("enemy-visibility");return;}\n'
          'if(scrNTTEFullSmokeAsyncCase("FrontierEnemyCloneTopTests")) {scrFRIntegrationTestStart("enemy-visibility-clone");return;}\n'
          'if(scrNTTEFullSmokeAsyncCase("FrontierEnemyCloneTossTests")) {scrFRIntegrationTestStart("enemy-visibility-toss");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', before=True)
    return {"clone_top_ownership_repair": True, "clone_toss_ownership_repair": True,
            "native_case": "FrontierEnemyVisibilityTests", "city_maps": 24,
            "clone_top_rates": [30, 60], "clone_toss_rates": [30, 60]}
