#region make menu

scrLetterbox(false, 0)
image_speed = 0

crown = crwn_none
race = Race.Random

char = array_create(Race.NUM_ALL_RACE_TYPES, noone)

scrLoadoutMenuInit()

scrCampfireMenuCreate()

with Campfire {
	scr_camera_set_position(x, y)
	break
}

scrFRContent211BuildSelect();

#endregion

portrait_offsets = array_create(INPUT_MAX_PLAYERS, 0)
textappear = array_create(INPUT_MAX_PLAYERS, 2)
splatindex = 0

loadout_open = false
loadout_crown = crwn_none
loadout_frame = 0
loadout_arrow_pointed = false
loadout_crown_pointed = false
loadout_skin_pointed = false
loadout_weapon_pointed = false

weekly = false

if (scrGameIsCustomMode()) {
	scrMenuPrepareCustomLoadout()
}
else if (scrGameIsWeeklyRun()) {
	scrMenuPrepareWeeklyLoadout()
}

unlock_hint = ""
unlock_hint_pop = 0
tooltip = undefined
tooltip_pop = 0

if !instance_exists(MusCont) {
	instance_create(0, 0, MusCont)
}

with MusCont {
	audio_stop_sound(amb)
	amb = custom_sound_check(amb0)
	snd_play_ambience(amb, true)
}

event_user(0)

menu_hid_offset = 0

if instance_exists(char[race]) {
	with char[race] {
	    view_xview = x - view_width / 2
	    view_yview = y - view_height / 2
	}
	
	scr_camera_set_position(view_xview, view_yview)
}

loadout_wep = 0
loadout_bwep = 0

gpadmode = false
gpadpointed = 0

mousex = gui_w / 2
mousey = gui_h / 2

event_perform(ev_step, ev_step_begin)

if global.custom_seed {
	seed_text = string(global.custom_seed)
}

alarm[10] = 5