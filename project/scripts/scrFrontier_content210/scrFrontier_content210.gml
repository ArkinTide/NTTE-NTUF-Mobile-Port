// Persistent content switches share NTTE's existing progress/options store.
// A live run retains its content until it ends; changing a pack in Pause
// must not strand its player, held weapon or active boss halfway through.
function scrFRContent210Requested(_pack) {
    return !!scrNTTEFullOptionRaw("content:"+_pack);
}
function scrFRContent210RuntimeReady() {
    return variable_global_exists("fr_enabled") && global.fr_enabled && instance_exists(FRWorld);
}
function scrFRContent210Active(_pack) {
    var _key="fr_content210_"+_pack;
    return variable_global_exists(_key)?variable_global_get(_key):true;
}
function scrFRContent210InRun() {
    return instance_exists(GameCont) && !instance_exists(Menu) && !instance_exists(MenuGen)
        && !instance_exists(MainMenu);
}
function scrFRContent210WeaponEnabled(_weapon) {
    var _part=scrNTTEFullWeaponModel(_weapon),_depth=0;
    while(true) {
        var _raw=scrNTTEFullWeaponRaw(_part);
        if(_raw>=174 && _raw<=178 && !scrFRContent210Active("undergrowth")) return false;
        if(variable_global_exists("fr_weapon_keys") && !is_undefined(global.fr_weapon_keys[$ string(_raw)])
            && !scrFRContent210Active("ntuf")) return false;
        if(scrNTTEFullWeaponHasMerge(_part)==false) break;
        if(++_depth>100) return false;
        _part=scrNTTEFullWeaponMergedPart(_part);
    }
    return true;
}
function scrFRContent210Suspend() {
    // Unpause activates all native instances. Keep the library metadata live,
    // while disabled source actors stay inactive across that boundary.
    if(!scrFRContent210RuntimeReady() || scrFRContent210Active("ntuf")) return;
    var _types=[FRCustomObject,FRCustomHitme,FRCustomEnemy,FRCustomProp,
        FRCustomProjectile,FRCustomSlash,FRBinding,FRSourceEffect,FRSourcePickup];
    for(var _i=0;_i<array_length(_types);++_i) with(_types[_i]) {
        if(scrFRSessionPreserve(id)) continue;
        if(!array_contains(global.fr_content210_suspended,real(id)))
            array_push(global.fr_content210_suspended,real(id));
        instance_deactivate_object(id);
    }
}
function scrFRContent210Wake() {
    if(!variable_global_exists("fr_content210_suspended")) return;
    for(var _i=0;_i<array_length(global.fr_content210_suspended);++_i)
        instance_activate_object(global.fr_content210_suspended[_i]);
    global.fr_content210_suspended=[];
}
function scrFRContent210Selections() {
    var _players=scr_playerinstances_get_all();
    for(var _i=0;_i<array_length(_players);++_i) {
        var _p=_players[_i];
        if(!scrFRContent210Active("ntuf")) {
            if(scrFRRaceIs(_p.race)) {_p.race=Race.Fish;_p.skin=0;}
            if(scrFRSkinIs(_p.skin)) _p.skin=0;
        }
        if(!scrFRContent210WeaponEnabled(_p.cwep)) _p.cwep=wep_revolver;
        if(!scrFRContent210WeaponEnabled(_p.bwep)) _p.bwep=wep_none;
    }
    if(!scrFRContent210Active("ntuf") && scrFRCrownKey(global.crownpick)!="")
        global.crownpick=crwn_none;
}
function scrFRContent210NewRun() {
    // Also runs for Retry, where a menu frame may never occur.
    global.fr_content210_undergrowth=scrFRContent210Requested("undergrowth");
    scrFRContent210Apply(scrFRContent210Requested("ntuf"));
    scrFRContent210Selections();
}
function scrFRContent210Apply(_on) {
    if(_on==scrFRContent210Active("ntuf")) return;
    if(!_on) {
        // Source modules can replace compiled sprites in place. Snapshot the
        // current NTUF variant, then restore the original NTTE/native asset.
        global.fr_content210_sprite_on={};
        var _keys=variable_struct_get_names(global.fr_sprite_backups);
        for(var _i=0;_i<array_length(_keys);++_i) {
            var _target=handle_parse(_keys[_i]);
            if(!sprite_exists(_target)) _target=real(_keys[_i]);
            if(!sprite_exists(_target)) continue;
            global.fr_content210_sprite_on[$ _keys[_i]]=sprite_duplicate(_target);
            sprite_assign(_target,global.fr_sprite_backups[$ _keys[_i]]);
        }
        // Keep module data and the library owner for restoration. Only idle
        // source controllers remain in menus; session actors already retire
        // through the host's normal session teardown.
        global.fr_content210_suspended=[];
    } else {
        var _keys=variable_struct_get_names(global.fr_content210_sprite_on);
        for(var _i=0;_i<array_length(_keys);++_i) {
            var _target=handle_parse(_keys[_i]);
            if(!sprite_exists(_target)) _target=real(_keys[_i]);
            var _copy=global.fr_content210_sprite_on[$ _keys[_i]];
            if(sprite_exists(_target) && sprite_exists(_copy)) sprite_assign(_target,_copy);
            if(sprite_exists(_copy)) sprite_delete(_copy);
        }
        global.fr_content210_sprite_on={};
        scrFRContent210Wake();
        FRWorld.fr_previous_game=noone;
        var _lib=scrFRLibGlobal();
        if(instance_exists(_lib)) _lib.lastUpdatedFrame=scrFRSourceFrame();
    }
    global.fr_content210_ntuf=_on;
    if(!_on) scrFRContent210Suspend();
    // Native ammo/skill session state may already be retired during Retry.
    // Refresh source metadata only; native weapon rows do not need resetting.
    if(instance_exists(UberCont)) with(UberCont) {
        if(_on) scrFRWeaponsRefresh();
        scrFRSkillsInit();
    }
}
function scrFRContent210Import(_state) {
    // Old saves predate these switches and contain both enabled packs.
    // Continuing such a run must keep its existing areas and inventory valid.
    var _packs=_state[$ "content210"]??{ntuf:true,undergrowth:true};
    global.fr_content210_undergrowth=_packs.undergrowth;
    scrFRContent210Apply(_packs.ntuf);
}
function scrFRContent210Sync() {
    if(!scrFRContent210RuntimeReady() || scrFRContent210InRun()) return;
    // Complete authored initialization once even when the saved switch is
    // OFF. It supplies the settings data; no gameplay room exists yet.
    if(!scrNTTEFullValue(FRWorld,"fr_content210_boot_ready",false)) {
        for(var _i=0;_i<array_length(global.fr_tasks);++_i) {
            var _task=global.fr_tasks[_i],_name=script_get_name(_task.code);
            if(!_task.done && string_pos("_init_resume",_name)>0) return;
        }
        FRWorld.fr_content210_boot_ready=true;
    }
    global.fr_content210_undergrowth=scrFRContent210Requested("undergrowth");
    scrFRContent210Apply(scrFRContent210Requested("ntuf"));
    scrFRContent210Selections();
}
function scrFRContent210Toggle(_option) {
    if(scrFRContent210InRun()) return false;
    var _pack=_option.fr_content210_pack;
    scrNTTEFullOptionSet("content:"+_pack,!scrFRContent210Requested(_pack));
    scrFRContent210Sync();
    // The page is already open: refresh availability immediately instead of
    // waiting for its next category-awake callback.
    with(MenuOptions) {
        var _rows=options[OptionCategory.Frontier];
        for(var _i=0;_i<array_length(_rows);++_i)
            if(variable_struct_exists(_rows[_i],"fr_page"))
                _rows[_i].available=scrFRContent210Requested("ntuf");
    }
    return true;
}
function scrFRContent210Options() {
    var _old=option_number;
    scrOptionsMenuCategoryBegin(OptionCategory.Frontier);
    option_list=options[OptionCategory.Frontier];
    var _toggle={type:"button",name:scrNTTEUpdateText("NTUF CONTENT","NTUF 内容"),
        fr_content210_pack:"ntuf",halign:fa_left,available:!scrFRContent210InRun(),
        awake:function(_opt){_opt.available=!scrFRContent210InRun();},
        get_value:function(_opt){return scrFRContent210Requested(_opt.fr_content210_pack)?OPTION_ON:OPTION_OFF;},
        click:function(_opt){return scrFRContent210Toggle(_opt);}};
    // Place the sole enabled switch before the source's category rows.
    var _rows=option_list;option_list=[];scrOptionsMenuCreateElement(_toggle);
    option_list=array_concat(option_list,_rows);
    scrFRMenuOptionsDescription(scrNTTEUpdateText("CONTENT SWITCHES ARE ONLY AVAILABLE IN MENUS","内容开关仅能在主菜单或选人界面调整"));
    scrOptionsMenuCategoryEnd();
    var _rows=options[OptionCategory.Frontier];
    for(var _i=0;_i<array_length(_rows);++_i) {
        var _row=_rows[_i];
        if(variable_struct_exists(_row,"fr_page")) {
            _row.available=scrFRContent210Requested("ntuf");
            _row.awake=function(_opt){_opt.available=scrFRContent210Requested("ntuf");};
        }
    }
    scrOptionsMenuCategoryBegin(OptionCategory.NTTE_Options);
    var _existing=options[OptionCategory.NTTE_Options];option_list=[];
    for(var _i=0;_i<array_length(_existing);++_i)
        if(!variable_struct_exists(_existing[_i],"fr_content210_pack")) array_push(option_list,_existing[_i]);
    scrOptionsMenuCreateElement({type:"button",name:scrNTTEUpdateText("UNDERGROWTH CONTENT","Undergrowth 内容"),
        fr_content210_pack:"undergrowth",halign:fa_left,available:!scrFRContent210InRun(),
        awake:function(_opt){_opt.available=!scrFRContent210InRun();},
        get_value:function(_opt){return scrFRContent210Requested(_opt.fr_content210_pack)?OPTION_ON:OPTION_OFF;},
        click:function(_opt){return scrFRContent210Toggle(_opt);}});
    scrOptionsMenuCategoryEnd();option_number=_old;
}
