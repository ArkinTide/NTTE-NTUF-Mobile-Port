"""Read-only review of selected 2.1.0 evidence. Never build or publish."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_input_manifest

CASE_SELECTION=ROOT/'review/release210-cases.json'
PRIOR_MANIFEST=ROOT/'mobile-release205-20261109/staged-source-manifest.json'

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def read(path): return json.loads(Path(path).read_text('utf-8-sig'))

PRIOR_MANIFEST_SHA256=sha(PRIOR_MANIFEST)
REQUIRED210_CASES=frozenset({
    'FrontierFeatures210Tests','FrontierContent210Tests','FrontierRedTerrain210Tests',
    'FrontierDronePerformance204Tests','HyperionProjectileTests','FrontierVisual205Tests',
    'FrontierOptionTests','FrontierWeaponTests','FrontierAreaTests','FrontierRestartTests',
    'FrontierContinueWriteTests','FrontierContinueReadTests','FrontierEventTests',
    'FrontierFollowup210Tests','FrontierBluescreenUI204Yes30Tests','FrontierBluescreenUI204Yes60Tests'})

def load_cases():
    s=read(CASE_SELECTION)
    assert s['version']=='2.1.0' and s['internal']==105
    c=s['cases']
    assert len(c)==len(set(c))==28 and REQUIRED210_CASES<=set(c)
    assert all(re.fullmatch(r'[A-Za-z]\w+Tests',v) for v in c)
    return tuple(c)

FINAL_CASES=load_cases()

def verify_case_identity(case,smoke,artifacts,directory):
    assert case in FINAL_CASES
    assert smoke.count('PASS full internal selected implemented branches')==1
    markers={
      'FrontierFeatures210Tests':[
        'PASS NTUF210 source charge HUD and sticky achievement gates',
        'PASS NTUF210 same-room weather/native music boundary and next-room isolation',
        'PASS NTUF210 reciprocal friendly bubble collision and live spatial threat teams',
        'NTUF210 content cycle 1 enabled=0'],
      'FrontierContent210Tests':[
        'PASS NTUF210 actual MenuOptions Enter dispatch ntuf',
        'PASS NTUF210 actual MenuOptions Enter dispatch undergrowth',
        'PASS NTUF210 genuine OFF new-run, loadout fallback, pause, saved packs, ON Retry and asynchronous weather music'],
      'FrontierFollowup210Tests':[
        'PASS NTUF210 separate Frontier_Fishing records obey per-slot disk and console gates',
        'PASS NTUF210 per-slot NTTE+NTUF disk persistence, console sticky/Continue exclusions, gold gates, actual Beetle tooltip and real charged powder30/60'],
      'FrontierBluescreenUI204Yes30Tests':[
        'PASS NTUF210 real Robot death -> raw YES -> three processors/waves -> actual portal -> normal desert'],
      'FrontierBluescreenUI204Yes60Tests':[
        'PASS NTUF210 real Robot death -> raw YES -> three processors/waves -> actual portal -> normal desert'],
      'FrontierRedTerrain210Tests':[
        'NTUF210 red terrain seed=1 ', 'NTUF210 red terrain seed=9 ', 'NTUF210 red terrain seed=91 ',
        'PASS NTUF210 mutable wall clips, unique cells and generated red secret-road boundaries'],
      'FrontierDronePerformance204Tests':['FRONTIER DRONE204 ACCEPTED '],
    }
    for marker in markers.get(case,[]): assert marker in smoke,(case,marker)
    if case=='FrontierDronePerformance204Tests':
        name='frontier-drone-performance204.json'
        assert name in artifacts
        data=read(directory/name)
        assert data['physical_device_tested'] is False
        rows=data['natural_collision']
        assert len(rows)==4 and {(r['rate'],r['reference']) for r in rows}=={
            (30,False),(30,True),(60,False),(60,True)}
        # Two lanes,256 projectiles each; variants1/2 are hostile and0/3
        # are allied/neutral. Verify the actual512-projectile fixture split.
        assert all(r['projectiles']==512 and r['hostile_intercepted']==256
                   and r['allied_neutral_passed']==256 for r in rows)
    return {'native_assertions_completed':True,'physical_device_tested':False}

def check_run(name,cases,compiled):
    assert re.fullmatch(r'\d{8}T\d+Z',name) and tuple(cases)==FINAL_CASES
    run=ROOT/'tests'/name
    assert read(run/'compiled-build.json')==compiled
    assert sha(run/'compile.log')==compiled['log_sha256']
    results=[]
    for case in cases:
        d=run/case;r=read(d/'receipt.json')
        assert r['case']==case and r['status']=='PASS' and r['exit']==0 and r['termination_reason'] is None
        assert r['vm_sha256']==compiled['vm_sha256'] and r['input_sha256']==compiled['input_sha256']
        assert r['physical_device_tested'] is False and r['muted_resources']>100 and r['desktop']=='private, never activated'
        if 'previous_failed_attempt' in r:
            prior=r['previous_failed_attempt'];p=(ROOT/prior['path']).resolve(strict=True)
            assert p.is_relative_to((ROOT/'tests/failed-attempts').resolve())
            assert sha(p/'receipt.json')==prior['receipt_sha256']
            failed=read(p/'receipt.json')
            assert failed['status']=='FAIL' and failed['case']==case
            assert failed['vm_sha256']==r['vm_sha256'] and failed['input_sha256']==r['input_sha256']
        smoke=(d/'smoke.txt').read_text('utf8');log=(d/'runner.log').read_text('utf8',errors='replace')
        assert '###game_end###0' in log and 'ERROR!!!' not in log and 'ERROR!!!' not in smoke
        assert not re.search(r'^ERROR(?:\s|$)',smoke,re.M)
        artifacts=r['artifacts_sha256']
        for a,pin in artifacts.items():
            assert Path(a).name==a and sha(d/a)==pin
        verify_case_identity(case,smoke,artifacts,d)
        results.append({**r,'receipt_sha256':sha(d/'receipt.json'),'smoke_sha256':sha(d/'smoke.txt'),
                        'runner_log_sha256':sha(d/'runner.log')})
    assert len({r['silent_vm_sha256'] for r in results})==1
    return {'count':len(results),'results':results}

def capture_module():
    directory=str(ROOT/'review')
    if directory not in sys.path:sys.path.insert(0,directory)
    p=ROOT/'review/capture210_python.py'
    spec=importlib.util.spec_from_file_location('capture210_current',p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

def verify_python_sources(evidence):
    m=capture_module()
    assert evidence['version']=='2.1.0' and evidence['internal']==105
    assert evidence['exit']==0 and evidence['tests']>=110
    assert evidence['source_inputs_unchanged'] and evidence['reviewer_inputs_unchanged']
    assert evidence['source_inputs']==m.inputs() and evidence['reviewer_inputs']==m.reviewer_inputs()
    p=(ROOT/evidence['log']).resolve();assert p.is_relative_to((ROOT/'review').resolve())
    assert sha(p)==evidence['log_sha256']
    output=p.read_text('utf8')
    assert re.search(r'^Ran '+str(evidence['tests'])+r' tests in ',output,re.M)
    assert re.search(r'\nOK\s*$',output) and not re.search(r'^(FAILED|ERROR:|FAIL:)',output,re.M)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('python_evidence');args=ap.parse_args()
    current=build_input_manifest.snapshot();compiled=read(ROOT/'build-windows/last-success.json')
    assert current['input_sha256']==compiled['input_sha256']
    assert sha(ROOT/'build-windows/nuclearthronemobile.win')==compiled['vm_sha256']
    assert sha(ROOT/'build-windows/compile.log')==compiled['log_sha256']
    assert '#macro GAME_VERSION "2.1.0"' in (ROOT/'staging/project/objects/UberCont/Create_0.gml').read_text('utf8')
    observed=check_run(Path(args.run).name,FINAL_CASES,compiled)
    python=read(ROOT/args.python_evidence);verify_python_sources(python)
    python={**python,'evidence_scope':'exact current maintained Python/native/reviewer inputs and passing aggregate log'}
    old=read(PRIOR_MANIFEST)['files'];new=current['staged_files']
    changes=[{'path':n,'before':old.get(n),'after':new.get(n)} for n in sorted(old.keys()|new.keys()) if old.get(n)!=new.get(n)]
    workspace=ROOT.parents[2]
    protected=[workspace/'github-publish/release-2.0.5/publication-receipt.json',
               ROOT/'mobile-release205-20261109/deliverables/NuclearThrone.NTTE-NTUF-Android-2.0.5.apk',
               ROOT/'mobile-release205-20261109/deliverables/NuclearThrone.NTTE-NTUF-iOS-2.0.5.ipa']
    report={'status':'SELECTED_DEVELOPMENT_CHECKS_VERIFIED','version':'2.1.0','internal':105,
      'current_compiled_build':compiled,'current_native_run':observed,'python':python,
      'case_selection':CASE_SELECTION.relative_to(ROOT).as_posix(),'case_selection_sha256':sha(CASE_SELECTION),
      'prior_vm_runs':[],'prior_source_manifest_sha256':PRIOR_MANIFEST_SHA256,
      'changed_inputs_since_prior_vm':changes,'staged_files':len(new),
      'published_files_unchanged':{str(p):sha(p) for p in protected},
      'physical_device_tested':False,'packaging_commit_publication_upload_performed':False,
      'utc':datetime.now(timezone.utc).isoformat()}
    out=ROOT/'review'/('post210-development-review-'+Path(args.run).name+'.json')
    with out.open('x',encoding='utf8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
    print(out)

if __name__=='__main__': main()
