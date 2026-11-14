// Drive genuine General -> gamepad / JoystickAttack + ButtonActive sampling,
// then let the ordinary Player weapon and source race EndStep run themselves.
function scrFRBubblesAttack212TestsState() {
    if(os_type!=os_windows || !scrNTTEFullSmokeEnabled()) return undefined;
    var _state=undefined;
    with(FRIntegrationTest) if(variable_instance_exists(id,"fr_bubbles_attack212")) {
        _state=fr_bubbles_attack212;break;
    }
    return _state;
}

function scrFRBubblesAttack212TouchState() {
    var _state=scrFRBubblesAttack212TestsState();
    return is_struct(_state) && _state.active && _state.tick>=48?_state:scrFRBubblesAttack205TouchState();
}

function scrFRBubblesAttack212TestsRound(_state) {
    var _rate=_state.round==0?30:60,_p=instance_find(Player,0);
    save_set_value("options","framerate",_rate);scrOptionsUpdate();
    game_set_speed(_rate,gamespeed_fps);global.time_scale=30/_rate;
    scrFRPlayerSetRace(_p.index,"bubbles");
    assert(_p.race==19 && scr_playerinstance_find(_p.index).race==19,
        "Bubbles212 fixture did not enter the real unlocked native Bubbles race");
    _p.wep=wep_machinegun;_p.bwep=wep_revolver;
    _p.ntte_state=undefined;_p.bntte_state=undefined;
    _p.reload=0;_p.can_shoot=true;_p.can_spec=true;_p.can_aim=true;_p.visible=true;
    _p.ammo[Ammo.Bullets]=200;
    _p.bubbles_maxBubbleCharge=300;_p.bubbles_bubbleCharge=300;_p.bubbles_bubbleCooldown=0;
    _p.hp=100000;_p.max_hp=100000;_p.nexthurt=current_frame+100000;
    _p.fr_bubbles_attack_mode205=false;
    // The host's settled smoke Player can retain an attack sampled before
    // this fixture takes over. Start at a clean physical release boundary.
    _p.clicked=false;
    KeyCont.hold_fire[_p.index]=false;KeyCont.press_fire[_p.index]=false;
    KeyCont.release_fire[_p.index]=false;
    KeyCont.hold_spec[_p.index]=false;KeyCont.press_spec[_p.index]=false;
    KeyCont.release_spec[_p.index]=false;
    save_set_value("cprefs","bubbles",true);scrOptionsUpdate();
    KeyCont.activeforever[_p.index]=false;
    UberCont.opt_keyboard=false;UberCont.opt_gamepad=true;
    UberCont.opt_aimbot=false;UberCont.opt_assist=false;
    UberCont.opt_splitfire=false;UberCont.opt_stickregions=false;
    UberCont.block_input_frames=0;UberCont.block_input_fire=false;
    is_mobile=true;global.console_active=false;keymap_ret_nogamepad=false;
    var _pad={fire_held:false,fire_pressed:false,fire_released:false,
        spec_held:false,spec_pressed:false,spec_released:false};
    _pad.get_held=method(_pad,function(_key) {
        return _key==gp_shoulderr?fire_held:(_key==gp_face1?spec_held:false);
    });
    _pad.get_pressed=method(_pad,function(_key) {
        return _key==gp_shoulderr?fire_pressed:(_key==gp_face1?spec_pressed:false);
    });
    _pad.get_released=method(_pad,function(_key) {
        return _key==gp_shoulderr?fire_released:(_key==gp_face1?spec_released:false);
    });
    _pad.get_value=method(_pad,function(_axis) {return _axis==gp_axisrh?1:0;});
    Key.fire=[-1,gp_shoulderr];Key.spec=[-1,gp_face1];
    Key.pick=[-1,gp_face2];Key.swap=[-1,gp_face3];Key.horn=[-1,gp_select];Key.scythe=[-1,gp_face4];
    _state.pad=_pad;_state.player=_p;_state.tick=0;_state.active=true;_state.rate=_rate;
    _state.ammo=200;_state.charge=300;_state.idle_charge=300;
    _state.touch={held:false,pressed:false,released:false};
    _state.stick=instance_exists(JoystickAttack)?instance_find(JoystickAttack,0):instance_create(0,0,JoystickAttack);
    _state.button=instance_exists(ButtonActive)?instance_find(ButtonActive,0):instance_create(0,0,ButtonActive);
    _state.stick.index=-1;_state.stick.hold=0;_state.stick.dis=0;
    _state.button.volume_control_command=0;
}

function scrFRBubblesAttack212TestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && !instance_exists(GenCont) && !instance_exists(MenuOptions),
        "Bubbles212 needs the settled isolated native runner");
    var _state={active:false,round:0,tick:0,ticks:0,rate:30,
        pad:undefined,original_pads:global.__input_gamepads,rows:[],
        original_unlock:scrFRModCallArray("mod","libSaves","save_get",["Frontier","unlock_bubbles"])};
    _driver.fr_bubbles_attack212=_state;
    scrFRBubblesPreference212Tests();
    // A new isolated save has not unlocked Bubbles. Its source create()
    // correctly falls back to Fish until this genuine unlock entry is set.
    scrFRModCallArray("mod","libSaves","save_set",["Frontier","unlock_bubbles",1]);
    scrFRBubblesAttack212TestsRound(_state);
}

function scrFRBubblesAttack212TestsBeforeInput() {
    var _state=scrFRBubblesAttack212TestsState();
    if(!is_struct(_state) || !_state.active) {scrFRBubblesAttack205TestsBeforeInput();return;}
    var _t=++_state.tick,_p=_state.player,_slot=_p.index,_pad=_state.pad;
    assert(instance_exists(_p),"Bubbles212 lost its actual native Player");
    _p.nexthurt=current_frame+100000;
    _pad.fire_held=(_t>=5 && _t<20) || (_t>=26 && _t<34) || (_t>=37 && _t<44);
    _pad.fire_pressed=_t==5 || _t==26 || _t==37;
    _pad.fire_released=_t==20 || _t==34 || _t==44;
    _pad.spec_held=_t==1 || _t==25 || (_t>=36 && _t<41);
    _pad.spec_pressed=_t==1 || _t==25 || _t==36;
    _pad.spec_released=_t==2 || _t==26 || _t==41;
    if(_t<48) global.__input_gamepads=[_pad];
    if(_t==5) _state.charge=_p.bubbles_bubbleCharge;
    if(_t==22) {
        scrNTTESmokeLog("BUBBLES212 HELD STATE "+json_stringify({race:_p.race,
            charge:_p.bubbles_bubbleCharge,initial_charge:_state.charge,
            ammo:_p.ammo[Ammo.Bullets],can_spec:_p.can_spec,cooldown:_p.bubbles_bubbleCooldown,
            ready:scrFRReadyTick(),paused:UberCont.paused,visible:_p.visible,
            held_spec:KeyCont.hold_spec[_slot],held_fire:KeyCont.hold_fire[_slot],
            mode:KeyCont.activeforever[_slot],rate:_state.rate}));
        assert(_p.bubbles_bubbleCharge<_state.charge && _p.ammo[Ammo.Bullets]<200,
            "Real held controller attack did not fire both the weapon and source bubbles");
        _state.idle_charge=_p.bubbles_bubbleCharge;
    }
    if(_t==25) {
        assert(_p.bubbles_bubbleCharge>=_state.idle_charge,
            "Released controller attack continued consuming Bubbles ability charge");
        _state.ammo=_p.ammo[Ammo.Bullets];
    }
    if(_t==36) {
        assert(_p.ammo[Ammo.Bullets]<_state.ammo,"Controller weapon attacks stopped when bubble mode was turned off");
        _state.ammo=_p.ammo[Ammo.Bullets];_state.charge=_p.bubbles_bubbleCharge;
        save_set_value("cprefs","bubbles",false);scrOptionsUpdate();
        UberCont.opt_gamepad=true;UberCont.opt_keyboard=false;
    }
    if(_t==46) {
        assert(_p.ammo[Ammo.Bullets]<_state.ammo && _p.bubbles_bubbleCharge<_state.charge,
            "Disabled controller preference lost original independent weapon/hold-ability controls");
        save_set_value("cprefs","bubbles",true);scrOptionsUpdate();
        UberCont.opt_gamepad=true;UberCont.opt_keyboard=false;
    }
    if(_t==48) {
        UberCont.opt_gamepad=false;UberCont.opt_keyboard=false;
        global.__input_gamepads=_state.original_pads;
        KeyCont.activeforever[_slot]=false;
        _state.ammo=_p.ammo[Ammo.Bullets];
        _state.stick.index=-1;_state.stick.hold=0;_state.stick.dis=0;
    }
    if(_t>=48) {
        _state.touch={held:(_t>=54 && _t<69) || (_t>=74 && _t<79) || (_t>=86 && _t<90),
            pressed:_t==54 || _t==74 || _t==86,released:_t==69 || _t==79 || _t==90};
        if(_t==50 || _t==72) _state.button.volume_control_command=1;
        if(_t==54) _state.charge=_p.bubbles_bubbleCharge;
        if(_t==70) _state.idle_charge=_p.bubbles_bubbleCharge;
        if(_t==72) {
            assert(_p.bubbles_bubbleCharge<_state.charge
                && _p.bubbles_bubbleCharge>=_state.idle_charge && _p.ammo[Ammo.Bullets]<_state.ammo,
                "Real JoystickAttack/Bubbles touch mode failed simultaneous weapon/bubble fire or release");
            _state.ammo=_p.ammo[Ammo.Bullets];
        }
        if(_t==84) {
            assert(_p.ammo[Ammo.Bullets]<_state.ammo,"Switching real touch ability mode off did not restore weapon attacks");
            _state.ammo=_p.ammo[Ammo.Bullets];_state.charge=_p.bubbles_bubbleCharge;
            save_set_value("cprefs","bubbles",false);scrOptionsUpdate();
            UberCont.opt_gamepad=false;UberCont.opt_keyboard=false;
        }
        if(_t>=85 && _t<90) _state.button.volume_control_command=_t==85?1:2;
        if(_t==90) _state.button.volume_control_command=-1;
        if(_t==94) assert(_p.ammo[Ammo.Bullets]<_state.ammo
            && _p.bubbles_bubbleCharge<_state.charge,
            "Disabled touch preference lost original independently held ability and weapon input");
    }
    // scrOptionsUpdate intentionally reloads real saved bindings when the
    // preference changes. Reattach this virtual controller's explicit map
    // after that reload, just as a configured connected device would use it.
    if(_t<48) {
        Key.fire=[-1,gp_shoulderr];Key.spec=[-1,gp_face1];
        Key.pick=[-1,gp_face2];Key.swap=[-1,gp_face3];
        Key.horn=[-1,gp_select];Key.scythe=[-1,gp_face4];
    }
}

function scrFRBubblesAttack212TestsAfterInput() {
    var _state=scrFRBubblesAttack212TestsState();
    if(!is_struct(_state) || !_state.active) {scrFRBubblesAttack205TestsAfterInput();return;}
    var _t=_state.tick,_slot=_state.player.index;
    if(_t==1 || _t==4 || _t==50 || _t==53) {
        scrNTTESmokeLog("BUBBLES212 IDLE INPUT "+json_stringify({tick:_t,rate:_state.rate,
            slot:_slot,index:global.index,race:_state.player.race,
            mode:KeyCont.activeforever[_slot],held_spec:KeyCont.hold_spec[_slot],
            pressed_spec:KeyCont.press_spec[_slot],held_fire:KeyCont.hold_fire[_slot],
            pressed_fire:KeyCont.press_fire[_slot],raw_spec:key_check("spec",keystate_press),
            raw_fire:key_check("fire",keystate_hold),preference:scr_player_pref(scr_playerinstance_find(_slot),"bubbles"),
            gamepad:UberCont.opt_gamepad,keyboard:UberCont.opt_keyboard,
            blocked:scrFRBubblesInputBlocked(),menu:instance_exists(MenuOptions),
            generation:instance_exists(GenCont),transition:instance_exists(LevCont),
            paused:scrGameIsPaused(),locked:scrGameIsLockState()}));
        assert(KeyCont.activeforever[_slot] && !KeyCont.hold_spec[_slot],
            "Turning Bubbles mode on started the ability without ordinary attack input");
    }
    if((_t>=5 && _t<20) || (_t>=54 && _t<69))
        assert(KeyCont.hold_spec[_slot] && KeyCont.hold_fire[_slot]
            && KeyCont.press_spec[_slot]==KeyCont.press_fire[_slot]
            && KeyCont.release_spec[_slot]==KeyCont.release_fire[_slot]
            && !scrFRBubblesWeaponBlocked205(_state.player),
            "Actual input producers did not preserve weapon input while adding Bubbles ability");
    if(_t==21 || _t==24 || _t==70 || _t==71)
        assert(!KeyCont.hold_spec[_slot],"Released real attack retained a latched bubble spray");
    if(_t==26 || _t==74)
        assert(!KeyCont.activeforever[_slot] && KeyCont.hold_fire[_slot]
            && !scrFRBubblesWeaponBlocked205(_state.player),"Disabled ability mode retained weapon suppression");
    if(_t==36 || _t==86)
        assert(!KeyCont.activeforever[_slot] && KeyCont.hold_spec[_slot],
            "Disabled preference did not retain the source hold-to-spray path");
}

function scrFRBubblesAttack212TestsStep(_driver) {
    var _state=_driver.fr_bubbles_attack212;
    assert(++_state.ticks<600,"Bubbles212 actual input/Player source-step acceptance timed out");
    if(_state.tick<95) return false;
    array_push(_state.rows,{rate:_state.rate,actual_general:true,controller_named_buttons:true,
        touch_joystick_and_ability:true,idle_no_spray:true,release_stops:true,
        weapon_simultaneous:true,mode_off_fires:true,preference_off_original_controls:true});
    scrNTTESmokeLog("NTUF BUBBLES212 "+json_stringify(_state.rows[array_length(_state.rows)-1]));
    _state.active=false;
    if(++_state.round<2) {scrFRBubblesAttack212TestsRound(_state);return false;}
    global.__input_gamepads=_state.original_pads;
    scrFRModCallArray("mod","libSaves","save_set",["Frontier","unlock_bubbles",_state.original_unlock]);
    scrNTTESmokeLog("PASS NTUF BUBBLES212 actual General + native controller + touch JoystickAttack/ButtonActive + real Player firing/source race EndStep at30/60Hz");
    return true;
}
