"""Prepare explicit 2.1.2 review selection, then bind fresh evidence only.

The prepare phase edits review metadata only and leaves contracts DRAFT.
The finalize phase validates the finished current-VM report and Python log;
it never compiles, packages, publishes, or reuses historical PASS evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'review'
VERSION = '2.1.2'
INTERNAL = 107


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_new_or_identical(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')
    if path.is_file():
        assert path.read_bytes() == data, 'Preserve existing reviewed metadata: ' + str(path)
    else:
        with path.open('xb') as stream:
            stream.write(data)


def entry(markers, *, artifacts=(), png=(), conditions=None, marker_counts=None,
          requirements=(), validator=None, source=()):
    result = {'required': True, 'requirements': list(requirements), 'markers': list(markers),
              'artifacts': list(artifacts), 'source_files': list(source)}
    if png:
        result['png_artifacts'] = list(png)
    if conditions:
        result['json_conditions'] = conditions
    if marker_counts:
        result['marker_counts'] = marker_counts
    if validator:
        result['validator'] = validator
    return result


def condition(path, op, value):
    return {'path': path, 'op': op, 'value': value}


def regression_contracts():
    wall = [f'frontier-wall-surface205-{kind}{area}.png' for area in (0, 7, 206)
            for kind in ('area', 'reference')]
    hud = [f'frontier-bubbles-{label}-hud.png' for label in
           ('meter', 'tinted', 'native', 'retired', 'normal', 'pause', 'low', 'fainted', 'health', 'partial')]
    visual = entry([
        'PASS FRONTIER native scrWeapons rebuild retained77 source metadata rows, both Bubbles starters and a physical fusion',
        'PASS FRONTIER real GPU native Bubbles health anchor119,11, ordinary/paused/low-health/fainted GUI, neutral restored drawing state, source fill and no duplicate old projection',
        'PASS FRONTIER all10 NTUF melee callbacks match native fire, all7 NTTE melee swings and source primary/secondary physical reload at30/60Hz',
    ], artifacts=hud, png=hud, source=('native/weapon_visual_tests.gml', 'native/tests.gml'))
    visual['png_exact_dimensions'] = {name: [160, 96] for name in hud}
    records = {
        'FrontierCollision212Tests': entry([
            'PASS NTUF212 native stale wall and live Slash contact rate=30',
            'PASS NTUF212 native stale wall and live Slash contact rate=60',
        ], requirements=(3,), source=('native/collision212_tests.gml',)),
        'FrontierPlayerWallTests': entry([
            'PASS FRONTIER PLAYER WALL real tile/packed overlap/walk/slide/seam/negative/fractional/equal-floor/roll/Frog/Hammerhead at30/60Hz',
        ], source=('native/player_wall_tests.gml',)),
        'FrontierRedConnectivity204Tests': entry([
            'NTUF RED REGRESSION204 PASS generated seams, ordinary Warp paths and hidden-room round trips',
        ], artifacts=('frontier-red-regression204.json',), validator='red204',
            source=('native/red_connectivity204_tests.gml',)),
        'FrontierWallSurface205Tests': entry([
            'PASS WALL SURFACE205 actual native art/collision, all29 area styles and independent GPU reference',
        ], artifacts=('frontier-wall-surface205.json', *wall), png=wall, validator='wall205',
            source=('native/wall_surface205_tests.gml',)),
        'FrontierWeaponTests': entry([
            'PASS FRONTIER 77 ordinary input and NPC fire paths at30/60, charge release, team/owner, inventory, dynamic metadata and mixed fusion',
            'PASS FRONTIER ordinary source MOD strings through locals/arrays/controller slots and actual metadata dispatch; native numeric inventory and canonical LWO identity retained',
            'PASS FRONTIER actual native same-type twin swap, source ground assignment, two-way pickup/drop and extra-slot state identity',
            'PASS FRONTIER real weapon fire and state compatibility',
        ], source=('native/weapon_tests.gml', 'native/tests.gml')),
        'FrontierWeaponVisualTests': visual,
        'FrontierContinueWriteTests': entry([
            'FRONTIER COLD WRITE native session/globals/Player binary + independent symbolic expected fixture OK',
            'FRONTIER COLD WRITE ordinary next-room lifecycle preserved source ammo deltas and native live caps/grants',
        ], artifacts=('frontier-cold-expected.json',), source=('native/continue_tests.gml', 'native/tests.gml')),
        'FrontierContinueReadTests': entry([
            'FRONTIER COLD READ native preview/full loader + new Bubbles Player + Surgery/assets/cache/pool/LWO/status/ammo adoption OK',
            'FRONTIER COLD READ real room_restart + async terrain + saved events + finalized Bubbles/LWO +24source ticks OK',
        ], source=('native/continue_tests.gml', 'native/tests.gml')),
        'FrontierLifecycleTests': entry([
            'NTUF LIFECYCLE native pause/Continue/SkillIcon.Mouse4/GenCont PASS',
            'PASS FRONTIER native pause, mutation and generation lifecycle at30/60Hz',
        ], marker_counts={'NTUF LIFECYCLE native pause/Continue/SkillIcon.Mouse4/GenCont PASS': 2},
            source=('native/lifecycle_tests.gml', 'native/tests.gml')),
        'FrontierWeatherPerformanceTests': entry([
            'PASS NTUF actual Aurora/Meteor/Scrapyards nested actor callbacks use live native background colour',
            'PASS NTUF FRESH WEATHER FILTER',
        ], artifacts=('frontier-weather-performance.json',), validator='weather-perf',
            source=('native/weather_performance_tests.gml', 'native/tests.gml')),
        'VisualOptionsDrawTests': entry([
            'PASS Trench actual land pixels/pit alpha/nested sparks/cache frame/target loss/two quality settings',
            'FULL VISUAL OPTIONS actual Coast8/Sludge/Pit mask+wall+spark targets/main+minor/default floating display/min1of3/fractional resize/no cap/sourceSludge2of3 threshold/Unblend[2]1of4+partial fallback pixels/caller target+draw state OK @30',
            'FULL VISUAL OPTIONS actual Coast8/Sludge/Pit mask+wall+spark targets/main+minor/default floating display/min1of3/fractional resize/no cap/sourceSludge2of3 threshold/Unblend[2]1of4+partial fallback pixels/caller target+draw state OK @60',
        ], marker_counts={'PASS Trench actual land pixels/pit alpha/nested sparks/cache frame/target loss/two quality settings': 2},
            artifacts=('ntte-trench-alpha-30.png', 'ntte-trench-alpha-60.png'),
            png=('ntte-trench-alpha-30.png', 'ntte-trench-alpha-60.png'),
            source=('staging/project/scripts/scrNTTEFullVisualOptionsNativeTests/scrNTTEFullVisualOptionsNativeTests.gml',)),
        'IOSRenderSurfaceTests': entry([
            'IOS SURFACE BOUNDS: actual eight Coast targets/phone-scale>5000 request/bind rejection parent protection/direct shore safe-frame/native visibility/next-frame smaller recovery/resume OK @30',
            'IOS SURFACE BOUNDS: actual eight Coast targets/phone-scale>5000 request/bind rejection parent protection/direct shore safe-frame/native visibility/next-frame smaller recovery/resume OK @60',
        ], source=('staging/project/scripts/scrNTTEFullIOSRenderSurfaceTests/scrNTTEFullIOSRenderSurfaceTests.gml',)),
    }
    records['FrontierWallSurface205Tests']['png_exact_dimensions'] = {name: [128, 96] for name in wall}
    return records


PYTHON_MODULES = (
    'review/test_delivery212.py', 'review/test_review212.py', 'review/test_prepare_review212.py',
    'review/test_package_review212.py',
    'tools/test_frontier_compiler.py', 'tools/test_frontier_native_test_entrypoints.py',
    'tools/test_frontier_content_hooks.py', 'tools/test_fr_bluescreen_ui_hooks.py',
    'tools/test_frontier_bluescreen204_hooks.py', 'tools/test_frontier_bubbles_preference_hooks.py',
    'tools/test_frontier_lifecycle_hooks.py', 'tools/test_frontier_wall_hooks.py',
    'tools/test_frontier_wall_surface205_hooks.py', 'tools/test_frontier_red_connectivity204_hooks.py',
    'tools/test_fr_red212_hooks.py',
    'tools/test_frontier_red_wall_query204_hooks.py', 'tools/test_frontier_weapon_visual_hooks.py',
    'tools/test_frontier_post203_weather_wall_hooks.py', 'tools/test_frontier_lib_performance_hooks.py',
    'tools/test_frontier_performance_hooks.py', 'tools/test_frontier_menu_hooks.py',
)


def verify_source_anchors(records):
    for case, contract in records.items():
        sources = contract.get('source_files', [])
        if not sources:
            continue
        text = '\n'.join((ROOT / name).read_text('utf-8-sig') for name in sources)
        for marker in contract['markers']:
            # Numeric @rate suffixes and the collision loop's rate are emitted
            # at runtime. Check their retained literal source prefix here.
            literal = re.sub(r'(?:@(?:30|60)|rate=(?:30|60))$', lambda match: 'rate=' if match[0].startswith('rate=') else '@', marker)
            assert literal in text, (case, 'Dedicated source marker missing', marker)


def prepare():
    registry_path = REVIEW / 'release212-case-contracts.json'
    registry = read(registry_path)
    assert registry['version'] == VERSION and registry['internal'] == INTERNAL and registry['status'] == 'DRAFT'
    additions = regression_contracts()
    verify_source_anchors(additions)
    for case, contract in additions.items():
        assert case not in registry['cases'] or registry['cases'][case] == contract, ('Preserve existing case contract', case)
        registry['cases'][case] = contract
    with registry_path.open('w', encoding='utf8') as stream:
        json.dump(registry, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    required = ['FrontierRed212ScheduledTests', 'FrontierCollision212Tests',
                'FrontierMenus212Tests', 'FrontierClock212Tests', 'FrontierClock212LiveTests',
                'FrontierBubblesAttack212Tests',
                'FrontierBluescreenUI204Yes30Tests', 'FrontierBluescreenUI204No30Tests',
                'FrontierBluescreenUI204Yes60Tests', 'FrontierBluescreenUI204No60Tests',
                *[name for name in additions if name != 'FrontierCollision212Tests']]
    write_new_or_identical(REVIEW / 'release212-cases.json', {
        'version': VERSION, 'internal': INTERNAL, 'status': 'DRAFT', 'cases': required,
        'pending': 'Finalize the real 2.1.2 red-corridor repair contract; the diagnostic probe is excluded.',
        'order_dependencies': [['FrontierContinueWriteTests', 'FrontierContinueReadTests']],
        'historical_pass_evidence_reused': False,
    })
    write_new_or_identical(REVIEW / 'release212-python-tests.json', {
        'version': VERSION, 'internal': INTERNAL, 'status': 'DRAFT', 'modules': list(PYTHON_MODULES),
        'scope': 'Explicit fixture/compiler/installer/gate tests on current maintained source. Native runtime results are separate.',
    })
    write_new_or_identical(REVIEW / 'release212-config.json', {
        'version': VERSION, 'internal': INTERNAL, 'status': 'DRAFT',
        'reason': 'Fresh complete current-VM runtime and current Python evidence are required before finalization.',
    })
    print(json.dumps({'status': 'DRAFT', 'planned_cases': required, 'python_modules': len(PYTHON_MODULES),
                      'missing_case_contracts': [case for case in required if case not in registry['cases']],
                      'production_source_modified': False, 'build_or_publication_performed': False}, indent=2))


def load_review():
    path = REVIEW / 'verify_212_repairs.py'
    spec = importlib.util.spec_from_file_location('ntuf212_review_finalization', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def finalize(run_name, python_name):
    assert re.fullmatch(r'\d{8}T\d+Z', run_name)
    assert re.fullmatch(r'post212-python-regression(?:-[a-z0-9]+)?\.json', python_name)
    reviewer = load_review()
    reviewer.require_selection()
    assert read(REVIEW / 'release212-cases.json')['status'] == 'READY'
    assert read(REVIEW / 'release212-python-tests.json')['status'] == 'READY'
    python_path = REVIEW / python_name
    reviewer.verify_python_sources(read(python_path))
    report = REVIEW / ('post212-development-review-' + run_name + '.json')
    if not report.is_file():
        subprocess.run([sys.executable, '-B', str(REVIEW / 'verify_212_repairs.py'),
                        'tests/' + run_name, 'review/' + python_name], cwd=ROOT, check=True)
    observed = read(report)
    # Also verify current staged bytes when reusing an existing review report.
    # A previously valid report cannot finalize edited sources or a changed VM.
    current, compiled = reviewer.current_build()
    assert observed['version'] == VERSION and observed['internal'] == INTERNAL
    assert observed['status'] == 'SELECTED_DEVELOPMENT_CHECKS_VERIFIED'
    assert observed['current_compiled_build'] == compiled
    assert observed['staged_files'] == len(current['staged_files'])
    assert observed['current_native_run'] == reviewer.check_run(run_name, reviewer.FINAL_CASES, compiled)
    assert observed['red212_supplement'] == reviewer.verify_red212_supplement(compiled)
    assert observed['case_selection_sha256'] == sha(REVIEW / 'release212-cases.json')
    assert observed['case_contracts_sha256'] == sha(REVIEW / 'release212-case-contracts.json')
    assert observed['prior_vm_runs'] == [] and observed['physical_device_tested'] is False
    assert {key: observed['python'][key] for key in read(python_path)} == read(python_path)
    config = {'version': VERSION, 'internal': INTERNAL, 'status': 'READY', 'run': 'tests/' + run_name,
              'report': report.relative_to(ROOT).as_posix(), 'report_sha256': sha(report),
              'python_evidence': python_path.relative_to(ROOT).as_posix(), 'python_evidence_sha256': sha(python_path),
              'case_selection_sha256': sha(REVIEW / 'release212-cases.json'),
              'review_verifier_sha256': sha(REVIEW / 'verify_212_repairs.py'),
              'vm_sha256': compiled['vm_sha256'], 'input_sha256': compiled['input_sha256'],
              'silent_vm_sha256': sha(ROOT / 'build-windows/frontier-silent.win'),
              'compile_receipt_sha256': sha(ROOT / 'build-windows/last-success.json')}
    path = REVIEW / 'release212-config.json'
    if path.is_file():
        prior = read(path)
        if prior.get('status') == 'READY':
            assert prior == config, 'Preserve an existing finalized release config'
            print(path)
            return
        assert prior.get('status') == 'DRAFT' and prior['version'] == VERSION and prior['internal'] == INTERNAL
        archive = REVIEW / 'draft-configs212'
        archive.mkdir(exist_ok=True)
        saved = archive / (sha(path) + '.json')
        if not saved.is_file():
            with saved.open('xb') as stream:
                stream.write(path.read_bytes())
    data = (json.dumps(config, ensure_ascii=False, indent=2) + '\n').encode('utf8')
    pending = path.with_suffix('.pending.json')
    with pending.open('xb') as stream:
        stream.write(data)
    pending.replace(path)
    print(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='phase', required=True)
    sub.add_parser('prepare')
    final = sub.add_parser('finalize')
    final.add_argument('run', help='Selected current run directory name, without tests/')
    final.add_argument('python_evidence', help='Current review JSON basename')
    args = parser.parse_args()
    if args.phase == 'prepare':
        prepare()
    else:
        finalize(args.run, args.python_evidence)


if __name__ == '__main__':
    main()
