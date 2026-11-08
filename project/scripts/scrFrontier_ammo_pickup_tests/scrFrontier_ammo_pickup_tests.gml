// Explicit silent desktop acceptance. The engine schedules FRWorld's real
// acquired-skill callbacks and the real AmmoPickup/Player collision events.
function scrFRAmmoPickupTestsStart(_driver) {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Ammo pickup acceptance requires the settled isolated native runner");
    var _original=UberCont.saveData,_map=ds_map_create();ds_map_copy(_map,_original);
    _driver.fr_ammo_pickup={world:scrNTTEFullWorldEventsNaturalWorldCapture(),
        original_map:_original,map_bytes:ds_map_write(_original),fixture_map:_map,
        phase:0,round:0,age:0,elapsed:0,serial:0,batch:0,index:0,queue:[],items:[],beacons:[],
        player:instance_find(Player,0),second:noone,active:undefined,grants:0,
        second_index:player_count,second_slot:undefined,
        kinds:[0,0,0,0,0],types:[0,0,0,0,0],stacked:0,coop_grants:0,
        skills:["AugmentSecondStomach","AugmentRabbitPaw","AugmentOpenMind"],
        weapons:[wep_none,wep_revolver,wep_shotgun,wep_crossbow,wep_grenade_launcher,wep_laser_pistol]};
    UberCont.saveData=_map;
    assert(_driver.fr_ammo_pickup.second_index<INPUT_MAX_PLAYERS
        && !is_struct(scr_playerinstance_find(_driver.fr_ammo_pickup.second_index)),
        "Ammo pickup acceptance needs one unused contiguous native PlayerInstance slot");
}

function scrFRAmmoPickupTestsClear(_state) {
    for(var _i=0;_i<array_length(_state.skills);++_i) scrFRSetSkill(_state.skills[_i],0);
    for(var _i=0;_i<array_length(_state.items);++_i)
        if(instance_exists(_state.items[_i])) instance_destroy(_state.items[_i],false);
    for(var _i=0;_i<array_length(_state.beacons);++_i)
        if(instance_exists(_state.beacons[_i])) instance_destroy(_state.beacons[_i],false);
    if(instance_exists(_state.second)) instance_destroy(_state.second,false);
    if(is_struct(_state.second_slot)) {
        assert(scr_playerinstance_find(_state.second_index)==_state.second_slot,
            "Ammo pickup acceptance lost its actual secondary native player registration");
        scr_playerinstance_destroy(_state.second_index);
        _state.second_slot=undefined;
    }
    _state.items=[];_state.beacons=[];_state.second=noone;
    scr_ultra_set(Race.CoopUltra,1,0);
}

function scrFRAmmoPickupTestsSpawn(_state,_kind,_type,_slot) {
    var _x=920000+_slot*128,_y=920000,
        _object=_kind==0?AmmoPickup:(_kind==1?CursedPickup:NTTEFullSourceAmmoPickup),
        _pickup=instance_create(_x,_y,_object),_quantity=_kind==1?1.5:1;
    if(_kind>=2) {
        _quantity=_kind-1;
        scrNTTEFullBackpackSetAmmo(_pickup,_kind==3,_quantity,1000);
    }
    assert(instance_exists(_pickup),"Actual ammo pickup constructor did not retain its requested family");
    // Haste shortens native pickup lifetime; keep the last real collision
    // available while this acceptance deliberately collects one bag at a time.
    _pickup.alarm[0]=1000;
    array_push(_state.items,_pickup);
    return {pickup:_pickup,kind:_kind,type:_type,base:_quantity,quantity:_quantity};
}

function scrFRAmmoPickupTestsBatch(_state,_batch) {
    _state.batch=_batch;_state.queue=[];_state.index=0;_state.active=undefined;
    _state.player.x=900000;_state.player.y=900000;
    _state.second.x=898000;_state.second.y=900000;
    // Ordinary, native cursed, and the actual NTTE source-configured bags
    // with authored multipliers 1,2,3 are all collected for all five types.
    // The stacked negative controls occupy slots128..191 and remain alive.
    // Keep the later shared batch outside those real pickup collision masks.
    var _base_slot=_batch==4?256:_batch*32;
    for(var _kind=0;_kind<5;++_kind) for(var _type=Ammo.Bullets;_type<Ammo.NUM_AMMO_TYPES;++_type)
        array_push(_state.queue,scrFRAmmoPickupTestsSpawn(_state,_kind,_type,
            _kind*5+_type+_base_slot));
    _state.serial=FRWorld.logic_serial;_state.phase=2;
    scrNTTESmokeLog("FRONTIER AMMO batch "+string(_batch)+" at "+string(_state.round==0?30:60)+"Hz");
}

function scrFRAmmoPickupTestsCheck(_state,_increase) {
    for(var _i=0;_i<array_length(_state.queue);++_i) {
        var _row=_state.queue[_i],_pickup=_row.pickup,_expected=_row.base+_increase;
        assert(instance_exists(_pickup) && scrFRAmmoPickupQuantity(_pickup)==_expected,
            "Actual acquired ammo augment changed a pickup more than once or lost its authored baseline "
            +json_stringify({batch:_state.batch,kind:_row.kind,type:_row.type,expected:_expected,
                actual:instance_exists(_pickup)?scrFRAmmoPickupQuantity(_pickup):-1}));
        _row.quantity=_expected;
        if(_increase>0) assert(scrNTTEFullValue(_pickup,"fr_augmentSecondStomach_check",false)
            && _pickup.fr_augmentAmmoTier==1,
            "Actual FRWorld acquired Shellular Division hook did not apply exactly one source upgrade");
    }
}

function scrFRAmmoPickupTestsCollect(_state) {
    if(is_undefined(_state.active)) {
        if(_state.index>=array_length(_state.queue)) return true;
        var _row=_state.queue[_state.index],_pickup=_row.pickup,
            _player=_state.player,_second=_state.second,_type=_row.type,_weapon=_state.weapons[_type];
        assert(instance_exists(_pickup),"Native ammo pickup disappeared before its actual collection");
        for(var _i=0;_i<array_length(_state.items);++_i) {
            var _remaining=_state.items[_i];
            if(instance_exists(_remaining) && _remaining!=_pickup)
                assert(point_distance(_pickup.x,_pickup.y,_remaining.x,_remaining.y)>64,
                    "Ammo fixture placed two actual native grants inside one collision scene");
        }
        with(_player) {
            x=_pickup.x;y=_pickup.y;xprevious=x;yprevious=y;speed=0;
            wep=_weapon;bwep=wep_none;scrExtraWepsReset();ammo=array_create(Ammo.NUM_AMMO_TYPES,0);
            can_walk=false;can_aim=false;can_shoot=false;bcan_shoot=false;infammo=0;
        }
        with(_second) {
            wep=_weapon;bwep=wep_none;scrExtraWepsReset();ammo=array_create(Ammo.NUM_AMMO_TYPES,0);
            can_walk=false;can_aim=false;can_shoot=false;bcan_shoot=false;infammo=0;
        }
        _row.expected=round(scrFRAmmoRead(_player,"typ_ammo",_type)*_row.quantity)
            +(scrCrownCheck(crwn_haste)?1:0);
        _row.expected_second=scr_ultra_get(Race.CoopUltra,1)
            ?round(scrFRAmmoRead(_second,"typ_ammo",_type)*_row.quantity)+(scrCrownCheck(crwn_haste)?1:0):0;
        _state.active=_row;_state.age=0;return false;
    }
    var _row=_state.active;
    assert(++_state.age<12,"Real Player collision did not collect the prepared ammo pickup");
    if(instance_exists(_row.pickup)) return false;
    var _actual=_state.player.ammo[_row.type],_other=_state.second.ammo[_row.type];
    assert(_actual==_row.expected && _other==_row.expected_second,
        "Real ammo collision lost additive quantity, recipient modifiers, rounding, Haste or sharing "
        +json_stringify({batch:_state.batch,kind:_row.kind,type:_row.type,quantity:_row.quantity,
            expected:_row.expected,actual:_actual,expected_second:_row.expected_second,actual_second:_other}));
    _state.grants++;_state.kinds[_row.kind]++;_state.types[_row.type-1]++;
    if(_row.expected_second>0) _state.coop_grants++;
    _state.index++;_state.active=undefined;return false;
}

function scrFRAmmoPickupTestsStack(_state) {
    scrFRSetSkill("AugmentRabbitPaw",1);scrFRSetSkill("AugmentOpenMind",1);
    _state.queue=[];
    for(var _i=0;_i<64;++_i) {
        var _row=scrFRAmmoPickupTestsSpawn(_state,_i mod 5,1+(_i mod 5),128+_i),
            _pickup=_row.pickup,_beacon=scrFRInvoke(GameCont.id,
                fr_Mutations_AugmentOpenMind_skill_gml_Beacon_create,[_pickup.x,_pickup.y]);
        assert(instance_exists(_beacon),"Actual source beacon constructor returned no world actor");
        array_push(_state.beacons,_beacon);array_push(_state.queue,_row);
    }
    _state.player.x=900000;_state.player.y=900000;
    _state.serial=FRWorld.logic_serial;_state.phase=6;
}

function scrFRAmmoPickupTestsStackCheck(_state,_first) {
    var _upgraded=0;
    for(var _i=0;_i<array_length(_state.queue);++_i) {
        var _row=_state.queue[_i],_pickup=_row.pickup,_tier=scrNTTEFullValue(_pickup,"fr_augmentAmmoTier",-1);
        assert(scrNTTEFullValue(_pickup,"fr_augmentSecondStomach_check",false)
            && scrNTTEFullValue(_pickup,"fr_augmentRabbitPaw_check",false)
            && scrNTTEFullValue(_pickup,"fr_augmentBeaconed",false)
            && (_tier==2 || _tier==3),
            "Actual source skill/beacon callbacks did not keep each augment's independent once marker");
        var _expected=_row.base+0.5*_tier;
        assert(scrFRAmmoPickupQuantity(_pickup)==_expected && (_first || _row.quantity==_expected),
            "Distinct real augments did not stack additively or repeated world ticks reapplied their bonus");
        _row.quantity=_expected;if(_tier==3) _upgraded++;
    }
    assert(_upgraded>0,"Real Micro Refinery RNG did not exercise its positive ammo-upgrade branch");
    _state.stacked+=_first?_upgraded:0;
}

function scrFRAmmoPickupTestsFinish(_state) {
    assert(_state.grants==210 && _state.coop_grants==50 && _state.stacked>0,
        "Ammo acceptance did not exercise all intended real pickup grants");
    for(var _i=0;_i<5;++_i) assert(_state.kinds[_i]==42 && _state.types[_i]==42,
        "Ammo acceptance omitted a native family or ammo type");
    scrFRAmmoPickupTestsClear(_state);
    scrNTTEFullWorldEventsNaturalWorldRestore(_state.world);
    UberCont.saveData=_state.original_map;ds_map_destroy(_state.fixture_map);scrOptionsUpdate();
    assert(ds_map_write(_state.original_map)==_state.map_bytes,
        "Ammo pickup acceptance changed the user's original permanent save map");
    scrNTTESmokeLog("PASS FRONTIER AMMO real FRWorld acquired/late/repeated/stacked augments and native pickup collisions at30/60Hz "
        +json_stringify({grants:_state.grants,kinds:_state.kinds,types:_state.types,
            rabbit_positive:_state.stacked,coop_haste_grants:_state.coop_grants}));
    return true;
}

function scrFRAmmoPickupTestsStep(_driver) {
    var _state=_driver.fr_ammo_pickup;
    assert(++_state.elapsed<2400,"Ammo pickup acceptance timed out phase="+string(_state.phase));
    GameCont.is_level_ended=true;
    with(Player) {hp=10000;max_hp=10000;lsthealth=10000;nexthurt=current_frame+10000;
        can_walk=false;can_aim=false;can_shoot=false;bcan_shoot=false;speed=0;}
    if(_state.phase==0) {
        scrFRAmmoPickupTestsClear(_state);
        save_set_value("options","framerate",_state.round==0?30:60);
        save_set_value("options","autopause",false);save_set_value("visual","freezeframes",0);scrOptionsUpdate();
        GameCont.crown=crwn_none;GameCont.area=area_desert;GameCont.loops=0;GameCont.killenemies=false;
        // This Player runs real engine Step/alarms between collisions, so it
        // needs the same contiguous native registration as a real co-op join.
        _state.second_slot=new PlayerInstance(_state.second_index);
        scr_playerinstance_add(_state.second_index,_state.second_slot);
        _state.second=scrPlayerCreate(_state.second_index,Race.Venuz,0);
        _state.second.x=898000;_state.second.y=900000;
        with(Player) {race=Race.Venuz;curse=0;bcurse=0;can_die=false;}
        with(UberCont) scrAmmoUpdateTypeStats();
        _state.serial=FRWorld.logic_serial;_state.phase=1;return false;
    }
    if(_state.phase==1) {
        if(FRWorld.logic_serial-_state.serial<3) return false;
        assert(timescale==(_state.round==0?1:0.5),"Ammo pickup test did not apply the native30/60Hz policy");
        scrFRAmmoPickupTestsBatch(_state,0);return false;
    }
    if(_state.phase==2) {
        if(FRWorld.logic_serial-_state.serial<4) return false;
        scrFRAmmoPickupTestsCheck(_state,_state.batch==0?0:0.5);
        _state.serial=FRWorld.logic_serial;_state.phase=3;return false;
    }
    if(_state.phase==3) {
        if(FRWorld.logic_serial-_state.serial<4) return false;
        scrFRAmmoPickupTestsCheck(_state,_state.batch==0?0:0.5);
        _state.phase=4;return false;
    }
    if(_state.phase==4) {
        if(!scrFRAmmoPickupTestsCollect(_state)) return false;
        if(_state.batch==0) {
            // Existing pickups precede the actual acquisition. Positive
            // Wibbly gain changes are real per-player source mutation calls.
            scrFRAmmoPickupTestsBatch(_state,1);
            for(var _type=Ammo.Bullets;_type<Ammo.NUM_AMMO_TYPES;++_type) {
                scrFRModCallArray("mod","wibbly","ammoGainBonus_add",[_state.player.index,_type,1]);
                scrFRModCallArray("mod","wibbly","ammoGainBonus_add",[_state.second.index,_type,3]);
            }
            scrFRSetSkill("AugmentSecondStomach",1);return false;
        }
        if(_state.batch==1) {scrFRAmmoPickupTestsBatch(_state,2);return false;}
        if(_state.batch==2) {scrFRAmmoPickupTestsStack(_state);return false;}
        if(_state.batch==3) {
            scrFRSetSkill("AugmentRabbitPaw",0);scrFRSetSkill("AugmentOpenMind",0);
            for(var _i=0;_i<array_length(_state.beacons);++_i)
                if(instance_exists(_state.beacons[_i])) instance_destroy(_state.beacons[_i],false);
            _state.beacons=[];
            scr_ultra_set(Race.CoopUltra,1,1);GameCont.crown=crwn_haste;
            with(UberCont) scrAmmoUpdateTypeStats();
            scrFRAmmoPickupTestsBatch(_state,4);return false;
        }
        for(var _type=Ammo.Bullets;_type<Ammo.NUM_AMMO_TYPES;++_type) {
            scrFRModCallArray("mod","wibbly","ammoGainBonus_add",[_state.player.index,_type,-1]);
            scrFRModCallArray("mod","wibbly","ammoGainBonus_add",[_state.second.index,_type,-3]);
        }
        if(++_state.round<2) {_state.phase=0;return false;}
        return scrFRAmmoPickupTestsFinish(_state);
    }
    if(_state.phase==6) {
        if(FRWorld.logic_serial-_state.serial<4) return false;
        scrFRAmmoPickupTestsStackCheck(_state,true);
        _state.serial=FRWorld.logic_serial;_state.phase=7;return false;
    }
    if(_state.phase==7) {
        if(FRWorld.logic_serial-_state.serial<5) return false;
        scrFRAmmoPickupTestsStackCheck(_state,false);
        // Collect one actual stacked pickup from every native family. The
        // remaining actors stay alive as the repeated-step negative control.
        var _selected=[];for(var _i=0;_i<5;++_i) array_push(_selected,_state.queue[_i]);
        _state.queue=_selected;_state.batch=3;_state.index=0;
        _state.active=undefined;_state.phase=4;return false;
    }
    return false;
}
