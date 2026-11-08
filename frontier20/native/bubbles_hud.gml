// Draw the authored charge meter in the same GUI transform as native health.
// NTT's old d3d HUD projection flips vertically in this runner; it must not
// own a second, independent screen-space pass for this one local HUD.
function scrFRBubblesHUD(_player) {
    if(!scrFREnabled() || (!is_struct(_player) && !instance_exists(_player))
        || !scrFRRaceIs(_player.race)) return false;
    var _color=draw_get_color(),_alpha=draw_get_alpha();
    try {
        draw_set_color(c_white);draw_set_alpha(1);
        scrFRModCallArray("mod","Frontier_CharHuds","player_hud",[_player,0,false]);
    } finally {draw_set_color(_color);draw_set_alpha(_alpha);}
    return true;
}
