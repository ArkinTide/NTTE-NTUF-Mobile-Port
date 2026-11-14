"""Read-only current2.1.2 review; explicit per-case identity and exact VM pins.

The case-contract registry is authored before the run. Unknown native cases,
generic PASS-only logs, historical VM receipts and unpinned artifacts fail.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
CASE_SELECTION=ROOT/'review/release212-cases.json'
CONTRACTS=ROOT/'review/release212-case-contracts.json'
RED_SUPPLEMENT=ROOT/'review/release212-red-supplement.json'
VERSION='2.1.2'
INTERNAL=107
PRIOR_VM='9266303a3cc9f8e121a2601072304a4d5b06ca20b6b59026925b971619c8a308'
PRIOR_INPUT='62ed4a216ed10c19249bdfebeb42cdc16effa568e60ccfbcf220e5a0e4084d57'
RED212_FAILED_SEEDS=(15,22,33,48,74,81,82,94,96)
RED212_NEGATIVE={
    'run':'tests/20261113T172205902876Z','case':'FrontierRed212ProbeTests',
    'receipt_sha256':'3b104aabb5d23a4370c1443cd2359e089bbe63b9e83ae195d192ff7dedad55b8',
    'artifact_sha256':'3193abe067d9507966f96576deaeb079feba4697d11f185eb7b8b424a4719010',
    'vm_sha256':'9ab12f841785238dbe60dd4048bc70d23ad1e5098e097c23d59208951cbff4fb',
    'input_sha256':'522d0109149074dfe31084d290447b80ad38b84a39221f6a6c30728ccd579c0e',
}
RED212_PUBLIC_EVIDENCE=frozenset(('review/RED212_CAUSE.md','review/red212-native-seed15-evidence.json',
                                  'review/red212-native-sweep-after-summary.json'))


def read(path):return json.loads(Path(path).read_text('utf-8-sig'))


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    exec(compile(Path(path).read_bytes(),str(path),'exec'),module.__dict__)
    return module


def contracts():
    value=read(CONTRACTS)
    assert value['version']==VERSION and value['internal']==INTERNAL and value['status']=='READY'
    records=value['cases']
    assert isinstance(records,dict) and records
    for case,contract in records.items():
        assert re.fullmatch(r'[A-Za-z]\w+Tests',case)
        markers=contract.get('markers',[])
        assert isinstance(markers,list) and markers and len(markers)==len(set(markers))
        assert all(isinstance(marker,str) and marker and 'PASS full internal' not in marker for marker in markers)
        assert type(contract.get('required')) is bool
        assert all(type(requirement) is int and 1<=requirement<=6 for requirement in contract.get('requirements',[]))
        for name in contract.get('artifacts',[]):assert Path(name).name==name
    return records


def selected_cases():
    if not CASE_SELECTION.is_file():return ()
    value=read(CASE_SELECTION)
    assert value['version']==VERSION and value['internal']==INTERNAL
    cases=value['cases']
    assert isinstance(cases,list) and all(isinstance(c,str) and re.fullmatch(r'[A-Za-z]\w+Tests',c) for c in cases)
    assert len(cases)==len(set(cases))
    return tuple(cases)


FINAL_CASES=selected_cases()
REQUIRED212_CASES=frozenset(case for case,contract in contracts().items() if contract['required']) if CONTRACTS.is_file() and read(CONTRACTS).get('status')=='READY' else frozenset()


def require_selection():
    assert FINAL_CASES and FINAL_CASES==selected_cases(),'Freeze current case selection before review'
    registered=contracts()
    assert set(FINAL_CASES)<=set(registered),'Every selected case needs its own reviewed identity contract'
    assert REQUIRED212_CASES and REQUIRED212_CASES<=set(FINAL_CASES)
    covered={r for case in FINAL_CASES for r in registered[case]['requirements']}
    assert covered=={1,2,3,4,5,6},'Current case selection must cover all six requested repairs'
    return registered


def _artifact_conditions(data,conditions):
    for condition in conditions:
        value=data
        for part in condition['path']:
            value=value[part]
        operator=condition['op']
        target=condition['value']
        if operator=='eq':assert value==target,(condition,value)
        elif operator=='ge':assert value>=target,(condition,value)
        elif operator=='le':assert value<=target,(condition,value)
        elif operator=='len':assert len(value)==target,(condition,value)
        elif operator=='minlen':assert len(value)>=target,(condition,value)
        else:raise AssertionError('Unreviewed artifact condition operator: '+operator)


def _near(value,target,tolerance):assert abs(value-target)<=tolerance,(value,target,tolerance)


def verify_menu212(directory):
    data=read(directory/'ntuf212-menus.json')
    assert data['passed'] and data['physical_device_tested'] is False and data['checks']>=30
    robots=[r for r in data['cases'] if r['kind']=='robot']
    assert len(robots)==8
    expected={(424,240,848,480),(640,360,640,360),(320,180,640,360),(280,160,840,480)}
    assert {tuple(r['view']) for r in robots}==expected
    for view in expected:
        rows=[r for r in robots if tuple(r['view'])==view]
        assert len(rows)==2 and {bool(r['yes']) for r in rows}=={False,True}
        for row in rows:
            rect=row['gui_rect']
            assert row['pixel_changes']>6 and 0<=rect[0]<rect[2]<view[2] and 0<=rect[1]<rect[3]<view[3]
    augments=[r for r in data['cases'] if r['kind']=='augment']
    assert augments and {r['language'] for r in augments}=={'Simplified Chinese','English'}
    assert {r['skill'] for r in augments if r['language']=='Simplified Chinese'}=={r['skill'] for r in augments if r['language']=='English'}
    for row in augments:
        layout=row['layout']
        assert layout['body_y']>=layout['title_y']+layout['title_h']+4
        assert layout['replace_y']>=layout['body_y']+layout['body_h']+7
        assert layout['width']>0 and layout['height']>0
    return data


def verify_clock212(directory,live):
    data=read(directory/('ntuf212-clock-live.json' if live else 'ntuf212-clock-unit.json'))
    assert data['passed'] and data['physical_device_tested'] is False
    if live:
        rows=data['segments'];assert len(rows)==3 and [r['rate'] for r in rows]==[60,30,60]
        for row in rows:
            assert row['host_frames']==row['rate']
            _near(row['distance'],60,2)
            for field in ('source_callbacks','logical_time','alarm_elapsed'):_near(row[field],30,1)
    else:
        assert data['checks']>=60
        rows=data['transitions'];assert len(rows)==4 and [r['rate'] for r in rows]==[60,30,60,30]
        for row in rows:
            scale=30/row['rate'];_near(row['scale'],scale,.0001)
            _near(row['hspeed'],3*scale,.0001);_near(row['friction'],.2*scale*scale,.0001)
            _near(row['rocket_cap'],12*scale,.0001)
        assert len({r['source_max'] for r in rows})==1 and len({r['source_anim'] for r in rows})==1
        bounces=data.get('wallbounce')
        assert isinstance(bounces,list) and len(bounces)==4
        assert [row['rate'] for row in bounces]==[60,30,60,30]
        for index,row in enumerate(bounces):
            scale=30/row['rate'];_near(row['scale'],scale,.0001)
            # Bullet2 stores physical displacement. Authored NTUF and NTTE
            # callbacks store source-tick units and apply timescale themselves.
            for family,initial in (('native',5),('ntuf',4),('red',7),('venom',4),('shell',4)):
                current=initial*.95**index
                decayed=current*.95
                _near(row[family+'_field'],decayed*(scale if family=='native' else 1),.0001)
                _near(row[family+'_speed'],min(4.8+current,16),.0001)
            _near(row['native_logical'],5*.95**(index+1),.0001)
    return data


def verify_bluescreen204(case,directory):
    data=read(directory/'frontier-bluescreen-ui204.json')
    assert data['passed'] and data['physical_device_tested'] is False
    assert data['rate']==(60 if '60' in case else 30) and bool(data['accept'])==('Yes' in case)
    assert len(data['input_frames'])>=2 and data['actual_click']['click']==0
    return data


def _red212_id(value):
    assert type(value) in (int,float) and math.isfinite(value) and value>0 and value==int(value)
    return value


def _red212_position(value):
    assert isinstance(value,list) and len(value)==2
    assert all(type(item) in (int,float) and math.isfinite(item) for item in value)
    return value


def _verify_red212_walk(walk):
    assert walk['kind'] in ('warp','twins') and walk['genuine_generated_target'] is True
    _red212_id(walk['target_id']);_red212_position(walk['target_position'])
    assert walk['steps']>0 and walk['reached'] is True and walk['returned'] is True and walk['blocked']==[]
    for flag in ('actual_wall_collision_events','actual_helper_endstep','manual_pixel_integration'):
        assert walk[flag] is True
    for field in ('closed_overlapping_after_endstep','orphan_helpers_after_endstep',
                  'open_helpers_after_return','reveal_after_return'):
        assert walk[field]==0
    contacts=walk['fake_contact_ids'];assert isinstance(contacts,list) and len(set(contacts))==len(contacts)
    for identity in contacts:_red212_id(identity)
    assert walk['fake_collision_events']>=len(contacts)


def verify_red212(directory):
    data=read(directory/'frontier-red212-scheduled.json')
    assert data['status']=='PASS' and data['diagnostic'] is False and data['physical_device_tested'] is False
    assert data['native_scheduled_frames']==12 and data['actual_player_mask']=='mskPlayer 8x10'
    rows=data['rows'];assert isinstance(rows,list) and len(rows)==8
    expected={(mode,seed,loops,rate) for mode in ('normal','in-room')
              for seed,loops,rate in ((15,3,30),(15,3,60),(22,0,30),(48,3,60))}
    assert {(row['mode'],row['seed'],row['loops'],row['rate']) for row in rows}==expected
    assert any(row['native_clearance_rocks']>0 for row in rows)
    assert sum(row['protected_rocks'] for row in rows)>0
    for row in rows:
        assert row['native_scheduler'] is True and row['manual_alarm_dispatch'] is False
        assert row['engine_rate']==row['rate']
        assert 0<row['native_gen_frames']<600 and row['post_population_shifts']==0
        trace=row['generation_trace'];assert isinstance(trace,list)
        if row['mode']=='normal' and row['seed']==15:assert trace
        for shift in trace:
            assert all(shift['before'][field]==0 for field in ('walls','fake','helpers'))
        road=row['road']
        assert road['expected_points']>0 and road['expected_edges']>0 and road['pixel_swept'] is True
        assert road['changed']==[] and road['blocked_expected_edges']==[]
        assert row['rock_clearance_rule']=='exclude actual PortalClear mask overlap'
        clearance=row['native_clearance_rocks']
        assert type(clearance) in (int,float) and clearance>=0 and clearance==int(clearance)
        rocks=row['protected_rocks']
        assert type(rocks) in (int,float) and rocks>=0 and rocks==int(rocks)
        assert row['protected_rocks']==row['preserved_rocks']
        capture=row['rock_capture'];assert isinstance(capture,list)
        assert len({rock['id'] for rock in capture})==len(capture)
        for rock in capture:
            assert rock['exists'] is True and type(rock['portal_clear']) is bool
            assert isinstance(rock['overlap'],list)
        assert clearance==sum(rock['portal_clear'] for rock in capture)
        assert rocks==sum(not rock['portal_clear'] for rock in capture)
        walks=row['walks'];assert isinstance(walks,list) and len(walks)>=2
        assert {'warp','twins'}<={walk['kind'] for walk in walks}
        assert len({walk['target_id'] for walk in walks})==len(walks)
        twins=row['before']['twins'];assert isinstance(twins,list) and twins
        identities=[_red212_id(twin['id']) for twin in twins]
        assert len(set(identities))==len(identities)
        actual_twins={twin['id']:twin for twin in twins};anchors={}
        assert {walk['target_id'] for walk in walks if walk['kind']=='twins'}==set(actual_twins)
        for twin in twins:
            _red212_position(twin['position']);partner=twin['partner_id']
            if partner==0:
                assert type(partner) in (int,float)
                anchors[twin['id']]=twin['id']
            else:
                _red212_id(partner)
                assert partner!=twin['id'] and partner in actual_twins
                assert actual_twins[partner]['partner_id']==twin['id']
                anchors[twin['id']]=min(twin['id'],partner)
        for walk in walks:
            _verify_red212_walk(walk)
            if walk['kind']!='twins':continue
            assert walk['fake_collision_events']>0 and walk['peak_reveal']>0
            direct=walk['direct_route'];_verify_red212_walk(direct)
            for field in ('kind','target_id','target_position','genuine_generated_target'):
                assert direct[field]==walk[field]
            via=walk['via_fake'];identity=_red212_id(via['id'])
            _red212_position(via['position']);_red212_position(via['waypoint'])
            assert via['waypoint_player_mask_intersects'] is True and via['generated_this_room'] is True
            assert identity in walk['fake_contact_ids']
            window=via['generation_window']
            target=walk['target_id'];anchor=anchors[target]
            assert walk['target_position']==actual_twins[target]['position']
            assert window['twins_id']==target and window['room_twins_id']==anchor
            assert window['partner_id']==actual_twins[target]['partner_id']
            previous=max((other for other in set(anchors.values()) if other<anchor),default=0)
            assert window['previous_twins_id']==previous and previous<identity<anchor
            geometry=row['before']['geometry'];walls=geometry['walls'];helpers=geometry['helpers']
            actual=[wall for wall in walls if wall['id']==identity]
            assert len(actual)==1 and actual[0]['object']=='NTTEFullWallFake'
            assert via['position']==[actual[0]['x'],actual[0]['y']] and via['bbox']==actual[0]['bbox']
            helper_id=_red212_id(via['helper_id'])
            assert previous<helper_id<anchor and via['helper_creator']==identity
            actual_helpers=[helper for helper in helpers if helper['id']==helper_id]
            assert len(actual_helpers)==1 and actual_helpers[0]['creator']==identity
    return data


def red212_sweep_rows(data):
    assert data['diagnostic'] is True and data['native_scheduler'] is True
    assert data['manual_alarm_dispatch'] is False and data['physical_device_tested'] is False
    assert data['actual_player_mask']=='mskPlayer 8x10'
    rows=data['rows'];assert isinstance(rows,list) and len(rows)==96
    assert {(row['seed'],row['loops']) for row in rows}=={
        (seed,(0,1,3)[(seed-1)%3]) for seed in range(1,97)}
    normalized=[]
    for row in rows:
        assert 0<row['native_gen_frames']<=600
        assert row['before_secret_protected']>0 and row['expected_edges']>0
        assert row['actual_player_mask_pixel_sweep'] is True
        trace=row['generation_trace'];assert isinstance(trace,list)
        shifts=sum(any(shift['before'][field]>0 for field in ('walls','fake','helpers')) for shift in trace)
        assert row['post_wall_shifts']==shifts
        normalized.append({'seed':int(row['seed']),'loops':int(row['loops']),
            'native_gen_frames':int(row['native_gen_frames']),
            'expected_points':int(row['before_secret_protected']),'expected_edges':int(row['expected_edges']),
            'changed_points':len(row['changed']),'blocked_edges':len(row['blocked_expected_edges']),
            'post_population_shifts':shifts})
    return sorted(normalized,key=lambda row:row['seed'])


def red212_supplement_summary(descriptor,negative_rows,positive_rows):
    return {'version':VERSION,'internal':INTERNAL,'status':'SUPPLEMENTAL_DIAGNOSTIC_VERIFIED',
        'negative':descriptor['negative'],'positive':descriptor['positive'],
        'worlds_per_control':96,'negative_failed_seeds':list(RED212_FAILED_SEEDS),
        'positive_rows':positive_rows,'negative_failed_rows':[
            row for row in negative_rows if row['changed_points'] or row['blocked_edges']],
        'counted_in_formal_21_cases':False,'physical_device_tested':False}


def verify_red212_supplement(compiled):
    descriptor=read(RED_SUPPLEMENT)
    assert descriptor['version']==VERSION and descriptor['internal']==INTERNAL and descriptor['status']=='READY'
    assert descriptor['negative']==RED212_NEGATIVE
    assert set(descriptor['public_evidence'])==RED212_PUBLIC_EVIDENCE
    for name,pin in descriptor['public_evidence'].items():
        path=(ROOT/name).resolve(strict=True)
        assert path.is_relative_to((ROOT/'review').resolve()) and set(pin)=={'sha256'}
        assert sha(path)==pin['sha256']
    normalized={}
    for kind in ('negative','positive'):
        control=descriptor[kind]
        assert control['case']=='FrontierRed212ProbeTests'
        assert re.fullmatch(r'tests/\d{8}T\d+Z',control['run'])
        run=(ROOT/control['run']).resolve(strict=True)
        assert run.is_relative_to((ROOT/'tests').resolve())
        directory=run/control['case'];receipt_path=directory/'receipt.json'
        artifact=directory/'frontier-red212-native-sweep.json'
        assert sha(receipt_path)==control['receipt_sha256'] and sha(artifact)==control['artifact_sha256']
        receipt=read(receipt_path);build=read(run/'compiled-build.json')
        assert receipt['case']==control['case'] and receipt['physical_device_tested'] is False
        assert receipt['muted_resources']>100 and receipt['desktop']=='private, never activated'
        assert sha(run/'compile.log')==build['log_sha256']
        assert receipt['artifacts_sha256']['frontier-red212-native-sweep.json']==control['artifact_sha256']
        for key in ('vm_sha256','input_sha256'):assert receipt[key]==control[key]==build[key]
        data=read(artifact);rows=red212_sweep_rows(data);normalized[kind]=rows
        failed=[row['seed'] for row in rows if row['changed_points'] or row['blocked_edges']]
        assert data['expected_road_failures']==len(failed)
        if kind=='negative':
            assert receipt['status']=='FAIL' and receipt['exit']!=0 and receipt['termination_reason']=='runtime_error'
            assert tuple(failed)==RED212_FAILED_SEEDS
            assert all(row['post_population_shifts']>0 for row in rows if row['seed'] in failed)
            assert all(control[key]!=compiled[key] for key in ('vm_sha256','input_sha256'))
        else:
            assert receipt['status']=='PASS' and receipt['exit']==0 and receipt['termination_reason'] is None
            assert all(control[key]==compiled[key] for key in ('vm_sha256','input_sha256'))
            assert not failed and all(row['post_population_shifts']==0 for row in rows)
            log=(directory/'runner.log').read_text('utf8',errors='replace')
            assert '###game_end###0' in log and 'ERROR!!!' not in log
            assert not re.search(r'^(?:ERROR|FAIL)(?:\s|:|$)',log,re.M)
    expected=red212_supplement_summary(descriptor,normalized['negative'],normalized['positive'])
    assert read(ROOT/'review/red212-native-sweep-after-summary.json')==expected
    seed15=read(ROOT/'review/red212-native-seed15-evidence.json')['negative_control']
    assert seed15['run']==RED212_NEGATIVE['run'] and seed15['case']==RED212_NEGATIVE['case']
    assert seed15['receipt_sha256']==RED212_NEGATIVE['receipt_sha256']
    assert seed15['raw_sweep_sha256']==RED212_NEGATIVE['artifact_sha256']
    assert all(seed15['compiled_build'][key]==RED212_NEGATIVE[key] for key in ('vm_sha256','input_sha256'))
    return {'descriptor':RED_SUPPLEMENT.relative_to(ROOT).as_posix(),'descriptor_sha256':sha(RED_SUPPLEMENT),
            'negative':descriptor['negative'],'positive':descriptor['positive'],
            'public_evidence':descriptor['public_evidence'],'worlds_per_control':96,
            'negative_failed_seeds':list(RED212_FAILED_SEEDS),'counted_in_formal_21_cases':False,
            'physical_device_tested':False}


def verify_red204(directory):
    data=read(directory/'frontier-red-regression204.json')
    assert data['status']=='PASS' and data['physical_device_tested'] is False and data['rates']==[30,60]
    for flag in ('actual_gencont','actual_player_mask','actual_player_collision_event','actual_helper_endstep',
                 'manual_collision_dispatch','manual_pixel_integration'):
        assert data[flag] is True
    assert len(data['worlds'])==6 and {(row['seed'],row['rate']) for row in data['worlds']}=={
        (seed,rate) for seed in (1,2,3) for rate in (30,60)}
    assert len(data['walks'])>=4 and {row['rate'] for row in data['walks']}=={30,60}
    for row in data['walks']:
        walk=row['walk']
        assert row['components']==1 and row['nodes']>0
        assert walk['steps']>0 and walk['reached'] and walk['returned'] and not walk['blocked']
        for field in ('closed_overlapping_after_endstep','orphan_helpers_after_endstep',
                      'open_helpers_after_return','reveal_after_return'):
            assert walk[field]==0
    assert any(row['target']['kind']=='twins' and row['walk']['fake_collision_events']>0
               and row['walk']['peak_reveal']>0 for row in data['walks'])
    return data


def verify_wall205(directory):
    data=read(directory/'frontier-wall-surface205.json')
    assert data['status']=='PASS' and data['physical_device_tested'] is False
    rows=data['rows']
    assert len(rows)==29 and len({row['area'] for row in rows})==29
    for row in rows:
        assert row['actual_native_draw'] and row['physical_collision_retained'] and row['reference_pixels_equal']
    return data


def verify_weather_performance(directory):
    data=read(directory/'frontier-weather-performance.json')
    assert data['physical_device_tested'] is False and data['parity_comparisons']>=100
    assert data['actual_source_callback_calls']==120 and data['actual_source_callback_us']>=0
    rows=data['rows'];assert len(rows)==3 and [row['round'] for row in rows]==[0,1,2]
    for row in rows:
        assert row['terrain']==1601 and row['queries']==60
        # The fixture invokes CoastNight twice before timing (including the
        # newly created tile). Each source callback marks every matching
        # undefined target, so these queries measure the processed steady
        # state, not an unprocessed population. Native assertions separately
        # require real sprite changes and old/new membership parity.
        total=row['same_result_total']
        assert type(total) in (int,float) and math.isfinite(total) and total==0
        assert row['original_snapshot_us']>=0 and row['fresh_native_us']>=0 and row['ratio']>=0
    return data


def verify_case_identity(case,smoke,artifacts,directory):
    registered=require_selection()
    assert case in FINAL_CASES and case in registered
    contract=registered[case]
    assert smoke.count('PASS full internal selected implemented branches')==1
    assert 'ERROR!!!' not in smoke and not re.search(r'^(?:ERROR|FAIL)(?:\s|:|$)',smoke,re.M)
    for marker in contract['markers']:
        count=smoke.count(marker)
        expected=contract.get('marker_counts',{}).get(marker,1)
        assert count==expected,(case,marker,count,expected)
    assert set(contract.get('artifacts',[]))<=set(artifacts),(case,'Missing current required screenshot/data')
    for name,conditions in contract.get('json_conditions',{}).items():
        assert name in artifacts and name.endswith('.json')
        _artifact_conditions(read(directory/name),conditions)
    for name in contract.get('png_artifacts',[]):
        assert name in artifacts
        from PIL import Image
        with Image.open(directory/name) as image:
            image.verify()
        with Image.open(directory/name) as image:
            exact=contract.get('png_exact_dimensions',{}).get(name)
            if exact is not None:
                assert isinstance(exact,list) and len(exact)==2 and all(type(value) is int and value>0 for value in exact)
                assert image.size==tuple(exact),(case,'Authored surface dimensions',image.size,exact)
            else:
                assert image.width>=240 and image.height>=135,(case,'Screenshot dimensions',image.size)
    validator=contract.get('validator')
    if validator is not None:
        if validator=='bubbles212':
            helper=load('ntuf212_bubbles_review',ROOT/'review/verify_bubbles212.py')
            helper.verify_bubbles212(smoke)
        elif validator=='menus212':verify_menu212(directory)
        elif validator=='clock212':verify_clock212(directory,False)
        elif validator=='clock212-live':verify_clock212(directory,True)
        elif validator=='bluescreen204':verify_bluescreen204(case,directory)
        elif validator=='red212':verify_red212(directory)
        elif validator=='red204':verify_red204(directory)
        elif validator=='wall205':verify_wall205(directory)
        elif validator=='weather-perf':verify_weather_performance(directory)
        else:raise AssertionError('Unknown current native case validator: '+validator)
    return {'native_assertions_completed':True,'explicit_identity_contract':True,'physical_device_tested':False}


def check_run(name,cases,compiled):
    require_selection()
    assert re.fullmatch(r'\d{8}T\d+Z',name) and tuple(cases)==FINAL_CASES
    assert compiled['vm_sha256']!=PRIOR_VM and compiled['input_sha256']!=PRIOR_INPUT
    run=ROOT/'tests'/name
    assert read(run/'compiled-build.json')==compiled
    assert sha(run/'compile.log')==compiled['log_sha256']
    results=[]
    for case in cases:
        directory=run/case
        receipt=read(directory/'receipt.json')
        assert receipt['case']==case and receipt['status']=='PASS' and receipt['exit']==0
        assert receipt['termination_reason'] is None
        assert receipt['vm_sha256']==compiled['vm_sha256'] and receipt['input_sha256']==compiled['input_sha256']
        assert receipt['physical_device_tested'] is False and receipt['muted_resources']>100
        assert receipt['desktop']=='private, never activated'
        if 'previous_failed_attempt' in receipt:
            prior=receipt['previous_failed_attempt']
            path=(ROOT/prior['path']).resolve(strict=True)
            assert path.is_relative_to((ROOT/'tests/failed-attempts').resolve())
            assert sha(path/'receipt.json')==prior['receipt_sha256']
            failed=read(path/'receipt.json')
            assert failed['status']=='FAIL' and failed['case']==case
            assert failed['vm_sha256']==receipt['vm_sha256'] and failed['input_sha256']==receipt['input_sha256']
        smoke=(directory/'smoke.txt').read_text('utf8')
        log=(directory/'runner.log').read_text('utf8',errors='replace')
        assert '###game_end###0' in log and 'ERROR!!!' not in log
        assert not re.search(r'^(?:ERROR|FAIL)(?:\s|:|$)',log,re.M)
        artifacts=receipt['artifacts_sha256']
        actual={p.name for p in directory.iterdir() if p.is_file() and p.name.startswith(('frontier-','ntuf-','ntuf212-','ntte-')) and p.suffix.lower() in {'.png','.json'}}
        assert set(artifacts)==actual
        for artifact,pin in artifacts.items():
            assert Path(artifact).name==artifact and sha(directory/artifact)==pin
        verify_case_identity(case,smoke,artifacts,directory)
        results.append({**receipt,'receipt_sha256':sha(directory/'receipt.json'),
                        'smoke_sha256':sha(directory/'smoke.txt'),'runner_log_sha256':sha(directory/'runner.log')})
    assert len({row['silent_vm_sha256'] for row in results})==1
    assert sha(ROOT/'build-windows/frontier-silent.win')==results[0]['silent_vm_sha256']
    return {'count':len(results),'results':results}


def capture_module():return load('ntuf212_python_capture',ROOT/'review/capture212_python.py')


def verify_python_sources(evidence):
    capture=capture_module()
    assert evidence['version']==VERSION and evidence['internal']==INTERNAL
    assert evidence['exit']==0 and type(evidence['tests']) is int and evidence['tests']>0
    assert evidence['source_inputs_unchanged'] and evidence['reviewer_inputs_unchanged']
    assert evidence['source_inputs']==capture.inputs() and evidence['reviewer_inputs']==capture.reviewer_inputs()
    path=(ROOT/evidence['log']).resolve()
    assert path.is_relative_to((ROOT/'review').resolve()) and sha(path)==evidence['log_sha256']
    output=path.read_text('utf8')
    assert re.search(r'^Ran '+str(evidence['tests'])+r' tests in ',output,re.M)
    assert re.search(r'\nOK\s*$',output) and not re.search(r'^(?:FAILED|ERROR:|FAIL:)',output,re.M)


def current_build():
    manifest=load('ntuf212_current_inputs',ROOT/'tools/build_input_manifest.py')
    current=manifest.snapshot();compiled=read(ROOT/'build-windows/last-success.json')
    assert compiled['status']=='COMPILED_NOT_PLAYABLE_VERIFIED'
    assert current['input_sha256']==compiled['input_sha256']
    assert sha(ROOT/'build-windows/nuclearthronemobile.win')==compiled['vm_sha256']
    assert sha(ROOT/'build-windows/compile.log')==compiled['log_sha256']
    captured_path=(ROOT/compiled['input_manifest']).resolve()
    assert captured_path.is_relative_to(ROOT.resolve())
    captured=read(captured_path)
    assert captured['input_sha256']==current['input_sha256']
    assert captured['staged_files']==current['staged_files'], 'Compiled source/resource manifest changed'
    return current,compiled


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run');parser.add_argument('python_evidence')
    args=parser.parse_args()
    current,compiled=current_build()
    assert '#macro GAME_VERSION "2.1.2"' in (ROOT/'staging/project/objects/UberCont/Create_0.gml').read_text('utf-8-sig')
    observed=check_run(Path(args.run).name,FINAL_CASES,compiled)
    red_supplement=verify_red212_supplement(compiled)
    python_path=(ROOT/args.python_evidence).resolve()
    assert python_path.is_relative_to((ROOT/'review').resolve())
    python=read(python_path);verify_python_sources(python)
    report={'status':'SELECTED_DEVELOPMENT_CHECKS_VERIFIED','version':VERSION,'internal':INTERNAL,
            'current_compiled_build':compiled,'current_native_run':observed,'red212_supplement':red_supplement,
            'python':{**python,'evidence_scope':'exact current maintained Python/native/reviewer inputs and passing aggregate log'},
            'case_selection':CASE_SELECTION.relative_to(ROOT).as_posix(),'case_selection_sha256':sha(CASE_SELECTION),
            'case_contracts_sha256':sha(CONTRACTS),'prior_vm_runs':[],'staged_files':len(current['staged_files']),
            'physical_device_tested':False,'packaging_commit_publication_upload_performed':False,
            'utc':datetime.now(timezone.utc).isoformat()}
    path=ROOT/'review'/('post212-development-review-'+Path(args.run).name+'.json')
    with path.open('x',encoding='utf8') as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
    print(path)


if __name__=='__main__':main()
