function scrFRReticle213Tests() {
    var _driver=id,_old_color=UberCont.opt_color,_old_toggle=UberCont.opt_ntte_reticlecolor,
        _old_saved=UberCont.saveData[? "visual_ntte_reticlecolor"],
        _old_saved_color=UberCont.saveData[? "options_color"],
        _before=scrNTTEFullInstances(all),_surface=-1,_camera=-1,_target=false,
        _world=matrix_get(matrix_world),_view=matrix_get(matrix_view),_projection=matrix_get(matrix_projection),
        _keyboard=UberCont.opt_keyboard,_gamepad=UberCont.opt_gamepad;
    try {
        ds_map_delete(UberCont.saveData,"visual_ntte_reticlecolor");scrOptionsUpdate();
        assert(UberCont.opt_ntte_reticlecolor,"Crosshair color must default ON");
        var _colors=[c_black,c_white,make_color_rgb(27,109,226)];
        for(var _i=0;_i<array_length(_colors);++_i) {
            save_set_value("options","color",scrFRVisual205ColorHex(_colors[_i]));scrOptionsUpdate();
            assert(scrFRReticle213Color()==_colors[_i] && UberCont.opt_cursorcol==_colors[_i]
                && UberCont.opt_healthcol==_colors[_i],"Explicit color must reach all cursor consumers, including black");
            save_set_value("visual","ntte_reticlecolor",false);scrOptionsUpdate();
            assert(UberCont.opt_cursorcol==c_white && scrFRReticle213Color()==c_white
                && UberCont.opt_healthcol==_colors[_i],"Disabled cursor matching must preserve health color and use white");
            save_set_value("visual","ntte_reticlecolor",true);scrOptionsUpdate();
        }
        save_set_value("options","color",false);scrOptionsUpdate();
        assert(scrFRReticle213Color()==c_white,"Unconfigured crosshair must be white");
        _surface=surface_create(gui_w,gui_h);_camera=camera_create_view(0,0,gui_w,gui_h,0,noone,-1,-1,-1,-1);
        surface_set_target(_surface);_target=true;camera_apply(_camera);
        matrix_set(matrix_world,matrix_build_identity());shader_reset();gpu_set_blendmode(bm_normal);
        var _menu=instance_create(0,0,MenuOptions),_row=undefined,_row_index=-1;
        with(_menu) {scrOptionsMenuChangeCategory(OptionCategory.Game_Color);last_change=current_frame-1000;
            wait=1;mouse_active=false;pointed_item=-1;slider=undefined;slider_change=0;
            mx_last=device_mouse_x_to_gui(0);my_last=device_mouse_y_to_gui(0);}
        with(_menu) event_perform(ev_draw,ev_gui);
        for(var _i=0;_i<array_length(_menu.items);++_i)
            if((_menu.items[_i][$ "key"]??"")=="visual_ntte_reticlecolor") {_row=_menu.items[_i];_row_index=_i;}
        assert(is_struct(_row) && _row.available && _row.value,"Color category must contain enabled default switch");
        UberCont.opt_keyboard=true;UberCont.opt_gamepad=false;
        _driver.fr_followup210_keyboard={held:-1,pressed:vk_enter,released:-1};
        with(_menu) {wait=0;pointed_item=_row_index;mouse_active=false;}
        with(_menu) event_perform(ev_draw,ev_gui);
        assert(!_row.value && !UberCont.opt_ntte_reticlecolor && UberCont.opt_cursorcol==c_white,"Actual color menu confirmation failed");
        _driver.fr_followup210_keyboard=undefined;
        draw_clear_alpha(c_black,1);with(_menu) event_perform(ev_draw,ev_gui);
        surface_save(_surface,working_directory+"frontier-reticle213-color-settings.png");
        scrNTTESmokeLog("PASS reticle213 default, black/RGB persistence, OFF white and actual color menu confirmation");
    } finally {
        _driver.fr_followup210_keyboard=undefined;
        if(_target) surface_reset_target();
        if(surface_exists(_surface)) surface_free(_surface);if(_camera>=0) camera_destroy(_camera);
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        if(is_undefined(_old_saved)) ds_map_delete(UberCont.saveData,"visual_ntte_reticlecolor");
        else UberCont.saveData[? "visual_ntte_reticlecolor"]=_old_saved;
        if(is_undefined(_old_saved_color)) ds_map_delete(UberCont.saveData,"options_color");
        else UberCont.saveData[? "options_color"]=_old_saved_color;
        scrOptionsUpdate();UberCont.opt_color=_old_color;UberCont.opt_ntte_reticlecolor=_old_toggle;
        UberCont.opt_keyboard=_keyboard;UberCont.opt_gamepad=_gamepad;
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);matrix_set(matrix_projection,_projection);
    }
}
