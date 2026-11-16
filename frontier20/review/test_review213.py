"""Current213 identities, source binding and negative release-gate controls."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import importlib.util
import json
import unittest

HERE=Path(__file__).resolve().parent


def subject(relative):
    path=HERE.parent/relative
    spec=importlib.util.spec_from_file_location('current213_'+path.stem,path)
    module=importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


class Review213Tests(unittest.TestCase):
    def fixture(self,module,root):
        selection=json.loads(module.CASE_SELECTION.read_text('utf-8-sig'))
        contracts=json.loads(module.CONTRACTS.read_text('utf-8-sig'))
        module.CASE_SELECTION=root/'cases.json';module.CONTRACTS=root/'contracts.json'
        module.CASE_SELECTION.write_text(json.dumps(selection),'utf8')
        module.CONTRACTS.write_text(json.dumps(contracts),'utf8')
        return selection,contracts

    def test_independent32_case_scope_and_all17_repairs(self):
        module=subject('review/verify_213_repairs.py')
        self.assertEqual(len(module.EXPECTED213_CASES),32)
        self.assertEqual(len(module.require_selection()),32)
        with TemporaryDirectory() as temporary:
            root=Path(temporary);selection,contracts=self.fixture(module,root)
            module.require_selection()
            for cases in (selection['cases'][:-1],['UnreviewedTests',*selection['cases'][1:]]):
                changed=dict(selection,cases=cases)
                module.FINAL_CASES=tuple(cases)
                module.CASE_SELECTION.write_text(json.dumps(changed),'utf8')
                with self.assertRaises(AssertionError):module.require_selection()
            module.FINAL_CASES=module.EXPECTED213_CASES
            module.CASE_SELECTION.write_text(json.dumps(selection),'utf8')
            for flag in (False,None,1):
                changed=deepcopy(contracts)
                changed['cases']['FrontierBubbles213Tests']['required']=flag
                module.CONTRACTS.write_text(json.dumps(changed),'utf8')
                with self.assertRaises(AssertionError):module.require_selection()
            changed=deepcopy(contracts)
            for contract in changed['cases'].values():
                contract['requirements']=[number for number in contract.get('requirements',[]) if number!=17]
            module.CONTRACTS.write_text(json.dumps(changed),'utf8')
            with self.assertRaises(AssertionError):module.require_selection()

    def test_current_markers_reject_generic_duplicate_or_error(self):
        module=subject('review/verify_213_repairs.py')
        case='FrontierBubbles213Tests'
        marker=module.require_selection()[case]['markers'][0]
        generic='PASS full internal selected implemented branches\n'
        with TemporaryDirectory() as temporary:
            directory=Path(temporary)
            module.verify_case_identity(case,marker+'\n'+generic,{},directory)
            for smoke in (generic,marker+'\n'+marker+'\n'+generic,
                          marker+'\n'+generic+'ERROR failed native path\n'):
                with self.assertRaises(AssertionError):module.verify_case_identity(case,smoke,{},directory)

    def test_quest_requires_complete_assertion_markers_at_each_native_rate(self):
        module=subject('review/verify_213_repairs.py');contracts=module.require_selection()
        cases=('QuestLockedNativeTests','QuestFloorNativeTests','QuestTeleporterNativeTests','QuestHubNativeTests')
        with TemporaryDirectory() as temporary:
            for case in cases:
                markers=contracts[case]['markers'];prefix,*full=markers
                self.assertEqual(contracts[case]['marker_counts'][prefix],2)
                self.assertEqual([marker[-3:] for marker in full],['@30','@60'])
                smoke='\n'.join(full)+'\nPASS full internal selected implemented branches\n'
                module.verify_case_identity(case,smoke,{},Path(temporary))
                for malformed in (smoke.replace(full[1],full[0]),smoke.replace(full[1],prefix),
                                  smoke.replace(full[1],full[1].replace(' OK @60',' @60'))):
                    with self.subTest(case=case),self.assertRaises(AssertionError):
                        module.verify_case_identity(case,malformed,{},Path(temporary))

    def test_bubbles_startup_requires_source_defined_new_retry_at_both_rates(self):
        module=subject('review/verify_213_repairs.py')
        for case,skin in (('FrontierBubblesStartupATests',0),('FrontierBubblesStartupBTests',1)):
            rows=[]
            for rate,trial in ((30,'new'),(30,'retry'),(60,'new'),(60,'retry')):
                rows.append({'requested_rate':rate,'rate':rate,'option_rate':rate,'scale':30/rate,
                             'trial':trial,'skin':skin,'random':False,'language':'English' if rate==30 else 'Simplified Chinese',
                             'native_runs':1,'source_runs':1,'source_ticks':180,'weapon':187+skin,'weapon_swing':True,
                             'bubbles':2,'steps':180,'ends':180,'draws':180,'huds':180,
                             'attack_hits':[{'mode':mode,'damage':6+skin*3,'hp_loss':6+skin*3}
                                            for mode in ('desktop-hold','mobile-tap','mobile-hold')]})
            def smoke(values):
                return '\n'.join('NTUF BUBBLES STARTUP real new-run acceptance PASS '+json.dumps(row) for row in values)+(
                    '\nNTUF BUBBLES STARTUP genuine death-menu Retry returned {}\n'
                    'NTUF BUBBLES STARTUP actual GameOver PauseButton Retry requested\n')*2
            self.assertEqual(len(module.verify_bubbles_startup213(case,smoke(rows))),4)
            bad=deepcopy(rows);bad[3]['trial']='new'
            wrong_damage=deepcopy(rows);wrong_damage[2]['attack_hits'][2]['hp_loss']=0
            incomplete=deepcopy(rows);incomplete[0]['source_ticks']=179
            for values in (rows[:-1],bad,wrong_damage,incomplete):
                with self.subTest(case=case),self.assertRaises(AssertionError):
                    module.verify_bubbles_startup213(case,smoke(values))

    def test_current_performance_artifact_never_claims_phone_test(self):
        module=subject('review/verify_213_repairs.py')
        case='FrontierPerformance213Tests';contract=module.require_selection()[case]
        smoke='\n'.join(contract['markers'])+'\nPASS full internal selected implemented branches\n'
        with TemporaryDirectory() as temporary:
            directory=Path(temporary);artifact=directory/'ntuf213-performance.json'
            for tested in (False,True):
                artifact.write_text(json.dumps({'passed':True,'device_tested':tested,'checks':6339,
                    'scope':'CPU mask queries; no Android frame-rate claim',
                    'laser':[{'hostiles':250,'candidates':2,'contacts':136,'oracle_us':1000,'optimized_us':100}]}),'utf8')
                pins={artifact.name:module.sha(artifact)}
                if tested:
                    with self.assertRaises(AssertionError):module.verify_case_identity(case,smoke,pins,directory)
                else:module.verify_case_identity(case,smoke,pins,directory)

    def test_current_clock_requires_complete_failed_recovery_scene_pause_evidence(self):
        module=subject('review/verify_213_repairs.py')
        recovery={'checks':16,'failed_recovery_probes':1,'latched_rate':30,
                  'same_area_generation_reset':True,'pause_keeps_latch':True,'device_tested':False}
        value={'passed':True,'physical_device_tested':False,'checks':145,'recovery213':recovery}
        self.assertEqual(module.verify_clock_recovery213(value),recovery)
        missing=dict(value);missing.pop('recovery213')
        bad=[missing,dict(value,checks=129),dict(value,physical_device_tested=True)]
        for key,wrong in (('checks',15),('failed_recovery_probes',0),('failed_recovery_probes',2),
                          ('failed_recovery_probes',True),('latched_rate',60),
                          ('same_area_generation_reset',False),('pause_keeps_latch',False),('device_tested',True)):
            changed=deepcopy(value);changed['recovery213'][key]=wrong;bad.append(changed)
        for item in bad:
            with self.subTest(item=item),self.assertRaises(AssertionError):module.verify_clock_recovery213(item)

    def test_legacy_clock_marker_cannot_bypass_current_recovery_evidence(self):
        module=subject('review/verify_213_repairs.py');case='FrontierClock212Tests'
        contract=deepcopy(module.require_selection()[case]);contract['artifacts']=['ntuf212-clock-unit.json']
        module.require_selection=lambda:{case:contract}
        # Even if the retained212 assertion implementation accepted a generic
        # old fixture, the current213 dispatch must require its own evidence.
        module.load=lambda *args:SimpleNamespace(FINAL_CASES=(case,),verify_case_identity=lambda *args:'old accepted')
        smoke='\n'.join(contract['markers'])+'\nPASS full internal selected implemented branches\n'
        with TemporaryDirectory() as temporary:
            directory=Path(temporary);artifact=directory/'ntuf212-clock-unit.json'
            artifact.write_text(json.dumps({'passed':True,'checks':129,'physical_device_tested':False}),'utf8')
            with self.assertRaises(AssertionError):
                module.verify_case_identity(case,smoke,{artifact.name:module.sha(artifact)},directory)

    def test_rerun212_and_new213_artifacts_both_need_pins(self):
        module=subject('review/verify_213_repairs.py')
        with TemporaryDirectory() as temporary:
            root=Path(temporary)
            for name in ('ntuf212-clock.json','ntuf213-performance.json','frontier-case.png'):
                (root/name).write_bytes(b'fixture')
            (root/'unrelated.txt').write_bytes(b'fixture')
            self.assertEqual(module.artifact_inventory(root),
                             {'ntuf212-clock.json','ntuf213-performance.json','frontier-case.png'})

    def test_python_capture_binds_every_executed_reviewer_dependency(self):
        capture=subject('review/capture213_python.py')
        verifier=subject('review/verify_213_repairs.py')
        pins=capture.reviewer_inputs()
        self.assertLessEqual(verifier.REVIEW_DEPENDENCIES,set(pins))
        self.assertIn('review/test_review213.py',pins)
        modules=capture.suite_command()[1]
        self.assertIn('review/test_review213.py',modules)

    def test_missing_reviewer_dependency_cannot_satisfy_python_binding(self):
        module=subject('review/verify_213_repairs.py')
        value={'version':'2.1.3','internal':108,'exit':0,'tests':1,
               'source_inputs_unchanged':True,'reviewer_inputs_unchanged':True,
               'source_inputs':{},'reviewer_inputs':{}}
        with self.assertRaises(AssertionError):module.verify_python_sources(value)


class Delivery213Tests(unittest.TestCase):
    def test_inert_current_identity_and_no_historical_acceptance_definitions(self):
        module=subject('tools/release213_delivery.py');plan=module.plan()
        self.assertEqual((plan['version'],plan['internal'],plan['android_version_code']),('2.1.3',108,3000108))
        self.assertEqual(len(plan['required_cases']),32)
        self.assertFalse(plan['executes_builds_in_plan']);self.assertFalse(plan['publishes'])
        self.assertFalse(plan['historical_acceptance_reused'])
        self.assertEqual(module.package_path('Android').name,'NuclearThrone.NTTE-NTUF-Android-2.1.3.apk')
        self.assertEqual(module.package_path('iOS').name,'NuclearThrone.NTTE-NTUF-iOS-2.1.3.ipa')
        self.assertFalse(set(module.REUSED_FUNCTIONS)&{'gate','accept','configured_evidence','required_cases','main'})

    def test_old_identity_and_draft_review_never_unlock_current_gate(self):
        module=subject('tools/release213_delivery.py')
        with TemporaryDirectory() as temporary:
            module.CONFIG=Path(temporary)/'config.json'
            for version,internal,status in (('2.1.2',107,'READY'),('2.1.3',108,'DRAFT')):
                module.CONFIG.write_text(json.dumps({'version':version,'internal':internal,'status':status}),'utf8')
                with self.assertRaises(AssertionError):module.configured_evidence()

    def test_current_source_or_vm_change_invalidates_compiler_binding(self):
        module=subject('tools/release213_delivery.py')
        with TemporaryDirectory() as temporary:
            root=Path(temporary);module.FRONTIER=root;build=root/'build-windows';build.mkdir()
            vm=build/'nuclearthronemobile.win';vm.write_bytes(b'current213 VM')
            log=build/'compile.log';log.write_bytes(b'current213 compiler log')
            current={'input_sha256':'a'*64,'staged_files':{'current.gml':'b'*64}}
            capture=root/'capture.json';capture.write_text(json.dumps(current),'utf8')
            compiled={'status':'COMPILED_NOT_PLAYABLE_VERIFIED','input_sha256':current['input_sha256'],
                      'vm_sha256':module.sha(vm),'log_sha256':module.sha(log),'input_manifest':'capture.json'}
            (build/'last-success.json').write_text(json.dumps(compiled),'utf8')
            module.load=lambda *args:SimpleNamespace(snapshot=lambda:current)
            module.configured_evidence=lambda:({'input_sha256':compiled['input_sha256'],'vm_sha256':compiled['vm_sha256']},None,None)
            module.snapshot=lambda *args:dict(current['staged_files'])
            self.assertEqual(module.input_state(),(current,compiled))
            current['staged_files']['current.gml']='c'*64
            with self.assertRaises(AssertionError):module.input_state()
            current['staged_files']['current.gml']='b'*64;vm.write_bytes(b'old VM')
            with self.assertRaises(AssertionError):module.input_state()

    def test_delivery_rejects_omitted212_or213_artifact(self):
        for prefix in ('ntuf212-','ntuf213-'):
            module=subject('tools/release213_delivery.py')
            with self.subTest(prefix=prefix),TemporaryDirectory() as temporary:
                root=Path(temporary);module.FRONTIER=root
                directory=root/'tests/20261115T000000Z/Fixture213Tests';directory.mkdir(parents=True)
                compiled={'vm_sha256':'a'*64,'input_sha256':'b'*64}
                (directory.parent/'compiled-build.json').write_text(json.dumps(compiled),'utf8')
                (directory/'smoke.txt').write_text('PASS full internal selected implemented branches\n','utf8')
                (directory/'runner.log').write_text('###game_end###0','utf8')
                artifact=directory/(prefix+'fixture.json');artifact.write_text('{"passed":true}','utf8')
                module.load=lambda *args:SimpleNamespace(verify_case_identity=lambda *args:None)
                record={'case':'Fixture213Tests','status':'PASS','exit':0,'termination_reason':None,
                        **compiled,'physical_device_tested':False,'muted_resources':101,
                        'desktop':'private, never activated','artifacts_sha256':{artifact.name:module.sha(artifact)}}
                receipt=directory/'receipt.json';receipt.write_text(json.dumps(record),'utf8')
                module.verify_case(receipt,'Fixture213Tests',compiled)
                record['artifacts_sha256']={};receipt.write_text(json.dumps(record),'utf8')
                with self.assertRaises(AssertionError):module.verify_case(receipt,'Fixture213Tests',compiled)

    def test_fresh_android_signature_rejects_another_certificate(self):
        module=subject('tools/release213_delivery.py')
        with TemporaryDirectory() as temporary:
            root=Path(temporary);module.ANDROID=root
            toolchain=root/'toolchain';(toolchain/'jdk-17-fixture').mkdir(parents=True)
            module.android_env=lambda *args:{};module.native_layout=lambda *args:{'alignment_16kb_verified':True}
            signer={'certificate':module.CERTIFICATE}
            def run(command,path,**kwargs):
                if 'signature' in path.name:
                    output=('Verified using v1 scheme (JAR signing): true\n'
                            'Verified using v2 scheme (APK Signature Scheme v2): true\n'
                            'Signer #1 certificate SHA-256 digest: '+signer['certificate'])
                elif 'badging' in path.name:
                    output=("package: name='com.arkintide.nuclearthronentte' versionCode='3000108' versionName='2.1.3'\n"
                            "application-label:'Nuclear Throne :Territorial Expansion'\n"
                            "sdkVersion:'21' targetSdkVersion:'36'\n"
                            "native-code: 'armeabi-v7a' 'arm64-v8a'")
                else:output='Alignment successful'
                path.write_text(output,'utf8');return 0
            module.run=run
            module.verify_android(root/'fixture.apk',toolchain,root,phase='assemble')
            signer['certificate']='f'*64
            with self.assertRaises(AssertionError):module.verify_android(root/'fixture.apk',toolchain,root,phase='assemble')

    def test_independent_package_audit_requires_current32_cases(self):
        module=subject('review/inspect_release213_packages.py')
        source=(HERE.parent/'tools/release213_delivery.py').read_text('utf8')
        selection=json.loads((HERE/'release213-cases.json').read_text('utf8'))
        self.assertEqual(len(module.delivery_cases(source,selection)),32)
        for cases in (selection['cases'][:21],['UnreviewedTests',*selection['cases'][1:]],
                      [selection['cases'][1],selection['cases'][0],*selection['cases'][2:]]):
            with self.subTest(cases=cases),self.assertRaises(RuntimeError):
                module.delivery_cases(source,dict(selection,cases=cases))


if __name__=='__main__':unittest.main()
