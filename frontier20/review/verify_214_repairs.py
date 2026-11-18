"""Read-only214 case identities and exact-source evidence. No old PASS reuse."""
from pathlib import Path
import hashlib, importlib.util, json, math, re, sys

ROOT=Path(__file__).resolve().parents[1]
CASE_SELECTION=ROOT/'review/release214-cases.json'
CONTRACTS=ROOT/'review/release214-case-contracts.json'
VERSION='2.1.4'
INTERNAL=109

def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    exec(compile(Path(path).read_bytes(),str(path),'exec'),module.__dict__);return module

# This independently authored scope must not shrink when the mutable selector
# is edited. All37 cases run again on the current214 VM; no old receipt counts.
EXPECTED214_CASES=(
    'FrontierMelee214Tests','FrontierCrash214Tests','FrontierMenus214Tests','FrontierPerformance214Tests','FrontierMovement214Tests',
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
REQUIRED214_CASES=frozenset(EXPECTED214_CASES)
FINAL_CASES=tuple(read(CASE_SELECTION)['cases'])
ARTIFACT_PREFIXES=('frontier-','ntuf-','ntuf212-','ntuf213-','ntuf214-','ntte-')
REVIEW_DEPENDENCIES=frozenset((
    'review/verify_214_repairs.py','review/release214-cases.json',
    'review/release214-case-contracts.json','review/release214-python-tests.json',
    'review/capture214_python.py','review/inspect_release214_packages.py',
    'review/verify_212_repairs.py','review/release212-cases.json',
    'review/release212-case-contracts.json','review/verify_bubbles212.py',
    'review/test_review214.py',
    'review/verify_213_repairs.py','review/capture213_python.py',
    'review/inspect_release213_packages.py','review/release213-cases.json',
    'review/release213-case-contracts.json','review/release213-python-tests.json',
))
REQUIRED214_PYTHON_MODULES=frozenset((
    'review/test_review214.py','tools/test_fr_crash214_hooks.py',
    'tools/test_fr_perf214_hooks.py','tools/test_frontier_melee214_hooks.py',
    'tools/test_fr_menus214_hooks.py','tools/test_fr_movement214_hooks.py',
))
MENUS214_PNGS=frozenset(
    [f'ntuf214-robot-{hz}-{view}.png' for hz in (30,60) for view in range(2)]
    +[f'ntuf214-surgery-{language}-{view}-{slot}.png' for language in range(2)
      for view in range(2) for slot in range(5)]
    +[f'ntuf214-preferences-{language}.png' for language in range(2)])
MELEE214_WEAPONS=frozenset((234,202,208,211,214,217,219,222,187,188,
                          134,144,149,160,164,165,177))
SCYTHE214_PNGS=frozenset(f'ntuf214-scythe-natural-{hz}-{stack}-{heavy}.png'
                         for hz in (30,60) for stack in range(2) for heavy in range(2))
MELEE214_ARTIFACTS=SCYTHE214_PNGS|{
    'ntuf214-scythe-natural.json','ntuf214-scythe-control-no-arrow.png',
    'ntuf214-scythe-control-old-arrow-negative.png'}
PERFORMANCE214_SELECTORS=frozenset((
    'projectile','custom_projectile','thrown_weapon','ordinary_slash',
    'array_union','array_duplicate','array_empty'))
PERFORMANCE214_TARGETS=frozenset((
    'base_ref','base_numeric','slash_ref','custom_projectile_ref','custom_projectile_numeric',
    'custom_slash_ref','custom_slash_numeric','ordinary_object_ref','thrown_ref','pickup_ref',
    'selector_projectile','selector_custom_projectile','selector_slash','selector_weapon_pickup',
    'noone','self_keyword','other_keyword','self_alias','other_alias','all_alias',
    'deleted_ref','deleted_numeric','invalid_positive','invalid_negative','undefined',
    'struct_empty','struct_id','array_empty','array_instances','string','method','ptr_null',
    'boolean_true','zero_numeric'))

def require_selection():
    selection=read(CASE_SELECTION)
    assert selection['version']==VERSION and selection['internal']==INTERNAL and selection['status']=='READY'
    assert tuple(selection['cases'])==FINAL_CASES==EXPECTED214_CASES,'Current reviewed37-case scope differs'
    contracts=read(CONTRACTS)
    assert contracts['version']==VERSION and contracts['internal']==INTERNAL and contracts['status']=='READY'
    registered=contracts['cases']
    assert set(registered)==REQUIRED214_CASES,'Every current case needs its independently reviewed contract'
    covered=set()
    for case in EXPECTED214_CASES:
        contract=registered[case]
        assert contract['required'] is True
        markers=contract['markers']
        assert isinstance(markers,list) and markers and len(markers)==len(set(markers))
        assert all(isinstance(marker,str) and marker and 'PASS full internal' not in marker for marker in markers)
        counts=contract.get('marker_counts',{})
        assert isinstance(counts,dict) and set(counts)<=set(markers)
        assert all(type(count) is int and count>=1 for count in counts.values())
        requirements=contract.get('requirements',[])
        assert all(type(value) is int and 1<=value<=8 for value in requirements)
        covered.update(requirements)
        for name in contract.get('artifacts',[]):assert Path(name).name==name
    assert covered==set(range(1,9)),'Current cases must cover all8 requested repairs'
    assert set(registered['FrontierMenus214Tests']['artifacts'])==MENUS214_PNGS|{'ntuf214-menus.json'}
    assert set(registered['FrontierMenus214Tests']['png_artifacts'])==MENUS214_PNGS
    assert set(registered['FrontierMelee214Tests']['artifacts'])==MELEE214_ARTIFACTS
    assert set(registered['FrontierMelee214Tests']['png_artifacts'])==MELEE214_ARTIFACTS-{'ntuf214-scythe-natural.json'}
    assert registered['FrontierPerformance214Tests']['artifacts']==['ntuf214-performance.json']
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


def number(value, *, minimum=None):
    assert type(value) in (int,float) and math.isfinite(value),'Invalid numeric evidence'
    if minimum is not None:assert value>=minimum
    return value


def verify_menus214(value):
    assert value.get('passed') is True and value.get('physical_android_tested') is False
    assert number(value.get('checks'))==140
    rows=value.get('cases');assert isinstance(rows,list) and len(rows)==28
    robot=[row for row in rows if row.get('kind')=='robot']
    surgery=[row for row in rows if row.get('kind')=='surgery']
    preferences=[row for row in rows if row.get('kind')=='preference']
    views=((424,240,848,480),(280,160,840,480))
    assert len(robot)==4 and {(row['hz'],tuple(row['view'])) for row in robot}=={
        (hz,view) for hz in (30,60) for view in views}
    for row in robot:
        assert number(row['samples'])>20 and number(row['old_matrix_pixel_errors'])>10
        assert number(row['fixed_matrix_pixel_errors'])==0 and row['missing_child_recovered'] is True
    languages=('Simplified Chinese','English')
    assert len(surgery)==20 and {(row['language'],tuple(row['view']),row['slot']) for row in surgery}=={
        (language,view,slot) for language in languages for view in views for slot in range(5)}
    for row in surgery:
        layout=row['layout'];width,height=row['view'][:2]
        for key in ('x','top','width','height','title_y','body_y','title_h','body_h','title_scale','body_scale'):
            number(layout[key])
        assert layout['width']>0 and layout['height']>0 and layout['title_h']>0 and layout['body_h']>0
        assert 0<layout['title_scale']<=1 and 0<layout['body_scale']<=1
        assert layout['body_y']>=layout['title_y']+layout['title_h']+6
        assert layout['title_y']>=layout['top']+8
        assert layout['body_y']+layout['body_h']<=layout['top']+layout['height']-7.9
        # The authored fixture uses this displaced native world view. Bounds
        # must come from the measured final font, not the source's16px guess.
        assert layout['x']-layout['width']/2>=500000+7.9
        assert layout['x']+layout['width']/2<=500000+width-7.9
        assert layout['top']>=499800+7.9 and layout['top']+layout['height']<=499800+height-7.9
        assert isinstance(layout['title'],str) and layout['title']
        assert isinstance(layout['body'],str) and layout['body']
        assert layout['cjk'] is (row['language']=='Simplified Chinese')
        assert number(row['glyph_samples'])>15
        ink=row['line_ink'];assert isinstance(ink,list) and len(ink)==len(layout['body'].split('\n'))
        last=-1
        for span in ink:
            assert len(span)==2 and number(span[0])>=0 and number(span[1])>=span[0]
            assert last<0 or span[0]>last+1,'Rendered Surgery lines lack blank leading'
            last=span[1]
    assert len(preferences)==4 and {(row['language'],row['key']) for row in preferences}=={
        (language,key) for language in languages for key in ('cprefs_parrot','cprefs_bubbles')}
    for language in languages:
        pair=[row['layout'] for row in preferences if row['language']==language]
        assert all(number(row['menu_pixels'])>100 for row in preferences if row['language']==language)
        for layout in pair:
            for key in ('text_x','text_y','icon_cx','icon_cy','icon_x','icon_y'):number(layout[key])
            assert isinstance(layout['label'],str) and layout['label']
            assert 100<layout['text_x']<160 and layout['text_x']>layout['icon_cx']
            assert number(layout['value_x'])>layout['text_x']
            assert number(layout['text_width'])>0 and 0<number(layout['text_scale'])<=1
            assert layout['text_x']+layout['text_width']<=layout['value_x']-7.9
        assert all(abs(pair[0][key]-pair[1][key])<0.000001 for key in ('text_x','icon_cx','icon_cy'))
    return rows


def verify_performance214(value):
    assert value.get('physical_device_tested') is False
    assert value.get('scope')=='Fresh projectile family queries; no device FPS claim'
    assert number(value.get('checks'))==4*3*(2+261)
    rows=value.get('rows');assert isinstance(rows,list) and len(rows)==12
    selectors={row['selector'] for row in rows}
    assert selectors=={'@ref object(projectile)','@ref object(FRCustomProjectile)',-10110}
    assert {(row['phase'],row['selector']) for row in rows}=={
        (phase,selector) for phase in range(4) for selector in selectors}
    for row in rows:
        number(row['count'],minimum=0)
        assert row['count']==int(row['count'])
        number(row['oracle_us'],minimum=0);number(row['optimized_us'],minimum=0)
    assert value.get('compatibility_contract')=='legacy-scrFRInstanceIs-without-fast-v1'
    assert number(value.get('compatibility_checks'))==266
    compatibility=value.get('compatibility');assert isinstance(compatibility,list) and len(compatibility)==266
    expected={(context,target,selector)
              for context,targets in (
                  ('fixture_scope',PERFORMANCE214_TARGETS),
                  ('projectile_with_scope',{'self_keyword','other_keyword','self_alias','other_alias'}))
              for target in targets for selector in PERFORMANCE214_SELECTORS}
    assert len(expected)==266
    assert {(row['context'],row['target'],row['selector']) for row in compatibility}==expected
    for row in compatibility:
        assert row.get('matched') is True
        assert row['outcome']==row['optimized_outcome'] and row['outcome'] in ('return','throw')
        if row['outcome']=='return':
            assert isinstance(row.get('value_type'),str) and row['value_type']
            assert type(row.get('value')) is bool or number(row.get('value')) in (0,1)
        else:assert 'value' not in row and 'value_type' not in row
    return rows


def verify_melee214(smoke):
    raw_prefix='FRONTIER214 Long Arms launch '
    fusion_prefix='FRONTIER214 Long Arms fusion launch '
    rows=[]
    for line in smoke.splitlines():
        if line.startswith(raw_prefix):
            row=json.loads(line[len(raw_prefix):]);assert row.get('fusion',False) is False
            assert isinstance(row['name'],str) and row['name'] and row['name']!='LOCKED';rows.append(row)
        if line.startswith(fusion_prefix):
            row=json.loads(line[len(fusion_prefix):]);assert row.get('fusion') is True
            assert row.get('melee_role')=='front';rows.append(row)
    assert len(rows)==68 and {row['hz'] for row in rows}=={30,60}
    weapons={row['weapon'] for row in rows};assert weapons==MELEE214_WEAPONS
    assert {(row['weapon'],row['hz'],row.get('fusion',False)) for row in rows}=={
        (weapon,hz,fusion) for weapon in weapons for hz in (30,60) for fusion in (False,True)}
    for row in rows:
        number(row['weapon'])
        probes=row['probes'];assert isinstance(probes,list) and len(probes)==3
        for probe in probes:
            assert number(probe['count'])>0
            number(probe['reach']);number(probe['speed'])
        assert probes[0]['count']==probes[1]['count']==probes[2]['count']
        # Hookpole and Powder Spear author range through Shank travel, keeping
        # a fixed birth point. Every real attack must retain its offset and
        # gain travel speed; do not invent a universal extra birth offset.
        assert probes[1]['reach']>=probes[0]['reach']-.010001 and probes[2]['reach']>=probes[1]['reach']-.010001
        assert probes[1]['speed']>probes[0]['speed']+0.5 and probes[2]['speed']>probes[1]['speed']+0.5
    aggregate='PASS FRONTIER214 actual native Long Arms0/1/2 geometric range and speed for all10 NTUF and7 NTTE melee at30/60Hz '
    final=[json.loads(line[len(aggregate):]) for line in smoke.splitlines() if line.startswith(aggregate)]
    assert final==[rows],'Melee214 final aggregate differs from the real launch observations'
    control='PASS FRONTIER214 actual Scythe control Draw retained icon/button and excluded exact old arrow overlay '
    controls=[json.loads(line[len(control):]) for line in smoke.splitlines() if line.startswith(control)]
    assert len(controls)==2
    for item in controls:
        assert number(item['ink'])>0 and number(item['overlay_change'])>0
    return rows


def verify_scythe_natural214(value,smoke):
    assert value.get('status')=='PASS' and value.get('manual_damage_or_collision_calls') is False
    assert value.get('actual_skill_icon_selection') is True
    rows=value.get('rows');assert isinstance(rows,list) and len(rows)==8
    expected=[(hz,stack,heavy) for hz in (30,60) for stack in range(2) for heavy in (False,True)]
    assert [(row['hz'],row['stack'],row['heavy']) for row in rows]==expected
    prefix='FRONTIER214 Scythe actual engine hit range '
    observed=[json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    assert observed==rows,'Natural Scythe artifact differs from the scheduled engine observations'
    for row in rows:
        assert type(row['heavy']) is bool
        assert row['selection']==('SkillIcon.Select' if row['stack']==1 else 'unowned')
        assert 0<number(row['max_hit'])<196 and row['max_hit']%4==0
        assert number(row['frames'])>=2 and row['frames']==int(row['frames'])
        distances=row['hit_distances'];assert isinstance(distances,list) and distances
        assert len(distances)==len(set(distances)) and all(number(item) in range(8,201,4) for item in distances)
        assert max(distances)==row['max_hit']
        samples=row['samples'];assert isinstance(samples,list) and len(samples)==row['frames']
        age=-1;index=-1;hits=-1
        for sample in samples:
            for key in ('age','x','index','bbox_left','bbox_right','hits'):number(sample[key])
            assert age<sample['age']<=30 and sample['index']>=index
            assert sample['bbox_left']<=sample['bbox_right']
            assert hits<=sample['hits']<=len(distances) and sample['hits']>=0 and sample['hits']==int(sample['hits'])
            age=sample['age'];index=sample['index'];hits=sample['hits']
    for rate in range(2):
        for heavy in range(2):assert rows[rate*4+2+heavy]['max_hit']>=rows[rate*4+heavy]['max_hit']+8
    for slot in range(4):assert abs(rows[slot]['max_hit']-rows[slot+4]['max_hit'])<=4
    return rows


def verify_movement214(smoke):
    prefix='FRONTIER214 MOVEMENT RESULTS '
    values=[json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    assert len(values)==1;value=values[0]
    assert value['rates']==[30,60] and number(value['checks'])==51
    assert number(value['deadzone_gui_px'])==2 and number(value['fine_move_gui_px'])==3
    assert value['fixture']=='Windows raw touch through JoystickMove'
    ramp=value['ramp'];assert isinstance(ramp,list) and len(ramp)==2
    for row in ramp:
        assert isinstance(row,list) and len(row)==3
        for item in row:number(item)
        assert abs(row[0]-15)<0.000001 and abs(row[1]-(0.25+3/36))<0.000001 and 0<row[2]<=1
    assert all(abs(a-b)<0.000001 for a,b in zip(ramp[0],ramp[1]))
    return value

def verify_case_identity(case,smoke,artifacts,directory):
    registered=require_selection()
    assert case in REQUIRED214_CASES
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
    if case=='FrontierMenus214Tests':verify_menus214(read(Path(directory)/'ntuf214-menus.json'))
    if case=='FrontierPerformance214Tests':verify_performance214(read(Path(directory)/'ntuf214-performance.json'))
    if case=='FrontierMelee214Tests':
        verify_melee214(smoke)
        verify_scythe_natural214(read(Path(directory)/'ntuf214-scythe-natural.json'),smoke)
    if case=='FrontierMovement214Tests':verify_movement214(smoke)
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

def require_python_scope(modules):
    assert isinstance(modules,list) and modules and len(modules)==len(set(modules))
    assert REQUIRED214_PYTHON_MODULES<=set(modules),'Missing executed214 regression or negative controls'
    return modules


def verify_python_sources(value):
    assert value['version']==VERSION and value['internal']==INTERNAL and value['exit']==0 and value['tests']>0
    assert value['source_inputs_unchanged'] and value['reviewer_inputs_unchanged']
    require_python_scope(value['review_test_modules'])
    assert REVIEW_DEPENDENCIES<=set(value['reviewer_inputs']),'Missing executed reviewer dependency binding'
    for field in ('source_inputs','reviewer_inputs'):
        assert value[field]
        for name,pin in value[field].items():assert sha(ROOT/name)==pin,(field,name)
    capture=load('current213_source_capture',ROOT/'review/capture214_python.py')
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
    report_path=ROOT/'review'/('post214-development-review-'+run+'.json')
    report_path.write_text(json.dumps(report,indent=2),'utf8')
    config={'version':VERSION,'internal':INTERNAL,'status':'READY','run':'tests/'+run,
            'report':report_path.relative_to(ROOT).as_posix(),'report_sha256':sha(report_path),
            'python_evidence':'review/'+python_name,'python_evidence_sha256':sha(ROOT/'review'/python_name),
            'case_selection_sha256':sha(CASE_SELECTION),'review_verifier_sha256':sha(Path(__file__)),
            'vm_sha256':compiled['vm_sha256'],'input_sha256':compiled['input_sha256'],
            'silent_vm_sha256':sha(ROOT/'build-windows/frontier-silent.win'),
            'compile_receipt_sha256':sha(ROOT/'build-windows/last-success.json')}
    (ROOT/'review/release214-config.json').write_text(json.dumps(config,indent=2),'utf8')
    print(json.dumps({'status':'READY','cases':len(FINAL_CASES),'run':run}))

if __name__=='__main__':finalize(sys.argv[1],sys.argv[2])
