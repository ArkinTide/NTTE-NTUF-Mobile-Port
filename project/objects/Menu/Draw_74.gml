if instance_exists(DailyList) exit

if !instance_exists(Player) scrDrawGameModeIndication()

// render loadout
event_user(1)

with (CharSelect) {
	if (can && race != Race.Random && !UberCont.ctot_dead[race]) {
	    draw_sprite(sprNew, -1, bbox_right - view_xview, y - view_yview)
	}
	
	if (tooltip) {
		var _str = can
			? loc("Races", race, "Name", scrRaceGetName(race))
			: loc("Races", race, "Unlock", scrRaceGetUnlockDescription(race))
		
		scrDrawTooltip(bbox_center_x - view_xview, bbox_top - view_yview, loc(_str), 0, true)
	}
}

with (GoButton) if (tooltip) {
	scrDrawTooltip(bbox_center_x - view_xview, bbox_top - view_yview, loc("MainMenu:Start", "START RUN"), 0, true)
}

//
if string_length(unlock_hint) {
    // FRONTIER VISUAL205 ACTUAL RICH-TEXT TOOLTIP
    scrFRVisual205UnlockDraw(unlock_hint,unlock_hint_pop);
    unlock_hint_pop = approach(unlock_hint_pop, 0, timescale)
}