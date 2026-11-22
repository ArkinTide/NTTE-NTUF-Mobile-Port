function scrTurnIntoSkeleton() {
    with GameCont {
        level = 1
        rad = 0
        ultrapoints = 0
        patient = -1
        race = other.race
        ds_list_clear(skills)
		
		repeat (4) {
			var _ultra = scr_ultra_get_from_race(Race.Melting)
			
			if (_ultra != -1) {
				scr_ultra_set(Race.Melting, _ultra, false)
			}
		}
    }

    maxspeed = (3) * timescale
    ntte_player_physics_scale=timescale;
    accuracy = 1.5
	
	scrPlayerRaceChange(Race.Skeleton, scr_loadout_race_get_skin(Race.Skeleton))
	
    with (scr_playerinstance_find(index)) race = other.race
	
    // Complete revival before any later event can observe the new body.
    hp = 1
    ntte_skeleton_revive_until = current_frame + 5
    nexthurt = max(nexthurt, ntte_skeleton_revive_until)
    // An input sampled for Melting must not become a Skeleton blood gamble.
    KeyCont.activeforever[index] = false
    KeyCont.press_spec[index] = false
    KeyCont.hold_spec[index] = false
    KeyCont.release_spec[index] = false
    sprite_index = spr_hurt
	image_index = 0
    
	snd_play_hit_big(sndMutant14Turn, 0.2)
    
	scrWeapons()
}

function scrSkeletonRevivalProtected() {
    return race == Race.Skeleton
        && current_frame < (self[$ "ntte_skeleton_revive_until"] ?? -1)
}

// Runs only via the explicit desktop harness, with redirected disposable saves.
function scrSkeletonRevivalTests() {
    var _scope=scrNTTEFullSkinUnlockNaturalBegin("skeleton-revival");
    try {
        var _p=instance_find(Player,0),_slot=_p.index;
        UberCont.custom=false;UberCont.opt_practice=false;UberCont.opt_cheats=false;
        global.cheats=false;global.__debug_immortality=false;
        GameCont.fr_progress210_blocked=false;GameCont.fr_achievements_blocked210=false;
        GameCont.level=7;GameCont.rad=100;GameCont.ultrapoints=1;
        ds_list_add(GameCont.skills,mut_long_arms);
        with(_p) {
            scrPlayerRaceChange(Race.Melting,0);
            hp=0;spirit=false;spirit_index=0;can_die=true;
            visible=true;can_shoot=true;can_spec=true;reload=0;
            wep=wep_revolver;bwep=0;nexthurt=0;
        }
        KeyCont.press_fire[_slot]=false;KeyCont.hold_fire[_slot]=false;
        KeyCont.press_spec[_slot]=true;KeyCont.hold_spec[_slot]=true;
        KeyCont.activeforever[_slot]=true;
        // An interrupted mounted-input mask must be restored before clearing
        // the old body's sampled controls, otherwise cleanup reintroduces them.
        _p.ntte_salamander_input={hold:true,press:true,can:true,pet:noone};
        var _circle=instance_create(_p.x,_p.y,ReviveCircle),_shots=instance_number(projectile);
        with(_p) event_perform(ev_step,ev_step_normal);
        assert(instance_exists(_p) && instance_is(_p,Player) && _p.race==Race.Skeleton
            && _p.hp==1 && _p.max_hp==4,
            "Real Melting death/ReviveCircle did not atomically revive the same body at 1/4 HP");
        assert(GameCont.level==1 && GameCont.rad==0 && GameCont.ultrapoints==0 && ds_list_size(GameCont.skills)==0,
            "Skeleton revival lost its original level/radiation/mutation reset");
        assert(!KeyCont.activeforever[_slot] && !KeyCont.press_spec[_slot]
            && !KeyCont.hold_spec[_slot] && instance_number(projectile)==_shots,
            "Melting input was reinterpreted as a Skeleton gamble or shot in the revival event");
        var _until=_p.ntte_skeleton_revive_until,_begin=current_frame;
        assert(_until-_begin==5,"Revival protection changed authored five logical ticks");
        scrPlayerHeal(_p,2);
        assert(_p.hp==3,"Revival protection prevented healing during grace");
        _p.hp=1;
        var _shot=instance_create(_p.x,_p.y,EnemyBullet1),_blast=instance_create(_p.x,_p.y,Explosion);
        _shot.team=team_enemy;_blast.team=team_enemy;
        while(current_frame<_until) {
            with(_shot) if(scr_can_hit(_p,false)) scr_projectile_hit(_p,1);
            with(_blast) scr_projectile_hit(_p,5,0,0);
            with(_p) scr_hit_self(1,HitId.BloodGamble);
            assert(_p.hp==1,"Bypassed iframe/raw damage killed Skeleton during revival grace");
            current_frame+=timescale;
        }
        scrPlayerHeal(_p,2);
        assert(_p.hp==3,"Revival protection prevented healing");
        with(_shot) scr_projectile_hit(_p,1);
        assert(_p.hp==2,"Skeleton stayed invulnerable after the logical revival deadline");
        with(_p) scr_hit_self(1,HitId.BloodGamble);
        assert(_p.hp==1,"Ordinary Skeleton gambling stopped costing HP after revival");
        instance_destroy(_shot,false);instance_destroy(_blast,false);instance_destroy(_circle,false);
        // Use the actual level-up event to verify the challenge's completion reward.
        UberCont.cgot[Race.Skeleton]=false;
        GameCont.level=9;GameCont.rad=10000;
        with(GameCont) event_perform(ev_step,ev_step_normal);
        assert(GameCont.level==10 && scr_race_is_unlocked(Race.Skeleton),
            "Surviving Skeleton could not complete its real level-Ultra unlock");
        scrNTTESmokeLog("SKELETON REVIVAL: real death/circle/input handoff, same body 1/4HP, five logical ticks vs bullet/explosion/raw hits, expiry and genuine Ultra unlock OK @"+string(30/timescale));
    } finally {
        scrNTTEFullSkinUnlockNaturalEnd(_scope);
    }
}
