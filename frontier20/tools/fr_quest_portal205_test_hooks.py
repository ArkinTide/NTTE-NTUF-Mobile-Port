"""Expose the independent ordinary Vault regression and readonly corpse probe."""
from pathlib import Path
import argparse
import json

DRIVER = 'function scrFRIntegrationTestStep() {'
DRIVER_FIXED = DRIVER + '''
    // BEGIN FRONTIER QUEST PORTAL205 TEST DRIVER
    if(fr_test_case=="quest-vault205") {
        if(variable_instance_exists(id,"fr_quest_portal205")) {
            if(scrFRQuestPortal205TestsStep(id)) {
                scrNTTESmokeLog("PASS FRONTIER ordinary generated Vault205 genuine four guardians/deaths/native corpse exit x30/60");
                scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");
                game_end();
            }
            return;
        }
        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;
        if(++fr_test_ticks<45) return;
        scrFRQuestPortal205TestsStart(id);return;
    }
    // END FRONTIER QUEST PORTAL205 TEST DRIVER
'''
ENTRY = '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))'
ENTRY_FIXED = '''// BEGIN FRONTIER QUEST PORTAL205 TEST ENTRY
if(scrNTTEFullSmokeAsyncCase("FrontierQuestVault205Tests")) {scrFRIntegrationTestStart("quest-vault205");return;}
// END FRONTIER QUEST PORTAL205 TEST ENTRY
''' + ENTRY
SITES = (
    ('scripts/scrFrontier_tests/scrFrontier_tests.gml', DRIVER, DRIVER_FIXED),
    ('scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', ENTRY, ENTRY_FIXED),
    ('objects/Corpse/Alarm_0.gml', 'scrFRQuestPortal204CorpseProbe("before");',
     'scrFRQuestPortal204CorpseProbe("before");\n// FRONTIER QUEST PORTAL205 CORPSE BEFORE\nscrFRQuestPortal205CorpseProbe("before");'),
    ('objects/Corpse/Alarm_0.gml', 'scrFRQuestPortal204CorpseProbe("passed");',
     'scrFRQuestPortal204CorpseProbe("passed");\n// FRONTIER QUEST PORTAL205 CORPSE PASS\nscrFRQuestPortal205CorpseProbe("passed");'),
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
            raise RuntimeError('Quest vault205 test target escapes project')
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
                raise RuntimeError('Quest vault205 test consumer changed during preflight')
            written.append((path, old));path.write_bytes(updated)
    except BaseException:
        for path, old in reversed(written):
            path.write_bytes(old)
        raise
    return {'changed_paths': [p.relative_to(project).as_posix() for p, _, _ in changes],
            'case': 'FrontierQuestVault205Tests'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', required=True, type=Path)
    print(json.dumps(apply(parser.parse_args().apply), indent=2))
