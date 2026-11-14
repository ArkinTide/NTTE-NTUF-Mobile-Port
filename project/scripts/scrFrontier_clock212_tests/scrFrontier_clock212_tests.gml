// Windows smoke-only diagnostics. Production clocks never read fixture data.
function scrFRClock212TestsNear(_a,_b,_what) {
    assert(abs(_a-_b)<=.0001,_what+" expected "+string(_b)+" actual "+string(_a));
}

function scrFRClock212WallBounceTests() {
    scrFRClockApply212(30);
    var _wall=instance_create(510000,510000,Wall),_player=instance_find(Player,0),
        _native=instance_create(510000,510000,Bullet2),_custom=noone,
        _red=instance_create(510000,510000,NTTEFullRedBullet),
        _venom=instance_create(510000,510000,NTTEVenomPellet),
        _shell=instance_create(510000,510000,NTTEFullCustomShell),_rows=[];
    with(_player) _custom=scrFRModCall("mod","Frontier_Projectiles2","CreepShell_create",510000,510000,false);
    assert(instance_exists(_custom) && _custom.object_index==FRCustomProjectile
        && !is_undefined(_custom.on_wall),"Clock bounce fixture missed the real NTUF CreepShell factory");
    _native.wallbounce=5;_custom.wallbounce=4;_red.wallbounce=7;_venom.wallbounce=4;_shell.wallbounce=4;
    var _shots=[_native,_custom,_red,_venom,_shell],_bounce=[5,4,7,4,4];
    for(var _round=0;_round<4;++_round) {
        for(var _i=0;_i<array_length(_shots);++_i) with(_shots[_i]) {
            x=_wall.x-4;y=_wall.y+8;xprevious=x;yprevious=y;direction=0;speed=6*timescale;
        }
        var _rate=(_round mod 2)==0?60:30;
        scrFRClockApply212(_rate);
        scrFRClock212TestsNear(_native.wallbounce,_bounce[0]*timescale,"Native physical bounce across rate switch");
        for(var _i=1;_i<array_length(_shots);++_i)
            scrFRClock212TestsNear(_shots[_i].wallbounce,_bounce[_i],"Source logical bounce across rate switch");
        // Dispatch each actual native Collision_Wall event. The FR event
        // reaches its authored CreepShell callback through scrFRActorCallback.
        for(var _i=0;_i<array_length(_shots);++_i) {
            with(_wall) with(_shots[_i]) event_perform(ev_collision,Wall);
            assert(instance_exists(_shots[_i]),"Rate switch destroyed a surviving bounce projectile");
            scrFRClock212TestsNear(_shots[_i].speed,
                min(6*.8+_bounce[_i],16)*timescale,"Actual wall callback's physical output");
            _bounce[_i]*=.95;
            scrFRClock212TestsNear(_shots[_i].wallbounce,
                _bounce[_i]*(_i==0?timescale:1),"Actual wall callback's bounce decay");
        }
        array_push(_rows,{rate:_rate,scale:timescale,native_field:_native.wallbounce,
            native_logical:_native.wallbounce/timescale,native_speed:_native.speed/timescale,
            ntuf_field:_custom.wallbounce,ntuf_speed:_custom.speed/timescale,
            red_field:_red.wallbounce,red_speed:_red.speed/timescale,
            venom_field:_venom.wallbounce,venom_speed:_venom.speed/timescale,
            shell_field:_shell.wallbounce,shell_speed:_shell.speed/timescale});
    }
    scrNTTESmokeLog("PASS NTUF212 native physical and NTUF/Red/Venom/CustomShell logical wall-bounce fields and actual collision callbacks across60->30->60->30");
    return _rows;
}

function scrFRClock212Tests() {
    var _before=scrNTTEFullInstances(all),_driver=instance_find(FRIntegrationTest,0),
        _old_rate=game_get_speed(gamespeed_fps),_old_cap=UberCont.opt_framerate,
        _old_auto=UberCont.opt_ntte_autoframerate,_old_save=UberCont.saveData[? "visual_ntte_autoframerate"],
        _old_opt=save_get_value("options","framerate",60),_old_keyboard=UberCont.opt_keyboard,
        _old_gamepad=UberCont.opt_gamepad,_budget=variable_instance_get(instance_find(UberCont,0),"fr_clock_budget212"),
        _old_paused=UberCont.paused,_old_want=UberCont.want_pause,_old_quit=UberCont.quit_pause,
        _draw=scrNTTEFullCoastDrawState(),_font=draw_get_font(),_ha=draw_get_halign(),_va=draw_get_valign(),
        _surface=-1,_camera=-1,_target=false,_checks=0,_rows=[];
    gpu_push_state();
    try {
        ds_map_delete(UberCont.saveData,"visual_ntte_autoframerate");scrOptionsUpdate();
        assert(UberCont.opt_ntte_autoframerate && UberCont.saveData[? "visual_ntte_autoframerate"],
            "Missing auto-framerate preference did not initialize ON");_checks++;
        var _state={limited:false,hot:0,cool:0,rate:60};
        for(var _i=0;_i<45;++_i) _state=scrFRClockBudget212(_state,60,30,1/60,true);
        assert(!_state.limited && _state.rate==60,"Short load spike reduced the engine cap prematurely");
        for(var _i=0;_i<8;++_i) _state=scrFRClockBudget212(_state,60,30,1/60,true);
        assert(_state.limited && _state.rate==30,"Sustained load did not reduce the engine cap");
        for(var _i=0;_i<140;++_i) _state=scrFRClockBudget212(_state,60,60,1/30,true);
        assert(_state.limited && _state.rate==30,"Auto cap retried before its recovery interval");
        for(var _i=0;_i<12;++_i) _state=scrFRClockBudget212(_state,60,60,1/30,true);
        assert(!_state.limited && _state.rate==60,"Auto cap did not recover to the requested rate");
        _state=scrFRClockBudget212({limited:true,hot:0,cool:0,rate:30},60,20,.016,false);
        assert(!_state.limited && _state.rate==60,"Disabling auto cap did not restore the requested rate");
        _state=scrFRClockBudget212({limited:true,hot:0,cool:0,rate:30},30,20,.016,true);
        assert(!_state.limited && _state.rate==30,"Auto policy overrode the user's explicit30cap");_checks+=6;

        UberCont.want_pause=0;UberCont.quit_pause=false;UberCont.paused=false;
        assert(scrFRClockSafe212(),"Stable gameplay was not a safe rate transaction");
        UberCont.paused=true;assert(!scrFRClockSafe212(),"Paused instances admitted a rate transaction");
        UberCont.paused=false;UberCont.quit_pause=true;
        assert(!scrFRClockSafe212(),"Unpause activation boundary admitted a rate transaction");
        UberCont.quit_pause=false;UberCont.want_pause=1;
        assert(!scrFRClockSafe212(),"Pending pause admitted a rate transaction");UberCont.want_pause=0;_checks+=4;

        scrFRClockApply212(30);
        var _custom=instance_create(500000,500000,FRCustomObject);
        with(_custom) {sprite_index=sprBanditIdle;hspeed=3;vspeed=-2;friction=.2;gravity=.1;
            image_speed=.4;maxspeed=8;knockback_speed=6;}
        var _rocket=instance_create(500000,500000,Rocket),_disc=instance_create(500000,500000,NTTELightningDisc),
            _player=instance_find(Player,0),_logical_max=scrFRVariableGet(_custom,"maxspeed"),
            _logical_anim=scrFRVariableGet(_custom,"image_speed"),_disc_max=_disc.maxspeed,
            _player_speed=_player.maxspeed;
        for(var _i=0;_i<4;++_i) {
            var _rate=(_i mod 2)==0?60:30,_ts=30/_rate;
            scrFRClockApply212(_rate);
            scrFRClock212TestsNear(timescale,_ts,"Native time scale");
            scrFRClock212TestsNear(_custom.hspeed,3*_ts,"Custom horizontal speed");
            scrFRClock212TestsNear(_custom.vspeed,-2*_ts,"Custom vertical speed");
            scrFRClock212TestsNear(_custom.friction,.2*_ts*_ts,"Custom physical friction");
            scrFRClock212TestsNear(_custom.gravity,.1*_ts*_ts,"Custom physical gravity");
            scrFRClock212TestsNear(scrFRVariableGet(_custom,"maxspeed"),_logical_max,"Source maxspeed unit");
            scrFRClock212TestsNear(scrFRVariableGet(_custom,"image_speed"),_logical_anim,"Source animation unit");
            scrFRClock212TestsNear(scrFRVariableGet(_custom,"force"),6,"Source mapped force unit");
            scrFRClock212TestsNear(_rocket.maxspeed,12*_ts,"Native cached rocket cap");
            scrFRClock212TestsNear(_disc.maxspeed,_disc_max,"Logical lightning disc cap");
            scrFRClock212TestsNear(_player.maxspeed,_player_speed*_ts,"Native player cached speed");_checks+=11;
            array_push(_rows,{kind:"transition",rate:_rate,scale:timescale,hspeed:_custom.hspeed,
                friction:_custom.friction,source_max:scrFRVariableGet(_custom,"maxspeed"),
                source_anim:scrFRVariableGet(_custom,"image_speed"),rocket_cap:_rocket.maxspeed});
        }

        var _bounce_rows=scrFRClock212WallBounceTests();_checks+=60;

        // Restore the same scalar fields that a real Player.Load imports,
        // then exercise the production after-load rebase at the other cap.
        var _player_fields=["maxspeed","hspeed","vspeed","friction","gravity","image_speed","knockback_speed","ntte_player_physics_scale"],
            _player_saved={};
        for(var _fi=0;_fi<array_length(_player_fields);++_fi)
            _player_saved[$ _player_fields[_fi]]=_player[$ _player_fields[_fi]]??undefined;
        try {
            scrFRClockApply212(60);
            with(_player) {maxspeed=4;hspeed=3;vspeed=-2;friction=.4;gravity=0;image_speed=.4;
                knockback_speed=6;ntte_player_physics_scale=1;scrNTTEFullPlayerRateAfterLoad({ntte_player_physics_scale:1});}
            scrFRClock212TestsNear(_player.maxspeed,2,"Loaded30Hz player cap in60Hz game");
            scrFRClock212TestsNear(_player.hspeed,1.5,"Loaded player horizontal velocity");
            scrFRClock212TestsNear(_player.vspeed,-1,"Loaded player vertical velocity");
            scrFRClock212TestsNear(_player.friction,.1,"Loaded player friction");
            scrFRClock212TestsNear(_player.image_speed,.2,"Loaded player animation");
            scrFRClock212TestsNear(_player.knockback_speed,3,"Loaded player force");
            scrFRClock212TestsNear(_player.ntte_player_physics_scale,.5,"Loaded player physics marker");
            // Old saves omitted the marker. The original canonical-speed
            // inference must cover their remaining physical cache as well.
            var _canonical=(_player.race==Race.Plant?4.5:(_player.race==Race.BigDog?2:(_player.race==Race.Skeleton?3:4)))+.5*_player.footextra;
            with(_player) {maxspeed=_canonical;hspeed=3;vspeed=0;friction=.4;image_speed=.4;
                scrNTTEFullPlayerRateAfterLoad({});}
            scrFRClock212TestsNear(_player.maxspeed,_canonical*.5,"Legacy unmarked save cap");
            scrFRClock212TestsNear(_player.hspeed,1.5,"Legacy unmarked save velocity");
            scrFRClock212TestsNear(_player.friction,.1,"Legacy unmarked save friction");_checks+=10;
        } finally {
            scrFRClockApply212(30);
            for(var _fi=0;_fi<array_length(_player_fields);++_fi)
                if(!is_undefined(_player_saved[$ _player_fields[_fi]]))
                    _player[$ _player_fields[_fi]]=_player_saved[$ _player_fields[_fi]];
        }

        // The real options handler receives a keyboard confirmation and
        // persists through the same saveData -> scrOptionsUpdate path.
        _surface=surface_create(gui_w,gui_h);
        _camera=camera_create_view(0,0,gui_w,gui_h,0,noone,-1,-1,-1,-1);
        assert(surface_exists(_surface),"Auto cap video menu surface unavailable");
        surface_set_target(_surface);_target=true;camera_apply(_camera);
        matrix_set(matrix_world,matrix_build_identity());shader_reset();gpu_set_blendmode(bm_normal);
        var _menu=instance_create(0,0,MenuOptions),_row=undefined,_row_index=-1;
        with(_menu) {scrOptionsMenuChangeCategory(OptionCategory.Video);last_change=current_frame-1000;
            wait=1;mouse_active=false;pointed_item=-1;slider=undefined;slider_change=0;
            mx_last=device_mouse_x_to_gui(0);my_last=device_mouse_y_to_gui(0);}
        with(_menu) event_perform(ev_draw,ev_gui);
        with(_menu) {scroll=scroll_min;scroll_speed=0;}
        for(var _i=0;_i<array_length(_menu.items);++_i)
            if((_menu.items[_i][$ "key"]??"")=="visual_ntte_autoframerate") {_row=_menu.items[_i];_row_index=_i;}
        assert(is_struct(_row) && _row.available && _row.value,
            "Video menu omitted its enabled default-ON auto cap switch");
        UberCont.opt_keyboard=true;UberCont.opt_gamepad=false;
        _driver.fr_followup210_keyboard={held:-1,pressed:vk_enter,released:-1};
        with(_menu) {wait=0;mouse_active=false;pointed_item=_row_index;
            mx_last=device_mouse_x_to_gui(0);my_last=device_mouse_y_to_gui(0);}
        with(_menu) event_perform(ev_draw,ev_gui);
        assert(!_row.value && !UberCont.opt_ntte_autoframerate && !save_get_value("visual","ntte_autoframerate",true),
            "Real Video keyboard confirmation did not switch auto cap OFF");
        _driver.fr_followup210_keyboard=undefined;scrOptionsUpdate();
        assert(!UberCont.opt_ntte_autoframerate,"Reloading saved options lost disabled auto cap");
        UberCont.opt_keyboard=true;UberCont.opt_gamepad=false;
        _driver.fr_followup210_keyboard={held:-1,pressed:vk_enter,released:-1};
        with(_menu) {wait=0;mouse_active=false;pointed_item=_row_index;
            mx_last=device_mouse_x_to_gui(0);my_last=device_mouse_y_to_gui(0);}
        with(_menu) event_perform(ev_draw,ev_gui);
        assert(_row.value && UberCont.opt_ntte_autoframerate && save_get_value("visual","ntte_autoframerate",false),
            "Real Video confirmation did not switch auto cap ON");
        _driver.fr_followup210_keyboard=undefined;
        with(_menu) event_perform(ev_draw,ev_gui); // Show final persisted ON state after the confirmation frame.
        surface_reset_target();_target=false;
        surface_save(_surface,working_directory+"ntuf212-auto-framerate-video.png");_checks+=4;
        var _file=file_text_open_write(working_directory+"ntuf212-clock-unit.json");
        file_text_write_string(_file,json_stringify({passed:true,checks:_checks,transitions:_rows,
            wallbounce:_bounce_rows,physical_device_tested:false}));
        file_text_close(_file);scrNTTESmokeLog("PASS NTUF212 default/persisted automatic cap, actual Video confirmation, budget recovery, API unit preservation, pause guards "+string(_checks));
    } finally {
        _driver.fr_followup210_keyboard=undefined;
        if(_target) surface_reset_target();
        if(_surface>=0 && surface_exists(_surface)) surface_free(_surface);
        if(_camera>=0) camera_destroy(_camera);
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        save_set_value("options","framerate",_old_opt);
        if(is_undefined(_old_save)) ds_map_delete(UberCont.saveData,"visual_ntte_autoframerate");
        else UberCont.saveData[? "visual_ntte_autoframerate"]=_old_save;
        UberCont.opt_framerate=_old_cap;UberCont.opt_ntte_autoframerate=_old_auto;
        UberCont.opt_keyboard=_old_keyboard;UberCont.opt_gamepad=_old_gamepad;
        UberCont.paused=_old_paused;UberCont.want_pause=_old_want;UberCont.quit_pause=_old_quit;
        UberCont.fr_clock_budget212=_budget;scrFRClockApply212(_old_rate);
        gpu_pop_state();matrix_set(matrix_world,_draw.world);matrix_set(matrix_view,_draw.view);matrix_set(matrix_projection,_draw.projection);
        if(_draw.shader>=0) shader_set(_draw.shader);else shader_reset();
        draw_set_font(_font);draw_set_halign(_ha);draw_set_valign(_va);draw_set_color(_draw.color);draw_set_alpha(_draw.alpha);
    }
}

function scrFRClock212LiveActor() { fr_clock212_ticks++; }

function scrFRClock212LiveStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled(),"Clock live test needs isolated Windows runner");
    save_set_value("options","framerate",60);save_set_value("visual","ntte_autoframerate",false);scrOptionsUpdate();
    UberCont.opt_autopause=false;UberCont.paused=false;UberCont.want_pause=0;UberCont.quit_pause=false;
    var _actor=instance_create(500000,500000,FRCustomObject),_native=instance_find(Player,0);
    with(_actor) {visible=false;friction=0;gravity=0;hspeed=2*timescale;vspeed=0;
        fr_clock212_ticks=0;on_step=scrFRClock212LiveActor;}
    // FRCustomObject has no engine Alarm11 event: its unused native slot does
    // not count down. Exercise the real Player Alarm10 event instead.
    var _saved_alarm=_native.alarm[10];_native.alarm[10]=300;
    _driver.fr_clock212_live={phase:0,host:0,actor:_actor,segments:[],rates:[60,30,60],
        begin_x:_actor.x,begin_ticks:0,begin_frame:current_frame,begin_alarm:_native.alarm[10],
        native:_native,saved_native_alarm:_saved_alarm};
}

function scrFRClock212LiveStep(_driver) {
    var _s=_driver.fr_clock212_live;_s.host++;
    assert(_s.host<600 && instance_exists(_s.actor),"Clock live actor timed out or disappeared");
    var _rate=_s.rates[_s.phase];
    if(game_get_speed(gamespeed_fps)!=_rate) return false;
    if(!variable_struct_exists(_s,"segment_hosts")) {
        _s.segment_hosts=0;_s.begin_x=_s.actor.x;_s.begin_ticks=_s.actor.fr_clock212_ticks;
        _s.begin_frame=current_frame;_s.begin_alarm=_s.native.alarm[10];return false;
    }
    if(++_s.segment_hosts<_rate) return false;
    var _distance=_s.actor.x-_s.begin_x,_ticks=_s.actor.fr_clock212_ticks-_s.begin_ticks,
        _logical=current_frame-_s.begin_frame,_alarm=_s.begin_alarm-_s.native.alarm[10];
    assert(abs(_distance-60)<=2,"Scheduled native motion changed with engine cap: "+string(_distance));
    assert(abs(_ticks-30)<=1,"Scheduled FR30Hz callbacks changed with engine cap: "+string(_ticks));
    assert(abs(_logical-30)<=1,"Scheduled native logic clock changed with engine cap: "+string(_logical));
    assert(abs(_alarm-30)<=1,"Engine Alarm countdown changed with engine cap: "+string(_alarm));
    array_push(_s.segments,{rate:_rate,host_frames:_s.segment_hosts,distance:_distance,
        source_callbacks:_ticks,logical_time:_logical,alarm_elapsed:_alarm});
    if(++_s.phase>=array_length(_s.rates)) {
        var _file=file_text_open_write(working_directory+"ntuf212-clock-live.json");
        file_text_write_string(_file,json_stringify({passed:true,segments:_s.segments,physical_device_tested:false}));
        file_text_close(_file);_s.native.alarm[10]=_s.saved_native_alarm;instance_destroy(_s.actor);
        scrNTTESmokeLog("PASS NTUF212 actual host60->30->60 callbacks, equal physical travel, native alarms and FR30Hz ticks "+json_stringify(_s.segments));
        return true;
    }
    variable_struct_remove(_s,"segment_hosts");save_set_value("options","framerate",_s.rates[_s.phase]);scrOptionsUpdate();
    return false;
}
