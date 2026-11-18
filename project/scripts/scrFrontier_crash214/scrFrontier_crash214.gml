// Loading-screen spirals are decorative. Keep a corrupt or unusually large
// host time step out of their constructor warm-up and native image bounds.
// Normal 30/60/120 Hz deltas pass through unchanged; never alter gameplay time.
function scrFRSpiralDelta214(_dt) {
    if(!is_numeric(_dt)) return 1;
    if(!(_dt>0)) return 1;
    return clamp(_dt,.25,1);
}

function scrFRSpiralWarmCount214(_dt) {
    return clamp(round(150/scrFRSpiralDelta214(_dt)),150,600);
}

function scrFRSpiralAdvance214(_dt,_controller) {
    // Calculate and validate locally before assigning image_xscale/yscale:
    // the runner updates native collision bounds on those assignments and
    // throws before a later instance_destroy can remove an infinite scale.
    if(!(grow>=0 && grow<=16 && image_xscale>=0 && image_xscale<=16
        && image_yscale>=0 && image_yscale<=16)) return false;
    var _grow=grow+.0002*_dt;
    if(sprite_index==sprSpiralProto) _grow+=.0003*_dt;
    var _sx=image_xscale+_grow*_dt,_sy=image_yscale+_grow*_dt;
    _grow+=(.0005*_sx*(_grow+1))*_dt;
    if(!_controller) _grow*=power(1.5,_dt);
    if(!(_sx>=0 && _sx<=16 && _sy>=0 && _sy<=16 && _grow>=0 && _grow<=16)) return false;
    grow=_grow;image_xscale=_sx;image_yscale=_sy;
    return true;
}
