// Explicit private regression: actual Player/Collision_Wall events, followed
// by scheduled native movement/collision phases. No window or audio is used.
function scrFRPalacePlayerContactTestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Palace player contact requires a settled isolated native runner");
    _driver.fr_palace_contacts={world:scrNTTEFullWorldEventsNaturalWorldCapture(),
        phase:0,rate:0,scene:0,wait:0,elapsed:0,rows:[],
        player:instance_find(Player,0),block:noone,stack:noone,wall:noone,
        x:844992,y:844992};
}

function scrFRPalacePlayerContactTestsBlock(_x,_y,_moving,_direction) {
    var _block=scrFRModCallArray("mod","Frontier_Palace","CrushBlock_create",[_x,_y]);
    _block.mywall=scrFRModCallArray("mod","Frontier_Palace","crushBlock_wall_create",[_block]);
    _block.myWallisReal=true;_block.myWallGetReal=0;
    _block.moveCooldown=100000;_block.active=_moving;_block.direction=_direction;
    _block.speed=(_moving?6:0)*timescale;
    assert(_block.crushspeed==6 && _block.damage==8 && _block.damage_enemy==30,
        "Palace player fixture changed authored speed/crush damage");
    return _block;
}

function scrFRPalacePlayerContactTestsSourceStep() {
    // Preserve the real generated source callback and its scope/RNG. Observe
    // immediately after its predictive push, before engine Collision and the
    // later End Step proxy synchronization can introduce an outer-shell touch.
    scrFRInvoke(id,fr_palace_contact_source_step,[]);
    var _state=fr_palace_contact_state,_row=_state.row,_player=_state.player;
    _row.scheduled_source_steps++;
    if(_state.scene!=0 && _state.scene!=4) return;
    if(_player.fr_palace_push_frame!=current_frame || _player.fr_palace_push_owner!=id) return;
    var _body=id,_dx=hspeed,_dy=vspeed,_separated=false;
    // The source temporarily advances its INNER body by native hspeed/vspeed
    // while pushing, then restores it. Translating only the query point gives
    // the exact same relative real masks without moving either live instance.
    with(_player) _separated=!place_meeting(x-_dx,y-_dy,_body);
    _row.scheduled_source_pushes++;
    _row.source_phase_inner_separated=_row.source_phase_inner_separated && _separated;
    assert(_separated,"Scheduled Palace original push left its actual predictive inner mask overlapping: "+json_stringify(_row));
}

function scrFRPalaceMoveOutsideNativeProbe(_player) {
    // Exercise the actual engine builtin in a closed solid, including its
    // special nonpositive-distance behavior. This is diagnostic only; the
    // authored trap's hspeed/vspeed guard cannot push when its speed is zero.
    var _wall=instance_create(898000,898000,Wall),_rows=[],
        _x=_player.x,_y=_player.y,_xp=_player.xprevious,_yp=_player.yprevious;
    _wall.image_xscale=256;_wall.image_yscale=256;
    for(var _i=0;_i<3;++_i) {
        var _distance=[6,0,-1][_i],_elapsed=get_timer(),_startx=899000;
        with(_player) {x=_startx;y=899000;move_outside_solid(0,_distance);}
        _elapsed=get_timer()-_elapsed;
        var _inside=false;with(_player) _inside=place_meeting(x,y,_wall);
        array_push(_rows,{max_distance:_distance,elapsed_us:_elapsed,
            displacement:_player.x-_startx,still_inside:_inside});
        assert(_elapsed<2000000,"Native move_outside_solid exceeded bounded diagnostic time: "+json_stringify(_rows));
    }
    instance_destroy(_wall,false);
    _player.x=_x;_player.y=_y;_player.xprevious=_xp;_player.yprevious=_yp;
    return _rows;
}

function scrFRPalacePlayerContactTestsPrepare(_state) {
    scrFRWallFixTestsReset(_state.world);
    GameCont.area=area_palace;GameCont.is_level_ended=true;
    var _x=_state.x,_y=_state.y,_vertical=_state.scene>=4;
    // A representative large room makes accidental generic map-wide recovery
    // visible. The production contact path never enumerates these Floors.
    for(var _iy=-20;_iy<20;++_iy) for(var _ix=-20;_ix<20;++_ix)
        instance_create(_x+32*_ix,_y+32*_iy,Floor);
    var _player=_state.player;
    with(_player) {
        x=_x+(_vertical?0:80);y=_y+(_vertical?80:0);
        xprevious=x;yprevious=y;mask_index=mskPlayer;image_xscale=1;image_yscale=1;
        race=Race.Venuz;roll=false;hammerhead=0;hammering=0;
        can_walk=false;can_aim=false;can_spec=false;can_shoot=false;bcan_shoot=false;
        speed=0;friction=0;maxspeed=4*timescale;ntte_player_physics_scale=timescale;
        hp=10000;max_hp=10000;lsthealth=10000;nexthurt=current_frame+100000;
        fr_palace_push_frame=-1000;fr_palace_push_owner=noone;
    }
    _state.wall=noone;_state.stack=noone;
    if(_state.scene==1 || _state.scene==5) {
        for(var _i=-2;_i<=2;++_i) {
            var _wall=instance_create(_x+(_vertical?16*_i:112),_y+(_vertical?112:16*_i),Wall);
            if(_i==0) _state.wall=_wall;
        }
    }
    if(_state.scene==2) _state.stack=scrFRPalacePlayerContactTestsBlock(_x+112,_y,false,180);
    _state.block=scrFRPalacePlayerContactTestsBlock(_x,_y,_state.scene!=3,_vertical?270:0);
    if(_state.scene==0) _state.move_outside_probe=scrFRPalaceMoveOutsideNativeProbe(_player);
    var _block=_state.block,_proxy=_block.mywall;
    _state.row={rate:30/timescale,scene:["open-x","wall-trap-x","stacked","zero-velocity","open-y","wall-trap-y"][_state.scene],
        collision_calls:0,map_wall_calls:0,squeeze_restores:0,probe_calls:0,probe_us:0,
        source_push_displacement:0,source_push_unchanged:true,player_x:0,player_y:0,
        block_x:0,block_y:0,proxy_alive:true,elapsed_ticks:0,
        scheduled_source_steps:0,scheduled_source_pushes:0,source_phase_inner_separated:true,
        end_inner_overlap:false,end_proxy_overlap:false};
    _player.fr_palace_contact_test=_state.row;
    // Exercise the exact event even at zero velocity and in a sandwich. The
    // old handler could repeatedly scan every Floor and delete the proxy.
    var _started=get_timer(),_probe_x=_player.x,_probe_y=_player.y;
    repeat(32) with(_proxy) with(_player) event_perform(ev_collision,Wall);
    _state.row.probe_us=get_timer()-_started;
    _state.row.probe_calls=_state.row.collision_calls;
    assert(_state.row.probe_calls==32 && instance_exists(_proxy)
        && _player.x==_probe_x && _player.y==_probe_y && _state.row.probe_us<2000000,
        "Palace native proxy Collision_Wall did not finish boundedly without map recovery: "+json_stringify(_state.row));
    if(instance_exists(_state.wall)) {
        // Reproduce the second half of a squeeze: the source push crosses a
        // static wall, then the REAL native wall event must restore the clear
        // pre-push point without deleting any scenery or searching Floors.
        with(_player) {
            if(_vertical) y=_state.wall.bbox_top-(bbox_bottom-y)-1;
            else x=_state.wall.bbox_left-(bbox_right-x)-1;
            scrFRPalaceRememberPush(_block);
            if(_vertical) y+=2;else x+=2;
            assert(place_meeting(x,y,_state.wall),"Palace squeeze positive control missed its actual map-wall mask");
        }
        with(_state.wall) with(_player) event_perform(ev_collision,Wall);
        assert(_state.row.squeeze_restores==1 && instance_exists(_state.wall)
            && _player.x==_player.fr_palace_push_x && _player.y==_player.fr_palace_push_y,
            "Palace map-wall squeeze did not restore its exact pre-push position");
    }
    if(_state.scene==0 || _state.scene==4) {
        // The complete original generated source Step is the push oracle.
        // It still owns movement, move_outside_solid(max=6), damage and RNG.
        // Passing its result through the new real native event must leave it
        // byte-for-byte unchanged, in both axes at both host rates.
        with(_player) {
            x=_x;y=_y;
            if(_vertical) y=_block.bbox_bottom-(bbox_top-y)-1;
            else x=_block.bbox_right-(bbox_left-x)-1;
        }
        var _before=_vertical?_player.y:_player.x;
        scrFRInvoke(_block,fr_Objects_Frontier_Palace_mod_gml_crushBlock_step,[]);
        var _after_x=_player.x,_after_y=_player.y,_seed=scrFRSourceRandomGetSeed();
        with(_proxy) with(_player) event_perform(ev_collision,Wall);
        _state.row.source_push_displacement=(_vertical?_after_y:_after_x)-_before;
        _state.row.source_push_unchanged=_player.x==_after_x && _player.y==_after_y
            && scrFRSourceRandomGetSeed()==_seed;
        assert(_state.row.source_push_unchanged && _state.row.source_push_displacement>=6*timescale
            && _state.row.source_push_displacement<=6*timescale+7,
            "Native Palace contact changed the original generated normal push result: "+json_stringify(_state.row));
    }
    _player.x=_x+(_vertical?0:(_state.scene==3?18:80));
    _player.y=_y+(_vertical?80:0);_player.xprevious=_player.x;_player.yprevious=_player.y;
    _player.speed=0;_player.fr_palace_push_frame=-1000;_player.fr_palace_push_owner=noone;
    _state.row.collision_calls=0;_state.row.map_wall_calls=0;_state.row.squeeze_restores=0;
    _block.fr_palace_contact_state=_state;
    _block.fr_palace_contact_source_step=_block.on_step;
    _block.on_step=scrFRPalacePlayerContactTestsSourceStep;
    _state.elapsed=0;_state.phase=2;
    scrFRPalacePlayerContactTestsDrive(_state);
}

function scrFRPalacePlayerContactTestsDrive(_state) {
    // Install normal physical velocity between End Step observations. The
    // native Player Step, engine movement and real collisions remain scheduled.
    with(_state.player) {
        if(_state.scene>=4) vspeed=-2*timescale;
        else hspeed=-2*timescale;
    }
}

function scrFRPalacePlayerContactTestsStep(_driver) {
    var _state=_driver.fr_palace_contacts;
    if(_state.phase==0) {
        save_set_value("options","framerate",_state.rate==0?30:60);
        save_set_value("options","autopause",false);save_set_value("visual","freezeframes",0);
        scrOptionsUpdate();_state.wait=0;_state.phase=1;return false;
    }
    if(_state.phase==1) {
        if(++_state.wait<3) return false;
        assert(timescale==(_state.rate==0?1:0.5),"Palace player fixture did not apply native30/60Hz timing");
        scrFRPalacePlayerContactTestsPrepare(_state);return false;
    }
    _state.elapsed+=timescale;
    assert(instance_exists(_state.block) && instance_exists(_state.block.mywall)
        && (!instance_exists(_state.stack) || instance_exists(_state.stack.mywall)),
        "Scheduled Palace player collision destroyed a moving proxy/body");
    assert(abs(_state.player.x-_state.x)<640 && abs(_state.player.y-_state.y)<640,
        "Scheduled Palace player contact displaced the player across the map");
    if(_state.elapsed<30) {scrFRPalacePlayerContactTestsDrive(_state);return false;}
    var _row=_state.row,_block=_state.block,_player=_state.player;
    _row.player_x=_player.x-_state.x;_row.player_y=_player.y-_state.y;
    _row.block_x=_block.x-_state.x;_row.block_y=_block.y-_state.y;
    _row.elapsed_ticks=_state.elapsed;_row.proxy_alive=instance_exists(_block.mywall);
    // Authored pushes use the predictive inner body (bbox1..30). The solid
    // proxy's bbox0..31 is one pixel wider and synchronizes in End Step, after
    // native Collision. Its outer shell can therefore touch at this sample
    // even though every true source push separated the intended inner masks.
    // Require those real scheduled pushes as well as the exact manual oracle;
    // retain both end-phase mask results instead of treating them as one mask.
    with(_player) {
        _row.end_inner_overlap=place_meeting(x,y,_block);
        _row.end_proxy_overlap=place_meeting(x,y,_block.mywall);
    }
    if(_state.scene==0 || _state.scene==4) {
        assert(_row.source_push_unchanged && _row.scheduled_source_steps>0
            && _row.scheduled_source_pushes>0 && _row.source_phase_inner_separated,
            "Scheduled Palace normal source pushes did not separate their actual inner masks: "+json_stringify(_row));
    }
    if(_state.scene==3) assert(_row.collision_calls>0,
        "Scheduled Palace stationary overlap never reached the actual native collision phase: "+json_stringify(_row));
    if(_state.scene==0) assert(_row.block_x>=168 && _row.player_x>168,
        "Scheduled Palace horizontal push lost the original six-pixel source speed: "+json_stringify(_row));
    if(_state.scene==4) assert(_row.block_y>=168 && _row.player_y>168,
        "Scheduled Palace vertical push lost the original six-pixel source speed: "+json_stringify(_row));
    if(_state.scene==1 || _state.scene==5) assert(instance_exists(_state.wall),"Squeeze deleted a static map wall");
    _player.fr_palace_contact_test=undefined;
    array_push(_state.rows,_row);scrNTTESmokeLog("FRONTIER PALACE PLAYER CONTACT "+json_stringify(_row));
    if(++_state.scene<6) {scrFRPalacePlayerContactTestsPrepare(_state);return false;}
    _state.scene=0;
    if(++_state.rate<2) {_state.phase=0;return false;}
    scrNTTEFullWorldEventsNaturalWorldRestore(_state.world);
    var _file=file_text_open_write("frontier-palace-player-contact.json");
    file_text_write_string(_file,json_stringify({physical_device_tested:false,rows:_state.rows,
        move_outside_native_probe:_state.move_outside_probe}));file_text_close(_file);
    scrNTTESmokeLog("PASS FRONTIER PALACE PLAYER CONTACT bounded native proxy/map-wall events, original normal push, wall traps, stacked bodies and zero velocity at30/60Hz");
    return true;
}
