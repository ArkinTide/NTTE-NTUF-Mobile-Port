// Finalize only mutable Red room boundaries, after all appended rooms and
// corridors exist. A former boundary must not survive inside a later floor.
function scrFRRedTerrain210Finish() {
    if(GameCont.area!=206) return;
    var _walls=scrNTTEFullInstances(Wall),_seen={};
    for(var _i=0;_i<array_length(_walls);++_i) {
        var _wall=_walls[_i];
        if(!instance_exists(_wall) || _wall.object_index!=Wall || _wall.area!=206) continue;
        var _key=string(_wall.x)+":"+string(_wall.y),_inside=
            position_meeting(_wall.bbox_left,_wall.bbox_top,Floor)
            && position_meeting(_wall.bbox_right-1,_wall.bbox_top,Floor)
            && position_meeting(_wall.bbox_left,_wall.bbox_bottom-1,Floor)
            && position_meeting(_wall.bbox_right-1,_wall.bbox_bottom-1,Floor);
        if(variable_struct_exists(_seen,_key) || (_inside && !(_wall[$ "fr_red210_rock"]??false))) {
            instance_destroy(_wall,false);continue;
        }
        _seen[$ _key]=true;
    }
    _seen={};
    with(TopSmall) if(area==206) {
        var _key=string(x)+":"+string(y);
        if(variable_struct_exists(_seen,_key) || position_meeting(x,y,Floor) || scrNTTESolidWallPlanPoint(x,y)) {
            instance_destroy(id,false);continue;
        }
        _seen[$ _key]=true;
    }
    // Rebuild art from the final authored boundary. Compact solid exterior
    // remains present for collision and is ignored only by the clip probes.
    for(var _i=0;_i<array_length(_walls);++_i) {
        var _wall=_walls[_i];
        if(instance_exists(_wall) && _wall.object_index==Wall && _wall.area==206)
            scrNTTEFullWallUpdate(_wall.x,_wall.y,_wall.x,_wall.y);
    }
}
