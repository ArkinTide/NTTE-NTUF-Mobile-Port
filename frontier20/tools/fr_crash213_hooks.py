"""Narrow fixes for data scopes, orphan actors, homing and sparse menus.

This module does not import assets or regenerate modules. It preserves source
callbacks and patches only four audited homing target guards in their emitted
module, including the reported IDPD micromissile callback.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTOR_OLD = '''    if(_type==IceFlower && scrFRPromptIs(id)) {
        var _proxy=instance_create(_x,_y,FRCustomObject);
        _proxy.name="LibPromptProxy";_proxy.fr_prompt_proxy=true;
        _proxy.visible=false;_proxy.mask_index=mskNone;_proxy.sprite_index=mskNone;
        _proxy.image_speed=0;
        return real(_proxy);
    }'''
ACTOR_NEW = '''    // FRONTIER213 DATA CALLBACK CREATION: area and array-with callbacks
    // may run on plain structs. Never evaluate the instance-only id field
    // until the scope is known to be a native instance, even when this
    // runner evaluates both operands of a boolean expression.
    if(_type==IceFlower) {
        if(!is_struct(self)) {
            if(scrFRPromptIs(id)) {
                var _proxy=instance_create(_x,_y,FRCustomObject);
                _proxy.name="LibPromptProxy";_proxy.fr_prompt_proxy=true;
                _proxy.visible=false;_proxy.mask_index=mskNone;_proxy.sprite_index=mskNone;
                _proxy.image_speed=0;
                return real(_proxy);
            }
        }
    }'''
MENU_OLD = '''\t    array_foreach(options, function(_categories) {
\t\t\tarray_foreach(_categories, function(_opt) {
\t\t\t\tif (is_string(_opt[$ "key"]) && _opt.key != "game_tutorial") {
\t\t\t\t\tds_map_delete(UberCont.saveData, _opt.key)
\t\t\t\t}
\t\t\t})
\t    })'''
MENU_NEW = '''\t    // FRONTIER213 SPARSE CATEGORY RESET
\t    scrOptionsEraseKeys213(options,UberCont.saveData)'''
HOMING_FUNCTIONS = {
    "SwarmRocket_step": "_frl_myTarget",
    "EnergyPellet_wall": "_frl__enemy",
    "QuarkShell_detach": "_frl__enemy",
    "PopoRocketSmall_step": "_frl_myTarget",
}
IMPACT_OLD = '''function fr_Mutations_AugmentImpactWrists_skill_gml_ImpactDroneHitbox_destroy() {
creator.droneHitbox = noone;
;
}'''
IMPACT_NEW = '''function fr_Mutations_AugmentImpactWrists_skill_gml_ImpactDroneHitbox_destroy() {
// FRONTIER213 ORPHAN HITBOX DESTROY: endstep deliberately retires this
// receiver after its drone disappears. Keep the live-owner handoff only.
if (scrFRInstanceExists(creator)) {
creator.droneHitbox = noone;
;
}
}'''


def replace_once(source, before, after, label):
    if after in source:
        if source.count(after) != 1 or before in source:
            raise RuntimeError("Partial/duplicate Frontier213 hook: " + label)
        return source
    if source.count(before) != 1:
        raise RuntimeError("Frontier213 source anchor changed: " + label)
    return source.replace(before, after, 1)


def transform_actor(source):
    return replace_once(source, ACTOR_OLD, ACTOR_NEW, "data callback creation")


def transform_menu(source):
    return replace_once(source, MENU_OLD, MENU_NEW, "sparse category reset")


def transform_impact(source):
    return replace_once(source, IMPACT_OLD, IMPACT_NEW, "orphan impact drone hitbox")


def transform_projectiles(source):
    for name, target in HOMING_FUNCTIONS.items():
        begin = source.index("function fr_Objects_Frontier_Projectiles2_mod_gml_" + name + "(")
        end = source.find("\n// Original ", begin)
        if end < 0:
            end = len(source)
        body = source[begin:end]
        before = ("if (scrFRInstanceExists(enemy)) {\n{\nvar " + target
                  + " = instance_nearest(x, y, enemy);\n;")
        after = ("// FRONTIER213 VALIDATE SELECTED HOMING TARGET\nvar " + target
                 + " = instance_nearest(x, y, enemy);\n"
                 + "if (instance_exists(" + target + ")) {\n{")
        body = replace_once(body, before, after, "homing " + name)
        source = source[:begin] + body + source[end:]
    return source


def apply(project, *, native=False):
    project = Path(project)
    modules = list(project.glob("scripts/frCode_Frontier_Projectiles2_mod_*/*.gml"))
    if len(modules) != 1:
        raise RuntimeError("Expected exactly one Frontier_Projectiles2 source module")
    impacts = list(project.glob("scripts/frCode_AugmentImpactWrists_skill_*/*.gml"))
    if len(impacts) != 1:
        raise RuntimeError("Expected exactly one AugmentImpactWrists source module")
    targets = {
        project / "scripts/scrFRActors/scrFRActors.gml": transform_actor,
        project / "scripts/scrOptionsUpdate/scrOptionsUpdate.gml": transform_menu,
        modules[0]: transform_projectiles,
        impacts[0]: transform_impact,
    }
    if native:
        targets[ROOT / "native/actors.gml"] = transform_actor
    changes = []
    # Validate all source boundaries before writing any production file.
    for path, transform in targets.items():
        raw = path.read_bytes()
        source = raw.decode("utf-8-sig").replace("\r\n", "\n")
        result = transform(source)
        newline = "\r\n" if b"\r\n" in raw else "\n"
        bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
        changes.append((path, raw, bom + result.replace("\n", newline).encode("utf8")))
    for path, raw, updated in changes:
        if raw != updated:
            path.write_bytes(updated)
    return {"files": [str(path) for path, _, _ in changes],
            "homing_callbacks": list(HOMING_FUNCTIONS)}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--native", action="store_true", help="Also update this tool's maintained actor source")
    args = parser.parse_args()
    print(json.dumps(apply(args.project, native=args.native), indent=2))
