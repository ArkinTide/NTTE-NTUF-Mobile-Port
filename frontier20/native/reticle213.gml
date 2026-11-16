// One saved preference owns desktop, gamepad and touch crosshair tint.
function scrFRReticle213Color(_index=global.index) {
    if(!instance_exists(UberCont) || !UberCont.opt_ntte_reticlecolor) return c_white;
    var _owner=scr_playerinstance_find(_index);
    if(!is_struct(_owner)) return c_white;
    if(_owner==my_player && !scrFRVisual205ColorConfigured()) return c_white;
    var _color=_owner.color;
    return is_numeric(_color) && _color>=0 && _color<=16777215?_color:c_white;
}
function scrFRReticle213Options() {
    var _old=option_number;
    scrOptionsMenuCategoryBegin(OptionCategory.Game_Color);
    option_list=options[OptionCategory.Game_Color];
    scrOptionsMenuCreateElement({type:"switch",
        name:scrNTTEUpdateText("MATCH CROSSHAIR COLOR","同时更换准心颜色"),
        key:"visual_ntte_reticlecolor",value:save_get_option("visual","ntte_reticlecolor",true)});
    scrOptionsMenuCategoryEnd();option_number=_old;
}
