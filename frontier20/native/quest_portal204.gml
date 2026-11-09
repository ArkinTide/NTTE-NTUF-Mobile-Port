// Ultimate Quest heart waves append enemies inside the crown-vault room.
// An empty wave is an artifact-merging interval, not a cleared level. Keep
// the ordinary corpse/recovery exit owned by the live locked quest chest.
// Successful unlock replaces that owner with the reward chest and releases
// this guard. Explicit CrownPickup exits retain their native direct path.
function scrFRQuestPortal204Blocked() {
    return instance_exists(NTTEFullLockedHugeQuestChest);
}
