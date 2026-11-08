"""Preserve authored additive ammo upgrades at the real native consumer."""
from pathlib import Path


def replace(path, before, after):
    source = path.read_text(encoding="utf-8-sig")
    if after in source:
        assert before not in source, (path, "mixed old and adapted pickup quantity")
        return
    assert source.count(before) == 1, (path, before, source.count(before))
    path.write_text(source.replace(before, after, 1), encoding="utf8", newline="\n")


def apply(project):
    project = Path(project)
    reviewed = []
    for name in ("AugmentSecondStomach", "AugmentRabbitPaw", "AugmentOpenMind"):
        paths = list((project / "scripts").glob("frCode_" + name + "_skill_*/*.gml"))
        assert len(paths) == 1, (name, "unique authored ammo upgrade", len(paths))
        replace(paths[0], "num += 0.5;", "scrFRAmmoPickupUpgrade(id,0.5);")
        reviewed.append(name)
    path = project / "objects/AmmoPickup/Collision_Player.gml"
    # This runs inside each recipient Player's with scope. Preserve that
    # player's live Fish/Wibbly/source gain table and the later Haste term.
    # Cursed's authored 1.5 is already part of the additive quantity baseline.
    replace(path, '_give_amount = scrFRAmmoRead(id,"typ_ammo",_ammo_type)\n\t\n'
            '\tif instance_is(other, CursedPickup) {\n'
            '\t\t_give_amount = round(_give_amount * 1.5)\n\t}\n',
            '_give_amount = round(scrFRAmmoRead(id,"typ_ammo",_ammo_type) * scrFRAmmoPickupQuantity(other.id))\n')
    return {"source_ammo_upgrades": reviewed,
            "quantity": "additive multiplier; configured NTTE field remains authoritative",
            "consumer": "actual native collision, per-recipient base then Haste"}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    print(json.dumps(apply(args.project), ensure_ascii=False, indent=2))
