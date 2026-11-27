function scrRunStart() {
    scrFRContent210NewRun(); // FRONTIER210 RETRY AND NEW GAME
	if (!instance_exists(GameCont)) instance_create(0, 0, GameCont)
    GameCont.fr_progress210_blocked=scrFRProgress210Cheated();
    GameCont.fr_achievements_blocked210=!scrFRAchievementsAllowed210();
	
    random_set_seed(global.seed)
	
	print("Run started. Seed:", global.seed)
	
	with (CoopController) global.index = index
	
    var _selected_crown=global.crownpick;
    scrCreatePlayers(global.index)
    if(scrGameIsCustomMode()) {
        var _race=scr_playerinstance_find(global.index).get_race();
        var _forced=scrCustomParam("crown",crwn_random)==_selected_crown
            && scrNTTEFullCrownContentAvailable(_selected_crown);
        // The preset initialized the menu already. Random Character may
        // replace the selection during player creation, so recheck it
        // against the actual character before keeping it.
        if(_selected_crown<=crwn_none || _forced || scr_loadout_race_is_crown_unlocked(_race,_selected_crown))
            global.crownpick=_selected_crown;
        else
            global.crownpick=scr_loadout_race_get_start_crown(_race);
    }
	
	if (global.crownpick == crwn_random) {
		var _crown, _iteration = 0;
		
		do {
			_crown = irandom_range(2, crownmax)
			var _all_have = true
			
			for(var i = 0; i < player_count; ++i) {
				var _race = scr_playerinstance_find(i).get_race()
				
				if (!scr_loadout_race_is_crown_unlocked(_race, _crown)) {
					_all_have = false
					break
				}
			}
			
			if (!_all_have) _crown = crwn_none
		}
		until (_crown > crwn_none || ((++ _iteration) >= 50))
		
		scrCrownSetCurrent(_crown)
	}
	else {
		scrCrownSetCurrent(global.crownpick, true)
	}
	
    with (Player) {
		snd_play(scr_race_get_sound(race, "Cnfm", sndMutant0Cnfm))
	}
	
	scrAmmoUpdateTypeStats()
    scrNTTEFullLoadoutWeaponGameStart()
	
    if scrGameIsDailyRun() {
        save_set_value("etc", "seed", UberCont.daily_seed)
    }
	
	if scrGameIsCustomMode() {
		// Starting muts
		var _mutlist = scrCustomParam("skill_start"),
			_count = array_length(_mutlist)
		
		for(var i = _count - 1; i >= 0; --i) {
			scr_skill_set(_mutlist[i], true)
		}
		
		with (GameCont) {
			area = scrCustomParam("area", area_desert)
			subarea = scrCustomParam("subarea", 1)
			loops = scrCustomParam("loops", 1)
			rad = scrCustomParam("rad", 0)
			can_advance_stage = false
			
			hard = scrAreaGetDifficulty(area, subarea, loops)
			if (_count) level = clamp(_count + 1, 1, PLAYER_LEVEL_MAX - 1)
			if (scrCustomParam("endpoints")) ultrapoints = 1
			
			waypnt[waypoints] = area
			waysub[waypoints] = subarea
			waylps[waypoints] = loops
			waypoints ++
		}
	}
	
    // Source game_start: selected native slots exist; continuation does not replay this.
    scrNTTEFullRaceProgressRunStart()
    scrNTTEFullCrystalHeartRunStart()
    // Source race game_start: new native Players exist before first level_start.
    with(Player) scrNTTEFullRaceNativeGameStart();
    room_restart()
	
	if (scrPlayerCountRace(Race.Venuz) && scrPlayerCountRace(Race.Cuz)) {
		snd_play(choose(sndYVCuzCoop1, sndYVCuzCoop2, sndYVCuzCoop3))
	}
}
