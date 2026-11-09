// The saved preference selects a weapon/ability mode switch. Bubbles only
// sprays while the ordinary attack input is held, as Horror's mobile mode.
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
    if(!scrFREnabled() || !instance_exists(_player) || !scrFRRaceIs(_player.race)
        || scrNTTEFullMountedAbilityRaw(_player)) return false;
    var _pinst=scr_playerinstance_find(_player.index);
    return is_struct(_pinst) && scr_player_pref(_pinst,"bubbles")
        && KeyCont.activeforever[_player.index];
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
    if(_active && !_blocked) {
        if(!(_player[$ "fr_bubbles_attack_mode205"]??false))
            scrNTTEFullChargeInputCancel(_player);
        KeyCont.hold_fire[_index]=false;
        KeyCont.press_fire[_index]=false;
        KeyCont.release_fire[_index]=false;
        // A nonautomatic weapon may have buffered this from the last mode.
        _player.clicked=false;
    }
    _player.fr_bubbles_attack_mode205=_active && !_blocked;
}
