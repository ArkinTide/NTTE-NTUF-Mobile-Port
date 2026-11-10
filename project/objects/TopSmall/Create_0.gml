if (scrNTTESolidWallPlanPoint(x, y) /* FRONTIER PACKED CAP LAYOUT */ || position_meeting(x, y, Floor)) {
    instance_destroy()
    exit
}

// FRONTIER210 UNIQUE TRANSITION CELL
var _tx=x,_ty=y,_tid=real(id),_duplicate=false;
with(TopSmall) if(x==_tx && y==_ty && real(id)<_tid) {_duplicate=true;break;}
if(_duplicate) {instance_destroy(id,false);exit;}

var _area;

if (!instance_exists(MenuGen) && !instance_exists(Menu)) {
    _area = GameCont.area
}
else {
	_area = area_campfire
}

sprite_index = scrNTTEFullAreaWallSprite(_area,"Trans")

image_index = irandom(image_number)
image_speed = 0
// NTTE Coast source terrain origin/filter
area=_area; scrNTTEFullCoastConstructUnwall();
scrNTTEFullRedWallShineEnsure();
