// Diagnostic only: real native Red generation, both direct and in-room.
// Collect blocked floor cells as well as open-node components; counting only
// existing open components can miss a completely sealed floor/corridor cell.
function scrFRRed212ProbeCells(_player,_pixel_sweep=true) {
    var _floors=scrNTTEFullInstances(Floor),_seen={},_cells=[],_lookup={},_blocked=[],_walls=ds_list_create();
    try {
        for(var _i=0;_i<array_length(_floors);++_i) {
            var _floor=_floors[_i];
            for(var _y=floor(_floor.bbox_top/16)*16+8;_y<_floor.bbox_bottom;_y+=16)
                for(var _x=floor(_floor.bbox_left/16)*16+8;_x<_floor.bbox_right;_x+=16) {
                    var _key=string(_x)+","+string(_y);
                    if(variable_struct_exists(_seen,_key)) continue;
                    _seen[$ _key]=true;ds_list_clear(_walls);
                    with(_player) {instance_place_list(_x,_y,Wall,_walls,false);}
                    var _hits=[];
                    for(var _w=0;_w<ds_list_size(_walls);++_w) {
                        var _wall=_walls[|_w];
                        if(instance_is(_wall,NTTEFullWallFake)) continue;
                        array_push(_hits,{object:object_get_name(_wall.object_index),x:_wall.x,y:_wall.y,
                            area:_wall.area,rock:scrNTTEFullValue(_wall,"fr_red210_rock",false),
                            bbox:[_wall.bbox_left,_wall.bbox_top,_wall.bbox_right,_wall.bbox_bottom]});
                    }
                    if(array_length(_hits)) array_push(_blocked,{x:_x,y:_y,style:_floor.styleb,
                        floor_area:_floor.area,floor_object:object_get_name(_floor.object_index),hits:_hits});
                    else {
                        _lookup[$ _key]=array_length(_cells);
                        array_push(_cells,{x:_x,y:_y,component:-1});
                    }
                }
        }
        var _components=0,_sizes=[];
        for(var _i=0;_i<array_length(_cells);++_i) {
            if(_cells[_i].component>=0) continue;
            var _queue=[_i],_head=0,_size=0;_cells[_i].component=_components;
            while(_head<array_length(_queue)) {
                var _cell=_cells[_queue[_head++]];_size+=1;
                for(var _dir=0;_dir<4;++_dir) {
                    var _nx=_cell.x+(_dir==0?16:(_dir==1?-16:0)),
                        _ny=_cell.y+(_dir==2?16:(_dir==3?-16:0)),_key=string(_nx)+","+string(_ny);
                    if(!variable_struct_exists(_lookup,_key)) continue;
                    var _next=_lookup[$ _key];
                    if(_cells[_next].component>=0 || (_pixel_sweep && !scrFRRedConnectivity204Edge(_player,_cell.x,_cell.y,_nx,_ny))) continue;
                    _cells[_next].component=_components;array_push(_queue,_next);
                }
            }
            array_push(_sizes,_size);_components+=1;
        }
        var _geometry={floors:[],walls:[],helpers:[]};
        with(Floor) array_push(_geometry.floors,{id:real(id),object:object_get_name(object_index),area:area,style:styleb,
            bbox:[bbox_left,bbox_top,bbox_right,bbox_bottom]});
        with(Wall) array_push(_geometry.walls,{id:real(id),object:object_get_name(object_index),x:x,y:y,area:area,
            rock:scrNTTEFullValue(id,"fr_red210_rock",false),solid:solid,bbox:[bbox_left,bbox_top,bbox_right,bbox_bottom]});
        with(NTTEFullWallFakeHelper) array_push(_geometry.helpers,{id:real(id),creator:real(creator),solid:solid,
            bbox:[bbox_left,bbox_top,bbox_right,bbox_bottom]});
        var _twins=[];
        with(NTTEFullPet) if(pet=="Twins") array_push(_twins,{id:real(id),position:[x,y],
            partner_id:instance_exists(partner)?real(partner.id):0});
        return {pixel_swept:_pixel_sweep,cells:array_length(_cells),components:_components,sizes:_sizes,blocked:_blocked,geometry:_geometry,nodes:_cells,twins:_twins,
            floors:instance_number(Floor),walls:instance_number(Wall),fake:instance_number(NTTEFullWallFake),
            caps:instance_number(TopSmall)};
    } finally {ds_list_destroy(_walls);}
}
function scrFRRed212Generate(_state,_seed,_loops,_manual=true,_rate=30) {
    scrFRWallFixTestsReset(_state);
    save_set_value("options","framerate",_rate);scrOptionsUpdate();
    // Options intentionally defer a live clock change to a safe Begin Step.
    // This explicit fixture starts GenCont in the same End Step, so establish
    // the requested real engine rate before generation makes that gate unsafe.
    scrFRClockApply212(_rate);
    assert(game_get_speed(gamespeed_fps)==_rate,"Red212 did not set its real generation rate");
    // The isolated save defaults to the tutorial. Its Alarm0 cleanup deletes
    // every Wall over Floor, including legitimate Red rocks and fake walls.
    // Exercise a real run rather than accidentally testing tutorial cleanup.
    save_set_value("game","tutorial",false);
    global.fr_red204_active=false;global.fr_red204_fast_scan=true;global.fr_red204_boundaries=[];
    global.fr_red204_protected=[];global.fr_red204_protected_styles=[0,0];global.fr_red204_protected_edges=[];
    variable_struct_set(global.ntte_full_progress.unlocks,"quest:part:3",false);
    GameCont.area=206;GameCont.subarea=1;GameCont.loops=_loops;GameCont.hard=5;
    GameCont.maxsubarea=1;GameCont.finalsubarea=true;GameCont.levseed=_seed;
    GameCont.ntte_quest_spawned_part_index_list=[];GameCont.ntte_full_source_seed=scrNTTEFullSourceSeedBuild(_seed);
    global.rng_state[@RNGStates.Generation]=_seed;global.ntte_full_sync_generation=false;random_set_seed(_seed);
    with(Player) {x=10016;y=10016;mask_index=mskPlayer;image_xscale=1;image_yscale=1;image_angle=0;race=Race.Fish;roll=false;hammerhead=0;}
    scrNTTEFullFloorResetStyle();scrNTTEFullFloorResetAlign();scrNTTEFullAreaNativeInit();
    var _gen=instance_create(0,0,GenCont);
    if(!_manual) return _gen;
    with(_gen) event_perform(ev_alarm,2);
    with(_gen) event_perform(ev_alarm,0);
    _gen.ntte_full_sync_compact_defer=true;
    with(_gen) event_perform(ev_alarm,1);
    assert(!instance_exists(TutCont),"Red212 diagnostic accidentally tested tutorial cleanup");
    assert(instance_exists(NTTEFullWallFake) && instance_exists(NTTEFullWallFakeHelper),
        "Red212 diagnostic must preserve actual hidden-corridor fake walls");
    return instance_find(Player,0);
}
function scrFRRed212ProbeTests() {
    var _state=scrNTTEFullWorldEventsNaturalWorldCapture(),_rows=[],
        _old_lock=lockstep_stop,_scale=timescale,_old_quest=scrNTTEFullUnlockGet("quest:part:3",undefined),
        _quest_had=variable_struct_exists(global.ntte_full_progress.unlocks,"quest:part:3");
    try {
        lockstep_stop=false;
        for(var _loops=0;_loops<=3;_loops+=(_loops==0?1:2)) for(var _seed=1;_seed<=24;++_seed) {
            var _player=scrFRRed212Generate(_state,_seed,_loops);
            scrNTTESolidWallGenerate();
            var _probe=scrFRRed212ProbeCells(_player,false);
            // Wide diagnostics screen discrete topology cheaply, then retain
            // the exact Player-mask pixel sweep for every suspected split.
            if(_probe.components>1) _probe=scrFRRed212ProbeCells(_player,true);
            _probe.seed=_seed;_probe.mode="normal";_probe.loops=_loops;
            array_push(_rows,_probe);
            scrNTTESmokeLog("RED212 PROBE "+json_stringify(_probe));
        }
        for(var _seed=1;_seed<=16;++_seed) {
            scrFRWallFixTestsReset(_state);global.time_scale=1;global.fr_red204_active=false;
            GameCont.area=area_desert;GameCont.subarea=1;GameCont.hard=5;GameCont.loops=1;
            GameCont.maxsubarea=3;GameCont.finalsubarea=false;GameCont.levseed=_seed;
            GameCont.ntte_quest_spawned_part_index_list=[];
            GameCont.ntte_full_source_seed=scrNTTEFullSourceSeedBuild(_seed);
            global.ntte_full_sync_generation=false;random_set_seed(_seed);
            with(Player) {x=10016;y=10016;mask_index=mskPlayer;image_xscale=1;image_yscale=1;image_angle=0;race=Race.Fish;roll=false;hammerhead=0;}
            scrNTTEFullAreaNativeInit();
            scrNTTEFullAreaGenerateNative(area_desert,1,1,10016,10016,true,0);
            var _before=scrFRRed212ProbeCells(instance_find(Player,0),false);
            scrNTTEFullAreaGenerateNative(206,1,1,10016,10016,false,0);
            var _probe=scrFRRed212ProbeCells(instance_find(Player,0),false);
            if(_probe.components>_before.components) _probe=scrFRRed212ProbeCells(instance_find(Player,0),true);
            _probe.seed=_seed;_probe.mode="in-room";_probe.before=_before;
            array_push(_rows,_probe);scrNTTESmokeLog("RED212 PROBE "+json_stringify(_probe));
        }
        var _file=file_text_open_write(working_directory+"frontier-red212-probe.json");
        file_text_write_string(_file,json_stringify({diagnostic:true,rows:_rows,physical_device_tested:false}));file_text_close(_file);
    } finally {
        global.fr_red204_active=false;
        if(_quest_had) variable_struct_set(global.ntte_full_progress.unlocks,"quest:part:3",_old_quest);
        else variable_struct_remove(global.ntte_full_progress.unlocks,"quest:part:3");
        scrNTTEFullWorldEventsNaturalWorldRestore(_state);lockstep_stop=_old_lock;global.time_scale=_scale;
    }
}
// Let native movement/collision, PortalClear and the delayed Top rebuild run
// between samples. Synchronous generation alone cannot exercise those events.
function scrFRRed212ScheduledStart(_driver) {
    var _old_auto=UberCont.opt_ntte_autoframerate,_old_save=UberCont.saveData[? "visual_ntte_autoframerate"],
        _old_cap=UberCont.opt_framerate,_old_opt=save_get_value("options","framerate",60),
        _budget=variable_instance_get(instance_find(UberCont,0),"fr_clock_budget212");
    if(is_struct(_budget)) _budget=json_parse(json_stringify(_budget));
    _driver.fr_red212={world:scrNTTEFullWorldEventsNaturalWorldCapture(),rows:[],index:0,phase:0,wait:0,parked:[],
        scale:timescale,lock:lockstep_stop,
        auto_before:_old_auto,auto_save:_old_save,cap_before:_old_cap,rate_option:_old_opt,budget:_budget,
        rate:game_get_speed(gamespeed_fps),edge_guard:variable_global_exists("fr_red212_edge_guard")?global.fr_red212_edge_guard:false,
        observe:variable_global_exists("fr_red212_native_observe")?global.fr_red212_native_observe:false,
        trace:variable_global_exists("fr_red212_native_trace")?global.fr_red212_native_trace:[],
        quest_had:variable_struct_exists(global.ntte_full_progress.unlocks,"quest:part:3"),
        quest:scrNTTEFullUnlockGet("quest:part:3",undefined)};
    save_set_value("visual","ntte_autoframerate",false);scrOptionsUpdate();
}
function scrFRRed212RockSnapshot(_rocks) {
    var _rows=[],_hits=ds_list_create();
    try {
        for(var _i=0;_i<array_length(_rocks);++_i) {
            var _rock=_rocks[_i];
            if(!instance_exists(_rock)) {array_push(_rows,{id:real(_rock),exists:false});continue;}
            var _overlap=[],_clear=false;
            ds_list_clear(_hits);
            with(_rock) {instance_place_list(x,y,Wall,_hits,false);_clear=place_meeting(x,y,PortalClear);}
            for(var _j=0;_j<ds_list_size(_hits);++_j) {
                var _wall=_hits[|_j];if(_wall==_rock) continue;
                array_push(_overlap,{id:real(_wall),object:object_get_name(_wall.object_index),x:_wall.x,y:_wall.y});
            }
            array_push(_rows,{id:real(_rock),exists:true,x:_rock.x,y:_rock.y,
                origin_distance:point_distance(_rock.x,_rock.y,10016,10016),portal_clear:_clear?true:false,
                overlap:_overlap});
        }
    } finally {ds_list_destroy(_hits);}
    return _rows;
}
// Bind the intended hidden entrance to this actual generated secret room.
// Fake instances are created only by RedSecretRoom's genuine fake corridor,
// after the preceding room's Twins anchor and before this room's first Twins.
// A genuine Twins Step may then create its linked partner in the same room.
// Derive the room anchor from that actual reciprocal link. Select a
// reachable graph cell using the real Player-mask collision query, never by
// moving a pet/wall or overriding its native collision/reveal state.
function scrFRRed212HiddenWaypoint(_player,_graph,_target,_twins,_geometry) {
    var _previous=0,_target_id=real(_target.id),_anchor=_target_id,_partner_id=0,
        _from=scrFRRedConnectivity204Nearest(_graph,_player.x,_player.y),
        _to=scrFRRedConnectivity204Nearest(_graph,_target.x,_target.y);
    if(instance_exists(_target.partner)) {
        var _partner=_target.partner;
        scrNTTESmokeLog("RED212 TWINS RAW LINK "+json_stringify({target:real(_target),partner:real(_partner),
            partner_pet:_partner.pet,back:real(_partner.partner),same_ref:_partner.partner==_target,
            same_numeric:real(_partner.partner)==real(_target),target_type:typeof(_target),back_type:typeof(_partner.partner)}));
        assert(_partner.pet=="Twins" && scrNTTEFullTwinsHistorySame(_partner.partner,_target),
            "Red212 current Twins does not have its real reciprocal partner");
        _partner_id=real(_partner.id);_anchor=min(_target_id,_partner_id);
    }
    for(var _i=0;_i<array_length(_twins);++_i) {
        var _other=_twins[_i],_room_anchor=real(_other.id);
        if(instance_exists(_other.partner)) {
            assert(_other.partner.pet=="Twins" && scrNTTEFullTwinsHistorySame(_other.partner.partner,_other),
                "Red212 captured Twins does not have its real reciprocal partner");
            _room_anchor=min(_room_anchor,real(_other.partner.id));
        }
        if(_room_anchor<_anchor) _previous=max(_previous,_room_anchor);
    }
    assert(_from>=0 && _to>=0,"Red212 hidden entrance lacks real spawn/Twins graph nodes");
    for(var _i=0;_i<array_length(_geometry.walls);++_i) {
        var _wall_row=_geometry.walls[_i],_fake=_wall_row.id;
        if(_wall_row.object!="NTTEFullWallFake" || _fake<=_previous || _fake>=_anchor || !instance_exists(_fake)) continue;
        var _helper=noone;
        with(NTTEFullWallFakeHelper) if(creator==_fake) {_helper=id;break;}
        if(!instance_exists(_helper)) continue;
        for(var _n=0;_n<array_length(_graph.nodes);++_n) {
            var _node=_graph.nodes[_n];
            if(_node.component!=_graph.nodes[_from].component || _node.component!=_graph.nodes[_to].component) continue;
            var _intersects=false;
            with(_player) _intersects=place_meeting(_node.x,_node.y,_fake);
            if(!_intersects) continue;
            return {id:real(_fake),position:[_fake.x,_fake.y],bbox:_wall_row.bbox,
                helper_id:real(_helper),helper_creator:real(_helper.creator),waypoint:[_node.x,_node.y],node:_n,
                waypoint_player_mask_intersects:true,generated_this_room:true,
                generation_window:{previous_twins_id:_previous,twins_id:_target_id,
                    room_twins_id:_anchor,partner_id:_partner_id}};
        }
    }
    assert(false,"Red212 genuine Twins has no reachable real hidden Fake corridor waypoint");
    return undefined;
}
function scrFRRed212ScheduledStep(_driver) {
    var _s=_driver.fr_red212;
    lockstep_stop=false;
    if(_s.phase!=0) assert(game_get_speed(gamespeed_fps)==_s.meta.rate,
        "Red212 real engine rate changed during native generation or settle");
    if(_s.phase==0) {
        for(var _i=0;_i<array_length(_s.parked);++_i) instance_activate_object(_s.parked[_i]);
        _s.parked=[];
        if(_s.index>=8) {
            var _rock_total=0;
            for(var _i=0;_i<array_length(_s.rows);++_i) _rock_total+=_s.rows[_i].protected_rocks;
            assert(_rock_total>0,"Red212 did not exercise any legitimate preserved ordinary rocks");
            var _file=file_text_open_write(working_directory+"frontier-red212-scheduled.json");
            file_text_write_string(_file,json_stringify({status:"PASS",diagnostic:false,native_scheduled_frames:12,
                actual_player_mask:"mskPlayer 8x10",rows:_s.rows,physical_device_tested:false}));
            file_text_close(_file);global.fr_red204_active=false;
            global.fr_red212_native_observe=_s.observe;global.fr_red212_native_trace=_s.trace;
            global.fr_red212_edge_guard=_s.edge_guard;
            if(_s.quest_had) variable_struct_set(global.ntte_full_progress.unlocks,"quest:part:3",_s.quest);
            else variable_struct_remove(global.ntte_full_progress.unlocks,"quest:part:3");
            scrNTTEFullWorldEventsNaturalWorldRestore(_s.world);lockstep_stop=_s.lock;
            save_set_value("options","framerate",_s.rate_option);
            if(is_undefined(_s.auto_save)) ds_map_delete(UberCont.saveData,"visual_ntte_autoframerate");
            else UberCont.saveData[? "visual_ntte_autoframerate"]=_s.auto_save;
            scrOptionsUpdate();UberCont.opt_framerate=_s.cap_before;UberCont.opt_ntte_autoframerate=_s.auto_before;
            UberCont.fr_clock_budget212=_s.budget;global.time_scale=_s.scale;scrFRClockApply212(_s.rate);
            scrNTTESmokeLog("PASS RED212 native scheduled normal and in-room 30/60Hz expected ordinary roads, zero post-population shifts, rocks and Warp/Twins round trips");
            return true;
        }
        var _seeds=[15,15,22,48],_loops=[3,3,0,3],_rates=[30,60,30,60],
            _seed=_seeds[_s.index mod 4],_loop=_loops[_s.index mod 4],_rate=_rates[_s.index mod 4],
            _mode=_s.index<4?"normal":"in-room";
        global.fr_red212_native_observe=true;global.fr_red212_native_trace=[];
        _s.meta={seed:_seed,loops:_loop,mode:_mode,rate:_rate};_s.gen_frames=0;
        if(_mode=="normal") {
            _s.gen=scrFRRed212Generate(_s.world,_seed,_loop,false,_rate);_s.phase=10;
            global.fr_red204_active=true;global.fr_red204_fast_scan=true;global.fr_red212_edge_guard=true;
        }
        else {
            scrFRWallFixTestsReset(_s.world);global.fr_red204_active=false;
            save_set_value("options","framerate",_rate);scrOptionsUpdate();
            scrFRClockApply212(_rate);
            save_set_value("game","tutorial",false);
            GameCont.area=area_desert;GameCont.subarea=1;GameCont.hard=5;GameCont.loops=_loop;
            GameCont.maxsubarea=3;GameCont.finalsubarea=false;GameCont.levseed=_seed;
            GameCont.ntte_quest_spawned_part_index_list=[];
            GameCont.ntte_full_source_seed=scrNTTEFullSourceSeedBuild(_seed);
            global.ntte_full_sync_generation=false;random_set_seed(_seed);
            with(Player) {x=10016;y=10016;mask_index=mskPlayer;image_xscale=1;image_yscale=1;image_angle=0;race=Race.Fish;roll=false;hammerhead=0;}
            scrNTTEFullAreaNativeInit();
            _s.gen=instance_create(0,0,GenCont);_s.phase=11;
        }
        assert(game_get_speed(gamespeed_fps)==_rate,"Red212 generator started at the wrong actual engine rate");
        with(Player) {can_walk=false;can_aim=false;can_spec=false;can_shoot=false;bcan_shoot=false;speed=0;nexthurt=current_frame+100000;}
        return false;
    }
    if(_s.phase==10 || _s.phase==11) {
        if(instance_exists(_s.gen)) {
            _s.gen_frames+=1;
            if(_s.gen_frames>=600) {
                scrNTTESmokeLog("RED212 NATIVE TIMEOUT "+json_stringify({meta:_s.meta,frames:_s.gen_frames,
                    floors:instance_number(Floor),walls:instance_number(Wall),maker:instance_exists(FloorMaker),
                    safespawn:_s.gen.safespawn,alarm0:_s.gen.alarm[0],alarm1:_s.gen.alarm[1],alarm2:_s.gen.alarm[2]}));
                assert(false,"Red212 native generator did not finalize within 600 real engine frames");
            }
            return false;
        }
        assert(!instance_exists(TutCont),"Red212 native scheduled generation entered tutorial");
        var _original=undefined,_p=instance_find(Player,0);
        if(_s.phase==11) {
            _original=scrFRRed212ProbeCells(_p,false);
            global.fr_red204_active=true;global.fr_red204_fast_scan=true;global.fr_red212_edge_guard=true;
            global.fr_red204_boundaries=[];global.fr_red204_protected=[];global.fr_red204_protected_edges=[];
            scrNTTEFullAreaGenerateNative(206,1,_s.meta.loops,10016,10016,false,0);
        }
        scrFRRedConnectivity204FastBoundary("scheduled-final");
        var _road=global.fr_red204_boundaries[array_length(global.fr_red204_boundaries)-1],_post_shifts=0,
            _trace=global.fr_red212_native_trace,_rocks=[],_rock_candidates=[];
        for(var _i=0;_i<array_length(_trace);++_i) {
            var _shift=_trace[_i],_before_shift=_shift.before;
            if(_before_shift.walls>0 || _before_shift.fake>0 || _before_shift.helpers>0) _post_shifts+=1;
        }
        assert(_post_shifts==0,"Red212 moved completed population away from its walls");
        assert(_road.protected_points>0 && _road.protected_edges>0,"Red212 expected-road snapshot is empty");
        assert(array_length(_road.changed)==0 && array_length(_road.blocked_expected_edges)==0,
            "Red212 lost pre-secret ordinary road nodes or actual Player-mask pixel edges");
        with(Wall) if(object_index==Wall && scrNTTEFullValue(id,"fr_red210_rock",false)
            && point_distance(x,y,_p.x,_p.y)>64) array_push(_rock_candidates,id);
        var _rock_capture=scrFRRed212RockSnapshot(_rock_candidates);
        // In-room generation retains real, still-active PortalClear instances.
        // Their native collision event intentionally removes intersecting walls
        // on the next engine frame. Protect only props outside that actual mask,
        // retaining the complete candidate snapshot for independent validation.
        for(var _i=0;_i<array_length(_rock_candidates);++_i)
            if(!_rock_capture[_i].portal_clear) array_push(_rocks,_rock_candidates[_i]);
        _s.rocks=_rocks;
        scrNTTESmokeLog("RED212 ROCK CAPTURE "+json_stringify({meta:_s.meta,rocks:_rock_capture}));
        _s.twins=[];
        with(NTTEFullPet) if(pet=="Twins") array_push(_s.twins,id);
        assert(array_length(_s.twins)>0,"Red212 native secret room did not create its genuine Twins target");
        _s.row={seed:_s.meta.seed,loops:_s.meta.loops,mode:_s.meta.mode,rate:_s.meta.rate,
            engine_rate:game_get_speed(gamespeed_fps),original:_original,
            native_gen_frames:_s.gen_frames,native_scheduler:true,manual_alarm_dispatch:false,
            generation_trace:_trace,post_population_shifts:_post_shifts,
            road:{expected_points:_road.protected_points,expected_edges:_road.protected_edges,
                changed:_road.changed,blocked_expected_edges:_road.blocked_expected_edges,pixel_swept:true},
            rock_clearance_rule:"exclude actual PortalClear mask overlap",rock_capture:_rock_capture,
            native_clearance_rocks:array_length(_rock_candidates)-array_length(_rocks),
            before:scrFRRed212ProbeCells(_p,false)};
        scrNTTESmokeLog("RED212 TWINS CAPTURE "+json_stringify({meta:_s.meta,twins:_s.row.before.twins}));
        with(hitme) if(!instance_is(id,Player)) {array_push(_s.parked,id);instance_deactivate_object(id);}
        with(Player) {can_walk=false;can_aim=false;can_spec=false;can_shoot=false;bcan_shoot=false;speed=0;nexthurt=current_frame+100000;}
        GameCont.is_level_ended=true;_s.phase=1;_s.wait=0;
        return false;
    }
    _s.wait+=timescale;if(_s.wait<12) return false;
    scrNTTESmokeLog("RED212 ROCK SETTLED "+json_stringify({meta:_s.meta,rocks:scrFRRed212RockSnapshot(_s.rocks)}));
    // Keep the real pet parked during native settle so its wandering AI cannot
    // move the authored route target. Reactivate that exact generated instance
    // before collecting targets; broad hitme parking also includes NTTEFullPet.
    for(var _i=0;_i<array_length(_s.twins);++_i) {
        instance_activate_object(_s.twins[_i]);
        assert(instance_exists(_s.twins[_i]),"Red212 lost its native Twins while settling the world");
    }
    var _p=instance_find(Player,0),_graph=scrFRRedConnectivity204Map(_p),_walks=[],_objects=[NTTEFullWarp,NTTEFullPet],
        _warp_count=0,_twins_count=0,_reveal_witness=false;
    for(var _o=0;_o<array_length(_objects);++_o) {
        var _targets=scrNTTEFullInstances(_objects[_o]);
        for(var _i=0;_i<array_length(_targets);++_i) {
            var _target=_targets[_i];if(_o==1 && _target.pet!="Twins") continue;
            var _target_id=real(_target.id),_target_position=[_target.x,_target.y],_via=undefined;
            if(_o==1) _via=scrFRRed212HiddenWaypoint(_p,_graph,_target,_s.twins,_s.row.before.geometry);
            var _walk=scrFRRedConnectivity204Walk(_p,_graph,_target);
            if(_o==1) {
                // Preserve the original direct round trip as independent
                // evidence even when its BFS tree uses an alternate entrance.
                _walk.kind="twins";_walk.genuine_generated_target=true;
                _walk.target_id=_target_id;_walk.target_position=_target_position;
                assert(_walk.reached && _walk.returned && array_length(_walk.blocked)==0,
                    "Red212 original direct Twins round trip failed");
                var _direct=_walk;
                _walk=scrFRRedConnectivity204Walk(_p,_graph,_target,_via.node);
                _walk.direct_route=_direct;_walk.via_fake=_via;
                assert(array_get_index(_walk.fake_contact_ids,_via.id)>=0,
                    "Red212 intended secret entrance had no actual Fake Wall collision");
            }
            _walk.kind=_o==0?"warp":"twins";_walk.target_id=_target_id;
            _walk.target_position=_target_position;_walk.genuine_generated_target=true;array_push(_walks,_walk);
            scrNTTESmokeLog("RED212 NATIVE WALK "+json_stringify({meta:_s.meta,walk:_walk}));
            if(_o==0) {_warp_count+=1;} else {_twins_count+=1;}
            if(_o==1 && _walk.fake_collision_events>0 && _walk.peak_reveal>0) _reveal_witness=true;
            assert(_walk.reached && _walk.returned && array_length(_walk.blocked)==0,
                "Red212 actual Player-mask/Wall events could not reach and return from "+_walk.kind);
        }
    }
    assert(_warp_count>0 && _twins_count>0,"Red212 must visit both genuine Warp and Twins targets");
    assert(_reveal_witness,"Red212 Twins route did not exercise native Fake collision and hidden-wall reveal");
    var _preserved=0;for(var _i=0;_i<array_length(_s.rocks);++_i) if(instance_exists(_s.rocks[_i])) _preserved+=1;
    scrNTTESmokeLog("RED212 ROCK WALKED "+json_stringify({meta:_s.meta,rocks:scrFRRed212RockSnapshot(_s.rocks)}));
    assert(_preserved==array_length(_s.rocks),"Red212 removed legitimate ordinary rock props");
    scrFRRedConnectivity204FastBoundary("after-native-settle");
    var _final_road=global.fr_red204_boundaries[array_length(global.fr_red204_boundaries)-1];
    assert(array_length(_final_road.changed)==0 && array_length(_final_road.blocked_expected_edges)==0,
        "Red212 settled world lost expected ordinary road cells or edges");
    _s.row.walks=_walks;_s.row.protected_rocks=array_length(_s.rocks);_s.row.preserved_rocks=_preserved;
    _s.row.after=scrFRRed212ProbeCells(_p,false);
    array_push(_s.rows,_s.row);scrNTTESmokeLog("RED212 SCHEDULED "+json_stringify(_s.row));
    _s.index+=1;_s.phase=0;
    return false;
}

// Called only around the real GenCont.Step event during an explicit private
// desktop diagnostic; never dispatches that event or modifies generation.
function scrFRRed212NativeStepProbe(_gen,_phase) {
    if(!variable_global_exists("fr_red212_native_observe") || !global.fr_red212_native_observe
        || !instance_exists(_gen) || GameCont.area!=206) return;
    if(_phase=="before") {
        var _anchor=instance_find(Floor,0);
        _gen.fr_red212_step_before={anchor:_anchor,x:instance_exists(_anchor)?_anchor.x:0,
            y:instance_exists(_anchor)?_anchor.y:0,walls:instance_number(Wall),fake:instance_number(NTTEFullWallFake),
            helpers:instance_number(NTTEFullWallFakeHelper),floors:instance_number(Floor),
            alarm0:_gen.alarm[0],alarm1:_gen.alarm[1],alarm2:_gen.alarm[2]};
        return;
    }
    var _before=_gen.fr_red212_step_before,_anchor=_before.anchor;
    var _row={phase:"native-safespawn-shift",before:_before,
        dx:instance_exists(_anchor)?_anchor.x-_before.x:0,dy:instance_exists(_anchor)?_anchor.y-_before.y:0,
        walls:instance_number(Wall),fake:instance_number(NTTEFullWallFake),helpers:instance_number(NTTEFullWallFakeHelper),
        floors:instance_number(Floor),alarm0:_gen.alarm[0],alarm1:_gen.alarm[1],alarm2:_gen.alarm[2]};
    if(_before.walls>0) _row.geometry=scrFRRed212ProbeCells(instance_find(Player,0),false);
    array_push(global.fr_red212_native_trace,_row);
    scrNTTESmokeLog("RED212 NATIVE SHIFT "+json_stringify(_row));
}

// Broad, deliberately non-acceptance diagnostic. Let the engine schedule the
// complete generator, then compare the ordinary road BEFORE its secret room
// against the finished map. Full geometry is saved only for suspect worlds.
function scrFRRed212SweepStart(_driver) {
    _driver.fr_red212_sweep={world:scrNTTEFullWorldEventsNaturalWorldCapture(),rows:[],index:0,phase:0,frames:0,failures:0,
        scale:timescale,lock:lockstep_stop,
        edge_guard:variable_global_exists("fr_red212_edge_guard")?global.fr_red212_edge_guard:false,
        observe:variable_global_exists("fr_red212_native_observe")?global.fr_red212_native_observe:false,
        trace:variable_global_exists("fr_red212_native_trace")?global.fr_red212_native_trace:[],
        quest_had:variable_struct_exists(global.ntte_full_progress.unlocks,"quest:part:3"),
        quest:scrNTTEFullUnlockGet("quest:part:3",undefined)};
}
function scrFRRed212SweepStep(_driver) {
    var _s=_driver.fr_red212_sweep;
    lockstep_stop=false;
    if(_s.phase==0) {
        if(_s.index>=96) {
            var _file=file_text_open_write(working_directory+"frontier-red212-native-sweep.json");
            file_text_write_string(_file,json_stringify({diagnostic:true,native_scheduler:true,
                manual_alarm_dispatch:false,expected_road_failures:_s.failures,
                actual_player_mask:"mskPlayer 8x10",rows:_s.rows,physical_device_tested:false}));
            file_text_close(_file);global.fr_red204_active=false;
            global.fr_red212_native_observe=_s.observe;global.fr_red212_native_trace=_s.trace;
            global.fr_red212_edge_guard=_s.edge_guard;
            if(_s.quest_had) variable_struct_set(global.ntte_full_progress.unlocks,"quest:part:3",_s.quest);
            else variable_struct_remove(global.ntte_full_progress.unlocks,"quest:part:3");
            scrNTTEFullWorldEventsNaturalWorldRestore(_s.world);lockstep_stop=_s.lock;global.time_scale=_s.scale;
            assert(_s.failures==0,"Native Red generation sealed pre-secret ordinary road cells or actual Player-mask edges");
            return true;
        }
        var _seed=_s.index+1,_loop_values=[0,1,3],_loops=_loop_values[_s.index mod 3];
        global.fr_red212_native_observe=true;global.fr_red212_native_trace=[];
        _s.gen=scrFRRed212Generate(_s.world,_seed,_loops,false);
        global.fr_red204_active=true;global.fr_red204_fast_scan=true;global.fr_red212_edge_guard=true;
        _s.meta={seed:_seed,loops:_loops};_s.frames=0;_s.phase=1;
        with(Player) {can_walk=false;can_aim=false;can_spec=false;can_shoot=false;bcan_shoot=false;speed=0;nexthurt=current_frame+100000;}
        return false;
    }
    if(instance_exists(_s.gen)) {
        if(++_s.frames>600) assert(false,"Red212 native sweep generator timed out; seed="+string(_s.meta.seed));
        return false;
    }
    scrFRRedConnectivity204FastBoundary("scheduled-final");
    var _last=global.fr_red204_boundaries[array_length(global.fr_red204_boundaries)-1],
        _post_walls=0,_native_trace=global.fr_red212_native_trace,
        _probe=scrFRRed212ProbeCells(instance_find(Player,0),false),_suspect=false;
    for(var _i=0;_i<array_length(_native_trace);++_i) {
        var _shift=_native_trace[_i],_shift_before=_shift.before;
        if(_shift_before.walls>0) _post_walls+=1;
    }
    var _expected_fail=array_length(_last.changed)>0 || array_length(_last.blocked_expected_edges)>0;
    if(_expected_fail) _s.failures+=1;
    _suspect=_expected_fail || _post_walls>0 || _probe.components>1;
    var _row={seed:_s.meta.seed,loops:_s.meta.loops,native_gen_frames:_s.frames,
        before_secret_protected:_last.protected_points,changed:_last.changed,
        expected_edges:_last.protected_edges,blocked_expected_edges:_last.blocked_expected_edges,
        actual_player_mask_pixel_sweep:_last.pixel_swept_expected_edges,
        post_wall_shifts:_post_walls,components:_probe.components,sizes:_probe.sizes,
        blocked:_probe.blocked,generation_trace:_native_trace,suspect:_suspect};
    if(_suspect) _row.geometry=_probe.geometry;
    if(_s.index<3) _row.seam=scrFRRedConnectivity204Seam(instance_find(Player,0));
    array_push(_s.rows,_row);scrNTTESmokeLog("RED212 NATIVE SWEEP "+json_stringify(_row));
    _s.index+=1;_s.phase=0;
    return false;
}
