// The native move stick still supplies the host's original analog magnitude,
// acceleration boost and precise angle. Only its touch lifecycle/timing changes.
function scrFRMovementNearest214(_radius) {
    if(is_undefined(scrFRTouchFixtureSample(0))) return scrFRTouchNearest(_radius);
    // The explicit desktop raw-touch fixture follows the same MobileUI owner
    // and closest-control rules as the shipping get_nearest_touch selector.
    if(global.console_active) return -1;
    var _self=id,_reach=get_touch_radius(_radius);
    for(var _touch=0;_touch<5;++_touch) {
        if(!scrFRTouchHeld(_touch)) continue;
        var _mx=scrFRTouchX(_touch),_my=scrFRTouchY(_touch);
        if(point_distance(x,y,_mx,_my)>_reach) continue;
        var _owned=false;
        with(MobileUI) if(id!=_self && index==_touch) {_owned=true;break;}
        if(_owned || instance_nearest(_mx,_my,MobileUI)!=id) continue;
        return _touch;
    }
    return -1;
}

function scrFRMovementStick214() {
    var _slot=global.index,_dt=timescale;
    if(!is_real(_dt) || !(_dt>=0 && _dt<=4)) _dt=1;
    var _lost=index>=0 && (!scrFRTouchHeld(index) || scrFRTouchReleased(index));
    if(global.console_active || _lost) index=-1;
    // A released/cancelled pointer must stop this hardware frame. A different
    // finger may be acquired on the next frame through normal ownership rules.
    if(index<0 && !_lost && !global.console_active) index=scrFRMovementNearest214(rad);

    KeyCont.moving[_slot]=0;
    KeyCont.hold_east[_slot]=false;KeyCont.hold_west[_slot]=false;
    KeyCont.hold_nort[_slot]=false;KeyCont.hold_sout[_slot]=false;
    if(index>=0) {
        var _dx=scrFRTouchX(index)-x,_dy=scrFRTouchY(index)-y;
        dis=point_distance(0,0,_dx,_dy);
        // At the default32px radius this is exactly2 GUI pixels. Preserve the
        // original dis/rad response outside it, including very slow fine moves.
        var _dead=min(2,max(0,rad)*0.0625);
        if(dis>_dead && rad>0) {
            dir=point_direction(0,0,_dx,_dy);
            if(abs(angle_difference(dir,KeyCont.dir_move[_slot]))<10)
                current_move_direction_time=min(30,max(0,current_move_direction_time)+_dt);
            else current_move_direction_time=max(0,current_move_direction_time-3*_dt);
            var _same=max(0,current_move_direction_time-10)/20;
            KeyCont.dir_move[_slot]=dir;
            KeyCont.moving[_slot]=min(1,_same+dis/rad);
            // Use raw deltas rather than sin/cos signs: cardinal directions
            // must not gain a perpendicular key from floating-point roundoff.
            KeyCont.hold_east[_slot]=_dx>0;KeyCont.hold_west[_slot]=_dx<0;
            KeyCont.hold_sout[_slot]=_dy>0;KeyCont.hold_nort[_slot]=_dy<0;
        } else current_move_direction_time=0;
    } else {
        dis=0;current_move_direction_time=0;
    }
    scrFRTouchMovementSample(_slot,index);
    if(UberCont.opt_hiddensticks)
        image_alpha=lerp(image_alpha,(index>=0)*0.2,1-power(0.6,_dt));
}
