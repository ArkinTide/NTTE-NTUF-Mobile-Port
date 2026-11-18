"""Install the reviewed NTTE+NTUF214 native touch move event only."""
from pathlib import Path

OLD = '''event_inherited()

if instance_exists(MenuOptions) or UberCont.opt_keyboard or UberCont.opt_gamepad
\texit

var i = scrFRTouchNearest(rad) // FRONTIER TOUCH MOVE NEAREST

// reset movement
KeyCont.moving[global.index] = 0

if (index == -1) index = i

if (index != -1) {
    var mx = scrFRTouchX(index) /* FRONTIER TOUCH MOVE X */,
\t\tmy = scrFRTouchY(index) /* FRONTIER TOUCH MOVE Y */,
\t\t
\t\tdir = point_direction(x, y, mx, my),
\t\tdis = point_distance(x, y, mx, my),
\t\t
\t\tmh = sign(ldrx(1, dir)),
\t\tmv = sign(ldry(1, dir))
\t
\tif (dis == 0) {
\t\tmh = 0
\t\tmv = 0
\t}
\t
\tif (abs(angle_difference(dir, KeyCont.dir_move[global.index])) < 10) {
\t\tif (current_move_direction_time < 30) {
\t\t\tcurrent_move_direction_time ++
\t\t}
\t}
\telse if (current_move_direction_time > 0) {
\t\tcurrent_move_direction_time -= 3
\t\tif (!current_move_direction_time) {
\t\t\tcurrent_move_direction_time = 0
\t\t}
\t}
\t
\tvar _same_move = max(0, current_move_direction_time - 10) / 20
\t
    KeyCont.dir_move[global.index] = dir
    KeyCont.moving[global.index] = min(1, _same_move + (dis / rad))
\t
\tKeyCont.hold_east[global.index] = (mh == 1)
\tKeyCont.hold_west[global.index] = (mh == -1)
\tKeyCont.hold_sout[global.index] = (mv == 1)
\tKeyCont.hold_nort[global.index] = (mv == -1)

    if scrFRTouchReleased(index) /* FRONTIER TOUCH MOVE RELEASE */ {
\t\tindex = -1
\t}
}
else if (current_move_direction_time > 0) {
\tcurrent_move_direction_time -= 3
\tif (!current_move_direction_time) {
\t\tcurrent_move_direction_time = 0
\t}
}

scrFRTouchMovementSample(global.index,index); // FRONTIER TOUCH MOVE EDGES

if UberCont.opt_hiddensticks {
\timage_alpha = lerp(image_alpha, (index != -1) * 0.2, 0.4)
}
'''
NEW = '''event_inherited()

if instance_exists(MenuOptions) or UberCont.opt_keyboard or UberCont.opt_gamepad
\texit

// FRONTIER214 MOVE: validated capture, center deadzone and logical-time ramp.
scrFRMovementStick214();
'''


def transform(source):
    if source == NEW:
        return source
    if source not in (OLD, OLD.rstrip('\n')):
        raise RuntimeError('Frontier214 JoystickMove input event source anchor changed')
    return NEW


def apply(project):
    path = Path(project) / 'objects/JoystickMove/Other_10.gml'
    raw = path.read_bytes()
    source = raw.decode('utf-8-sig').replace('\r\n', '\n')
    result = transform(source)
    newline = '\r\n' if b'\r\n' in raw else '\n'
    bom = b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b''
    encoded = bom + result.replace('\n', newline).encode('utf8')
    if raw != encoded:
        path.write_bytes(encoded)
    return str(path)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    print(apply(args.project))
