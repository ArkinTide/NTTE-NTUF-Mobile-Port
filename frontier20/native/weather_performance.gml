// Aurora's authored one-time marker is still read live on every native
// instance. Avoid allocating filter/union/with snapshots for all marked tiles
// every tick; newly created, changed or reactivated instances remain eligible.
function scrFRWeatherSourceOracle() {
    return os_type==os_windows && scrNTTEFullSmokeEnabled()
        && variable_global_exists("fr_weather_source_oracle") && global.fr_weather_source_oracle;
}
function scrFRAuroraApplySprites() {
    static _types=[Floor,FloorExplo,Wall,Top,TopSmall,Debris,Detail,Bones,prop,TopPot,CarThrow,SnowBotCar];
    for(var _i=0;_i<array_length(_types);++_i) {
        var _type=_types[_i];
        with(_type) {
            if(_type==Wall && object_index==NTTESolidWall) continue;
            if(variable_instance_exists(id,"fr_aurora_check") && !is_undefined(fr_aurora_check)) continue;
            fr_aurora_check=true;
            fr_Frontier_Events_mod_gml_Aurora_sprite_set(scrFRObjectIndex(id));
        }
    }
}
