// This explicit private test bypasses the smoke world's synthetic gameplay
// setup. It retains the actual cold-start Logo, MainMenu and native input path.
function scrFRMenuAudioBootTestsSelected() {
    static _selected=undefined;
    if(!is_undefined(_selected)) return _selected;
    _selected=false;
    if(os_type!=os_windows || !scrNTTEFullSmokeEnabled()) return false;
    // The regular async selector also increments a counter initialized only
    // after synthetic gameplay setup. This case deliberately precedes it.
    for(var _i=1;_i<=parameter_count();++_i)
        if(parameter_string(_i)=="--ntte-full-case=FrontierMenuAudioBootTests") _selected=true;
    return _selected;
}
function scrFRMenuAudioBootTestsStep(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled(),"Cold menu audio requires the private muted Runner");
    if(!variable_instance_exists(_driver,"fr_audio_boot")) {
        var _original=UberCont.saveData,_copy=ds_map_create();
        ds_map_copy(_copy,_original);UberCont.saveData=_copy;
        var _state={boot:true,phase:-2,round:0,ticks:0,wait:0,driver:_driver,voices:[],snapshots:[],rows:[],
            original_map:_original,fixture_map:_copy,original_bytes:ds_map_write(_original),
            old_source:-1,portal:-1,ambient:-1,mode_start:-1,track_start:0,gain_start:0,
            portal_plays_start:0,wall_start:0};
        _driver.fr_audio_boot=_state;global.fr_menu_audio_test_state=_state;
        UberCont.opt_autopause=false;UberCont.paused=false;UberCont.opt_freeze=0;
        save_set_value("options","autopause",false);save_set_value("game","tutorial",false);
        save_set_value("volume","master",1);save_set_value("volume","music",.6);
        save_set_value("volume","ambient",.5);save_set_value("volume","sfx",.7);
        scrNTTESmokeLog("NTUF MENU AUDIO true cold-boot observer started without synthetic GameCont");
    }
    var _state=_driver.fr_audio_boot;
    assert(++_state.ticks<2400,"Cold boot audio timed out at phase "+string(_state.phase));
    assert(!instance_exists(GameCont) || _state.phase>=5,"Cold boot fixture accidentally created a gameplay owner");
    if(_state.phase==-2) {
        // Retain the private VM's initial zero resource gains until the
        // external per-process mute has been applied. Do not create/replay Logo.
        ++_state.wait;
        if(_state.wait==ceil(45/timescale)) {
            scrFRMenuAudioTestsRestoreResourceGains();scrOptionsUpdate();scrVolume();
        }
        // Vlambeer's real alarms take about420 logical ticks before Logo is
        // created. Then wait for Logo's actual Alarm0, without replaying it.
        if(!instance_exists(Logo) || Logo.image_index<7) return;
        audio_sound_gain(sndLogoLoop,UberCont.opt_ambvol,0);
        _state.logo=Logo.id;_state.logo_voice=scrFRMenuAudioTestsLatest(_state,sndLogoLoop);
        assert(_state.logo_voice>=0 && audio_is_playing(_state.logo_voice)
            && scrFRMenuAudioTestsCount(_state,sndLogoLoop,true)==1,
            "Cold boot native Logo loop was absent or duplicated");
        with(_state.logo) event_perform(ev_mouse,ev_global_left_press);
        _state.phase=0;return;
    }
    if(_state.phase==0) {
        if(instance_exists(_state.logo)) return;
        assert(!audio_is_playing(_state.logo_voice),"Cold boot Logo loop leaked after native dismiss");
        var _play=noone;with(MainMenuButton)
            if(object_index==MainMenuButton && image_index==0) {_play=id;break;}
        assert(instance_exists(_play),"Cold boot did not reach the actual MainMenu Play receiver");
        with(_play) event_perform(ev_other,ev_user0);
        assert(instance_number(SpiralCont)==1 && instance_number(PlayButton)>=2,
            "Cold boot native Play did not reach the actual recorded mode-selection menu");
        _state.phase=1;_state.wait=0;return;
    }
    if(_state.phase==1) {
        if(++_state.wait<3) return;
        scrFRMenuAudioTestsIdleBegin(_state,2);return;
    }
    if(_state.phase==2) {
        if(++_state.wait<90/timescale) return;
        scrFRMenuAudioTestsIdleEnd(_state,"actual-cold-boot-mode-menu");
        var _normal=noone;with(PlayButton) if(num==0) {_normal=id;break;}
        assert(instance_exists(_normal),"Cold boot omitted the actual Normal-mode receiver");
        _state.phase=5;with(_normal) event_perform(ev_other,ev_user0);
        _state.wait=0;return;
    }
    if(_state.phase==5) {
        if(instance_exists(FloorMaker) || !instance_exists(Menu)) return;
        if(++_state.wait<30/timescale) return;
        assert(!audio_is_playing(_state.portal) && scrFRMenuAudioTestsCount(_state,amb0,true)==1,
            "Cold boot actual character-menu handoff retained portal audio or duplicated ambience");
        var _back=instance_find(BackButton,0);
        assert(instance_exists(_back),"Cold boot character selection omitted its actual BackButton");
        _state.phase=6;_state.wait=0;
        with(_back) event_perform(ev_other,ev_user0);return;
    }
    if(_state.phase==6) {
        if(instance_exists(GameCont) || !instance_exists(SpiralCont)) return;
        scrFRMenuAudioTestsNoRunLoading("true-cold-boot-back");
        scrFRMenuAudioTestsIdleBegin(_state,7);return;
    }
    if(_state.phase==7) {
        if(++_state.wait<90/timescale) return;
        scrFRMenuAudioTestsIdleEnd(_state,"actual-cold-boot-after-character-back");
        var _result={kind:"actual application cold-boot menu voice lifecycle",physical_device_tested:false,
            audio_output_captured:false,rows:_state.rows,voices:_state.voices,snapshots:_state.snapshots};
        var _file=file_text_open_write(working_directory+"ntuf-menu-audio-cold-boot.json");
        file_text_write_string(_file,json_stringify(_result));file_text_close(_file);
        UberCont.saveData=_state.original_map;ds_map_destroy(_state.fixture_map);
        assert(ds_map_write(_state.original_map)==_state.original_bytes,
            "Cold boot audio test changed the original permanent save map");
        _state.phase=99;
        scrNTTESmokeLog("PASS FRONTIER actual cold-boot Logo, mode menu, character selection and Back audio lifecycle");
        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");game_end();
    }
}
