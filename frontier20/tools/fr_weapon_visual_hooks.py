"""Keep source melee/reload ownership and the Bubbles native health HUD."""
from pathlib import Path

from fr_content_hooks import patch


def replace(project, relative, before, after):
    path = Path(project) / relative
    source = path.read_text(encoding="utf-8-sig")
    if after in source:
        return
    assert source.count(before) == 1, (relative, before, source.count(before))
    path.write_text(source.replace(before, after, 1), encoding="utf8", newline="\n")


def apply(project):
    project = Path(project)
    replace(project, "scripts/scrFire/scrFire.gml",
            "else wepangle *= -1", "else if(!scrFRWeaponOwnsSwing(_wep)) wepangle *= -1")
    # Undergrowth retains its original weapon_fire callback, including the
    # angle flip. Its source post API is (kick,shift,shake), like Frontier.
    replace(project, "scripts/scrUndergrowthNative/scrUndergrowthNative.gml",
            "function scrUGWeaponPost(_kick,_reloadkick,_shake) {scr_weapon_post(gunangle,_kick,_reloadkick,_shake);}",
            "function scrUGWeaponPost(_kick,_reloadkick,_shake) {scr_weapon_post(gunangle,_reloadkick,_shake,_kick);}")
    scythe = "scripts/scrNTTEFullScythe/scrNTTEFullScythe.gml"
    replace(project, scythe,
            "scr_weapon_post(gunangle,_heavy?-5:5,2,6+10*_heavy);",
            "scr_weapon_post(gunangle,6+10*_heavy,2,_heavy?-5:5);")
    replace(project, scythe,
            "scr_weapon_post(gunangle,12,15,17);", "scr_weapon_post(gunangle,17,15,12);")
    replace(project, scythe,
            "scr_weapon_post(gunangle,6,7,3);", "scr_weapon_post(gunangle,3,7,6);")
    step = "objects/Player/Step_0.gml"
    replace(project, step,
            "if(!scrNTTEFullMergedRuntimeStateReloaded(true) && !scrNTTEFullRedWeaponReloaded(true)) {",
            "if(!_fr_reloaded && !scrNTTEFullMergedRuntimeStateReloaded(true) && !scrNTTEFullRedWeaponReloaded(true)) {")
    replace(project, step,
            "if(!scrNTTEFullMergedRuntimeStateReloaded(false) && !scrNTTEFullRedWeaponReloaded(false)) {",
            "if(!_fr_breloaded && !scrNTTEFullMergedRuntimeStateReloaded(false) && !scrNTTEFullRedWeaponReloaded(false)) {")
    replace(project, step, "scrPlayerGunReloadFX(bwep);\n\t\t\t\twepflip *= -1;",
            "scrPlayerGunReloadFX(bwep);\n\t\t\t\tbwepflip *= -1;")
    patch(project, "scripts/scrNTTEFullMergedRuntimeState/scrNTTEFullMergedRuntimeState.gml",
          "SOURCE PHYSICAL RELOAD",
          'if(scrFREnabled() && scrFRWeaponMergedCallback(_actor,_part,_primary,"weapon_reloaded")) return;',
          anchor="function scrNTTEFullMergedRuntimeStateReloadOne(_actor,_part,_primary) {")
    patch(project, "scripts/scrWeapons/scrWeapons.gml", "LOADED WEAPON TABLE RESTORE",
          "scrFRWeaponTablesRestore();", anchor="\tscrAmmoInit()")
    patch(project, "scripts/scrDrawPlayerHUD/scrDrawPlayerHUD.gml", "BUBBLES HEALTH METER",
          "scrFRBubblesHUD(_player);", anchor="\tscrNTTEFullParrotHUD(_player);")
    replace(project, "scripts/scrDrawPlayerHUD/scrDrawPlayerHUD.gml",
            'scrNTTEFullDrawText(110, 7, string(_txt))',
            'scrNTTEFullDrawText(scrFREnabled() && scrFRRaceIs(_race) ? 132 : 110, 7, string(_txt))')

    paths = list((project / "scripts").glob("frCode_Frontier_CharHuds_mod_*/*.gml"))
    assert len(paths) == 1, ("Frontier Bubbles authored HUD", len(paths))
    path = paths[0]
    source = path.read_text(encoding="utf8")
    # Native health begins at x20 and ends at x108. Preserve the source's
    # 18px circular meter, with its center at x119 beside that health bar.
    # Do not change the source charge/fill animation or packaged artwork.
    old_x = "var _frl__hudX = (scrFRPlayerIsActive(1) ? (_frl__hudSide ? (- 7) : 102) : 102);"
    new_x = "var _frl__hudX = 119; // FRONTIER NATIVE HEALTH ANCHOR"
    if new_x not in source:
        assert source.count(old_x) == 1, "Frontier Bubbles source HUD position changed"
        source = source.replace(old_x, new_x, 1)
    # These source callbacks only manage the old projection/loop and pause
    # snapshot. The native player-HUD consumer already owns those lifecycles.
    for name in ("draw_gui", "draw_pause"):
        signature = "function fr_Characters_Frontier_CharHuds_mod_gml_" + name + "() {"
        marker = "// FRONTIER NATIVE HEALTH OWNS " + name
        if marker in source:
            continue
        start = source.index(signature)
        next_function = source.find("\n// Original ", start + len(signature))
        end = next_function if next_function >= 0 else len(source)
        source = source[:start] + signature + "\n    " + marker + "\n}\n" + source[end:]
    path.write_text(source, encoding="utf8", newline="\n")
    return {"source_swing": "one source-owned flip including Fossil Hammer", "reload": "one callback per physical part",
            "metadata": "replayed after native table rebuild", "bubbles_hud": "native health anchor119,11"}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    print(json.dumps(apply(args.project), ensure_ascii=False, indent=2))
