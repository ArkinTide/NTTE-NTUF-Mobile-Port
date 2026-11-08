"""Add Bubbles to the existing native character preference and input paths."""
from pathlib import Path


def hook_specs():
    hooks = []

    def add(path, anchor, replacement, marker):
        hooks.append({"path": path, "anchor": anchor, "replacement": replacement, "marker": marker})

    anchor = '        cpref_parrot = save_get_option("cprefs", "parrot", true)'
    add("scripts/scrOptionsUpdate/scrOptionsUpdate.gml", anchor,
        anchor + '\n        array_push(cpref_list,"bubbles"); // FRONTIER BUBBLES PREFERENCE BIT\n'
        '        cpref_bubbles=save_get_option("cprefs","bubbles",true);',
        "// FRONTIER BUBBLES PREFERENCE BIT")
    anchor = ')\n\n\n#endregion Controls_Preferences'
    add("objects/MenuOptions/Other_20.gml", anchor,
        '    // FRONTIER BUBBLES PREFERENCE ROW\n'
        '    { type: "switch", name: "BUBBLES ABILITY TOGGLE", key: "cprefs_bubbles", char: 19,\n'
        '        condition: cpref_condition, get_name: scrFRBubblesPreferenceName },\n' + anchor,
        "// FRONTIER BUBBLES PREFERENCE ROW")
    anchor = '        scrNTTEFullParrotToggleInput(_index)'
    add("scripts/InputHandling/InputHandling.gml", anchor,
        anchor + '\n        scrFRBubblesToggleInput(_index); // FRONTIER BUBBLES SAMPLED TOGGLE',
        "// FRONTIER BUBBLES SAMPLED TOGGLE")
    anchor = '        or (player.race == NTTEFullRace.Parrot && scr_player_pref(pinst,"parrot"))'
    add("objects/ButtonActive/Create_0.gml", anchor,
        anchor + '\n        or (scrFRRaceIs(player.race) && scr_player_pref(pinst,"bubbles")) // FRONTIER BUBBLES TOUCH TOGGLE',
        "// FRONTIER BUBBLES TOUCH TOGGLE")
    path = "objects/ButtonActive/Other_10.gml"
    anchor = 'if !player\n\texit'
    add(path, anchor,
        anchor + '\n\nif(scrFRBubblesTouchBlocked(player)) {\n'
        '    volume_control_command=0;exit;\n} // FRONTIER BUBBLES MENU INPUT GUARD',
        "// FRONTIER BUBBLES MENU INPUT GUARD")
    anchor = '(player.race == 12 || player.race == NTTEFullRace.Parrot) && forever'
    add(path, anchor,
        '(player.race == 12 || player.race == NTTEFullRace.Parrot || scrFRRaceIs(player.race)) && forever /* FRONTIER BUBBLES TOUCH PRESS */',
        "/* FRONTIER BUBBLES TOUCH PRESS */")
    anchor = 'if player.race == 3 || player.race == NTTEFullRace.Parrot'
    add(path, anchor,
        anchor + ' || scrFRRaceIs(player.race) /* FRONTIER BUBBLES TOUCH HOLD */',
        "/* FRONTIER BUBBLES TOUCH HOLD */")
    anchor = 'function scrPlayerRaceChange(_race, _skin = -1) {'
    add("scripts/scrPlayerCreate/scrPlayerCreate.gml", anchor,
        anchor + '\n    if(race!=_race && (scrFRRaceIs(race) || scrFRRaceIs(_race)))\n'
        '        KeyCont.activeforever[index]=false; // FRONTIER BUBBLES RACE LATCH RESET',
        "// FRONTIER BUBBLES RACE LATCH RESET")
    return hooks


def apply(project):
    project = Path(project)
    changed, originals, report = {}, {}, []
    for hook in hook_specs():
        path = project / hook["path"]
        if path not in originals:
            raw = path.read_bytes()
            originals[path] = raw
            changed[path] = raw.decode("utf-8-sig").replace("\r\n", "\n")
        source = changed[path]
        if hook["replacement"] in source:
            if source.count(hook["replacement"]) != 1:
                raise RuntimeError("Duplicate Bubbles preference hook: " + hook["marker"])
            report.append({"path": hook["path"], "status": "already-applied"})
            continue
        if hook["marker"] in source or source.count(hook["anchor"]) != 1:
            raise RuntimeError("Bubbles preference anchor changed: " + hook["marker"])
        changed[path] = source.replace(hook["anchor"], hook["replacement"], 1)
        report.append({"path": hook["path"], "status": "patched"})
    for path, source in changed.items():
        raw = originals[path]
        bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
        newline = "\r\n" if b"\r\n" in raw else "\n"
        updated = bom + source.replace("\n", newline).encode("utf8")
        if updated != raw:
            path.write_bytes(updated)
    return report


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    print(json.dumps(apply(parser.parse_args().project), indent=2))
