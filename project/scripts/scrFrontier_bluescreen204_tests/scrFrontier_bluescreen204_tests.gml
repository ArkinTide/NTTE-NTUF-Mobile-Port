// Query unit controls complement the separately scheduled genuine Robot death
// -> source manager -> raw YES/NO -> native destination/GameOver diagnostics.
function scrFRBluescreen204Tests() {
    var _players=scrNTTEFullInstances(Player),_managers=[],_manager=noone,
        _enabled=scrFRModGet("area","cyberspace","settingCyberspaceEnabled"),
        _visited=GameCont.fr_visitedCyberspace,_win=GameCont.win;
    with(FRCustomObject) if(name=="wib_PlayerManager") array_push(_managers,id);
    try {
        for(var _i=0;_i<array_length(_managers);++_i) instance_deactivate_object(_managers[_i]);
        for(var _i=0;_i<array_length(_players);++_i) instance_deactivate_object(_players[_i]);
        scrFRModSet("area","cyberspace","settingCyberspaceEnabled",true);
        GameCont.fr_visitedCyberspace=false;GameCont.win=false;
        assert(!scrFRBluescreenPendingAdmission204(),"No active Wibbly manager must allow ordinary death");
        _manager=scrFRModCallArray("mod","wibbly","PlayerManager_create",[10016,10016]);
        _manager.livingPlayers=array_create(INPUT_MAX_PLAYERS,0);
        _manager.playerRace=array_create(INPUT_MAX_PLAYERS,"");
        _manager.playerRace[0]="robot";
        assert(!scrFRBluescreenPendingAdmission204(),"An already observed death must not hold GameOver");
        _manager.livingPlayers[0]=1;
        var _before=json_stringify({living:_manager.livingPlayers,races:_manager.playerRace,
            visited:GameCont.fr_visitedCyberspace,win:GameCont.win});
        assert(scrFRBluescreenPendingAdmission204() && scrFRBluescreenPendingAdmission204(),
            "An eligible Robot death must wait for its real manager's next Step");
        assert(_before==json_stringify({living:_manager.livingPlayers,races:_manager.playerRace,
            visited:GameCont.fr_visitedCyberspace,win:GameCont.win}),
            "Pending admission query changed source clocks, arrays or decisions");
        _manager.livingPlayers[0]=0;_manager.livingPlayers[1]=1;
        _manager.playerRace[1]="fish";
        assert(scrFRBluescreenPendingAdmission204(),
            "Last surviving teammate's death must retain the earlier Robot's source revival opportunity");
        _manager.playerRace[0]="fish";
        assert(!scrFRBluescreenPendingAdmission204(),"A team without Robot must allow ordinary death");
        _manager.playerRace[0]="robot";
        GameCont.fr_visitedCyberspace=true;
        assert(!scrFRBluescreenPendingAdmission204(),"YES/NO or a previously visited Cyberspace must release death");
        GameCont.fr_visitedCyberspace=false;GameCont.win=true;
        assert(!scrFRBluescreenPendingAdmission204(),"A finished run must not enter pending admission");
        GameCont.win=false;scrFRModSet("area","cyberspace","settingCyberspaceEnabled",false);
        assert(!scrFRBluescreenPendingAdmission204(),"Disabled Cyberspace must allow ordinary death");
        scrFRModSet("area","cyberspace","settingCyberspaceEnabled",true);
        var _callback=_manager.on_step;
        _manager.on_step=undefined;
        assert(!scrFRBluescreenPendingAdmission204(),"A manager without its source Step cannot hold death");
        _manager.on_step=scrFRBluescreenPendingAdmission204;
        assert(!scrFRBluescreenPendingAdmission204(),"An unrelated callback with a manager name cannot hold death");
        _manager.on_step=_callback;_manager.name="UnrelatedActor";
        assert(!scrFRBluescreenPendingAdmission204(),"An unrelated actor cannot hold death");
        _manager.name="wib_PlayerManager";
        instance_deactivate_object(_manager);
        assert(!scrFRBluescreenPendingAdmission204(),"An inactive manager cannot observe the death");
        instance_activate_object(_manager);
        var _living=_manager.livingPlayers,_races=_manager.playerRace;
        _manager.livingPlayers=undefined;
        assert(!scrFRBluescreenPendingAdmission204(),"An uninitialized manager must allow ordinary death");
        _manager.livingPlayers=_living;_manager.playerRace=undefined;
        assert(!scrFRBluescreenPendingAdmission204(),"An uninitialized race array must allow ordinary death");
        _manager.playerRace=_races;
        if(array_length(_players)>0) {
            instance_activate_object(_players[0]);
            assert(!scrFRBluescreenPendingAdmission204(),"A living teammate must not enter death admission");
            instance_deactivate_object(_players[0]);
        }
        // This is the real source Step, not a recreated version of its loop.
        // Its win branch declines revival without touching death-drop state.
        GameCont.win=true;
        with(_manager) scrFRModCallArray("mod","wibbly","PlayerManager_step",[]);
        GameCont.win=false;
        assert(_manager.livingPlayers[1]==0 && !scrFRBluescreenPendingAdmission204(),
            "Original manager consumption must release pending death without a timer or synthetic revival");
        scrNTTESmokeLog("PASS FRONTIER BLUESCREEN204 pending native death query; real manager identity, team Robot, one observation, source release and disabled/visited/win/living/invalid controls");
    } finally {
        if(_manager!=noone) {
            instance_activate_object(_manager);
            if(instance_exists(_manager)) instance_destroy(_manager);
        }
        for(var _i=0;_i<array_length(_managers);++_i) instance_activate_object(_managers[_i]);
        for(var _i=0;_i<array_length(_players);++_i) instance_activate_object(_players[_i]);
        scrFRModSet("area","cyberspace","settingCyberspaceEnabled",_enabled);
        GameCont.fr_visitedCyberspace=_visited;GameCont.win=_win;
    }
}
