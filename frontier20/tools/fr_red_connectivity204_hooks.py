"""Register the narrow Red Caves connectivity probe without importing content."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "scrFrontier_red_connectivity204_tests"

def specs():
    driver_anchor = "function scrFRIntegrationTestStep() {"
    driver_marker = "// FRONTIER RED CONNECTIVITY204 DRIVER"
    driver = driver_anchor + "\n" + driver_marker + """
    if(fr_test_case=="red-connectivity204") {
        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;
        if(++fr_test_ticks<45) return;
        scrFRRedConnectivity204Tests();
        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");
        game_end();return;
    }
"""
    entry = '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))'
    marker = "// FRONTIER RED CONNECTIVITY204 ENTRY"
    red="scripts/scrNTTEFullRedAreaNative/scrNTTEFullRedAreaNative.gml"
    boundary=lambda phase: '\n    // FRONTIER RED CONNECTIVITY204 '+phase.upper()+'\n    if(variable_global_exists("fr_red204_active") && global.fr_red204_active) scrFRRedConnectivity204Boundary("'+phase+'");'
    return [
        ("scripts/scrFrontier_tests/scrFrontier_tests.gml",driver_anchor,driver,driver_marker),
        ("scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml",entry,
         marker+'\nif(scrNTTEFullSmokeAsyncCase("FrontierRedConnectivity204Tests")) {scrFRIntegrationTestStart("red-connectivity204");return;}\n'+entry,marker),
        (red,"function scrNTTEFullRedSecretRoom() {", "function scrNTTEFullRedSecretRoom() {"+boundary("secret-before"), "// FRONTIER RED CONNECTIVITY204 SECRET-BEFORE"),
        (red,"            scrNTTEFullRedCorridor(_room,_floors,true)", "            scrNTTEFullRedCorridor(_room,_floors,true)"+boundary("corridor-after"), "// FRONTIER RED CONNECTIVITY204 CORRIDOR-AFTER"),
        (red,"            scrNTTEFullQuestRedSideRoom(_room)", "            scrNTTEFullQuestRedSideRoom(_room)"+boundary("quest-after"), "// FRONTIER RED CONNECTIVITY204 QUEST-AFTER"),
        ("scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml",marker,
         '// FRONTIER RED CONNECTIVITY204 SCAN ENTRY\nif(scrNTTEFullSmokeAsyncCase("FrontierRedConnectivity204Scan")) {global.fr_red204_fast_scan=true;scrFRIntegrationTestStart("red-connectivity204");return;}\n'+marker,
         "// FRONTIER RED CONNECTIVITY204 SCAN ENTRY"),
    ]

def read_json(raw):
    return json.loads(re.sub(r",(?=\s*[}\]])", "", raw.decode("utf-8-sig")))

def apply(project):
    project=Path(project).resolve()
    originals,planned,report={},{},[]
    for relative,before,after,marker in specs():
        path=project/relative
        if path not in originals: originals[path]=path.read_bytes()
        text=planned.get(path,originals[path]).decode("utf-8-sig").replace("\r\n","\n")
        if after in text:
            if text.count(after)!=1 or text.count(marker)!=1: raise RuntimeError("Red connectivity204 installed hook ambiguous: "+marker)
            report.append({"path":relative,"status":"already-applied"});continue
        if marker in text or text.count(before)!=1: raise RuntimeError("Red connectivity204 anchor changed: "+marker)
        planned[path]=text.replace(before,after,1).encode("utf8")
        report.append({"path":relative,"status":"patched"})
    yyp=project/"nuclearthronemobile.yyp";originals[yyp]=yyp.read_bytes()
    model=read_json(originals[yyp]);rel=f"scripts/{SCRIPT}/{SCRIPT}.yy"
    matching=[r for r in model["resources"] if r["id"]["path"]==rel]
    if len(matching)>1: raise RuntimeError("Duplicate Red connectivity204 resource")
    if not matching:
        model["resources"].append({"id":{"name":SCRIPT,"path":rel}})
        planned[yyp]=(json.dumps(model,ensure_ascii=False,indent=2)+"\n").encode("utf8")
    template=read_json((project/"scripts/scrNTTEFullAreas/scrNTTEFullAreas.yy").read_bytes())
    template["name"]=template["%Name"]=SCRIPT
    for path,raw in [(project/rel,(json.dumps(template,ensure_ascii=False,indent=2)+"\n").encode("utf8")),
                     (project/f"scripts/{SCRIPT}/{SCRIPT}.gml",(ROOT/"native/red_connectivity204_tests.gml").read_bytes())]:
        originals[path]=path.read_bytes() if path.exists() else None;planned[path]=raw
    for path,raw in originals.items():
        if (path.read_bytes() if path.exists() else None)!=raw: raise RuntimeError("Red connectivity204 file changed during preflight: "+str(path))
    for path,raw in planned.items():
        if raw!=originals[path]: path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--apply",type=Path,required=True)
    print(json.dumps(apply(parser.parse_args().apply),indent=2))
