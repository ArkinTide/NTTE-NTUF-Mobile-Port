// Isolated native input, real touch-button and native JSON preference checks.
function scrFRBubblesPreferenceTestsSample(_index,_hold,_press,_release) {
    KeyCont.hold_spec[_index]=_hold;KeyCont.press_spec[_index]=_press;
    KeyCont.release_spec[_index]=_release;
    scrFRBubblesToggleInput(_index);
}

function scrFRBubblesPreferenceTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont) && !instance_exists(MenuOptions),
        "Bubbles preference checks need the settled isolated native runner");
    var _p=instance_find(Player,0),_pi=scr_playerinstance_find(_p.index),_prefs=_pi.cprefs,
        _map=UberCont.saveData,_bytes=ds_map_write(_map),_fixture=ds_map_create(),
        _players=scrNTTEFullAreaGeneratorSnapshot(Player),_uber=scrNTTEFullAreaGeneratorSnapshot(UberCont),
        _keys=scrNTTEFullAreaGeneratorSnapshot(KeyCont),_before=scrNTTEFullInstances(all),
        _rate=game_get_speed(gamespeed_fps),_scale=timescale,_tick=current_frame,_mobile=is_mobile,
        _path=working_directory+"ntuf-bubbles-prefs-"+string(get_timer())+".json",_loaded=-1;
    assert(is_struct(_pi) && my_player==_pi,"Bubbles preference fixture needs the native local PlayerInstance");
    ds_map_copy(_fixture,_map);UberCont.saveData=_fixture;
    try {
        ds_map_delete(_fixture,"cprefs_bubbles");
        UberCont.paused=false;UberCont.want_pause=false;
        scrOptionsUpdate();
        var _old=["eyes","melting","plant","yv","steroids","horror","rogue","skeleton","parrot"];
        for(var _i=0;_i<array_length(_old);++_i)
            assert(UberCont.cpref_list[_i]==_old[_i],"Bubbles preference shifted an existing saved bit");
        assert(array_get_index(UberCont.cpref_list,"bubbles")==9 && UberCont.cpref_bubbles,
            "Bubbles preference is absent or differs from Parrot's default-on toggle");
        var _bit=1<<10;
        for(var _hz=30;_hz<=60;_hz+=30) {
            save_set_value("options","framerate",_hz);scrOptionsUpdate();
            game_set_speed(_hz,gamespeed_fps);global.time_scale=30/_hz;
            assert(game_get_speed(gamespeed_fps)==_hz && timescale==30/_hz,
                "Bubbles preference case did not use its actual native 30/60Hz rate");
            _p.race=19;_pi.cprefs|=_bit;UberCont.paused=false;
            KeyCont.activeforever[_p.index]=false;
            scrFRBubblesPreferenceTestsSample(_p.index,true,true,false);
            assert(KeyCont.activeforever[_p.index] && KeyCont.press_spec[_p.index]
                && scrFRButtonCheck(_p.index,"spec"),"Bubbles first desktop/gamepad press did not switch skill on");
            repeat(_hz/5) {
                scrFRBubblesPreferenceTestsSample(_p.index,true,false,false);
                assert(scrFRButtonCheck(_p.index,"spec") && !KeyCont.press_spec[_p.index],
                    "Holding the native spec input retriggered a toggle edge");
                current_frame+=timescale;
            }
            scrFRBubblesPreferenceTestsSample(_p.index,false,false,true);
            assert(scrFRButtonCheck(_p.index,"spec") && KeyCont.activeforever[_p.index]
                && !KeyCont.release_spec[_p.index],"Bubbles physical release stopped toggled source skill");
            scrFRBubblesPreferenceTestsSample(_p.index,true,true,false);
            assert(!scrFRButtonCheck(_p.index,"spec") && !KeyCont.activeforever[_p.index]
                && KeyCont.release_spec[_p.index],"Bubbles second native press did not switch skill off");

            save_set_value("cprefs","bubbles",false);scrOptionsUpdate();
            assert(!scr_player_pref(_pi,"bubbles") && !KeyCont.activeforever[_p.index],
                "Disabling Bubbles preference did not refresh the native bitset and clear its latch");
            scrFRBubblesPreferenceTestsSample(_p.index,true,true,false);
            assert(scrFRButtonCheck(_p.index,"spec") && KeyCont.press_spec[_p.index],
                "Disabled Bubbles toggle removed the original hold skill");
            scrFRBubblesPreferenceTestsSample(_p.index,false,false,true);
            assert(!scrFRButtonCheck(_p.index,"spec") && KeyCont.release_spec[_p.index],
                "Disabled Bubbles toggle did not preserve raw hold release");

            // Serialize/reload the real cprefs storage for both switch values.
            for(var _enabled=0;_enabled<2;++_enabled) {
                save_set_value("cprefs","bubbles",!!_enabled);scrOptionsUpdate();
                var _saved=json_encode(_fixture);
                assert(scrPersistentJsonSave(_path,_saved),"Native Bubbles preference JSON save failed");
                var _serialized=scrPersistentJsonLoad(_path);
                assert(is_string(_serialized),"Native Bubbles preference JSON reload failed");
                _loaded=json_decode(_serialized);UberCont.saveData=_loaded;
                scrOptionsUpdate();
                assert(UberCont.cpref_bubbles==!!_enabled && scr_player_pref(_pi,"bubbles")==!!_enabled,
                    "Bubbles saved switch value did not survive native file reload");
                UberCont.saveData=_fixture;ds_map_destroy(_loaded);_loaded=-1;
            }
            save_set_value("cprefs","bubbles",true);scrOptionsUpdate();
            is_mobile=true;
            var _button=instance_create(180,100,ButtonActive);
            assert(_button.can_forever(_p),"Real mobile skill button did not recognize Bubbles preference");
            KeyCont.activeforever[_p.index]=false;
            _button.volume_control_command=1;with(_button) event_perform(ev_other,ev_user0);
            assert(KeyCont.activeforever[_p.index] && KeyCont.press_spec[_p.index]
                && scrFRButtonCheck(_p.index,"spec"),"Real mobile Bubbles first press did not enable its source skill");
            _button.volume_control_command=0;with(_button) event_perform(ev_other,ev_user0);
            assert(KeyCont.activeforever[_p.index] && scrFRButtonCheck(_p.index,"spec")
                && !KeyCont.press_spec[_p.index],"Real mobile Bubbles release cleared its enabled skill");
            _button.volume_control_command=1;with(_button) event_perform(ev_other,ev_user0);
            assert(!KeyCont.activeforever[_p.index] && !scrFRButtonCheck(_p.index,"spec"),
                "Real mobile Bubbles second press did not disable its source skill");

            save_set_value("cprefs","bubbles",false);scrOptionsUpdate();
            assert(!_button.can_forever(_p),"Disabled Bubbles mobile preference still requested a latch");
            _button.volume_control_command=1;with(_button) event_perform(ev_other,ev_user0);
            assert(!KeyCont.activeforever[_p.index] && KeyCont.press_spec[_p.index],
                "Disabled Bubbles mobile preference removed the original press edge");
            _button.volume_control_command=2;with(_button) event_perform(ev_other,ev_user0);
            assert(scrFRButtonCheck(_p.index,"spec") && !KeyCont.activeforever[_p.index],
                "Disabled Bubbles mobile preference lost original held skill input");
            _button.volume_control_command=-1;with(_button) event_perform(ev_other,ev_user0);
            assert(!scrFRButtonCheck(_p.index,"spec") && KeyCont.release_spec[_p.index],
                "Disabled Bubbles mobile preference lost original skill release");
            save_set_value("cprefs","bubbles",true);scrOptionsUpdate();

            UberCont.ctot_time[19]=1;
            var _menu=instance_create(0,0,MenuOptions),_rows=_menu.options[OptionCategory.Controls_Preferences],_found=0;
            for(var _r=0;_r<array_length(_rows);++_r) if(_rows[_r].key=="cprefs_bubbles") {
                _found+=1;
                assert(_rows[_r].char==19 && method_execute(_rows[_r].condition,_rows[_r])
                    && string_pos(sprite_get_name(scrFRRaceNativeSprite("Map",0)),
                        method_execute(_rows[_r].get_name,_rows[_r]))>0,
                    "Native character preference row has wrong race, unlock condition or Bubbles icon");
            }
            assert(_found==1,"Bubbles character preference row is missing or duplicated");
            KeyCont.activeforever[_p.index]=true;
            scrFRBubblesPreferenceTestsSample(_p.index,true,true,false);
            assert(KeyCont.activeforever[_p.index] && !KeyCont.press_spec[_p.index],
                "Opening the native options menu toggled Bubbles skill");
            _button.volume_control_command=1;with(_button) event_perform(ev_other,ev_user0);
            assert(KeyCont.activeforever[_p.index],"Mobile menu input toggled Bubbles skill");
            instance_destroy(_menu,false);UberCont.paused=false;
            for(var _r=0;_r<2;++_r) {
                _p.race=_r==0?Race.Fish:NTTEFullRace.Parrot;
                KeyCont.activeforever[_p.index]=true;
                scrFRBubblesPreferenceTestsSample(_p.index,false,true,true);
                assert(KeyCont.activeforever[_p.index] && !KeyCont.hold_spec[_p.index]
                    && KeyCont.press_spec[_p.index] && KeyCont.release_spec[_p.index],
                    "Bubbles preference rewrote another race's raw input/latch");
            }
            _p.race=19;KeyCont.activeforever[_p.index]=true;
            with(_p) scrPlayerRaceChange(Race.Fish);
            assert(!KeyCont.activeforever[_p.index],"Changing away from Bubbles retained a stale skill toggle");
            instance_destroy(_button,false);
            scrNTTESmokeLog("NTUF BUBBLES PREFERENCE "+json_stringify({rate:_hz,legacy_bits_unchanged:true,
                desktop_gamepad_toggle:true,touch_toggle:true,raw_hold_preserved:true,
                persistent_on_off:true,native_menu_row:true,menu_ignored:true,other_races_unchanged:true}));
        }
    } finally {
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        if(_loaded>=0 && ds_exists(_loaded,ds_type_map)) ds_map_destroy(_loaded);
        scrNTTEFullAreaGeneratorRestore(_players);scrNTTEFullAreaGeneratorRestore(_keys);
        scrNTTEFullAreaGeneratorRestore(_uber);UberCont.saveData=_map;_pi.cprefs=_prefs;
        if(ds_exists(_fixture,ds_type_map)) ds_map_destroy(_fixture);
        game_set_speed(_rate,gamespeed_fps);global.time_scale=_scale;current_frame=_tick;is_mobile=_mobile;
        var _files=[_path,_path+".bak",_path+".tmp"];
        for(var _i=0;_i<array_length(_files);++_i) if(file_exists(_files[_i])) file_delete(_files[_i]);
        assert(ds_map_write(_map)==_bytes,"Bubbles preference fixture changed the original save map");
    }
    scrNTTESmokeLog("PASS NTUF BUBBLES native character preference:30/60Hz real touch, sampled input, original hold, file roundtrip, menus and other races");
}
