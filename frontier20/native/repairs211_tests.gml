// Real native menu consumers and source factories, in the private-save VM.
function scrFRRepairs211Tests() {
    var _before=scrNTTEFullInstances(all),_p=scr_playerinstance_find(),
        _p_copy=json_stringify(_p),_slots=UberCont.custom_mode_slots,
        _custom=UberCont.custom,_options=UberCont.custom_options,
        _console=UberCont.opt_console,_practice=UberCont.opt_practice,_open=global.console_active,
        _blocked=scrNTTEFullValue(GameCont,"fr_progress210_blocked",false),
        _ach=scrNTTEFullValue(GameCont,"fr_achievements_blocked210",false),
        _ntuf=scrFRContent210Active("ntuf"),_ug=scrFRContent210Active("undergrowth"),
        _vx=view_xview,_vy=view_yview,_vw=view_width,_vh=view_height;
    try {
        UberCont.opt_console=false;UberCont.opt_practice=false;global.console_active=false;
        GameCont.fr_progress210_blocked=false;GameCont.fr_achievements_blocked210=false;
        UberCont.custom=true;UberCont.custom_mode_slots=[];
        var _source_weapon=FR_BUBBLES_CUTLASS;
        for(var _i=0;_i<9;++_i) {
            var _slot=new CustomModeOptions(string(_i));
            _slot.wep=_source_weapon;_slot.bwep={wep:_source_weapon};
            _slot.protowep=scrNTTEFullWeaponMerge({wep:wep_revolver},{wep:_source_weapon});
            _slot.protowep_s=174;_slot.race=_i==0?19:Race.Chicken;
            _slot.area=_i==1?207:301;array_push(UberCont.custom_mode_slots,_slot);
        }
        UberCont.custom_options=UberCont.custom_mode_slots[0];
        scrFRContent210Apply(false);global.fr_content210_undergrowth=false;
        // Before preset migration, the getter alone must protect every menu.
        assert(scrCustomParam("wep")==-1 && scrCustomParam("bwep")==-1
            && scrCustomParam("protowep")==-1,"Disabled saved scalar/struct/fusion escaped Custom getter");
        var _m=instance_create(0,0,MenuOptions);
        with(_m) {
            var _primary=__custom_mode_weapon("wep"),_secondary=__custom_mode_weapon("bwep"),
                _proto=__custom_mode_weapon("protowep");
            assert(string_pos(sprite_get_name(sprCustomModeWeaponDefault),_primary)>0
                && string_pos(sprite_get_name(sprCustomModeWeaponDefault),_secondary)>0
                && string_pos(sprite_get_name(sprCustomModeWeaponDefault),_proto)>0,
                "Actual Custom value renderer failed its character-default icons");
            UberCont.custom_options.wep=maxwep+12345;
            assert(is_string(__custom_mode_weapon("wep")),"Malformed legacy weapon left the menu sprite uninitialized");
            UberCont.custom_options.wep=FR_BUBBLES_CUTLASS;
        }
        scrFRContent211Presets();
        for(var _i=0;_i<9;++_i) {
            var _slot=UberCont.custom_mode_slots[_i];
            assert(_slot.wep==-1 && _slot.bwep==-1 && _slot.protowep==-1 && _slot.protowep_s==-1
                && _slot.area==area_desert && scrFRContent211RaceVisible(_slot.race),
                "Disabled pack survived migration in Custom slot "+string(_i));
        }
        scrCustomModeLoadPresets();
        assert(UberCont.custom_mode_slots[8].wep==-1,"Custom fallback did not survive actual disk reload");
        var _races=[Race.Chicken,Race.Rogue,Race.Venuz,17,Race.Fish],_starters=[];
        for(var _i=0;_i<array_length(_races);++_i) {
            _p.race=_races[_i];_p.skin=0;_p.cwep=_source_weapon;_p.bwep=174;
            scrFRContent210Selections();
            var _expected=scrRaceGetStarterWeapon(_races[_i]);
            assert(_p.cwep==_expected && _p.bwep==_expected,
                "Disabled weapon did not become this character's starter: "+string(_races[_i]));
            array_push(_starters,{race:_races[_i],weapon:_p.cwep});
        }
        _p.race=19;_p.cwep=_source_weapon;scrFRContent210Selections();
        assert(_p.race==Race.Fish && _p.cwep==wep_revolver,"Disabled Bubbles remained the active character");
        UberCont.custom=false;
        var _menu=instance_create(0,0,Menu);
        with(CharSelect) assert(!scrFRRaceIs(race),"Disabled Bubbles icon survived actual Menu.Create");
        with(_menu) {
            scrFRContent210Apply(true);scrFRContent211BuildSelect();
            var _found=0;with(CharSelect) if(scrFRRaceIs(race)) _found++;
            assert(_found==1,"Re-enabled Bubbles icon was missing or duplicated");
            scrFRContent210Apply(false);scrFRContent211BuildSelect();
            with(CharSelect) assert(!scrFRRaceIs(race),"Existing selection menu retained disabled Bubbles");
        }
        var _stats=instance_create(0,0,DrawStats);
        with(StatChar) assert(!scrFRRaceIs(num),"Disabled Bubbles survived actual Statistics.Create");
        var _count=instance_number(UGEnemy)+instance_number(UGProp)+instance_number(UGObject);
        assert(scrUGCreate(410000,410000,"Millipede")==noone
            && scrUGCreate(410000,410000,"FireFlower")==noone,"Disabled UG factory still creates actors");
        scrUGAfterGeneration();scrUG_area_pop_extras();scrUG_area_pop_enemies();scrUG_area_pop_props();
        assert(_count==instance_number(UGEnemy)+instance_number(UGProp)+instance_number(UGObject),
            "Disabled Undergrowth source population leaked actors");
        assert(!scrFRNTTEExists("mod","undergrowth") && !scrFRContent210WeaponEnabled(174),
            "Disabled Undergrowth module or weapon still available");
        scrNTTESmokeLog("PASS NTUF211 actual Custom menu, nine-slot disk migration, character-specific starters, dynamic selection/statistics and UG factories "+json_stringify(_starters));
        // Call both authored notice APIs after enabling the console. No
        // controller, queued portrait, popup or native award may be created.
        var _notices=instance_number(NTTEFullUnlockCont)+instance_number(AchievementSplash),
            _controllers=array_length(scrFRMatching(FRCustomObject,"name","UnlockCont"));
        UberCont.opt_console=true;
        scrNTTEFullUnlockSplat("TEST","BLOCKED",sprDefault,sndMut);
        scrFRModCallArray("mod","libSaves","unlock_popup",["TEST","BLOCKED"]);
        scrFRModCallArray("mod","libSaves","unlock_splat",["TEST","BLOCKED",sprDefault,sndMut]);
        scrFRModCallArray("mod","libSaves","unlock_splat_ext",["TEST","TEST","BLOCKED",sprDefault,0,sndMut]);
        assert(instance_number(NTTEFullUnlockCont)+instance_number(AchievementSplash)==_notices
            && array_length(scrFRMatching(FRCustomObject,"name","UnlockCont"))==_controllers,
            "Console run still presented authored NTTE/NTUF unlock notifications");
        UberCont.opt_console=false;
        scrNTTEFullUnlockSplat("TEST","BLOCKED",sprDefault,sndMut);
        assert(instance_number(NTTEFullUnlockCont)+instance_number(AchievementSplash)==_notices,
            "Closing console re-enabled notifications for the same run");
        GameCont.fr_progress210_blocked=false;GameCont.fr_achievements_blocked210=false;
        scrFRContent210Apply(true);global.fr_content210_undergrowth=true;
        var _controller=fr_Areas_cyberspace_area_gml_BluescreenController_create(10016,10016);
        with(_controller) {blueTime=114;blueChecks=3;}
        view_width=520;view_height=240;view_xview=500000.25;view_yview=499700.75;
        with(_controller) fr_Areas_cyberspace_area_gml_bluescreen_step();
        var _buttons=scrFRBluescreenUITestsButtons();
        assert(array_length(_buttons)==2,"Natural threshold failed to create YES and NO");
        for(var _i=0;_i<2;++_i) {
            var _b=_buttons[_i];
            assert(_b.creator==_controller && abs(_b.x-(_vx+260))>1000
                && abs(_b.x-(view_xview+260+(_b.yesButton?-87:-16)))<0.01
                && abs(_b.y-(view_yview+120+51))<0.01,"Blue UI buttons used stale source-world origin");
        }
        view_xview+=137.25;view_yview-=52.75;
        with(_controller) scrFRBluescreen211Align();
        for(var _i=0;_i<2;++_i) {
            var _b=_buttons[_i];
            assert(abs(_b.x-(view_xview+view_width/2+(_b.yesButton?-87:-16)))<0.01,
                "Existing Blue UI buttons did not follow a changed viewport");
        }
        scrNTTESmokeLog("PASS NTUF211 console authored notification exclusion and shifted/wide blue UI button anchors");
        view_width=_vw;view_height=_vh;view_xview=_vx;view_yview=_vy;
        var _samples=[wep_revolver,wep_chicken_sword,174,FR_BUBBLES_CUTLASS],_count=15000,_checksum=0,
            _start=get_timer();
        for(var _i=0;_i<_count;++_i) _checksum+=scrFRContent210WeaponEnabled(_samples[_i mod 4]);
        var _optimized=get_timer()-_start;_start=get_timer();
        for(var _i=0;_i<_count;++_i) _checksum+=scrFRRepairs211OldWeaponEnabled(_samples[_i mod 4]);
        var _reference=get_timer()-_start;
        assert(_checksum==_count*2,"Fast enabled-pack branch changed the weapon pool");
        var _file=file_text_open_write(working_directory+"frontier-repairs211.json");
        file_text_write_string(_file,json_stringify({version:"2.1.1",physical_device_tested:false,
            checks:["disabled-presets","race-default-starters","menu-icons","statistics","undergrowth-factories","console-popups","blue-ui-anchors"],
            benchmark:{calls:_count,optimized_us:_optimized,previous_us:_reference},starters:_starters}));
        file_text_close(_file);
        scrNTTESmokeLog("NTUF211 weapon-pool hot path "+json_stringify({calls:_count,optimized_us:_optimized,previous_us:_reference}));
    } finally {
        view_xview=_vx;view_yview=_vy;view_width=_vw;view_height=_vh;
        scrFRContent210Apply(_ntuf);global.fr_content210_undergrowth=_ug;
        _p.read_from_struct(json_parse(_p_copy));
        UberCont.custom=_custom;UberCont.custom_options=_options;UberCont.custom_mode_slots=_slots;
        UberCont.opt_console=_console;UberCont.opt_practice=_practice;global.console_active=_open;
        GameCont.fr_progress210_blocked=_blocked;GameCont.fr_achievements_blocked210=_ach;
        scrNTTEFullMergedRuntimeTestCleanup(_before);
    }
}
function scrFRRepairs211OldWeaponEnabled(_weapon) {
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
