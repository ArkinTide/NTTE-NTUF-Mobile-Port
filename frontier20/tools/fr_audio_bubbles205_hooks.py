"""Narrow 2.0.5 audio lifetimes and Bubbles attack-mode consumers.

Production hooks preserve the current imported project and frozen modules.
Tests are opt-in because their public dispatchers are integrated in sequence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def hook_specs(*, tests=False):
    hooks = []

    def add(path, anchor, replacement, marker):
        hooks.append(dict(path=path, anchor=anchor, replacement=replacement, marker=marker))

    path = "scripts/frCode_Frontier_Bosses_mod_e991af6211/frCode_Frontier_Bosses_mod_e991af6211.gml"
    for kind, field, sample in (("laser", "bulwarkLaserLoop", "sndBulwarkLaserLoop"),
                                ("shock", "bulwarkShockLoop", "sndBulwarkShockLoop")):
        anchor = (f'global.fr_module_vars[$ "mod:Frontier_Bosses"].{field} = '
                  f'scrFRSoundLoop(global.fr_module_vars[$ "mod:Frontier_Bosses"].{sample});')
        marker = f"// FRONTIER BULWARK {kind.upper()} VOICE205"
        add(path, anchor, anchor.replace("scrFRSoundLoop(", f'scrFRBulwarkLoop205("{kind}",')
            + " " + marker, marker)
    anchor = "on_death = fr_Objects_Frontier_Bosses_mod_gml_RoboBoss_death;"
    marker = "// FRONTIER BULWARK CLEANUP VOICES205"
    add(path, anchor, anchor + "\non_cleanup = scrFRBulwarkAudioCleanup205; " + marker, marker)

    path = "scripts/scrFrontier_saves/scrFrontier_saves.gml"
    anchor = "function scrFRContinuePlayerNativeState(_field,_value,_decode) {"
    marker = "// FRONTIER CONTINUE TRANSIENT AUDIO205"
    add(path, anchor, anchor + "\n    if(scrFRContinueAudioField205(_field)) return -1; " + marker, marker)
    for path, anchor in (("objects/Player/Other_5.gml", "snd_stop(sndCarLoop)"),
                         ("objects/Player/Destroy_0.gml", "snd_stop(sndFishTB)")):
        marker = "// FRONTIER PLAYER AUDIO OWNER205"
        add(path, anchor, "scrFRPlayerAudioStop205(); " + marker + "\n" + anchor, marker)

    path = "scripts/scrFrontier_bubbles_preferences/scrFrontier_bubbles_preferences.gml"
    anchor = '''function scrFRBubblesToggleInput(_index) {
    if(!scrFREnabled()) return;
    var _pinst=scr_playerinstance_find(_index),_player=noone;
    with(Player) if(index==_index) {_player=id;break;}
    if(!instance_exists(_player) || !is_struct(_pinst) || !scrFRRaceIs(_player.race)) return;
    if(scrNTTEFullMountedAbilityRaw(_player)) {KeyCont.activeforever[_index]=false;return;}
    if(!scr_player_pref(_pinst,"bubbles")) return;
    var _press=KeyCont.press_spec[_index],_active=KeyCont.activeforever[_index],
        _blocked=scrFRBubblesInputBlocked();
    if(!_blocked && _press) {_active=!_active;KeyCont.activeforever[_index]=_active;}
    KeyCont.hold_spec[_index]=_active;
    KeyCont.press_spec[_index]=_press && _active && !_blocked;
    KeyCont.release_spec[_index]=_press && !_active && !_blocked;
}'''
    marker = "// FRONTIER BUBBLES ATTACK MODE205"
    replacement = ("function scrFRBubblesToggleInput(_index) {\n"
                   "    scrFRBubblesToggle205(_index); " + marker + "\n}")
    add(path, anchor, replacement, marker)
    # Accept only the exact early 2.0.5 working form when replacing its
    # temporary early-return bridge with the final maintained function.
    hooks[-1]["previous"] = anchor.replace("{\n", "{\n    scrFRBubblesToggle205(_index);return; " + marker + "\n", 1)
    path = "scripts/InputHandling/InputHandling.gml"
    anchor = "    scrFRPocketTeleporterSample204(_index); // FRONTIER POCKET 204 RAW INPUT START"
    marker = "// FRONTIER BUBBLES FINAL ATTACK INPUT205"
    add(path, anchor, "    scrFRBubblesAttackInput205(_index); " + marker + "\n" + anchor, marker)
    path = "scripts/scrPlayerFiring/scrPlayerFiring.gml"
    anchor = "function scrPlayerFiring(_primary = true) {"
    marker = "// FRONTIER BUBBLES WEAPON EXCLUSION205"
    add(path, anchor, anchor + "\n    if(scrFRBubblesWeaponBlocked205(id)) {clicked=false;return;} " + marker, marker)

    if tests:
        path = "scripts/scrFrontier_tests/scrFrontier_tests.gml"
        anchor = "function scrFRIntegrationTestStep() {"
        marker = "// FRONTIER AUDIO BUBBLES205 TEST DISPATCH"
        body = '''
    if(fr_test_case=="continue_audio205") {
        if(!variable_instance_exists(id,"fr_continue_audio205")) {
            if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;
            if(++fr_test_ticks<45) return;
            scrFRContinueAudio205TestsStart(id);return;
        }
        if(scrFRContinueAudio205TestsStep(id)) {scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");game_end();}
        return;
    }
    if(fr_test_case=="bubbles_attack205") {
        if(!variable_instance_exists(id,"fr_bubbles_attack205")) {
            if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;
            if(++fr_test_ticks<45) return;
            scrFRBubblesAttack205TestsStart(id);return;
        }
        if(scrFRBubblesAttack205TestsStep(id)) {scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");game_end();}
        return;
    }
'''
        add(path, anchor, anchor + "\n" + marker + body, marker)
        path = "scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml"
        anchor = '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))'
        marker = "// FRONTIER AUDIO BUBBLES205 SMOKE ENTRY"
        body = ('        ' + marker + '\n'
                '        if(scrNTTEFullSmokeAsyncCase("FrontierContinueAudio205Tests")) {scrFRIntegrationTestStart("continue_audio205");return;}\n'
                '        if(scrNTTEFullSmokeAsyncCase("FrontierBubblesAttack205Tests")) {scrFRIntegrationTestStart("bubbles_attack205");return;}\n')
        add(path, anchor, body + anchor, marker)
        path = "objects/UberCont/Step_0.gml"
        anchor = "scrHandleInputsGeneral(global.index)"
        marker = "// FRONTIER BUBBLES205 REAL INPUT FIXTURE"
        add(path, anchor, "if(os_type==os_windows && scrNTTEFullSmokeEnabled()) scrFRBubblesAttack205TestsBeforeInput(); "
            + marker + "\n" + anchor + "\n"
            + "if(os_type==os_windows && scrNTTEFullSmokeEnabled()) scrFRBubblesAttack205TestsAfterInput();", marker)
        path = "scripts/scrFrontier_bubbles_startup_tests/scrFrontier_bubbles_startup_tests.gml"
        anchor = "function scrFRBubblesStartupTestsTouchState() {"
        marker = "// FRONTIER BUBBLES205 RAW TOUCH DEVICE"
        add(path, anchor, anchor + "\n    var _fr205=scrFRBubblesAttack205TouchState();\n"
            + "    if(is_struct(_fr205)) return _fr205; " + marker, marker)
    return hooks


def apply(project, *, tests=False):
    project = Path(project).resolve()
    originals, changed, report = {}, {}, []
    for hook in hook_specs(tests=tests):
        path = project / hook["path"]
        if path not in originals:
            originals[path] = path.read_bytes()
            changed[path] = originals[path].decode("utf-8-sig").replace("\r\n", "\n")
        source = changed[path]
        if hook["replacement"] in source:
            if source.count(hook["replacement"]) != 1 or source.count(hook["marker"]) != 1:
                raise RuntimeError("Duplicate audio/Bubbles205 hook: " + hook["marker"])
            report.append(dict(path=hook["path"], status="already-applied"))
            continue
        # Independent test modules prepend to the same dispatcher or smoke
        # anchor. Their ordering can separate our complete installed block
        # from that anchor without changing our own code.
        if tests and hook["marker"] in source:
            fragment = hook["replacement"]
            if fragment.startswith(hook["anchor"]):
                fragment = fragment[len(hook["anchor"]):]
            elif fragment.endswith(hook["anchor"]):
                fragment = fragment[:-len(hook["anchor"])]
            if (fragment != hook["replacement"] and source.count(fragment) == 1
                    and source.count(hook["marker"]) == 1):
                report.append(dict(path=hook["path"], status="already-applied"))
                continue
        previous = hook.get("previous")
        if previous and source.count(previous) == 1 and source.count(hook["marker"]) == 1:
            changed[path] = source.replace(previous, hook["replacement"], 1)
            report.append(dict(path=hook["path"], status="patched"))
            continue
        if hook["marker"] in source or source.count(hook["anchor"]) != 1:
            raise RuntimeError("Changed audio/Bubbles205 hook boundary: " + hook["marker"])
        changed[path] = source.replace(hook["anchor"], hook["replacement"], 1)
        report.append(dict(path=hook["path"], status="patched"))
    # Validate every boundary before making any mutation.
    for path, source in changed.items():
        raw = originals[path]
        newline = "\r\n" if b"\r\n" in raw else "\n"
        bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
        encoded = bom + source.replace("\n", newline).encode("utf8")
        if encoded != raw:
            path.write_bytes(encoded)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--tests", action="store_true")
    args = parser.parse_args()
    print(json.dumps(apply(args.project, tests=args.tests), indent=2))
