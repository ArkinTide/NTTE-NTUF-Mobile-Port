// Hyperion's physical drone and shock retain the source collision masks,
// allegiance rules, projectile destruction events, damage and cooldowns.
// Only redundant nearest-query adapters and surplus overlapping cosmetics
// are bypassed. The reference branch is available only in isolated Windows
// acceptance; ordinary games cannot enable it through a save option.
function scrFRDroneReference204Enabled() {
    return variable_global_exists("fr_drone204_reference") && global.fr_drone204_reference
        && os_type==os_windows && scrNTTEFullSmokeEnabled()
        && instance_exists(FRIntegrationTest);
}

function scrFRDroneNearestHostile204(_x,_y) {
    var _nearest=noone,_distance=infinity;
    // Match the existing hostile collector and libGeneral's strict centre-
    // distance comparison in native enumeration order. No list is retained
    // across frames: reflection, creation and deletion are immediately live.
    with(projectile) {
        // The abstract native projectile parent does not initialize typ.
        // Preserve the established collector's missing-field-as-zero rule.
        if((self[$ "typ"]??0)<=0 || (team!=team_enemy && team!=team_popo)) continue;
        var _candidate_distance=point_distance(_x,_y,x,y);
        if(_candidate_distance<_distance) {_distance=_candidate_distance;_nearest=real(id);}
    }
    return _nearest;
}

function scrFRDroneCosmeticBatch204() {
    var _game=instance_exists(GameCont)?real(GameCont.id):noone,
        _state=variable_global_exists("fr_drone204_batch")?global.fr_drone204_batch:undefined;
    // current_frame has fractional host-frame values at60Hz. A new batch
    // therefore opens every rendered simulation frame at either real rate.
    if(!is_struct(_state) || _state.frame!=current_frame || _state.game!=_game || _state.room!=room) {
        _state={frame:current_frame,game:_game,room:room,hits:0,effects:0,
            sounds:0,cells:{}};
        global.fr_drone204_batch=_state;
    }
    return _state;
}

function scrFRDroneIntercept204(_shot) {
    if(scrFRDroneReference204Enabled()) return false;
    if(!scrFRHyperionEnemyProjectile(_shot)) return true;
    var _state=scrFRDroneCosmeticBatch204();
    _state.hits+=1;
    // The authored source consumes one pitch draw for EVERY intercepted
    // shot. Coalescing sound must not alter subsequent seeded combat/drops.
    var _pitch=1.3+scrFRSourceRandom(0.2);
    if(_state.sounds==0) {
        scrFRSoundPitchVolume(sndPickupDisappear,_pitch,0.4);
        _state.sounds+=1;
    }
    var _cell=string(floor(_shot.x/24))+":"+string(floor(_shot.y/24)),
        _seen=variable_struct_exists(_state.cells,_cell);
    // Preserve sparse visual feedback exactly. Dense bursts retain the first32
    // source flashes plus one flash at each new position up to64 per host
    // frame. This cap applies only to Null sprites, never to hostile shots,
    // shock damage, collision events or the native projectile death effect.
    if(_state.effects<4 || (!_seen && _state.effects<8)) {
        var _effect=instance_create(_shot.x,_shot.y,BulletHit),
            _vars=global.fr_module_vars[$ "skill:AugmentCompassion"];
        _effect.sprite_index=scrFRAreaSourceSprite(_vars.settingGreenAugments?_vars.sprGreenNull:_vars.sprNull);
        _state.cells[$ _cell]=true;
        _state.effects+=1;
    } else {
        // BulletHit.Create consumes one native random_angle. Keep that draw
        // even when an identical cosmetic flash is omitted.
        var _discard_angle=random(360);
    }
    // Preserve ordinary projectile.Destroy, including grenade/native source
    // handlers. Skipping that event would change interception gameplay.
    instance_destroy(_shot);
    return true;
}
