// Gameplay loop voices belong to their live producer, never to a checkpoint.
// Keep the author's shared module slots for normal laser/shock callbacks, but
// retain the exact returned voices on Bulwark so Room Cleanup can retire them.
function scrFRBulwarkLoop205(_kind,_sample) {
    var _voice=scrFRSoundLoop(_sample);
    var _owner=id;
    // The shock loop is started by an orbital in the source, whereas laser
    // starts in the boss Alarm. Both belong to the boss's room lifetime.
    if(_kind=="shock") {
        var _creator=self[$ "creator"]??noone;
        if(instance_exists(_creator) && (_creator[$ "name"]??"")=="BULWARK SYSTEM") _owner=_creator;
    }
    _owner[$ "fr_bulwark_"+_kind+"_voice205"]=_voice;
    return _voice;
}

function scrFRBulwarkAudioCleanup205() {
    var _fields=["fr_bulwark_laser_voice205","fr_bulwark_shock_voice205"];
    for(var _i=0;_i<array_length(_fields);++_i) {
        var _field=_fields[_i],_voice=self[$ _field]??-1;
        // Only a voice captured from this instance can be stopped here. A
        // later boss may already own the shared source module's new voice.
        if(is_real(_voice) && _voice>=0 && audio_exists(_voice)) audio_stop_sound(_voice);
        self[$ _field]=-1;
    }
}

function scrFRContinueAudioField205(_field) {
    return _field=="eyesloop" || _field=="horrorloop" || _field=="ntte_cat_loop";
}

function scrFRPlayerAudioStop205() {
    var _fields=["eyesloop","horrorloop","ntte_cat_loop"];
    for(var _i=0;_i<array_length(_fields);++_i) {
        var _field=_fields[_i];
        if(!variable_instance_exists(id,_field)) continue;
        var _voice=self[$ _field];
        if(is_real(_voice) && _voice>=0 && audio_exists(_voice)) audio_stop_sound(_voice);
        self[$ _field]=-1;
    }
}
