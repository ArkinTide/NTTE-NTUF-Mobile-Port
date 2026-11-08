function scr_keyboard_is_typing() {
	// console 打开时，游戏侧（暂停 / 方向键移动 / …）一律不再吃键盘输入 ——
	// 与 debug overlay 同一思路：键盘输入先归「正在输入的那个界面」。
	// 原版只认 debug overlay，所以打开 console 后方向键仍会移动角色、删除键仍会触发暂停（实测）。
	return is_keyboard_used_debug_overlay() || instance_exists(DebugObjectSpawner) || global.console_active
}

function scr_keyboard_check_pressed(_keycode) {
// BEGIN FRONTIER MENU INPUT204 RAW KEYBOARD PRESSED
// Explicit native test fixture; normal keyboard sampling falls through.
var _fr_menu_key=undefined;
if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest)) _fr_menu_key=scrFRMenuInput204Keyboard("pressed",_keycode);
if(!is_undefined(_fr_menu_key)) return _fr_menu_key;
// END FRONTIER MENU INPUT204 RAW KEYBOARD PRESSED

	/*if keyboard_check_pressed(_keycode) {
		// keypress was handled by some action
		if scrKeyboardHandleKeyPress(_keycode) {
			return false
		}
		// don't allow keypress detection when typing
		return !scr_keyboard_is_typing()
	}
	return false*/
	gml_pragma("forceinline")
	return !scr_keyboard_is_typing() && keyboard_check_pressed(_keycode)
}

function scr_keyboard_check_held(_keycode) {
// BEGIN FRONTIER MENU INPUT204 RAW KEYBOARD HELD
// Explicit native test fixture; normal keyboard sampling falls through.
var _fr_menu_key=undefined;
if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest)) _fr_menu_key=scrFRMenuInput204Keyboard("held",_keycode);
if(!is_undefined(_fr_menu_key)) return _fr_menu_key;
// END FRONTIER MENU INPUT204 RAW KEYBOARD HELD

	gml_pragma("forceinline")
	return !scr_keyboard_is_typing() && keyboard_check(_keycode)
}

function scr_keyboard_check_released(_keycode) {
// BEGIN FRONTIER MENU INPUT204 RAW KEYBOARD RELEASED
// Explicit native test fixture; normal keyboard sampling falls through.
var _fr_menu_key=undefined;
if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest)) _fr_menu_key=scrFRMenuInput204Keyboard("released",_keycode);
if(!is_undefined(_fr_menu_key)) return _fr_menu_key;
// END FRONTIER MENU INPUT204 RAW KEYBOARD RELEASED

	gml_pragma("forceinline")
	return !scr_keyboard_is_typing() && keyboard_check_released(_keycode)
}