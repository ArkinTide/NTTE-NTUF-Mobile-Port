// Focused native desktop regression: real room colour ownership and source
// weather callbacks, with an independently retained pre-optimization oracle.
function scrFRWeatherFilterCompare(_target,_field,_values,_operation,_label) {
    var _old=scrFRWeatherFilterOracle(_target,_field,_values,_operation),
        _new=scrFRFilter(_target,_field,_values,_operation);
    assert(array_length(_old)==array_length(_new),"Weather fresh filter membership changed: "+_label);
    for(var _i=0;_i<array_length(_old);++_i)
        assert(_old[_i]==_new[_i] && typeof(_old[_i])==typeof(_new[_i]),
            "Weather fresh filter order or numeric instance identity changed: "+_label);
    return array_length(_new);
}
function scrFRWeatherFilterTime(_oracle,_target,_field,_values,_count) {
    var _start=get_timer(),_total=0;
    repeat(_count) {
        var _items=_oracle?scrFRWeatherFilterOracle(_target,_field,_values,0)
            :scrFRFilter(_target,_field,_values,0);
        _total+=array_length(_items);
    }
    return {us:get_timer()-_start,total:_total};
}
function scrFRWeatherPerformanceTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled(),"Weather comparison requires the isolated native harness");
    var _before=scrNTTEFullInstances(all),_color=scrFRWallBackgroundColor(),_area=GameCont.area,
        _seed=random_get_seed(),_parked=noone,_comparisons=0,_rows=[];
    try {
        // A custom actor can carry an unrelated instance field with this
        // spelling. Neither direct nor nested source reads may use that field.
        var _actor=instance_create(186016,186016,FRCustomObject);
        _actor.name="fr_pelagicbottom";_actor.background_color=c_red;
        var _callbacks=[fr_Frontier_Events_mod_gml_Aurora_compatsprite,
            fr_Frontier_Events_mod_gml_MeteorShower_compatsprite,
            fr_Frontier_Events_mod_gml_ScrapyardsNight_compatsprite],
            _colors=[make_color_rgb(77,73,127),make_color_rgb(106,122,175),make_color_rgb(83,85,119)];
        for(var _i=0;_i<array_length(_callbacks);++_i) {
            background_set_colour(_colors[_i]);
            assert(scrFRBackgroundColour()==_colors[_i],"Native room background getter ignored current weather");
            _actor.image_blend=c_white;
            scrFRInvoke(_actor,_callbacks[_i],[]);
            assert(_actor.image_blend==_colors[_i] && _actor.background_color==c_red,
                "Actual weather compatibility callback read actor state instead of native room background");
        }
        scrNTTESmokeLog("PASS NTUF actual Aurora/Meteor/Scrapyards nested actor callbacks use live native background colour");
        // Real native terrain spread over unique cells, plus overlapping
        // families, numeric IDs, missing markers and mutable fields.
        GameCont.area=area_desert;
        var _floors=[],_walls=[],_objects=[];
        for(var _i=0;_i<1200;++_i) {
            var _v=instance_create(190000+(_i mod 60)*32,190000+floor(_i/60)*32,Floor);
            assert(instance_exists(_v),"Weather benchmark terrain overlapped an existing floor");
            _v.sprite_index=scrFRNTTEGet("mod","teassets","spr").FloorCoast;
            if(_i mod 5!=0) _v.fr_coastnight_check=true;
            _v.fr_weather_value=_i mod 3;array_push(_floors,_v);
        }
        for(var _i=0;_i<400;++_i) {
            var _v=instance_create(194000+(_i mod 40)*16,194000+floor(_i/40)*16,Wall);
            _v.fr_weather_value=_i mod 3;
            if(_i mod 5!=0) _v.fr_coastnight_check=true;
            array_push(_walls,_v);
        }
        for(var _i=0;_i<40;++_i) {
            var _v=instance_create(196000+_i*16,196000,FRCustomObject);
            if(_i mod 3!=0) _v.fr_weather_value=_i mod 3;
            _v.name=_i mod 2==0?"weather-match":"weather-other";array_push(_objects,_v);
        }
        var _targets=[Floor,Wall,FRCustomObject,[Floor,Wall,Floor],[FRCustomObject,[Floor,Wall]],[],
            [_floors[0],real(_floors[0]),Floor],all,noone,FR_OBJECT_GAME,FRCustomHitme],
            _values=[[undefined],[true],[false],[noone],[0,2],[]];
        for(var _t=0;_t<array_length(_targets);++_t)
            for(var _v=0;_v<array_length(_values);++_v) for(var _op=0;_op<2;++_op) {
                scrFRWeatherFilterCompare(_targets[_t],"fr_weather_value",_values[_v],_op,
                    string(_t)+"/"+string(_v)+"/"+string(_op));_comparisons++;
            }
        // These queries are also used for projectile creator/ownerid and
        // source on_step callbacks. Retain the old == rules for references,
        // script IDs, bound methods, and shared/distinct array field values.
        var _method=method(_objects[0],scrFRBackgroundColour),
            _other_method=method(_objects[1],scrFRBackgroundColour),
            _array=[1,2],_equal_array=[1,2],_other_array=[1,3];
        _objects[0].fr_weather_ref=_floors[0];
        _objects[1].fr_weather_ref=real(_floors[0]);
        _objects[2].fr_weather_ref=_floors[1];
        _objects[0].fr_weather_code=scrFRBackgroundColour;
        _objects[1].fr_weather_code=_method;
        _objects[2].fr_weather_code=_other_method;
        _objects[0].fr_weather_array=_array;
        _objects[1].fr_weather_array=_equal_array;
        _objects[2].fr_weather_array=_other_array;
        var _edges=[["fr_weather_ref",[_floors[0]]],
            ["fr_weather_ref",[real(_floors[0])]],
            ["fr_weather_ref",[_floors[0],_floors[1]]],
            ["fr_weather_code",[scrFRBackgroundColour]],
            ["fr_weather_code",[_method]],
            ["fr_weather_code",[_other_method]],
            ["fr_weather_code",[method_get_index(_method)]],
            ["fr_weather_array",[_array]],
            ["fr_weather_array",[_equal_array]],
            ["fr_weather_array",[_other_array]]];
        for(var _i=0;_i<array_length(_edges);++_i) for(var _op=0;_op<2;++_op) {
            var _edge=_edges[_i];
            scrFRWeatherFilterCompare(FRCustomObject,_edge[0],_edge[1],_op,
                "reference/code/array "+string(_i)+"/"+string(_op));_comparisons++;
        }
        var _specials=[["object_index",[Floor]],["bbox_right",[190031]],
            ["alarm0",[-1]],["my_health",[1]],["name",["NTTEPet"]],
            ["sprite_index",[scrFRNTTEGet("mod","teassets","spr").FloorCoast]]];
        for(var _i=0;_i<array_length(_specials);++_i) {
            var _s=_specials[_i];
            scrFRWeatherFilterCompare(FRCustomHitme,_s[0],_s[1],0,"native-special/pet "+_s[0]);_comparisons++;
        }
        _parked=_objects[0];instance_deactivate_object(_parked);
        scrFRWeatherFilterCompare(FRCustomObject,"name",["weather-match"],0,"deactivated");_comparisons++;
        instance_activate_object(_parked);_parked=noone;
        scrFRWeatherFilterCompare(FRCustomObject,"name",["weather-match"],0,"reactivated");_comparisons++;
        _objects[0].name="weather-other";
        scrFRWeatherFilterCompare(FRCustomObject,"name",["weather-match"],0,"immediate rename");_comparisons++;
        var _retired=_objects[1];instance_destroy(_retired,false);
        var _replacement=instance_create(196800,196000,FRCustomObject);_replacement.name="weather-match";
        scrFRWeatherFilterCompare(FRCustomObject,"name",["weather-match"],0,"destroy/recreate");_comparisons++;
        // Invoke the exact upstream NTTE coast-night path. First pass must
        // convert ordinary floors, and a late tile must be seen immediately.
        GameCont.area=201;
        var _events=global.fr_module_vars[$ "mod:Frontier_Events"];
        scrFRInvokeHere(fr_Frontier_Events_mod_gml_CoastNight_applysprites,[]);
        assert(_floors[0].fr_coastnight_check && _floors[0].sprite_index==_events.sprFloorCoastNight,
            "Actual NTTE coast night did not apply its source sprite to an unprocessed tile");
        var _late=instance_create(198000,198000,Floor);
        _late.sprite_index=scrFRNTTEGet("mod","teassets","spr").FloorCoast;_late.styleb=false;
        scrFRInvokeHere(fr_Frontier_Events_mod_gml_CoastNight_applysprites,[]);
        assert(_late.fr_coastnight_check && _late.sprite_index==_events.sprFloorCoastNight,
            "Fresh weather query missed a newly constructed NTTE tile");
        var _types=[Floor,FloorExplo,Wall,Debris,Detail,JungleAssassin];
        for(var _round=0;_round<3;++_round) {
            var _old=scrFRWeatherFilterTime(true,_types,"fr_coastnight_check",[undefined],60),
                _new=scrFRWeatherFilterTime(false,_types,"fr_coastnight_check",[undefined],60);
            assert(_old.total==_new.total,"Weather benchmark compared different workloads");
            array_push(_rows,{round:_round,terrain:array_length(_floors)+array_length(_walls)+1,
                queries:60,original_snapshot_us:_old.us,fresh_native_us:_new.us,
                ratio:_new.us/max(1,_old.us),same_result_total:_new.total});
        }
        var _start=get_timer();
        repeat(120) scrFRInvokeHere(fr_Frontier_Events_mod_gml_CoastNight_applysprites,[]);
        var _callback_us=get_timer()-_start;
        assert(_floors[0].sprite_index==_events.sprFloorCoastNight,
            "Repeated real weather callbacks reverted an already converted tile");
        var _evidence={kind:"native Windows weather query/callback comparison",physical_device_tested:false,
            parity_comparisons:_comparisons,rows:_rows,actual_source_callback_calls:120,
            actual_source_callback_us:_callback_us,source_callback_mean_us:_callback_us/120};
        var _file=file_text_open_write(working_directory+"frontier-weather-performance.json");
        file_text_write_string(_file,json_stringify(_evidence));file_text_close(_file);
        scrNTTESmokeLog("PASS NTUF FRESH WEATHER FILTER "+json_stringify(_evidence));
    } finally {
        if(_parked!=noone) instance_activate_object(_parked);
        GameCont.area=_area;background_set_colour(_color);random_set_seed(_seed);
        scrNTTEFullMergedRuntimeTestCleanup(_before);
    }
}


// The original translated source body remains the explicit private oracle.
// Both paths call the same original sprite_set, with the same live markers.
function scrFRAuroraTestsApply(_source) {
    var _source_rng=scrFRSourceRandomGetSeed();
    global.fr_weather_source_oracle=_source;
    try {
        fr_Frontier_Events_mod_gml_Aurora_applysprites();
        assert(scrFRSourceRandomGetSeed()==_source_rng,
            "Aurora sprite traversal unexpectedly consumed the source RNG cursor");
    }
    finally {global.fr_weather_source_oracle=false;}
}
function scrFRAuroraTestsSnapshot(_items) {
    var _rows=[];
    for(var _i=0;_i<array_length(_items);++_i) {
        var _item=_items[_i];
        array_push(_rows,{type:object_get_name(_item.object_index),sprite:_item.sprite_index,
            marker_exists:variable_instance_exists(_item,"fr_aurora_check"),
            marker:variable_instance_exists(_item,"fr_aurora_check")?_item.fr_aurora_check:undefined,
            topspr:_item.topspr,outspr:_item.outspr,spr_idle:_item.spr_idle});
    }
    return _rows;
}
function scrFRAuroraTestsFixture(_source) {
    var _types=[Floor,Floor,FloorExplo,Wall,Top,TopSmall,Debris,Detail,Bones,
        prop,TopPot,CarThrow,SnowBotCar,Car,FRCustomProp,NTTESolidWall],
        _sprites=[sprFloor5,sprFloor5B,sprDefault,sprWall5Bot,sprDefault,sprWall5Trans,
        sprDebris5,sprDetail5,sprIceDecal,sprDefault,sprDefault,sprDefault,sprDefault,
        sprDefault,sprDefault,sprWall5Bot],_items=[],_rows=[];
    try {
        for(var _i=0;_i<array_length(_types);++_i) {
            var _item=instance_create(50000+_i*32,50000,FRCustomObject);
            with(_item) instance_change(_types[_i],false);
            _item.sprite_index=_sprites[_i];_item.styleb=(_i==1);
            _item.topspr=sprDefault;_item.outspr=sprDefault;_item.spr_idle=sprDefault;
            if(_i==9) _item.fr_aurora_check=false;
            if(_i==10) _item.fr_aurora_check=0;
            if(_i==11) _item.fr_aurora_check=true;
            if(_i==12) _item.fr_aurora_check=undefined;
            array_push(_items,_item);
        }
        scrFRAuroraTestsApply(_source);
        array_push(_rows,scrFRAuroraTestsSnapshot(_items));
        assert(_items[0].sprite_index==scrFRAreaSourceSprite(global.fr_module_vars[$ "mod:Frontier_Events"].sprFloor5Night)
            && _items[3].sprite_index==scrFRAreaSourceSprite(global.fr_module_vars[$ "mod:Frontier_Events"].sprWall5BotNight),
            "Aurora oracle/optimized fixture did not exercise real floor and wall sprite changes");
        assert(!_items[9].fr_aurora_check && _items[10].fr_aurora_check==0
            && !variable_instance_exists(_items[15],"fr_aurora_check"),
            "Aurora changed source false/zero markers or packed exterior collision terrain");
        // A new instance after the initial pass must be handled immediately.
        var _new=instance_create(51000,50000,Floor);
        _new.sprite_index=sprFloor5;_new.styleb=false;
        _new.topspr=sprDefault;_new.outspr=sprDefault;_new.spr_idle=sprDefault;
        array_push(_items,_new);
        scrFRAuroraTestsApply(_source);
        assert(_new.fr_aurora_check==true && _new.sprite_index!=sprFloor5,
            "Aurora failed immediate styling of actual newly created native terrain");
        // Explicitly clear a marker on an existing instance; no membership or
        // mutable-field cache may hide it from the next callback.
        _items[0].fr_aurora_check=undefined;_items[0].sprite_index=sprFloor5;
        scrFRAuroraTestsApply(_source);
        assert(_items[0].fr_aurora_check==true && _items[0].sprite_index!=sprFloor5,
            "Aurora cached a mutable existing marker");
        array_push(_rows,scrFRAuroraTestsSnapshot(_items));
        // Changing a non-target object without Create must still be discovered.
        var _changed=instance_create(52000,50000,FRCustomObject);
        with(_changed) instance_change(Floor,false);
        _changed.sprite_index=sprFloor5;_changed.styleb=false;
        _changed.topspr=sprDefault;_changed.outspr=sprDefault;_changed.spr_idle=sprDefault;
        array_push(_items,_changed);
        instance_deactivate_object(_changed);
        scrFRAuroraTestsApply(_source);
        instance_activate_object(_changed);
        assert(!variable_instance_exists(_changed,"fr_aurora_check"),
            "Aurora changed a native deactivated instance");
        scrFRAuroraTestsApply(_source);
        assert(_changed.fr_aurora_check==true && _changed.sprite_index!=sprFloor5,
            "Aurora failed immediate styling after reactivation/instance_change(false)");
        array_push(_rows,scrFRAuroraTestsSnapshot(_items));
    } finally {
        for(var _i=0;_i<array_length(_items);++_i)
            if(instance_exists(_items[_i])) with(_items[_i]) instance_destroy(id,false);
        global.fr_weather_source_oracle=false;
    }
    return _rows;
}
function scrFRAuroraPerformanceTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled(),"Aurora equivalence requires private native test");
    var _source=scrFRAuroraTestsFixture(true),_direct=scrFRAuroraTestsFixture(false);
    assert(json_stringify(_source)==json_stringify(_direct),
        "Aurora direct native traversal differs from its original source sprite/marker results");
    var _rows=[],_codes=[true,false];
    for(var _i=0;_i<2;++_i) {
        scrFRAuroraTestsApply(_codes[_i]);
        var _start=get_timer();repeat(120) scrFRAuroraTestsApply(_codes[_i]);
        array_push(_rows,{source:_codes[_i],calls:120,total_us:get_timer()-_start});
    }
    var _file=file_text_open_write(working_directory+"ntuf-aurora-equivalence.json");
    file_text_write_string(_file,json_stringify({physical_device_tested:false,source_rng_unchanged:true,
        equivalence:_source,timings:_rows}));file_text_close(_file);
    scrNTTESmokeLog("PASS FRONTIER Aurora original source/direct traversal, live markers, create, activation and type changes");
}
