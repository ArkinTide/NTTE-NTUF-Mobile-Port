// Native physics are pixels/callback; source callbacks keep their 30 Hz units.
function scrFRClockWallBouncePhysical212(_object) {
    // These native collision handlers add wallbounce directly to physical
    // speed. NTUF custom shots and NTTE Red/Venom/CustomShell instead keep
    // this field in source units and multiply it by timescale when used.
    // Projectile ancestry therefore cannot determine the field's units.
    switch(_object) {
        case Bullet2: case EnemyBullet3: case EnemyFlak: case FlameShell:
        case HeavySlug: case HyperSlug: case PopoSlug: case Slug: return true;
    }
    return false;
}

function scrFRClockActor212(_from,_to) {
    var _ratio=_to/max(.001,_from);
    hspeed*=_ratio;vspeed*=_ratio;friction*=_ratio*_ratio;
    gravity*=object_index==Bubble?_ratio:_ratio*_ratio;
    if((self[$ "fr_custom_actor"]??false) || !sprite_exists(sprite_index)
       || sprite_get_speed_type(sprite_index)!=spritespeed_framespersecond)
        image_speed*=_ratio;
    if(variable_instance_exists(id,"knockback_speed")) knockback_speed*=_ratio;
    if(object_index==Player || object_index==DogGuardian || object_index==InvSpider
        || object_index==Spider || object_index==Rocket || object_index==JockRocket
        || (self[$ "fr_custom_actor"]??false)) {
        if(variable_instance_exists(id,"maxspeed")) maxspeed*=_ratio;
    }
    if(scrFRClockWallBouncePhysical212(object_index)
       && variable_instance_exists(id,"wallbounce")) wallbounce*=_ratio;
    if(object_index==DogGuardian || object_index==SodaCan) zspeed*=_ratio;
    if(object_index==Player) ntte_player_physics_scale=_to;
}

function scrFRClockApply212(_rate) {
    if(_rate>=game_speed_uncaped) return false;
    var _from=global.time_scale,_to=scrNTTEFullRateScale(_rate);
    if(abs(_from-_to)>.000001) with(all) scrFRClockActor212(_from,_to);
    global.time_scale=_to;
    if(game_get_speed(gamespeed_fps)!=_rate) game_set_speed(_rate,gamespeed_fps);
    return true;
}

function scrFRClockBudget212(_state,_target,_capacity,_elapsed,_enabled) {
    if(!_enabled || _target!=60) return {limited:false,hot:0,cool:0,rate:_target};
    var _dt=clamp(_elapsed,0,.1);
    if(_state.limited) {
        _state.cool+=_dt;
        if(_state.cool>=5) {_state.limited=false;_state.hot=0;_state.cool=0;}
    } else {
        _state.hot=_capacity<54?_state.hot+_dt:max(0,_state.hot-_dt*2);
        if(_state.hot>=.8) {_state.limited=true;_state.hot=0;_state.cool=0;}
    }
    _state.rate=_state.limited?30:60;
    return _state;
}

function scrFRClockSafe212() {
    return instance_exists(UberCont) && !UberCont.paused && UberCont.want_pause<=0
        && !UberCont.quit_pause && !instance_exists(PauseImage) && !lockstep_stop
        && !instance_exists(GenCont);
}

function scrFRClockBegin212() {
    if(!instance_exists(UberCont)) return;
    with(UberCont) {
        // Both worlds call before timers; their creation order is immaterial.
        if((self[$ "fr_clock_frame212"]??-999)==current_frame) return;
        fr_clock_frame212=current_frame;
        if(!scrFRClockSafe212() || game_get_speed(gamespeed_fps)>=game_speed_uncaped) return;
        if(is_undefined(self[$ "fr_clock_budget212"]))
            fr_clock_budget212={limited:false,hot:0,cool:0,rate:opt_framerate};
        var _capacity=delta_time>0?1000000/delta_time:fps_real;
        fr_clock_budget212=scrFRClockBudget212(fr_clock_budget212,opt_framerate,
            _capacity,delta_time/1000000,instance_exists(GameCont) && instance_exists(Player)
            && (self[$ "opt_ntte_autoframerate"]??true));
        scrFRClockApply212(fr_clock_budget212.rate);
    }
}
