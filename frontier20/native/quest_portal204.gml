// A dormant chest also exists during ordinary Crown Guardian visits. Only
// accepting four eligible components and starting the first merge countdown
// claims ordinary exit recovery. Keep that claim through every empty wave.
// GameCont's scalar is included by the native Continue session serializer.
// CrownPickup.Destroy restores logical area before the vault actually ends,
// so release at successful UNLOCK/RoomEnd rather than testing GameCont.area.
function scrFRQuestPortal204Blocked() {
    return instance_exists(NTTEFullLockedHugeQuestChest)
        && instance_exists(GameCont) && scrNTTEFullValue(GameCont,"fr_quest_portal205_active",false);
}
function scrFRQuestPortal205Activate() {
    if(!instance_exists(GameCont)) return;
    if(scrNTTEFullValue(GameCont,"fr_quest_portal205_active",false)) return;
    GameCont.fr_quest_portal205_active=true;
    // Guardians may have opened an ordinary exit before the player elected
    // to start the quest. Retire only that exit; CrownPickup type3 remains
    // its native explicitly granted route.
    with(Portal) if(type==1 || type==2) {
        instance_create(x,y,PortalClear);instance_destroy(id,false);
    }
}
function scrFRQuestPortal205Release() {
    if(instance_exists(GameCont)) GameCont.fr_quest_portal205_active=false;
}
function scrFRQuestPortal205RestoreChest(_chest) {
    if(!instance_exists(_chest) || !instance_exists(GameCont)
        || !scrNTTEFullValue(GameCont,"fr_quest_portal205_active",false)) return;
    // Continue restores the actual held native weapon graph before GenCont
    // rebuilds this chest. A claimed quest with all four merged components
    // already completed the source final merge; do not reset its UNLOCK stage.
    // Dormant vault visits and unfinished merges retain the native false state.
    with(Player) if(hp>0) {
        var _held=scrNTTEFullQuestPartList(wep,scrNTTEFullValue(id,"ntte_state",undefined)),
            _back=scrNTTEFullQuestPartList(bwep,scrNTTEFullValue(id,"bntte_state",undefined));
        if(array_length(_held)>=4 || array_length(_back)>=4) {
            _chest.is_unlockable=true;break;
        }
    }
}
