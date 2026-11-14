// Native collision entry regression for the reported Slash -> Wall crash.
function scrFRCollision212Tests() {
    var _before=scrNTTEFullInstances(all),
        _old_mode=variable_global_exists("ntte_merge_native_collision_mode") && global.ntte_merge_native_collision_mode,
        _old_stack=variable_global_exists("ntte_merge_native_collision_stack")?global.ntte_merge_native_collision_stack:[],
        _old_frame=current_frame,_scale=timescale,_old_area=GameCont.area;
    try {
        global.ntte_merge_native_collision_mode=true;global.ntte_merge_native_collision_stack=[];
        for(var _rate=30;_rate<=60;_rate+=30) {
            global.time_scale=30/_rate;current_frame+=1;
            // A genuine FloorExplo callback refreshes a wall beside the
            // invisible exterior fill. Its clipping must match the normal
            // authored-art macro while that fill remains solid for gameplay.
            GameCont.area=206;
            var _ax=874000+_rate*16,_ay=874000,
                _art_wall=instance_create(_ax,_ay,Wall),
                _fill=scrNTTESolidWallBlock(_ax-16,_ay,16,16),
                _blast=instance_create(_ax,_ay+32,FloorExplo),
                _actual=[_art_wall.l,_art_wall.r,_art_wall.w,_art_wall.h];
            with(_art_wall) {mcr_wall_update_lrwh;}
            var _expected=[_art_wall.l,_art_wall.r,_art_wall.w,_art_wall.h];
            assert(_actual[0]==0 && _actual[0]==_expected[0] && _actual[1]==_expected[1]
                && _actual[2]==_expected[2] && _actual[3]==_expected[3],
                "Real FloorExplo clipped Red wall artwork against invisible exterior collision");
            assert(instance_exists(_fill) && _fill.solid,
                "Artwork refresh removed the exterior collision instead of ignoring it for clipping");
            scrNTTESmokeLog("PASS NTUF212 FloorExplo authored wall art rate="+string(_rate)
                +" actual="+json_stringify(_actual)+" expected="+json_stringify(_expected));
            var _x=870000,_y=870000,_wall=instance_create(_x,_y,Wall),
                _slash=instance_create(_x-100,_y,Slash),_dead=_wall;
            _slash.team=team_player;_slash.speed=0;_slash.walled=false;_slash.shank=false;
            _slash.xprevious=_slash.x;_slash.yprevious=_slash.y;
            // The actual collision dispatch has a valid `other`, but the
            // predicted overlap is false, as on a restored solid collision.
            // Before 2.1.2 the deleted wall reached Slash's native art code.
            scrNTTEFullMergedProjectileAddEvent(_slash,"wall",function() {
                scrWallDestroy(other.id);return true;
            });
            with(_wall) with(_slash) event_perform(ev_collision,Wall);
            assert(!instance_exists(_wall) && instance_exists(_slash) && !_slash.walled,
                "Deleted wall entered native Slash handler after a non-overlapping merged callback");
            assert(!array_length(global.ntte_merge_native_collision_stack),
                "Destroyed wall callback leaked collision guard state");
            var _entry=scrNTTEFullMergedNativeCollisionBegin(_slash,_dead),
                _point=scrNTTESolidWallContact(_dead,_x+3,_y+7);
            assert(is_struct(_entry) && !_entry.allow && !_entry.stacked,
                "Queued stale native collision was allowed to dereference its deleted pair");
            assert(_point[0]==_x+3 && _point[1]==_y+7,
                "Deleted wall contact broke the caller's contact-array contract");
            var _live=instance_create(_x+64,_y,Wall),_live_slash=instance_create(_x+64,_y,Slash);
            _live_slash.team=team_player;_live_slash.speed=0;_live_slash.walled=false;_live_slash.shank=false;
            _live_slash.xprevious=_live_slash.x;_live_slash.yprevious=_live_slash.y;
            current_frame+=1;
            with(_live) with(_live_slash) event_perform(ev_collision,Wall);
            assert(instance_exists(_live) && _live_slash.walled,
                "Live ordinary wall no longer ran the native Slash contact response");
            scrNTTESmokeLog("PASS NTUF212 native stale wall and live Slash contact rate="+string(_rate));
        }
    } finally {
        var _all=scrNTTEFullInstances(all);
        for(var _i=array_length(_all)-1;_i>=0;--_i)
            if(array_get_index(_before,_all[_i])<0 && instance_exists(_all[_i])) instance_destroy(_all[_i],false);
        global.ntte_merge_native_collision_mode=_old_mode;global.ntte_merge_native_collision_stack=_old_stack;
        current_frame=_old_frame;global.time_scale=_scale;GameCont.area=_old_area;
    }
}
