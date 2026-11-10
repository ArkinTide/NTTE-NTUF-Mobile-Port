"""Read-only current2.1.0 binary audit, retaining prior concrete package checks."""
from pathlib import Path as _Path
import runpy as _runpy
_prior=_Path(__file__).with_name('inspect_release205_packages.py')
_source=_runpy.run_path(str(_prior))['_text205']
for _old,_new in [('mobile-release205-20261109','mobile-release210-build105-20261110'),
                 ('release205','release210'),('internal103','internal105'),
                 ('2.0.5','2.1.0'),('3000103','3000105'),
                 (', 103',', 105'),('"103"','"105"'),
                 ('dbg-font-full-range-coverage-205','dbg-font-full-range-coverage-210')]:
    _source=_source.replace(_old,_new)
assert _source.count(r'2\.0\.5')==1
_source=_source.replace(r'2\.0\.5',r'2\.1\.0')
_entry='\nif __name__ == "__main__":\n    main()\n'
assert _source.count(_entry)==1
exec(compile(_source.replace(_entry,'\n'),str(_Path(__file__)),'exec'),globals())
_original_delivery_cases=delivery_cases

def delivery_cases(source,selection):
    # Independently reconstruct the frozen205 implementation plus the literal
    # current substitutions, rather than trusting an arbitrary imported CLI.
    path=ROOT/'tools/release210_delivery.py'
    require(source==path.read_text('utf8'),'Current delivery bytes changed')
    tree=ast.parse(source)
    declarations=[n.value for n in tree.body if isinstance(n,ast.Assign)
                  and any(isinstance(t,ast.Name) and t.id=='_changes' for t in n.targets)]
    require(len(declarations)==1,'Ambiguous current delivery substitutions')
    changes=ast.literal_eval(declarations[0])
    prior=_runpy.run_path(str(ROOT/'tools/release205_delivery.py'))
    effective=prior['reviewed_delivery_source']()
    for old,new in changes:
        require(old in effective,'Frozen delivery anchor differs')
        effective=effective.replace(old,new)
    require(selection['version']==VERSION=='2.1.0' and selection['internal']==INTERNAL==105,
            'Current version differs')
    result=_original_delivery_cases(effective,selection)
    require(len(result)==len(set(result))==28,'Current28-case selection differs')
    return result

if __name__=='__main__':main()
