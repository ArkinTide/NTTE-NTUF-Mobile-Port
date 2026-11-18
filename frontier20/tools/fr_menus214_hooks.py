"""Measured Surgery text and camera-independent Robot reboot choices.

Only the authored disposable text callback, Robot controller/decision hooks,
and its existing GUI-End entry change. Module regeneration is not needed.
"""
from pathlib import Path


SURGERY_OLD = '''function fr_Objects_Frontier_Objects_mod_gml_BetaSurgeryStation_text(_frl__x=undefined, _frl__y=undefined, _frl__surgeryName=undefined, _frl__description=undefined, _frl__player=undefined) {
var _frl__bob = (sin((scrFRSourceFrame() * 0.1)) * 1);
var _frl__halign = draw_get_halign();
var _frl__valign = draw_get_valign();
;
var _frl__yoff = (((16 * round((string_count("#", _frl__description) + 1))) + 28) + _frl__bob);
var _frl__xtextoff = 0;
;
draw_set_font(fntSmall);
;
draw_set_halign(1);
draw_set_valign(0);
scrFRDrawText((_frl__x + _frl__xtextoff), (_frl__y - _frl__yoff), _frl__description);
draw_set_font(fntM1);
;
draw_set_valign(2);
scrFRDrawText((_frl__x + _frl__xtextoff), ((_frl__y - _frl__yoff) - 1), _frl__surgeryName);
draw_set_halign(_frl__halign);
draw_set_valign(_frl__valign);
scrFRInstanceDestroy();
;
}'''
SURGERY_NEW = '''function fr_Objects_Frontier_Objects_mod_gml_BetaSurgeryStation_text(_frl__x=undefined, _frl__y=undefined, _frl__surgeryName=undefined, _frl__description=undefined, _frl__player=undefined) {
// FRONTIER214 MEASURE TRANSLATED SURGERY GLYPHS
scrFRSurgery214Draw(_frl__x,_frl__y,_frl__surgeryName,_frl__description);
scrFRInstanceDestroy();
}'''
CONTROLLER_OLD = 'on_step = fr_Areas_cyberspace_area_gml_bluescreen_step;'
CONTROLLER_NEW = 'on_step = scrFRBluescreen214ControllerStep; // FRONTIER214 RECOVER LIVE CHOICES'
CLICK_OLD = '''function fr_Areas_cyberspace_area_gml_BluescreenButton_click() {
if ((yesButton == true)) {'''
CLICK_NEW = '''function fr_Areas_cyberspace_area_gml_BluescreenButton_click() {
// FRONTIER214 COMMIT ONCE BEFORE THE AUTHORED ACCEPT/DENY CALLBACK
if(!scrFRBluescreen214CommitChoice(creator)) return;
if ((yesButton == true)) {'''
GUI_OLD = 'scrFRBluescreen212DrawGui(); // FRONTIER212 NATIVE GUI END'
GUI_NEW = 'scrFRBluescreen214DrawGui(); // FRONTIER214 EXPLICIT GUI VIEW AND PROJECTION'
PREFERENCE_OLD = 'scrNTTEFullDrawMenuText(drawx, drawy, loc(_name), _text_scale)'
PREFERENCE_NEW = 'scrFRPreference214DrawName(drawx,drawy,loc(_name),_text_scale,_opt) // FRONTIER214 NATIVE PREFERENCE COLUMNS'


def replace_once(source, before, after, label):
    if after in source:
        if source.count(after) != 1 or before in source:
            raise RuntimeError('Partial/duplicate Frontier214 menu hook: ' + label)
        return source
    if source.count(before) != 1:
        raise RuntimeError('Frontier214 menu source anchor changed: ' + label)
    return source.replace(before, after, 1)


def transform_surgery(source):
    return replace_once(source, SURGERY_OLD, SURGERY_NEW, 'Surgery tooltip')


def transform_cyberspace(source):
    source = replace_once(source, CONTROLLER_OLD, CONTROLLER_NEW, 'Robot choice recovery')
    return replace_once(source, CLICK_OLD, CLICK_NEW, 'Robot commit guard')


def transform_gui(source):
    return replace_once(source, GUI_OLD, GUI_NEW, 'Robot screen projection')


def transform_preferences(source):
    return replace_once(source, PREFERENCE_OLD, PREFERENCE_NEW, 'Parrot/Bubbles preference columns')


def apply(project):
    project = Path(project)
    objects = list(project.glob('scripts/frCode_Frontier_Objects_mod_*/*.gml'))
    cyberspace = list(project.glob('scripts/frCode_cyberspace_area_*/*.gml'))
    if len(objects) != 1 or len(cyberspace) != 1:
        raise RuntimeError('Expected exactly one Surgery and one cyberspace source module')
    targets = {
        objects[0]: transform_surgery,
        cyberspace[0]: transform_cyberspace,
        project / 'objects/UberCont/Draw_75.gml': transform_gui,
        project / 'objects/MenuOptions/Other_10.gml': transform_preferences,
    }
    changes = []
    # Validate every boundary before writing any part of the project.
    for path, transform in targets.items():
        raw = path.read_bytes()
        source = raw.decode('utf-8-sig').replace('\r\n', '\n')
        result = transform(source)
        newline = '\r\n' if b'\r\n' in raw else '\n'
        bom = b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b''
        changes.append((path, raw, bom + result.replace('\n', newline).encode('utf8')))
    for path, original, updated in changes:
        if updated != original:
            path.write_bytes(updated)
    return {'files': [str(path) for path, _, _ in changes]}


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    print(json.dumps(apply(args.project), indent=2))
