"""Latch Ultimate Quest exit ownership at its first eligible merge countdown.

No project import/build: preflight and patch two existing native consumers.
The GameCont scalar uses the existing session serializer for Continue.
"""
from pathlib import Path
import argparse
import json

LOCKED = 'scripts/scrNTTEFullQuestLockedNative/scrNTTEFullQuestLockedNative.gml'
ROOM_END = 'objects/GameCont/Other_5.gml'
SITES = (
    (LOCKED, '    max_merge_delay=120;merge_delay=max_merge_delay;is_unlockable=false;is_playing_music=false',
     '    max_merge_delay=120;merge_delay=max_merge_delay;is_unlockable=false;is_playing_music=false\n'
     '    // FRONTIER QUEST PORTAL205 RESTORE COMPLETED CONTINUE\n'
     '    scrFRQuestPortal205RestoreChest(id);'),
    (LOCKED, '    if(merge_delay>0) merge_delay-=timescale',
     '    // FRONTIER QUEST PORTAL205 ACTIVATE\n'
     '    scrFRQuestPortal205Activate();\n'
     '    if(merge_delay>0) merge_delay-=timescale'),
    (LOCKED, '    instance_create(x,y,NTTEFullHugeQuestChest)',
     '    // FRONTIER QUEST PORTAL205 UNLOCK RELEASE\n'
     '    scrFRQuestPortal205Release();\n'
     '    instance_create(x,y,NTTEFullHugeQuestChest)'),
    (ROOM_END, 'scrNTTEFullGuardianEscapeRoomEndBegin();',
     'scrNTTEFullGuardianEscapeRoomEndBegin();\n'
     '// FRONTIER QUEST PORTAL205 ROOM RELEASE\n'
     'scrFRQuestPortal205Release();'),
)


def replace_exact(source, before, after):
    if after in source:
        if source.count(after) != 1 or before in source.replace(after, '', 1):
            raise RuntimeError('Quest portal205 installed anchor ambiguous: ' + before)
        return source
    # Other independent installers may add their own entry/dispatcher block
    # between our signature and our intact owned insertion. Preserve that
    # block instead of mistaking the original signature for an unpatched file.
    # Accept only a single complete insertion in the same native function.
    addition = ''
    if after.startswith(before):
        addition = after[len(before):]
        if addition and source.count(addition) == 1 and source.count(before) == 1:
            start = source.index(before) + len(before)
            end = source.index(addition)
            if end >= start and '\nfunction ' not in source[start:end]:
                return source
    elif after.endswith(before):
        addition = after[:-len(before)]
        if addition and source.count(addition) == 1 and source.count(before) == 1:
            start = source.index(addition) + len(addition)
            end = source.index(before)
            if end >= start and '\nfunction ' not in source[start:end]:
                return source
    for line in addition.splitlines():
        marker = line.strip()
        if marker.startswith('//') and 'FRONTIER ' in marker and marker in source:
            raise RuntimeError('Quest205 partial or moved owned insertion: ' + marker)
    if source.count(before) != 1:
        raise RuntimeError('Quest portal205 anchor changed: ' + before)
    return source.replace(before, after, 1)


def apply(project):
    project = Path(project).resolve()
    original, result = {}, {}
    for relative, _, _ in SITES:
        if relative in original:
            continue
        path = project / relative
        if path.is_symlink() or not path.resolve().is_relative_to(project):
            raise RuntimeError('Quest portal205 target escapes project')
        original[relative] = path.read_bytes()
        result[relative] = original[relative].decode('utf-8-sig').replace('\r\n', '\n')
    for relative, before, after in SITES:
        result[relative] = replace_exact(result[relative], before, after)
    changes = [(project / relative, original[relative], updated.encode('utf8'))
               for relative, updated in result.items()
               if updated != original[relative].decode('utf-8-sig').replace('\r\n', '\n')]
    for path, old, _ in changes:
        if path.read_bytes() != old:
            raise RuntimeError('Quest portal205 concurrent consumer edit')
    written = []
    try:
        for path, old, updated in changes:
            written.append((path, old));path.write_bytes(updated)
    except BaseException:
        for path, old in reversed(written):
            path.write_bytes(old)
        raise
    return {'changed_paths': [p.relative_to(project).as_posix() for p, _, _ in changes],
            'activation': 'first eligible four-component merge countdown',
            'continue_session_field': 'fr_quest_portal205_active'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', required=True, type=Path)
    print(json.dumps(apply(parser.parse_args().apply), indent=2))
