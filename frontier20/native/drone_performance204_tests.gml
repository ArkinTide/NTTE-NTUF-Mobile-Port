// Dense interception acceptance uses the actual registered Hyperion factories,
// its original translated reference branch and real native collision events.
// Hostile shots are never reduced to obtain a performance result.
function scrFRDronePerformance204Factory(_x,_y,_shock) {
    var _p=instance_find(Player,0),_pet=instance_create(_x-80,_y,FRCustomHitme);
    _pet.name="NTTEPet";_pet.leader=_p;_pet.team=team_player;_pet.hp=100;
    var _drone=scrFRModCall("skill","AugmentCompassion","CompassionDrone_create",_x,_y,_pet);
    _drone.dist=80;_drone.angle=0;_drone.orbitSpeed=0;_drone.shockCooldown=9999;
    if(!_shock) return _drone;
    var _result;
    with(_drone) _result=scrFRModCall("skill","AugmentCompassion","DroneShock_create",x,y,1);
    _result.image_xscale=1;_result.image_yscale=1;_result.image_alpha=1;
    return _result;
}

function scrFRDronePerformance204QueryOracle(_x,_y) {
    return fr_dependencies_libGeneral_mod_gml_instance_nearest_array(_x,_y,scrFRHyperionEnemyProjectiles());
}

function scrFRDronePerformance204DestroyWitness() {
    global.fr_drone204_destroy_witness.calls+=1;
    global.fr_drone204_destroy_witness.source=real(id);
}

function scrFRDronePerformance204DestroyChecks(_reference,_rate,_shock) {
    var _rows=[];
    for(var _variant=0;_variant<3;++_variant) {
        var _before=scrNTTEFullInstances(all),_blocker=noone;
        global.fr_drone204_reference=_reference;global.fr_drone204_batch=undefined;
        global.fr_drone204_destroy_witness={calls:0,source:noone};
        try {
            _blocker=scrFRDronePerformance204Factory(217000,217000,_shock);
            var _shot=instance_create(_blocker.x,_blocker.y,_variant<2?Grenade:FRCustomProjectile),
                _shot_id=real(_shot),_explosions=instance_number(Explosion),
                _expected_explosions=_variant==0?1:(_variant==1?3:0);
            _shot.team=team_enemy;_shot.typ=1;_shot.speed=0;
            _shot.creator=instance_find(Player,0);
            if(_variant<2) _shot.sticky=(_variant==1);
            else _shot.on_destroy=scrFRDronePerformance204DestroyWitness;
            with(_shot) with(_blocker) event_perform(ev_collision,projectile);
            assert(!instance_exists(_shot),"Hyperion204 Destroy acceptance did not intercept the hostile shot");
            assert(instance_number(Explosion)-_explosions==_expected_explosions,
                "Hyperion204 suppressed or duplicated Grenade/sticky native Destroy explosions");
            var _witness=global.fr_drone204_destroy_witness;
            assert(_witness.calls==(_variant==2?1:0)
                && (_variant!=2 || _witness.source==_shot_id),
                "Hyperion204 bypassed or duplicated the source projectile on_destroy callback");
            array_push(_rows,{reference:_reference,rate:_rate,shock:_shock,
                projectile:_variant==0?"Grenade":(_variant==1?"StickyGrenade":"FRCustomProjectile"),
                native_explosions:instance_number(Explosion)-_explosions,
                source_destroy_calls:_witness.calls,source_destroy_id_matches:_variant!=2 || _witness.source==_shot_id});
        } finally {scrNTTEFullMergedRuntimeTestCleanup(_before);global.fr_drone204_reference=false;}
    }
    return _rows;
}

function scrFRDronePerformance204Bench(_reference,_rate,_shock) {
    var _before=scrNTTEFullInstances(all),_p=instance_find(Player,0),_shots=[],
        _count=512,_hostile=0,_native_next=[],_source_next=[],_query_checks=0,
        _result=undefined;
    global.fr_drone204_reference=_reference;
    global.fr_drone204_batch=undefined;
    random_set_seed(204617);scrFRSourceRandomSetSeed(204617);
    try {
        var _blocker=scrFRDronePerformance204Factory(213000,213000,_shock),
            _missing_typ=instance_create(212900,213040,projectile);
        _missing_typ.team=team_enemy;
        assert(!variable_instance_exists(_missing_typ,"typ") && !scrFRHyperionEnemyProjectile(_missing_typ),
            "Hyperion204 missing-typ fixture no longer models the abstract native projectile constructor");
        // Seed the SAME interleaved candidate list in both modes. Exact
        // nearest identity must survive live reflection and destruction.
        for(var _i=0;_i<_count;++_i) {
            var _shot=instance_create(213000+(_i mod 23)-11,213000+(_i mod 17)-8,FRCustomProjectile),
                _variant=_i mod 8;
            _shot.team=_variant<4?team_enemy:(_variant==4?team_popo:(_variant==5?team_none:team_player));
            _shot.typ=_variant==7?0:1;_shot.speed=0;_shot.creator=_p;
            array_push(_shots,_shot);
            if(scrFRHyperionEnemyProjectile(_shot)) _hostile+=1;
        }
        // Negative typ values are excluded by the same established >0
        // collision predicate; the old source's generic !=0 query is not
        // accidentally reintroduced by the optimized nearest scan.
        _shots[7].typ=-1;
        for(var _probe=0;_probe<12;++_probe) {
            var _x=212900+_probe*17,_y=213040-_probe*9;
            assert(scrFRDroneNearestHostile204(_x,_y)==scrFRDronePerformance204QueryOracle(_x,_y),
                "Hyperion204 fresh nearest differs from original candidate order/centre distance");
            _query_checks+=1;
        }
        _shots[0].team=team_player;_shots[6].team=team_enemy;
        for(var _probe=0;_probe<4;++_probe) {
            assert(scrFRDroneNearestHostile204(213000+_probe,213000)==scrFRDronePerformance204QueryOracle(213000+_probe,213000),
                "Hyperion204 nearest cached stale projectile reflection");
            _query_checks+=1;
        }
        var _query_start=get_timer();
        for(var _probe=0;_probe<96;++_probe) {
            if(_reference) scrFRDronePerformance204QueryOracle(213000+(_probe mod 9),213000);
            else scrFRDroneNearestHostile204(213000+(_probe mod 9),213000);
        }
        var _query_us=get_timer()-_query_start,_null_before=scrFRHyperionProjectileTestsNullFX(),
            _callbacks_start=get_timer(),_intercepted=0,_passed=0;
        for(var _i=0;_i<array_length(_shots);++_i) {
            var _shot=_shots[_i],_expected=scrFRHyperionEnemyProjectile(_shot),
                _state=[_shot.x,_shot.y,_shot.team,_shot.creator,_shot.typ,_shot.speed,_shot.direction];
            with(_shot) with(_blocker) event_perform(ev_collision,projectile);
            assert(instance_exists(_shot)!=_expected,"Hyperion204 dense collision removed the wrong allegiance");
            if(_expected) _intercepted+=1;
            else {
                _passed+=1;
                assert(json_stringify(_state)==json_stringify([_shot.x,_shot.y,_shot.team,_shot.creator,_shot.typ,_shot.speed,_shot.direction]),
                    "Hyperion204 dense collision changed an allied/neutral/typ0 projectile");
            }
        }
        var _callbacks_us=get_timer()-_callbacks_start,_effects=scrFRHyperionProjectileTestsNullFX()-_null_before;
        for(var _i=0;_i<5;++_i) {array_push(_native_next,random(1));array_push(_source_next,scrFRSourceRandom(1));}
        assert(_intercepted==_hostile && _passed==_count-_hostile,"Hyperion204 dense collision lost a shot");
        assert(_reference?_effects==_hostile:(_effects>=4 && _effects<=8),
            "Hyperion204 cosmetic budget altered sparse/dense feedback outside its bounds");
        _result={rate:_rate,shock:_shock,reference:_reference,projectiles:_count,
            hostile_intercepted:_intercepted,allied_neutral_typ0_passed:_passed,
            query_checks:_query_checks,query_iterations:96,query_us:_query_us,missing_typ_ignored:true,
            callback_us:_callbacks_us,null_effects:_effects,native_rng_next:_native_next,
            source_rng_next:_source_next,sound_requests:_reference?_hostile:global.fr_drone204_batch.sounds};
    } finally {scrNTTEFullMergedRuntimeTestCleanup(_before);global.fr_drone204_reference=false;}
    return _result;
}

function scrFRDronePerformance204TestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Hyperion204 acceptance requires a settled isolated native runner");
    var _s={before:scrNTTEFullInstances(all),seed:random_get_seed(),rng:scrNTTEFullArrayCopy(global.rng_state),
        source_seed:scrFRSourceRandomGetSeed(),rate:UberCont.opt_framerate,rows:[],moving:[],destroy_callbacks:[],
        round:-1,elapsed:0,shots:[],blockers:[],rates:[30,60],reference:false};
    _driver.fr_drone_performance204=_s;
    // Preserve the pre-existing friendly/enemy/grenade/laser acceptance too.
    scrFRHyperionProjectileTestsCollisionMatrix();
    for(var _r=0;_r<2;++_r) {
        save_set_value("options","framerate",_s.rates[_r]);scrOptionsUpdate();scrNTTEFullRateApply();
        for(var _shock=0;_shock<2;++_shock) {
            var _reference_destruction=scrFRDronePerformance204DestroyChecks(true,_s.rates[_r],_shock!=0),
                _optimized_destruction=scrFRDronePerformance204DestroyChecks(false,_s.rates[_r],_shock!=0);
            for(var _i=0;_i<3;++_i) {
                array_push(_s.destroy_callbacks,_reference_destruction[_i]);
                array_push(_s.destroy_callbacks,_optimized_destruction[_i]);
            }
            var _old=scrFRDronePerformance204Bench(true,_s.rates[_r],_shock!=0),
                _new=scrFRDronePerformance204Bench(false,_s.rates[_r],_shock!=0);
            assert(json_stringify(_old.native_rng_next)==json_stringify(_new.native_rng_next)
                && json_stringify(_old.source_rng_next)==json_stringify(_new.source_rng_next),
                "Hyperion204 cosmetic coalescing changed native/source seeded random draw sequence");
            array_push(_s.rows,{reference:_old,optimized:_new,
                query_ratio:_new.query_us/max(1,_old.query_us),
                callback_ratio:_new.callback_us/max(1,_old.callback_us)});
        }
    }
    scrFRDronePerformance204TestsNext(_driver);
}

function scrFRDronePerformance204TestsNext(_driver) {
    var _s=_driver.fr_drone_performance204;
    scrNTTEFullMergedRuntimeTestCleanup(_s.before);
    _s.round+=1;
    if(_s.round>=4) return;
    var _rate=_s.rates[floor(_s.round/2)];_s.reference=(_s.round mod 2)==0;
    global.fr_drone204_reference=_s.reference;global.fr_drone204_batch=undefined;
    save_set_value("options","framerate",_rate);scrOptionsUpdate();scrNTTEFullRateApply();
    random_set_seed(204991);scrFRSourceRandomSetSeed(204991);
    _s.elapsed=0;_s.host_frames=0;_s.shots=[];_s.blockers=[];
    for(var _lane=0;_lane<2;++_lane) {
        var _x=215000,_y=215000+_lane*400,
            _blocker=scrFRDronePerformance204Factory(_x,_y,_lane==1);
        array_push(_s.blockers,_blocker);
        for(var _i=0;_i<256;++_i) {
            var _shot=instance_create(_x-80,_y,FRCustomProjectile),_variant=_i mod 4;
            _shot.sprite_index=sprBullet1;_shot.mask_index=mskBullet1;_shot.image_speed=0;
            _shot.team=_variant==0?team_player:(_variant==1?team_enemy:(_variant==2?team_popo:team_none));
            _shot.creator=instance_find(Player,0);_shot.typ=1;_shot.direction=0;_shot.speed=10*timescale;
            var _overlap=false;with(_shot) _overlap=place_meeting(x,y,_blocker);
            assert(!_overlap && _shot.bbox_right<_blocker.bbox_left,
                "Hyperion204 dense moving fixture started inside the actual interceptor mask");
            array_push(_s.shots,{id:_shot,lane:_lane,blocked:_variant==1 || _variant==2});
        }
    }
    _s.start=get_timer();
}

function scrFRDronePerformance204TestsStep(_driver) {
    var _s=_driver.fr_drone_performance204;
    _s.host_frames+=1;_s.elapsed+=timescale;
    if(_s.elapsed<16) return false;
    var _blocked=0,_passed=0;
    for(var _i=0;_i<array_length(_s.shots);++_i) {
        var _entry=_s.shots[_i],_shot=_entry.id,_blocker=_s.blockers[_entry.lane];
        assert(instance_exists(_blocker),"Hyperion204 dense moving acceptance lost its source interceptor");
        assert(instance_exists(_shot)!=_entry.blocked,"Hyperion204 real dense collision changed projectile allegiance");
        if(_entry.blocked) _blocked+=1;
        else {
            _passed+=1;
            assert(_shot.bbox_left>_blocker.bbox_right && (_shot.team==team_player || _shot.team==team_none),
                "Hyperion204 real dense collision obstructed allied or neutral fire");
        }
    }
    array_push(_s.moving,{rate:_s.rates[floor(_s.round/2)],reference:_s.reference,
        host_frames:_s.host_frames,source_ticks:_s.elapsed,projectiles:array_length(_s.shots),
        hostile_intercepted:_blocked,allied_neutral_passed:_passed,elapsed_us:get_timer()-_s.start});
    scrFRDronePerformance204TestsNext(_driver);
    if(_s.round<4) return false;
    global.fr_drone204_reference=false;global.fr_drone204_batch=undefined;
    scrNTTEFullMergedRuntimeTestCleanup(_s.before);
    random_set_seed(_s.seed);global.rng_state=_s.rng;scrFRSourceRandomSetSeed(_s.source_seed);
    save_set_value("options","framerate",_s.rate);scrOptionsUpdate();scrNTTEFullRateApply();
    var _artifact={physical_device_tested:false,production_rules_unchanged:true,
            benchmarks:_s.rows,natural_collision:_s.moving,destroy_callbacks:_s.destroy_callbacks},
        _file=file_text_open_write(working_directory+"frontier-drone-performance204.json");
    file_text_write_string(_file,json_stringify(_artifact));
    file_text_close(_file);
    scrNTTESmokeLog("FRONTIER DRONE204 ACCEPTED "+json_stringify(_artifact));
    scrNTTESmokeLog("PASS NTUF Hyperion dense real native collision at30/60Hz, live nearest parity and both RNG ladders "+json_stringify(_s.rows));
    return true;
}
