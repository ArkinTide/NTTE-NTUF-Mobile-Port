// Fresh family predicates/counts avoid allocating a full projectile array for
// every collision test. No membership, team or mutable pickup state is cached.
function scrFRProjectileFamilyCount214(_type,_exists_only=false) {
    var _count=0;
    switch(_type) {
        case FRCustomProjectile:
            if(_exists_only) return instance_exists(FRCustomProjectile) || instance_exists(FRCustomSlash);
            // These are distinct native descendants (projectile and Slash).
            return instance_number(FRCustomProjectile)+instance_number(FRCustomSlash);
        case projectile:
            _count=instance_number(projectile);
            if(_exists_only && _count>0) return true;
            break;
        case FR_OBJECT_THROWN_WEP:break;
        default:return undefined;
    }
    with(WepPickup) if(scrFRIsThrownWeapon(id)) {
        if(_exists_only) return true;
        _count++;
    }
    return _exists_only?_count>0:_count;
}

function scrFRProjectileFamilyIs214(_target,_type) {
    if(_type!=projectile && _type!=FRCustomProjectile && _type!=FR_OBJECT_THROWN_WEP) return undefined;
    // Object selectors and non-instance operands retain the generic API.
    if(is_struct(_target) || is_array(_target) || is_string(_target) || is_undefined(_target)
        || is_method(_target) || is_ptr(_target)) return undefined;
    if(_target<100000) return undefined;
    if(!instance_exists(_target)) return false;
    switch(_type) {
        case FRCustomProjectile:
            return instance_is(_target,FRCustomProjectile) || instance_is(_target,FRCustomSlash);
        case projectile:
            return instance_is(_target,projectile) || scrFRIsThrownWeapon(_target);
        case FR_OBJECT_THROWN_WEP:return scrFRIsThrownWeapon(_target);
    }
    return undefined;
}
