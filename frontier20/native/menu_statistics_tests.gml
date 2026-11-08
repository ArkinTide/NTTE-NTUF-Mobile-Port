// Isolated private-save fixtures; all page navigation uses the real native
// Frontier menu click callback. The user's live namespace/file is never reset.
function scrFRMenuStatisticsTestSameJSON(_left,_right) {
    // JSON object member order is not data. save_load parses and reserializes
    // the object, so compare every field recursively while retaining array
    // order and the distinction between numbers, booleans and strings.
    if(is_struct(_left) || is_struct(_right)) {
        if(!is_struct(_left) || !is_struct(_right)) return false;
        var _keys=variable_struct_get_names(_left);
        if(array_length(_keys)!=array_length(variable_struct_get_names(_right))) return false;
        for(var _i=0;_i<array_length(_keys);++_i) {
            var _key=_keys[_i];
            if(!variable_struct_exists(_right,_key)
                || !scrFRMenuStatisticsTestSameJSON(_left[$ _key],_right[$ _key])) return false;
        }
        return true;
    }
    if(is_array(_left) || is_array(_right)) {
        if(!is_array(_left) || !is_array(_right) || array_length(_left)!=array_length(_right)) return false;
        for(var _i=0;_i<array_length(_left);++_i)
            if(!scrFRMenuStatisticsTestSameJSON(_left[_i],_right[_i])) return false;
        return true;
    }
    if(is_bool(_left) || is_bool(_right)) return is_bool(_left) && is_bool(_right) && _left==_right;
    if(is_string(_left) || is_string(_right)) return is_string(_left) && is_string(_right) && _left==_right;
    // An integer literal and its parsed JSON number have the same JSON type.
    if(is_numeric(_left) || is_numeric(_right)) return is_numeric(_left) && is_numeric(_right) && _left==_right;
    return is_undefined(_left) && is_undefined(_right);
}

function scrFRMenuStatisticsTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled(),
        "Statistics acceptance requires the isolated desktop runner");
    var _namespace=global.fr_module_vars[$ "mod:libSaves"].saves,
        _had=variable_struct_exists(_namespace,"Frontier"),_original=_namespace[$ "Frontier"],
        _original_json=json_stringify(_original),_actual_path=scrFRPrivateFile("FrontierSave.json"),
        _had_file=file_exists(_actual_path),_actual_bytes=_had_file?scrFRStringLoad("FrontierSave.json"):undefined,
        _language=global.language_current[$ "Init:Id"],_menu=noone,
        _module="__frontier_statistics_fixture_"+string(get_timer()),_paths=[],_names=[],_rows=[];
    var _cases=[
        {name:"cold-new",data:undefined,area:"N/A",meals:"0",unique:"0 / 45",kills:"0"},
        {name:"old-missing-best",data:{meals_eaten:12,bubbles_runs:3,bubbles_best_kills:77,
            pirate_conversions:["FR_Flintlock","FR_Hookpole"],legacy_extra:{keep:"unchanged",total:91}},
            area:"N/A",meals:"12",unique:"2 / 45",kills:"77"},
        {name:"populated-numeric",data:{meals_eaten:31,bubbles_kills:9001,bubbles_time:3661,
            pirate_trades:24,pirate_conversions:["FR_Flintlock","FR_Hookpole","FR_Ballista"],
            bubbles_best_area:[7,4,3],bubbles_best_kills:4096,legacy_extra:{keep:[1,2,3]}},
            area:"7-4 L3",meals:"31",unique:"3 / 45",kills:"4096"},
        {name:"populated-loaded-area",data:{bubbles_best_area:["cove",2,1],bubbles_best_kills:300,
            pirate_conversions:["FR_Hookpole"]},area:"",meals:"0",unique:"1 / 45",kills:"300"},
        {name:"populated-unavailable-area",data:{bubbles_best_area:["missing_optional_area",4,6],
            bubbles_best_kills:500},area:"AREA NOT LOADED L6",meals:"0",unique:"0 / 45",kills:"500"},
        {name:"legacy-partial-record",data:{bubbles_best_area:[3,2],bubbles_best_kills:99,
            pirate_conversions:0,unrelated_unlock:true},area:"N/A",meals:"0",unique:"0 / 45",kills:"99"}
    ];
    try {
        assert(scrFRMenuStatisticsTestSameJSON({a:1,b:[true,"2",{keep:3}]},{b:[true,"2",{keep:3}],a:1})
            && !scrFRMenuStatisticsTestSameJSON({keep:1},{keep:1,extra:0})
            && !scrFRMenuStatisticsTestSameJSON([1,2],[2,1])
            && !scrFRMenuStatisticsTestSameJSON([1],[1,2])
            && !scrFRMenuStatisticsTestSameJSON(true,1)
            && !scrFRMenuStatisticsTestSameJSON("1",1),
            "Statistics JSON comparison omitted a field, reordered an array or coerced a scalar type");
        global.language_current[$ "Init:Id"]="English";
        _menu=instance_create(0,0,MenuOptions);
        for(var _i=0;_i<array_length(_cases);++_i) {
            var _case=_cases[_i],_name=_module+"_"+string(_i),_path=_name+"Save.json";
            array_push(_paths,_path);array_push(_names,_name);
            assert(!scrFRFileExists(_path),"Statistics private-save fixture collided with an existing file");
            if(!is_undefined(_case.data)) scrFRStringSave(json_stringify(_case.data),_path);
            scrFRModCallArray("mod","libSaves","save_load",[_name,{pirate_conversions:[],bubbles_best_area:0}]);
            var _data=_namespace[$ _name],_before=json_stringify(_data),_file_before=scrFRStringLoad(_path);
            _namespace.Frontier=_data;
            with(_menu) {
                scrFRMenuOptionsBuild();
                var _options=options[OptionCategory.Frontier],_button=undefined;
                for(var _j=0;_j<array_length(_options);++_j)
                    if((_options[_j][$ "fr_page"]??"")==scrFROptionPageKey("mod","Frontier_Options","stats"))
                        _button=_options[_j];
                assert(is_struct(_button) && is_method(_button.click),"Statistics menu has no real native click entry");
                method_execute(_button.click,_button);
                var _stats=options[OptionCategory.Frontier_Page],_area=_stats[20].fr_info_value;
                assert(array_length(_stats)==22 && _stats[2].fr_info_value==_case.meals
                    && _stats[10].fr_info_value==_case.unique && _stats[21].fr_info_value==_case.kills,
                    "Statistics lost existing counters or unique trade data for "+_case.name);
                if(_case.name=="populated-loaded-area")
                    assert(_area==scrFRDebugAreaLabel(scrFRAreaResolve("cove"),2)+" L1",
                        "Statistics failed to resolve a saved loaded MOD area");
                else assert(_area==_case.area,"Statistics changed the saved best route for "+_case.name+": "+_area);
                array_push(_rows,{fixture:_case.name,area:_area,meals:_stats[2].fr_info_value,
                    unique:_stats[10].fr_info_value,kills:_stats[21].fr_info_value});
            }
            assert(json_stringify(_data)==_before && scrFRStringLoad(_path)==_file_before,
                "Opening Statistics rewrote counters, unlocks, unknown fields or the saved route for "+_case.name);
            // Test cold JSON reload after opening the page, not only the live
            // object. Historical fields and nonempty arrays must survive.
            scrFRModCallArray("mod","libSaves","save_load",[_name,{pirate_conversions:[],bubbles_best_area:0}]);
            var _reloaded=_namespace[$ _name];
            assert(scrFRMenuStatisticsTestSameJSON(_data,_reloaded),
                "Statistics private save round-trip changed historical data for "+_case.name
                    +": before="+_before+", after="+json_stringify(_reloaded));
        }
        // Undefined/deleted records must be treated as absent data, never as
        // an instance on which to run array indexing or object existence.
        assert(scrFRMenuBestArea(undefined)=="N/A" && scrFRMenuBestArea(noone)=="N/A"
            && scrFRMenuBestArea(false)=="N/A" && scrFRMenuBestArea([])=="N/A",
            "Statistics absent best-run sentinels still require array storage");
        scrNTTESmokeLog("PASS FRONTIER real Statistics menu click cold/legacy/populated JSON, route sentinel and no save rewrite "+json_stringify(_rows));
    } finally {
        if(_had) _namespace.Frontier=_original;else variable_struct_remove(_namespace,"Frontier");
        for(var _i=0;_i<array_length(_names);++_i) variable_struct_remove(_namespace,_names[_i]);
        for(var _i=0;_i<array_length(_paths);++_i) {
            var _target=scrFRPrivateFile(_paths[_i]);if(file_exists(_target)) file_delete(_target);
        }
        if(instance_exists(_menu)) instance_destroy(_menu,false);
        global.language_current[$ "Init:Id"]=_language;
        assert(json_stringify(_original)==_original_json && file_exists(_actual_path)==_had_file
            && (!_had_file || scrFRStringLoad("FrontierSave.json")==_actual_bytes),
            "Statistics acceptance changed the actual Frontier source save");
    }
}
