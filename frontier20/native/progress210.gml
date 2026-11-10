// Permanent progress has three domains: normal, one custom slot, or a
// disposable console/practice run. Configuration remains shared.
function scrFRProgress210Cheated() {
    if(!instance_exists(UberCont)) return false;
    var _blocked=scrNTTEFullValue(UberCont,"opt_console",false) || scrNTTEFullValue(UberCont,"opt_practice",false)
        || (variable_global_exists("console_active") && global.console_active);
    if(instance_exists(GameCont)) {
        if(_blocked) GameCont.fr_progress210_blocked=true;
        return scrNTTEFullValue(GameCont,"fr_progress210_blocked",false);
    }
    return _blocked;
}
function scrFRProgress210Slot() {
    if(!instance_exists(UberCont) || !scrNTTEFullValue(UberCont,"custom",false)) return -1;
    if(instance_exists(GameCont) && scrFRContent210InRun()) {
        if(!is_real(scrNTTEFullValue(GameCont,"fr_progress210_slot",undefined)))
            GameCont.fr_progress210_slot=clamp(floor(UberCont.custom_mode_slot_index),0,max_custom_mode_slots-1);
        return GameCont.fr_progress210_slot;
    }
    return clamp(floor(UberCont.custom_mode_slot_index),0,max_custom_mode_slots-1);
}
function scrFRProgress210State() {
    if(!variable_global_exists("ntte_full_progress")) scrNTTEFullProgressLoad();
    var _root=global.ntte_full_progress,_slot=scrFRProgress210Slot(),_state=_root;
    if(_slot>=0) {
        if(!is_struct(_root[$ "custom210"]??undefined)) _root.custom210={};
        var _key=string(_slot);
        if(!is_struct(_root.custom210[$ _key]??undefined)) {
            // Each slot starts from the normal unlock baseline, then owns
            // its own data; never alias nested arrays/structs to normal data.
            _root.custom210[$ _key]=json_parse(json_stringify({unlocks:_root.unlocks,
                stats:_root.stats,loadouts:_root.loadouts}));
        }
        _state=_root.custom210[$ _key];
    }
    if(scrFRProgress210Cheated() && instance_exists(GameCont)) {
        if(!is_struct(scrNTTEFullValue(GameCont,"fr_progress210_volatile",undefined)))
            GameCont.fr_progress210_volatile=json_parse(json_stringify(_state));
        return GameCont.fr_progress210_volatile;
    }
    return _state;
}
function scrFRProgress210CanUnlock() { return !scrFRProgress210Cheated(); }
function scrFRProgress210CanStoreGold() {
    return !scrGameIsCustomMode() && !scrFRProgress210Cheated();
}
function scrFRProgress210ContentModule(_module) {
    return _module=="Frontier" || _module=="Frontier_Fishing";
}
function scrFRProgress210Field(_module) {
    return _module=="Frontier"?"frontier210":"frontier_fishing210";
}
function scrFRProgress210Frontier(_module="Frontier") {
    var _state=scrFRProgress210State(),_field=scrFRProgress210Field(_module);
    if(!is_struct(_state[$ _field]??undefined)) {
        var _normal=global.fr_module_vars[$ "mod:libSaves"].saves[$ _module]??{};
        _state[$ _field]=json_parse(json_stringify(_normal));
    }
    return _state[$ _field];
}
function scrFRProgress210SourceScoped(_module) {
    return scrFRProgress210ContentModule(_module) && (scrFRProgress210Slot()>=0 || scrFRProgress210Cheated());
}
function scrFRProgress210SourceGet(_key,_default=noone,_module="Frontier") {
    return scrFRProgress210Frontier(_module)[$ _key]??_default;
}
function scrFRProgress210SourceSet(_key,_value,_module="Frontier") {
    if(!scrFRProgress210CanUnlock()) return false;
    var _frontier=scrFRProgress210Frontier(_module);_frontier[$ _key]=_value;
    scrNTTEFullProgressSave();return true;
}
