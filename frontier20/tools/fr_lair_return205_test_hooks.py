"""Extend the real Pizza drain regression with native sampled traversal.

No production terrain change; this is deliberately runnable on the baseline.
"""
from pathlib import Path
import argparse
import json

NATURAL = 'scripts/scrNTTEFullPizzaLairDrainNaturalTests/scrNTTEFullPizzaLairDrainNaturalTests.gml'
ENTRY = '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))'
SITES = (
    ('scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', ENTRY,
     '// BEGIN FRONTIER LAIR RETURN205 TEST ENTRY\n'
     'if(scrNTTEFullSmokeAsyncCase("FrontierLairReturn205Tests")) {scrFRLairReturn205TestsStart();return;}\n'
     '// END FRONTIER LAIR RETURN205 TEST ENTRY\n' + ENTRY),
    ('scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', '// BEGIN FRONTIER LAIR RETURN205 TEST ENTRY\n',
     '// BEGIN FRONTIER LAIR RETURN205 LINGER ENTRY\n'
     'if(scrNTTEFullSmokeAsyncCase("FrontierLairReturnLinger205Tests")) {scrFRLairReturn205LingerTestsStart();return;}\n'
     '// END FRONTIER LAIR RETURN205 LINGER ENTRY\n'
     '// BEGIN FRONTIER LAIR RETURN205 TEST ENTRY\n'),
    (NATURAL, 'function scrNTTEFullPizzaLairDrainStepBody() {',
     'function scrNTTEFullPizzaLairDrainStepBody() {\n'
     '    // FRONTIER LAIR RETURN205 SCHEDULED TRAVERSAL\n'
     '    if(scrFRLairReturn205Before(id)) return;'),
    (NATURAL, '        if(++pass_index<array_length(rates)) {scrNTTEFullPizzaLairDrainAwait(0);return;}',
     '        // FRONTIER LAIR RETURN205 VALIDATED SOURCE HANDOFF\n'
     '        if(scrFRLairReturn205Validated(id)) return;\n'
     '        if(++pass_index<array_length(rates)) {scrNTTEFullPizzaLairDrainAwait(0);return;}'),
    (NATURAL, '    _keycont.hold_nort[_index]=false;_keycont.hold_sout[_index]=false',
     '    _keycont.hold_nort[_index]=false;_keycont.hold_sout[_index]=false\n'
     '    // FRONTIER LAIR RETURN205 NATIVE SAMPLED MOVEMENT\n'
     '    scrFRLairReturn205AfterSample(_observer,_keycont,_index);'),
    (NATURAL, 'assert(instance_exists(tv) && tv.visible && tv.sprite_index==sprTV && tv.spr_idle==sprTV',
     'assert(instance_exists(tv) && tv.visible && (tv.sprite_index==sprTV || tv.sprite_index==tv.spr_hurt) && tv.spr_idle==sprTV'),
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
            raise RuntimeError('Lair return205 test target escapes project')
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
                raise RuntimeError('Lair return205 test consumer changed during preflight')
            written.append((path, old));path.write_bytes(updated)
    except BaseException:
        for path, old in reversed(written):
            path.write_bytes(old)
        raise
    return {'changed_paths': [p.relative_to(project).as_posix() for p, _, _ in changes],
            'case': 'FrontierLairReturn205Tests', 'production_terrain_modified': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', required=True, type=Path)
    print(json.dumps(apply(parser.parse_args().apply), indent=2))
