// Red secret-wall artwork is a non-solid Wall child whose proximity helper
// owns its temporary collision. A REAL wall collision must not eject against
// a second visual Fake wall that happens to share the player's mask.
function scrNTTEFullPlayerWallMeeting(_x,_y) {
    var _wall=instance_place(_x,_y,Wall);
    if(_wall==noone) return false;
    if(!instance_is(_wall,NTTEFullWallFake)) return true;

    // Ordinary terrain takes the allocation-free path above. Only a Fake as
    // the first result needs enumeration so a simultaneous real Wall remains
    // blocking. Do not filter by `solid`: other Wall families keep their
    // existing native collision semantics.
    var _walls=ds_list_create();
    try {
        instance_place_list(_x,_y,Wall,_walls,false);
        for(var _i=0;_i<ds_list_size(_walls);++_i)
            if(!instance_is(_walls[|_i],NTTEFullWallFake)) return true;
        return false;
    } finally {ds_list_destroy(_walls);}
}
