// Seeded asynchronous maps. Only the test emits real friendly Bullet1 bodies
// at currently visible, mask-bearing combatants. Natural hidden/spawned actors
// and all Top controllers retain their own scheduled AI/alarms/physics.
function scrFRBiomeClearance204NaturalState() {
    var _driver=instance_find(FRIntegrationTest,0);
    if(!instance_exists(_driver)) return undefined;
    var _s=_driver[$ "fr_biome_clearance204_natural"]??undefined;
    if(is_undefined(_s) || _s.phase==0 || !variable_struct_exists(_s,"row")) return undefined;
    return _s;
}
function scrFRBiomeClearance204NaturalCreated(_actor) {
    var _s=scrFRBiomeClearance204NaturalState();
    if(is_undefined(_s) || !instance_exists(_actor)) return;
    array_push(_s.row.births,{frame:current_frame,ticks:_s.elapsed,
        stage:_s.phase,actor:scrFRBiomeClearance204Snapshot(_actor),
        name:_actor[$ "name"]??"",callstack:debug_get_callstack(99)});
}
function scrFRBiomeClearance204NaturalLifecycle(_kind,_controller,_once=false) {
    var _s=scrFRBiomeClearance204NaturalState();
    if(is_undefined(_s) || !instance_exists(_controller)) return;
    var _key=_kind+":"+string(real(_controller));
    if(_once && (_s.seen[$ _key]??false)) return;
    _s.seen[$ _key]=true;
    var _target=_controller.object_index==NTTEFullTopObject?_controller.target:_controller.creator,
        _row={kind:_kind,frame:current_frame,ticks:_s.elapsed,stage:_s.phase,
        id:real(_controller),object:object_get_name(_controller.object_index),
        x:_controller.x,y:_controller.y,z:_controller.z,zspeed:_controller.zspeed,
        saved_mask:real(_controller.mask_index),saved_depth:_controller.depth,
        target:instance_exists(_target)?scrFRBiomeClearance204Snapshot(_target):{exists:false,id:real(_target)},
        target_name:instance_exists(_target)?(_target[$ "name"]??""):"",
        callstack:debug_get_callstack(99)};
    if(_controller.object_index==NTTEFullTopObject) _row.saved=_controller.target_save;
    else _row.cleaned=_controller.ntte_toss_cleaned;
    array_push(_s.row.lifecycle,_row);
}
function scrFRBiomeClearance204NaturalSample(_state,_all=false) {
    var _actors=[],_hidden=[],_spawn=[];
    with(enemy) if(team!=team_player && !instance_is(id,Van) && !instance_is(id,BigDogMissile)) {
        var _row=scrFREnemyVisibilitySnapshot(id);
        if(_all || !visible || mask_index==mskNone || _row.wall_contact || !_row.floor_contact)
            array_push(_actors,_row);
    }
    with(MeleeFake) if(team!=team_player)
        array_push(_hidden,scrFRBiomeClearance204Snapshot(id));
    with(becomenemy) if(!(variable_instance_exists(id,"team") && team==team_player))
        array_push(_spawn,{id:real(id),object:object_get_name(object_index),x:x,y:y,
            visible:visible,sprite:real(sprite_index),mask:real(mask_index),alarms:
                [alarm[0],alarm[1],alarm[2]],canspawn:self[$ "canspawn"]??undefined});
    var _prevent=[];
    with(NTTEFullPortalPrevent) array_push(_prevent,{id:real(id),creator:real(creator),
        owner_exists:instance_exists(creator),owner_object:instance_exists(creator)?
            object_get_name(creator.object_index):undefined});
    var _toss=[],_tops=[],_pipes=[],_crates=[];
    with(NTTEFullPalankingToss) array_push(_toss,{id:real(id),creator:real(creator),
        owner_exists:instance_exists(creator),owner_object:instance_exists(creator)?
            object_get_name(creator.object_index):undefined,
        x:x,y:y,z:z,zspeed:zspeed,mask:real(mask_index),depth:depth,
        cleaned:ntte_toss_cleaned,shadow_y:spr_shadow_y});
    with(NTTEFullTopObject) array_push(_tops,{id:real(id),target:real(target),
        owner_exists:instance_exists(target),owner_object:instance_exists(target)?
            object_get_name(target.object_index):undefined,
        x:x,y:y,z:z,zspeed:zspeed,type:real(type),jump_time:jump_time,
        saved:target_save});
    with(NTTEFullBigPipe) array_push(_pipes,{id:real(id),x:x,y:y,
        delay:spawn_delay,count:spawn_count});
    with(NTTEFullWallCrate) {
        var _walls=[];
        for(var _i=0;_i<array_length(crate_wall);++_i) {
            var _wall=crate_wall[_i],_row={id:real(_wall),exists:instance_exists(_wall)};
            if(_row.exists) {
                _row.object=object_get_name(_wall.object_index);
                _row.sprite=real(_wall.sprite_index);_row.mask=real(_wall.mask_index);
                _row.bbox=[_wall.bbox_left,_wall.bbox_top,_wall.bbox_right,_wall.bbox_bottom];
            }
            array_push(_walls,_row);
        }
        array_push(_crates,{id:real(id),x:x,y:y,loot:real(crate_loot),
            loot_exists:instance_exists(crate_loot),loot_object:instance_exists(crate_loot)?
                object_get_name(crate_loot.object_index):undefined,walls:_walls});
    }
    return {ticks:_state.elapsed,enemies:instance_number(enemy),actors:_actors,
        dormant:_hidden,transforming:_spawn,prevents:_prevent,
        clear_check:scr_check_enemies(),portal_blocked:scrNTTEFullPortalBlocked(),
        pending_police:scrFRPendingPoliceCount(),corpses:instance_number(Corpse),
        portals:instance_number(Portal),top_controllers:instance_number(NTTEFullTopObject),
        tops:_tops,tosses:_toss,big_pipes:_pipes,wall_crates:_crates};
}
function scrFRBiomeClearance204NaturalTestsStart(_driver,_suspect_only=false) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Natural biome diagnostic requires the isolated native runner");
    var _cases=[];
    if(_suspect_only) _cases=[
        {area:area_desert,subarea:2,loops:1,seed:100005,rate:30},
        {area:area_desert,subarea:2,loops:3,seed:100006,rate:60},
        {area:area_jungle,subarea:1,loops:1,seed:204086,rate:60}];
    else for(var _loops=0;_loops<=3;_loops+=(_loops==0?1:2)) {
        array_push(_cases,{area:area_desert,subarea:2,loops:_loops,seed:100005,rate:30});
        array_push(_cases,{area:area_desert,subarea:2,loops:_loops,seed:100006,rate:60});
        array_push(_cases,{area:area_jungle,subarea:1,loops:_loops,seed:204071,rate:30});
        array_push(_cases,{area:area_jungle,subarea:1,loops:_loops,seed:204086,rate:60});
    }
    _driver.fr_biome_clearance204_natural={world:scrNTTEFullWorldEventsNaturalWorldCapture(),
        cases:_cases,index:-1,phase:0,elapsed:0,wait:0,rows:[],seen:{}};
}
function scrFRBiomeClearance204NaturalNext(_state) {
    scrNTTEFullWorldEventsCleanup();scrFRWallFixTestsReset(_state.world);
    if(++_state.index>=array_length(_state.cases)) {
        var _file=file_text_open_write(working_directory+"frontier-biome-clearance204-natural.json");
        file_text_write_string(_file,json_stringify({diagnostic_only:true,
            physical_device_tested:false,cases:_state.rows}));file_text_close(_file);
        scrNTTEFullWorldEventsNaturalWorldRestore(_state.world);
        return true;
    }
    var _case=_state.cases[_state.index];
    save_set_value("options","framerate",_case.rate);save_set_value("options","autopause",false);
    save_set_value("visual","freezeframes",0);scrOptionsUpdate();
    scrNTTEFullWorldEventsNaturalWorldConfigure(_state.world,[_case.area,_case.subarea],_case.seed);
    GameCont.loops=_case.loops;GameCont.hard=3+10*_case.loops;
    GameCont.is_level_ended=true;GameCont.popolevel=0;GameCont.killenemies=false;
    global.fr_continue_generation=undefined;global.fr_continue_events=undefined;
    var _baseline=[],_skills=[];
    for(var _i=0;_i<array_length(_state.world.before);++_i)
        array_push(_baseline,real(_state.world.before[_i]));
    for(var _i=0;_i<ds_list_size(GameCont.skills);++_i)
        array_push(_skills,GameCont.skills[|_i]);
    _state.row={area:_case.area,subarea:_case.subarea,loops:_case.loops,
        seed:_case.seed,rate:_case.rate,samples:[],test_bullets:0,
        baseline_ids:_baseline,baseline_skills:_skills,births:[],lifecycle:[]};
    _state.seen={};
    _state.wait=0;_state.elapsed=0;_state.phase=1;
    scrNTTESmokeLog("BIOME CLEARANCE204 NATURAL BEGIN "+json_stringify(_case));
    return false;
}
function scrFRBiomeClearance204NaturalTestsStep(_driver) {
    var _state=_driver.fr_biome_clearance204_natural;
    with(Player) {
        hp=100000;max_hp=100000;nexthurt=current_frame+100000;
        speed=0;can_walk=false;can_aim=false;can_spec=false;can_shoot=false;bcan_shoot=false;
    }
    GameCont.is_level_ended=true;
    if(_state.phase==0) return scrFRBiomeClearance204NaturalNext(_state);
    if(_state.phase==1) {
        if(++_state.wait<3) return false;
        var _gen=instance_create(0,0,GenCont);
        assert(instance_exists(_gen) && !_gen.ntte_full_sync_generation,
            "Natural biome diagnostic replaced asynchronous source generation");
        _state.wait=0;_state.phase=2;return false;
    }
    if(_state.phase==2) {
        assert(++_state.wait<3600,"Natural biome diagnostic generation did not settle");
        if(instance_exists(GenCont) || instance_exists(FloorMaker)) return false;
        var _case=_state.cases[_state.index];
        assert(GameCont.area==_case.area && GameCont.subarea==_case.subarea
            && GameCont.loops==_case.loops && instance_number(Floor)>20,
            "Natural biome diagnostic lost its populated requested map");
        _state.row.floors=instance_number(Floor);_state.row.initial_enemies=instance_number(enemy);
        assert(_state.row.initial_enemies>0,"Natural biome diagnostic generated an empty world");
        array_push(_state.row.samples,scrFRBiomeClearance204NaturalSample(_state,true));
        _state.phase=3;_state.elapsed=0;return false;
    }
    var _old=_state.elapsed;_state.elapsed+=timescale;
    // Clear ordinary hittable combatants via the normal collision scheduler;
    // never alter hidden/maskless actors to manufacture a passing clear check.
    if(_state.elapsed>=30 && _state.elapsed<=150 && floor(_old/30)<floor(_state.elapsed/30)) {
        var _targets=scrNTTEFullInstances(enemy),_p=instance_find(Player,0);
        for(var _i=0;_i<array_length(_targets);++_i) {
            var _actor=_targets[_i];
            if(!instance_exists(_actor) || _actor.hp<=0 || _actor.team==team_player
                || !_actor.visible || _actor.image_alpha<=0 || _actor.mask_index==mskNone
                || instance_is(_actor,Van) || instance_is(_actor,BigDogMissile)) continue;
            var _shot=instance_create(_actor.x,_actor.y,Bullet1);
            _shot.creator=_p;_shot.team=team_player;_shot.speed=0;_shot.damage=_actor.hp+100;
            ++_state.row.test_bullets;
        }
    }
    if((_old<30 && _state.elapsed>=30) || (_old<120 && _state.elapsed>=120)
        || (_old<300 && _state.elapsed>=300))
        array_push(_state.row.samples,scrFRBiomeClearance204NaturalSample(_state,_state.elapsed>=300));
    if(_state.elapsed<300) return false;
    array_push(_state.rows,_state.row);
    scrNTTESmokeLog("BIOME CLEARANCE204 NATURAL OBSERVED "+json_stringify(_state.row));
    _state.phase=0;
    return false;
}
