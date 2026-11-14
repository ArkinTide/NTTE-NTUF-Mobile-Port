"""Fresh 2.1.2 native debugger range and current Silver font evidence.

Imports and plan are inert. Explicit audit reads current assets and the retained
iOS executable, then writes only the new 212 evidence JSON. Historical globals,
acceptance and CLI are never executed.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
HOST = ROOT.parent / "ntte-complete"
SOURCE = ROOT / "native/menu_repairs.gml"
FONT = ROOT / "staging/project/datafiles/lang/Silver.ttf"
IPA = WORKSPACE / "outputs/NuclearThroneIOS.ipa"
OUTPUT = ROOT / "review/dbg-font-full-range-coverage-212.json"
MACHO = HOST.parent / "inspect_native_timing.py"
REGISTRATION = HOST / "audit_ios_vm_builtins.py"
FROZEN = ROOT / "review/verify_release204_debug_font.py"
FROZEN_SHA = "5197ca1587d2217b0d1f6b6e5aea93c89ab715a8ec80ba350721a901f4721a00"


def install_definitions():
    raw = FROZEN.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == FROZEN_SHA, "Frozen font definitions changed"
    text = raw.decode("utf-8-sig")
    for before, after in (("Preserve completed204 font evidence", "Preserve completed212 font evidence"),
                          ('"version":"2.0.4","internal":100', '"version":"2.1.2","internal":107')):
        assert text.count(before) == 1
        text = text.replace(before, after)
    tree = ast.parse(text, str(FROZEN))
    wanted = {"sha", "functions", "cmap_has", "audit"}
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    assert {node.name for node in nodes} == wanted
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(__file__), "exec"), globals())


install_definitions()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("plan", "audit"), default="plan", nargs="?")
    if parser.parse_args().operation == "audit":
        audit()
    else:
        print(json.dumps({"status": "NOT_REVIEWED", "version": "2.1.2", "internal": 107,
                          "evidence_exists": OUTPUT.exists(),
                          "writes": "Only explicit audit writes new212 static font evidence",
                          "game_build_or_network": False}))


if __name__ == "__main__":
    main()
