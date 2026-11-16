function scrFRWorld213Tests() {
    assert(scrNTTESmokeEnabled(),"World213 tests require the isolated smoke harness");
    var _before=scrNTTEFullInstances(all),_game=scrNTTEFullAreaGeneratorSnapshot(GameCont),
        _players=scrNTTEFullAreaGeneratorSnapshot(Player),_seed=random_get_seed(),
        _parked=scrNTTEFullInstances(enemy),_progress=global.ntte_full_progress,
        _frame=current_frame,_gameDirectory=game_directory,
        _scratch=working_directory+"world213-fixture/";
    directory_create(_scratch);game_directory=_scratch;
    scrNTTEFullFloorInit();
    var _align=[global.ntte_full_floor_aw,global.ntte_full_floor_ah,
        global.ntte_full_floor_ax,global.ntte_full_floor_ay];
    for(var _i=0;_i<array_length(_parked);++_i) instance_deactivate_object(_parked[_i]);
    global.ntte_full_progress=json_parse(json_stringify(_progress));
    GameCont.ntte_full_source_seed=json_parse(json_stringify(scrNTTEFullSourceSeedState()));
    try {
        GameCont.area=area_desert;GameCont.subarea=1;
        scrFRWorld213MaggotTests();
        scrFRWorld213CursedTests();
        scrFRWorld213QuestAnchorTests();
        scrFRWorld213CoastEntryTests();
    } finally {
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        for(var _i=0;_i<array_length(_parked);++_i) instance_activate_object(_parked[_i]);
        scrNTTEFullAreaGeneratorRestore(_game);scrNTTEFullAreaGeneratorRestore(_players);
        global.ntte_full_progress=_progress;random_set_seed(_seed);current_frame=_frame;
        scrNTTEFullFloorSetAlign(_align[0],_align[1],_align[2],_align[3]);
        var _files=[_scratch+"ntte-full-progress.json",_scratch+"ntte-full-progress.json.bak",
            _scratch+"ntte-full-progress.json.tmp"];
        for(var _i=0;_i<array_length(_files);++_i) if(file_exists(_files[_i])) file_delete(_files[_i]);
        game_directory=_gameDirectory;
    }
    scrNTTESmokeLog("PASS FRONTIER213 world: single-use fired larvae, cursed bone exclusion, replaced quest Floors, enclosed Coast orb shoreline access");
}

function scrFRWorld213MaggotTests() {
    var _player=instance_find(Player,0),_wall=instance_create(628000,628000,Wall),
        _shot=instance_create(628024,628008,FiredMaggot),_count=instance_number(Maggot);
    _player.x=_shot.x;_player.y=_shot.y;_player.hp=max(_player.hp,1);_player.team=0;
    _shot.team=1;
    with(_player) with(_shot) event_perform(ev_collision,Player);
    assert(!instance_exists(_shot) && instance_number(Maggot)==_count+1,
        "Fired larva contact failed to consume its source exactly once");
    var _dead=instance_create(628024,628008,FiredMaggot);
    _dead.hp=0;
    with(_wall) with(_dead) event_perform(ev_collision,Wall);
    assert(!instance_exists(_dead) && instance_number(Maggot)==_count+1,
        "A killed fired larva became a fresh enemy on its following collision");
    var _ally=instance_create(628024,628008,FiredMaggot);
    _ally.team=_player.team;
    with(_player) with(_ally) event_perform(ev_collision,Player);
    assert(instance_exists(_ally) && instance_number(Maggot)==_count+1,
        "Allied fired larva incorrectly landed on its own team");
    var _land=instance_create(628024,628008,FiredMaggot);
    with(_wall) with(_land) event_perform(ev_collision,Wall);
    assert(!instance_exists(_land) && instance_number(Maggot)==_count+2,
        "Wall contact lost the ordinary single landed larva");
    scrNTTESmokeLog("FRONTIER213 MAGGOT: real Player/Wall collision consumption, killed-before-collision and allied controls OK");
}

function scrFRWorld213CursedTests() {
    var _player=instance_find(Player,0),_context={x:628000,y:628000,curse:0},
        _identity=function(_n) {return _n-1;};
    _player.race=Race.Fish;_player.wep=wep_revolver;_player.bwep=wep_ntte_bone;
    _player.ntte_state=undefined;_player.bntte_state=undefined;
    assert(scrNTTEFullWeaponDropArea("crabbone",_context)==4,
        "Normal source bone availability was removed with cursed drops");
    // Bypass the ordinary duplicate slot, as an initialized physical LWO does.
    _player.bntte_state=scrNTTENewState(wep_ntte_bone);
    scrNTTEFullWeaponDropLWOInit(wep_ntte_bone,_player.bntte_state,"step");
    assert(scrNTTEFullWeaponDropSelect(["crabbone"],0,99,_context,_player,_identity)==wep_ntte_bone,
        "Normal chest lost its valid conditional source bone candidate");
    _context.curse=1;
    assert(scrNTTEFullWeaponDropArea("crabbone",_context)==-1
        && scrNTTEFullWeaponDropSelect(["crabbone"],0,99,_context,_player,_identity)==wep_screwdriver,
        "Cursed chest still selected a quest bone through the native shuffled pool");
    // A physical cursed-big chest is authoritative even when its caller says false.
    var _big=instance_create(628128,628000,CursedBigChest),_result;
    _big.curse=true;
    repeat(32) {
        with(_big) _result=scrNTTEFullChestDecide(20,false);
        assert(_result!=wep_ntte_bone,"Physical cursed-big chest emitted a bone");
    }
    scrNTTESmokeLog("FRONTIER213 CURSED: conditional normal bone remains legal; cursed shuffled-only candidate and 32 physical cursed-big choices exclude it");
}

function scrFRWorld213QuestAnchorTests() {
    GameCont.area=area_vault;GameCont.subarea=1;
    var _pair=scrNTTEFullQuestTeleporterPair(629016,629016,629272,629016),
        _pad=_pair[0],_dest=_pair[1],_floor=_pad.target,
        _x=_floor.x,_y=_floor.y,_tx=_pad.teleport_x,_ty=_pad.teleport_y;
    var _replacement=scrNTTEFullFloorSet(_x,_y,true);
    assert(!instance_exists(_floor) && instance_exists(_replacement),
        "Quest recovery fixture failed to replace its original native Floor");
    with(_pad) event_perform(ev_step,ev_step_end);
    assert(instance_exists(_pad),"Replacing a quest Floor deleted the live hub entrance");
    assert(_pad.target==_replacement && _replacement.sprite_index==scrNTTERefSprite("QuestTeleporterFloor")
        && _pad.teleport_x==_tx && _pad.teleport_y==_ty && instance_exists(_dest),
        "Quest hub rebind lost its exact tile art, paired destination or coordinates");
    instance_destroy(_replacement,false);
    with(_pad) event_perform(ev_step,ev_step_end);
    assert(instance_exists(_pad),"Cleared quest Floor deleted its authored hub entrance");
    assert(instance_exists(_pad.target),"Cleared quest entrance did not restore physical Floor");
    assert(_pad.target.x==_x && _pad.target.y==_y
        && _pad.target.sprite_index==scrNTTERefSprite("QuestTeleporterFloor"),
        "Restored hub tile moved or lost its source teleport decoration");
    var _keyfloor=scrNTTEFullFloorSet(629504,629000,true);
    _keyfloor.sprite_index=scrNTTERefSprite("QuestFloor");_keyfloor.image_index=2;
    var _key=instance_create(_keyfloor.x+16,_keyfloor.y+16,NTTEFullQuestFloorCont);
    _key.part_index=2;_key.target=_keyfloor;
    scrFRWorld213QuestFloorBind(_key);
    var _newfloor=scrNTTEFullFloorSet(_keyfloor.x,_keyfloor.y,true);
    with(_key) event_perform(ev_step,ev_step_normal);
    assert(instance_exists(_key),"Replacing a quest key tile deleted its DROP controller");
    assert(_key.target==_newfloor && _newfloor.image_index==2
        && _newfloor.sprite_index==scrNTTERefSprite("QuestFloor") && instance_exists(_key.prompt),
        "Quest key tile rebind lost its physical target, part image or interaction prompt");
    scrNTTESmokeLog("FRONTIER213 QUEST: real paired hub and key controller survive native FloorSet replacement and erased-floor recovery");
}

function scrFRWorld213CoastEntryTests() {
    GameCont.area=area_desert;GameCont.subarea=1;
    var _x=630016,_y=630016,_player=instance_find(Player,0),
        _old=instance_create(_x-128,_y+256,Wall),_generation=instance_create(0,0,BulletHit);
    _player.x=_x-96;_player.y=_y+32;
    for(var _island=0;_island<2;++_island) {
        var _ix=_x+_island*256;
        for(var _fy=0;_fy<64;_fy+=32) for(var _fx=0;_fx<64;_fx+=32)
            instance_create(_ix+_fx,_y+_fy,Floor);
        for(var _off=-16;_off<=64;_off+=16) {
            instance_create(_ix+_off,_y-16,Wall);instance_create(_ix+_off,_y+64,Wall);
            if(_off>=0 && _off<64) {
                instance_create(_ix-16,_y+_off,Wall);instance_create(_ix+64,_y+_off,Wall);
            }
        }
        instance_create(_ix+32,_y+32,Bandit);
        assert(collision_line(_ix-48,_y+32,_ix+32,_y+32,Wall,false,false),
            "Coast topology fixture was not actually sealed by real native Walls");
    }
    GameCont.area=scrNTTEFullAreaId("coast");
    var _floors=instance_number(Floor),_opened=scrFRWorld213CoastOrbEntry(_generation);
    assert(_opened==2 && instance_exists(_old) && instance_number(Floor)==_floors,
        "Coast orb failed per-component entry, modified old walls, or filled walkable sea");
    for(var _island=0;_island<2;++_island) {
        var _ix=_x+_island*256;
        assert(!collision_line(_ix-48,_y+32,_ix+32,_y+32,Wall,false,false),
            "Coast orb's live enemies remain inaccessible behind its sealed shore");
    }
    var _remaining=instance_number(Wall);
    assert(scrFRWorld213CoastOrbEntry(_generation)==0 && instance_number(Wall)==_remaining,
        "Already accessible Coast islands were repeatedly carved");
    GameCont.area=area_desert;
    assert(scrFRWorld213CoastOrbEntry(_generation)==0,
        "Coast shoreline repair changed an ordinary land biome");
    scrNTTESmokeLog("FRONTIER213 COAST ORB: two sealed live-enemy islands receive 48px sea entrances; old walls, land count, already-open and ordinary-biome controls preserved");
}
