if lockstep_stop
	exit

// The ceiling trap advances at 30 Hz while native animation runs each frame.
var _descent = self[$ "fr_cave_descent_owner"] ?? noone;
var _body_sprite = sprite_index;
var _body_frame = -1;
if (instance_exists(_descent)) {
	if (_descent.droppingSpider && real(_descent.mySpider) == real(id)) {
		_body_sprite = _descent.spr_spider;
		_body_frame = 0;
	}
}
draw_sprite_ext(_body_sprite, _body_frame, x, y, right, 1, 0, c_white, 1)