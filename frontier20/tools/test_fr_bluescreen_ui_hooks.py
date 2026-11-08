"""Private blue UI observers preserve real input and scheduled actor dispatch."""
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest

import fr_bluescreen_ui_hooks as hook


HOSTS = {
    "objects/UberCont/Step_0.gml": "input_tick()\nscrHandleInputsGeneral(global.index)\n",
    "objects/FRCustomObject/Step_0.gml": 'scrFRActorStep("on_step");\n',
    "objects/FRCustomObject/Step_2.gml": 'scrFRActorStep("on_end_step");\n',
    "objects/FRCustomObject/Draw_0.gml": "scrFRActorDraw();\n",
    "objects/FRBinding/Draw_0.gml": "scrFRBindingDraw();\n",
    "objects/UberCont/Draw_75.gml": "draw_real_native_gui();\n",
    "objects/Vlambeer/Create_0.gml":
        'if (global.ntte_smoke_active && !scrFRMenuAudioBootTestsSelected()) { instance_destroy(); exit }\n',
    "scripts/scrFrontier_tests/scrFrontier_tests.gml":
        "function scrFRIntegrationTestStep() {\n}\nscrFRCyberspaceReviveTests();\n",
    "scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml":
        '        if(scrNTTEFullSmokeAsyncCase("Release127PerfTests")) {keep_native_case();}\n',
}


class BluescreenUIHooks(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        for relative, text in HOSTS.items():
            path = self.project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf8")

    def text(self, relative):
        return (self.project / relative).read_text("utf-8-sig")

    def test_hooks_preserve_only_the_nine_native_hosts_and_are_idempotent(self):
        result = hook.apply(self.project)
        first = {path.relative_to(self.project).as_posix(): path.read_bytes()
                 for path in self.project.rglob("*.gml")}
        self.assertEqual(set(first), set(HOSTS))
        self.assertTrue(result["diagnostic_only"])
        self.assertEqual(result["rates"], [30, 60])
        hook.apply(self.project)
        self.assertEqual(first, {path.relative_to(self.project).as_posix(): path.read_bytes()
                                 for path in self.project.rglob("*.gml")})
        for relative, original in HOSTS.items():
            text = re.sub(r"^[ \t]*// BEGIN FRONTIER BLUESCREEN UI204[^\n]*\n.*?"
                          r"^[ \t]*// END FRONTIER BLUESCREEN UI204[^\n]*(?:\n|$)",
                          "", self.text(relative), flags=re.M | re.S)
            self.assertEqual([line.strip() for line in text.splitlines() if line.strip()],
                             [line.strip() for line in original.splitlines() if line.strip()], relative)

    def test_raw_touch_precedes_native_input_and_observers_follow_actual_callbacks(self):
        hook.apply(self.project)
        step = self.text("objects/UberCont/Step_0.gml")
        self.assertLess(step.index("input_tick()"), step.index("scrFRBluescreenUITestsBeforeInput()"))
        self.assertLess(step.index("scrFRBluescreenUITestsBeforeInput()"),
                        step.index("scrHandleInputsGeneral(global.index)"))
        for relative, native, observer in (
                ("objects/FRCustomObject/Step_0.gml", 'scrFRActorStep("on_step");', 'Observe("step")'),
                ("objects/FRCustomObject/Draw_0.gml", "scrFRActorDraw();", 'Observe("draw")'),
                ("objects/FRBinding/Draw_0.gml", "scrFRBindingDraw();", "scrFRBluescreenUITestsBindingDraw()"),
                ("objects/UberCont/Draw_75.gml", "draw_real_native_gui();", "scrFRBluescreenUITestsDraw()")):
            text = self.text(relative)
            self.assertEqual(text.count(native), 1)
            self.assertLess(text.index(native), text.index(observer), relative)
        end = self.text("objects/FRCustomObject/Step_2.gml")
        self.assertLess(end.index('Observe("end-before")'), end.index('scrFRActorStep("on_end_step");'))
        for relative in (name for name in HOSTS if name.startswith("objects/")):
            text = self.text(relative)
            self.assertIn("os_type==os_windows && scrNTTEFullSmokeEnabled() && instance_exists(FRIntegrationTest)", text)

    def test_eight_exact_choices_dispatch_distinct_rates_before_existing_smoke_case(self):
        result = hook.apply(self.project)
        names = ["FrontierBluescreenUI204Yes30Tests", "FrontierBluescreenUI204Yes60Tests",
                 "FrontierBluescreenUI204No30Tests", "FrontierBluescreenUI204No60Tests",
                 "FrontierBluescreenUI204Disabled30Tests", "FrontierBluescreenUI204Disabled60Tests",
                 "FrontierBluescreenUI204Visited30Tests", "FrontierBluescreenUI204Visited60Tests"]
        self.assertEqual(result["native_cases"], names)
        smoke = self.text("scripts/scrNTTEFullSmoke/scrNTTEFullSmoke.gml")
        for name, suffix in zip(names, ("yes30", "yes60", "no30", "no60", "disabled30", "disabled60", "visited30", "visited60")):
            self.assertEqual(smoke.count('scrNTTEFullSmokeAsyncCase("' + name + '")'), 1)
            self.assertIn('scrFRIntegrationTestStart("bluescreen-ui204-' + suffix + '")', smoke)
            self.assertLess(smoke.index(name), smoke.index("Release127PerfTests"))
        driver = self.text("scripts/scrFrontier_tests/scrFrontier_tests.gml")
        self.assertIn('if(!scrFRReadyTick() || instance_exists(GenCont) || instance_exists(FloorMaker)) return;', driver)
        self.assertLess(driver.index("if(scrFRBluescreenUITestsStep(id))"), driver.index("game_end();"))
        self.assertNotIn("scrFRInvoke(", driver)
        self.assertNotIn("event_perform(", driver)
        self.assertIn('"visited":"eligible"', driver)
        self.assertIn('scrFRBluescreenUITestsStart(id,_rate,string_pos("yes",fr_test_case)>0,_entry);', driver)

    def test_native_restart_keeps_smoke_isolation_and_core_gate_assertions(self):
        hook.apply(self.project)
        text = self.text("objects/Vlambeer/Create_0.gml")
        guard = HOSTS["objects/Vlambeer/Create_0.gml"].strip()
        self.assertEqual(text.count(guard), 1)
        self.assertLess(text.index("scrFRBluescreenUITestsNativeBootstrap()"), text.index(guard))
        self.assertIn("if(!_fr_blue_native_bootstrap) {", text)
        self.assertNotRegex(text, r"global\.ntte_smoke_active\s*=(?!=)")
        driver = self.text("scripts/scrFrontier_tests/scrFrontier_tests.gml")
        self.assertEqual(driver.count("scrFRBluescreen204Tests();"), 1)
        self.assertLess(driver.index("scrFRCyberspaceReviveTests();"), driver.index("scrFRBluescreen204Tests();"))

    def test_missing_or_duplicate_real_input_anchor_is_rejected(self):
        for content in ("input_tick()\n", "scrHandleInputsGeneral(global.index)\n" * 2):
            path = self.project / "objects/UberCont/Step_0.gml"
            path.write_text(content, encoding="utf8")
            with self.subTest(content=content), self.assertRaises(AssertionError):
                hook.apply(self.project)


if __name__ == "__main__":
    unittest.main()
