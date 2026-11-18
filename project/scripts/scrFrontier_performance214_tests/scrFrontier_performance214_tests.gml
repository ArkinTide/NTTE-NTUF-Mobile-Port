function scrFRPerformance214MembershipOracle(_target,_type) {
    if(!instance_exists(_target)) return false;
    var _items=scrFRObjectInstances(_type),_number=real(_target.id);
    for(var _i=0;_i<array_length(_items);++_i) if(real(_items[_i])==_number) return true;
    return false;
}

// Exact pre214 scrFRInstanceIs body: keep its selector handling, native custom
// instance_is fallback and failure behavior. Do not call the optimized adapter.
function scrFRPerformance214LegacyIs(_target,_type) {
    if(scrFRObjectSelector(_type) || is_array(_type)) {
        if(!instance_exists(_target)) return false;
        var _items=scrFRObjectInstances(_type),_id=real(_target.id);
        for(var _i=0;_i<array_length(_items);++_i) if(real(_items[_i])==_id) return true;
        return false;
    }
    return instance_is(_target,_type);
}

function scrFRPerformance214CompatibilityCheck(_target,_type,_target_name,_type_name,_context) {
    var _old_ok=false,_new_ok=false,_old_value=undefined,_new_value=undefined;
    try {_old_value=scrFRPerformance214LegacyIs(_target,_type);_old_ok=true;}
    catch(_legacy_error) {_old_ok=false;}
    try {_new_value=scrFRInstanceIs(_target,_type);_new_ok=true;}
    catch(_optimized_error) {_new_ok=false;}
    var _matched=_old_ok==_new_ok;
    if(_old_ok && _new_ok)
        _matched=_matched && typeof(_old_value)==typeof(_new_value) && _old_value==_new_value;
    var _row={context:_context,target:_target_name,selector:_type_name,
        outcome:_old_ok?"return":"throw",optimized_outcome:_new_ok?"return":"throw",matched:_matched};
    if(_old_ok) {_row.value=_old_value;_row.value_type=typeof(_old_value);}
    if(!_matched) scrNTTESmokeLog("FRONTIER214 QUERY COMPATIBILITY MISMATCH "+json_stringify(_row));
    assert(_matched,"Optimized instance_is changed legacy success/failure or return value: "+_context+"/"+_target_name+"/"+_type_name);
    // Error names/messages include implementation-local variables. Only the
    // fact of throwing is part of this compatibility contract.
    return _row;
}

function scrFRPerformance214CompatibilityTests(_base,_slash,_plain,_pickup,_thrown,_custom,_custom_slash,_deleted) {
    var _method=method({compatibility_fixture:214},function(){return 214;}),
        _targets=[
            ["base_ref",_base],["base_numeric",real(_base)],["slash_ref",_slash],
            ["custom_projectile_ref",_custom],["custom_projectile_numeric",real(_custom)],
            ["custom_slash_ref",_custom_slash],["custom_slash_numeric",real(_custom_slash)],
            ["ordinary_object_ref",_plain],["thrown_ref",_thrown],["pickup_ref",_pickup],
            ["selector_projectile",projectile],["selector_custom_projectile",FRCustomProjectile],
            ["selector_slash",Slash],["selector_weapon_pickup",WepPickup],
            ["noone",noone],["self_keyword",self],["other_keyword",other],
            ["self_alias",-1],["other_alias",-2],["all_alias",-3],
            ["deleted_ref",_deleted],["deleted_numeric",real(_deleted)],
            ["invalid_positive",2147483647],["invalid_negative",-30000],
            ["undefined",undefined],["struct_empty",{}],["struct_id",{id:_base}],
            ["array_empty",[]],["array_instances",[_base,_plain]],
            ["string","projectile"],["method",_method],["ptr_null",ptr(0)],
            ["boolean_true",true],["zero_numeric",0]],
        _types=[["projectile",projectile],["custom_projectile",FRCustomProjectile],
            ["thrown_weapon",FR_OBJECT_THROWN_WEP],["ordinary_slash",Slash],
            ["array_union",[projectile,FRCustomProjectile]],
            ["array_duplicate",[projectile,projectile]],["array_empty",[]]],
        _results=[];
    for(var _t=0;_t<array_length(_targets);++_t)
        for(var _s=0;_s<array_length(_types);++_s)
            array_push(_results,scrFRPerformance214CompatibilityCheck(_targets[_t][1],_types[_s][1],
                _targets[_t][0],_types[_s][0],"fixture_scope"));
    // Resolve the actual self/other aliases in a projectile with scope too.
    // The two adapters run synchronously in the identical native context.
    with(_base) {
        var _aliases=[["self_keyword",self],["other_keyword",other],["self_alias",-1],["other_alias",-2]];
        for(var _a=0;_a<array_length(_aliases);++_a)
            for(var _s=0;_s<array_length(_types);++_s)
                array_push(_results,scrFRPerformance214CompatibilityCheck(_aliases[_a][1],_types[_s][1],
                    _aliases[_a][0],_types[_s][0],"projectile_with_scope"));
    }
    assert(array_length(_results)==266,"Instance query compatibility matrix coverage changed");
    scrNTTESmokeLog("PASS NTUF214 exact legacy instance_is differential typed/numeric/object/self/other/array/invalid operands "+string(array_length(_results)));
    return _results;
}

function scrFRPerformance214Tests() {
    var _before=scrNTTEFullInstances(all),_seed=random_get_seed(),_checks=0,_rows=[];
    try {
        var _owner=instance_find(Player,0),_probes=[],_types=[projectile,FRCustomProjectile,FR_OBJECT_THROWN_WEP],
            _base=instance_create(482000,482000,projectile),
            _slash=instance_create(482000,482000,Slash),
            _plain=instance_create(482000,482000,FRCustomObject),
            _pickup=instance_create(482000,482000,WepPickup),
            _thrown=instance_create(482000,482000,WepPickup);
        _thrown.mask_index=mskPlasma;_thrown.creator=_owner;
        _pickup.mask_index=mskWepPickup;_pickup.creator=noone;
        array_push(_probes,_base,_slash,_plain,_pickup,_thrown);
        for(var _i=0;_i<256;++_i) {
            var _shot=instance_create(482000+_i,482000,_i mod 2?FRCustomSlash:FRCustomProjectile);
            _shot.speed=0;array_push(_probes,_shot);
        }
        for(var _phase=0;_phase<4;++_phase) {
            if(_phase==1) _thrown.mask_index=mskWepPickup;
            if(_phase==2) {_thrown.mask_index=mskPlasma;_thrown.creator=noone;}
            if(_phase==3) {_thrown.creator=_owner;instance_destroy(_probes[10],false);}
            for(var _t=0;_t<array_length(_types);++_t) {
                var _type=_types[_t],_expected=array_length(scrFRObjectInstances(_type));
                assert(scrFRInstanceNumber(_type)==_expected && scrFRInstanceExists(_type)==(_expected>0),
                    "Projectile count/existence differed after pickup landing, ownership or destruction");
                _checks+=2;
                for(var _p=0;_p<array_length(_probes);++_p) {
                    assert(scrFRInstanceIs(_probes[_p],_type)==scrFRPerformance214MembershipOracle(_probes[_p],_type),
                        "Projectile native ancestry membership differed from authored family union");
                    _checks++;
                }
                var _start=get_timer(),_old=0;
                repeat(80) _old+=array_length(scrFRObjectInstances(_type));
                var _oracle_us=get_timer()-_start,_new=0;_start=get_timer();
                repeat(80) _new+=scrFRInstanceNumber(_type);
                assert(_new==_old,"Projectile count benchmark changed results");
                array_push(_rows,{phase:_phase,selector:_type,count:_expected,
                    oracle_us:_oracle_us,optimized_us:get_timer()-_start});
            }
        }
        // Arrays continue through the original de-duplicating union path.
        var _array=[projectile,FRCustomProjectile,projectile],_items=scrFRObjectInstances(_array);
        assert(scrFRInstanceNumber(_array)==array_length(_items),"Array selector lost duplicate union behavior");
        var _compatibility=scrFRPerformance214CompatibilityTests(_base,_slash,_plain,_pickup,_thrown,
            _probes[5],_probes[6],_probes[10]);
        var _file=file_text_open_write(working_directory+"ntuf214-performance.json");
        file_text_write_string(_file,json_stringify({checks:_checks,rows:_rows,physical_device_tested:false,
            compatibility_checks:array_length(_compatibility),compatibility:_compatibility,
            compatibility_contract:"legacy-scrFRInstanceIs-without-fast-v1",
            scope:"Fresh projectile family queries; no device FPS claim"}));file_text_close(_file);
        scrNTTESmokeLog("PASS NTUF214 fresh projectile ancestry/count/existence parity with live landing, missing owner and deletion "+string(_checks));
    } finally {scrNTTEFullMergedRuntimeTestCleanup(_before);random_set_seed(_seed);}
}
