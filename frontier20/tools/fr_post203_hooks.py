"""Narrow post-2.0.3 source hooks; never reimport the maintained project."""
from pathlib import Path
import tempfile
from fr_content_hooks import patch


OUTSIDE = ('#macro frMacro_Frontier_Main_mod_gml_currently_outside '
           '((scrFRArrayFindIndex([1, 3, 5, 0, 105, "coast"], GameCont.area) >= 0) || '
           '(scrFRSourceAreaIsString(GameCont.area) && '
           '(scrFRModCall("area", GameCont.area, "area_outside") = true)))')
OUTSIDE_FIXED = ('#macro frMacro_Frontier_Main_mod_gml_currently_outside '
                 'scrFRSourceCurrentlyOutside(GameCont.area)')


def specs(project):
    candidates = list((Path(project)/"scripts").glob("frCode_Frontier_Main_mod_*/*.gml"))
    assert len(candidates) == 1, "Frontier Main stage identity is ambiguous"
    return [
        (candidates[0], OUTSIDE, OUTSIDE_FIXED),
        (Path(project)/"scripts/scrNTTEFullUnlockPresentation/scrNTTEFullUnlockPresentation.gml",
         '    scrUGLocalize();\n',
         '    scrUGLocalize();\n    scrFRLightringLocalizationInstall(); // FRONTIER LIGHTRING DISPLAY\n'),
        (Path(project)/"scripts/scrNTTEFullUnlockPresentation/scrNTTEFullUnlockPresentation.gml",
         '["LAUNCHER","发射器"],["MACHINEGUN","机枪"]',
         '["LIGHTRING","电环"],["LAUNCHER","发射器"],["MACHINEGUN","机枪"]'),
    ]


def _apply_preflight_copy(project):
    pending = {}
    report = []
    for path, before, after in specs(project):
        source = pending.get(path, path.read_text("utf-8-sig"))
        if after in source:
            assert source.count(after) == 1 and before not in source.replace(after, "", 1), \
                f"Post203 installed hook is ambiguous: {path}: {after[:80]}"
            report.append({"file":str(path),"status":"already-applied"})
            continue
        assert source.count(before) == 1, f"Post203 hook anchor changed: {path}: {before[:80]}"
        pending[path] = source.replace(before, after, 1)
        report.append({"file":str(path),"status":"patched"})
    for path, source in pending.items():
        path.write_text(source, "utf-8", newline="\n")
    patch(Path(project), "scripts/scrFrontier_tests/scrFrontier_tests.gml", "POST203 COMPAT DRIVER",
          'if(fr_test_case=="post203-compat") {\n'
          '    if(!scrFRReadyTick()) return;\n'
          '    if(++fr_test_ticks<45) return;\n'
          '    scrFRPost203CompatTests();\n'
          '    scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
          '    game_end();return;\n'
          '}', anchor="function scrFRIntegrationTestStep() {")
    patch(Path(project), "scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml", "POST203 COMPAT ENTRY",
          'if(scrNTTEFullSmokeAsyncCase("FrontierPost203CompatTests")) {scrFRIntegrationTestStart("post203-compat");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', before=True)
    return report


def apply(project):
    """Validate every consumer on copies before modifying any real file.

    The standard marker patcher performs its own anchor/marker validation.
    Run that same patcher against isolated copies as part of this transaction,
    so a late driver/entry anchor failure cannot leave earlier content changed.
    """
    project = Path(project)
    relatives = [path.relative_to(project) for path, _, _ in specs(project)]
    relatives += [
        Path("scripts/scrFrontier_tests/scrFrontier_tests.gml"),
        Path("scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml"),
    ]
    relatives = list(dict.fromkeys(relatives))
    originals = {relative: (project/relative).read_bytes() for relative in relatives}
    with tempfile.TemporaryDirectory(prefix="frontier-post203-preflight-") as temporary:
        copy = Path(temporary)
        for relative, source in originals.items():
            target = copy/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source)
        report = _apply_preflight_copy(copy)
        planned = {relative: (copy/relative).read_bytes() for relative in relatives}
        for record in report:
            record["file"] = str(project/Path(record["file"]).relative_to(copy))
    # Do not overwrite an intervening stage mutation after preflight.
    for relative, source in originals.items():
        assert (project/relative).read_bytes() == source, f"Post203 consumer changed during preflight: {project/relative}"
    for relative, source in planned.items():
        if source != originals[relative]:
            (project/relative).write_bytes(source)
    return report
