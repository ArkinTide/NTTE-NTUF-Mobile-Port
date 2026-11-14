// Supplement the scheduled real-death -> raw touch -> portal YES/NO cases.
// This case verifies actual GUI pixels, short views, camera displacement and
// every authored augmentation using the same callbacks as the game.
function scrFRMenus212Tests() {
    var _before=scrNTTEFullInstances(all),_draw=scrNTTEFullCoastDrawState(),
        _font=draw_get_font(),_ha=draw_get_halign(),_va=draw_get_valign(),
        _language=global.language_current,_small=global.language_font_default,
        _big=global.language_font_bigname_default,_vw=view_width,_vh=view_height,
        _vx=view_xview,_vy=view_yview,_gw=gui_w,_gh=gui_h,_paused=UberCont.paused,
        _rows=[],_checks=0,_surface=-1,_camera=-1,_target=false,
        _parked=scrFRMatching(FRCustomObject,"name","fr_bluescreenController");
    for(var _p=0;_p<array_length(_parked);++_p) instance_deactivate_object(_parked[_p]);
    gpu_push_state();
    try {
        UberCont.paused=false;
        var _views=[[424,240,848,480],[640,360,640,360],[320,180,640,360],[280,160,840,480]];
        for(var _v=0;_v<array_length(_views);++_v) {
            view_width=_views[_v][0];view_height=_views[_v][1];
            display_set_gui_size(_views[_v][2],_views[_v][3]);
            view_xview=500012.25+_v*137.5;view_yview=499917.75-_v*64.25;
            _surface=surface_create(gui_w,gui_h);
            _camera=camera_create_view(0,0,gui_w,gui_h,0,noone,-1,-1,-1,-1);
            assert(surface_exists(_surface),"Robot GUI pixel surface unavailable");
            surface_set_target(_surface);_target=true;camera_apply(_camera);
            matrix_set(matrix_world,matrix_build_identity());shader_reset();gpu_set_blendmode(bm_normal);
            draw_clear_alpha(c_black,1);
            var _controller=fr_Areas_cyberspace_area_gml_BluescreenController_create(10016,10016);
            with(_controller) {blueTime=114;blueChecks=3;barHeight=-36;fr_Areas_cyberspace_area_gml_bluescreen_step();}
            var _buttons=scrFRBluescreenUITestsButtons(),_owned=[];
            for(var _i=0;_i<array_length(_buttons);++_i) if(_buttons[_i].creator==_controller) array_push(_owned,_buttons[_i]);
            assert(array_length(_owned)==2,"Robot natural threshold omitted a choice");
            for(var _i=0;_i<2;++_i) _owned[_i].visible=false;
            with(UberCont) event_perform(ev_draw,75);
            var _baseline=[],_rects=[];
            for(var _i=0;_i<2;++_i) {
                var _b=_owned[_i],_sx=_b.image_xscale*gui_w/view_width,_sy=_b.image_yscale*gui_h/view_height,
                    _x=(_b.x-view_xview)*gui_w/view_width-sprite_get_xoffset(_b.sprite_index)*_sx,
                    _y=(_b.y-view_yview)*gui_h/view_height-sprite_get_yoffset(_b.sprite_index)*_sy,
                    _rect=[max(0,ceil(_x)),max(0,ceil(_y)),
                        min(gui_w-1,floor(_x+sprite_get_width(_b.sprite_index)*_sx-1)),
                        min(gui_h-1,floor(_y+sprite_get_height(_b.sprite_index)*_sy-1))],_pixels=[];
                assert(_rect[0]<_rect[2] && _rect[1]<_rect[3],"Robot scaled button is outside GUI");
                for(var _py=_rect[1];_py<=_rect[3];_py+=2) for(var _px=_rect[0];_px<=_rect[2];_px+=2)
                    array_push(_pixels,surface_getpixel(_surface,_px,_py));
                array_push(_baseline,_pixels);array_push(_rects,_rect);_b.visible=true;
            }
            with(UberCont) event_perform(ev_draw,75);
            for(var _i=0;_i<2;++_i) {
                var _rect=_rects[_i],_changed=0,_at=0,_b=_owned[_i];
                for(var _py=_rect[1];_py<=_rect[3];_py+=2) for(var _px=_rect[0];_px<=_rect[2];_px+=2)
                    if(surface_getpixel(_surface,_px,_py)!=_baseline[_i][_at++]) _changed++;
                assert(_changed>6,"Robot GUI-End ran without visible YES/NO pixels");
                assert((_b[$ "fr_blue212_gui_draws"]??0)>0 &&
                    scrFRScriptRef(_b.on_step)==scrFRScriptRef(scrFRBluescreen212ButtonStep),
                    "Robot choice is missing its real GUI drawing or scaled raw-touch Step");
                array_push(_rows,{kind:"robot",view:_views[_v],yes:_b.yesButton,pixel_changes:_changed,
                    world:[_b.x,_b.y],gui_rect:_rect});_checks+=3;
            }
            surface_reset_target();_target=false;
            surface_save(_surface,working_directory+"ntuf212-robot-view-"+string(_v)+".png");
            surface_free(_surface);_surface=-1;camera_destroy(_camera);_camera=-1;
            for(var _i=0;_i<2;++_i) instance_destroy(_owned[_i]);instance_destroy(_controller);
        }

        view_width=424;view_height=240;view_xview=500000;view_yview=499800;display_set_gui_size(424,240);
        _surface=surface_create(view_width,view_height);
        _camera=camera_create_view(view_xview,view_yview,view_width,view_height,0,noone,-1,-1,-1,-1);
        assert(surface_exists(_surface),"IDPD tooltip surface unavailable");
        var _augments=global.fr_module_vars[$ "mod:Frontier_IDPD"].fr_augments_array,
            _languages=["Simplified Chinese","English"];
        for(var _li=0;_li<array_length(_languages);++_li) {
            scrLanguageSet(_languages[_li]);
            var _chosen=0,_longest=-1;
            for(var _ai=0;_ai<array_length(_augments);++_ai) {
                var _skill=_augments[_ai],_name=scrFRModCall("skill",_skill,"skill_name"),
                    _text=scrFRModCall("skill",_skill,"skill_text"),
                    _old=scrFRModCall("skill",_skill,"skill_augment"),
                    _layout=scrFRAugment212Layout(view_xview+8,view_yview+100,_name,_text,_old);
                assert(_layout.body_y>=_layout.title_y+_layout.title_h+4,
                    "IDPD description overlaps its translated name: "+string(_skill));
                assert(_layout.replace_y>=_layout.body_y+_layout.body_h+7,
                    "IDPD replacement row overlaps its translated description: "+string(_skill));
                assert(_layout.x-_layout.width/2>=view_xview+7.9 &&
                    _layout.x+_layout.width/2<=view_xview+view_width-7.9 &&
                    _layout.top>=view_yview+8 && _layout.top+_layout.height<=view_yview+view_height-8,
                    "IDPD measured tooltip exceeds the visible camera: "+string(_skill));
                if(_layout.height>_longest) {_longest=_layout.height;_chosen=_ai;}
                array_push(_rows,{kind:"augment",language:_languages[_li],skill:_skill,layout:_layout});_checks+=3;
            }
            surface_set_target(_surface);_target=true;camera_apply(_camera);
            matrix_set(matrix_world,matrix_build_identity());shader_reset();gpu_set_blendmode(bm_normal);
            draw_clear_alpha(make_color_rgb(20,24,35),1);
            // Use the production authored station callback through its real
            // disposable draw binding, including localized replacement icon.
            var _skill=_augments[_chosen],_binding=scrFRBindDraw(
                fr_Objects_Frontier_IDPD_mod_gml_AugmentStation_text,-1000,
                view_xview+view_width/2,view_yview+230,
                scrFRModCall("skill",_skill,"skill_name"),scrFRModCall("skill",_skill,"skill_text"),
                scrFRModCall("skill",_skill,"skill_augment"));
            with(_binding) scrFRBindingDraw();
            surface_reset_target();_target=false;
            surface_save(_surface,working_directory+"ntuf212-idpd-tooltip-"+string(_li)+".png");
            instance_destroy(_binding);
        }
        var _file=file_text_open_write(working_directory+"ntuf212-menus.json");
        file_text_write_string(_file,json_stringify({passed:true,checks:_checks,cases:_rows,
            physical_device_tested:false}));file_text_close(_file);
        scrNTTESmokeLog("PASS NTUF212 Robot native GUI-End pixels in four viewport/GUI mappings and all IDPD augment layouts "+string(_checks));
    } finally {
        if(_target) surface_reset_target();
        if(_surface>=0 && surface_exists(_surface)) surface_free(_surface);
        if(_camera>=0) camera_destroy(_camera);
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        for(var _p=0;_p<array_length(_parked);++_p) instance_activate_object(_parked[_p]);
        global.language_current=_language;global.language_font_default=_small;global.language_font_bigname_default=_big;
        view_width=_vw;view_height=_vh;view_xview=_vx;view_yview=_vy;display_set_gui_size(_gw,_gh);UberCont.paused=_paused;
        gpu_pop_state();matrix_set(matrix_world,_draw.world);matrix_set(matrix_view,_draw.view);matrix_set(matrix_projection,_draw.projection);
        if(_draw.shader>=0) shader_set(_draw.shader);else shader_reset();
        draw_set_font(_font);draw_set_halign(_ha);draw_set_valign(_va);draw_set_color(_draw.color);draw_set_alpha(_draw.alpha);
    }
}
