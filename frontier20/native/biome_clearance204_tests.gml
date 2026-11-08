// Read-only diagnostics of real native wall-top actor lifecycles. The fixture
// creates ordinary source actors; it never deletes a hidden blocker, forces a
// clear portal, changes actor visibility/masks, or substitutes their AI.
function scrFRBiomeClearance204Snapshot(_actor) {
    if(!instance_exists(_actor)) return {exists:false};
    var _wall=false,_floor=false;
    with(_actor) {_wall=place_meeting(x,y,Wall);_floor=place_meeting(x,y,Floor);}
    return {exists:true,id:real(_actor),object:object_get_name(_actor.object_index),
        x:_actor.x,y:_actor.y,hp:_actor[$ "hp"]??undefined,team:_actor[$ "team"]??undefined,
        visible:_actor.visible,alpha:_actor.image_alpha,mask:_actor.mask_index,
        depth:_actor.depth,in_wall:_wall,on_floor:_floor,
        top:real(_actor[$ "ntte_full_top_object"]??noone)};
}
function scrFRBiomeClearance204TestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Biome clearance diagnostic requires the settled isolated native runner");
    _driver.fr_biome_clearance204={world:scrNTTEFullWorldEventsNaturalWorldCapture(),
        index:-1,phase:0,elapsed:0,rows:[],cases:[
            {area:area_jungle,type:JungleAssassinHide,kind:"jungle-wall-hidden-wakeup"},
            {area:area_jungle,type:JungleBandit,kind:"jungle-wall-bandit-control"},
            {area:area_desert,type:Bandit,kind:"desert-wall-bandit-control"},
            {area:area_desert,type:JungleFly,kind:"desert-wall-fly-control"}]};
}
function scrFRBiomeClearance204TestsNext(_state) {
    scrNTTEFullWorldEventsCleanup();scrFRWallFixTestsReset(_state.world);
    if(++_state.index>=array_length(_state.cases)) {
        var _file=file_text_open_write(working_directory+"frontier-biome-clearance204-diagnostic.json");
        file_text_write_string(_file,json_stringify({diagnostic_only:true,
            no_production_changes:true,physical_device_tested:false,cases:_state.rows}));
        file_text_close(_file);
        scrNTTEFullWorldEventsNaturalWorldRestore(_state.world);
        return true;
    }
    var _case=_state.cases[_state.index],_x=942000,_y=942000,
        _player=instance_find(Player,0);
    GameCont.area=_case.area;GameCont.subarea=1;GameCont.loops=1;GameCont.hard=13;
    // Prevent UI/timeout/recovery from modifying the diagnostic room. The real
    // assassin Step still uses the unmodified enemy count to decide to wake.
    GameCont.is_level_ended=true;GameCont.killenemies=false;GameCont.popolevel=0;
    _player.x=_x+128;_player.y=_y+128;_player.xprevious=_player.x;_player.yprevious=_player.y;
    _player.hp=max(1,_player.hp);_player.nexthurt=current_frame+100000;
    for(var _ix=0;_ix<8;++_ix) for(var _iy=0;_iy<8;++_iy)
        instance_create(_x+32*_ix,_y+32*_iy,Floor);
    for(var _ix=0;_ix<16;++_ix) for(var _iy=1;_iy<=4;++_iy)
        instance_create(_x+16*_ix,_y-16*_iy,Wall);
    random_set_seed(204057);
    var _actor=instance_create(_x+64,_y-16,_case.type),
        _top=scrNTTEFullTopCreate(_actor.x,_actor.y,_actor,90,16);
    assert(instance_exists(_actor) && instance_exists(_top) && _top.target==_actor,
        "Biome fixture lost actual native TopCreate ownership");
    _state.actor=_actor;_state.top=_top;_state.elapsed=0;_state.phase=1;
    _state.row={area:_case.area,loops:1,kind:_case.kind,
        original:scrFRBiomeClearance204Snapshot(_actor),top_origin:[_top.x,_top.y,_top.z],
        source_search:[_top.search_x1,_top.search_y1,_top.search_x2,_top.search_y2],samples:[]};
    array_push(_state.rows,_state.row);
    scrNTTESmokeLog("BIOME CLEARANCE204 BEGIN "+json_stringify(_state.row));
    return false;
}
function scrFRBiomeClearance204TestsStep(_driver) {
    var _state=_driver.fr_biome_clearance204;
    if(_state.phase==0) return scrFRBiomeClearance204TestsNext(_state);
    _state.elapsed+=timescale;
    var _enemies=scrNTTEFullInstances(enemy),_actors=[];
    for(var _i=0;_i<array_length(_enemies);++_i)
        array_push(_actors,scrFRBiomeClearance204Snapshot(_enemies[_i]));
    if(_state.elapsed==timescale || abs(_state.elapsed-30)<.001 || abs(_state.elapsed-120)<.001) {
        var _sample={ticks:_state.elapsed,original:scrFRBiomeClearance204Snapshot(_state.actor),
            original_top_alive:instance_exists(_state.top),enemies:_actors,
            clear_check:scr_check_enemies(),hidden:instance_number(MeleeFake)};
        array_push(_state.row.samples,_sample);
        scrNTTESmokeLog("BIOME CLEARANCE204 SAMPLE "+json_stringify(_sample));
    }
    if(_state.elapsed<120) return false;
    _state.phase=0;
    return false;
}
