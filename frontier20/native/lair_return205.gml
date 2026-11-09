// A live player returning into the last 64px of the closing Pizza corridor
// used to enter the persistent-actor salvage array. PizzaRubble then pinned
// that player to rubble.y+16 forever. Preserve the deeper native lethal cave-in
// and item/pet salvage, but release live players onto real clear Lair floor.
function scrFRLairReturn205ReleasePlayer(_player,_edge_x,_edge_y) {
    if(!instance_exists(_player) || !instance_is(_player,Player) || _player.hp<=0) return false;
    var _best=infinity,_goal_x=0,_goal_y=0,
        _from_x=_player.x,_from_y=_player.y;
    with(Floor) {
        var _last_y=min(bbox_bottom-8,_edge_y-24);
        for(var _cy=bbox_top+8;_cy<=_last_y;_cy+=16)
            for(var _cx=bbox_left+8;_cx<=bbox_right-8;_cx+=16) {
                var _distance=point_distance(_from_x,_from_y,_cx,_cy);
                if(_distance>=_best) continue;
                var _clear=false;
                with(_player) _clear=!scrNTTEFullPlayerWallMeeting(_cx,_cy)
                    && !place_meeting(_cx,_cy,InvisiWall);
                if(_clear) {_best=_distance;_goal_x=_cx;_goal_y=_cy;}
            }
    }
    if(_best==infinity) return false;
    with(_player) {
        visible=true;x=_goal_x;y=_goal_y;xprevious=x;yprevious=y;
        speed=0;hspeed=0;vspeed=0;
    }
    return true;
}
function scrFRLairReturn205ReleaseBorderSaved(_border) {
    for(var _i=array_length(_border.ntte_full_cavein_saved)-1;_i>=0;--_i) {
        var _actor=_border.ntte_full_cavein_saved[_i];
        if(scrFRLairReturn205ReleasePlayer(_actor,_border.x,_border.y))
            array_delete(_border.ntte_full_cavein_saved,_i,1);
    }
}
