// Native Player death runs on every host frame, while the authored Wibbly
// manager notices that death on its next 30 Hz Step. Let that one pending
// observation finish before TopCont commits the native GameOver screen.
// The original manager alone decides whether Cyberspace/Cuz can revive.
function scrFRBluescreenPendingAdmission204() {
    if(!scrFREnabled() || !instance_exists(GameCont) || instance_exists(Player)
        || GameCont.win || scrNTTEFullValue(GameCont,"fr_visitedCyberspace",false)
        || !scrFRModGet("area","cyberspace","settingCyberspaceEnabled")) return false;
    with(FRCustomObject) {
        // A name alone must not let unrelated source actors hold the death UI.
        if(name!="wib_PlayerManager" || is_undefined(on_step)
            || scrFRScriptRef(on_step)!=scrFRScriptRef(fr_dependencies_wibbly_mod_gml_PlayerManager_step)) continue;
        var _living=self[$ "livingPlayers"]??undefined,_races=self[$ "playerRace"]??undefined;
        if(!is_array(_living) || !is_array(_races)
            || scrFRArrayFindIndex(_races,"robot")<0) continue;
        // Source checks for a Robot anywhere in the team when its last member
        // dies. The unobserved living slot need not be the Robot's own slot.
        for(var _i=0;_i<min(INPUT_MAX_PLAYERS,array_length(_living));++_i)
            if(_living[_i]>0) return true;
    }
    return false;
}
