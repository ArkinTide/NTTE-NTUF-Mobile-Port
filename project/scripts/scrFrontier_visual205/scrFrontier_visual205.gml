// Native video options and NTT's four one-pixel body outlines. The existing
// Pet/charm compositor remains the owner of their source draw callbacks.
function scrFRVisual205ColorConfigured() {
    return instance_exists(UberCont) && is_string(UberCont.opt_color)
        && string_length(UberCont.opt_color)>0;
}
function scrFRVisual205ColorSync() {
    if(!instance_exists(UberCont)) return;
    // Zero is a valid explicitly selected black, as well as the host's legacy
    // sentinel for an unset profile. Keep that distinction in the UI/HUD.
    if(scrFRVisual205ColorConfigured()) {
        // The host's base_convert returns a decimal string even when its
        // destination base is ten. Native PI/HUD tint values must be numbers;
        // otherwise the owner-color validity check treats every saved HEX as
        // invalid and black also fails equality against its numeric color.
        global.player_color=real(base_convert(UberCont.opt_color,16,10));
        UberCont.opt_healthcol=global.player_color;
    }
    if(variable_global_exists("playerinstance_list") && is_struct(my_player))
        my_player.color=global.player_color;
}
function scrFRVisual205OwnerColor(_index) {
    var _owner=scr_playerinstance_find(_index);
    if(!is_struct(_owner)) return c_white;
    var _color=_owner.color;
    if(_owner==my_player && _color==0 && !scrFRVisual205ColorConfigured())
        return make_color_rgb(252,56,0);
    return is_numeric(_color) && _color>=0 && _color<=16777215?_color:c_white;
}
function scrFRVisual205HealthColor(_player,_fallback) {
    var _index=scrNTTEFullValue(_player,"index",global.index);
    if(is_struct(my_player) && _index==my_player.index && scrFRVisual205ColorConfigured())
        return global.player_color;
    return _fallback;
}
function scrFRVisual205ColorLabel() {
    return scrFRVisual205ColorConfigured()?"["+string(UberCont.opt_color)+"]":
        scrNTTEUpdateText("DEFAULT","默认");
}
function scrFRVisual205ColorHex(_color) {
    var _hex=base_convert(real(_color),10,16);
    while(string_length(_hex)<6) _hex="0"+_hex;
    return string_upper(_hex);
}
function scrFRVisual205Options() {
    // Reuse the established source settings, including their saved AUTO
    // state; changing these rows also updates NTTE's original option page.
    var _old=option_number;
    scrOptionsMenuCategoryBegin(OptionCategory.Video);
    option_list=options[OptionCategory.Video];
    var _rows=[["PLAYER OUTLINE","角色轮廓","outline:players"],
        ["PET OUTLINE","宠物轮廓","outline:pets"]];
    for(var _i=0;_i<array_length(_rows);++_i) {
        var _row=_rows[_i];
        scrOptionsMenuCreateElement({type:"button",name:scrNTTEUpdateText(_row[0],_row[1]),
            fr_visual205_option:_row[2],value:scrNTTEFullOptionRaw(_row[2]),halign:fa_left,
            awake:function(_opt){_opt.value=scrNTTEFullOptionRaw(_opt.fr_visual205_option);},
            get_value:function(_opt){return _opt.value==2?"AUTO":(_opt.value?OPTION_ON:OPTION_OFF);},
            click:function(_opt){
                _opt.value=(_opt.value+1) mod 3;
                scrNTTEFullOptionSet(_opt.fr_visual205_option,_opt.value);
                return true;
            }});
    }
    scrOptionsMenuCreateElement({type:"button",name:scrNTTEUpdateText("OUTLINE / HEALTH COLOR","轮廓／血条颜色"),
        fr_visual205_color:true,width:300,value:"",halign:fa_left,
        get_value:function(_opt){return scrFRVisual205ColorLabel();},
        click:function(_opt){
            // The native category stack records this Video origin and the
            // same color page still returns to Profile from its old entry.
            option_can_change=false;
            scrOptionsMenuChangeCategory(OptionCategory.Game_Color);
            return true;
        }});
    scrOptionsMenuCategoryEnd();option_number=_old;
}
function scrFRVisual205PlayerOutline(_sprite,_frame,_x,_y,_xs,_ys,_angle) {
    if(lockstep_stop || fainted || !scrNTTEFullOptionGet("outline:players") || !sprite_exists(_sprite)) return false;
    var _w=sprite_get_width(_sprite),_h=sprite_get_height(_sprite),
        _ox=sprite_get_xoffset(_sprite),_oy=sprite_get_yoffset(_sprite),
        _entry=scrNTTEFullOutlineCacheSetup("Player205:"+string(index),_w,_h,1),
        _world=matrix_get(matrix_world),_view=matrix_get(matrix_view),_projection=matrix_get(matrix_projection),
        _color=draw_get_color(),_alpha=draw_get_alpha(),_shader=shader_current(),_target=false;
    if(!surface_exists(_entry.surf)) return false;
    gpu_push_state();
    try {
        shader_reset();gpu_set_texfilter(false);gpu_set_fog(false,0,0,0);
        gpu_set_ztestenable(false);gpu_set_zwriteenable(false);gpu_set_alphatestenable(false);
        gpu_set_colorwriteenable(true,true,true,true);
        surface_set_target(_entry.surf);_target=true;
        var _camera=scrNTTEFullOutlineManager().outline_camera;
        camera_set_view_pos(_camera,0,0);camera_set_view_size(_camera,_w,_h);camera_apply(_camera);
        matrix_set(matrix_world,matrix_build_identity());draw_clear_alpha(c_black,0);
        // Copy the sprite's exact alpha. No Player.Draw replay, full-screen
        // capture, fog tint, source shader or additional body draw is needed.
        gpu_set_blendmode_ext(bm_one,bm_zero);
        draw_sprite_ext(_sprite,_frame,_ox,_oy,1,1,0,c_white,1);
        gpu_set_colorwriteenable(true,true,true,false);
        draw_set_color(scrFRVisual205OwnerColor(index));draw_set_alpha(1);
        draw_rectangle(0,0,_w,_h,false);
        surface_reset_target();_target=false;
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);matrix_set(matrix_projection,_projection);
        gpu_set_colorwriteenable(true,true,true,true);gpu_set_blendmode(bm_normal);
        var _left=_x-lengthdir_x(_ox*_xs,_angle)-lengthdir_x(_oy*_ys,_angle-90),
            _top=_y-lengthdir_y(_ox*_xs,_angle)-lengthdir_y(_oy*_ys,_angle-90);
        for(var _ang=0;_ang<360;_ang+=90)
            draw_surface_ext(_entry.surf,_left+lengthdir_x(1,_ang),_top+lengthdir_y(1,_ang),
                _xs,_ys,_angle,c_white,1);
    } finally {
        if(_target) surface_reset_target();
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);matrix_set(matrix_projection,_projection);
        draw_set_color(_color);draw_set_alpha(_alpha);gpu_pop_state();
        if(_shader>=0) shader_set(_shader);else shader_reset();
    }
    return true;
}
function scrFRVisual205BubblesSkinLock() {
    var _conversions=scrFRModCallArray("mod","libSaves","save_get",["Frontier","pirate_conversions"]),
        _count=is_array(_conversions)?array_length(_conversions):0,
        _icon="@1("+string(scrFRRaceVar("sprCoveIcon"))+":0)";
    return scrNTTEUpdateText("TRADE 10#UNIQUE WEAPONS#","交易十种不同武器#")
        +_icon+"@s(@w"+string(_count)+"@s/@w10@s)"+_icon;
}
function scrFRVisual205UnlockLayout(_message,_pop,_gw=gui_w,_gh=gui_h) {
    var _info=render_parse_text(_message),_pad=8,
        _scale=min(1,max(1,_gw-2*(_pad+8+abs(_pop)))/max(1,_info.width),
            max(1,_gh*0.4-2*_pad)/max(1,_info.height)),
        _width=_info.width*_scale/2+_pad+abs(_pop),
        _height=_info.height*_scale/2+_pad,
        _x=_gw/2,_y=clamp(_gh-30,_height+8,_gh-_height-8);
    return {x:_x,y:_y,width:_width,height:_height,scale:_scale,text:_message,
        left:_x-_width,right:_x+_width,top:_y-_height,bottom:_y+_height};
}
function scrFRVisual205UnlockDraw(_text,_pop) {
    var _world=matrix_get(matrix_world),_view=matrix_get(matrix_view),_projection=matrix_get(matrix_projection),
        _font=draw_get_font(),_ha=draw_get_halign(),_va=draw_get_valign(),
        _color=draw_get_color(),_alpha=draw_get_alpha(),_layout;
    try {
        var _message=string_hash_to_newline(scrFRLocalize(loc(_text)));
        scrFRLocalizationFont(_message);
        _layout=scrFRVisual205UnlockLayout(_message,_pop);
        draw_align(fa_center,fa_middle);draw_set_alpha(1);draw_set_color(c_tooltip);
        draw_roundrect_ext(_layout.left,_layout.top,_layout.right,_layout.bottom,4,4,false);
        draw_set_color(c_white);
        draw_text_nt(_layout.x,_layout.y+_pop,_message,_layout.scale);
    } finally {
        // Native transformed text / inline sprite draws can leave their
        // renderer transform active. The tooltip is an overlay within the
        // caller's GUI target and must preserve that caller's three matrices.
        draw_set_font(_font);draw_align(_ha,_va);draw_set_color(_color);draw_set_alpha(_alpha);
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);matrix_set(matrix_projection,_projection);
    }
    return _layout;
}
