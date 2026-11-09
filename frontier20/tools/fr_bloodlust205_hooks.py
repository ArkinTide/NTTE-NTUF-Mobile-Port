"""Retain source Carnivorous Enzymes kills at the native final death boundary."""
from pathlib import Path
from tempfile import TemporaryDirectory

from fr_content_hooks import patch


DEATHS = (
    ("objects/enemy/Destroy_0.gml", "scrNTTEPortalDeathRemember();", False),
    # Both throne phases omit inherited Destroy. Other NTTE leaves either
    # inherit it or explicitly event_perform_object(enemy, ev_destroy, 0).
    ("objects/Nothing/Destroy_0.gml", "instance_create(x, y, NothingDeath)", True),
    ("objects/Nothing2/Destroy_0.gml", "instance_create(x, y, Nothing2Death)", True),
)


def _atomic_patches(project, specs):
    project = Path(project)
    with TemporaryDirectory(prefix="fr-bloodlust205-") as folder:
        probe = Path(folder)
        originals = {}
        for relative, *_ in specs:
            if relative in originals:
                continue
            target = probe / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            originals[relative] = (project / relative).read_bytes()
            target.write_bytes(originals[relative])
        for relative, label, body, anchor, before in specs:
            patch(probe, relative, label, body, anchor=anchor, before=before)
        updates = [(project / relative, (probe / relative).read_bytes())
                   for relative in originals]
    for path, content in updates:
        if path.read_bytes() != content:
            path.write_bytes(content)


def apply(project):
    _atomic_patches(project, [
        (relative, "BLOODLUST205 DYING ENEMY", "scrFRBloodlust205EnemyDeath();", anchor, before)
        for relative, anchor, before in DEATHS
    ])
    return {"death_boundaries": [relative for relative, *_ in DEATHS],
            "authored_threshold_and_healing_retained": True}


def apply_tests(project):
    _atomic_patches(project, [
        ("scripts/scrFrontier_tests/scrFrontier_tests.gml", "BLOODLUST205 COMBAT DRIVER",
         'if(fr_test_case=="bloodlust205") {\n'
         '    if(!variable_instance_exists(id,"fr_bloodlust205")) {\n'
         '        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;\n'
         '        if(++fr_test_ticks<45) return;\n'
         '        scrFRBloodlust205TestsStart(id);return;\n'
         '    }\n'
         '    if(scrFRBloodlust205TestsStep(id)) {\n'
         '        scrNTTESmokeLog("PASS Carnivorous Enzymes actual AugmentStation grant, native projectiles,12+1 deaths, deduplication and injured Player healing across native/NTTE/NTUF at30/60Hz");\n'
         '        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
         '        game_end();\n'
         '    }\n'
         '    return;\n'
         '}', "function scrFRIntegrationTestStep() {", False),
        ("scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml", "BLOODLUST205 COMBAT ENTRY",
         'if(scrNTTEFullSmokeAsyncCase("FrontierBloodlust205Tests")) '
         '{scrFRIntegrationTestStart("bloodlust205");return;}',
         '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', True),
        ("objects/enemy/Destroy_0.gml", "BLOODLUST205 READONLY DEATH",
         'if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))\n'
         '    scrFRBloodlust205TestsDeath();', "scrNTTEPortalDeathRemember();", True),
        ("objects/NTTEFullBloodLust/Create_0.gml", "BLOODLUST205 READONLY PROC",
         'if(os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest))\n'
         '    scrFRBloodlust205TestsProc();', None, False),
    ])
    return {"native_case": "FrontierBloodlust205Tests", "diagnostic_only": False}
