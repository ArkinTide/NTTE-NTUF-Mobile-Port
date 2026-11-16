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

function scrFRClockState213(_rate) {
    return {limited:false,hot:0,cool:0,rate:_rate,dwell:0,
        recovered:false,probe_elapsed:0,blocked:false};
}

function scrFRClockBudget212(_state,_target,_capacity,_elapsed,_enabled,_work_capacity=undefined) {
    if(!_enabled || _target!=60) return scrFRClockState213(_target);
    var _dt=clamp(_elapsed,0,.1);
    if(is_undefined(_work_capacity)) _work_capacity=_capacity;
    if(_state.limited) {
        // delta_time includes the intentional30Hz cap wait. Only measured
        // processing headroom can justify recovery, never a periodic retry.
        _state.dwell=(_state[$ "dwell"]??0)+_dt;
        _state.cool=!(_state[$ "blocked"]??false) && _work_capacity>=90?_state.cool+_dt:0;
        if(!(_state[$ "blocked"]??false) && _state.dwell>=5 && _state.cool>=3) {
            _state.limited=false;_state.hot=0;_state.cool=0;_state.dwell=0;
            _state.recovered=true;_state.probe_elapsed=0;
        }
    } else {
        // CPU headroom cannot measure a GPU/presentation bottleneck. A
        // failed recovery probe must not cause another five-second cycle
        // in the same scene. Five sustained stable seconds accept a probe.
        if(_state[$ "recovered"]??false) {
            _state.probe_elapsed=_capacity>=54?(_state[$ "probe_elapsed"]??0)+_dt:0;
            if(_state.probe_elapsed>=5) {_state.recovered=false;_state.probe_elapsed=0;}
        }
        _state.hot=_capacity<54?_state.hot+_dt:max(0,_state.hot-_dt*2);
        if(_state.hot>=.8) {
            _state.blocked=_state[$ "recovered"]??false;
            _state.limited=true;_state.hot=0;_state.cool=0;_state.dwell=0;
            _state.recovered=false;_state.probe_elapsed=0;
        }
    }
    _state.rate=_state.limited?30:60;
    return _state;
}

function scrFRClockSafe212() {
    return instance_exists(UberCont) && !UberCont.paused && UberCont.want_pause<=0
        && !UberCont.quit_pause && !instance_exists(PauseImage) && !lockstep_stop
        && !instance_exists(GenCont);
}

// Called with UberCont before the safe-transaction guard. Pausing keeps the
// scene's failed-probe latch; a real new generator id, menu or opt-out clears
// it. Generation ids distinguish even two consecutive maps of the same area.
function scrFRClockContext213(_generation,_playing,_enabled) {
    var _new_generation=_generation!=noone && _generation!=(self[$ "fr_clock_generation213"]??noone);
    if(_generation!=noone) fr_clock_generation213=_generation;
    if(_new_generation || !_playing || !_enabled || is_undefined(self[$ "fr_clock_budget212"]))
        fr_clock_budget212=scrFRClockState213(opt_framerate);
}

function scrFRClockBegin212() {
    if(!instance_exists(UberCont)) return;
    with(UberCont) {
        // Both worlds call before timers; their creation order is immaterial.
        if((self[$ "fr_clock_frame212"]??-999)==current_frame) return;
        fr_clock_frame212=current_frame;
        fr_clock_started213=get_timer();fr_clock_measuring213=true;
        // Pause deactivates Player but keeps GameCont alive. Preserve the
        // scene through that interval and the unpause activation boundary;
        // only actual campfire/menu controllers count as leaving gameplay.
        var _pause_boundary=paused || want_pause>0 || quit_pause || instance_exists(PauseImage),
            _playing=instance_exists(GameCont) && !instance_exists(Menu) && !instance_exists(MenuGen)
                && (instance_exists(Player) || _pause_boundary),
            _enabled=self[$ "opt_ntte_autoframerate"]??true;
        scrFRClockContext213(instance_find(GenCont,0),_playing,_enabled);
        if(!scrFRClockSafe212() || game_get_speed(gamespeed_fps)>=game_speed_uncaped) return;
        var _capacity=delta_time>0?1000000/delta_time:fps_real;
        fr_clock_budget212=scrFRClockBudget212(fr_clock_budget212,opt_framerate,
            _capacity,delta_time/1000000,_playing && _enabled,
            1000000/max(1,self[$ "fr_clock_work213"]??1000000));
        scrFRClockApply212(fr_clock_budget212.rate);
    }
}

// GUI End follows native/source Step and Draw work, before the engine's cap
// wait. A slow single frame cannot request recovery: Budget needs3s headroom.
function scrFRClockEnd213() {
    if(!instance_exists(UberCont)) return;
    with(UberCont) if(self[$ "fr_clock_measuring213"]??false) {
        fr_clock_work213=max(1,get_timer()-fr_clock_started213);
        fr_clock_measuring213=false;
    }
}
