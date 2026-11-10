// NTUF AugmentCompassion: ATTENDANT DRONE 'HYPERION'. The source's nearest
// target filter excluded allied shots, but its shared drone/shock collision
// callback did not. Current projectile allegiance is authoritative: a reflected
// enemy shot keeps its original creator while becoming a friendly projectile.
function scrFRHyperionFriendly210(_shot) {
    var _team=_shot[$ "team"]??team_none;
    return _team==team_player || (_team==1724
        && (_shot[$ "fr_powder_team210"]??team_none)==team_player);
}
function scrFRHyperionEnemyProjectile(_shot) {
    if(!instance_exists(_shot) || !instance_is(_shot,projectile)) return false;
    if(scrFRHyperionFriendly210(_shot)) return false;
    var _team=_shot[$ "team"]??team_none,_typ=_shot[$ "typ"]??0;
    return _typ>0 && (_team==team_enemy || _team==team_popo);
}

function scrFRHyperionEnemyProjectiles() {
    var _result=[];
    with(projectile) if(scrFRHyperionEnemyProjectile(id)) array_push(_result,id);
    return _result;
}

function scrFRHyperionInterceptor210(_actor) {
    return instance_exists(_actor) && instance_is(_actor,FRCustomSlash)
        && (_actor[$ "on_projectile"]??undefined)==fr_Mutations_AugmentCompassion_skill_gml_DroneShock_nullify;
}
function scrFRHyperionAlliedPair210(_a,_b) {
    if(!instance_exists(_a) || !instance_exists(_b)) return false;
    // Both collision directions matter: custom weapon waves also have a
    // projectile callback and can deflect themselves against a Slash child.
    if(scrFRHyperionInterceptor210(_a))
        return scrFRHyperionFriendly210(_b);
    if(scrFRHyperionInterceptor210(_b))
        return scrFRHyperionFriendly210(_a);
    return false;
}

function scrFRDroneThreat210() {
    // The source asks whether a shot is within 64px of the drone mask. Use
    // the engine's spatial collision query, rather than scanning every
    // projectile in the room once per pet. Keep current teams live.
    static _near=ds_list_create();
    ds_list_clear(_near);
    collision_rectangle_list(bbox_left-64,bbox_top-64,bbox_right+64,bbox_bottom+64,
        projectile,false,true,_near,false);
    for(var _i=0;_i<ds_list_size(_near);++_i) {
        var _shot=_near[|_i];
        if(scrFRHyperionEnemyProjectile(_shot) && distance_to_object(_shot)<64) return true;
    }
    return false;
}
