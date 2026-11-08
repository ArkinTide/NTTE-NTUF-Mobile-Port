// A Heart appends real floor and Wall geometry, then its source decoration
// randomly expands Top/TopTiny beyond that edge. Compact exterior collision
// is intentionally plain: it must not turn those decorative caps into more
// apparent walls. Retain one transition tile beside an authored wall only.
function scrFROrbWallMergeOccludes(_new,_old) {
    // The source merge runs after the old map is reactivated. Its plain
    // collision collar is not authored wall art and must not suppress an
    // appended transition cap. Real walls/floors retain their native priority.
    if(_old.object_index==NTTESolidWall && instance_is(_new,TopSmall)) return false;
    var _touch=false;
    with(_new) _touch=place_meeting(x,y,_old);
    return _touch;
}

function scrFROrbWallTopHasEdge(_top,_near) {
    // Reuse one native spatial-query list for this orb. Do not enumerate all
    // old-map walls again for every new cap in a high-loop room.
    ds_list_clear(_near);
    collision_rectangle_list(_top.x-16,_top.y-16,_top.x+31,_top.y+31,Wall,false,false,_near,false);
    for(var _i=0;_i<ds_list_size(_near);++_i) {
        var _wall=_near[|_i];
        if(instance_exists(_wall) && _wall.solid && _wall.object_index!=NTTESolidWall) return true;
    }
    return false;
}

function scrFROrbWallPruneTops(_generation) {
    var _tops=scrNTTEFullCrystalHeartNewInstances(TopSmall,_generation),_removed=0;
    if(!array_length(_tops)) return 0;
    var _near=ds_list_create();
    try {
        for(var _i=0;_i<array_length(_tops);++_i) {
            var _top=_tops[_i];
            if(!instance_exists(_top) || scrFROrbWallTopHasEdge(_top,_near)) continue;
            // TopTiny's cleanup restores any pending neighbour masks. This
            // removes this orb's decoration, never walls or old caps.
            instance_destroy(_top,false);_removed+=1;
        }
    } finally {ds_list_destroy(_near);}
    return _removed;
}
