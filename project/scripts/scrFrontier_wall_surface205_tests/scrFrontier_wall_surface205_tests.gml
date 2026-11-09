// Render the real wall-top pass against the source edge order. Compact fill
// is physical background and must not crop or repaint the authored boundary.
function scrFRWallSurface205Capture(_actual,_wall,_x,_y) {
    var _surface=-1,_buffer=-1,_camera=-1,_success=false,_target=surface_get_target(),
        _world=matrix_get(matrix_world),_view=matrix_get(matrix_view),_projection=matrix_get(matrix_projection),
        _color=draw_get_color(),_alpha=draw_get_alpha(),_shader=shader_current();
    gpu_push_state();
    try {
        _surface=surface_create(128,96);_buffer=buffer_create(128*96*4,buffer_fixed,1);
        _camera=camera_create_view(_x-48,_y-40,128,96,0,noone,-1,-1,-1,-1);
        surface_set_target(_surface);camera_apply(_camera);matrix_set(matrix_world,matrix_build_identity());
        shader_reset();gpu_set_fog(false,0,0,0);gpu_set_blendmode(bm_normal);gpu_set_texfilter(false);
        draw_set_color(c_white);draw_set_alpha(1);draw_clear_alpha(c_black,0);
        if(_actual==1) with(SubTopCont) event_perform(ev_draw,0);
        else {
            // Independent expected order: background -> source outline -> cap.
            if(_actual!=2) scrNTTESolidWallDraw();
            with(_wall) {
                draw_sprite_part_ext(outspr,outindex,l,r,w,h,
                    x-4+l,y-12+r,image_xscale,image_yscale,image_blend,image_alpha);
                draw_sprite_ext(topspr,topindex,x,y-8,1,1,0,image_blend,1);
            }
            if(_actual==2) scrNTTESolidWallDraw();
        }
        assert(real(surface_get_target())==real(_surface),"Wall205 actual draw lost its render target");
        surface_reset_target();buffer_get_surface(_buffer,_surface,0);_success=true;
        return {surface:_surface,pixels:_buffer,width:128,height:96};
    } finally {
        if(surface_get_target()==_surface) surface_reset_target();
        if(_target>=0 && surface_get_target()!=_target) surface_set_target(_target);
        if(_camera>=0) camera_destroy(_camera);
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);matrix_set(matrix_projection,_projection);
        gpu_pop_state();if(_shader<0) shader_reset();else shader_set(_shader);
        draw_set_color(_color);draw_set_alpha(_alpha);
        if(!_success) {
            if(surface_exists(_surface)) surface_free(_surface);
            if(buffer_exists(_buffer)) buffer_delete(_buffer);
        }
    }
}

function scrFRWallSurface205Tests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled()
        && instance_exists(Player) && !instance_exists(GenCont),"Wall205 requires the isolated settled runner");
    var _state=scrNTTEFullWorldEventsNaturalWorldCapture(),_old_walls=global.lis_walls_visible,
        _old_floors=global.lis_floors_visible,_old_fill=scrNTTEFullValue(UberCont,"ntte_fill_visible",undefined),
        _walls=ds_list_create(),_floors=ds_list_create(),_lock=lockstep_stop,
        _actual=undefined,_reference=undefined,_control=undefined,_rows=[],
        _areas=[0,1,2,3,4,5,6,7,100,101,102,103,104,105,106,107,
            201,202,203,204,205,206,207,301,302,303,304,305,306],
        _map=UberCont.saveData,_map_bytes=ds_map_write(_map);
    global.lis_walls_visible=_walls;global.lis_floors_visible=_floors;lockstep_stop=false;
    try {
        for(var _a=0;_a<array_length(_areas);++_a) {
            scrFRWallFixTestsReset(_state);GameCont.area=_areas[_a];GameCont.subarea=1;
            var _x=627000,_y=627000,_floor=instance_create(_x,_y+16,Floor),
                _wall=instance_create(_x,_y,Wall);
            with(_wall) {mcr_wall_update_lrwh;}
            var _original=[_wall.l,_wall.r,_wall.w,_wall.h],
                _left=scrNTTESolidWallBlock(_x-64,_y-64,64,128),
                _right=scrNTTESolidWallBlock(_x+16,_y-64,64,80),
                _above=scrNTTESolidWallBlock(_x,_y-64,16,64);
            with(_wall) {mcr_wall_update_lrwh;}
            assert(_wall.l==_original[0] && _wall.r==_original[1]
                && _wall.w==_original[2] && _wall.h==_original[3],
                "Compact collision cropped source boundary art in area "+string(_areas[_a]));
            // Still respect a true solid neighbouring wall and the real actor
            // collision mask. The helper is only for the art-clipping macro.
            var _solid=instance_create(_x-16,_y,Wall),_blocked=false;
            with(_wall) _blocked=!scrFRWallArtFree205(x-16,y);
            assert(_blocked,"Wall205 clipping ignored a true authored solid neighbour");
            instance_destroy(_solid,false);
            assert(position_meeting(_x-24,_y+8,Wall)
                && _left.solid && _left.ntte_fill_width==64,
                "Wall205 art repair removed physical exterior collision");
            ds_list_clear(_walls);ds_list_add(_walls,_wall);
            UberCont.ntte_fill_visible=[_left,_right,_above];
            _actual=scrFRWallSurface205Capture(true,_wall,_x,_y);
            _reference=scrFRWallSurface205Capture(false,_wall,_x,_y);
            assert(scrFRVisualSamePixels(_actual,_reference),
                "Compact fill covered source wall outlines/cap in area "+string(_areas[_a]));
            _control=scrFRWallSurface205Capture(2,_wall,_x,_y);
            if(_areas[_a]==1) assert(!scrFRVisualSamePixels(_reference,_control),
                "Wall205 source outline fixture did not expose the old fill-over-art error");
            if(_a==0 || _areas[_a]==7 || _areas[_a]==206) {
                scrFRVisualSave(_actual,"frontier-wall-surface205-area"+string(_areas[_a])+".png");
                scrFRVisualSave(_reference,"frontier-wall-surface205-reference"+string(_areas[_a])+".png");
            }
            array_push(_rows,{area:_areas[_a],source_clip:_original,actual_native_draw:true,
                physical_collision_retained:true,reference_pixels_equal:true});
            scrFRVisualFree(_actual);scrFRVisualFree(_reference);scrFRVisualFree(_control);
            _actual=undefined;_reference=undefined;_control=undefined;
        }
    } finally {
        scrFRVisualFree(_actual);scrFRVisualFree(_reference);scrFRVisualFree(_control);
        scrNTTEFullWorldEventsNaturalWorldRestore(_state);
        global.lis_walls_visible=_old_walls;global.lis_floors_visible=_old_floors;UberCont.ntte_fill_visible=_old_fill;
        lockstep_stop=_lock;
        if(ds_exists(_walls,ds_type_list)) ds_list_destroy(_walls);
        if(ds_exists(_floors,ds_type_list)) ds_list_destroy(_floors);
        assert(ds_map_write(_map)==_map_bytes,"Wall205 test changed the persistent save");
    }
    var _file=file_text_open_write(working_directory+"frontier-wall-surface205.json");
    file_text_write_string(_file,json_stringify({status:"PASS",physical_device_tested:false,rows:_rows}));
    file_text_close(_file);
    scrNTTESmokeLog("PASS WALL SURFACE205 actual native art/collision, all29 area styles and independent GPU reference");
}
