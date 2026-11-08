// The real Heart Destroy/GenCont paths below are supplied by WallFixTests.
// The independent topology oracle never invokes the production edge predicate.
function scrFROrbWallTestsGenerated(_before,_seed,_pass) {
    var _tops=scrNTTEFullInstances(TopSmall),_walls=scrNTTEFullInstances(Wall),_new=0,_target=0;
    for(var _i=0;_i<array_length(_tops);++_i) {
        var _top=_tops[_i];
        if(array_get_index(_before,_top)>=0) continue;
        _new+=1;if(_top.area==206) _target+=1;
        var _supported=false;
        for(var _j=0;_j<array_length(_walls);++_j) {
            var _wall=_walls[_j];
            if(_wall.object_index==NTTESolidWall || !_wall.solid) continue;
            // Original 16px transition cells may occupy any neighbour of a
            // real edge cell; the next ring is unsupported decorative roof.
            if(_wall.bbox_left<=_top.x+31 && _wall.bbox_right-1>=_top.x-16
                && _wall.bbox_top<=_top.y+31 && _wall.bbox_bottom-1>=_top.y-16) {
                _supported=true;break;
            }
        }
        assert(_supported,"Heart left a top-only wall beyond its real edge: "+json_stringify({
            seed:_seed,pass:_pass,x:_top.x,y:_top.y,object:object_get_name(_top.object_index)}));
    }
    var _authored=0,_target_walls=0;
    for(var _j=0;_j<array_length(_walls);++_j) {
        var _wall=_walls[_j];
        if(_wall.object_index==NTTESolidWall || !_wall.solid) continue;
        _authored+=1;if(_wall.area==206) _target_walls+=1;
    }
    scrNTTESmokeLog("NTUF ORB WALL before edge-survival assertion "+json_stringify({
        seed:_seed,pass:_pass,new_caps:_new,target_caps:_target,
        authored_walls:_authored,target_walls:_target_walls}));
    assert(_new>0 && _target>0,"Heart cap repair removed the actual new Red edge transition");
    scrNTTESmokeLog("NTUF ORB WALL real Destroy edge topology "+json_stringify({
        seed:_seed,pass:_pass,rate:30/timescale,new_caps:_new,target_caps:_target,unsupported_caps:0}));
}

function scrFROrbWallTestsLayoutControls(_state) {
    scrFRWallFixTestsReset(_state);
    GameCont.area=area_sewers;GameCont.subarea=1;
    var _x=618000,_y=618000,_wall=instance_create(_x,_y,Wall),
        _floor=instance_create(_x+256,_y,Floor),
        _pack=scrNTTESolidWallBlock(_x+16,_y+16,128,64);
    // The synchronous source generator creates caps while the old collision
    // is inactive, then activates it before its exact priority reconciliation.
    instance_deactivate_object(_pack);
    var _translated=instance_create(_x+16,_y+16,TopSmall);
    instance_activate_object(_pack);
    assert(instance_exists(_translated),"Cap layout fixture never built its real pre-activation cap");
    var _source_touch=false;
    with(_translated) _source_touch=place_meeting(x,y,_pack);
    assert(_source_touch && !scrFROrbWallMergeOccludes(_translated,_pack),
        "Cap merge control failed to distinguish the original raw compact collision from authored art");
    // Heart's later decoration runs with the pack active. Call the actual
    // TopSmall.Create again, rather than an emulation of its layout probe.
    var _live=instance_create(_x+16,_y+16,TopSmall),
        _blocked_wall=instance_create(_x,_y,TopSmall),
        _blocked_floor=instance_create(_x+256,_y,TopSmall);
    scrNTTESmokeLog("NTUF ORB WALL native cap layout controls "+json_stringify({
        source_raw_old_pack_touch:_source_touch,translated_cap:instance_exists(_translated),
        active_pack_cap:instance_exists(_live),real_wall_cap:instance_exists(_blocked_wall),
        real_floor_cap:instance_exists(_blocked_floor)}));
    assert(instance_exists(_live) && !instance_exists(_blocked_wall) && !instance_exists(_blocked_floor),
        "Real cap.Create confuses plain collision fill with authored art, or admits a true Wall/Floor overlap");
    _translated.x=_x;_translated.y=_y;
    assert(scrFROrbWallMergeOccludes(_translated,_wall),"Cap merge no longer respects an authored old wall");
    _translated.x=_x+256;
    assert(scrFROrbWallMergeOccludes(_translated,_floor),"Cap merge no longer respects an authored old floor");
    assert(instance_exists(_pack) && _pack.solid && _pack.ntte_fill_width==128
        && _pack.ntte_fill_height==64 && position_meeting(_x+32,_y+32,Wall),
        "Decorative layout repair mutated or removed plain packed collision");
    scrNTTESmokeLog("PASS NTUF ORB WALL real cap.Create and source merge positive/negative controls: compact collision survives beneath art; true Wall/Floor still occlude");
}

function scrFROrbWallTestsControls(_state) {
    scrFROrbWallTestsLayoutControls(_state);
    scrFRWallFixTestsReset(_state);
    GameCont.area=area_sewers;GameCont.subarea=1;
    var _x=619008,_y=619008,_color=make_color_rgb(34,61,73);
    background_set_colour(_color);
    var _old=instance_create(_x+256,_y,TopSmall),_old_sprite=_old.sprite_index,
        _old_color=_old.image_blend,_generation=instance_create(0,0,BulletHit),
        _wall=instance_create(_x,_y,Wall),_edge=instance_create(_x+16,_y,TopSmall),
        _orphan=instance_create(_x+48,_y,TopSmall),
        _pack=scrNTTESolidWallBlock(_x+32,_y,128,64),
        // Floor.Create materializes overlapping packed walls through the
        // actual terrain hook. Keep this preservation witness separate so
        // that event cannot legitimately replace the pack before pruning.
        _floor=instance_create(_x-128,_y+128,Floor),_wall_sprite=_wall.sprite_index,
        _floor_sprite=_floor.sprite_index,_pack_color=scrFRWallFillColor(_pack);
    assert(instance_exists(_old) && instance_exists(_edge) && instance_exists(_orphan),
        "Orb positive control failed to construct its actual native cap instances");
    var _removed=scrFROrbWallPruneTops(_generation);
    assert(_removed==1 && !instance_exists(_orphan) && instance_exists(_edge),
        "Orb cap repair did not distinguish plain packed exterior from a real edge transition");
    assert(instance_exists(_old) && _old.sprite_index==_old_sprite && _old.image_blend==_old_color,
        "Orb cap repair touched an old map's unsupported decorative cap");
    assert(instance_exists(_wall) && _wall.solid && _wall.sprite_index==_wall_sprite
        && instance_exists(_pack) && _pack.solid && _pack.ntte_fill_width==128
        && _pack.ntte_fill_height==64 && scrFRWallFillColor(_pack)==_pack_color
        && instance_exists(_floor) && _floor.sprite_index==_floor_sprite
        && position_meeting(_x+56,_y+8,Wall),
        "Orb cap pruning changed collision, authored wall/floor or old exterior colour");
    scrNTTESmokeLog("PASS NTUF ORB WALL positive controls: old cap identity/art retained, real edge transition retained, unsupported new cap removed, wall/floor and plain packed collision/colour unchanged");
}
