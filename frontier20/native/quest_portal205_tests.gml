// Real asynchronous ordinary Vault generation and genuine projectile deaths.
// No manual enemy destruction, alarm scheduling, portal creation or recovery.
function scrFRQuestPortal205TestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled(),"Vault205 requires the private native runner");
    var _world=scrNTTEFullWorldEventsNaturalWorldCapture();
    _driver.fr_quest_portal205={world:_world,phase:0,index:0,rates:[30,60],ticks:0,ready:0,
        old_rate:game_get_speed(gamespeed_fps),old_directory:game_directory,rows:[],row:undefined};
    var _s=_driver.fr_quest_portal205;
    _s.scratch=working_directory+"quest-vault205-"+string(get_timer())+"/";
    directory_create(_s.scratch);game_directory=_s.scratch;
    global.ntte_full_progress={schema:1,unlocks:{},loadouts:{},stats:{}};
}
function scrFRQuestPortal205NativeShot(_target) {
    var _shot=noone;
    with(Player) {_shot=scr_projectile_create(_target.x,_target.y,Bullet1,0,0);break;}
    assert(instance_exists(_shot) && _shot.creator!=noone,"Vault205 projectile lacks real player ownership");
    _shot.damage=100000;_shot.speed=0;
}
function scrFRQuestPortal205TestsStep(_driver) {
    var _s=_driver.fr_quest_portal205;
    if(_s.phase==0) {
        scrFRWallFixTestsReset(_s.world);scrFRQuestPortal205Release();
        save_set_value("game","tutorial",false);
        save_set_value("options","framerate",_s.rates[_s.index]);save_set_value("options","autopause",false);
        scrOptionsUpdate();UberCont.opt_bossintro=false;UberCont.opt_freeze=0;
        GameCont.area=area_vault;GameCont.subarea=0;GameCont.maxsubarea=1;
        GameCont.lastarea=area_desert;GameCont.lastsubarea=3;GameCont.crownvisits=3;
        GameCont.nochest=0;GameCont.rad=0;GameCont.popolevel=0;GameCont.can_advance_stage=true;
        GameCont.ntte_full_source_pending_generation=undefined;
        global.ntte_full_sync_generation=false;random_set_seed(205713);
        with(Player) {hp=100000;max_hp=100000;nexthurt=current_frame+100000;
            speed=0;can_walk=false;can_aim=false;can_shoot=false;bcan_shoot=false;}
        _s.row={rate:_s.rates[_s.index],actual_async_generator:true,dormant_frames:0,
            statues_seen:[],guardians_seen:[],actual_shots:0,corpse_attempts:0,corpse_passes:0,portal_type:-1};
        var _gen=instance_create(0,0,GenCont);
        assert(!_gen.ntte_full_sync_generation,"Vault205 bypassed native asynchronous generator");
        _s.phase=1;_s.ticks=0;_s.ready=0;return false;
    }
    _s.ticks+=timescale;
    assert(_s.ticks<1800,"Ordinary generated Vault failed to produce its genuine guardian-clear exit");
    assert(game_get_speed(gamespeed_fps)==_s.rates[_s.index] && timescale==30/_s.rates[_s.index],
        "Vault205 native frame rate differs from requested fixture");
    if(_s.phase==1) {
        if(instance_exists(GenCont) || instance_exists(FloorMaker)) {_s.ready=0;return false;}
        if(++_s.ready<8) return false;
        assert(instance_number(Floor)>20 && instance_exists(CrownPickup)
            && instance_number(VaultStatue)==4 && instance_exists(NTTEFullLockedHugeQuestChest),
            "Generated ordinary Vault omitted real CrownPickup/four guardian statues/dormant quest chest");
        _s.row.statues_seen=scrNTTEFullInstances(VaultStatue);
        _s.phase=2;_s.ticks=0;return false;
    }
    assert(instance_exists(NTTEFullLockedHugeQuestChest) && !scrFRQuestPortal204Blocked()
        && !scrNTTEFullValue(GameCont,"fr_quest_portal205_active",false),
        "Dormant locked quest chest claimed an ordinary guardian visit");
    _s.row.dormant_frames++;
    var _guardians=scrNTTEFullInstances(CrownGuardian);
    for(var _i=0;_i<array_length(_guardians);++_i)
        if(array_get_index(_s.row.guardians_seen,_guardians[_i])<0) array_push(_s.row.guardians_seen,_guardians[_i]);
    if(_s.phase==2) {
        if(_s.ticks>=10 && instance_exists(VaultStatue) && _s.row.actual_shots==0) {
            scrFRQuestPortal205NativeShot(instance_find(VaultStatue,0));_s.row.actual_shots++;
        }
        if(!instance_exists(VaultStatue) && array_length(_s.row.guardians_seen)==4) {
            _s.phase=3;_s.ticks=0;
            assert(!instance_exists(CrownPickup) && GameCont.area==area_desert,
                "Actual statue death did not run CrownPickup native logical-area restoration");
        }
        return false;
    }
    if(_s.ticks mod 15<timescale) for(var _i=0;_i<array_length(_guardians);++_i) {
        scrFRQuestPortal205NativeShot(_guardians[_i]);_s.row.actual_shots++;
    }
    var _portal=noone;with(Portal) if(type==1) {_portal=id;break;}
    if(!instance_exists(_portal)) return false;
    _s.row.portal_type=_portal.type;
    assert(!instance_exists(CrownGuardian) && !instance_exists(VaultStatue)
        && _s.row.actual_shots>=5 && _s.row.corpse_attempts>0 && _s.row.corpse_passes>0,
        "Vault205 exit lacks actual guardian damage/death and passing native Corpse.Alarm0");
    array_push(_s.rows,_s.row);
    scrNTTESmokeLog("FR_QUEST_VAULT205 "+json_stringify(_s.row));
    if(++_s.index<array_length(_s.rates)) {_s.phase=0;return false;}
    var _out={schema:1,status:"PASS",physical_device_tested:false,routes:_s.rows};
    var _file=file_text_open_write(working_directory+"frontier-quest-vault205.json");
    file_text_write_string(_file,json_stringify(_out));file_text_close(_file);
    scrNTTEFullWorldEventsNaturalWorldRestore(_s.world);game_directory=_s.old_directory;
    save_set_value("options","framerate",_s.old_rate);scrOptionsUpdate();
    return true;
}
function scrFRQuestPortal205CorpseProbe(_kind) {
    if(os_type!=os_windows || !scrNTTEFullSmokeEnabled()) return;
    var _driver=instance_find(FRIntegrationTest,0);
    if(!instance_exists(_driver) || !variable_instance_exists(_driver,"fr_quest_portal205")) return;
    var _s=_driver.fr_quest_portal205;
    if(is_undefined(_s.row)) return;
    if(_kind=="before") _s.row.corpse_attempts++;
    if(_kind=="passed") _s.row.corpse_passes++;
}
