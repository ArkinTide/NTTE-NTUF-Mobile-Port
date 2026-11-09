// The authored dynamic intro callback is enabled and invoked, then its real
// replacement targets are read back from the GPU. Missing art must still fail.
function scrFRBossArt204Capture(_sprite) {
    return scrFRVisualCapture("native-actor",512,256,0,0,
        [_sprite,0,sprite_get_xoffset(_sprite),sprite_get_yoffset(_sprite),1,1,0]);
}

function scrFRBossArt204IntroPose() {
    UberCont.bossx=10;UberCont.bossnamex=0;UberCont.splatindex=3;
    UberCont.letterbox_frame=0;UberCont.pausespr=-1;
}

function scrFRBossArt204Different(_a,_b) {
    assert(_a.width==_b.width && _a.height==_b.height,"Boss art204 native Draw control dimensions differ");
    var _changed=0;
    for(var _at=0;_at<_a.width*_a.height*4;_at+=4)
        if(buffer_peek(_a.pixels,_at,buffer_u32)!=buffer_peek(_b.pixels,_at,buffer_u32)) {_changed+=1;}
    return _changed;
}

function scrFRBossArt204Tests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont) && !instance_exists(PauseImage),
        "Boss art204 requires the settled isolated desktop runner");
    var _bosses=["CoveHyperCrystal","GraveyardBoss","LightningHyperCrystal",
        "OurpleCursedHyperCrystal","RoboBoss"],_roles=["Main","Back","Name"],
        // Counted from the alpha channel of the frozen original PNGs. The
        // Graveyard Main layer is an authored transparent placeholder; its
        // visible boss is in Back, so preserve its exact empty pixels.
        _coverages=[[30337,4915,3492],[0,23032,3492],[31234,4915,3492],
            [30337,4915,3492],[12106,54714,4180]],
        _inks=[[26139,3538,3492],[0,23032,3492],[27037,3538,3492],
            [26139,3538,3492],[12106,45215,4180]],
        // Name PNGs are authored single-colour white lettering. Their
        // exact one-colour palette is valid, not a missing-art fallback.
        _colours=[[8,6,1],[0,6,1],[8,6,1],[8,6,1],[3,11,1]],
        _targets=[sprBossIntro,sprBossIntroBackLayer,sprBossName],_captures=[],_snapshots=[],
        _resources=[],_intros=[],_binding=noone,_negative=false,
        _old_loop=GameCont.loops,_old_subarea=GameCont.subarea,_old_option=UberCont.opt_bossintro,
        _old_rng=random_get_seed(),_musics=[],_uber_alarms=[],
        _uber=scrNTTEFullAreaGeneratorSnapshot(UberCont),_keys=scrNTTEFullAreaGeneratorSnapshot(KeyCont),
        _all_before=scrNTTEFullInstances(all),_native_name_unchanged=false,_disabled_guard=false,
        _owner_control=noone,_guard_binding=noone,_coop_guard=noone,_parked=[],_rejected_guards=[],
        _destroyed_owner=false,_ordinary_replacement=false,_ntte_replacement=false,
        _interrupted=[],_destroyed_pixels=false,
        _old_art_state=variable_global_exists("fr_boss_art204_state")?global.fr_boss_art204_state:undefined;
    for(var _alarm=0;_alarm<12;++_alarm) array_push(_uber_alarms,scrFRAlarmRead(UberCont,_alarm));
    var _music_ids=scrFRInstances(MusCont);
    for(var _i=0;_i<array_length(_music_ids);++_i) {
        var _music=_music_ids[_i],_alarms=[];
        for(var _alarm=0;_alarm<12;++_alarm) array_push(_alarms,scrFRAlarmRead(_music,_alarm));
        array_push(_musics,{id:_music,alarms:_alarms});
    }
    try {
        global.fr_boss_art204_state={targets:[],copies:[],starting:false};
        // Preserve any pre-existing pause bitmap/surface handles; the real
        // native unpause path may delete only this test's own handles.
        UberCont.pausespr=-1;UberCont.pauseimg=-1;
        var _control=scrFRVisualCapture("control",32,32,0,0,[]),
            _empty=scrFRVisualCapture("empty",32,32,0,0,[]);
        array_push(_captures,_control,_empty);
        assert(_control.coverage==1024 && _control.ink==1024 && _control.colours==4
            && _empty.coverage==0 && _empty.ink==0,
            "Boss art204 actual GPU positive/transparent controls failed");
        scrFRVisualSave(_control,"frontier-boss-art204-control.png");
        for(var _role=0;_role<3;++_role) {
            var _target=_targets[_role],_key=string(_target),
                _copy=sprite_duplicate(_target),_before=scrFRBossArt204Capture(_target),
                _had_backup=variable_struct_exists(global.fr_sprite_backups,_key),
                _old_backup=global.fr_sprite_backups[$ _key];
            assert(sprite_exists(_copy) && _before.coverage>0,"Boss art204 native target snapshot failed");
            array_push(_captures,_before);
            array_push(_snapshots,{target:_target,key:_key,copy:_copy,capture:_before,
                xorigin:sprite_get_xoffset(_target),yorigin:sprite_get_yoffset(_target),
                had_backup:_had_backup,backup:_old_backup});
            variable_struct_remove(global.fr_sprite_backups,_key);
        }
        for(var _boss=0;_boss<array_length(_bosses);++_boss) {
            var _name=_bosses[_boss],_sources=[],_triplet_coverage=0;
            for(var _role=0;_role<3;++_role) {
                var _path=string_lower("sprites/menu/intros/spr"+_name+_roles[_role]+".png"),
                    _source=global.fr_asset_sources[$ _path],_alias=global.fr_asset_sources[$ "../"+_path];
                assert(sprite_exists(_source) && _source==_alias && sprite_get_number(_source)==1,
                    "Boss art204 dynamic artwork aliases missing: "+_path);
                assert(sprite_get_xoffset(_source)==_snapshots[_role].xorigin
                    && sprite_get_yoffset(_source)==_snapshots[_role].yorigin,
                    "Boss art204 packaged source lost the native replacement origin: "+_path);
                var _source_pixels=scrFRBossArt204Capture(_source);array_push(_captures,_source_pixels);
                var _expected_coverage=_coverages[_boss][_role],_transparent=_expected_coverage==0,
                    _expected_ink=_inks[_boss][_role],_expected_colours=_colours[_boss][_role],
                    _source_exact=_source_pixels.coverage==_expected_coverage
                        && _source_pixels.ink==_expected_ink && _source_pixels.colours==_expected_colours,
                    _source_diagnostic={path:_path,coverage:_source_pixels.coverage,expected_coverage:_expected_coverage,
                        ink:_source_pixels.ink,expected_ink:_expected_ink,
                        colours:_source_pixels.colours,expected_colours:_expected_colours};
                scrNTTESmokeLog("FR_BOSS_ART204_SOURCE "+json_stringify(_source_diagnostic));
                if(!_source_exact) scrFRVisualSave(_source_pixels,"frontier-boss-art204-source-failure.png");
                assert(_source_exact,"Boss art204 packaged GPU source differs from frozen original pixels: "+json_stringify(_source_diagnostic));
                _triplet_coverage+=_source_pixels.coverage;
                array_push(_sources,{sprite:_source,path:_path,capture:_source_pixels});
            }
            assert(_triplet_coverage>20,"Boss art204 accepted an invisible complete boss triplet");
            GameCont.loops=0;UberCont.opt_bossintro=true;
            UberCont.ntte_full_intro_key="Tesseract";
            var _subarea=GameCont.subarea,_baseline=scrNTTEFullInstances(all);
            // Use the original compiled factory and its original enabled
            // begin-step callback, including the source's dynamic paths.
            _binding=fr_Objects_Frontier_Bosses_mod_gml_boss_intro(_name);
            assert(instance_exists(_binding) && _binding.intro && _binding.boss==_name,
                "Boss art204 authored source factory failed: "+_name);
            scrFRInvoke(_binding,_binding.fr_binding_code,_binding.fr_binding_args);
            assert(instance_exists(_binding) && !_binding.intro,
                "Boss art204 actual enabled source begin-step did not execute: "+_name);
            var _native_started=UberCont.bossintro && UberCont.paused && UberCont.want_pause
                && UberCont.letterbox && UberCont.boss==0 && scrFRAlarmRead(UberCont,2)==40
                && scrFRBossArt204IntroActive() && UberCont.ntte_full_intro_key=="";
            assert(_native_started,"Boss art204 authored callback did not start the native visible intro: "+_name);
            var _applied=true;
            for(var _role=0;_role<3;++_role) {
                var _target=_targets[_role],_source=_sources[_role],_actual=scrFRBossArt204Capture(_target);
                array_push(_captures,_actual);
                var _pixels=scrFRVisualSamePixels(_actual,_source.capture),
                    _origin=sprite_get_xoffset(_target)==sprite_get_xoffset(_source.sprite)
                        && sprite_get_yoffset(_target)==sprite_get_yoffset(_source.sprite);
                var _actual_diagnostic={path:_source.path,coverage:_actual.coverage,ink:_actual.ink,colours:_actual.colours,
                    pixels_match:_pixels,origin_match:_origin,xorigin:sprite_get_xoffset(_target),yorigin:sprite_get_yoffset(_target)};
                scrNTTESmokeLog("FR_BOSS_ART204_TARGET "+json_stringify(_actual_diagnostic));
                if(!_pixels || !_origin) scrFRVisualSave(_actual,"frontier-boss-art204-target-failure.png");
                assert(_pixels && _origin,"Boss art204 actual source callback changed pixels/origin: "+json_stringify(_actual_diagnostic));
                _applied=_applied && _pixels && _origin;
                scrFRVisualSave(_actual,"frontier-boss-art204-"+string_lower(_name)+"-"+string_lower(_roles[_role])+".png");
                array_push(_resources,{boss:_name,role:_roles[_role],path:_source.path,
                    resource:sprite_get_name(_source.sprite),target:sprite_get_name(_target),
                    width:sprite_get_width(_source.sprite),height:sprite_get_height(_source.sprite),
                    origin_x:sprite_get_xoffset(_source.sprite),origin_y:sprite_get_yoffset(_source.sprite),
                    aliases_resolve:true,source_nonempty:_source.capture.coverage>0,
                    authored_transparent:_coverages[_boss][_role]==0,
                    expected_source_coverage:_coverages[_boss][_role],source_coverage:_source.capture.coverage,
                    expected_source_ink:_inks[_boss][_role],expected_source_colours:_colours[_boss][_role],
                    source_ink:_source.capture.ink,source_colours:_source.capture.colours,
                    replacement_pixels_match:_pixels,replacement_origin_match:_origin,
                    restored_pixels_match:false,restored_origin_match:false});
            }
            // Running the actual callback again while the native animation
            // is active must retain all three replacement layers.
            scrFRInvoke(_binding,_binding.fr_binding_code,_binding.fr_binding_args);
            var _retained=instance_exists(_binding) && scrFRBossArt204IntroActive();
            for(var _role=0;_role<3;++_role) {
                var _hold=scrFRBossArt204Capture(_targets[_role]);array_push(_captures,_hold);
                _retained=_retained && scrFRVisualSamePixels(_hold,_sources[_role].capture);
            }
            assert(_retained,"Boss art204 restored artwork before the real native intro finished");
            // Execute the actual native Begin Step pause barrier. Its binding
            // must remain inactive while its authored pixels and Name survive.
            var _barrier_scale=timescale;timescale=1;
            try {with(UberCont) event_perform(ev_step,ev_step_begin);}
            finally {timescale=_barrier_scale;}
            var _pause_barrier=UberCont.paused && UberCont.want_pause==0
                && !instance_exists(Player),_owner_inactive=!instance_exists(_binding),
                _pause_retained=scrFRBossArt204IntroActive();
            for(var _role=0;_role<3;++_role) {
                var _paused_art=scrFRBossArt204Capture(_targets[_role]);array_push(_captures,_paused_art);
                _pause_retained=_pause_retained && scrFRVisualSamePixels(_paused_art,_sources[_role].capture);
            }
            var _name_png=is_undefined(scrFRBossArt204IntroName(scrMenuButtonName(sprBossName,0)));
            var _owner_still_inactive=!instance_exists(_binding);
            assert(_pause_barrier && _owner_inactive && _owner_still_inactive && _pause_retained && _name_png,
                "Boss art204 native pause barrier lost inactive owner art or its authored Name PNG");
            scrFRBossArt204IntroPose();
            var _draw=scrFRVisualCapture("actor-event",view_width,view_height,view_xview,view_yview,[UberCont]);
            array_push(_captures,_draw);
            scrFRVisualSave(_draw,"frontier-boss-art204-"+string_lower(_name)+"-native-intro.png");
            // Independent negative control: replace the targets with the
            // saved original native art, then render the same real consumer.
            for(var _role=0;_role<3;++_role) sprite_assign(_targets[_role],_snapshots[_role].copy);
            scrFRBossArt204IntroPose();
            var _ordinary_draw=scrFRVisualCapture("actor-event",view_width,view_height,view_xview,view_yview,[UberCont]);
            array_push(_captures,_ordinary_draw);
            var _draw_changes=scrFRBossArt204Different(_draw,_ordinary_draw),_draw_visible=_draw_changes>100;
            for(var _role=0;_role<3;++_role) scrFRBossArt204Replace(_targets[_role],_sources[_role].sprite,0);
            assert(_draw_visible,"Boss art204 real native intro Draw did not consume its authored artwork");
            with(UberCont) event_perform(ev_alarm,2);
            var _closed=!UberCont.bossintro && !UberCont.paused && !scrFRBossArt204IntroActive();
            assert(_closed,"Boss art204 actual native intro Alarm2 did not close and unpause");
            scrFRInvoke(_binding,_binding.fr_binding_code,_binding.fr_binding_args);
            assert(!instance_exists(_binding),"Boss art204 actual source intro cleanup did not retire its binding");
            _binding=noone;
            var _restored=true;
            for(var _role=0;_role<3;++_role) {
                var _snapshot=_snapshots[_role],_target=_targets[_role],_restored_pixels=scrFRBossArt204Capture(_target);
                array_push(_captures,_restored_pixels);
                var _pixels=scrFRVisualSamePixels(_restored_pixels,_snapshot.capture),
                    _origin=sprite_get_xoffset(_target)==_snapshot.xorigin
                        && sprite_get_yoffset(_target)==_snapshot.yorigin,
                    _row=_resources[array_length(_resources)-3+_role];
                assert(_pixels && _origin,"Boss art204 authored cleanup failed to restore native art: "+_name+_roles[_role]);
                _row.restored_pixels_match=_pixels;_row.restored_origin_match=_origin;
                _restored=_restored && _pixels && _origin;
            }
            var _state=GameCont.loops==0 && GameCont.subarea==_subarea && UberCont.opt_bossintro;
            assert(_state,"Boss art204 source callback leaked its temporary loop/subarea/option state");
            var _new=scrNTTEFullMergedRuntimeNew(_baseline);
            for(var _i=array_length(_new)-1;_i>=0;--_i)
                if(instance_exists(_new[_i])) instance_destroy(_new[_i],false);
            array_push(_intros,{boss:_name,enabled:true,actual_source_callback:true,
                artwork_applied:_applied,artwork_restored:_restored,state_preserved:_state,
                native_intro_started:_native_started,artwork_retained_while_active:_retained,
                native_intro_closed:_closed,frontend_name_png_selected:_name_png,
                actual_native_draw_visible:_draw_visible,native_draw_changed_pixels:_draw_changes,
                actual_pause_barrier:_pause_barrier,owner_inactive_at_barrier:_owner_inactive,
                owner_remained_inactive:_owner_still_inactive,pause_artwork_retained:_pause_retained});
        }
        var _missing="../sprites/menu/intros/sprrobobossmain.png",
            _saved_alias=global.fr_asset_sources[$ _missing];
        variable_struct_remove(global.fr_asset_sources,_missing);
        try {scrFRBossArt204Replace(sprBossIntro,_missing,0);}
        catch(_error) {_negative=is_string(_error) && _error=="Frontier boss artwork was not packaged: "+_missing;}
        finally {global.fr_asset_sources[$ _missing]=_saved_alias;}
        assert(_negative,"Boss art204 missing-alias negative control silently accepted unpackaged art");
        UberCont.fr_boss_art204_intro=false;UberCont.bossintro=true;
        var _ordinary_name=scrMenuButtonName(sprBossName,0);
        _native_name_unchanged=scrFRBossArt204IntroName(_ordinary_name)==_ordinary_name
            && scrFRBossArt204IntroName("NATIVE CONTROL")=="NATIVE CONTROL";
        assert(_native_name_unchanged,"Boss art204 changed an ordinary native/NTTE intro name path");
        _owner_control=fr_Objects_Frontier_Bosses_mod_gml_boss_intro("RoboBoss");
        scrFRInvoke(_owner_control,_owner_control.fr_binding_code,_owner_control.fr_binding_args);
        assert(scrFRBossArt204IntroActive() && array_length(scrFRBossArt204State().targets)==3,
            "Boss art204 rejected-start control did not apply real authored artwork");
        for(var _guard_case=0;_guard_case<3;++_guard_case) {
            var _guard_kind="no-player";
            if(_guard_case==0) _guard_kind="disabled";
            else if(_guard_case==1) _guard_kind="coop";
            UberCont.ntte_full_intro_key="REJECTED START SENTINEL";
            UberCont.opt_bossintro=_guard_case!=0;
            if(_guard_case==1) {
                // Presence-only native guard fixture. Do not initialize a
                // networking session or sockets merely to test this guard.
                _coop_guard=instance_create(0,0,FRCustomObject);
                with(_coop_guard) instance_change(CoopController,false);
            }
            if(_guard_case==2) {
                _parked=scrFRInstances(Player);
                for(var _i=0;_i<array_length(_parked);++_i) instance_deactivate_object(_parked[_i]);
            }
            var _refused=!scrFRBossArt204IntroStart(_owner_control);
            scrBossIntro(0); // The same rejected native call must not clear prior state.
            _guard_binding=fr_Objects_Frontier_Bosses_mod_gml_boss_intro("CoveHyperCrystal");
            scrFRInvoke(_guard_binding,_guard_binding.fr_binding_code,_guard_binding.fr_binding_args);
            var _source_refused=instance_exists(_guard_binding) && !_guard_binding.intro
                && !_guard_binding.fr_boss_art204_prepared;
            // Also advance the refused source's real cleanup: it must retire
            // itself without restoring another binding's active artwork.
            scrFRInvoke(_guard_binding,_guard_binding.fr_binding_code,_guard_binding.fr_binding_args);
            var _source_retired=!instance_exists(_guard_binding);_guard_binding=noone;
            var _key_preserved=UberCont.ntte_full_intro_key=="REJECTED START SENTINEL",
                _state_preserved=UberCont.fr_boss_art204_intro && UberCont.fr_boss_art204_owner==_owner_control
                    && UberCont.bossintro,_art_preserved=true;
            for(var _role=0;_role<3;++_role) {
                var _guard_art=scrFRBossArt204Capture(_targets[_role]);array_push(_captures,_guard_art);
                _art_preserved=_art_preserved && scrFRVisualSamePixels(_guard_art,_sources[_role].capture)
                    && sprite_get_xoffset(_targets[_role])==_snapshots[_role].xorigin
                    && sprite_get_yoffset(_targets[_role])==_snapshots[_role].yorigin;
            }
            for(var _i=0;_i<array_length(_parked);++_i) instance_activate_object(_parked[_i]);
            _parked=[];
            if(instance_exists(_coop_guard)) {
                with(_coop_guard) instance_change(FRCustomObject,false);
                instance_destroy(_coop_guard,false);
            }
            _coop_guard=noone;
            assert(_refused && _key_preserved && _state_preserved && _art_preserved && _source_refused && _source_retired,
                "Boss art204 rejected "+_guard_kind+" source start/cleanup changed existing key/owner/flag/artwork");
            array_push(_rejected_guards,{kind:_guard_kind,refused:_refused,
                ntte_key_preserved:_key_preserved,state_preserved:_state_preserved,
                artwork_preserved:_art_preserved,actual_source_callback_rejected:_source_refused,
                rejected_source_cleanup_preserved:_source_retired && _art_preserved});
        }
        _disabled_guard=true;
        UberCont.opt_bossintro=true;
        instance_destroy(_owner_control,false);_owner_control=noone;
        scrFRBossArt204IntroFinish();
        with(UberCont) event_perform(ev_alarm,2);
        for(var _route=0;_route<3;++_route) {
            var _kind="destroyed-owner";
            if(_route==0) _kind="ordinary";
            else if(_route==1) _kind="ntte";
            _owner_control=fr_Objects_Frontier_Bosses_mod_gml_boss_intro("RoboBoss");
            scrFRInvoke(_owner_control,_owner_control.fr_binding_code,_owner_control.fr_binding_args);
            var _actual_source=instance_exists(_owner_control) && !_owner_control.intro
                && _owner_control.fr_boss_art204_prepared && scrFRBossArt204IntroActive(),
                _dirty_rows=[],_restored_rows=[],_dirty=true;
            for(var _role=0;_role<3;++_role) {
                var _dirty_art=scrFRBossArt204Capture(_targets[_role]);array_push(_captures,_dirty_art);
                var _changed=!scrFRVisualSamePixels(_dirty_art,_snapshots[_role].capture),
                    _authored=scrFRVisualSamePixels(_dirty_art,_sources[_role].capture);
                _dirty=_dirty && _changed && _authored;
                array_push(_dirty_rows,{role:_roles[_role],target:sprite_get_name(_targets[_role]),
                    authored_pixels_match:_authored,changed_from_native:_changed});
            }
            assert(_actual_source && _dirty,"Boss art204 interrupted "+_kind+" fixture did not dirty all three real targets");
            var _destroyed_id=_owner_control;
            instance_destroy(_owner_control,false);_owner_control=noone;
            var _owner_destroyed=!instance_exists(_destroyed_id),_name_ok=false;
            // Do not query IntroActive before either accepted replacement.
            // Their real native entry must itself restore the orphaned art.
            if(_route==0) {
                UberCont.ntte_full_intro_key="";scrBossIntro(0);
            } else if(_route==1) {
                UberCont.ntte_full_intro_key="Tesseract";scrBossIntro(0);
            } else {
                _destroyed_owner=!scrFRBossArt204IntroActive() && UberCont.fr_boss_art204_owner==noone
                    && scrFRBossArt204IntroName("AFTER RESTART")=="AFTER RESTART";
                _name_ok=_destroyed_owner;
            }
            var _all_restored=true;
            for(var _role=0;_role<3;++_role) {
                var _restored_art=scrFRBossArt204Capture(_targets[_role]);array_push(_captures,_restored_art);
                var _pixels=scrFRVisualSamePixels(_restored_art,_snapshots[_role].capture),
                    _origin=sprite_get_xoffset(_targets[_role])==_snapshots[_role].xorigin
                        && sprite_get_yoffset(_targets[_role])==_snapshots[_role].yorigin;
                _all_restored=_all_restored && _pixels && _origin;
                scrFRVisualSave(_restored_art,"frontier-boss-art204-interrupted-"+_kind+"-"+string_lower(_roles[_role])+".png");
                array_push(_restored_rows,{role:_roles[_role],target:sprite_get_name(_targets[_role]),
                    restored_pixels_match:_pixels,restored_origin_match:_origin});
            }
            // This assertion intentionally precedes every Active/Name query
            // after an accepted entry: those queries can also retire stale art
            // and must not conceal a broken native-start restoration bridge.
            var _restored_before_query=_all_restored && array_length(scrFRBossArt204State().targets)==0;
            assert(_restored_before_query,"Boss art204 accepted "+_kind+" entry did not restore pixels before an Active/Name query");
            if(_route==0) {
                _ordinary_replacement=!scrFRBossArt204IntroActive()
                    && scrFRBossArt204IntroName(_ordinary_name)==_ordinary_name
                    && UberCont.fr_boss_art204_owner==noone;
                _name_ok=_ordinary_replacement;
            } else if(_route==1) {
                _ntte_replacement=!scrFRBossArt204IntroActive() && scrNTTEFullBossIntroActive()
                    && scrNTTEFullBossIntroSprite(sprBossIntro)==scrNTTERefSprite("Intro.Tesseract.Main")
                    && scrFRBossArt204IntroName("NTTE CONTROL")=="NTTE CONTROL";
                _name_ok=_ntte_replacement;
            }
            assert(_owner_destroyed && _name_ok && _all_restored && array_length(scrFRBossArt204State().targets)==0,
                "Boss art204 interrupted "+_kind+" leaked authored pixels/origin/name into the next consumer");
            if(_route<2) array_push(_interrupted,{kind:_kind,actual_source_callback:_actual_source,
                owner_destroyed:_owner_destroyed,name_path_preserved:_name_ok,dirty_layers:_dirty_rows,
                restored_layers:_restored_rows,all_native_pixels_restored:_all_restored,
                restored_before_active_query:_restored_before_query});
            else _destroyed_pixels=_all_restored;
            with(UberCont) event_perform(ev_alarm,2);
        }
        var _artifact={status:"PASS",physical_device_tested:false,resource_count:15,alias_count:30,
            resources:_resources,intros:_intros,missing_alias_rejected:_negative,
            control_coverage:_control.coverage,control_ink:_control.ink,empty_coverage:_empty.coverage,
            native_name_path_unchanged:_native_name_unchanged,disabled_intro_guard_preserved:_disabled_guard,
            rejected_start_guards:_rejected_guards,destroyed_owner_rejected:_destroyed_owner,
            ordinary_intro_replacement_isolated:_ordinary_replacement,ntte_intro_replacement_isolated:_ntte_replacement,
            interrupted_intro_restoration:_interrupted,destroyed_owner_pixels_restored:_destroyed_pixels};
        var _file=file_text_open_write(working_directory+"frontier-boss-art204.json");
        file_text_write_string(_file,json_stringify(_artifact));file_text_close(_file);
        scrNTTESmokeLog("FR_BOSS_ART204 "+json_stringify(_artifact));
    } finally {
        if(UberCont.paused) scrGameUnpause();
        scrFRBossArt204IntroFinish();
        if(instance_exists(_binding)) instance_destroy(_binding,false);
        if(instance_exists(_guard_binding)) instance_destroy(_guard_binding,false);
        for(var _i=0;_i<array_length(_parked);++_i) instance_activate_object(_parked[_i]);
        if(instance_exists(_coop_guard)) {
            with(_coop_guard) instance_change(FRCustomObject,false);
            instance_destroy(_coop_guard,false);
        }
        if(instance_exists(_owner_control)) instance_destroy(_owner_control,false);
        var _new=scrNTTEFullMergedRuntimeNew(_all_before);
        for(var _i=array_length(_new)-1;_i>=0;--_i)
            if(instance_exists(_new[_i])) instance_destroy(_new[_i],false);
        if(sprite_exists(UberCont.pausespr)) sprite_delete(UberCont.pausespr);
        if(surface_exists(UberCont.pauseimg)) surface_free(UberCont.pauseimg);
        scrNTTEFullAreaGeneratorRestore(_uber);scrNTTEFullAreaGeneratorRestore(_keys);
        for(var _alarm=0;_alarm<12;++_alarm) scrFRAlarmWrite(UberCont,_alarm,_uber_alarms[_alarm]);
        GameCont.loops=_old_loop;GameCont.subarea=_old_subarea;UberCont.opt_bossintro=_old_option;
        random_set_seed(_old_rng);
        for(var _i=0;_i<array_length(_musics);++_i) {
            var _music=_musics[_i];
            if(instance_exists(_music.id)) for(var _alarm=0;_alarm<12;++_alarm)
                scrFRAlarmWrite(_music.id,_alarm,_music.alarms[_alarm]);
        }
        for(var _i=0;_i<array_length(_snapshots);++_i) {
            var _snapshot=_snapshots[_i],_test_backup=global.fr_sprite_backups[$ _snapshot.key];
            if(sprite_exists(_snapshot.copy)) {
                sprite_assign(_snapshot.target,_snapshot.copy);sprite_delete(_snapshot.copy);
            }
            if(!is_undefined(_test_backup) && sprite_exists(_test_backup) && _test_backup!=_snapshot.backup)
                sprite_delete(_test_backup);
            if(_snapshot.had_backup) global.fr_sprite_backups[$ _snapshot.key]=_snapshot.backup;
            else variable_struct_remove(global.fr_sprite_backups,_snapshot.key);
        }
        for(var _i=0;_i<array_length(_captures);++_i) scrFRVisualFree(_captures[_i]);
        global.fr_boss_art204_state=_old_art_state;
    }
    scrNTTESmokeLog("PASS FRONTIER boss art204: all15 authored resources,30 aliases,5 enabled actual source intros, GPU pixels/origins and restoration");
}
