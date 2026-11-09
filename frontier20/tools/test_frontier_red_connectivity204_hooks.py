"""Guard narrow native registration while geometry is tested by the Runner."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import fr_red_connectivity204_hooks as hooks


class RedConnectivity204HookTests(unittest.TestCase):
    def fixture(self, folder):
        project=Path(folder)
        for relative,before,after,marker in hooks.specs()[:-1]:
            path=project/relative;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text((path.read_text("utf8") if path.exists() else "")+before+"\n","utf8")
        template=project/"scripts/scrNTTEFullAreas/scrNTTEFullAreas.yy"
        template.parent.mkdir(parents=True,exist_ok=True)
        template.write_text(json.dumps({"name":"scrNTTEFullAreas","%Name":"scrNTTEFullAreas","resourceType":"GMScript"}),"utf8")
        (project/"nuclearthronemobile.yyp").write_text(json.dumps({"resources":[]}),"utf8")
        return project

    def snapshot(self, project):
        return {p.relative_to(project).as_posix():p.read_bytes() for p in project.rglob("*") if p.is_file()}

    def test_registration_is_idempotent_and_uses_maintained_real_geometry_probe(self):
        with TemporaryDirectory() as folder:
            project=self.fixture(folder);hooks.apply(project);before=self.snapshot(project)
            for _ in range(3): hooks.apply(project);self.assertEqual(before,self.snapshot(project))
            resource=json.loads((project/"nuclearthronemobile.yyp").read_text("utf8"))["resources"]
            self.assertEqual([hooks.SCRIPT],[r["id"]["name"] for r in resource])
            staged=project/f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.gml"
            self.assertEqual((hooks.ROOT/"native/red_connectivity204_tests.gml").read_bytes(),staged.read_bytes())
            source=staged.read_text("utf8")
            for token in ["instance_create(0,0,GenCont)","event_perform(ev_alarm,2)","event_perform(ev_alarm,0)",
                          "event_perform(ev_alarm,1)","instance_place_list(_x,_y,Wall", "scrNTTESolidWallGenerate()"]:
                self.assertIn(token,source)

    def test_late_hook_failure_and_duplicate_resource_never_write_partial_stage(self):
        for variant in ["missing","duplicate","partial","resource"]:
            with self.subTest(variant=variant),TemporaryDirectory() as folder:
                project=self.fixture(folder)
                if variant=="resource":
                    r={"id":{"name":hooks.SCRIPT,"path":f"scripts/{hooks.SCRIPT}/{hooks.SCRIPT}.yy"}}
                    (project/"nuclearthronemobile.yyp").write_text(json.dumps({"resources":[r,r]}),"utf8")
                else:
                    relative,before,after,marker=hooks.specs()[-1];path=project/relative
                    path.write_text({"missing":"unrelated", "duplicate":before+before,"partial":before+marker}[variant],"utf8")
                initial=self.snapshot(project)
                with self.assertRaises(RuntimeError):hooks.apply(project)
                self.assertEqual(initial,self.snapshot(project))


if __name__=="__main__":unittest.main()
