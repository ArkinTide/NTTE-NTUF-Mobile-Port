"""Read-only213 case identities and exact-source evidence. No old PASS reuse."""
from pathlib import Path
import hashlib, importlib.util, json, re, sys

ROOT=Path(__file__).resolve().parents[1]
CASE_SELECTION=ROOT/'review/release213-cases.json'
CONTRACTS=ROOT/'review/release213-case-contracts.json'
VERSION='2.1.3'
INTERNAL=108

def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    exec(compile(Path(path).read_bytes(),str(path),'exec'),module.__dict__);return module

# This independently authored scope must not shrink when the mutable selector
# is edited. All32 cases run again on the current213 VM; no old receipt counts.
EXPECTED213_CASES=(
    'FrontierBubbles213Tests','FrontierCrash213Tests','FrontierWorld213Tests',
    'FrontierPerformance213Tests','FrontierReticle213Tests','FrontierRed212ScheduledTests',
    'FrontierCollision212Tests','FrontierMenus212Tests','FrontierClock212Tests',
    'FrontierClock212LiveTests','FrontierBubblesAttack212Tests',
    'FrontierBluescreenUI204Yes30Tests','FrontierBluescreenUI204No30Tests',
    'FrontierBluescreenUI204Yes60Tests','FrontierBluescreenUI204No60Tests',
    'FrontierPlayerWallTests','FrontierRedConnectivity204Tests','FrontierWallSurface205Tests',
    'FrontierWeaponTests','FrontierWeaponVisualTests','FrontierContinueWriteTests',
    'FrontierContinueReadTests','FrontierLifecycleTests','FrontierWeatherPerformanceTests',
    'VisualOptionsDrawTests','IOSRenderSurfaceTests','QuestLockedNativeTests',
    'QuestFloorNativeTests','QuestTeleporterNativeTests','QuestHubNativeTests',
    'FrontierBubblesStartupATests','FrontierBubblesStartupBTests',
)
REQUIRED213_CASES=frozenset(EXPECTED213_CASES)
FINAL_CASES=tuple(read(CASE_SELECTION)['cases'])
ARTIFACT_PREFIXES=('frontier-','ntuf-','ntuf212-','ntuf213-','ntte-')
REVIEW_DEPENDENCIES=frozenset((
    'review/verify_213_repairs.py','review/release213-cases.json',
    'review/release213-case-contracts.json','review/release213-python-tests.json',
    'review/capture213_python.py','review/inspect_release213_packages.py',
    'review/verify_212_repairs.py','review/release212-cases.json',
    'review/release212-case-contracts.json','review/verify_bubbles212.py',
))

def require_selection():
    selection=read(CASE_SELECTION)
    assert selection['version']==VERSION and selection['internal']==INTERNAL and selection['status']=='READY'
    assert tuple(selection['cases'])==FINAL_CASES==EXPECTED213_CASES,'Current reviewed32-case scope differs'
    contracts=read(CONTRACTS)
    assert contracts['version']==VERSION and contracts['internal']==INTERNAL and contracts['status']=='READY'
    registered=contracts['cases']
    assert set(registered)==REQUIRED213_CASES,'Every current case needs its independently reviewed contract'
    covered=set()
    for case in EXPECTED213_CASES:
        contract=registered[case]
        assert contract['required'] is True
        markers=contract['markers']
        assert isinstance(markers,list) and markers and len(markers)==len(set(markers))
        assert all(isinstance(marker,str) and marker and 'PASS full internal' not in marker for marker in markers)
        counts=contract.get('marker_counts',{})
        assert isinstance(counts,dict) and set(counts)<=set(markers)
        assert all(type(count) is int and count>=1 for count in counts.values())
        requirements=contract.get('requirements',[])
        assert all(type(value) is int and 1<=value<=17 for value in requirements)
        covered.update(requirements)
        for name in contract.get('artifacts',[]):assert Path(name).name==name
    assert covered==set(range(1,18)),'Current cases must cover all17 requested repairs'
    return registered

def artifact_inventory(directory):
    return {p.name for p in Path(directory).iterdir() if p.is_file()
            and p.name.startswith(ARTIFACT_PREFIXES) and p.suffix.lower() in {'.png','.json'}}

def verify_bubbles_startup213(case,smoke):
    # Source state machine: two rounds(30/60), each new -> real lethal
    # projectile/GameOver/Retry -> retry, then its180 source-tick assertions.
    prefix='NTUF BUBBLES STARTUP real new-run acceptance PASS '
    rows=[json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    expected=[(30,'new'),(30,'retry'),(60,'new'),(60,'retry')]
    assert len(rows)==4 and [(row['requested_rate'],row['trial']) for row in rows]==expected
    skin=0 if case=='FrontierBubblesStartupATests' else 1
    for row,(rate,trial) in zip(rows,expected):
        assert row['skin']==skin and row['random'] is False
        assert row['rate']==row['option_rate']==rate and row['scale']==30/rate
        assert row['language']==('English' if rate==30 else 'Simplified Chinese')
        assert row['native_runs']==row['source_runs']==1 and row['source_ticks']==180
        assert row['weapon']==187+skin and row['weapon_swing'] is True and row['bubbles']>0
        assert row['steps']>=60 and row['ends']>=60 and row['draws']>=30 and row['huds']>=30
        hits=row['attack_hits']
        assert len(hits)==3 and [hit['mode'] for hit in hits]==['desktop-hold','mobile-tap','mobile-hold']
        assert all(hit['damage']==hit['hp_loss']==(6 if skin==0 else 9) for hit in hits)
    assert smoke.count('NTUF BUBBLES STARTUP genuine death-menu Retry returned ')==2
    assert smoke.count('NTUF BUBBLES STARTUP actual GameOver PauseButton Retry requested')==2
    return rows

def verify_clock_recovery213(value):
    # This result is emitted only after the current source's16 recovery
    # assertions, including the production Begin path with inactive Players,
    # same/new GenCont identities, menu and disabled-option boundaries.
    assert value.get('passed') is True and value.get('physical_device_tested') is False
    record=value.get('recovery213')
    assert isinstance(record,dict),'Missing current failed-recovery assertions'
    assert type(record.get('checks')) in (int,float) and record['checks']==16
    assert type(value.get('checks')) in (int,float) and value['checks']>=129+16
    assert type(record.get('failed_recovery_probes')) in (int,float) and record['failed_recovery_probes']==1
    assert type(record.get('latched_rate')) in (int,float) and record['latched_rate']==30
    assert record.get('same_area_generation_reset') is True
    assert record.get('pause_keeps_latch') is True and record.get('device_tested') is False
    return record

def verify_case_identity(case,smoke,artifacts,directory):
    registered=require_selection()
    assert case in REQUIRED213_CASES
    assert smoke.count('PASS full internal selected implemented branches')==1
    assert not re.search(r'^(?:ERROR|FAIL)(?:\s|:|$)',smoke,re.M) and 'ERROR!!!' not in smoke
    record=registered[case]
    for marker in record['markers']:
        assert smoke.count(marker)==record.get('marker_counts',{}).get(marker,1),(case,marker)
    for name in record.get('artifacts',[]):
        assert name in artifacts and sha(Path(directory)/name)==artifacts[name]
        if name.endswith('.png'):
            from PIL import Image
            with Image.open(Path(directory)/name) as image:image.verify()
    if case=='FrontierPerformance213Tests':
        value=read(Path(directory)/'ntuf213-performance.json')
        assert value['passed'] is True and value['device_tested'] is False
        # Four signed scales x24 directions x(65 sampled points+endpoint),
        # plus3 Alarm assertions. Timings describe CPU queries, never phone FPS.
        assert value['checks']==4*24*66+3 and len(value['laser'])==1
        assert value['scope']=='CPU mask queries; no Android frame-rate claim'
        row=value['laser'][0]
        assert row['hostiles']==250 and 0<row['candidates']<row['hostiles']/4 and row['contacts']>0
        assert row['oracle_us']>=0 and row['optimized_us']>=0
    if record.get('validator')=='bubbles-startup213':verify_bubbles_startup213(case,smoke)
    if case=='FrontierClock212Tests':verify_clock_recovery213(read(Path(directory)/'ntuf212-clock-unit.json'))
    old=load('current213_prior_case_implementations',ROOT/'review/verify_212_repairs.py')
    if case in old.FINAL_CASES:
        # Reuse the bound assertion implementations, never old run receipts.
        return old.verify_case_identity(case,smoke,artifacts,Path(directory))

def check_run(run,cases,compiled):
    require_selection()
    assert re.fullmatch(r'\d{8}T\d+Z',run)
    assert tuple(cases)==FINAL_CASES and len(set(cases))==len(cases)
    directory=ROOT/'tests'/run
    assert directory.resolve().parent==(ROOT/'tests').resolve()
    assert read(directory/'compiled-build.json')==compiled
    assert sha(directory/'compile.log')==compiled['log_sha256']
    results=[]
    for case in cases:
        base=directory/case;record=read(base/'receipt.json')
        assert record['case']==case and record['status']=='PASS' and record['exit']==0
        assert record['termination_reason'] is None and record['muted_resources']>100
        assert record['physical_device_tested'] is False and record['desktop']=='private, never activated'
        for key in ('vm_sha256','input_sha256'):assert record[key]==compiled[key]
        assert record['silent_vm_sha256']==sha(ROOT/'build-windows/frontier-silent.win')
        smoke=(base/'smoke.txt').read_text('utf8');log=(base/'runner.log').read_text('utf8',errors='replace')
        assert '###game_end###0' in log and 'ERROR!!!' not in log
        assert not re.search(r'^(?:ERROR|FAIL)(?:\s|:|$)',log,re.M)
        assert set(record['artifacts_sha256'])==artifact_inventory(base),'Missing or unbound current artifact'
        for name,pin in record['artifacts_sha256'].items():assert Path(name).name==name and sha(base/name)==pin
        verify_case_identity(case,smoke,record['artifacts_sha256'],base)
        results.append(record)
    return {'run':'tests/'+run,'count':len(results),'results':results}

def verify_python_sources(value):
    assert value['version']==VERSION and value['internal']==INTERNAL and value['exit']==0 and value['tests']>0
    assert value['source_inputs_unchanged'] and value['reviewer_inputs_unchanged']
    assert REVIEW_DEPENDENCIES<=set(value['reviewer_inputs']),'Missing executed reviewer dependency binding'
    for field in ('source_inputs','reviewer_inputs'):
        assert value[field]
        for name,pin in value[field].items():assert sha(ROOT/name)==pin,(field,name)
    capture=load('current213_source_capture',ROOT/'review/capture213_python.py')
    assert value['source_inputs']==capture.inputs(),'Maintained source inventory changed after Python regression'
    assert value['reviewer_inputs']==capture.reviewer_inputs(),'Reviewer inventory changed after Python regression'
    assert value['review_test_modules']==capture.suite_command()[1]
    log=ROOT/value['log'];assert sha(log)==value['log_sha256']
    text=log.read_text('utf8');assert re.search(r'^Ran '+str(value['tests'])+r' tests in ',text,re.M) and re.search(r'\nOK\s*$',text)

def finalize(run,python_name):
    compiled=read(ROOT/'build-windows/last-success.json');value=read(ROOT/'review'/python_name)
    verify_python_sources(value);observed=check_run(run,FINAL_CASES,compiled)
    report={'status':'SELECTED_DEVELOPMENT_CHECKS_VERIFIED','version':VERSION,'internal':INTERNAL,
            'current_compiled_build':compiled,'current_native_run':observed,'prior_vm_runs':[],
            'case_selection':CASE_SELECTION.relative_to(ROOT).as_posix(),'case_selection_sha256':sha(CASE_SELECTION),
            'case_contracts_sha256':sha(CONTRACTS),'python':value,'physical_device_tested':False,
            'packaging_commit_publication_upload_performed':False}
    report_path=ROOT/'review'/('post213-development-review-'+run+'.json')
    report_path.write_text(json.dumps(report,indent=2),'utf8')
    config={'version':VERSION,'internal':INTERNAL,'status':'READY','run':'tests/'+run,
            'report':report_path.relative_to(ROOT).as_posix(),'report_sha256':sha(report_path),
            'python_evidence':'review/'+python_name,'python_evidence_sha256':sha(ROOT/'review'/python_name),
            'case_selection_sha256':sha(CASE_SELECTION),'review_verifier_sha256':sha(Path(__file__)),
            'vm_sha256':compiled['vm_sha256'],'input_sha256':compiled['input_sha256'],
            'silent_vm_sha256':sha(ROOT/'build-windows/frontier-silent.win'),
            'compile_receipt_sha256':sha(ROOT/'build-windows/last-success.json')}
    (ROOT/'review/release213-config.json').write_text(json.dumps(config,indent=2),'utf8')
    print(json.dumps({'status':'READY','cases':len(FINAL_CASES),'run':run}))

if __name__=='__main__':finalize(sys.argv[1],sys.argv[2])
