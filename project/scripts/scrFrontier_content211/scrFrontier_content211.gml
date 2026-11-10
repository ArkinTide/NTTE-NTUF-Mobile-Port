// Disabled packs keep their stable IDs on disk, but cannot enter a new run.
// DEFAULT (-1) is resolved after the actual character, including Random.
function scrFRCustom211Held() {
    for(var _i=0;_i<4;++_i) if(scrFRTouchHeld(_i)) return true;
    return false;
}
function scrFRCustom211Clicked() {
    if(!is_mobile) return mouse_ui_clicked();
    for(var _i=0;_i<4;++_i) if(scrFRTouchReleased(_i)) return true;
    return false;
}

function scrFRContent211RawEnabled(_raw,_ntuf,_ug) {
    if(is_string(_raw)) {
        var _name=string_lower(_raw);
        if(string_pos("weapon:",_name)==1) _name=string_delete(_name,1,7);
        if(!_ug && array_contains(["fossil pistol","fossil gun","fossil cannon",
            "fossil hammer","mega grenade launcher"],_name)) return false;
        if(!_ntuf && variable_global_exists("fr_weapon_ids")
            && !is_undefined(global.fr_weapon_ids[$ _raw]??global.fr_weapon_ids[$ _name])) return false;
    } else {
        if(!_ug && _raw>=174 && _raw<=178) return false;
        if(!_ntuf && variable_global_exists("fr_weapon_keys")
            && !is_undefined(global.fr_weapon_keys[$ string(_raw)])) return false;
    }
    return true;
}
function scrFRContent211CustomWeapon(_key,_value) {
    if(array_contains(["wep","bwep","protowep","protowep_s"],_key)
        && !scrFRContent210WeaponEnabled(_value)) return -1;
    return _value;
}
function scrFRContent211Starter(_race,_skin=0) {
    if(!scrFRContent211RaceVisible(_race)) _race=Race.Fish;
    var _weapon=scrFRRaceIs(_race)?scrFRRaceStarterWeapon(_skin):scrRaceGetStarterWeapon(_race);
    return scrFRContent210WeaponEnabled(_weapon)?_weapon:wep_revolver;
}
function scrFRContent211RaceVisible(_race) {
    return !scrFRRaceIs(_race) || scrFRContent210Active("ntuf");
}
function scrFRContent211Presets() {
    if(!instance_exists(UberCont) || !variable_instance_exists(UberCont,"custom_mode_slots")) return;
    var _slots=UberCont.custom_mode_slots,_dirty=false;
    for(var _i=0;_i<array_length(_slots);++_i) {
        var _slot=_slots[_i];
        if(!is_struct(_slot)) continue;
        var _fields=["wep","bwep","protowep","protowep_s"];
        for(var _j=0;_j<array_length(_fields);++_j) {
            var _field=_fields[_j],_old=_slot[$ _field]??-1,
                _new=scrFRContent211CustomWeapon(_field,_old);
            if(_old!=_new) {_slot[$ _field]=_new;_dirty=true;}
        }
        if(!scrFRContent211RaceVisible(_slot.race)) {_slot.race=Race.Fish;_slot.bskin=0;_dirty=true;}
        if(!scrFRContent210Active("ntuf")) {
            if(scrFRSkinIs(_slot.bskin)) {_slot.bskin=0;_dirty=true;}
            if(scrFRCrownKey(_slot.crown)!="") {_slot.crown=crwn_none;_dirty=true;}
            var _skills=_slot.skill_start;
            for(var _j=array_length(_skills)-1;_j>=0;--_j)
                if(!is_undefined(scrFRSkillKey(_skills[_j]))) {array_delete(_skills,_j,1);_dirty=true;}
            _slot.skill_start=_skills;
        }
        if((_slot.area>=301 && !scrFRContent210Active("ntuf"))
            || (_slot.area==207 && !scrFRContent210Active("undergrowth"))) {
            _slot.area=area_desert;_slot.subarea=1;_dirty=true;
        }
    }
    if(_dirty) scrCustomModeSavePresets();
}

// Blue UI is rendered at the view centre, rather than the source's fixed
// world coordinate10016. Anchor its buttons to the same view every frame,
// including a resized mobile viewport, camera shake and cooperative views.
function scrFRBluescreen211Align() {
    if(!instance_exists(id)) return;
    x=scrFRViewCoordinate(0)+view_width/2;
    y=scrFRViewCoordinate(1)+view_height/2;
    var _buttons=scrFRMatching(FRCustomObject,"fr_bluescreenbutton",true);
    for(var _i=0;_i<array_length(_buttons);++_i) with(_buttons[_i]) {
        x=other.x+(yesButton?-87:-16);y=other.y+51;
    }
}

function scrFRContent211BuildSelect() {
var _slot_index = 0,
	_slot_height = sprite_get_height(sprCharSelect),
	_unlocked_chars = 0,
	_char_list = [];

for(var _race_id = Race.Random; _race_id < Race.NUM_ALL_RACE_TYPES; ++_race_id) {
    if(!scrFRContent211RaceVisible(_race_id)) continue;
	if(scrNTTEFullRaceNumeric(_race_id)>=0 && !scrNTTEFullRaceReady(_race_id)) continue
	if (!scrRaceIsHidden(_race_id) || scr_race_is_unlocked(_race_id)) {
		array_push(_char_list, _race_id)
	}
}

    // Menu.Create already builds the current list. The next content sync
    // must not retire identical icons while native input still owns them.
    var _signature=json_stringify(_char_list)+":"+string(view_width)+":"+string(global.is_server);
    if(scrNTTEFullValue(id,"fr_select211_signature","")==_signature
        && instance_number(CharSelect)==array_length(_char_list)) return;
    fr_select211_signature=_signature;
    var _go=instance_find(GoButton,0),_show=instance_exists(_go) && _go.visible;
    with(CharSelect) instance_destroy();
    with(GoButton) instance_destroy();

var _count = array_length(_char_list),
	_slot_ystart = view_height - _slot_height - ((LETTERBOX_SIZE - _slot_height) div 2),
	// 选人栏间隙（原版遗留问题 · v2）。原式：min(20, floor((320−40)/角色数)) ——
	// 两个问题：① 预算被写死 320，而宽屏手机的菜单 view_width 实际 ≈496（240×宽高比）→ 右侧大量空余没用上
	//（用户截图「底部没有排满」即此）；② 满员 16 角色时步距 17 → 间隙仅 1px（「几乎紧贴」）。
	// v1 曾试「单机收回 40px 预留」→ 失败：单机按下 Play 后 is_server 也 = true（PlayButton/Other_10），条件永不满足。
	// v4 修法：**只把预算基准从写死的 game_screen_width 换成真实 view_width**，预留维持开发者原值 40px
	//（联机 GO 按钮预留 —— 与 toncho 2026-07 Discord 说明一致；v4 起不再引入任何自造数字）：
	//   步距 = min(20, floor((view_width − 40) / 角色数))
	//   宽屏（view≥368）：16 角色步距 17→20（间隙 1px→4px）；14 角色维持 20（不变）；
	//   窄屏（view=320）：floor(280/16)=17 与修前一致（= 原版数值）；GO 定位沿用原版公式（见下方）。
	_slot_step_size = min(20, floor((view_width - 40) / max(1, _count))),
	_slot_xstart = 8,
	_slot_x = _slot_xstart

for(var i = 0; i < _count; ++i) {
	// relative to the camera
	_slot_x = _slot_xstart + _slot_step_size * _slot_index
	
    with instance_create(_slot_x, _slot_ystart, CharSelect) {
        slot_index = _slot_index
        race = _char_list[i]
    }
	
	_slot_index ++
}

if global.is_server && _slot_x < (view_width - 30) {
	var _sprite = sprGoButtonSymbolic,
		_offset = sprite_get_bbox_height(_sprite) div 2,
		_ypos = view_height - LETTERBOX_SIZE + _offset - 2
    
	// GO 定位回归**原版公式** `_slot_x + _slot_step_size + 2`
	//（v2 的 `+6`、v3 的 `+22` 都是自造数值 → v4 起不再引入任何新数字）。
	// 机理：循环结束时 `_slot_x` = 最后一个槽位自身的 x；原版「空一个步距再 +2」在步距=20 时
	// 恰好等于「槽位宽 16 + 间隙 6」，GO 完整落在最后槽位右侧（PC-2 被盖是 v2 的 +6 所致）。
	with instance_create(_slot_x + _slot_step_size + 2, _ypos, GoButton) {
		sprite_index = _sprite
		visible = false
	}
}

    with(GoButton) visible=_show;
    if(!scrFRContent211RaceVisible(race)) race=Race.Fish;
}
