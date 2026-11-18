"""Current214 structured-evidence validators and negative release controls.

These synthetic fixtures test the reviewers only; they are never accepted as
gameplay evidence or written into a native-run receipt directory.
"""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import importlib.util
import json
import unittest


ROOT=Path(__file__).resolve().parents[1]


def subject():
    path=ROOT/'review/verify_214_repairs.py'
    spec=importlib.util.spec_from_file_location('review214_negative_subject',path)
    module=importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def menus_fixture():
    views=[[424,240,848,480],[280,160,840,480]];rows=[]
    for hz in (30,60):
        for view in views:
            rows.append(dict(kind='robot',hz=hz,view=view,samples=100,
                             old_matrix_pixel_errors=100,fixed_matrix_pixel_errors=0,
                             missing_child_recovered=True))
    for language in ('Simplified Chinese','English'):
        for view in views:
            for slot in range(5):
                rows.append(dict(kind='surgery',language=language,view=view,slot=slot,glyph_samples=40,
                    line_ink=[[52,62],[72,82]],layout=dict(x=500100,top=499820,width=184,height=80,
                    title_y=499828,body_y=499850,title_h=12,body_h=36,title_scale=.9,body_scale=.8,
                    title='手术' if language=='Simplified Chinese' else 'SURGERY',body='GAIN\nLOSE',
                    cjk=language=='Simplified Chinese')))
        for key in ('cprefs_parrot','cprefs_bubbles'):
            rows.append(dict(kind='preference',language=language,key=key,menu_pixels=200,
                             layout=dict(text_x=124,text_y=90.5,icon_cx=111.5,icon_cy=96,
                                         icon_x=112,icon_y=96,label='TOGGLE',value_x=290,
                                         text_width=100,text_scale=1)))
    return dict(passed=True,physical_android_tested=False,checks=140,cases=rows)


def melee_smoke(rows):
    text='\n'.join(('FRONTIER214 Long Arms fusion launch ' if row.get('fusion',False)
                    else 'FRONTIER214 Long Arms launch ')+json.dumps(row) for row in rows)+'\n'
    text+='PASS FRONTIER214 actual native Long Arms0/1/2 geometric range and speed for all10 NTUF and7 NTTE melee at30/60Hz '+json.dumps(rows)+'\n'
    text+=('PASS FRONTIER214 actual Scythe control Draw retained icon/button and excluded exact old arrow overlay '+
           json.dumps(dict(ink=100,overlay_change=20))+'\n')*2
    return text


def performance_fixture(module):
    compatibility=[dict(context=context,target=target,selector=selector,outcome='return',
                        optimized_outcome='return',matched=True,value=True,value_type='bool')
                   for context,targets in (
                       ('fixture_scope',sorted(module.PERFORMANCE214_TARGETS)),
                       ('projectile_with_scope',('self_keyword','other_keyword','self_alias','other_alias')))
                   for target in targets for selector in sorted(module.PERFORMANCE214_SELECTORS)]
    # Keep both legacy branches covered by the reviewer negative controls.
    compatibility[0].update(outcome='throw',optimized_outcome='throw')
    del compatibility[0]['value'];del compatibility[0]['value_type']
    return dict(physical_device_tested=False,scope='Fresh projectile family queries; no device FPS claim',
                checks=3156,rows=[dict(phase=phase,selector=selector,count=100,
                oracle_us=10,optimized_us=2) for phase in range(4) for selector in (
                    '@ref object(projectile)','@ref object(FRCustomProjectile)',-10110)],
                compatibility_contract='legacy-scrFRInstanceIs-without-fast-v1',
                compatibility_checks=266,compatibility=compatibility)


def scythe_fixture():
    rows=[]
    for hz in (30,60):
        for stack in range(2):
            for heavy in (False,True):
                reach=48+8*stack+8*heavy
                rows.append(dict(hz=hz,stack=stack,heavy=heavy,frames=2,max_hit=reach,
                    selection='SkillIcon.Select' if stack else 'unowned',hit_distances=[8,reach],
                    samples=[dict(age=age,x=8+age,index=age,bbox_left=8,bbox_right=24+age,hits=age)
                             for age in (1,2)]))
    return dict(status='PASS',rows=rows,manual_damage_or_collision_calls=False,actual_skill_icon_selection=True)


def scythe_smoke(value):
    return '\n'.join('FRONTIER214 Scythe actual engine hit range '+json.dumps(row) for row in value['rows'])


class Review214Tests(unittest.TestCase):
    def test_independent37_case_scope_all8_repairs_and_complete_ui_images(self):
        module=subject()
        self.assertEqual(len(module.EXPECTED214_CASES),37)
        selection=module.read(module.CASE_SELECTION);contracts=module.read(module.CONTRACTS)
        with TemporaryDirectory() as temporary:
            root=Path(temporary);module.CASE_SELECTION=root/'cases.json';module.CONTRACTS=root/'contracts.json'
            selection['status']=contracts['status']='READY'
            module.CASE_SELECTION.write_text(json.dumps(selection),'utf8')
            module.CONTRACTS.write_text(json.dumps(contracts),'utf8')
            accepted=module.require_selection()
            self.assertEqual(len(accepted),37)
            self.assertEqual(len(accepted['FrontierMenus214Tests']['png_artifacts']),26)
            self.assertEqual(set(accepted['FrontierMenus214Tests']['requirements']),{3,4,7})
            for cases in (selection['cases'][:-1],['UnreviewedTests',*selection['cases'][1:]]):
                module.FINAL_CASES=tuple(cases)
                module.CASE_SELECTION.write_text(json.dumps(dict(selection,cases=cases)),'utf8')
                with self.assertRaises(AssertionError):module.require_selection()
            module.FINAL_CASES=module.EXPECTED214_CASES
            module.CASE_SELECTION.write_text(json.dumps(selection),'utf8')
            missing=deepcopy(contracts)
            for record in missing['cases'].values():record['requirements']=[x for x in record.get('requirements',[]) if x!=7]
            module.CONTRACTS.write_text(json.dumps(missing),'utf8')
            with self.assertRaises(AssertionError):module.require_selection()
            missing=deepcopy(contracts);missing['cases']['FrontierMenus214Tests']['artifacts'].pop()
            module.CONTRACTS.write_text(json.dumps(missing),'utf8')
            with self.assertRaises(AssertionError):module.require_selection()
            missing=deepcopy(contracts);missing['cases']['FrontierMelee214Tests']['artifacts'].pop()
            module.CONTRACTS.write_text(json.dumps(missing),'utf8')
            with self.assertRaises(AssertionError):module.require_selection()

    def test_ui_requires_independent_pixels_actual_rows_and_visible_line_leading(self):
        module=subject();value=menus_fixture()
        self.assertEqual(len(module.verify_menus214(value)),28)
        malformed=[]
        for row,key,wrong in ((0,'old_matrix_pixel_errors',0),(0,'fixed_matrix_pixel_errors',1),
                              (0,'missing_child_recovered',False),(4,'glyph_samples',0),
                              (-1,'menu_pixels',0)):
            bad=deepcopy(value);bad['cases'][row][key]=wrong;malformed.append(bad)
        bad=deepcopy(value);bad['cases'][4]['layout']['body_y']=bad['cases'][4]['layout']['title_y'];malformed.append(bad)
        bad=deepcopy(value);bad['cases'][4]['line_ink']=[[52,62],[62,72]];malformed.append(bad)
        bad=deepcopy(value);bad['cases'][-1]['layout']['text_x']-=3;malformed.append(bad)
        bad=deepcopy(value);bad['cases'][-1]['layout']['text_width']=200;malformed.append(bad)
        malformed.extend((dict(value,physical_android_tested=True),dict(value,checks=139),
                          dict(value,cases=value['cases'][:-1])))
        for index,bad in enumerate(malformed):
            with self.subTest(negative=index),self.assertRaises(AssertionError):module.verify_menus214(bad)

    def test_performance_requires_fresh_complete_ancestry_grid_without_phone_fps_claim(self):
        module=subject();value=performance_fixture(module)
        self.assertEqual(len(module.verify_performance214(value)),12)
        bad=deepcopy(value);bad['rows'][0]['optimized_us']=float('nan')
        missing=dict(value,rows=value['rows'][:-1]);duplicated=deepcopy(value);duplicated['rows'][0]=duplicated['rows'][1]
        wrong_contract=dict(value,compatibility_contract='fast-oracle')
        missing_compat=dict(value,compatibility=value['compatibility'][:-1])
        duplicated_compat=deepcopy(value);duplicated_compat['compatibility'][0]=duplicated_compat['compatibility'][1]
        mismatched=deepcopy(value);mismatched['compatibility'][1]['matched']=False
        changed_throw=deepcopy(value);changed_throw['compatibility'][0]['optimized_outcome']='return'
        throw_value=deepcopy(value);throw_value['compatibility'][0]['value']=False
        invalid_return=deepcopy(value);invalid_return['compatibility'][1]['value']=2
        for broken in (bad,missing,duplicated,dict(value,checks=3155),dict(value,physical_device_tested=True),
                       dict(value,scope='Android60FPS'),wrong_contract,missing_compat,duplicated_compat,
                       mismatched,changed_throw,throw_value,invalid_return,dict(value,compatibility_checks=265)):
            with self.assertRaises(AssertionError):module.verify_performance214(broken)

    def test_melee_requires_all17_weapons_both_rates_and_real_increasing_geometry(self):
        module=subject()
        rows=[]
        for hz in (30,60):
            for weapon in sorted(module.MELEE214_WEAPONS):
                for fusion in (False,True):
                    row=dict(weapon=weapon,hz=hz,probes=[dict(count=1,reach=10,
                             speed=2.5+stack*2) for stack in range(3)])
                    if fusion:row.update(fusion=True,melee_role='front')
                    else:row.update(name='MELEE')
                    rows.append(row)
        self.assertEqual(len(module.verify_melee214(melee_smoke(rows))),68)
        reach=deepcopy(rows);reach[0]['probes'][1]['reach']=5
        speed=deepcopy(rows);speed[-1]['probes'][2]['speed']=2.5
        count=deepcopy(rows);count[3]['probes'][1]['count']=2
        identity=deepcopy(rows)
        for row in identity:
            if row['weapon']==134:row['weapon']=999
        locked=deepcopy(rows);locked[0]['name']='LOCKED'
        for bad in (rows[:-1],reach,speed,count,identity,locked):
            with self.assertRaises(AssertionError):module.verify_melee214(melee_smoke(bad))
        broken=melee_smoke(rows).replace('"overlay_change": 20','"overlay_change": 0')
        with self.assertRaises(AssertionError):module.verify_melee214(broken)

    def test_scythe_requires_scheduled_engine_samples_real_selection_and_hit_distances(self):
        module=subject();value=scythe_fixture()
        self.assertEqual(len(module.verify_scythe_natural214(value,scythe_smoke(value))),8)
        negatives=[]
        for field,wrong in (('manual_damage_or_collision_calls',True),('actual_skill_icon_selection',False),
                            ('status','DRAFT')):
            negatives.append(dict(value,**{field:wrong}))
        for field,wrong in (('max_hit',200),('frames',3),('selection','assigned flag'),
                            ('hit_distances',[]),('heavy',0)):
            bad=deepcopy(value);bad['rows'][0][field]=wrong;negatives.append(bad)
        for field,wrong in (('age',1),('index',0),('hits',50),('bbox_right',7),('x',float('nan'))):
            bad=deepcopy(value);bad['rows'][0]['samples'][1][field]=wrong;negatives.append(bad)
        bad=deepcopy(value);bad['rows'][2]['max_hit']=52;bad['rows'][2]['hit_distances']=[8,52];negatives.append(bad)
        bad=deepcopy(value);bad['rows'][4]['max_hit']=56;bad['rows'][4]['hit_distances']=[8,56];negatives.append(bad)
        negatives.append(dict(value,rows=value['rows'][:-1]))
        for index,bad in enumerate(negatives):
            with self.subTest(negative=index),self.assertRaises(AssertionError):
                module.verify_scythe_natural214(bad,scythe_smoke(bad))
        with self.assertRaises(AssertionError):module.verify_scythe_natural214(value,'')

    def test_movement_requires_equal_time_continuous_native_input_evidence(self):
        module=subject();prefix='FRONTIER214 MOVEMENT RESULTS '
        value=dict(rates=[30,60],checks=51,deadzone_gui_px=2,fine_move_gui_px=3,
                   fixture='Windows raw touch through JoystickMove',ramp=[[15,1/3,.2],[15,1/3,.2]])
        module.verify_movement214(prefix+json.dumps(value))
        ramp=deepcopy(value);ramp['ramp'][1][0]=30
        for bad in (ramp,dict(value,rates=[60,60]),dict(value,checks=50),dict(value,deadzone_gui_px=8)):
            with self.assertRaises(AssertionError):module.verify_movement214(prefix+json.dumps(bad))

    def test_generic_pass_marker_cannot_bypass_current_structured_ui_evidence(self):
        module=subject();case='FrontierMenus214Tests'
        contract=dict(required=True,markers=['PASS UI214 ACTUAL'],artifacts=['ntuf214-menus.json'])
        module.require_selection=lambda:{case:contract}
        module.load=lambda *args:SimpleNamespace(FINAL_CASES=())
        smoke='PASS UI214 ACTUAL\nPASS full internal selected implemented branches\n'
        with TemporaryDirectory() as temporary:
            directory=Path(temporary);artifact=directory/'ntuf214-menus.json'
            artifact.write_text(json.dumps(menus_fixture()),'utf8')
            module.verify_case_identity(case,smoke,{artifact.name:module.sha(artifact)},directory)
            value=menus_fixture();value['cases'][0]['fixed_matrix_pixel_errors']=10
            artifact.write_text(json.dumps(value),'utf8')
            with self.assertRaises(AssertionError):
                module.verify_case_identity(case,smoke,{artifact.name:module.sha(artifact)},directory)
            with self.assertRaises(AssertionError):module.verify_case_identity(case,smoke,{},directory)

    def test_current_python_selection_keeps_menu_hooks_and_own_negative_controls(self):
        plan=json.loads((ROOT/'review/release214-python-tests.json').read_text('utf-8-sig'))
        self.assertIn('review/test_review214.py',plan['modules'])
        self.assertIn('tools/test_fr_menus214_hooks.py',plan['modules'])
        self.assertIn('tools/test_fr_movement214_hooks.py',plan['modules'])
        module=subject()
        module.require_python_scope(plan['modules'])
        for missing in module.REQUIRED214_PYTHON_MODULES:
            with self.subTest(missing=missing),self.assertRaises(AssertionError):
                module.require_python_scope([name for name in plan['modules'] if name!=missing])
        self.assertIn('ntuf214-pixels.png',self.artifacts(module,'ntuf214-pixels.png'))

    def artifacts(self,module,name):
        with TemporaryDirectory() as temporary:
            directory=Path(temporary);(directory/name).write_bytes(b'fixture')
            return module.artifact_inventory(directory)


if __name__=='__main__':unittest.main()
