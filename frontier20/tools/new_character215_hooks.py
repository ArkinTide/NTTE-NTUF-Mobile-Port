"""Reinstall NTTE/NTUF custom-character access and its native regressions.

Run after the maintained Frontier staging installers. Original gameplay and
permanent unlock eligibility stay owned by their existing source providers.
"""
from __future__ import annotations
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIGNATURE = b"function scr_race_is_unlocked(_race) {"
BEGIN = b"// BEGIN CUSTOM CHARACTER215 ACCESS"
END = b"// END CUSTOM CHARACTER215 ACCESS"
TEST_BEGIN = b"// BEGIN NEW CHARACTER215 REGRESSIONS"
TEST_END = b"// END NEW CHARACTER215 REGRESSIONS"


def replace_block(data, begin, end, block, *, after=None):
    if begin in data:
        if data.count(begin) != 1 or data.count(end) != 1:
            raise ValueError("Ambiguous existing character215 block")
        start = data.index(begin)
        finish = data.index(end, start) + len(end)
        return data[:start] + block + data[finish:]
    if after is None:
        return data + b"\r\n" + block + b"\r\n"
    if data.count(after) != 1:
        raise ValueError("Character215 insertion anchor changed")
    return data.replace(after, after + b"\r\n    " + block + b"\r\n", 1)


def install(project):
    project = Path(project)
    path = project / "scripts/scrRaces/scrRaces.gml"
    data = path.read_bytes()
    newline = b"\r\n" if b"\r\n" in data else b"\n"
    block = newline.join([
        BEGIN,
        b"    // Custom character access is temporary; disabled content and",
        b"    // unavailable runtimes retain their ordinary selection gates.",
        b"    if(scrGameIsCustomMode() && scrCustomParam(\"unlock_chars\")) {",
        b"        var _native=scrNTTEFullRaceNumeric(_race);",
        b"        if(_native>=0) return scrNTTEFullRaceReady(_native);",
        b"        if(scrFRRaceIs(_race)) return scrFREnabled();",
        b"    }",
        b"    " + END,
    ])
    changed = []
    updated = replace_block(data, BEGIN, END, block, after=SIGNATURE)
    if updated != data:
        path.write_bytes(updated)
        changed.append(str(path))
    tests = ROOT / "native/new_character215_tests.gml"
    path = project / "scripts/scrNTTEFullRaceProgressionNativeTests/scrNTTEFullRaceProgressionNativeTests.gml"
    data = path.read_bytes()
    block = TEST_BEGIN + b"\r\n" + tests.read_bytes().rstrip(b"\r\n") + b"\r\n" + TEST_END
    updated = replace_block(data, TEST_BEGIN, TEST_END, block)
    if updated != data:
        path.write_bytes(updated)
        changed.append(str(path))
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT / "staging/project")
    print("\n".join(install(parser.parse_args().project)) or "Already installed")
