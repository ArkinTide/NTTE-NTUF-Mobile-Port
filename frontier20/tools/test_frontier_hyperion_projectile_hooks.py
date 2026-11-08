from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fr_hyperion_projectile_hooks import (
    apply, ASSIGN, ASSIGN_NEW, CALLBACK, ENTRY, ENTRY_NEW, QUERY, QUERY_NEW,
)


RELATIVE = "scripts/frCode_AugmentCompassion_skill_fixture/source.gml"
FRAGMENT = (
    "function compassion_drone_create() {\n" + ASSIGN + "\nreturn self;\n}\n"
    "function compassion_shock_create() {\n" + ASSIGN + "\nreturn self;\n}\n"
    "function compassion_endstep() {\nvar nearest=" + QUERY + ";\n}\n"
    + ENTRY + "\nif(other.typ>0) { source_sound(); source_fx(); instance_destroy(other); }\n}\n"
    "function unrelated_drone() { on_projectile=other_drone_callback; }\n"
)


class HyperionProjectileHookTests(unittest.TestCase):
    def fixture(self, root, fragment=FRAGMENT, crlf=False, bom=False):
        path = root / RELATIVE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((b"\xef\xbb\xbf" if bom else b"") +
                         fragment.replace("\n", "\r\n" if crlf else "\n").encode("utf8"))
        return path

    def test_one_callback_two_actors_restage_and_preserve_source_effects(self):
        for crlf, bom in ((False, False), (True, True)):
            with self.subTest(crlf=crlf), TemporaryDirectory() as temporary:
                root = Path(temporary)
                path = self.fixture(root, crlf=crlf, bom=bom)
                apply(root)
                once = path.read_bytes()
                for _ in range(3):
                    apply(root)
                    self.assertEqual(path.read_bytes(), once)
                source = path.read_text("utf-8-sig")
                self.assertEqual(source.count(ASSIGN_NEW), 2)
                self.assertEqual(source.count(ENTRY_NEW), 1)
                self.assertEqual(source.count(QUERY_NEW), 1)
                self.assertIn("source_sound(); source_fx(); instance_destroy(other)", source)
                self.assertIn("on_projectile=other_drone_callback", source)
                self.assertEqual(once.startswith(b"\xef\xbb\xbf"), bom)
                self.assertEqual(b"\r\n" in once, crlf)

    def test_changed_duplicate_and_partial_anchors_fail_without_write(self):
        variants = (
            FRAGMENT.replace(QUERY, "changed_source_query"),
            FRAGMENT + ENTRY + "\n}\n",
            FRAGMENT + ASSIGN + "\n",
            FRAGMENT + "// BEGIN FRONTIER HYPERION HOSTILE COLLISION\n",
            FRAGMENT.replace(ENTRY, ENTRY_NEW.replace("// END FRONTIER", "// BROKEN END")),
        )
        for fragment in variants:
            with self.subTest(fragment=fragment[-70:]), TemporaryDirectory() as temporary:
                root = Path(temporary)
                path = self.fixture(root, fragment)
                before = path.read_bytes()
                with self.assertRaises(RuntimeError):
                    apply(root)
                self.assertEqual(path.read_bytes(), before)

    def test_requires_one_exact_mutation_module(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(RuntimeError):
                apply(root)
            path = self.fixture(root)
            other = root / RELATIVE.replace("_fixture", "_duplicate")
            other.parent.mkdir(parents=True)
            other.write_bytes(path.read_bytes())
            with self.assertRaises(RuntimeError):
                apply(root)
            self.assertEqual(path.read_text(), FRAGMENT)


if __name__ == "__main__":
    unittest.main()
