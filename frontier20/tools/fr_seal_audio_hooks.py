"""Give the Heavy Seal's one overdriven swing transient output headroom."""
from pathlib import Path


RELATIVE = "scripts/scrNTTEFullSealHeavy/scrNTTEFullSealHeavy.gml"
ANCHOR = 'snd_play(sndMeleeFlip,0.1+random(0.1),instance_exists(anchor) ? 8:1.5)'
REPLACEMENT = 'scrFRSealHeavySpinSound(instance_exists(anchor)) /* FRONTIER SEAL SPIN AUDIO HEADROOM */'
MARKER = '/* FRONTIER SEAL SPIN AUDIO HEADROOM */'


def apply(project):
    project = Path(project)
    path = project / RELATIVE
    raw = path.read_bytes()
    source = raw.decode("utf-8-sig").replace("\r\n", "\n")
    if REPLACEMENT in source:
        if source.count(REPLACEMENT) != 1 or source.count(MARKER) != 1 or ANCHOR in source:
            raise RuntimeError("Duplicate/partial Heavy Seal spin audio hook")
        return {"file": RELATIVE, "status": "already-applied"}
    if MARKER in source or source.count(ANCHOR) != 1:
        raise RuntimeError("Heavy Seal spin audio source anchor changed")
    source = source.replace(ANCHOR, REPLACEMENT, 1)
    newline = "\r\n" if b"\r\n" in raw else "\n"
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    path.write_bytes(bom + source.replace("\n", newline).encode("utf8"))
    return {"file": RELATIVE, "status": "patched"}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    print(json.dumps(apply(parser.parse_args().project), indent=2))
