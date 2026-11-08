// Read raw touch through the shipping JoystickMove event, then invoke the
// original registered Pocket Teleporter callback at both host frame rates.
function scrFRMenuPointer204Query(_box,_mode=0,_slot=undefined) {
    return scrFRModCallArray("mod","libMenu","menubutton_check",
        [_box[0],_box[1],_box[2],_box[3],_mode,0,_slot]);
}

function scrFRMenuPointer204Tests(_slot) {
    var _checks=0,_gx=94,_gy=80,
        _box=[scrFRMouseGuiToWorld(0,_gx)-8,scrFRMouseGuiToWorld(1,_gy)-8,16,16];
    for(var _rate=30;_rate<=60;_rate+=30) {
        var _delta=30/_rate;
        global.time_scale=_delta;global.fr_touch_input=undefined;
        // Model the actual host ordering: input_tick/early raw poll, then
        // UberCont's logical clock advance, then the real libMenu query.
        // At60Hz this short press ends before the next authored UI Step.
        scrFRInputTestsRaw(_gx,_gy,true,true,false,_rate==30,0,4);
        scrFRTouchPoll();current_frame+=_delta;
        if(_rate==60) {
            scrFRInputTestsRaw(_gx,_gy,false,false,true,true,0,4);
            scrFRTouchPoll();current_frame+=_delta;
        }
        assert(scrFRMenuPointer204Query(_box)==_slot,
            "Real libMenu lost a short finger press across early/late native polls at "+string(_rate)+"Hz");
        // All buttons may inspect one source input tick; a second poll must
        // neither consume another finger nor clear the shared press edge.
        scrFRTouchPoll();
        assert(scrFRMenuPointer204Query(_box)==_slot,
            "Same hardware frame re-poll changed libMenu's shared press edge");
        _checks+=2;
        if(_rate==60) {
            scrFRInputTestsRaw(_gx,_gy,false,false,false,false,0,4);
            scrFRTouchPoll();current_frame+=_delta;
        }
        scrFRInputTestsRaw(_gx,_gy,false,false,false,true,0,4);
        scrFRTouchPoll();current_frame+=_delta;
        assert(scrFRMenuPointer204Query(_box)==-1,
            "A consumed short touch replayed on a later authored UI Step");
        _checks++;
        // A finger already held before a future button exists may hover it,
        // but must never become a fresh click when that button starts ticking.
        global.fr_touch_input=undefined;
        scrFRInputTestsRaw(_gx,_gy,true,true,false,true,0,4);
        scrFRTouchPoll();current_frame+=_delta;
        for(var _host=0;_host<4;++_host) {
            var _ready=_rate==30 || (_host mod 2)==1;
            scrFRInputTestsRaw(_gx,_gy,true,false,false,_ready,0,4);
            scrFRTouchPoll();current_frame+=_delta;
            if(!_ready) continue;
            assert(scrFRMenuPointer204Query(_box)==-1 && scrFRMenuPointer204Query(_box,2)==_slot,
                "An old held finger synthesized a click when a later source UI appeared");
            _checks++;
        }
        scrFRInputTestsRaw(_gx,_gy,false,false,true,true,0,4);
        scrFRTouchPoll();current_frame+=_delta;
        scrFRInputTestsRaw(_gx,_gy,true,true,false,true,0,4);
        scrFRTouchPoll();current_frame+=_delta;
        var _outside=[_box[0]+500,_box[1]+500,16,16];
        assert(scrFRMenuPointer204Query(_outside)==-1
            && scrFRMenuPointer204Query(_box,0,(_slot+1) mod INPUT_MAX_PLAYERS)==-1
            && scrFRMenuPointer204Query(_box)==_slot && scrFRMenuPointer204Query(_box,1)==_slot,
            "Stable hardware pointer leaked outside its real hit box/local slot or lost its held state");
        _checks++;
        scrFRInputTestsRaw(_gx,_gy,true,false,false,true,0,4);
        scrFRTouchPoll();current_frame+=_delta;
        assert(scrFRMenuPointer204Query(_box)==-1 && scrFRMenuPointer204Query(_box,1)==_slot,
            "Holding a real finger repeated its click instead of only its hold state");
        scrFRInputTestsRaw(_gx,_gy,false,false,true,true,0,4);
        scrFRTouchPoll();current_frame+=_delta;
        assert(scrFRMenuPointer204Query(_box)==-1 && scrFRMenuPointer204Query(_box,1)==-1,
            "Released real finger retained a click or held state");
        _checks+=2;
    }
    scrNTTESmokeLog("PASS FRONTIER INPUT204 real libMenu30/60Hz short press, same-host early/late polls, once-only later source ticks, stale pre-button hold, local hitbox/slot and release: "+string(_checks));
    return _checks;
}

function scrFRInput204Tests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled(),"Input204 fixture requires explicit desktop smoke mode");
    var _before=scrNTTEFullInstances(all),_p=instance_find(Player,0),_slot=global.index,
        _players=scrNTTEFullAreaGeneratorSnapshot(Player),_keys={nodes:[]},
        _keyboard=UberCont.opt_keyboard,_gamepad=UberCont.opt_gamepad,_console=global.console_active,
        _frame=current_frame,_input_frame=global.__input_frame,_scale=timescale,_serial=FRWorld.logic_serial,_tick=FRWorld.logic_tick,
        _render=global.fr_render_context,_pads=global.__input_gamepads,
        _saved_input=variable_global_exists("fr_touch_input")?global.fr_touch_input:undefined,
        _saved_fixture=variable_global_exists("fr_touch_input_fixture")?global.fr_touch_input_fixture:undefined,
        _saved_pocket=variable_global_exists("fr_pocket_input204")?global.fr_pocket_input204:undefined,
        _skill=scrFRSkillResolve("AugmentExtraFeet"),_amount=scrFRGetSkill(_skill),
        _stick=noone,_checks=0;
    scrNTTEFullAreaSnapshotContainer(KeyCont,_keys);
    try {
        assert(instance_exists(_p),"Input204 fixture requires native player");
        global.index=_p.index;UberCont.opt_keyboard=false;UberCont.opt_gamepad=false;global.console_active=false;
        KeyCont.touch[_p.index]=true;KeyCont.gamepad[_p.index]=false;
        global.fr_render_context=false;scrFRSetSkill(_skill,1);
        _stick=instance_create(160,164,JoystickMove);_stick.rad=36;
        _checks+=scrFRMenuPointer204Tests(_p.index);
        for(var _hz=30;_hz<=60;_hz+=30) for(var _d=0;_d<4;++_d) {
            var _angles=[23,106,238,338],_angle=_angles[_d],_delta=30/_hz;
            global.time_scale=_delta;current_frame=19000;global.fr_touch_input=undefined;
            _p.x=191000;_p.y=191000;_p.can_walk=true;_p.speed=0;
            _p.mask_index=mskPlayer;_p.image_xscale=1;_p.image_yscale=1;
            with(_p) scrFRModCallArray("skill","AugmentExtraFeet","skill_take",[]);
            _stick.index=-1;_stick.current_move_direction_time=0;
            KeyCont.moving[_p.index]=0;
            var _sx=_p.x,_sy=_p.y,
                _tx=_stick.x+lengthdir_x(24,_angle),_ty=_stick.y+lengthdir_y(24,_angle);
            scrFRInputTestsRaw(_tx,_ty,true,true,false,_hz==30,_delta);
            with(_stick) event_user(0);
            if(_hz==30) scrFRInputTestsSourceDash(_p);
            scrFRInputTestsRaw(_tx,_ty,false,false,true,true,_delta);
            with(_stick) event_user(0);scrFRInputTestsSourceDash(_p);
            assert(_p.x==_sx && _p.y==_sy,"A single short analogue tap triggered Pocket Teleporter");
            // A small angle change between real touches must not lose the
            // second tap, and the dash must keep its precise new angle.
            _angle+=5;_tx=_stick.x+lengthdir_x(24,_angle);_ty=_stick.y+lengthdir_y(24,_angle);
            scrFRInputTestsRaw(_tx,_ty,true,true,false,true,_delta);
            with(_stick) event_user(0);scrFRInputTestsSourceDash(_p);
            // Runner instance positions use float32 precision. At this remote
            // isolated coordinate their ULP is 1/64 px; check the endpoints
            // within that rounding budget as well as exact dash metadata.
            scrNTTESmokeLog("FRONTIER INPUT204 ANGLE "+json_stringify({rate:_hz,angle:_angle,
                actual:_p.fr_dashaugment_angle,length:_p.fr_dashaugment_length,
                distance:point_distance(_sx,_sy,_p.x,_p.y),x:_p.x-_sx,y:_p.y-_sy}));
            assert(abs(angle_difference(_p.fr_dashaugment_angle,_angle))<0.001
                && _p.fr_dashaugment_length==50
                && abs(_p.x-(_sx+lengthdir_x(50,_angle)))<=1/64
                && abs(_p.y-(_sy+lengthdir_y(50,_angle)))<=1/64,
                "Pocket Teleporter quantized/lost actual analogue double tap at "+string(_hz)+" Hz angle "+string(_angle));
            var _landx=_p.x,_landy=_p.y;
            // Moving across an axis while still holding the stick must not
            // count as a fresh tap or trigger a second teleport.
            scrFRInputTestsRaw(_stick.x+24,_stick.y,true,false,false,true,_delta);
            with(_stick) event_user(0);scrFRInputTestsSourceDash(_p);
            assert(_p.x==_landx && _p.y==_landy,"Held analogue stick repeated Pocket Teleporter");
            _checks+=3;
        }
        // Real native collision masks stop an arbitrary-angle dash before
        // the player's body overlaps a thin corner or packed solid block.
        _p.x=191000;_p.y=191000;
        var _wall=instance_create(_p.x+32,_p.y-8,Wall),_distance=0;
        with(_p) {
            _distance=scrFRPocketTeleporterDistance204(50,0);
            assert(_distance<50 && !place_meeting(x+_distance,y,Wall)
                && place_meeting(x+_distance+1,y,Wall),"Pocket Teleporter mask sweep did not stop at native wall contact");
        }
        instance_destroy(_wall,false);
        _wall=scrNTTESolidWallBlock(_p.x+24,_p.y-48,48,48);
        with(_p) {
            _distance=scrFRPocketTeleporterDistance204(50,37);
            assert(_distance<50 && !place_meeting(x+lengthdir_x(_distance,37),y+lengthdir_y(_distance,37),Wall),
                "Continuous Pocket Teleporter crossed a packed wall corner");
        }
        _checks+=2;
        // Use a nonzero device while global.index deliberately names a
        // different slot: left/right sticks, D-pad and releases must agree.
        var _test_slot=1,_pad={kh:0.8,kv:0.4,rh:-0.6,rv:-0.2,button:-1,
            get_value:function(_axis) {switch(_axis) {case gp_axislh:return kh;case gp_axislv:return kv;case gp_axisrh:return rh;case gp_axisrv:return rv;}return 0;},
            get_held:function(_key){return _key==button;},get_pressed:function(_key){return _key==button;},get_released:function(_key){return false;}};
        global.__input_gamepads=array_create(6,undefined);global.__input_gamepads[_test_slot]=_pad;
        global.index=0;UberCont.opt_gamepad=true;KeyCont.touch[_test_slot]=false;KeyCont.gamepad[_test_slot]=true;
        KeyCont.hold_east[_test_slot]=false;KeyCont.hold_west[_test_slot]=false;
        KeyCont.hold_nort[_test_slot]=false;KeyCont.hold_sout[_test_slot]=false;
        scrSetGamepadInputs(_test_slot);
        assert(KeyCont.hold_east[_test_slot] && KeyCont.hold_sout[_test_slot]
            && abs(angle_difference(KeyCont.dir_move[_test_slot],point_direction(0,0,0.8,0.4)))<0.001
            && abs(angle_difference(KeyCont.dir_fire[_test_slot],point_direction(0,0,-0.6,-0.2)))<0.001,
            "Controller movement/aim ignored explicitly selected nonzero device");
        _pad.kh=-0.8;_pad.kv=-0.4;scrSetGamepadInputs(_test_slot);
        assert(KeyCont.release_east[_test_slot] && KeyCont.release_sout[_test_slot]
            && KeyCont.press_west[_test_slot] && KeyCont.press_nort[_test_slot]
            && !KeyCont.hold_east[_test_slot] && !KeyCont.hold_sout[_test_slot],
            "Direct controller reversal retained opposite held directions");
        _pad.kh=0.01;_pad.kv=-0.01;_pad.button=gp_padr;scrSetGamepadInputs(_test_slot);
        assert(KeyCont.moving[_test_slot] && KeyCont.dir_move[_test_slot]==0,"Controller D-pad did not work with neutral stick drift");
        _pad.button=-1;scrSetGamepadInputs(_test_slot);
        assert(!KeyCont.moving[_test_slot] && KeyCont.release_east[_test_slot],"Controller neutral retained movement");
        global.index=_test_slot;_pad.button=gp_stickr;
        assert(scrGamepadAnykey()==gp_stickr,"Right stick remapping still reads keyboard instead of selected controller");
        _pad.button=gp_face1;
        assert(scrFRButtonPressed(_test_slot,"okay"),"Frontier confirm missed selected controller");
        var _map=scrFRGamepadMap204([false,false,false,false,false,true],[],4);
        assert(_map[0]==5 && _map[1]==-1,"Controller discovery ignored nonzero hardware slot");
        _map=scrFRGamepadMap204([false,true,false,false,false,true],_map,4);
        assert(_map[0]==5 && _map[1]==1,"Hot-plug changed existing controller or shared device between players");
        _map=scrFRGamepadMap204([false,true,false,false,false,false],_map,4);
        assert(_map[0]==-1 && _map[1]==1,"Disconnect retained missing device or stole another player's controller");
        _checks+=9;
        scrNTTESmokeLog("PASS FRONTIER INPUT204 continuous 28/111/243/343deg actual touch double taps 30/60Hz, short taps/held drift, native+packed wall mask, nonzero controller/reversal/D-pad/right-stick/confirm/hot-plug: "+string(_checks)+"; physical Android/iOS controller untested");
    } finally {
        scrFRSetSkill(_skill,_amount);scrNTTEFullMergedRuntimeTestCleanup(_before);
        scrNTTEFullAreaGeneratorRestore(_players);
        scrNTTEFullAreaGeneratorRestore({instances:[],containers:_keys.nodes});
        UberCont.opt_keyboard=_keyboard;UberCont.opt_gamepad=_gamepad;global.console_active=_console;
        global.index=_slot;current_frame=_frame;global.__input_frame=_input_frame;global.time_scale=_scale;
        FRWorld.logic_serial=_serial;FRWorld.logic_tick=_tick;global.fr_render_context=_render;
        global.__input_gamepads=_pads;global.fr_touch_input=_saved_input;global.fr_touch_input_fixture=_saved_fixture;
        global.fr_pocket_input204=_saved_pocket;
    }
}
