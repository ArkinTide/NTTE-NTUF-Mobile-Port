// NTTE's source setup_topify discovers a newly awakened MeleeFake replacement
// inside its parent's Top search envelope. The native wake event must make
// that same new enemy controller before destroying the dormant prop body.
function scrFRBiomeAwakenOwnTop(_dormant,_awake) {
    if(!instance_exists(_dormant) || !instance_exists(_awake)) return noone;
    var _old=_dormant[$ "ntte_full_top_object"]??noone;
    if(!instance_exists(_old) || _old.object_index!=NTTEFullTopObject
        || _old.target!=_dormant) return noone;
    if(_awake.xstart<_old.search_x1 || _awake.xstart>_old.search_x2
        || _awake.ystart<_old.search_y1 || _awake.ystart>_old.search_y2) return noone;
    var _elevated=false;
    with(_awake) _elevated=place_meeting(x,y,Wall) || !position_meeting(x,y,Floor);
    if(!_elevated) return noone;
    // The old prop's type/saved fields cannot restore an enemy's native
    // alarms, mask and AI. Use TopCreate's own enemy capture and landing.
    return scrNTTEFullTopCreate(_awake.x,_awake.y,_awake,0,0);
}
