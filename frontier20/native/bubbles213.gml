// Manual aiming emits a semi-automatic weapon's press on finger release.
// A return through the dead zone must retain a previously valid Bubbles
// gesture until that release. Dragging beyond three radii still cancels it.
function scrFRBubblesManualRelease213(_pointer,_mx,_my,_dis,_dir,_pressed,_held,_released) {
    var _player=scrFRBubblesPlayer205(global.index),
        _gesture=self[$ "fr_bubbles_touch213"]??undefined;
    if(!scrFREnabled() || !instance_exists(_player) || !scrFRRaceIs(_player.race)
        || UberCont.opt_splitfire || scrFRBubblesInputBlocked()) {
        fr_bubbles_touch213=undefined;return;
    }
    if(!is_struct(_gesture) || _gesture.pointer!=_pointer || _pressed) {
        _gesture={pointer:_pointer,armed:false,cancelled:false,dir:0,dis:0};
        fr_bubbles_touch213=_gesture;
    }
    if(distance_to_point(_mx,_my)>rad*3) {
        _gesture.armed=false;_gesture.cancelled=true;
    }
    if(_gesture.cancelled) {
        KeyCont.hold_fire[global.index]=false;
        KeyCont.press_fire[global.index]=false;
        KeyCont.release_fire[global.index]=false;
    } else {
        if(_dis/rad>ATTACK_BUTTON_DEADZONE) {
            _gesture.armed=true;_gesture.dir=_dir;_gesture.dis=_dis;
        } else if(_released && _gesture.armed) {
            KeyCont.dir_fire[global.index]=_gesture.dir;
            KeyCont.dis_fire[global.index]=_gesture.dis;
            KeyCont.press_fire[global.index]=true;
            KeyCont.hold_fire[global.index]=true;
        }
    }
    if(_released || !_held) _gesture.armed=false;
}
