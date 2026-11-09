// Isolated native Windows regression. Six real source quest-hub routes run
// at actual 30/60 Hz. Probes never create, remove or reschedule a quest portal.
// Withhold the fixture's UNLOCK key for 90 eligible logical ticks after the
// real four-part artifact is held; keep its source combat active for late police.
function scrFRQuestPortal204TestState() {
    if(os_type!=os_windows || !scrNTTEFullSmokeEnabled()) return undefined;
    var _driver=instance_find(FRIntegrationTest,0);
    if(!instance_exists(_driver) || _driver.fr_test_case!="quest-portal204") return undefined;
    return _driver[$ "fr_quest_portal204"]??undefined;
}
function scrFRQuestPortal204NaturalState(_observer) {
    var _s=scrFRQuestPortal204TestState();
    if(is_undefined(_s) || _s.phase!=1 || !instance_exists(_observer)
        || _s.observer!=_observer) return undefined;
    return _s;
}
function scrFRQuestPortal204Write(_state,_status,_reason="") {
    var _artifact={schema:1,status:_status,reason:_reason,physical_device_tested:false,
        actual_native_frames:true,actual_enemy_damage_and_deaths:true,
        ordinary_portals_deleted:false,routes:_state.rows,controls:_state.controls};
    if(!is_undefined(_state.row)) _artifact.active_route=_state.row;
    var _file=file_text_open_write(working_directory+"frontier-quest-portal204.json");
    file_text_write_string(_file,json_stringify(_artifact));file_text_close(_file);
    scrNTTESmokeLog("FR_QUEST_PORTAL204 "+json_stringify(_artifact));
}
function scrFRQuestPortal204Fail(_state,_reason) {
    scrFRQuestPortal204Write(_state,"FAIL",_reason);
    throw _reason;
}
function scrFRQuestPortal204Eligibility() {
    // Keep this independent of the new production owner helper. The baseline
    // must compile unchanged and expose a real erroneous type 1 portal.
    var _prevents=0;
    with(NTTEFullPortalPrevent) if(instance_exists(creator)) _prevents++;
    var _allowed=scrNTTEPortalRecoveryAllowed(),_enemies=scr_check_enemies(),
        _crown=instance_exists(CrownPickup),_statue=instance_exists(VaultStatue),
        _guardian=instance_exists(CrownGuardian),_tut=instance_exists(TutCont),
        _rad=instance_exists(RadMaggotChest),_scrap=instance_exists(BecomeScrapBoss),
        _special=(GameCont.area==area_palace || GameCont.area==area_hq)
            && GameCont.subarea==GameCont.maxsubarea;
    return {recovery_allowed:_allowed,check_enemies:_enemies,
        hearts:instance_number(NTTEFullCrystalHeartBullet),
        CrownPickup:_crown,VaultStatue:_statue,CrownGuardian:_guardian,
        TutCont:_tut,RadMaggotChest:_rad,BecomeScrapBoss:_scrap,
        LevCont:instance_exists(LevCont),GenCont:instance_exists(GenCont),
        Menu:instance_exists(Menu),Cinematic:instance_exists(Cinematic),
        GameOver:instance_exists(GameOver),SitDown:instance_exists(SitDown),
        active_portal_prevents:_prevents,special_final_area:_special,
        player:instance_exists(Player),locked:instance_exists(NTTEFullLockedHugeQuestChest),
        full_portal_blocked:scrNTTEFullPortalBlocked(),
        eligible:_allowed && !_enemies && !_crown && !_statue && !_guardian
            && !_tut && !_rad && !_scrap && !_special && _prevents==0
            && GameCont.area!=area_crib && instance_exists(Player)};
}
function scrFRQuestPortal204ObservePortals(_state) {
    if(!instance_exists(NTTEFullLockedHugeQuestChest)) return;
    with(Portal) if(type==1 || type==2) {
        array_push(_state.row.ordinary_portals,{id:real(id),type:type,frame:current_frame,
            x:x,y:y,phase:_state.observer.phase,eligibility:scrFRQuestPortal204Eligibility()});
        scrFRQuestPortal204Fail(_state,"Ordinary portal interrupted a live Ultimate Quest locked chest");
    }
}
function scrFRQuestPortal204HasHeldArtifact(_observer) {
    return instance_exists(_observer.player)
        && array_length(scrNTTEFullQuestPartList(_observer.player.wep,_observer.player.ntte_state))>=4;
}
function scrFRQuestPortal204NaturalBegin(_observer) {
    var _s=scrFRQuestPortal204NaturalState(_observer);
    if(is_undefined(_s)) return;
    var _r=_s.row;
    _r.frames++;_r.logical_ticks+=timescale;
    if(game_get_speed(gamespeed_fps)!=_r.rate || abs(timescale-30/_r.rate)>0.00001)
        scrFRQuestPortal204Fail(_s,"Quest portal route did not run at its real requested frame rate");
    scrFRQuestPortal204ObservePortals(_s);
    var _e=scrFRQuestPortal204Eligibility();
    if(_e.locked) {
        _r.locked_frames++;
        if(!_e.full_portal_blocked) _r.unblocked_locked_frames++;
        if(_observer.phase==5 && _e.eligible && _e.hearts==0) {
            _r.empty_run+=timescale;_r.eligible_empty_ticks+=timescale;
            _r.eligible_empty_frames++;
            if(is_undefined(_r.eligible_empty_witness)) _r.eligible_empty_witness=_e;
        } else if(_r.empty_run>0) {
            _r.last_empty_run=_r.empty_run;_r.empty_run=0;
        }
        if((_observer.phase==7 || (_observer.phase==6 && scrFRQuestPortal204HasHeldArtifact(_observer)))
            && _e.eligible) {
            _r.final_unlock_wait_ticks+=timescale;
            if(is_undefined(_r.final_unlock_wait_witness)) _r.final_unlock_wait_witness=_e;
        }
    }
}
function scrFRQuestPortal204NaturalEnd(_observer) {
    var _s=scrFRQuestPortal204NaturalState(_observer);
    if(is_undefined(_s)) return;
    var _r=_s.row;
    scrFRQuestPortal204ObservePortals(_s);
    if(_observer.phase>=5) for(var _i=0;_i<3;++_i)
        if(_observer.merges_seen[_i] && !_r.merges[_i]) {
            _r.merges[_i]=true;
            array_push(_r.empty_gaps,{before_merge:_i,
                ticks:max(_r.empty_run,_r.last_empty_run),
                native_deaths_before:array_length(_r.native_deaths),
                hearts_seen:array_length(_observer.hearts_seen),frame:current_frame});
            _r.empty_run=0;_r.last_empty_run=0;
        }
    scrFRQuestPortal204ObserveOwnerRelease(_s,_observer);
}
function scrFRQuestPortal204ObserveOwnerRelease(_state,_observer) {
    var _r=_state.row;
    if(!instance_exists(NTTEFullLockedHugeQuestChest) && _observer.phase>=7
        && instance_exists(NTTEFullHugeQuestChest) && !_r.owner_release_seen) {
        _r.owner_release_seen=true;
        _r.owner_release={locked_exists:false,reward_exists:true,
            full_portal_blocked:scrNTTEFullPortalBlocked(),
            remaining_floor_controllers:instance_number(NTTEFullQuestFloorCont),frame:current_frame};
        if(_r.owner_release.full_portal_blocked)
            scrFRQuestPortal204Fail(_state,"Actual UNLOCK left ordinary exit blocked after the locked owner disappeared");
    }
}
function scrFRQuestPortal204UnlockedProbe() {
    // Exact successful native Unlock boundary: source has created its reward
    // and destroyed the locked owner, before another actor can auto-open it.
    var _s=scrFRQuestPortal204TestState();
    if(is_undefined(_s) || _s.phase!=1 || !instance_exists(_s.observer)) return;
    scrFRQuestPortal204ObserveOwnerRelease(_s,_s.observer);
}
function scrFRQuestPortal204InputAllowed(_observer) {
    var _s=scrFRQuestPortal204NaturalState(_observer);
    if(is_undefined(_s)) return true;
    if(_observer.phase==7 || (_observer.phase==6 && scrFRQuestPortal204HasHeldArtifact(_observer)))
        return _s.row.final_unlock_wait_ticks>=90;
    return true;
}
function scrFRQuestPortal204NaturalBefore(_observer) {
    var _s=scrFRQuestPortal204NaturalState(_observer);
    if(is_undefined(_s)) return false;
    var _r=_s.row;
    if(_observer.phase==6 && scrFRQuestPortal204HasHeldArtifact(_observer)
        && _r.final_unlock_wait_ticks<90) {
        // Keep the source fixture at its actual artifact pickup, outside the
        // chest prompt. The genuine pickup key must not become same-frame
        // UNLOCK input when the fixture next approaches the locked owner.
        _observer.want_pick=false;
        // The HQ Heart submap may still have genuine delayed IDPD reservations
        // after source phase 5 ends. Continue the same native Bullet1 combat
        // rather than leaving real late police alive while waiting to unlock.
        with(_observer) scrNTTEFullQuestHubNaturalShootEnemies();
        _r.final_wait_elapsed+=timescale;
        if(_r.final_wait_elapsed>=_r.final_wait_diagnostic_next) {
            _r.final_wait_diagnostic_next+=30;
            var _chest=instance_find(NTTEFullLockedHugeQuestChest,0),_actors=[],_spawns=[],_prevents=[];
            with(enemy) array_push(_actors,{id:real(id),object:object_get_name(object_index),
                hp:hp,team:team,x:x,y:y,visible:visible,mask:real(mask_index)});
            with(becomenemy) array_push(_spawns,{id:real(id),object:object_get_name(object_index),
                x:x,y:y,team:self[$ "team"]??undefined,canspawn:self[$ "canspawn"]??undefined});
            with(NTTEFullPortalPrevent) array_push(_prevents,{id:real(id),creator:real(creator),
                owner_exists:instance_exists(creator),owner_object:instance_exists(creator)?
                    object_get_name(creator.object_index):undefined});
            _r.final_wait_last={eligibility:scrFRQuestPortal204Eligibility(),
                heldpart_count:array_length(scrNTTEFullQuestPartList(_observer.player.wep,_observer.player.ntte_state)),
                player:{id:real(_observer.player),x:_observer.player.x,y:_observer.player.y},
                chest:instance_exists(_chest)?{id:real(_chest),x:_chest.x,y:_chest.y,
                    is_unlockable:_chest.is_unlockable}:undefined,
                player_chest_distance:instance_exists(_chest)?point_distance(_observer.player.x,
                    _observer.player.y,_chest.x,_chest.y):-1,
                current_frame:current_frame,logical_ticks:_r.logical_ticks,
                wait_elapsed:_r.final_wait_elapsed,eligible_wait_ticks:_r.final_unlock_wait_ticks,
                level_ended:GameCont.is_level_ended,lockstep:lockstep_stop,
                pending_police:scrFRPendingPoliceCount(),enemy_count:array_length(_actors),
                spawn_count:array_length(_spawns),source_combat_shots:_observer.shot_count,
                enemies:_actors,spawns:_spawns,prevents:_prevents};
            array_push(_r.final_wait_diagnostics,_r.final_wait_last);
            scrNTTESmokeLog("FR_QUEST_PORTAL204_WAIT "+json_stringify(_r.final_wait_last));
        }
        if(_r.final_wait_elapsed>=600 && _r.final_unlock_wait_ticks<90)
            scrFRQuestPortal204Fail(_s,"Held-artifact fixture lacked 90 genuinely eligible ticks within its bounded final wait");
        return true;
    }
    if(_observer.phase!=9) return false;
    _r.reward_opened=!instance_exists(_observer.reward);
    if(_observer.draw_frames-_observer.draw_start<8) return false;
    if(!_r.crown_created) {
        assert(!instance_exists(CrownPickup) && !instance_exists(VaultStatue)
            && !instance_exists(CrownObject),"Legal crown-exit fixture has unrelated crown blockers");
        GameCont.crownvisits=0;
        var _crown=instance_create(_observer.depot_x,_observer.depot_y,CrownPickup);
        _r.crown_created=true;_r.crown_id=real(_crown);_r.crown_wait=0;
    }
    if(!_r.legal_crown_portal.native_collision) {
        _r.crown_wait+=timescale;
        if(_r.crown_wait>90) scrFRQuestPortal204Fail(_s,"Genuine CrownPickup contact omitted its legal type 3 exit");
        with(_observer) scrNTTEFullQuestHubNaturalMove(depot_x,depot_y);
        return true;
    }
    return false;
}
function scrFRQuestPortal204NaturalFinish(_observer) {
    var _s=scrFRQuestPortal204NaturalState(_observer);
    if(is_undefined(_s) || _observer.phase!=9 || !_s.row.legal_crown_portal.native_collision) return;
    var _r=_s.row;
    _r.hearts_seen=array_length(_observer.hearts_seen);
    _r.generated_enemies_seen=array_length(_observer.enemies_seen);
    _r.actual_shots=_observer.shot_count;
    _r.heart_gate_intervals=_observer.heart_gate_intervals;
    _r.enemy_gate_intervals=_observer.enemy_gate_intervals;
    // A failed compound acceptance assertion must leave its real counters.
    // IN_PROGRESS cannot satisfy the reviewer or any publication gate.
    scrFRQuestPortal204Write(_s,"IN_PROGRESS","native route reached final acceptance assertions");
    assert(_r.locked_frames>0 && _r.unblocked_locked_frames==0,
        "Locked quest owner was not guarded for its whole live lifecycle");
    assert(array_length(_r.empty_gaps)==3 && _r.hearts_seen==8
        && _r.generated_enemies_seen>0 && _r.actual_shots>0
        && array_length(_r.native_deaths)>0 && _r.heart_gate_intervals>0 && _r.enemy_gate_intervals>0,
        "Quest portal test omitted real source merges, generated combat, native deaths or source gate intervals");
    for(var _i=0;_i<3;++_i) {
        var _gap=_r.empty_gaps[_i];
        assert(_gap.before_merge==_i && _gap.ticks>=30
            && (_i==0 || _gap.native_deaths_before>0),
            "Quest portal acceptance omitted an eligible post-death empty interval before a genuine next merge");
    }
    assert(_r.recovery_eligible_calls>0 && _r.corpse_eligible_attempts>0
        && _r.corpse_rejected_attempts>0 && _r.final_unlock_wait_ticks>=90,
        "Quest portal test did not expose real recovery/corpse alarms or final unlockable waiting");
    assert(_r.owner_release_seen && !_r.owner_release.full_portal_blocked && _r.reward_opened
        && _r.legal_crown_portal.type==3 && array_length(_r.ordinary_portals)==0,
        "Quest completion did not release the owner guard and preserve the genuine crown exit");
    _r.completed=true;array_push(_s.rows,_r);_s.phase=2;
    scrNTTESmokeLog("FR_QUEST_PORTAL204 ROUTE PASS "+json_stringify(_r));
}
function scrFRQuestPortal204RecoveryProbe() {
    var _s=scrFRQuestPortal204TestState();
    if(is_undefined(_s) || _s.phase!=1 || !instance_exists(_s.observer)) return;
    var _e=scrFRQuestPortal204Eligibility();
    if(_e.locked && _e.eligible && _e.hearts==0) _s.row.recovery_eligible_calls++;
}
function scrFRQuestPortal204CorpseProbe(_kind) {
    var _s=scrFRQuestPortal204TestState();
    if(is_undefined(_s)) return;
    var _e=scrFRQuestPortal204Eligibility();
    if(_s.phase==1 && instance_exists(_s.observer)) {
        var _r=_s.row;
        if(_e.locked) array_push(_r.corpse_all_alarms,{kind:_kind,corpse:real(id),frame:current_frame,
            forceportal:forceportal,native_deaths_before:array_length(_r.native_deaths),eligibility:_e});
        if(_e.locked && _e.eligible && _e.hearts==0) {
            if(_kind=="before") _r.corpse_eligible_attempts++;
            if(_kind=="rejected") _r.corpse_rejected_attempts++;
            array_push(_r.corpse_alarms,{kind:_kind,corpse:real(id),frame:current_frame,
                forceportal:forceportal,native_deaths_before:array_length(_r.native_deaths),eligibility:_e});
        }
        scrFRQuestPortal204ObservePortals(_s);
    } else if(_s.phase==3 && _s.control_phase==2) {
        if(_kind=="before") _s.control.corpse_attempts++;
        if(_kind=="passed") _s.control.corpse_passes++;
    }
}
function scrFRQuestPortal204EnemyDeathProbe() {
    var _s=scrFRQuestPortal204TestState();
    if(is_undefined(_s) || hp>0) return;
    var _row={id:real(id),object:object_get_name(object_index),hp:hp,frame:current_frame};
    if(_s.phase==1 && instance_exists(_s.observer)
        && array_get_index(_s.observer.enemies_seen,id)>=0)
        array_push(_s.row.native_deaths,_row);
    else if(_s.phase==3 && _s.control_phase==2 && _s.control.enemy_id==real(id))
        array_push(_s.control.native_deaths,_row);
}
function scrFRQuestPortal204CrownCollisionProbe() {
    var _s=scrFRQuestPortal204TestState();
    if(is_undefined(_s) || _s.phase!=1 || !instance_exists(_s.observer)
        || real(id)!=_s.row.crown_id) return;
    var _portal=noone;
    with(Portal) if(type==3) {_portal=id;break;}
    if(!instance_exists(_portal)) scrFRQuestPortal204Fail(_s,"Actual CrownPickup collision did not create a type 3 portal");
    _s.row.legal_crown_portal={native_collision:true,type:_portal.type,id:real(_portal),frame:current_frame};
}
function scrFRQuestPortal204TestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(Player),
        "Quest portal204 requires the isolated native desktop runner");
    _driver.fr_quest_portal204={phase:0,index:-1,observer:noone,row:undefined,rows:[],controls:[],
        cases:[{route:"QuestHubNatural",stored:false,seed:702643,rate:30},
            {route:"QuestStoredHubNatural",stored:true,seed:41,rate:30},
            {route:"QuestStoredHubAltSeedNatural",stored:true,seed:702643,rate:30},
            {route:"QuestHubNatural",stored:false,seed:702643,rate:60},
            {route:"QuestStoredHubNatural",stored:true,seed:41,rate:60},
            {route:"QuestStoredHubAltSeedNatural",stored:true,seed:702643,rate:60}],
        old_rate:game_get_speed(gamespeed_fps),control_phase:0};
}
function scrFRQuestPortal204Next(_state) {
    if(++_state.index>=array_length(_state.cases)) {
        _state.phase=3;_state.row=undefined;
        _state.control_world=scrNTTEFullWorldEventsNaturalWorldCapture();
        _state.old_directory=game_directory;
        _state.scratch=working_directory+"quest-portal204-controls-"+string(get_timer())+"/";
        directory_create(_state.scratch);game_directory=_state.scratch;
        global.ntte_full_progress={schema:1,unlocks:{},loadouts:{},stats:{}};
        return;
    }
    var _case=_state.cases[_state.index];
    save_set_value("options","framerate",_case.rate);save_set_value("options","autopause",false);
    save_set_value("visual","freezeframes",0);scrOptionsUpdate();
    if(_case.stored) scrNTTEFullQuestStoredHubNaturalTests(_case.seed);
    else scrNTTEFullQuestHubNaturalTests();
    _state.observer=instance_find(NTTEFullQuestHubNaturalTest,0);
    assert(instance_exists(_state.observer),"Actual quest route omitted its source observer");
    GameCont.is_level_ended=false;GameCont.crownvisits=0;
    _state.row={route:_case.route,stored:_case.stored,seed:_case.seed,rate:_case.rate,
        runtime_fps:game_get_speed(gamespeed_fps),logic_scale:timescale,
        observer_id:real(_state.observer),frames:0,logical_ticks:0,locked_frames:0,
        unblocked_locked_frames:0,eligible_empty_ticks:0,eligible_empty_frames:0,
        eligible_empty_witness:undefined,empty_run:0,last_empty_run:0,empty_gaps:[],
        merges:[false,false,false],native_deaths:[],recovery_eligible_calls:0,
        corpse_eligible_attempts:0,corpse_rejected_attempts:0,corpse_alarms:[],corpse_all_alarms:[],
        final_unlock_wait_ticks:0,final_unlock_wait_witness:undefined,
        final_wait_elapsed:0,final_wait_diagnostic_next:30,final_wait_last:undefined,final_wait_diagnostics:[],
        owner_release_seen:false,reward_opened:false,crown_created:false,crown_id:-1,
        legal_crown_portal:{native_collision:false,type:-1},ordinary_portals:[],completed:false};
    _state.phase=1;
    scrNTTESmokeLog("FR_QUEST_PORTAL204 ROUTE BEGIN "+json_stringify(_case));
}
function scrFRQuestPortal204ControlWorld(_state) {
    scrFRWallFixTestsReset(_state.control_world);
    GameCont.area=area_desert;GameCont.subarea=0;GameCont.maxsubarea=3;
    GameCont.popolevel=0;GameCont.is_level_ended=false;GameCont.crownvisits=0;
    with(Player) {
        x=650016;y=650016;xprevious=x;yprevious=y;speed=0;
        hp=100000;max_hp=100000;nexthurt=current_frame+100000;
        can_walk=false;can_aim=false;can_shoot=false;bcan_shoot=false;
        wep=wep_revolver;bwep=wep_none;ntte_state=undefined;bntte_state=undefined;
    }
    for(var _x=-3;_x<=3;++_x) for(var _y=-3;_y<=3;++_y)
        instance_create(650000+32*_x,650000+32*_y,Floor);
}
function scrFRQuestPortal204ControlsStep(_state) {
    if(_state.control_phase==0) {
        var _kinds=["FloorCont-only","CrownPed-only","HugeQuestChest-before-open","ordinary-HeartBullet"];
        for(var _i=0;_i<array_length(_kinds);++_i) {
            scrFRQuestPortal204ControlWorld(_state);
            var _actor=noone;
            switch(_i) {
                case 0:
                    _actor=instance_create(650016,650016,NTTEFullQuestFloorCont);
                    _actor.part_index=0;_actor.target=instance_find(Floor,0);break;
                case 1:_actor=instance_create(650016,650016,CrownPed);break;
                case 2:_actor=instance_create(650048,650016,NTTEFullHugeQuestChest);break;
                case 3:_actor=instance_create(650048,650016,NTTEFullCrystalHeartBullet);break;
            }
            var _blocked=scrNTTEFullPortalBlocked();
            assert(instance_exists(_actor) && !instance_exists(NTTEFullLockedHugeQuestChest)
                && !_blocked,"Unrelated quest-shaped object blocked ordinary level exit");
            array_push(_state.controls,{kind:_kinds[_i],actor:real(_actor),
                live_actor:true,locked_exists:false,full_portal_blocked:_blocked});
        }
        // Genuine contact opening, without manually dispatching collision or
        // deleting the chest. Distinct control worlds are retired only here.
        scrFRQuestPortal204ControlWorld(_state);
        _state.control_chest=instance_create(650016,650016,NTTEFullHugeQuestChest);
        _state.control_wait=0;_state.control_phase=1;return false;
    }
    if(_state.control_phase==1) {
        _state.control_wait+=timescale;
        if(_state.control_wait>90) scrFRQuestPortal204Fail(_state,"Ordinary ultimate chest did not open through genuine player contact");
        if(instance_exists(_state.control_chest)) return false;
        assert(!scrNTTEFullPortalBlocked(),"An opened ordinary ultimate chest left an ownerless exit guard");
        array_push(_state.controls,{kind:"HugeQuestChest-after-open",genuine_contact:true,
            locked_exists:false,full_portal_blocked:false});
        scrFRQuestPortal204ControlWorld(_state);
        var _enemy=instance_create(650048,650016,Bandit);
        _state.control={kind:"normal-combat-release",enemy_id:real(_enemy),native_deaths:[],
            corpse_attempts:0,corpse_passes:0,actual_shots:0,portal_type:-1};
        _state.control_wait=0;_state.control_phase=2;return false;
    }
    _state.control_wait+=timescale;
    if(_state.control_wait>300) scrFRQuestPortal204Fail(_state,"Ordinary post-combat exit was suppressed after quest controls");
    if(_state.control_wait>=5 && instance_exists(_state.control.enemy_id)
        && _state.control.actual_shots==0) {
        var _target=_state.control.enemy_id,_shot=noone;
        with(Player) {_shot=scr_projectile_create(_target.x,_target.y,Bullet1,0,0);break;}
        _shot.damage=100000;_shot.speed=0;_state.control.actual_shots++;
    }
    var _portal=noone;
    with(Portal) if(type==1) {_portal=id;break;}
    if(!instance_exists(_portal)) return false;
    _state.control.portal_type=_portal.type;
    _state.control.full_portal_blocked=scrNTTEFullPortalBlocked();
    assert(array_length(_state.control.native_deaths)==1 && _state.control.actual_shots==1
        && _state.control.corpse_attempts>0 && _state.control.corpse_passes>0
        && !_state.control.full_portal_blocked,"Ordinary combat exit lacked actual damage/death/native corpse creation");
    array_push(_state.controls,_state.control);
    scrNTTEFullWorldEventsNaturalWorldRestore(_state.control_world);
    game_directory=_state.old_directory;
    for(var _suffix=0;_suffix<3;++_suffix) {
        // Isolated scratch JSON is never a user save. Remove all known names.
        var _names=["ntte-full-progress.json","ntte-full-progress.json.bak","ntte-full-progress.json.tmp"];
        var _path=_state.scratch+_names[_suffix];if(file_exists(_path)) file_delete(_path);
    }
    save_set_value("options","framerate",_state.old_rate);scrOptionsUpdate();
    scrFRQuestPortal204Write(_state,"PASS");return true;
}
function scrFRQuestPortal204TestsStep(_driver) {
    var _s=_driver.fr_quest_portal204;
    if(_s.phase==0) {scrFRQuestPortal204Next(_s);return false;}
    if(_s.phase==1) {
        assert(instance_exists(_s.observer),"Actual quest observer vanished before native completion");
        return false;
    }
    if(_s.phase==2) {
        if(instance_exists(_s.observer)) return false;
        scrFRQuestPortal204Next(_s);return false;
    }
    return scrFRQuestPortal204ControlsStep(_s);
}
