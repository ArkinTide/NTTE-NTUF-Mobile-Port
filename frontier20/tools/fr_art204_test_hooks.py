"""Install isolated artwork acceptance entry points without importing the stage."""
from pathlib import Path
import argparse
import json


def apply(project):
    project = Path(project).resolve()
    driver = 'function scrFRIntegrationTestStep() {'
    driver_patch = driver + '''
// FRONTIER ART204 DRIVER
    if(fr_test_case=="loadout-art204" || fr_test_case=="boss-art204") {
        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;
        if(++fr_test_ticks<45) return;
        if(fr_test_case=="loadout-art204") scrFRLoadoutArt204Tests();
        else scrFRBossArt204Tests();
        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");
        game_end();return;
    }
'''
    entry = '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))'
    entry_patch = '''// FRONTIER ART204 ENTRY
if(scrNTTEFullSmokeAsyncCase("FrontierLoadoutArt204Tests")) {scrFRIntegrationTestStart("loadout-art204");return;}
if(scrNTTEFullSmokeAsyncCase("FrontierBossArt204Tests")) {scrFRIntegrationTestStart("boss-art204");return;}
''' + entry
    changes = []
    for rel, before, after, marker in (
        ('scripts/scrFrontier_tests/scrFrontier_tests.gml', driver, driver_patch, '// FRONTIER ART204 DRIVER'),
        ('scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', entry, entry_patch, '// FRONTIER ART204 ENTRY'),
    ):
        path = project / rel
        raw = path.read_bytes()
        text = raw.decode('utf-8-sig').replace('\r\n', '\n')
        if after in text:
            assert text.count(after) == text.count(marker) == 1, ('Ambiguous artwork hook', rel)
        else:
            assert marker not in text and text.count(before) == 1, ('Artwork hook anchor changed', rel)
            changes.append((path, raw, text.replace(before, after, 1).encode('utf8')))
    for path, raw, _ in changes:
        assert path.read_bytes() == raw, 'Artwork test consumer changed during preflight'
    written = []
    try:
        for path, raw, data in changes:
            written.append((path, raw))
            path.write_bytes(data)
    except Exception:
        for path, raw in reversed(written):
            path.write_bytes(raw)
        raise
    return [p.relative_to(project).as_posix() for p, _, _ in changes]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', required=True, type=Path)
    print(json.dumps(apply(parser.parse_args().apply), indent=2))
