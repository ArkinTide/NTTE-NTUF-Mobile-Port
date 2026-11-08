// Real asynchronous maps and ordinary native combat/clearance. The test moves
// its invulnerable player near dormant ambush sources; only actual friendly
// Bullet1 collisions defeat hostiles and attackable BigPipe spawners. Authored
// WallCrates holding hostiles receive an ordinary wall-breaking Explosion.
function scrFRBiomeClearance204MapBulletBefore(_shot,_target) {
    var _driver=instance_find(FRIntegrationTest,0);
    if(!instance_exists(_driver)) return undefined;
    var _s=_driver[$ "fr_biome_clearance204_maps"]??undefined;
    if(is_undefined(_s) || _s.phase==0) return undefined;
    var _requested=_s.shots[$ string(real(_shot))]??undefined;
    if(is_undefined(_requested)) return undefined;
    return {state:_s,bullet:real(_shot),requested:_requested,target:real(_target),
        object:object_get_name(_target.object_index),team:_shot.team,
        hp:_target[$ "hp"]??undefined,damage:_shot.damage,ticks:_s.elapsed,
        x:_shot.x,y:_shot.y};
}
function scrFRBiomeClearance204MapBulletAfter(_record) {
    var _s=_record.state;variable_struct_remove(_record,"state");
    if(_s.phase==0) return;
    _record.after=instance_exists(_record.target)?(_record.target[$ "hp"]??undefined):undefined;
    _record.consumed=!instance_exists(_record.bullet);
    if(_record.consumed || _record.hp!=_record.after) array_push(_s.row.hits,_record);
}
function scrFRBiomeClearance204MapWrite(_s,_passed) {
    var _file=file_text_open_write(working_directory+"frontier-biome-clearance204-maps.json");
    file_text_write_string(_file,json_stringify({passed:_passed,
        physical_device_tested:false,cases:_s.rows}));file_text_close(_file);
}
function scrFRBiomeClearance204MapFail(_s,_reason) {
    _s.row.result="failed";_s.row.reason=_reason;
    _s.row.final=scrFRBiomeClearance204NaturalSample(_s,true);
    _s.phase=0;
    array_push(_s.rows,_s.row);scrFRBiomeClearance204MapWrite(_s,false);
    scrNTTESmokeLog("BIOME CLEARANCE204 MAP FAILED "+json_stringify(_s.row));
    throw _reason;
}
function scrFRBiomeClearance204MapTestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Biome map clearance requires the isolated native runner");
    var _cases=[];
    for(var _loops=0;_loops<=3;_loops+=(_loops==0?1:2)) {
        array_push(_cases,{area:area_desert,subarea:2,loops:_loops,seed:100005,rate:30});
        array_push(_cases,{area:area_desert,subarea:2,loops:_loops,seed:100006,rate:60});
        array_push(_cases,{area:area_jungle,subarea:1,loops:_loops,seed:204071,rate:30});
        array_push(_cases,{area:area_jungle,subarea:1,loops:_loops,seed:204086,rate:60});
    }
    var _s={world:scrNTTEFullWorldEventsNaturalWorldCapture(),cases:_cases,index:-1,
        phase:0,elapsed:0,wait:0,rows:[],seen:{},shots:{}};
    _driver.fr_biome_clearance204_maps=_s;
    // The same strictly read-only creation/lifecycle probes cover both cases.
    _driver.fr_biome_clearance204_natural=_s;
}
function scrFRBiomeClearance204MapNext(_s) {
    scrNTTEFullWorldEventsCleanup();scrFRWallFixTestsReset(_s.world);
    if(++_s.index>=array_length(_s.cases)) {
        scrFRBiomeClearance204MapWrite(_s,true);
        scrNTTEFullWorldEventsNaturalWorldRestore(_s.world);return true;
    }
    var _case=_s.cases[_s.index];
    save_set_value("options","framerate",_case.rate);save_set_value("options","autopause",false);
    save_set_value("visual","freezeframes",0);scrOptionsUpdate();
    scrNTTEFullWorldEventsNaturalWorldConfigure(_s.world,[_case.area,_case.subarea],_case.seed);
    GameCont.loops=_case.loops;GameCont.hard=3+10*_case.loops;
    GameCont.is_level_ended=false;GameCont.popolevel=0;GameCont.killenemies=false;
    global.fr_continue_generation=undefined;global.fr_continue_events=undefined;
    var _skills=[],_baseline=[];
    for(var _i=0;_i<ds_list_size(GameCont.skills);++_i) array_push(_skills,GameCont.skills[|_i]);
    for(var _i=0;_i<array_length(_s.world.before);++_i) array_push(_baseline,real(_s.world.before[_i]));
    _s.row={area:_case.area,subarea:_case.subarea,loops:_case.loops,seed:_case.seed,rate:_case.rate,
        samples:[],births:[],lifecycle:[],hits:[],approaches:[],shot_placements:[],crate_attacks:[],test_bullets:0,
        baseline_ids:_baseline,baseline_skills:_skills};
    _s.seen={};_s.shots={};_s.visits={};_s.crates={};_s.elapsed=0;_s.wait=0;_s.phase=1;
    scrNTTESmokeLog("BIOME CLEARANCE204 MAP BEGIN "+json_stringify(_case));return false;
}
function scrFRBiomeClearance204MapFire(_s) {
    var _targets=scrNTTEFullInstances([enemy,NTTEFullBigPipe]),_player=instance_find(Player,0);
    // GatorAmbush deliberately locks even Mimics inside four breakable Walls.
    // Bullet1 cannot open those authored crates. Use the real Explosion mask
    // and scheduled Collision_Wall/scrWallDestroy path, without moving loot,
    // changing enemy fields, invoking callbacks, or manufacturing an exit.
    var _crates=scrNTTEFullInstances(NTTEFullWallCrate);
    for(var _i=0;_i<array_length(_crates);++_i) {
        var _crate=_crates[_i],_key=string(real(_crate)),_loot=_crate.crate_loot;
        if((_s.crates[$ _key]??false) || !instance_exists(_loot)
            || !instance_is(_loot,enemy) || _loot.team==team_player
            || array_length(_crate.crate_wall)==0) continue;
        var _walls=[];
        for(var _w=0;_w<array_length(_crate.crate_wall);++_w)
            array_push(_walls,real(_crate.crate_wall[_w]));
        var _blast=instance_create(_crate.x,_crate.y,Explosion);
        _blast.creator=_player;_blast.team=team_player;
        _s.crates[$ _key]=true;
        array_push(_s.row.crate_attacks,{ticks:_s.elapsed,crate:real(_crate),
            loot:real(_loot),loot_object:object_get_name(_loot.object_index),
            loot_hp:_loot.hp,loot_enemy:instance_is(_loot,enemy),loot_team:_loot.team,
            walls:_walls,attack:real(_blast),
            object:object_get_name(_blast.object_index),damage:_blast.damage,
            team:_blast.team,creator:real(_blast.creator),
            creator_object:object_get_name(_blast.creator.object_index),x:_blast.x,y:_blast.y,
            mask:real(_blast.mask_index)});
    }
    for(var _i=0;_i<array_length(_targets);++_i) {
        var _actor=_targets[_i];
        if(!instance_exists(_actor) || _actor.hp<=0 || _actor.team==team_player
            || !_actor.visible || _actor.image_alpha<=0 || _actor.mask_index==mskNone
            || instance_is(_actor,Van) || instance_is(_actor,BigDogMissile)) continue;
        var _shot=instance_create(_actor.x,_actor.y,Bullet1);
        _shot.creator=_player;_shot.team=team_player;_shot.speed=0;_shot.damage=_actor.hp+100;
        // A stationary bullet at an actor's origin can overlap a neighbouring
        // Wall before reaching hitme, even when part of the enemy is exposed.
        // Find contact using the real projectile/target masks, never changing
        // either mask or forcing a collision callback.
        var _found=false,_bx=_actor.x,_by=_actor.y,_best=infinity;
        with(_shot) _found=place_meeting(x,y,_actor)
            && !place_meeting(x,y,Wall) && !place_meeting(x,y,InvisiWall);
        if(!_found) {
            var _left=floor(_actor.bbox_left-16),_right=ceil(_actor.bbox_right+16),
                _top=floor(_actor.bbox_top-16),_bottom=ceil(_actor.bbox_bottom+16);
            for(var _y=_top;_y<=_bottom;_y+=2) for(var _x=_left;_x<=_right;_x+=2) {
                var _distance=point_distance(_actor.x,_actor.y,_x,_y),_contact=false;
                if(_distance>=_best) continue;
                with(_shot) _contact=place_meeting(_x,_y,_actor)
                    && !place_meeting(_x,_y,Wall) && !place_meeting(_x,_y,InvisiWall);
                if(_contact) {_found=true;_best=_distance;_bx=_x;_by=_y;}
            }
        }
        var _walls=[];
        if(!_found) {
            var _near=scrNTTEFullRectInstances(_actor.bbox_left-16,_actor.bbox_top-16,
                _actor.bbox_right+16,_actor.bbox_bottom+16,Wall);
            for(var _w=0;_w<array_length(_near);++_w) {
                var _wall=_near[_w];
                array_push(_walls,{id:real(_wall),object:object_get_name(_wall.object_index),
                    x:_wall.x,y:_wall.y,solid:_wall.solid,
                    bbox:[_wall.bbox_left,_wall.bbox_top,_wall.bbox_right,_wall.bbox_bottom]});
            }
        }
        array_push(_s.row.shot_placements,{ticks:_s.elapsed,target:real(_actor),
            object:object_get_name(_actor.object_index),hp:_actor.hp,
            origin:[_actor.x,_actor.y],bbox:[_actor.bbox_left,_actor.bbox_top,
                _actor.bbox_right,_actor.bbox_bottom],mask:real(_actor.mask_index),
            projectile_mask:real(_shot.mask_index),found:_found,point:[_bx,_by],walls:_walls});
        if(!_found) {instance_destroy(_shot,false);continue;}
        _shot.x=_bx;_shot.y=_by;_shot.xprevious=_bx;_shot.yprevious=_by;
        _s.shots[$ string(real(_shot))]=real(_actor);++_s.row.test_bullets;
    }
}
function scrFRBiomeClearance204MapApproach(_s) {
    var _target=noone,_best=infinity,_fewest=infinity,_player=instance_find(Player,0),_seen={},
        _candidates=scrNTTEFullInstances([enemy,NTTEFullWantBigMaggot,MeleeFake,NTTEFullTopObject]);
    for(var _i=0;_i<array_length(_candidates);++_i) {
        var _actor=_candidates[_i];
        if(!instance_exists(_actor)) continue;
        if(_actor.object_index==NTTEFullTopObject) {
            if(!instance_exists(_actor.target) || !instance_is(_actor.target,enemy)) continue;
            _actor=_actor.target;
        }
        if((variable_instance_exists(_actor,"team") && _actor.team==team_player)
            || instance_is(_actor,Van) || instance_is(_actor,BigDogMissile)) continue;
        var _key=string(real(_actor)),_visits=_s.visits[$ _key]??0;
        if(_seen[$ _key]??false) continue;
        _seen[$ _key]=true;
        var _distance=point_distance(_player.x,_player.y,_actor.x,_actor.y);
        if(_visits<_fewest || (_visits==_fewest && _distance<_best)) {
            _fewest=_visits;_best=_distance;_target=_actor;
        }
    }
    if(!instance_exists(_target)) return;
    _s.visits[$ string(real(_target))]=_fewest+1;
    var _floor=scrNTTEFullNearestBBox(_target.x,_target.y,Floor);
    if(!instance_exists(_floor)) return;
    var _x=(_floor.bbox_left+_floor.bbox_right)/2,_y=(_floor.bbox_top+_floor.bbox_bottom)/2,
        _free=false;
    with(_player) _free=!place_meeting(_x,_y,Wall) && !place_meeting(_x,_y,InvisiWall);
    if(!_free) return;
    array_push(_s.row.approaches,{ticks:_s.elapsed,target:real(_target),
        object:object_get_name(_target.object_index),visit:_fewest+1,
        from:[_player.x,_player.y],to:[_x,_y]});
    _player.x=_x;_player.y=_y;_player.xprevious=_x;_player.yprevious=_y;
}
function scrFRBiomeClearance204MapTestsStep(_driver) {
    var _s=_driver.fr_biome_clearance204_maps;
    with(Player) {
        hp=100000;max_hp=100000;nexthurt=current_frame+100000;
        speed=0;can_walk=false;can_aim=false;can_spec=false;can_shoot=false;bcan_shoot=false;
    }
    if(_s.phase==0) return scrFRBiomeClearance204MapNext(_s);
    if(_s.phase==1) {
        if(++_s.wait<3) return false;
        var _gen=instance_create(0,0,GenCont);
        assert(instance_exists(_gen) && !_gen.ntte_full_sync_generation,
            "Biome map clearance replaced genuine asynchronous generation");
        _s.wait=0;_s.phase=2;return false;
    }
    if(_s.phase==2) {
        if(++_s.wait>=3600) scrFRBiomeClearance204MapFail(_s,"Biome map source generation did not settle");
        if(instance_exists(GenCont) || instance_exists(FloorMaker)) return false;
        var _case=_s.cases[_s.index];
        assert(GameCont.area==_case.area && GameCont.subarea==_case.subarea
            && GameCont.loops==_case.loops && instance_number(Floor)>20 && instance_number(enemy)>0,
            "Biome map clearance lost its requested populated source map");
        _s.row.floors=instance_number(Floor);_s.row.initial_enemies=instance_number(enemy);
        _s.row.initial_pipes=instance_number(NTTEFullBigPipe);
        array_push(_s.row.samples,scrFRBiomeClearance204NaturalSample(_s,true));
        _s.phase=3;_s.elapsed=0;return false;
    }
    var _old=_s.elapsed;_s.elapsed+=timescale;
    if(_s.elapsed>=15 && floor(_old/15)<floor(_s.elapsed/15)) scrFRBiomeClearance204MapFire(_s);
    if(_s.elapsed>=60 && floor(_old/60)<floor(_s.elapsed/60)) {
        array_push(_s.row.samples,scrFRBiomeClearance204NaturalSample(_s,true));
        scrFRBiomeClearance204MapApproach(_s);
    }
    if(instance_exists(Portal)) {
        var _portal=instance_find(Portal,0);
        // Source clearance counts enemy/becomenemy and pending police. Neutral
        // hitme props such as BigPipe can legally remain beside an open exit.
        if(_portal.type!=1 || scr_check_enemies() || !array_length(_s.row.hits))
            scrFRBiomeClearance204MapFail(_s,"Biome map exit did not satisfy ordinary native hostile clearance");
        _s.row.portal={id:real(_portal),type:_portal.type,x:_portal.x,y:_portal.y,ticks:_s.elapsed};
        _s.row.final=scrFRBiomeClearance204NaturalSample(_s,true);_s.row.result="passed";
        array_push(_s.rows,_s.row);scrNTTESmokeLog("BIOME CLEARANCE204 MAP ACCEPTED "+json_stringify(_s.row));
        _s.phase=0;return false;
    }
    if(_s.elapsed>=900) scrFRBiomeClearance204MapFail(_s,"Biome map combat did not produce its ordinary type1 exit within30seconds");
    return false;
}
