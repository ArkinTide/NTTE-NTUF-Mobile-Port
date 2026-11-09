"""Add readonly Ultimate Quest portal probes and one isolated native test case.

The installer is independent of the production repair. Its test native code
compiles on the old production baseline and fails only after observing a real
ordinary exit, not on a missing new helper. Importing this module is readonly.
"""
from pathlib import Path
import argparse
import json


DRIVER = 'function scrFRIntegrationTestStep() {'
DRIVER_FIXED = DRIVER + '''
    // BEGIN FRONTIER QUEST PORTAL204 TEST DRIVER
    if(fr_test_case=="quest-portal204") {
        if(variable_instance_exists(id,"fr_quest_portal204")) {
            if(scrFRQuestPortal204TestsStep(id)) {
                scrNTTESmokeLog("PASS FRONTIER QUEST PORTAL204 six real source routes, recovery/corpse alarms, reward and legal crown exit");
                scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");
                game_end();
            }
            return;
        }
        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;
        if(++fr_test_ticks<45) return;
        scrFRQuestPortal204TestsStart(id);return;
    }
    // END FRONTIER QUEST PORTAL204 TEST DRIVER
'''
ENTRY = '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))'
ENTRY_FIXED = '''// BEGIN FRONTIER QUEST PORTAL204 TEST ENTRY
if(scrNTTEFullSmokeAsyncCase("FrontierQuestPortal204Tests")) {scrFRIntegrationTestStart("quest-portal204");return;}
// END FRONTIER QUEST PORTAL204 TEST ENTRY
''' + ENTRY

NATURAL = 'scripts/scrNTTEFullQuestHubNaturalTests/scrNTTEFullQuestHubNaturalTests.gml'
NATURAL_SITES = (
    ('function scrNTTEFullQuestHubNaturalGateBegin() {',
     '    scrFRQuestPortal204NaturalBegin(id);', 'BEGIN'),
    ('    try {scrNTTEFullQuestHubNaturalGateEndBody()}',
     '    try {scrNTTEFullQuestHubNaturalGateEndBody();scrFRQuestPortal204NaturalEnd(id)}', 'END'),
    ('function scrNTTEFullQuestHubNaturalStepBody() {',
     '    if(scrFRQuestPortal204NaturalBefore(id)) return;', 'STEP'),
    ('    _keycont.press_pick[_index]=true',
     '    if(!scrFRQuestPortal204InputAllowed(_observer)) return;\n    _keycont.press_pick[_index]=true', 'INPUT'),
    ('function scrNTTEFullQuestHubNaturalFinish() {',
     '    scrFRQuestPortal204NaturalFinish(id);', 'FINISH'),
)
CORPSE = 'objects/Corpse/Alarm_0.gml'
CORPSE_BEFORE = 'if (\n    !scrNTTEPortalRecoveryAllowed() || scrNTTEFullPortalBlocked() ||'
CORPSE_REJECT = '|| instance_exists(SitDown)\n) {\n\texit\n}'
CROWN = 'objects/CrownPickup/Collision_Player.gml'
ENEMY = 'objects/enemy/Destroy_0.gml'
RECOVERY = 'scripts/scrNTTEAllies/scrNTTEAllies.gml'
LOCKED = 'scripts/scrNTTEFullQuestLockedNative/scrNTTEFullQuestLockedNative.gml'
UNLOCK = ('    if(instance_exists(prompt)) instance_destroy(prompt,false)\n'
          '    instance_destroy(id,false)\n    return true')
SITES = (
    ('scripts/scrFrontier_tests/scrFrontier_tests.gml', DRIVER, DRIVER_FIXED, 'DRIVER'),
    ('scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', ENTRY, ENTRY_FIXED, 'ENTRY'),
)


def replace_exact(source, before, after, identity):
    if before == after:
        raise RuntimeError('Quest portal204 test has an empty transformation: ' + identity)
    if after in source:
        if source.count(after) != 1:
            raise RuntimeError('Quest portal204 duplicate test hook: ' + identity)
        # The original may be a prefix of the installed function signature.
        remainder = source.replace(after, '', 1)
        if before in remainder:
            raise RuntimeError('Quest portal204 ambiguous installed anchor: ' + identity)
        return source
    marker = 'FRONTIER QUEST PORTAL204 TEST ' + identity
    if marker in source or source.count(before) != 1:
        raise RuntimeError('Quest portal204 changed/partial test anchor: ' + identity)
    return source.replace(before, after, 1)


def call_block(call, identity):
    return ('// BEGIN FRONTIER QUEST PORTAL204 TEST ' + identity + '\n'
            + call + '\n// END FRONTIER QUEST PORTAL204 TEST ' + identity + '\n')


def natural_transform(source):
    for before, insertion, identity in NATURAL_SITES:
        if identity in ('BEGIN', 'STEP', 'FINISH'):
            after = before + '\n' + call_block(insertion, identity).rstrip('\n')
        else:
            after = call_block(insertion, identity).rstrip('\n')
        source = replace_exact(source, before, after, identity)
    return source


def corpse_transform(source):
    source = replace_exact(source, CORPSE_BEFORE,
        call_block('scrFRQuestPortal204CorpseProbe("before");', 'CORPSE BEFORE') + CORPSE_BEFORE,
        'CORPSE BEFORE')
    source = replace_exact(source, CORPSE_REJECT,
        CORPSE_REJECT.replace('\texit', call_block('scrFRQuestPortal204CorpseProbe("rejected");', 'CORPSE REJECT') + '\texit'),
        'CORPSE REJECT')
    tail = call_block('scrFRQuestPortal204CorpseProbe("passed");', 'CORPSE PASS')
    marker = 'FRONTIER QUEST PORTAL204 TEST CORPSE PASS'
    if marker in source:
        if source.count(tail) != 1 or not source.endswith(tail):
            raise RuntimeError('Quest portal204 partial or moved corpse tail')
    else:
        source = source.rstrip('\n') + '\n' + tail
    return source


def transforms(source_by_path):
    result = {}
    for relative, before, after, identity in SITES:
        result[relative] = replace_exact(source_by_path[relative], before, after, identity)
    result[NATURAL] = natural_transform(source_by_path[NATURAL])
    result[CORPSE] = corpse_transform(source_by_path[CORPSE])
    result[RECOVERY] = replace_exact(source_by_path[RECOVERY],
        'function scrNTTEAllyPortalStep() {',
        'function scrNTTEAllyPortalStep() {\n' + call_block('    scrFRQuestPortal204RecoveryProbe();', 'RECOVERY').rstrip('\n'),
        'RECOVERY')
    result[ENEMY] = replace_exact(source_by_path[ENEMY],
        'scrNTTEPortalDeathRemember();',
        call_block('scrFRQuestPortal204EnemyDeathProbe();', 'ENEMY DEATH') + 'scrNTTEPortalDeathRemember();',
        'ENEMY DEATH')
    result[CROWN] = replace_exact(source_by_path[CROWN],
        'instance_destroy()',
        call_block('scrFRQuestPortal204CrownCollisionProbe();', 'CROWN COLLISION') + 'instance_destroy()',
        'CROWN COLLISION')
    result[LOCKED] = replace_exact(source_by_path[LOCKED], UNLOCK,
        UNLOCK.replace('    return true', call_block('    scrFRQuestPortal204UnlockedProbe();', 'NATIVE UNLOCK') + '    return true'),
        'NATIVE UNLOCK')
    return result


def apply(project):
    project = Path(project).resolve()
    paths = [row[0] for row in SITES] + [NATURAL, CORPSE, RECOVERY, ENEMY, CROWN, LOCKED]
    originals = {}
    for relative in paths:
        target = project / relative
        if target.is_symlink() or not target.resolve().is_relative_to(project):
            raise RuntimeError('Quest portal204 test path escapes project: ' + relative)
        originals[relative] = target.read_bytes()
    source = {key: raw.decode('utf-8-sig').replace('\r\n', '\n') for key, raw in originals.items()}
    updated = transforms(source)
    changes = [(project / key, originals[key], value.encode('utf8'))
               for key, value in updated.items() if value != source[key]]
    for target, raw, _ in changes:
        if target.read_bytes() != raw:
            raise RuntimeError('Quest portal204 test consumer changed during preflight')
    written = []
    try:
        for target, raw, data in changes:
            written.append((target, raw))
            target.write_bytes(data)
    except BaseException:
        for target, raw in reversed(written):
            target.write_bytes(raw)
        raise
    return {'changed_paths': [p.relative_to(project).as_posix() for p, _, _ in changes],
            'case': 'FrontierQuestPortal204Tests', 'production_helper_required': False,
            'readonly_probes': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', required=True, type=Path)
    print(json.dumps(apply(parser.parse_args().apply), indent=2))
