// Source crowns/*.crown_menu_avail is global loadout:crown:key ownership;
// native per-race crowngot arrays cannot represent that separate progression.
function scrNTTEFullCrownContentAvailable(_crown) {
    if(_crown==17) return scrFRCrownReady();
    if(_crown>=14 && _crown<=16)
        return scrNTTEFullFeatureReady("crown:"+scrNTTEFullCrownKey(_crown));
    return scr_crown_is_valid(_crown);
}
function scrNTTEFullCrownLoadoutSlots() {
    var _slots=[]
    for(var _id=0;_id<=17;++_id)
        if(scrNTTEFullCrownContentAvailable(_id)) array_push(_slots,_id);
    return _slots
}
function scrNTTEFullCrownLoadoutAvailable(_race,_crown) {
    return scrNTTEFullCrownContentAvailable(_crown)
        && (scrCustomParam("unlock_crowns",false)
            || (scr_race_is_unlocked(_race) && scrNTTEFullCrownLoadoutOwned(_crown)));
}
function scrNTTEFullCrownLoadoutOwned(_crown) {
    var _key="loadout:crown:"+scrNTTEFullCrownKey(_crown);
    // An older Custom slot may predate a crown earned in Normal.
    return scrNTTEFullUnlockGet(_key) || (scrGameIsCustomMode()
        && scrNTTEFullValue(global.ntte_full_progress.unlocks,_key,false));
}
function scrNTTEFullCrownLoadoutCount(_race) {
    var _count=0
    for(var _id=crwn_none+1;_id<=17;++_id) {
        if(scr_loadout_race_is_crown_unlocked(_race,_id)) _count+=1;
    }
    return _count
}
function scrNTTEFullCrownLoadoutSprite(_crown,_unlocked=true) {
    if(scrFRCrownKey(_crown)!="") return [sprFRStormsLoadout,_unlocked?0:1];

    if(_crown>=14 && _crown<=16) return [scrNTTEFullCrownSprite(_crown,"Loadout"),_unlocked?0:1]
    return [_unlocked?sprLoadoutCrown:sprLockedLoadoutCrown,_crown]
}
function scrNTTEFullCrownLoadoutUnlock(_crown) {
    var _key=scrNTTEFullCrownKey(_crown);
    if(_key=="" || !scrNTTEFullCrownContentAvailable(_crown) || scrNTTEFullCrownLoadoutOwned(_crown)) return false;
    return scrNTTEFullUnlockSet("loadout:crown:"+_key,true)
}
function scrNTTEFullCrownLoadoutUnlockCurrent() {
    return scrNTTEFullCrownLoadoutUnlock(GameCont.crown);
}
