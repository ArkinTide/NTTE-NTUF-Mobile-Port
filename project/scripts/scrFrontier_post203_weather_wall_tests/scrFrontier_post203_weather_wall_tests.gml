// Isolated rendered join checks and the actual chamber transition entry point.
// No game clock, snow density, actor AI or texture source is replaced here.
function scrFRPost203WeatherWallTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled(),
        "Blizzard/chamber regression requires the isolated muted native harness");
    var _before=scrNTTEFullInstances(all),_area=GameCont.area,_seed=random_get_seed(),
        _source_seed=scrFRSourceRandomGetSeed(),_surface=-1,_camera=-1,_target=surface_get_target(),
        _world=matrix_get(matrix_world),_view=matrix_get(matrix_view),_projection=matrix_get(matrix_projection),
        _color=draw_get_color(),_alpha=draw_get_alpha(),_shader=shader_current(),
        _oldx=view_xview,_oldy=view_yview,_oldw=view_width,_oldh=view_height,
        _events=global.fr_module_vars[$ "mod:Frontier_Events"],_rows=[];
    gpu_push_state();
    try {
        // Reproduce a newly created chamber door inheriting the campfire body
        // while the copied top belongs to Labs/HQ. Invoke the production
        // transition, retaining native collision and authored frame choices.
        var _areas=[area_labs,area_hq];
        for(var _i=0;_i<array_length(_areas);++_i) {
            GameCont.area=area_campfire;
            var _wall=instance_create(214000+64*_i,214000,Wall),_mask=_wall.mask_index,
                _solid=_wall.solid,_x=_wall.x,_y=_wall.y;
            _wall.topindex=3;_wall.outindex=2;_wall.image_index=1;_wall.image_blend=c_aqua;
            GameCont.area=_areas[_i];
            scrNTTEFullChamberTransition(_wall,_areas[_i]);
            assert(_wall.area==_areas[_i] && _wall.outspr==scrNTTEFullAreaWallSprite(_areas[_i],"Out")
                && _wall.sprite_index==(_areas[_i]==area_labs?scrNTTERefSprite("Wall6BotTrans")
                    :scrNTTEFullAreaWallSprite(_areas[_i],"Bot")),
                "Hidden room retained its campfire body/outer edge instead of the chamber area");
            assert(_wall.topspr==scrNTTEFullAreaWallSprite(_areas[_i],"Trans")
                && _wall.topindex==3 && _wall.outindex==2 && _wall.image_index==1
                && _wall.image_blend==c_aqua && _wall.mask_index==_mask && _wall.solid==_solid
                && _wall.x==_x && _wall.y==_y,
                "Hidden-room wall style changed its native collision or authored frame state");
            // The top-only sliding door path must retain the source tile cap.
            _wall.topspr=scrNTTEFullAreaWallSprite(_areas[_i],"Top");
            var _top=_wall.topspr;
            scrFRChamberWallStyle(_wall,_areas[_i]);
            assert(_wall.topspr==_top && _wall.topindex==3,
                "Sliding door area repair replaced its restored source top tile");
        }
        GameCont.area=_area;
        // A wide viewport reproduces the phone screenshot's inner-mask join.
        // Integer and fractional world/camera offsets exercise both raster
        // alignment directions; Eyes/Bat Ears radii retain a clear centre.
        view_width=960;view_height=240;
        _surface=surface_create(view_width,view_height);
        surface_set_target(_surface);matrix_set(matrix_world,matrix_build_identity());
        shader_reset();gpu_set_fog(false,0,0,0);gpu_set_texfilter(false);gpu_set_blendmode(bm_normal);
        var _scales=[.6,.9,1.2,1.5],_offsets=[[0,0,.0,.0],[10000.25,10000.75,.25,.5],[-1000.75,-800.25,.75,.25]],
            _fog=make_color_rgb(63,43,150),_background=make_color_rgb(11,19,27);
        for(var _o=0;_o<array_length(_offsets);++_o) {
            var _off=_offsets[_o];view_xview=_off[0];view_yview=_off[1];
            if(_camera>=0) camera_destroy(_camera);
            _camera=camera_create_view(view_xview,view_yview,view_width,view_height,0,noone,-1,-1,-1,-1);
            camera_apply(_camera);
            var _px=view_xview+480+_off[2],_py=view_yview+120+_off[3];
            for(var _s=0;_s<array_length(_scales);++_s) {
                var _scale=_scales[_s],_checks=0;
                draw_clear(_background);draw_set_color(c_white);draw_set_alpha(1);
                draw_sprite_ext(_events.sprVignette,0,_px,_py,_scale,_scale,0,_fog,1);
                draw_set_alpha(.37);
                // The Runner may quantize a requested alpha. Preserve the
                // getter's actual incoming state, not the ideal setter value.
                var _incoming_alpha=draw_get_alpha();
                scrFRBlizzardOuterMask(_px,_py,_scale,_fog);
                var _returned_alpha=draw_get_alpha();
                assert(_returned_alpha==_incoming_alpha,
                    "Blizzard outer mask leaked Draw alpha state: incoming="
                        +string(_incoming_alpha)+" returned="+string(_returned_alpha));
                assert(surface_getpixel(_surface,480,120)==_background,
                    "Blizzard mask obscured the authored clear centre");
                var _edge=round(250*_scale),_ys=[8,64,120,184,232];
                for(var _side=-1;_side<=1;_side+=2)
                    for(var _dx=-1;_dx<=3;++_dx) for(var _j=0;_j<array_length(_ys);++_j) {
                        var _sample=surface_getpixel(_surface,480+_side*(_edge+_dx),_ys[_j]);
                        assert(abs(color_get_red(_sample)-color_get_red(_fog))<=1
                            && abs(color_get_green(_sample)-color_get_green(_fog))<=1
                            && abs(color_get_blue(_sample)-color_get_blue(_fog))<=1,
                            "Blizzard inner/outer mask exposed a bright seam at a fractional viewport join");
                        _checks++;
                    }
                array_push(_rows,{scale:_scale,camera:[view_xview,view_yview],
                    incoming_alpha:_incoming_alpha,returned_alpha:_returned_alpha,seam_pixels_checked:_checks});
            }
        }
        assert(scrFRSourceRandomGetSeed()==_source_seed,"Weather/chamber repair consumed source gameplay RNG");
        var _file=file_text_open_write(working_directory+"ntuf-post203-weather-wall.json");
        file_text_write_string(_file,json_stringify({physical_device_tested:false,
            chamber_areas:_areas,rendered_join_cases:_rows,source_rng_unchanged:true}));file_text_close(_file);
        scrNTTESmokeLog("PASS NTUF Labs/HQ chamber side/out ownership and 12 rendered wide-view Blizzard join cases");
    } finally {
        if(surface_get_target()==_surface) surface_reset_target();
        if(_target>=0 && surface_get_target()!=_target) surface_set_target(_target);
        if(_camera>=0) camera_destroy(_camera);if(surface_exists(_surface)) surface_free(_surface);
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);matrix_set(matrix_projection,_projection);
        gpu_pop_state();if(_shader<0) shader_reset();else shader_set(_shader);
        draw_set_color(_color);draw_set_alpha(_alpha);
        view_xview=_oldx;view_yview=_oldy;view_width=_oldw;view_height=_oldh;
        GameCont.area=_area;random_set_seed(_seed);scrNTTEFullMergedRuntimeTestCleanup(_before);
    }
}
