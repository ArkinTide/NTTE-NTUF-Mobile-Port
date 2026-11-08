"""Optimize only Hyperion's query and interception cosmetic hot paths."""
from pathlib import Path
import tempfile

from fr_content_hooks import patch
from fr_hyperion_projectile_hooks import ENTRY_NEW, QUERY_NEW


PATTERN = "scripts/frCode_AugmentCompassion_skill_*/*.gml"
NEAREST = ('frMacro_Mutations_AugmentCompassion_skill_gml_call('
           'frMacro_Mutations_AugmentCompassion_skill_gml_scr.instance_nearest_array, x, y, '
           + QUERY_NEW + ')')
NEAREST_NEW = ('(scrFRDroneReference204Enabled() ? ' + NEAREST
               + ' : scrFRDroneNearestHostile204(x,y)) /* FRONTIER DRONE204 DIRECT NEAREST */')
COLLISION_MARK = "// FRONTIER DRONE204 DIRECT INTERCEPT"
COLLISION_NEW = (ENTRY_NEW + '\nif(scrFRDroneIntercept204(scrFROther(other))) return; '
                 + COLLISION_MARK)
DRIVER = ('if(fr_test_case=="drone-performance204") {\n'
          '    if(!variable_instance_exists(id,"fr_drone_performance204")) {\n'
          '        if(!scrFRReadyTick()) return;\n'
          '        if(++fr_test_ticks<45) return;\n'
          '        scrFRDronePerformance204TestsStart(id);\n'
          '    }\n'
          '    if(scrFRDronePerformance204TestsStep(id)) {\n'
          '        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
          '        game_end();\n'
          '    }\n'
          '    return;\n'
          '}')


def _apply_copy(project):
    candidates = sorted(project.glob(PATTERN))
    assert len(candidates) == 1, "Hyperion204 source module is ambiguous"
    path = candidates[0]
    raw = path.read_bytes()
    source = raw.decode("utf-8-sig").replace("\r\n", "\n")
    for old, new, marker in [
        (NEAREST, NEAREST_NEW, "/* FRONTIER DRONE204 DIRECT NEAREST */"),
        (ENTRY_NEW, COLLISION_NEW, COLLISION_MARK),
    ]:
        if new in source:
            assert source.count(new) == 1 and source.count(marker) == 1, "Duplicate Hyperion204 hook"
            assert old not in source.replace(new, "", 1), "Extra Hyperion204 source anchor"
            continue
        assert marker not in source and source.count(old) == 1, "Changed Hyperion204 source anchor: " + marker
        source = source.replace(old, new, 1)
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    newline = "\r\n" if b"\r\n" in raw else "\n"
    path.write_bytes(bom + source.replace("\n", newline).encode("utf8"))
    patch(project, "scripts/scrFrontier_tests/scrFrontier_tests.gml", "DRONE204 PERFORMANCE DRIVER",
          DRIVER, anchor="function scrFRIntegrationTestStep() {")
    patch(project, "scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml", "DRONE204 PERFORMANCE ENTRY",
          'if(scrNTTEFullSmokeAsyncCase("FrontierDronePerformance204Tests")) {scrFRIntegrationTestStart("drone-performance204");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', before=True)
    return {"module": path.relative_to(project).as_posix(), "native_case": "FrontierDronePerformance204Tests",
            "projectile_rules": "unchanged", "cosmetics_per_host_frame": [32, 64],
            "native_and_source_rng_draws": "preserved"}


def apply(project):
    """Preflight all consumers before committing any real stage edit."""
    project = Path(project)
    candidates = sorted(project.glob(PATTERN))
    assert len(candidates) == 1, "Hyperion204 source module is ambiguous"
    relatives = [candidates[0].relative_to(project),
                 Path("scripts/scrFrontier_tests/scrFrontier_tests.gml"),
                 Path("scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml")]
    originals = {relative: (project/relative).read_bytes() for relative in relatives}
    with tempfile.TemporaryDirectory(prefix="frontier-drone204-") as temporary:
        copy = Path(temporary)
        for relative, data in originals.items():
            target = copy/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        result = _apply_copy(copy)
        planned = {relative: (copy/relative).read_bytes() for relative in relatives}
    for relative, data in originals.items():
        assert (project/relative).read_bytes() == data, "Hyperion204 consumer changed during preflight"
    for relative, data in planned.items():
        if data != originals[relative]:
            (project/relative).write_bytes(data)
    return result


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    print(json.dumps(apply(parser.parse_args().project), indent=2))
