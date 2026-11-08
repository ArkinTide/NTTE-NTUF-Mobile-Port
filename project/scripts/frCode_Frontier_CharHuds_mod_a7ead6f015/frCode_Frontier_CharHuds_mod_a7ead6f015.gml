// Original Characters/Frontier_CharHuds.mod.gml:1
function fr_Characters_Frontier_CharHuds_mod_gml___load() {

}

// Original Characters/Frontier_CharHuds.mod.gml:1
function fr_Characters_Frontier_CharHuds_mod_gml_init() {
global.fr_module_vars[$ "mod:Frontier_CharHuds"].sprBubblesHud = sprFR_sprBubblesHud_775af471ac4b;
;
global.fr_module_vars[$ "mod:Frontier_CharHuds"].sprBubblesHudBack = sprFR_sprBubblesHudBack_49e846621318;
;
global.fr_module_vars[$ "mod:Frontier_CharHuds"].sprBubblesHudSlice = sprFR_sprBubblesHudSlice_035b030755a5;
;
global.fr_module_vars[$ "mod:Frontier_CharHuds"].sprBubblesHudSliceEnd = sprFR_sprBubblesHudSliceEnd_71d3cbe12522;
;
global.fr_module_vars[$ "mod:Frontier_CharHuds"].sprBubblesHudSliceEnd2 = sprFR_sprBubblesHudSliceEnd2_0c9d9f5db404;
;
}

// Original Characters/Frontier_CharHuds.mod.gml:16
function fr_Characters_Frontier_CharHuds_mod_gml_player_hud(_frl__player=undefined, _frl__hudIndex=undefined, _frl__hudSide=undefined) {
{ var __fr_switch_value1=_frl__player.race, __fr_switch_case2=-1;
if(__fr_switch_case2==-1 && __fr_switch_value1==(scrFRRaceTryResolve("bubbles"))) __fr_switch_case2=0;
if(__fr_switch_case2==-1) __fr_switch_case2=-1;
switch(__fr_switch_case2) {
case 0:
{
var _frl__bubbleCharge = _frl__player.bubbles_bubbleCharge;
var _frl__maxBubbleCharge = _frl__player.bubbles_maxBubbleCharge;
var _frl__hudX = 119; // FRONTIER NATIVE HEALTH ANCHOR
var _frl__hudY = ((_frl__hudIndex >= 2) ? 11 : 11);
;
var _frl__barX = (_frl__hudX - 7);
;
var _frl__barY = (_frl__hudY - 7);
;
var _frl__barMaxHeight = 13;
;
var _frl__barHeight = 13;
;
var _frl__barSize = (13 - (_frl__barMaxHeight * (_frl__bubbleCharge / _frl__maxBubbleCharge)));
;
scrFRDrawSprite(global.fr_module_vars[$ "mod:Frontier_CharHuds"].sprBubblesHudBack, 0, _frl__hudX, _frl__hudY);
;
draw_sprite_stretched(global.fr_module_vars[$ "mod:Frontier_CharHuds"].sprBubblesHudSlice, 0, _frl__barX, (_frl__barY + _frl__barSize), 13, (13 - _frl__barSize));
;
if ((_frl__barSize > 3)) {
{
draw_sprite_part(global.fr_module_vars[$ "mod:Frontier_CharHuds"].sprBubblesHudSliceEnd, (scrFRSourceFrame() * 0.4), 0, 0, 13, 3, _frl__barX, ((_frl__barY + _frl__barSize) - 3));
;
}
} else {
{
draw_sprite_part(global.fr_module_vars[$ "mod:Frontier_CharHuds"].sprBubblesHudSliceEnd2, (scrFRSourceFrame() * 0.4), 0, 0, 13, 3, _frl__barX, ((_frl__barY + _frl__barSize) - 3));
;
}
}
var _frl__barEndWidth = clamp((_frl__barMaxHeight - _frl__barSize), 0, _frl__barHeight);
;
var _frl__barEndX = (_frl__barX + _frl__barSize);
;
scrFRDrawSprite(global.fr_module_vars[$ "mod:Frontier_CharHuds"].sprBubblesHud, 0, _frl__hudX, _frl__hudY);
// BEGIN FRONTIER BUBBLES STARTUP REAL HUD
if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest)) scrFRBubblesStartupTestsObserve("hud",_frl__player);
// END FRONTIER BUBBLES STARTUP REAL HUD

;
break;
;
}
}
}
}

// Original Characters/Frontier_CharHuds.mod.gml:101
function fr_Characters_Frontier_CharHuds_mod_gml_draw_gui() {
    // FRONTIER NATIVE HEALTH OWNS draw_gui
}

// Original Characters/Frontier_CharHuds.mod.gml:189
function fr_Characters_Frontier_CharHuds_mod_gml_draw_pause() {
    // FRONTIER NATIVE HEALTH OWNS draw_pause
}
