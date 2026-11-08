// Only ordinary native constructors, scheduled Top AI/landing and real
// Bullet1 collision/death produce clearance. No timer/mask/portal forcing.
function scrFRBiomeClearance204BulletBefore(_shot,_target) {
    var _driver=instance_find(FRIntegrationTest,0);
    if(!instance_exists(_driver)) return undefined;
    var _s=_driver[$ "fr_biome_clearance204_acceptance"]??undefined;
    if(is_undefined(_s) || _s.bullet!=_shot || _s.actor!=_target) return undefined;
    return {state:_s,bullet:real(_shot),target:real(_target),damage:_shot.damage,
        before:_target.hp,phase:_s.phase};
}
function scrFRBiomeClearance204BulletAfter(_record) {
    var _s=_record.state;variable_struct_remove(_record,"state");
    _record.after=instance_exists(_record.target)?_record.target.hp:undefined;
    _record.consumed=!instance_exists(_record.bullet);
    _s.hit=_record;
    scrNTTESmokeLog("BIOME CLEARANCE204 ACTUAL BULLET "+json_stringify(_record));
}
function scrFRBiomeClearance204AcceptanceStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Biome acceptance requires the isolated native runner");
    _driver.fr_biome_clearance204_acceptance={world:scrNTTEFullWorldEventsNaturalWorldCapture(),
        index:-1,phase:0,elapsed:0,rows:[],actor:noone,bullet:noone,hit:undefined,cases:[
            {rate:30,wall:true},{rate:60,wall:true},
            {rate:30,wall:false},{rate:60,wall:false}]};
}
function scrFRBiomeClearance204AcceptanceNext(_s) {
    scrNTTEFullWorldEventsCleanup();scrFRWallFixTestsReset(_s.world);
    if(++_s.index>=array_length(_s.cases)) {
        var _file=file_text_open_write(working_directory+"frontier-biome-clearance204-acceptance.json");
        file_text_write_string(_file,json_stringify({physical_device_tested:false,cases:_s.rows}));
        file_text_close(_file);scrNTTEFullWorldEventsNaturalWorldRestore(_s.world);return true;
    }
    var _case=_s.cases[_s.index],_x=943000,_y=943000,_player=instance_find(Player,0);
    save_set_value("options","framerate",_case.rate);save_set_value("options","autopause",false);
    save_set_value("visual","freezeframes",0);scrOptionsUpdate();
    GameCont.area=area_jungle;GameCont.subarea=1;GameCont.maxsubarea=1;
    GameCont.loops=1;GameCont.hard=13;GameCont.is_level_ended=false;
    GameCont.popolevel=0;GameCont.killenemies=false;
    _player.x=_x+128;_player.y=_y+128;_player.xprevious=_player.x;_player.yprevious=_player.y;
    _player.hp=max(1,_player.hp);_player.nexthurt=current_frame+100000;
    for(var _ix=0;_ix<8;++_ix) for(var _iy=0;_iy<8;++_iy)
        instance_create(_x+32*_ix,_y+32*_iy,Floor);
    for(var _ix=0;_ix<16;++_ix) for(var _iy=1;_iy<=4;++_iy)
        instance_create(_x+16*_ix,_y-16*_iy,Wall);
    random_set_seed(204057);
    _s.dormant=instance_create(_x+64,_y+(_case.wall?-16:64),JungleAssassinHide);
    _s.old_top=_case.wall?scrNTTEFullTopCreate(_s.dormant.x,_s.dormant.y,_s.dormant,90,16):noone;
    _s.actor=noone;_s.bullet=noone;_s.hit=undefined;_s.elapsed=0;_s.phase=1;
    _s.row={rate:_case.rate,wall:_case.wall,
        dormant:scrFRBiomeClearance204Snapshot(_s.dormant),samples:[]};
    array_push(_s.rows,_s.row);
    scrNTTESmokeLog("BIOME CLEARANCE204 ACCEPTANCE BEGIN "+json_stringify(_s.row));
    return false;
}
function scrFRBiomeClearance204AcceptanceFire(_s,_lethal=false) {
    var _actor=_s.actor,_shot=instance_create(_actor.x,_actor.y,Bullet1);
    _shot.creator=instance_find(Player,0);_shot.team=team_player;_shot.speed=0;
    if(_lethal) _shot.damage=_actor.hp+100;
    _s.bullet=_shot;_s.hit=undefined;_s.shot_hp=_actor.hp;_s.shot_ticks=_s.elapsed;
}
function scrFRBiomeClearance204AcceptanceStep(_driver) {
    var _s=_driver.fr_biome_clearance204_acceptance;
    if(_s.phase==0) return scrFRBiomeClearance204AcceptanceNext(_s);
    _s.elapsed+=timescale;
    if(_s.phase==1) {
        if(instance_exists(_s.dormant)) {
            assert(_s.elapsed<8,"Native dormant assassin failed ordinary last-hostile wakeup");return false;
        }
        _s.actor=instance_find(JungleAssassin,0);
        assert(instance_exists(_s.actor),"Native wake event did not create its actual JungleAssassin");
        var _top=_s.actor[$ "ntte_full_top_object"]??noone,_case=_s.cases[_s.index];
        _s.row.awake=scrFRBiomeClearance204Snapshot(_s.actor);
        if(_case.wall) {
            assert(instance_exists(_top) && _top!=_s.old_top && _top.target==_s.actor
                && _top.type==enemy && _top.override_mask && is_array(_top.target_save.ntte_full_saved_alarms),
                "Wall wake replacement lost its own actual enemy Top/alarm owner");
            _s.top=_top;_s.expected_mask=_top.target_save.mask_index;
            _s.expected_depth=_top.target_save.depth;
            _s.expected_shadow=_top.target_save[$ "spr_shadow"]??(_s.actor[$ "spr_shadow"]??undefined);
            _s.expected_canfly=_top.target_save[$ "canfly"]??(_s.actor[$ "canfly"]??undefined);
        } else assert(!instance_exists(_top),"Ground wake control was incorrectly elevated");
        _s.phase=2;return false;
    }
    if(_s.phase==2) {
        assert(instance_exists(_s.actor),"Awakened native assassin vanished before scheduled combat");
        var _actor=_s.actor,_row=scrFRBiomeClearance204Snapshot(_actor);
        if((_s.elapsed mod 30)<timescale) array_push(_s.row.samples,_row);
        if(instance_exists(_actor[$ "ntte_full_top_object"]??noone)
            || _row.in_wall || !_row.on_floor || _actor.mask_index==mskNone) {
            assert(_s.elapsed<600,"Awakened wall assassin did not reach a shootable floor through native Top AI");
            return false;
        }
        if(_s.cases[_s.index].wall) assert(_actor.mask_index==_s.expected_mask
            && _actor.depth==_s.expected_depth && (_actor[$ "spr_shadow"]??undefined)==_s.expected_shadow
            && (_actor[$ "canfly"]??undefined)==_s.expected_canfly && !instance_exists(_s.old_top),
            "Native Top landing failed mask/depth/shadow/canfly restoration or abandoned its old prop");
        _s.row.landed=_row;_s.phase=3;scrFRBiomeClearance204AcceptanceFire(_s);return false;
    }
    if(_s.phase==3) {
        assert(instance_exists(_s.actor),"Ordinary3damage bullet unexpectedly removed native assassin");
        if(is_undefined(_s.hit)) {
            assert(_s.elapsed-_s.shot_ticks<8,"Real Bullet1 scheduler did not collide with landed assassin");return false;
        }
        assert(_s.hit.damage==3 && _s.hit.consumed && _s.actor.hp==_s.shot_hp-3,
            "Actual native Bullet1 did not inflict authored3damage after ordinary landing");
        _s.row.nonlethal=_s.hit;_s.phase=4;return false;
    }
    if(_s.phase==4) {
        if(!scr_can_hit(_s.actor,true,instance_find(Player,0))) return false;
        _s.phase=5;scrFRBiomeClearance204AcceptanceFire(_s,true);return false;
    }
    if(_s.phase==5) {
        if(instance_exists(_s.actor)) {
            assert(_s.elapsed-_s.shot_ticks<10,"Lethal actual Bullet1 failed native enemy death");return false;
        }
        assert(!is_undefined(_s.hit) && _s.hit.consumed && instance_number(Corpse)>0,
            "Native combat death failed its genuine collision/corpse lifecycle");
        _s.row.lethal=_s.hit;_s.row.death_ticks=_s.elapsed;_s.phase=6;return false;
    }
    if(_s.phase==6) {
        assert(!scr_check_enemies() && instance_number(MeleeFake)==0,
            "Defeated awakened native actor still blocks ordinary clearance");
        if(!instance_exists(Portal)) {
            assert(_s.elapsed-_s.row.death_ticks<180,"Normal death/recovery failed eventual native exit");return false;
        }
        var _portal=instance_find(Portal,0);
        assert(_portal.type==1,"Ordinary Jungle combat opened the wrong portal type");
        _s.row.portal={id:real(_portal),type:_portal.type,x:_portal.x,y:_portal.y,
            ticks:_s.elapsed};
        scrNTTESmokeLog("BIOME CLEARANCE204 ACCEPTED "+json_stringify(_s.row));
        _s.phase=0;return false;
    }
    throw "Unknown biome clearance acceptance phase";
}
