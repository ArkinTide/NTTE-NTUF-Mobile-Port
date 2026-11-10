// Read the physical charge record only. Rendering must never initialize a
// weapon, consume ammunition, advance its clock or change a fusion mount.
function scrFRChargeBars210Part(_part,_out) {
    if(!is_struct(_part)) return _out;
    var _physical=_part[$ "ntte_native_state"]??undefined;
    _out=scrFRChargeBars210State(_physical,_out);
    if(scrNTTEFullWeaponHasMerge(_part)==true && !_part.temerge.is_part)
        _out=scrFRChargeBars210Part(scrNTTEFullWeaponMergedPart(_part),_out);
    return _out;
}
function scrFRChargeBars210State(_physical,_out) {
    if(!is_struct(_physical)) return _out;
    var _source=_physical[$ "fr_source_weapon"]??_physical;
    if(!is_struct(_source) || (_source[$ "chrg"]??0)<=0
        || (_source[$ "chrg_num"]??0)<=0 || (_source[$ "chrg_max"]??0)<=0) return _out;
    // A mounted root can be reached through both the physical slot and its
    // fusion model. Preserve distinct components, but draw each record once.
    for(var _i=0;_i<array_length(_out);++_i) if(_out[_i].state==_source) return _out;
    array_push(_out,{state:_source,fraction:clamp(_source.chrg_num/_source.chrg_max,0,1)});
    return _out;
}
function scrFRChargeBars210Collect() {
    var _out=[];
    if(!scrFREnabled()) return _out;
    for(var _slot=0;_slot<(race==Race.Steroids?2:1);++_slot) {
        var _field=_slot==0?"wep":"bwep",_state=self[$ (_slot==0?"ntte_state":"bntte_state")]??undefined,
            _source=self[$ (_slot==0?"fr_source_wep":"fr_source_bwep")]??undefined,
            _weapon=variable_instance_get(id,_field);
        _out=scrFRChargeBars210State(_state,_out);
        _out=scrFRChargeBars210State(_source,_out);
        if(is_struct(_weapon) || scrNTTEFullWeaponIsNative(_weapon))
            _out=scrFRChargeBars210Part(scrNTTEFullWeaponModel(_weapon),_out);
    }
    return _out;
}
function scrFRChargeBars210Draw() {
    var _bars=scrFRChargeBars210Collect(),_color=draw_get_color(),_alpha=draw_get_alpha();
    draw_set_alpha(1);
    for(var _i=0;_i<array_length(_bars);++_i) {
        var _y=y-27-_i*5,_fraction=_bars[_i].fraction;
        draw_set_color(c_black);draw_rectangle(x-9,_y,x+9,_y+3,false);
        draw_set_color(_fraction>=1?c_lime:c_white);
        draw_rectangle(x-8,_y+1,x-8+16*_fraction,_y+2,false);
    }
    draw_set_color(_color);draw_set_alpha(_alpha);
}

// Eligibility belongs to a run, survives Continue, and can only change from
// eligible to ineligible until a new GameCont is created.
function scrFRAchievementsAllowed210() {
    if(!instance_exists(UberCont)) return true;
    var _blocked=UberCont.custom || UberCont.opt_practice || UberCont.opt_console
        || (variable_global_exists("console_active") && global.console_active);
    if(instance_exists(GameCont)) {
        if(_blocked) GameCont.fr_achievements_blocked210=true;
        return !scrNTTEFullValue(GameCont,"fr_achievements_blocked210",false);
    }
    return !_blocked;
}
