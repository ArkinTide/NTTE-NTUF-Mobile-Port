// The ability button toggles additional bubble fire while the ordinary
// attack input continues to drive the equipped weapon. // FRONTIER BUBBLES212
function scrFRBubblesPlayer205(_index) {
    var _player=noone;
    with(Player) if(index==_index) {_player=id;break;}
    return _player;
}

function scrFRBubblesToggle205(_index) {
    if(!scrFREnabled()) return;
    var _player=scrFRBubblesPlayer205(_index),_pinst=scr_playerinstance_find(_index);
    if(!instance_exists(_player) || !is_struct(_pinst) || !scrFRRaceIs(_player.race)) return;
    if(scrNTTEFullMountedAbilityRaw(_player)) {KeyCont.activeforever[_index]=false;return;}
    if(!scr_player_pref(_pinst,"bubbles")) return;
    if(!scrFRBubblesInputBlocked() && KeyCont.press_spec[_index])
        KeyCont.activeforever[_index]=!KeyCont.activeforever[_index];
}

function scrFRBubblesWeaponBlocked205(_player) {
    // Keep the established firing boundary/API without suppressing or
    // invoking the weapon a second time. PlayerFiring remains its sole owner.
    return false; // FRONTIER BUBBLES212 SIMULTANEOUS WEAPON
}

function scrFRBubblesAttackInput205(_index) {
    if(!scrFREnabled()) return;
    var _player=scrFRBubblesPlayer205(_index),_pinst=scr_playerinstance_find(_index);
    if(!instance_exists(_player) || !is_struct(_pinst) || !scrFRRaceIs(_player.race)) return;
    if(scrNTTEFullMountedAbilityRaw(_player)) {
        KeyCont.activeforever[_index]=false;
        _player.fr_bubbles_attack_mode205=false;return;
    }
    if(!scr_player_pref(_pinst,"bubbles")) {
        KeyCont.activeforever[_index]=false;
        _player.fr_bubbles_attack_mode205=false;return;
    }
    var _active=KeyCont.activeforever[_index],_blocked=scrFRBubblesInputBlocked();
    // This runs after every genuine producer, including ButtonActive (which
    // is deliberately the final touch control). No second hardware sample.
    KeyCont.hold_spec[_index]=!_blocked && _active && KeyCont.hold_fire[_index];
    KeyCont.press_spec[_index]=!_blocked && _active && KeyCont.press_fire[_index];
    KeyCont.release_spec[_index]=!_blocked && _active && KeyCont.release_fire[_index];
    // Preserve all physical weapon edges, accumulated charge and the click
    // buffer. The source race consumes the added spec edges in End Step.
    _player.fr_bubbles_attack_mode205=_active && !_blocked; // FRONTIER BUBBLES212
}
