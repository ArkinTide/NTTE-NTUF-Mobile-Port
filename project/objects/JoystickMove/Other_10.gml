event_inherited()

if instance_exists(MenuOptions) or UberCont.opt_keyboard or UberCont.opt_gamepad
	exit

// FRONTIER214 MOVE: validated capture, center deadzone and logical-time ramp.
scrFRMovementStick214();
