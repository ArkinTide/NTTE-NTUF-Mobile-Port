// Keep exact native mask tests; prune only objects outside the swept mask.
// Quasar/melee replacements often begin inside their friendly creator. The
// former any-Hitme gate then scanned every hostile at every ray-march point.
function scrFRMergedLaserCandidates213(_enemies,_maximum,_dx,_dy) {
    var _xend=x+_dx*_maximum,_yend=y+_dy*_maximum,
        // Native place_meeting rounds sampled positions. One pixel of padding
        // keeps fractional origins/endpoints conservative without changing hits.
        _left=min(x,_xend)+(bbox_left-x)-1,_right=max(x,_xend)+(bbox_right-x)+1,
        _top=min(y,_yend)+(bbox_top-y)-1,_bottom=max(y,_yend)+(bbox_bottom-y)+1,_out=[];
    for(var _i=0;_i<array_length(_enemies);++_i) {
        var _target=_enemies[_i];
        if(instance_exists(_target)) {
            if(_target!=id && _target.bbox_right>=_left && _target.bbox_left<=_right
                && _target.bbox_bottom>=_top && _target.bbox_top<=_bottom) array_push(_out,_target);
        }
    }
    return _out;
}

function scrFRMergedLaserMeeting213(_enemies) {
    var _self=id,_left=bbox_left,_right=bbox_right,_top=bbox_top,_bottom=bbox_bottom;
    for(var _i=0;_i<array_length(_enemies);++_i) {
        var _target=_enemies[_i];
        if(instance_exists(_target)) {
            if(_target.bbox_right>=_left && _target.bbox_left<=_right
                && _target.bbox_bottom>=_top && _target.bbox_top<=_bottom) {
                with(_target) if(place_meeting(x,y,_self)) return true;
            }
        }
    }
    return false;
}

function scrFRAlarmTopUp213(_add) {
    if(!variable_global_exists("fr_alarm_slots213") || !is_array(global.fr_alarm_slots213)) scrFRAlarmSlotsInit213();
    var _all_slots=global.fr_alarm_slots213,_unknown=[0,1,2,3,4,5,6,7,8,9,10,11];
    with(all) {
        var _slots=object_index<array_length(_all_slots)?_all_slots[object_index]:_unknown;
        // Future objects absent from a generated table retain the old path.
        if(!is_array(_slots)) _slots=_unknown;
        for(var _j=0;_j<array_length(_slots);++_j) {
            var _slot=_slots[_j];
            if(alarm[_slot]>0) alarm[_slot]+=_add;
        }
    }
}

// Ordinary native Spiral has two complementary masks. At the source30Hz,
// image_speed=2 samples frame0 on every draw. A physical60Hz rebase to1
// must not alternate those masks; every other portal sprite keeps animation.
function scrFRSpiralDraw213(_sprite,_frame,_x,_y,_sx,_sy,_angle,_color,_alpha) {
    draw_sprite_ext(_sprite,_sprite==sprSpiral?0:_frame,_x,_y,_sx,_sy,_angle,_color,_alpha);
}
