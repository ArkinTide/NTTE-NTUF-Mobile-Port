// Explicit private desktop regression. Real LevCont Draw GUI events rebuild
// every Griller page; real ordinary rolls and authored exclusive grants are
// exercised separately. No fake SkillIcon chooser is used by this fixture.
function scrFRMutationPool204Groups() {
    var _groups={mini:[],hidden:[],augment:[],surgery:[],burden:[]};
    var _mini=["bat ears","lead ribs","magnetic pulse","toad breath"],
        _hidden=["annihilation","reroll","silver tongue"];
    for(var _i=0;_i<array_length(_mini);++_i)
        array_push(_groups.mini,{name:_mini[_i],id:scrNTTEFullSkillId(_mini[_i])});
    for(var _i=0;_i<array_length(_hidden);++_i)
        array_push(_groups.hidden,{name:_hidden[_i],id:scrNTTEFullSkillId(_hidden[_i])});
    var _ids=variable_struct_get_names(global.fr_skill_keys);
    for(var _i=0;_i<array_length(_ids);++_i) {
        var _id=real(_ids[_i]),_name=string_delete(scrFRSkillKey(_id),1,6),
            _row={name:_name,id:_id};
        if(string_pos("Augment",_name)==1) array_push(_groups.augment,_row);
        else if(string_pos("SurgerySlot",_name)==1) array_push(_groups.surgery,_row);
        else if(string_pos("Burden",_name)==1) array_push(_groups.burden,_row);
        else throw "Mutation pool204 encountered an unclassified skill: "+_name;
    }
    assert(array_length(_groups.mini)==4 && array_length(_groups.hidden)==3
        && array_length(_groups.augment)==18 && array_length(_groups.surgery)==4
        && array_length(_groups.burden)==4,"Mutation pool204 omitted a registered exclusive category");
    return _groups;
}

function scrFRMutationPool204AssertOrdinary(_skill,_main,_groups) {
    assert(scr_skill_is_valid(_skill),"Normal mutation choice has invalid metadata");
    var _denied=[_groups.mini,_groups.hidden,_groups.surgery,_groups.burden];
    if(!_main) array_push(_denied,_groups.augment);
    for(var _g=0;_g<array_length(_denied);++_g)
        for(var _i=0;_i<array_length(_denied[_g]);++_i)
            assert(_denied[_g][_i].id!=_skill,
                "Exclusive mutation leaked into real normal selection: "+_denied[_g][_i].name);
}

function scrFRMutationPool204Draw(_selection,_surface) {
    var _set=false;
    try {
        surface_set_target(_surface);_set=true;draw_clear_alpha(c_black,0);
        with(_selection) event_perform(ev_draw,64);
    } finally {if(_set) surface_reset_target();}
}

function scrFRMutationPool204Pages(_rate,_main,_groups,_surface) {
    scrFRModSet("mod","Frontier_IDPD","settingMainPoolAugments",_main);
    GameCont.heavyheart=0;GameCont.wantheavy=false;
    var _selection=instance_create(0,0,LevCont),_row={rate:_rate,main_pool_augments:_main,
        pages:[],eligible_ids:[],ordinary_rolls:[],left_wrap:false,right_wrap:false},_seen=[];
    // Independently observe the public eligibility contract. Assertions below
    // also name every exclusive source group, so a weakened predicate fails.
    for(var _skill=1;_skill<=maxskill;++_skill)
        if(scr_skill_can_appear(_skill)) array_push(_row.eligible_ids,_skill);
    assert(array_length(_row.eligible_ids)>20,"Mutation pool204 normal positive controls are absent");
    var _count=(view_width-64) div 32,_pages=ceil(array_length(_row.eligible_ids)/_count);
    _selection.grillpage=-1;_selection.overgrilled=false;
    for(var _page=0;_page<_pages;++_page) {
        _selection.grillpadchange=1;
        scrFRMutationPool204Draw(_selection,_surface);
        assert(_selection.grillpage==_page,"Real Griller page navigation skipped a page");
        var _ids=[];
        for(var _i=0;_i<instance_number(SkillIcon);++_i) {
            var _icon=instance_find(SkillIcon,_i),_skill=_icon.skill;
            scrFRMutationPool204AssertOrdinary(_skill,_main,_groups);
            assert(scr_skill_can_appear(_skill) && array_get_index(_seen,_skill)<0,
                "Real Griller duplicated or bypassed normal eligibility");
            assert(_icon.xstart==_icon.x && _icon.ystart==_icon.y,
                "Filtered Griller pages lost the native icon hit-box alignment event");
            array_push(_ids,_skill);array_push(_seen,_skill);
        }
        assert(array_length(_ids)==min(_count,array_length(_row.eligible_ids)-_page*_count),
            "Real Griller page omitted an eligible ordinary mutation");
        array_push(_row.pages,_ids);
    }
    assert(array_length(_seen)==array_length(_row.eligible_ids),"Griller omitted a legal ordinary mutation");
    for(var _i=0;_i<array_length(_row.eligible_ids);++_i)
        assert(array_get_index(_seen,_row.eligible_ids[_i])>=0,"Griller failed complete filtered pool coverage");
    _selection.grillpadchange=1;scrFRMutationPool204Draw(_selection,_surface);
    _row.right_wrap=_selection.grillpage==0;
    _selection.grillpadchange=-1;scrFRMutationPool204Draw(_selection,_surface);
    _row.left_wrap=_selection.grillpage==_pages-1;
    assert(_row.right_wrap && _row.left_wrap,"Filtered Griller page arrows failed wraparound");
    instance_destroy(SkillIcon,false);instance_destroy(_selection,false);
    // Use the genuine randomized ordinary chooser after retiring page icons.
    // Neither its algorithm nor RNG is substituted by the test.
    repeat(256) {
        var _rolled=scrDecideSkill(true);
        scrFRMutationPool204AssertOrdinary(_rolled,_main,_groups);
        assert(scr_skill_can_appear(_rolled),"Real random chooser bypassed normal availability");
        array_push(_row.ordinary_rolls,_rolled);
    }
    if(_main) {
        var _augment_seen=false;
        for(var _a=0;_a<array_length(_groups.augment);++_a)
            _augment_seen|=array_get_index(_seen,_groups.augment[_a].id)>=0;
        assert(_augment_seen,"Explicit main-pool augment setting no longer enables its legal choices");
    }
    scrNTTESmokeLog("NTUF MUTATION POOL204 ROW "+json_stringify(_row));
    return _row;
}

function scrFRMutationPool204Special(_rate,_groups,_surface) {
    scrFRModSet("mod","Frontier_IDPD","settingMainPoolAugments",false);
    var _special={rate:_rate,rat_ids:[],rat_eligible:[],rat_natural_grants_passed:false,
        compassion_when_full:false,compassion_when_not_full:false,
        heavy_heart_when_ready:false,heavy_heart_when_not_ready:false,
        disabled_normal_excluded:false,idpd_station:{}};
    for(var _i=0;_i<array_length(_groups.mini);++_i) {
        var _id=_groups.mini[_i].id,_available=scrNTTEFullSkillAvailable(_id,true);
        assert(_available && !scr_skill_can_appear(_id),"Mini reward lost its exclusive Rat eligibility");
        array_push(_special.rat_ids,_id);array_push(_special.rat_eligible,_available);
    }
    var _player=instance_find(Player,0),_pet=instance_create(122000,122000,FRMarker);
    _player.ntte_pet_max=1;_player.ntte_pet=[];
    _special.compassion_when_not_full=scr_skill_can_appear(NTTEFullSkill.Compassion);
    _player.ntte_pet=[_pet];
    _special.compassion_when_full=scr_skill_can_appear(NTTEFullSkill.Compassion);
    assert(!_special.compassion_when_not_full && _special.compassion_when_full,
        "Normal mutation filter removed the original full-pet Compassion condition");
    instance_destroy(_pet,false);_player.ntte_pet=[];
    // The native selector has its own earned Heavy Heart injection. Retain
    // that legal reward while using filtered ordinary pages for everything else.
    GameCont.heavyheart=3;GameCont.wantheavy=false;
    var _selection=instance_create(0,0,LevCont);_selection.grillpage=-1;
    repeat(5) {
        _selection.grillpadchange=1;scrFRMutationPool204Draw(_selection,_surface);
        with(SkillIcon) if(skill==mut_heavy_heart) _special.heavy_heart_when_ready=true;
    }
    assert(_special.heavy_heart_when_ready,"Filtered Griller removed earned Heavy Heart");
    instance_destroy(SkillIcon,false);instance_destroy(_selection,false);
    GameCont.heavyheart=0;GameCont.wantheavy=false;
    scrFRSkillSetActive(mut_extra_feet,false);
    _selection=instance_create(0,0,LevCont);_selection.grillpage=-1;
    _special.disabled_normal_excluded=true;
    repeat(5) {
        _selection.grillpadchange=1;scrFRMutationPool204Draw(_selection,_surface);
        with(SkillIcon) {
            if(skill==mut_heavy_heart) _special.heavy_heart_when_not_ready=true;
            if(skill==mut_extra_feet) _special.disabled_normal_excluded=false;
        }
    }
    assert(!_special.heavy_heart_when_not_ready && _special.disabled_normal_excluded,
        "Griller ignored Heavy Heart progression or source pool deactivation");
    scrFRSkillSetActive(mut_extra_feet,true);
    instance_destroy(SkillIcon,false);instance_destroy(_selection,false);
    // Existing regression drives each real Rat chest's shuffled stock,
    // purchase prompt, native Orchid ball grant, Continue and expiry.
    scrNTTEFullRatRewardNaturalTests();
    _special.rat_natural_grants_passed=true;
    // This is the real source station constructor and its real first Step.
    // Its source coroutine applies the grant before its first visual wait.
    var _new="AugmentEuphoria",_old=scrFRModCall("skill",_new,"skill_augment"),
        _new_id=scrFRSkillResolve(_new);
    scrFRSetSkill(_old,1);
    var _station=scrFRInvoke(GameCont,fr_Objects_Frontier_IDPD_mod_gml_AugmentStation_create,[122000,122000]);
    with(_station) {
        augment=_new;newskill=_new;oldskill=_old;
        augmentname=scrFRModCall("skill",_new,"skill_name");
        description=scrFRModCall("skill",_new,"skill_text");pick=1;
        event_perform(ev_step,ev_step_normal);
    }
    _special.idpd_station={grant_name:_new,grant_id:_new_id,base_id:_old,
        opened:_station.opened,grant_count:scrFRGetSkill(_new),base_count:scrFRGetSkill(_old),
        base_deactivated:!scrFRSkillActive(_old),ordinary_available:scr_skill_can_appear(_new_id)};
    assert(_special.idpd_station.opened && _special.idpd_station.grant_count==1
        && _special.idpd_station.base_count==0 && _special.idpd_station.base_deactivated
        && !_special.idpd_station.ordinary_available,
        "Normal pool repair changed the real HQ station's exclusive replacement grant");
    instance_destroy(_station,false);scrFRSetSkill(_new,0);scrFRSkillSetActive(_old,true);
    scrNTTESmokeLog("NTUF MUTATION POOL204 SPECIAL "+json_stringify(_special));
    return _special;
}

function scrFRMutationPool204Tests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(GameCont) && instance_exists(Player) && !instance_exists(GenCont),
        "Mutation pool204 requires the settled isolated desktop harness");
    var _before=scrNTTEFullInstances(all),_game=scrNTTEFullAreaGeneratorSnapshot(GameCont),
        _players=scrNTTEFullAreaGeneratorSnapshot(Player),_keys={nodes:[]},_graph={nodes:[]},
        _skills=ds_list_create(),_seed=random_get_seed(),_rng=scrNTTEFullArrayCopy(global.rng_state),
        _tasks=scrNTTEFullArrayCopy(global.fr_tasks),_pool=global.fr_skill_pool,
        _ready=global.ntte_full_feature_ready,_griller=UberCont.opt_griller,
        _console=global.console_active,_stop=lockstep_stop,_scale=timescale,
        _vx=view_xview,_vy=view_yview,_paused=UberCont.paused,
        _hidden=scrNTTEFullInstances([LevCont,SkillIcon,CrownIcon,UltraIcon,Cinematic]),
        _surface=surface_create(view_width,view_height),_groups=scrFRMutationPool204Groups(),
        _rows=[],_special=[];
    assert(surface_exists(_surface),"Mutation pool204 Draw GUI target allocation failed");
    scrNTTEFullAreaSnapshotContainer(KeyCont,_keys);
    scrNTTEFullAreaSnapshotContainer(global.fr_module_vars,_graph);
    try {
        for(var _i=0;_i<array_length(_hidden);++_i) instance_deactivate_object(_hidden[_i]);
        lockstep_stop=false;UberCont.opt_griller=true;UberCont.paused=false;global.console_active=true;
        GameCont.skills=_skills;GameCont.ntte_full_skills={};GameCont.ntte_full_skill_order=[];
        GameCont.ntte_full_native_skill_counts={};GameCont.fr_skills={};global.fr_skill_pool={};
        GameCont.crown=Crown.None;GameCont.skillpoints=1;GameCont.crownpoints=0;GameCont.ultrapoints=0;
        GameCont.patiencepick=false;GameCont.codpick=false;GameCont.area=area_desert;
        global.ntte_full_feature_ready={};
        for(var _id=30;_id<=37;++_id)
            global.ntte_full_feature_ready[$ "skill:"+scrNTTEFullSkillKey(_id)]=true;
        with(Player) {ntte_pet=[];ntte_pet_max=1;}
        for(var _rate=30;_rate<=60;_rate+=30) {
            global.time_scale=30/_rate;
            array_push(_rows,scrFRMutationPool204Pages(_rate,false,_groups,_surface));
            array_push(_rows,scrFRMutationPool204Pages(_rate,true,_groups,_surface));
            array_push(_special,scrFRMutationPool204Special(_rate,_groups,_surface));
        }
        var _file=file_text_open_write(working_directory+"frontier-mutation-pool204.json");
        file_text_write_string(_file,json_stringify({status:"PASS",rates:[30,60],groups:_groups,
            rows:_rows,special:_special,physical_device_tested:false,
            actual_levcont_draw_gui:true,actual_random_chooser:true,
            actual_rat_reward_grants:true,actual_idpd_station_grants:true}));
        file_text_close(_file);
        scrNTTESmokeLog("PASS NTUF MUTATION POOL204 actual native pages,normal rolls,exclusive Rat and HQ grants30/60");
    } finally {
        scrNTTEFullMergedRuntimeTestCleanup(_before);
        for(var _i=0;_i<array_length(_hidden);++_i) instance_activate_object(_hidden[_i]);
        scrNTTEFullAreaGeneratorRestore(_game);scrNTTEFullAreaGeneratorRestore(_players);
        scrNTTEFullAreaGeneratorRestore({instances:[],containers:_keys.nodes});
        scrNTTEFullAreaGeneratorRestore({instances:[],containers:_graph.nodes});
        global.fr_tasks=_tasks;global.fr_skill_pool=_pool;global.ntte_full_feature_ready=_ready;
        global.rng_state=_rng;random_set_seed(_seed);global.time_scale=_scale;
        UberCont.opt_griller=_griller;UberCont.paused=_paused;global.console_active=_console;
        lockstep_stop=_stop;view_xview=_vx;view_yview=_vy;
        if(surface_exists(_surface)) surface_free(_surface);
        if(ds_exists(_skills,ds_type_list)) ds_list_destroy(_skills);
    }
}
