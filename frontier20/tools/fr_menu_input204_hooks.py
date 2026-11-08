"""Native menu mode ownership plus explicit scheduled touch/navigation regressions.

The production guard is deliberately independent of all development fixtures.
Use production_fix=False only on a separate defect-reproduction compiler copy.
"""
from pathlib import Path
import re

from fr_content_hooks import patch

CASES = ("FrontierMenuInput20430Tests", "FrontierMenuInput20460Tests")


def hook_specs(production_fix=True):
    guard = ("if(os_type==os_windows && scrNTTEFullSmokeEnabled() "
             "&& instance_exists(FRIntegrationTest)) ")
    rows = []

    def add(path, label, body, anchor, before=False):
        rows.append(dict(path=path, label=label, body=body, anchor=anchor, before=before))

    if production_fix:
        add("scripts/scrGamepadUIControl/scrGamepadUIControl.gml", "MENU204 INPUT MODE OWNERSHIP",
            "// Touch movement edges are not native keyboard/controller menu navigation.\n"
            "if(!KeyCont.keyboard[global.index] && !KeyCont.gamepad[global.index]) {\n"
            "    gamepad_h=0;gamepad_v=0;return;\n}",
            "function scrGamepadUIControl() {")
        add("scripts/scrNTTEFullSingleplayerUIEntryTests/scrNTTEFullSingleplayerUIEntryTests.gml",
            "MENU INPUT204 DECLARED CONTROLLER FIXTURE MODE",
            "// This direct native navigation fixture owns a controller-mode sample.\n"
            "KeyCont.keyboard[global.index]=false;KeyCont.gamepad[global.index]=true;\n"
            "KeyCont.touch[global.index]=false;",
            "UberCont.opt_gamepad=true;UberCont.gamepad_sel=-1")
        add("objects/MenuOptions/Other_10.gml", "MENU204 OPTIONS INPUT MODE OWNERSHIP",
            "// Touch gameplay direction edges cannot navigate the options list.\n"
            "if(!KeyCont.keyboard[global.index] && !KeyCont.gamepad[global.index]) { kh=0;kv=0; }",
            "var kv = KeyCont.press_sout[global.index] - KeyCont.press_nort[global.index],\n"
            "\tkh = KeyCont.press_east[global.index] - KeyCont.press_west[global.index]")
    add("objects/UberCont/Step_0.gml", "MENU INPUT204 BEFORE REAL INPUT",
        guard + "scrFRMenuInput204BeforeInput();", "scrHandleInputsGeneral(global.index)", True)
    add("objects/UberCont/Step_0.gml", "MENU INPUT204 AFTER REAL INPUT",
        guard + "scrFRMenuInput204AfterInput();", "scrGamepadUIControl()", True)
    for name, kind in (("pressed", "pressed"), ("held", "held"), ("released", "released")):
        add("scripts/scr_keyboard_check_pressed/scr_keyboard_check_pressed.gml",
            "MENU INPUT204 RAW KEYBOARD " + name.upper(),
            "// Explicit native test fixture; normal keyboard sampling falls through.\n"
            "var _fr_menu_key=undefined;\n" + guard
            + '_fr_menu_key=scrFRMenuInput204Keyboard("' + kind + '",_keycode);\n'
            "if(!is_undefined(_fr_menu_key)) return _fr_menu_key;",
            "function scr_keyboard_check_" + name + "(_keycode) {")
    add("objects/MenuOptions/Other_10.gml", "MENU INPUT204 OBSERVE OPTIONS DIRECTIONS",
        guard + "scrFRMenuInput204OptionsObserve(kh,kv);",
        "if item_count != -1 {", True)
    add("scripts/scrFrontier_tests/scrFrontier_tests.gml", "MENU INPUT204 DRIVER",
        'if(string_pos("menu-input204-",fr_test_case)==1) {\n'
        '    if(!variable_instance_exists(id,"fr_menu_input204")) {\n'
        '        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;\n'
        '        if(++fr_test_ticks<45) return;\n'
        '        scrFRMenuInput204Start(id,string_pos("60",fr_test_case)>0?60:30);\n'
        '    }\n'
        '    if(scrFRMenuInput204Step(id)) {\n'
        '        scrNTTESmokeLog("PASS scheduled raw JoystickMove owner removal, native menu idle, touch/keyboard/controller/mode positive controls");\n'
        '        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
        '        game_end();\n'
        '    }\n'
        '    return;\n'
        '}', "function scrFRIntegrationTestStep() {")
    add("scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml", "MENU INPUT204 ENTRY",
        '\n'.join('if(scrNTTEFullSmokeAsyncCase("' + name + '")) '
                  '{scrFRIntegrationTestStart("menu-input204-' + str(rate) + '");return;}'
                  for name, rate in zip(CASES, (30, 60))),
        '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', True)
    return rows


def apply(project, production_fix=True):
    project = Path(project)
    specs = hook_specs(production_fix)
    # Validate the entire hook inventory before the first write. Existing
    # labeled blocks are delegated to the shared idempotent patch owner.
    for spec in specs:
        text = (project / spec["path"]).read_text(encoding="utf-8-sig")
        begin, end = "// BEGIN FRONTIER " + spec["label"], "// END FRONTIER " + spec["label"]
        starts = list(re.finditer(r"^[ \t]*" + re.escape(begin) + r"(?=\r?$)", text, re.M))
        ends = list(re.finditer(r"^[ \t]*" + re.escape(end) + r"(?=\r?$)", text, re.M))
        if len(starts) != len(ends) or len(starts) > 1:
            raise RuntimeError("Menu input204 partial hook: " + spec["label"])
        host = text
        if starts:
            block = re.search(r"^[ \t]*" + re.escape(begin) + r"\r?\n.*?^[ \t]*"
                              + re.escape(end) + r"(?:\r?\n|$)", text, re.M | re.S)
            if block is None:
                raise RuntimeError("Menu input204 hook order: " + spec["label"])
            host = text[:block.start()] + text[block.end():]
        anchor = spec["anchor"].replace("\r\n", "\n")
        if host.replace("\r\n", "\n").count(anchor) != 1:
            raise RuntimeError("Menu input204 changed anchor: " + spec["label"])
    for spec in specs:
        patch(project, spec["path"], spec["label"], spec["body"],
              anchor=spec["anchor"], before=spec["before"])
    return {"native_cases": list(CASES), "production_fix": production_fix,
            "rates": [30, 60], "physical_device_tested": False,
            "pointer_or_movement_queues_changed": False,
            "options_reader": "local input-mode ownership guard" if production_fix else "unguarded diagnostic"}
