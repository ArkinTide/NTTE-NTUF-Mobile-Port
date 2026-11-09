// Desktop-only regression: the actual selection-menu consumer must draw the
// declared loadout portrait, not its smaller in-game weapon fallback.
function scrFRLoadoutArt204Capture(_kind,_weapon,_sprite) {
    var _surface=-1,_buffer=-1,_camera=-1,_target=false,_success=false;
    var _world=matrix_get(matrix_world),_view=matrix_get(matrix_view),_projection=matrix_get(matrix_projection),
        _colour=draw_get_color(),_alpha=draw_get_alpha(),_shader=shader_current();
    gpu_push_state();
    try {
        _surface=surface_create(128,128);_buffer=buffer_create(128*128*4,buffer_fixed,1);
        _camera=camera_create_view(0,0,128,128,0,noone,-1,-1,-1,-1);
        assert(surface_exists(_surface) && buffer_exists(_buffer),"Loadout art204 capture allocation failed");
        surface_set_target(_surface);_target=true;camera_apply(_camera);
        matrix_set(matrix_world,matrix_build_identity());shader_reset();
        gpu_set_blendmode(bm_normal);gpu_set_texfilter(false);gpu_set_fog(false,0,0,0);
        draw_set_alpha(1);draw_set_color(c_white);draw_clear_alpha(c_black,0);
        switch(_kind) {
            case "control":draw_set_color(c_lime);draw_rectangle(0,0,15,15,false);break;
            case "consumer":scrLoadoutDrawWeapon(_weapon,64,64,c_white);break;
            case "portrait":draw_sprite_ext(_sprite,0,64,64,1,1,0,c_white,1);break;
            case "fallback":
                var _ox=sprite_get_xoffset(_sprite),_oy=sprite_get_yoffset(_sprite);
                try {
                    sprite_set_offset(_sprite,sprite_get_width(_sprite) div 2,sprite_get_height(_sprite) div 2);
                    draw_sprite_ext(_sprite,0,64,64,2,2,30,c_white,1);
                } finally {sprite_set_offset(_sprite,_ox,_oy);}
                break;
            case "empty":break;
            default:throw "Unknown loadout art204 capture kind";
        }
        assert(real(surface_get_target())==real(_surface),"Loadout consumer changed its GPU target");
        surface_reset_target();_target=false;buffer_get_surface(_buffer,_surface,0);
        var _coverage=0,_ink=0;
        for(var _at=0;_at<128*128*4;_at+=4) {
            if(buffer_peek(_buffer,_at+3,buffer_u8)==0) continue;
            ++_coverage;
            var _brightness=buffer_peek(_buffer,_at,buffer_u8)+buffer_peek(_buffer,_at+1,buffer_u8)+buffer_peek(_buffer,_at+2,buffer_u8);
            if(_brightness>48) {
                _ink+=1;
            }
        }
        _success=true;
        return {surface:_surface,pixels:_buffer,coverage:_coverage,ink:_ink};
    } finally {
        if(_target) surface_reset_target();
        if(_camera>=0) camera_destroy(_camera);
        gpu_pop_state();if(_shader<0) shader_reset();else shader_set(_shader);
        matrix_set(matrix_world,_world);matrix_set(matrix_view,_view);matrix_set(matrix_projection,_projection);
        draw_set_color(_colour);draw_set_alpha(_alpha);
        if(!_success) {
            if(surface_exists(_surface)) surface_free(_surface);
            if(buffer_exists(_buffer)) buffer_delete(_buffer);
        }
    }
}

function scrFRLoadoutArt204Same(_a,_b) {
    for(var _at=0;_at<128*128*4;_at+=4)
        if(buffer_peek(_a.pixels,_at,buffer_u32)!=buffer_peek(_b.pixels,_at,buffer_u32)) return false;
    return true;
}

function scrFRLoadoutArt204Tests() {
    assert(os_type==os_windows && scrNTTEFullSmokeEnabled() && scrFREnabled(),
        "Loadout art204 checks require the settled isolated native desktop runner");
    var _ids=variable_struct_get_names(global.fr_weapon_keys),_gameplay=[],_captures=[],_rows=[],_phases=[],_fallback=noone;
    for(var _i=0;_i<array_length(_ids);++_i) {
        var _weapon=real(_ids[_i]);
        array_push(_gameplay,{weapon:_weapon,sprite:scr_weapon_get_sprite(_weapon)});
        if(global.fr_weapon_keys[$ _ids[_i]]=="weapon:FR_StarPistol") _fallback=_weapon;
    }
    assert(_fallback!=noone,"Loadout art204 has no ordinary source fallback control");
    try {
        var _control=scrFRLoadoutArt204Capture("control",0,0);array_push(_captures,_control);
        var _empty=scrFRLoadoutArt204Capture("empty",0,0);array_push(_captures,_empty);
        assert(_control.coverage==256 && _control.ink==256 && _empty.coverage==0,
            "Loadout art204 GPU positive/transparent controls failed");
        for(var _phase=0;_phase<3;++_phase) {
            if(_phase==1) scrFRWeaponsRefresh();
            if(_phase==2) scrWeapons();
            var _declared=0,_cutlass=false,_shovel=false,_no_art=0;
            for(var _i=0;_i<array_length(_ids);++_i) {
                var _weapon=real(_ids[_i]),_key=global.fr_weapon_keys[$ _ids[_i]],
                    _code=global.fr_module_scripts[$ _key][$ "weapon_loadout"],
                    _sprite=scr_weapon_get_loadout_sprite(_weapon);
                assert(scr_weapon_get_sprite(_weapon)==_gameplay[_i].sprite,
                    "Replaying loadout artwork changed a gameplay weapon sprite: "+_key);
                if(is_undefined(_code)) {
                    assert(_sprite==-1,"Weapon without authored portrait lost native -1 fallback: "+_key);
                    ++_no_art;continue;
                }
                ++_declared;
                var _expected=scrFRWeaponProperty(_key,"weapon_loadout",-1);
                assert(_sprite==_expected && sprite_exists(_sprite),
                    "Authored loadout artwork was absent from the real native metadata table: "+_key);
                if(_key=="weapon:FR_BubblesCutlass") {
                    _cutlass=true;
                    assert(_sprite==sprFR_sprBubblesCutlassLoadout_a3f9cae1b4d8,
                        "Bubbles cutlass does not use its authored packaged loadout portrait");
                }
                if(_key=="weapon:FR_BubblesShovel") {
                    _shovel=true;
                    assert(_sprite==sprFR_sprBubblesShovelLoadout_b0d98bdf1533,
                        "Bubbles B shovel does not use its authored packaged loadout portrait");
                }
                var _ox=sprite_get_xoffset(scr_weapon_get_sprite(_weapon)),
                    _oy=sprite_get_yoffset(scr_weapon_get_sprite(_weapon)),
                    _actual=scrFRLoadoutArt204Capture("consumer",_weapon,_sprite),
                    _expected_pixels=scrFRLoadoutArt204Capture("portrait",_weapon,_sprite),
                    _gameplay_pixels=scrFRLoadoutArt204Capture("fallback",_weapon,scr_weapon_get_sprite(_weapon));
                array_push(_captures,_actual,_expected_pixels,_gameplay_pixels);
                assert(_actual.coverage>20 && _actual.ink>10 && scrFRLoadoutArt204Same(_actual,_expected_pixels),
                    "Real selection consumer failed to draw visible exact authored portrait pixels: "+_key);
                assert(!scrFRLoadoutArt204Same(_actual,_gameplay_pixels),
                    "Loadout art204 accidentally accepted the gameplay fallback as portrait: "+_key);
                assert(sprite_get_xoffset(scr_weapon_get_sprite(_weapon))==_ox
                    && sprite_get_yoffset(scr_weapon_get_sprite(_weapon))==_oy,
                    "Selection portrait checks changed a live gameplay sprite origin");
                if(_phase==0) surface_save(_actual.surface,working_directory+"frontier-loadout-art204-"+string(_weapon)+".png");
                array_push(_rows,{phase:_phase,key:_key,weapon:_weapon,portrait:sprite_get_name(_sprite),
                    coverage:_actual.coverage,ink:_actual.ink,exact_authored_pixels:true,gameplay_fallback_rejected:true});
            }
            assert(_declared>=2 && _cutlass && _shovel && _no_art>0,
                "Loadout art204 omitted source declarations or the no-art fallback family");
            var _fallback_actual=scrFRLoadoutArt204Capture("consumer",_fallback,-1),
                _fallback_expected=scrFRLoadoutArt204Capture("fallback",_fallback,scr_weapon_get_sprite(_fallback));
            array_push(_captures,_fallback_actual,_fallback_expected);
            assert(_fallback_actual.coverage>5 && scrFRLoadoutArt204Same(_fallback_actual,_fallback_expected),
                "An ordinary source weapon without a portrait lost its original gameplay-sprite fallback");
            var _phase_row={phase:_phase,declared:_declared,absent_callbacks:_no_art,
                checked_weapons:array_length(_ids),all_gameplay_sprites_unchanged:true,
                ordinary_fallback_pixels_verified:true,ordinary_fallback_coverage:_fallback_actual.coverage};
            array_push(_phases,_phase_row);
            scrNTTESmokeLog("LOADOUT ART204 "+json_stringify(_phase_row));
        }
        var _file=file_text_open_write(working_directory+"frontier-loadout-art204.json");
        file_text_write_string(_file,json_stringify({status:"PASS",rows:_rows,phases:_phases,
            control_coverage:_control.coverage,control_ink:_control.ink,empty_coverage:_empty.coverage,
            refresh_and_native_rebuild_verified:true,all_declared_callbacks_checked:true}));file_text_close(_file);
    } finally {
        for(var _i=0;_i<array_length(_captures);++_i) {
            if(surface_exists(_captures[_i].surface)) surface_free(_captures[_i].surface);
            if(buffer_exists(_captures[_i].pixels)) buffer_delete(_captures[_i].pixels);
        }
    }
    scrNTTESmokeLog("PASS FRONTIER authored loadout portraits: all source callbacks, genuine native consumer GPU pixels, refresh/rebuild and no-art fallback");
}
