function scrFRRedTerrain210Tests() {
    var _state=scrNTTEFullWorldEventsNaturalWorldCapture(),_rows=[];
    try {
        scrFRWallFixTestsReset(_state);GameCont.area=206;GameCont.subarea=1;
        var _x=627000,_y=627000,_floor=instance_create(_x,_y+16,Floor),
            _wall=instance_create(_x,_y,Wall);
        with(_wall) {mcr_wall_update_lrwh;}
        var _clip=[_wall.l,_wall.r,_wall.w,_wall.h];
        scrNTTESolidWallBlock(_x-64,_y-64,64,128);
        scrNTTESolidWallBlock(_x+16,_y-64,64,80);
        scrNTTESolidWallBlock(_x,_y-64,16,64);
        scrNTTEFullWallUpdate(_x,_y,_x,_y);
        assert(json_stringify(_clip)==json_stringify([_wall.l,_wall.r,_wall.w,_wall.h]),
            "Mutable wall update clipped art against physical exterior fill");
        scrNTTEFullFloorWalls(_floor);scrNTTEFullFloorWalls(_floor);
        var _seen={};with(Wall) {
            if(object_index!=Wall) continue;
            var _key=string(x)+":"+string(y);
            assert(!variable_struct_exists(_seen,_key),"Floor mutation stacked duplicate wall cells");_seen[$ _key]=true;
        }
        scrNTTEFullWallUpdate(_x-16,_y-16,_x+64,_y+64);
        scrNTTEFullWallUpdate(_x-16,_y-16,_x+64,_y+64);
        _seen={};with(TopSmall) {
            var _key=string(x)+":"+string(y);
            assert(!variable_struct_exists(_seen,_key),"Mutable terrain stacked transition cells");_seen[$ _key]=true;
        }
        var _seeds=[1,9,91];
        for(var _i=0;_i<array_length(_seeds);++_i) {
            var _player=scrFRRedConnectivity204Generate(_state,_seeds[_i]);
            scrFRRedConnectivity204AssertBoundaries(global.fr_red204_boundaries);
            var _walls=0,_tops=0;_seen={};
            with(Wall) if(object_index==Wall) {
                var _key=string(x)+":"+string(y);
                // Source random rock props can share an existing edge; this
                // assertion covers the appended hidden corridor's builders.
                if(!position_meeting(x+8,y+8,Floor)) {
                    assert(!variable_struct_exists(_seen,_key),"Generated corridor duplicated a boundary");
                    _seen[$ _key]=true;
                }
                _walls++;
            }
            with(TopSmall) {
                assert(!position_meeting(x,y,Floor) && !scrNTTESolidWallPlanPoint(x,y),
                    "Generated cap-only transition covered a walkable floor");_tops++;
            }
            var _graph=scrFRRedConnectivity204Map(_player);
            assert(_graph.components==1,"Red ordinary and hidden-room road graph became disconnected");
            array_push(_rows,{seed:_seeds[_i],walls:_walls,transitions:_tops,boundaries:global.fr_red204_boundaries});
            scrNTTESmokeLog("NTUF210 red terrain seed="+string(_seeds[_i])+" walls="+string(_walls));
        }
        scrNTTESmokeLog("PASS NTUF210 mutable wall clips, unique cells and generated red secret-road boundaries");
    } finally {global.fr_red204_active=false;scrNTTEFullWorldEventsNaturalWorldRestore(_state);}
}
