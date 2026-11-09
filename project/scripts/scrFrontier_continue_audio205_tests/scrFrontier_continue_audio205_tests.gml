// Actual source Bulwark -> native voices -> Destroy/Cleanup -> genuine
// preview/full checkpoint loader and asynchronous room regeneration.
function scrFRContinueAudio205TestsBoss() {
    var _p=instance_find(Player,0),_boss=scrFRModCallArray("mod","Frontier_Bosses","RoboBoss_create",[_p.x+120,_p.y]);
    assert(instance_exists(_boss),"Audio205 source RoboBoss factory did not return a native actor");
    with(_boss) {
        // Alarm events have the same object as self and other. Keep that
        // native scope for the source's explicit other.i beam offsets.
        with(id) {
            laserWarnings=0;laserCount=3;laserAngle=0;
            scrFRActorCallback("on_alrm2");
        }
    }
    var _voice=scrFRModGet("mod","Frontier_Bosses","bulwarkLaserLoop");
    assert(_voice>=0 && audio_exists(_voice) && audio_is_playing(_voice)
        && (_boss[$ "fr_bulwark_laser_voice205"]??-1)==_voice,
        "Audio205 did not obtain a genuinely started source laser voice owned by Bulwark");
    return {boss:_boss,voice:_voice};
}

function scrFRContinueAudio205TestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled(),
        "Audio205 requires the private externally muted Windows runner");
    _driver.persistent=true;
    var _state={phase:0,ticks:0,wait:0,marker:noone,generation:false,voice:-1,
        horror:-1,eyes:-1,sentinel:-1,player:noone,rows:[]};
    _driver.fr_continue_audio205=_state;
    // Distinct ordinary sample is a positive control: a global-stop workaround
    // would retire this voice and fail the preview/full-load assertions.
    _state.sentinel=audio_play_sound(sndPistol,2,true,.3);
    assert(_state.sentinel>=0 && audio_is_playing(_state.sentinel),"Audio205 sentinel voice was unavailable");
    var _normal=scrFRContinueAudio205TestsBoss();
    instance_destroy(_normal.boss);
    assert(!audio_is_playing(_normal.voice) && audio_is_playing(_state.sentinel),
        "Ordinary Bulwark Destroy leaked its loop or stopped unrelated audio");
    var _cleanup=scrFRContinueAudio205TestsBoss();
    instance_destroy(_cleanup.boss,false);
    assert(!audio_is_playing(_cleanup.voice) && audio_is_playing(_state.sentinel),
        "Bulwark Cleanup without Destroy leaked its real laser voice");
    // A different instance's late cleanup must never stop a new module voice.
    var _old=scrFRContinueAudio205TestsBoss(),_new=scrFRContinueAudio205TestsBoss();
    instance_destroy(_old.boss,false);
    assert(audio_is_playing(_new.voice),"Old Bulwark Cleanup stopped a newer boss's voice of the same sample");
    instance_destroy(_new.boss,false);
    assert(!audio_is_playing(_new.voice),"Current Bulwark Cleanup did not stop its own captured voice");
    var _room=scrFRContinueAudio205TestsBoss();
    _state.voice=_room.voice;_state.boss=_room.boss;
    _state.player=instance_find(Player,0);
    with(_state.player) {
        horrorloop=snd_play_loop(sndHorrorLoop);eyesloop=snd_play_loop(sndEyesLoop);
    }
    _state.horror=_state.player.horrorloop;_state.eyes=_state.player.eyesloop;
    assert(audio_is_playing(_state.horror) && audio_is_playing(_state.eyes),
        "Audio205 failed to create actual native Player loop handles");
    // Check old saves explicitly, including an otherwise valid current voice.
    assert(scrFRContinuePlayerNativeState("horrorloop",_state.sentinel,true)==-1
        && scrFRContinuePlayerNativeState("eyesloop",_state.sentinel,false)==-1
        && audio_is_playing(_state.sentinel),"Audio205 stale checkpoint handles edited a current native voice");
    scrSavegameSave();
    assert(file_exists(savegame_file),"Audio205 failed to write its isolated native checkpoint");
    scrSavegameLoad(true);
    assert(audio_is_playing(_state.voice) && audio_is_playing(_state.horror)
        && audio_is_playing(_state.eyes) && audio_is_playing(_state.sentinel),
        "Checkpoint preview changed live gameplay or unrelated voices");
    GameCont.ntte_full_pending_destination=undefined;
    GameCont.can_advance_stage=false;GameCont.is_level_ended=true;
    global.ntte_full_sync_generation=false;
    _state.marker=instance_create(0,0,FRMarker);_state.phase=1;
    scrNTTESmokeLog("NTUF AUDIO205 source loop + normal Destroy + Cleanup-only + reused sample + preview PASS");
    room_restart();
}

function scrFRContinueAudio205TestsStep(_driver) {
    var _state=_driver.fr_continue_audio205;
    assert(++_state.ticks<2400,"Audio205 actual Continue regeneration timed out");
    with(Player) {hp=100000;max_hp=100000;nexthurt=current_frame+100000;speed=0;}
    if(_state.phase==1) {
        if(instance_exists(_state.marker)) return false;
        assert(!instance_exists(_state.boss) && !audio_is_playing(_state.voice)
            && !audio_is_playing(_state.horror) && !audio_is_playing(_state.eyes),
            "Actual room disposal retained a source laser or native Player skill loop");
        assert(audio_is_playing(_state.sentinel),"Room Cleanup used a global audio-stop workaround");
        instance_destroy(Player,false);
        assert(scrSavegameLoad(false) && instance_number(Player)==1,
            "Audio205 genuine full checkpoint loader did not reconstruct exactly one Player");
        assert(Player.horrorloop==-1 && Player.eyesloop==-1
            && audio_is_playing(_state.sentinel),"Full Continue restored transient voice IDs or stopped unrelated audio");
        if(!instance_exists(BackCont)) instance_create(0,0,BackCont);
        if(!instance_exists(MusCont)) instance_create(0,0,MusCont);
        assert(!instance_exists(GenCont) && instance_number(Floor)==0,
            "Audio205 full-load fixture did not dispose its old native terrain");
        instance_create(0,0,GenCont);_state.phase=2;return false;
    }
    if(_state.phase==2) {
        if(instance_exists(GenCont) || instance_exists(FloorMaker) || scrGameIsGenerationScreen()
            || !instance_exists(Player) || !instance_exists(TopCont)) return false;
        if(++_state.wait<24) return false;
        assert(instance_number(Floor)>20 && instance_number(Wall)>0
            && !audio_is_playing(_state.voice) && !audio_is_playing(_state.horror)
            && !audio_is_playing(_state.eyes),"Finalized Continue regeneration restarted a retired source laser/skill loop");
        audio_stop_sound(_state.sentinel);
        scrNTTESmokeLog("PASS NTUF AUDIO205 actual source Bulwark voices, normal Destroy, Cleanup-only, reused sample, native preview/full loader + room_restart + async terrain");
        return true;
    }
    return false;
}
