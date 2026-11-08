// Share the native character-preference bitset and ability latch with Parrot.
// Turning this preference off retains the authored hold-to-spray controls.
function scrFRBubblesPreferenceName(_option) {
    var _icon=scrFRRaceNativeSprite("Map",0,sprMapIcon),
        _name=scrNTTEFullIsSimplifiedChinese()?"泡泡技能切换"
            :loc("CharacterPrefOptions:BubblesToggle","BUBBLES ABILITY TOGGLE");
    return "@("+sprite_get_name(_icon)+",0,0,-10) "+_name;
}

function scrFRBubblesInputBlocked() {
    return scrGameIsPaused() || instance_exists(MenuOptions) || instance_exists(LevCont)
        || instance_exists(GameOver) || scrGameIsLockState();
}

function scrFRBubblesTouchBlocked(_player) {
    return scrFREnabled() && instance_exists(_player) && scrFRRaceIs(_player.race)
        && scrFRBubblesInputBlocked();
}

function scrFRBubblesToggleInput(_index) {
    if(!scrFREnabled()) return;
    var _pinst=scr_playerinstance_find(_index),_player=noone;
    with(Player) if(index==_index) {_player=id;break;}
    if(!instance_exists(_player) || !is_struct(_pinst) || !scrFRRaceIs(_player.race)) return;
    if(scrNTTEFullMountedAbilityRaw(_player)) {KeyCont.activeforever[_index]=false;return;}
    if(!scr_player_pref(_pinst,"bubbles")) return;
    var _press=KeyCont.press_spec[_index],_active=KeyCont.activeforever[_index],
        _blocked=scrFRBubblesInputBlocked();
    if(!_blocked && _press) {_active=!_active;KeyCont.activeforever[_index]=_active;}
    KeyCont.hold_spec[_index]=_active;
    KeyCont.press_spec[_index]=_press && _active && !_blocked;
    KeyCont.release_spec[_index]=_press && !_active && !_blocked;
}
