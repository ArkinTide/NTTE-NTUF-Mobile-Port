"""Restrict an unfolding Heart's new roof decoration to its authored edge."""
from pathlib import Path


RELATIVE = "scripts/scrNTTEFullCrystalHeart/scrNTTEFullCrystalHeart.gml"
ANCHOR = '    var _reveal=scrNTTEFullCrystalHeartNewInstances([Floor,Wall,TopSmall],_generation)'
TOP_RELATIVE = 'objects/TopSmall/Create_0.gml'
TOP_ANCHOR = 'position_meeting(x, y, Wall)'
TOP_REPLACEMENT = 'scrNTTESolidWallPlanPoint(x, y) /* FRONTIER PACKED CAP LAYOUT */'
MERGE_RELATIVE = 'scripts/scrNTTEFullInRoomGeneration/scrNTTEFullInRoomGeneration.gml'
MERGE_ANCHOR = ('if (instance_exists(_old_list[_j]) && place_meeting(x,y,_old_list[_j])) '
                '{ instance_destroy(id,false); break }')
MERGE_REPLACEMENT = ('if (instance_exists(_old_list[_j]) && scrFROrbWallMergeOccludes(id,_old_list[_j])) '
                     '{ instance_destroy(id,false); break } /* FRONTIER PACKED CAP MERGE */')


def hook_specs():
    block = ('// BEGIN FRONTIER HEART AUTHORED EDGE TOPS\n'
             '    // Finish source decoration before flash/reveal snapshots.\n'
             '    scrFROrbWallPruneTops(_generation);\n'
             '// END FRONTIER HEART AUTHORED EDGE TOPS\n')
    return [
        (RELATIVE, ANCHOR, block + ANCHOR, '// BEGIN FRONTIER HEART AUTHORED EDGE TOPS'),
        (TOP_RELATIVE, TOP_ANCHOR, TOP_REPLACEMENT, '/* FRONTIER PACKED CAP LAYOUT */'),
        (MERGE_RELATIVE, MERGE_ANCHOR, MERGE_REPLACEMENT, '/* FRONTIER PACKED CAP MERGE */'),
    ]


def apply(project):
    project = Path(project)
    changed, originals = {}, {}
    for relative, anchor, replacement, marker in hook_specs():
        path = project / relative
        if path not in originals:
            originals[path] = path.read_bytes()
            changed[path] = originals[path].decode('utf-8-sig').replace('\r\n', '\n')
        source = changed[path]
        if relative == RELATIVE:
            assert source.count('// BEGIN FRONTIER HEART AUTHORED EDGE TOPS') == source.count(
                '// END FRONTIER HEART AUTHORED EDGE TOPS') <= 1, (relative, 'partial orb wall markers')
        if replacement in source:
            assert source.count(replacement) == 1 and source.count(marker) == 1, (relative, 'duplicate orb wall hook')
            assert source.count(anchor) == replacement.count(anchor), (relative, 'duplicate orb wall anchor')
            continue
        assert marker not in source and source.count(anchor) == 1, (relative, 'orb wall anchor changed')
        changed[path] = source.replace(anchor, replacement, 1)
    # Source generation, cap.Create and post-decoration pruning form one
    # contract. Validate all three before modifying any selected project file.
    for path, source in changed.items():
        raw = originals[path]
        bom = b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b''
        newline = '\r\n' if b'\r\n' in raw else '\n'
        updated = bom + source.replace('\n', newline).encode('utf-8')
        if updated != raw:
            path.write_bytes(updated)
    return {"file": RELATIVE,
            "kind": "Heart authored edge transitions over plain compact collision; unsupported roof removal"}
