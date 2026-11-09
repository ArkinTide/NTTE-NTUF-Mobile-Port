// Provenance and scheduled friendly collisions in real L1 Cove maps.
// A health debug label is not itself proof of an enemy: the native
// overlay iterates hitme, including neutral props and collision proxies.
function scrFRPirateVisibility205State() {
    if(os_type!=os_windows || !scrNTTEFullSmokeEnabled()) return undefined;
    var _driver=instance_find(FRIntegrationTest,0);
    if(!instance_exists(_driver)) return undefined;
    return _driver[$ "fr_pirate_visibility205"]??undefined;
}

function scrFRPirateVisibility205Body(_actor) {
    var _team=_actor[$ "team"]??team_none,_hp=_actor[$ "hp"]??undefined,
        _max=_actor[$ "max_hp"]??undefined,_top=_actor[$ "ntte_full_top_object"]??noone;
    return {id:real(_actor),object:object_get_name(_actor.object_index),
        name:_actor[$ "name"]??"",x:_actor.x,y:_actor.y,hp:_hp,max_hp:_max,team:_team,
        counted_hostile:instance_is(_actor,enemy) && _team!=team_player
            && !instance_is(_actor,Van) && !instance_is(_actor,BigDogMissile),
        visible:_actor.visible,alpha:_actor.image_alpha,sprite:real(_actor.sprite_index),
        mask:real(_actor.mask_index),sprite_exists:sprite_exists(_actor.sprite_index),
        on_step:!is_undefined(_actor[$ "on_step"]),on_draw:!is_undefined(_actor[$ "on_draw"]),
        on_hurt:!is_undefined(_actor[$ "on_hurt"]),depth:_actor.depth,
        top:real(_top),top_exists:instance_exists(_top),
        top_owns_target:instance_exists(_top) && (_top[$ "target"]??noone)==_actor,
        fr_source_maxhealth_seen:_actor[$ "fr_source_maxhealth_seen"]??false,
        fr_maxhealth_init:_actor[$ "fr_maxhealth_init"]??undefined,
        possessing:_actor[$ "possessing"]??undefined,
        possess_target:real(_actor[$ "possess_target"]??noone),
        canfly:_actor[$ "canfly"]??undefined,
        fr_actor_cleaned:_actor[$ "fr_actor_cleaned"]??undefined,
        factory_retained:!is_undefined(_actor[$ "fr_cluster_factory"])};
}

function scrFRPirateVisibility205ClusterCreated(_source,_actor) {
    var _s=scrFRPirateVisibility205State();
    if(!is_struct(_s) || _s.phase==0 || !variable_struct_exists(_s,"row")) return;
    assert(!is_undefined(_actor) && instance_exists(_actor)
        && _actor.object_index==_source.object_index && _actor.name==_source.name,
        "Cove205 loop cluster lost its source factory species");
    assert(sprite_exists(_actor.sprite_index) && sprite_exists(_actor.mask_index)
        && _actor.mask_index!=mskNone && _actor.max_hp==_source.max_hp
        && _actor.max_hp>1 && _actor.hp>0 && !_actor.fr_maxhealth_init,
        "Cove205 loop cluster retained an uninitialized enemy shell");
    assert(!is_undefined(_actor.on_step) && !is_undefined(_actor.on_hurt)
        && !is_undefined(_actor.on_draw) && !is_undefined(_actor.on_death),
        "Cove205 loop cluster lost its authored callbacks");
    assert(abs(_actor.x-_s.cluster_x)<0.001 && abs(_actor.y-_s.cluster_y)<0.001,
        "Cove205 loop cluster changed native scatter coordinates");
    array_push(_s.row.clusters,{source:scrFRPirateVisibility205Body(_source),
        actor:scrFRPirateVisibility205Body(_actor),scheduled_bullet:false});
    ++_s.cluster_count;
}

function scrFRPirateVisibility205Created(_actor) {
    var _s=scrFRPirateVisibility205State();
    if(!is_struct(_s) || _s.phase==0 || !variable_struct_exists(_s,"row")) return;
    array_push(_s.row.hitme_births,{frame:current_frame,ticks:_s.elapsed,
        phase:_s.phase,body:scrFRPirateVisibility205Body(_actor),
        callstack:debug_get_callstack(99)});
}

function scrFRPirateVisibility205Sample(_s,_all=false) {
    var _bodies=[],_counted=[];
    with(hitme) {
        var _row=scrFRPirateVisibility205Body(id);
        if(_all || _row.counted_hostile || (!is_undefined(_row.hp) && _row.hp<=1))
            array_push(_bodies,_row);
        if(_row.counted_hostile) array_push(_counted,_row);
    }
    return {ticks:_s.elapsed,all_hitme:_bodies,counted_enemies:_counted,
        natural:scrFRBiomeClearance204NaturalSample(_s,_all)};
}

function scrFRPirateVisibility205Save(_s) {
    var _file=file_text_open_write(working_directory+"frontier-pirate-visibility205.json");
    file_text_write_string(_file,json_stringify({diagnostic_only:false,
        physical_device_tested:false,reported_area:"Cove L1",cases:_s.rows}));
    file_text_close(_file);
}

function scrFRPirateVisibility205TestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Pirate205 requires the settled private native runner");
    var _s={world:scrNTTEFullWorldEventsNaturalWorldCapture(),cases:[],
        index:-1,phase:0,elapsed:0,wait:0,rows:[],seen:{},cluster_count:0};
    for(var _i=0;_i<2;++_i) for(var _rate=30;_rate<=60;_rate+=30)
        array_push(_s.cases,{area:scrFRAreaResolve("cove"),subarea:1,loops:1,
            seed:205091+60*_i,rate:_rate});
    _driver.fr_pirate_visibility205=_s;
    // Reuse the existing read-only Top/Toss/native-enemy birth observer.
    // Its state alias does not enter that diagnostic's driver or mutate AI.
    _driver.fr_biome_clearance204_natural=_s;
}

function scrFRPirateVisibility205Next(_s) {
    scrNTTEFullWorldEventsCleanup();scrFRWallFixTestsReset(_s.world);
    if(++_s.index>=array_length(_s.cases)) {
        assert(_s.cluster_count>0,"Cove205 did not exercise a real native loop cluster");
        scrFRPirateVisibility205Save(_s);
        scrNTTEFullWorldEventsNaturalWorldRestore(_s.world);return true;
    }
    var _case=_s.cases[_s.index];
    save_set_value("options","framerate",_case.rate);
    save_set_value("options","autopause",false);save_set_value("visual","freezeframes",0);
    scrOptionsUpdate();
    scrNTTEFullWorldEventsNaturalWorldConfigure(_s.world,[_case.area,_case.subarea],_case.seed);
    GameCont.loops=1;GameCont.hard=13;GameCont.is_level_ended=true;
    GameCont.popolevel=0;GameCont.killenemies=false;
    global.fr_continue_generation=undefined;global.fr_continue_events=undefined;
    _s.row={area:_case.area,subarea:1,loops:1,seed:_case.seed,rate:_case.rate,
        samples:[],hitme_births:[],births:[],lifecycle:[],test_bullets:0,shots:[],clusters:[]};
    _s.elapsed=0;_s.wait=0;_s.seen={};_s.phase=1;
    scrNTTESmokeLog("PIRATE VISIBILITY205 NATURAL BEGIN "+json_stringify(_case));
    return false;
}

function scrFRPirateVisibility205TestsStep(_driver) {
    var _s=_driver.fr_pirate_visibility205;
    with(Player) {hp=100000;max_hp=100000;nexthurt=current_frame+100000;
        speed=0;can_walk=false;can_aim=false;can_spec=false;can_shoot=false;bcan_shoot=false;}
    if(_s.phase==0) return scrFRPirateVisibility205Next(_s);
    if(_s.phase==1) {
        if(++_s.wait<3) return false;
        var _gen=instance_create(0,0,GenCont);
        assert(instance_exists(_gen) && !_gen.ntte_full_sync_generation,
            "Pirate205 replaced genuine asynchronous generation");
        _s.wait=0;_s.phase=2;return false;
    }
    if(_s.phase==2) {
        assert(++_s.wait<3600,"Pirate205 actual Cove generation timed out");
        if(instance_exists(GenCont) || instance_exists(FloorMaker)) return false;
        assert(GameCont.area==scrFRAreaResolve("cove") && GameCont.loops==1
            && instance_number(Floor)>20 && instance_number(enemy)>0,
            "Pirate205 did not obtain its real populated Cove L1 map");
        array_push(_s.row.samples,scrFRPirateVisibility205Sample(_s,true));
        _s.phase=3;_s.elapsed=0;GameCont.is_level_ended=false;return false;
    }
    var _old=_s.elapsed;_s.elapsed+=timescale;
    // Leave hidden, alpha-zero, maskless, wall-suspended and source sentinels
    // untouched. Only ordinary scheduled Bullet1 collision can kill a body.
    if(_s.elapsed>=30 && _s.elapsed<=570 && floor(_old/30)<floor(_s.elapsed/30)) {
        var _targets=scrNTTEFullInstances(enemy),_p=instance_find(Player,0);
        for(var _i=0;_i<array_length(_targets);++_i) {
            var _a=_targets[_i];
            if(!instance_exists(_a) || _a.hp<=0 || abs(_a.hp)>=1/0
                || _a.team==team_player || !_a.visible || _a.image_alpha<=0
                || _a.mask_index==mskNone || instance_is(_a,Van) || instance_is(_a,BigDogMissile)
                || (!sprite_exists(_a.mask_index) && !sprite_exists(_a.sprite_index))) continue;
            var _shot=instance_create(_a.x,_a.y,Bullet1);
            _shot.creator=_p;_shot.team=team_player;_shot.speed=0;_shot.damage=_a.hp+10000;
            ++_s.row.test_bullets;
            for(var _c=0;_c<array_length(_s.row.clusters);++_c)
                if(_s.row.clusters[_c].actor.id==real(_a))
                    _s.row.clusters[_c].scheduled_bullet=true;
            array_push(_s.row.shots,{ticks:_s.elapsed,target:scrFRPirateVisibility205Body(_a),
                bullet:real(_shot),damage:_shot.damage});
        }
    }
    if((_old<30 && _s.elapsed>=30) || (_old<120 && _s.elapsed>=120)
        || (_old<300 && _s.elapsed>=300) || (_old<600 && _s.elapsed>=600))
        array_push(_s.row.samples,scrFRPirateVisibility205Sample(_s,_s.elapsed>=600));
    if(_s.elapsed<600) return false;
    var _final=_s.row.samples[array_length(_s.row.samples)-1];
    for(var _c=0;_c<array_length(_s.row.clusters);++_c) {
        var _cluster=_s.row.clusters[_c];
        assert(_cluster.scheduled_bullet && !instance_exists(_cluster.actor.id),
            "Cove205 factory cluster did not die through scheduled friendly Bullet1 collision");
    }
    assert(array_length(_final.counted_enemies)==0 && !_final.natural.clear_check
        && !_final.natural.portal_blocked && _final.natural.pending_police==0
        && _final.natural.portals>0,
        "Cove205 genuine map did not naturally clear and open its exit");
    array_push(_s.rows,_s.row);scrFRPirateVisibility205Save(_s);
    scrNTTESmokeLog("PIRATE VISIBILITY205 NATURAL OBSERVED "+json_stringify({
        seed:_s.row.seed,rate:_s.row.rate,shots:_s.row.test_bullets,
        final:_s.row.samples[array_length(_s.row.samples)-1]}));
    _s.phase=0;return false;
}
