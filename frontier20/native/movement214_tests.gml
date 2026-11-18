// Hardware fixtures enter the shipping JoystickMove user event, not a stand-in
// movement function. The ordinary Player precise-movement consumer is unchanged.
function scrFRMovement214Sample(_stick,_x,_y,_held,_pressed,_released,_ready,_delta,_touch=0) {
    scrFRInputTestsRaw(_x,_y,_held,_pressed,_released,_ready,_delta,_touch);
    with(_stick) event_user(0);
}

function scrFRMovement214Tests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled(),"Movement214 raw fixture requires explicit desktop smoke mode");
    var _before=scrNTTEFullInstances(all),_keys={nodes:[]},_slot=global.index,
        _keyboard=UberCont.opt_keyboard,_gamepad=UberCont.opt_gamepad,
        _hidden=UberCont.opt_hiddensticks,_console=global.console_active,
        _frame=current_frame,_input_frame=global.__input_frame,_scale=timescale,_epsilon=math_get_epsilon(),
        _serial=FRWorld.logic_serial,_tick=FRWorld.logic_tick,
        _saved_input=variable_global_exists("fr_touch_input")?global.fr_touch_input:undefined,
        _saved_fixture=variable_global_exists("fr_touch_input_fixture")?global.fr_touch_input_fixture:undefined,
        _parked=scrNTTEFullInstances(MobileUI),_stick=noone,_attack=noone,_checks=0,_ramp=[];
    scrNTTEFullAreaSnapshotContainer(KeyCont,_keys);
    for(var _i=0;_i<array_length(_parked);++_i) instance_deactivate_object(_parked[_i]);
    try {
        // The engine's default comparison epsilon exceeds the numeric test
        // tolerance. Restrict exact comparisons to this synchronous fixture.
        math_set_epsilon(0);
        UberCont.opt_keyboard=false;UberCont.opt_gamepad=false;UberCont.opt_hiddensticks=true;
        global.console_active=false;KeyCont.touch[_slot]=true;
        _stick=instance_create(160,164,JoystickMove);_stick.x=160;_stick.y=164;_stick.rad=36;
        _attack=instance_create(280,164,JoystickAttack);_attack.x=280;_attack.y=164;_attack.rad=36;
        _attack.index=-1;
        for(var _hz=30;_hz<=60;_hz+=30) {
            var _dt=30/_hz;
            global.time_scale=_dt;global.fr_touch_input=undefined;current_frame=28000;
            _stick.index=-1;_stick.current_move_direction_time=30;
            scrFRMovement214Sample(_stick,161.5,164,true,true,false,true,_dt);
            assert(_stick.index==0 && KeyCont.moving[_slot]==0
                && _stick.current_move_direction_time==0 && !KeyCont.hold_east[_slot]
                && !KeyCont.hold_west[_slot] && !KeyCont.hold_nort[_slot] && !KeyCont.hold_sout[_slot],
                "Sub2px center input retained boost/movement at "+string(_hz)+"Hz");
            scrFRMovement214Sample(_stick,163,164,true,false,false,true,_dt);
            scrNTTESmokeLog("FRONTIER214 MOVE FINE DIAG "+json_stringify({rate:_hz,delta:timescale,
                expected:3/36,moving:KeyCont.moving[_slot],east:KeyCont.hold_east[_slot],
                west:KeyCont.hold_west[_slot],north:KeyCont.hold_nort[_slot],south:KeyCont.hold_sout[_slot],
                slot:_slot,stick_index:_stick.index,x:_stick.x,y:_stick.y,rad:_stick.rad,dis:_stick.dis,
                ramp:_stick.current_move_direction_time,held:scrFRTouchHeld(0),
                touch_x:scrFRTouchX(0),touch_y:scrFRTouchY(0)}));
            assert(abs(KeyCont.moving[_slot]-3/36)<0.000001
                && KeyCont.hold_east[_slot] && !KeyCont.hold_nort[_slot] && !KeyCont.hold_sout[_slot],
                "Fine3px movement was lost or remapped outside the2px deadzone");
            _checks+=2;

            // Real touch angles remain continuous. A full diagonal and a full
            // cardinal input both have unit magnitude, with no sqrt2 speed-up.
            var _angles=[0,90,180,270,45,135,225,315,23];
            for(var _a=0;_a<array_length(_angles);++_a) {
                var _angle=_angles[_a];_stick.current_move_direction_time=0;
                scrFRMovement214Sample(_stick,160+lengthdir_x(36,_angle),164+lengthdir_y(36,_angle),
                    true,false,false,true,_dt);
                assert(abs(KeyCont.moving[_slot]-1)<0.000001
                    && abs(angle_difference(KeyCont.dir_move[_slot],_angle))<0.0001,
                    "Move stick changed analog angle or diagonal magnitude");
                if(_a<4) {
                    var _held=KeyCont.hold_east[_slot]+KeyCont.hold_nort[_slot]
                        +KeyCont.hold_west[_slot]+KeyCont.hold_sout[_slot];
                    assert(_held==1,"Cardinal movement gained a perpendicular direction edge");
                }
                _checks++;
            }

            // Both a normal release and a missing release edge (OS touch
            // cancellation/app backgrounding) stop acceleration in this frame.
            for(var _cancel=0;_cancel<2;++_cancel) {
                _stick.index=-1;_stick.current_move_direction_time=0;
                scrFRMovement214Sample(_stick,184,164,true,true,false,true,_dt);
                assert(KeyCont.moving[_slot]>0 && KeyCont.hold_east[_slot],"Move pointer was not captured");
                scrFRMovement214Sample(_stick,184,164,false,false,_cancel==0,true,_dt);
                assert(_stick.index==-1 && KeyCont.moving[_slot]==0
                    && !KeyCont.hold_east[_slot] && scrFRButtonReleased(_slot,"east")
                    && _stick.current_move_direction_time==0,
                    "Released/lost pointer retained a positive Player moving value");
                scrFRMovement214Sample(_stick,184,164,false,false,false,true,_dt);
                assert(KeyCont.moving[_slot]==0 && !scrFRButtonReleased(_slot,"east"),
                    "A lost pointer replayed its release or stale movement");
                _checks+=3;
            }

            // The captured move finger may leave its acquisition circle; a
            // second finger (including an attack finger) must not redirect it.
            _stick.index=-1;_stick.current_move_direction_time=0;
            scrFRMovement214Sample(_stick,184,164,true,true,false,true,_dt);
            _attack.index=1;
            scrFRInputTestsRaw(304,164,true,false,false,true,_dt);
            var _samples=global.fr_touch_input_fixture.samples;
            _samples[1]={x:160,y:140,held:true,pressed:true,released:false};
            global.fr_touch_input_fixture.samples=_samples;
            with(_stick) event_user(0);
            assert(_stick.index==0 && KeyCont.dir_move[_slot]==0 && KeyCont.moving[_slot]==1
                && _attack.index==1,"Second finger stole/reoriented a live out-of-range move pointer");
            scrFRInputTestsRaw(304,164,false,false,true,true,_dt);
            _samples=global.fr_touch_input_fixture.samples;
            _samples[1]={x:160,y:140,held:true,pressed:false,released:false};
            global.fr_touch_input_fixture.samples=_samples;
            with(_stick) event_user(0);
            assert(_stick.index==-1 && KeyCont.moving[_slot]==0 && _attack.index==1,
                "Move release switched directly into another held finger");
            scrFRInputTestsRaw(160,140,true,false,false,true,_dt,1);
            with(_stick) event_user(0);
            assert(_stick.index==-1 && KeyCont.moving[_slot]==0,
                "Move selector captured the pointer already owned by attack UI");
            _attack.index=-1;_checks+=3;

            // A tap nearest another control is not a move tap even when it
            // falls inside the larger move acquisition radius.
            scrFRMovement214Sample(_stick,238,164,true,true,false,true,_dt,2);
            assert(_stick.index==-1 && KeyCont.moving[_slot]==0,"Move selector ignored nearest-control ownership");
            _checks++;

            // The authored acceleration ramp is still present, but advances in
            //30Hz logical units equally at30/60Hz and cannot become negative.
            _stick.index=-1;_stick.current_move_direction_time=0;_stick.image_alpha=0;
            KeyCont.dir_move[_slot]=0;
            for(var _f=0;_f<_hz/2;++_f)
                scrFRMovement214Sample(_stick,163,164,true,_f==0,false,
                    _hz==30 || (_f mod 2)==1,_dt);
            array_push(_ramp,[_stick.current_move_direction_time,KeyCont.moving[_slot],_stick.image_alpha]);
            assert(abs(_stick.current_move_direction_time-15)<0.000001
                && abs(KeyCont.moving[_slot]-(0.25+3/36))<0.000001,
                "Move ramp depends on hardware frame rate");
            _stick.current_move_direction_time=0.5;
            scrFRMovement214Sample(_stick,157,164,true,false,false,true,_dt);
            assert(_stick.current_move_direction_time==0 && KeyCont.hold_west[_slot],
                "Turn decay made the move ramp negative or delayed the direction");
            scrFRMovement214Sample(_stick,160,164,true,false,false,true,_dt);
            assert(KeyCont.moving[_slot]==0 && _stick.current_move_direction_time==0,
                "Centering a held stick retained time-based drift");
            _checks+=3;

            scrFRMovement214Sample(_stick,184,164,true,false,false,true,_dt);
            global.console_active=true;
            scrFRMovement214Sample(_stick,184,164,true,false,false,true,_dt);
            assert(_stick.index==-1 && KeyCont.moving[_slot]==0,"Console retained an active touch move pointer");
            global.console_active=false;_checks++;
        }
        assert(abs(_ramp[0][0]-_ramp[1][0])<0.000001
            && abs(_ramp[0][1]-_ramp[1][1])<0.000001
            && abs(_ramp[0][2]-_ramp[1][2])<0.000001,
            "Equal-time30/60Hz stick acceleration or visibility differs");
        scrNTTESmokeLog("FRONTIER214 MOVEMENT RESULTS "+json_stringify({rates:[30,60],
            ramp:_ramp,checks:_checks+1,deadzone_gui_px:2,fine_move_gui_px:3,
            fixture:"Windows raw touch through JoystickMove"}));
        scrNTTESmokeLog("PASS FRONTIER MOVEMENT214 actual JoystickMove30/60Hz raw pointer center/fine/cardinal/diagonal, release/lost-background touch, ownership/multitouch, range, console, equal-time ramp: "+string(_checks+1));
    } finally {
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        for(var _i=0;_i<array_length(_parked);++_i) instance_activate_object(_parked[_i]);
        scrNTTEFullAreaGeneratorRestore({instances:[],containers:_keys.nodes});
        UberCont.opt_keyboard=_keyboard;UberCont.opt_gamepad=_gamepad;UberCont.opt_hiddensticks=_hidden;
        global.index=_slot;global.console_active=_console;
        current_frame=_frame;global.__input_frame=_input_frame;global.time_scale=_scale;
        FRWorld.logic_serial=_serial;FRWorld.logic_tick=_tick;
        global.fr_touch_input=_saved_input;global.fr_touch_input_fixture=_saved_fixture;
        math_set_epsilon(_epsilon);
    }
}
