function scrLoadoutMenuInit() {
	with UberCont {
		var _all_crowns = true,
			_any_crowns = false,
			_crownmax = min(crownmax,13)
		
		for (var _race_id = Race.Fish; _race_id < Race.NUM_ALL_RACE_TYPES; ++_race_id) {
			_all_crowns = true
			
			var _unlocked_crowns = 0
			
			for (var _crown_id = 1; _crown_id <= _crownmax; _crown_id++) {
				if (crowngot[_race_id, _crown_id]) {
					if (_crown_id > crwn_none) {
						_unlocked_crowns ++
						_any_crowns = true
					}
				}
				else if (_crown_id > crwn_none) {
					_all_crowns = false
				}
			}
		
			save_set_value("crowngottotal", _race_id, _unlocked_crowns)

			if _all_crowns {
				scrAchievementUnlock(Achievement.VAULT_RAIDER)
			}
		}

		if _any_crowns {
			scrAchievementUnlock(Achievement.CROWN_LIFE)
		}
	}
}


/// @function scr_loadout_race_get_stored_weapon
/// @param {Real|Enum.Race} race_id
function scr_loadout_race_get_stored_weapon(_race_id) {
	with UberCont {
		var _cwep = cwep[_race_id]
		
		if _cwep == 0 {
			return race_swep[_race_id]
		}
		
		return scrFRContent210WeaponEnabled(_cwep)?_cwep:scrFRContent211Starter(_race_id)
	}
	
	return wep_none
}

/// @function scr_loadout_race_set_stored_weapon
/// @param {Real|Enum.Race} race_id
function scr_loadout_race_set_stored_weapon(_race_id, _weapon_id) {
    if(!scrFRProgress210CanStoreGold()) return false;
    if(scrNTTEFullLoadoutWeaponEligible(_weapon_id)) return scrNTTEFullLoadoutWeaponStore(_race_id,_weapon_id);
    // Ordinary golden weapons use a stable native ID in permanent storage.
    _weapon_id=scrNTTEFullWeaponRaw(_weapon_id);
    with(UberCont) {
        if(cwep[_race_id]==_weapon_id) return false;
        scr_loadout_race_set_start_weapon(_race_id,_weapon_id);
        cwep[_race_id]=_weapon_id;
        scrSave();
        return true;
    }
    return false;
}

/// @function scr_loadout_race_get_start_weapon
/// @praam {Real|Enum.Race} race_id
function scr_loadout_race_get_start_weapon(_race_id) {
    // BEGIN FRONTIER RACE SAVED STARTER
    if(scrFRRaceIs(_race_id)) return scrFRRaceLoadoutWeapon(_race_id);
    // END FRONTIER RACE SAVED STARTER

	with UberCont {
		return save_get_value("cswep", _race_id, scrRaceGetStarterWeapon(_race_id))
	}
	
	return wep_none
}

/// @function scr_loadout_race_set_start_weapon
/// @praam {Real|Enum.Race} race_id
/// @param weapon_id
function scr_loadout_race_set_start_weapon(_race_id, _weapon_id) {
    if(scrNTTEFullLoadoutWeaponSelect(_race_id,_weapon_id)) return true
    if(scrNTTEFullLoadoutGet(scrNTTEFullLoadoutWeaponKey(_race_id),"")!="") scrNTTEFullLoadoutSet(scrNTTEFullLoadoutWeaponKey(_race_id),"")
	with UberCont {
		if (!scr_weapon_is_valid(_weapon_id)) break
		
		if (my_player.get_race() == _race_id && !scrGameIsEventRun()) {
			my_player.cwep = _weapon_id
		}
		
		save_set_value("cswep", _race_id, _weapon_id)
	}
}

/// @function scr_loadout_race_get_start_crown
/// @param {Real|Enum.Race} race_id
function scr_loadout_race_get_start_crown(_race_id) {
    if(scrGameIsCustomMode()) {
        var _custom=scrNTTEFullLoadoutGet("start:crown:"+string(_race_id),crwn_none);
        return scr_loadout_race_is_crown_unlocked(_race_id,_custom)?_custom:crwn_none;
    }
    var _saved=save_get_value("ccrown",_race_id,crwn_none);
    if(_saved>=14 && _saved<=17)
        return scrNTTEFullCrownLoadoutAvailable(_race_id,_saved)?_saved:crwn_none;
    return scr_race_is_unlocked(_race_id)?_saved:crwn_none;
}

/// @function scr_loadout_race_set_start_crown
/// @param {Real|Enum.Race} race_id
/// @param crown_id
function scr_loadout_race_set_start_crown(_race_id, _crown_id) {
    if(!scr_loadout_race_is_crown_unlocked(_race_id,_crown_id)) return false;
    if(scrGameIsCustomMode()) {
        if(!scrFRProgress210CanUnlock()) return false;
        scrNTTEFullLoadoutSet("start:crown:"+string(_race_id),_crown_id);
    } else {
        save_set_value("ccrown",_race_id,_crown_id);
    }
    return true;
}

/// @function scr_loadout_race_is_crown_unlocked
/// @param {Real|Enum.Race} race_id
/// @param crown_id
function scr_loadout_race_is_crown_unlocked(_race_id, _crown_id) {
    if(!scr_crown_is_valid(_crown_id)) return false;
    if(_crown_id>=14 && _crown_id<=17) return scrNTTEFullCrownLoadoutAvailable(_race_id,_crown_id);
	with UberCont {
		if (scrGameIsCustomMode() && scrCustomParam("unlock_crowns")) {
			return true
		}
		
		return scr_race_is_unlocked(_race_id) && crowngot[_race_id, _crown_id]
	}
	
	return false
}

/// @function scr_loadout_race_unlock_crown
/// @param {Real|Enum.Race} race_id
/// @param {Real|Enum.Crown} crown_id
function scr_loadout_race_unlock_crown(_race_id, _crown_id) {
    if(!scrNTTEFullCrownContentAvailable(_crown_id) || !scrFRProgress210CanUnlock()) return false;
    if(_crown_id>=14 && _crown_id<=17)
        return scrNTTEFullCrownLoadoutUnlock(_crown_id);
    with(UberCont) {
        if(crowngot[_race_id,_crown_id]) return false;
        scr_loadout_race_set_start_crown(_race_id,_crown_id);
        crowngot[_race_id,_crown_id]=true;
        scrSave();
        return true;
    }
    return false;
}

/// @function scr_loadout_race_get_unlocked_crowns_count
/// @param {Real|Enum.Race} race_id
function scr_loadout_race_get_unlocked_crowns_count(_race_id) {
    return scrNTTEFullCrownLoadoutCount(_race_id)
}

/// @function scr_loadout_race_get_skin
/// @param {Real|Enum.Race} race_id
function scr_loadout_race_get_skin(_race_id) {
    var _custom=scrNTTEFullSkinSaved(_race_id)
    if (_custom>=200) return _custom
	return UberCont.cskin[_race_id]
}

/// @function scr_loadout_race_set_skin
/// @param {Real|Enum.Race} race_id
/// @param skin_id
function scr_loadout_race_set_skin(_race_id, _skin_id) {
    if (_skin_id>=200) {
        if (!scr_race_is_skin_unlocked(_race_id,_skin_id)) return false
        scrNTTEFullLoadoutSet("skin:"+string(_race_id),scrNTTEFullSkinKey(_skin_id))
        return true
    }
	with UberCont {
		if scr_race_is_unlocked(_race_id) && scr_race_is_skin_unlocked(_race_id,_skin_id) {
			cskin[_race_id] = _skin_id
            if (scrNTTEFullLoadoutGet("skin:"+string(_race_id),"")!="") scrNTTEFullLoadoutSet("skin:"+string(_race_id),"")
			return true
		}
	}
	
	return false
}

/// @function scr_loadout_is_available_for_race
/// @param {Real|Enum.Race} race_id
function scr_loadout_is_available_for_race(_race) {
	if (scrGameIsCustomMode() && scrCustomParam("unlock_crowns")) {
		return true
	}
	
	if (_race == Race.BigDog || _race == Race.Skeleton || _race == Race.Frog) {
		return (!instance_exists(CoopController) && !scrGameIsEventRun()
			&& scr_loadout_can_access_hidden_ntt_skins())
	}
	
	return true
}

function scr_loadout_can_access_hidden_ntt_skins() {
	return scrCustomParam("unlock_chars", false) || save_get_value("achievement", Achievement.ULTRA_MUTANT)
}
