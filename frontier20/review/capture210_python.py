"""Capture current maintained source and passing Python log for 2.1.0."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import re
import subprocess
import sys
import capture205_python as previous

ROOT=Path(__file__).resolve().parents[1]
REVIEW_TESTS=(*previous.REVIEW_TESTS,'review/test_review210.py')
REVIEW_INPUTS=(*previous.REVIEW_INPUTS,'review/verify_210_repairs.py','review/capture210_python.py',
              'review/test_review210.py','review/release210-cases.json','review/release210-user-requirements.json',
              'review/inspect_release210_packages.py','review/verify_release210_debug_font.py')
inputs=previous.inputs

def reviewer_inputs():
    return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in REVIEW_INPUTS}

def main():
    label=sys.argv[1] if len(sys.argv)>1 else 'post210-python-regression'
    assert re.fullmatch(r'post210-python-regression(?:-[a-z0-9]+)?',label)
    log=ROOT/'review'/(label+'.txt');receipt=log.with_suffix('.json')
    assert not log.exists() and not receipt.exists()
    before,review=inputs(),reviewer_inputs()
    previous.REVIEW_TESTS=REVIEW_TESTS
    result=subprocess.run(previous.suite_command(),cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output=result.stdout.decode('utf8',errors='replace')
    counts=re.findall(r'^Ran (\d+) tests in ',output,re.M)
    count=int(counts[0]) if len(counts)==1 else 0
    record={'version':'2.1.0','internal':105,'tests':count,'exit':result.returncode,
      'log':log.relative_to(ROOT).as_posix(),'log_sha256':hashlib.sha256(result.stdout).hexdigest(),
      'source_inputs':before,'source_inputs_unchanged':before==inputs(),
      'reviewer_inputs':review,'reviewer_inputs_unchanged':review==reviewer_inputs(),
      'review_test_modules':list(REVIEW_TESTS),'utc':datetime.now(timezone.utc).isoformat()}
    log.write_bytes(result.stdout);receipt.write_text(json.dumps(record,indent=2)+'\n','utf8')
    print(output[-7000:])
    assert result.returncode==0 and count>=110 and re.search(r'\nOK\s*$',output)
    assert record['source_inputs_unchanged'] and record['reviewer_inputs_unchanged']

if __name__=='__main__': main()
