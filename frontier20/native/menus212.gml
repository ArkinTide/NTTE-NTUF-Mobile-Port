// Robot's reboot is a screen UI. Its source actors keep the decision and
// deferred cleanup lifecycle; one GUI-End pass owns the actual picture.
function scrFRBluescreen212Actor(_actor) {
    return instance_exists(_actor) && _actor.object_index==FRCustomObject
        && ((_actor[$ "name"]??"")=="fr_bluescreenController"
            || (_actor[$ "fr_bluescreenbutton"]??false));
}

function scrFRBluescreen212Layout() {
    var _scale=min(1,max(1,view_width-16)/320,max(1,view_height-16)/200);
    return {cx:view_xview+view_width/2,cy:view_yview+view_height/2,scale:_scale,
        gx:gui_w/2,gy:gui_h/2,sx:_scale*gui_w/max(1,view_width),
        sy:_scale*gui_h/max(1,view_height)};
}

function scrFRBluescreen212Align() {
    if(!instance_exists(id)) return;
    var _layout=scrFRBluescreen212Layout(),_owner=id;
    x=_layout.cx;y=_layout.cy;
    var _buttons=scrFRMatching(FRCustomObject,"fr_bluescreenbutton",true);
    for(var _i=0;_i<array_length(_buttons);++_i) with(_buttons[_i]) {
        if(creator!=_owner) continue;
        x=_layout.cx+(yesButton?-87:-16)*_layout.scale;
        y=_layout.cy+51*_layout.scale;
        image_xscale=_layout.scale;image_yscale=_layout.scale;
    }
}

function scrFRBluescreen212ButtonStep() {
    if(!instance_exists(creator) || done || creator.drawConnect) return;
    with(creator) scrFRBluescreen212Align();
    // Explicit scaled offsets keep the visible GUI artwork and raw touch
    // rectangle equal on short viewports. The generic libButton path uses
    // the unscaled source sprite offsets.
    var _left=x-sprite_get_xoffset(sprite_index)*image_xscale,
        _top=y-sprite_get_yoffset(sprite_index)*image_yscale,
        _width=sprite_get_width(sprite_index)*image_xscale,
        _height=sprite_get_height(sprite_index)*image_yscale;
    clickIndex=fr_dependencies_libMenu_mod_gml_menubutton_check(_left,_top,_width,_height,0);
    hoverIndex=fr_dependencies_libMenu_mod_gml_menubutton_check(_left,_top,_width,_height,2);
    holdIndex=fr_dependencies_libMenu_mod_gml_menubutton_check(_left,_top,_width,_height,1);
    if(clickIndex!=-1) scrFRScriptCall(clickScr,clickIndex,scrFRSelf(self));
    if(instance_exists(id) && hoverIndex!=-1) scrFRScriptCall(hoverScr,hoverIndex,scrFRSelf(self));
}

function scrFRBluescreen212DrawGui() {
    if(!scrFREnabled() || room!=romGame || UberCont.paused || instance_exists(MenuOptions)) return;
    var _controllers=scrFRMatching(FRCustomObject,"name","fr_bluescreenController");
    if(array_length(_controllers)==0) return;
    var _draw=scrNTTEFullCoastDrawState(),_font=draw_get_font(),_ha=draw_get_halign(),
        _va=draw_get_valign(),_vars=global.fr_module_vars[$ "area:cyberspace"];
    gpu_push_state();
    try {
        shader_reset();gpu_set_fog(false,0,0,0);gpu_set_ztestenable(false);
        gpu_set_zwriteenable(false);gpu_set_colorwriteenable(true,true,true,true);
        gpu_set_blendmode(bm_normal);gpu_set_texfilter(false);
        matrix_set(matrix_world,matrix_build_identity());
        draw_set_color(c_white);draw_set_alpha(1);
        for(var _ci=0;_ci<array_length(_controllers);++_ci) with(_controllers[_ci]) {
            if(!visible) continue;
            scrFRBluescreen212Align();
            var _layout=scrFRBluescreen212Layout(),_sx=_layout.sx,_sy=_layout.sy,
                _cx=_layout.gx,_cy=_layout.gy;
            draw_sprite_stretched(_vars.sprBluescreenBackgroundExt,0,0,0,gui_w,gui_h);
            draw_sprite_ext(_vars.sprBluescreenBackground,0,_cx,_cy,_sx,_sy,0,c_white,1);
            if(drawDots) draw_sprite_ext(_vars.sprBluescreenBackgroundSearch,
                scrFRSourceFrame()*.2,_cx+106*_sx,_cy-2*_sy,_sx,_sy,0,c_white,1);
            draw_sprite_stretched(_vars.sprBluescreenBackgroundBar,0,_cx-160*_sx,
                _cy-barHeight*_sy,320*_sx,200*_sy);
            if(drawConnect) {
                draw_sprite_ext(_vars.sprBluescreenBackgroundReboot,0,_cx,_cy,_sx,_sy,0,c_white,1);
                draw_sprite_ext(_vars.sprBluescreenBackgroundSearch,scrFRSourceFrame()*.2,
                    _cx+81*_sx,_cy+2*_sy,_sx,_sy,0,c_white,1);
            }
            fr_blue212_gui_draws=(self[$ "fr_blue212_gui_draws"]??0)+1;
            if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))
                scrFRBluescreenUITestsObserve("draw");
            var _owner=id,_buttons=scrFRMatching(FRCustomObject,"fr_bluescreenbutton",true);
            for(var _bi=0;_bi<array_length(_buttons);++_bi) with(_buttons[_bi]) {
                if(creator!=_owner || done || !visible || _owner.drawConnect) continue;
                var _dx=(x-view_xview)*gui_w/max(1,view_width),
                    _dy=(y-view_yview)*gui_h/max(1,view_height);
                draw_sprite_ext(sprite_index,image_index,_dx,_dy,_sx,_sy,0,c_white,1);
                fr_blue212_gui_draws=(self[$ "fr_blue212_gui_draws"]??0)+1;
                if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))
                    scrFRBluescreenUITestsObserve("draw");
            }
        }
    } finally {
        gpu_pop_state();matrix_set(matrix_world,_draw.world);matrix_set(matrix_view,_draw.view);
        matrix_set(matrix_projection,_draw.projection);
        if(_draw.shader>=0) shader_set(_draw.shader);else shader_reset();
        draw_set_font(_font);draw_set_halign(_ha);draw_set_valign(_va);
        draw_set_color(_draw.color);draw_set_alpha(_draw.alpha);
    }
}

// Rich text keeps inline colours and sprite tokens intact while CJK can wrap
// at each glyph. All dimensions below come from the font actually rendered.
function scrFRAugment212Wrap(_text,_width) {
    static _cache={};static _count=0;
    var _key=font_get_name(draw_get_font())+":"+string(_width)+":"+_text;
    if(!is_undefined(_cache[$ _key])) return _cache[$ _key];
    var _out="",_line="";
    for(var _at=1;_at<=string_length(_text);++_at) {
        var _end=scrFRLocalizationTokenEnd(_text,_at),_unit=string_char_at(_text,_at);
        if(_end>0) {_unit=string_copy(_text,_at,_end-_at+1);_at=_end;}
        if(_unit=="\n") {_out+=_line+"\n";_line="";continue;}
        if(render_parse_text(_line+_unit).width>_width && render_parse_text(_line).width>0) {
            _out+=_line+"\n";_line="";
            if(_unit==" ") continue;
        }
        _line+=_unit;
    }
    _out+=_line;
    if(_count>=256) {_cache={};_count=0;}
    _cache[$ _key]=_out;_count++;return _out;
}

function scrFRAugment212Layout(_x,_y,_name,_description,_oldSkill) {
    var _font=draw_get_font(),_cjk=scrNTTEFullIsSimplifiedChinese(),
        _title=scrFROptionText(_name,"",false),_body=scrFROptionText(_description,"",false),
        _replace=scrFRLocalize("REPLACES"),_width=min(280,max(64,view_width-24)),
        _title_scale=_cjk?.9:1,_body_scale=_cjk?.8:1,_replace_scale=_cjk?.8:1;
    draw_set_font(_cjk?fntCJK:fntM1);
    _title=scrFRAugment212Wrap(_title,_width/_title_scale);
    var _title_info=render_parse_text(_title),_title_h=ceil(_title_info.height*_title_scale);
    draw_set_font(_cjk?fntCJK:fntSmall);
    _body=scrFRAugment212Wrap(_body,_width/_body_scale);
    var _body_info=render_parse_text(_body),_body_h=ceil(_body_info.height*_body_scale);
    draw_set_font(_cjk?fntCJK:fntM1);
    var _replace_info=render_parse_text(_replace),_icon=fr_dependencies_libMuts_mod_gml_skill_get_icon(_oldSkill),
        _icon_w=sprite_exists(_icon[0])?sprite_get_width(_icon[0]):16,
        _icon_h=sprite_exists(_icon[0])?sprite_get_height(_icon[0]):16,
        _replace_h=max(ceil(_replace_info.height*_replace_scale),_icon_h),
        _replace_w=ceil(_replace_info.width*_replace_scale)+6+_icon_w,
        _panel_w=ceil(max(_title_info.width*_title_scale,_body_info.width*_body_scale,_replace_w))+16,
        _panel_h=_title_h+4+_body_h+7+_replace_h+16,
        _cx=clamp(_x,view_xview+8+_panel_w/2,view_xview+view_width-8-_panel_w/2),
        _bottom=min(_y-45,view_yview+view_height-8),
        _top=max(view_yview+8,_bottom-_panel_h);
    draw_set_font(_font);
    return {x:_cx,top:_top,width:_panel_w,height:_panel_h,title:_title,body:_body,
        replace:_replace,icon:_icon,title_y:_top+8,body_y:_top+8+_title_h+4,
        replace_y:_top+8+_title_h+4+_body_h+7,title_h:_title_h,body_h:_body_h,
        replace_h:_replace_h,replace_w:_replace_w,icon_w:_icon_w,icon_h:_icon_h,
        title_scale:_title_scale,body_scale:_body_scale,replace_scale:_replace_scale,cjk:_cjk};
}

function scrFRAugment212Draw(_x,_y,_name,_description,_oldSkill) {
    var _font=draw_get_font(),_ha=draw_get_halign(),_va=draw_get_valign(),
        _color=draw_get_color(),_alpha=draw_get_alpha(),
        _layout=scrFRAugment212Layout(_x,_y,_name,_description,_oldSkill);
    try {
        var _bg=global.fr_module_vars[$ "mod:Frontier_IDPD"].sprAugmentTextBackground;
        draw_sprite_ext(_bg,2,_layout.x,_layout.top+_layout.height/2,
            _layout.width/sprite_get_width(_bg),_layout.height/sprite_get_height(_bg),0,c_white,.55);
        draw_set_color(c_white);draw_set_alpha(1);draw_set_halign(fa_center);draw_set_valign(fa_top);
        draw_set_font(_layout.cjk?fntCJK:fntM1);
        scrFRDrawText(_layout.x,_layout.title_y,_layout.title,_layout.title_scale);
        draw_set_font(_layout.cjk?fntCJK:fntSmall);
        scrFRDrawText(_layout.x,_layout.body_y,_layout.body,_layout.body_scale);
        draw_set_font(_layout.cjk?fntCJK:fntM1);draw_set_halign(fa_left);
        var _left=_layout.x-_layout.replace_w/2,
            _icon_x=_left+_layout.replace_w-_layout.icon_w;
        scrFRDrawText(_left,_layout.replace_y+(_layout.replace_h-
            render_parse_text(_layout.replace).height*_layout.replace_scale)/2,
            _layout.replace,_layout.replace_scale);
        var _spr=_layout.icon[0];
        if(sprite_exists(_spr)) draw_sprite_ext(_spr,_layout.icon[1],
            _icon_x+sprite_get_xoffset(_spr),_layout.replace_y+(_layout.replace_h-_layout.icon_h)/2+
                sprite_get_yoffset(_spr),1,1,0,c_white,1);
    } finally {
        draw_set_font(_font);draw_set_halign(_ha);draw_set_valign(_va);
        draw_set_color(_color);draw_set_alpha(_alpha);
    }
    return _layout;
}
