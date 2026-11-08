"""Private scheduled Cyberspace YES/NO diagnostics with raw touchscreen input."""
from pathlib import Path
from fr_content_hooks import patch


def apply(project):
    project = Path(project)
    guard = ('if(os_type==os_windows && scrNTTEFullSmokeEnabled() '
             '&& instance_exists(FRIntegrationTest)) ')
    patch(project, 'objects/UberCont/Step_0.gml', 'BLUESCREEN UI204 BEFORE REAL INPUT',
          guard + 'scrFRBluescreenUITestsBeforeInput();',
          anchor='scrHandleInputsGeneral(global.index)', before=True)
    patch(project, 'objects/FRCustomObject/Step_0.gml', 'BLUESCREEN UI204 ACTUAL STEP',
          guard + 'if(instance_exists(id)) scrFRBluescreenUITestsObserve("step");')
    patch(project, 'objects/FRCustomObject/Step_2.gml', 'BLUESCREEN UI204 ACTUAL END BEFORE',
          guard + 'scrFRBluescreenUITestsObserve("end-before");',
          anchor='scrFRActorStep("on_end_step");', before=True)
    patch(project, 'objects/FRCustomObject/Draw_0.gml', 'BLUESCREEN UI204 ACTUAL DRAW',
          guard + 'if(instance_exists(id)) scrFRBluescreenUITestsObserve("draw");')
    patch(project, 'objects/FRBinding/Draw_0.gml', 'BLUESCREEN UI204 ACTUAL DENIAL DRAW',
          guard + 'if(instance_exists(id)) scrFRBluescreenUITestsBindingDraw();')
    # GUI End follows world/application-surface drawing. The observer only
    # counts completed host frames; the later Step saves the completed image.
    patch(project, 'objects/UberCont/Draw_75.gml', 'BLUESCREEN UI204 COMPLETED DRAW',
          guard + 'scrFRBluescreenUITestsDraw();')
    # Preserve the original skip guard and the global smoke/save isolation.
    # Only this live fixture's post-YES natural Portal restart may execute
    # Vlambeer's ordinary bootstrap and its asynchronous GenCont creation.
    bootstrap = 'if (global.ntte_smoke_active && !scrFRMenuAudioBootTestsSelected()) { instance_destroy(); exit }'
    patch(project, 'objects/Vlambeer/Create_0.gml', 'BLUESCREEN UI204 NATIVE BOOTSTRAP BEFORE',
          'var _fr_blue_native_bootstrap=false;\n'
          + guard + '_fr_blue_native_bootstrap=scrFRBluescreenUITestsNativeBootstrap();\n'
          'if(!_fr_blue_native_bootstrap) {', anchor=bootstrap, before=True)
    patch(project, 'objects/Vlambeer/Create_0.gml', 'BLUESCREEN UI204 NATIVE BOOTSTRAP AFTER',
          '}', anchor=bootstrap)
    patch(project, 'scripts/scrFrontier_tests/scrFrontier_tests.gml', 'BLUESCREEN UI204 NATIVE DEATH GATE TESTS',
          'scrFRBluescreen204Tests();', anchor='scrFRCyberspaceReviveTests();')
    patch(project, 'scripts/scrFrontier_tests/scrFrontier_tests.gml', 'BLUESCREEN UI204 DRIVER',
          'if(string_pos("bluescreen-ui204-",fr_test_case)==1) {\n'
          '    if(!variable_instance_exists(id,"fr_bluescreen_ui")) {\n'
          '        if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;\n'
          '        if(++fr_test_ticks<45) return;\n'
          '        var _rate=string_pos("60",fr_test_case)>0?60:30;\n'
          '        var _entry=string_pos("disabled",fr_test_case)>0?"disabled":\n'
          '            (string_pos("visited",fr_test_case)>0?"visited":"eligible");\n'
          '        scrFRBluescreenUITestsStart(id,_rate,string_pos("yes",fr_test_case)>0,_entry);\n'
          '    }\n'
          '    if(scrFRBluescreenUITestsStep(id)) {\n'
          '        scrNTTESmokeLog("PASS scheduled Robot fatal damage, auto-created blue YES/NO, raw touch, delayed EndStep and native destination/death lifecycle");\n'
          '        scrNTTESmokeLog("PASS full internal selected implemented branches; not complete MOD coverage");\n'
          '        game_end();\n'
          '    }\n'
          '    return;\n'
          '}', anchor='function scrFRIntegrationTestStep() {')
    rows = [('FrontierBluescreenUI204Yes30Tests', 'yes30'),
            ('FrontierBluescreenUI204Yes60Tests', 'yes60'),
            ('FrontierBluescreenUI204No30Tests', 'no30'),
            ('FrontierBluescreenUI204No60Tests', 'no60'),
            ('FrontierBluescreenUI204Disabled30Tests', 'disabled30'),
            ('FrontierBluescreenUI204Disabled60Tests', 'disabled60'),
            ('FrontierBluescreenUI204Visited30Tests', 'visited30'),
            ('FrontierBluescreenUI204Visited60Tests', 'visited60')]
    body = '\n'.join('if(scrNTTEFullSmokeAsyncCase("' + name + '")) '
                     '{scrFRIntegrationTestStart("bluescreen-ui204-' + suffix + '");return;}'
                     for name, suffix in rows)
    patch(project, 'scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml', 'BLUESCREEN UI204 ENTRY',
          body, anchor='        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests"))', before=True)
    return {'diagnostic_only': True, 'native_cases': [name for name, _ in rows],
            'rates': [30, 60], 'raw_device': 'existing desktop-only touch fixture'}
