// Explicit silent desktop acceptance. Real mobile GPU hardware is not tested.
function scrFRVisual205TestsDrawState(_expected,_where) {
    assert(surface_get_target()==_expected.target && shader_current()==_expected.shader
        && draw_get_color()==_expected.color && draw_get_alpha()==_expected.alpha,
        "Visual205 leaked render target/shader/draw state: "+_where);
    var _actual=[matrix_get(matrix_world),matrix_get(matrix_view),matrix_get(matrix_projection)],
        _saved=[_expected.world,_expected.view,_expected.projection];
    for(var _m=0;_m<3;++_m) for(var _i=0;_i<16;++_i)
        // GML's global comparison epsilon treats zero and1e-5 as equal;
        // strict '<1e-5' can therefore reject two identical matrices.
        assert(abs(_actual[_m][_i]-_saved[_m][_i])<=0.00001,
            "Visual205 leaked camera matrix: "+_where+" matrix="+string(_m)+" element="+string(_i)
            +" expected="+string(_saved[_m][_i])+" actual="+string(_actual[_m][_i])
            +" all_expected="+json_stringify(_saved)+" all_actual="+json_stringify(_actual));
}
function scrFRVisual205TestsMenuRow(_menu,_field,_value) {
    var _rows=_menu.options[OptionCategory.Video],_found=undefined,_count=0;
    for(var _i=0;_i<array_length(_rows);++_i)
        if((_rows[_i][$ _field]??undefined)==_value) {_found=_rows[_i];_count++;}
    assert(_count==1,"Visual205 video row absent or duplicated: "+_field+"="+string(_value));
    return _found;
}
function scrFRVisual205TestsUI(_menu,_screen) {
    var _player=scrFRVisual205TestsMenuRow(_menu,"fr_visual205_option","outline:players"),
        _pet=scrFRVisual205TestsMenuRow(_menu,"fr_visual205_option","outline:pets"),
        _color=scrFRVisual205TestsMenuRow(_menu,"fr_visual205_color",true),
        _rows=[_player,_pet],_keys=["outline:players","outline:pets"];
    with(_menu) {
        scrOptionsMenuChangeCategory(OptionCategory.Video);
        for(var _i=0;_i<2;++_i) for(var _value=0;_value<3;++_value) {
            scrNTTEFullOptionSet(_keys[_i],_value);
            method_execute(_rows[_i].awake,_rows[_i]);
            assert(_rows[_i].value==_value,"Video outline row lost saved source preference");
            method_execute(_rows[_i].click,_rows[_i]);
            assert(scrNTTEFullOptionRaw(_keys[_i])==(_value+1) mod 3,
                "Video outline row did not change actual source preference");
        }
        method_execute(_color.click,_color);
        assert(category==OptionCategory.Game_Color && ds_stack_top(category_stack)==OptionCategory.Video,
            "Video color button did not preserve its native return category");
        event_perform(ev_keypress,vk_backspace);
        assert(category==OptionCategory.Video,"Back from Video color picker escaped to another menu");
        scrOptionsMenuChangeCategory(OptionCategory.Game_Profile);
        scrOptionsMenuChangeCategory(OptionCategory.Game_Color);
        event_perform(ev_keypress,vk_backspace);
        assert(category==OptionCategory.Game_Profile,"Existing Profile color picker lost its native return category");
    }
    var _local=scr_playerinstance_find(global.index),_remote=noone,_slot=-1,_old_slot=undefined;
    for(var _i=0;_i<array_length(global.playerinstance_list);++_i)
        if(is_undefined(global.playerinstance_list[_i])) {_slot=_i;break;}
    assert(_slot>=0,"Visual205 isolated multiplayer color fixture lacks free slot");
    _old_slot=global.playerinstance_list[_slot];
    _remote=new PlayerInstance(_slot);_remote.color=c_blue;global.playerinstance_list[_slot]=_remote;
    try {
        var _colors=[c_black,make_color_rgb(237,75,142),c_lime];
        for(var _i=0;_i<array_length(_colors);++_i) {
            var _chosen=_colors[_i];
            with(_menu) colorpicker_update_options(_chosen);
            assert(scrFRVisual205ColorConfigured() && is_numeric(global.player_color)
                && _local.color==_chosen && UberCont.opt_healthcol==_chosen
                && scrFRVisual205OwnerColor(global.index)==_chosen
                && scrNTTEFullOutlineOwnerColor(global.index)==_chosen
                && scrFRVisual205HealthColor(instance_find(Player,0),c_white)==_chosen,
                "Video RGB/HEX color did not synchronize local body/Pet/HUD, including black: "+json_stringify({
                    chosen:_chosen,saved:UberCont.opt_color,global_color:global.player_color,local_color:_local.color,
                    health:UberCont.opt_healthcol,owner:scrFRVisual205OwnerColor(global.index),
                    pet:scrNTTEFullOutlineOwnerColor(global.index),hud:scrFRVisual205HealthColor(instance_find(Player,0),c_white)}));
            assert(_remote.color==c_blue && scrFRVisual205OwnerColor(_slot)==c_blue,
                "Changing local outline color overwrote another player's color");
            assert(string_length(UberCont.opt_color)==6,"Color picker failed six-digit black/low-value HEX persistence");
            scrOptionsUpdate();
            assert(global.player_color==_chosen && _local.color==_chosen && UberCont.opt_healthcol==_chosen,
                "Re-reading saved options lost local outline/HUD color");
        }
    } finally {global.playerinstance_list[_slot]=_old_slot;}
    // Real native options drawing with the original scroll/appearance logic.
    with(_menu) {
        scrOptionsMenuChangeCategory(OptionCategory.Video);last_change=current_frame-100;
        wait=true;mouse_active=false;pointed_item=-1;slider=undefined;slider_change=0;
        mx_last=device_mouse_x_to_gui(0);my_last=device_mouse_y_to_gui(0);
    }
    draw_clear_alpha(make_color_rgb(28,28,36),1);
    with(_menu) event_perform(ev_draw,ev_gui);
    // Run the native scroll measurement first, then capture the appended rows.
    with(_menu) {scroll=scroll_max;scroll_speed=0;}
    draw_clear_alpha(make_color_rgb(28,28,36),1);
    with(_menu) event_perform(ev_draw,ev_gui);
    assert(surface_get_target()==_screen,"Video options drawing lost its outer screenshot target");
    surface_save(_screen,working_directory+"frontier-visual205-video-settings.png");
    with(_menu) method_execute(_color.click,_color);
    with(_menu) {last_change=current_frame-100;wait=true;mouse_active=false;pointed_item=-1;}
    draw_clear_alpha(make_color_rgb(28,28,36),1);
    with(_menu) event_perform(ev_draw,ev_gui);
    assert(surface_get_target()==_screen,"Native color picker lost its outer screenshot target");
    surface_save(_screen,working_directory+"frontier-visual205-color-picker.png");
    with(_menu) event_perform(ev_keypress,vk_backspace);
    scrNTTESmokeLog("PASS FRONTIER visual205 real Video settings ON/OFF/AUTO, RGB/HEX black+pink+green persistence, local body/Pet/HUD color and remote color preservation, native Video/Profile color back navigation and Draw GUI screenshots");
}
function scrFRVisual205TestsOutline(_p) {
    var _screen=-1,_nested=-1,_seed_surface=-1,_sprite=-1,_camera=-1,_target=false,
        _reference=undefined,_pixelbuffer=-1,
        _before=scrNTTEFullCoastDrawState(),_player=scrNTTEFullAreaGeneratorSnapshot(_p),
        _view=[view_xview,view_yview,view_width,view_height],_old_lockstep=lockstep_stop,
        _old_sprite=_p.sprite_index;
    gpu_push_state();
    try {
        _screen=surface_create(64,64);_nested=surface_create(64,64);_seed_surface=surface_create(7,7);
        _camera=camera_create_view(0,0,7,7,0,noone,-1,-1,-1,-1);
        surface_set_target(_seed_surface);_target=true;camera_apply(_camera);
        matrix_set(matrix_world,matrix_build_identity());shader_reset();gpu_set_blendmode(bm_normal);
        draw_clear_alpha(c_black,0);draw_set_alpha(1);draw_set_color(c_black);draw_rectangle(2,2,4,4,false);
        _sprite=sprite_create_from_surface(_seed_surface,0,0,7,7,false,false,3,3);
        surface_reset_target();_target=false;
        assert(sprite_exists(_sprite),"Visual205 actual black-art sprite creation failed");
        view_xview=0;view_yview=0;view_width=64;view_height=64;
        camera_set_view_size(_camera,64,64);
        _p.x=32;_p.y=32;_p.sprite_index=_sprite;_p.image_index=0;_p.right=1;
        _p.angle=0;_p.image_angle=0;_p.wep=0;_p.bwep=0;_p.extra_weps=[];_p.max_extra_weps=0;
        _p.fainted=false;_p.race=Race.Fish;_p.infammo=false;_p.back=false;
        _p.ntte_pet=[];_p.swapanim=0;
        lockstep_stop=false;
        var _background=make_color_rgb(12,30,70),_tint=make_color_rgb(237,75,142),
            _owner=scr_playerinstance_find(_p.index);
        _owner.color=_tint;UberCont.opt_color=scrFRVisual205ColorHex(_tint);global.player_color=_tint;
        scrNTTEFullOptionSet("outline:players",1);
        for(var _pass=0;_pass<2;++_pass) {
            surface_set_target(_screen);_target=true;camera_apply(_camera);matrix_set(matrix_world,matrix_build_identity());
            if(_pass==1) surface_set_target(_nested);
            var _active=_pass==1?_nested:_screen;
            draw_clear_alpha(_background,1);draw_set_color(c_white);draw_set_alpha(1);shader_reset();
            var _state=scrNTTEFullCoastDrawState();
            with(_p) scrFRVisual205PlayerOutline(sprite_index,0,x,y,right,1,0);
            scrFRVisual205TestsDrawState(_state,"outline nested="+string(_pass));
            assert(surface_getpixel(_active,30,32)==_tint && surface_getpixel(_active,34,32)==_tint
                && surface_getpixel(_active,32,30)==_tint && surface_getpixel(_active,32,34)==_tint
                && surface_getpixel(_active,30,30)==_background && surface_getpixel(_active,4,4)==_background,
                "Player outline lost exact NTT cardinal1px mask over black sprite or changed background");
            // Run the unchanged full native event once: it supplies the body
            // between weapons/status passes, with our border at its real site.
            draw_clear_alpha(_background,1);
            with(_p) event_perform(ev_draw,0);
            assert(surface_getpixel(_active,32,32)==c_black && surface_getpixel(_active,30,32)==_tint,
                "Actual Player.Draw omitted/recolored the body or disconnected its outline consumer");
            assert(surface_get_target()==_active,"Actual Player.Draw consumed its capture target");
            if(_pass==1) {
                surface_save(_active,working_directory+"frontier-visual205-player-outline.png");
                surface_reset_target();assert(surface_get_target()==_screen,"Nested screenshot target stack changed");
            }
            surface_reset_target();_target=false;
        }
        surface_set_target(_screen);_target=true;camera_apply(_camera);matrix_set(matrix_world,matrix_build_identity());
        _pixelbuffer=buffer_create(64*64*4,buffer_fixed,1);
        for(var _shaders=0;_shaders<2;++_shaders) {
            scrNTTEFullOptionSet("shaders",_shaders);
            for(var _mirror=-1;_mirror<=1;_mirror+=2) for(var _angle=0;_angle<=90;_angle+=90) {
                draw_clear_alpha(_background,1);
                with(_p) scrFRVisual205PlayerOutline(sprite_index,0,32,32,_mirror,1,_angle);
                // The engine mirrors/rotates around pixel boundaries, so an
                // odd-sized sprite's occupied pixels are not always centred
                // on the untransformed pixel32. Derive the exact four-neighbour
                // mask from an independent actual native sprite draw instead
                // of assuming that two fixed screen pixels remain occupied.
                _reference=scrFRVisualCapture("native-actor",64,64,0,0,
                    [_sprite,0,32,32,_mirror,1,_angle]);
                assert(_reference.coverage==9,"Visual205 transformed reference omitted the real black-art sprite");
                buffer_get_surface(_pixelbuffer,_screen,0);
                var _different=0,_first=[],_actual_ink=0,_expected_ink=0;
                for(var _py=0;_py<64;++_py) for(var _px=0;_px<64;++_px) {
                    var _mask=false,_neighbours=[[_px-1,_py],[_px+1,_py],[_px,_py-1],[_px,_py+1]];
                    for(var _n=0;_n<4;++_n) {
                        var _nx=_neighbours[_n][0],_ny=_neighbours[_n][1];
                        if(_nx>=0 && _nx<64 && _ny>=0 && _ny<64
                            && buffer_peek(_reference.pixels,4*(_ny*64+_nx)+3,buffer_u8)>0) _mask=true;
                    }
                    var _expected=_mask?_tint:_background,
                        _actual=buffer_peek(_pixelbuffer,4*(_py*64+_px),buffer_u32)&16777215;
                    if(_mask) _expected_ink++;
                    if(_actual==_tint) _actual_ink++;
                    if(_actual!=_expected) {
                        _different++;
                        if(array_length(_first)<8) array_push(_first,{x:_px,y:_py,actual:_actual,expected:_expected});
                    }
                }
                var _diagnostic={shaders:_shaders,mirror:_mirror,angle:_angle,
                    source_bounds:[_reference.left,_reference.top,_reference.right,_reference.bottom],
                    actual_ink:_actual_ink,expected_ink:_expected_ink,different:_different,first:_first};
                scrNTTESmokeLog("VISUAL205 TRANSFORM "+json_stringify(_diagnostic));
                surface_save(_screen,working_directory+"frontier-visual205-outline-s"+string(_shaders)
                    +"-m"+string(_mirror)+"-a"+string(_angle)+".png");
                assert(_different==0,"Mirrored/rotated alpha outline differs from independent native cardinal mask: "+json_stringify(_diagnostic));
                scrFRVisualFree(_reference);_reference=undefined;
            }
        }
        scrNTTEFullOptionSet("outline:players",0);draw_clear_alpha(_background,1);
        with(_p) event_perform(ev_draw,0);
        assert(surface_getpixel(_screen,32,32)==c_black && surface_getpixel(_screen,30,32)==_background,
            "Disabled player outline hid the body or left a visible border");
        scrNTTEFullOptionSet("outline:players",1);lockstep_stop=true;draw_clear_alpha(_background,1);
        with(_p) event_perform(ev_draw,0);
        assert(surface_getpixel(_screen,32,32)==_background && surface_getpixel(_screen,30,32)==_background,
            "Paused Player.Draw rendered through the original lockstep guard");
        lockstep_stop=false;
        var _entry=scrNTTEFullOutlineManager().entries[$ "Player205:"+string(_p.index)];
        assert(surface_get_width(_entry.surf)==7 && surface_get_height(_entry.surf)==7,
            "Player outline allocated a full-screen capture instead of its sprite-sized mask");
        surface_free(_entry.surf);with(_p) scrFRVisual205PlayerOutline(sprite_index,0,32,32,1,1,0);
        assert(surface_exists(_entry.surf),"Player outline did not recover its cache after context loss");
        scrNTTESmokeLog("PASS FRONTIER visual205 actual Player.Draw, black-art cardinal1px sprite-sized alpha outlines, nested screenshot targets, camera/draw state, source shader toggles, mirror/rotation, OFF and pause guards, context-loss recreation");
    } finally {
        if(_target) surface_reset_target();
        scrFRVisualFree(_reference);
        if(buffer_exists(_pixelbuffer)) buffer_delete(_pixelbuffer);
        lockstep_stop=_old_lockstep;
        scrNTTEFullAreaGeneratorRestore(_player);
        _p.sprite_index=_old_sprite;
        view_xview=_view[0];view_yview=_view[1];view_width=_view[2];view_height=_view[3];
        if(_sprite>=0 && sprite_exists(_sprite)) sprite_delete(_sprite);
        var _surfaces=[_screen,_nested,_seed_surface];
        for(var _i=0;_i<3;++_i) if(surface_exists(_surfaces[_i])) surface_free(_surfaces[_i]);
        if(_camera>=0) camera_destroy(_camera);
        gpu_pop_state();matrix_set(matrix_world,_before.world);matrix_set(matrix_view,_before.view);matrix_set(matrix_projection,_before.projection);
        draw_set_color(_before.color);draw_set_alpha(_before.alpha);
        if(_before.shader>=0) shader_set(_before.shader);else shader_reset();
    }
}
function scrFRVisual205Tests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled(),"Visual205 tests need isolated desktop acceptance");
    var _before=scrNTTEFullInstances(all),_progress=global.ntte_full_progress,
        _old_map=UberCont.saveData,_map=ds_map_create(),_uber=scrNTTEFullAreaGeneratorSnapshot(UberCont),
        _local=scr_playerinstance_find(global.index),_old_color=_local.color,_global_color=global.player_color,
        _language=global.language_current[$ "Init:Id"],_font=draw_get_font(),
        _default_font=global.language_font_default,_draw=scrNTTEFullCoastDrawState(),
        _parked=scrNTTEFullInstances([Menu,MenuOptions,BackButton]),_menu=noone,
        _screen=-1,_camera=-1,_target=false;
    ds_map_copy(_map,_old_map);UberCont.saveData=_map;
    global.ntte_full_progress=json_parse(json_stringify(_progress));
    for(var _i=0;_i<array_length(_parked);++_i) instance_deactivate_object(_parked[_i]);
    gpu_push_state();
    try {
        _screen=surface_create(ceil(gui_w),ceil(gui_h));
        _camera=camera_create_view(0,0,gui_w,gui_h,0,noone,-1,-1,-1,-1);
        surface_set_target(_screen);_target=true;camera_apply(_camera);matrix_set(matrix_world,matrix_build_identity());
        shader_reset();gpu_set_blendmode(bm_normal);draw_set_alpha(1);draw_set_color(c_white);
        global.language_current[$ "Init:Id"]="Simplified Chinese";global.language_font_default=fntCJK;draw_set_font(fntCJK);
        _menu=instance_create(0,0,MenuOptions);scrFRVisual205TestsUI(_menu,_screen);
        var _languages=["Simplified Chinese","English"],_sizes=[[320,240],[426,240],[480,270]],_cases=0;
        for(var _lang=0;_lang<2;++_lang) {
            global.language_current[$ "Init:Id"]=_languages[_lang];draw_set_font(_lang==0?fntCJK:fntM1);
            var _text=scrRaceGetSkinUnlockDescription(19,1);
            assert(string_pos("@1(",_text)>0 && string_pos("/",_text)>0
                && (_lang!=0 || (string_pos("交易十种不同武器",_text)>0 && string_pos("TRADE",_text)==0)),
                "Actual Bubbles B-skin hint lost Chinese dynamic progress or original icon slots");
            _text=string_hash_to_newline(_text);
            for(var _size=0;_size<array_length(_sizes);++_size) {
                var _layout=scrFRVisual205UnlockLayout(_text,2,_sizes[_size][0],_sizes[_size][1]);
                assert(_layout.left>=7 && _layout.right<=_sizes[_size][0]-7
                    && _layout.top>=7 && _layout.bottom<=_sizes[_size][1]-7
                    && _layout.height*2<_sizes[_size][1]*0.5,
                    "Bubbles B-skin rich-text tooltip covers screen or escapes native GUI");
                _cases++;
            }
            if(_lang==0) {
                draw_clear_alpha(make_color_rgb(28,28,36),1);
                var _state=scrNTTEFullCoastDrawState();
                scrFRVisual205TestsDrawState(_state,"before unlock tooltip");
                scrFRVisual205UnlockDraw(_text,0);scrFRVisual205TestsDrawState(_state,"unlock tooltip");
                surface_save(_screen,working_directory+"frontier-visual205-bubbles-unlock.png");
            }
        }
        draw_clear_alpha(make_color_rgb(62,62,74),1);
        var _locked=scrNTTEFullCrownLoadoutSprite(17,false),_unlocked=scrNTTEFullCrownLoadoutSprite(17,true);
        draw_sprite(sprLockedLoadoutCrown,1,gui_w/2-48,gui_h/2);
        draw_sprite(_locked[0],_locked[1],gui_w/2,gui_h/2);
        draw_sprite(_unlocked[0],_unlocked[1],gui_w/2+48,gui_h/2);
        assert(surface_getpixel(_screen,gui_w/2-12,gui_h/2-14)==make_color_rgb(62,62,74)
            && surface_getpixel(_screen,gui_w/2,gui_h/2)==make_color_rgb(40,40,40),
            "Locked Storms uses an opaque icon rectangle rather than original transparent crown shape");
        surface_save(_screen,working_directory+"frontier-visual205-locked-storms.png");
        surface_reset_target();_target=false;
        scrFRVisual205TestsOutline(instance_find(Player,0));
        scrNTTESmokeLog("PASS FRONTIER visual205 six real B-skin rich-text locale/GUI bounds, dynamic progress, transparent source Storms silhouette and screenshot evidence; desktop only, mobile hardware not tested");
    } finally {
        if(_target) surface_reset_target();
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        if(surface_exists(_screen)) surface_free(_screen);if(_camera>=0) camera_destroy(_camera);
        global.ntte_full_progress=_progress;global.player_color=_global_color;_local.color=_old_color;
        global.language_current[$ "Init:Id"]=_language;global.language_font_default=_default_font;
        scrNTTEFullAreaGeneratorRestore(_uber);UberCont.saveData=_old_map;ds_map_destroy(_map);
        for(var _i=0;_i<array_length(_parked);++_i) instance_activate_object(_parked[_i]);
        gpu_pop_state();matrix_set(matrix_world,_draw.world);matrix_set(matrix_view,_draw.view);matrix_set(matrix_projection,_draw.projection);
        draw_set_color(_draw.color);draw_set_alpha(_draw.alpha);draw_set_font(_font);
        if(_draw.shader>=0) shader_set(_draw.shader);else shader_reset();
    }
}
