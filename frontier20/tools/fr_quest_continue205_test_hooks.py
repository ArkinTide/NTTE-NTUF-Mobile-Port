"""Add full-binary active Ultimate Quest Continue acceptance to private host."""
from pathlib import Path
import argparse
import json

HOST = 'scripts/scrNTTEFullPizzaLairDrainNaturalTests/scrNTTEFullPizzaLairDrainNaturalTests.gml'
ENTRY = '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))'
SITES = (
    ('scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', ENTRY,
     '// BEGIN FRONTIER QUEST CONTINUE205 ENTRY\n'
     'if(scrNTTEFullSmokeAsyncCase("FrontierQuestContinue205Tests")) {scrFRQuestContinue205TestsStart();return;}\n'
     '// END FRONTIER QUEST CONTINUE205 ENTRY\n'+ENTRY),
    (HOST,'function scrNTTEFullPizzaLairDrainStepBody() {',
     'function scrNTTEFullPizzaLairDrainStepBody() {\n'
     '    // FRONTIER QUEST CONTINUE205 HOST\n'
     '    if(scrFRQuestContinue205HostStep(id)) return;'),
    (HOST,'function scrNTTEFullPizzaLairDrainBotAfterSample(_keycont,_index) {',
     'function scrNTTEFullPizzaLairDrainBotAfterSample(_keycont,_index) {\n'
     '    // FRONTIER QUEST CONTINUE205 SOURCE INPUT OWNERSHIP\n'
     '    if(scrFRQuestContinue205BypassPizzaBot()) return;'),
    (HOST,'    scrFRLairReturn205AfterSample(_observer,_keycont,_index);',
     '    scrFRLairReturn205AfterSample(_observer,_keycont,_index);\n'
     '    // FRONTIER QUEST CONTINUE205 SAMPLED INPUT\n'
     '    scrFRQuestContinue205AfterSample(_observer,_keycont,_index);'),
    ('scripts/scrNTTEFullQuestHubNaturalTests/scrNTTEFullQuestHubNaturalTests.gml',
     '    if(!scrFRQuestPortal204InputAllowed(_observer)) return;',
     '    if(!scrFRQuestPortal204InputAllowed(_observer)) return;\n'
     '    // FRONTIER QUEST CONTINUE205 CHECKPOINT\n'
     '    if(!scrFRQuestContinue205InputAllowed(_observer)) return;'),
    ('scripts/scrNTTEFullQuestLockedNative/scrNTTEFullQuestLockedNative.gml',
     '    scrFRQuestPortal204UnlockedProbe();',
     '    scrFRQuestPortal204UnlockedProbe();\n'
     '    // FRONTIER QUEST CONTINUE205 NATIVE UNLOCK\n'
     '    scrFRQuestContinue205UnlockedProbe();'),
)


def apply(project):
    from fr_quest_portal205_hooks import replace_exact
    project=Path(project).resolve();original={};result={}
    for relative,_,_ in SITES:
        if relative in original: continue
        path=project/relative
        if path.is_symlink() or not path.resolve().is_relative_to(project):
            raise RuntimeError('Quest Continue205 test path escapes project')
        original[relative]=path.read_bytes()
        result[relative]=original[relative].decode('utf-8-sig').replace('\r\n','\n')
    for relative,before,after in SITES:
        result[relative]=replace_exact(result[relative],before,after)
    changes=[(project/key,original[key],value.encode('utf8')) for key,value in result.items()
             if value!=original[key].decode('utf-8-sig').replace('\r\n','\n')]
    written=[]
    try:
        for path,old,updated in changes:
            if path.read_bytes()!=old: raise RuntimeError('Quest Continue205 concurrent consumer edit')
            written.append((path,old));path.write_bytes(updated)
    except BaseException:
        for path,old in reversed(written): path.write_bytes(old)
        raise
    return {'changed_paths':[p.relative_to(project).as_posix() for p,_,_ in changes],
            'case':'FrontierQuestContinue205Tests','production_save_modified':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',required=True,type=Path)
    print(json.dumps(apply(parser.parse_args().apply),indent=2))
