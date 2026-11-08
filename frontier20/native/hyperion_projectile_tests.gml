// Isolated native source-factory and real collision-event acceptance. The
// asynchronous half also lets the engine move shots through the real masks.
function scrFRHyperionProjectileTestsNullFX() {
    var _vars=global.fr_module_vars[$ "skill:AugmentCompassion"],
        _sprite=scrFRAreaSourceSprite(_vars.settingGreenAugments?_vars.sprGreenNull:_vars.sprNull),
        _effects=scrNTTEFullInstances(BulletHit),_count=0;
    for(var _i=0;_i<array_length(_effects);++_i)
        if(_effects[_i].sprite_index==_sprite) _count++;
    return _count;
}

function scrFRHyperionProjectileTestsShot(_blocker,_object,_team,_creator,_label,_blocked,_typ=undefined) {
    var _shot=instance_create(_blocker.x,_blocker.y,_object);
    _shot.team=_team;_shot.creator=_creator;_shot.speed=3*timescale;_shot.direction=17;
    if(!is_undefined(_typ)) _shot.typ=_typ;
    var _state=[_shot.x,_shot.y,_shot.speed,_shot.direction,_shot.team,_shot.creator,
        _shot.typ,_shot.alarm[0],_shot.alarm[1]],_fx=scrFRHyperionProjectileTestsNullFX();
    assert(scrFRHyperionEnemyProjectile(_shot)==_blocked,
        "Hyperion hostile classification differs from the current projectile team: "+_label);
    with(_shot) with(_blocker) event_perform(ev_collision,projectile);
    assert(instance_exists(_shot)!=_blocked,"Hyperion source collision removed/preserved the wrong shot: "+_label);
    // Real native projectile.Destroy also creates its ordinary spr_fade
    // BulletHit. Identify the authored Null sprite rather than counting that
    // extra native terminal effect as a duplicate/missing source interception.
    assert(scrFRHyperionProjectileTestsNullFX()==_fx+_blocked,
        "Hyperion collision lost its source intercept effect or created one for an allied shot: "+_label);
    if(!_blocked) {
        var _now=[_shot.x,_shot.y,_shot.speed,_shot.direction,_shot.team,_shot.creator,
            _shot.typ,_shot.alarm[0],_shot.alarm[1]];
        assert(json_stringify(_now)==json_stringify(_state),
            "Hyperion altered friendly/neutral projectile motion, allegiance or explosive timer: "+_label);
        instance_destroy(_shot,false);
    }
}

function scrFRHyperionProjectileTestsCollisionMatrix() {
    var _before=scrNTTEFullInstances(all),_p=instance_find(Player,0),
        _seed=random_get_seed(),_rng=scrNTTEFullArrayCopy(global.rng_state);
    try {
        var _pet=instance_create(184920,184000,FRCustomHitme),
            _ally=instance_create(184000,184800,FRCustomObject),
            _hostile=instance_create(184000,184900,FRCustomObject);
        _pet.name="NTTEPet";_pet.leader=_p;_pet.team=team_player;_pet.hp=100;
        _ally.team=team_player;_hostile.team=team_enemy;
        var _drone=scrFRModCall("skill","AugmentCompassion","CompassionDrone_create",185000,184000,_pet),_shock;
        assert(instance_exists(_drone) && _drone.object_index==FRCustomSlash
            && _drone.name=="fr_compassiondrone" && _drone.owner==_pet
            && _drone.on_projectile==_drone.on_grenade,
            "Hyperion fixture did not use its actual source drone factory and both native collision routes");
        with(_drone) _shock=scrFRModCall("skill","AugmentCompassion","DroneShock_create",x,y,1);
        assert(instance_exists(_shock) && _shock.object_index==FRCustomSlash
            && _shock.creator==_drone && _shock.on_projectile==_shock.on_grenade,
            "Hyperion fixture did not use its actual source shock factory/callback");
        _shock.image_xscale=1;_shock.image_yscale=1;
        var _blockers=[_drone,_shock];
        for(var _i=0;_i<2;++_i) {
            var _blocker=_blockers[_i],_label=_i==0?"drone":"shock";
            scrFRHyperionProjectileTestsShot(_blocker,Bullet1,team_player,_p,_label+" local player",false);
            // Co-op and allied actors use the same native team_player value.
            // Distinct creators must not turn their shared-team shots hostile.
            scrFRHyperionProjectileTestsShot(_blocker,Bullet1,team_player,_ally,_label+" other allied owner",false);
            scrFRHyperionProjectileTestsShot(_blocker,EnemyBullet1,team_player,_hostile,_label+" reflected enemy",false);
            scrFRHyperionProjectileTestsShot(_blocker,FRCustomProjectile,team_player,_p,_label+" source friendly",false,1);
            scrFRHyperionProjectileTestsShot(_blocker,Rocket,team_player,_p,_label+" player rocket",false);
            scrFRHyperionProjectileTestsShot(_blocker,Nuke,team_player,_p,_label+" player nuke",false);
            scrFRHyperionProjectileTestsShot(_blocker,Grenade,team_player,_p,_label+" player grenade",false);
            scrFRHyperionProjectileTestsShot(_blocker,Laser,team_player,_p,_label+" player laser",false);
            scrFRHyperionProjectileTestsShot(_blocker,EnemyLaser,team_enemy,_hostile,_label+" source-excluded laser typ0",false);
            scrFRHyperionProjectileTestsShot(_blocker,Bullet1,team_none,noone,_label+" neutral",false);
            scrFRHyperionProjectileTestsShot(_blocker,EnemyBullet1,team_enemy,_hostile,_label+" enemy",true);
            scrFRHyperionProjectileTestsShot(_blocker,EnemyBullet1,team_popo,_hostile,_label+" IDPD",true);
            scrFRHyperionProjectileTestsShot(_blocker,FRCustomProjectile,team_enemy,_hostile,_label+" source enemy",true,1);
            scrFRHyperionProjectileTestsShot(_blocker,Bullet1,team_enemy,_p,_label+" enemy-reflected player",true);
            scrFRHyperionProjectileTestsShot(_blocker,Grenade,team_enemy,_hostile,_label+" enemy grenade",true);
        }
        var _friendly=instance_create(_drone.x,_drone.y,Bullet1),
            _neutral=instance_create(_drone.x,_drone.y,Bullet1),
            _enemy=instance_create(_drone.x+40,_drone.y,EnemyBullet1),
            _laser=instance_create(_drone.x,_drone.y,EnemyLaser);
        _friendly.team=team_player;_friendly.creator=_hostile;
        _neutral.team=team_none;_enemy.team=team_enemy;_laser.team=team_enemy;
        var _candidates=scrFRHyperionEnemyProjectiles();
        assert(array_contains(_candidates,_enemy) && !array_contains(_candidates,_friendly)
            && !array_contains(_candidates,_neutral) && !array_contains(_candidates,_laser),
            "Hyperion pursuit candidates disagree with the actual collision/typ filter");
        instance_destroy(_enemy,false);
        _drone.dist=0;_drone.orbitSpeed=0;_drone.shockCooldown=0;
        _pet.x=_drone.x;_pet.y=_drone.y;
        var _slashes=instance_number(FRCustomSlash);
        with(_drone) scrFRActorCallback("on_end_step");
        assert(instance_number(FRCustomSlash)==_slashes && _drone.shockCooldown<=0,
            "Hyperion activated a shock solely for friendly, neutral or non-interceptable laser shots");
        _enemy=instance_create(_drone.x+40,_drone.y,EnemyBullet1);_enemy.team=team_enemy;
        with(_drone) scrFRActorCallback("on_end_step");
        assert(instance_number(FRCustomSlash)==_slashes+1 && _drone.shockCooldown>0,
            "Hyperion no longer activates its authored shock for nearby hostile projectiles");
        scrNTTESmokeLog("NTUF HYPERION real source drone/shock: native projectile/grenade callbacks, current-team reflection, player/allied explosives/lasers and hostile pursuit PASS");
    } finally {
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        random_set_seed(_seed);global.rng_state=_rng;
    }
}

function scrFRHyperionProjectileTestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Hyperion tests require the settled isolated native harness");
    scrFRHyperionProjectileTestsCollisionMatrix();
    _driver.fr_hyperion_projectiles={before:scrNTTEFullInstances(all),round:-1,elapsed:0,rows:[],
        rate:UberCont.opt_framerate,seed:random_get_seed(),rng:scrNTTEFullArrayCopy(global.rng_state),
        rates:[30,60],shots:[],blockers:[],starts:[],blocked:[]};
    scrFRHyperionProjectileTestsRound(_driver);
}

function scrFRHyperionProjectileTestsRound(_driver) {
    var _s=_driver.fr_hyperion_projectiles;
    if(++_s.round>=array_length(_s.rates)) return;
    var _rate=_s.rates[_s.round];
    save_set_value("options","framerate",_rate);scrOptionsUpdate();scrNTTEFullRateApply();
    assert(game_get_speed(gamespeed_fps)==_rate,"Hyperion moving fixture did not apply the real native rate");
    _s.elapsed=0;_s.ticks=0;_s.shots=[];_s.blockers=[];_s.starts=[];_s.blocked=[];_s.start_gap_min=1000000;
    var _p=instance_find(Player,0),_hostile=instance_create(186000,188000,FRCustomObject),
        _ally=instance_create(186000,188100,FRCustomObject);
    _hostile.team=team_enemy;_ally.team=team_player;
    for(var _i=0;_i<8;++_i) {
        var _x=186000+_s.round*4000,_y=186000+_i*160,_blocker;
        if(_i<4) {
            var _pet=instance_create(_x-80,_y,FRCustomHitme);
            _pet.name="NTTEPet";_pet.leader=_p;_pet.team=team_player;_pet.hp=100;
            _blocker=scrFRModCall("skill","AugmentCompassion","CompassionDrone_create",_x,_y,_pet);
            _blocker.dist=80;_blocker.angle=0;_blocker.orbitSpeed=0;_blocker.shockCooldown=9999;
        } else {
            var _anchor=instance_create(_x,_y,FRCustomObject);_anchor.team=team_player;
            with(_anchor) _blocker=scrFRModCall("skill","AugmentCompassion","DroneShock_create",x,y,1);
            _blocker.image_xscale=1;_blocker.image_yscale=1;_blocker.image_alpha=1;
        }
        // Both real factories inherit mskSlash, whose off-centre 64x48 mask
        // can extend over 50px after rotation. Start beyond that actual mask,
        // then cross it before the unchanged full-size shock fades at 20
        // source ticks. The source callback and engine collision stay live.
        var _shot=instance_create(_x-80,_y,FRCustomProjectile),_variant=_i mod 4,
            _blocked=_variant==1 || _variant==3;
        _shot.sprite_index=sprBullet1;_shot.mask_index=mskBullet1;_shot.image_speed=0;
        _shot.team=_variant==1?team_enemy:(_variant==3?team_popo:team_player);
        _shot.creator=_variant==0?_ally:_hostile;_shot.typ=1;
        _shot.direction=0;_shot.speed=10*timescale;
        var _overlap=false;with(_shot) _overlap=place_meeting(x,y,_blocker);
        assert(!_overlap && _shot.bbox_right<_blocker.bbox_left,
            "Hyperion moving shot started inside its intercept mask, case="+string(_i));
        _s.start_gap_min=min(_s.start_gap_min,_blocker.bbox_left-_shot.bbox_right);
        array_push(_s.shots,_shot);array_push(_s.blockers,_blocker);
        array_push(_s.starts,[_shot.x,_shot.y]);array_push(_s.blocked,_blocked);
    }
    scrNTTESmokeLog("NTUF HYPERION moving native collision start rate="+string(_rate));
}

function scrFRHyperionProjectileTestsCleanup(_driver) {
    var _s=_driver.fr_hyperion_projectiles;
    scrNTTEFullMergedRuntimeTestCleanup(_s.before);
    random_set_seed(_s.seed);global.rng_state=_s.rng;
    save_set_value("options","framerate",_s.rate);scrOptionsUpdate();scrNTTEFullRateApply();
}

// Call every host frame, before the common source-tick gate in the driver.
function scrFRHyperionProjectileTestsStep(_driver) {
    var _s=_driver.fr_hyperion_projectiles;
    _s.elapsed+=timescale;_s.ticks++;
    if(_s.elapsed<16) return false;
    var _end_gap_min=1000000;
    for(var _i=0;_i<array_length(_s.shots);++_i) {
        var _shot=_s.shots[_i],_blocker=_s.blockers[_i],_blocked=_s.blocked[_i];
        assert(instance_exists(_blocker),"Hyperion moving collision lost its real source interceptor");
        assert(instance_exists(_shot)!=_blocked,
            "Natural native movement/collision did not respect Hyperion allegiance, case="+string(_i));
        if(!_blocked) {
            assert(_shot.x>_blocker.x+12 && _shot.x>_s.starts[_i][0]+48
                && _shot.bbox_left>_blocker.bbox_right
                && _shot.team==team_player && _shot.direction==0,
                "Friendly/reflected source shot did not move unchanged through the actual Hyperion mask");
            _end_gap_min=min(_end_gap_min,_shot.bbox_left-_blocker.bbox_right);
        }
    }
    array_push(_s.rows,{rate:_s.rates[_s.round],host_frames:_s.ticks,source_elapsed:_s.elapsed,
        natural_enemy_intercepts:4,natural_friendly_passes:4,start_gap_min:_s.start_gap_min,
        friendly_end_gap_min:_end_gap_min,shot_source_speed:10});
    scrNTTEFullMergedRuntimeTestCleanup(_s.before);
    scrFRHyperionProjectileTestsRound(_driver);
    if(_s.round<array_length(_s.rates)) return false;
    scrFRHyperionProjectileTestsCleanup(_driver);
    scrNTTESmokeLog("PASS NTUF HYPERION real source factories + native collision matrix + moving projectiles at30/60Hz "+json_stringify(_s.rows));
    return true;
}
