"""Set2.1.1/build106 and preserve save protocol3004."""
from pathlib import Path

def apply(project=None):
    base=Path(__file__).with_name('set_release205_identity.py')
    source=base.read_text('utf-8-sig').replace('2.0.5','2.1.1').replace('103','106').replace('Release205','Release211')
    entry='\nif __name__ == "__main__":\n    print(json.dumps(apply(), indent=2))\n'
    assert source.count(entry)==1
    scope={'__file__':str(base),'__name__':'release211_identity'}
    exec(compile(source.replace(entry,'\n'),str(base),'exec'),scope)
    return scope['apply']() if project is None else scope['apply'](project)

if __name__=='__main__': print(apply())
