"""Reject omitted scope and wrong/missing completion evidence offline."""
from pathlib import Path
import ast
import importlib.util
import re
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch

P=Path(__file__).with_name('verify_210_repairs.py')
spec=importlib.util.spec_from_file_location('review210_guard',P)
tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool)

class Review210Tests(unittest.TestCase):
    def test_exact_scope(self):
        self.assertEqual(len(tool.load_cases()),28)
        original=tool.read(tool.CASE_SELECTION)
        for kind in ('omit','duplicate','identity'):
            value={**original,'cases':list(original['cases'])}
            if kind=='omit':value['cases'].pop(0)
            if kind=='duplicate':value['cases'][-1]=value['cases'][0]
            if kind=='identity':value['internal']=103
            with self.subTest(kind=kind),patch.object(tool,'read',return_value=value):
                with self.assertRaises(AssertionError):tool.load_cases()

    def test_210_assertion_marker_required(self):
        for case in ('FrontierFeatures210Tests','FrontierContent210Tests','FrontierRedTerrain210Tests',
                     'FrontierFollowup210Tests','FrontierBluescreenUI204Yes30Tests','FrontierBluescreenUI204Yes60Tests'):
            with self.subTest(case=case),self.assertRaises(AssertionError):
                tool.verify_case_identity(case,'PASS full internal selected implemented branches',{},Path('.'))

    def test_native_case_and_dense_collision_contract(self):
        with self.assertRaises(AssertionError):
            tool.verify_case_identity('UnknownTests','PASS full internal selected implemented branches',{},Path('.'))
        rows=[dict(rate=rate,reference=reference,projectiles=512,
                   hostile_intercepted=256,allied_neutral_passed=256)
              for rate in (30,60) for reference in (False,True)]
        artifact={'physical_device_tested':False,'natural_collision':rows}
        smoke='FRONTIER DRONE204 ACCEPTED PASS full internal selected implemented branches'
        files={'frontier-drone-performance204.json':'checked-in-check_run'}
        with patch.object(tool,'read',return_value=artifact):
            tool.verify_case_identity('FrontierDronePerformance204Tests',smoke,files,Path('.'))
            rows[0]['hostile_intercepted']=286
            with self.assertRaises(AssertionError):
                tool.verify_case_identity('FrontierDronePerformance204Tests',smoke,files,Path('.'))

    def test_ios_package_review_accepts_current_canonical_version(self):
        package=runpy.run_path(str(P.with_name('inspect_release210_packages.py')))
        tree=ast.parse(package['_source'])
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='source_chain')
        calls=[n for n in ast.walk(function) if isinstance(n,ast.Call)
               and isinstance(n.func,ast.Attribute) and n.func.attr=='subn']
        self.assertEqual(len(calls),1)
        pattern,replacement=[ast.literal_eval(n) for n in calls[0].args[:2]]
        raw=(tool.ROOT/'staging/project/options/ios/options_ios.yy').read_text('utf8')
        checked,count=re.subn(pattern,replacement,raw)
        self.assertEqual(count,1)
        self.assertEqual(checked,raw)

    def test_capture_import_from_delivery_entrypoint(self):
        script="import runpy; m=runpy.run_path('review/verify_210_repairs.py'); assert m['capture_module']().ROOT==m['ROOT']"
        result=subprocess.run([sys.executable,'-B','-c',script],cwd=tool.ROOT,
                              capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main()
