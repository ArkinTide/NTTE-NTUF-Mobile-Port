// Explicit desktop acceptance: use the real native fire/reload/table/HUD
// consumers and compare their visual state to each authored source callback.
function scrFRWeaponVisualTestsPrepare(_player,_weapon) {
    with(_player) {
        x=390000;y=390000;speed=0;gunangle=0;accuracy=0;race=Race.Fish;
        wep=_weapon;bwep=wep_none;wepangle=120;wepflip=1;wkick=0;
        bwepangle=0;bwepflip=1;bwkick=0;reload=0;breload=0;can_shoot=true;bcan_shoot=true;
        curse=0;ntte_red_ammo=0;
        infammo=30;ammo=array_create(Ammo.NUM_AMMO_TYPES,1000);
        ntte_state=scrNTTENewState(_weapon);bntte_state=undefined;
        fr_source_wep=undefined;fr_source_bwep=undefined;
        var _source=scrFRWeaponPrepare(_weapon,true);
        // Release one real logical tick of charge. Powder Hammer deliberately
        // has no attack for a zero-charge release; it is not a swing failure.
        if(is_struct(_source) && variable_struct_exists(_source,"chrg")) {
            _source.chrg=-1;_source.chrg_num=1;
        }
    }
}

function scrFRWeaponVisualTestsRetire(_before) {
    var _new=scrNTTEFullMergedRuntimeNew(_before);
    for(var _i=array_length(_new)-1;_i>=0;--_i)
        if(instance_exists(_new[_i])) instance_destroy(_new[_i],false);
}

function scrFRWeaponVisualTestsTables() {
    var _keys=global.fr_weapon_keys,_scripts=global.fr_module_scripts,
        _ids=variable_struct_get_names(_keys),_rows=[];
    for(var _i=0;_i<array_length(_ids);++_i) {
        var _raw=real(_ids[_i]);
        array_push(_rows,{weapon:_raw,name:scr_weapon_get_name(_raw),sprite:scr_weapon_get_sprite(_raw),
            melee:scr_weapon_is_melee(_raw),load:scr_weapon_get_load(_raw)});
    }
    var _model=scrNTTEFullWeaponMerge(FR_BUBBLES_CUTLASS,wep_revolver),
        _handle=scrNTTEFullWeaponNative(_model),_name=scr_weapon_get_name(_handle),
        _physical=scrNTTEFullWeaponNativeState(_handle),_max=maxwep;
    with(UberCont) scrWeapons();
    assert(maxwep==_max && global.fr_weapon_keys==_keys && global.fr_module_scripts==_scripts,
        "Native table rebuild lost the declared Frontier range or source registry");
    for(var _i=0;_i<array_length(_rows);++_i) {
        var _row=_rows[_i],_raw=_row.weapon;
        assert(scr_weapon_is_valid(_raw) && scr_weapon_get_name(_raw)==_row.name
            && scr_weapon_get_sprite(_raw)==_row.sprite && scr_weapon_is_melee(_raw)==_row.melee
            && scr_weapon_get_load(_raw)==_row.load,
            "Native table rebuild lost source name, sprite or melee metadata for "+string(_raw));
    }
    assert(scrNTTEFullWeaponModel(_handle)==_model && scrNTTEFullWeaponNativeState(_handle)==_physical
        && scr_weapon_get_name(_handle)==_name && wep_name[_handle]==_name
        && scr_weapon_is_melee(_handle),
        "Native table rebuild changed a live physical fusion or erased its numeric metadata cache");
    for(var _skin=0;_skin<2;++_skin) {
        var _weapon=scrFRRaceStarterWeapon(_skin),_key=_keys[$ string(_weapon)],
            _name=scrFRWeaponProperty(_key,"weapon_name","");
        assert(scr_weapon_is_valid(_weapon) && sprite_exists(scr_weapon_get_sprite(_weapon))
            && scr_weapon_get_sprite(_weapon)!=sprDefault
            && scr_weapon_get_name(_weapon)==string_upper(_name)
            && string_pos("WEAPON",scr_weapon_get_name(_weapon))!=1,
            "Bubbles A/B starter became invalid, a source-code name or an invisible fallback after table rebuild");
    }
    scrNTTESmokeLog("PASS FRONTIER native scrWeapons rebuild retained77 source metadata rows, both Bubbles starters and a physical fusion");
}

function scrFRWeaponVisualTestsHUDCapture(_player,_kind,_label=undefined) {
    if(is_undefined(_label)) _label=_kind;
    scrNTTESmokeLog("FRONTIER native HUD capture "+_label+" via "+_kind);
    var _surface=-1,_buffer=-1,_camera=-1,_target=false,_success=false,_draw_state=undefined,
        _world=matrix_get(matrix_world),_view=matrix_get(matrix_view),_projection=matrix_get(matrix_projection),
        _font=draw_get_font(),_ha=draw_get_halign(),_va=draw_get_valign(),
        _color=draw_get_color(),_alpha=draw_get_alpha(),_shader=shader_current();
    gpu_push_state();
    try {
        _surface=surface_create(160,96);_buffer=buffer_create(160*96*4,buffer_fixed,1);
        _camera=camera_create_view(0,0,160,96,0,noone,-1,-1,-1,-1);
        assert(surface_exists(_surface) && buffer_exists(_buffer),"Bubbles HUD GPU capture allocation failed");
        surface_set_target(_surface);_target=true;camera_apply(_camera);
        matrix_set(matrix_world,matrix_build_identity());shader_reset();gpu_set_blendmode(bm_normal);
        gpu_set_texfilter(false);gpu_set_fog(false,0,0,0);draw_set_color(c_white);draw_set_alpha(1);
        draw_clear_alpha(c_black,0);
        if(_kind=="native") with(TopCont) scrDrawPlayerHUD(_player,false);
        else if(_kind=="normal") with(TopCont) event_perform(ev_draw,64);
        else if(_kind=="pause") with(UberCont) event_perform(ev_draw,64);
        else if(_kind=="meter" || _kind=="tinted") {
            if(_kind=="tinted") {draw_set_color(c_red);draw_set_alpha(0.25);}
            var _before_color=draw_get_color(),_before_alpha=draw_get_alpha();
            assert(scrFRBubblesHUD(_player),"Bubbles meter refused the native player HUD context");
            if(_kind=="tinted") {
                var _after_color=draw_get_color(),_after_alpha=draw_get_alpha();
                _draw_state={before_color:_before_color,after_color:_after_color,
                        before_alpha:_before_alpha,after_alpha:_after_alpha};
                scrNTTESmokeLog("FRONTIER Bubbles HUD drawing state "+json_stringify(_draw_state));
            }
        }
        else if(_kind=="retired") {
            scrFRModCallArray("mod","Frontier_CharHuds","draw_gui",[]);
            scrFRModCallArray("mod","Frontier_CharHuds","draw_pause",[]);
        }
        surface_reset_target();_target=false;buffer_get_surface(_buffer,_surface,0);
        surface_save(_surface,working_directory+"frontier-bubbles-"+_label+"-hud.png");
        _success=true;return {surface:_surface,pixels:_buffer,state:_draw_state};
    } finally {
        if(_target) surface_reset_target();
        if(_camera>=0) camera_destroy(_camera);
        gpu_pop_state();if(_shader<0) shader_reset();else shader_set(_shader);
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);matrix_set(matrix_projection,_projection);
        draw_set_font(_font);draw_set_halign(_ha);draw_set_valign(_va);
        draw_set_color(_color);draw_set_alpha(_alpha);
        if(!_success) {
            if(surface_exists(_surface)) surface_free(_surface);
            if(buffer_exists(_buffer)) buffer_delete(_buffer);
        }
    }
}

function scrFRWeaponVisualTestsHUD(_player) {
    // The focused smoke world creates Player directly, bypassing GenCont's
    // ordinary TopCont creation. Use its real Create event (and SubTopCont),
    // rather than borrowing the integration driver's scope or fake fields.
    if(!instance_exists(TopCont)) instance_create(0,0,TopCont);
    assert(instance_exists(TopCont) && instance_exists(SubTopCont),
        "Bubbles HUD acceptance could not initialize the real native GUI controllers");
    _player.race=19;_player.bubbles_bubbleCharge=100;_player.bubbles_maxBubbleCharge=100;
    var _captures=[],_pause=UberCont.paused,_want_pause=UberCont.want_pause,
        _want_menu=UberCont.want_menu,_want_restart=UberCont.want_restart,_top_wave=TopCont.wave;
    try {
        _player.hp=_player.max_hp;_player.lsthealth=_player.max_hp;
        _player.drawlowhp=0;_player.fainted=0;_player.bleed=0;_player.nexthurt=current_frame;
        TopCont.wave=pi/2;
        var _meter=scrFRWeaponVisualTestsHUDCapture(_player,"meter");array_push(_captures,_meter);
        var _tinted=scrFRWeaponVisualTestsHUDCapture(_player,"tinted");array_push(_captures,_tinted);
        var _native=scrFRWeaponVisualTestsHUDCapture(_player,"native");array_push(_captures,_native);
        var _retired=scrFRWeaponVisualTestsHUDCapture(_player,"retired");array_push(_captures,_retired);
        assert(!lockstep_stop && instance_exists(TopCont) && !instance_exists(Cinematic),
            "Actual Bubbles GUI acceptance requires the settled ordinary gameplay path");
        UberCont.paused=false;UberCont.want_pause=false;
        var _normal=scrFRWeaponVisualTestsHUDCapture(_player,"normal");array_push(_captures,_normal);
        UberCont.paused=true;UberCont.want_menu=false;UberCont.want_restart=false;
        var _paused_native=scrFRWeaponVisualTestsHUDCapture(_player,"pause");array_push(_captures,_paused_native);
        instance_activate_object(Player);
        UberCont.paused=false;
        _player.hp=1;_player.drawlowhp=30;
        var _low=scrFRWeaponVisualTestsHUDCapture(_player,"normal","low");array_push(_captures,_low);
        _player.fainted=30;
        var _fainted=scrFRWeaponVisualTestsHUDCapture(_player,"normal","fainted");array_push(_captures,_fainted);
        // The runner quantizes draw alpha when set; restoration must retain
        // the caller's measured state, not the unquantized input literal.
        // All named PNGs are saved before checking state/artwork invariants.
        var _drawing=_tinted.state;
        assert(_drawing.after_color==_drawing.before_color && _drawing.after_alpha==_drawing.before_alpha,
            "Bubbles meter leaked its neutral drawing state into the native HUD "+json_stringify(_drawing));
        var _ink=0;
        for(var _y=0;_y<96;++_y) for(var _x=0;_x<160;++_x) {
            var _offset=4*(_y*160+_x),_pixel=buffer_peek(_meter.pixels,_offset,buffer_u32);
            if(buffer_peek(_meter.pixels,_offset+3,buffer_u8)>0) {
                _ink++;
                var _where=" at "+string(_x)+","+string(_y)+" expected="+string(_pixel)+" actual=";
                assert(_x>=110 && _x<=128 && _y>=2 && _y<=20,
                    "Bubbles charge meter escaped its health-bar anchor"+_where+string(_pixel));
                assert(buffer_peek(_native.pixels,_offset,buffer_u32)==_pixel,
                    "Actual scrDrawPlayerHUD did not render the authored meter beside health"+_where+string(buffer_peek(_native.pixels,_offset,buffer_u32)));
                assert(buffer_peek(_normal.pixels,_offset,buffer_u32)==_pixel,
                    "Ordinary TopCont Draw GUI omitted the Bubbles meter outside portal transitions"+_where+string(buffer_peek(_normal.pixels,_offset,buffer_u32)));
                assert(buffer_peek(_paused_native.pixels,_offset,buffer_u32)==_pixel,
                    "Actual paused UberCont Draw GUI omitted the Bubbles meter"+_where+string(buffer_peek(_paused_native.pixels,_offset,buffer_u32)));
                assert(buffer_peek(_tinted.pixels,_offset,buffer_u32)==_pixel,
                    "Bubbles source meter inherited the preceding native HUD color or alpha"+_where+string(buffer_peek(_tinted.pixels,_offset,buffer_u32)));
                assert(buffer_peek(_low.pixels,_offset,buffer_u32)==_pixel,
                    "Actual native LOW HP text painted over the Bubbles charge meter"+_where+string(buffer_peek(_low.pixels,_offset,buffer_u32)));
                assert(buffer_peek(_fainted.pixels,_offset,buffer_u32)==_pixel,
                    "Actual fainted native HUD changed the Bubbles charge artwork"+_where+string(buffer_peek(_fainted.pixels,_offset,buffer_u32)));
            }
            assert(buffer_peek(_retired.pixels,_offset+3,buffer_u8)==0,
                "Retired source projection rendered a second Bubbles meter at "+string(_x)+","+string(_y));
        }
        assert(_ink>32,"Bubbles HUD placement passed with empty or invisible source artwork");
        var _warning=0;
        for(var _y=2;_y<=20;++_y) for(var _x=132;_x<160;++_x) {
            var _offset=4*(_y*160+_x);
            if(buffer_peek(_low.pixels,_offset,buffer_u32)!=buffer_peek(_normal.pixels,_offset,buffer_u32)) _warning++;
        }
        scrNTTESmokeLog("FRONTIER Bubbles HUD pixel counts "+json_stringify({artwork:_ink,low_health_warning:_warning}));
        assert(_warning>8,"Actual Bubbles low-health warning was hidden instead of placed beside the meter; pixels="+string(_warning));
        surface_save(_native.surface,working_directory+"frontier-bubbles-health-hud.png");
        var _paused={race:19,bubbles_bubbleCharge:25,bubbles_maxBubbleCharge:100};
        var _partial=scrFRWeaponVisualTestsHUDCapture(_paused,"meter","partial");array_push(_captures,_partial);
        var _different=0;
        for(var _offset=0;_offset<160*96*4;_offset+=4)
            if(buffer_peek(_partial.pixels,_offset,buffer_u32)!=buffer_peek(_meter.pixels,_offset,buffer_u32)) _different++;
        assert(_different>16,"Bubbles native HUD lost the authored charge fill in a paused struct context; changed pixels="+string(_different));
        scrNTTESmokeLog("PASS FRONTIER real GPU native Bubbles health anchor119,11, ordinary/paused/low-health/fainted GUI, neutral restored drawing state, source fill and no duplicate old projection");
    } finally {
        instance_activate_object(Player);
        UberCont.paused=_pause;UberCont.want_pause=_want_pause;
        UberCont.want_menu=_want_menu;UberCont.want_restart=_want_restart;
        TopCont.wave=_top_wave;
        for(var _i=0;_i<array_length(_captures);++_i) {
            if(surface_exists(_captures[_i].surface)) surface_free(_captures[_i].surface);
            if(buffer_exists(_captures[_i].pixels)) buffer_delete(_captures[_i].pixels);
        }
    }
}

function scrFRWeaponVisualTestsRate(_rate) {
    // This is a synchronous callback comparison, not a scheduled gameplay
    // transaction. Establish actual physical units before each manual call.
    save_set_value("options","framerate",_rate);
    save_set_value("options","autopause",false);
    save_set_value("visual","freezeframes",0);
    save_set_value("visual","bossintro",false);
    scrOptionsUpdate();
    assert(scrFRClockApply212(_rate) && game_get_speed(gamespeed_fps)==_rate
        && UberCont.opt_framerate==_rate && timescale==30/_rate && !UberCont.opt_autopause,
        "Synchronous weapon visual callback fixture did not establish actual rate units");
}

function scrFRWeaponVisualTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled(),
        "Source/native melee acceptance requires the isolated desktop runner");
    var _player=instance_find(Player,0),_players=scrNTTEFullAreaGeneratorSnapshot(Player),
        _before=scrNTTEFullInstances(all),_seed=random_get_seed(),_frame=current_frame,
        _old_rate=game_get_speed(gamespeed_fps),
        _options={rate:save_get_option("options","framerate",60),
            autopause:save_get_option("options","autopause",true),freeze:save_get_option("visual","freezeframes",true),
            bossintro:save_get_option("visual","bossintro",true)},
        _keys={nodes:[]},_rows=[];
    assert(instance_exists(_player),"Melee visual fixture requires a real native Player");
    scrNTTEFullAreaSnapshotContainer(KeyCont,_keys);
    try {
        scrFRWeaponVisualTestsTables();
        var _melee=[];
        var _ids=variable_struct_get_names(global.fr_weapon_keys);
        for(var _i=0;_i<array_length(_ids);++_i) {
            var _raw=real(_ids[_i]);
            if(scr_weapon_is_melee(_raw)) array_push(_melee,_raw);
        }
        assert(array_length(_melee)==10,"Melee visual regression did not enumerate all10 authored NTUF melee weapons");
        for(var _round=0;_round<2;++_round) {
            var _rate=_round==0?30:60;
            scrFRWeaponVisualTestsRate(_rate);
            for(var _i=0;_i<array_length(_melee);++_i) {
                var _raw=_melee[_i],_baseline=scrNTTEFullInstances(all),_rng=random_get_seed();
                scrFRWeaponVisualTestsPrepare(_player,_raw);
                with(_player) scrFRWeaponFire(_raw,true);
                var _source_state=_player.fr_source_wep,
                    _source={angle:_player.wepangle,kick:_player.wkick,
                        chrg:is_struct(_source_state)?(_source_state[$ "chrg"]??undefined):undefined,
                        charge:is_struct(_source_state)?(_source_state[$ "chrg_num"]??undefined):undefined};
                scrFRWeaponVisualTestsRetire(_baseline);random_set_seed(_rng);
                scrFRWeaponVisualTestsPrepare(_player,_raw);
                with(_player) scrFire(_raw,false,true);
                var _native_state=_player.fr_source_wep,
                    _actual={angle:_player.wepangle,kick:_player.wkick,
                        chrg:is_struct(_native_state)?(_native_state[$ "chrg"]??undefined):undefined,
                        charge:is_struct(_native_state)?(_native_state[$ "chrg_num"]??undefined):undefined},
                    _diag={weapon:global.fr_weapon_keys[$ string(_raw)],rate:_rate,source:_source,native:_actual};
                scrNTTESmokeLog("FRONTIER melee visual comparison "+json_stringify(_diag));
                assert(_player.wepangle==_source.angle && _player.wkick==_source.kick
                    && (_player.wepangle!=120 || _player.wkick!=0),
                    "Native melee fire lost or double-flipped the authored swing "+json_stringify(_diag));
                array_push(_rows,{weapon:_raw,rate:_rate,engine_rate:game_get_speed(gamespeed_fps),
                    scale:timescale,manual_callbacks:true,angle:_player.wepangle,kick:_player.wkick});
                scrFRWeaponVisualTestsRetire(_baseline);
            }
            // Keep the existing native NTTE source ports in the same dispatch
            // contract: each conventional bat swings once and applies recoil.
            var _native=[wep_ntte_bubble_bat,wep_ntte_energy_bat,wep_ntte_pizza_cutter,
                wep_ntte_bone_scythe,wep_ntte_annihilator,wep_ntte_entangler,wep_ug_fossil_hammer],
                _native_kicks=[-4,-4,-4,5,-4,-4,-5];
            for(var _i=0;_i<array_length(_native);++_i) {
                var _raw=_native[_i],_baseline=scrNTTEFullInstances(all);
                scrFRWeaponVisualTestsPrepare(_player,_raw);
                _player.ntte_state.chrg=-1;_player.ntte_state.chrg_num=0;
                _player.ntte_state.chrg_max=15;
                with(_player) scrFire(_raw,false,true);
                assert(_player.wepangle==-120 && _player.wkick==_native_kicks[_i],
                    "NTTE native melee lost its source swing/recoil for "+string(_raw));
                scrFRWeaponVisualTestsRetire(_baseline);
            }
            // The real reload block must stop after the source callback sets
            // wepflip; a following native *= -1 used to undo that orientation.
            scrFRWeaponVisualTestsPrepare(_player,FR_BUBBLES_CUTLASS);
            _player.wepangle=-120;_player.wepflip=1;_player.reload=timescale;
            _player.can_shoot=false;_player.reloadspeed=1;
            for(var _slot=0;_slot<array_length(KeyCont.hold_fire);++_slot) {
                KeyCont.hold_fire[_slot]=false;KeyCont.press_fire[_slot]=false;
            }
            with(_player) event_perform(ev_step,0);
            assert(_player.reload==0 && _player.can_shoot && _player.wepflip==-1,
                "Native reload double-flipped the source Bubbles melee orientation");
            // A Frontier stock plus an ordinary native front must reload both
            // parts. The source stock sets -1; native front flips it to +1.
            // This catches both the old double-source dispatch and a broad
            // skip that would silently omit another fusion part's callback.
            scrFRWeaponVisualTestsPrepare(_player,FR_BUBBLES_CUTLASS);
            var _fusion=scrNTTEFullWeaponMerge(FR_BUBBLES_CUTLASS,wep_revolver),
                _handle=scrNTTEFullWeaponNative(_fusion);
            _player.wep=_handle;_player.ntte_state=scrNTTEFullWeaponNativeState(_handle);
            _player.wepangle=-120;_player.wepflip=1;_player.reload=timescale;
            _player.can_shoot=false;_player.reloadspeed=1;
            with(_player) event_perform(ev_step,0);
            assert(_player.wep==_handle && _player.wepflip==1 && _player.can_shoot,
                "Recursive fusion reload skipped its native part or dispatched the source melee part twice");
            // Steroids' reload event does not perform the temporary firing
            // swap. Direct authored visual writes must target the real b-slot.
            scrFRWeaponVisualTestsPrepare(_player,wep_revolver);
            _player.race=Race.Steroids;_player.wepangle=0;_player.wepflip=1;
            _player.bwep=FR_BUBBLES_CUTLASS;_player.bntte_state=scrNTTENewState(FR_BUBBLES_CUTLASS);
            _player.bwepangle=-120;_player.bwepflip=1;_player.breload=timescale;
            _player.bcan_shoot=false;_player.reloadspeed=1;
            with(_player) event_perform(ev_step,0);
            assert(_player.breload==0 && _player.bcan_shoot && _player.bwepflip==-1
                && _player.wepflip==1 && _player.wepangle==0,
                "Secondary raw source reload altered the primary flip or failed to update the secondary flip");
            scrFRWeaponVisualTestsPrepare(_player,wep_revolver);
            _player.race=Race.Steroids;_player.wepangle=0;_player.wepflip=1;
            _player.bwep=_handle;_player.bntte_state=scrNTTEFullWeaponNativeState(_handle);
            _player.bwepangle=-120;_player.bwepflip=1;_player.breload=timescale;
            _player.bcan_shoot=false;_player.reloadspeed=1;
            with(_player) event_perform(ev_step,0);
            assert(_player.bwep==_handle && _player.bcan_shoot && _player.bwepflip==1
                && _player.wepflip==1 && _player.wepangle==0,
                "Secondary fusion reload lost its source/native callbacks or leaked the visual view into primary");
            // Powder Hammer deliberately uses explicit wep_get(false) and
            // wep_set(false). The event view must preserve that direct b-write.
            scrFRWeaponVisualTestsPrepare(_player,wep_revolver);
            _player.race=Race.Steroids;_player.wepangle=0;_player.wepflip=1;
            var _hammer=global.fr_weapon_ids[$ "FR_PowderHammer"];
            _player.bwep=_hammer;_player.bntte_state=scrNTTENewState(_hammer);
            _player.bwepangle=-120;_player.bwepflip=1;_player.breload=timescale;
            _player.bcan_shoot=false;_player.reloadspeed=1;
            with(_player) {var _charge=scrFRWeaponPrepare(_hammer,false);_charge.chrg=1;}
            with(_player) event_perform(ev_step,0);
            assert(_player.breload==0 && _player.bcan_shoot && _player.bwepflip==-1 && _player.wepflip==1,
                "Secondary reload visual view undid the source's explicit wep_set(false) flip");
            scrFRWeaponVisualTestsPrepare(_player,wep_revolver);
            _player.race=Race.Steroids;_player.wepangle=0;_player.wepflip=1;
            _player.bwep=wep_ug_fossil_hammer;_player.bntte_state=scrNTTENewState(_player.bwep);
            _player.bwepangle=-120;_player.bwepflip=1;_player.breload=timescale;
            _player.bcan_shoot=false;_player.reloadspeed=1;
            with(_player) event_perform(ev_step,0);
            assert(_player.breload==0 && _player.bcan_shoot && _player.bwepflip==-1 && _player.wepflip==1,
                "Native secondary Fossil Hammer reload flipped the primary hand instead of the secondary");
        }
        scrFRWeaponVisualTestsPrepare(_player,FR_BUBBLES_CUTLASS);
        scrFRWeaponVisualTestsHUD(_player);
        scrNTTESmokeLog("PASS FRONTIER all10 NTUF melee callbacks match native fire, all7 NTTE melee swings and source primary/secondary physical reload at30/60Hz "+json_stringify(_rows));
    } finally {
        scrFRWeaponVisualTestsRetire(_before);
        scrFRClockApply212(_old_rate);
        scrNTTEFullAreaGeneratorRestore(_players);
        scrNTTEFullAreaGeneratorRestore({instances:[],containers:_keys.nodes});
        save_set_value("options","framerate",_options.rate);save_set_value("options","autopause",_options.autopause);
        save_set_value("visual","freezeframes",_options.freeze);save_set_value("visual","bossintro",_options.bossintro);
        scrOptionsUpdate();random_set_seed(_seed);current_frame=_frame;
    }
}
