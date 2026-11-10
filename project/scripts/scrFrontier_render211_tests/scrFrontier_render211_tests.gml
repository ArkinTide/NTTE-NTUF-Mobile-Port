function scrFRRender211Tests() {
    var _before=scrNTTEFullInstances(all),_game=scrNTTEFullAreaGeneratorSnapshot(GameCont),
        _state=scrNTTEFullCoastDrawState(),_vx=view_xview,_vy=view_yview,
        _minor=variable_global_exists("ntte_full_minor_quality")?global.ntte_full_minor_quality:undefined,
        _main_option=scrNTTEFullOptionRaw("quality:main"),_minor_option=scrNTTEFullOptionRaw("quality:minor"),
        _parked=scrNTTEFullInstances([Floor,Wall,TopSmall,GenCont,NTTEFullCoastSea,NTTEFullCoastSeaTop,NTTEFullCoastSeaVisible]),
        _output=-1,_pattern=-1,_sprite=-1,_camera=-1,_rows=[];
    for(var _i=0;_i<array_length(_parked);++_i) instance_deactivate_object(_parked[_i]);
    gpu_push_state();
    try {
        view_xview=42000;view_yview=42000;GameCont.area=201;GameCont.subarea=1;
        GameCont.ntte_full_active_coast=true;GameCont.ntte_sea_inst=[];
        global.ntte_full_minor_quality=1/3;
        global.ntte_full_progress.loadouts[$ "option:quality:main"]=0;
        _output=surface_create(ceil(view_width),ceil(view_height));
        _camera=camera_create_view(view_xview,view_yview,view_width,view_height,0,noone,-1,-1,-1,-1);
        _pattern=surface_create(16,24);surface_set_target(_pattern);draw_clear_alpha(c_black,0);
        matrix_set(matrix_world,matrix_build_identity());
        var _small_camera=camera_create_view(0,0,16,24,0,noone,-1,-1,-1,-1);camera_apply(_small_camera);
        draw_set_alpha(1);
        for(var _x=0;_x<16;++_x) {
            draw_set_color((_x mod 2)?c_lime:c_red);draw_rectangle(_x,0,_x+1,24,false);
        }
        _sprite=sprite_create_from_surface(_pattern,0,0,16,24,false,false,8,24);
        camera_destroy(_small_camera);surface_reset_target();
        var _actor=instance_create(42120,42070,AnimParticle);
        _actor.sprite_index=_sprite;_actor.image_speed=0;_actor.image_index=0;
        _actor.wading=18;_actor.wading_wave=0;_actor.wading_sink=0;_actor.visible=false;
        GameCont.ntte_sea_inst=[_actor];
        var _sea=scrNTTEFullCoastSeaEnsure();
        surface_set_target(_output);camera_apply(_camera);
        for(var _compat=0;_compat<2;++_compat) {
            _sea.ntte_coast_opaque_output=(_compat==1);_sea.ntte_coast_fast_swim=(_compat==0);
            draw_clear_alpha(c_black,0);draw_set_color(c_white);draw_set_alpha(1);
            with(_sea) event_perform(ev_draw,0);
            assert(_sea.ntte_coast_draw_ready && !_sea.ntte_coast_frame_fallback
                && _sea.ntte_coast_swimmer_count==1,"Actual sea failed its one-pixel swimmer fixture");
            for(var _i=4;_i<8;++_i)
                assert(_sea.ntte_coast_surfaces[_i].scale>=1,"Actor intermediate still downsampled below native pixels");
            with(_sea) scrNTTEFullCoastSurfacePresent(ntte_coast_surfaces[5]);
            var _top=_sea.ntte_coast_surfaces[5],_different=0,_last=-1,_opaque=0;
            for(var _x=113;_x<127;++_x) {
                var _pixel=surface_getpixel_ext(_top.surf,_x,50);
                if(_last!=-1 && (_pixel&$ffffff)!=(_last&$ffffff)) _different++;
                if(((_pixel>>24)&255)>200) _opaque++;
                _last=_pixel;
            }
            assert(_different>=11 && _opaque>=12,
                "One-pixel swimmer stripes lost detail in actual water capture: "+string([_compat,_different,_opaque]));
            surface_save(_output,working_directory+"frontier-water211-"+string(_compat)+".png");
            array_push(_rows,{compat:_compat,edge_changes:_different,opaque_samples:_opaque,
                actor_scales:[_sea.ntte_coast_surfaces[4].scale,_sea.ntte_coast_surfaces[5].scale,
                    _sea.ntte_coast_surfaces[6].scale,_sea.ntte_coast_surfaces[7].scale],
                regional_pixels:_sea.ntte_coast_swim_blit_pixels});
        }
        var _notices=scrFRRender211Notices(_output,_camera),_custom=scrFRCustom211ScrollTests();
        var _file=file_text_open_write(working_directory+"frontier-water211.json");
        file_text_write_string(_file,json_stringify({physical_device_tested:false,rows:_rows,notices:_notices,custom_scroll:_custom}));file_text_close(_file);
        scrNTTESmokeLog("PASS NTUF211 native one-pixel swimmer detail through Android and iOS compositor branches "+json_stringify(_rows));
    } finally {
        for(var _i=0;_i<16 && real(surface_get_target())!=real(_state.target);++_i) surface_reset_target();
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        if(sprite_exists(_sprite)) sprite_delete(_sprite);
        if(surface_exists(_pattern)) surface_free(_pattern);
        if(surface_exists(_output)) surface_free(_output);
        if(_camera>=0) camera_destroy(_camera);
        scrNTTEFullAreaGeneratorRestore(_game);
        for(var _i=0;_i<array_length(_parked);++_i) instance_activate_object(_parked[_i]);
        view_xview=_vx;view_yview=_vy;global.ntte_full_minor_quality=_minor;
        global.ntte_full_progress.loadouts[$ "option:quality:main"]=_main_option;
        global.ntte_full_progress.loadouts[$ "option:quality:minor"]=_minor_option;
        gpu_pop_state();matrix_set(matrix_world,_state.world);matrix_set(matrix_view,_state.view);matrix_set(matrix_projection,_state.projection);
        if(_state.shader>=0) shader_set(_state.shader);else shader_reset();
        draw_set_color(_state.color);draw_set_alpha(_state.alpha);
    }
}

function scrFRCustom211ScrollTests() {
    var _gw=gui_w,_gh=gui_h,_vw=view_width,_vh=view_height,_mobile=is_mobile,
        _touch=KeyCont.touch[global.index],
        _old_rate=save_get_option("options","framerate",30),
        _options=UberCont.custom_options,_custom=UberCont.custom,_rows=[],_before=scrNTTEFullInstances(all),
        _draw=scrNTTEFullCoastDrawState(),_surface=-1,_camera=-1,
        _fixture=variable_global_exists("fr_touch_input_fixture")?global.fr_touch_input_fixture:undefined;
    try {
        is_mobile=true;KeyCont.touch[global.index]=true;UberCont.custom=true;
        UberCont.custom_options=new CustomModeOptions("211 scroll acceptance");
        for(var _wide=0;_wide<2;++_wide) for(var _rate=30;_rate<=60;_rate+=30) {
            save_set_value("options","framerate",_rate);scrOptionsUpdate();scrNTTEFullRateApply();
            assert(abs(timescale-30/_rate)<0.001,"Custom slider test did not apply the actual host rate");
            var _w=_wide?580:426,_h=240;
            // Wide case also exercises GUI/view size disagreement. The
            // settings thumb and its raw input must share GUI coordinates.
            display_set_gui_size(_w,_h);view_width=_w+(_wide?80:0);view_height=_h;
            _surface=surface_create(_w,_h);_camera=camera_create_view(0,0,_w,_h,0,noone,-1,-1,-1,-1);
            surface_set_target(_surface);camera_apply(_camera);matrix_set(matrix_world,matrix_build_identity());
            var _menu=instance_create(0,0,MenuOptions);
            with(_menu) {
                scrOptionsMenuChangeCategory(OptionCategory.CustomMode_SkillSelector);
                wait=false;last_change=current_frame-100;
            }
            var _selector=instance_create(0,0,CustomModeSkillSelector);
            global.fr_touch_input_fixture={active:true,samples:[{x:-1000,y:-1000,held:false,pressed:false,released:false}]};
            with(_menu) event_perform(ev_other,10);
            assert(_menu.scroll_max>0 && _selector.height>gui_h-LETTERBOX_SIZE,
                "Clipped custom mutations still omitted their existing settings scrollbar");
            // Actual native slider hit/drag moves from the top to the bottom.
            // Only the raw hardware sample is synthetic; no scroll variable or
            // mutation selection is assigned by this test after initialization.
            for(var _drag=0;_drag<3;++_drag) {
                global.fr_touch_input_fixture.samples[0]={x:_w-20,
                    y:LETTERBOX_SIZE+(_h-80)*(_drag==0?0:1),
                    held:_drag<2,pressed:_drag==0,released:_drag==2};
                with(_menu) event_perform(ev_other,10);
                if(_drag==0) assert(_menu.dragging && abs(_selector.scroll)<0.01,"Scrollbar top drag did not reach first row");
            }
            assert(!_menu.dragging && abs(_selector.scroll-2*_menu.scroll_max)<0.01,
                "Scrollbar bottom drag failed to expose the final mutation row");
            var _step=sprite_get_width(sprSkillIcon)+4,_ystep=sprite_get_height(sprSkillIcon)+4,
                _start=gui_w div 6,_columns=ceil((gui_w-2*_start)/_step),
                _x=_start+((maxskill-1) mod _columns)*_step,
                _y=LETTERBOX_SIZE+40+((maxskill-1) div _columns)*_ystep-_selector.scroll,
                _bottom=_y+1+sprite_get_height(sprSkillIcon) div 2;
            assert(_y>LETTERBOX_SIZE && _bottom<gui_h-LETTERBOX_SIZE,
                "Full final mutation portrait remains under the bottom letterbox");
            UberCont.custom_options.skill_start=[];
            // Touch selection has the host's two-release tooltip/confirm
            // behavior. Both releases must hit the scrolled icon, not its old
            // pre-scroll position or another mutation.
            repeat(2) {
                global.fr_touch_input_fixture.samples[0]={x:_x,y:_y,held:false,pressed:false,released:true};
                with(_menu) event_perform(ev_other,10);
            }
            assert(array_length(UberCont.custom_options.skill_start)==1
                && UberCont.custom_options.skill_start[0]==maxskill,
                "Scrolled mutation hitbox differs from its visible final icon");
            draw_clear_alpha(c_black,1);
            global.fr_touch_input_fixture.samples[0]={x:-1000,y:-1000,held:false,pressed:false,released:false};
            with(_menu) event_perform(ev_other,11);
            surface_save(_surface,working_directory+"frontier-custom211-"+string(_w)+"-"+string(_rate)+".png");
            array_push(_rows,{width:_w,rate:_rate,range:2*_menu.scroll_max,last_id:maxskill,
                selected:UberCont.custom_options.skill_start[0],last_bottom:_bottom,viewport_bottom:gui_h-LETTERBOX_SIZE});
            surface_reset_target();surface_free(_surface);_surface=-1;camera_destroy(_camera);_camera=-1;
            instance_destroy(_selector,false);instance_destroy(_menu,false);
        }
        scrNTTESmokeLog("PASS NTUF211 actual Custom mutation slider raw top/bottom drag and final-icon touch selection at two widths and30/60 "+json_stringify(_rows));
    } finally {
        if(surface_exists(_surface)) {surface_reset_target();surface_free(_surface);}
        if(_camera>=0) camera_destroy(_camera);
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        save_set_value("options","framerate",_old_rate);scrOptionsUpdate();scrNTTEFullRateApply();
        display_set_gui_size(_gw,_gh);view_width=_vw;view_height=_vh;is_mobile=_mobile;
        KeyCont.touch[global.index]=_touch;
        UberCont.custom_options=_options;UberCont.custom=_custom;global.fr_touch_input_fixture=_fixture;
        matrix_set(matrix_world,_draw.world);matrix_set(matrix_view,_draw.view);matrix_set(matrix_projection,_draw.projection);
        draw_set_color(_draw.color);draw_set_alpha(_draw.alpha);
    }
    return _rows;
}

// Render the same real notification under white and inherited black tint.
// Pixel equality catches the reported intermittent black text while checking
// that both adapters restore the caller's color and alpha afterwards.
function scrFRRender211Notices(_output,_camera) {
    var _console=UberCont.opt_console,_practice=UberCont.opt_practice,
        _blocked=scrNTTEFullValue(GameCont,"fr_progress210_blocked",false),
        _awards=scrNTTEFullValue(GameCont,"fr_achievements_blocked210",false),
        _open=global.console_active,_rows=[],_actors=[];
    try {
        UberCont.opt_console=false;UberCont.opt_practice=false;global.console_active=false;
        GameCont.fr_progress210_blocked=false;GameCont.fr_achievements_blocked210=false;
        scrNTTEFullUnlockSplat("WHITE NOTICE","VISIBLE TEXT",-1,-1);
        scrFRModCallArray("mod","libSaves","unlock_popup",["WHITE NOTICE","VISIBLE TEXT"]);
        var _native=instance_find(NTTEFullUnlockCont,0),_source=scrFRUnlockTestsController();
        assert(instance_exists(_native) && instance_exists(_source),"Actual notification APIs did not create their controllers");
        _actors=[_native,_source];
        for(var _kind=0;_kind<2;++_kind) {
            var _actor=_actors[_kind],_checksum=-1,_bright=0;
            _actor.splash_index=0;_actor.splash_image=1;_actor.splash_texty=-1;
            for(var _tint=0;_tint<2;++_tint) {
                surface_set_target(_output);camera_apply(_camera);draw_clear_alpha(c_black,0);
                draw_set_color(_tint?c_black:c_white);draw_set_alpha(_tint?0.2:1);
                with(_actor) {
                    if(_kind==0) scrNTTEFullUnlockDraw();else scrFRUnlockDraw();
                }
                assert(draw_get_color()==(_tint?c_black:c_white)
                    && abs(draw_get_alpha()-(_tint?0.2:1))<0.001,"Notification leaked its white drawing state");
                var _buffer=buffer_create(ceil(view_width)*ceil(view_height)*4,buffer_fixed,1),_sum=0;
                buffer_get_surface(_buffer,_output,0);
                for(var _pixel=0;_pixel<ceil(view_width)*ceil(view_height);++_pixel) {
                    var _offset=_pixel*4,_a=buffer_peek(_buffer,_offset+3,buffer_u8),
                        _rgb=buffer_peek(_buffer,_offset,buffer_u8)+buffer_peek(_buffer,_offset+1,buffer_u8)
                            +buffer_peek(_buffer,_offset+2,buffer_u8);
                    _sum+=_a*(_rgb+1);
                    if(_tint==0 && _a>200 && _rgb>600) _bright++;
                }
                buffer_delete(_buffer);surface_reset_target();
                if(_tint==0) _checksum=_sum;
                else assert(_sum==_checksum && _bright>20,"Actual notification pixels inherited black/transparent caller tint");
                if(_tint==1) surface_save(_output,working_directory+"frontier-notice211-"+string(_kind)+".png");
            }
            array_push(_rows,{kind:_kind,identical_under_black:true,bright_pixels:_bright,checksum:_checksum});
        }
        scrNTTESmokeLog("PASS NTUF211 real NTTE/NTUF notification pixels ignore inherited black color and restore drawing state");
    } finally {
        for(var _i=0;_i<array_length(_actors);++_i) if(instance_exists(_actors[_i])) instance_destroy(_actors[_i],false);
        UberCont.opt_console=_console;UberCont.opt_practice=_practice;global.console_active=_open;
        GameCont.fr_progress210_blocked=_blocked;GameCont.fr_achievements_blocked210=_awards;
    }
    return _rows;
}
