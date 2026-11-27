function scrStickRegions(touch) {
	// A second finger must never recenter a stick during an active drag.
	if index >= 0 or global.console_active or !scrFRTouchPressed(touch) or !scrFRTouchHeld(touch)
		exit
	
	var mx = scrFRTouchX(touch),
		my = scrFRTouchY(touch)
	
	if mx > gui_w / 2 {
		if object_index == JoystickMove
			exit
	}
	else if object_index == JoystickAttack
		exit
	
	var border = 20
	
	if mx < border or mx > gui_w - border
		exit
	
	var _owned = false
	with MobileUI {
		if index == touch {
			_owned = true
			break
		}
	}
	if _owned exit
	
	var _nearest = instance_nearest(mx, my, MobileUI)
	with (_nearest) {
		if distance_to_point(mx, my) <= get_touch_radius(rad)
			_owned = true
	}
	if _owned exit
	
	if object_index == JoystickAttack {
		x = lerp(x, mx, 0.8)
		y = lerp(y, my, 0.8)
	}
	else {
		x = mx
		y = my
		// Claim the new floating move stick before another new finger can
		// relocate it in this same hardware frame.
		index = touch
	}
}
