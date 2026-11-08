"""Install the 2.0.4 Blizzard join and explicit hidden-room wall style fixes.

Importing this module is read-only. Only the project supplied to apply changes.
The original mod and archived release projects are never installer targets.
"""
from pathlib import Path

from fr_content_hooks import patch


OUTER_BEFORE = 'scrFRDrawSpriteExt(global.fr_module_vars[$ "mod:Frontier_Events"].sprVignetteOuter, 0, x, y, (((0.6 + _frl_eyesRadius) + (scrFRGetSkill("bat ears") * 0.3)) * 3), (((0.6 + _frl_eyesRadius) + (scrFRGetSkill("bat ears") * 0.3)) * 3), 0, _frl__color, 1);'
OUTER_AFTER = 'scrFRBlizzardOuterMask(x, y, (0.6 + _frl_eyesRadius) + (scrFRGetSkill("bat ears") * 0.3), _frl__color);'
TRANSITION_BEFORE = ('function scrNTTEFullChamberTransition(_wall,_area) {\n'
                     '    _wall.topspr=scrNTTEFullAreaWallSprite(_area,"Trans")\n'
                     '    if(_wall.sprite_index==sprWall6Bot) _wall.sprite_index=scrNTTERefSprite("Wall6BotTrans")\n'
                     '}')
TRANSITION_AFTER = ('function scrNTTEFullChamberTransition(_wall,_area) {\n'
                    '    scrFRChamberWallStyle(_wall,_area);\n'
                    '    _wall.topspr=scrNTTEFullAreaWallSprite(_area,"Trans")\n'
                    '}')
TOP_BEFORE = ('                    var _wall=instance_create(_top.x,_top.y,Wall)\n'
              '                    _wall.topspr=_top.values.sprite_index;_wall.topindex=_top.values.image_index')
TOP_AFTER = ('                    var _wall=instance_create(_top.x,_top.y,Wall)\n'
             '                    scrFRChamberWallStyle(_wall,area);\n'
             '                    _wall.topspr=_top.values.sprite_index;_wall.topindex=_top.values.image_index')


def replace_checked(text, before, after, label):
    if after in text:
        if text.count(after) != 1 or text.count(before) != after.count(before):
            raise RuntimeError(f'post203 weather/wall duplicate anchor: {label}')
        return text
    if text.count(before) != 1:
        raise RuntimeError(f'post203 weather/wall anchor changed: {label}')
    return text.replace(before, after, 1)


def apply(project):
    project = Path(project)
    modules = list((project / 'scripts').glob('frCode_Frontier_Events_mod_*/*.gml'))
    if len(modules) != 1:
        raise RuntimeError('post203 weather/wall event module is ambiguous')
    chamber = project / 'scripts/scrNTTEFullFreakChamberNative/scrNTTEFullFreakChamberNative.gml'
    # Validate every production anchor before mutating either source file.
    event_old = modules[0].read_text('utf-8-sig')
    event_new = replace_checked(event_old, OUTER_BEFORE, OUTER_AFTER, 'Blizzard outer mask')
    chamber_old = chamber.read_text('utf-8-sig')
    chamber_new = replace_checked(chamber_old, TRANSITION_BEFORE, TRANSITION_AFTER, 'chamber edge')
    chamber_new = replace_checked(chamber_new, TOP_BEFORE, TOP_AFTER, 'sliding top')
    for path, old, new in ((modules[0], event_old, event_new), (chamber, chamber_old, chamber_new)):
        if old != new:
            path.write_text(new, 'utf-8', newline='\n')
    patch(project, 'scripts/scrFrontier_tests/scrFrontier_tests.gml', 'POST203 WEATHER WALL DRIVER',
          'if(fr_test_case=="post203-weather-wall") {\n'
          '    if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;\n'
          '    if(++fr_test_ticks<45) return;\n'
          '    scrFRPost203WeatherWallTests();\n'
          '    scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
          '    game_end();return;\n'
          '}', anchor='function scrFRIntegrationTestStep() {')
    patch(project, 'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', 'POST203 WEATHER WALL ENTRY',
          'if(scrNTTEFullSmokeAsyncCase("FrontierPost203WeatherWallTests")) {scrFRIntegrationTestStart("post203-weather-wall");return;}',
          anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', before=True)
    return {'native_case': 'FrontierPost203WeatherWallTests',
            'changes': ['Blizzard mask join', 'explicit chamber body and outer wall area']}
