"""Make native Griller pages obey the same eligibility as ordinary level-up rolls.

Only the native selection presentation changes. Rat rewards, IDPD stations,
temporary grants and the explicit Frontier main-pool augment option retain
their authored availability/grant callbacks.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DRAW = "objects/LevCont/Draw_64.gml"
SCRIPT = "scrFrontier_mutation_pool204_tests"

OLD_PAGE = "\t\t_pagemax = maxskill div _count"
NEW_PAGE = """        _pool = []

    // FRONTIER MUTATION POOL204 ELIGIBLE PAGES
    // Griller is another presentation of normal level-up choices. Checking
    // ownership alone admits station-only and temporary reward mutations.
    for(var _candidate=1;_candidate<=maxskill;++_candidate) {
        var _heavy_ready=_candidate==mut_heavy_heart && !scr_skill_get(_candidate)
            && GameCont.heavyheart>=3;
        if(scr_skill_can_appear(_candidate) || _heavy_ready) array_push(_pool,_candidate);
    }
    var _pagemax=max(0,(array_length(_pool)-1) div _count)"""

OLD_CHOICES = """\t\tfor(var i = 0; i < _count; i ++) {
\t\t\twith instance_create(i * 32, _dy, SkillIcon) {
\t\t\t\tvar _tries = 1
\t\t\t\t
\t\t\t\tdo {
\t\t\t\t\tskill = (i + (_page * _count)) % (maxskill) + _tries
\t\t\t\t\t
\t\t\t\t\tif (++ _tries) > 99 {
\t\t\t\t\t\tinstance_destroy()
\t\t\t\t\t\tbreak
\t\t\t\t\t}
\t\t\t\t}
\t\t\t\tuntil skill > 0 && !scr_skill_get(skill) && !instance_exists_var_notme(SkillIcon, "skill", skill)
\t\t\t\t
\t\t\t\tif (skill < 0) skill = maxskill + skill
\t\t\t\t
\t\t\t\tif (skill < 0 || skill > maxskill) instance_destroy()
\t\t\t\t
\t\t\t\tnum = i
\t\t\t}
\t\t}"""
NEW_CHOICES = """        // FRONTIER MUTATION POOL204 DISTINCT PAGE SLICE
        for(var i = 0; i < _count; i ++) {
            var _at=_page*_count+i;
            if(_at>=array_length(_pool)) break;
            with instance_create(i * 32, _dy, SkillIcon) {
                skill=_pool[_at];num=i;
            }
        }"""


def specs():
    driver_anchor = "function scrFRIntegrationTestStep() {"
    driver_marker = "// FRONTIER MUTATION POOL204 DRIVER"
    driver = driver_anchor + "\n" + driver_marker + """
    if(fr_test_case=="mutation-pool204") {
        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;
        if(++fr_test_ticks<45) return;
        scrFRMutationPool204Tests();
        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");
        game_end();return;
    }
"""
    entry_anchor = '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))'
    entry_marker = "// FRONTIER MUTATION POOL204 ENTRY"
    return [
        (DRAW, OLD_PAGE, NEW_PAGE, "// FRONTIER MUTATION POOL204 ELIGIBLE PAGES"),
        (DRAW, OLD_CHOICES, NEW_CHOICES, "// FRONTIER MUTATION POOL204 DISTINCT PAGE SLICE"),
        (DRAW, "\t\t\tmut = mut_last_wish", "\t\t\tskill = mut_last_wish // FRONTIER MUTATION POOL204 FALLBACK", "// FRONTIER MUTATION POOL204 FALLBACK"),
        ("scripts/scrFrontier_tests/scrFrontier_tests.gml", driver_anchor, driver, driver_marker),
        ("scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml", entry_anchor,
         entry_marker + '\nif(scrNTTEFullSmokeAsyncCase("FrontierMutationPool204Tests")) {scrFRIntegrationTestStart("mutation-pool204");return;}\n' + entry_anchor,
         entry_marker),
    ]


def read_json(raw):
    return json.loads(re.sub(r",(?=\s*[}\]])", "", raw.decode("utf-8-sig")))


def apply(project):
    project = Path(project).resolve()
    originals, planned, report = {}, {}, []
    for relative, before, after, marker in specs():
        path = project / relative
        if path not in originals:
            originals[path] = path.read_bytes()
        text = planned.get(path, originals[path]).decode("utf-8-sig").replace("\r\n", "\n")
        if after in text:
            if text.count(after) != 1 or text.count(marker) != 1:
                raise RuntimeError("Mutation pool204 installed hook ambiguous: " + marker)
            report.append({"path": relative, "status": "already-applied"})
            continue
        if marker in text or text.count(before) != 1:
            raise RuntimeError("Mutation pool204 native anchor changed: " + marker)
        planned[path] = text.replace(before, after, 1).encode("utf8")
        report.append({"path": relative, "status": "patched"})
    # Register exactly one maintained test script, without a full stage import.
    yyp = project / "nuclearthronemobile.yyp"
    originals[yyp] = yyp.read_bytes()
    model = read_json(originals[yyp])
    rel_yy = f"scripts/{SCRIPT}/{SCRIPT}.yy"
    matching = [r for r in model["resources"] if r["id"]["path"] == rel_yy]
    if len(matching) > 1:
        raise RuntimeError("Duplicate mutation pool204 native script resource")
    if not matching:
        model["resources"].append({"id": {"name": SCRIPT, "path": rel_yy}})
        planned[yyp] = (json.dumps(model, ensure_ascii=False, indent=2)+"\n").encode("utf8")
    template = read_json((project / "scripts/scrNTTEFullAreas/scrNTTEFullAreas.yy").read_bytes())
    template["name"] = template["%Name"] = SCRIPT
    for path, data in [
        (project / rel_yy, (json.dumps(template, ensure_ascii=False, indent=2)+"\n").encode("utf8")),
        (project / f"scripts/{SCRIPT}/{SCRIPT}.gml", (ROOT / "native/mutation_pool204_tests.gml").read_bytes()),
    ]:
        originals[path] = path.read_bytes() if path.exists() else None
        planned[path] = data
    for path, raw in originals.items():
        if (path.read_bytes() if path.exists() else None) != raw:
            raise RuntimeError("Mutation pool204 consumer changed during preflight: " + str(path))
    for path, raw in planned.items():
        if raw != originals[path]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", type=Path, required=True)
    print(json.dumps(apply(parser.parse_args().apply), indent=2))
