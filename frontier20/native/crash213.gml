// Menu categories are indexed by OptionCategory. Platform-only and optional
// content pages intentionally leave holes, so this is a sparse array rather
// than an array of arrays. Only real setting rows belong to the reset action.
function scrOptionsEraseKeys213(_categories,_settings) {
    var _removed=0;
    if(!is_array(_categories)) return _removed;
    for(var _c=0;_c<array_length(_categories);++_c) {
        var _rows=_categories[_c];
        if(!is_array(_rows)) continue;
        for(var _r=0;_r<array_length(_rows);++_r) {
            var _option=_rows[_r];
            if(!is_struct(_option)) continue;
            var _key=_option[$ "key"];
            if(!is_string(_key)) continue;
            if(_key=="game_tutorial") continue;
            if(ds_map_exists(_settings,_key)) {
                ds_map_delete(_settings,_key);++_removed;
            }
        }
    }
    return _removed;
}
