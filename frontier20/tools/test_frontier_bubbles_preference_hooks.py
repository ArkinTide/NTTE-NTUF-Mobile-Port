from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fr_bubbles_preference_hooks import apply


FRAGMENTS = {
    "scripts/scrOptionsUpdate/scrOptionsUpdate.gml": '''function scrOptionsUpdate() {
cpref_list = [ "eyes", "melting", "plant", "yv", "steroids", "horror", "rogue", "skeleton", "parrot" ]
        cpref_parrot = save_get_option("cprefs", "parrot", true)
my_player.update_cprefs();
}
''',
    "objects/MenuOptions/Other_20.gml": '''scrOptionsMenuCreateElements(
{key:"cprefs_parrot",char:NTTEFullRace.Parrot},
)


#endregion Controls_Preferences
next_menu_category();
''',
    "scripts/InputHandling/InputHandling.gml": '''_k.press_spec[_index]=raw_press;
        scrNTTEFullParrotToggleInput(_index)
next_input();
''',
    "objects/ButtonActive/Create_0.gml": '''can_forever=function(player) {
return (player.race==3 && scr_player_pref(pinst,"eyes"))
        or (player.race == NTTEFullRace.Parrot && scr_player_pref(pinst,"parrot"))
}
''',
    "objects/ButtonActive/Other_10.gml": '''if !player
	exit
if (player.race == 12 || player.race == NTTEFullRace.Parrot) && forever
    KeyCont.press_spec[_index]=true;
if player.race == 3 || player.race == NTTEFullRace.Parrot
    KeyCont.hold_spec[_index]=true;
raw_hold_release();
''',
    "scripts/scrPlayerCreate/scrPlayerCreate.gml": '''function scrPlayerRaceChange(_race, _skin = -1) {
    if(race!=_race && (race==NTTEFullRace.Parrot || _race==NTTEFullRace.Parrot))
        KeyCont.activeforever[index]=false
    race=_race;
}
''',
}


class BubblesPreferenceHookTests(unittest.TestCase):
    def fixture(self, root, crlf=False, bom=False):
        for name, source in FRAGMENTS.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + source.replace("\n", "\r\n" if crlf else "\n").encode())

    def test_preserves_old_bits_parrot_and_raw_hold_with_stable_restaging(self):
        for crlf, bom in ((False, False), (True, True)):
            with self.subTest(crlf=crlf), TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.fixture(root, crlf, bom)
                apply(root)
                once = {p.relative_to(root): p.read_bytes() for p in root.rglob("*.gml")}
                for _ in range(3):
                    apply(root)
                    self.assertEqual(once, {p.relative_to(root): p.read_bytes() for p in root.rglob("*.gml")})
                read = lambda name: (root / name).read_text("utf-8-sig")
                options = read("scripts/scrOptionsUpdate/scrOptionsUpdate.gml")
                self.assertIn('"skeleton", "parrot" ]', options)
                self.assertEqual(options.count('array_push(cpref_list,"bubbles")'), 1)
                self.assertLess(options.index('cpref_parrot ='), options.index('cpref_bubbles='))
                self.assertIn('save_get_option("cprefs","bubbles",true)', options)
                menu = read("objects/MenuOptions/Other_20.gml")
                self.assertEqual(menu.count('key: "cprefs_bubbles"'), 1)
                self.assertIn('key:"cprefs_parrot",char:NTTEFullRace.Parrot', menu)
                touch = read("objects/ButtonActive/Other_10.gml")
                self.assertIn("raw_hold_release();", touch)
                self.assertIn("scrFRBubblesTouchBlocked(player)", touch)
                sampling = read("scripts/InputHandling/InputHandling.gml")
                self.assertLess(sampling.index("scrNTTEFullParrotToggleInput"), sampling.index("scrFRBubblesToggleInput"))
                for raw in once.values():
                    self.assertEqual(raw.startswith(b"\xef\xbb\xbf"), bom)
                    self.assertEqual(b"\r\n" in raw, crlf)

    def test_changed_duplicate_or_partial_boundary_fails_without_any_write(self):
        target = "objects/ButtonActive/Other_10.gml"
        variants = (
            FRAGMENTS[target].replace("if !player", "if !valid_player"),
            FRAGMENTS[target] + FRAGMENTS[target],
            FRAGMENTS[target] + "// FRONTIER BUBBLES MENU INPUT GUARD\n",
        )
        for fragment in variants:
            with self.subTest(fragment=fragment[:40]), TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.fixture(root)
                (root / target).write_text(fragment, "utf8")
                before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*.gml")}
                with self.assertRaises(RuntimeError):
                    apply(root)
                self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob("*.gml")})


if __name__ == "__main__":
    unittest.main()
