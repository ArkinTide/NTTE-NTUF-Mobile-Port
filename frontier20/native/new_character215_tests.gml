// Reuse the existing desktop-only sampled-pointer seam. Production input
// and hit-testing still consume the actual native loadout rows below.
function scrNTTEFullNewCharacterMenuPoint(_menu,_observer,_x,_y) {
    _observer.pointer_x=_x;_observer.pointer_y=_y;_observer.want_pointer=true;
    var _count=_observer.pointer_injections;
    with(_menu) scrMenuDrawLoadout(my_player);
    assert(!_observer.want_pointer && _observer.pointer_injections==_count+1,
        "Additional-role native loadout did not consume its sampled UI input");
}

// The real room-start and win/loop providers must accept every mobile race.
// Keep the caller's live state and durable files outside this isolated fixture.
function scrNTTEFullNewCharacterUnlockTests() {
    var _scope=scrNTTEFullSkinUnlockNaturalBegin("new-character-progress215"),_reload_map=-1;
    try {
        UberCont.custom=false;UberCont.opt_console=false;UberCont.opt_practice=false;
        global.console_active=false;GameCont.fr_progress210_blocked=false;
        GameCont.fr_achievements_blocked210=false;
        global.ntte_full_feature_ready={};
        global.ntte_full_feature_ready[$ "race:beetle"]=true;
        global.ntte_full_feature_ready[$ "race:parrot"]=true;
        global.ntte_full_progress.unlocks[$ "race:beetle"]=true;
        global.ntte_full_progress.unlocks[$ "race:parrot"]=true;
        var _source=global.fr_module_vars[$ "mod:libSaves"].saves[$ "Frontier"];
        _source.unlock_bubbles=1;
        var _p=instance_find(Player,0),_slot=scr_playerinstance_find(_p.index);
        assert(_p.index==global.index && scr_player_is_local(_p.index),"New-role fixture lost its local player slot");
        for(var _race=17;_race<=19;++_race) {
            with(_p) scrPlayerRaceChange(_race,0);
            assert(_p.race==_race && _slot.race==_race && scr_player_is_local(_p.index),
                "Actual race-change bridge lost source/native local identity: "+string(_race));
            assert(scr_race_is_unlocked(_race),"Owned additional role is unavailable in a normal run: "+string(_race));
            _p.extra_weps=[];_p.wep=wep_golden_machinegun;_p.bwep=wep_none;
            _p.ntte_state=scrNTTENewState(_p.wep);_p.bntte_state=undefined;
            UberCont.cwep[_race]=scrRaceGetStarterWeapon(_race);
            save_set_value("achievement",string(Achievement.GOOD_FIND),0);
            // Actual native Room Start owns the ordinary carried-gold callback.
            with(_p) event_perform(ev_other,ev_room_start);
            assert(UberCont.cwep[_race]==wep_golden_machinegun
                && save_get_value("cwep",string(_race))==wep_golden_machinegun
                && scrAchievementIsUnlocked(Achievement.GOOD_FIND),
                "Additional role lost carried gold or its achievement at native Room Start: "+string(_race));
            GameCont.crown=Crown.Haste;UberCont.crowngot[_race,Crown.Haste]=false;
            scrUnlocksWinOrLoop();
            assert(scr_loadout_race_is_crown_unlocked(_race,Crown.Haste)
                && save_get_value("crowngot"+string(_race),string(Crown.Haste)),
                "Additional role lost crown ownership at actual win/loop provider: "+string(_race));
            // Test the common persistent ownership boundary; source-specific
            // acquisition predicates have their own existing natural fixtures.
            if(_race<19) variable_struct_remove(global.ntte_full_progress.unlocks,"skin:"+scrNTTEFullRaceKey(_race)+":1");
            else _source.unlock_bubbles_bskin=0;
            scrRaceUnlockSkin(_race,1);
            assert(scr_race_is_skin_unlocked(_race,1),"Additional role skin award was rejected: "+string(_race));
            scr_loadout_race_set_skin(_race,1);
            assert(scr_loadout_race_get_skin(_race)==1,"Additional role could not select its earned skin: "+string(_race));
            scrSave();
            var _main=json_parse(scrNTTEFullSkinUnlockNaturalRead(game_directory+"NuclearThrone.sav"));
            assert(_main[$ "cwep_"+string(_race)]==wep_golden_machinegun
                && _main[$ "crowngot"+string(_race)+"_"+string(Crown.Haste)],
                "Additional role's native gold/crown was not in the actual saved JSON: "+string(_race));
            var _owned=json_stringify(global.ntte_full_progress);
            assert(scrNTTEFullProgressLoad() && json_stringify(global.ntte_full_progress)==_owned,
                "Additional role progress changed through actual file reload: "+string(_race));
            if(_race==19) {
                _source.unlock_bubbles_bskin=0;
                scrFRSaveLoad("Frontier");
                _source=global.fr_module_vars[$ "mod:libSaves"].saves[$ "Frontier"];
                assert(_source.unlock_bubbles_bskin==1,"Bubbles skin was not committed to its actual source save");
            }
            scrNTTESmokeLog("NEW ROLE NORMAL PROGRESS "+string(_race)+" native RoomStart/gold/achievement/win-crown/skin award/native+source JSON reload OK");
        }
        // Reconstruct the native arrays through the actual startup reader,
        // rather than treating a successful JSON write as a reload test.
        save_set_value("cheats","console",false);save_set_value("cheats","orig_console",false);
        save_set_value("cheats","practice",false);scrSave();
        for(var _race=17;_race<=19;++_race) {
            UberCont.cwep[_race]=scrRaceGetStarterWeapon(_race);
            UberCont.crowngot[_race,Crown.Haste]=false;UberCont.cskin[_race]=0;
        }
        global.ntte_full_progress={schema:1,unlocks:{},loadouts:{},stats:{}};
        assert(scrNTTEFullProgressLoad(),"New-role cold read could not load NTTE source progress");
        global.fr_module_vars[$ "mod:libSaves"].saves[$ "Frontier"]={};
        scrFRSaveLoad("Frontier");
        with(UberCont) scrInit();
        _reload_map=UberCont.saveData;
        for(var _race=17;_race<=19;++_race) {
            assert(scr_race_is_unlocked(_race) && scr_race_is_skin_unlocked(_race,1)
                && scr_loadout_race_get_skin(_race)==1
                && scr_loadout_race_get_stored_weapon(_race)==wep_golden_machinegun
                && scr_loadout_race_get_start_weapon(_race)==wep_golden_machinegun
                && scr_loadout_race_is_crown_unlocked(_race,Crown.Haste),
                "Actual native scrInit/file reload lost additional-role ownership/loadout: "+string(_race));
        }
        var _menu=instance_create(0,0,Menu),_observer=instance_create(0,0,NTTEFullSkinNativeMenuTest);
        _observer.menu=_menu;_observer.phase=3;_observer.want_pointer=false;
        _observer.pointer_injections=0;_observer.injected_phase=-1;
        _menu.loadout_open=true;_menu.loadout_frame=4;
        for(var _race=17;_race<=19;++_race) {
            scrCampfireMenuSelectionChange(_p.index,_race);_observer.target_race=_race;
            assert(my_player.race==_race,"Native menu could not preview an earned additional role");
            var _size=sprite_get_height(sprLoadoutCrown)-4,_right=gui_w+12,
                _rows=max(1,(gui_h-LETTERBOX_SIZE*4) div _size),
                _left=_right-(array_length(scrNTTEFullCrownLoadoutSlots()) div _rows)*_size,
                _wepx=(_right+_left) div 2-44+20,
                _wepy=gui_h-LETTERBOX_SIZE*2+_size div 2-19;
            scrNTTEFullNewCharacterMenuPoint(_menu,_observer,_wepx,_wepy);
            assert(my_player.cwep==scrFRContent211Starter(_race,my_player.skin),
                "Additional-role native default weapon choice failed");
            scrNTTEFullNewCharacterMenuPoint(_menu,_observer,_wepx+44,_wepy);
            assert(my_player.cwep==wep_golden_machinegun
                && scr_loadout_race_get_start_weapon(_race)==wep_golden_machinegun,
                "Additional-role saved golden weapon was invisible/unselectable in the actual native loadout: "+string(_race));
            var _skins=scrNTTEFullSkinSlots(_race),_step=sprite_get_width(sprLoadoutSkin)-4,
                _skin_x=_left-_size div 2-22,_skin_y=gui_h div 2-(_step*.5)*array_length(_skins)-2;
            scrNTTEFullNewCharacterMenuPoint(_menu,_observer,_skin_x,_skin_y);
            assert(my_player.skin==0,"Additional-role native A-skin choice failed");
            scrNTTEFullNewCharacterMenuPoint(_menu,_observer,_skin_x,_skin_y+_step);
            assert(my_player.skin==1 && scr_loadout_race_get_skin(_race)==1,
                "Additional-role earned B-skin was unavailable in the actual native loadout: "+string(_race));
            var _crowns=scrNTTEFullCrownLoadoutSlots(),_cx=_right-_size*3,
                _cy=LETTERBOX_SIZE*2-24,_found=false;
            GameCont.crown=crwn_none;
            for(var _i=0;_i<array_length(_crowns);++_i) {
                var _crown=_crowns[_i];
                if(_crown==Crown.Haste) {
                    scrNTTEFullNewCharacterMenuPoint(_menu,_observer,_cx,_cy);_found=true;break;
                }
                _cx+=_size;
                if(_cx>=_right || _crown==crwn_none) {_cx=_left;_cy+=_size;}
            }
            assert(_found && GameCont.crown==Crown.Haste && scr_loadout_race_get_start_crown(_race)==Crown.Haste,
                "Additional-role earned crown was unavailable in the actual native loadout: "+string(_race));
        }
        scrNTTESmokeLog("PASS NEW ROLE COLD READ/UI: actual native scrInit rebuild plus NTTE/Frontier file readers; real native loadout default/gold, A/B skin and crown selection for all3 roles @"+string(30/timescale));
    } finally {
        scrNTTEFullSkinUnlockNaturalEnd(_scope);
        if(_reload_map>=0 && _reload_map!=UberCont.saveData && ds_exists(_reload_map,ds_type_map)) ds_map_destroy(_reload_map);
    }
}

function scrNTTEFullCustomCharacterTests() {
    var _scope=scrNTTEFullSkinUnlockNaturalBegin("custom-character215");
    try {
        UberCont.opt_console=false;UberCont.opt_practice=false;global.console_active=false;
        GameCont.fr_progress210_blocked=false;GameCont.fr_achievements_blocked210=false;
        GameCont.fr_progress210_slot=undefined;UberCont.custom=true;
        UberCont.custom_mode_slot_index=0;UberCont.custom_options=new CustomModeOptions("CHARACTER215");
        UberCont.custom_options.unlock_chars=true;
        global.ntte_full_feature_ready[$ "race:beetle"]=true;
        global.ntte_full_feature_ready[$ "race:parrot"]=true;
        global.fr_module_vars[$ "mod:libSaves"].saves[$ "Frontier"].unlock_bubbles=0;
        var _before=json_stringify(global.ntte_full_progress),_saved=scrFRProgress210State();
        var _menu=instance_create(0,0,Menu);
        for(var _race=17;_race<=19;++_race) {
            assert(scr_race_is_unlocked(_race),"Custom Unlock Characters excludes an enabled additional role: "+string(_race));
            var _icon=noone;
            with(CharSelect) if(race==_race) _icon=id;
            assert(instance_exists(_icon),"Real custom menu omitted enabled additional role: "+string(_race));
            with(_icon) event_perform(ev_draw,0);
            assert(_icon.can,"Real custom CharSelect Draw rejected an additional role: "+string(_race));
            my_player.race=Race.Fish;
            with(_icon) event_perform(ev_mouse,ev_left_press);
            assert(my_player.race==_race,"Custom CharSelect click failed to select additional role: "+string(_race));
        }
        assert(scrFRProgress210State()==_saved,"Custom character selection replaced its isolated progress domain");
        assert(!scrFRProgress210CanStoreGold() && !scrFRAchievementsAllowed210(),
            "Temporary custom character access enabled permanent gold/achievements");
        assert(!scrNTTEFullUnlockGet("race:beetle") && !scrNTTEFullUnlockGet("race:parrot")
            && !scrFRProgress210SourceGet("unlock_bubbles",0),
            "Custom Unlock Characters awarded permanent role ownership");
        global.fr_content210_ntuf=false;
        assert(!scr_race_is_unlocked(19),"Custom Unlock Characters bypassed disabled NTUF content");
        global.fr_content210_ntuf=true;
        global.ntte_full_feature_ready[$ "race:beetle"]=false;
        assert(!scr_race_is_unlocked(17),"Custom Unlock Characters bypassed missing NTTE runtime readiness");
        scrNTTESmokeLog("PASS CUSTOM NEW ROLES: enabled roles in real CharSelect Draw/click; no permanent unlock/gold/achievement; disabled NTUF/readiness gates retained @"+string(30/timescale));
    } finally {scrNTTEFullSkinUnlockNaturalEnd(_scope);}
}
