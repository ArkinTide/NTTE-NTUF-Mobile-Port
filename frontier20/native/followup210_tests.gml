// Feedback acceptance: actual menu dispatch, source powder lifecycle, and
// normal/custom-slot/console progress boundaries in an isolated native save.
function scrFRFollowup210MenuClick(_pack) {
    var _m=instance_create(0,0,MenuOptions),_keyboard=UberCont.opt_keyboard,
        _gamepad=UberCont.opt_gamepad,_old=scrFRContent210Requested(_pack),
        _driver=instance_find(FRIntegrationTest,0);
    var _target=surface_create(max(640,gui_w),max(480,gui_h));
    try {
        UberCont.opt_keyboard=true;UberCont.opt_gamepad=false;
        surface_set_target(_target);
        with(_m) {
            scrFRMenuOptionsBuild();
            scrOptionsMenuChangeCategory(_pack=="ntuf"?OptionCategory.Frontier:OptionCategory.NTTE_Options);
            var _index=-1;
            for(var _i=0;_i<array_length(items);++_i)
                if((items[_i][$ "fr_content210_pack"]??"")==_pack) _index=_i;
            assert(_index>=0 && is_method(items[_index].click),"Content row lacks a native executable click method");
            wait=false;last_change=current_frame-100;pointed_item=_index;
            mouse_active=false;scroll_speed=0;slider=undefined;slider_change=0;
            mx_last=device_mouse_x_to_gui(0);my_last=device_mouse_y_to_gui(0);
            // Measure the real list before keeping its target row in view.
            wait=true;event_perform(ev_other,10);wait=false;
            scroll=_index==0?scroll_min:scroll_max;
            pointed_item=_index;mouse_active=false;
            // Feed one raw Enter sample through the existing desktop fixture.
            // The real options event still owns hit selection and dispatch.
            _driver.fr_followup210_keyboard={held:-1,pressed:vk_enter,released:-1};
            event_perform(ev_other,10);
            _driver.fr_followup210_keyboard=undefined;
        }
        if(scrFRContent210Requested(_pack)==_old)
            scrNTTESmokeLog("CONTENT210 MENU DISPATCH "+json_stringify({pack:_pack,
                category:_m.category,pointed:_m.pointed_item,mouse:_m.mouse_active,
                count:_m.item_count,wait:_m.wait,scroll:_m.scroll,run:scrFRContent210InRun(),
                first_available:_m.items[0].available,first_name:_m.items[0].name}));
        assert(scrFRContent210Requested(_pack)!=_old,"Native Enter/click dispatcher failed content toggle "+_pack);
        assert(scrFRContent210Active(_pack)==!_old,"Menu switch did not apply its real content state");
        if(_pack=="ntuf") {
            var _rows=_m.options[OptionCategory.Frontier];
            for(var _i=0;_i<array_length(_rows);++_i)
                if(variable_struct_exists(_rows[_i],"fr_page"))
                    assert(_rows[_i].available==!_old,"Open NTUF settings page did not refresh its disabled rows");
        }
        scrNTTESmokeLog("PASS NTUF210 actual MenuOptions Enter dispatch "+_pack);
    } finally {
        _driver.fr_followup210_keyboard=undefined;surface_reset_target();
        if(surface_exists(_target)) surface_free(_target);
        UberCont.opt_keyboard=_keyboard;UberCont.opt_gamepad=_gamepad;
        if(instance_exists(_m)) instance_destroy(_m);
    }
}
function scrFRFollowup210Tests() {
    var _progress=global.ntte_full_progress,_before=scrNTTEFullInstances(all),
        _players=scrNTTEFullAreaGeneratorSnapshot(Player),_p=instance_find(Player,0),
        _console=UberCont.opt_console,_practice=UberCont.opt_practice,_custom=UberCont.custom,
        _slot=UberCont.custom_mode_slot_index,_open=global.console_active,
        _blocked=scrNTTEFullValue(GameCont,"fr_progress210_blocked",false),
        _pinned=scrNTTEFullValue(GameCont,"fr_progress210_slot",undefined),
        _volatile=scrNTTEFullValue(GameCont,"fr_progress210_volatile",undefined),
        _ach=scrNTTEFullValue(GameCont,"fr_achievements_blocked210",false),
        _language=global.language_current[$ "Init:Id"],_gold=scr_loadout_race_get_stored_weapon(_p.race),
        _namespace=global.fr_module_vars[$ "mod:libSaves"].saves,
        _frontier=_namespace[$ "Frontier"],_frontier_copy=json_stringify(_namespace[$ "Frontier"]),
        _fishing=_namespace[$ "Frontier_Fishing"]??{},
        _fishing_copy=json_stringify(_namespace[$ "Frontier_Fishing"]??{});
    try {
        global.ntte_full_progress=json_parse(json_stringify(_progress));
        UberCont.opt_console=false;UberCont.opt_practice=false;UberCont.custom=false;global.console_active=false;
        GameCont.fr_progress210_blocked=false;GameCont.fr_achievements_blocked210=false;
        var _key="__followup210",_normal=scrNTTEFullUnlockGet(_key,false);
        assert(!_normal,"Progress fixture key is not isolated");
        for(var _i=0;_i<2;++_i) {
            UberCont.custom=true;UberCont.custom_mode_slot_index=_i;GameCont.fr_progress210_slot=_i;
            assert(!scrNTTEFullUnlockGet(_key,false),"Custom slots share NTTE unlocks");
            assert(scrFRModCallArray("mod","libSaves","save_get",["Frontier",_key,0])==0,
                "Custom slots share Frontier unlocks");
            assert(scrFRModCallArray("mod","libSaves","save_get",["Frontier_Fishing",_key,0])==0,
                "Custom slots share Fishing discoveries");
            scrNTTEFullUnlockSet(_key,_i+1);
            scrFRModCallArray("mod","libSaves","save_set",["Frontier",_key,_i+1]);
            scrFRModCallArray("mod","libSaves","save_set",["Frontier_Fishing",_key,_i+11]);
            assert(scrNTTEFullUnlockGet(_key)==_i+1
                && scrFRModCallArray("mod","libSaves","save_get",["Frontier",_key])==_i+1
                && scrFRModCallArray("mod","libSaves","save_get",["Frontier_Fishing",_key])==_i+11,
                "Custom slot failed its real unlock/save APIs");
            assert(!scr_loadout_race_set_stored_weapon(_p.race,wep_golden_revolver),"Custom mode stored native gold");
            scrAchievementUnlock(0);assert(!scrFRAchievementsAllowed210(),"Custom mode awarded native achievement");
        }
        // Reload the actual disk progress file, then switch slots and normal.
        scrNTTEFullProgressLoad();
        for(var _i=0;_i<2;++_i) {
            UberCont.custom_mode_slot_index=_i;GameCont.fr_progress210_slot=_i;
            assert(scrNTTEFullUnlockGet(_key)==_i+1
                && scrFRModCallArray("mod","libSaves","save_get",["Frontier",_key])==_i+1
                && scrFRModCallArray("mod","libSaves","save_get",["Frontier_Fishing",_key])==_i+11,
                "Slot-specific unlocks failed disk reload");
        }
        UberCont.custom=false;
        assert(!scrNTTEFullUnlockGet(_key,false) && json_stringify(_namespace[$ "Frontier"])==_frontier_copy
            && json_stringify(_namespace[$ "Frontier_Fishing"]??{})==_fishing_copy,
            "Custom unlocks polluted normal NTTE or source Frontier data");
        global.console_active=true;
        assert(!scrNTTEFullUnlockSet(_key,true),"Open console unlocked NTTE content");
        scrFRModCallArray("mod","libSaves","save_set",["Frontier",_key,9]);
        scrFRModCallArray("mod","libSaves","save_set",["Frontier_Fishing",_key,9]);
        assert(json_stringify(_namespace[$ "Frontier"])==_frontier_copy,"Open console wrote Frontier progress");
        assert(json_stringify(_namespace[$ "Frontier_Fishing"]??{})==_fishing_copy,"Open console wrote Fishing records");
        scrNTTESmokeLog("PASS NTUF210 separate Frontier_Fishing records obey per-slot disk and console gates");
        assert(!scr_loadout_race_set_stored_weapon(_p.race,wep_golden_revolver),"Open console stored gold");
        global.console_active=false;
        var _saved=scrNTTEFullSystemsExport();GameCont.fr_progress210_blocked=false;
        scrNTTEFullSystemsImport(json_parse(json_stringify(_saved)));
        assert(!scrFRProgress210CanUnlock() && !scrFRProgress210CanStoreGold(),
            "Closing console/Continue restored permanent progress eligibility");
        assert(scr_loadout_race_get_stored_weapon(_p.race)==_gold,"Blocked storage changed owned gold");
        GameCont.fr_progress210_blocked=false;GameCont.fr_achievements_blocked210=false;
        global.language_current[$ "Init:Id"]="Simplified Chinese";
        assert(scrRaceGetUnlockDescription(NTTEFullRace.Beetle)=="打开秘密宝箱",
            "Actual character-menu unlock description is not the requested Chinese text");
        for(var _rate=30;_rate<=60;_rate+=30) {
            save_set_value("options","framerate",_rate);scrOptionsUpdate();scrNTTEFullRateApply();
            var _hammer=global.fr_weapon_ids[$ "FR_PowderHammer"];
            scrFRWeaponVisualTestsPrepare(_p,_hammer);
            with(_p) {
                var _charge=scrFRWeaponPrepare(_hammer,true);
                _charge.chrg=-1;_charge.chrg_num=_charge.chrg_max;
                scrFire(wep,false,true);
            }
            var _shots=[];
            with(FRCustomProjectile) if(on_destroy==fr_Objects_Frontier_Projectiles_mod_gml_GunpowderProjectile_destroy)
                array_push(_shots,id);
            assert(array_length(_shots)==6,"Real fully charged Powder Hammer failed to fire six powder shots");
            var _drone=scrFRDronePerformance204Factory(_p.x,_p.y,false);
            for(var _j=0;_j<array_length(_shots);++_j) {
                var _shot=_shots[_j];
                assert(_shot.team==team_player && !scrFRHyperionEnemyProjectile(_shot),"Powder flight lost friendly team");
                with(_drone) with(_shot) event_perform(ev_collision,projectile);
                assert(instance_exists(_shot),"Friendly flying powder was intercepted");
                instance_destroy(_shot);
            }
            var _creeps=[];
            with(FRCustomSlash) if(on_step==fr_Objects_Frontier_Projectiles_mod_gml_GunpowderCreep_step) array_push(_creeps,id);
            assert(array_length(_creeps)==6,"Actual powder destruction did not create its six ground creeps");
            for(var _j=0;_j<array_length(_creeps);++_j) {
                var _creep=_creeps[_j];
                assert(_creep.team==1724 && scrFRHyperionAlliedPair210(_drone,_creep)
                    && scrFRHyperionAlliedPair210(_creep,_drone),"Ground powder lost friendly origin");
                with(_drone) with(_creep) event_perform(ev_collision,projectile);
                assert(instance_exists(_creep) && !scrFRHyperionEnemyProjectile(_creep),"Drone nullified allied ground powder");
            }
            scrNTTEFullMergedRuntimeTestCleanup(_before);
        }
        scrNTTESmokeLog("PASS NTUF210 per-slot NTTE+NTUF disk persistence, console sticky/Continue exclusions, gold gates, actual Beetle tooltip and real charged powder30/60");
    } finally {
        scrNTTEFullMergedRuntimeTestCleanup(_before);scrNTTEFullAreaGeneratorRestore(_players);
        global.ntte_full_progress=_progress;_namespace.Frontier=_frontier;
        _namespace.Frontier_Fishing=_fishing;scrNTTEFullProgressSave();
        UberCont.opt_console=_console;UberCont.opt_practice=_practice;UberCont.custom=_custom;
        UberCont.custom_mode_slot_index=_slot;global.console_active=_open;
        GameCont.fr_progress210_blocked=_blocked;GameCont.fr_progress210_slot=_pinned;
        GameCont.fr_progress210_volatile=_volatile;GameCont.fr_achievements_blocked210=_ach;
        global.language_current[$ "Init:Id"]=_language;
    }
}
