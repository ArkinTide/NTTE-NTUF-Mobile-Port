// Explicit silent GPU acceptance. The source options and actual Pet/feather
// charm Draw consumers remain in charge; no production test override exists.
function scrFROutlineTestsEqual(_first,_second,_where) {
    var _w=surface_get_width(_first),_h=surface_get_height(_first),
        _a=buffer_create(_w*_h*4,buffer_fixed,1),_b=buffer_create(_w*_h*4,buffer_fixed,1);
    try {
        buffer_get_surface(_a,_first,0);buffer_get_surface(_b,_second,0);
        for(var _i=0;_i<_w*_h*4;_i+=4) {
            var _actual=buffer_peek(_a,_i,buffer_u32),_expected=buffer_peek(_b,_i,buffer_u32);
            if(_actual!=_expected) {
                surface_save(_first,working_directory+"frontier-outline-oracle-current.png");
                surface_save(_second,working_directory+"frontier-outline-oracle-reference.png");
            }
            assert(_actual==_expected,
                "Fog-independent outline changed source RGBA "+_where+" pixel="+string(_i div 4)
                    +" actual="+string(_actual)+" expected="+string(_expected));
        }
    }
    finally {buffer_delete(_a);buffer_delete(_b);}
}

function scrFROutlineTestsBackground(_background) {
    // BodyCache intentionally leaves its last internal blend operation to its
    // protected caller. The two independent oracle targets need equal scene
    // paint state before drawing this identical opaque checkerboard.
    draw_clear_alpha(_background,1);draw_set_alpha(1);gpu_set_blendmode(bm_normal);
    draw_set_color(make_color_rgb(83,118,105));
    for(var _yy=0;_yy<64;_yy+=8) for(var _xx=0;_xx<64;_xx+=8)
        if((_xx+_yy) mod 16==0) draw_rectangle(_xx,_yy,_xx+3,_yy+3,false);
    draw_set_color(c_white);
}

function scrFROutlineTestsMask(_screen,_background) {
    var _cases=0,_coverage=0,_alphas=[1,0.5,0.25],_qualities=[1/3,0.5,1,1.75],
        _tints=[c_lime,make_color_rgb(237,75,142)],_rawscales=[1,2],_reference=-1,_buffer=-1;
    try {
        _reference=surface_create(64,64);_buffer=buffer_create(64*64*4,buffer_fixed,1);
        for(var _r=0;_r<array_length(_rawscales);++_r)
        for(var _q=0;_q<array_length(_qualities);++_q)
        for(var _a=0;_a<array_length(_alphas);++_a)
        for(var _t=0;_t<array_length(_tints);++_t)
        for(var _shaders=0;_shaders<2;++_shaders) {
            var _scale=_rawscales[_r],_quality=_qualities[_q],_opacity=_alphas[_a],_tint=_tints[_t],
                _raw=scrNTTEFullOutlineCacheSetup("OutlineAcceptanceRaw",64,64,_scale),
                _old=scrNTTEFullOutlineCacheSetup("OutlineAcceptanceOld",64,64,_quality),
                _new=scrNTTEFullOutlineCacheSetup("OutlineAcceptanceNew",64,64,_quality);
            scrNTTEFullOptionSet("shaders",_shaders);
            surface_set_target(_raw.surf);scrNTTEFullOutlineCamera();draw_clear_alpha(c_black,0);
            gpu_set_blendmode(bm_normal);draw_set_alpha(_opacity);draw_set_color(c_black);
            draw_rectangle(24.25,22.25,34.25,33.25,false);
            draw_set_color(make_color_rgb(252,56,0));draw_rectangle(28.25,26.25,30.25,29.25,false);
            surface_reset_target();draw_set_alpha(1);draw_set_color(c_white);
            scrNTTEFullOutlineBodyCache(_raw,_old);scrNTTEFullOutlineBodyCache(_raw,_new);
            var _size=surface_get_width(_new.surf)*surface_get_height(_new.surf)*4,
                _before=buffer_create(_size,buffer_fixed,1),_after=buffer_create(_size,buffer_fixed,1);
            try {
                buffer_get_surface(_before,_new.surf,0);
                var _state=json_stringify({fog:gpu_get_fog(),blend:gpu_get_blendmode(),
                    write:gpu_get_colorwriteenable(),filter:gpu_get_texfilter(),shader:shader_current(),
                    world:matrix_get(matrix_world),view:matrix_get(matrix_view),projection:matrix_get(matrix_projection),
                    color:draw_get_color(),alpha:draw_get_alpha(),target:surface_get_target()});
                scrNTTEFullOutlineTintCache(_new,_tint);
                assert(_state==json_stringify({fog:gpu_get_fog(),blend:gpu_get_blendmode(),
                    write:gpu_get_colorwriteenable(),filter:gpu_get_texfilter(),shader:shader_current(),
                    world:matrix_get(matrix_world),view:matrix_get(matrix_view),projection:matrix_get(matrix_projection),
                    color:draw_get_color(),alpha:draw_get_alpha(),target:surface_get_target()}),
                    "In-place outline tint leaked GPU/matrix/target/draw state");
                buffer_get_surface(_after,_new.surf,0);
                for(var _i=0;_i<_size;_i+=4) {
                    assert(buffer_peek(_before,_i+3,buffer_u8)==buffer_peek(_after,_i+3,buffer_u8),
                        "In-place outline tint changed transparent or partial source coverage");
                    if(buffer_peek(_before,_i+3,buffer_u8)>0) _coverage++;
                }
            } finally {buffer_delete(_before);buffer_delete(_after);}
            // Retain the old desktop source fog operation as an independent
            // oracle. The production path contains no enabled fog operation.
            surface_set_target(_reference);scrNTTEFullOutlineCamera();scrFROutlineTestsBackground(_background);
            gpu_set_blendmode(bm_normal);gpu_set_fog(true,_tint,0,0);
            for(var _angle=0;_angle<360;_angle+=90)
                scrNTTEFullOutlineSurfaceDraw(_old,lengthdir_x(1,_angle),lengthdir_y(1,_angle));
            gpu_set_fog(false,0,0,0);scrNTTEFullOutlineSurfaceDraw(_old,0,0);surface_reset_target();
            scrNTTEFullOutlineCamera();scrFROutlineTestsBackground(_background);gpu_set_blendmode(bm_normal);
            for(var _angle=0;_angle<360;_angle+=90)
                scrNTTEFullOutlineSurfaceDraw(_new,lengthdir_x(1,_angle),lengthdir_y(1,_angle));
            scrNTTEFullOutlineBodyCache(_raw,_new);scrNTTEFullOutlineCamera();gpu_set_blendmode(bm_normal);
            scrNTTEFullOutlineSurfaceDraw(_new,0,0);
            scrFROutlineTestsEqual(_screen,_reference,json_stringify({raw:_scale,quality:_quality,
                opacity:_opacity,tint:_tint,shaders:_shaders}));
            _cases++;
        }
        assert(_cases==96 && _coverage>0,"Outline GPU acceptance omitted its quality/alpha/shader matrix");
        scrNTTESmokeLog("PASS FRONTIER outline alpha-only mask/source fog GPU oracle "+json_stringify({
            cases:_cases,compared_rgba_pixels:64*64*_cases,covered_cache_pixels:_coverage,
            raw_scales:_rawscales,qualities:_qualities,alpha:_alphas,shader_options:[0,1]}));
    }
    finally {if(surface_exists(_reference)) surface_free(_reference);if(buffer_exists(_buffer)) buffer_delete(_buffer);}
}

function scrFROutlineTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled(),"Outline GPU acceptance needs isolated desktop smoke");
    // Existing actual Pet hooks, native Bandit/charm replay, source eye-color
    // shader and disabled/unowned/revive controls remain part of acceptance.
    scrNTTEFullOutlineOptionsNativeTests();
    var _before=scrNTTEFullInstances(all),_progress=global.ntte_full_progress,
        _game=scrNTTEFullAreaGeneratorSnapshot(GameCont),_players=scrNTTEFullAreaGeneratorSnapshot(Player),
        _view=[view_xview,view_yview,view_width,view_height],_world=matrix_get(matrix_world),
        _matrixview=matrix_get(matrix_view),_projection=matrix_get(matrix_projection),
        _color=draw_get_color(),_alpha=draw_get_alpha(),_shader=shader_current(),_target=false,
        _hidden=scrNTTEFullInstances([Menu,NTTEFullOutlineCache,NTTEFullCharmOutlineDraw,CoopController]),
        _screen=-1,_camera=-1,_p=instance_find(Player,0),_pi=scr_playerinstance_find(_p.index),
        _ownercolor=_pi.color,_native_outlines=UberCont.opt_outlines,
        _oldcharms=scrNTTEFullValue(GameCont,"ntte_charm_instance_list",[]),
        _oldvars=scrNTTEFullValue(GameCont,"ntte_charm_instance_vars",[]),_seed=random_get_seed();
    global.ntte_full_progress=json_parse(json_stringify(_progress));gpu_push_state();
    for(var _i=0;_i<array_length(_hidden);++_i) instance_deactivate_object(_hidden[_i]);
    try {
        view_xview=0;view_yview=0;view_width=64;view_height=64;_pi.color=c_lime;
        GameCont.ntte_charm_instance_list=[];GameCont.ntte_charm_instance_vars=[];
        var _display=scrNTTEFullSourceDisplayScale(),_background=make_color_rgb(12,30,70);
        scrNTTEFullOptionSet("quality:main",(1-1/3)/(_display-1/3));
        _screen=surface_create(64,64);_camera=camera_create_view(0,0,64,64,0,noone,-1,-1,-1,-1);
        assert(surface_exists(_screen),"Outline actual scene target allocation failed");
        surface_set_target(_screen);_target=true;camera_apply(_camera);matrix_set(matrix_world,matrix_build_identity());
        shader_reset();gpu_set_texfilter(false);gpu_set_fog(false,0,0,0);gpu_set_blendmode(bm_normal);
        gpu_set_colorwriteenable(true,true,true,true);draw_set_alpha(1);draw_set_color(c_white);
        // Exercise the real three-state option API without a co-op controller.
        for(var _setting=0;_setting<2;++_setting) {
            var _name=_setting==0?"outline:pets":"outline:charm";
            scrNTTEFullOptionSet(_name,0);assert(!scrNTTEFullOptionGet(_name),"OFF outline setting was ignored");
            scrNTTEFullOptionSet(_name,1);assert(scrNTTEFullOptionGet(_name),"ON outline setting incorrectly required co-op");
            scrNTTEFullOptionSet(_name,2);assert(!scrNTTEFullOptionGet(_name),"AUTO outline setting lost native single-player gate");
            scrNTTEFullOptionSet(_name,1);
        }
        var _pet=instance_create(16,24,NTTEFullPet),_enemy=instance_create(42,32,Bandit);
        _pet.leader=_p;_pet.spr_shadow=-1;_pet.ntte_outline_probe=0;
        _pet.hooks.draw=method(_pet,function(_spr,_img,_x,_y,_xs,_ys,_angle,_color,_alpha) {
            ntte_outline_probe++;draw_set_color(c_black);draw_set_alpha(_alpha);draw_rectangle(_x,_y,_x+4,_y+4,false);
        });
        _p.race=NTTEFullRace.Parrot;
        var _feather=scrNTTEFullParrotFeatherNew(_enemy.x,_enemy.y,_p,_enemy,_p.index);
        with(_feather) event_perform(ev_step,ev_step_normal);
        assert(_feather.stick && _enemy.ntte_charm.charmed && _enemy.ntte_charm.feather
            && _enemy.ntte_charm.index==_p.index,"Actual native Parrot feather did not register its real owner/charm");
        scrNTTEFullCharmOutlineSync();var _groups=scrNTTEFullOutlineManager().groups,_group=noone;
        for(var _i=0;_i<array_length(_groups);++_i) if(_groups[_i].owner_index==_p.index) _group=_groups[_i];
        assert(instance_exists(_group) && array_contains(_group.members,_enemy),"Feather-charmed enemy missed its actual outline renderer");
        for(var _shaders=0;_shaders<2;++_shaders) {
            scrNTTEFullOptionSet("shaders",_shaders);scrFROutlineTestsBackground(_background);
            with(_pet) event_perform(ev_draw,0);with(_enemy) event_perform(ev_draw,0);
            with(_group) event_perform(ev_draw,0);
            assert(surface_getpixel(_screen,15,26)==c_lime,"Real enabled Pet outline lost owner color over black art");
            var _border=scrNTTEFullOutlineManager().entries[$ "CharmBorder"],_count=0;
            for(var _yy=0;_yy<64;++_yy) for(var _xx=0;_xx<64;++_xx) {
                var _pixel=surface_getpixel_ext(_border.surf,_xx,_yy);
                if((_pixel>>24)&255) {assert((_pixel&$ffffff)==c_lime,"Real feather charm border lost owner color");_count++;}
            }
            assert(_count>0,"Real feather-charmed Bandit had no colored outline coverage");
            surface_save(_screen,working_directory+"frontier-outline-feather-shaders-"+string(_shaders)+".png");
        }
        scrFROutlineTestsBackground(_background);
        gpu_set_colorwriteenable(false,true,false,false);gpu_set_ztestenable(true);gpu_set_zwriteenable(true);
        gpu_set_alphatestenable(true);gpu_set_blendmode(bm_add);draw_set_color(c_red);draw_set_alpha(0.25);
        var _dirty=json_stringify({write:gpu_get_colorwriteenable(),ztest:gpu_get_ztestenable(),
            zwrite:gpu_get_zwriteenable(),alphatest:gpu_get_alphatestenable(),blend:gpu_get_blendmode(),
            color:draw_get_color(),alpha:draw_get_alpha(),target:surface_get_target()});
        with(_pet) event_perform(ev_draw,0);with(_group) event_perform(ev_draw,0);
        assert(_dirty==json_stringify({write:gpu_get_colorwriteenable(),ztest:gpu_get_ztestenable(),
            zwrite:gpu_get_zwriteenable(),alphatest:gpu_get_alphatestenable(),blend:gpu_get_blendmode(),
            color:draw_get_color(),alpha:draw_get_alpha(),target:surface_get_target()}),
            "Actual Pet/charm Draw did not restore the caller's nondefault GPU/draw state");
        assert(surface_getpixel(_screen,15,26)==c_lime,
            "Actual Pet capture inherited an unrelated caller's color/depth/alpha write state");
        gpu_set_colorwriteenable(true,true,true,true);gpu_set_ztestenable(false);gpu_set_zwriteenable(false);
        gpu_set_alphatestenable(false);gpu_set_blendmode(bm_normal);draw_set_color(c_white);draw_set_alpha(1);
        scrNTTEFullOptionSet("outline:pets",0);scrNTTEFullOptionSet("outline:charm",0);
        scrNTTEFullOptionSet("shaders",0);scrFROutlineTestsBackground(_background);
        with(_pet) event_perform(ev_draw,0);with(_group) event_perform(ev_draw,0);
        assert(surface_getpixel(_screen,15,26)==_background,"Disabled Pet outline remained visible");
        scrFROutlineTestsMask(_screen,_background);
        assert(_pet.ntte_outline_probe==4,"Pet outline implementation duplicated its actual body callback");
        scrNTTESmokeLog("PASS FRONTIER real option API OFF/ON/AUTO, actual Parrot feather charm registration/native Bandit GPU outline, black-art Pet body one-call and shader ON/OFF; mobile hardware not exercised");
    }
    finally {
        if(_target) surface_reset_target();
        _pi.color=_ownercolor;UberCont.opt_outlines=_native_outlines;
        var _after=scrNTTEFullInstances(all);
        for(var _i=array_length(_after)-1;_i>=0;--_i) if(array_get_index(_before,_after[_i])<0 && instance_exists(_after[_i]))
            instance_destroy(_after[_i],false);
        for(var _i=0;_i<array_length(_hidden);++_i) instance_activate_object(_hidden[_i]);
        if(surface_exists(_screen)) surface_free(_screen);if(_camera>=0) camera_destroy(_camera);
        scrNTTEFullAreaGeneratorRestore(_game);scrNTTEFullAreaGeneratorRestore(_players);
        GameCont.ntte_charm_instance_list=_oldcharms;GameCont.ntte_charm_instance_vars=_oldvars;
        global.ntte_full_progress=_progress;scrNTTEFullProgressSave();
        view_xview=_view[0];view_yview=_view[1];view_width=_view[2];view_height=_view[3];
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_matrixview);matrix_set(matrix_projection,_projection);
        draw_set_color(_color);draw_set_alpha(_alpha);gpu_pop_state();
        if(_shader>=0) shader_set(_shader);else shader_reset();random_set_seed(_seed);
    }
}
