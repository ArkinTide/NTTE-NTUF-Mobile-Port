"""Current review refuses generic PASS, absent artifacts and stale identities."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import importlib.util
import json
import unittest

HERE=Path(__file__).resolve().parent


def subject():
    path=HERE/'verify_212_repairs.py'
    spec=importlib.util.spec_from_file_location('review212_test_subject',path)
    module=importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


class Review212Tests(unittest.TestCase):
    def test_small_authored_surface_contract_requires_exact_dimensions(self):
        from PIL import Image
        module=subject()
        with TemporaryDirectory() as temporary:
            directory=Path(temporary)
            contract={'required':True,'requirements':[1,2,3,4,5,6],
                      'markers':['PASS specific native212 assertions'],'artifacts':['fixture.png'],
                      'png_artifacts':['fixture.png'],'png_exact_dimensions':{'fixture.png':[128,96]}}
            smoke=self.fixture(module,directory,contract)
            path=directory/'fixture.png';Image.new('RGBA',(128,96)).save(path)
            module.verify_case_identity('Fixture212Tests',smoke,{path.name:'fixture'},directory)
            for size in ((127,96),(129,96),(128,95),(128,97)):
                Image.new('RGBA',size).save(path)
                with self.assertRaises(AssertionError):
                    module.verify_case_identity('Fixture212Tests',smoke,{path.name:'fixture'},directory)

    def test_current_build_rejects_edited_source_and_changed_vm(self):
        module=subject()
        with TemporaryDirectory() as temporary:
            root=Path(temporary);module.ROOT=root;build=root/'build-windows';build.mkdir()
            vm=build/'nuclearthronemobile.win';vm.write_bytes(b'current VM')
            log=build/'compile.log';log.write_bytes(b'current compiler log')
            snapshot={'input_sha256':'a'*64,'staged_files':{'current.gml':'b'*64}}
            captured=root/'capture.json';captured.write_text(json.dumps(snapshot),'utf8')
            compiled={'status':'COMPILED_NOT_PLAYABLE_VERIFIED','input_sha256':snapshot['input_sha256'],
                      'vm_sha256':module.sha(vm),'log_sha256':module.sha(log),'input_manifest':'capture.json'}
            (build/'last-success.json').write_text(json.dumps(compiled),'utf8')
            module.load=lambda *args:SimpleNamespace(snapshot=lambda:snapshot)
            self.assertEqual(module.current_build(),(snapshot,compiled))
            snapshot['staged_files']['current.gml']='c'*64
            with self.assertRaises(AssertionError):module.current_build()
            snapshot['staged_files']['current.gml']='b'*64;vm.write_bytes(b'edited VM')
            with self.assertRaises(AssertionError):module.current_build()

    def fixture(self,module,directory,contract=None):
        module.CASE_SELECTION=directory/'cases.json'
        module.CONTRACTS=directory/'contracts.json'
        module.FINAL_CASES=('Fixture212Tests',)
        module.REQUIRED212_CASES=frozenset(module.FINAL_CASES)
        module.CASE_SELECTION.write_text(json.dumps({'version':'2.1.2','internal':107,'cases':list(module.FINAL_CASES)}),'utf8')
        entry=contract or {'required':True,'requirements':[1,2,3,4,5,6],'markers':['PASS specific native212 assertions'],'artifacts':[]}
        module.CONTRACTS.write_text(json.dumps({'version':'2.1.2','internal':107,'status':'READY','cases':{'Fixture212Tests':entry}}),'utf8')
        return 'PASS specific native212 assertions\nPASS full internal selected implemented branches; not complete MOD coverage\n'

    def test_registered_specific_marker_is_required(self):
        module=subject()
        with TemporaryDirectory() as temporary:
            directory=Path(temporary);smoke=self.fixture(module,directory)
            self.assertTrue(module.verify_case_identity('Fixture212Tests',smoke,{},directory)['explicit_identity_contract'])
            with self.assertRaises(AssertionError):
                module.verify_case_identity('Fixture212Tests','PASS full internal selected implemented branches\n',{},directory)
            with self.assertRaises(AssertionError):
                module.verify_case_identity('UnknownTests',smoke,{},directory)

    def test_error_or_duplicate_marker_rejected(self):
        module=subject()
        with TemporaryDirectory() as temporary:
            directory=Path(temporary);smoke=self.fixture(module,directory)
            for suffix in ('ERROR!!! stale wall\n','ERROR stale wall\n','FAIL: native assertions\n','PASS specific native212 assertions\n'):
                with self.subTest(suffix=suffix),self.assertRaises(AssertionError):
                    module.verify_case_identity('Fixture212Tests',smoke+suffix,{},directory)

    def test_missing_or_failed_artifact_rejected(self):
        module=subject()
        with TemporaryDirectory() as temporary:
            directory=Path(temporary)
            contract={'required':True,'requirements':[1,2,3,4,5,6],
                      'markers':['PASS specific native212 assertions'],'artifacts':['ntuf212-fixture.json'],
                      'json_conditions':{'ntuf212-fixture.json':[{'path':['passed'],'op':'eq','value':True},
                                                               {'path':['rows'],'op':'minlen','value':2}]}}
            smoke=self.fixture(module,directory,contract)
            with self.assertRaises(AssertionError):module.verify_case_identity('Fixture212Tests',smoke,{},directory)
            artifact=directory/'ntuf212-fixture.json';artifact.write_text(json.dumps({'passed':False,'rows':[1,2]}),'utf8')
            with self.assertRaises(AssertionError):module.verify_case_identity('Fixture212Tests',smoke,{artifact.name:'fixture'},directory)
            artifact.write_text(json.dumps({'passed':True,'rows':[1,2]}),'utf8')
            module.verify_case_identity('Fixture212Tests',smoke,{artifact.name:'fixture'},directory)

    def test_selection_must_cover_all_six_current_requirements(self):
        module=subject()
        with TemporaryDirectory() as temporary:
            directory=Path(temporary);self.fixture(module,directory)
            registry=json.loads(module.CONTRACTS.read_text('utf8'))
            registry['cases']['Fixture212Tests']['requirements']=[1,2,3,4,5]
            module.CONTRACTS.write_text(json.dumps(registry),'utf8')
            with self.assertRaises(AssertionError):module.require_selection()

    def test_weather_benchmark_requires_processed_zero_result_steady_state(self):
        module=subject()
        with TemporaryDirectory() as temporary:
            directory=Path(temporary)
            data={'physical_device_tested':False,'parity_comparisons':162,
                  'actual_source_callback_calls':120,'actual_source_callback_us':100,
                  'rows':[{'round':index,'terrain':1601,'queries':60,
                           'same_result_total':0,'original_snapshot_us':100,
                           'fresh_native_us':20,'ratio':.2} for index in range(3)]}
            path=directory/'frontier-weather-performance.json'
            for total in (0,0.0):
                data['rows'][0]['same_result_total']=total
                path.write_text(json.dumps(data),'utf8')
                module.verify_weather_performance(directory)
            for total in (1,-1,.5,True,False,float('inf'),float('nan'),'0',None):
                with self.subTest(total=total):
                    data['rows'][0]['same_result_total']=total
                    path.write_text(json.dumps(data),'utf8')
                    with self.assertRaises(AssertionError):module.verify_weather_performance(directory)

    def test_live_clock_checks_each_rate_motion_alarm_and_source_tick(self):
        module=subject()
        with TemporaryDirectory() as temporary:
            directory=Path(temporary)
            data={'passed':True,'physical_device_tested':False,'segments':[
                {'rate':rate,'host_frames':rate,'distance':60,'source_callbacks':30,'logical_time':30,'alarm_elapsed':30}
                for rate in (60,30,60)]}
            path=directory/'ntuf212-clock-live.json';path.write_text(json.dumps(data),'utf8')
            module.verify_clock212(directory,True)
            data['segments'][1]['distance']=120;path.write_text(json.dumps(data),'utf8')
            with self.assertRaises(AssertionError):module.verify_clock212(directory,True)

    def red212_fixture(self):
        import copy
        walk={'steps':4,'reached':True,'returned':True,'blocked':[],
              'actual_wall_collision_events':True,'actual_helper_endstep':True,'manual_pixel_integration':True,
              'closed_overlapping_after_endstep':0,'orphan_helpers_after_endstep':0,
              'open_helpers_after_return':0,'reveal_after_return':0,'fake_collision_events':2,
              'fake_contact_ids':[9001],'peak_reveal':1}
        rows=[]
        for mode in ('normal','in-room'):
            for seed,loops,rate in ((15,3,30),(15,3,60),(22,0,30),(48,3,60)):
                targets=[dict(copy.deepcopy(walk),kind=kind,target_id=100001+index,
                              target_position=[10016+16*index,10016],genuine_generated_target=True)
                         for index,kind in enumerate(('warp','twins'))]
                targets[1]['direct_route']=dict(copy.deepcopy(targets[1]),fake_collision_events=0,
                                                fake_contact_ids=[],peak_reveal=0)
                targets[1]['via_fake']={'id':9001,'position':[10016,10000],
                    'bbox':[10016,10000,10032,10016],'helper_id':9002,'helper_creator':9001,
                    'waypoint':[10024,10008],'waypoint_player_mask_intersects':True,
                    'generated_this_room':True,'generation_window':{'previous_twins_id':0,'twins_id':100002,
                        'room_twins_id':100002,'partner_id':0}}
                rows.append({'mode':mode,'seed':seed,'loops':loops,'rate':rate,'engine_rate':rate,
                    'native_scheduler':True,'manual_alarm_dispatch':False,'native_gen_frames':6,
                    'post_population_shifts':0,'generation_trace':[{'before':{'walls':0,'fake':0,'helpers':0}}],
                    'road':{'expected_points':120,'expected_edges':160,'pixel_swept':True,
                            'changed':[],'blocked_expected_edges':[]},
                    'rock_clearance_rule':'exclude actual PortalClear mask overlap',
                    'native_clearance_rocks':1 if mode=='in-room' and seed==22 else 0,
                    'protected_rocks':2,'preserved_rocks':2,
                    'rock_capture':[{'id':id_value,'exists':True,'portal_clear':clear,'overlap':[]}
                        for id_value,clear in enumerate([False,False]+([True] if mode=='in-room' and seed==22 else []))],
                    'before':{'twins':[{'id':100002,'position':[10032,10016],'partner_id':0}],
                        'geometry':{'walls':[{'id':9001,'x':10016,'y':10000,
                        'bbox':[10016,10000,10032,10016],'object':'NTTEFullWallFake'}],
                        'helpers':[{'id':9002,'creator':9001}]}},'walks':targets})
        return {'status':'PASS','diagnostic':False,'physical_device_tested':False,
                'native_scheduled_frames':12,'actual_player_mask':'mskPlayer 8x10','rows':rows}

    def test_red212_requires_all_scheduled_worlds_and_zero_late_shifts(self):
        import copy
        module=subject()
        with TemporaryDirectory() as temporary:
            directory=Path(temporary);path=directory/'frontier-red212-scheduled.json'
            data=self.red212_fixture();path.write_text(json.dumps(data),'utf8')
            module.verify_red212(directory)
            # GameMaker's serializer may emit integral values as 2.0.
            for row in data['rows']:row['protected_rocks']=float(row['protected_rocks'])
            path.write_text(json.dumps(data),'utf8');module.verify_red212(directory)
            invalid=[]
            for field,value in (('diagnostic',True),('status','FAIL'),('physical_device_tested',True),
                                ('native_scheduled_frames',0),('actual_player_mask','wrong mask')):
                changed=copy.deepcopy(data);changed[field]=value;invalid.append(changed)
            changed=copy.deepcopy(data);changed['rows'].pop();invalid.append(changed)
            changed=copy.deepcopy(data);changed['rows'][-1]=copy.deepcopy(changed['rows'][0]);invalid.append(changed)
            for field,value in (('native_scheduler',False),('manual_alarm_dispatch',True),
                                ('engine_rate',45),
                                ('native_gen_frames',0),('native_gen_frames',600),
                                ('post_population_shifts',1),('generation_trace',[])):
                changed=copy.deepcopy(data);changed['rows'][0][field]=value;invalid.append(changed)
            for field in ('walls','fake','helpers'):
                changed=copy.deepcopy(data);changed['rows'][0]['generation_trace'][0]['before'][field]=1
                invalid.append(changed)
            for index,changed in enumerate(invalid):
                path.write_text(json.dumps(changed),'utf8')
                with self.subTest(index=index),self.assertRaises(AssertionError):module.verify_red212(directory)

    def test_red212_binds_twins_entry_to_generated_fake_and_keeps_direct_route(self):
        import copy
        module=subject()
        with TemporaryDirectory() as temporary:
            directory=Path(temporary);path=directory/'frontier-red212-scheduled.json'
            data=self.red212_fixture();path.write_text(json.dumps(data),'utf8');module.verify_red212(directory)
            invalid=[]
            for field,value in (('reached',False),('returned',False),('blocked',[[1,2]]),
                                ('actual_wall_collision_events',False),('actual_helper_endstep',False),
                                ('manual_pixel_integration',False),('closed_overlapping_after_endstep',1),
                                ('orphan_helpers_after_endstep',1),('open_helpers_after_return',1),
                                ('reveal_after_return',1),('target_id',100003),('target_position',[0,0]),
                                ('genuine_generated_target',False),('kind','warp')):
                changed=copy.deepcopy(data);changed['rows'][0]['walks'][1]['direct_route'][field]=value
                invalid.append(changed)
            for field,value in (('id',True),('id',100002),('position',[1,2]),('bbox',[0,0,16,16]),
                                ('helper_id',9003),('helper_creator',9003),
                                ('waypoint',[0,float('nan')]),('waypoint_player_mask_intersects',False),
                                ('generated_this_room',False),
                                ('generation_window',{'previous_twins_id':9000,'twins_id':100002,
                                    'room_twins_id':100002,'partner_id':0}),
                                ('generation_window',{'previous_twins_id':0,'twins_id':100003,
                                    'room_twins_id':100002,'partner_id':0})):
                changed=copy.deepcopy(data);changed['rows'][0]['walks'][1]['via_fake'][field]=value
                invalid.append(changed)
            for field,value in (('fake_contact_ids',[]),('fake_contact_ids',[9002]),
                                ('fake_contact_ids',[9001,9001]),('fake_contact_ids',[True])):
                changed=copy.deepcopy(data);changed['rows'][0]['walks'][1][field]=value;invalid.append(changed)
            for category,field,value in (('walls','id',9003),('walls','object','Wall'),
                                         ('walls','x',10000),('helpers','creator',9003)):
                changed=copy.deepcopy(data);changed['rows'][0]['before']['geometry'][category][0][field]=value
                invalid.append(changed)
            for category in ('walls','helpers'):
                changed=copy.deepcopy(data);changed['rows'][0]['before']['geometry'][category]*=2
                invalid.append(changed)
            changed=copy.deepcopy(data);changed['rows'][0]['before']['twins'][0]['partner_id']=True
            invalid.append(changed)
            for index,changed in enumerate(invalid):
                path.write_text(json.dumps(changed),'utf8')
                with self.subTest(index=index),self.assertRaises(AssertionError):module.verify_red212(directory)
            # A genuine pair shares one preceding secret-corridor creation
            # window; both actual targets must still be walked independently.
            paired=copy.deepcopy(data);row=paired['rows'][0];first=row['walks'][1]
            second=copy.deepcopy(first);second['target_id']=100003;second['target_position']=[10048,10016]
            second['direct_route']['target_id']=100003
            second['direct_route']['target_position']=[10048,10016]
            first['via_fake']['generation_window']['partner_id']=100003
            second['via_fake']['generation_window'].update(twins_id=100003,partner_id=100002)
            row['walks'].append(second)
            row['before']['twins']=[{'id':100002,'position':[10032,10016],'partner_id':100003},
                                    {'id':100003,'position':[10048,10016],'partner_id':100002}]
            path.write_text(json.dumps(paired),'utf8');module.verify_red212(directory)
            invalid=[]
            changed=copy.deepcopy(paired);changed['rows'][0]['before']['twins'][1]['partner_id']=0
            invalid.append(changed)
            changed=copy.deepcopy(paired);changed['rows'][0]['walks'].pop();invalid.append(changed)
            changed=copy.deepcopy(paired);changed['rows'][0]['before']['twins'][1]['position']=[0,0]
            invalid.append(changed)
            for field,value in (('room_twins_id',100003),('previous_twins_id',100002),('partner_id',0)):
                changed=copy.deepcopy(paired)
                changed['rows'][0]['walks'][2]['via_fake']['generation_window'][field]=value
                invalid.append(changed)
            for index,changed in enumerate(invalid):
                path.write_text(json.dumps(changed),'utf8')
                with self.subTest(pair_index=index),self.assertRaises(AssertionError):module.verify_red212(directory)

    def test_red212_requires_original_roads_rocks_and_actual_hidden_round_trip(self):
        import copy
        module=subject()
        with TemporaryDirectory() as temporary:
            directory=Path(temporary);path=directory/'frontier-red212-scheduled.json'
            data=self.red212_fixture();invalid=[]
            for field,value in (('expected_points',0),('expected_edges',0),('pixel_swept',False),
                                ('changed',[[1,2]]),('blocked_expected_edges',[[1,2]])):
                changed=copy.deepcopy(data);changed['rows'][0]['road'][field]=value;invalid.append(changed)
            changed=copy.deepcopy(data);changed['rows'][0]['preserved_rocks']=1;invalid.append(changed)
            changed=copy.deepcopy(data);changed['rows'][0]['native_clearance_rocks']=-1;invalid.append(changed)
            changed=copy.deepcopy(data);changed['rows'][0]['rock_clearance_rule']='exclude nearby rocks';invalid.append(changed)
            changed=copy.deepcopy(data);changed['rows'][0]['rock_capture'][0]['portal_clear']=True;invalid.append(changed)
            changed=copy.deepcopy(data);changed['rows'][0]['rock_capture'][0]['exists']=False;invalid.append(changed)
            changed=copy.deepcopy(data)
            for row in changed['rows']:row['native_clearance_rocks']=0
            invalid.append(changed)
            changed=copy.deepcopy(data);changed['rows'][0]['walks'].pop();invalid.append(changed)
            changed=copy.deepcopy(data);changed['rows'][0]['walks'][1]['kind']='warp';invalid.append(changed)
            changed=copy.deepcopy(data);changed['rows'][0]['walks'][1]['target_id']=100001;invalid.append(changed)
            for field,value in (('steps',0),('reached',False),('returned',False),('blocked',[[1,2]]),
                                ('genuine_generated_target',False),('target_id',0),('target_id',1.5),
                                ('target_id',True),('target_position',[1]),('target_position',[1,float('nan')]),
                                ('target_position',[True,1]),
                                ('actual_wall_collision_events',False),('actual_helper_endstep',False),
                                ('manual_pixel_integration',False),('closed_overlapping_after_endstep',1),
                                ('orphan_helpers_after_endstep',1),('open_helpers_after_return',1),
                                ('reveal_after_return',1),('fake_collision_events',0),('peak_reveal',0)):
                changed=copy.deepcopy(data);changed['rows'][0]['walks'][1][field]=value;invalid.append(changed)
            for index,changed in enumerate(invalid):
                path.write_text(json.dumps(changed),'utf8')
                with self.subTest(index=index),self.assertRaises(AssertionError):module.verify_red212(directory)

    def red212_sweep_fixture(self,module,negative=False):
        rows=[]
        for seed in range(1,97):
            failed=negative and seed in module.RED212_FAILED_SEEDS
            rows.append({'seed':seed,'loops':(0,1,3)[(seed-1)%3],'native_gen_frames':6,
                'before_secret_protected':100,'expected_edges':120,'actual_player_mask_pixel_sweep':True,
                'generation_trace':[{'before':{'walls':1 if failed else 0,'fake':0,'helpers':0}}],
                'post_wall_shifts':1 if failed else 0,'changed':[[1,2]] if failed else [],
                'blocked_expected_edges':[[1,2]] if failed else []})
        return {'diagnostic':True,'native_scheduler':True,'manual_alarm_dispatch':False,
                'physical_device_tested':False,'actual_player_mask':'mskPlayer 8x10','rows':rows,
                'expected_road_failures':len(module.RED212_FAILED_SEEDS) if negative else 0}

    def test_red212_sweep_keeps_all_96_native_seeds_and_derives_late_shifts(self):
        import copy
        module=subject();data=self.red212_sweep_fixture(module)
        self.assertEqual(len(module.red212_sweep_rows(data)),96)
        invalid=[]
        changed=copy.deepcopy(data);changed['rows'].pop();invalid.append(changed)
        changed=copy.deepcopy(data);changed['rows'][-1]=copy.deepcopy(changed['rows'][0]);invalid.append(changed)
        for field,value in (('diagnostic',False),('native_scheduler',False),('manual_alarm_dispatch',True),
                            ('actual_player_mask','wrong mask')):
            changed=copy.deepcopy(data);changed[field]=value;invalid.append(changed)
        for field,value in (('before_secret_protected',0),('expected_edges',0),
                            ('actual_player_mask_pixel_sweep',False),('native_gen_frames',0)):
            changed=copy.deepcopy(data);changed['rows'][0][field]=value;invalid.append(changed)
        changed=copy.deepcopy(data);changed['rows'][0]['generation_trace'][0]['before']['helpers']=1
        invalid.append(changed)
        for index,changed in enumerate(invalid):
            with self.subTest(index=index),self.assertRaises(AssertionError):module.red212_sweep_rows(changed)

    def red212_supplement_fixture(self,module,root):
        module.ROOT=root;review=root/'review';review.mkdir()
        module.RED_SUPPLEMENT=review/'release212-red-supplement.json'
        descriptor={'version':'2.1.2','internal':107,'status':'READY'};builds={};data={}
        for index,kind in enumerate(('negative','positive')):
            run_name='tests/20261113T00000'+str(index)+'Z';run=root/run_name
            directory=run/'FrontierRed212ProbeTests';directory.mkdir(parents=True)
            data[kind]=self.red212_sweep_fixture(module,kind=='negative')
            artifact=directory/'frontier-red212-native-sweep.json';artifact.write_text(json.dumps(data[kind]),'utf8')
            (directory/'runner.log').write_text('###game_end###0','utf8')
            compile_log=run/'compile.log';compile_log.write_text(kind+' compile log','utf8')
            build={'vm_sha256':('a' if index==0 else 'c')*64,'input_sha256':('b' if index==0 else 'd')*64,
                   'log_sha256':module.sha(compile_log)};builds[kind]=build
            (run/'compiled-build.json').write_text(json.dumps(build),'utf8')
            receipt={'case':'FrontierRed212ProbeTests','status':'FAIL' if index==0 else 'PASS','exit':1-index,
                'termination_reason':'runtime_error' if index==0 else None,'physical_device_tested':False,
                'vm_sha256':build['vm_sha256'],'input_sha256':build['input_sha256'],
                'muted_resources':101,'desktop':'private, never activated',
                'artifacts_sha256':{artifact.name:module.sha(artifact)}}
            receipt_path=directory/'receipt.json';receipt_path.write_text(json.dumps(receipt),'utf8')
            descriptor[kind]={'run':run_name,'case':receipt['case'],'receipt_sha256':module.sha(receipt_path),
                'artifact_sha256':module.sha(artifact),'vm_sha256':build['vm_sha256'],'input_sha256':build['input_sha256']}
        module.RED212_NEGATIVE=dict(descriptor['negative'])
        seed15={'negative_control':{'run':descriptor['negative']['run'],'case':descriptor['negative']['case'],
            'receipt_sha256':descriptor['negative']['receipt_sha256'],
            'raw_sweep_sha256':descriptor['negative']['artifact_sha256'],'compiled_build':builds['negative']}}
        (review/'red212-native-seed15-evidence.json').write_text(json.dumps(seed15),'utf8')
        (review/'RED212_CAUSE.md').write_text('Recorded native negative and positive controls.','utf8')
        summary=module.red212_supplement_summary(descriptor,module.red212_sweep_rows(data['negative']),
                                                module.red212_sweep_rows(data['positive']))
        (review/'red212-native-sweep-after-summary.json').write_text(json.dumps(summary),'utf8')
        descriptor['public_evidence']={name:{'sha256':module.sha(root/name)} for name in module.RED212_PUBLIC_EVIDENCE}
        module.RED_SUPPLEMENT.write_text(json.dumps(descriptor),'utf8')
        return descriptor,builds['positive']

    def test_red212_supplement_rejects_unbound_files_stale_vm_and_public_evidence(self):
        import copy
        module=subject()
        with TemporaryDirectory() as temporary:
            root=Path(temporary);descriptor,compiled=self.red212_supplement_fixture(module,root)
            observed=module.verify_red212_supplement(compiled)
            self.assertFalse(observed['counted_in_formal_21_cases'])
            changed=copy.deepcopy(compiled);changed['input_sha256']='f'*64
            with self.assertRaises(AssertionError):module.verify_red212_supplement(changed)
            invalid=[]
            changed=copy.deepcopy(descriptor);changed['positive']['run']='tests/../outside';invalid.append(changed)
            changed=copy.deepcopy(descriptor);changed['positive']['receipt_sha256']='f'*64;invalid.append(changed)
            changed=copy.deepcopy(descriptor);changed['positive']['artifact_sha256']='f'*64;invalid.append(changed)
            changed=copy.deepcopy(descriptor);changed['negative']['vm_sha256']='f'*64;invalid.append(changed)
            changed=copy.deepcopy(descriptor);changed['public_evidence'].pop('review/RED212_CAUSE.md');invalid.append(changed)
            for index,changed in enumerate(invalid):
                module.RED_SUPPLEMENT.write_text(json.dumps(changed),'utf8')
                with self.subTest(index=index),self.assertRaises(AssertionError):module.verify_red212_supplement(compiled)
            module.RED_SUPPLEMENT.write_text(json.dumps(descriptor),'utf8')
            (root/'review/RED212_CAUSE.md').write_text('Changed after review.','utf8')
            with self.assertRaises(AssertionError):module.verify_red212_supplement(compiled)

    def test_red212_supplement_rejects_freshly_pinned_positive_failure(self):
        for field in ('road','shift','summary'):
            module=subject()
            with self.subTest(field=field),TemporaryDirectory() as temporary:
                root=Path(temporary);descriptor,compiled=self.red212_supplement_fixture(module,root)
                directory=root/descriptor['positive']['run']/'FrontierRed212ProbeTests'
                artifact=directory/'frontier-red212-native-sweep.json'
                data=json.loads(artifact.read_text('utf8'))
                if field=='road':
                    data['rows'][14]['changed']=[[1,2]];data['expected_road_failures']=1
                elif field=='shift':
                    data['rows'][14]['generation_trace'][0]['before']['walls']=1
                    data['rows'][14]['post_wall_shifts']=1
                else:
                    summary=root/'review/red212-native-sweep-after-summary.json'
                    record=json.loads(summary.read_text('utf8'));record['positive_rows'][14]['expected_points']+=1
                    summary.write_text(json.dumps(record),'utf8')
                    descriptor['public_evidence']['review/red212-native-sweep-after-summary.json']['sha256']=module.sha(summary)
                artifact.write_text(json.dumps(data),'utf8')
                receipt_path=directory/'receipt.json';receipt=json.loads(receipt_path.read_text('utf8'))
                receipt['artifacts_sha256'][artifact.name]=module.sha(artifact)
                receipt_path.write_text(json.dumps(receipt),'utf8')
                descriptor['positive']['artifact_sha256']=module.sha(artifact)
                descriptor['positive']['receipt_sha256']=module.sha(receipt_path)
                module.RED_SUPPLEMENT.write_text(json.dumps(descriptor),'utf8')
                with self.assertRaises(AssertionError):module.verify_red212_supplement(compiled)

    def test_clock_unit_requires_all_five_wallbounce_unit_contracts(self):
        import copy
        module=subject()
        with TemporaryDirectory() as temporary:
            directory=Path(temporary)
            data={'passed':True,'physical_device_tested':False,'checks':64,'transitions':[], 'wallbounce':[]}
            for index,rate in enumerate((60,30,60,30)):
                scale=30/rate
                data['transitions'].append({'rate':rate,'scale':scale,'hspeed':3*scale,
                    'friction':.2*scale*scale,'rocket_cap':12*scale,'source_max':4,'source_anim':.4})
                row={'rate':rate,'scale':scale,'native_logical':5*.95**(index+1)}
                for family,initial in (('native',5),('ntuf',4),('red',7),('venom',4),('shell',4)):
                    row[family+'_field']=initial*.95**(index+1)*(scale if family=='native' else 1)
                    row[family+'_speed']=min(4.8+initial*.95**index,16)
                data['wallbounce'].append(row)
            path=directory/'ntuf212-clock-unit.json';path.write_text(json.dumps(data),'utf8')
            module.verify_clock212(directory,False)
            for family in ('native','ntuf','red','venom','shell'):
                for suffix in ('field','speed'):
                    changed=copy.deepcopy(data)
                    changed['wallbounce'][0][family+'_'+suffix]*=.5
                    path.write_text(json.dumps(changed),'utf8')
                    with self.subTest(family=family,suffix=suffix),self.assertRaises(AssertionError):
                        module.verify_clock212(directory,False)
            for changed in ({k:v for k,v in data.items() if k!='wallbounce'},
                            dict(data,wallbounce=data['wallbounce'][:-1])):
                path.write_text(json.dumps(changed),'utf8')
                with self.assertRaises(AssertionError):module.verify_clock212(directory,False)

    def test_current_run_requires_hash_binding_for_ntuf212_artifact(self):
        module=subject()
        with TemporaryDirectory() as temporary:
            root=Path(temporary);module.ROOT=root;smoke=self.fixture(module,root)
            name='20261113T000000Z';run=root/'tests'/name;directory=run/'Fixture212Tests'
            directory.mkdir(parents=True);(root/'build-windows').mkdir()
            compile_log=run/'compile.log';compile_log.write_text('current compile','utf8')
            silent=root/'build-windows/frontier-silent.win';silent.write_bytes(b'current silent VM')
            compiled={'vm_sha256':'a'*64,'input_sha256':'b'*64,'log_sha256':module.sha(compile_log)}
            (run/'compiled-build.json').write_text(json.dumps(compiled),'utf8')
            (directory/'smoke.txt').write_text(smoke,'utf8')
            (directory/'runner.log').write_text('###game_end###0','utf8')
            artifact=directory/'ntuf212-fixture.json';artifact.write_text('{"passed":true}','utf8')
            receipt={'case':'Fixture212Tests','status':'PASS','exit':0,'termination_reason':None,
                     'vm_sha256':compiled['vm_sha256'],'input_sha256':compiled['input_sha256'],
                     'silent_vm_sha256':module.sha(silent),'physical_device_tested':False,
                     'muted_resources':101,'desktop':'private, never activated',
                     'artifacts_sha256':{artifact.name:module.sha(artifact)}}
            receipt_path=directory/'receipt.json';receipt_path.write_text(json.dumps(receipt),'utf8')
            self.assertEqual(module.check_run(name,module.FINAL_CASES,compiled)['count'],1)
            receipt['artifacts_sha256']={};receipt_path.write_text(json.dumps(receipt),'utf8')
            with self.assertRaises(AssertionError):module.check_run(name,module.FINAL_CASES,compiled)


if __name__=='__main__':unittest.main()
