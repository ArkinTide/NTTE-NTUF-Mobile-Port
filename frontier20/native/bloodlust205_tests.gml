// The real station grants the mutation. Native projectiles then hurt Player
// and kill real native, NTTE and NTUF actors during ordinary engine frames.
// No test calls the mutation step, death counter or healing effect directly.
function scrFRBloodlust205TestsState() {
    if(os_type!=os_windows || !scrNTTEFullSmokeEnabled()) return undefined;
    var _driver=instance_find(FRIntegrationTest,0);
    return instance_exists(_driver)?(_driver[$ "fr_bloodlust205"]??undefined):undefined;
}
function scrFRBloodlust205TestsCount() {
    return scrFRModGet("skill","AugmentBloodlust","augmentBloodlustCount");
}
function scrFRBloodlust205TestsWrite(_s,_status,_reason="") {
    var _out={schema:1,status:_status,reason:_reason,physical_device_tested:false,
        direct_effect_calls:false,routes:_s.rows,active:_s.row};
    var _file=file_text_open_write(working_directory+"frontier-bloodlust205.json");
    file_text_write_string(_file,json_stringify(_out));file_text_close(_file);
}
function scrFRBloodlust205TestsCheck(_s,_condition,_reason) {
    if(_condition) return;
    array_push(_s.row.failures,_reason);
    scrNTTESmokeLog("FR_BLOODLUST205 FAILURE "+_reason);
}
function scrFRBloodlust205TestsDeath() {
    var _s=scrFRBloodlust205TestsState();
    if(!is_struct(_s) || is_undefined(_s.row) || id!=_s.target) return;
    array_push(_s.row.deaths,{id:real(id),object:object_get_name(object_index),
        name:self[$ "name"]??"",hp:hp,frame:current_frame,
        ready:scrFRReadyTick(),counter_before_death:scrFRBloodlust205TestsCount(),
        marker_before_death:self[$ "fr_AugmentBloodlust"]??false,
        phase:_s.phase,kill_index:_s.kills,callstack:debug_get_callstack(32)});
}
function scrFRBloodlust205TestsProc() {
    var _s=scrFRBloodlust205TestsState();
    if(!is_struct(_s) || is_undefined(_s.row)) return;
    array_push(_s.row.procs,{frame:current_frame,counter:scrFRBloodlust205TestsCount(),
        callstack:debug_get_callstack(32)});
}
function scrFRBloodlust205TestsActor(_s) {
    var _p=_s.player,_actor=noone;
    switch(_s.row.family) {
        case "native":_actor=instance_create(_p.x+128,_p.y,Bandit);break;
        case "NTTE":_actor=instance_create(_p.x+128,_p.y,NTTEBat);break;
        case "NTUF":_actor=scrFRInvoke(GameCont.id,
            fr_Objects_Frontier_Caves_mod_gml_Parrot_create,[_p.x+128,_p.y]);break;
    }
    assert(instance_exists(_actor) && _actor.hp>0 && sprite_exists(_actor.mask_index),
        "Bloodlust205 genuine enemy factory did not return a live masked actor");
    _s.target=_actor;return _actor;
}
function scrFRBloodlust205TestsShot(_s,_target,_enemy=false) {
    var _shot=noone;
    if(_enemy) {
        _shot=instance_create(_target.x,_target.y,EnemyBullet1);
        _shot.team=team_enemy;_shot.creator=noone;_shot.damage=3;
    } else {
        with(_s.player) _shot=scr_projectile_create(_target.x,_target.y,Bullet1,0,0);
        _shot.damage=_target.hp+10000;
    }
    assert(instance_exists(_shot),"Bloodlust205 failed to create the real native projectile");
    _shot.speed=0;
    array_push(_s.row.shots,{frame:current_frame,id:real(_shot),
        projectile:object_get_name(_shot.object_index),target:real(_target),
        target_object:object_get_name(_target.object_index),team:_shot.team,
        creator:real(_shot.creator),damage:_shot.damage,phase:_s.phase,kill_index:_s.kills});
}
function scrFRBloodlust205TestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Bloodlust205 requires the settled private native runner");
    var _s={world:scrNTTEFullWorldEventsNaturalWorldCapture(),player:instance_find(Player,0),
        cases:[],index:-1,phase:0,ticks:0,wait:0,kills:0,target:noone,rows:[],row:undefined,
        old_rate:game_get_speed(gamespeed_fps),held_ticks:0};
    var _families=["native","NTTE","NTUF"];
    for(var _rate=30;_rate<=60;_rate+=30)
        for(var _i=0;_i<3;++_i) array_push(_s.cases,{rate:_rate,family:_families[_i]});
    _driver.fr_bloodlust205=_s;
}
function scrFRBloodlust205TestsNext(_s) {
    if(++_s.index>=array_length(_s.cases)) {
        var _failures=0;for(var _i=0;_i<array_length(_s.rows);++_i) _failures+=array_length(_s.rows[_i].failures);
        scrFRBloodlust205TestsWrite(_s,_failures==0?"PASS":"FAIL");
        assert(_failures==0,"Carnivorous Enzymes real native combat acceptance failed; see frontier-bloodlust205.json");
        scrNTTEFullWorldEventsNaturalWorldRestore(_s.world);
        save_set_value("options","framerate",_s.old_rate);scrOptionsUpdate();return true;
    }
    var _case=_s.cases[_s.index];
    save_set_value("options","framerate",_case.rate);save_set_value("options","autopause",false);
    save_set_value("visual","freezeframes",0);scrOptionsUpdate();
    GameCont.is_level_ended=true;GameCont.loops=0;GameCont.popolevel=0;
    scrFRSetSkill("AugmentBloodlust",0);scr_skill_set(mut_bloodlust,0);
    // The source skill_lose owns its reset. Do not inject the counter or call
    // a mutation step/effect to manufacture its later combat threshold.
    assert(scrFRBloodlust205TestsCount()==0,"Source skill_lose did not reset its own counter");
    _s.row={rate:_case.rate,family:_case.family,grant:"actual AugmentStation source step",
        failures:[],deaths:[],shots:[],procs:[],settled:[],counter_at_12:-1,counter_after_13:-1,
        unowned_counter:-1,live_despawn_counter:-1,initial_hp:8,injured_hp:-1,healed_hp:-1,
        station_opened:false,held_dead_source_poll:false};
    _s.ticks=0;_s.wait=0;_s.kills=0;_s.held_ticks=0;_s.target=noone;
    with(_s.player) {x=62000;y=62000;hp=8;max_hp=8;nexthurt=current_frame-1;
        speed=0;hspeed=0;vspeed=0;can_walk=false;can_shoot=false;bcan_shoot=false;can_spec=false;}
    _s.phase=1;var _actor=scrFRBloodlust205TestsActor(_s);
    scrFRBloodlust205TestsShot(_s,_actor);return false;
}
function scrFRBloodlust205TestsStep(_driver) {
    var _s=_driver.fr_bloodlust205;
    if(_s.phase==0) return scrFRBloodlust205TestsNext(_s);
    assert(++_s.ticks<2400,"Bloodlust205 actual combat/death sequence timed out");
    var _p=_s.player;
    assert(instance_exists(_p) && _p.hp>0,"Bloodlust205 lost its genuine injured Player");
    assert(game_get_speed(gamespeed_fps)==_s.row.rate && timescale==30/_s.row.rate,
        "Bloodlust205 requested/native frame rates differ");
    if(_s.phase!=3) _p.nexthurt=current_frame+100000;
    _p.hspeed=0;_p.vspeed=0;
    if(_s.phase==1) {
        if(instance_exists(_s.target)) return false;
        _s.wait+=timescale;if(_s.wait<4) return false;
        _s.row.unowned_counter=scrFRBloodlust205TestsCount();
        scrFRBloodlust205TestsCheck(_s,_s.row.unowned_counter==0 && array_length(_s.row.procs)==0,
            "Unowned real enemy death counted or procced");
        scr_skill_set(mut_bloodlust,1);
        var _station=scrFRInvoke(GameCont.id,fr_Objects_Frontier_IDPD_mod_gml_AugmentStation_create,[_p.x-96,_p.y]);
        _station.oldskill=mut_bloodlust;_station.newskill="AugmentBloodlust";_station.pick=1;
        _s.station=_station;_s.phase=2;_s.wait=0;return false;
    }
    if(_s.phase==2) {
        if(!(_s.station[$ "opened"]??false)) return false;
        _s.row.station_opened=scrFRGetSkill("AugmentBloodlust")==1 && scr_skill_get(mut_bloodlust)==0;
        assert(_s.row.station_opened,"Actual AugmentStation did not replace Bloodlust with Carnivorous Enzymes");
        var _despawn=scrFRBloodlust205TestsActor(_s);
        assert(_despawn.hp>0,"Bloodlust205 live-despawn control was already dead");
        instance_destroy(_despawn);_s.target=noone;
        _s.row.live_despawn_counter=scrFRBloodlust205TestsCount();
        scrFRBloodlust205TestsCheck(_s,_s.row.live_despawn_counter==0,
            "Positive-HP cleanup counted as a combat death");
        _p.nexthurt=current_frame-1;
        _s.phase=3;scrFRBloodlust205TestsShot(_s,_p,true);return false;
    }
    if(_s.phase==3) {
        if(_p.hp==8) return false;
        assert(_p.hp==5,"Real enemy Bullet1 did not inflict its expected3 damage");
        _s.row.injured_hp=_p.hp;_p.nexthurt=current_frame+100000;
        _s.phase=4;_s.wait=0;return false;
    }
    if(_s.phase==4) {
        _s.wait+=timescale;if(_s.wait<4) return false;
        var _actor=scrFRBloodlust205TestsActor(_s);
        if(_s.row.family=="NTUF" && _s.kills==6) {_actor.can_die=false;_s.held_ticks=0;}
        _s.phase=5;_s.wait=0;scrFRBloodlust205TestsShot(_s,_actor);return false;
    }
    if(_s.phase==5) {
        if(instance_exists(_s.target)) {
            if(_s.row.family=="NTUF" && _s.kills==6 && _s.target.hp<=0) {
                _s.held_ticks+=timescale;
                if(_s.held_ticks>=4) {
                    _s.row.held_dead_source_poll=(_s.target[$ "fr_AugmentBloodlust"]??false)
                        && scrFRBloodlust205TestsCount()==7;
                    _s.target.can_die=true;
                }
            }
            return false;
        }
        _s.wait+=timescale;if(_s.wait<6) return false;
        ++_s.kills;
        var _count=scrFRBloodlust205TestsCount(),_expected=_s.kills==13?0:_s.kills,
            _hp_expected=_s.kills==13?6:5,_proc_expected=_s.kills==13?1:0;
        array_push(_s.row.settled,{kills:_s.kills,counter:_count,hp:_p.hp,
            procs:array_length(_s.row.procs),frame:current_frame});
        scrFRBloodlust205TestsCheck(_s,_count==_expected,
            "Actual kill"+string(_s.kills)+" counter "+string(_count)+" expected "+string(_expected));
        scrFRBloodlust205TestsCheck(_s,_p.hp==_hp_expected && array_length(_s.row.procs)==_proc_expected,
            "Actual kill"+string(_s.kills)+" premature/missing/duplicate source healing or proc");
        if(_s.kills==12) {_s.row.counter_at_12=_count;_s.wait=-12;}
        if(_s.kills<13) {_s.phase=4;return false;}
        _s.row.counter_after_13=_count;_s.row.healed_hp=_p.hp;
        if(_s.row.family=="NTUF") scrFRBloodlust205TestsCheck(_s,_s.row.held_dead_source_poll,
            "Real dead NTUF actor was not marked by the original source poll before final Destroy");
        _s.phase=6;_s.wait=0;return false;
    }
    _s.wait+=timescale;if(_s.wait<18) return false;
    scrFRBloodlust205TestsCheck(_s,scrFRBloodlust205TestsCount()==0 && _p.hp==6
        && array_length(_s.row.procs)==1,"Idle frames duplicated the13th-kill heal/counter");
    array_push(_s.rows,_s.row);
    scrNTTESmokeLog("FR_BLOODLUST205 OBSERVED "+json_stringify(_s.row));
    scrFRBloodlust205TestsWrite(_s,"IN_PROGRESS");_s.phase=0;return false;
}
