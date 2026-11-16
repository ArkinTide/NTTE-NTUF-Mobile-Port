function scrFRMergedLaserOracle213(_enemies) {
    if(!array_length(_enemies) || !place_meeting(x,y,hitme)) return false;
    var _self=id;
    for(var _i=0;_i<array_length(_enemies);++_i) if(instance_exists(_enemies[_i])) with(_enemies[_i]) {
        if(id!=_self && place_meeting(x,y,_self)) return true;
    }
    return false;
}

function scrFRMenuSpiral213Tests() {
    var _state=scrNTTEFullCoastDrawState(),_surface=surface_create(64,64),
        _camera=camera_create_view(0,0,64,64,0,noone,-1,-1,-1,-1),_target=false,
        _normal=[],_difference=0;
    gpu_push_state();
    try {
        assert(surface_exists(_surface),"Spiral visual test surface allocation failed");
        surface_set_target(_surface);_target=true;camera_apply(_camera);
        matrix_set(matrix_world,matrix_build_identity());shader_reset();gpu_set_blendmode(bm_normal);
        draw_clear_alpha(c_black,0);
        scrFRSpiralDraw213(sprSpiral,0,32,32,1,1,0,c_white,1);
        for(var _y=0;_y<64;_y+=8) for(var _x=0;_x<64;_x+=8)
            array_push(_normal,surface_getpixel_ext(_surface,_x,_y));
        draw_clear_alpha(c_black,0);
        scrFRSpiralDraw213(sprSpiral,1,32,32,1,1,0,c_white,1);
        var _i=0;
        for(var _y=0;_y<64;_y+=8) for(var _x=0;_x<64;_x+=8)
            assert(_normal[_i++]==surface_getpixel_ext(_surface,_x,_y),
                "Ordinary menu spiral alternated complementary masks after a60Hz image rebase");
        draw_clear_alpha(c_black,0);
        draw_sprite_ext(sprSpiral,1,32,32,1,1,0,c_white,1);_i=0;
        for(var _y=0;_y<64;_y+=8) for(var _x=0;_x<64;_x+=8)
            _difference+=_normal[_i++]!=surface_getpixel_ext(_surface,_x,_y);
        assert(_difference>0,"Menu regression fixture did not contain the complementary native mask");
        // IDPD and Proto remain animated by their authored native frame.
        draw_clear_alpha(c_black,0);
        scrFRSpiralDraw213(sprSpiralIDPD,1,32,32,1,1,0,c_white,1);_normal=[];
        for(var _y=0;_y<64;_y+=8) for(var _x=0;_x<64;_x+=8)
            array_push(_normal,surface_getpixel_ext(_surface,_x,_y));
        draw_clear_alpha(c_black,0);
        draw_sprite_ext(sprSpiralIDPD,1,32,32,1,1,0,c_white,1);_i=0;
        for(var _y=0;_y<64;_y+=8) for(var _x=0;_x<64;_x+=8)
            assert(_normal[_i++]==surface_getpixel_ext(_surface,_x,_y),
                "Normal spiral sampling fix changed the native IDPD portal frame");
        scrNTTESmokeLog("PASS NTUF213 normal menu mask stable across complementary image frames; IDPD authored frame unchanged");
    } finally {
        if(_target) surface_reset_target();
        if(surface_exists(_surface)) surface_free(_surface);camera_destroy(_camera);
        gpu_pop_state();matrix_set(matrix_world,_state.world);matrix_set(matrix_view,_state.view);
        matrix_set(matrix_projection,_state.projection);
        if(_state.shader>=0) shader_set(_state.shader);else shader_reset();
        draw_set_color(_state.color);draw_set_alpha(_state.alpha);
    }
}

function scrFRPerformance213Tests() {
    var _before=scrNTTEFullInstances(all),_seed=random_get_seed(),_timer_rows=[],
        _saved_slots=variable_global_exists("fr_alarm_slots213")?global.fr_alarm_slots213:undefined,
        _checks=0,_alarms=[];
    for(var _i=0;_i<array_length(_before);++_i) if(instance_exists(_before[_i])) {
        var _slots=[];for(var _j=0;_j<12;++_j) array_push(_slots,_before[_i].alarm[_j]);
        array_push(_alarms,[_before[_i],_slots]);
    }
    try {
        scrFRAlarmSlotsInit213();
        assert(array_length(global.fr_alarm_slots213[Floor])==0
            && array_length(global.fr_alarm_slots213[FRCustomObject])==0,
            "Alarm metadata failed to skip bodies with no native countdown events");
        assert(array_get_index(global.fr_alarm_slots213[Player],10)>=0
            && array_get_index(global.fr_alarm_slots213[Player],11)<0,
            "Alarm metadata lost the native Player Alarm10 or invented Alarm11");
        var _p=instance_find(Player,0),_alarm10=_p.alarm[10],_alarm11=_p.alarm[11];
        try {
            _p.alarm[10]=50;_p.alarm[11]=75;
            scrFRAlarmTopUp213(2);
            assert(_p.alarm[10]==52 && _p.alarm[11]==75,
                "Exact alarm top-up changed dormant no-event alarms or missed live slots");
        } finally {_p.alarm[10]=_alarm10;_p.alarm[11]=_alarm11;}
        _checks+=3;

        var _shot=instance_create(550000,550000,Bullet1),_enemies=[],_sx=_shot.x,_sy=_shot.y;
        _shot.speed=0;_shot.team=team_player;_shot.mask_index=sprBanditIdle;
        repeat(240) {
            var _e=instance_create(_sx+32+irandom(240),_sy+400+irandom(500),FRCustomHitme);
            _e.mask_index=sprBanditIdle;_e.sprite_index=sprBanditIdle;_e.team=team_enemy;_e.visible=false;
            array_push(_enemies,_e);
        }
        for(var _i=0;_i<9;++_i) {
            var _a=45*_i,_e=instance_create(_sx+lengthdir_x(96,_a),_sy+lengthdir_y(96,_a),FRCustomHitme);
            _e.mask_index=sprBanditIdle;_e.sprite_index=sprBanditIdle;_e.team=team_enemy;_e.visible=false;
            array_push(_enemies,_e);
        }
        var _stale=instance_create(_sx,_sy,FRCustomHitme);
        with(_stale) instance_destroy();array_push(_enemies,_stale);
        var _scales=[1,3,-1,-3];
        for(var _si=0;_si<array_length(_scales);++_si) with(_shot) {
            image_xscale=_scales[_si];image_yscale=abs(_scales[_si]);
            var _ox=_sx+0.375,_oy=_sy-0.625,_range=256.375;
            for(var _a=0;_a<360;_a+=15) {
                x=_ox;y=_oy;var _dx=dcos(_a),_dy=-dsin(_a),
                    _candidates=scrFRMergedLaserCandidates213(_enemies,_range,_dx,_dy);
                for(var _dis=0;_dis<=_range;_dis+=4) {
                    x=_ox+_dx*_dis;y=_oy+_dy*_dis;
                    var _expected=scrFRMergedLaserOracle213(_enemies),
                        _actual=array_length(_candidates)>0 && place_meeting(x,y,hitme)
                            && scrFRMergedLaserMeeting213(_candidates);
                    assert(_expected==_actual,"Quasar ray candidate pruning changed precise mask contact");
                    _checks++;
                }
                x=_ox+_dx*_range;y=_oy+_dy*_range;
                assert(scrFRMergedLaserOracle213(_enemies)
                    ==(array_length(_candidates)>0 && place_meeting(x,y,hitme)
                        && scrFRMergedLaserMeeting213(_candidates)),
                    "Quasar ray fractional endpoint changed precise mask contact");
                _checks++;
            }
        }
        with(_shot) {
            image_xscale=3;image_yscale=3;x=_sx;y=_sy;
            var _candidates=scrFRMergedLaserCandidates213(_enemies,256,1,0),_begin=get_timer(),_hits=0;
            repeat(8) for(var _dis=0;_dis<=256;_dis+=4) {
                x=_sx+_dis;y=_sy;_hits+=scrFRMergedLaserOracle213(_enemies);
            }
            var _oracle_us=get_timer()-_begin,_oracle_hits=_hits;_hits=0;_begin=get_timer();
            repeat(8) for(var _dis=0;_dis<=256;_dis+=4) {
                x=_sx+_dis;y=_sy;
                _hits+=array_length(_candidates)>0 && place_meeting(x,y,hitme)
                    && scrFRMergedLaserMeeting213(_candidates);
            }
            var _optimized_us=get_timer()-_begin;
            assert(_hits==_oracle_hits && array_length(_candidates)<array_length(_enemies)/4,
                "Quasar benchmark did not retain contacts or exclude off-ray hostile bodies");
            array_push(_timer_rows,{hostiles:array_length(_enemies),candidates:array_length(_candidates),
                oracle_us:_oracle_us,optimized_us:_optimized_us,contacts:_hits});
        }
        var _file=file_text_open_write(working_directory+"ntuf213-performance.json");
        file_text_write_string(_file,json_stringify({passed:true,checks:_checks,laser:_timer_rows,
            device_tested:false,scope:"CPU mask queries; no Android frame-rate claim"}));file_text_close(_file);
        scrFRMenuSpiral213Tests();
        scrNTTESmokeLog("PASS NTUF213 exact inherited alarm slots and Quasar/melee swept-bbox mask parity "+string(_checks)+" "+json_stringify(_timer_rows));
    } finally {
        global.fr_alarm_slots213=_saved_slots;
        for(var _i=0;_i<array_length(_alarms);++_i) if(instance_exists(_alarms[_i][0]))
            for(var _j=0;_j<12;++_j) _alarms[_i][0].alarm[_j]=_alarms[_i][1][_j];
        scrNTTEFullMergedRuntimeTestCleanup(_before);random_set_seed(_seed);
    }
}
