// Observe real City generation and test a separately recorded clone witness
// on its generated floor. Both that witness and the independent clone fixture
// use real Top landing and native Bullet1 collision, never forced masks.
function scrFREnemyVisibilitySnapshot(_actor) {
    var _top=_actor[$ "ntte_full_top_object"]??noone,_clone=noone;
    with(NTTEFullCrystalClone) if(target==_actor) {_clone=id;break;}
    var _row={id:real(_actor.id),object:object_get_name(_actor.object_index),
        name:_actor[$ "name"]??"",x:_actor.x,y:_actor.y,hp:_actor.hp,team:_actor.team,
        visible:_actor.visible,alpha:_actor.image_alpha,mask:real(_actor.mask_index),
        sprite:real(_actor.sprite_index),depth:_actor.depth,canfly:_actor[$ "canfly"]??false,
        intro:_actor[$ "intro"]??undefined,top:real(_top),top_exists:instance_exists(_top),
        top_owns_target:instance_exists(_top) && _top.target==_actor,
        clone:real(_clone),clone_appear:instance_exists(_clone)?_clone.appear:undefined,
        clone_lifetime:instance_exists(_clone)?_clone.time:undefined,
        cat_active:_actor[$ "ntte_cat_active"]??undefined,
        cat_hidden_age:_actor[$ "ntte_cat_hidden_age"]??undefined,
        brain_teleport:_actor[$ "teleport"]??undefined,
        possessing:_actor[$ "possessing"]??undefined,
        possess_target:real(_actor[$ "possess_target"]??noone),
        possess_target_exists:instance_exists(_actor[$ "possess_target"]??noone),
        possess_target_hp:instance_exists(_actor[$ "possess_target"]??noone)?
            (_actor.possess_target[$ "hp"]??undefined):undefined,
        floor_contact:false,wall_contact:false,alarms:[]};
    with(_actor) {
        _row.floor_contact=place_meeting(x,y,Floor);
        _row.wall_contact=place_meeting(x,y,Wall);
        for(var _i=0;_i<12;++_i) array_push(_row.alarms,alarm[_i]);
    }
    if(instance_exists(_top)) {
        _row.top_target=real(_top.target);_row.top_z=_top.z;
        _row.top_jump_time=_top.jump_time;_row.top_canmove=_top.canmove;
        _row.top_floor_contact=false;
        with(_top) _row.top_floor_contact=place_meeting(x+mask_x,y+mask_y,Floor);
    }
    return _row;
}

function scrFREnemyVisibilityObserve(_state,_all=false) {
    var _rows=[],_suspects=[];
    with(enemy) if(hp>0 && team!=team_player) {
        var _row=scrFREnemyVisibilitySnapshot(id),_hidden=!visible || mask_index==mskNone,
            _key=string(real(id)),_age=_state.ages[$ _key]??0;
        _age=_hidden?_age+timescale:0;_state.ages[$ _key]=_age;
        if(_all || _hidden) array_push(_rows,_row);
        if(_hidden) {
            _row.hidden_age=_age;
            // Classify, but do not excuse or mutate, intended transient states.
            _row.reason=_row.top_owns_target?"owned-wall-top":
                (instance_exists(_row.clone) && _row.clone_appear>0?"clone-appearing":
                (_row.cat_active==false?"cat-in-cover":
                (_row.brain_teleport==true?"brain-teleport":"unowned")));
            array_push(_suspects,_row);
        }
    }
    return {source_ticks:_state.elapsed,enemies:instance_number(enemy),
        actors:_rows,hidden_or_maskless:_suspects};
}

function scrFREnemyVisibilityTestsStart(_driver,_clone_only=false,_toss_only=false) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Enemy visibility diagnostics require the settled isolated native runner");
    var _cases=[];
    // Twelve independent seeds per loop profile, all three City subareas,
    // using genuine asynchronous GenCont/FloorMaker and scheduled enemy AI.
    for(var _i=0;_i<12;++_i) for(var _loop=0;_loop<2;++_loop)
        array_push(_cases,{seed:103038+97*_i,loops:_loop*3,subarea:1+(_i mod 3),
            rate:(_i mod 2)==0?30:60});
    _driver.fr_enemy_visibility={world:scrNTTEFullWorldEventsNaturalWorldCapture(),
        cases:_cases,index:-1,phase:_toss_only?10:(_clone_only?4:0),clone_only:_clone_only,
        toss_only:_toss_only,toss_rate:0,toss_rows:[],
        wait:0,elapsed:0,ages:{},rows:[],clone_rows:[],
        natural_clone_rates:{},natural_clone:undefined,ghost_rows:[],ghost:undefined,
        clone_rate:0,clone_source:noone,clone_copy:noone,clone_top:noone,clone_controller:noone};
}

function scrFREnemyVisibilityNext(_state) {
    scrNTTEFullWorldEventsCleanup();scrFRWallFixTestsReset(_state.world);
    if(++_state.index>=array_length(_state.cases)) {
        assert((_state.natural_clone_rates[$ "30"]??false)
            && (_state.natural_clone_rates[$ "60"]??false),
            "Natural City clone acceptance omitted a real30/60Hz map witness");
        _state.phase=4;return;
    }
    var _case=_state.cases[_state.index];
    save_set_value("options","framerate",_case.rate);save_set_value("options","autopause",false);
    save_set_value("visual","freezeframes",0);scrOptionsUpdate();
    scrNTTEFullWorldEventsNaturalWorldConfigure(_state.world,[area_city,_case.subarea],_case.seed);
    GameCont.loops=_case.loops;GameCont.hard=3+10*_case.loops;GameCont.is_level_ended=true;
    GameCont.popolevel=0;GameCont.killenemies=false;
    global.fr_continue_generation=undefined;global.fr_continue_events=undefined;
    _state.elapsed=0;_state.wait=0;_state.ages={};_state.row={seed:_case.seed,
        loops:_case.loops,subarea:_case.subarea,rate:_case.rate,samples:[]};
    _state.natural_clone=undefined;
    _state.phase=1;
    scrNTTESmokeLog("FRONTIER ENEMY VISIBILITY CITY BEGIN "+json_stringify(_case));
}

function scrFREnemyVisibilityNaturalCloneStart(_state) {
    var _case=_state.cases[_state.index],_rate=string(_case.rate);
    if(_state.natural_clone_rates[$ _rate]??false) return;
    var _source=noone;
    with(enemy) if(hp>=12 && size<5 && team!=team_player && visible
        && image_alpha>0 && mask_index!=mskNone && !(self[$ "canfly"]??false)
        && (self[$ "intro"]??true)!=false && place_meeting(x,y,Floor)
        && !place_meeting(x,y,Wall)) {_source=id;break;}
    if(!instance_exists(_source)) return;
    var _clone=instance_create(_source.x,_source.y,NTTEFullCrystalClone);
    assert(array_get_index(_clone.clone,_source)>=0,
        "Natural City source was absent from the genuine grounded clone candidate snapshot");
    _clone.clone=[_source];_clone.team=_source.team;
    // Reproduce the real ordering race after the default candidate snapshot:
    // the original Top constructor and gravity own every suspension field.
    var _top=scrNTTEFullTopCreate(_source.x,_source.y,_source,0,0);
    assert(instance_exists(_top) && _top.zfriction>0 && _source.mask_index==mskNone,
        "Natural City candidate did not enter a real falling Top lifecycle");
    with(_clone) event_perform(ev_step,ev_step_normal);
    var _copy=_clone.target;
    assert(instance_exists(_copy) && instance_exists(_copy.ntte_full_top_object)
        && _copy.ntte_full_top_object!=_top
        && _copy.ntte_full_top_object.target==_copy,
        "Natural City clone did not acquire its own actual Top controller");
    _state.natural_clone={source:_source,copy:_copy,controller:_clone,
        source_top:_top,copy_top:_copy.ntte_full_top_object,phase:0,
        before:scrFREnemyVisibilitySnapshot(_copy),host_ticks:0};
    _state.natural_clone_rates[$ _rate]=true;
}

function scrFREnemyVisibilityNaturalCloneStep(_state) {
    var _trial=_state.natural_clone;
    if(is_undefined(_trial) || _trial.phase==2) return;
    var _copy=_trial.copy;
    assert(instance_exists(_copy),"Natural City clone disappeared before its real hit acceptance");
    if(_trial.phase==0) {
        if(_state.elapsed<30) return;
        if(instance_exists(_trial.copy_top) || instance_exists(_trial.source_top)
            || _copy.mask_index==mskNone || !_copy.visible) {
            assert(_state.elapsed<120,"Natural City clone never landed/revealed through its ordinary scheduler");
            return;
        }
        _trial.landed=scrFREnemyVisibilitySnapshot(_copy);
        _trial.separated=scrFREnemyVisibilitySeparateHitBodies(_copy);
        _trial.hp=_copy.hp;_copy.nexthurt=-1;
        var _bullet=instance_create(_copy.x,_copy.y,Bullet1);
        _bullet.creator=instance_find(Player,0);_bullet.team=team_player;_bullet.speed=0;
        _trial.bullet=_bullet;_trial.phase=1;
        _state.active_hit_bullet=_bullet;_state.active_hit_target=_copy;_state.active_hit_record=undefined;
        return;
    }
    if(_copy.hp==_trial.hp && ++_trial.host_ticks<8) return;
    var _record=_state.active_hit_record;
    var _hit=(!is_undefined(_record) && _record.damage==3
        && _record.target==real(_copy) && !instance_exists(_trial.bullet));
    if(!_hit) scrFREnemyVisibilitySaveHitFailure(_state,_trial,"natural-city-clone");
    assert(_hit,
        "Natural City landed clone could not be damaged by real friendly Bullet1 collision");
    _trial.after_hit=scrFREnemyVisibilitySnapshot(_copy);_trial.phase=2;
    _state.row.natural_clone={before:_trial.before,landed:_trial.landed,
        after_hit:_trial.after_hit,damage:_trial.hp-_copy.hp,
        source:real(_trial.source),bullet:real(_trial.bullet),host_ticks:_trial.host_ticks,
        separated_hit_bodies:_trial.separated,actual_bullet_collision:_record};
}

function scrFREnemyVisibilitySeparateHitBodies(_copy) {
    var _bodies=ds_list_create(),_moved=[];
    try {
        with(_copy) instance_place_list(x,y,hitme,_bodies,false);
        // Native collision order is allowed to visit the earlier source body
        // first. Isolate that real mask using another generated Floor; keep
        // the target copy, its HP/mask and projectile dispatch unchanged.
        for(var _i=0;_i<ds_list_size(_bodies);++_i) {
            var _body=_bodies[|_i];
            if(!instance_exists(_body) || _body==_copy || _body.team==team_player) continue;
            var _before=scrFREnemyVisibilitySnapshot(_body),_destination=noone,
                _distance=infinity,_px=_copy.x,_py=_copy.y;
            with(Floor) {
                var _fx=(bbox_left+bbox_right+1)/2,_fy=(bbox_top+bbox_bottom+1)/2,
                    _d=point_distance(_fx,_fy,_px,_py),_fits=false;
                if(_d<128 || _d>=_distance) continue;
                with(_body) _fits=place_meeting(_fx,_fy,Floor)
                    && !place_meeting(_fx,_fy,Wall) && !place_meeting(_fx,_fy,_copy);
                if(_fits) {_destination=id;_distance=_d;}
            }
            assert(instance_exists(_destination),
                "Natural City bullet witness could not isolate an overlapping body on real Floor");
            _body.x=(_destination.bbox_left+_destination.bbox_right+1)/2;
            _body.y=(_destination.bbox_top+_destination.bbox_bottom+1)/2;
            _body.xprevious=_body.x;_body.yprevious=_body.y;
            var _overlap=false;
            with(_copy) _overlap=place_meeting(x,y,_body);
            assert(!_overlap,"Real Floor body isolation left a source over the hit-test copy");
            array_push(_moved,{before:_before,after:scrFREnemyVisibilitySnapshot(_body),
                floor:real(_destination)});
        }
    } finally {ds_list_destroy(_bodies);}
    return _moved;
}

function scrFREnemyVisibilitySaveHitFailure(_state,_trial,_kind) {
    var _row={kind:_kind,case:(_state.clone_only || _state.toss_only)?{clone_rate:30/timescale}:
            _state.cases[clamp(_state.index,0,array_length(_state.cases)-1)],
        expected_hp_before:_trial.hp,source_ticks:_state.elapsed,
        source:instance_exists(_trial.source)?scrFREnemyVisibilitySnapshot(_trial.source):"destroyed",
        copy:instance_exists(_trial.copy)?scrFREnemyVisibilitySnapshot(_trial.copy):"destroyed",
        bullet:instance_exists(_trial.bullet)?scrFREnemyVisibilityShotSnapshot(_trial.bullet):"consumed",
        separated_hit_bodies:_trial.separated??[]};
    var _file=file_text_open_write(working_directory+"frontier-enemy-visibility-hit-failure.json");
    file_text_write_string(_file,json_stringify(_row));file_text_close(_file);
    scrNTTESmokeLog("FRONTIER ENEMY VISIBILITY HIT FAILURE "+json_stringify(_row));
}

function scrFREnemyVisibilityShotSnapshot(_shot) {
    var _row={id:real(_shot),object:object_get_name(_shot.object_index),x:_shot.x,y:_shot.y,
        hspeed:_shot.hspeed,vspeed:_shot.vspeed,damage:_shot.damage,
        team:_shot.team,creator:real(_shot.creator),mask:real(_shot.mask_index),
        left:_shot.bbox_left,right:_shot.bbox_right,top:_shot.bbox_top,bottom:_shot.bbox_bottom,
        wall:false,floor:false,hitme:[]};
    with(_shot) {
        _row.wall=place_meeting(x,y,Wall);_row.floor=place_meeting(x,y,Floor);
        var _list=ds_list_create();
        try {
            instance_place_list(x,y,hitme,_list,false);
            for(var _i=0;_i<ds_list_size(_list);++_i) {
                var _body=_list[|_i];
                array_push(_row.hitme,{id:real(_body),object:object_get_name(_body.object_index),
                    hp:_body.hp,team:_body.team,x:_body.x,y:_body.y,mask:real(_body.mask_index)});
            }
        } finally {ds_list_destroy(_list);}
    }
    return _row;
}

function scrFREnemyVisibilityBulletBefore(_shot,_target) {
    var _driver=instance_find(FRIntegrationTest,0);
    if(!instance_exists(_driver)) return undefined;
    var _state=_driver[$ "fr_enemy_visibility"]??undefined;
    if(is_undefined(_state) || (_state[$ "active_hit_bullet"]??noone)!=_shot
        || (_state[$ "active_hit_target"]??noone)!=_target) return undefined;
    return {state:_state,bullet:real(_shot),target:real(_target),hp_before:_target.hp,
        damage_field:_shot.damage,team:_shot.team,object:object_get_name(_shot.object_index),
        frame:current_frame,source_ticks:_state.elapsed,
        target_before:scrFREnemyVisibilitySnapshot(_target)};
}

function scrFREnemyVisibilityBulletAfter(_record) {
    var _state=_record.state;variable_struct_remove(_record,"state");
    _record.hp_after=instance_exists(_record.target)?_record.target.hp:undefined;
    _record.damage=_record.hp_before-_record.hp_after;
    _record.bullet_consumed=!instance_exists(_record.bullet);
    _state.active_hit_record=_record;
    scrNTTESmokeLog("FRONTIER ENEMY VISIBILITY ACTUAL BULLET COLLISION "+json_stringify(_record));
}

function scrFREnemyVisibilityGhostStart(_state) {
    var _ghost=noone;
    with(FRCustomEnemy) if(name=="Voltergeist" && possessing && instance_exists(possess_target)
        && instance_is(possess_target,enemy) && possess_target.hp>0
        && possess_target.mask_index!=mskNone) {_ghost=id;break;}
    if(!instance_exists(_ghost)) return false;
    var _host=_ghost.possess_target,_bullet=instance_create(_host.x,_host.y,Bullet1);
    _bullet.creator=instance_find(Player,0);_bullet.team=team_player;_bullet.speed=0;
    _bullet.damage=max(100,_host.hp+10);
    _state.ghost={ghost:_ghost,host:_host,bullet:_bullet,elapsed:0,
        before:scrFREnemyVisibilitySnapshot(_ghost),host_hp:_host.hp};
    _state.phase=9;return true;
}

function scrFREnemyVisibilityClonePrepare(_state) {
    scrNTTEFullWorldEventsCleanup();scrFRWallFixTestsReset(_state.world);
    save_set_value("options","framerate",_state.clone_rate==0?30:60);
    save_set_value("options","autopause",false);scrOptionsUpdate();
    _state.wait=0;_state.phase=5;
}

function scrFREnemyVisibilityCloneCreate(_state) {
    var _x=934016,_y=934016;
    GameCont.area=area_city;GameCont.loops=3;GameCont.is_level_ended=true;
    for(var _ix=0;_ix<7;++_ix) for(var _iy=0;_iy<7;++_iy)
        instance_create(_x+32*_ix,_y+32*_iy,Floor);
    for(var _ix=0;_ix<14;++_ix) instance_create(_x+16*_ix,_y-16,Wall);
    var _source=instance_create(_x+64,_y+64,Bandit);
    _source.hp=1000;_source.team=team_enemy;_source.intro=true;_source.speed=0;
    _source.alarm[1]=91;
    var _controller=instance_create(_source.x,_source.y,NTTEFullCrystalClone);
    assert(array_get_index(_controller.clone,_source)>=0,
        "Crystal race fixture did not capture the genuine grounded default candidate");
    _controller.clone=[_source];_controller.team=team_enemy;_controller.budge=false;
    // Elevation happens after the grounded candidate snapshot. Keep the copy
    // in the same nearby wall lip/search envelope that original topify scans.
    var _top=scrNTTEFullTopCreate(_x+64,_y-16,_source,0,0);
    _top.z=48;_top.zspeed=0;_top.zfriction=0;_top.jump=0;_top.grav=0;_top.canmove=false;
    _top.hspeed=0.3*timescale;_top.vspeed=0.1*timescale;
    with(_top) scrNTTEFullTopEndStep();
    // Snapshot a genuine active vertical flight phase after initial setup.
    _top.zspeed=0.6;_top.zfriction=0.02;
    assert(_source.mask_index==mskNone && _top.target==_source,
        "Crystal race source did not enter genuine suspended wall-top state");
    with(_controller) event_perform(ev_step,ev_step_normal);
    var _copy=_controller.target;
    assert(instance_exists(_copy) && _copy!=_source,
        "Crystal race failed to create a real independently existing enemy copy");
    var _copy_top=_copy.ntte_full_top_object;
    assert(instance_exists(_copy_top) && _copy_top!=_top && _copy_top.target==_copy,
        "Crystal wall copy inherited somebody else's Top controller");
    var _motion={rate:30/timescale,source:scrFREnemyVisibilityTopMotion(_top),
        copy:scrFREnemyVisibilityTopMotion(_copy_top)};
    scrNTTESmokeLog("FRONTIER ENEMY CLONE TOP INITIAL MOTION "+json_stringify(_motion));
    assert(_copy_top.hspeed==_top.hspeed && _copy_top.vspeed==_top.vspeed
        && _copy_top.z==_top.z && _copy_top.zspeed==_top.zspeed
        && _copy_top.zfriction==_top.zfriction,
        "Independent Top clone omitted its source's actual planar velocity");
    var _saved_alarm=_top.target_save.ntte_full_saved_alarms[1];
    _copy_top.target_save.ntte_full_saved_alarms[1]=_saved_alarm+7;
    assert(_top.target_save.ntte_full_saved_alarms[1]==_saved_alarm,
        "Independent wall clone shares mutable saved alarm state with source");
    _copy_top.target_save.ntte_full_saved_alarms[1]=_saved_alarm;
    assert(_copy.xstart>=_top.search_x1 && _copy.xstart<=_top.search_x2
        && _copy.ystart>=_top.search_y1 && _copy.ystart<=_top.search_y2,
        "Crystal race copy lies outside original auto-topify discovery envelope");
    _state.clone_source=_source;_state.clone_copy=_copy;_state.clone_top=_top;
    _state.clone_controller=_controller;_state.elapsed=0;
    _state.clone_copy_top=_copy_top;
    _state.clone_top_offset_x=_copy_top.x-_top.x;
    _state.clone_top_offset_y=_copy_top.y-_top.y;
    _state.clone_row={rate:30/timescale,source_before:scrFREnemyVisibilitySnapshot(_source),
        initial_motion:_motion,
        copy_at_create:scrFREnemyVisibilitySnapshot(_copy),samples:[],
        original_semantics:"CrystalClone_create captures candidates once; instance_clone copies all fields shallowly; tegeneral ntte_setup_topify handles new nearby actors"};
    _state.phase=6;
}

function scrFREnemyVisibilityTopMotion(_top) {
    return {id:real(_top),x:_top.x,y:_top.y,xprevious:_top.xprevious,yprevious:_top.yprevious,
        hspeed:_top.hspeed,vspeed:_top.vspeed,speed:_top.speed,direction:_top.direction,
        friction:_top.friction,gravity:_top.gravity,gravity_direction:_top.gravity_direction,
        z:_top.z,zspeed:_top.zspeed,zfriction:_top.zfriction,
        target:real(_top.target),target_x:_top.target.x,target_y:_top.target.y,
        target_xprevious:_top.target.xprevious,target_yprevious:_top.target.yprevious};
}

function scrFREnemyVisibilityTossMotion(_toss) {
    return {id:real(_toss),creator:real(_toss.creator),x:_toss.x,y:_toss.y,
        xprevious:_toss.xprevious,yprevious:_toss.yprevious,
        direction:_toss.direction,hspeed:_toss.hspeed,vspeed:_toss.vspeed,
        speed:_toss.speed,friction:_toss.friction,
        z:_toss.z,zspeed:_toss.zspeed,zfriction:_toss.zfriction,
        saved_mask:real(_toss.mask_index),saved_depth:_toss.depth,
        saved_shadow_y:_toss.spr_shadow_y,cleaned:_toss.ntte_toss_cleaned,
        target:scrFREnemyVisibilitySnapshot(_toss.creator)};
}

function scrFREnemyVisibilityTossCreate(_state) {
    var _x=944016,_y=944016;
    GameCont.area=area_city;GameCont.loops=3;GameCont.is_level_ended=true;
    for(var _ix=0;_ix<12;++_ix) for(var _iy=0;_iy<10;++_iy)
        instance_create(_x+32*_ix,_y+32*_iy,Floor);
    var _source=instance_create(_x+64,_y+160,Bandit);
    _source.hp=1000;_source.team=team_enemy;_source.intro=true;
    _source.speed=0;_source.walk=0;_source.alarm[1]=-1;_source.nexthurt=-1;
    var _ground=scrFREnemyVisibilitySnapshot(_source),
        _controller=instance_create(_source.x,_source.y,NTTEFullCrystalClone);
    assert(array_get_index(_controller.clone,_source)>=0,
        "Toss race omitted a genuine grounded default clone candidate");
    _controller.clone=[_source];_controller.team=team_enemy;_controller.budge=false;
    // Use the original controller and its real suspension write after the
    // candidate snapshot. No mask/depth/canfly is supplied by this fixture.
    var _toss=instance_create(_source.x,_source.y,NTTEFullPalankingToss);
    _toss.creator=_source;_toss.depth=_source.depth;_toss.mask_index=_source.mask_index;
    _toss.spr_shadow_y=_source.spr_shadow_y;_toss.direction=15;_toss.speed=2*timescale;
    _toss.z=48;_toss.zspeed=0.6;_toss.zfriction=0.05;
    with(_toss) event_perform(ev_step,ev_step_end);
    assert(_source.mask_index==mskNone && _source.canfly && _source.depth==-9,
        "Original Toss did not actually suspend its captured source");
    with(_controller) event_perform(ev_step,ev_step_normal);
    var _copy=_controller.target,_copy_toss=noone;
    with(NTTEFullPalankingToss) if(creator==_copy && !ntte_toss_cleaned) {_copy_toss=id;break;}
    assert(instance_exists(_copy) && instance_exists(_copy_toss) && _copy_toss!=_toss
        && _toss.creator==_source && _copy_toss.creator==_copy,
        "Crystal Toss copy failed to own an independent real native controller");
    assert(_copy.mask_index==mskNone && _copy.canfly && _copy.depth==-9,
        "Toss clone acceptance forced an early hittable mask instead of preserving flight");
    var _motion={source:scrFREnemyVisibilityTossMotion(_toss),
        copy:scrFREnemyVisibilityTossMotion(_copy_toss)};
    assert(_copy_toss.hspeed==_toss.hspeed && _copy_toss.vspeed==_toss.vspeed
        && _copy_toss.z==_toss.z && _copy_toss.zspeed==_toss.zspeed
        && _copy_toss.zfriction==_toss.zfriction,
        "Toss clone did not preserve its already running movement phase");
    _state.toss_source=_source;_state.toss_copy=_copy;
    _state.toss_source_toss=_toss;_state.toss_copy_toss=_copy_toss;
    _state.toss_controller=_controller;_state.toss_initial_hp=_copy.hp;
    _state.toss_offset_x=_copy_toss.x-_toss.x;
    _state.toss_offset_y=_copy_toss.y-_toss.y;
    _state.toss_row={rate:30/timescale,grounded_source:_ground,
        initial_motion:_motion,copy_at_create:scrFREnemyVisibilitySnapshot(_copy)};
    _state.elapsed=0;_state.phase=12;
}

function scrFREnemyVisibilityFinish(_state) {
    var _file=file_text_open_write(working_directory+"frontier-enemy-visibility-diagnostic.json");
    file_text_write_string(_file,json_stringify({
        clone_top_repair_tested:array_length(_state.clone_rows)==2,
        clone_toss_repair_tested:array_length(_state.toss_rows)==2,
        clone_only:_state.clone_only,toss_only:_state.toss_only,physical_device_tested:false,
        natural_city:_state.rows,clone_top_race:_state.clone_rows,
        clone_toss_race:_state.toss_rows,possessed_host_deaths:_state.ghost_rows}));
    file_text_close(_file);
    scrNTTEFullWorldEventsNaturalWorldRestore(_state.world);
    scrNTTESmokeLog("PASS FRONTIER ENEMY VISIBILITY "+string(array_length(_state.rows))
        +" natural City maps; independent Top cases="+string(array_length(_state.clone_rows))
        +", independent Toss cases="+string(array_length(_state.toss_rows))
        +"; scheduled Bullet1 and real Guardian damage accepted30/60Hz");
    return true;
}

function scrFREnemyVisibilityTestsStep(_driver) {
    var _state=_driver.fr_enemy_visibility;
    with(Player) {
        hp=100000;max_hp=100000;nexthurt=current_frame+100000;
        speed=0;can_walk=false;can_aim=false;can_spec=false;can_shoot=false;bcan_shoot=false;
    }
    GameCont.is_level_ended=true;
    if(_state.phase==0) {scrFREnemyVisibilityNext(_state);return false;}
    if(_state.phase==1) {
        if(++_state.wait<3) return false;
        var _case=_state.cases[_state.index];
        assert(30/timescale==_case.rate,"City diagnostic did not apply the actual requested rate");
        if(!instance_exists(BackCont)) instance_create(0,0,BackCont);
        var _gen=instance_create(0,0,GenCont);
        assert(instance_exists(_gen) && !_gen.ntte_full_sync_generation,
            "Enemy diagnostic replaced actual asynchronous generation");
        _state.wait=0;_state.phase=2;return false;
    }
    if(_state.phase==2) {
        assert(++_state.wait<3600,"City diagnostic natural generator did not settle");
        if(instance_exists(GenCont) || instance_exists(FloorMaker)) return false;
        var _case=_state.cases[_state.index];
        assert(GameCont.area==area_city && GameCont.subarea==_case.subarea
            && GameCont.loops==_case.loops,
            "City diagnostic generation changed its actual requested route/loop");
        assert(instance_number(Floor)>20 && instance_exists(Player),
            "City diagnostic omitted natural terrain or player");
        _state.row.floors=instance_number(Floor);_state.row.initial_enemies=instance_number(enemy);
        array_push(_state.row.samples,scrFREnemyVisibilityObserve(_state,true));
        scrFREnemyVisibilityNaturalCloneStart(_state);
        _state.elapsed=0;_state.phase=3;return false;
    }
    if(_state.phase==3) {
        var _case=_state.cases[_state.index];
        assert(GameCont.area==area_city && GameCont.subarea==_case.subarea
            && GameCont.loops==_case.loops && !instance_exists(GenCont),
            "City diagnostic transitioned/restored its observed map before sampling");
        var _old=_state.elapsed;_state.elapsed+=timescale;
        scrFREnemyVisibilityNaturalCloneStep(_state);
        var _sample=scrFREnemyVisibilityObserve(_state,false);
        if((_old<24 && _state.elapsed>=24) || (_old<90 && _state.elapsed>=90)
            || (_old<240 && _state.elapsed>=240)) array_push(_state.row.samples,_sample);
        if(_state.elapsed<240) return false;
        assert(is_undefined(_state.natural_clone) || _state.natural_clone.phase==2,
            "Natural City clone hit acceptance did not finish");
        if(array_length(_state.ghost_rows)<2 && scrFREnemyVisibilityGhostStart(_state)) return false;
        array_push(_state.rows,_state.row);
        scrNTTESmokeLog("FRONTIER ENEMY VISIBILITY CITY OBSERVED "+json_stringify(_state.row));
        scrFREnemyVisibilityNext(_state);return false;
    }
    if(_state.phase==9) {
        var _trial=_state.ghost;_trial.elapsed+=timescale;
        if(_trial.elapsed<60) return false;
        var _ghost=_trial.ghost,_host=_trial.host;
        assert(!instance_exists(_trial.bullet) && (!instance_exists(_host)
            || !instance_is(_host,enemy) || _host.hp<=0),
            "Real friendly bullet did not kill the natural possessed host");
        var _after=instance_exists(_ghost)?scrFREnemyVisibilitySnapshot(_ghost):undefined;
        assert(!instance_exists(_ghost) || _ghost.hp<=0 || (!_ghost.possessing
            && _ghost.image_alpha==1 && _ghost.mask_index==_ghost.mask_nrml),
            "Natural Voltergeist failed to restore its own visible hittable body after real host death");
        array_push(_state.ghost_rows,{before:_trial.before,after:_after,
            host:real(_host),host_exists:instance_exists(_host),host_hp_before:_trial.host_hp,
            host_after_object:instance_exists(_host)?object_get_name(_host.object_index):"destroyed"});
        array_push(_state.rows,_state.row);
        scrNTTESmokeLog("FRONTIER ENEMY VISIBILITY CITY OBSERVED "+json_stringify(_state.row));
        scrFREnemyVisibilityNext(_state);return false;
    }
    if(_state.phase==4) {scrFREnemyVisibilityClonePrepare(_state);return false;}
    if(_state.phase==5) {
        if(++_state.wait<3) return false;
        scrFREnemyVisibilityCloneCreate(_state);return false;
    }
    if(_state.phase==6) {
        _state.elapsed+=timescale;
        assert(instance_exists(_state.clone_source) && instance_exists(_state.clone_copy)
            && instance_exists(_state.clone_controller),"Crystal diagnostic lost a live witness");
        if(_state.elapsed<26) return false;
        var _top=_state.clone_top;
        assert(abs((_state.clone_copy_top.x-_top.x)-_state.clone_top_offset_x)<2
            && abs((_state.clone_copy_top.y-_top.y)-_state.clone_top_offset_y)<2
            && abs(_state.clone_copy_top.z-_top.z)<0.001
            && abs(_state.clone_copy_top.zspeed-_top.zspeed)<0.001,
            "Independent moving Top copy diverged from its source's planar flight before landing");
        _state.clone_row.after_flight_motion={source:scrFREnemyVisibilityTopMotion(_top),
            copy:scrFREnemyVisibilityTopMotion(_state.clone_copy_top)};
        array_push(_state.clone_row.samples,{source_ticks:_state.elapsed,
            source:scrFREnemyVisibilitySnapshot(_state.clone_source),
            copy:scrFREnemyVisibilitySnapshot(_state.clone_copy)});
        assert(_state.clone_controller.appear<=0 && _state.clone_copy.visible,
            "Crystal diagnostic appearance failed to finish after26 source ticks");
        _top.z=0;_top.zspeed=0;_top.zfriction=0;
        with(_top) event_perform(ev_step,ev_step_end);
        assert(!instance_exists(_top) && _state.clone_source.mask_index!=mskNone,
            "Crystal diagnostic genuine source landing did not restore its own mask");
        _state.elapsed=0;_state.phase=7;return false;
    }
    if(_state.phase==7) {
        _state.elapsed+=timescale;if(_state.elapsed<3) return false;
        _state.clone_row.after_source_landing={source:scrFREnemyVisibilitySnapshot(_state.clone_source),
            copy:scrFREnemyVisibilitySnapshot(_state.clone_copy)};
        var _copy=_state.clone_copy,_copy_top=_state.clone_copy_top;
        assert(instance_exists(_copy_top) && _copy_top.target==_copy
            && _copy.ntte_full_top_object==_copy_top && _copy.mask_index==mskNone,
            "Landing source changed its copy's independent suspended lifecycle");
        _copy_top.z=0;_copy_top.zspeed=0;_copy_top.zfriction=0;
        with(_copy_top) event_perform(ev_step,ev_step_end);
        assert(!instance_exists(_copy_top) && _copy.ntte_full_top_object==noone
            && _copy.mask_index==_state.clone_source.mask_index
            && _copy.mask_index!=mskNone && _copy.alarm[1]>=88,
            "Independent clone landing failed to restore its actual mask/AI alarm");
        _state.clone_row.after_copy_landing=scrFREnemyVisibilitySnapshot(_copy);
        // Separate the restored source body so the real collision scheduler
        // cannot let it intercept the friendly projectile intended for copy.
        _state.clone_source.x+=160;_state.clone_source.xprevious=_state.clone_source.x;
        _copy.speed=0;_copy.walk=0;_copy.alarm[1]=-1;
        _state.hit_hp=_copy.hp;_state.hit_ticks=0;
        var _shot=instance_create(_copy.x,_copy.y,Bullet1);
        _shot.creator=instance_find(Player,0);_shot.team=team_player;_shot.speed=0;
        _state.hit_bullet=_shot;_state.clone_row.bullet_before={id:real(_shot),
            object:object_get_name(_shot.object_index),team:_shot.team,
            target:real(_copy),target_hp:_copy.hp,mask:real(_copy.mask_index),
            source:scrFREnemyVisibilitySnapshot(_state.clone_source),
            copy:scrFREnemyVisibilitySnapshot(_copy),projectile:scrFREnemyVisibilityShotSnapshot(_shot)};
        _state.active_hit_bullet=_shot;_state.active_hit_target=_copy;_state.active_hit_record=undefined;
        scrNTTESmokeLog("FRONTIER ENEMY CLONE BULLET BEFORE "+json_stringify(_state.clone_row.bullet_before));
        _state.phase=8;return false;
    }
    if(_state.phase==8) {
        var _copy=_state.clone_copy;
        if(_copy.hp==_state.hit_hp && ++_state.hit_ticks<6) return false;
        var _record=_state.active_hit_record;
        var _hit=!is_undefined(_record) && _record.damage==3
            && _record.target==real(_copy) && !instance_exists(_state.hit_bullet);
        if(!_hit) {
            var _trial={source:_state.clone_source,copy:_copy,bullet:_state.hit_bullet,
                hp:_state.hit_hp,separated:[]};
            scrFREnemyVisibilitySaveHitFailure(_state,_trial,"independent-moving-clone");
        }
        assert(_hit,
            "Real friendly Bullet1 scheduled collision could not hurt restored wall clone");
        _state.clone_row.bullet_after={hp:_copy.hp,damage:_state.hit_hp-_copy.hp,
            scheduled_host_ticks:_state.hit_ticks,actual_bullet_collision:_record};
        _state.pet_hp=_copy.hp;_copy.nexthurt=-1;
        var _pet=instance_create(_copy.x,_copy.y,NTTEFullPet);
        with(_pet) {
            pet="Guardian";scrNTTEFullPetGuardianCreate();hp=max_hp;
            leader=instance_find(Player,0);team=team_player;visible=true;
            sprite_index=spr_idle;direction=0;dash_charge=1;
            scrNTTEFullPetGuardianDashHit();
        }
        assert(_copy.hp==_state.pet_hp-15 && _pet.stat.punches>=1,
            "Real Guardian dash hit could not damage restored clone through actual collision mask");
        _state.clone_row.guardian_hit={pet:real(_pet),target:real(_copy),
            damage:_state.pet_hp-_copy.hp,punches:_pet.stat.punches};
        array_push(_state.clone_rows,_state.clone_row);
        scrNTTESmokeLog("FRONTIER ENEMY VISIBILITY CLONE OBSERVED "+json_stringify(_state.clone_row));
        if(++_state.clone_rate<2) {_state.phase=4;return false;}
        if(_state.clone_only) return scrFREnemyVisibilityFinish(_state);
        _state.phase=10;return false;
    }
    if(_state.phase==10) {
        scrNTTEFullWorldEventsCleanup();scrFRWallFixTestsReset(_state.world);
        save_set_value("options","framerate",_state.toss_rate==0?30:60);
        save_set_value("options","autopause",false);scrOptionsUpdate();
        _state.wait=0;_state.phase=11;return false;
    }
    if(_state.phase==11) {
        if(++_state.wait<3) return false;
        scrFREnemyVisibilityTossCreate(_state);return false;
    }
    if(_state.phase==12) {
        _state.elapsed+=timescale;if(_state.elapsed<26) return false;
        var _source_toss=_state.toss_source_toss,_copy_toss=_state.toss_copy_toss;
        assert(instance_exists(_source_toss) && instance_exists(_copy_toss)
            && instance_exists(_state.toss_source) && instance_exists(_state.toss_copy),
            "Moving Toss witness disappeared before appearance completed");
        assert(abs((_copy_toss.x-_source_toss.x)-_state.toss_offset_x)<0.01
            && abs((_copy_toss.y-_source_toss.y)-_state.toss_offset_y)<0.01
            && abs(_copy_toss.z-_source_toss.z)<0.001
            && abs(_copy_toss.zspeed-_source_toss.zspeed)<0.001,
            "Independent Toss movement diverged from its source snapshot");
        assert(_state.toss_controller.appear<=0 && _state.toss_copy.visible,
            "Toss clone appearance failed its original24-source-tick completion");
        _state.toss_row.after_flight_motion={source:scrFREnemyVisibilityTossMotion(_source_toss),
            copy:scrFREnemyVisibilityTossMotion(_copy_toss)};
        // Real Destroy/Cleanup must restore only the original creator. The
        // copy continues scheduled gravity and must land through EndStep.
        instance_destroy(_source_toss);
        var _source=_state.toss_source,_copy=_state.toss_copy;
        _state.toss_row.after_source_cleanup={source:scrFREnemyVisibilitySnapshot(_source),
            copy:scrFREnemyVisibilitySnapshot(_copy),copy_toss_exists:instance_exists(_copy_toss)};
        assert(_source.mask_index==_state.toss_row.grounded_source.mask
            && !_source.canfly && _source.depth==_state.toss_row.grounded_source.depth
            && instance_exists(_copy_toss) && _copy_toss.creator==_copy
            && _copy.mask_index==mskNone && _copy.canfly,
            "Original Toss Cleanup failed independent source/copy ownership");
        _source.x+=160;_source.xprevious=_source.x;
        _state.phase=13;return false;
    }
    if(_state.phase==13) {
        _state.elapsed+=timescale;
        if(instance_exists(_state.toss_copy_toss)) {
            assert(_state.elapsed<120,"Copied Toss never landed through its actual scheduled gravity");
            return false;
        }
        var _copy=_state.toss_copy,_landed=scrFREnemyVisibilitySnapshot(_copy);
        assert(_copy.visible && _copy.mask_index==_state.toss_row.grounded_source.mask
            && !_copy.canfly && _copy.depth==_state.toss_row.grounded_source.depth
            && _landed.floor_contact && !_landed.wall_contact,
            "Actual copied Toss landing failed to restore its hittable ground body");
        _state.toss_row.after_copy_landing=_landed;
        _state.toss_row.landing_damage=_state.toss_initial_hp-_copy.hp;
        assert(_state.toss_row.landing_damage==1,
            "Copied Toss changed the original native one-HP landing damage");
        _copy.speed=0;_copy.walk=0;_copy.alarm[1]=-1;_copy.nexthurt=-1;
        _state.hit_hp=_copy.hp;_state.hit_ticks=0;
        var _shot=instance_create(_copy.x,_copy.y,Bullet1);
        _shot.creator=instance_find(Player,0);_shot.team=team_player;_shot.speed=0;
        _state.hit_bullet=_shot;_state.active_hit_bullet=_shot;
        _state.active_hit_target=_copy;_state.active_hit_record=undefined;
        _state.toss_row.bullet_before={target:real(_copy),hp:_copy.hp,
            projectile:scrFREnemyVisibilityShotSnapshot(_shot)};
        _state.phase=14;return false;
    }
    if(_state.phase==14) {
        var _copy=_state.toss_copy;
        if(_copy.hp==_state.hit_hp && ++_state.hit_ticks<8) return false;
        var _record=_state.active_hit_record;
        var _hit=!is_undefined(_record) && _record.damage==3
            && _record.target==real(_copy) && _copy.hp==_state.hit_hp-3
            && !instance_exists(_state.hit_bullet);
        if(!_hit) scrFREnemyVisibilitySaveHitFailure(_state,
            {source:_state.toss_source,copy:_copy,bullet:_state.hit_bullet,
                hp:_state.hit_hp,separated:[]},"independent-moving-toss-clone");
        assert(_hit,
            "Real native Bullet1 did not deal exactly3HP to the naturally landed Toss copy");
        _state.toss_row.actual_bullet_collision=_record;
        _state.pet_hp=_copy.hp;_copy.nexthurt=-1;
        var _pet=instance_create(_copy.x,_copy.y,NTTEFullPet);
        with(_pet) {
            pet="Guardian";scrNTTEFullPetGuardianCreate();hp=max_hp;
            leader=instance_find(Player,0);team=team_player;visible=true;
            sprite_index=spr_idle;direction=0;dash_charge=1;
            scrNTTEFullPetGuardianDashHit();
        }
        assert(_copy.hp==_state.pet_hp-15 && _pet.stat.punches>=1,
            "Actual Guardian dash failed to hit the restored Toss copy");
        _state.toss_row.guardian_hit={pet:real(_pet),target:real(_copy),
            damage:_state.pet_hp-_copy.hp,punches:_pet.stat.punches};
        array_push(_state.toss_rows,_state.toss_row);
        scrNTTESmokeLog("FRONTIER ENEMY VISIBILITY TOSS OBSERVED "+json_stringify(_state.toss_row));
        if(++_state.toss_rate<2) {_state.phase=10;return false;}
        return scrFREnemyVisibilityFinish(_state);
    }
    return false;
}
