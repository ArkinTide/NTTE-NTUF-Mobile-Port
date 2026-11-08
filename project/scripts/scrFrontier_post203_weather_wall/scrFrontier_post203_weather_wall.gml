// The authored outer Blizzard mask is a solid white rectangle with a square
// opening. Rasterizing it separately from the 500px inner mask can expose one
// native pixel at their join on a wide mobile viewport. Keep that opening
// underneath the inner mask's opaque border and draw only the visible solid
// portion. This also avoids sampling a 1920x1080 texture for a flat colour.
function scrFRBlizzardOuterMask(_x,_y,_scale,_color) {
    var _left=view_xview-2,_top=view_yview-2,
        _right=view_xview+view_width+2,_bottom=view_yview+view_height+2,
        _radius=max(0,250*_scale-2),
        _a=clamp(_x-_radius,_left,_right),_b=clamp(_y-_radius,_top,_bottom),
        _c=clamp(_x+_radius,_left,_right),_d=clamp(_y+_radius,_top,_bottom),
        _alpha=draw_get_alpha();
    draw_set_alpha(1);
    if(_top<_b) draw_rectangle_color(_left,_top,_right,_b,_color,_color,_color,_color,false);
    if(_d<_bottom) draw_rectangle_color(_left,_d,_right,_bottom,_color,_color,_color,_color,false);
    if(_b<_d) {
        if(_left<_a) draw_rectangle_color(_left,_b,_a,_d,_color,_color,_color,_color,false);
        if(_c<_right) draw_rectangle_color(_c,_b,_right,_d,_color,_color,_color,_color,false);
    }
    draw_set_alpha(_alpha);
}

// A chamber copies the existing top/sliding-door artwork after construction.
// Its body and outer edge must come from the chamber's explicit area as well,
// rather than Wall.Create's campfire fallback during a live Menu context.
function scrFRChamberWallStyle(_wall,_area) {
    if(!instance_exists(_wall)) return;
    _wall.area=_area;
    _wall.sprite_index=scrNTTEFullAreaWallSprite(_area,"Bot");
    _wall.outspr=scrNTTEFullAreaWallSprite(_area,"Out");
    if(_area==area_labs) _wall.sprite_index=scrNTTERefSprite("Wall6BotTrans");
}
