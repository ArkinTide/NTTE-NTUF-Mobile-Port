"""Fix source world consumers without regenerating unrelated modules."""
from pathlib import Path


FIRED_PLAYER = 'objects/FiredMaggot/Collision_Player.gml'
FIRED_WALL = 'objects/FiredMaggot/Collision_Wall.gml'
DROP = 'scripts/scrNTTEFullWeaponDrop/scrNTTEFullWeaponDrop.gml'
HUB = 'scripts/scrNTTEFullQuestHubNative/scrNTTEFullQuestHubNative.gml'
FLOOR = 'scripts/scrNTTEFullQuestFloorNative/scrNTTEFullQuestFloorNative.gml'
PAD = 'scripts/scrNTTEFullQuestTeleporterNative/scrNTTEFullQuestTeleporterNative.gml'
HEART = 'scripts/scrNTTEFullCrystalHeart/scrNTTEFullCrystalHeart.gml'
MAGGOT_OLD = '''    with instance_create(x, y, Maggot) {
        motion_add(point_direction(other.x, other.y, x, y), (4) * timescale)
        givekill = 0
    }'''
WALL_OLD = '''with instance_create(x, y, Maggot) {
    motion_add(point_direction(other.x, other.y, x, y), (4) * timescale)
    givekill = 0
}

instance_destroy(id, 0)'''

SITES = (
    (FIRED_PLAYER, MAGGOT_OLD,
     '    scrFRWorld213FiredMaggotLand(); // FRONTIER213 CONSUME FIRED LARVA'),
    (FIRED_WALL, WALL_OLD,
     'scrFRWorld213FiredMaggotLand(); // FRONTIER213 CONSUME FIRED LARVA'),
    (DROP, '    if(_raw=="crabbone") {',
     '    if(_raw=="crabbone") {\n'
     '        // FRONTIER213 CURSED CHEST EXCLUDES QUEST BONE\n'
     '        if(scrNTTEFullValue(_context,"curse",0)>0) return -1;'),
    (HUB, '    _b.target=_from;_b.teleport_x=_tx;_b.teleport_y=_ty',
     '    _b.target=_from;_b.teleport_x=_tx;_b.teleport_y=_ty\n'
     '    scrFRWorld213QuestFloorBind(_a);scrFRWorld213QuestFloorBind(_b); // FRONTIER213 QUEST PAD LOCATION'),
    (HUB, '        _cont.part_index=_part;_cont.target=_floor;array_push(_controllers,_cont)',
     '        _cont.part_index=_part;_cont.target=_floor;array_push(_controllers,_cont)\n'
     '        scrFRWorld213QuestFloorBind(_cont); // FRONTIER213 QUEST KEY LOCATION'),
    (FLOOR, '    if(!instance_exists(target)) { instance_destroy();return }',
     '    if(!scrFRWorld213QuestFloorEnsure(id)) { instance_destroy();return } // FRONTIER213 QUEST FLOOR RECOVERY'),
    (PAD, '    if(!instance_exists(target)) { instance_destroy();return }',
     '    if(!scrFRWorld213QuestFloorEnsure(id)) { instance_destroy();return } // FRONTIER213 QUEST PAD RECOVERY'),
    (HEART, '    scrFROrbWallPruneTops(_generation);',
     '    scrFROrbWallPruneTops(_generation);\n'
     '    scrFRWorld213CoastOrbEntry(_generation); // FRONTIER213 COAST ORB SHORE ENTRY'),
)


def replace_once(source, before, after):
    if after in source:
        if source.count(after) != 1 or before in source.replace(after, '', 1):
            raise RuntimeError('World213 installed hook ambiguous: ' + before)
        return source
    if source.count(before) != 1:
        raise RuntimeError('World213 source anchor changed: ' + before)
    return source.replace(before, after, 1)


def apply(project):
    project = Path(project).resolve()
    original, changed = {}, {}
    for relative, before, after in SITES:
        path = project / relative
        if path.is_symlink() or not path.resolve().is_relative_to(project):
            raise RuntimeError('World213 consumer escapes project')
        if relative not in original:
            original[relative] = path.read_bytes()
            changed[relative] = original[relative].decode('utf-8-sig').replace('\r\n', '\n')
        changed[relative] = replace_once(changed[relative], before, after)
    writes = []
    for relative, source in changed.items():
        raw = original[relative]
        bom = b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b''
        newline = '\r\n' if b'\r\n' in raw else '\n'
        updated = bom + source.replace('\n', newline).encode('utf8')
        if updated != raw:
            writes.append((project / relative, raw, updated))
    for path, raw, _ in writes:
        if path.read_bytes() != raw:
            raise RuntimeError('World213 concurrent consumer edit')
    written = []
    try:
        for path, raw, updated in writes:
            written.append((path, raw))
            path.write_bytes(updated)
    except BaseException:
        for path, raw in reversed(written):
            path.write_bytes(raw)
        raise
    return {'changed_paths': [p.relative_to(project).as_posix() for p, _, _ in writes]}


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', required=True, type=Path)
    print(json.dumps(apply(parser.parse_args().apply), indent=2))
