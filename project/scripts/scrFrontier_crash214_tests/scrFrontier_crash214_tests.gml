function scrFRCrash214Tests() {
    // Re-run the real prior regression paths for supplied images 3 through 7.
    // These are current execution, not inherited release213 PASS claims.
    scrFRCrash213Tests();
    scrFRCollision212Tests();
    scrFRCrash214MansionTests();
    scrFRCrash214SpiralTests();
    scrNTTESmokeLog("PASS FRONTIER214 all seven screenshot paths: mansion local, finite loading spiral, native stale Slash wall, reset categories, orphan homing target and data-scope creation");
}

function scrFRCrash214MansionTests() {
    assert(!instance_exists(GenCont),"Mansion regression requires a completed native room");
    // Some cold rooms never call a custom FloorSet. Initialize its optional
    // alignment globals before the fixture takes its restoration snapshot.
    scrNTTEFullFloorInit();
    var _before=scrNTTEFullInstances(all),_game=scrNTTEFullAreaGeneratorSnapshot(GameCont),
        _seed=scrFRSourceRandomGetSeed(),_floor=scrNTTEFullInstances(Floor),
        _module=global.fr_module_vars[$ "mod:Frontier_Main"],
        _graph={nodes:[]},_align=[global.ntte_full_floor_aw,global.ntte_full_floor_ah,
            global.ntte_full_floor_ax,global.ntte_full_floor_ay];
    scrNTTEFullAreaSnapshotContainer(_module,_graph);
    var _module_snapshot={instances:[],containers:_graph.nodes};
    for(var _i=0;_i<array_length(_floor);++_i) instance_deactivate_object(_floor[_i]);
    try {
        GameCont.area=scrFRAreaTryResolve(103);GameCont.subarea=1;
        GameCont.loops=1;GameCont.fr_prevLoop=1;GameCont.hard=1;
        GameCont.fr_decryptors=0;
        _module.settingNewIDPD=false;_module.settingBigStrikeChests=false;
        // No oasis callback has run in this function invocation. The mansion
        // branch must use its own local index even with zero valid floor cells.
        _module.levelStart=true;
        with(FRWorld) fr_Frontier_Main_mod_gml_step();
        assert(!_module.levelStart,"Empty mansion floor branch did not finish its room-start hook");
        var _count=array_length(scrFRMatching(FRCustomHitme,"name","fr_GoldExchanger"));
        var _tile=instance_create(894000,894000,Floor);
        _module.levelStart=true;
        with(FRWorld) fr_Frontier_Main_mod_gml_step();
        var _stations=scrFRMatching(FRCustomHitme,"name","fr_GoldExchanger");
        assert(array_length(_stations)==_count+1,
            "Mansion room-start hook failed to spawn exactly one gold exchanger from a valid floor");
        var _station=_stations[array_length(_stations)-1];
        assert(_station.x==894016 && _station.y==894000,
            "Mansion gold exchanger lost its authored floor-relative position");
        with(FRWorld) fr_Frontier_Main_mod_gml_step();
        assert(array_length(scrFRMatching(FRCustomHitme,"name","fr_GoldExchanger"))==_count+1,
            "Mansion room-start hook repeated its gold exchanger on the next source tick");
    } finally {
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        for(var _i=0;_i<array_length(_floor);++_i) instance_activate_object(_floor[_i]);
        scrNTTEFullAreaGeneratorRestore(_module_snapshot);
        scrNTTEFullAreaGeneratorRestore(_game);scrFRSourceRandomSetSeed(_seed);
        scrNTTEFullFloorSetAlign(_align[0],_align[1],_align[2],_align[3]);
    }
    scrNTTESmokeLog("FRONTIER214 MANSION: actual room-start callback with zero/one eligible floor; independent gold index and exactly-once authored factory");
}

function scrFRCrash214SpiralTests() {
    var _before=scrNTTEFullInstances(all),_scale=timescale,_stop=lockstep_stop,_epsilon=math_get_epsilon(),
        _game=scrNTTEFullAreaGeneratorSnapshot(GameCont),_seed=random_get_seed(),
        _parked=[];
    var _types=[SpiralCont,Spiral,SpiralDebris,SpiralStar,NTTEFullSpiralStarfield];
    for(var _t=0;_t<array_length(_types);++_t) {
        var _items=scrNTTEFullInstances(_types[_t]);
        for(var _i=0;_i<array_length(_items);++_i) {
            if(array_get_index(_parked,_items[_i])<0) {
                array_push(_parked,_items[_i]);instance_deactivate_object(_items[_i]);
            }
        }
    }
    try {
        math_set_epsilon(0);
        GameCont.area=area_desert;lockstep_stop=false;
        // Match the old valid recurrence for both ordinary and prototype art.
        // No controller is active, preserving the authored 1.5^dt exit growth.
        var _scales=[1,.5,.25];
        for(var _s=0;_s<array_length(_scales);++_s) {
            var _dt=_scales[_s];global.time_scale=_dt;
            assert(scrFRSpiralDelta214(_dt)==_dt
                && scrFRSpiralWarmCount214(_dt)==round(150/_dt),
                "Supported transition frame rate changed its warm-up duration");
            for(var _proto=0;_proto<=1;++_proto) {
                var _ring=instance_create(0,0,Spiral),_grow=0,_sx=0;
                _ring.image_xscale=0;_ring.image_yscale=0;_ring.grow=0;_ring.lanim=-200;
                _ring.sprite_index=_proto?sprSpiralProto:sprSpiral;
                var _iteration=0,_scale_error=0,_grow_error=0;
                repeat(round(16/_dt)) {
                    _grow+=(.0002+(_proto?.0003:0))*_dt;
                    _sx+=_grow*_dt;
                    _grow+=(.0005*_sx*(_grow+1))*_dt;
                    _grow*=power(1.5,_dt);
                    with(_ring) event_perform(ev_step,ev_step_normal);
                    var _exists=instance_exists(_ring);
                    if(_exists) {
                        _scale_error=max(_scale_error,abs(_ring.image_xscale-_sx));
                        _grow_error=max(_grow_error,abs(_ring.grow-_grow));
                    }
                    // Native image scales use float32; the authored recurrence
                    // here uses doubles.1e-6 covers their finite rounding, while
                    // still detecting a changed growth term or host delta.
                    if(!_exists || abs(_ring.image_xscale-_sx)>=.000001
                       || _ring.image_yscale!=_ring.image_xscale || abs(_ring.grow-_grow)>=.000001)
                        scrNTTESmokeLog("FRONTIER214 SPIRAL TRAJECTORY DIAG "+json_stringify({
                            delta:timescale,requested_delta:_dt,proto:_proto,iteration:_iteration,
                            exists:_exists,controller:instance_exists(SpiralCont),expected_grow:_grow,expected_scale:_sx,
                            grow:_exists?_ring.grow:undefined,sx:_exists?_ring.image_xscale:undefined,
                            sy:_exists?_ring.image_yscale:undefined}));
                    assert(instance_exists(_ring)
                        && abs(_ring.image_xscale-_sx)<.000001
                        && _ring.image_yscale==_ring.image_xscale
                        && abs(_ring.grow-_grow)<.000001,
                        "Ordinary loading spiral lost its authored growth trajectory");
                    _iteration++;
                }
                scrNTTESmokeLog("FRONTIER214 SPIRAL ROUNDING "+json_stringify({delta:_dt,proto:_proto,
                    maximum_scale_error:_scale_error,maximum_grow_error:_grow_error,tolerance:0.000001}));
                instance_destroy(_ring,false);
            }
        }
        // A large custom grow value is safe to assign; image scales are not.
        // The real native Step must retire before it can write infinite bounds.
        var _bad=instance_create(0,0,Spiral);
        _bad.grow=power(10,300);global.time_scale=1;
        with(_bad) event_perform(ev_step,ev_step_normal);
        assert(!instance_exists(_bad),"Corrupt loading-ring grow reached a native image scale assignment");
        var _invalid=[0,-1,power(10,300)];
        for(var _i=0;_i<array_length(_invalid);++_i) {
            var _invalid_dt=_invalid[_i];global.time_scale=_invalid_dt;
            assert(scrFRSpiralWarmCount214(_invalid_dt)==150,
                "Invalid loading time step created an unbounded warm-up");
            // Exercise the actual constructor, including debris/star steps.
            var _controller=instance_create(0,0,SpiralCont);
            assert(instance_exists(_controller) && timescale==_invalid_dt,
                "Visual warm-up failed to restore the host timing value");
            with(Spiral) assert(image_xscale>=0 && image_xscale<=16
                && image_yscale>=0 && image_yscale<=16,
                "Actual loading controller constructor produced invalid native bounds");
            instance_destroy(_controller,false);
            with(Spiral) instance_destroy(id,false);
            with(SpiralDebris) instance_destroy(id,false);
            with(SpiralStar) instance_destroy(id,false);
        }
    } finally {
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        for(var _i=0;_i<array_length(_parked);++_i) instance_activate_object(_parked[_i]);
        global.time_scale=_scale;lockstep_stop=_stop;random_set_seed(_seed);
        scrNTTEFullAreaGeneratorRestore(_game);
        math_set_epsilon(_epsilon);
    }
    scrNTTESmokeLog("FRONTIER214 SPIRAL: exact normal/prototype growth at30/60/120Hz, oversized custom grow and real controller warm-up with invalid host timing");
}
