function scrFRFeatures210Tests() {
    scrFRContent210Tests();
    scrFRWeatherMusic210Tests();
    scrFRHyperionPair210Tests();
    var _player=instance_find(Player,0),_players=scrNTTEFullAreaGeneratorSnapshot(Player),
        _before=scrNTTEFullInstances(all),_seed=random_get_seed(),_rng=scrNTTEFullArrayCopy(global.rng_state),
        _console=UberCont.opt_console,_practice=UberCont.opt_practice,_custom=UberCont.custom,
        _open=global.console_active,_blocked=scrNTTEFullValue(GameCont,"fr_achievements_blocked210",false);
    try {
        UberCont.opt_console=false;UberCont.opt_practice=false;UberCont.custom=false;global.console_active=false;
        GameCont.fr_achievements_blocked210=false;
        assert(scrFRAchievementsAllowed210(),"Ordinary run lost achievement eligibility");
        // Native ID 0 has no legacy/source alias. Exercise the actual award
        // consumer, not just the eligibility helper, in this isolated save.
        var _achievement=save_get_value("achievement","0");
        save_set_value("achievement","0",0);
        assert(!scrAchievementIsUnlocked(0),"Achievement negative control was already unlocked");
        var _reasons=["console","practice","custom","open"];
        for(var _i=0;_i<4;++_i) {
            GameCont.fr_achievements_blocked210=false;
            UberCont.opt_console=_i==0;UberCont.opt_practice=_i==1;
            UberCont.custom=_i==2;global.console_active=_i==3;
            assert(!scrFRAchievementsAllowed210(),"Achievement gate missed "+_reasons[_i]);
            var _splashes=instance_number(AchievementSplash);
            scrAchievementUnlock(0);
            assert(!scrAchievementIsUnlocked(0) && instance_number(AchievementSplash)==_splashes,
                "Blocked native achievement award wrote a save or notification");
            UberCont.opt_console=false;UberCont.opt_practice=false;UberCont.custom=false;global.console_active=false;
            assert(!scrFRAchievementsAllowed210(),"Closing cheat state re-enabled this run's achievements");
            var _saved=scrNTTEFullSystemsExport();GameCont.fr_achievements_blocked210=false;
            scrNTTEFullSystemsImport(_saved);
            assert(!scrFRAchievementsAllowed210(),"Continue discarded achievement exclusion");
        }
        GameCont.fr_achievements_blocked210=false;
        save_set_value("achievement","0",_achievement);
        var _count=0,_ids=variable_struct_get_names(global.fr_weapon_keys),_rows=[];
        for(var _i=0;_i<array_length(_ids);++_i) {
            var _raw=real(_ids[_i]),_key=global.fr_weapon_keys[$ _ids[_i]];
            if(!scrFRWeaponProperty(_key,"weapon_chrg",false)) continue;
            with(_player) {
                wep=_raw;bwep=wep_wrench;race=Race.Fish;ntte_state=scrNTTENewState(_raw);
                fr_source_wep=undefined;fr_source_bwep=undefined;
                var _state=scrFRWeaponChargeState(_raw,true),_max=_state.chrg_max;
                _state.chrg=1;_state.chrg_num=_max/2;
                var _serialized=json_stringify(_state),_bars=scrFRChargeBars210Collect();
                assert(array_length(_bars)==1 && _bars[0].fraction==0.5,
                    "Charge HUD did not read physical source state: "+_key);
                assert(json_stringify(_state)==_serialized,"Charge HUD mutated weapon state");
                _state.chrg_num=_max;_state.chrg=2;
                assert(scrFRChargeBars210Collect()[0].fraction==1,"Full charge HUD did not reach 100%: "+_key);
                _state.chrg_num=0;_state.chrg=0;
                assert(array_length(scrFRChargeBars210Collect())==0,"Released charge HUD remained visible: "+_key);
                array_push(_rows,{weapon:_key,maximum:_max});_count++;
            }
        }
        assert(_count>=6,"NTUF charge weapon enumeration missed source charge declarations");
        with(_player) {
            var _charged=real(_ids[0]);
            for(var _j=0;_j<array_length(_ids);++_j)
                if(scrFRWeaponProperty(global.fr_weapon_keys[$ _ids[_j]],"weapon_chrg",false)) {_charged=real(_ids[_j]);break;}
            race=Race.Steroids;wep=_charged;bwep=_charged;
            ntte_state=scrNTTENewState(wep);bntte_state=scrNTTENewState(bwep);
            fr_source_wep=undefined;fr_source_bwep=undefined;
            var _a=scrFRWeaponChargeState(wep,true),_b=scrFRWeaponChargeState(bwep,false);
            _a.chrg=1;_a.chrg_num=_a.chrg_max*0.25;
            _b.chrg=1;_b.chrg_num=_b.chrg_max*0.75;
            var _bars=scrFRChargeBars210Collect();
            assert(array_length(_bars)==2 && _bars[0].fraction==0.25 && _bars[1].fraction==0.75,
                "Dual-wield charge HUD conflated the two physical weapons");
            var _merged=scrNTTEFullWeaponMerge({wep:_charged},{wep:_charged}),
                _front=scrNTTEFullWeaponMergedPart(_merged);
            _merged.ntte_native_state={fr_source_weapon:_a};_front.ntte_native_state={fr_source_weapon:_b};
            var _parts=scrFRChargeBars210Part(_merged,[]);
            assert(array_length(_parts)==2,"Fusion charge HUD omitted a physical component");
        }
        scrNTTESmokeLog("PASS NTUF210 source charge HUD and sticky achievement gates "+json_stringify(_rows));
    } finally {
        scrNTTEFullMergedRuntimeTestCleanup(_before);scrNTTEFullAreaGeneratorRestore(_players);
        UberCont.opt_console=_console;UberCont.opt_practice=_practice;UberCont.custom=_custom;
        global.console_active=_open;GameCont.fr_achievements_blocked210=_blocked;
        random_set_seed(_seed);global.rng_state=_rng;
    }
}

function scrFRHyperionPair210Tests() {
    var _before=scrNTTEFullInstances(all),_p=instance_find(Player,0);
    try {
        var _drone=scrFRDronePerformance204Factory(217000,217000,false),
            _bubble=instance_create(216920,217000,NTTEAttack);
        _bubble.kind=NTTEKind.Bubble;_bubble.team=team_player;_bubble.creator=_p;
        _bubble.direction=17;_bubble.speed=3;
        with(_drone) with(_bubble) event_perform(ev_collision,projectile);
        assert(instance_exists(_bubble) && _bubble.direction==17 && _bubble.speed==3,
            "Friendly bubble deflected itself against Hyperion's inherited Slash identity");
        var _shot=instance_create(_drone.x+40,_drone.y,EnemyBullet1),_threat=false;
        _shot.team=team_enemy;with(_drone) _threat=scrFRDroneThreat210();
        assert(_threat,"Spatial threat query missed a nearby hostile projectile");
        _shot.team=team_player;with(_drone) _threat=scrFRDroneThreat210();
        assert(!_threat,"Spatial threat query retained a reflected friendly projectile");
        scrNTTESmokeLog("PASS NTUF210 reciprocal friendly bubble collision and live spatial threat teams");
    } finally {scrNTTEFullMergedRuntimeTestCleanup(_before);}
}

function scrFRContent210Tests() {
    var _before=scrNTTEFullInstances(all),_old=scrFRContent210Active("ntuf"),
        _ug=scrFRContent210Active("undergrowth"),_menu=noone,
        _requested=scrFRContent210Requested("ntuf"),_ug_requested=scrFRContent210Requested("undergrowth");
    try {
        _menu=instance_create(0,0,MenuOptions);
        with(_menu) {
            scrFRMenuOptionsBuild();
            var _rows=options[OptionCategory.Frontier],_switches=0,_pages=0;
            for(var _i=0;_i<array_length(_rows);++_i) {
                var _row=_rows[_i];
                if(variable_struct_exists(_row,"fr_content210_pack")) _switches++;
                if(variable_struct_exists(_row,"fr_page")) _pages++;
            }
            assert(_switches==1 && _pages==6,"Content switch must retain all NTUF settings pages");
        }
        for(var _pass=0;_pass<3;++_pass) {
            var _on=(_pass mod 2)==0;
            scrNTTEFullOptionSet("content:ntuf",_on);
            scrNTTEFullOptionSet("content:undergrowth",_on);
            global.fr_content210_undergrowth=_on;scrFRContent210Apply(_on);
            assert(scrFREnabled()==_on,"NTUF runtime ignored content switch");
            assert(scrFRContent210RuntimeReady(),"Content switch removed its own settings owner");
            assert(scr_weapon_is_valid(wep_revolver),"NTUF OFF removed native weapon support");
            assert(scrFRContent210WeaponEnabled(174)==_on,"Undergrowth weapon leaked while disabled");
            var _ids=variable_struct_get_names(global.fr_weapon_keys);
            for(var _i=0;_i<array_length(_ids);++_i) {
                var _w=real(_ids[_i]);
                assert(scrFRContent210WeaponEnabled(_w)==_on && scr_weapon_is_valid(_w)==_on,
                    "NTUF weapon pool ignored content switch: "+_ids[_i]);
            }
            assert(_on || (!scrFRRaceAvailable() && !scrFRCrownAvailable() && !scrFRSkillAvailable("AugmentCompassion")),
                "Disabled NTUF race/crown/mutation remained selectable");
            with(_menu) {
                scrFRMenuOptionsBuild();var _rows=options[OptionCategory.Frontier],_pages=0;
                for(var _i=0;_i<array_length(_rows);++_i) {
                    var _row=_rows[_i];
                    if(variable_struct_exists(_row,"fr_page")) {
                        assert(_row.available==_on,"Disabled NTUF setting remained clickable");_pages++;
                    }
                    if(variable_struct_exists(_row,"fr_content210_pack"))
                        assert(_row.available==!scrFRContent210InRun(),"Content switch ignored live-run lock");
                }
                assert(_pages==6,"Content toggle discarded a recoverable settings page");
            }
            scrNTTESmokeLog("NTUF210 content cycle "+string(_pass)+" enabled="+string(_on));
        }
    } finally {
        scrNTTEFullOptionSet("content:ntuf",_requested);
        scrNTTEFullOptionSet("content:undergrowth",_ug_requested);
        scrFRContent210Apply(_old);global.fr_content210_undergrowth=_ug;
        scrNTTEFullMergedRuntimeTestCleanup(_before);
    }
}

function scrFRWeatherMusic210Tests() {
    var _created=!instance_exists(MusCont);
    if(_created) instance_create(0,0,MusCont);
    var _area=GameCont.area,_sub=GameCont.subarea,_loops=GameCont.loops,
        _token=scrNTTEFullValue(GameCont,"fr_weather_music210",undefined),
        _song=MusCont.song,_amb=MusCont.amb,_old=MusCont.oldarea,
        _music=global.fr_module_vars[$ "mod:Frontier_Events"].musThunderstorm;
    try {
        // Exercise the actual native late area-music event, including the
        // NTTE custom-area early return that used to overwrite weather.
        for(var _i=0;_i<2;++_i) {
            GameCont.area=_i==0?area_desert:201;GameCont.subarea=1;GameCont.loops=1;
            scrFRWeatherMusic210(_music);
            MusCont.oldarea=-99;
            with(MusCont) event_perform(ev_alarm,11);
            assert(MusCont.song==custom_sound_check(_music),"Weather music was overwritten in its trigger room");
            scrFRSoundMusic(musBoss1);
            assert(MusCont.song==custom_sound_check(musBoss1),"Weather prevented boss theme from taking priority");
            GameCont.subarea=2;
            assert(!scrFRWeatherMusic210Apply(),"Previous-room weather music leaked into the next level");
        }
        scrNTTESmokeLog("PASS NTUF210 same-room weather/native music boundary and next-room isolation");
    } finally {
        GameCont.area=_area;GameCont.subarea=_sub;GameCont.loops=_loops;
        GameCont.fr_weather_music210=_token;MusCont.oldarea=_old;
        scrFRSoundMusic(_song);MusCont.amb=_amb;
        if(_created) instance_destroy(MusCont);
    }
}
