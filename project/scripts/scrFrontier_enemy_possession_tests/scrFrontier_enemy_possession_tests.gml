// Exercise authored Haunted City possession against real native host
// transitions. No test code changes the spirit's visibility, mask or HP.
// Friendly projectile and Guardian damage must work after source detachment.
function scrFREnemyPossessionTestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Possession diagnostic requires the settled isolated native runner");
    _driver.fr_enemy_possession={world:scrNTTEFullWorldEventsNaturalWorldCapture(),
        cases:[],index:-1,phase:0,elapsed:0,rows:[]};
    var _state=_driver.fr_enemy_possession;
    for(var _rate=30;_rate<=60;_rate+=30) {
        array_push(_state.cases,{rate:_rate,kind:"native-host-death",type:Wolf});
        array_push(_state.cases,{rate:_rate,kind:"native-car-pickup",type:SnowBot});
        array_push(_state.cases,{rate:_rate,kind:"native-parrot-charm",type:Wolf});
        array_push(_state.cases,{rate:_rate,kind:"living-host-control",type:Wolf});
    }
}

function scrFREnemyPossessionTestsSave(_state) {
    var _path=working_directory+"frontier-enemy-possession-diagnostic.json",
        _file=file_text_open_write(_path);
    file_text_write_string(_file,json_stringify({reported_area:"City 5-1",loops:1,
        screenshot_hp:17,regression:true,physical_device_tested:false,
        cases:_state.rows}));
    file_text_close(_file);
}

function scrFREnemyPossessionTestsNext(_state) {
    scrNTTEFullWorldEventsCleanup();scrFRWallFixTestsReset(_state.world);
    if(++_state.index>=array_length(_state.cases)) {
        scrFREnemyPossessionTestsSave(_state);
        scrNTTEFullWorldEventsNaturalWorldRestore(_state.world);
        return true;
    }
    var _case=_state.cases[_state.index];
    save_set_value("options","framerate",_case.rate);
    save_set_value("options","autopause",false);scrOptionsUpdate();
    GameCont.area=area_city;GameCont.subarea=1;GameCont.loops=1;GameCont.hard=13;
    GameCont.is_level_ended=true;GameCont.killenemies=false;GameCont.popolevel=0;
    _state.elapsed=0;_state.wait=0;_state.phase=1;
    scrNTTESmokeLog("FRONTIER ENEMY POSSESSION BEGIN "+json_stringify(_case));
    return false;
}

function scrFREnemyPossessionTestsCreate(_state) {
    var _case=_state.cases[_state.index],_x=936016,_y=936016;
    for(var _ix=0;_ix<16;++_ix) for(var _iy=0;_iy<16;++_iy)
        instance_create(_x+32*_ix,_y+32*_iy,Floor);
    // Run the actual registered HauntedCity source constructor. Sixteen
    // legitimate candidates preserve its real one-in-four random selection.
    // Bounded retries use new ordinary hosts, not a fabricated hidden ghost.
    var _ghost=noone,_host=noone,_attempts=0;
    for(var _attempt=0;_attempt<4 && !instance_exists(_ghost);++_attempt) {
        for(var _i=0;_i<16;++_i)
            instance_create(_x+32*_i,_y+64,_case.type);
        scrFRInvoke(GameCont.id,["mod","Frontier_Events","HauntedCity_create"],[]);
        ++_attempts;
        with(FRCustomEnemy) if(name=="Voltergeist" && possessing
            && instance_exists(possess_target) && possess_target.object_index==_case.type) {
            _ghost=id;_host=possess_target;break;
        }
    }
    assert(instance_exists(_ghost) && instance_exists(_host),
        "Actual HauntedCity constructor produced no ordinary possessed host");
    assert(_ghost.hp==17 && _ghost.max_hp==17 && _ghost.image_alpha==0
        && _ghost.mask_index==mskNone && _host.fr_possessed && _host.fr_possessor==_ghost,
        "Actual L1 HauntedCity did not match the reported17/17 hidden possessor");
    // Isolate the selected genuine pair from independent source-generated
    // actors. They cannot intercept the explicitly scheduled host-death shot.
    with(enemy) if(id!=_ghost && id!=_host) instance_destroy(id,false);
    // A real unpossessed hostile remains available to the authored spirit.
    // Without one its ordinary next-step behavior deliberately dies; keeping
    // a legitimate candidate lets the regression exercise actual hit masks.
    var _spare=instance_create(_host.x,_host.y+256,Wolf);
    _state.spare=_spare;
    _state.ghost=_ghost;_state.host=_host;
    _state.row={rate:_case.rate,kind:_case.kind,host_type:object_get_name(_case.type),
        source_constructor:"Frontier_Events::HauntedCity_create",attempts:_attempts,
        initial:scrFREnemyVisibilitySnapshot(_ghost),samples:[],detached:false,
        restored_hittable:false,host_action:undefined,
        spare:real(_spare),actual_bullet_collision:undefined,guardian_hit:undefined};
    _state.phase=2;_state.elapsed=0;
}

function scrFREnemyPossessionTestsAct(_state) {
    var _case=_state.cases[_state.index],_host=_state.host,_ghost=_state.ghost;
    assert(instance_exists(_host) && instance_exists(_ghost),
        "Possession diagnostic lost its genuine pair before the native action");
    _state.row.before_action=scrFREnemyVisibilitySnapshot(_ghost);
    if(_case.kind=="native-host-death") {
        var _shot=instance_create(_host.x,_host.y,Bullet1);
        _shot.creator=instance_find(Player,0);_shot.team=team_player;_shot.speed=0;
        _shot.damage=_host.hp+100;
        _state.shot=_shot;
        _state.row.host_action={bullet:real(_shot),damage:_shot.damage,
            host_hp:_host.hp,collision_dispatched_by_engine:true};
    } else if(_case.kind=="native-car-pickup") {
        var _car=instance_create(_host.x,_host.y,Car);
        _car.spr_idle=sprFrozenCar;_car.sprite_index=_car.spr_idle;
        _state.car=_car;
        _state.row.host_action={car:real(_car),collision_dispatched_by_engine:true};
    } else if(_case.kind=="native-parrot-charm") {
        var _charm=scrNTTEFullParrotCharm(_host,true),_player=instance_find(Player,0);
        _charm.index=_player.index;_charm.time=600;
        assert(_host.team==team_player && _charm.charmed,
            "Actual native Parrot charm failed to change the possessed host team");
        _state.row.host_action={native_charm:true,host_team:_host.team};
    } else {
        _state.row.host_action={unchanged_living_host:true,host_team:_host.team};
    }
    _state.phase=3;_state.elapsed=0;
}

function scrFREnemyPossessionTestsStep(_driver) {
    var _state=_driver.fr_enemy_possession;
    with(Player) {
        hp=100000;max_hp=100000;nexthurt=current_frame+100000;
        speed=0;can_walk=false;can_aim=false;can_spec=false;can_shoot=false;bcan_shoot=false;
    }
    GameCont.is_level_ended=true;
    if(_state.phase==0) return scrFREnemyPossessionTestsNext(_state);
    if(_state.phase==1) {
        if(++_state.wait<3) return false;
        assert(30/timescale==_state.cases[_state.index].rate,
            "Possession diagnostic did not apply its actual native rate");
        scrFREnemyPossessionTestsCreate(_state);return false;
    }
    if(_state.phase==2) {
        _state.elapsed+=timescale;
        if(_state.elapsed<3) return false;
        scrFREnemyPossessionTestsAct(_state);return false;
    }
    var _ghost=_state.ghost,_old=_state.elapsed,_case=_state.cases[_state.index];
    _state.elapsed+=timescale;
    if(_state.phase==4) {
        var _record=_state[$ "active_hit_record"]??undefined;
        if(is_undefined(_record) && ++_state.hit_wait<8) return false;
        assert(!is_undefined(_record) && _record.damage==3
            && _record.target==real(_ghost) && !instance_exists(_state.active_hit_bullet),
            "Detached real Voltergeist could not be damaged by scheduled friendly Bullet1");
        _state.row.actual_bullet_collision=_record;
        assert(instance_exists(_ghost),"Detached17HP spirit disappeared before native Guardian hit");
        var _before=_ghost.hp,_pet=instance_create(_ghost.x,_ghost.y,NTTEFullPet);
        // Native projectile hurt cooldown is six source ticks. Let that
        // original timer expire before the independently scheduled pet hit.
        _state.pet=_pet;_state.pet_hp=_before;_state.hit_wait=0;_state.phase=5;
        return false;
    }
    if(_state.phase==5) {
        if(++_state.hit_wait<14) return false;
        assert(instance_exists(_ghost) && !_ghost.possessing
            && _ghost.image_alpha==1 && _ghost.mask_index==_ghost.mask_nrml,
            "Detached spirit lost its restored native body before Guardian hit");
        var _pet=_state.pet,_before=_ghost.hp;
        _pet.x=_ghost.x;_pet.y=_ghost.y;
        with(_pet) {
            pet="Guardian";scrNTTEFullPetGuardianCreate();hp=max_hp;
            leader=instance_find(Player,0);team=team_player;visible=true;
            sprite_index=spr_idle;direction=0;dash_charge=1;
            scrNTTEFullPetGuardianDashHit();
        }
        assert(_ghost.hp==_before-15 && _pet.stat.punches>=1,
            "Detached real Voltergeist could not be damaged by native Guardian dash collision");
        _state.row.guardian_hit={pet:real(_pet),target:real(_ghost),
            damage:_before-_ghost.hp,punches:_pet.stat.punches};
        _state.row.ghost_after=scrFREnemyVisibilitySnapshot(_ghost);
        array_push(_state.rows,_state.row);scrFREnemyPossessionTestsSave(_state);
        scrNTTESmokeLog("FRONTIER ENEMY POSSESSION ACCEPTED "+json_stringify(_state.row));
        return scrFREnemyPossessionTestsNext(_state);
    }
    if(instance_exists(_ghost)) {
        if(!_ghost.possessing) _state.row.detached=true;
        if(!_ghost.possessing && _ghost.image_alpha==1 && _ghost.mask_index==_ghost.mask_nrml)
            _state.row.restored_hittable=true;
    }
    if((_old<1 && _state.elapsed>=1) || (_old<10 && _state.elapsed>=10)
        || (_old<30 && _state.elapsed>=30) || (_old<60 && _state.elapsed>=60))
        array_push(_state.row.samples,{source_ticks:_state.elapsed,
            ghost:instance_exists(_ghost)?scrFREnemyVisibilitySnapshot(_ghost):"destroyed"});
    if(_case.kind!="living-host-control" && _state.row.restored_hittable) {
        var _host=_state.host;
        if(_case.kind=="native-parrot-charm") {
            assert(instance_exists(_host) && _host.team==team_player && !_host.fr_possessed
                && _host.fr_possessor==noone && _host.fr_buffVoltergeist_time<=0,
                "Native charm detachment retained reciprocal ownership or infinite possession buff");
        }
        _state.row.host_after=instance_exists(_host)?{id:real(_host),
            object:object_get_name(_host.object_index),hp:_host.hp,team:_host.team}:"destroyed";
        _state.row.detached_at=_state.elapsed;
        _state.row.restored=scrFREnemyVisibilitySnapshot(_ghost);
        _state.hit_wait=0;
        var _shot=instance_create(_ghost.x,_ghost.y,Bullet1);
        _shot.creator=instance_find(Player,0);_shot.team=team_player;_shot.speed=0;
        _state.active_hit_bullet=_shot;_state.active_hit_target=_ghost;
        _state.active_hit_record=undefined;_state.phase=4;
        return false;
    }
    if(_case.kind!="living-host-control") {
        assert(_state.elapsed<10,
            "Actual native host transition left its hostile Voltergeist hidden or maskless");
        return false;
    }
    if(_state.elapsed<60) return false;
    var _host=_state.host;
    _state.row.host_after=instance_exists(_host)?{id:real(_host),
        object:object_get_name(_host.object_index),hp:_host.hp,team:_host.team}:"destroyed";
    _state.row.ghost_after=instance_exists(_ghost)?scrFREnemyVisibilitySnapshot(_ghost):"destroyed";
    assert(instance_exists(_ghost) && instance_exists(_host)
        && _ghost.possessing && _ghost.possess_target==_host
        && _ghost.image_alpha==0 && _ghost.mask_index==mskNone
        && _host.fr_possessed && _host.team!=team_player,
        "Living hostile possession was changed by the allied-host repair");
    array_push(_state.rows,_state.row);scrFREnemyPossessionTestsSave(_state);
    scrNTTESmokeLog("FRONTIER ENEMY POSSESSION ACCEPTED "+json_stringify(_state.row));
    return scrFREnemyPossessionTestsNext(_state);
}
