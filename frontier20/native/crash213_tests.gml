// Run from a ready source tick in the isolated native integration harness.
function scrFRCrash213Tests() {
    scrFRCrash213CreationTests();
    scrFRCrash213HomingTests();
    scrFRCrash213OrphanHitboxTests();
    scrFRCrash213ResetTests();
    scrNTTESmokeLog("PASS FRONTIER213 data-scope instance creation, selected homing target lifetime, orphan hitbox destroy and sparse settings reset");
}

function scrFRCrash213OrphanHitboxTests() {
    var _before=scrNTTEFullInstances(all),_owner=noone,_hitbox=noone;
    try {
        _owner=instance_create(10016,10016,FRCustomObject);
        _owner.team=team_player;_owner.wantHitbox=true;
        with(_owner) fr_Mutations_AugmentImpactWrists_skill_gml_ImpactDroneHitbox_create(x,y,real(id));
        with(FRCustomProjectile) if(creator==_owner) {_hitbox=id;break;}
        assert(instance_exists(_hitbox),"Actual impact drone factory created no native hitbox");
        _owner.droneHitbox=_hitbox;
        // Native Destroy must still clear the live drone's reference.
        instance_destroy(_hitbox);
        assert(_owner.droneHitbox==noone,"Live impact drone retained its destroyed hitbox");
        _hitbox=noone;
        with(_owner) fr_Mutations_AugmentImpactWrists_skill_gml_ImpactDroneHitbox_create(x,y,real(id));
        with(FRCustomProjectile) if(creator==_owner) {_hitbox=id;break;}
        assert(instance_exists(_hitbox),"Second impact drone factory created no native hitbox");
        _owner.droneHitbox=_hitbox;
        instance_destroy(_owner,false);
        assert(!instance_exists(_owner),"Owner-first destroy fixture left its drone alive");
        // Exercise the real authored End Step and native Destroy event chain,
        // rather than calling the guarded destroy function in isolation.
        scrFRInvoke(_hitbox,_hitbox.on_end_step,[]);
        assert(!instance_exists(_hitbox),"Orphan impact hitbox failed to retire itself");
    } finally {scrNTTEFullMergedRuntimeTestCleanup(_before);}
}

function scrFRCrash213CreationTests() {
    var _before=scrNTTEFullInstances(all),_plain={tag:"graveyard-area-data"},
        _data={tag:"source-with",hitid:[sprBullet1,"DATA CALLBACK"]},
        _ordinary,_flower,_shot,_proxy,_prompt=instance_create(10016,10016,FRCustomObject);
    try {
        // A data scope has no native id. Exercise both the reported area
        // creation branch and the genuine IceFlower branch, not only a type
        // that avoids the proxy guard on a short-circuiting runner.
        assert(!variable_struct_exists(_plain,"id"),"Creation fixture accidentally has a native id");
        with(_plain) {
            _ordinary=scrFRInstanceCreate(10016,10016,FRCustomObject);
            _flower=scrFRInstanceCreate(10048,10016,IceFlower);
        }
        assert(instance_exists(_ordinary) && _ordinary.object_index==FRCustomObject,
            "Area data callback failed to construct an authored object");
        assert(instance_exists(_flower) && _flower.object_index==IceFlower,
            "Data callback incorrectly created an interaction proxy instead of a real flower");
        with(_data) _shot=scrFRInstanceCreate(10080,10016,BouncerBullet);
        assert(instance_exists(_shot) && _shot.hitid==_data.hitid,
            "Data callback creation lost its explicitly supplied damage identity");
        _prompt.name="LibPrompt";
        with(_prompt) _proxy=scrFRInstanceCreate(x,y,IceFlower);
        assert(instance_exists(_proxy) && _proxy.object_index==FRCustomObject
            && _proxy.fr_prompt_proxy && !_proxy.visible && _proxy.mask_index==mskNone,
            "Real prompt instance lost its nonphysical collision proxy");
    } finally {scrNTTEFullMergedRuntimeTestCleanup(_before);}
}

function scrFRCrash213HomingTests() {
    var _before=scrNTTEFullInstances(all),_parked=scrNTTEFullInstances(enemy),
        _seed=scrFRSourceRandomGetSeed(),_rocket=noone,_target=noone,
        _player=instance_find(Player,0);
    assert(instance_exists(_player),"Micromissile fixture requires its real player owner");
    assert(frMacro_Objects_Frontier_Projectiles2_mod_gml_current_frame_active,
        "Micromissile test must run on a real active source tick");
    for(var _i=0;_i<array_length(_parked);++_i) instance_deactivate_object(_parked[_i]);
    try {
        with(_player) _rocket=fr_Objects_Frontier_Projectiles2_mod_gml_PopoRocketSmall_create(10016,10016);
        assert(instance_exists(_rocket),"Actual IDPD micromissile factory returned no projectile");
        _rocket.direction=0;_rocket.image_angle=0;
        scrFRInvoke(_rocket,["mod","Frontier_Projectiles2","PopoRocketSmall_step"],[]);
        assert(instance_exists(_rocket) && _rocket.direction==0,
            "Targetless micromissile stopped flying or acquired a false heading");
        _target=instance_create(10016,9888,FRCustomEnemy);
        var _desired=point_direction(_rocket.x,_rocket.y,_target.x,_target.y),
            _expected=_rocket.direction-angle_difference(_rocket.direction,_desired)*.2;
        scrFRInvoke(_rocket,["mod","Frontier_Projectiles2","PopoRocketSmall_step"],[]);
        assert(abs(angle_difference(_rocket.direction,_expected))*1000000<1
            && _rocket.image_angle==_rocket.direction,
            "Live target failed to retain the authored micromissile homing strength");
        instance_destroy(_target,false);_target=noone;
        var _heading=_rocket.direction;
        repeat(4) scrFRInvoke(_rocket,["mod","Frontier_Projectiles2","PopoRocketSmall_step"],[]);
        assert(instance_exists(_rocket) && _rocket.direction==_heading,
            "Destroying the final target corrupted an in-flight micromissile");
        // Owner removal is independent of target lifetime; a delayed shot
        // must still finish without reading a deleted source actor.
        var _owner=instance_create(10016,10016,FRCustomObject),_orphan;
        _owner.team=_player.team;
        with(_owner) _orphan=fr_Objects_Frontier_Projectiles2_mod_gml_PopoRocketSmall_create(x,y);
        instance_destroy(_owner,false);
        scrFRInvoke(_orphan,["mod","Frontier_Projectiles2","PopoRocketSmall_step"],[]);
        assert(instance_exists(_orphan),"A valid orphaned micromissile failed its targetless Step");
    } finally {
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        for(var _i=0;_i<array_length(_parked);++_i) instance_activate_object(_parked[_i]);
        scrFRSourceRandomSetSeed(_seed);
    }
}

function scrFRCrash213ResetTests() {
    var _settings=ds_map_create(),_categories=[];
    try {
        _settings[? "video_framerate"]=60;_settings[? "ntuf_content"]=false;
        _settings[? "game_tutorial"]=true;_settings[? "unlocked_character"]=true;
        _settings[? "custom_slot"]=7;
        _categories[0]=[{key:"video_framerate"},{key:"game_tutorial"}];
        _categories[9]=[{key:"ntuf_content"},{key:"video_framerate"},
            {key:undefined},{type:"button"},undefined,42,"old platform slot"];
        _categories[4]=undefined;_categories[6]={retired:true};
        assert(scrOptionsEraseKeys213(_categories,_settings)==2,
            "Sparse/reset categories failed to erase exactly the two saved settings");
        assert(!ds_map_exists(_settings,"video_framerate") && !ds_map_exists(_settings,"ntuf_content"),
            "Settings reset silently left registered values in the save map");
        assert(_settings[? "game_tutorial"] && _settings[? "unlocked_character"]
            && _settings[? "custom_slot"]==7,
            "Settings reset erased tutorial, progression or a custom save slot");
        assert(scrOptionsEraseKeys213(_categories,_settings)==0
            && scrOptionsEraseKeys213(undefined,_settings)==0,
            "Repeated reset or an absent menu collection corrupted saved data");
    } finally {ds_map_destroy(_settings);}
}
