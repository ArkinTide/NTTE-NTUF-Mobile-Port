max_hp=1;spr_idle=-1;spr_walk=-1;spr_hurt=-1;spr_dead=-1;raddrop=0;size=1;
meleedamage=0;event_inherited();scrFRActorInit();
max_hp=1;hp=1;fr_maxhealth_init=true;

// BEGIN FRONTIER BIOME CLEARANCE204 READONLY BIRTH
if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))
    scrFRBiomeClearance204NaturalCreated(id);
// END FRONTIER BIOME CLEARANCE204 READONLY BIRTH
