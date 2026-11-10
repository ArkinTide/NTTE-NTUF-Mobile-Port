// Real Retry retires this driver. Its observer belongs to surviving UberCont.
function scrFRContent210TestsObserve() {
    if(!variable_global_exists("fr_content210_test")) return;
    var _s=global.fr_content210_test;
    if(_s.phase==99) return;
    instance_activate_object(_s.driver);
    if(instance_exists(_s.driver)) return;
    var _d=instance_create(0,0,FRIntegrationTest);
    _d.fr_test_case="content210";_s.driver=_d;
}
function scrFRContent210TestsStart(_d) {
    global.fr_content210_test={phase:1,driver:_d,ticks:0,wait:0,
        owner:FRWorld.id,lib:scrFRLibGlobal(),generation:global.fr_boot_generation};
    save_set_value("game","tutorial",false);
    save_set_value("visual","bossintro",false);
    UberCont.opt_autopause=false;UberCont.opt_freeze=0;
    global.index=0;global.is_server=true;
    scrNTTEFullOptionSet("content:ntuf",false);
    scrNTTEFullOptionSet("content:undergrowth",false);
    my_player.race=19;my_player.skin=1;my_player.cwep=FR_BUBBLES_SHOVEL;
    global.crownpick=17;
    scrGameRestart(false);
}
function scrFRContent210TestsGenerate(_s,_weather=false) {
    assert(instance_number(Player)==1 && instance_number(GameCont)==1,
        "Content Retry failed to construct a single native run");
    if(!instance_exists(BackCont)) instance_create(0,0,BackCont);
    if(!instance_exists(MusCont)) instance_create(0,0,MusCont);
    if(_weather) {
        GameCont.area=201;GameCont.subarea=1;
        global.fr_continue_events={game:GameCont.id,events:[["mod","Frontier_Events","Thunderstorm"]]};
    }
    instance_create(0,0,SpiralCont);
    var _g=instance_create(0,0,GenCont);
    assert(!_g.ntte_full_sync_generation,"Content acceptance bypassed asynchronous generation");
    _s.wait=0;
}
function scrFRContent210TestsStep(_d) {
    if(!variable_global_exists("fr_content210_test")) {
        if(!scrFRReadyTick() || ++_d.fr_test_ticks<45) return false;
        scrFRContent210TestsStart(_d);return false;
    }
    var _s=global.fr_content210_test;
    assert(++_s.ticks<3600,"Content lifecycle acceptance timed out phase="+string(_s.phase));
    assert(scrFRContent210RuntimeReady() && instance_number(FRWorld)==1
        && FRWorld.id==_s.owner && global.fr_boot_generation==_s.generation
        && scrFRLibGlobal()==_s.lib,"Content Retry duplicated or lost its initialized owner");
    with(Player) {hp=100000;max_hp=100000;nexthurt=current_frame+100000;can_walk=false;can_aim=false;speed=0;}
    if(instance_exists(GameCont)) GameCont.is_level_ended=true;
    if(_s.phase==1) {
        assert(!scrFREnabled() && !scrFRContent210Active("undergrowth"),"Retry ignored saved OFF switches");
        var _p=instance_find(Player,0);
        assert(_p.race==Race.Fish && _p.wep==wep_revolver && GameCont.crown!=17,
            "Disabled Bubbles, starter or crown leaked through a real new run");
        scrFRContent210TestsGenerate(_s);_s.phase=2;return false;
    }
    if(_s.phase==2) {
        if(instance_exists(GenCont) || instance_exists(FloorMaker) || !instance_exists(TopCont)) return false;
        assert(instance_number(Floor)>20 && instance_number(FRCustomEnemy)==0,
            "NTUF OFF did not finish a native populated room");
        _s.actor=instance_create(16000,16000,FRCustomObject);
        scrFRContent210Suspend();assert(!instance_exists(_s.actor),"Disabled actor was not suspended");
        scrGamePause();_s.phase=3;return false;
    }
    if(_s.phase==3) {
        if(!UberCont.paused || UberCont.want_pause>0) return false;
        scrGameUnpause();
        assert(!instance_exists(_s.actor),"Unpause reactivated disabled source content");
        // Activation is deferred by the native runner until this event ends.
        // Use the next frame, as a real pause-menu click would.
        _s.phase=7;return false;
    }
    if(_s.phase==7) {
        assert(instance_exists(GameCont),"Unpause lost the native game controller");
        assert(!scrFRContent210Toggle({fr_content210_pack:"ntuf"})
            && !scrFRContent210Toggle({fr_content210_pack:"undergrowth"})
            && !scrFRContent210Requested("ntuf") && !scrFRContent210Requested("undergrowth"),
            "Live run accepted a content switch click");
        scrFRContent210Sync();assert(!scrFREnabled(),"Pause setting changed the active run's content");
        var _saved=scrNTTEFullSystemsExport();
        assert(!_saved.content210.ntuf && !_saved.content210.undergrowth,"Continue saved requested packs instead of active packs");
        scrNTTEFullSystemsImport(json_parse(json_stringify(_saved)));
        assert(!scrFREnabled(),"Continue ignored the saved run's disabled content");
        _s.phase=6;scrGameRestart(true);return false;
    }
    if(_s.phase==6) {
        if(instance_exists(Player)) return false;
        assert(!instance_exists(GameCont),"Quit retained the old game controller");
        assert(!scrFRContent210InRun(),"Quit did not release the live-run settings lock");
        scrFRFollowup210MenuClick("ntuf");
        scrFRFollowup210MenuClick("undergrowth");
        UberCont.want_quit_to_menu=false;UberCont.want_menu=false;UberCont.want_restart=false;
        if(!instance_exists(MusCont)) instance_create(0,0,MusCont);
        var _play=instance_create(0,0,PlayButton);_play.num=0;
        with(_play) event_perform(ev_other,10);
        assert(instance_exists(Menu) && instance_exists(GameCont),"Real Play failed to restore the character menu");
        my_player.race=19;my_player.skin=0;my_player.cwep=FR_BUBBLES_CUTLASS;
        _s.phase=4;scrGameRestart(false);return false;
    }
    if(_s.phase==4) {
        assert(scrFREnabled() && scrFRContent210Active("undergrowth") && !instance_exists(_s.actor),
            "Retry failed to enable requested packs or kept a retired suspended actor");
        var _p=instance_find(Player,0);
        assert(_p.race==19 && _p.wep==FR_BUBBLES_CUTLASS,"Enabled new run lost its authored Bubbles starter");
        scrFRContent210TestsGenerate(_s,true);_s.phase=5;return false;
    }
    if(_s.phase==5) {
        if(instance_exists(GenCont) || instance_exists(FloorMaker) || !instance_exists(TopCont)) return false;
        if(++_s.wait<60) return false;
        var _music=global.fr_module_vars[$ "mod:Frontier_Events"].musThunderstorm,
            _token=scrNTTEFullValue(GameCont,"fr_weather_music210",undefined);
        assert(is_struct(_token) && _token.area==201 && MusCont.song==custom_sound_check(_music),
            "Real weather setup failed to start its music in its generated NTTE room");
        scrNTTESmokeLog("PASS NTUF210 genuine OFF new-run, loadout fallback, pause, saved packs, ON Retry and asynchronous weather music");
        _s.phase=99;return true;
    }
    return false;
}
