"""Bidirectional Hyperion collision gates and spatial threat probes."""
from apply_release210_repairs import ROOT, PROJECT, change
from install_native205 import apply


def main():
    # Actors are maintained under their original script identity scrFRActors.
    # Do not register a second script containing the same declarations.
    import json
    from install_native205 import load
    accidental=PROJECT/'scripts/scrFrontier_actors'
    if accidental.is_dir():
        for name in ['scrFrontier_actors.gml','scrFrontier_actors.yy']:
            (accidental/name).unlink(missing_ok=True)
        accidental.rmdir()
        project=PROJECT/'nuclearthronemobile.yyp'
        data=load(project)
        data['resources']=[r for r in data['resources'] if r['id']['path']!='scripts/scrFrontier_actors/scrFrontier_actors.yy']
        project.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    path=PROJECT/'scripts/scrFRActors/scrFRActors.gml'
    change(path,'    if(lockstep_stop) return true;\n    var _field=instance_is(other.id,Grenade)?"on_grenade":"on_projectile";',
           '    if(lockstep_stop) return true;\n    if(scrFRHyperionAlliedPair210(id,other.id)) return true;\n    var _field=instance_is(other.id,Grenade)?"on_grenade":"on_projectile";')
    change(path,'    scrFRActorCallback(_field);\n    return true;',
           '    if(scrFRHyperionInterceptor210(id) && !scrFRDroneReference204Enabled()) {\n        scrFRDroneIntercept204(other.id);return true;\n    }\n    scrFRActorCallback(_field);\n    return true;')
    for path in (PROJECT / 'objects').glob('*/Collision_projectile.gml'):
        change(path, path.read_text('utf-8-sig'),
               'if(scrFRHyperionAlliedPair210(id,other.id)) exit; // FRONTIER210 ALLIED INTERCEPTOR\n'
               + path.read_text('utf-8-sig')) if 'FRONTIER210 ALLIED INTERCEPTOR' not in path.read_text('utf-8-sig') else None
    path=PROJECT/'scripts/frCode_AugmentCompassion_skill_0a14ee0be2/frCode_AugmentCompassion_skill_0a14ee0be2.gml'
    change(path,'if (((distance_to_object(enemy) < 48) || (distance_to_object(_frl__nearestProjectile) < 64))) {',
           'if (((distance_to_object(enemy) < 48) || (scrFRDroneReference204Enabled() ? distance_to_object(_frl__nearestProjectile) < 64 : scrFRDroneThreat210()))) {')
    change(path,' : scrFRDroneNearestHostile204(x,y)) /* FRONTIER DRONE204 DIRECT NEAREST */;',
           ' : noone) /* FRONTIER DRONE204 DIRECT NEAREST */;')
    # Existing acceptance records the intentionally reduced cosmetic budget.
    for path in [ROOT/'native/drone_performance204_tests.gml',PROJECT/'scripts/scrFrontier_drone_performance204_tests/scrFrontier_drone_performance204_tests.gml']:
        change(path,'(_effects>=32 && _effects<=64)','(_effects>=4 && _effects<=8)')
    apply(PROJECT,{'hyperion_projectiles.gml':'scrFrontier_hyperion_projectiles',
                   'drone_performance204.gml':'scrFrontier_drone_performance204'})


if __name__=='__main__': main()
