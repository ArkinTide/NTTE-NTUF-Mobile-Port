from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest

import fr_cluster_factory205_hooks as hook


ROOT = Path(__file__).resolve().parents[1]
UG = "scripts/scrUndergrowthNative/scrUndergrowthNative.gml"


class ClusterFactory205HookTests(unittest.TestCase):
    def fixture(self, project):
        for relative in [UG]:
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / "staging/project" / relative, target)
        for source in (ROOT / "generated-code").glob("*.gml"):
            target = project / "scripts" / ("frCode_" + source.stem) / (source.stem + ".gml")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    def test_all_real_factories_and_native_hook_are_idempotent(self):
        with TemporaryDirectory() as folder:
            project = Path(folder)
            self.fixture(project)
            report = hook.apply(project)
            self.assertEqual(report["source_factories_retained"], 35)
            first = {p.relative_to(project): p.read_bytes() for p in project.rglob("*.gml")}
            hook.apply(project)
            self.assertEqual(first, {p.relative_to(project): p.read_bytes()
                                    for p in project.rglob("*.gml")})
            ug = (project / UG).read_text("utf-8-sig")
            self.assertEqual(ug.count("return scrFRClusterCreate(_x,_y,_source);"), 1)
            self.assertIn("return scrUGCreate(_x,_y,_source.name);", ug)
            self.assertIn("return instance_create(_x,_y,_object);", ug)

    def test_missing_anchor_cannot_leave_partial_factory_edits(self):
        with TemporaryDirectory() as folder:
            project = Path(folder)
            self.fixture(project)
            (project / UG).write_text("function unsupported_base() {}\n", "utf-8")
            before = {p.relative_to(project): p.read_bytes() for p in project.rglob("*.gml")}
            with self.assertRaises(AssertionError):
                hook.apply(project)
            self.assertEqual(before, {p.relative_to(project): p.read_bytes()
                                     for p in project.rglob("*.gml")})

    def test_constructor_coordinates_and_extra_inputs_survive(self):
        raw = ("function fr_T_create(_frl__x=undefined, _frl__y=undefined, _frl__config=undefined) {\n"
               "return scrFRInstanceCreate(_frl__x, (_frl__y + choose(4, 8)), FRCustomEnemy);\n}\n")
        updated, count = hook.retain_factories(raw)
        self.assertEqual(count, 1)
        self.assertIn("scrFRClusterEnemyCreate(_frl__x, (_frl__y + choose(4, 8)), fr_T_create, "
                      "[_frl__x, _frl__y, _frl__config])", updated)
        self.assertEqual(hook.retain_factories(updated), (updated, 0))
        native = (ROOT / "native/cluster_factory205.gml").read_text("utf-8")
        self.assertIn("_actor.fr_cluster_args=scrFRClusterInputCopy(_args)", native)
        self.assertIn("var _args=scrFRClusterInputCopy(_inputs)", native)
        self.assertNotIn("instance_destroy(", native)


if __name__ == "__main__":
    unittest.main()
