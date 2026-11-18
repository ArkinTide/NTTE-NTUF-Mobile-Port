function scrFRMenus214OwnedChoices(_owner) {
    var _all=scrFRBluescreenUITestsButtons(),_owned=[];
    for(var _i=0;_i<array_length(_all);++_i)
        if(_all[_i].creator==_owner && !_all[_i].done) array_push(_owned,_all[_i]);
    return _owned;
}

function scrFRMenus214MatrixEqual(_a,_b) {
    for(var _i=0;_i<16;++_i) if(abs(_a[_i]-_b[_i])>.000001) return false;
    return true;
}

function scrFRMenus214ChoicePixels(_surface,_choices) {
    var _pixels=[];
    for(var _i=0;_i<array_length(_choices);++_i) {
        var _b=_choices[_i],_sx=_b.image_xscale*gui_w/view_width,
            _sy=_b.image_yscale*gui_h/view_height,
            _x=(_b.x-view_xview)*gui_w/view_width-sprite_get_xoffset(_b.sprite_index)*_sx,
            _y=(_b.y-view_yview)*gui_h/view_height-sprite_get_yoffset(_b.sprite_index)*_sy;
        for(var _py=ceil(_y);_py<min(gui_h,_y+sprite_get_height(_b.sprite_index)*_sy);_py+=3)
            for(var _px=ceil(_x);_px<min(gui_w,_x+sprite_get_width(_b.sprite_index)*_sx);_px+=3)
                array_push(_pixels,surface_getpixel(_surface,max(0,_px),max(0,_py)));
    }
    return _pixels;
}

// Native GPU pixels, real authored timer/factories/draw binding and menu
// callbacks. Android physical-device resume is intentionally not claimed.
function scrFRMenus214Tests() {
    var _before=scrNTTEFullInstances(all),_draw=scrNTTEFullCoastDrawState(),
        _font=draw_get_font(),_ha=draw_get_halign(),_va=draw_get_valign(),
        _language=global.language_current,_small=global.language_font_default,
        _big=global.language_font_bigname_default,_vw=view_width,_vh=view_height,
        _vx=view_xview,_vy=view_yview,_gw=gui_w,_gh=gui_h,_paused=UberCont.paused,
        _mobile=is_mobile,_rate=game_get_speed(gamespeed_fps),_scale=global.time_scale,
        _source=global.fr_source_scale_override,_render=global.fr_render_context,
        _totals=UberCont.ctot_time,_rows=[],_checks=0,_surface=-1,_camera=-1,_target=false,
        _parked=scrFRMatching(FRCustomObject,"name","fr_bluescreenController");
    for(var _p=0;_p<array_length(_parked);++_p) instance_deactivate_object(_parked[_p]);
    gpu_push_state();
    try {
        UberCont.paused=false;is_mobile=true;
        global.fr_source_scale_override=undefined;global.fr_render_context=false;
        var _views=[[424,240,848,480],[280,160,840,480]];
        for(var _hz=30;_hz<=60;_hz+=30) for(var _v=0;_v<array_length(_views);++_v) {
            game_set_speed(_hz,gamespeed_fps);global.time_scale=30/_hz;
            view_width=_views[_v][0];view_height=_views[_v][1];
            view_xview=500137.25;view_yview=499851.5;
            display_set_gui_size(_views[_v][2],_views[_v][3]);
            _surface=surface_create(gui_w,gui_h);
            _camera=camera_create_view(0,0,gui_w,gui_h,0,noone,-1,-1,-1,-1);
            assert(surface_exists(_surface),"Robot214 GUI surface unavailable");
            var _controller=fr_Areas_cyberspace_area_gml_BluescreenController_create(10016,10016);
            with(_controller) {blueTime=100;blueChecks=3;scrFRBluescreen214EnsureChoices();}
            assert(array_length(scrFRMenus214OwnedChoices(_controller))==0,
                "Robot214 repaired choices before the authored prompt threshold");
            with(_controller) {blueTime=114;blueChecks=3;barHeight=-36;
                scrFRInvoke(id,on_step,[]);}
            var _choices=scrFRMenus214OwnedChoices(_controller);
            assert(array_length(_choices)==2,"Robot214 natural timer did not create YES and NO");
            var _kept=_choices[1];instance_destroy(_choices[0]);
            with(_controller) scrFRInvoke(id,on_step,[]);
            _choices=scrFRMenus214OwnedChoices(_controller);
            assert(array_length(_choices)==2 && instance_exists(_kept),
                "Robot214 did not recover a missing child while preserving the other choice");
            for(var _repeat=0;_repeat<4;++_repeat) with(_controller) scrFRBluescreen214EnsureChoices();
            assert(array_length(scrFRMenus214OwnedChoices(_controller))==2,"Robot214 duplicated live choices");
            surface_set_target(_surface);_target=true;camera_apply(_camera);
            matrix_set(matrix_world,matrix_build_identity());shader_reset();gpu_set_blendmode(bm_normal);
            draw_clear_alpha(c_black,1);
            // Independent, unmodified212 reference under a native GUI
            // camera. Do not use the214 wrapper to produce its own oracle.
            scrFRBluescreen212DrawGui();
            var _reference=scrFRMenus214ChoicePixels(_surface,_choices);
            assert(array_length(_reference)>20,"Robot214 choices have no visible screen rectangle");
            var _poison_world=matrix_build(971,-752,0,0,0,23,2,3,1),
                _poison_view=matrix_build(-500000,-500000,0,0,0,17,1,1,1),
                _poison_proj=matrix_build_projection_ortho(123,77,0,32000);
            matrix_set(matrix_world,_poison_world);matrix_set(matrix_view,_poison_view);
            matrix_set(matrix_projection,_poison_proj);draw_clear_alpha(c_black,1);
            // Negative control: the previous GUI path retains world-camera
            // matrices and cannot put the real choice sprites on screen.
            scrFRBluescreen212DrawGui();
            var _old=scrFRMenus214ChoicePixels(_surface,_choices),_old_diff=0;
            for(var _i=0;_i<array_length(_reference);++_i) if(_reference[_i]!=_old[_i]) _old_diff++;
            assert(_old_diff>10,"Robot214 matrix regression negative control did not reproduce");
            draw_clear_alpha(c_black,1);with(UberCont) event_perform(ev_draw,75);
            var _fixed=scrFRMenus214ChoicePixels(_surface,_choices),_diff=0;
            for(var _i=0;_i<array_length(_reference);++_i) if(_reference[_i]!=_fixed[_i]) _diff++;
            assert(_diff==0,"Robot214 choices changed pixels after a stale world view/projection");
            assert(scrFRMenus214MatrixEqual(matrix_get(matrix_world),_poison_world)
                && scrFRMenus214MatrixEqual(matrix_get(matrix_view),_poison_view)
                && scrFRMenus214MatrixEqual(matrix_get(matrix_projection),_poison_proj),
                "Robot214 GUI leaked its screen matrices into the caller");
            surface_reset_target();_target=false;
            surface_save(_surface,working_directory+"ntuf214-robot-"+string(_hz)+"-"+string(_v)+".png");
            surface_free(_surface);_surface=-1;camera_destroy(_camera);_camera=-1;
            assert(scrFRBluescreen214CommitChoice(_controller),"Robot214 rejected a live first choice");
            assert(!scrFRBluescreen214CommitChoice(_controller),"Robot214 accepted a duplicate decision");
            for(var _i=0;_i<array_length(_choices);++_i) instance_destroy(_choices[_i]);
            with(_controller) scrFRBluescreen214EnsureChoices();
            assert(array_length(scrFRMenus214OwnedChoices(_controller))==0,
                "Robot214 revived buttons after the player committed a choice");
            instance_destroy(_controller);
            array_push(_rows,{kind:"robot",hz:_hz,view:_views[_v],samples:array_length(_reference),
                old_matrix_pixel_errors:_old_diff,fixed_matrix_pixel_errors:_diff,missing_child_recovered:true});
            _checks+=9;
        }
        var _languages=["Simplified Chinese","English"],
            _skills=["SurgerySlot","SurgerySlot2","SurgerySlot3","SurgerySlot4"];
        for(var _li=0;_li<2;++_li) for(var _v=0;_v<2;++_v) {
            scrLanguageSet(_languages[_li]);view_width=_views[_v][0];view_height=_views[_v][1];
            view_xview=500000;view_yview=499800;display_set_gui_size(view_width,view_height);
            _surface=surface_create(view_width,view_height);
            _camera=camera_create_view(view_xview,view_yview,view_width,view_height,0,noone,-1,-1,-1,-1);
            for(var _si=0;_si<5;++_si) {
                var _name=_si<4?scrFRModCall("skill",_skills[_si],"skill_name"):"WARBORN NEURONS",
                    _text=_si<4?scrFRModCall("skill",_skills[_si],"skill_text"):
                        "@sGAIN @(color:2964142)25% PROJECTILE SPEED#@sLOSE @(color:2964142)30% RELOAD SPEED",
                    _layout=scrFRSurgery214Layout(view_xview+4,view_yview+view_height-8,_name,_text);
                assert(_layout.body_y>=_layout.title_y+_layout.title_h+6,
                    "Surgery214 translated description overlaps the title");
                assert(_layout.x-_layout.width/2>=view_xview+7.9
                    && _layout.x+_layout.width/2<=view_xview+view_width-7.9
                    && _layout.top>=view_yview+7.9
                    && _layout.top+_layout.height<=view_yview+view_height-7.9,
                    "Surgery214 measured text exceeds the camera");
                surface_set_target(_surface);_target=true;camera_apply(_camera);
                shader_reset();gpu_set_blendmode(bm_normal);matrix_set(matrix_world,matrix_build_identity());
                draw_clear_alpha(make_color_rgb(20,24,35),1);
                draw_set_font(fntSmall);draw_set_halign(fa_right);draw_set_valign(fa_bottom);
                draw_set_color(c_red);draw_set_alpha(.35);
                var _binding=scrFRBindDraw(fr_Objects_Frontier_Objects_mod_gml_BetaSurgeryStation_text,
                    -1000,view_xview+4,view_yview+view_height-8,_name,_text,noone);
                with(_binding) scrFRBindingDraw();
                assert(draw_get_font()==fntSmall && draw_get_halign()==fa_right
                    && draw_get_valign()==fa_bottom && draw_get_color()==c_red && abs(draw_get_alpha()-.35)<.001,
                    "Surgery214 authored text callback leaked its draw state");
                assert(_binding.fr_binding_expire_serial>=0,"Surgery214 lost disposable binding cleanup");
                var _bright=0,_left=ceil(_layout.x-_layout.width/2-view_xview),
                    _top=ceil(_layout.top-view_yview),
                    _right=floor(_layout.x+_layout.width/2-view_xview),
                    _bottom=floor(_layout.top+_layout.height-view_yview);
                for(var _py=_top;_py<_bottom;_py+=3) for(var _px=_left;_px<_right;_px+=3) {
                    var _pixel=surface_getpixel(_surface,_px,_py);
                    if(color_get_red(_pixel)>100 || color_get_green(_pixel)>100) _bright++;
                }
                assert(_bright>15,"Surgery214 has measured bounds without visible text glyphs");
                var _body_lines=string_split(_layout.body,"\n"),_ink=[],_last_ink=-1;
                for(var _line=0;_line<array_length(_body_lines);++_line) {
                    var _first=-1,_last=-1,_start=ceil(_layout.body_y-view_yview+_line*_layout.body_step);
                    for(var _py=_start;_py<min(view_height,_start+_layout.body_step);++_py)
                        for(var _px=_left;_px<_right;++_px) {
                            var _pixel=surface_getpixel(_surface,_px,_py);
                            if(color_get_red(_pixel)>100 || color_get_green(_pixel)>100) {
                                if(_first<0) _first=_py;_last=_py;
                            }
                        }
                    assert(_first>=0 && (_last_ink<0 || _first>_last_ink+1),
                        "Surgery214 adjacent rendered text lines have no visible blank leading");
                    array_push(_ink,[_first,_last]);_last_ink=_last;
                }
                surface_reset_target();_target=false;
                surface_save(_surface,working_directory+"ntuf214-surgery-"+string(_li)+"-"+string(_v)+"-"+string(_si)+".png");
                instance_destroy(_binding);
                array_push(_rows,{kind:"surgery",language:_languages[_li],view:_views[_v],
                    slot:_si,layout:_layout,glyph_samples:_bright,line_ink:_ink});_checks+=5;
            }
            surface_free(_surface);_surface=-1;camera_destroy(_camera);_camera=-1;
        }
        display_set_gui_size(640,480);view_width=640;view_height=480;
        for(var _li=0;_li<2;++_li) {
            scrLanguageSet(_languages[_li]);
            for(var _i=0;_i<array_length(UberCont.ctot_time);++_i) UberCont.ctot_time[_i]=max(1,UberCont.ctot_time[_i]);
            var _menu=instance_create(0,0,MenuOptions),_options=_menu.options[OptionCategory.Controls_Preferences],_found=0;
            _surface=surface_create(gui_w,gui_h);
            _camera=camera_create_view(0,0,gui_w,gui_h,0,noone,-1,-1,-1,-1);
            surface_set_target(_surface);_target=true;camera_apply(_camera);
            matrix_set(matrix_world,matrix_build_identity());shader_reset();draw_clear_alpha(c_black,1);
            with(_menu) {
                scrOptionsMenuChangeCategory(OptionCategory.Controls_Preferences,false);
                last_change=current_frame-100;
                for(var _ri=0;_ri<array_length(items);++_ri) items[_ri].anim=0;
                event_perform(ev_draw,64);
            }
            var _menu_pixels=0;
            for(var _py=60;_py<gui_h-24;_py+=3) for(var _px=100;_px<gui_w-100;_px+=3) {
                var _pixel=surface_getpixel(_surface,_px,_py);
                if(color_get_red(_pixel)>60 || color_get_green(_pixel)>60 || color_get_blue(_pixel)>60) _menu_pixels++;
            }
            assert(_menu_pixels>100,"Preference214 actual menu screenshot has no rendered preference rows");
            for(var _i=0;_i<array_length(_options);++_i) {
                var _option=_options[_i];
                if(_option.key!="cprefs_parrot" && _option.key!="cprefs_bubbles") continue;
                var _name=method_execute(_option.get_name,_option),
                    _layout=scrFRPreference214Layout(100,100,_name,_option),
                    _prefix=render_parse_text("@(sprMapIcon,0,0,-10) ").width;
                assert(is_struct(_layout) && abs(_layout.text_x-(100+_prefix))<.001,
                    "Preference214 text column differs from the native character rows");
                assert(_layout.text_x+_layout.text_width<=_layout.value_x-7.9
                    && _layout.text_scale>0 && _layout.text_scale<=1,
                    "Preference214 label crosses the native ON/OFF value column");
                array_push(_rows,{kind:"preference",language:_languages[_li],key:_option.key,layout:_layout,menu_pixels:_menu_pixels});
                _found++;_checks++;
            }
            assert(_found==2,"Preference214 screenshot omitted Parrot or Bubbles");
            surface_reset_target();_target=false;
            surface_save(_surface,working_directory+"ntuf214-preferences-"+string(_li)+".png");
            surface_free(_surface);_surface=-1;camera_destroy(_camera);_camera=-1;
            instance_destroy(_menu,false);UberCont.paused=false;
        }
        var _file=file_text_open_write(working_directory+"ntuf214-menus.json");
        file_text_write_string(_file,json_stringify({passed:true,checks:_checks,cases:_rows,physical_android_tested:false}));
        file_text_close(_file);
        scrNTTESmokeLog("PASS NTUF214 measured Surgery CJK/English, native preference columns and Robot missing-child/poisoned-camera GPU regression "+string(_checks));
    } finally {
        if(_target) surface_reset_target();
        if(_surface>=0 && surface_exists(_surface)) surface_free(_surface);
        if(_camera>=0) camera_destroy(_camera);
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        for(var _p=0;_p<array_length(_parked);++_p) instance_activate_object(_parked[_p]);
        global.language_current=_language;global.language_font_default=_small;global.language_font_bigname_default=_big;
        view_width=_vw;view_height=_vh;view_xview=_vx;view_yview=_vy;display_set_gui_size(_gw,_gh);
        UberCont.paused=_paused;UberCont.ctot_time=_totals;is_mobile=_mobile;
        game_set_speed(_rate,gamespeed_fps);global.time_scale=_scale;
        global.fr_source_scale_override=_source;global.fr_render_context=_render;
        gpu_pop_state();matrix_set(matrix_world,_draw.world);matrix_set(matrix_view,_draw.view);matrix_set(matrix_projection,_draw.projection);
        if(_draw.shader>=0) shader_set(_draw.shader);else shader_reset();
        draw_set_font(_font);draw_set_halign(_ha);draw_set_valign(_va);draw_set_color(_draw.color);draw_set_alpha(_draw.alpha);
    }
}
