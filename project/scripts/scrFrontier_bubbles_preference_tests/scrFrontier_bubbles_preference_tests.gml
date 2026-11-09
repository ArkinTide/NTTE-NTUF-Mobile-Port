// Preference persistence and edge policy. The separate Bubbles205 case lets
// actual 30/60Hz Player frames prove weapon exclusion and source bubble spray.
function scrFRBubblesPreferenceTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont) && !instance_exists(MenuOptions),
        "Bubbles preference checks need the settled isolated native runner");
    var _p=instance_find(Player,0),_pi=scr_playerinstance_find(_p.index),_prefs=_pi.cprefs,
        _map=UberCont.saveData,_bytes=ds_map_write(_map),_fixture=ds_map_create(),
        _players=scrNTTEFullAreaGeneratorSnapshot(Player),_uber=scrNTTEFullAreaGeneratorSnapshot(UberCont),
        _keys=scrNTTEFullAreaGeneratorSnapshot(KeyCont),_before=scrNTTEFullInstances(all),
        _mobile=is_mobile,_path=working_directory+"ntuf-bubbles-mode205-"+string(get_timer())+".json",_loaded=-1;
    ds_map_copy(_fixture,_map);UberCont.saveData=_fixture;
    try {
        ds_map_delete(_fixture,"cprefs_bubbles");UberCont.paused=false;UberCont.want_pause=false;
        scrOptionsUpdate();
        var _old=["eyes","melting","plant","yv","steroids","horror","rogue","skeleton","parrot"];
        for(var _i=0;_i<array_length(_old);++_i)
            assert(UberCont.cpref_list[_i]==_old[_i],"Bubbles preference shifted an existing saved bit");
        assert(array_get_index(UberCont.cpref_list,"bubbles")==9 && UberCont.cpref_bubbles,
            "Bubbles preference lost its saved bit or default-enabled mode switch");
        _p.race=19;_pi.cprefs|=1<<10;KeyCont.activeforever[_p.index]=false;
        KeyCont.hold_fire[_p.index]=false;KeyCont.press_fire[_p.index]=false;KeyCont.release_fire[_p.index]=false;
        KeyCont.hold_spec[_p.index]=true;KeyCont.press_spec[_p.index]=true;KeyCont.release_spec[_p.index]=false;
        scrFRBubblesToggleInput(_p.index);scrFRBubblesAttackInput205(_p.index);
        assert(KeyCont.activeforever[_p.index] && !KeyCont.hold_spec[_p.index],
            "Sampled mode press started bubbles without an attack input");
        KeyCont.hold_fire[_p.index]=true;KeyCont.press_fire[_p.index]=true;
        KeyCont.press_spec[_p.index]=false;
        scrFRBubblesToggleInput(_p.index);scrFRBubblesAttackInput205(_p.index);
        assert(KeyCont.hold_spec[_p.index] && KeyCont.press_spec[_p.index]
            && !KeyCont.hold_fire[_p.index] && !KeyCont.press_fire[_p.index],
            "Sampled attack was not exclusively remapped to Bubbles skill");
        KeyCont.hold_fire[_p.index]=false;KeyCont.press_fire[_p.index]=false;
        KeyCont.release_fire[_p.index]=true;KeyCont.press_spec[_p.index]=false;
        scrFRBubblesToggleInput(_p.index);scrFRBubblesAttackInput205(_p.index);
        assert(!KeyCont.hold_spec[_p.index] && KeyCont.release_spec[_p.index]
            && !KeyCont.release_fire[_p.index],"Sampled release left bubbles spraying or fired a charged weapon");
        KeyCont.press_spec[_p.index]=true;scrFRBubblesToggleInput(_p.index);
        KeyCont.hold_fire[_p.index]=true;KeyCont.press_fire[_p.index]=true;
        scrFRBubblesAttackInput205(_p.index);
        assert(!KeyCont.activeforever[_p.index] && KeyCont.hold_fire[_p.index]
            && KeyCont.press_fire[_p.index] && !KeyCont.hold_spec[_p.index],
            "Second mode press did not restore ordinary weapon input");
        is_mobile=true;var _button=instance_create(180,100,ButtonActive);
        assert(_button.can_forever(_p),"Real mobile skill button did not recognize the saved Bubbles mode preference");
        KeyCont.hold_fire[_p.index]=false;KeyCont.press_fire[_p.index]=false;KeyCont.release_fire[_p.index]=false;
        _button.volume_control_command=1;with(_button) event_perform(ev_other,ev_user0);
        scrFRBubblesAttackInput205(_p.index);
        assert(KeyCont.activeforever[_p.index] && !KeyCont.hold_spec[_p.index],
            "Real touch ability switch started bubbles without attack input");
        _button.volume_control_command=1;with(_button) event_perform(ev_other,ev_user0);
        scrFRBubblesAttackInput205(_p.index);
        assert(!KeyCont.activeforever[_p.index],"Real touch ability switch did not turn off");
        for(var _enabled=0;_enabled<2;++_enabled) {
            save_set_value("cprefs","bubbles",!!_enabled);scrOptionsUpdate();
            assert(scrPersistentJsonSave(_path,json_encode(_fixture)),"Native Bubbles preference JSON save failed");
            _loaded=json_decode(scrPersistentJsonLoad(_path));UberCont.saveData=_loaded;scrOptionsUpdate();
            assert(UberCont.cpref_bubbles==!!_enabled && scr_player_pref(_pi,"bubbles")==!!_enabled,
                "Bubbles mode preference did not survive actual native JSON reload");
            UberCont.saveData=_fixture;ds_map_destroy(_loaded);_loaded=-1;
        }
        save_set_value("cprefs","bubbles",false);scrOptionsUpdate();
        assert(!_button.can_forever(_p),"Disabled mobile preference still requested a mode latch");
        KeyCont.hold_fire[_p.index]=true;KeyCont.press_fire[_p.index]=true;
        _button.volume_control_command=2;with(_button) event_perform(ev_other,ev_user0);
        scrFRBubblesAttackInput205(_p.index);
        assert(KeyCont.hold_spec[_p.index] && KeyCont.hold_fire[_p.index]
            && KeyCont.press_fire[_p.index],"Disabled preference removed original independent ability/weapon controls");
        save_set_value("cprefs","bubbles",true);scrOptionsUpdate();
        UberCont.ctot_time[19]=1;
        var _menu=instance_create(0,0,MenuOptions),_rows=_menu.options[OptionCategory.Controls_Preferences],_found=0;
        for(var _r=0;_r<array_length(_rows);++_r) if(_rows[_r].key=="cprefs_bubbles") {
            _found+=1;assert(_rows[_r].char==19,"Bubbles preference row points at the wrong native race");
        }
        assert(_found==1,"Bubbles preference row is missing or duplicated");
        KeyCont.activeforever[_p.index]=true;KeyCont.press_spec[_p.index]=true;
        scrFRBubblesToggleInput(_p.index);scrFRBubblesAttackInput205(_p.index);
        assert(KeyCont.activeforever[_p.index] && !KeyCont.hold_spec[_p.index],
            "Opening native options toggled Bubbles mode or kept its spray active");
        instance_destroy(_menu,false);UberCont.paused=false;
        _p.race=Race.Fish;KeyCont.hold_fire[_p.index]=true;KeyCont.hold_spec[_p.index]=false;
        scrFRBubblesToggleInput(_p.index);scrFRBubblesAttackInput205(_p.index);
        assert(KeyCont.hold_fire[_p.index] && !KeyCont.hold_spec[_p.index],"Bubbles mode rewrote another race's input");
    } finally {
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        if(_loaded>=0 && ds_exists(_loaded,ds_type_map)) ds_map_destroy(_loaded);
        scrNTTEFullAreaGeneratorRestore(_players);scrNTTEFullAreaGeneratorRestore(_keys);
        scrNTTEFullAreaGeneratorRestore(_uber);UberCont.saveData=_map;_pi.cprefs=_prefs;
        if(ds_exists(_fixture,ds_type_map)) ds_map_destroy(_fixture);is_mobile=_mobile;
        var _files=[_path,_path+".bak",_path+".tmp"];
        for(var _i=0;_i<array_length(_files);++_i) if(file_exists(_files[_i])) file_delete(_files[_i]);
        assert(ds_map_write(_map)==_bytes,"Bubbles preference fixture changed the original save map");
    }
    scrNTTESmokeLog("PASS NTUF BUBBLES205 saved bits/default, real touch mode button, sampled fire/release mapping, disabled preference, JSON, menu and other race");
}
