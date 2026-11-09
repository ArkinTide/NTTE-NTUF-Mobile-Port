creator=noone; sprite_index=sprBloodLust; image_speed=0.4*timescale; depth=-4

// BEGIN FRONTIER BLOODLUST205 READONLY PROC
if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))
    scrFRBloodlust205TestsProc();
// END FRONTIER BLOODLUST205 READONLY PROC
