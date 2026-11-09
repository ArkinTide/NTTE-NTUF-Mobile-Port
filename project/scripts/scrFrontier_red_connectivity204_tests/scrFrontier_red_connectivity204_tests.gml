// Isolated geometry probe. Every sample uses the real Player mask and real
// Floor/Wall collision queries; graph edges are checked at every pixel.
function scrFRRedConnectivity204Interior(_wall) {
    if(!instance_exists(_wall) || _wall.object_index!=Wall || !_wall.solid) return false;
    return position_meeting(_wall.bbox_left,_wall.bbox_top,Floor)
        && position_meeting(_wall.bbox_right-1,_wall.bbox_top,Floor)
        && position_meeting(_wall.bbox_left,_wall.bbox_bottom-1,Floor)
        && position_meeting(_wall.bbox_right-1,_wall.bbox_bottom-1,Floor);
}
function scrFRRedConnectivity204FastBoundary(_phase) {
    var _player=instance_find(Player,0),_points=[],_lookup={},_blocked=[],_fake_hits=0,_helper_hits=0,_styles=[0,0];
    if(_phase=="secret-before") {
        var _floors=scrNTTEFullInstances(Floor,true);
        for(var _f=0;_f<array_length(_floors);++_f) {
            var _floor=_floors[_f];if(_floor.styleb!=0 && _floor.styleb!=1) continue;
            for(var _y=floor(_floor.bbox_top/16)*16+8;_y<_floor.bbox_bottom;_y+=16)
                for(var _x=floor(_floor.bbox_left/16)*16+8;_x<_floor.bbox_right;_x+=16) {
                    var _key=string(_x)+","+string(_y);
                    if(variable_struct_exists(_lookup,_key) || !scrFRRedConnectivity204Open(_player,_x,_y)) continue;
                    _lookup[$ _key]=true;array_push(_points,[_x,_y,_floor.styleb]);_styles[_floor.styleb]+=1;
                }
        }
        global.fr_red204_protected=_points;global.fr_red204_protected_styles=_styles;
    }
    else {
        _points=global.fr_red204_protected;
        for(var _i=0;_i<array_length(_points);++_i) {
            var _point=_points[_i],_x=_point[0],_y=_point[1],_fake=false,_helper=false;
            with(_player) {
                _fake=place_meeting(_x,_y,NTTEFullWallFake);
                _helper=place_meeting(_x,_y,NTTEFullWallFakeHelper);
            }
            if(_fake) _fake_hits+=1;
            if(_helper) _helper_hits+=1;
            if(!scrFRRedConnectivity204Open(_player,_x,_y) || _fake || _helper) {
                var _walls=[],_hits=ds_list_create();
                try {
                    with(_player) {instance_place_list(_x,_y,Wall,_hits,false);instance_place_list(_x,_y,NTTEFullWallFakeHelper,_hits,false);}
                    for(var _w=0;_w<ds_list_size(_hits);++_w) {
                        var _wall=_hits[|_w];
                        array_push(_walls,{id:real(_wall),object:object_get_name(_wall.object_index),solid:_wall.solid,
                            x:_wall.x,y:_wall.y,bbox:[_wall.bbox_left,_wall.bbox_top,_wall.bbox_right,_wall.bbox_bottom]});
                    }
                } finally {ds_list_destroy(_hits);}
                array_push(_blocked,{point:_point,structural_open:scrFRRedConnectivity204Open(_player,_x,_y),
                    floor_lost:!position_meeting(_x,_y,Floor),fake:_fake,helper:_helper,walls:_walls});
            }
        }
    }
    var _row={phase:_phase,protected_points:array_length(_points),protected_styles:global.fr_red204_protected_styles,changed:_blocked,
        fake_overlap:_fake_hits,helper_overlap:_helper_hits,helpers:scrFRRedConnectivity204Helpers()};
    array_push(global.fr_red204_boundaries,_row);
    scrNTTESmokeLog("NTUF RED SCAN204 BOUNDARY "+_phase+" points="+string(array_length(_points))+" changed="+string(array_length(_blocked)));
}
function scrFRRedConnectivity204SeamContact(_player,_wall,_start,_at,_mode,_fakes,_helpers) {
    var _states=[];
    for(var _i=0;_i<array_length(_fakes);++_i) {
        array_push(_states,[_fakes[_i],_fakes[_i].mask_index]);
        if(_mode!="authored") _fakes[_i].mask_index=mskNone;
    }
    for(var _i=0;_i<array_length(_helpers);++_i) {
        array_push(_states,[_helpers[_i],_helpers[_i].solid]);
        if(_mode=="fake-and-helper-open") _helpers[_i].solid=false;
    }
    var _result=undefined;
    try {
        _player.xprevious=_start[0];_player.yprevious=_start[1];
        _player.x=_at[0];_player.y=_at[1];
        _player.hspeed=_at[0]-_start[0];_player.vspeed=_at[1]-_start[1];
        with(_wall) with(_player) event_perform(ev_collision,Wall);
        var _resolved=false;
        if(instance_exists(_wall)) with(_player) _resolved=!place_meeting(x,y,_wall);
        _result={mode:_mode,position:[_player.x,_player.y],motion:[_player.hspeed,_player.vspeed],
            wall_survived:instance_exists(_wall),ordinary_contact_resolved:_resolved};
        return _result;
    } finally {
        for(var _i=0;_i<array_length(_fakes);++_i) if(instance_exists(_states[_i][0])) _states[_i][0].mask_index=_states[_i][1];
        for(var _i=0;_i<array_length(_helpers);++_i) {
            var _state=_states[array_length(_fakes)+_i];if(instance_exists(_state[0])) _state[0].solid=_state[1];
        }
    }
}
function scrFRRedConnectivity204SeamPreconditions(_player,_wall,_fake,_start,_at) {
    var _start_helper=false,_start_wall=false,_contact_wall=false,_contact_fake=false;
    with(_player) {
        _start_helper=place_meeting(_start[0],_start[1],NTTEFullWallFakeHelper);
        _start_wall=scrNTTEFullPlayerWallMeeting(_start[0],_start[1]);
        _contact_wall=place_meeting(_at[0],_at[1],_wall);
        _contact_fake=place_meeting(_at[0],_at[1],_fake);
    }
    var _helper=noone;
    with(NTTEFullWallFakeHelper) if(creator==_fake) {_helper=id;break;}
    return {start_helper_overlap:_start_helper,start_ordinary_wall_overlap:_start_wall,
        contact_real_wall:_contact_wall,contact_fake_wall:_contact_fake,
        fake_native_mask:_fake.mask_index==object_get_mask(Wall),helper_exists:instance_exists(_helper),
        helper_closed:instance_exists(_helper) && _helper.solid,
        wall_object:object_get_name(_wall.object_index),wall_id:real(_wall),
        wall_bbox:[_wall.bbox_left,_wall.bbox_top,_wall.bbox_right,_wall.bbox_bottom]};
}
function scrFRRedConnectivity204AssertSeam(_fixture) {
    assert(!_fixture.invalid,"Red seam control was invalid");
    var _p=_fixture.preconditions,_a=_fixture.authored,_b=_fixture.controls[1];
    assert(!_p.start_helper_overlap && !_p.start_ordinary_wall_overlap && _p.contact_real_wall
        && _p.contact_fake_wall && _p.fake_native_mask && _p.helper_exists && _p.helper_closed,
        "Red seam did not begin at a closed, real ordinary/Fake wall boundary");
    assert(_a.wall_survived && _a.ordinary_contact_resolved,"Red seam destroyed or remained inside the ordinary wall");
    assert(point_distance(_a.position[0],_a.position[1],_b.position[0],_b.position[1])<0.01
        && point_distance(_a.motion[0],_a.motion[1],_b.motion[0],_b.motion[1])<0.01,
        "Red seam response still includes the visual Fake family");
}
function scrFRRedConnectivity204Seam(_player) {
    var _fakes=scrNTTEFullInstances(NTTEFullWallFake),_helpers=scrNTTEFullInstances(NTTEFullWallFakeHelper),
        _origin=[_player.x,_player.y],_parked=[],_actors=scrNTTEFullInstances(hitme),_chosen=undefined;
    for(var _i=0;_i<array_length(_actors);++_i) if(_actors[_i]!=_player) {
        array_push(_parked,_actors[_i]);instance_deactivate_object(_actors[_i]);
    }
    try {
        for(var _f=0;_f<array_length(_fakes) && is_undefined(_chosen);++_f) {
            var _fake=_fakes[_f],_walls=scrNTTEFullRectInstances(_fake.bbox_left-16,_fake.bbox_top-16,
                _fake.bbox_right+15,_fake.bbox_bottom+15,Wall);
            for(var _w=0;_w<array_length(_walls) && is_undefined(_chosen);++_w) {
                var _wall=_walls[_w];if(_wall.object_index!=Wall || !_wall.solid) continue;
                var _x1=max(_fake.bbox_left-3,_wall.bbox_left-3),_x2=min(_fake.bbox_right+3,_wall.bbox_right+3),
                    _y1=max(_fake.bbox_top-5,_wall.bbox_top-5),_y2=min(_fake.bbox_bottom+3,_wall.bbox_bottom+3);
                for(var _y=_y1;_y<=_y2 && is_undefined(_chosen);++_y) for(var _x=_x1;_x<=_x2 && is_undefined(_chosen);++_x) {
                    var _both=false;with(_player) _both=place_meeting(_x,_y,_fake) && place_meeting(_x,_y,_wall);
                    if(!_both) continue;
                    for(var _dx=-3;_dx<=3 && is_undefined(_chosen);_dx+=3) for(var _dy=-3;_dy<=3 && is_undefined(_chosen);_dy+=3) {
                        if(_dx==0 && _dy==0) continue;
                        var _sx=_x-_dx,_sy=_y-_dy,_outside=false;
                        with(_player) _outside=!place_meeting(_sx,_sy,NTTEFullWallFakeHelper);
                        if(!_outside || !scrFRRedConnectivity204Open(_player,_sx,_sy,false,true)) continue;
                        _player.x=_sx;_player.y=_sy;_player.speed=0;
                        with(NTTEFullWallFakeController) event_perform(ev_step,2);
                        var _start=[_sx,_sy],_at=[_x,_y],_wall_position=[_wall.x,_wall.y],
                            _pre=scrFRRedConnectivity204SeamPreconditions(_player,_wall,_fake,_start,_at),
                            _open=scrFRRedConnectivity204SeamContact(_player,_wall,_start,_at,"fake-and-helper-open",_fakes,_helpers);
                        if(!_open.wall_survived) {_chosen={invalid:true,reason:"control destroyed normal wall"};break;}
                        var _fake_open=scrFRRedConnectivity204SeamContact(_player,_wall,_start,_at,"fake-open",_fakes,_helpers);
                        if(!_fake_open.wall_survived) {_chosen={invalid:true,reason:"helper control destroyed normal wall"};break;}
                        var _authored=scrFRRedConnectivity204SeamContact(_player,_wall,_start,_at,"authored",_fakes,_helpers);
                        _chosen={invalid:false,start:_start,contact:_at,fake:[_fake.x,_fake.y],wall:_wall_position,preconditions:_pre,
                            controls:[_open,_fake_open],authored:_authored,actual_collision_event:true,
                            manual_collision_dispatch:true,physical_device_tested:false};
                    }
                }
            }
        }
        return is_undefined(_chosen)?{candidate:false}:{candidate:true,fixture:_chosen};
    } finally {
        _player.x=_origin[0];_player.y=_origin[1];_player.speed=0;
        for(var _i=0;_i<array_length(_parked);++_i) instance_activate_object(_parked[_i]);
    }
}
function scrFRRedConnectivity204DeterministicSeamTests(_state) {
    var _rows=[];
    for(var _rate=30;_rate<=60;_rate+=30) {
        scrFRWallFixTestsReset(_state);global.time_scale=30/_rate;
        GameCont.area=206;GameCont.subarea=1;GameCont.loops=0;
        var _x=810000,_y=810000,_floor=instance_create(_x+16,_y-16,Floor),
            _wall=instance_create(_x,_y-16,Wall),_fake=instance_create(_x,_y,NTTEFullWallFake),
            _player=instance_find(Player,0),_at=[_x+19,_y-5],_start=[_x+19+3*timescale,_y-5-3*timescale],
            _fakes=scrNTTEFullInstances(NTTEFullWallFake),_helpers=scrNTTEFullInstances(NTTEFullWallFakeHelper);
        with(_player) {mask_index=mskPlayer;image_xscale=1;image_yscale=1;image_angle=0;race=Race.Fish;roll=false;hammerhead=0;}
        _player.x=_start[0];_player.y=_start[1];_player.speed=0;
        with(NTTEFullWallFakeController) event_perform(ev_step,2);
        var _pre=scrFRRedConnectivity204SeamPreconditions(_player,_wall,_fake,_start,_at),
            _ordinary=scrFRRedConnectivity204SeamContact(_player,_wall,_start,_at,"fake-and-helper-open",_fakes,_helpers),
            _fake_open=scrFRRedConnectivity204SeamContact(_player,_wall,_start,_at,"fake-open",_fakes,_helpers),
            _authored=scrFRRedConnectivity204SeamContact(_player,_wall,_start,_at,"authored",_fakes,_helpers);
        _player.x=_at[0];_player.y=_at[1];_player.hspeed=0;_player.vspeed=3*timescale;
        with(_fake) with(_player) event_perform(ev_collision,Wall);
        var _fake_only=[_player.x,_player.y],_ordinary_resolved=false;
        with(_player) _ordinary_resolved=!place_meeting(_ordinary.position[0],_ordinary.position[1],_wall);
        var _row={rate:_rate,contact:_at,start:_start,ordinary:_ordinary,fake_open:_fake_open,authored:_authored,preconditions:_pre,
            fake_only:_fake_only,ordinary_contact_resolved:_ordinary_resolved,
            authored_vs_fake_open_distance:point_distance(_authored.position[0],_authored.position[1],_fake_open.position[0],_fake_open.position[1]),
            actual_player_collision_event:true,actual_native_floor_and_wall_create:true,
            actual_wall_fake_create_and_helper:true,manual_collision_dispatch:true,physical_device_tested:false};
        scrFRRedConnectivity204AssertSeam({invalid:false,preconditions:_pre,authored:_authored,controls:[_ordinary,_fake_open]});
        assert(point_distance(_fake_only[0],_fake_only[1],_at[0],_at[1])<0.01,"Fake-only native collision no longer passes through");
        array_push(_rows,_row);scrNTTESmokeLog("NTUF RED SEAM204 ROW "+json_stringify(_row));
    }
    return _rows;
}
function scrFRRedConnectivity204ScanTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && !instance_exists(GenCont),"Red scan requires isolated native runtime");
    var _state=scrNTTEFullWorldEventsNaturalWorldCapture(),_scale=timescale,_rows=[],_lock=lockstep_stop,
        _quest_had=variable_struct_exists(global.ntte_full_progress.unlocks,"quest:part:3"),
        _quest_value=scrNTTEFullUnlockGet("quest:part:3",undefined),_seams=[];
    try {
        lockstep_stop=false;global.fr_red204_active=false;
        _seams=scrFRRedConnectivity204DeterministicSeamTests(_state);global.time_scale=1;
        for(var _seed=1;_seed<=128;++_seed) {
            scrFRWallFixTestsReset(_state);global.fr_red204_active=true;global.fr_red204_boundaries=[];
            global.fr_red204_protected=[];variable_struct_set(global.ntte_full_progress.unlocks,"quest:part:3",false);
            GameCont.area=206;GameCont.subarea=1;GameCont.loops=0;GameCont.hard=5;
            GameCont.maxsubarea=1;GameCont.finalsubarea=true;GameCont.levseed=_seed;
            GameCont.ntte_quest_spawned_part_index_list=[];GameCont.ntte_full_source_seed=scrNTTEFullSourceSeedBuild(_seed);
            global.rng_state[@RNGStates.Generation]=_seed;global.ntte_full_sync_generation=false;random_set_seed(_seed);
            with(Player) {x=10016;y=10016;mask_index=mskPlayer;image_xscale=1;image_yscale=1;image_angle=0;race=Race.Fish;roll=false;hammerhead=0;}
            scrNTTEFullFloorResetStyle();scrNTTEFullFloorResetAlign();scrNTTEFullAreaNativeInit();
            scrNTTESmokeLog("NTUF RED SCAN204 START seed="+string(_seed));
            var _gen=instance_create(0,0,GenCont);
            with(_gen) event_perform(ev_alarm,2);
            with(_gen) event_perform(ev_alarm,0);
            _gen.ntte_full_sync_compact_defer=true;
            with(_gen) event_perform(ev_alarm,1);
            var _row={seed:_seed,rate:30,boundaries:global.fr_red204_boundaries,
                seam:_seed<=8?scrFRRedConnectivity204Seam(instance_find(Player,0)):{candidate:false,omitted:true}};
            array_push(_rows,_row);scrNTTESmokeLog("NTUF RED SCAN204 ROW "+json_stringify(_row));
        }
        var _file=file_text_open_write(working_directory+"frontier-red-scan204.json");
        file_text_write_string(_file,json_stringify({status:"DIAGNOSTIC",rates:[30],rows:_rows,seams:_seams,
            actual_gencont:true,actual_player_mask:true,physical_device_tested:false}));file_text_close(_file);
        scrNTTESmokeLog("NTUF RED SCAN204 DIAGNOSTIC complete");
    } finally {
        global.fr_red204_active=false;
        if(_quest_had) variable_struct_set(global.ntte_full_progress.unlocks,"quest:part:3",_quest_value);
        else variable_struct_remove(global.ntte_full_progress.unlocks,"quest:part:3");
        scrNTTEFullWorldEventsNaturalWorldRestore(_state);global.time_scale=_scale;lockstep_stop=_lock;
    }
}
function scrFRRedConnectivity204Open(_player,_x,_y,_ignore_internal=false,_normal_only=false,_helpers=false) {
    var _floor=false,_hits=ds_list_create(),_open=true;
    try {
        with(_player) {
            if(_normal_only) {
                instance_place_list(_x,_y,Floor,_hits,false);
                for(var _f=0;_f<ds_list_size(_hits);++_f) {
                    var _floor_hit=_hits[|_f];
                    if(!_floor_hit.styleb) {_floor=true;break;}
                }
                ds_list_clear(_hits);
            }
            else _floor=place_meeting(_x,_y,Floor);
            instance_place_list(_x,_y,Wall,_hits,false);
            instance_place_list(_x,_y,InvisiWall,_hits,false);
            if(_helpers) instance_place_list(_x,_y,NTTEFullWallFakeHelper,_hits,false);
        }
        if(!_floor) return false;
        for(var _i=0;_i<ds_list_size(_hits);++_i) {
            var _wall=_hits[|_i];
            // The authored hidden passage deliberately shares real floor
            // with visual fake walls and their proximity-opened helpers.
            if(instance_is(_wall,NTTEFullWallFake)) continue;
            if(!_wall.solid) continue;
            if(_ignore_internal && scrFRRedConnectivity204Interior(_wall)) continue;
            _open=false;break;
        }
        return _open;
    } finally {ds_list_destroy(_hits);}
}
function scrFRRedConnectivity204Edge(_player,_x,_y,_nx,_ny,_ignore_internal=false,_normal_only=false,_helpers=false) {
    var _steps=max(abs(_nx-_x),abs(_ny-_y));
    for(var _at=1;_at<=_steps;++_at)
        if(!scrFRRedConnectivity204Open(_player,lerp(_x,_nx,_at/_steps),lerp(_y,_ny,_at/_steps),_ignore_internal,_normal_only,_helpers)) return false;
    return true;
}
function scrFRRedConnectivity204Map(_player,_ignore_internal=false,_normal_only=false,_helpers=false) {
    // Floors and both authored/Fake walls share the native 16px lattice.
    // Test its cell centres with the actual 8x10 Player mask, retaining every
    // pixel of every edge instead of repeating four equivalent 8px samples.
    var _floors=scrNTTEFullInstances(Floor),_nodes=[],_lookup={},_step=16;
    for(var _f=0;_f<array_length(_floors);++_f) {
        var _floor=_floors[_f];
        if(_normal_only && _floor.styleb) continue;
        for(var _y=floor(_floor.bbox_top/_step)*_step+8;_y<_floor.bbox_bottom;_y+=_step)
            for(var _x=floor(_floor.bbox_left/_step)*_step+8;_x<_floor.bbox_right;_x+=_step) {
                var _key=string(_x)+","+string(_y);
                if(variable_struct_exists(_lookup,_key) || !scrFRRedConnectivity204Open(_player,_x,_y,_ignore_internal,_normal_only,_helpers)) continue;
                _lookup[$ _key]=array_length(_nodes);
                array_push(_nodes,{x:_x,y:_y,component:-1,distance:-1,parent:-1});
            }
    }
    var _components=0,_sizes=[];
    for(var _s=0;_s<array_length(_nodes);++_s) {
        if(_nodes[_s].component>=0) continue;
        var _queue=[_s],_head=0,_size=0;
        _nodes[_s].component=_components;_nodes[_s].distance=0;
        while(_head<array_length(_queue)) {
            var _index=_queue[_head++],_node=_nodes[_index];++_size;
            for(var _dir=0;_dir<4;++_dir) {
                var _nx=_node.x+(_dir==0?_step:(_dir==1?-_step:0)),
                    _ny=_node.y+(_dir==2?_step:(_dir==3?-_step:0)),_key=string(_nx)+","+string(_ny);
                if(!variable_struct_exists(_lookup,_key)) continue;
                var _next=_lookup[$ _key];
                if(_nodes[_next].component>=0 || !scrFRRedConnectivity204Edge(_player,_node.x,_node.y,_nx,_ny,_ignore_internal,_normal_only,_helpers)) continue;
                _nodes[_next].component=_components;_nodes[_next].distance=_node.distance+1;_nodes[_next].parent=_index;
                array_push(_queue,_next);
            }
        }
        array_push(_sizes,_size);++_components;
    }
    return {nodes:_nodes,lookup:_lookup,components:_components,sizes:_sizes};
}
function scrFRRedConnectivity204Helpers() {
    var _rows=[];
    with(NTTEFullWallFakeHelper) {
        var _normal=false,_floors=scrNTTEFullRectInstances(bbox_left,bbox_top,bbox_right-1,bbox_bottom-1,Floor),_styles=[];
        for(var _f=0;_f<array_length(_floors);++_f) {
            array_push(_styles,_floors[_f].styleb);
            if(!_floors[_f].styleb) _normal=true;
        }
        var _exists=instance_exists(creator);
        array_push(_rows,{id:real(id),x:x,y:y,solid:solid,bbox:[bbox_left,bbox_top,bbox_right,bbox_bottom],
            creator:real(creator),creator_exists:_exists,normal_floor_overlap:_normal,floor_styles:_styles,
            creator_mask:_exists && sprite_exists(creator.mask_index)?sprite_get_name(creator.mask_index):"missing"});
    }
    return _rows;
}
function scrFRRedConnectivity204Boundary(_phase) {
    if(!variable_global_exists("fr_red204_active") || !global.fr_red204_active || !instance_exists(Player)) return;
    if(variable_global_exists("fr_red204_fast_scan") && global.fr_red204_fast_scan) {scrFRRedConnectivity204FastBoundary(_phase);return;}
    var _player=instance_find(Player,0),_normal=scrFRRedConnectivity204Map(_player,false,true),
        _closed=scrFRRedConnectivity204Map(_player,false,true,true),_nodes=[];
    for(var _i=0;_i<array_length(_normal.nodes);++_i)
        array_push(_nodes,[_normal.nodes[_i].x,_normal.nodes[_i].y,_normal.nodes[_i].component]);
    var _row={phase:_phase,normal_nodes:array_length(_normal.nodes),normal_components:_normal.components,
        normal_component_sizes:_normal.sizes,closed_helper_nodes:array_length(_closed.nodes),
        closed_helper_components:_closed.components,closed_helper_component_sizes:_closed.sizes,
        normal_node_coordinates:_nodes,helpers:scrFRRedConnectivity204Helpers()};
    array_push(global.fr_red204_boundaries,_row);
    scrNTTESmokeLog("NTUF RED CONNECTIVITY204 BOUNDARY "+json_stringify(_row));
}
function scrFRRedConnectivity204Route(_graph,_from,_to) {
    if(_from<0 || _to<0 || _graph.nodes[_from].component!=_graph.nodes[_to].component) return [];
    var _from_path=[],_to_path=[],_at=_from;
    while(_at>=0) {array_push(_from_path,_at);_at=_graph.nodes[_at].parent;}
    _at=_to;
    while(_at>=0 && array_get_index(_from_path,_at)<0) {array_push(_to_path,_at);_at=_graph.nodes[_at].parent;}
    if(_at<0) return [];
    var _route=[];
    for(var _i=0;_i<=array_get_index(_from_path,_at);++_i) array_push(_route,_from_path[_i]);
    for(var _i=array_length(_to_path)-1;_i>=0;--_i) array_push(_route,_to_path[_i]);
    return _route;
}
function scrFRRedConnectivity204Walk(_player,_graph,_target) {
    var _spawn=[_player.x,_player.y],_from=scrFRRedConnectivity204Nearest(_graph,_player.x,_player.y),
        _to=scrFRRedConnectivity204Nearest(_graph,_target.x,_target.y),_route=scrFRRedConnectivity204Route(_graph,_from,_to),
        _parked=[],_steps=0,_contacts=0,_blocked=[],_peak=0,_overlap_closed=0,_hits=ds_list_create(),_reached=false;
    if(!array_length(_route)) {ds_list_destroy(_hits);return {steps:0,reached:false,reason:"no structural route"};}
    var _actors=scrNTTEFullInstances(hitme);
    for(var _i=0;_i<array_length(_actors);++_i) if(_actors[_i]!=_player) {
        array_push(_parked,_actors[_i]);instance_deactivate_object(_actors[_i]);
    }
    try {
        var _points=[[_player.x,_player.y]];
        for(var _i=0;_i<array_length(_route);++_i) {
            var _node=_graph.nodes[_route[_i]];array_push(_points,[_node.x,_node.y]);
        }
        array_push(_points,[_target.x,_target.y]);
        var _forward_count=array_length(_points);
        for(var _i=_forward_count-2;_i>=0;--_i) array_push(_points,_points[_i]);
        // Integrate the authored Player one pixel at a time and dispatch its
        // actual collision event with the contacted Wall as `other`. Helpers
        // have no Player collision event; their real controller EndStep owns
        // the temporary solid state and masks. This is not a hardware input test.
        for(var _leg=1;_leg<array_length(_points);++_leg) {
            var _start=[_player.x,_player.y],_goal=_points[_leg],
                _distance=max(abs(_goal[0]-_start[0]),abs(_goal[1]-_start[1]));
            for(var _pixel=1;_pixel<=_distance;++_pixel) {
                var _x=lerp(_start[0],_goal[0],_pixel/_distance),_y=lerp(_start[1],_goal[1],_pixel/_distance);
                _player.xprevious=_player.x;_player.yprevious=_player.y;
                _player.hspeed=_x-_player.x;_player.vspeed=_y-_player.y;
                _player.x=_x;_player.y=_y;
                ds_list_clear(_hits);
                with(_player) instance_place_list(x,y,Wall,_hits,false);
                for(var _w=0;_w<ds_list_size(_hits);++_w) {
                    var _wall=_hits[|_w];
                    if(instance_is(_wall,NTTEFullWallFake)) _contacts+=1;
                    with(_wall) with(_player) event_perform(ev_collision,Wall);
                }
                with(NTTEFullWallFakeController) event_perform(ev_step,2);
                _peak=max(_peak,scrNTTEFullValue(_player,"red_wall_fake",0));
                ds_list_clear(_hits);
                with(_player) instance_place_list(x,y,NTTEFullWallFakeHelper,_hits,false);
                for(var _h=0;_h<ds_list_size(_hits);++_h) {
                    var _helper_hit=_hits[|_h];if(_helper_hit.solid) _overlap_closed+=1;
                }
                _steps+=1;
                if(point_distance(_player.x,_player.y,_x,_y)>0.01) {
                    array_push(_blocked,{at:[_x,_y],actual:[_player.x,_player.y],walls:ds_list_size(_hits)});
                    break;
                }
            }
            if(_leg==_forward_count-1) _reached=point_distance(_player.x,_player.y,_target.x,_target.y)<0.01;
            if(array_length(_blocked)) break;
        }
        var _returned=point_distance(_player.x,_player.y,_spawn[0],_spawn[1])<0.01,_final=[_player.x,_player.y];
        _player.speed=0;
        repeat(ceil(12/timescale)) with(NTTEFullWallFakeController) event_perform(ev_step,2);
        var _orphans=0,_open=0;
        with(NTTEFullWallFakeHelper) {if(!instance_exists(creator)) _orphans+=1;if(!solid) _open+=1;}
        return {steps:_steps,reached:_reached,returned:_returned,blocked:_blocked,final:_final,fake_collision_events:_contacts,
            peak_reveal:_peak,closed_overlapping_after_endstep:_overlap_closed,
            orphan_helpers_after_endstep:_orphans,open_helpers_after_return:_open,
            reveal_after_return:scrNTTEFullValue(_player,"red_wall_fake",0),
            actual_wall_collision_events:true,actual_helper_endstep:true,manual_pixel_integration:true};
    } finally {
        ds_list_destroy(_hits);
        _player.x=_spawn[0];_player.y=_spawn[1];_player.speed=0;
        for(var _i=0;_i<array_length(_parked);++_i) instance_activate_object(_parked[_i]);
    }
}
function scrFRRedConnectivity204Nearest(_graph,_x,_y) {
    var _best=-1,_distance=infinity;
    for(var _i=0;_i<array_length(_graph.nodes);++_i) {
        var _node=_graph.nodes[_i],_d=point_distance(_x,_y,_node.x,_node.y);
        if(_d<_distance) {_best=_i;_distance=_d;}
    }
    return _best;
}
function scrFRRedConnectivity204Observe(_player,_rate,_seed,_phase,_generation="native-gencont") {
    var _graph=scrFRRedConnectivity204Map(_player),_relaxed=scrFRRedConnectivity204Map(_player,true),
        _spawn=scrFRRedConnectivity204Nearest(_graph,_player.x,_player.y),_targets=[],
        _relaxed_spawn=scrFRRedConnectivity204Nearest(_relaxed,_player.x,_player.y),
        _floors=scrNTTEFullInstances(Floor),_floor_masks=[],_internal=[],_overlap=0;
    for(var _i=0;_i<array_length(_floors);++_i) {
        var _f=_floors[_i];
        array_push(_floor_masks,{x:_f.x,y:_f.y,bbox:[_f.bbox_left,_f.bbox_top,_f.bbox_right,_f.bbox_bottom],
            mask:sprite_get_name(_f.mask_index>=0?_f.mask_index:_f.sprite_index),sprite:sprite_get_name(_f.sprite_index),
            visible:_f.visible,scale:[_f.image_xscale,_f.image_yscale],style:_f.styleb});
        if(collision_rectangle(_f.bbox_left,_f.bbox_top,_f.bbox_right-1,_f.bbox_bottom-1,NTTESolidWall,false,false)) {_overlap+=1;}
    }
    with(Wall) if(scrFRRedConnectivity204Interior(id)) array_push(_internal,{x:x,y:y,id:real(id)});
    var _objects=[NTTEFullWarp,NTTEFullPet];
    for(var _o=0;_o<array_length(_objects);++_o) with(_objects[_o]) {
        if(_objects[_o]==NTTEFullPet && pet!="Twins") continue;
        var _at=scrFRRedConnectivity204Nearest(_graph,x,y),_relaxed_at=scrFRRedConnectivity204Nearest(_relaxed,x,y);
        array_push(_targets,{kind:_o==0?"warp":"twins",x:x,y:y,
            reached:_spawn>=0 && _at>=0 && _graph.nodes[_spawn].component==_graph.nodes[_at].component,
            relaxed_reached:_relaxed_spawn>=0 && _relaxed_at>=0
                && _relaxed.nodes[_relaxed_spawn].component==_relaxed.nodes[_relaxed_at].component,
            nearest:[_at<0?0:_graph.nodes[_at].x,_at<0?0:_graph.nodes[_at].y],
            nearest_distance:_at<0?-1:point_distance(x,y,_graph.nodes[_at].x,_graph.nodes[_at].y),
            target_edge_open:_at>=0 && scrFRRedConnectivity204Edge(_player,_graph.nodes[_at].x,_graph.nodes[_at].y,x,y)});
    }
    var _row={rate:_rate,seed:_seed,phase:_phase,generation:_generation,area:GameCont.area,spawn:[_player.x,_player.y],
        player_mask:sprite_get_name(_player.mask_index>=0?_player.mask_index:_player.sprite_index),
        player_bbox:[_player.bbox_left,_player.bbox_top,_player.bbox_right,_player.bbox_bottom],
        floor_masks:_floor_masks,floor_count:array_length(_floors),internal_walls:_internal,
        nodes:array_length(_graph.nodes),components:_graph.components,component_sizes:_graph.sizes,
        relaxed_nodes:array_length(_relaxed.nodes),relaxed_components:_relaxed.components,
        relaxed_component_sizes:_relaxed.sizes,targets:_targets,fill_count:instance_number(NTTESolidWall),
        floor_fill_overlap:_overlap,fake_count:instance_number(NTTEFullWallFake),
        helper_count:instance_number(NTTEFullWallFakeHelper),helpers:scrFRRedConnectivity204Helpers(),
        boundaries:global.fr_red204_boundaries};
    if(_phase!="source") {
        var _twins=noone;
        with(NTTEFullPet) if(pet=="Twins") {_twins=id;break;}
        _row.walk=instance_exists(_twins)?scrFRRedConnectivity204Walk(_player,_graph,_twins):{reached:false,reason:"no twins"};
        _row.helpers_after_walk=scrFRRedConnectivity204Helpers();
    }
    scrNTTESmokeLog("NTUF RED CONNECTIVITY204 ROW "+json_stringify(_row));
    return _row;
}
function scrFRRedConnectivity204DiagnosticTests() {
    if(variable_global_exists("fr_red204_fast_scan") && global.fr_red204_fast_scan) {scrFRRedConnectivity204ScanTests();return;}
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),"Red geometry requires isolated native runtime");
    var _state=scrNTTEFullWorldEventsNaturalWorldCapture(),_scale=timescale,_rows=[],
        _seeds=[91,4458],_lock=lockstep_stop,
        _old_active=variable_global_exists("fr_red204_active")?global.fr_red204_active:false,
        _quest_had=variable_struct_exists(global.ntte_full_progress.unlocks,"quest:part:3"),
        _quest_value=scrNTTEFullUnlockGet("quest:part:3",undefined);
    try {
        lockstep_stop=false;
        for(var _rate=30;_rate<=60;_rate+=30) for(var _s=0;_s<array_length(_seeds);++_s) {
            scrFRWallFixTestsReset(_state);global.time_scale=30/_rate;
            global.fr_red204_active=true;global.fr_red204_boundaries=[];
            variable_struct_set(global.ntte_full_progress.unlocks,"quest:part:3",false);
            var _seed=_seeds[_s];
            GameCont.area=206;GameCont.subarea=1;GameCont.loops=0;GameCont.hard=5;
            GameCont.maxsubarea=1;GameCont.finalsubarea=true;GameCont.levseed=_seed;
            GameCont.ntte_quest_spawned_part_index_list=[];
            GameCont.ntte_full_source_seed=scrNTTEFullSourceSeedBuild(_seed);
            global.rng_state[@RNGStates.Generation]=_seed;
            scrNTTEFullFloorResetStyle();scrNTTEFullFloorResetAlign();scrNTTEFullAreaNativeInit();
            global.ntte_full_sync_generation=false;random_set_seed(_seed);
            with(Player) {mask_index=mskPlayer;image_xscale=1;image_yscale=1;image_angle=0;race=Race.Fish;roll=false;hammerhead=0;}
            var _gen=instance_create(0,0,GenCont);
            with(_gen) event_perform(ev_alarm,2);
            with(_gen) event_perform(ev_alarm,0);
            // Defer only the additive fill to compare the SAME real source
            // topology before/after representation; no builder is replaced.
            _gen.ntte_full_sync_compact_defer=true;
            with(_gen) event_perform(ev_alarm,1);
            var _player=instance_find(Player,0);
            array_push(_rows,scrFRRedConnectivity204Observe(_player,_rate,_seed,"source"));
            scrNTTESolidWallGenerate();
            array_push(_rows,scrFRRedConnectivity204Observe(_player,_rate,_seed,"filled"));
        }
        // Real Crystal Heart InRoom generation merges its Red terrain into an
        // existing ordinary map; it is a separate lifecycle from GenCont.
        for(var _rate=30;_rate<=60;_rate+=30) {
            scrFRWallFixTestsReset(_state);global.time_scale=30/_rate;
            global.fr_red204_active=false;global.fr_red204_boundaries=[];
            variable_struct_set(global.ntte_full_progress.unlocks,"quest:part:3",false);
            GameCont.area=area_desert;GameCont.subarea=1;GameCont.hard=5;GameCont.loops=0;
            GameCont.maxsubarea=3;GameCont.finalsubarea=false;GameCont.levseed=91;
            GameCont.ntte_quest_spawned_part_index_list=[];
            GameCont.ntte_full_source_seed=scrNTTEFullSourceSeedBuild(91);
            global.ntte_full_sync_generation=false;random_set_seed(91);
            with(Player) {x=10016;y=10016;mask_index=mskPlayer;image_xscale=1;image_yscale=1;image_angle=0;race=Race.Fish;roll=false;hammerhead=0;}
            scrNTTEFullAreaNativeInit();
            scrNTTEFullAreaGenerateNative(area_desert,1,0,10016,10016,true,0);
            var _old_floor_count=instance_number(Floor),_old_fill_count=instance_number(NTTESolidWall);
            global.fr_red204_active=true;
            scrNTTEFullAreaGenerateNative(206,1,0,10016,10016,true,0);
            var _inroom_row=scrFRRedConnectivity204Observe(instance_find(Player,0),_rate,91,"in-room","native-in-room");
            _inroom_row.old_floor_count=_old_floor_count;_inroom_row.old_fill_count=_old_fill_count;
            array_push(_rows,_inroom_row);
        }
        var _file=file_text_open_write(working_directory+"frontier-red-connectivity204.json");
        file_text_write_string(_file,json_stringify({status:"DIAGNOSTIC",rates:[30,60],rows:_rows,
            actual_gencont:true,actual_player_mask:true,pixel_swept_edges:true,
            forced_artifact_side_room:true,physical_device_tested:false}));
        file_text_close(_file);
        scrNTTESmokeLog("NTUF RED CONNECTIVITY204 DIAGNOSTIC complete actual topology before/after fill");
    } finally {
        global.fr_red204_active=_old_active;
        if(_quest_had) variable_struct_set(global.ntte_full_progress.unlocks,"quest:part:3",_quest_value);
        else variable_struct_remove(global.ntte_full_progress.unlocks,"quest:part:3");
        scrNTTEFullWorldEventsNaturalWorldRestore(_state);global.time_scale=_scale;lockstep_stop=_lock;
    }
}
function scrFRRedConnectivity204Generate(_state,_seed) {
    scrFRWallFixTestsReset(_state);global.time_scale=1;
    global.fr_red204_active=true;global.fr_red204_fast_scan=true;global.fr_red204_boundaries=[];
    global.fr_red204_protected=[];global.fr_red204_protected_styles=[0,0];
    variable_struct_set(global.ntte_full_progress.unlocks,"quest:part:3",false);
    GameCont.area=206;GameCont.subarea=1;GameCont.loops=0;GameCont.hard=5;
    GameCont.maxsubarea=1;GameCont.finalsubarea=true;GameCont.levseed=_seed;
    GameCont.ntte_quest_spawned_part_index_list=[];GameCont.ntte_full_source_seed=scrNTTEFullSourceSeedBuild(_seed);
    global.rng_state[@RNGStates.Generation]=_seed;global.ntte_full_sync_generation=false;random_set_seed(_seed);
    with(Player) {x=10016;y=10016;mask_index=mskPlayer;image_xscale=1;image_yscale=1;image_angle=0;race=Race.Fish;roll=false;hammerhead=0;}
    scrNTTEFullFloorResetStyle();scrNTTEFullFloorResetAlign();scrNTTEFullAreaNativeInit();
    var _gen=instance_create(0,0,GenCont);
    with(_gen) event_perform(ev_alarm,2);
    with(_gen) event_perform(ev_alarm,0);
    _gen.ntte_full_sync_compact_defer=true;
    with(_gen) event_perform(ev_alarm,1);
    return instance_find(Player,0);
}
function scrFRRedConnectivity204QueryTests(_state) {
    scrFRWallFixTestsReset(_state);global.time_scale=1;GameCont.area=206;
    var _x=820000,_y=820000,_fake=instance_create(_x,_y,NTTEFullWallFake),
        _normal=instance_create(_x+64,_y,Wall),_packed=scrNTTESolidWallBlock(_x+128,_y,16,16),
        _player=instance_find(Player,0),_rows=[];
    _normal.solid=false;_packed.solid=false;
    with(_player) {mask_index=mskPlayer;image_xscale=1;image_yscale=1;image_angle=0;}
    var _objects=[_fake,_normal,_packed],_expected=[false,true,true];
    for(var _i=0;_i<array_length(_objects);++_i) {
        var _object=_objects[_i],_actual=false,_native=false;
        with(_player) {_native=place_meeting(_object.x+8,_object.y+8,Wall);_actual=scrNTTEFullPlayerWallMeeting(_object.x+8,_object.y+8);}
        var _row={object:object_get_name(_object.object_index),solid:_object.solid,native_meeting:_native,
            actual:_actual,expected:_expected[_i],fake_family:instance_is(_object,NTTEFullWallFake)};
        assert(_native && _actual==_expected[_i],"Red query changed a non-Fake Wall or retained the visual Fake mask");
        array_push(_rows,_row);
    }
    scrNTTESmokeLog("NTUF RED QUERY204 ROW "+json_stringify(_rows));return _rows;
}
function scrFRRedConnectivity204AssertBoundaries(_boundaries) {
    assert(array_length(_boundaries)==3,"Red generation boundaries did not all execute");
    var _phases=["secret-before","corridor-after","quest-after"],_styles=_boundaries[0].protected_styles;
    assert(_styles[0]>0 && _styles[1]>0,"Red generation did not include ordinary and Warp approach floors");
    for(var _i=0;_i<3;++_i) {
        var _b=_boundaries[_i];
        assert(_b.phase==_phases[_i] && _b.protected_points==_boundaries[0].protected_points
            && _b.protected_styles[0]==_styles[0] && _b.protected_styles[1]==_styles[1]
            && !array_length(_b.changed) && _b.fake_overlap==0 && _b.helper_overlap==0,
            "Hidden corridor construction occupied an existing ordinary or Warp route");
    }
}
function scrFRRedConnectivity204AssertWalk(_walk,_hidden) {
    assert(_walk.steps>0 && _walk.reached && _walk.returned && !array_length(_walk.blocked)
        && _walk.closed_overlapping_after_endstep==0 && _walk.orphan_helpers_after_endstep==0
        && _walk.open_helpers_after_return==0 && _walk.reveal_after_return==0,
        "Red ordinary or secret path could not be walked in both directions with real collision/EndStep");
    if(_hidden) assert(_walk.fake_collision_events>0 && _walk.peak_reveal>0,"Secret walk never exercised native Fake collision and reveal");
}
function scrFRRedConnectivity204RegressionTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),"Red regression requires isolated native runtime");
    var _state=scrNTTEFullWorldEventsNaturalWorldCapture(),_scale=timescale,_lock=lockstep_stop,
        _old_active=variable_global_exists("fr_red204_active")?global.fr_red204_active:false,
        _old_fast=variable_global_exists("fr_red204_fast_scan")?global.fr_red204_fast_scan:false,
        _quest_had=variable_struct_exists(global.ntte_full_progress.unlocks,"quest:part:3"),
        _quest_value=scrNTTEFullUnlockGet("quest:part:3",undefined),_seams=[],_worlds=[],_walks=[],_queries=[];
    try {
        lockstep_stop=false;global.fr_red204_active=false;
        _queries=scrFRRedConnectivity204QueryTests(_state);
        _seams=scrFRRedConnectivity204DeterministicSeamTests(_state);
        for(var _seed=1;_seed<=3;++_seed) {
            // Reuse the exact generated witness geometry at both simulation
            // rates. Generation runs at its native 30Hz source configuration.
            var _player=scrFRRedConnectivity204Generate(_state,_seed),_boundaries=global.fr_red204_boundaries;
            scrFRRedConnectivity204AssertBoundaries(_boundaries);
            for(var _rate=30;_rate<=60;_rate+=30) {
                global.time_scale=30/_rate;
                var _seam=scrFRRedConnectivity204Seam(_player);
                assert(_seam.candidate,"Known generated seam witness was not found");
                scrFRRedConnectivity204AssertSeam(_seam.fixture);
                var _row={seed:_seed,rate:_rate,generation_rate:30,seam:_seam,boundaries:_boundaries,
                    actual_gencont:true,actual_player_collision_event:true,actual_helper_endstep:true};
                array_push(_worlds,_row);scrNTTESmokeLog("NTUF RED REGRESSION204 WORLD "+json_stringify(_row));
            }
        }
        // One complete independently generated map exercises both ordinary
        // Warp approaches (style 1) and the entire hidden Twins path.
        var _player=scrFRRedConnectivity204Generate(_state,91);
        scrFRRedConnectivity204AssertBoundaries(global.fr_red204_boundaries);
        scrNTTESolidWallGenerate();
        var _graph=scrFRRedConnectivity204Map(_player),_targets=[];
        assert(_graph.components==1 && array_length(_graph.nodes)>0,"Red structural road graph became disconnected");
        with(NTTEFullWarp) array_push(_targets,{kind:"warp",x:x,y:y});
        with(NTTEFullPet) if(pet=="Twins") array_push(_targets,{kind:"twins",x:x,y:y});
        assert(array_length(_targets)>1 && _targets[array_length(_targets)-1].kind=="twins","Red walk targets were missing");
        for(var _rate=30;_rate<=60;_rate+=30) for(var _i=0;_i<array_length(_targets);++_i) {
            global.time_scale=30/_rate;
            var _target=_targets[_i],_walk=scrFRRedConnectivity204Walk(_player,_graph,_target);
            scrFRRedConnectivity204AssertWalk(_walk,_target.kind=="twins");
            var _row={seed:91,rate:_rate,generation_rate:30,target_index:_i,target_count:array_length(_targets),
                target:_target,walk:_walk,components:_graph.components,nodes:array_length(_graph.nodes),
                actual_gencont:true,pixel_swept_edges:true,helpers_after_walk:scrFRRedConnectivity204Helpers()};
            array_push(_walks,_row);scrNTTESmokeLog("NTUF RED REGRESSION204 WALK "+json_stringify(_row));
        }
        var _file=file_text_open_write(working_directory+"frontier-red-regression204.json");
        file_text_write_string(_file,json_stringify({status:"PASS",rates:[30,60],worlds:_worlds,seams:_seams,walks:_walks,queries:_queries,
            actual_gencont:true,actual_player_mask:true,actual_player_collision_event:true,actual_helper_endstep:true,
            manual_collision_dispatch:true,manual_pixel_integration:true,physical_device_tested:false}));
        file_text_close(_file);scrNTTESmokeLog("NTUF RED REGRESSION204 PASS generated seams, ordinary Warp paths and hidden-room round trips");
    } finally {
        global.fr_red204_active=_old_active;global.fr_red204_fast_scan=_old_fast;
        if(_quest_had) variable_struct_set(global.ntte_full_progress.unlocks,"quest:part:3",_quest_value);
        else variable_struct_remove(global.ntte_full_progress.unlocks,"quest:part:3");
        scrNTTEFullWorldEventsNaturalWorldRestore(_state);global.time_scale=_scale;lockstep_stop=_lock;
    }
}
function scrFRRedConnectivity204Tests() {
    if(variable_global_exists("fr_red204_fast_scan") && global.fr_red204_fast_scan) {scrFRRedConnectivity204ScanTests();return;}
    scrFRRedConnectivity204RegressionTests();
}
