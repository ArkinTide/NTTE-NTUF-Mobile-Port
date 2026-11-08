// Source menus sample each native hardware frame once, then share that edge
// with every authored menu query on the corresponding source logic tick.
function scrFRMenuTouchPoll204() {
    if(!scrFREnabled() || !KeyCont.touch[global.index]) return;
    var _state=scrFRTouchInputState().pointer,_host=global.__input_frame;
    // UberCont samples inputs before it advances current_frame. A later
    // authored menu query runs after that advance in the same hardware frame.
    // Resampling there used to clear an off-tick short press on its release.
    if((_state[$ "host_frame204"]??-1)==_host) return;
    if(_state.ready) _state.pending=array_create(5,undefined);
    for(var _i=0;_i<5;++_i) {
        var _sample={x:scrFRTouchX(_i),y:scrFRTouchY(_i),held:scrFRTouchHeld(_i)};
        _state.samples[_i]=_sample;
        if(scrFRTouchPressed(_i)) _state.pending[_i]=_sample;
    }
    _state.frame=current_frame;_state.ready=scrFRReadyTick();_state.host_frame204=_host;
}

// Pocket Teleporter consumes raw movement starts, not quantized direction
// buttons. Keep short taps until the next authored 30 Hz skill callback.
function scrFRPocketTeleporterInput204(_index) {
    var _world=instance_exists(FRWorld)?FRWorld.id:noone;
    if(!variable_global_exists("fr_pocket_input204") || !is_struct(global.fr_pocket_input204)
       || global.fr_pocket_input204.world!=_world)
        global.fr_pocket_input204={world:_world,slots:array_create(INPUT_MAX_PLAYERS,undefined)};
    var _state=global.fr_pocket_input204.slots[_index];
    if(is_undefined(_state)) {
        _state={frame:-1,down:false,angle:0,mode:-1,pending:[],last:-1000000,
            last_angle:0,dash_angle:undefined};
        global.fr_pocket_input204.slots[_index]=_state;
    }
    return _state;
}

function scrFRPocketTeleporterReset204() {
    global.fr_pocket_input204=undefined;
}

function scrFRPocketTeleporterSample204(_index) {
    if(!scrFREnabled() || _index<0 || _index>=INPUT_MAX_PLAYERS) return;
    var _state=scrFRPocketTeleporterInput204(_index);
    if(_state.frame==current_frame) return;
    _state.frame=current_frame;
    var _mode=KeyCont.touch[_index]?0:(KeyCont.gamepad[_index]?1:2),
        _active=KeyCont.moving[_index]>0 && (KeyCont.hold_east[_index] || KeyCont.hold_west[_index]
            || KeyCont.hold_nort[_index] || KeyCont.hold_sout[_index]),
        _angle=KeyCont.dir_move[_index],_fresh=_active && !_state.down;
    if(_state.mode!=_mode) {_state.down=false;_state.last=-1000000;_state.pending=[];_fresh=_active;}
    if(_mode==2) _fresh=_active && (KeyCont.press_east[_index] || KeyCont.press_west[_index]
        || KeyCont.press_nort[_index] || KeyCont.press_sout[_index]);
    // A direct stick reversal is a new direction; small analogue drift and
    // crossing a cardinal axis while holding the stick are not repeated taps.
    else if(_active && _state.down && abs(angle_difference(_angle,_state.angle))>100) _fresh=true;
    if(_fresh) {
        array_push(_state.pending,{frame:current_frame,angle:_angle});
        if(array_length(_state.pending)>8) array_delete(_state.pending,0,1);
    }
    _state.down=_active;_state.angle=_angle;_state.mode=_mode;
}

function scrFRPocketTeleporterStep204() {
    with(Player) {
        if(!variable_instance_exists(id,"fr_dashaugment_cooldown")) {
            fr_dashaugment_cooldown=0;fr_dashaugment_swapcooldown=0;
        }
        var _state=scrFRPocketTeleporterInput204(index),_pending=_state.pending;
        _state.pending=[];
        if(!can_walk) {_state.last=-1000000;continue;}
        for(var _i=0;_i<array_length(_pending);++_i) {
            var _tap=_pending[_i];
            if(_tap.frame<current_frame-7) continue;
            if(fr_dashaugment_cooldown<=0 && _tap.frame-_state.last<=7
               && _tap.frame>_state.last && abs(angle_difference(_tap.angle,_state.last_angle))<=60) {
                _state.dash_angle=_tap.angle;
                scrFRModCallArray("skill","AugmentExtraFeet","dash",[]);
                _state.dash_angle=undefined;_state.last=-1000000;
                fr_dashaugment_swapcooldown=current_frame+7;
            } else {_state.last=_tap.frame;_state.last_angle=_tap.angle;}
        }
        if(fr_dashaugment_cooldown>0) {
            speed+=timescale;
            scrFRModCallArray("skill","AugmentExtraFeet","after_image",[]);
            fr_dashaugment_cooldown-=scrFRSourceScale();
        }
    }
}

function scrFRPocketTeleporterAngle204(_index) {
    var _state=scrFRPocketTeleporterInput204(_index);
    return is_undefined(_state.dash_angle)?KeyCont.dir_move[_index]:_state.dash_angle;
}

function scrFRPocketTeleporterDistance204(_maximum,_angle) {
    // Sweep the player's entire collision mask in one-pixel increments. A
    // centre ray plus fixed back-off fails at arbitrary angles and wall seams.
    var _distance=0;
    for(var _step=1;_step<=max(0,_maximum);++_step) {
        var _x=x+lengthdir_x(_step,_angle),_y=y+lengthdir_y(_step,_angle);
        if(scrFRPlaceMeeting(_x,_y,Wall) || scrFRPlaceMeeting(_x,_y,InvisiWall)) break;
        _distance=_step;
    }
    return _distance;
}

// Android can expose a controller outside slot zero. Keep existing device
// assignments stable, give each logical player a distinct connected device,
// and release a disconnected slot before choosing its replacement.
function scrFRGamepadMap204(_available,_previous,_maximum) {
    var _map=array_create(_maximum,-1),_used=array_create(array_length(_available),false);
    for(var _i=0;_i<_maximum;++_i) {
        var _old=_i<array_length(_previous)?_previous[_i]:-1;
        if(_old>=0 && _old<array_length(_available) && _available[_old] && !_used[_old]) {
            _map[_i]=_old;_used[_old]=true;
        }
    }
    for(var _i=0;_i<_maximum;++_i) if(_map[_i]<0)
        for(var _d=0;_d<array_length(_available);++_d) if(_available[_d] && !_used[_d]) {
            _map[_i]=_d;_used[_d]=true;break;
        }
    return _map;
}

function scrFRGamepadDevice204(_logical) {
    if(!is_real(_logical) || _logical<0 || floor(_logical)!=_logical) return -1;
    if(os_type!=os_android) return _logical;
    if(_logical>=INPUT_MAX_PLAYERS) return -1;
    var _frame=global.__input_frame;
    if(!variable_global_exists("fr_gamepad_poll204") || global.fr_gamepad_poll204!=_frame) {
        var _count=gamepad_get_device_count(),_available=array_create(_count,false),
            _previous=variable_global_exists("fr_gamepad_map204")?global.fr_gamepad_map204:[];
        for(var _i=0;_i<_count;++_i) _available[_i]=gamepad_is_connected(_i) && gamepad_button_count(_i)>0;
        global.fr_gamepad_map204=scrFRGamepadMap204(_available,_previous,INPUT_MAX_PLAYERS);
        global.fr_gamepad_poll204=_frame;
    }
    return global.fr_gamepad_map204[_logical];
}

function scrFRGamepadAvailability204(_index) {
    if(os_type!=os_android || _index!=global.index) return;
    if(scrNTTEGamepadDeviceIndex(_index)<0) UberCont.opt_gamepad=false;
    else if(!UberCont.opt_gamepad && scrNTTEGamepadButton(gp_start,keystate_press,_index)) UberCont.opt_gamepad=true;
}

function scrFRGamepadInputs204(_index) {
    var _kh=scrNTTEGamepadAxis(gp_axislh,_index),_kv=scrNTTEGamepadAxis(gp_axislv,_index),
        _keys=["east","west","nort","sout"],
        _down=[_kh>0.15 || scrNTTEGamepadButton(gp_padr,keystate_hold,_index),
            _kh< -0.15 || scrNTTEGamepadButton(gp_padl,keystate_hold,_index),
            _kv< -0.15 || scrNTTEGamepadButton(gp_padu,keystate_hold,_index),
            _kv>0.15 || scrNTTEGamepadButton(gp_padd,keystate_hold,_index)];
    for(var _i=0;_i<4;++_i) {
        var _held=KeyCont[$ "hold_"+_keys[_i]],_press=KeyCont[$ "press_"+_keys[_i]],
            _release=KeyCont[$ "release_"+_keys[_i]],_old=_held[_index];
        _held[_index]=_down[_i];_press[_index]=_down[_i] && !_old;_release[_index]=!_down[_i] && _old;
    }
    if(abs(_kh)<=0.15) _kh=0;
    if(abs(_kv)<=0.15) _kv=0;
    if(_kh==0 && _kv==0) {_kh=_down[0]-_down[1];_kv=_down[3]-_down[2];}
    KeyCont.moving[_index]=_kh!=0 || _kv!=0;
    if(KeyCont.moving[_index]) KeyCont.dir_move[_index]=point_direction(0,0,_kh,_kv);
    _kh=scrNTTEGamepadAxis(gp_axisrh,_index);_kv=scrNTTEGamepadAxis(gp_axisrv,_index);
    if(abs(_kh)>0.15 || abs(_kv)>0.15) {
        KeyCont.dir_fire[_index]=point_direction(0,0,_kh,_kv);
        KeyCont.dis_fire[_index]=point_distance(0,0,_kh,_kv)*min(view_width,view_height)*0.4;
    }
}
