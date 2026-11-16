"""Install only reviewed213 helpers and hook boundaries into the current stage."""
from pathlib import Path
import json
from install_native205 import apply as install
from fr_world213_hooks import apply as world
from fr_crash213_hooks import apply as crashes
from fr_reticle213_hooks import apply as reticle
from fr_perf213_hooks import apply as performance
from fr_bubbles213_hooks import apply as bubbles

ROOT=Path(__file__).resolve().parents[1]
MAPPING={f'{name}.gml':f'scrFrontier_{name}' for name in (
    'world213','world213_tests','crash213','crash213_tests','reticle213','reticle213_tests',
    'bubbles213','bubbles213_tests','bubbles_startup_tests')}
CASES={'crash213':'scrFRCrash213Tests','world213':'scrFRWorld213Tests',
       'performance213':'scrFRPerformance213Tests','reticle213':'scrFRReticle213Tests',
       'bubbles213':'scrFRBubbles213Tests'}

def apply():
    project=ROOT/'staging/project'
    performance(project);install(project,MAPPING);world(project);crashes(project);reticle(project);bubbles(project,ROOT/'native')
    tests=ROOT/'native/tests.gml'
    text=tests.read_text('utf-8-sig')
    marker='    // FRONTIER213 EXPLICIT NATIVE ACCEPTANCE\n'
    if True:
        block=marker+'    if(array_contains('+json.dumps(list(CASES),separators=(',',':'))+',fr_test_case)) {\n'
        block+='        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker) || ++fr_test_ticks<45) return;\n'
        block+='        switch(fr_test_case) {\n'
        for name,entry in CASES.items():block+=f'            case "{name}":{entry}();break;\n'
        block+='        }\n        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");game_end();return;\n    }\n'
        needle='function scrFRIntegrationTestStep() {\n'
        assert text.count(needle)==1
        if marker in text:
            start=text.index(marker);end=text.index('    // FRONTIER BUBBLES212 REAL INPUT ACCEPTANCE',start)
            text=text[:start]+block+'\n'+text[end:]
        else:text=text.replace(needle,needle+block)
        if text!=tests.read_text('utf-8-sig'):tests.write_text(text,'utf8')
    install(project,{'tests.gml':'scrFrontier_tests'})
    smoke=project/'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml'
    text=smoke.read_text('utf-8-sig')
    needle='        if(scrNTTEFullSmokeAsyncCase("FrontierClock212Tests"))'
    assert text.count(needle)==1
    if True:
        entries='        // FRONTIER213 NATIVE ENTRY\n'
        for name in CASES:
            cls='Frontier'+name[0].upper()+name[1:]+'Tests'
            entries+=f'        if(scrNTTEFullSmokeAsyncCase("{cls}")) {{scrFRIntegrationTestStart("{name}");return;}}\n'
        if '// FRONTIER213 NATIVE ENTRY' in text:
            start=text.index('        // FRONTIER213 NATIVE ENTRY');end=text.index(needle,start)
            text=text[:start]+entries+text[end:]
        else:text=text.replace(needle,entries+needle)
        if text!=smoke.read_text('utf-8-sig'):smoke.write_text(text,'utf8')
    return MAPPING

if __name__=='__main__': print(json.dumps(apply(),indent=2))
