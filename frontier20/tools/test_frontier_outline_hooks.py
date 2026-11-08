"""Exact outline emitter and settings preservation checks in disposable projects."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fr_outline_hooks import ROOT, apply
from fr_gml_frontend import tokenize


class OutlineHookTests(unittest.TestCase):
    def test_install_is_idempotent_and_keeps_original_settings(self):
        source = (ROOT.parent / "outline-options-native.gml").read_text("utf8")
        with TemporaryDirectory() as temporary:
            project = Path(temporary)
            path = project / "scripts/scrNTTEFullOutlineOptionsNative/scrNTTEFullOutlineOptionsNative.gml"
            path.parent.mkdir(parents=True)
            path.write_text(source, "utf8")
            self.assertEqual(apply(project)["status"], "already-applied")
            before = path.read_bytes()
            for _ in range(3):
                apply(project)
                self.assertEqual(before, path.read_bytes())
            self.assertIn('if(!scrNTTEFullOptionGet("outline:pets")', source)
            self.assertIn('var _outline=scrNTTEFullOptionGet("outline:charm")', source)
            self.assertIn('(!_outline && !scrNTTEFullOptionGet("shaders"))', source)
            self.assertNotIn("gpu_set_fog(true,", source)
            self.assertIn("gpu_set_colorwriteenable(true,true,true,false)", source)
            self.assertIn("scrNTTEFullOutlineBodyCache(_raw,_cache)", source)
            sync=source.split("function scrNTTEFullCharmOutlineSync() {",1)[1].split("function scrNTTEFullCharmReplayReadOnly",1)[0]
            self.assertIn('scrNTTEFullArrayCopy(scrNTTEFullValue(GameCont,"ntte_charm_instance_list",[]))',sync)
            self.assertIn('with(enemy) if(visible && hp>0 && team==team_player',sync)
            self.assertIn('_index=_charmed?_charm.index:global.index',sync)
            self.assertNotIn('scrNTTEFullParrotCharm(',sync)
            self.assertNotIn('GameCont.ntte_charm_instance_list=',sync)

    def test_native_sources_have_balanced_tokens_and_no_test_production_override(self):
        for path in (ROOT.parent / "outline-options-native.gml", ROOT / "native/outline_tests.gml"):
            tokens = tokenize(path.read_text("utf8"))
            stack = []
            for token in tokens:
                if token.text in ("(", "[", "{"):
                    stack.append(token.text)
                elif token.text in (")", "]", "}"):
                    self.assertEqual(stack.pop(), {")": "(", "]": "[", "}": "{"}[token.text])
            self.assertEqual(stack, [])
        source = (ROOT.parent / "outline-options-native.gml").read_text("utf8")
        self.assertNotIn("os_type", source)
        self.assertNotIn("scrFROutlineTests", source)
        self.assertNotIn("SmokeEnabled", source)


if __name__ == "__main__":
    unittest.main()
