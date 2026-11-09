// Extends the existing genuine Pizza/40HP drain/Bolt20+20 native route.
// Movement is supplied only after actual native input sampling. The real
// Player moves/collides and the real border performs its scheduled cave-in.
function scrFRLairReturn205TestsStart() {
    scrNTTEFullPizzaLairDrainNaturalTests();
    with(NTTEFullPizzaLairDrainNaturalTest) {
        fr_lair_return205_requested=true;fr_lair_return205=undefined;fr_lair_return205_rows=[];
        rates=[30,60,30,60,30,60];fr_lair_return205_seeds=[6123,41,702643];
    }
}
function scrFRLairReturn205LingerTestsStart() {
    scrFRLairReturn205TestsStart();
    with(NTTEFullPizzaLairDrainNaturalTest) {
        fr_lair_return205_linger=true;rates=[30,60];fr_lair_return205_seeds=[6123];
    }
}
function scrFRLairReturn205PointClear(_player,_x,_y) {
    var _clear=false;
    with(_player) _clear=!scrNTTEFullPlayerWallMeeting(_x,_y) && !place_meeting(_x,_y,InvisiWall);
    return _clear && position_meeting(_x,_y,Floor);
}
// Test-only graph on actual generated Floor centers. The old mp_grid-based
// fixture rejected a safe subpixel Player beside a wall despite subsequent
// real sampled movement >100px through the same generated corridor.
// Keep the real subpixel start and validate every 1px along all graph edges.
// The graph only supplies ordinary sampled input; it never moves an actor.
function scrFRLairReturn205SegmentClear(_player,_x1,_y1,_x2,_y2) {
    var _steps=max(1,ceil(point_distance(_x1,_y1,_x2,_y2)));
    for(var _i=0;_i<=_steps;++_i)
        if(!scrFRLairReturn205PointClear(_player,lerp(_x1,_x2,_i/_steps),lerp(_y1,_y2,_i/_steps))) return false;
    return true;
}
function scrFRLairReturn205FloorGraph(_player) {
    var _nodes=[],_lookup={},_queue=[];
    with(Floor) for(var _y1=bbox_top+8;_y1<=bbox_bottom-8;_y1+=16)
        for(var _x1=bbox_left+8;_x1<=bbox_right-8;_x1+=16) {
            var _key=string(_x1)+","+string(_y1);
            if(!is_undefined(_lookup[$ _key]) || !scrFRLairReturn205PointClear(_player,_x1,_y1)) continue;
            _lookup[$ _key]=array_length(_nodes);
            array_push(_nodes,{x:_x1,y:_y1,parent:-2});
        }
    for(var _i=0;_i<array_length(_nodes);++_i) {
        var _node=_nodes[_i];
        if(point_distance(_player.x,_player.y,_node.x,_node.y)<=32
            && scrFRLairReturn205SegmentClear(_player,_player.x,_player.y,_node.x,_node.y)) {
            _node.parent=-1;array_push(_queue,_i);
        }
    }
    for(var _head=0;_head<array_length(_queue);++_head) {
        var _index=_queue[_head],_node=_nodes[_index];
        for(var _dy=-16;_dy<=16;_dy+=16) for(var _dx=-16;_dx<=16;_dx+=16) {
            if(_dx==0 && _dy==0) continue;
            var _key=string(_node.x+_dx)+","+string(_node.y+_dy),_next=_lookup[$ _key];
            if(is_undefined(_next) || _nodes[_next].parent!=-2) continue;
            var _neighbor=_nodes[_next];
            if(!scrFRLairReturn205SegmentClear(_player,_node.x,_node.y,_neighbor.x,_neighbor.y)) continue;
            _neighbor.parent=_index;array_push(_queue,_next);
        }
    }
    return {nodes:_nodes,lookup:_lookup,reachable:array_length(_queue)};
}
function scrFRLairReturn205NativePath(_player,_path,_x,_y) {
    path_clear_points(_path);
    if(scrFRLairReturn205SegmentClear(_player,_player.x,_player.y,_x,_y)) {
        path_add_point(_path,_player.x,_player.y,100);path_add_point(_path,_x,_y,100);return true;
    }
    var _graph=scrFRLairReturn205FloorGraph(_player),_key=string(_x)+","+string(_y),
        _index=_graph.lookup[$ _key],_reverse=[];
    if(is_undefined(_index) || _graph.nodes[_index].parent==-2) return false;
    while(_index>=0) {array_push(_reverse,_index);_index=_graph.nodes[_index].parent;}
    path_add_point(_path,_player.x,_player.y,100);
    for(var _i=array_length(_reverse)-1;_i>=0;--_i) {
        var _node=_graph.nodes[_reverse[_i]];path_add_point(_path,_node.x,_node.y,100);
    }
    return path_get_number(_path)>1;
}
function scrFRLairReturn205GoalDiagnostic(_observer,_x,_y) {
    var _p=_observer.player,_s=_observer.fr_lair_return205,_walls=[],_floors=[],_rays=[],
        _best=0,_direction=0;
    with(Wall) if(bbox_left<_p.x+96 && bbox_right>_p.x-96 && bbox_top<_p.y+96 && bbox_bottom>_p.y-96)
        array_push(_walls,{object:object_get_name(object_index),bbox:[bbox_left,bbox_top,bbox_right,bbox_bottom]});
    with(Floor) if(bbox_left<_p.x+96 && bbox_right>_p.x-96 && bbox_top<_p.y+96 && bbox_bottom>_p.y-96)
        array_push(_floors,{object:object_get_name(object_index),bbox:[bbox_left,bbox_top,bbox_right,bbox_bottom]});
    for(var _angle=0;_angle<360;_angle+=45) {
        var _distance=0;
        for(var _step=1;_step<=64;++_step) {
            if(!scrFRLairReturn205PointClear(_p,_p.x+lengthdir_x(_step,_angle),_p.y+lengthdir_y(_step,_angle))) break;
            _distance=_step;
        }
        array_push(_rays,[_angle,_distance]);
        if(_distance>_best) {_best=_distance;_direction=_angle;}
    }
    // Before rejecting the route, attempt real sampled movement in the best
    // clear direction. The failure report can distinguish a navigation-grid
    // rejection from a Player actually trapped by the completed cave-in.
    _s.goal_probe={start:[_p.x,_p.y],ticks:0,direction:_direction,clear_distance:_best,
        requested:[_x,_y],walls:_walls,floors:_floors,mask_rays:_rays};
    _s.goal=[_p.x+lengthdir_x(min(32,_best),_direction),_p.y+lengthdir_y(min(32,_best),_direction)];
    scrNTTESmokeLog("FR_LAIR_RETURN205_GOAL_DIAGNOSTIC "+json_stringify(_s.goal_probe));
}
function scrFRLairReturn205Goal(_observer,_x,_y,_minimum_move=0) {
    var _s=_observer.fr_lair_return205,_best=infinity,_gx=0,_gy=0,_player=_observer.player;
    // Preserve source dormant/entry projections. After collapse require a
    // distinct point in the actual Player-mask connected Floor component.
    if(_minimum_move>0) {
        var _graph=scrFRLairReturn205FloorGraph(_player);
        for(var _i=0;_i<array_length(_graph.nodes);++_i) {
            var _node=_graph.nodes[_i],_d=point_distance(_node.x,_node.y,_x,_y);
            if(_node.parent!=-2 && _d<_best
                && point_distance(_player.x,_player.y,_node.x,_node.y)>=_minimum_move) {
                _best=_d;_gx=_node.x;_gy=_node.y;
            }
        }
        _s.mask_graph={nodes:array_length(_graph.nodes),reachable:_graph.reachable,
            start:[_player.x,_player.y],goal:[_gx,_gy]};
    } else with(Floor) for(var _y1=bbox_top+8;_y1<=bbox_bottom-8;_y1+=16)
        for(var _x1=bbox_left+8;_x1<=bbox_right-8;_x1+=16) {
            var _d=point_distance(_x1,_y1,_x,_y);
            if(_d<_best && scrFRLairReturn205PointClear(_player,_x1,_y1)) {
                _best=_d;_gx=_x1;_gy=_y1;
            }
        }
    if(_best==infinity) {scrFRLairReturn205GoalDiagnostic(_observer,_x,_y);return;}
    _s.goal_probe=undefined;
    _s.goal=[_gx,_gy];_s.goal_ticks=0;_s.path_clock=0;_s.path_cursor=1;
    _s.last_xy=[_observer.player.x,_observer.player.y];_s.still_ticks=0;
    path_clear_points(_observer.bot_path);
}
function scrFRLairReturn205Write(_observer,_status,_reason="") {
    var _s=_observer.fr_lair_return205,_out={schema:1,status:_status,reason:_reason,
        physical_device_tested:false,native_sampled_movement:true,
        production_terrain_modified_by_test:false,routes:_observer.fr_lair_return205_rows,active:_s};
    var _file=file_text_open_write(working_directory+"frontier-lair-return205.json");
    file_text_write_string(_file,json_stringify(_out));file_text_close(_file);
    scrNTTESmokeLog("FR_LAIR_RETURN205 "+json_stringify(_out));
}
function scrFRLairReturn205Fail(_observer,_reason) {
    scrFRLairReturn205Write(_observer,"FAIL",_reason);throw _reason;
}
function scrFRLairReturn205Validated(_observer) {
    if(!scrNTTEFullValue(_observer,"fr_lair_return205_requested",false)) return false;
    var _border=instance_find(NTTEFullLairBorder,0);
    assert(instance_exists(_border),"Original Pizza/Lair route has no actual border");
    _observer.fr_lair_return205={rate:_observer.rates[_observer.pass_index],seed:_observer.current_seed,phase:0,ticks:0,
        border:_border,start:[_observer.player.x,_observer.player.y],goal:[],goal_ticks:0,
        path_clock:0,path_cursor:1,move_samples:0,overlap_ticks:0,still_ticks:0,witnesses:[],
        before_return:false,during_return:false,after_cavein:false,rubble:noone,
        initial_hp:_observer.player.hp,mask:_observer.player.mask_index,collision_witness:undefined,
        linger:scrNTTEFullValue(_observer,"fr_lair_return205_linger",false),linger_draw:-1,buried_witness:false,goal_probe:undefined};
    scrFRLairReturn205Goal(_observer,_border.x,_border.y+96);
    scrFRLairReturn205Write(_observer,"IN_PROGRESS","original native drain route passed; starting sampled entry/return");
    return true;
}
function scrFRLairReturn205Witness(_observer,_label) {
    var _s=_observer.fr_lair_return205,_p=_observer.player,_border=_s.border,
        _walls=scrNTTEFullRectInstances(_p.bbox_left-1,_p.bbox_top-1,_p.bbox_right+1,_p.bbox_bottom+1,[Wall,InvisiWall]),_near=[];
    for(var _i=0;_i<array_length(_walls);++_i) with(_walls[_i])
        array_push(_near,{object:object_get_name(object_index),id:real(id),xy:[x,y],
            bbox:[bbox_left,bbox_top,bbox_right,bbox_bottom],packed:object_index==NTTESolidWall,
            w:scrNTTEFullValue(id,"ntte_fill_width",16),h:scrNTTEFullValue(id,"ntte_fill_height",16)});
    var _row={label:_label,phase:_s.phase,frame:current_frame,xy:[_p.x,_p.y],hp:_p.hp,
        goal:_s.goal,cavein:_border.ntte_full_cavein,distance:_border.ntte_full_cavein_distance,
        in_wall:!scrFRLairReturn205PointClear(_p,_p.x,_p.y),walls:_near,path_points:path_get_number(_observer.bot_path),
        path_mode:_s[$ "path_mode"]??"not-sampled",
        visible:_p.visible,saved_by_border:array_get_index(_border.ntte_full_cavein_saved,_p)>=0,
        saved_by_rubble:instance_exists(NTTEFullPizzaRubble)?array_get_index(NTTEFullPizzaRubble.ntte_full_saved,_p)>=0:false};
    array_push(_s.witnesses,_row);scrNTTESmokeLog("FR_LAIR_RETURN205_WITNESS "+json_stringify(_row));
}
function scrFRLairReturn205AssertReleased(_observer) {
    var _s=_observer.fr_lair_return205,_p=_observer.player;
    assert(_p.visible && array_get_index(_s.border.ntte_full_cavein_saved,_p)<0
        && (!instance_exists(NTTEFullPizzaRubble)
            || array_get_index(NTTEFullPizzaRubble.ntte_full_saved,_p)<0),
        "Actual cave-in retained a live Player in hidden border/rubble salvage");
}
function scrFRLairReturn205Before(_observer) {
    if(!scrNTTEFullValue(_observer,"fr_lair_return205_requested",false)) return false;
    if(is_undefined(_observer.fr_lair_return205)) {
        _observer.current_seed=_observer.fr_lair_return205_seeds[floor(_observer.pass_index/2)];return false;
    }
    var _s=_observer.fr_lair_return205,_player=_observer.player,_border=_s.border;
    _s.ticks+=timescale;_s.goal_ticks+=timescale;
    if(!instance_exists(_player) || _player.hp<=0)
        scrFRLairReturn205Fail(_observer,"Native traversal player died; distinguish source cave-in hazard from a wall trap");
    assert(instance_exists(_border) && _player.mask_index==_s.mask,"Pizza traversal lost original border/player mask");
    // Suppress unrelated enemy damage only. The source cave-in assigns hp=0
    // directly and remains observable; health, speed and collision stay native.
    _player.nexthurt=current_frame+100000;
    if(!scrFRLairReturn205PointClear(_player,_player.x,_player.y)) _s.overlap_ticks+=timescale;
    else _s.overlap_ticks=0;
    if(_s.overlap_ticks>=15 && _s.phase!=7) {
        scrFRLairReturn205Witness(_observer,"persistent-wall-overlap");
        scrFRLairReturn205Fail(_observer,"Actual native Player remained inside wall collision for 15 logical ticks");
    }
    if(_s.goal_ticks>900) {
        scrFRLairReturn205Witness(_observer,"native-route-stalled");
        scrFRLairReturn205Fail(_observer,"Actual native sampled movement did not reach the generated corridor goal");
    }
    if(!is_undefined(_s.goal_probe)) {
        _s.goal_probe.ticks+=timescale;
        if(_s.goal_probe.ticks>=30) {
            _s.goal_probe.finish=[_player.x,_player.y];
            _s.goal_probe.actual_distance=point_distance(_player.x,_player.y,_s.goal_probe.start[0],_s.goal_probe.start[1]);
            scrFRLairReturn205Witness(_observer,"no-goal-after-real-sampled-mobility-probe");
            scrFRLairReturn205Fail(_observer,"No distinct native-mask reachable goal; actual sampled mobility and terrain recorded");
        }
        return true;
    }
    var _arrived=point_distance(_player.x,_player.y,_s.goal[0],_s.goal[1])<8;
    if(_s.phase==0 && _arrived) {
        assert(_border.ntte_full_cavein==0,"Pre-border entry unexpectedly triggered cave-in");
        scrFRLairReturn205Witness(_observer,"entered-before-border");_s.phase=1;
        scrFRLairReturn205Goal(_observer,_s.start[0],_s.start[1]);return true;
    }
    if(_s.phase==1 && _arrived) {
        assert(_border.ntte_full_cavein==0,"Returning before border unexpectedly triggered cave-in");
        _s.before_return=true;scrFRLairReturn205Witness(_observer,"returned-to-pizza-before-cavein");
        _s.phase=2;scrFRLairReturn205Goal(_observer,_border.x,_border.y-24);return true;
    }
    if(_s.phase==2 && _border.ntte_full_cavein>0) {
        scrFRLairReturn205Witness(_observer,"real-crossing-triggered-cavein");_s.phase=3;
        scrFRLairReturn205Goal(_observer,_border.x,_border.y+32);return true;
    }
    if(_s.phase==3 && _arrived) {
        _s.during_return=true;scrFRLairReturn205Witness(_observer,"returned-during-cavein-countdown");
        if(_s.linger) {_s.phase=7;_s.goal_ticks=0;return true;}
        _s.phase=4;scrFRLairReturn205Goal(_observer,_border.x,_border.y-128);return true;
    }
    if(_s.phase==7) {
        if(array_get_index(_border.ntte_full_cavein_saved,_player)>=0 && !_s.buried_witness) {
            _s.buried_witness=true;scrFRLairReturn205Witness(_observer,"native-border-captured-live-player");
        }
        if(_border.ntte_full_cavein>=0) return true;
        if(_s.linger_draw<0) {
            _s.linger_draw=_observer.draw_frames;
            scrFRLairReturn205Witness(_observer,"lingered-through-real-cavein");return true;
        }
        if(_observer.draw_frames-_s.linger_draw<8) return true;
        scrFRLairReturn205AssertReleased(_observer);
        _s.after_cavein=true;scrFRLairReturn205Witness(_observer,"eight-real-draws-after-lingering-cavein");
        _s.phase=8;_s.overlap_ticks=0;_s.post_begin=[_player.x,_player.y];
        scrFRLairReturn205Goal(_observer,_border.x,_border.y-128,32);return true;
    }
    if(_s.phase==4 && _arrived && _border.ntte_full_cavein<0) {
        scrFRLairReturn205AssertReleased(_observer);
        _s.after_cavein=true;scrFRLairReturn205Witness(_observer,"survived-real-cavein-clear-of-walls");
        assert(instance_exists(NTTEFullPizzaRubble),"Real completed cave-in failed to build original Pizza rubble");
        _s.rubble=instance_find(NTTEFullPizzaRubble,0);_s.phase=5;_s.post_begin=[_player.x,_player.y];
        // First move away, then approach the closed original rubble, then
        // retreat. Every target must be a distinct reachable actual Floor.
        scrFRLairReturn205Goal(_observer,_player.x,_player.y-96,32);return true;
    }
    if(_s.phase==5 && _arrived) {
        assert(point_distance(_player.x,_player.y,_s.post_begin[0],_s.post_begin[1])>=16,
            "Post-cavein initial retreat fixture did not actually move");
        scrFRLairReturn205Witness(_observer,"moved-away-from-completed-cavein");
        _s.post_begin=[_player.x,_player.y];_s.phase=6;
        scrFRLairReturn205Goal(_observer,_s.rubble.x,_s.rubble.y-40,32);return true;
    }
    if(_s.phase==6 && _arrived) {
        scrFRLairReturn205AssertReleased(_observer);
        assert(point_distance(_player.x,_player.y,_s.post_begin[0],_s.post_begin[1])>=16,
            "Post-cavein approach fixture did not actually move");
        scrFRLairReturn205Witness(_observer,"approached-closed-rubble-without-overlap");
        _s.post_begin=[_player.x,_player.y];_s.phase=9;
        scrFRLairReturn205Goal(_observer,_player.x,_player.y-96,32);return true;
    }
    if((_s.phase==9 || _s.phase==8) && _arrived) {
        scrFRLairReturn205AssertReleased(_observer);
        assert(point_distance(_player.x,_player.y,_s.post_begin[0],_s.post_begin[1])>=16,
            "Post-cavein retreat fixture did not actually move");
        scrFRLairReturn205Witness(_observer,"moved-away-after-cavein");
        assert(_s.before_return && _s.during_return && _s.after_cavein && _s.move_samples>0,
            "Pizza return acceptance omitted a real traversal branch");
        array_push(_observer.fr_lair_return205_rows,_s);
        scrFRLairReturn205Write(_observer,"IN_PROGRESS","native rate route completed");
        _observer.fr_lair_return205=undefined;
        if(++_observer.pass_index<array_length(_observer.rates)) {
            with(_observer) scrNTTEFullPizzaLairDrainAwait(0);return true;
        }
        // Publish PASS before source restore retires the dedicated observer.
        _observer.fr_lair_return205={completed:true};scrFRLairReturn205Write(_observer,"PASS");
        with(_observer) scrNTTEFullPizzaLairDrainRestore();
        scrNTTESmokeLog("PASS FRONTIER Pizza-to-Lair205 real opening, native sampled entry/return before/during cavein, postcavein movement x3seeds x30/60");
        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");game_end();
    }
    return true;
}
function scrFRLairReturn205AfterSample(_observer,_keycont,_index) {
    if(!scrNTTEFullValue(_observer,"fr_lair_return205_requested",false)
        || is_undefined(_observer.fr_lair_return205) || _observer.player.index!=_index) return;
    var _s=_observer.fr_lair_return205,_p=_observer.player,
        _moving=point_distance(_p.x,_p.y,_s.goal[0],_s.goal[1])>=6,
        _dir=point_direction(_p.x,_p.y,_s.goal[0],_s.goal[1]),
        _native_nav=_s.after_cavein || _s.border.ntte_full_cavein<0;
    // Phase4 must still reach its original north goal after the native
    // cave-in completes; its after_cavein acceptance flag is set only on
    // arrival. Select mask navigation from actual terrain state as well.
    _s.path_mode=_native_nav?"native-mask-floor-graph":"pre-collapse-source-grid";
    if(!is_undefined(_s.goal_probe)) {
        _keycont.moving[_index]=1;_keycont.dir_move[_index]=_s.goal_probe.direction;
        _keycont.hold_fire[_index]=false;_keycont.press_fire[_index]=false;_keycont.release_fire[_index]=false;
        _s.move_samples++;return;
    }
    if(_s.phase==7) _moving=false;
    _s.path_clock-=timescale;
    if(_moving) {
        if(_s.path_clock<=0) {
            _s.path_clock=15;_s.path_cursor=1;
            if(_native_nav) scrFRLairReturn205NativePath(_p,_observer.bot_path,_s.goal[0],_s.goal[1]);
            else {
                var _left=infinity,_top=infinity,_right=-infinity,_bottom=-infinity;
                with(Floor) {_left=min(_left,bbox_left);_top=min(_top,bbox_top);
                    _right=max(_right,bbox_right);_bottom=max(_bottom,bbox_bottom);}
                _left=floor((_left-64)/8)*8;_top=floor((_top-64)/8)*8;
                var _grid=mp_grid_create(_left,_top,ceil((_right+64-_left)/8),ceil((_bottom+64-_top)/8),8,8);
                with(Wall) mp_grid_add_rectangle(_grid,bbox_left-5,bbox_top-3,bbox_right+5,bbox_bottom+3);
                with(InvisiWall) mp_grid_add_rectangle(_grid,bbox_left-5,bbox_top-3,bbox_right+5,bbox_bottom+3);
                path_clear_points(_observer.bot_path);
                mp_grid_path(_grid,_observer.bot_path,_p.x,_p.y,_s.goal[0],_s.goal[1],false);mp_grid_destroy(_grid);
            }
        }
        var _path=_observer.bot_path;
        if(path_get_number(_path)>1) {
            while(_s.path_cursor<path_get_number(_path)-1
                && point_distance(_p.x,_p.y,path_get_point_x(_path,_s.path_cursor),path_get_point_y(_path,_s.path_cursor))<(_native_nav?2:6))
                _s.path_cursor++;
            _dir=point_direction(_p.x,_p.y,path_get_point_x(_path,_s.path_cursor),path_get_point_y(_path,_s.path_cursor));
        } else _moving=false;
    }
    if(_moving) _s.move_samples++;
    _keycont.moving[_index]=_moving?1:0;_keycont.dir_move[_index]=_dir;
    _keycont.hold_fire[_index]=false;_keycont.press_fire[_index]=false;_keycont.release_fire[_index]=false;
}
