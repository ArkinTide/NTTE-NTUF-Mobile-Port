"""Install current214 helpers into the maintained stage, without re-exporting."""
from pathlib import Path
import json
from install_native205 import apply as install
from fr_crash214_hooks import apply as crashes
from fr_perf214_hooks import apply as performance
from fr_melee214_hooks import apply as melee
from fr_menus214_hooks import apply as menus
from fr_movement214_hooks import apply as movement

ROOT=Path(__file__).resolve().parents[1]
MAPPING={f'{name}.gml':f'scrFrontier_{name}' for name in (
    'crash214','crash214_tests','performance214','performance214_tests','melee214_tests',
    'menus214','menus214_tests','movement214','movement214_tests')}
CASES={'crash214':'scrFRCrash214Tests','performance214':'scrFRPerformance214Tests',
       'melee214':'scrFRMelee214Tests','menus214':'scrFRMenus214Tests',
       'movement214':'scrFRMovement214Tests'}

def apply():
    project=ROOT/'staging/project'
    install(project,MAPPING);crashes(project);performance();melee(project);menus(project);movement(project)
    tests=ROOT/'native/tests.gml'
    data=tests.read_text('utf-8-sig')
    start='    // FRONTIER214 EXPLICIT NATIVE ACCEPTANCE\n'
    end='    // FRONTIER214 END NATIVE ACCEPTANCE\n'
    block=start+'    if(array_contains('+json.dumps(list(CASES),separators=(',',':'))+',fr_test_case)) {\n'
    block+='        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker) || ++fr_test_ticks<45) return;\n'
    block+='        switch(fr_test_case) {\n'
    for name,entry in CASES.items():
        if name=='melee214':block+='            case "melee214":if(!scrFRMelee214ScheduledTests()) return;break;\n'
        else:block+=f'            case "{name}":{entry}();break;\n'
    block+='        }\n        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");game_end();return;\n    }\n'+end
    if start in data:
        a=data.index(start);b=data.index(end,a)+len(end);data=data[:a]+block+data[b:]
    else:
        needle='function scrFRIntegrationTestStep() {\n';assert data.count(needle)==1
        data=data.replace(needle,needle+block)
    if tests.read_text('utf-8-sig')!=data:tests.write_text(data,'utf8')
    install(project,{'tests.gml':'scrFrontier_tests'})
    smoke=project/'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml'
    data=smoke.read_text('utf-8-sig')
    start='        // FRONTIER214 NATIVE ENTRY\n';end='        // FRONTIER214 END NATIVE ENTRY\n'
    block=start
    for name in CASES:
        cls='Frontier'+name[0].upper()+name[1:]+'Tests'
        block+=f'        if(scrNTTEFullSmokeAsyncCase("{cls}")) {{scrFRIntegrationTestStart("{name}");return;}}\n'
    block+=end
    if start in data:
        a=data.index(start);b=data.index(end,a)+len(end);data=data[:a]+block+data[b:]
    else:
        needle='        // FRONTIER213 NATIVE ENTRY';assert data.count(needle)==1
        data=data.replace(needle,block+needle)
    if smoke.read_text('utf-8-sig')!=data:smoke.write_text(data,'utf8')
    return MAPPING

if __name__=='__main__':print(json.dumps(apply(),indent=2))
