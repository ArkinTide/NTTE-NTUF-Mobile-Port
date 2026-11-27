// A captured move finger owns the stick until release. Displacement controls
// walking speed continuously, without accumulating a time-based speed boost.
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
    current_move_direction_time=0;
    KeyCont.hold_east[_slot]=false;KeyCont.hold_west[_slot]=false;
    KeyCont.hold_nort[_slot]=false;KeyCont.hold_sout[_slot]=false;
    if(index>=0) {
        var _dx=scrFRTouchX(index)-x,_dy=scrFRTouchY(index)-y;
        dis=point_distance(0,0,_dx,_dy);
        // At the default32px radius this is exactly 2 GUI pixels. Full speed
        // needs only 7/8 of the radius, leaving room for the thumb at the edge.
        var _dead=min(2,max(0,rad)*0.0625);
        if(dis>_dead && rad>0) {
            dir=point_direction(0,0,_dx,_dy);
            KeyCont.dir_move[_slot]=dir;
            KeyCont.moving[_slot]=clamp((dis-_dead)/max(1,rad*0.875-_dead),0,1);
            // Continuous movement keeps its exact angle. Direction buttons
            // ignore slight perpendicular thumb wobble near a cardinal axis.
            var _axis_dead=dis*0.12;
            KeyCont.hold_east[_slot]=_dx>_axis_dead;KeyCont.hold_west[_slot]=_dx<-_axis_dead;
            KeyCont.hold_sout[_slot]=_dy>_axis_dead;KeyCont.hold_nort[_slot]=_dy<-_axis_dead;
        }
    } else dis=0;
    scrFRTouchMovementSample(_slot,index);
    if(UberCont.opt_hiddensticks)
        image_alpha=lerp(image_alpha,(index>=0)*0.2,1-power(0.6,_dt));
}

// The native Player step uses this only for precise touchscreen walking.
// Aim toward a stable fraction of actual terrain-limited speed. Including
// existing friction in the target lets small thumb movements remain usable.
// Approach a velocity vector rather than adding thrust in the new direction
// until the total speed happens to be below the cap.
function scrFRMovementTouchWalk216(_walk_cap,_acceleration) {
    if(!KeyCont.touch[index] || !KeyCont.precisemovement[index]) return false;
    if(_walk_cap<=0 || _acceleration<=0 || speed>_walk_cap) return true;

    var _strength=clamp(KeyCont.moving[index],0,1);
    if(_strength<=0) return true;
    var _target=lerp(min(friction,_walk_cap),_walk_cap,_strength);
    var _vx=lengthdir_x(_target,KeyCont.dir_move[index]);
    var _vy=lengthdir_y(_target,KeyCont.dir_move[index]);
    var _dx=_vx-hspeed,_dy=_vy-vspeed;
    var _distance=point_distance(0,0,_dx,_dy);
    var _step=_acceleration*timescale;
    if(_distance>_step) {
        var _fraction=_step/_distance;
        hspeed+=_dx*_fraction;
        vspeed+=_dy*_fraction;
    } else {
        hspeed=_vx;
        vspeed=_vy;
    }
    return true;
}
