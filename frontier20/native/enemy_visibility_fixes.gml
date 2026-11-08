// Crystal copies must own their wall-top suspension. The original NTT
// discovery pass wrapped newly copied wall occupants; native Top controllers
// cannot safely share a target or its eventual landing restoration.
function scrFREnemyCloneTopValue(_value,_source,_copy) {
    if(is_method(_value)) {
        if(method_get_self(_value)==_source) return method(_copy,method_get_index(_value));
        return _value;
    }
    if(is_array(_value)) {
        var _result=array_create(array_length(_value));
        for(var _i=0;_i<array_length(_value);++_i)
            _result[_i]=scrFREnemyCloneTopValue(_value[_i],_source,_copy);
        return _result;
    }
    if(is_struct(_value)) {
        var _result={},_keys=variable_struct_get_names(_value);
        for(var _i=0;_i<array_length(_keys);++_i) {
            var _key=_keys[_i];
            _result[$ _key]=scrFREnemyCloneTopValue(_value[$ _key],_source,_copy);
        }
        return _result;
    }
    return _value;
}

function scrFREnemyCloneOwnTop(_source,_copy) {
    if(!instance_exists(_source) || !instance_exists(_copy)) return noone;
    var _source_top=_source[$ "ntte_full_top_object"]??noone;
    if(!instance_exists(_source_top) || _source_top.object_index!=NTTEFullTopObject
        || _source_top.target!=_source) return noone;
    var _old=_copy[$ "ntte_full_top_object"]??noone;
    if(instance_exists(_old) && _old.target==_copy) return _old;
    // TopObject's original constructor consumes its normal jump random draw;
    // copy only authored suspension fields, never instance/scheduler metadata.
    var _top=instance_create(_source_top.x,_source_top.y-8,NTTEFullTopObject),
        _fields=["spr_shadow","spr_shadow_x","spr_shadow_y","mask_index","mask_x","mask_y",
            "direction","hspeed","vspeed","friction","gravity","gravity_direction",
            "image_xscale","image_yscale","image_angle","image_blend","image_alpha",
            "z","zspeed","zfriction","maxspeed","grav","jump","jump_x","jump_y","jump_time",
            "idle_time","idle_wait","idle_walk","idle_walk_chance","canmove","spawn_dis","spawn_dir",
            "type","wobble","wobble_num","override_mask","unstick","target_save"];
    for(var _i=0;_i<array_length(_fields);++_i) {
        var _key=_fields[_i];
        _top[$ _key]=scrFREnemyCloneTopValue(_source_top[$ _key],_source_top,_top);
    }
    var _dx=_copy.x-_source.x,_dy=_copy.y-_source.y;
    _top.x=_source_top.x+_dx;_top.y=_source_top.y+_dy;
    _top.xprevious=_top.x;_top.yprevious=_top.y;
    _top.jump_x+=_dx;_top.jump_y+=_dy;
    _top.search_x1=_source_top.search_x1+_dx;_top.search_x2=_source_top.search_x2+_dx;
    _top.search_y1=_source_top.search_y1+_dy;_top.search_y2=_source_top.search_y2+_dy;
    _top.target=_copy;_copy.ntte_full_top_object=_top;
    // This is a snapshot of an already running suspension, not TopCreate's
    // first integration. Re-entering EndStep here would advance z twice and
    // reinterpret CrystalClone's initial placement offset as actor motion,
    // rotating direction (and thus hspeed/vspeed) away from the copied path.
    _copy.xprevious=_copy.x;_copy.yprevious=_copy.y;
    return _top;
}

// PalankingToss owns the same temporary mask/depth/canfly lifecycle without
// an actor-side Top reference. A candidate can be thrown after CrystalClone
// captured its grounded list, so its copied body needs an independent Toss.
function scrFREnemyCloneOwnToss(_source,_copy) {
    if(!instance_exists(_source) || !instance_exists(_copy)) return noone;
    var _source_toss=noone;
    with(NTTEFullPalankingToss) {
        if(ntte_toss_cleaned) continue;
        if(creator==_copy) return id;
        if(creator==_source) _source_toss=id;
    }
    if(!instance_exists(_source_toss)) return noone;
    var _toss=instance_create(_source_toss.x,_source_toss.y,NTTEFullPalankingToss),
        _fields=["direction","hspeed","vspeed","friction","gravity","gravity_direction",
            "z","zspeed","zfriction","explo","team","hitid",
            "depth","mask_index","spr_shadow_y"];
    for(var _i=0;_i<array_length(_fields);++_i) {
        var _key=_fields[_i];
        _toss[$ _key]=scrFREnemyCloneTopValue(_source_toss[$ _key],_source_toss,_toss);
    }
    // Preserve the running airborne phase and CrystalClone's placed offset.
    // An immediate EndStep would integrate gravity twice in this source tick.
    _toss.x=_source_toss.x+_copy.x-_source.x;
    _toss.y=_source_toss.y+_copy.y-_source.y;
    _toss.xprevious=_toss.x;_toss.yprevious=_toss.y;
    _toss.creator=_copy;_toss.ntte_toss_cleaned=false;
    _copy.xprevious=_copy.x;_copy.yprevious=_copy.y;
    return _toss;
}

// A native Parrot charm can change a possessed host to the player's team.
// The source only watches host existence, leaving its hostile17HP spirit
// permanently hidden over an allied body that friendly attacks cannot hit.
// End that one invalid ownership relationship through the source lifecycle.
function scrFREnemyPossessionValidateHost() {
    if(!possessing || team==team_player || !instance_exists(possess_target)
        || possess_target.team!=team_player) return false;
    var _host=possess_target;
    if((_host[$ "fr_possessor"]??noone)==id) {
        _host.fr_possessed=false;
        _host.fr_possessor=noone;
        // Keep this allied host out of the source's hostile candidate pool.
        _host.fr_possessable=false;
        // status_apply_set uses max(new,old), so setting an infinite buff via
        // that API cannot expire it. Its normal timer pass removes zero.
        _host.fr_buffVoltergeist_time=0;
    }
    fr_Objects_Frontier_Labs_mod_gml_Voltergeist_end_possession();
    possess_target=noone;
    return true;
}
