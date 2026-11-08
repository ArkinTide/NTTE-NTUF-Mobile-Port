"""Continuous Pocket Teleporter movement and consistent controller routing."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from fr_input_hooks import source_script


def hook_specs():
    hooks = []

    def add(path, anchor, replacement, marker):
        hooks.append(dict(path=path, anchor=anchor, replacement=replacement, marker=marker))

    source = source_script("Mutations/AugmentExtraFeet.skill.gml")
    for section, code in [
        ("skill_take", "scrFRPocketTeleporterReset204();"),
        ("step", "scrFRPocketTeleporterStep204(); return;"),
    ]:
        anchor = "function fr_Mutations_AugmentExtraFeet_skill_gml_" + section + "() {"
        marker = "// FRONTIER POCKET 204 " + section
        add(source, anchor, anchor + "\n    " + code + " " + marker, marker)
    # Retain the authored arrival particles, sound, cooldown and afterimage.
    # Only replace the old eight-way direction and centre-ray wall algorithm.
    marker = "// FRONTIER POCKET 204 CONTINUOUS MASK SWEEP"
    replacement = (marker + '\nfr_dashaugment_angle = scrFRPocketTeleporterAngle204(index);\n'
                   'fr_dashaugment_length = scrFRPocketTeleporterDistance204(50 * scrFRGetSkill("AugmentExtraFeet"), fr_dashaugment_angle);\n')
    hooks.append(dict(path=source, anchor='if (scrFRButtonCheck(index, "east")) {',
                      end="lastx = x;", scope="function fr_Mutations_AugmentExtraFeet_skill_gml_dash() {",
                      replacement=replacement, marker=marker))
    path = "scripts/scrFrontier_view_input/scrFrontier_view_input.gml"
    anchor = "function scrFRTouchPoll() {"
    marker = "// FRONTIER POINTER 204 STABLE HARDWARE FRAME"
    add(path, anchor, anchor + "\n    scrFRMenuTouchPoll204(); return; " + marker, marker)
    anchor = "_state.frame=current_frame;_state.ready=scrFRReadyTick();\n}\n\nfunction scrFRTouchMovementValue"
    marker = "// FRONTIER POCKET 204 RAW TOUCH START"
    add(path, anchor, anchor.replace("\n}", "\n    scrFRPocketTeleporterSample204(_index); " + marker + "\n}", 1), marker)
    path = "scripts/InputHandling/InputHandling.gml"
    anchor = "function scrHandleInputsGeneral(_index) {"
    marker = "// FRONTIER CONTROLLER 204 CONNECTION"
    add(path, anchor, anchor + "\n    scrFRGamepadAvailability204(_index); " + marker, marker)
    anchor = "scrFRTouchPoll(); // FRONTIER TOUCH MENU RAW SAMPLES"
    marker = "// FRONTIER POCKET 204 RAW INPUT START"
    add(path, anchor, "scrFRPocketTeleporterSample204(_index); " + marker + "\n    " + anchor, marker)
    anchor = "function scrSetGamepadInputs(_index = 0) {"
    marker = "// FRONTIER CONTROLLER 204 ANALOGUE EDGES"
    add(path, anchor, anchor + "\n    scrFRGamepadInputs204(_index); return; " + marker, marker)
    anchor = "function scrNTTEGamepadDeviceIndex(_logical=global.index) {"
    marker = "// FRONTIER CONTROLLER 204 STABLE UNIQUE SLOTS"
    add(path, anchor, anchor + "\n    return scrFRGamepadDevice204(_logical); " + marker, marker)
    anchor = "else if scr_keyboard_check_pressed(gp_stickr) {"
    marker = "// FRONTIER CONTROLLER 204 RIGHT STICK BUTTON"
    add(path, anchor, "else if scrNTTEGamepadButton(gp_stickr,keystate_press) { " + marker, marker)
    path = "scripts/scrFrontier_core_api/scrFrontier_core_api.gml"
    anchor = '? input_gamepad_check_pressed(_index,gp_face1) : input_gamepad_check(_index,gp_face1);'
    marker = "// FRONTIER CONTROLLER 204 SOURCE CONFIRM"
    add(path, anchor, '? scrNTTEGamepadButton(gp_face1,keystate_press,_index) : scrNTTEGamepadButton(gp_face1,keystate_hold,_index); ' + marker, marker)
    path = "scripts/scrFrontier_prompt_hud_tests/scrFrontier_prompt_hud_tests.gml"
    anchor = "scrFRInputTouchTests(); // FRONTIER ACTUAL TOUCH INPUT FIXTURE"
    marker = "// FRONTIER INPUT 204 REGRESSIONS"
    add(path, anchor, anchor + "\n    scrFRInput204Tests(); " + marker, marker)
    return hooks


def apply(project):
    project = Path(project).resolve()
    changed, report = {}, []
    for hook in hook_specs():
        path = project / hook["path"]
        text = changed.get(path, path.read_text("utf-8-sig"))
        if hook["replacement"] in text:
            report.append({"path": hook["path"], "status": "already-applied"})
            continue
        if hook["marker"] in text:
            raise RuntimeError("Frontier input204 hook anchor changed: " + hook["marker"])
        if "end" in hook:
            if text.count(hook["scope"]) != 1:
                raise RuntimeError("Frontier input204 scope changed: " + hook["marker"])
            start = text.find(hook["anchor"], text.index(hook["scope"]))
            end = text.find(hook["end"], start)
            if start < 0 or end < 0:
                raise RuntimeError("Frontier input204 sweep boundaries changed: " + hook["marker"])
            changed[path] = text[:start] + hook["replacement"] + text[end:]
        else:
            if text.count(hook["anchor"]) != 1:
                raise RuntimeError("Frontier input204 hook anchor changed: " + hook["marker"])
            changed[path] = text.replace(hook["anchor"], hook["replacement"], 1)
        report.append({"path": hook["path"], "status": "patched"})
    for path, text in changed.items():
        path.write_text(text, "utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", type=Path)
    args = parser.parse_args()
    print(json.dumps(apply(args.apply) if args.apply else hook_specs(), indent=2))
