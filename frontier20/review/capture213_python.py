"""Run explicit current2.1.3 Python modules and pin exact maintained sources.

No historical test result or fixed aggregate count is inherited. The owner
finalizes review/release213-python-tests.json before invoking this tool.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'review/release213-python-tests.json'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):return json.loads(path.read_text('utf-8-sig'))


def inputs():
    paths=[*sorted((ROOT/'tools').glob('*.py')),*sorted((ROOT/'native').glob('*.gml'))]
    paths += sorted(p for p in (ROOT/'tools/fixtures/frozen-archive20261111').rglob('*') if p.is_file())
    return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}


def reviewer_inputs():
    paths=[ROOT/'review/verify_213_repairs.py',ROOT/'review/release213-cases.json',
           ROOT/'review/release213-case-contracts.json',PLAN,Path(__file__).resolve(),
           ROOT/'review/inspect_release213_packages.py',ROOT/'review/verify_212_repairs.py',
           ROOT/'review/release212-cases.json',ROOT/'review/release212-case-contracts.json',
           ROOT/'review/verify_bubbles212.py']
    paths += [ROOT/name for name in read(PLAN)['modules'] if name.startswith('review/')]
    return {p.relative_to(ROOT).as_posix():sha(p) for p in paths}


def suite_command():
    plan=read(PLAN)
    assert plan['version']=='2.1.3' and plan['internal']==108 and plan['status']=='READY'
    modules=plan['modules']
    assert isinstance(modules,list) and modules and len(modules)==len(set(modules))
    for name in modules:
        assert re.fullmatch(r'(?:tools|review)/test_[A-Za-z0-9_]+\.py',name)
        assert (ROOT/name).is_file()
    bootstrap="""import importlib.util,pathlib,sys,unittest
root=pathlib.Path(sys.argv[1]);sys.path[:0]=[str(root/'tools'),str(root/'review')]
suite=unittest.TestSuite()
for index,name in enumerate(sys.argv[2:]):
 path=root/name;spec=importlib.util.spec_from_file_location('ntuf213_test_'+str(index),path)
 module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
 suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result=unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
"""
    return [sys.executable,'-B','-c',bootstrap,str(ROOT),*modules],modules


def main():
    label=sys.argv[1] if len(sys.argv)>1 else 'post213-python-regression'
    assert re.fullmatch(r'post213-python-regression(?:-[a-z0-9]+)?',label)
    log=ROOT/'review'/(label+'.txt');receipt=log.with_suffix('.json')
    assert not log.exists() and not receipt.exists()
    before,review=inputs(),reviewer_inputs()
    command,modules=suite_command()
    result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output=result.stdout.decode('utf8',errors='replace')
    counts=re.findall(r'^Ran (\d+) tests in ',output,re.M)
    count=int(counts[0]) if len(counts)==1 else 0
    record={'version':'2.1.3','internal':108,'tests':count,'exit':result.returncode,
            'log':log.relative_to(ROOT).as_posix(),'log_sha256':hashlib.sha256(result.stdout).hexdigest(),
            'source_inputs':before,'source_inputs_unchanged':before==inputs(),
            'reviewer_inputs':review,'reviewer_inputs_unchanged':review==reviewer_inputs(),
            'review_test_modules':modules,'utc':datetime.now(timezone.utc).isoformat()}
    log.write_bytes(result.stdout);receipt.write_text(json.dumps(record,indent=2)+'\n','utf8')
    print(output[-7000:])
    assert result.returncode==0 and count>0 and re.search(r'\nOK\s*$',output)
    assert record['source_inputs_unchanged'] and record['reviewer_inputs_unchanged']


if __name__=='__main__':main()
