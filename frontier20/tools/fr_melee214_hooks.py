"""Retained 2.1.4 melee/control changes on the current maintenance stage."""
from pathlib import Path


def apply(project):
    path = Path(project) / "scripts/scrNTTEFullScythe/scrNTTEFullScythe.gml"
    source = path.read_text(encoding="utf-8-sig")
    arrow = ("    draw_sprite_ext(sprLoadoutArrow,0,x+12*_scale,y-12*_scale,"
             "0.65*_scale,0.65*_scale,90,c_white,_alpha);")
    marker = "    // FRONTIER214 Scythe mode control keeps its weapon icon without a corner arrow."
    if marker not in source:
        assert source.count(arrow) == 1, ("Scythe mode corner arrow", source.count(arrow))
        source = source.replace(arrow, marker, 1)
        path.write_text(source, encoding="utf8", newline="\n")
    assert source.count(marker) == 1 and arrow not in source, "Scythe arrow-removal marker contradicts its draw body"
    return {"scythe_control": "removed only its decorative corner arrow; touch and form cycling retained"}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    print(json.dumps(apply(args.project), ensure_ascii=False, indent=2))
