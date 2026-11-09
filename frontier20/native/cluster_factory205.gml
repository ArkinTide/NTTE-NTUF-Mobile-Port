// Native loop clusters instantiate an object's class. Frontier shares that
// class between unrelated source enemies, so it must retain the authored
// constructor as well. Capture only constructor inputs, never combat state.
function scrFRClusterInputCopy(_value) {
    if(is_method(_value)) return _value;
    if(is_array(_value)) {
        var _copy=array_create(array_length(_value));
        for(var _i=0;_i<array_length(_value);++_i) _copy[_i]=scrFRClusterInputCopy(_value[_i]);
        return _copy;
    }
    if(is_struct(_value)) {
        var _copy={},_keys=variable_struct_get_names(_value);
        for(var _i=0;_i<array_length(_keys);++_i) {
            var _key=_keys[_i];_copy[$ _key]=scrFRClusterInputCopy(_value[$ _key]);
        }
        return _copy;
    }
    return _value;
}

function scrFRClusterEnemyCreate(_x,_y,_factory,_args) {
    var _actor=scrFRInstanceCreate(_x,_y,FRCustomEnemy);
    if(instance_exists(_actor)) {
        _actor.fr_cluster_factory=_factory;
        _actor.fr_cluster_args=scrFRClusterInputCopy(_args);
        _actor.fr_cluster_offset=[_x-_args[0],_y-_args[1]];
    }
    return _actor;
}

function scrFRClusterCreate(_x,_y,_source) {
    if(!instance_exists(_source)) return noone;
    var _factory=_source[$ "fr_cluster_factory"]??undefined,
        _inputs=_source[$ "fr_cluster_args"]??undefined,
        _offset=_source[$ "fr_cluster_offset"]??[0,0];
    // A raw shell deliberately created by a diagnostic or old integration
    // has no authored species to construct. Never add another blank enemy.
    if(is_undefined(_factory) || !is_array(_inputs) || array_length(_inputs)<2)
        return noone;
    var _args=scrFRClusterInputCopy(_inputs);
    _args[0]=_x-_offset[0];_args[1]=_y-_offset[1];
    if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest)) {
        var _test=scrFRPirateVisibility205State();
        if(is_struct(_test)) {_test.cluster_x=_x;_test.cluster_y=_y;}
    }
    var _actor=scrFRInvokeHere(_factory,_args);
    if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))
        scrFRPirateVisibility205ClusterCreated(_source,_actor);
    return _actor;
}
