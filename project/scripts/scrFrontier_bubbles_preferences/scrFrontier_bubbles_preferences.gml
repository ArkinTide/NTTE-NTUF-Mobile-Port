// Share the native character-preference bitset and ability latch with Parrot.
// Turning this preference off retains the authored hold-to-spray controls.
function scrFRBubblesPreferenceName(_option) {
    var _icon=scrFRRaceNativeSprite("Map",0,sprMapIcon),
        _name=scrNTTEFullIsSimplifiedChinese()?"按下技能后同时进行泡泡攻击"
            :loc("CharacterPrefOptions:BubblesSimultaneous","PRESS ABILITY TO ADD BUBBLE ATTACKS");
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
    scrFRBubblesToggle205(_index); // FRONTIER BUBBLES ATTACK MODE205
}
