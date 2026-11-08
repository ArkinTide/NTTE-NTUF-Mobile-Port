scrNTTESewerCreate(false)
event_inherited()
scrNTTESewerAfterCreate()

// NTTE Coast constructor wading variables
scrNTTEFullCoastConstructWading();
if(object_index==NTTEBabyGator) scrNTTEFullEnemyCreationHPFinish(); // NTTE FINAL ENEMY HP

// BEGIN FRONTIER BIOME CLEARANCE204 READONLY BIRTH
if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))
    scrFRBiomeClearance204NaturalCreated(id);
// END FRONTIER BIOME CLEARANCE204 READONLY BIRTH
