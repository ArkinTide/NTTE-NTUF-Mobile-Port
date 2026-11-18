"""Narrow 2.1.4 fixes for the mansion branch and native spiral construction.

Existing 2.1.2/2.1.3 guards for the other supplied screenshots are audited,
not duplicated or removed. This installer never imports assets or rebuilds.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GOLD_OLD = ('if ((_frl__statueIndex >= 0)) {\n'
            '{ var __fr_with147 = scrFRWithValues(scrFRIndexGet(_frl__goldStationFloor, (_frl__goldStationIndex--)))')
GOLD_NEW = ('// FRONTIER214 MANSION: this branch owns goldStationIndex, not the Oasis local.\n'
            'if ((_frl__goldStationIndex >= 0)) {\n'
            '{ var __fr_with147 = scrFRWithValues(scrFRIndexGet(_frl__goldStationFloor, (_frl__goldStationIndex--)))')
WARM_OLD = '''repeat (round(150 / timescale)) {
    event_perform(ev_step, 0)

    with Spiral
\t\tevent_perform(ev_step, 0)

    with SpiralDebris
\t\tevent_perform(ev_step, 0)

    with SpiralStar
\t\tevent_perform(ev_step, 0)
}'''
WARM_NEW = '''// FRONTIER214 bounded decorative warm-up. Only these visual events are
// simulated here. Restore host timing even if an authored visual callback fails.
var _fr_spiral_saved_dt214=timescale;
try {
    global.time_scale=scrFRSpiralDelta214(_fr_spiral_saved_dt214);
    repeat (scrFRSpiralWarmCount214(timescale)) {
        event_perform(ev_step, 0)
        with Spiral event_perform(ev_step, 0)
        with SpiralDebris event_perform(ev_step, 0)
        with SpiralStar event_perform(ev_step, 0)
    }
} finally {global.time_scale=_fr_spiral_saved_dt214;}'''
STEP_OLD = '''var _dt = timescale;

grow += 0.0002 * _dt

if (sprite_index == sprSpiralProto) {
    grow += 0.0003 * _dt
}

image_xscale += grow * _dt
image_yscale += grow * _dt
grow += (0.0005 * image_xscale * (grow + 1)) * _dt

var _m;

if (!instance_exists(SpiralCont)) {
\tgrow *= power(1.5, _dt)
\t_m = 3
}
else {
\t_m = 2.5
}'''
STEP_NEW = '''// FRONTIER214 validate local growth before native image bounds are changed.
var _dt=scrFRSpiralDelta214(timescale),_controller=instance_exists(SpiralCont);
if(!scrFRSpiralAdvance214(_dt,_controller)) {instance_destroy();exit;}
var _m=_controller?2.5:3;'''


def replace_once(source, before, after, label):
    if after in source:
        if source.count(after) != 1 or before in source:
            raise RuntimeError('Partial/duplicate Frontier214 hook: ' + label)
        return source
    if source.count(before) != 1:
        raise RuntimeError('Frontier214 source anchor changed: ' + label)
    return source.replace(before, after, 1)


def transform_main(source):
    return replace_once(source, GOLD_OLD, GOLD_NEW, 'mansion gold station')


def transform_warmup(source):
    return replace_once(source, WARM_OLD, WARM_NEW, 'spiral constructor warmup')


def transform_step(source):
    return replace_once(source, STEP_OLD, STEP_NEW, 'spiral finite bounds')


def audit_prior_guards(project):
    # Exact guards are required for all previously repaired screenshot paths.
    from fr_crash213_hooks import transform_actor, transform_menu, transform_projectiles
    project = Path(project)
    actors = (project / 'scripts/scrFRActors/scrFRActors.gml').read_text('utf-8-sig')
    menu = (project / 'scripts/scrOptionsUpdate/scrOptionsUpdate.gml').read_text('utf-8-sig')
    module = next(project.glob('scripts/frCode_Frontier_Projectiles2_mod_*/*.gml')).read_text('utf-8-sig')
    if any((transform_actor(actors) != actors, transform_menu(menu) != menu,
            transform_projectiles(module) != module)):
        raise RuntimeError('Prior213 screenshot guard is absent; install reviewed213 hooks first')
    wall = (project / 'scripts/scrNTTESolidWalls/scrNTTESolidWalls.gml').read_text('utf-8-sig')
    begin = wall.index('function scrNTTESolidWallContact(')
    body = wall[begin:wall.find('\n}', begin)+2]
    guard = 'if(!instance_exists(_wall)) return [_x,_y];'
    if guard not in body or body.index(guard) > body.index('_wall.object_index'):
        raise RuntimeError('Prior212 stale wall contact guard is absent')
    return ['image3: stale Slash/Wall contact', 'image4: sparse settings reset',
            'images5-6: PopoRocketSmall target lifetime', 'image7: struct instance creation']


def apply(project):
    project = Path(project)
    modules = list(project.glob('scripts/frCode_Frontier_Main_mod_*/*.gml'))
    if len(modules) != 1:
        raise RuntimeError('Expected one Frontier_Main module')
    audited = audit_prior_guards(project)
    targets = {modules[0]: transform_main,
               project / 'objects/SpiralCont/Create_0.gml': transform_warmup,
               project / 'objects/Spiral/Step_0.gml': transform_step}
    prepared = []
    for path, transform in targets.items():
        raw = path.read_bytes()
        source = raw.decode('utf-8-sig').replace('\r\n', '\n')
        result = transform(source)
        newline = '\r\n' if b'\r\n' in raw else '\n'
        bom = b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b''
        prepared.append((path, raw, bom+result.replace('\n', newline).encode('utf8')))
    for path, raw, result in prepared:
        if raw != result:
            path.write_bytes(result)
    return {'files': [str(path) for path, _, _ in prepared], 'prior_screenshot_guards': audited}


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    print(json.dumps(apply(args.project), indent=2))
