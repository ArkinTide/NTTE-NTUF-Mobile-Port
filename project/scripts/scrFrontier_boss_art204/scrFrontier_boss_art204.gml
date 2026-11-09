// These15 authored intro layers are single frames. Assign them directly so
// their exact native pixels/origins survive; other Frontier image APIs retain
// their existing multi-frame extraction contract.
function scrFRBossArt204State() {
    if(!variable_global_exists("fr_boss_art204_state") || !is_struct(global.fr_boss_art204_state))
        global.fr_boss_art204_state={targets:[],copies:[],starting:false};
    return global.fr_boss_art204_state;
}

function scrFRBossArt204OwnerValid(_owner) {
    if(is_undefined(_owner) || !is_numeric(_owner) || _owner==noone) return false;
    // Native boss intros deactivate gameplay bindings. Briefly resolve only
    // this owner, without advancing its callback or resuming its simulation.
    var _active=instance_exists(_owner);
    if(!_active) instance_activate_object(_owner);
    var _valid=instance_exists(_owner) && instance_is(_owner,FRBinding)
        && scrFRScriptRef(_owner.fr_binding_code)==scrFRScriptRef(fr_Objects_Frontier_Bosses_mod_gml_boss_intro_step);
    if(!_active && instance_exists(_owner)) instance_deactivate_object(_owner);
    return _valid;
}

function scrFRBossArt204IntroPrepare(_owner) {
    // The authored callback assigns all three sprites before starting the
    // native intro. Reject first so a refused callback cannot change live art.
    if(!instance_exists(UberCont) || instance_exists(CoopController)
        || !UberCont.opt_bossintro || !instance_exists(Player)
        || !scrFRBossArt204OwnerValid(_owner)) return false;
    scrFRBossArt204IntroFinish();
    _owner.fr_boss_art204_prepared=true;
    return true;
}

function scrFRBossArt204Replace(_target,_source,_image=0) {
    var _path=is_string(_source)?scrFRAssetPath(_source):"",_resolved=_source;
    if(is_string(_source)) {
        _resolved=global.fr_asset_sources[$ _path];
        if(is_undefined(_resolved)) throw "Frontier boss artwork was not packaged: "+_path;
    }
    var _role="",
        _bosses=["covehypercrystal","graveyardboss","lightninghypercrystal","ourplecursedhypercrystal","roboboss"],
        _allowed=false;
    if(_target==sprBossIntro) _role="main";
    else if(_target==sprBossIntroBackLayer) _role="back";
    else if(_target==sprBossName) _role="name";
    if(_role!="" && _image==0) for(var _i=0;_i<array_length(_bosses);++_i) {
        var _expected="sprites/menu/intros/spr"+_bosses[_i]+_role+".png",
            _asset=global.fr_asset_sources[$ _expected];
        if(_resolved==_asset && (_path=="" || _path==_expected || _path=="../"+_expected)) {
            _allowed=true;break;
        }
    }
    if(!_allowed || !sprite_exists(_target) || !sprite_exists(_resolved) || sprite_get_number(_resolved)!=1)
        throw "Frontier boss artwork is outside the packaged single-frame intro contract";
    // These private copies outlive a destroyed binding or a rebuilt Frontier
    // registry. Generic sprite backups and replacement semantics stay intact.
    var _state=scrFRBossArt204State();
    if(!array_contains(_state.targets,_target)) {
        var _copy=sprite_duplicate(_target);
        if(!sprite_exists(_copy)) throw "Frontier boss artwork snapshot failed";
        array_push(_state.targets,_target);array_push(_state.copies,_copy);
    }
    return scrFRSpriteReplace(_target,_resolved);
}

function scrFRBossArt204IntroStart(_owner=undefined) {
    if(!instance_exists(UberCont) || instance_exists(CoopController)
        || !UberCont.opt_bossintro || !instance_exists(Player)) return false;
    if(!scrFRBossArt204OwnerValid(_owner)) return false;
    // The NTT source uses BanditBoss Alarm6. Epsilon's native equivalent is
    // scrBossIntro, and an old NTTE lookup key must not redirect this art.
    UberCont.ntte_full_intro_key="";
    var _state=scrFRBossArt204State();
    _state.starting=true;
    try {scrBossIntro(0);}
    finally {_state.starting=false;}
    UberCont.fr_boss_art204_owner=_owner;
    UberCont.fr_boss_art204_intro=UberCont.bossintro;
    return scrFRBossArt204IntroActive();
}

function scrFRBossArt204IntroActive() {
    if(!instance_exists(UberCont)) return false;
    if(scrFRBossArt204State().starting) return false;
    var _uber=instance_find(UberCont,0),
        _owner=_uber[$ "fr_boss_art204_owner"]??noone;
    if(!UberCont.bossintro || !scrFRBossArt204OwnerValid(_owner)) {
        scrFRBossArt204IntroFinish();return false;
    }
    return _uber[$ "fr_boss_art204_intro"]??false;
}

function scrFRBossArt204IntroFinish() {
    var _state=scrFRBossArt204State();
    for(var _i=0;_i<array_length(_state.targets);++_i) {
        var _target=_state.targets[_i],_copy=_state.copies[_i];
        if(sprite_exists(_copy)) {
            if(sprite_exists(_target)) sprite_assign(_target,_copy);
            sprite_delete(_copy);
        }
    }
    _state.targets=[];_state.copies=[];
    if(instance_exists(UberCont)) {UberCont.fr_boss_art204_intro=false;UberCont.fr_boss_art204_owner=noone;}
}

function scrFRBossArt204NativeStart() {
    // Called only after the native Coop/option/no-player guards accepted.
    // An ordinary/NTTE intro retires stale Frontier pixels even if their
    // binding was destroyed before its authored cleanup could run.
    if(!scrFRBossArt204State().starting) scrFRBossArt204IntroFinish();
    if(instance_exists(UberCont)) {UberCont.fr_boss_art204_intro=false;UberCont.fr_boss_art204_owner=noone;}
}

function scrFRBossArt204IntroName(_native_name) {
    // A native Big Bandit translation would cover the source's Name PNG.
    // Return its existing result for every ordinary native/NTTE intro.
    return scrFRBossArt204IntroActive()?undefined:_native_name;
}
