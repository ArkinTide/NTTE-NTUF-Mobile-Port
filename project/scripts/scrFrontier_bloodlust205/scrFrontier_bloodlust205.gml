// The source augment polls dying enemy instances from its ordinary step.
// Native enemies can finish Destroy before that source tick is dispatched.
// Retain the same per-enemy mark and counter at that final native boundary;
// the authored skill step still owns its 13-kill threshold, healing and FX.
function scrFRBloodlust205EnemyDeath() {
    if(!scrFREnabled() || !instance_exists(GameCont) || hp>0
        || !is_undefined(self[$ "fr_AugmentBloodlust"])
        || scrFRGetSkill("AugmentBloodlust")<=0) return;
    fr_AugmentBloodlust=true;
    global.fr_module_vars[$ "skill:AugmentBloodlust"].augmentBloodlustCount+=1;
}
