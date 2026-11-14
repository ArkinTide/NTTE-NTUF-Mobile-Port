if lockstep_stop
	exit

if active && current_frame_active {
    motion_add_m(direction, accel * timescale, maxspeed)
    instance_create(x, y, Smoke)
}