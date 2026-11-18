"""Narrow allocation-free projectile membership/count hooks, no frame cache."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def transform(text):
    for name, args, statement in (
        ('scrFRInstanceExists', '_target',
         'var _fast214=scrFRProjectileFamilyCount214(_target,true);'),
        ('scrFRInstanceNumber', '_target',
         'var _fast214=scrFRProjectileFamilyCount214(_target,false);'),
        ('scrFRInstanceIs', '_target,_type',
         'var _fast214=scrFRProjectileFamilyIs214(_target,_type);'),
    ):
        anchor = f'function {name}({args}) {{'
        block = ('\n    // FRONTIER214 FRESH PROJECTILE FAMILY QUERY\n    ' + statement +
                 '\n    if(!is_undefined(_fast214)) return _fast214;')
        assert text.count(anchor) == 1, name
        if anchor + block not in text:
            text = text.replace(anchor, anchor + block, 1)
    return text


def apply(project=ROOT / 'staging/project'):
    paths = [ROOT / 'native/actors.gml',
             Path(project) / 'scripts/scrFRActors/scrFRActors.gml']
    pending = [(path, transform(path.read_text('utf-8-sig'))) for path in paths]
    for path, text in pending:
        if path.read_text('utf-8-sig') != text:
            path.write_text(text, 'utf8')
    return [str(path) for path, _ in pending]
