"""Install the maintained fog-independent Pet/charm compositor, no project writes on import."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def apply(project):
    project = Path(project)
    path = project / "scripts/scrNTTEFullOutlineOptionsNative/scrNTTEFullOutlineOptionsNative.gml"
    source = (ROOT.parent / "outline-options-native.gml").read_text("utf-8-sig")
    original = path.read_text("utf-8-sig")
    for name in ("scrNTTEFullPetOutlineDraw", "scrNTTEFullCharmOutlineDraw",
                 "scrNTTEFullOutlineBodyCache", "scrNTTEFullCharmReplayReadOnly"):
        assert original.count("function " + name + "(") == 1, (path, name)
        assert source.count("function " + name + "(") == 1, ("maintenance", name)
    assert "function scrNTTEFullOutlineTintCache(" in source
    assert "gpu_set_fog(true," not in source
    # This host source used to lag behind the maintained native baseline.
    # Keep its already-shipped visual-only friendly-eye grouping when replacing
    # the compositor: those allies must not become timed gameplay charms.
    assert 'scrNTTEFullArrayCopy(scrNTTEFullValue(GameCont,"ntte_charm_instance_list",[]))' in source
    assert 'if(!_charmed && (_actor.team!=team_player || _actor.hp<=0)) continue' in source
    if original != source:
        path.write_text(source, "utf-8", newline="\n")
    return {"path": str(path), "status": "already-applied" if original == source else "patched",
            "tint": "RGB-only in-place cache, exact alpha and quality grid",
            "settings": "original Pet/charm ON/OFF/AUTO and shader gates"}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    print(json.dumps(apply(parser.parse_args().project), ensure_ascii=False, indent=2))
