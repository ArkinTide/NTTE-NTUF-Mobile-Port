// Surgery generates rich text at runtime. Measure the translated glyphs in
// the same font and scale used by the renderer, including wrapped CJK lines.
function scrFRSurgery214Layout(_x,_y,_name,_description) {
    var _font=draw_get_font(),_cjk=scrNTTEFullIsSimplifiedChinese(),
        _title=scrFROptionText(_name,"",false),_body=scrFROptionText(_description,"",false),
        _width=min(280,max(48,view_width-24)),_available=max(48,view_height-24),
        _title_scale=_cjk?.9:1,_body_scale=_cjk?.8:1,
        _wrapped_title="",_wrapped_body="",_title_info=undefined,_body_info=undefined,
        _title_h=0,_body_h=0,_panel_h=0,_title_step=0,_body_step=0;
    try {
        for(var _pass=0;_pass<4;++_pass) {
            draw_set_font(_cjk?fntCJK:fntM1);
            _wrapped_title=scrFRAugment212Wrap(_title,_width/_title_scale);
            _title_info=render_parse_text(_wrapped_title);
            // font_get_string_height deliberately caps the shared CJK UI
            // metric. Use the runner's independent native font line extent
            // here, plus visible leading, rather than reusing that cap.
            _title_step=ceil(max(string_height(_cjk?"国Ag":"Ag"),
                font_get_string_height(_cjk?"国Ag":"Ag"))*_title_scale)+3;
            _title_h=array_length(string_split(_wrapped_title,"\n"))*_title_step-3;
            draw_set_font(_cjk?fntCJK:fntSmall);
            _wrapped_body=scrFRAugment212Wrap(_body,_width/_body_scale);
            _body_info=render_parse_text(_wrapped_body);
            _body_step=ceil(max(string_height(_cjk?"国Ag":"Ag"),
                font_get_string_height(_cjk?"国Ag":"Ag"))*_body_scale)+3;
            _body_h=array_length(string_split(_wrapped_body,"\n"))*_body_step-3;
            _panel_h=_title_h+6+_body_h+16;
            if(_panel_h<=_available) break;
            var _fit=max(.2,(_available-22)/max(1,_title_h+_body_h));
            _title_scale*=_fit;_body_scale*=_fit;
        }
        var _panel_w=ceil(max(_title_info.width*_title_scale,
                _body_info.width*_body_scale))+16,
            _cx=clamp(_x,view_xview+8+_panel_w/2,view_xview+view_width-8-_panel_w/2),
            _bob=sin(scrFRSourceFrame()*.1),
            _top=clamp(_y-32-_bob-_panel_h,view_yview+8,
                view_yview+view_height-8-_panel_h);
        return {x:_cx,top:_top,width:_panel_w,height:_panel_h,title:_wrapped_title,
            body:_wrapped_body,title_y:_top+8,body_y:_top+8+_title_h+6,
            title_h:_title_h,body_h:_body_h,title_scale:_title_scale,
            body_scale:_body_scale,title_step:_title_step,body_step:_body_step,cjk:_cjk};
    } finally {draw_set_font(_font);}
}

function scrFRSurgery214Draw(_x,_y,_name,_description) {
    var _font=draw_get_font(),_ha=draw_get_halign(),_va=draw_get_valign(),
        _color=draw_get_color(),_alpha=draw_get_alpha(),
        _layout=scrFRSurgery214Layout(_x,_y,_name,_description);
    try {
        draw_set_color(c_black);draw_set_alpha(.6);
        draw_rectangle(_layout.x-_layout.width/2,_layout.top,
            _layout.x+_layout.width/2,_layout.top+_layout.height,false);
        draw_set_color(c_white);draw_set_alpha(1);
        draw_set_halign(fa_center);draw_set_valign(fa_top);
        draw_set_font(_layout.cjk?fntCJK:fntM1);
        var _lines=string_split(_layout.title,"\n");
        for(var _i=0;_i<array_length(_lines);++_i)
            draw_text_nt(_layout.x,_layout.title_y+_i*_layout.title_step,_lines[_i],_layout.title_scale);
        draw_set_font(_layout.cjk?fntCJK:fntSmall);
        _lines=string_split(_layout.body,"\n");
        for(var _i=0;_i<array_length(_lines);++_i)
            draw_text_nt(_layout.x,_layout.body_y+_i*_layout.body_step,_lines[_i],_layout.body_scale);
    } finally {
        draw_set_font(_font);draw_set_halign(_ha);draw_set_valign(_va);
        draw_set_color(_color);draw_set_alpha(_alpha);
    }
    return _layout;
}

// The authored blue-screen timer creates its choices once. A live choice
// screen must recover an individually retired child without repeating the
// timer, sounds, acceptance, or denial. Never revive a committed decision.
function scrFRBluescreen214EnsureChoices() {
    if(blueChecks<4 || blueTime<115 || drawConnect || (self[$ "fr_blue214_decision"]??false)) return;
    var _owner=id,_yes=false,_no=false,
        _buttons=scrFRMatching(FRCustomObject,"fr_bluescreenbutton",true);
    for(var _i=0;_i<array_length(_buttons);++_i) with(_buttons[_i]) {
        if(creator!=_owner || done) continue;
        if(yesButton) _yes=true;else _no=true;
    }
    var _vars=global.fr_module_vars[$ "area:cyberspace"];
    if(!_yes) fr_Areas_cyberspace_area_gml_BluescreenButton_create(
        x-87,y+51,id,_vars.sprBluescreenButtonYes,true);
    if(!_no) fr_Areas_cyberspace_area_gml_BluescreenButton_create(
        x-16,y+51,id,_vars.sprBluescreenButtonNo,false);
    scrFRBluescreen212Align();
}

function scrFRBluescreen214ControllerStep() {
    fr_Areas_cyberspace_area_gml_bluescreen_step();
    if(instance_exists(id)) scrFRBluescreen214EnsureChoices();
}

function scrFRBluescreen214CommitChoice(_owner) {
    if(!instance_exists(_owner)) return false;
    if(_owner.drawConnect || (_owner[$ "fr_blue214_decision"]??false)) return false;
    _owner.fr_blue214_decision=true;
    return true;
}

// GUI-End can follow a mod's world-camera pass or an Android surface resume.
// Establish all three matrices explicitly; GUI coordinates must not inherit
// a world view/projection. Restore the caller's matrices even on early return.
function scrFRBluescreen214DrawGui() {
    static _camera=-1;
    if(!scrFREnabled() || room!=romGame || UberCont.paused || instance_exists(MenuOptions)) return;
    if(array_length(scrFRMatching(FRCustomObject,"name","fr_bluescreenController"))==0) return;
    var _world=matrix_get(matrix_world),_view=matrix_get(matrix_view),
        _projection=matrix_get(matrix_projection);
    try {
        if(_camera<0) _camera=camera_create_view(0,0,gui_w,gui_h,0,noone,-1,-1,-1,-1);
        camera_set_view_pos(_camera,0,0);camera_set_view_size(_camera,gui_w,gui_h);
        matrix_set(matrix_world,matrix_build_identity());
        // Use the runner's own GUI-camera orientation on each graphics
        // backend, including the surface/render-target Y convention.
        matrix_set(matrix_view,camera_get_view_mat(_camera));
        matrix_set(matrix_projection,camera_get_proj_mat(_camera));
        scrFRBluescreen212DrawGui();
    } finally {
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);
        matrix_set(matrix_projection,_projection);
    }
}

// The native rich-text icon prefix advances by the sprite's collision bbox.
// Parrot/Bubbles have smaller map-icon bboxes, which moved both their icons
// and text left. Keep the native prefix's text and icon columns explicitly;
// the standard switch renderer continues to own the value and hit rectangle.
function scrFRPreference214Layout(_x,_y,_name,_option,_scale=1) {
    var _icon=-1;
    if(_option.key=="cprefs_parrot") _icon=scrNTTEFullRaceSprite(NTTEFullRace.Parrot,"Map",0);
    else if(_option.key=="cprefs_bubbles") _icon=scrFRRaceNativeSprite("Map",0,sprMapIcon);
    if(!sprite_exists(_icon)) return undefined;
    var _split=string_pos(") ",_name);
    if(_split<=0) return undefined;
    var _label=string_delete(_name,1,_split+1),
        _prefix="@(sprMapIcon,0,0,-10) ",
        _native_w=sprite_get_bbox_right(sprMapIcon)-sprite_get_bbox_left(sprMapIcon),
        _native_h=sprite_get_bbox_bottom(sprMapIcon)-sprite_get_bbox_top(sprMapIcon),
        _height=render_parse_text(_prefix+_label).height,
        _icon_w=sprite_get_bbox_right(_icon)-sprite_get_bbox_left(_icon),
        _icon_h=sprite_get_bbox_bottom(_icon)-sprite_get_bbox_top(_icon),
        _cx=_x+(_native_w-8)+1-sprite_get_xoffset(sprMapIcon)
            +sprite_get_bbox_left(sprMapIcon)+_native_w/2,
        _cy=_y-_height/2-10+(_native_h-8)+font_get_height_diff()+1
            -sprite_get_yoffset(sprMapIcon)+sprite_get_bbox_top(sprMapIcon)+_native_h/2,
        _text_x=_x+render_parse_text(_prefix).width,_value_x=_x+_option.width/2+60,
        _max_width=max(1,_value_x-8-_text_x),_label_info=render_parse_text(_label),
        _text_scale=min(_scale,_max_width/max(1,_label_info.width));
    return {icon:_icon,label:_label,text_x:_text_x,value_x:_value_x,
        text_y:_y-_height/2+(_label_info.height-_label_info.height*_text_scale)/2,
        text_scale:_text_scale,text_width:_label_info.width*_text_scale,
        max_width:_max_width,icon_cx:_cx,icon_cy:_cy,
        icon_x:_cx+sprite_get_xoffset(_icon)-sprite_get_bbox_left(_icon)-_icon_w/2,
        icon_y:_cy+sprite_get_yoffset(_icon)-sprite_get_bbox_top(_icon)-_icon_h/2};
}

function scrFRPreference214DrawName(_x,_y,_name,_scale,_option) {
    if(category!=OptionCategory.Controls_Preferences) {
        scrNTTEFullDrawMenuText(_x,_y,_name,_scale);return;
    }
    var _layout=scrFRPreference214Layout(_x,_y,_name,_option,_scale);
    if(!is_struct(_layout)) {scrNTTEFullDrawMenuText(_x,_y,_name,_scale);return;}
    var _ha=draw_get_halign(),_va=draw_get_valign(),_color=draw_get_color(),_alpha=draw_get_alpha();
    try {
        draw_set_halign(fa_left);draw_set_valign(fa_top);
        draw_sprite_ext(_layout.icon,0,_layout.icon_x,_layout.icon_y,1,1,0,c_white,_alpha);
        scrNTTEFullDrawMenuText(_layout.text_x,_layout.text_y,_layout.label,_layout.text_scale);
    } finally {
        draw_set_halign(_ha);draw_set_valign(_va);draw_set_color(_color);draw_set_alpha(_alpha);
    }
}
