// Private callback/voice-state regression. The parent runner must be muted at
// its Windows audio session: these tests deliberately retain real nonzero mix
// and voice gains, and never record or play the resulting output for the user.
function scrFRSealSpinAudioTestsVoiceState(_voices) {
    var _out=[];
    for(var _i=0;_i<array_length(_voices);++_i) {
        var _item=_voices[_i],_voice=_item[0],_sample=_item[1];
        array_push(_out,[audio_is_playing(_voice),audio_sound_get_gain(_voice),
            audio_sound_get_pitch(_voice),audio_sound_get_gain(_sample)]);
    }
    return json_stringify(_out);
}

function scrFRSealSpinAudioTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled(),
        "Seal spin audio tests require the externally muted private native runner");
    var _before=scrNTTEFullInstances(all),_rate=game_get_speed(gamespeed_fps),
        _scale=timescale,_tick=current_frame,_seed=random_get_seed(),
        _rng=scrNTTEFullArrayCopy(global.rng_state),_volume=UberCont.opt_sndvol,
        _emitter_gain=audio_emitter_get_gain(UberCont.mainsound),
        _sample_gain=audio_sound_get_gain(sndMeleeFlip),
        _old_record=variable_global_exists("fr_menu_audio_test_state")?global.fr_menu_audio_test_state:undefined,
        _collector={phase:0,round:0,voices:[]},_voices=[],_rows=[];
    global.fr_menu_audio_test_state=_collector;
    try {
        UberCont.opt_sndvol=1;audio_emitter_gain(UberCont.mainsound,.7);
        audio_sound_gain(sndMeleeFlip,1,0);
        // Independent live music, ambience and effect voices detect accidental
        // asset/bus edits. Production swing playback uses the shared emitter.
        var _music=audio_play_sound(musThemeA,128,true,.6),
            _ambient=audio_play_sound(amb0,128,true,.5),
            _effect=audio_play_sound(sndPistol,128,true,.7);
        _voices=[[_music,musThemeA],[_ambient,amb0],[_effect,sndPistol]];
        for(var _i=0;_i<array_length(_voices);++_i)
            assert(_voices[_i][0]>=0 && audio_is_playing(_voices[_i][0]),
                "Seal audio fixture requires independent live native voices");
        var _mix=scrFRSealSpinAudioTestsVoiceState(_voices),
            _options=json_stringify([UberCont.opt_volume,UberCont.opt_musvol,UberCont.opt_ambvol,UberCont.mainvol]);
        for(var _hz=30;_hz<=60;_hz+=30) {
            game_set_speed(_hz,gamespeed_fps);global.time_scale=30/_hz;
            assert(game_get_speed(gamespeed_fps)==_hz && timescale==30/_hz,
                "Seal audio fixture did not use the actual30/60Hz engine rate");
            for(var _holding=0;_holding<2;++_holding) for(var _sign=-1;_sign<=1;_sign+=2) {
                var _heavy=instance_create(186000,186000,NTTEFullSealHeavy),_anchor=noone;
                _heavy.hp=32;_heavy.ntte_heavy_timer=10000;_heavy.anchor_spin=_sign*20;
                _heavy.anchor_throw=0;_heavy.anchor_retract=false;
                _heavy.gunangle=_sign>0?350:10;_heavy.sprite_index=_heavy.spr_idle;
                if(_holding) {
                    _anchor=instance_create(_heavy.x,_heavy.y,NTTEFullSealAnchor);
                    _anchor.creator=_heavy;_anchor.team=_heavy.team;_heavy.anchor=_anchor;
                }
                _collector.voices=[];_collector.round=_hz;current_frame=0;
                repeat(90*_hz/30) {
                    // This is the real object's registered Step event, not a
                    // duplicate swing implementation or direct sound-helper test.
                    with(_heavy) event_perform(ev_step,ev_step_normal);
                    assert(scrFRSealSpinAudioTestsVoiceState(_voices)==_mix
                        && json_stringify([UberCont.opt_volume,UberCont.opt_musvol,UberCont.opt_ambvol,UberCont.mainvol])==_options
                        && abs(audio_emitter_get_gain(UberCont.mainsound)-.7)<.0001
                        && abs(audio_sound_get_gain(sndMeleeFlip)-1)<.0001,
                        "Heavy Seal spin altered another voice, resource, emitter or global mix state");
                    current_frame+=timescale;
                }
                var _count=array_length(_collector.voices),_gain=_holding?.8:.15;
                assert(_count==5,"Heavy Seal spin must issue one transient per real revolution at30/60Hz");
                for(var _i=0;_i<_count;++_i) {
                    var _voice=_collector.voices[_i];
                    assert(_voice.sample==sndMeleeFlip && abs(_voice.gain_at_start-_gain)<.0001
                        && _voice.pitch_at_start>=.1 && _voice.pitch_at_start<.2
                        && abs(_voice.sample_gain_at_start-1)<.0001,
                        "Heavy Seal spin lost its authored pitch or retained unsafe8x transient gain");
                }
                array_push(_rows,{rate:_hz,holding_anchor:!!_holding,spin_sign:_sign,
                    real_step_calls:90*_hz/30,source_ticks:90,swing_voices:_count,
                    voice_gain:_gain,emitter_gain:audio_emitter_get_gain(UberCont.mainsound),
                    independent_voice_state:json_parse(_mix)});
                if(instance_exists(_anchor)) instance_destroy(_anchor,false);
                instance_destroy(_heavy,false);audio_stop_sound(sndMeleeFlip);
            }
        }
        // A later ordinary user of this shared sample must keep normal gain/
        // pitch. Per-resource poisoning would survive the swing and fail here.
        var _ordinary=snd_play(sndMeleeFlip);
        assert(_ordinary>=0 && audio_is_playing(_ordinary)
            && abs(audio_sound_get_gain(_ordinary)-1)<.0001
            && abs(audio_sound_get_pitch(_ordinary)-1)<.0001
            && scrFRSealSpinAudioTestsVoiceState(_voices)==_mix,
            "Heavy Seal spin poisoned later ordinary melee playback or independent mix voices");
        audio_stop_sound(_ordinary);
        var _file=file_text_open_write(working_directory+"ntuf-seal-spin-audio-voices.json");
        try {file_text_write_string(_file,json_stringify({rows:_rows,
            ordinary_voice_gain:1,ordinary_voice_pitch:1,audio_output_captured:false,
            physical_device_tested:false}));} finally {file_text_close(_file);}
        scrNTTESmokeLog("PASS FRONTIER Heavy Seal real Step30/60Hz both spin directions, windup/anchor gain headroom and independent music/ambient/effect voice+resource/emitter/global-state preservation");
    } finally {
        for(var _i=0;_i<array_length(_voices);++_i)
            if(audio_exists(_voices[_i][0])) audio_stop_sound(_voices[_i][0]);
        audio_stop_sound(sndMeleeFlip);audio_sound_gain(sndMeleeFlip,_sample_gain,0);
        var _all=scrNTTEFullInstances(all);
        for(var _i=0;_i<array_length(_all);++_i)
            if(array_get_index(_before,_all[_i])<0) instance_destroy(_all[_i],false);
        UberCont.opt_sndvol=_volume;audio_emitter_gain(UberCont.mainsound,_emitter_gain);
        global.fr_menu_audio_test_state=_old_record;game_set_speed(_rate,gamespeed_fps);
        global.time_scale=_scale;current_frame=_tick;random_set_seed(_seed);global.rng_state=_rng;
    }
}
