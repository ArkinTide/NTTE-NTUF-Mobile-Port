// Dedicated native binary Continue from a genuinely completed four-part quest
// held before UNLOCK. Reuses the existing private-process/save isolation host;
// source 120tick merges, all eight HeartBullets, generated combat and pickup
// execute normally before Vlambeer's real loader reconstructs a new Vault.
function scrFRQuestContinue205TestsStart() {
    scrNTTEFullPizzaLairDrainNaturalTests();
    with(NTTEFullPizzaLairDrainNaturalTest) {
        fr_quest_continue205={phase:0,index:0,rates:[30,60],ticks:0,rows:[],row:undefined,
            source:noone,want_pick:false,unlocked:false,ready_draw:-1};
    }
}
function scrFRQuestContinue205State() {
    if(os_type!=os_windows || !scrNTTEFullSmokeEnabled()) return undefined;
    var _host=instance_find(NTTEFullPizzaLairDrainNaturalTest,0);
    if(!instance_exists(_host)) return undefined;
    return scrNTTEFullValue(_host,"fr_quest_continue205",undefined);
}
function scrFRQuestContinue205InputAllowed(_observer) {
    var _s=scrFRQuestContinue205State();
    if(is_undefined(_s) || _s.source!=_observer) return true;
    return _observer.phase!=7;
}
function scrFRQuestContinue205BypassPizzaBot() {
    var _s=scrFRQuestContinue205State();
    return !is_undefined(_s) && _s.phase==1;
}
function scrFRQuestContinue205Write(_host,_status,_reason="") {
    var _s=_host.fr_quest_continue205,_out={schema:1,status:_status,reason:_reason,
        physical_device_tested:false,full_binary_native_continue:true,
        actual_source_merges_and_combat:true,rows:_s.rows,active:_s.row};
    var _file=file_text_open_write(working_directory+"frontier-quest-continue205.json");
    file_text_write_string(_file,json_stringify(_out));file_text_close(_file);
    scrNTTESmokeLog("FR_QUEST_CONTINUE205 "+json_stringify(_out));
}
function scrFRQuestContinue205Fail(_host,_reason) {
    scrFRQuestContinue205Write(_host,"FAIL",_reason);throw _reason;
}
function scrFRQuestContinue205UnlockedProbe() {
    var _s=scrFRQuestContinue205State();
    if(is_undefined(_s) || _s.phase!=3 || !_s.want_pick) return;
    _s.unlocked=true;
    _s.row.native_unlock={locked:instance_exists(NTTEFullLockedHugeQuestChest),
        reward:instance_exists(NTTEFullHugeQuestChest),guard:scrFRQuestPortal204Blocked(),
        active:scrNTTEFullValue(GameCont,"fr_quest_portal205_active",false),frame:current_frame};
}
function scrFRQuestContinue205AfterSample(_host,_keycont,_index) {
    var _s=scrNTTEFullValue(_host,"fr_quest_continue205",undefined);
    if(is_undefined(_s) || !instance_exists(_host.player) || _host.player.index!=_index) return;
    _keycont.press_pick[_index]=_s.want_pick;
    _keycont.hold_pick[_index]=_s.want_pick;
    _keycont.moving[_index]=0;_keycont.hold_fire[_index]=false;_keycont.press_fire[_index]=false;
}
function scrFRQuestContinue205HostStep(_host) {
    var _s=scrNTTEFullValue(_host,"fr_quest_continue205",undefined);
    if(is_undefined(_s)) return false;
    _s.ticks+=timescale;
    if(_s.ticks>5400) scrFRQuestContinue205Fail(_host,"Real quest/Continue route exceeded its native 5400tick bound");
    if(_s.phase==0) {
        with(_host) scrNTTEFullPizzaLairDrainClear();
        var _rate=_s.rates[_s.index];
        save_set_value("options","framerate",_rate);save_set_value("options","autopause",false);
        save_set_value("options","keyboard",true);save_set_value("options","gamepad",false);
        save_set_value("game","tutorial",false);save_set_value("visual","bossintro",false);save_set_value("visual","freezeframes",false);
        UberCont.opt_framerate=_rate;game_set_speed(_rate,gamespeed_fps);
        UberCont.opt_autopause=false;UberCont.paused=false;UberCont.want_pause=false;UberCont.opt_freeze=0;
        UberCont.opt_keyboard=true;UberCont.opt_gamepad=false;UberCont.opt_bossintro=false;
        UberCont.block_input_frames=0;UberCont.block_input_fire=false;
        UberCont.daily_run=false;UberCont.weekly_run=false;UberCont.coop=false;UberCont.hardmode=false;
        UberCont.continued_run=false;UberCont.want_quit_to_menu=false;UberCont.show_leaderboards_menu=false;
        global.is_server=true;global.index=0;global.custom_seed=41;global.recontinued_times=0;global.crownpick=crwn_none;
        global.__debug_infammo=false;scrGameCustomModeReset();scr_playerinstances_reset_all();
        my_player.race=Race.Fish;my_player.skin=0;
        global.ntte_full_feature_ready={};global.ntte_full_progress={schema:1,unlocks:{},loadouts:{},stats:{}};
        global.ntte_full_native_weapon_base=maxwep+1;global.ntte_full_native_weapon_models=[];
        game_directory=_host.scratch_root+"quest205-"+string(_rate)+"/";directory_create(game_directory);
        if(file_exists(savegame_file)) file_delete(savegame_file);
        instance_create(0,0,GameCont);instance_create(0,0,BackCont);instance_create(0,0,MusCont);scrCreatePlayers(0);
        _host.player=instance_find(Player,0);_host.room_ends=0;_host.room_starts=0;
        GameCont.area=area_vault;GameCont.subarea=0;GameCont.maxsubarea=1;GameCont.crownvisits=0;
        GameCont.lastarea=area_desert;GameCont.lastsubarea=3;GameCont.loops=0;GameCont.hard=5;
        GameCont.skillpoints=0;GameCont.ultrapoints=0;GameCont.crownpoints=0;GameCont.can_advance_stage=true;
        GameCont.ntte_full_pending_destination=undefined;scrFRQuestPortal205Release();
        scrRngStatesReset();scrNTTEFullQuestStoredHubNaturalTests(41);
        _s.source=instance_find(NTTEFullQuestHubNaturalTest,0);
        _s.row={rate:_rate,source_initial_player:real(_host.player),source_initial_chest:-1,
            actual_merges:[],source_hearts:0,source_enemies:0,source_shots:0,
            binary_bytes:0,loaded_player:-1,loaded_chest:-1,guarded_ticks:0,
            native_unlock:undefined,room_ends:0,room_starts:0};
        _s.phase=1;_s.ticks=0;_s.want_pick=false;_s.unlocked=false;_s.ready_draw=-1;
        return true;
    }
    if(_s.phase==1) {
        if(!instance_exists(_s.source)) scrFRQuestContinue205Fail(_host,"Source quest observer vanished before genuine four-part pickup");
        if(_s.source.phase!=7) return true;
        var _source=_s.source,_chest=_source.hub.main.chest,_player=_source.player;
        assert(instance_exists(_chest) && _chest.is_unlockable && scrFRQuestPortal204Blocked()
            && array_length(scrNTTEFullQuestPartList(_player.wep,_player.ntte_state))==4,
            "Continue checkpoint lacks source active/unlockable chest and native held four-part artifact");
        _s.row.source_initial_chest=real(_chest);_s.row.actual_merges=_source.merges_seen;
        _s.row.source_hearts=array_length(_source.hearts_seen);_s.row.source_enemies=array_length(_source.enemies_seen);
        _s.row.source_shots=_source.shot_count;_s.row.before_guard=scrFRQuestPortal204Blocked();
        assert(_s.row.source_hearts==8 && _s.row.source_enemies>0 && _s.row.source_shots>0,
            "Continue checkpoint omitted actual quest HeartBullet/combat chain");
        var _scratch=_source.scratch;
        array_push(_host.scratch_files,_scratch+"ntte-full-progress.json",_scratch+"ntte-full-progress.json.bak",_scratch+"ntte-full-progress.json.tmp");
        _host.player=_player;scrSavegameSave();
        assert(file_exists(savegame_file),"Quest205 full native binary save missing");
        var _binary=buffer_load(savegame_file);_s.row.binary_bytes=buffer_get_size(_binary);buffer_delete(_binary);
        assert(_s.row.binary_bytes>128,"Quest205 native binary is empty");
        _s.saved_player=_player;_s.saved_chest=_chest;_s.source=noone;
        with(_host) scrNTTEFullPizzaLairDrainClear();
        UberCont.want_quit_to_menu=false;_s.phase=2;_s.ticks=0;
        _host.room_ends=0;_host.room_starts=0;room_restart();return true;
    }
    _host.player=instance_find(Player,0);
    if(_s.phase==2) {
        if(!instance_exists(_host.player) || instance_exists(GenCont) || instance_exists(FloorMaker)) {_s.ready_draw=-1;return true;}
        if(_s.ready_draw<0) {_s.ready_draw=_host.draw_frames;return true;}
        if(_host.draw_frames-_s.ready_draw<8) return true;
        _s.row.room_ends=_host.room_ends;_s.row.room_starts=_host.room_starts;
        _s.row.loaded_player=real(_host.player);_s.row.continued=UberCont.continued_run;
        _s.row.active_after=scrNTTEFullValue(GameCont,"fr_quest_portal205_active",false);
        _s.row.guard_after=scrFRQuestPortal204Blocked();
        var _chest=instance_find(NTTEFullLockedHugeQuestChest,0);
        _s.row.loaded_chest=real(_chest);_s.row.unlockable_after=instance_exists(_chest)?_chest.is_unlockable:false;
        _s.row.held_parts=array_length(scrNTTEFullQuestPartList(_host.player.wep,_host.player.ntte_state));
        scrFRQuestContinue205Write(_host,"IN_PROGRESS","actual full native Continue + generated Vault + eight Draws");
        if(_host.room_ends!=1 || _host.room_starts!=1 || !UberCont.continued_run
            || _host.player==_s.saved_player || !instance_exists(_chest) || _chest==_s.saved_chest
            || !_s.row.active_after || !_s.row.guard_after || _s.row.held_parts!=4)
            scrFRQuestContinue205Fail(_host,"Actual full native Continue lost distinct loaded actors, held graph or active exit claim");
        if(!_chest.is_unlockable)
            scrFRQuestContinue205Fail(_host,"Actual full native Continue reset the completed locked chest's unlockable stage");
        _s.phase=3;_s.ticks=0;return true;
    }
    if(_s.unlocked) {
        assert(!_s.row.native_unlock.locked && _s.row.native_unlock.reward
            && !_s.row.native_unlock.guard && !_s.row.native_unlock.active && _s.row.guarded_ticks>=90,
            "Continued actual UNLOCK failed to release exit claim and create its native reward");
        array_push(_s.rows,_s.row);scrFRQuestContinue205Write(_host,"IN_PROGRESS","continued native UNLOCK passed");
        if(++_s.index<array_length(_s.rates)) {_s.phase=0;_s.ticks=0;return true;}
        scrFRQuestContinue205Write(_host,"PASS");
        with(_host) scrNTTEFullPizzaLairDrainRestore();
        scrNTTESmokeLog("PASS FRONTIER Quest205 genuine merges/held graph/full binary Vlambeer Continue/new Vault/eightDraw/90tick guard/native UNLOCK release x30/60");
        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");game_end();return true;
    }
    var _chest=instance_find(NTTEFullLockedHugeQuestChest,0);
    if(!instance_exists(_chest) || !scrFRQuestPortal204Blocked())
        scrFRQuestContinue205Fail(_host,"Continued quest lost its active guard before native UNLOCK");
    with(Portal) if(type==1 || type==2) scrFRQuestContinue205Fail(_host,"An ordinary portal interrupted the continued active quest");
    _s.row.guarded_ticks+=timescale;
    if(_s.row.guarded_ticks>=90) {
        _host.player.x=_chest.x;_host.player.y=_chest.y+8;
        _host.player.xprevious=_host.player.x;_host.player.yprevious=_host.player.y;
        _s.want_pick=true;
    }
    return true;
}
