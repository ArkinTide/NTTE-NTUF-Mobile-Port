// Edge artwork follows the source's empty exterior even though that exterior
// now has compact physical collision. Other solid scenery keeps its semantics.
function scrFRWallArtFree205(_x,_y) {
    // Packed rectangles have no edge artwork of their own. Their refresh
    // must not allocate collision lists during bulk terrain updates.
    if(object_index==NTTESolidWall) return false;
    if(!place_meeting(_x,_y,NTTESolidWall)) return place_free(_x,_y);
    var _near=ds_list_create();
    try {
        instance_place_list(_x,_y,all,_near,false);
        for(var _i=0;_i<ds_list_size(_near);++_i) {
            var _v=_near[|_i];
            if(_v!=id && _v.object_index!=NTTESolidWall && _v.solid) return false;
        }
        return true;
    } finally {ds_list_destroy(_near);}
}
