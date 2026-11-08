// NTTE retains numeric save IDs for areas that were named NTT modules.
// Only these two optional source predicates cross that representation boundary.
function scrFRNTTENativeArea(_area) {
    var _id=scrFRAreaTryResolve(_area);
    return is_real(_id) && _id>=201 && _id<=207 && _id==floor(_id) ? _id:-1;
}
function scrFRNTTEAreaPredicate(_area,_callback) {
    if(_callback=="area_underwater") {
        var _id=scrFRNTTENativeArea(_area);
        if(_id==202 || _id==205) return true;
    }
    // None of NTTE's seven source modules declares area_outside. An absent
    // optional callback in a loaded NTT area returns undefined, not an error.
    return undefined;
}
function scrFRSourceCurrentlyOutside(_area) {
    var _native=scrFRAreaTryResolve(_area);
    if(array_contains([1,3,5,0,105,201],_native)) return true;
    if(!scrFRSourceAreaIsString(_area)) return false;
    return scrFRModCall("area",_area,"area_outside")==true;
}

// Cache lexical normalization only. Alias targets and loaded state are read
// live on every dispatch, including aliases edited by a preceding callback.
function scrFRModuleStringKey(_kind,_name) {
    static _cache={},_count=0;
    var _cache_key=_kind+":"+_name,_key=_cache[$ _cache_key];
    var _oracle=os_type==os_windows && scrNTTEFullSmokeEnabled()
        && variable_global_exists("fr_module_key_oracle") && global.fr_module_key_oracle;
    if(is_undefined(_key) || _oracle) {
        _name=string_replace_all(_name,"\\","/");
        if(string_pos(":",_name)>0) _key=_name;
        else {
            var _suffixes=[".mod.gml",".mod.ntgml",".wep.gml",".area.gml",".skill.gml",".race.gml",".skin.gml",".crown.gml"];
            for(var _i=0;_i<array_length(_suffixes);++_i) {
                var _suffix=_suffixes[_i],_at=string_length(_name)-string_length(_suffix)+1;
                if(_at>0 && string_copy(_name,_at,string_length(_suffix))==_suffix) {
                    _name=string_delete(_name,_at,string_length(_suffix));break;
                }
            }
            _key=_kind+":"+_name;
        }
        if(!_oracle) {
            if(_count>=512) {_cache={};_count=0;}
            _cache[$ _cache_key]=_key;_count+=1;
        }
    }
    return global.fr_module_aliases[$ _key]??_key;
}

function scrFRLightringLocalizationInstall() {
    global.ntte_zh_dictionary[$ "LIGHTRING"]="电环";
    global.ntte_zh_dictionary[$ "LIGHTRING LAUNCHER"]="电环发射器";
    global.ntte_zh_dictionary[$ "LIGHTRING CANNON"]="电环加农炮";
}
