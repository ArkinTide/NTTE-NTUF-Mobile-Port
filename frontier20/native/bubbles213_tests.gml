function scrFRBubbles213TouchState() {
    if(os_type!=os_windows || !scrNTTEFullSmokeEnabled()) return undefined;
    return variable_global_exists("fr_bubbles_touch213_fixture")
        ?global.fr_bubbles_touch213_fixture:undefined;
}

function scrFRBubbles213SlashCount(_player) {
    var _count=0;
    with(Slash) if(object_index==Slash && creator==_player) _count++;
    return _count;
}

function scrFRBubbles213Sample(_state,_held,_pressed,_released,_dx,_dy=0) {
    _state.touch={held:_held,pressed:_pressed,released:_released,dx:_dx,dy:_dy};
    with(UberCont) scrHandleInputsGeneral(global.index);
    with(_state.player) {scrPlayerFiring();scrFRRaceCall("step");}
}

// Real General -> JoystickAttack / ButtonActive -> final ability mapper ->
// PlayerFiring / source Cutlass and Shovel / source ability callbacks. Only
// raw device samples are injected; production firing gates own the attack.
function scrFRBubbles213Tests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFRReadyTick()
        && !instance_exists(MenuOptions),"Bubbles213 requires a ready isolated source tick");
    var _before=scrNTTEFullInstances(all),_uber=scrNTTEFullAreaGeneratorSnapshot(UberCont),
        _game=scrNTTEFullAreaGeneratorSnapshot(GameCont),
        _mobile_ui=scrNTTEFullAreaGeneratorSnapshot(MobileUI),
        _keys=KeyCont,_index=global.index,_mobile=is_mobile,
        _console=global.console_active,_slot=INPUT_MAX_PLAYERS-1,
        _old_pinst=global.playerinstance_list[_slot],
        _unlock=scrFRRaceTestsSaveGet("unlock_bubbles"),
        _runs=scrFRRaceTestsSaveGet("bubbles_runs"),
        _preference=save_get_value("cprefs","bubbles",true),
        _seed=scrFRSourceRandomGetSeed(),_rows=[];
    assert(!instance_exists(scrFRPlayerFind(_slot)),"Bubbles213 needs a free native player slot");
    var _vars=["lastTime","lastKills","lastLoop","lastBubbles"],_values=[];
    for(var _v=0;_v<array_length(_vars);++_v) array_push(_values,scrFRRaceVar(_vars[_v]));
    try {
        KeyCont=json_parse(json_stringify(KeyCont));global.index=_slot;is_mobile=true;
        global.console_active=false;
        scrFRRaceTestsSaveSet("unlock_bubbles",true);
        global.playerinstance_list[_slot]=new PlayerInstance(_slot);
        var _p=scrPlayerCreate(_slot,19,0);
        global.playerinstance_list[_slot].race=19;
        _p.x=10016;_p.y=10016;_p.wep=FR_BUBBLES_CUTLASS;
        _p.can_spec=true;_p.can_aim=true;_p.hp=10000;_p.max_hp=10000;
        save_set_value("cprefs","bubbles",true);scrOptionsUpdate();
        // This isolated extra PlayerInstance is deliberately not my_player.
        // scrOptionsUpdate refreshes only the genuine local owner's bitset;
        // hydrate the fixture's preferences through the same native method.
        global.playerinstance_list[_slot].update_cprefs();
        assert(scr_player_pref(global.playerinstance_list[_slot],"bubbles"),
            "Bubbles213 virtual player did not load its enabled saved preference");
        UberCont.opt_keyboard=false;UberCont.opt_gamepad=false;
        UberCont.opt_aimbot=false;UberCont.opt_assist=false;
        UberCont.opt_splitfire=false;UberCont.opt_stickregions=false;
        UberCont.block_input_frames=0;UberCont.block_input_fire=false;
        var _stick=instance_find(JoystickAttack,0);
        if(!instance_exists(_stick)) _stick=instance_create(0,0,JoystickAttack);
        var _button=instance_find(ButtonActive,0);
        if(!instance_exists(_button)) _button=instance_create(0,0,ButtonActive);
        _button.volume_control_command=0;
        var _state={player:_p,touch:{held:false,pressed:false,released:false,dx:0,dy:0}};
        global.fr_bubbles_touch213_fixture=_state;
        for(var _mode=0;_mode<2;++_mode) for(var _weapon=0;_weapon<2;++_weapon) {
            _p.wep=_weapon?FR_BUBBLES_SHOVEL:FR_BUBBLES_CUTLASS;
            for(var _gesture=0;_gesture<4;++_gesture) {
                _p.reload=0;_p.can_shoot=true;_p.clicked=false;
                _p.bubbles_bubbleCharge=300;_p.bubbles_maxBubbleCharge=300;
                _p.bubbles_bubbleCooldown=0;
                KeyCont.activeforever[_slot]=_mode;
                _stick.index=-1;_stick.fr_bubbles_touch213=undefined;
                var _slashes=scrFRBubbles213SlashCount(_p),_bubbles=scrFRRaceVar("lastBubbles");
                // Gesture0: ordinary release outside the dead zone.
                // Gesture1: valid aim -> held centre -> centre release.
                // Gesture2: valid aim -> explicit outside cancellation.
                // Gesture3: centre-only tap must never fire.
                var _initial=_gesture==3?0:1;
                scrFRBubbles213Sample(_state,true,true,false,_gesture==1?0:_initial,_gesture==1?-1:0);
                assert(scrFRBubbles213SlashCount(_p)==_slashes,
                    "Bubbles213 changed the authored semi-automatic press/hold policy");
                assert((scrFRRaceVar("lastBubbles")>_bubbles)==(_mode && _initial>0),
                    "Bubbles213 skill ON/OFF lost the real held bubble ability path");
                if(_gesture==1) {
                    scrFRBubbles213Sample(_state,true,false,false,0);
                    assert(!KeyCont.press_fire[_slot] && !KeyCont.hold_fire[_slot],
                        "Returning to centre fired before the actual release");
                }
                if(_gesture==2) scrFRBubbles213Sample(_state,true,false,false,4);
                scrFRBubbles213Sample(_state,false,false,true,_gesture==0?1:0);
                var _fires=_gesture<2?1:0;
                assert(scrFRBubbles213SlashCount(_p)==_slashes+_fires,
                    "Bubbles213 real sword release/cancel count incorrect: "+string(_gesture));
                if(_gesture==1) assert(KeyCont.press_fire[_slot]
                    && KeyCont.dis_fire[_slot]>0
                    && abs(angle_difference(KeyCont.dir_fire[_slot],90))<.0001,
                    "Centre release lost the last effective aim direction");
                scrFRBubbles213Sample(_state,false,false,false,0);
                assert(!KeyCont.press_fire[_slot]
                    && scrFRBubbles213SlashCount(_p)==_slashes+_fires,
                    "Bubbles213 repeated an already consumed manual release");
                array_push(_rows,{skill:_mode,weapon:_p.wep,gesture:_gesture,slashes:_fires});
            }
        }
    } finally {
        global.fr_bubbles_touch213_fixture=undefined;
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        global.playerinstance_list[_slot]=_old_pinst;
        scrFRRaceTestsSaveSet("unlock_bubbles",_unlock);scrFRRaceTestsSaveSet("bubbles_runs",_runs);
        for(var _v=0;_v<array_length(_vars);++_v) scrFRModSet("race","bubbles",_vars[_v],_values[_v]);
        save_set_value("cprefs","bubbles",_preference);scrOptionsUpdate();
        scrNTTEFullAreaGeneratorRestore(_uber);scrNTTEFullAreaGeneratorRestore(_game);
        scrNTTEFullAreaGeneratorRestore(_mobile_ui);
        KeyCont=_keys;global.index=_index;is_mobile=_mobile;global.console_active=_console;
        scrFRSourceRandomSetSeed(_seed);
    }
    scrNTTESmokeLog("PASS BUBBLES213 actual General/touch/source sword+ability; "+json_stringify(_rows));
}
