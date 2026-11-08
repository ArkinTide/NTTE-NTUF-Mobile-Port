// NTUF AugmentCompassion: ATTENDANT DRONE 'HYPERION'. The source's nearest
// target filter excluded allied shots, but its shared drone/shock collision
// callback did not. Current projectile allegiance is authoritative: a reflected
// enemy shot keeps its original creator while becoming a friendly projectile.
function scrFRHyperionEnemyProjectile(_shot) {
    if(!instance_exists(_shot) || !instance_is(_shot,projectile)) return false;
    var _team=_shot[$ "team"]??team_none,_typ=_shot[$ "typ"]??0;
    return _typ>0 && (_team==team_enemy || _team==team_popo);
}

function scrFRHyperionEnemyProjectiles() {
    var _result=[];
    with(projectile) if(scrFRHyperionEnemyProjectile(id)) array_push(_result,id);
    return _result;
}
