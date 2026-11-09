"""Keep live players out of Pizza cave-in persistent-item salvage and rubble.

The original deeper lethal cave-in and all terrain/item behavior are retained.
Only native-mask-clear existing Floor is eligible for the safe-edge release.
"""
from pathlib import Path
import argparse
import json

LAIR = 'scripts/scrNTTEFullLairBorder/scrNTTEFullLairBorder.gml'
SITES = (
    (LAIR, '    if (ntte_full_cavein<0) return;',
     '    if (ntte_full_cavein<0) return;\n'
     '    // FRONTIER LAIR RETURN205 RELEASE PRIOR LIVE SALVAGE\n'
     '    scrFRLairReturn205ReleaseBorderSaved(id);'),
    (LAIR, '                else if (_v.persistent || instance_is(_v,chestprop)',
     '                // FRONTIER LAIR RETURN205 SAFE EDGE PLAYER\n'
     '                else if (scrFRLairReturn205ReleasePlayer(_v,x,y)) { }\n'
     '                else if (_v.persistent || instance_is(_v,chestprop)'),
    (LAIR, '        if (scrNTTEFullIsPickup(_v) && _v.alarm[0]>0) _v.alarm[0]=max(_v.alarm[0],90)',
     '        // FRONTIER LAIR RETURN205 RELEASE LIVE RUBBLE SALVAGE\n'
     '        if (scrFRLairReturn205ReleasePlayer(_v,x,y)) { array_delete(ntte_full_saved,_i,1); continue; }\n'
     '        if (scrNTTEFullIsPickup(_v) && _v.alarm[0]>0) _v.alarm[0]=max(_v.alarm[0],90)'),
)


def apply(project):
    from fr_quest_portal205_hooks import replace_exact
    project = Path(project).resolve()
    original, result = {}, {}
    for relative, _, _ in SITES:
        if relative in original:
            continue
        path = project / relative
        if path.is_symlink() or not path.resolve().is_relative_to(project):
            raise RuntimeError('Lair return205 target escapes project')
        original[relative] = path.read_bytes()
        result[relative] = original[relative].decode('utf-8-sig').replace('\r\n', '\n')
    for relative, before, after in SITES:
        result[relative] = replace_exact(result[relative], before, after)
    changes = [(project / key, original[key], value.encode('utf8')) for key, value in result.items()
               if value != original[key].decode('utf-8-sig').replace('\r\n', '\n')]
    written = []
    try:
        for path, old, updated in changes:
            if path.read_bytes() != old:
                raise RuntimeError('Lair return205 consumer changed during preflight')
            written.append((path, old));path.write_bytes(updated)
    except BaseException:
        for path, old in reversed(written):
            path.write_bytes(old)
        raise
    return {'changed_paths': [p.relative_to(project).as_posix() for p, _, _ in changes],
            'live_player_release': 'existing native-mask-clear Lair-side Floor',
            'deeper_native_lethal_cavein_retained': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', required=True, type=Path)
    print(json.dumps(apply(parser.parse_args().apply), indent=2))
