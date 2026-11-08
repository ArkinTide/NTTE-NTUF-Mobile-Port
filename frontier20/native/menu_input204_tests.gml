// Explicit desktop-only scheduled regression. Raw fixtures feed the shipping
// General/JoystickMove samplers. No test writes KeyCont direction edges or calls
// the selection helper. Native mouse-event emulation below is the sole stand-in
// for GameMaker's OS touch-to-Mouse4 delivery; its real hit box/event are retained.
function scrFRMenuInput204State() {
    if(os_type!=os_windows || !scrNTTEFullSmokeEnabled() || !instance_exists(FRIntegrationTest)) return undefined;
    var _driver=instance_find(FRIntegrationTest,0);
    return _driver[$ "fr_menu_input204"]??undefined;
}
function scrFRMenuInput204Write(_s,_passed=false) {
    var _f=file_text_open_write(working_directory+"frontier-menu-input204.json");
    file_text_write_string(_f,json_stringify({passed:_passed,rate:_s.rate,phase:_s.phase,
        host_frames:_s.host,scenario:_s.scenario,inputs:_s.inputs,observations:_s.observations,
        transitions:_s.transitions,positive:_s.positive,
        options_observations:_s.options_observations,
        physical_device_tested:false,os_mouse_dispatch_emulated:true,
        source_pointer_checks:_s[$ "source_pointer_checks"]??0,
        failure:_s[$ "failure"]??undefined}));file_text_close(_f);
}
function scrFRMenuInput204Check(_s,_condition,_message) {
    if(_condition) return;
    _s.failure=_message;scrFRMenuInput204Write(_s);
    scrNTTESmokeLog("MENU INPUT204 FAILURE "+json_stringify({message:_message,
        phase:_s.phase,rate:_s.rate,host:_s.host,observations:_s.observations}));
    throw _message;
}
function scrFRMenuInput204Observe(_s,_label) {
    var _i=global.index,_row={label:_label,host:_s.host,frame:current_frame,
        input_frame:global.__input_frame,phase:_s.phase,scenario:_s.scenario,
        race:my_player.race,selection:UberCont.gamepad_sel,
        keyboard:KeyCont.keyboard[_i],gamepad:KeyCont.gamepad[_i],touch:KeyCont.touch[_i],
        direction:{east:KeyCont.press_east[_i],west:KeyCont.press_west[_i],
            north:KeyCont.press_nort[_i],south:KeyCont.press_sout[_i]},
        owners:instance_number(JoystickMove),menus:instance_number(Menu),
        characters:instance_number(CharSelect)};
    array_push(_s.observations,_row);
    if(!is_undefined(_s[$ "previous_race"]??undefined) && _s.previous_race!=my_player.race)
        array_push(_s.transitions,_row);
    _s.previous_race=my_player.race;
    if(_label!="idle" || _s.elapsed mod _s.rate==0)
        scrNTTESmokeLog("MENU INPUT204 OBSERVE "+json_stringify(_row));
    return _row;
}
function scrFRMenuInput204Clear(_driver) {
    // Same real-object retirement boundary as the accepted Bubbles startup
    // fixture, after authored event cleanup has finished against its GameCont.
    with(all) {
        if(id==_driver || object_index==UberCont || object_index==Console || object_index==FRWorld) continue;
        if(persistent && (object_index==FRCustomObject || object_index==FRBinding)) continue;
        instance_destroy(id,false);
    }
    var _retained=[];
    for(var _i=0;_i<array_length(global.fr_tasks);++_i) {
        var _task=global.fr_tasks[_i],_scope=_task.scope;
        if(_task.done) continue;
        if(!is_struct(_scope) && instance_exists(_scope)
            && (_scope.object_index==FRWorld || (_scope.persistent
                && (_scope.object_index==FRCustomObject || _scope.object_index==FRBinding))))
            array_push(_retained,_task);
        else _task.done=true;
    }
    global.fr_tasks=_retained;
    assert(!instance_exists(Player) && !instance_exists(GameCont) && !instance_exists(MobileUI)
        && !instance_exists(Menu) && instance_number(Floor)==0,
        "Menu input fixture failed its ordinary native object retirement");
}
function scrFRMenuInput204Stick(_s,_vertical=false) {
    with(MobileUI) instance_destroy(id,false);
    UberCont.opt_keyboard=false;UberCont.opt_gamepad=false;
    global.fr_touch_input=undefined;
    _s.stick=instance_create(160,164,JoystickMove);_s.stick.rad=36;
    _s.raw_x=_s.stick.x+(_vertical?0:(_s.scenario==1?-24:24));
    _s.raw_y=_s.stick.y+(_vertical?-24:0);
    _s.input_index=0;_s.elapsed=0;
}
function scrFRMenuInput204Start(_driver,_rate) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled(),
        "Menu input204 requires the explicit isolated desktop harness");
    save_set_value("options","framerate",_rate);save_set_value("options","autopause",false);
    save_set_value("visual","freezeframes",0);save_set_value("visual","bossintro",false);
    scrOptionsUpdate();scrNTTEFullRateApply();
    UberCont.opt_autopause=false;UberCont.paused=false;UberCont.opt_freeze=0;
    UberCont.want_menu=false;UberCont.want_quit_to_menu=false;UberCont.want_restart=false;
    UberCont.opt_keyboard=false;UberCont.opt_gamepad=false;global.console_active=false;
    global.index=0;global.is_server=true;_driver.persistent=true;
    // This isolated save owns the unlocks. Enable through the real ownership
    // API so native Draw's can field, rather than the fixture, admits targets.
    for(var _race=0;_race<Race.NUM_ALL_RACE_TYPES;++_race) scr_race_set_unlocked(_race,true);
    _driver.fr_menu_input204={rate:_rate,phase:0,host:0,elapsed:0,scenario:0,
        driver:_driver,owner:FRWorld.id,generation:global.fr_boot_generation,
        stick:noone,input_index:0,raw_x:0,raw_y:0,inputs:[],observations:[],
        transitions:[],positive:[],options_observations:[],retiring_events:[],
        keyboard:{held:-1,pressed:-1,released:-1}};
    var _s=_driver.fr_menu_input204;
    with(FRCustomObject) if(name=="Event") array_push(_s.retiring_events,real(id));
    for(var _i=0;_i<array_length(_s.retiring_events);++_i)
        if(instance_exists(_s.retiring_events[_i])) with(_s.retiring_events[_i]) instance_destroy();
    _s.pad={kh:0,button:-1,pressed:false,released:false,
        get_value:function(_axis){return _axis==gp_axislh?kh:0;},
        get_held:function(_key){return _key==button;},
        get_pressed:function(_key){return _key==button && pressed;},
        get_released:function(_key){return _key==button && released;}};
    scrNTTESmokeLog("MENU INPUT204 START rate="+string(_rate));
}
function scrFRMenuInput204Keyboard(_kind,_key) {
    var _s=scrFRMenuInput204State();
    if(is_undefined(_s) || _s.phase!=4) return undefined;
    return _key==_s.keyboard[$ _kind];
}
function scrFRMenuInput204BeforeInput() {
    var _s=scrFRMenuInput204State();if(is_undefined(_s)) return;
    var _samples=[];
    for(var _i=0;_i<5;++_i) array_push(_samples,{x:0,y:0,held:false,pressed:false,released:false});
    if(_s.phase==1 || _s.phase==7) {
        _samples[0]={x:_s.raw_x,y:_s.raw_y,held:true,pressed:_s.input_index==0,released:false};
        _s.input_index++;
    } else if(_s.phase==2) {
        // Case0: release after owner disappears. Case1: hold through return,
        // then release. Case2: the release happened while no owner existed.
        var _hold=_s.scenario==1 && _s.elapsed<10,
            _release=(_s.scenario==0 && _s.elapsed==1) || (_s.scenario==1 && _s.elapsed==10);
        _samples[0]={x:_s.raw_x,y:_s.raw_y,held:_hold,pressed:false,released:_release};
    } else if(_s.phase==3) {
        var _icon=_s.touch_icon;
        _samples[0]={x:(_icon.bbox_left+_icon.bbox_right)/2-view_xview,
            y:(_icon.bbox_top+_icon.bbox_bottom)/2-view_yview,
            held:_s.elapsed==0,pressed:_s.elapsed==0,released:_s.elapsed==1};
    } else if(_s.phase==4) {
        var _f=_s.input_index++;_s.last_input=_f;
        _s.keyboard={held:((_f>=2 && _f<=6) || (_f>=10 && _f<=14))?vk_right:-1,
            pressed:(_f==2 || _f==10)?vk_right:-1,
            released:(_f==7 || _f==15)?vk_right:-1};
    } else if(_s.phase==5 || _s.phase==6) {
        var _f=_s.input_index++,_pad=_s.pad;_s.last_input=_f;
        _pad.kh=(_s.phase==6?_f==0:(_f>=2 && _f<=6))?0.8:0;
        _pad.button=_s.phase==5 && _f>=10 && _f<=14?gp_padr:-1;
        _pad.pressed=_f==10;_pad.released=_f==15;
        if(array_length(global.__input_gamepads)==0) array_resize(global.__input_gamepads,1);
        global.__input_gamepads[0]=_pad;
        if(_s.phase==6 && _f>0) {UberCont.opt_gamepad=false;UberCont.opt_keyboard=false;}
    }
    global.fr_touch_input_fixture={active:true,samples:_samples};
    if(_s.phase>0 && _s.phase<8) array_push(_s.inputs,{host:_s.host,phase:_s.phase,
        frame:global.__input_frame,touch:_samples[0],keyboard:_s.keyboard,
        pad:{x:_s.pad.kh,button:_s.pad.button}});
}
function scrFRMenuInput204AfterInput() {
    var _s=scrFRMenuInput204State();if(is_undefined(_s)) return;
    if(_s.phase==1 || _s.phase==7) {
        var _vertical=_s.phase==7,_edge=_vertical?KeyCont.press_nort[0]:
            (_s.scenario==1?KeyCont.press_west[0]:KeyCont.press_east[0]);
        scrFRMenuInput204Check(_s,_edge && instance_exists(_s.stick)
            && KeyCont.touch[0] && KeyCont.moving[0]>0,
            "Raw touch did not traverse the actual General -> JoystickMove direction sampler");
        scrFRMenuInput204Observe(_s,"real-joystick-fresh-edge");
        if(_vertical) {
            instance_destroy(_s.stick,false);_s.options=instance_create(0,0,MenuOptions);
            _s.options_start=_s.options.pointed_item;_s.phase=8;_s.elapsed=0;return;
        }
        scrFRMenuInput204Clear(_s.driver);
        if(!instance_exists(MusCont)) instance_create(0,0,MusCont);
        var _play=instance_create(0,0,PlayButton);_play.num=0;
        with(_play) event_perform(ev_other,10);
        scrFRMenuInput204Check(_s,instance_exists(Menu) && instance_exists(GameCont)
            && instance_number(CharSelect)>=2 && instance_number(Floor)>0
            && !instance_exists(MobileUI),
            "Real PlayButton did not create its native MenuGen/Menu/CharSelect room without joystick owners");
        _s.menu=Menu.id;_s.expected_race=my_player.race;_s.expected_selection=UberCont.gamepad_sel;
        _s.phase=2;_s.elapsed=0;scrFRMenuInput204Observe(_s,"native-menu-entered-with-stale-edge");
    } else if(_s.phase==3 && _s.elapsed==0) {
        // The desktop raw fixture cannot make GM synthesize an OS Mouse4.
        // Emulate only that hardware delivery, using the real mask/hit box;
        // the native Mouse4 event owns every actual selection side effect.
        var _sample=global.fr_touch_input_fixture.samples[0],_icon=_s.touch_icon;
        scrFRMenuInput204Check(_s,_sample.pressed && point_in_rectangle(_sample.x,_sample.y,
            _icon.bbox_left-view_xview,_icon.bbox_top-view_yview,
            _icon.bbox_right-view_xview,_icon.bbox_bottom-view_yview),
            "Raw touchscreen positive control missed its actual native character hit box");
        with(_icon) event_perform(ev_mouse,ev_left_press);
    }
}
function scrFRMenuInput204OptionsObserve(_kh,_kv) {
    var _s=scrFRMenuInput204State();if(is_undefined(_s) || _s.phase!=8) return;
    array_push(_s.options_observations,{host:_s.host,kh:_kh,kv:_kv,
        pointed:pointed_item,touch:KeyCont.touch[0],keyboard:KeyCont.keyboard[0],gamepad:KeyCont.gamepad[0]});
    scrFRMenuInput204Check(_s,_kh==0 && _kv==0 && KeyCont.touch[0],
        "Touch gameplay directions leaked into the independent native options reader");
}
function scrFRMenuInput204Step(_driver) {
    var _s=_driver.fr_menu_input204;_s.host++;
    scrFRMenuInput204Check(_s,_s.host<_s.rate*35,"Scheduled menu input204 case exceeded35seconds");
    scrFRMenuInput204Check(_s,FRWorld.id==_s.owner && global.fr_boot_generation==_s.generation
        && game_get_speed(gamespeed_fps)==_s.rate && timescale==30/_s.rate,
        "Menu lifecycle replaced the source runtime or actual requested native engine rate");
    if(_s.phase==0) {
        for(var _i=0;_i<array_length(global.fr_tasks);++_i) {
            var _task=global.fr_tasks[_i],_final=_task.final_scope;
            if(!_task.done && is_struct(_final) && array_contains(_s.retiring_events,_final.source)) return false;
        }
        scrFRMenuInput204Stick(_s);_s.phase=1;return false;
    }
    if(_s.phase==2) {
        scrFRMenuInput204Observe(_s,"idle");
        // Let the native Draw author can/selection first. The historical VM
        // then demonstrably changes race every frame with no new raw touch.
        if(_s.elapsed>=3) scrFRMenuInput204Check(_s,my_player.race==_s.expected_race
            && UberCont.gamepad_sel==_s.expected_selection,
            "Touch direction edge replayed every native menu frame after its joystick owner disappeared");
        if(_s.elapsed==5 && surface_exists(application_surface)) surface_save(application_surface,
            working_directory+"frontier-menu-input204-idle-"+string(_s.scenario)+".png");
        if(++_s.elapsed<_s.rate*2) return false;
        _s.scenario++;
        if(_s.scenario<3) {scrFRMenuInput204Stick(_s);_s.phase=1;return false;}
        _s.touch_icon=noone;with(CharSelect) if(race==Race.Fish && race!=my_player.race) {_s.touch_icon=id;break;}
        scrFRMenuInput204Check(_s,instance_exists(_s.touch_icon) && _s.touch_icon.can,
            "Ordinary native menu omitted its enabled nonselected Fish character for touch control");
        _s.touch_race=_s.touch_icon.race;
        _s.phase=3;_s.elapsed=0;return false;
    }
    if(_s.phase==3) {
        scrFRMenuInput204Check(_s,my_player.race==_s.touch_race && instance_exists(Menu)
            && instance_number(Player)==0,"Native raw-touch Mouse4 did not select its different target exactly once");
        if(++_s.elapsed<8) return false;
        array_push(_s.positive,{kind:"raw-touch-native-mouse4",race:my_player.race});
        for(var _i=0;_i<instance_number(CharSelect);++_i)
            if(instance_find(CharSelect,_i)==_s.touch_icon) UberCont.gamepad_sel=_i;
        _s.nav_base=UberCont.gamepad_sel;
        UberCont.opt_keyboard=true;UberCont.opt_gamepad=false;
        _s.phase=4;_s.input_index=0;return false;
    }
    if(_s.phase==4 || _s.phase==5) {
        var _f=_s.last_input,_expected=(_s.nav_base+(_f>=10?2:(_f>=2?1:0))) mod instance_number(CharSelect),
            _target=instance_find(CharSelect,_expected);
        scrFRMenuInput204Check(_s,instance_exists(_target) && _target.can
            && UberCont.gamepad_sel==_expected && my_player.race==_target.race,
            "Valid keyboard/controller fresh edge failed, held edge repeated, or neutral/release drifted");
        if(_f<20) return false;
        array_push(_s.positive,{kind:_s.phase==4?"keyboard-native-general":"analogue+dpad-native-general",
            fresh_edges:2,held_repeats:0,neutral_repeats:0});
        _s.input_index=0;_s.nav_base=UberCont.gamepad_sel;
        UberCont.opt_keyboard=false;UberCont.opt_gamepad=true;
        _s.phase++;return false;
    }
    if(_s.phase==6) {
        if(_s.last_input==0) {
            _s.expected_race=my_player.race;_s.expected_selection=UberCont.gamepad_sel;
            scrFRMenuInput204Observe(_s,"controller-before-touch-mode-boundary");
        } else scrFRMenuInput204Check(_s,my_player.race==_s.expected_race
            && UberCont.gamepad_sel==_s.expected_selection && KeyCont.touch[0],
            "Controller direction edge replayed after switching back to touchscreen mode");
        if(_s.last_input<_s.rate) return false;
        var _scale=timescale,_frame=current_frame,_input_frame=global.__input_frame,
            _serial=FRWorld.logic_serial,_tick=FRWorld.logic_tick,
            _pointer=global.fr_touch_input,_fixture=global.fr_touch_input_fixture;
        try {_s.source_pointer_checks=scrFRMenuPointer204Tests(0);}
        finally {
            global.time_scale=_scale;current_frame=_frame;global.__input_frame=_input_frame;
            FRWorld.logic_serial=_serial;FRWorld.logic_tick=_tick;
            global.fr_touch_input=_pointer;global.fr_touch_input_fixture=_fixture;
        }
        array_push(_s.positive,{kind:"controller-to-touch-mode",repeats:0});
        // The independent native options reader needs the same ownership
        // boundary. An old north edge otherwise navigates an unfilled list.
        scrFRMenuInput204Stick(_s,true);_s.phase=7;return false;
    }
    if(_s.phase==8) {
        if(++_s.elapsed<8) return false;
        scrFRMenuInput204Check(_s,array_length(_s.options_observations)>0,
            "Native options draw never exercised its independent direction reader");
        scrNTTESmokeLog("MENU INPUT204 SEPARATE TOUCH OPTIONS OBSERVATION "+json_stringify(_s.options_observations));
        if(surface_exists(application_surface)) surface_save(application_surface,
            working_directory+"frontier-menu-input204-after.png");
        scrFRMenuInput204Write(_s,true);_s.phase=9;
        scrNTTESmokeLog("MENU INPUT204 ACCEPTED "+json_stringify({rate:_s.rate,
            scenarios:3,positive:_s.positive,source_pointer_checks:_s.source_pointer_checks,
            physical_device_tested:false,options_reader_input_ownership_checked:true}));
        return true;
    }
    return _s.phase==9;
}
