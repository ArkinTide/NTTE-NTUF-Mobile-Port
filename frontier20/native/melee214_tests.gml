// Exercise real player/native/fusion firing with mutation ownership established
// through the same setter as a selected mutation. Never infer a range bonus
// merely from the authored callback containing a skill_get expression.
function scrFRMelee214Probe(_player,_weapon,_stack,_merged=false) {
    var _before=scrNTTEFullInstances(all),_origin=4000,_result={count:0,reach:-1,speed:-1};
    scr_skill_set(mut_long_arms,_stack);
    assert(scr_skill_get(mut_long_arms)==_stack && scrFRGetSkill(mut_long_arms)==_stack,
        "Long Arms native and source ownership views disagree");
    try {
        scrFRWeaponVisualTestsPrepare(_player,_weapon);
        _player.x=_origin;_player.y=_origin;_player.xprevious=_origin;_player.yprevious=_origin;
        _player.ntte_state.chrg=-1;_player.ntte_state.chrg_num=0;_player.ntte_state.chrg_max=15;
        if(_merged) {
            // Test the added melee as the emitted front of a genuine fusion.
            // A melee stock with a revolver front may deliberately replace its
            // slash with a Bullet (Powder Hammer's FireSlash does exactly that),
            // so requiring a retained stock slash would reject valid source
            // fusion behavior without measuring the melee's actual range.
            var _model=scrNTTEFullMergedRuntimePart(scrNTTEFullWeaponMerge(wep_revolver,_weapon)),
                _handle=scrNTTEFullWeaponNative(_model),_part=scrNTTEFullWeaponMergedPart(_model);
            _player.wep=_handle;_player.ntte_state=scrNTTEFullWeaponNativeState(_handle);
            var _state=scrNTTEFullWeaponNativeState(_part);
            _state.chrg=-1;_state.chrg_num=0;_state.chrg_max=15;
            var _mount=scrNTTEFullMergedRuntimeStateMount(_player,_part,true),
                _old=variable_global_exists("ntte_full_merged_state_fire")?global.ntte_full_merged_state_fire:undefined;
            global.ntte_full_merged_state_fire={actor:_player,part:_part,primary:true};
            try {with(_player) {
                var _source=scrFRWeaponPrepare(_weapon,true);
                if(is_struct(_source) && variable_struct_exists(_source,"chrg")) {
                    _source.chrg=-1;_source.chrg_num=1;
                }
            }} finally {
                global.ntte_full_merged_state_fire=_old;
                scrNTTEFullMergedRuntimeStateUnmount(_mount);
            }
        }
        with(_player) scrFire(wep,false,true);
        var _new=scrNTTEFullMergedRuntimeNew(_before);
        for(var _i=0;_i<array_length(_new);++_i) {
            var _shot=_new[_i];
            if(!instance_exists(_shot) || !(instance_is(_shot,Slash) || instance_is(_shot,Shank)
                || instance_is(_shot,EnergyShank) || instance_is(_shot,NTTESwing)
                || instance_is(_shot,NTTEFullBubbleSlash) || instance_is(_shot,NTTEFullEnergyBatSlash))) continue;
            _result.count++;
            _result.reach=max(_result.reach,_shot.x-_origin);
            _result.speed=max(_result.speed,_shot.speed/timescale);
        }
        return _result;
    } finally {scrFRWeaponVisualTestsRetire(_before);}
}

function scrFRMelee214ScytheFire(_player,_stack) {
    scr_skill_set(mut_long_arms,_stack);
    var _before=scrNTTEFullInstances(all),_origin=5000,_result=undefined;
    try {
        _player.x=_origin;_player.y=_origin;_player.xprevious=_origin;_player.yprevious=_origin;
        _player.speed=0;_player.gunangle=0;_player.accuracy=0;_player.wepangle=120;
        _player.can_shoot=true;_player.reload=0;
        with(_player) scrFire(wep,false,true);
        var _new=scrNTTEFullMergedRuntimeNew(_before);
        for(var _i=0;_i<array_length(_new);++_i) {
            var _shot=_new[_i];
            if(instance_exists(_shot) && instance_is(_shot,NTTEFullBoneSlash)) {
                assert(is_undefined(_result),"Physical Scythe duplicated its melee attack");
                _result={reach:_shot.x-_origin,speed:_shot.speed/timescale,
                    sprite:_shot.sprite_index,mask:_shot.mask_index};
            }
        }
        assert(is_struct(_result) && abs(_result.reach-(10+10*_stack))<0.01
            && abs(_result.speed-(2.5+2*_stack))<0.001,
            "Scythe lifecycle lost source Long Arms geometry "+string(_stack)+" "+json_stringify(_result));
        return _result;
    } finally {scrFRWeaponVisualTestsRetire(_before);}
}

function scrFRMelee214ScytheLifecycle(_player) {
    scrFRWeaponVisualTestsPrepare(_player,wep_ntte_bone_scythe);
    var _model={wep:wep_ntte_bone_scythe},_handle=scrNTTEFullWeaponNative(_model),
        _state=scrNTTEFullWeaponNativeState(_handle);
    _player.wep=_handle;_player.ntte_state=_state;
    _player.ntte_scythe_slots_migrated=true;_state.ammo=40;
    var _plain=scrFRMelee214ScytheFire(_player,0),_buffed=scrFRMelee214ScytheFire(_player,1);
    assert(_plain.sprite==_buffed.sprite && _plain.mask==_buffed.mask,
        "Long Arms changed the authored Scythe shape instead of its offset/travel range");
    // The dedicated touch command traverses Shotbow and Slugbow, then returns
    // the same physical weapon to melee. Arrow-only modes have no melee mask.
    for(var _mode=1;_mode<=3;++_mode) {
        assert(scrNTTEFullScytheControlPress(_player,0,true),"Scythe lifecycle rejected touch transform");
        with(_player) scrNTTEFullMergedRuntimeStateStepSlots();
        assert(_player.wep==_handle && scrNTTEFullWeaponRaw(_handle)==wep_ntte_bone_scythe+(_mode mod 3)
            && scrNTTEFullWeaponNativeState(_handle)==_state && _state.ammo==40,
            "Touch transform changed physical Scythe ownership/ammunition");
    }
    scrFRMelee214ScytheFire(_player,1);
    // The ordinary native inventory swap must preserve the physical state,
    // and continue-game JSON must preserve both that state and Long Arms.
    _player.bwep=wep_revolver;_player.bntte_state=scrNTTENewState(wep_revolver);
    with(_player) {scrSwapWeps(false);scrSwapWeps(false);}
    assert(_player.wep==_handle && _player.ntte_state==_state,"Inventory swap lost physical Scythe");
    scrFRMelee214ScytheFire(_player,1);
    var _weapons=json_parse(json_stringify(scrNTTEFullWeaponNativeExport())),
        _systems=json_parse(json_stringify(scrNTTEFullSystemsExport()));
    scrNTTEFullWeaponNativeImport(_weapons);
    assert(scrNTTEFullSystemsImport(_systems),"Long Arms Scythe continue-game fixture rejected systems save");
    _player.ntte_state=scrNTTEFullWeaponNativeState(_handle);
    scrFRMelee214ScytheFire(_player,1);
    assert(_player.wep==_handle && scrNTTEFullWeaponRaw(_handle)==wep_ntte_bone_scythe
        && scrNTTEFullWeaponNativeState(_handle).ammo==40,
        "Continue-game altered Scythe form/ammunition");
    scrNTTESmokeLog("PASS FRONTIER214 Scythe Long Arms real fire before/after touch three-mode cycle, inventory swap and JSON continuation; source mask retained");
}

function scrFRMelee214ScytheControlDraw(_player) {
    var _button=noone,_surface=-1,_camera=-1,_pixels=-1,_overlay=-1,_target=false,
        _world=matrix_get(matrix_world),_view=matrix_get(matrix_view),_projection=matrix_get(matrix_projection),
        _shader=shader_current(),_color=draw_get_color(),_alpha=draw_get_alpha();
    gpu_push_state();
    try {
        _button=instance_create(0,0,ButtonNTTEScythe);
        _button.x=80;_button.y=60;_button.index=-1;
        _surface=surface_create(160,120);_camera=camera_create_view(0,0,160,120,0,noone,-1,-1,-1,-1);
        _pixels=buffer_create(160*120*4,buffer_fixed,1);_overlay=buffer_create(160*120*4,buffer_fixed,1);
        assert(surface_exists(_surface) && buffer_exists(_pixels) && buffer_exists(_overlay),
            "Scythe control artwork capture allocation failed");
        surface_set_target(_surface);_target=true;camera_apply(_camera);
        matrix_set(matrix_world,matrix_build_identity());shader_reset();gpu_set_blendmode(bm_normal);
        gpu_set_texfilter(false);draw_clear_alpha(c_black,0);draw_set_color(c_white);draw_set_alpha(1);
        with(_button) scrNTTEFullScytheControlDraw(_player,1,false);
        surface_reset_target();_target=false;buffer_get_surface(_pixels,_surface,0);
        surface_save(_surface,working_directory+"ntuf214-scythe-control-no-arrow.png");
        // Exact removed decoration is a negative control. Drawing it onto an
        // already-present white arrow would leave identical pixels. Require
        // visible changed pixels, proving the native control omitted it.
        surface_set_target(_surface);_target=true;camera_apply(_camera);
        draw_sprite_ext(sprLoadoutArrow,0,92,48,0.65,0.65,90,c_white,1);
        surface_reset_target();_target=false;buffer_get_surface(_overlay,_surface,0);
        surface_save(_surface,working_directory+"ntuf214-scythe-control-old-arrow-negative.png");
        var _ink=0,_changed=0;
        for(var _offset=0;_offset<160*120*4;_offset+=4) {
            if(buffer_peek(_pixels,_offset+3,buffer_u8)>0) _ink++;
            if(buffer_peek(_pixels,_offset,buffer_u32)!=buffer_peek(_overlay,_offset,buffer_u32)) _changed++;
        }
        assert(_ink>40 && _changed>4,"Native Scythe control was empty or still contained its removed corner arrow "+json_stringify({ink:_ink,overlay_change:_changed}));
        scrNTTESmokeLog("PASS FRONTIER214 actual Scythe control Draw retained icon/button and excluded exact old arrow overlay "+json_stringify({ink:_ink,overlay_change:_changed}));
    } finally {
        if(_target) surface_reset_target();
        if(instance_exists(_button)) instance_destroy(_button,false);
        if(surface_exists(_surface)) surface_free(_surface);
        if(_camera>=0) camera_destroy(_camera);
        if(buffer_exists(_pixels)) buffer_delete(_pixels);
        if(buffer_exists(_overlay)) buffer_delete(_overlay);
        gpu_pop_state();if(_shader<0) shader_reset();else shader_set(_shader);
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);matrix_set(matrix_projection,_projection);
        draw_set_color(_color);draw_set_alpha(_alpha);
    }
}

function scrFRMelee214Tests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled(),
        "Long Arms acceptance requires the isolated desktop native runner");
    scrNTTEFullWeaponNativeInit();
    var _players=scrNTTEFullAreaGeneratorSnapshot(Player),_game=scrNTTEFullAreaGeneratorSnapshot(GameCont),
        _back=scrNTTEFullAreaGeneratorSnapshot(BackCont),_uber=scrNTTEFullAreaGeneratorSnapshot(UberCont),
        _keys=scrNTTEFullAreaGeneratorSnapshot(KeyCont),_seed=random_get_seed(),_frame=current_frame,
        _rate=game_get_speed(gamespeed_fps),_skills=ds_list_create(),_rows=[],
        _models=scrNTTEFullArrayCopy(global.ntte_full_native_weapon_models),_console=global.console_active,
        _progress=global.ntte_full_progress,
        _options={rate:save_get_option("options","framerate",60),autopause:save_get_option("options","autopause",true),
            freeze:save_get_option("visual","freezeframes",true),bossintro:save_get_option("visual","bossintro",true)};
    GameCont.skills=_skills;GameCont.ntte_full_native_skill_counts={};GameCont.area=1;GameCont.underwater=false;
    current_frame=2;global.console_active=false;
    // A clean private harness has not discovered the NTTE packs. Start from
    // an isolated owned-progress copy; do not bypass availability or persist
    // unlocks to the player's save. The source callbacks remain unchanged.
    global.ntte_full_progress=json_parse(json_stringify(_progress));
    var _owned=scrFRProgress210State().unlocks;
    _owned[$ "pack:oasis"]=true;_owned[$ "pack:lair"]=true;
    _owned[$ "pack:red"]=true;_owned[$ "wep:scythe"]=true;
    try {
        var _player=instance_find(Player,0),_melee=[],_ids=variable_struct_get_names(global.fr_weapon_keys);
        for(var _i=0;_i<array_length(_ids);++_i) {
            var _raw=real(_ids[_i]);
            if(scr_weapon_is_melee(_raw)) array_push(_melee,_raw);
        }
        assert(array_length(_melee)==10,"Long Arms acceptance omitted an NTUF melee declaration");
        array_push(_melee,wep_ntte_bubble_bat,wep_ntte_energy_bat,wep_ntte_pizza_cutter,
            wep_ntte_bone_scythe,wep_ntte_annihilator,wep_ntte_entangler,wep_ug_fossil_hammer);
        for(var _round=0;_round<2;++_round) {
            var _hz=_round==0?30:60;
            scrFRWeaponVisualTestsRate(_hz);
            for(var _i=0;_i<array_length(_melee);++_i) {
                var _weapon=_melee[_i],_rng=random_get_seed(),_probes=[];
                assert(scrNTTEFullWeaponAvailable(_weapon) && scr_weapon_get_name(_weapon)!="LOCKED",
                    "Long Arms acceptance did not establish legitimate owned weapon availability "+string(_weapon));
                for(var _stack=0;_stack<=2;++_stack) {
                    random_set_seed(_rng);
                    array_push(_probes,scrFRMelee214Probe(_player,_weapon,_stack));
                }
                var _row={weapon:_weapon,name:scr_weapon_get_name(_weapon),hz:_hz,probes:_probes};
                scrNTTESmokeLog("FRONTIER214 Long Arms launch "+json_stringify(_row));
                assert(_probes[0].count>0 && _probes[1].count==_probes[0].count && _probes[2].count==_probes[0].count,
                    "Long Arms changed the attack count or native melee did not fire "+json_stringify(_row));
                // Hookpole/Golden Hookpole/Powder Spear author their range
                // through Shank travel alone, retaining a fixed birth point.
                // Other slashes add disjoint as well as travel. Do not force
                // a universal birth offset that would alter source balance.
                assert(_probes[1].reach>=_probes[0].reach-0.01 && _probes[2].reach>=_probes[1].reach-0.01
                    && _probes[1].speed>_probes[0].speed+0.5 && _probes[2].speed>_probes[1].speed+0.5,
                    "Added melee lost its real Long Arms travel bonus or moved backwards "+json_stringify(_row));
                array_push(_rows,_row);
                var _fusion=[];
                for(var _stack=0;_stack<=2;++_stack) {
                    random_set_seed(_rng);
                    array_push(_fusion,scrFRMelee214Probe(_player,_weapon,_stack,true));
                }
                var _fusion_row={weapon:_weapon,hz:_hz,fusion:true,melee_role:"front",probes:_fusion};
                scrNTTESmokeLog("FRONTIER214 Long Arms fusion launch "+json_stringify(_fusion_row));
                assert(_fusion[0].count>0 && _fusion[1].count==_fusion[0].count && _fusion[2].count==_fusion[0].count
                    && _fusion[1].reach>=_fusion[0].reach-0.01 && _fusion[2].reach>=_fusion[1].reach-0.01
                    && _fusion[1].speed>_fusion[0].speed+0.5 && _fusion[2].speed>_fusion[1].speed+0.5,
                    "Physical fusion lost added-melee Long Arms range/travel "+json_stringify(_fusion_row));
                array_push(_rows,_fusion_row);
            }
            scrFRMelee214ScytheLifecycle(_player);
            scrFRMelee214ScytheControlDraw(_player);
        }
        scrNTTESmokeLog("PASS FRONTIER214 actual native Long Arms0/1/2 geometric range and speed for all10 NTUF and7 NTTE melee at30/60Hz "+json_stringify(_rows));
    } finally {
        scrFRClockApply212(_rate);
        scrNTTEFullAreaGeneratorRestore(_players);scrNTTEFullAreaGeneratorRestore(_game);
        scrNTTEFullAreaGeneratorRestore(_back);scrNTTEFullAreaGeneratorRestore(_uber);scrNTTEFullAreaGeneratorRestore(_keys);
        save_set_value("options","framerate",_options.rate);save_set_value("options","autopause",_options.autopause);
        save_set_value("visual","freezeframes",_options.freeze);save_set_value("visual","bossintro",_options.bossintro);
        scrOptionsUpdate();random_set_seed(_seed);current_frame=_frame;ds_list_destroy(_skills);
        global.ntte_full_native_weapon_models=_models;
        global.ntte_full_progress=_progress;
        global.console_active=_console;
    }
}

// The launch probes above do not stand in for a hit test. This second phase
// yields to the native runner between observations so GameMaker owns motion,
// sprite animation, precise-mask overlap and ordinary Collision_hitme events.
// No collision handler, projectile hit or target damage is invoked by it.
function scrFRMelee214NaturalSelect(_state) {
    scr_skill_set(mut_long_arms,0);
    assert(scr_skill_get(mut_long_arms)==0,"Scythe natural selection did not start unowned");
    if(_state.stack==0) return;
    var _before=scrNTTEFullInstances(all);
    GameCont.skillpoints=2;GameCont.ultrapoints=0;GameCont.crownpoints=0;
    var _icon=instance_create(0,0,SkillIcon);_icon.skill=mut_long_arms;
    with(_icon) event_user(0);
    assert(scr_skill_get(mut_long_arms)==1 && ds_list_find_index(GameCont.skills,mut_long_arms)>=0
        && GameCont.skillpoints==1,"Real SkillIcon.Select did not grant Long Arms once");
    // The real submission makes the next selection screen and saves this
    // private runner's continuation. Retire only those newborn UI instances
    // before yielding, retaining the genuine selected ownership in GameCont.
    scrFRWeaponVisualTestsRetire(_before);
    GameCont.skillpoints=0;
    scrNTTESmokeLog("FRONTIER214 Scythe genuine SkillIcon.Select Long Arms grant at"+string(_state.hz)+"Hz");
}

function scrFRMelee214NaturalShot(_state) {
    var _p=_state.player,_origin=51000;
    _state.before=scrNTTEFullInstances(all);_state.targets=[];_state.samples=[];
    scrFRMelee214NaturalSelect(_state);
    scrFRWeaponVisualTestsPrepare(_p,wep_ntte_bone_scythe);
    var _model={wep:wep_ntte_bone_scythe},_handle=scrNTTEFullWeaponNative(_model),
        _weapon=scrNTTEFullWeaponNativeState(_handle);
    _p.wep=_handle;_p.ntte_state=_weapon;_weapon.combo=_state.heavy?2:0;
    _p.ntte_scythe_slots_migrated=true;_p.x=_origin;_p.y=_origin;
    _p.xprevious=_origin;_p.yprevious=_origin;_p.visible=true;_p.hp=100000;
    _p.nexthurt=current_frame+10000;_p.gunangle=0;_p.accuracy=0;_p.speed=0;
    _p.reload=0;_p.can_shoot=true;
    for(var _distance=8;_distance<=200;_distance+=4) {
        var _enemy=instance_create(_origin+_distance,_origin,Bandit),
            _sprite=_enemy.sprite_index,_mask=_enemy.mask_index;
        with(_enemy) {
            // Retain the native Bandit collision mask, HP/damage/team fields
            // but retire its AI and enemy-to-enemy crowd repulsion. Only the
            // ordinary hitme Collision path should move/hurt this range grid.
            instance_change(hitme,false);
            sprite_index=_sprite;mask_index=_mask;image_speed=0;speed=0;
            hp=100000;max_hp=100000;can_die=false;nexthurt=-1;
        }
        array_push(_state.targets,{instance:_enemy,distance:_distance});
    }
    var _before_fire=scrNTTEFullInstances(all);
    with(_p) scrFire(wep,false,true);
    var _shots=scrNTTEFullMergedRuntimeNew(_before_fire);_state.shot=noone;
    for(var _i=0;_i<array_length(_shots);++_i)
        if(instance_exists(_shots[_i]) && instance_is(_shots[_i],NTTEFullBoneSlash)) {
            assert(_state.shot==noone,"Scythe natural firing duplicated a slash");_state.shot=_shots[_i];
        }
    assert(instance_exists(_state.shot),"Scythe ordinary physical melee form did not fire");
    _state.origin=_origin;_state.start=current_frame;_state.rendered=false;
    _state.max_hit=-1;_state.frames=0;_state.last_index=-1;_state.phase="flight";
}

function scrFRMelee214NaturalCapture(_state) {
    var _surface=-1,_camera=-1,_target=false,
        _world=matrix_get(matrix_world),_view=matrix_get(matrix_view),_projection=matrix_get(matrix_projection),
        _shader=shader_current(),_color=draw_get_color(),_alpha=draw_get_alpha();
    gpu_push_state();
    try {
        _surface=surface_create(240,96);_camera=camera_create_view(_state.origin-16,_state.origin-48,240,96,0,noone,-1,-1,-1,-1);
        assert(surface_exists(_surface),"Natural Scythe capture allocation failed");
        surface_set_target(_surface);_target=true;camera_apply(_camera);
        matrix_set(matrix_world,matrix_build_identity());shader_reset();gpu_set_blendmode(bm_normal);
        gpu_set_texfilter(false);draw_clear_alpha(make_color_rgb(28,28,36),1);draw_set_alpha(1);draw_set_color(c_white);
        // These are actual current engine sprites and masks, rather than a
        // recreated slash diagram or a manually simulated damage preview.
        var _p=_state.player,_shot=_state.shot;
        if(instance_exists(_p)) with(_p) draw_self();
        if(instance_exists(_shot)) with(_shot) draw_self();
        for(var _i=0;_i<array_length(_state.targets);_i+=4) {
            var _enemy=_state.targets[_i].instance;
            if(instance_exists(_enemy)) with(_enemy) draw_self();
        }
        surface_reset_target();_target=false;
        surface_save(_surface,working_directory+"ntuf214-scythe-natural-"+string(_state.hz)+"-"+string(_state.stack)+"-"+string(_state.heavy?1:0)+".png");
        _state.rendered=true;
    } finally {
        if(_target) surface_reset_target();
        if(surface_exists(_surface)) surface_free(_surface);
        if(_camera>=0) camera_destroy(_camera);
        gpu_pop_state();if(_shader<0) shader_reset();else shader_set(_shader);
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);matrix_set(matrix_projection,_projection);
        draw_set_color(_color);draw_set_alpha(_alpha);
    }
}

function scrFRMelee214ScheduledTests() {
    if(!variable_instance_exists(id,"fr_melee214")) {
        scrFRMelee214Tests();
        var _state={player:instance_find(Player,0),round:0,hz:30,stack:0,heavy:false,phase:"rate",
            rows:[],wait:0,models:scrNTTEFullArrayCopy(global.ntte_full_native_weapon_models),
            players:scrNTTEFullAreaGeneratorSnapshot(Player),game:scrNTTEFullAreaGeneratorSnapshot(GameCont),
            back:scrNTTEFullAreaGeneratorSnapshot(BackCont),uber:scrNTTEFullAreaGeneratorSnapshot(UberCont),
            keys:scrNTTEFullAreaGeneratorSnapshot(KeyCont),progress:global.ntte_full_progress,
            rate:game_get_speed(gamespeed_fps),old_rate:save_get_option("options","framerate",60),
            parked:scrNTTEFullInstances(enemy),skills:ds_list_create()};
        fr_melee214=_state;
        GameCont.skills=_state.skills;GameCont.ntte_full_native_skill_counts={};GameCont.is_level_ended=true;
        GameCont.area=area_desert;GameCont.underwater=false;
        global.ntte_full_progress=json_parse(json_stringify(_state.progress));
        var _owned=scrFRProgress210State().unlocks;_owned[$ "wep:scythe"]=true;
        for(var _i=0;_i<array_length(_state.parked);++_i) instance_deactivate_object(_state.parked[_i]);
        global.console_active=false;
        return false;
    }
    var _state=fr_melee214;
    if(_state.phase=="rate") {
        if(_state.wait==0) {
            save_set_value("options","framerate",_state.hz);save_set_value("visual","freezeframes",false);
            scrOptionsUpdate();_state.wait=1;return false;
        }
        assert(++_state.wait<120,"Natural Scythe requested rate did not commit");
        if(game_get_speed(gamespeed_fps)!=_state.hz || timescale!=30/_state.hz) return false;
        _state.phase="fire";
    }
    if(_state.phase=="fire") {scrFRMelee214NaturalShot(_state);return false;}
    var _age=current_frame-_state.start,_shot=_state.shot,_hits=0;
    for(var _i=0;_i<array_length(_state.targets);++_i) {
        var _row=_state.targets[_i],_enemy=_row.instance;
        assert(instance_exists(_enemy),"Natural Scythe range target disappeared before observing damage");
        if(_enemy.hp<100000) {_hits++;_state.max_hit=max(_state.max_hit,_row.distance);}
    }
    if(instance_exists(_shot)) {
        assert(_shot.image_index>=_state.last_index,"Natural Scythe animation went backwards");
        _state.last_index=_shot.image_index;_state.frames++;
        array_push(_state.samples,{age:_age,x:_shot.x-_state.origin,index:_shot.image_index,
            bbox_left:_shot.bbox_left-_state.origin,bbox_right:_shot.bbox_right-_state.origin,hits:_hits});
        if(!_state.rendered && _shot.image_index>=1) scrFRMelee214NaturalCapture(_state);
    }
    if(_age<30) return false;
    assert(_state.max_hit>0 && _state.max_hit<196 && _state.frames>=2 && _state.rendered,
        "Natural Scythe did not produce bounded native mask collisions/animation "+json_stringify(_state.samples));
    var _distances=[];
    for(var _i=0;_i<array_length(_state.targets);++_i) {
        var _row=_state.targets[_i];
        if(_row.instance.hp<100000) array_push(_distances,_row.distance);
    }
    var _record={hz:_state.hz,stack:_state.stack,heavy:_state.heavy,frames:_state.frames,
        max_hit:_state.max_hit,hit_distances:_distances,
        selection:_state.stack==1?"SkillIcon.Select":"unowned",samples:_state.samples};
    array_push(_state.rows,_record);scrNTTESmokeLog("FRONTIER214 Scythe actual engine hit range "+json_stringify(_record));
    scrFRWeaponVisualTestsRetire(_state.before);
    _state.round++;
    if(_state.round<8) {
        _state.hz=_state.round<4?30:60;_state.stack=(_state.round div 2) mod 2;_state.heavy=(_state.round mod 2)==1;
        _state.wait=0;_state.phase="rate";return false;
    }
    for(var _rate=0;_rate<2;++_rate) for(var _heavy=0;_heavy<2;++_heavy) {
        var _plain=_state.rows[_rate*4+_heavy],_long=_state.rows[_rate*4+2+_heavy];
        assert(_long.max_hit>=_plain.max_hit+8,
            "Ordinary Scythe Long Arms did not increase true engine hit range "+json_stringify([_plain,_long]));
    }
    for(var _i=0;_i<4;++_i)
        assert(abs(_state.rows[_i].max_hit-_state.rows[_i+4].max_hit)<=4,
            "Ordinary Scythe native hit range changed materially between30/60Hz");
    file_write(working_directory+"ntuf214-scythe-natural.json",json_stringify({status:"PASS",rows:_state.rows,
        manual_damage_or_collision_calls:false,actual_skill_icon_selection:true}));
    scrNTTESmokeLog("PASS FRONTIER214 ordinary physical Scythe natural engine light/heavy animation and collision range after genuine SkillIcon selection at30/60Hz");
    scrNTTEFullAreaGeneratorRestore(_state.players);scrNTTEFullAreaGeneratorRestore(_state.game);
    scrNTTEFullAreaGeneratorRestore(_state.back);scrNTTEFullAreaGeneratorRestore(_state.uber);scrNTTEFullAreaGeneratorRestore(_state.keys);
    for(var _i=0;_i<array_length(_state.parked);++_i) instance_activate_object(_state.parked[_i]);
    ds_list_destroy(_state.skills);global.ntte_full_progress=_state.progress;
    global.ntte_full_native_weapon_models=_state.models;
    save_set_value("options","framerate",_state.old_rate);scrOptionsUpdate();
    return true;
}
