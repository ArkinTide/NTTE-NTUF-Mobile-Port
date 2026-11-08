// Actual Heart Destroy -> synchronous GenCont.Create -> Cove.area_setup.
// Controllers are private fixture instances; the harness's original camera
// controllers and surfaces remain parked until the full fixture is restored.
function scrFRInRoomFrontierTestsLimit() {
    goal=16;safedist=0;
    with(FloorMaker) goal=16;
}

function scrFRInRoomFrontierTestsConfigure(_state,_seed) {
    scrFRWallFixTestsReset(_state);
    // The shared reset creates controllers under the harness area. Replace
    // only those private fixture instances, so Sewers really creates its
    // native dark surface and the old-surface preservation control is live.
    with(TopCont) {
        if(surface_exists(dark)) surface_free(dark);
        instance_destroy();
    }
    instance_destroy(SubTopCont,false);instance_destroy(BackCont,false);
    return scrNTTEFullInRoomOverlapConfigure(_state,_seed);
}

function scrFRInRoomFrontierTestsControllers() {
    assert(instance_number(BackCont)==1 && instance_number(TopCont)==1
        && instance_number(SubTopCont)==1,"Cove fixture did not start with one real native controller set");
    var _back=instance_find(BackCont,0),_top=instance_find(TopCont,0),
        _sub=instance_find(SubTopCont,0),_marker=make_color_rgb(19,121,207),
        _shadow=make_color_rgb(79,113,47),_target=surface_get_target(),
        _color=draw_get_color(),_alpha=draw_get_alpha();
    assert(surface_exists(_back.shad) && _back.area==area_sewers
        && _top.darkness && surface_exists(_top.dark),
        "Fixture Sewers controllers have no real native shadow/dark surface");
    try {
        surface_set_target(_back.shad);draw_clear_alpha(_marker,1);
        surface_reset_target();
    } finally {
        if(surface_get_target()==_back.shad) surface_reset_target();
        if(_target>=0 && surface_get_target()!=_target) surface_set_target(_target);
        draw_set_color(_color);draw_set_alpha(_alpha);
    }
    _back.shadow_color=_shadow;
    return {back:_back,top:_top,sub:_sub,shadow:_shadow,shad:_back.shad,
        shadow_pixel:surface_getpixel_ext(_back.shad,2,2),dark:_top.dark,
        dark_live:surface_exists(_top.dark),darkness:_top.darkness};
}

function scrFRInRoomFrontierTestsCamera(_seed) {
    view_xview=539536+_seed;view_yview=539328+_seed;
    var _camera=view_camera[0];
    camera_set_view_pos(_camera,view_xview-7,view_yview-11);
    return {camera:_camera,x:view_xview,y:view_yview,cx:camera_get_view_x(_camera),
        cy:camera_get_view_y(_camera),letterbox:UberCont.letterbox,frame:UberCont.letterbox_frame};
}

function scrFRInRoomFrontierTestsCameraAssert(_camera) {
    assert(view_camera[0]==_camera.camera && view_xview==_camera.x && view_yview==_camera.y
        && camera_get_view_x(_camera.camera)==_camera.cx && camera_get_view_y(_camera.camera)==_camera.cy
        && UberCont.letterbox==_camera.letterbox && UberCont.letterbox_frame==_camera.frame,
        "Actual Cove generation leaked its temporary camera or loading-screen state");
}

function scrFRInRoomFrontierTests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),
        "Cove in-room regression requires the settled isolated native runner");
    var _map=UberCont.saveData,_bytes=ds_map_write(_map),_fixture_map=ds_map_create(),
        _state=scrNTTEFullWorldEventsNaturalWorldCapture(),_old_back=scrNTTEFullInstances(BackCont),
        _dark_surfaces=[],_seeds=[7,41,99],_cove=scrFRAreaResolve("cove"),_rows=[];
    ds_map_copy(_fixture_map,_map);UberCont.saveData=_fixture_map;
    // NaturalWorldCapture already parks TopCont/SubTopCont but leaves the
    // independent BackCont alive. Park it too so setArea=true may legitimately
    // dispose of its old fixture controller without losing the real harness.
    for(var _i=0;_i<array_length(_old_back);++_i) {
        array_push(_state.parked,_old_back[_i]);instance_deactivate_object(_old_back[_i]);
    }
    try {
        for(var _case=0;_case<array_length(_seeds);++_case) {
            var _seed=_seeds[_case],_origin=scrFRInRoomFrontierTestsConfigure(_state,_seed),
                _controls=scrFRInRoomFrontierTestsControllers(),
                _camera=scrFRInRoomFrontierTestsCamera(_seed),
                _far=instance_create(_origin[0]-2048,_origin[1],Floor),
                _far_sprite=_far.sprite_index,_far_area=_far.area,
                _background=make_color_rgb(34,61,73),_player=instance_find(Player,0),
                _px=_player.x,_py=_player.y;
            if(_controls.dark_live) array_push(_dark_surfaces,_controls.dark);
            background_set_colour(_background);
            random_set_seed(_seed);
            var _bullet=instance_create(_origin[0]+96,_origin[1]+48,NTTEFullCrystalHeartBullet);
            _bullet.area=_cove;_bullet.subarea=1;_bullet.loops=0;
            _bullet.area_goal=16;_bullet.area_seed=_seed;_bullet.direction=0;
            _bullet.area_chest=[];_bullet.area_chest_pos="furthest";_bullet.area_chaos=false;
            // The genuine Destroy event enters GenCont.Create, whose source
            // Cove.area_setup writes BackCont.shadow_color immediately.
            instance_destroy(_bullet);
            assert(!instance_exists(_bullet) && !instance_exists(GenCont) && !instance_exists(FloorMaker),
                "Real Cove Heart Destroy did not complete synchronous native generation");
            assert(instance_number(BackCont)==1 && instance_find(BackCont,0)==_controls.back
                && instance_number(TopCont)==1 && instance_find(TopCont,0)==_controls.top
                && instance_number(SubTopCont)==1 && instance_find(SubTopCont,0)==_controls.sub,
                "setArea=false Cove orb lost old controllers or retained temporary duplicates");
            assert(_controls.back.shad==_controls.shad && surface_exists(_controls.shad)
                && surface_getpixel_ext(_controls.shad,2,2)==_controls.shadow_pixel
                && _controls.back.shadow_color==_controls.shadow
                && _controls.top.dark==_controls.dark && _controls.top.darkness==_controls.darkness
                && (!_controls.dark_live || surface_exists(_controls.dark)),
                "Cove orb changed an old controller's native surface identity/pixels or shadow/darkness");
            assert(GameCont.area==area_sewers && GameCont.subarea==1 && GameCont.loops==0
                && GameCont.maxsubarea==scrAreaGetMaxSubarea(area_sewers) && !GameCont.finalsubarea
                && !GameCont.underwater && scrFRWallBackgroundColor()==_background
                && _player.x==_px && _player.y==_py
                && instance_exists(_far) && _far.area==_far_area && _far.sprite_index==_far_sprite,
                "Cove Heart leaked target context, moved the old player or repainted distant old terrain");
            var _cove_floors=0;with(Floor) if(area==_cove) _cove_floors+=1;
            assert(_cove_floors>0,"Cove Heart fixture did not build any real target floor");
            scrFRInRoomFrontierTestsCameraAssert(_camera);
            var _row={seed:_seed,set_area:false,rate:30/timescale,target_floors:_cove_floors,
                old_controller_identity:true,old_surface_pixels:true,old_shadow:true,
                old_map_context:true,camera_preserved:true,controller_counts:[1,1,1]};
            array_push(_rows,_row);scrNTTESmokeLog("NTUF COVE INROOM "+json_stringify(_row));
        }
        var _origin=scrFRInRoomFrontierTestsConfigure(_state,173),
            _controls=scrFRInRoomFrontierTestsControllers(),
            _camera=scrFRInRoomFrontierTestsCamera(173);
        if(_controls.dark_live) array_push(_dark_surfaces,_controls.dark);
        random_set_seed(173);
        // Also exercise the genuine setArea=true controller ownership branch.
        scrNTTEFullAreaGenerateNative(_cove,1,0,_origin[0]+96,_origin[1]+48,true,0,scrFRInRoomFrontierTestsLimit);
        assert(!instance_exists(GenCont) && !instance_exists(FloorMaker)
            && GameCont.area==_cove && GameCont.subarea==1 && GameCont.loops==0,
            "setArea=true Cove generation did not adopt its real target context");
        var _back=instance_find(BackCont,0),_top=instance_find(TopCont,0);
        assert(instance_number(BackCont)==1 && instance_number(TopCont)==1 && instance_number(SubTopCont)==1
            && _back!=_controls.back && !instance_exists(_controls.back)
            && _top!=_controls.top && !instance_exists(_controls.top)
            && !instance_exists(_controls.sub),
            "setArea=true Cove failed to retain only its newly generated native controllers");
        assert(_back.area==_cove && surface_exists(_back.shad)
            && _back.shadow_color==scrFRAreaMetadata(_cove,"area_shadow_color",c_white)
            && _top.darkness==scrFRAreaMetadata(_cove,"area_darkness",false)
            && surface_exists(_top.dark),
            "New Cove controllers did not receive authored setup shadow/darkness or real native surfaces");
        array_push(_dark_surfaces,_top.dark);
        scrFRInRoomFrontierTestsCameraAssert(_camera);
        var _row={seed:173,set_area:true,rate:30/timescale,new_controller_only:true,
            target_shadow:true,target_dark_surface:true,camera_preserved:true,controller_counts:[1,1,1]};
        array_push(_rows,_row);scrNTTESmokeLog("NTUF COVE INROOM "+json_stringify(_row));
    } finally {
        scrNTTEFullMergedRuntimeTestCleanup(_state.before);
        for(var _i=0;_i<array_length(_dark_surfaces);++_i)
            if(surface_exists(_dark_surfaces[_i])) surface_free(_dark_surfaces[_i]);
        scrNTTEFullWorldEventsNaturalWorldRestore(_state);
        UberCont.saveData=_map;if(ds_exists(_fixture_map,ds_type_map)) ds_map_destroy(_fixture_map);
        assert(ds_map_write(_map)==_bytes,"Cove in-room fixture changed original permanent save bytes");
    }
    scrNTTESmokeLog("PASS NTUF COVE actual Heart Destroy/native GenCont source setup:3 preserved old-controller/surface/shadow/camera/local-map seeds and1 target-controller replacement "+json_stringify(_rows));
}
