// Private actual-room diagnostic. Instrumentation is installed only onto the
// real live test event/controllers, never on the default production hot path.
function scrFRBlizzardLiveRecord(_key,_start) {
    var _state=global.fr_blizzard_live_state;
    if(!_state.sampling) return;
    var _us=get_timer()-_start,_row=_state.profile[$ _key]??{calls:0,total_us:0,max_us:0};
    if(_row.calls==0) {
        var _target=surface_get_target();
        _row.render_target=_target;
        _row.render_target_size=surface_exists(_target)?[surface_get_width(_target),surface_get_height(_target)]:[];
    }
    _row.calls++;_row.total_us+=_us;_row.max_us=max(_row.max_us,_us);_state.profile[$ _key]=_row;
}
function scrFRBlizzardLiveBinding() {
    var _start=get_timer();
    try {return scrFRInvokeDraw(id,fr_weather_original_draw,fr_binding_args);}
    finally {scrFRBlizzardLiveRecord(fr_weather_profile_key,_start);}
}
function scrFRBlizzardLiveEventStep() {
    var _start=get_timer();
    try {return scrFRInvokeHere(fr_weather_original_step,[]);}
    finally {scrFRBlizzardLiveRecord(event+"_step",_start);}
}
function scrFRBlizzardLiveBindingStep() {
    var _start=get_timer();
    try {return scrFRInvokeHere(fr_weather_original_draw,fr_binding_args);}
    finally {scrFRBlizzardLiveRecord(fr_weather_profile_key,_start);}
}
function scrFRBlizzardLiveTestsStart(_driver) {
    _driver.persistent=true;
    _driver.fr_blizzard_live={index:-1,phase:0,ticks:0,rows:[],sampling:false,profile:{},cases:[
        {rate:30,events:[]},{rate:30,events:["Blizzard"]},{rate:30,events:["Aurora","Blizzard"]},
        {rate:60,events:[]},{rate:60,events:["Blizzard"]},{rate:60,events:["Aurora","Blizzard"]}]};
    global.fr_blizzard_live_state=_driver.fr_blizzard_live;
    scrFRBlizzardLiveTestsNext(_driver);
}
function scrFRBlizzardLiveTestsNext(_driver) {
    var _state=_driver.fr_blizzard_live;
    _state.sampling=false;
    if(++_state.index>=array_length(_state.cases)) {_state.phase=9;return;}
    var _case=_state.cases[_state.index];
    save_set_value("options","framerate",_case.rate);save_set_value("options","autopause",false);
    save_set_value("visual","freezeframes",0);save_set_value("visual","bossintro",false);
    save_set_value("game","tutorial",false);scrOptionsUpdate();
    UberCont.opt_autopause=false;UberCont.paused=false;UberCont.opt_freeze=0;
    UberCont.want_quit_to_menu=false;UberCont.want_restart=false;UberCont.want_menu=false;
    // Reuse the real asynchronous event generation boundary, with one fixed
    // map seed across the with/without-event samples. No source result forged.
    _driver.fr_event_index=0;
    scrFREventTestsPrepare(_driver,5,1,0,_case.events);
    _state.phase=-1;_state.ticks=0;_state.profile={};_state.bindings=[];
    scrNTTESmokeLog("NTUF BLIZZARD LIVE actual generation "+json_stringify(_case));
}
function scrFRBlizzardLiveFlakes() {
    var _visible=0,_count=0,_sheet_area=0,_bins=array_create(16*16,0),_max_overlap=0,
        _positions=[],_left=view_xview,_top=view_yview,_right=_left+view_width,_bottom=_top+view_height;
    with(SnowFlake) {
        _count++;
        var _sprite=sprite_index,_x=x+addx-sprite_get_xoffset(_sprite),
            _y=y-addy-sprite_get_yoffset(_sprite),_w=sprite_get_width(_sprite),_h=sprite_get_height(_sprite),
            _l=max(_left,_x),_t=max(_top,_y),_r=min(_right,_x+_w),_b=min(_bottom,_y+_h);
        if(_l<_r && _t<_b && image_alpha>0) {
            _visible++;_sheet_area+=(_r-_l)*(_b-_t);
            var _bx1=clamp(floor((_l-_left)*16/view_width),0,15),
                _by1=clamp(floor((_t-_top)*16/view_height),0,15),
                _bx2=clamp(floor((_r-_left)*16/view_width),0,15),
                _by2=clamp(floor((_b-_top)*16/view_height),0,15);
            for(var _bx=_bx1;_bx<=_bx2;++_bx) for(var _by=_by1;_by<=_by2;++_by) {
                _bins[_by*16+_bx]++;_max_overlap=max(_max_overlap,_bins[_by*16+_bx]);
            }
        }
        if(array_length(_positions)<80) array_push(_positions,{x:x,y:y,addx:addx,addy:addy,
            alpha:image_alpha,sprite:sprite_get_name(sprite_index),speed:speed,direction:direction});
    }
    return {total:_count,visible:_visible,clipped_sheet_view_areas:_sheet_area/(view_width*view_height),
        conservative_grid_overlap:_max_overlap,positions:_positions};
}
function scrFRBlizzardLiveInstrument(_driver) {
    var _state=_driver.fr_blizzard_live,_case=_state.cases[_state.index],_actual=[],_events=[];
    for(var _i=0;_i<array_length(_case.events);++_i) {
        var _event=scrFREventTestsController(_case.events[_i]);
        assert(instance_exists(_event),"Actual generated Blizzard weather controller was missing");
        array_push(_events,_event);
        _event.fr_weather_original_step=_event.on_step;_event.on_step=scrFRBlizzardLiveEventStep;
        with(FRBinding) if(creator==_event) {
            fr_weather_original_draw=fr_binding_code;
            fr_weather_profile_key=script_get_name(is_method(fr_binding_code)?method_get_index(fr_binding_code):fr_binding_code);
            array_push(_actual,{id:id,key:fr_weather_profile_key,kind:fr_binding_kind,depth:depth});
            array_push(_state.bindings,id);
            // End-step compatibility callbacks are timed with the same
            // original bound scope; Draw context is used only for draw binds.
            if(fr_binding_kind=="draw") fr_binding_code=scrFRBlizzardLiveBinding;
            else fr_binding_code=scrFRBlizzardLiveBindingStep;
        }
    }
    _state.binding_manifest=_actual;_state.event_controllers=_events;
    var _snow=0;for(var _i=0;_i<array_length(_actual);++_i)
        if(string_pos("BlizzardSnow_draw",_actual[_i].key)>0) _snow++;
    assert(_snow==(array_length(_case.events)>0?1:0),
        "Actual source generation duplicated or omitted Blizzard snow overlay bindings");
}
function scrFRBlizzardLiveGpu(_driver) {
    var _state=_driver.fr_blizzard_live,_surface=-1,_camera=-1,_target=surface_get_target(),
        _world=matrix_get(matrix_world),_view=matrix_get(matrix_view),_projection=matrix_get(matrix_projection),
        _color=draw_get_color(),_alpha=draw_get_alpha(),_shader=shader_current(),_rows=[];
    gpu_push_state();
    try {
        _surface=surface_create(view_width,view_height);
        _camera=camera_create_view(view_xview,view_yview,view_width,view_height,0,noone,-1,-1,-1,-1);
        surface_set_target(_surface);camera_apply(_camera);matrix_set(matrix_world,matrix_build_identity());
        shader_reset();gpu_set_fog(false,0,0,0);gpu_set_texfilter(false);gpu_set_blendmode(bm_normal);
        draw_set_color(c_white);draw_set_alpha(1);
        for(var _i=0;_i<array_length(_state.bindings);++_i) {
            var _binding=_state.bindings[_i];
            if(!instance_exists(_binding) || _binding.fr_binding_kind!="draw") continue;
            // Warm once before the measured workload. These are actual live
            // bindings/args, including Aurora's actual night sprite choice.
            scrFRInvokeDraw(_binding,_binding.fr_weather_original_draw,_binding.fr_binding_args);
            surface_getpixel_ext(_surface,view_width div 2,view_height div 2);
            draw_clear(make_color_rgb(37,58,74));var _start=get_timer();
            repeat(120) scrFRInvokeDraw(_binding,_binding.fr_weather_original_draw,_binding.fr_binding_args);
            var _pixel=surface_getpixel_ext(_surface,view_width div 2,view_height div 2);
            array_push(_rows,{key:_binding.fr_weather_profile_key,calls:120,total_us:get_timer()-_start,probe:_pixel});
        }
        with(SnowFlake) event_perform(ev_draw,0);
        surface_getpixel_ext(_surface,view_width div 2,view_height div 2);
        draw_clear(make_color_rgb(37,58,74));var _start=get_timer();
        repeat(120) with(SnowFlake) event_perform(ev_draw,0);
        var _pixel=surface_getpixel_ext(_surface,view_width div 2,view_height div 2);
        array_push(_rows,{key:"actual-natural-native-SnowFlake-draw",calls:120,total_us:get_timer()-_start,probe:_pixel});
    } finally {
        if(surface_get_target()==_surface) surface_reset_target();
        if(_target>=0 && surface_get_target()!=_target) surface_set_target(_target);
        if(_camera>=0) camera_destroy(_camera);if(surface_exists(_surface)) surface_free(_surface);
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);matrix_set(matrix_projection,_projection);
        gpu_pop_state();if(_shader<0) shader_reset();else shader_set(_shader);
        draw_set_color(_color);draw_set_alpha(_alpha);
    }
    return _rows;
}
function scrFRBlizzardLiveTestsStep(_driver) {
    var _state=_driver.fr_blizzard_live;
    if(_state.phase==9) {
        var _file=file_text_open_write(working_directory+"ntuf-blizzard-live.json");
        file_text_write_string(_file,json_stringify({physical_device_tested:false,rows:_state.rows}));file_text_close(_file);
        return true;
    }
    if(_state.phase==-1) {scrFREventTestsGenerate(_driver);_state.phase=0;return false;}
    if(instance_exists(GenCont) || instance_exists(FloorMaker) || !instance_exists(Player)) return false;
    if(!scrFRReadyTick()) return false;
    GameCont.is_level_ended=true;
    with(Player) {hp=100000;max_hp=100000;nexthurt=current_frame+100000;speed=0;}
    if(_state.phase==0) {
        if(++_state.ticks<360) return false;
        scrFRBlizzardLiveInstrument(_driver);_state.sampling=true;_state.ticks=0;_state.phase=1;
        _state.wall_start=get_timer();_state.logic_start=FRWorld.logic_serial;_state.frame_start=current_frame;
        _state.flakes_max=0;_state.flakes_visible_max=0;_state.flakes_overlap_max=0;_state.flakes_area_max=0;
        return false;
    }
    var _flake=scrFRBlizzardLiveFlakes();
    _state.flakes_max=max(_state.flakes_max,_flake.total);_state.flakes_visible_max=max(_state.flakes_visible_max,_flake.visible);
    _state.flakes_overlap_max=max(_state.flakes_overlap_max,_flake.conservative_grid_overlap);
    _state.flakes_area_max=max(_state.flakes_area_max,_flake.clipped_sheet_view_areas);
    if(++_state.ticks<120) return false;
    _state.sampling=false;
    var _final_bindings=[];
    with(FRBinding) if(array_contains(_state.event_controllers,creator))
        array_push(_final_bindings,{id:id,kind:fr_binding_kind,depth:depth,
            profiled:variable_instance_exists(id,"fr_weather_original_draw")});
    var _seconds=(get_timer()-_state.wall_start)/1000000,_row={scene:_state.cases[_state.index],
        wall_seconds:_seconds,simulation_seconds:(current_frame-_state.frame_start)/30,
        logical_ticks:FRWorld.logic_serial-_state.logic_start,profile:_state.profile,
        binding_manifest:_state.binding_manifest,final_binding_manifest:_final_bindings,
        active_event_count:array_length(scrFRModCallArray("mod","libEvents","event_get_active",[all])),
        flakes_max:_state.flakes_max,visible_max:_state.flakes_visible_max,
        conservative_grid_overlap_max:_state.flakes_overlap_max,clipped_sheet_view_areas_max:_state.flakes_area_max,
        final_flakes:_flake,viewport:[view_width,view_height],camera:[view_xview,view_yview],
        application_surface:surface_exists(application_surface)?[surface_get_width(application_surface),surface_get_height(application_surface)]:[],
        room:[room_width,room_height],instances:instance_count,walls:instance_number(Wall),floors:instance_number(Floor),
        gpu_components:scrFRBlizzardLiveGpu(_driver)};
    assert(_row.logical_ticks==120 && abs(_row.simulation_seconds-4)<.04,
        "Real Blizzard sampling lost native source logical ticks");
    array_push(_state.rows,_row);scrNTTESmokeLog("NTUF BLIZZARD LIVE RESULT "+json_stringify(_row));
    scrFRBlizzardLiveTestsNext(_driver);return false;
}
