// Isolated GPU/CPU diagnosis of the actual authored Blizzard components.
// This does not infer mobile FPS from the desktop Runner's presentation rate.
function scrFRBlizzardBench(_scope,_code,_args,_count) {
    draw_clear(make_color_rgb(37,58,74));
    var _start=get_timer();
    repeat(_count) scrFRInvokeDraw(_scope,_code,_args);
    // Force completion of every submitted draw before stopping the clock.
    var _pixel=surface_getpixel_ext(surface_get_target(),view_width div 2,view_height div 2);
    return {calls:_count,total_us:get_timer()-_start,probe:_pixel};
}

function scrFRBlizzardPerformanceTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player),"Blizzard diagnosis requires the private muted Runner");
    var _before=scrNTTEFullInstances(all),_seed=random_get_seed(),_surface=-1,_camera=-1,
        _target=surface_get_target(),_world=matrix_get(matrix_world),_view=matrix_get(matrix_view),
        _projection=matrix_get(matrix_projection),_colour=draw_get_colour(),_alpha=draw_get_alpha(),
        _shader=shader_current(),_oldx=view_xview,_oldy=view_yview,
        _events=global.fr_module_vars[$ "mod:Frontier_Events"],_pos=_events.blizzardSnowPos,
        _flake_sprite=_events.sprBlizzardSnow,_flakes=[],_rows=[],_scope=id,
        _music=instance_find(MusCont,0),_ambient=undefined,_song=undefined;
    // The generic native smoke handoff intentionally removes music owners.
    // Diagnose weather in that actual scope without constructing extra audio.
    if(instance_exists(_music)) {_ambient=_music.amb;_song=_music.song;}
    gpu_push_state();
    try {
        _surface=surface_create(view_width,view_height);
        _camera=camera_create_view(view_xview,view_yview,view_width,view_height,0,noone,-1,-1,-1,-1);
        surface_set_target(_surface);camera_apply(_camera);matrix_set(matrix_world,matrix_build_identity());
        shader_reset();gpu_set_fog(false,0,0,0);gpu_set_texfilter(false);gpu_set_blendmode(bm_normal);
        draw_set_color(c_white);draw_set_alpha(1);
        var _codes=[fr_Frontier_Events_mod_gml_BlizzardSnow_draw,
            fr_Frontier_Events_mod_gml_Blizzard_vignette,fr_Frontier_Events_mod_gml_SolidColorFog_add],
            _args=[[_flake_sprite,-8,2],[x,y,make_color_rgb(107,187,255)],[make_color_rgb(7,48,83),.75]],
            _names=["two-source-tiled-snow-layers","source-player-vignette","source-additive-fog"],
            _positions=[0,900,9000];
        for(var _frame=0;_frame<3;++_frame) {
            _events.blizzardSnowPos=_positions[_frame];
            for(var _i=0;_i<array_length(_codes);++_i) {
                var _row=scrFRBlizzardBench(_scope,_codes[_i],_args[_i],120);
                _row.kind=_names[_i];_row.snow_pos=_events.blizzardSnowPos;array_push(_rows,_row);
            }
        }
        // Natural native SnowFlake lifetime is about320logic ticks; reproduce
        // its full age range and the exact source sprite/direction assignment.
        for(var _i=0;_i<64;++_i) {
            var _flake=instance_create(view_xview+view_width/2,view_yview+view_height/2,SnowFlake);
            _flake.fr_blizzardSnowCheck=undefined;array_push(_flakes,_flake);
        }
        spr_snowflakes=_flake_sprite;
        var _start=get_timer();repeat(120) scrFRInvokeHere(fr_Frontier_Events_mod_gml_Blizzard_step,[]);
        array_push(_rows,{kind:"actual-source-step-64-flakes",calls:120,total_us:get_timer()-_start});
        for(var _i=0;_i<64;++_i) {
            var _flake=_flakes[_i],_age=_i*5;
            _flake.x=view_xview+view_width/2+lengthdir_x(8*_age,190);
            _flake.y=view_yview+view_height/2+lengthdir_y(8*_age,190);
            _flake.addy=max(0,320-_age);_flake.addx=0;
        }
        draw_clear(make_color_rgb(37,58,74));_start=get_timer();
        repeat(120) for(var _i=0;_i<64;++_i) with(_flakes[_i]) event_perform(ev_draw,0);
        var _pixel=surface_getpixel_ext(_surface,view_width div 2,view_height div 2);
        array_push(_rows,{kind:"actual-native-draw-64-source-flakes",calls:120,total_us:get_timer()-_start,probe:_pixel});
        var _evidence={kind:"native Blizzard component diagnosis",physical_device_tested:false,
            viewport:[view_width,view_height],rows:_rows,flake_count:64,
            original_flake_size:[sprite_get_width(sprSnowFlake),sprite_get_height(sprSnowFlake)],
            blizzard_flake_size:[sprite_get_width(_flake_sprite),sprite_get_height(_flake_sprite)]};
        var _file=file_text_open_write(working_directory+"ntuf-blizzard-components.json");
        file_text_write_string(_file,json_stringify(_evidence));file_text_close(_file);
        scrNTTESmokeLog("PASS BLIZZARD COMPONENT DIAGNOSIS "+json_stringify(_evidence));
    } finally {
        if(surface_get_target()==_surface) surface_reset_target();
        if(_target>=0 && surface_get_target()!=_target) surface_set_target(_target);
        if(_camera>=0) camera_destroy(_camera);if(surface_exists(_surface)) surface_free(_surface);
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);matrix_set(matrix_projection,_projection);
        gpu_pop_state();if(_shader<0) shader_reset();else shader_set(_shader);
        draw_set_color(_colour);draw_set_alpha(_alpha);view_xview=_oldx;view_yview=_oldy;
        _events.blizzardSnowPos=_pos;random_set_seed(_seed);
        assert(instance_find(MusCont,0)==_music,"Blizzard draw diagnosis created or removed a native music owner");
        if(instance_exists(_music)) assert(_music.amb==_ambient && _music.song==_song,
            "Blizzard draw diagnosis changed native audio selection");
        scrNTTEFullMergedRuntimeTestCleanup(_before);
    }
}
