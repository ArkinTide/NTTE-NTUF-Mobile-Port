// World repairs are event driven. No whole-room enemy/terrain scan runs each
// frame: orb connectivity runs once after generation, and quest anchors are
// rebuilt only if their physical Floor instance was replaced.
function scrFRWorld213FiredMaggotLand() {
    if(scrNTTEFullValue(id,"fr_world213_landed",false)) return noone;
    fr_world213_landed=true;
    var _landed=noone;
    // Damage and native collision can be delivered in the same source tick.
    // A killed larva must not become a new live enemy at the following wall.
    if(hp>0) {
        _landed=instance_create(x,y,Maggot);
        _landed.givekill=0;
        with(_landed) motion_add(point_direction(other.x,other.y,x,y),4*timescale);
    }
    instance_destroy(id,false);
    return _landed;
}

function scrFRWorld213QuestFloorBind(_controller) {
    if(!instance_exists(_controller)) return false;
    var _floor=_controller.target;
    if(!instance_exists(_floor)) return false;
    _controller.fr_world213_floor={
        dx:_floor.x-_controller.x,dy:_floor.y-_controller.y,
        sprite:_floor.sprite_index,image:_floor.image_index,
        blend:_floor.image_blend,depth:_floor.depth};
    return true;
}

function scrFRWorld213QuestFloorEnsure(_controller) {
    if(!instance_exists(_controller)) return false;
    if(instance_exists(_controller.target)) return true;
    var _saved=scrNTTEFullValue(_controller,"fr_world213_floor",undefined);
    if(!is_struct(_saved)) return false;
    // FloorSet and an unfolding area replace overlapping native Floors. A
    // teleporter belongs to its authored location, not the old instance id.
    var _x=_controller.x+_saved.dx,_y=_controller.y+_saved.dy,
        _floor=collision_point(_x+16,_y+16,Floor,false,false);
    var _replace=!instance_exists(_floor);
    if(!_replace) _replace=_floor.x!=_x || _floor.y!=_y || _floor.object_index!=Floor;
    if(_replace) {
        scrNTTEFullFloorInit();
        var _align=[global.ntte_full_floor_aw,global.ntte_full_floor_ah,
            global.ntte_full_floor_ax,global.ntte_full_floor_ay];
        scrNTTEFullFloorSetAlign(32,32,_x,_y);
        try {_floor=scrNTTEFullFloorSet(_x,_y,true);}
        finally {scrNTTEFullFloorSetAlign(_align[0],_align[1],_align[2],_align[3]);}
    }
    if(!instance_exists(_floor)) return false;
    _floor.sprite_index=_saved.sprite;_floor.image_index=_saved.image;
    _floor.image_blend=_saved.blend;_floor.depth=_saved.depth;
    _controller.target=_floor;
    return true;
}

function scrFRWorld213CellKey(_x,_y) {return string(_x)+","+string(_y);}

function scrFRWorld213CoastOrbEntry(_generation) {
    // Sea has no Floor and remains walkable. The land-only merge contract
    // otherwise permits a newly appended dungeon to have a sealed shore.
    if(GameCont.area!=scrNTTEFullAreaId("coast") || GameCont.subarea<=0) return 0;
    var _floors=scrNTTEFullCrystalHeartNewInstances(Floor,_generation),
        _walls=scrNTTEFullCrystalHeartNewInstances(Wall,_generation),
        _cells=ds_map_create(),_new_walls=ds_map_create(),_order=[],_doors=0;
    try {
        for(var _i=0;_i<array_length(_floors);++_i) {
            var _f=_floors[_i];
            for(var _gy=floor(_f.bbox_top/16);_gy<ceil(_f.bbox_bottom/16);++_gy)
                for(var _gx=floor(_f.bbox_left/16);_gx<ceil(_f.bbox_right/16);++_gx) {
                    var _key=scrFRWorld213CellKey(_gx,_gy);
                    if(ds_map_exists(_cells,_key)) continue;
                    var _cell={x:_gx,y:_gy,visited:false};
                    _cells[? _key]=_cell;array_push(_order,_cell);
                }
        }
        for(var _i=0;_i<array_length(_walls);++_i) {
            var _w=_walls[_i];
            if(!_w.solid) continue;
            for(var _gy=floor(_w.bbox_top/16);_gy<ceil(_w.bbox_bottom/16);++_gy)
                for(var _gx=floor(_w.bbox_left/16);_gx<ceil(_w.bbox_right/16);++_gx)
                    _new_walls[? scrFRWorld213CellKey(_gx,_gy)]=_w;
        }
        var _dirs=[[1,0],[-1,0],[0,1],[0,-1]],_players=scrNTTEFullInstances(Player),
            _px=x,_py=y;
        if(array_length(_players)) {_px=_players[0].x;_py=_players[0].y;}
        for(var _i=0;_i<array_length(_order);++_i) {
            var _first=_order[_i];
            if(_first.visited) continue;
            _first.visited=true;
            var _component=[_first],_minx=_first.x,_maxx=_first.x,
                _miny=_first.y,_maxy=_first.y;
            for(var _head=0;_head<array_length(_component);++_head) {
                var _cell=_component[_head];
                _minx=min(_minx,_cell.x);_maxx=max(_maxx,_cell.x);
                _miny=min(_miny,_cell.y);_maxy=max(_maxy,_cell.y);
                for(var _d=0;_d<4;++_d) {
                    var _key=scrFRWorld213CellKey(_cell.x+_dirs[_d][0],_cell.y+_dirs[_d][1]);
                    if(!ds_map_exists(_cells,_key)) continue;
                    var _next=_cells[? _key];
                    if(_next.visited) continue;
                    _next.visited=true;array_push(_component,_next);
                }
            }
            var _open=false,_best=undefined,_score=infinity;
            for(var _j=0;_j<array_length(_component) && !_open;++_j) {
                var _cell=_component[_j];
                for(var _d=0;_d<4 && !_open;++_d) {
                    // Only outward extremes lead to the sea. An empty hole
                    // inside a ring must not count as an existing entrance.
                    if((_d==0 && _cell.x!=_maxx) || (_d==1 && _cell.x!=_minx)
                        || (_d==2 && _cell.y!=_maxy) || (_d==3 && _cell.y!=_miny)) continue;
                    var _dx=_dirs[_d][0],_dy=_dirs[_d][1],_crossed=false;
                    for(var _step=1;_step<=6;++_step) {
                        var _gx=_cell.x+_dx*_step,_gy=_cell.y+_dy*_step,
                            _cx=_gx*16+8,_cy=_gy*16+8,
                            _wall=collision_point(_cx,_cy,Wall,false,false);
                        if(instance_exists(_wall)) {
                            var _key=scrFRWorld213CellKey(_gx,_gy);
                            if(!ds_map_exists(_new_walls,_key) || _new_walls[? _key]!=_wall) break;
                            _crossed=true;continue;
                        }
                        if(position_meeting(_cx,_cy,InvisiWall)) break;
                        // Existing land continues safely to the water too.
                        if(position_meeting(_cx,_cy,Floor)) continue;
                        if(!_crossed) {_open=true;break;}
                        var _distance=point_distance(_cx,_cy,_px,_py);
                        if(_distance<_score) {
                            _score=_distance;_best={x:_cell.x*16+8,y:_cell.y*16+8,
                                dx:_dx,dy:_dy,steps:_step};
                        }
                        break;
                    }
                }
            }
            if(_open || !is_struct(_best)) continue;
            // A 48px shore opening admits players and their shots. Touch only
            // this orb's new walls/caps; older rooms retain their own geometry.
            for(var _step=1;_step<=_best.steps;++_step) {
                var _cx=_best.x+16*_best.dx*_step,_cy=_best.y+16*_best.dy*_step,
                    _x1=_cx-7-16*abs(_best.dy),_y1=_cy-7-16*abs(_best.dx),
                    _x2=_cx+7+16*abs(_best.dy),_y2=_cy+7+16*abs(_best.dx),
                    _parts=scrNTTEFullRectInstances(_x1,_y1,_x2,_y2,[Wall,TopSmall]);
                for(var _p=0;_p<array_length(_parts);++_p) {
                    var _part=_parts[_p];
                    if(real(_part)>real(_generation) && _part.object_index!=NTTESolidWall)
                        instance_destroy(_part,false);
                }
            }
            _doors+=1;
        }
    } finally {ds_map_destroy(_cells);ds_map_destroy(_new_walls);}
    return _doors;
}
