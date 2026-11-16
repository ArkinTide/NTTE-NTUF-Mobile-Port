"""Narrow2.1.3 processing clock, timer-slot and merged-beam repairs."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'staging/project'


def read_yy(path):
    return json.loads(re.sub(r',(?=\s*[}\]])', '', path.read_text('utf-8-sig')))


def alarm_slots(project):
    objects = {p.stem: read_yy(p) for p in (Path(project) / 'objects').glob('*/*.yy')}
    memo = {}

    def resolve(name, trail=()):
        if name in memo:
            return memo[name]
        if name in trail:
            raise AssertionError('Object inheritance cycle: ' + name)
        obj = objects[name]
        parent = obj.get('parentObjectId')
        slots = set(resolve(parent['name'], (*trail, name))) if parent else set()
        slots.update(e['eventNum'] for e in obj.get('eventList', []) if e['eventType'] == 2)
        assert all(0 <= i < 12 for i in slots), name
        memo[name] = sorted(slots)
        return memo[name]

    return {name: resolve(name) for name in sorted(objects)}


def alarm_source(project):
    lines = ['// Generated from native object Alarm events, including inherited slots.',
             '// Rebuild with fr_perf213_hooks.py when the object registry changes.',
             'function scrFRAlarmSlotsInit213() {', '    var _slots=[];']
    for name, slots in alarm_slots(project).items():
        lines.append('    _slots[' + name + ']=[' + ','.join(map(str, slots)) + '];')
    lines.extend(['    global.fr_alarm_slots213=_slots;', '}', ''])
    return '\n'.join(lines)


def replace_once(text, before, after):
    if after in text:
        assert text.count(after) == 1
        return text
    assert text.count(before) == 1, before[:120]
    return text.replace(before, after, 1)


def apply(project=PROJECT, register=True):
    project = Path(project)
    writes = []

    def edit(path, transform):
        old = path.read_text('utf-8-sig')
        new = transform(old)
        if new != old:
            path.write_text(new, 'utf8')
            writes.append(str(path))

    alarm_path = ROOT / 'native/alarms213.gml'
    alarm_text = alarm_source(project)
    if not alarm_path.is_file() or alarm_path.read_text('utf8') != alarm_text:
        alarm_path.write_text(alarm_text, 'utf8')
        writes.append(str(alarm_path))
    script = lambda name: project / 'scripts' / name / (name + '.gml')
    edit(script('scrNTTEFullBaseFrameNative'), lambda t: re.sub(
        r'function scrNTTEFullAlarmTopUp\(_add\) \{[\s\S]*?\n\}',
        'function scrNTTEFullAlarmTopUp(_add) {\n    scrFRAlarmTopUp213(_add); // FRONTIER213 EXACT NATIVE ALARM SLOTS\n}', t, count=1))
    draw = project / 'objects/UberCont/Draw_75.gml'
    edit(draw, lambda t: t if 'scrFRClockEnd213();' in t else t + '\n// FRONTIER213 PROCESSING TIME EXCLUDES ENGINE CAP WAIT\nscrFRClockEnd213();\n')
    motion = script('scrNTTEFullMergedMotion')
    before = '''        while(_distance<_maximum) {
            _distance=min(_distance+_step,_maximum);x=_sx+_dx*_distance;y=_sy+_dy*_distance
            if(array_length(_enemies) && place_meeting(x,y,hitme)) {
                var _self=id
                for(var _e=0;_e<array_length(_enemies);++_e) if(instance_exists(_enemies[_e])) with(_enemies[_e]) {
                    if(id!=_self && place_meeting(x,y,_self)) { _meeting=true;break }
                }
                if(_meeting) { _distance-=_step;break }
            }'''
    after = '''        var _candidates=scrFRMergedLaserCandidates213(_enemies,_maximum,_dx,_dy)
        while(_distance<_maximum) {
            _distance=min(_distance+_step,_maximum);x=_sx+_dx*_distance;y=_sy+_dy*_distance
            if(array_length(_candidates) && place_meeting(x,y,hitme) && scrFRMergedLaserMeeting213(_candidates)) {
                _meeting=true;_distance-=_step;break
            }'''
    edit(motion, lambda t: replace_once(t, before, after))
    spiral = script('scrDrawSpiral')
    def draw_spiral(t):
        for suffix in ['c_white, 1)', 'c_black, (0.8 - image_xscale))']:
            call = 'draw_sprite_ext(sprite_index, -1, view_xview + x, view_yview + y, (image_xscale * 10), (image_yscale * 10), (image_angle + 45), ' + suffix
            t = replace_once(t, call, call.replace('draw_sprite_ext(', 'scrFRSpiralDraw213(', 1))
        return t
    edit(spiral, draw_spiral)
    if register:
        from install_native205 import apply as install
        install(project, {'clock212.gml':'scrFrontier_clock212',
                          'clock212_tests.gml':'scrFrontier_clock212_tests',
                          'performance213.gml':'scrFrontier_performance213',
                          'performance213_tests.gml':'scrFrontier_performance213_tests',
                          'alarms213.gml':'scrFrontier_alarms213'})
    return writes


if __name__ == '__main__':
    print(json.dumps(apply(), indent=2))
