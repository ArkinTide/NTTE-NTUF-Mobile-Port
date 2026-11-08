// Scheduled Robot death -> authored admission buttons -> raw touch -> native
// YES/NO lifecycle. The fixture never creates a controller/button, invokes a
// button callback, changes a UI timer, or calls AreaFinish/Portal events.
function scrFRBluescreenUITestsState() {
    if(os_type!=os_windows || !scrNTTEFullSmokeEnabled() || !instance_exists(FRIntegrationTest)) return undefined;
    var _driver=instance_find(FRIntegrationTest,0);
    return _driver[$ "fr_bluescreen_ui"]??undefined;
}
function scrFRBluescreenUITestsNativeBootstrap() {
    // The generic smoke bootstrap skips Vlambeer's Create event. Only after
    // this fixture's genuine YES callback/Portal may the normal room restart
    // initialize its destination. Keep the global smoke/save isolation flag.
    var _s=scrFRBluescreenUITestsState();
    return is_struct(_s) && _s.accept && _s.phase==5
        && is_real(_s[$ "clicked_at"]??undefined) && _s.input_stage==3;
}
function scrFRBluescreenUITestsPointer() {
    if(!variable_global_exists("fr_touch_input") || !is_struct(global.fr_touch_input)) return undefined;
    var _p=global.fr_touch_input.pointer,_result={frame:_p.frame,ready:_p.ready,serial:_p.serial,
        hardware_frame:_p[$ "host_frame204"]??-1};
    var _fields=["samples","pending","output"];
    for(var _i=0;_i<array_length(_fields);++_i) {
        var _samples=_p[$ _fields[_i]],_sample=_samples[4];
        _result[$ _fields[_i]]=is_undefined(_sample)?undefined:
            {x:_sample.x,y:_sample.y,held:_sample.held};
    }
    return _result;
}
function scrFRBluescreenUITestsWrite(_s,_passed=false) {
    var _file=file_text_open_write(working_directory+"frontier-bluescreen-ui204.json");
    file_text_write_string(_file,json_stringify({passed:_passed,physical_device_tested:false,
        rate:_s.rate,accept:_s.accept,entry_mode:_s.entry_mode,eligible:_s.eligible,
        phase:_s.phase,host_frames:_s.host,
        input_frames:_s.input_frames,observations:_s.observations,snapshots:_s.snapshots,
        stale_press:_s[$ "stale_press"]??undefined,draw_counts:_s.draw_counts,
        connection_draws:_s.connection_draws,denial_draws:_s.denial_draws,
        manager_before_death:_s[$ "manager_before_death"]??undefined,
        actual_click:_s[$ "actual_click"]??undefined,
        final:_s[$ "final"]??undefined}));file_text_close(_file);
}
function scrFRBluescreenUITestsButtons() {
    var _items=[];
    with(FRCustomObject) if(self[$ "fr_bluescreenbutton"]??false) array_push(_items,id);
    return _items;
}
function scrFRBluescreenUITestsActor(_actor) {
    if(!instance_exists(_actor)) return {id:real(_actor),exists:false};
    var _creator=_actor[$ "creator"]??noone;
    return {id:real(_actor),exists:true,object:object_get_name(_actor.object_index),
        name:_actor[$ "name"]??"",x:_actor.x,y:_actor.y,visible:_actor.visible,
        alpha:_actor.image_alpha,depth:_actor.depth,sprite:sprite_get_name(_actor.sprite_index),
        image:_actor.image_index,hp:_actor[$ "hp"]??undefined,max_hp:_actor[$ "max_hp"]??undefined,
        race:_actor[$ "race"]??undefined,creator:real(_creator),creator_exists:instance_exists(_creator),
        yes:_actor[$ "yesButton"]??undefined,done:_actor[$ "done"]??undefined,
        blueTime:_actor[$ "blueTime"]??undefined,blueChecks:_actor[$ "blueChecks"]??undefined,
        drawConnect:_actor[$ "drawConnect"]??undefined,
        box:[_actor.bbox_left,_actor.bbox_top,_actor.bbox_right,_actor.bbox_bottom]};
}
function scrFRBluescreenUITestsSnapshot(_s,_label) {
    var _buttons=scrFRBluescreenUITestsButtons(),_rows=[],_portals=[],_bindings=[];
    for(var _i=0;_i<array_length(_buttons);++_i) array_push(_rows,scrFRBluescreenUITestsActor(_buttons[_i]));
    with(Portal) array_push(_portals,{id:real(id),x:x,y:y,type:type,close:close,
        endgame:endgame,sprite:sprite_get_name(sprite_index),image:image_index});
    with(FRBinding) if(fr_binding_kind=="draw")
        array_push(_bindings,{id:real(id),kind:fr_binding_kind,creator:real(creator),
            creator_exists:instance_exists(creator),code:string(fr_binding_code),depth:depth});
    var _tasks=[];
    for(var _i=0;_i<min(32,array_length(global.fr_tasks));++_i) {
        var _task=global.fr_tasks[_i];
        array_push(_tasks,{code:string(_task.code),scope_type:typeof(_task.scope),scope:string(_task.scope),
            other_type:typeof(_task.other_scope),other:string(_task.other_scope),pc:_task.pc,
            wait_ticks:_task.wait_ticks,done:_task.done,last_tick:_task.last_tick});
    }
    var _row={label:_label,host:_s.host,frame:current_frame,ready:scrFRReadyTick(),
        serial:scrFRLogicSerial(),area:GameCont.area,subarea:GameCont.subarea,
        players:instance_number(Player),gameover:instance_exists(GameOver),
        player:scrFRBluescreenUITestsActor(scrFRPlayerFind(_s.slot)),
        controller:scrFRBluescreenUITestsActor(_s.controller),buttons:_rows,portals:_portals,
        bindings:_bindings,view:[view_xview,view_yview,view_width,view_height],
        gui:[gui_w,gui_h],camera_target:real(scrFRViewValue("object")),
        wibbly_managers:array_length(scrFREventTestsNamed(FRCustomObject,"wib_PlayerManager")),
        camera_pan:scrFRViewValue("pan"),draws:_s.draws,pointer:scrFRBluescreenUITestsPointer(),
        native:{floors:instance_number(Floor),walls:instance_number(Wall),tops:instance_number(TopCont),
            gen:instance_number(GenCont),floormakers:instance_number(FloorMaker),
            vlambeer:instance_number(Vlambeer),levcont:instance_number(LevCont),
            generation_screen:scrGameIsGenerationScreen(),level_ended:GameCont.is_level_ended,
            can_advance:GameCont.can_advance_stage,smoke_active:global.ntte_smoke_active,
            pending_destination:scrNTTEFullValue(GameCont,"ntte_full_pending_destination",undefined),
            pending_generation:scrNTTEFullValue(GameCont,"ntte_full_source_pending_generation",undefined),
            task_count:array_length(global.fr_tasks),tasks:_tasks},
        input_touch:KeyCont.touch[_s.slot],keyboard:UberCont.opt_keyboard,gamepad:UberCont.opt_gamepad};
    array_push(_s.snapshots,_row);
    scrNTTESmokeLog("BLUESCREEN UI204 SNAPSHOT "+json_stringify(_row));
    scrFRBluescreenUITestsWrite(_s);return _row;
}
function scrFRBluescreenUITestsCheck(_s,_condition,_message) {
    if(_condition) return;
    _s.final={result:"failed",reason:_message};scrFRBluescreenUITestsSnapshot(_s,"failed");
    throw _message;
}
function scrFRBluescreenUITestsObserve(_kind) {
    var _s=scrFRBluescreenUITestsState();
    if(is_undefined(_s) || !instance_exists(id)) return;
    if((self[$ "name"]??"")!="fr_bluescreenController"
        && !(self[$ "fr_bluescreenbutton"]??false)) return;
    // This observer is called in the real actor event after the unchanged
    // callback. Preserve and record the physical/native other at that boundary.
    var _other=scrFROther(other),_row={kind:_kind,host:_s.host,frame:current_frame,
        self:real(id),other_type:typeof(other),other_value:string(other),
        logical_other_type:typeof(_other),logical_other:string(_other),
        ready:scrFRReadyTick(),serial:scrFRLogicSerial(),
        click:self[$ "clickIndex"]??undefined,hover:self[$ "hoverIndex"]??undefined,
        hold:self[$ "holdIndex"]??undefined,pointer:scrFRBluescreenUITestsPointer(),
        actor:scrFRBluescreenUITestsActor(id)};
    if(_kind=="step" && (self[$ "name"]??"")=="fr_bluescreenController"
        && blueChecks==(_s[$ "last_checks"]??-1)) return;
    if(_kind=="step" && (self[$ "name"]??"")=="fr_bluescreenController") _s.last_checks=blueChecks;
    if(_kind=="draw") {
        var _key=string(real(id)),_count=(_s.draw_counts[$ _key]??0)+1;
        _s.draw_counts[$ _key]=_count;
        if((self[$ "name"]??"")=="fr_bluescreenController" && drawConnect) _s.connection_draws++;
        if(_count>2 && !(self[$ "done"]??false)) return;
    }
    if(_kind=="end-before" && !(self[$ "done"]??false)) return;
    array_push(_s.observations,_row);
    if(_kind=="step" && (self[$ "fr_bluescreenbutton"]??false)
        && (self[$ "done"]??false) && _row.click==_s.slot && id==_s.button)
        _s.actual_click=_row;
    scrNTTESmokeLog("BLUESCREEN UI204 ACTOR "+json_stringify(_row));
}
function scrFRBluescreenUITestsDraw() {
    var _s=scrFRBluescreenUITestsState();
    if(is_undefined(_s)) return;
    _s.draws++;
    _s.drawn_host=_s.host;
}
function scrFRBluescreenUITestsBindingDraw() {
    var _s=scrFRBluescreenUITestsState();
    if(is_undefined(_s) || fr_binding_kind!="draw") return;
    var _actual=scrFRScriptRef(fr_binding_code),
        _expected=scrFRScriptRef(global.fr_module_scripts[$ "area:cyberspace"][$ "denybluescreen_draw"]);
    if(_actual!=_expected) return;
    _s.denial_draws++;
    if(_s.denial_draws<=3) {
        var _row={kind:"deny-binding-draw",host:_s.host,frame:current_frame,
            self:real(id),creator:real(creator),creator_exists:instance_exists(creator),
            script:string(_actual),depth:depth};
        array_push(_s.observations,_row);
        scrNTTESmokeLog("BLUESCREEN UI204 ACTOR "+json_stringify(_row));
    }
}
function scrFRBluescreenUITestsBeforeInput() {
    var _s=scrFRBluescreenUITestsState();
    if(is_undefined(_s)) return;
    var _samples=[];
    for(var _i=0;_i<5;++_i) array_push(_samples,{x:0,y:0,held:false,pressed:false,released:false});
    if((_s.phase==2 || _s.phase==3) && instance_exists(_s.controller)
        && _s.controller.blueTime>=90) {
        // Begin this touch well before source tick115 creates either button.
        // Holding it over a future button must not synthesize a fresh press.
        var _first=!(_s[$ "stale_started"]??false),
            _wx=_s.controller.x+(_s.accept?-87:-16),_wy=_s.controller.y+51;
        _samples[4]={x:(_wx-view_xview)*gui_w/view_width,
            y:(_wy-view_yview)*gui_h/view_height,held:true,pressed:_first,released:false};
        if(_first) {
            _s.stale_started=true;
            _s.stale_press={host:_s.host,frame:current_frame,blueTime:_s.controller.blueTime,
                x:_samples[4].x,y:_samples[4].y};
            scrNTTESmokeLog("BLUESCREEN UI204 PREEXISTING HELD TOUCH "+json_stringify(_s.stale_press));
        }
    }
    if(_s.phase==4 && _s.input_stage<3) {
        // A 60 Hz press/release pair occupies only two physical frames. The
        // production pointer queue must carry it into the source UI's30Hz step.
        var _press=_s.input_stage==1,_button=_s.button,
            _x=(_s.tap_world[0]-view_xview)*gui_w/view_width,
            _y=(_s.tap_world[1]-view_yview)*gui_h/view_height;
        _samples[4]={x:_x,y:_y,held:_press,pressed:_press,released:!_press};
        array_push(_s.input_frames,{host:_s.host,hardware_frame:global.__input_frame,
            frame:current_frame,ready:scrFRReadyTick(),
            serial:scrFRLogicSerial(),touch:4,x:_x,y:_y,held:_press,pressed:_press,
            released:!_press,button:real(_button),view:[view_xview,view_yview]});
        _s.input_stage++;
        scrNTTESmokeLog("BLUESCREEN UI204 RAW TOUCH "+json_stringify(_s.input_frames[array_length(_s.input_frames)-1]));
        scrFRBluescreenUITestsWrite(_s);
    }
    global.fr_touch_input_fixture={active:true,samples:_samples};
}
function scrFRBluescreenUITestsStart(_driver,_rate=30,_accept=true,_entry_mode="eligible") {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_number(Player)==1 && !instance_exists(GenCont),
        "Bluescreen UI acceptance requires the isolated live native runner");
    save_set_value("options","framerate",_rate);save_set_value("options","autopause",false);
    save_set_value("visual","freezeframes",0);save_set_value("visual","bossintro",false);
    scrOptionsUpdate();scrNTTEFullRateApply();
    UberCont.opt_autopause=false;UberCont.paused=false;UberCont.opt_freeze=0;
    UberCont.want_quit_to_menu=false;UberCont.want_restart=false;UberCont.want_menu=false;
    global.__debug_immortality=false;UberCont.opt_practice=false;
    var _p=instance_find(Player,0);
    global.index=_p.index;
    scrFRModSet("area","cyberspace","settingCyberspaceEnabled",_entry_mode!="disabled");
    UberCont.opt_keyboard=false;UberCont.opt_gamepad=false;KeyCont.touch[_p.index]=true;
    global.fr_touch_input=undefined;
    _driver.fr_bluescreen_ui={rate:_rate,accept:_accept,entry_mode:_entry_mode,
        eligible:_entry_mode=="eligible",slot:_p.index,phase:-2,host:0,
        ticks:0,draws:0,drawn_host:-1,draw_counts:{},connection_draws:0,denial_draws:0,controller:noone,button:noone,
        input_stage:0,input_frames:[],observations:[],snapshots:[],player:_p,
        start_frame:current_frame,entry_area:GameCont.area,entry_subarea:GameCont.subarea};
    scrFRBluescreenUITestsBeforeInput();
    scrFRBluescreenUITestsSnapshot(_driver.fr_bluescreen_ui,"start");
    // Generic smoke bootstrap does not perform a native level_start. Reuse
    // EventTests' authenticated room disposal/async GenCont boundary so the
    // real source Wibbly manager is created by ordinary generation.
    _driver.fr_event_index=0;
    scrFREventTestsPrepare(_driver,1,1,0,[]);
}
function scrFRBluescreenUITestsStep(_driver) {
    var _s=_driver.fr_bluescreen_ui;
    _s.host++;
    scrFRBluescreenUITestsCheck(_s,_s.host<_s.rate*70,
        "Bluescreen UI scheduled lifecycle exceeded70seconds");
    if(scrFRReadyTick()) _s.ticks++;
    if(_s.eligible && ((_s.phase>=1 && _s.phase<=3) || (_s.phase==4 && _s.input_stage==0)))
        scrFRBluescreenUITestsCheck(_s,!instance_exists(GameOver),
            "Native GameOver raced the authored Robot admission/revive before its real YES/NO choice");
    if(_s.eligible && _s.accept && _s.phase>=5 && _s.phase<=7)
        scrFRBluescreenUITestsCheck(_s,!instance_exists(GameOver),
            "Accepted Robot admission retained native GameOver during its real Cyberspace handoff/gameplay");
    if(_s.phase==-2) {
        if(instance_exists(_driver.fr_event_room_marker)) return false;
        scrFREventTestsGenerate(_driver);_s.phase=-1;_s.warm_ticks=0;return false;
    }
    if(_s.phase==-1) {
        if(instance_exists(GenCont) || instance_exists(FloorMaker) || scrGameIsGenerationScreen()
            || !instance_exists(Player)) return false;
        if(scrFRReadyTick()) _s.warm_ticks++;
        if(_s.warm_ticks<24) return false;
        var _managers=scrFREventTestsNamed(FRCustomObject,"wib_PlayerManager");
        scrFRBluescreenUITestsCheck(_s,array_length(_managers)==1,
            "Actual asynchronous generation did not create its ordinary source Wibbly PlayerManager");
        _s.player=scrFRPlayerFind(_s.slot);_s.manager=real(_managers[0]);
        scrFRPlayerSetRace(_s.slot,"robot");scrFRPlayerSetSkin(_s.slot,0);
        GameCont.fr_visitedCyberspace=_s.entry_mode=="visited";
        GameCont.win=false;GameCont.is_level_ended=false;
        global.__debug_immortality=false;UberCont.opt_practice=false;
        UberCont.opt_keyboard=false;UberCont.opt_gamepad=false;KeyCont.touch[_s.slot]=true;
        _s.phase=0;_s.ticks=0;scrFRBluescreenUITestsSnapshot(_s,"authentic-level-start");return false;
    }
    if(_s.phase==0) {
        if(_s.ticks<8) return false;
        var _p=scrFRPlayerFind(_s.slot);
        scrFRBluescreenUITestsCheck(_s,instance_exists(_p),"Natural Robot disappeared before requested fatal damage");
        var _manager=_s.manager;
        scrFRBluescreenUITestsCheck(_s,instance_exists(_manager)
            && _manager.livingPlayers[_s.slot]==1 && _manager.playerRace[_s.slot]=="robot",
            "Authentic Wibbly manager did not observe the living Robot before real fatal damage");
        _s.manager_before_death={id:real(_manager),slot:_s.slot,
            living:_manager.livingPlayers[_s.slot],race:_manager.playerRace[_s.slot],
            x:_manager.playerX[_s.slot],y:_manager.playerY[_s.slot]};
        _s.death_at=_s.host;_s.phase=1;
        with(_p) {nexthurt=0;spirit=false;spirit_index=0;scr_hit_self(1000000);}
        scrFRBluescreenUITestsSnapshot(_s,"fatal-damage-requested");return false;
    }
    if(_s.phase==1) {
        var _controllers=scrFREventTestsNamed(FRCustomObject,"fr_bluescreenController");
        if(!_s.eligible) {
            scrFRBluescreenUITestsCheck(_s,array_length(_controllers)==0
                && array_length(scrFRBluescreenUITestsButtons())==0,
                "Disabled/already-visited Cyberspace incorrectly admitted a dead Robot");
            if(instance_exists(Player) || !instance_exists(GameOver)) return false;
            _s.native_death_at=_s.host;_s.deathcause=GameCont.deathcause;_s.phase=10;
            scrFRBluescreenUITestsSnapshot(_s,"ineligible-native-gameover");return false;
        }
        if(array_length(_controllers)==0) return false;
        scrFRBluescreenUITestsCheck(_s,array_length(_controllers)==1 && GameCont.fr_visitedCyberspace
            && instance_number(Player)==1 && scrFRPlayerRace(_s.slot)=="robot",
            "Genuine Robot death failed its one authored native admission/revive");
        _s.controller=_controllers[0];_s.player=scrFRPlayerFind(_s.slot);
        _s.deathcause=GameCont.deathcause;_s.phase=2;
        scrFRBluescreenUITestsSnapshot(_s,"natural-controller");return false;
    }
    if(_s.phase==2) {
        var _buttons=scrFRBluescreenUITestsButtons();
        if(array_length(_buttons)==0) return false;
        scrFRBluescreenUITestsSnapshot(_s,"natural-buttons");
        scrFRBluescreenUITestsCheck(_s,array_length(_buttons)==2,"Natural admission UI did not create exactly YES and NO");
        _s.button_ids=[];
        for(var _i=0;_i<2;++_i) {
            var _button=_buttons[_i];array_push(_s.button_ids,real(_button));
            scrFRBluescreenUITestsCheck(_s,_button.creator==_s.controller,
                "Natural admission button creator is not its live bluescreen controller");
            if(_button.yesButton==_s.accept) _s.button=_button;
        }
        scrFRBluescreenUITestsCheck(_s,instance_exists(_s.button),"Natural admission omitted the requested YES/NO button");
        _s.visible_after=_s.draws+3;_s.phase=3;return false;
    }
    if(_s.phase==3) {
        if(_s.draws<_s.visible_after) return false;
        var _button=_s.button,_bx=_button.x-sprite_get_xoffset(_button.sprite_index),
            _by=_button.y-sprite_get_yoffset(_button.sprite_index);
        _s.tap_world=[_bx+sprite_get_width(_button.sprite_index)/2,
            _by+sprite_get_height(_button.sprite_index)/2];
        scrFRBluescreenUITestsSnapshot(_s,"drawn-before-input");
        if(surface_exists(application_surface)) surface_save(application_surface,
            working_directory+"frontier-bluescreen-ui204-before.png");
        scrFRBluescreenUITestsCheck(_s,_button.visible && _button.image_alpha>0
            && point_in_rectangle(_s.tap_world[0],_s.tap_world[1],view_xview,view_yview,
                view_xview+view_width,view_yview+view_height),
            "Natural admission button vanished outside the camera-relative visible blue UI");
        for(var _i=0;_i<array_length(_s.button_ids);++_i)
            scrFRBluescreenUITestsCheck(_s,(_s.draw_counts[$ string(_s.button_ids[_i])]??0)>=2,
                "Naturally generated admission button did not draw on two actual host frames");
        _s.phase=4;_s.click_at=_s.host;return false;
    }
    if(_s.phase==4) {
        if(_s.input_stage<3) return false;
        var _buttons=scrFRBluescreenUITestsButtons();
        if(array_length(_buttons)>0) {
            scrFRBluescreenUITestsCheck(_s,_s.host-_s.click_at<12,
                "Raw touch failed the naturally generated YES/NO button or deferred End Step cleanup");
            return false;
        }
        _s.clicked_at=_s.host;_s.phase=5;
        scrFRBluescreenUITestsCheck(_s,is_struct(_s[$ "actual_click"]??undefined)
            && _s.actual_click.self==real(_s.button) && _s.actual_click.click==_s.slot,
            "Deferred admission cleanup lacked an actual scheduled native button clickIndex");
        scrFRBluescreenUITestsSnapshot(_s,"after-touch-and-endstep");
        if(_s.accept) {
            scrFRBluescreenUITestsCheck(_s,instance_exists(_s.controller)
                && _s.controller.drawConnect && GameCont.area==302 && GameCont.subarea==0
                && instance_exists(Portal),"Natural raw YES did not preserve its connection UI and genuine Portal");
            _s.portal=real(instance_find(Portal,0));
        } else scrFRBluescreenUITestsCheck(_s,!instance_exists(_s.controller)
            && !instance_exists(Player) && GameCont.deathcause==_s.deathcause,
            "Natural raw NO failed original deathcause/player/controller disposal");
        return false;
    }
    if(_s.phase==5) {
        if(_s.host-_s.clicked_at==3 || _s.host-_s.clicked_at==15)
            scrFRBluescreenUITestsSnapshot(_s,"postclick-later-frame");
        if(_s.accept) {
            if(instance_exists(_s.controller)) {
                scrFRBluescreenUITestsCheck(_s,_s.controller.drawConnect,
                    "YES lost its original reboot UI before native portal transition");
                return false;
            }
            if(!is_real(_s[$ "handoff_at"]??undefined)) {
                _s.handoff_at=_s.host;scrFRBluescreenUITestsSnapshot(_s,"native-portal-room-handoff");
            }
            if(instance_exists(GenCont) || instance_exists(FloorMaker) || scrGameIsGenerationScreen()) return false;
            if(GameCont.area==302 && GameCont.subarea==1 && instance_number(Floor)==0
                && _s.host-_s.handoff_at<_s.rate*15) return false;
            scrFRBluescreenUITestsCheck(_s,GameCont.area==302 && GameCont.subarea==1
                && instance_exists(Player) && instance_number(Floor)>0,
                "YES delayed native Portal lifecycle did not generate actual Cyberspace");
            scrFRBluescreenUITestsCheck(_s,_s.connection_draws>=2,
                "YES lost the real reboot/connection Draw callback before its native transition");
            _s.destination_at=_s.host;_s.phase=6;return false;
        }
        if(!instance_exists(GameOver) || _s.host-_s.clicked_at<30*_s.rate/30) return false;
        scrFRBluescreenUITestsCheck(_s,!instance_exists(Player)
            && array_length(scrFRBluescreenUITestsButtons())==0
            && GameCont.deathcause==_s.deathcause,"NO revived/replayed or changed deathcause on a later native frame");
        scrFRBluescreenUITestsCheck(_s,_s.denial_draws>=2,
            "NO lost its authored denial Draw binding after deferred button disposal");
        _s.phase=7;
    }
    if(_s.phase==6) {
        if(_s.host-_s.destination_at<_s.rate) return false;
        scrFRBluescreenUITestsCheck(_s,instance_exists(Player) && GameCont.area==302
            && GameCont.subarea==1 && array_length(scrFRBluescreenUITestsButtons())==0,
            "Cyberspace admission regressed during later actual gameplay frames");
        _s.phase=7;
    }
    if(_s.phase==10) {
        if(_s.host-_s.native_death_at<_s.rate) return false;
        scrFRBluescreenUITestsCheck(_s,!instance_exists(Player) && instance_exists(GameOver)
            && array_length(scrFREventTestsNamed(FRCustomObject,"fr_bluescreenController"))==0
            && array_length(scrFRBluescreenUITestsButtons())==0
            && GameCont.deathcause==_s.deathcause,
            "Disabled/already-visited native death failed its later ordinary GameOver lifecycle");
        _s.phase=7;
    }
    if(_s.phase==7) {
        _s.final=scrFRBluescreenUITestsSnapshot(_s,"accepted");
        if(surface_exists(application_surface)) surface_save(application_surface,
            working_directory+"frontier-bluescreen-ui204-after.png");
        scrFRBluescreenUITestsWrite(_s,true);
        scrNTTESmokeLog("BLUESCREEN UI204 ACCEPTED "+json_stringify({rate:_s.rate,accept:_s.accept,
            frames:_s.host,input:_s.input_frames,final:_s.final}));
        _s.phase=8;return true;
    }
    return _s.phase==8;
}
