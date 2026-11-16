"""Narrow, repeatable reticle setting/draw hooks; never reimport a stage."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def apply(project):
    project=Path(project)
    edits={
        'scripts/scrOptionsUpdate/scrOptionsUpdate.gml':[
            ('cursor = self[$ "opt_cursor"],','cursor = self[$ "opt_cursor"],\n            cursorcolor = self[$ "opt_cursorcol"],'),
            ('opt_color = save_get_option("options", "color", false)', 'opt_color = save_get_option("options", "color", false)\n        opt_ntte_reticlecolor=save_get_option("visual","ntte_reticlecolor",true);'),
            ('scrFRVisual205ColorSync(); // FRONTIER VISUAL205 LOCAL LIVE COLOR','scrFRVisual205ColorSync(); // FRONTIER VISUAL205 LOCAL LIVE COLOR\n        opt_cursorcol=scrFRReticle213Color(); // FRONTIER RETICLE213'),
            ('(opt_cursor != cursor or opt_crosshair != crosshair)','(opt_cursor != cursor or opt_crosshair != crosshair or opt_cursorcol != cursorcolor)'),
        ],
        'objects/MenuOptions/Other_20.gml':[
            ('scrFRVisual205Options(); // FRONTIER VISUAL205 VIDEO SETTINGS','scrFRVisual205Options(); // FRONTIER VISUAL205 VIDEO SETTINGS\nscrFRReticle213Options(); // FRONTIER RETICLE213 SETTINGS'),
        ],
        'objects/TopCont/Draw_0.gml':[
            ('0, (_color ? _color : c_white), _alpha)','0, scrFRReticle213Color(index), _alpha)'),
        ],
        'scripts/scrDrawMobileControls/scrDrawMobileControls.gml':[
            ('var _color = 0x0dfd98,','var _color = scrFRReticle213Color(_index),'),
            ('if (!_splitfire && UberCont.opt_cursorcol != c_white) _color = UberCont.opt_cursorcol','// FRONTIER RETICLE213: the saved toggle also owns split-fire tint.'),
            # The separate local attack button deliberately consumes the same
            # opt_cursorcol cache rebuilt by OptionsUpdate above.
            ('\t\t\t_color = c_white\n        }','\t\t\t// Keep the chosen crosshair tint in simplified controls.\n        }'),
            ('\t    if _color == c_white\n\t        _color = make_color_rgb(125, 253, 13)','\t    // FRONTIER RETICLE213: disabled color matching is white.'),
        ],
        'scripts/scrSave/scrSave.gml':[
            ('"visual_particles", "visual_ntte_autoframerate",','"visual_particles", "visual_ntte_autoframerate", "visual_ntte_reticlecolor",'),
        ],
    }
    pending=[]
    for relative,pairs in edits.items():
        path=project/relative
        raw=path.read_bytes(); text=raw.decode('utf-8-sig').replace('\r\n','\n')
        for old,new in pairs:
            if new in text: continue
            assert text.count(old)==1,(relative,old,text.count(old))
            text=text.replace(old,new)
        out=text.replace('\n','\r\n').encode('utf-8') if b'\r\n' in raw else text.encode('utf-8')
        if raw.startswith(b'\xef\xbb\xbf'):out=b'\xef\xbb\xbf'+out
        pending.append((path,out))
    for path,out in pending:
        if path.read_bytes()!=out:path.write_bytes(out)
    return {'files':len(pending)}

if __name__=='__main__':
    print(apply(ROOT/'staging/project'))
