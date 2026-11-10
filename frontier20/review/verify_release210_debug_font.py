"""Current2.1.0 static font range evidence; leaves previous reports untouched."""
from pathlib import Path as _Path
import runpy as _runpy
_source=_runpy.run_path(str(_Path(__file__).with_name('verify_release205_debug_font.py')))['_text205']
for _old,_new in [('dbg-font-full-range-coverage-205','dbg-font-full-range-coverage-210'),
                 ('"internal":103','"internal":104'),('"version":"2.0.5"','"version":"2.1.0"')]:
    assert _old in _source
    _source=_source.replace(_old,_new)
_entry='\nif __name__=="__main__":main()\n'
assert _source.count(_entry)==1
exec(compile(_source.replace(_entry,'\n'),str(_Path(__file__)),'exec'),globals())
if __name__=='__main__':main()
