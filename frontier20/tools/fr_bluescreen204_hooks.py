"""Defer native GameOver only for an unobserved eligible Robot admission."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


RELATIVE = "objects/TopCont/Step_2.gml"
MARKER = "// FRONTIER BLUESCREEN 204 PENDING DEATH"
ANCHOR = ("    if (!UberCont.paused && !instance_exists(GameOver) "
          "&& !scrNTTEFullUnlockPendingPortrait()) {")
REPLACEMENT = ("    " + MARKER + "\n"
               "    if (!UberCont.paused && !instance_exists(GameOver) "
               "&& !scrNTTEFullUnlockPendingPortrait()\n"
               "        && !scrFRBluescreenPendingAdmission204()) {")


def hook_specs():
    return [dict(path=RELATIVE, anchor=ANCHOR, replacement=REPLACEMENT, marker=MARKER)]


def apply(project):
    path = Path(project).resolve() / RELATIVE
    raw = path.read_bytes()
    # Byte replacement retains every unrelated byte, including BOM and the
    # existing newline format. A changed native death gate fails closed.
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    anchor = ANCHOR.encode("utf8")
    replacement = REPLACEMENT.replace("\n", newline.decode()).encode("utf8")
    marker = MARKER.encode("utf8")
    if replacement in raw:
        if raw.count(replacement) != 1 or raw.count(marker) != 1 or anchor in raw:
            raise RuntimeError("Frontier bluescreen204 installed death gate is ambiguous")
        return [dict(path=RELATIVE, status="already-applied")]
    if marker in raw or raw.count(anchor) != 1:
        raise RuntimeError("Frontier bluescreen204 native death gate anchor changed")
    path.write_bytes(raw.replace(anchor, replacement, 1))
    return [dict(path=RELATIVE, status="patched")]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", type=Path)
    args = parser.parse_args()
    print(json.dumps(apply(args.apply) if args.apply else hook_specs(), indent=2))
