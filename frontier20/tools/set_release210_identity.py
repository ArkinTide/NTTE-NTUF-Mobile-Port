"""Set 2.1.0/internal105 without changing native save protocol 3004."""
from pathlib import Path
import hashlib

BASE=Path(__file__).with_name('set_release205_identity.py')

def apply(project=None):
    text=BASE.read_text('utf-8-sig').replace('2.0.5','2.1.0').replace('103','105').replace('Release205','Release210')
    entry='\nif __name__ == "__main__":\n    print(json.dumps(apply(), indent=2))\n'
    assert text.count(entry)==1
    scope={'__file__':str(BASE),'__name__':'release210_identity_base'}
    exec(compile(text.replace(entry,'\n'),str(BASE),'exec'),scope)
    return scope['apply']() if project is None else scope['apply'](project)

if __name__=='__main__':
    print(apply())
