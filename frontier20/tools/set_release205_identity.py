"""Set the release identity without changing the native save protocol."""
from pathlib import Path
import json
import re

PROJECT = Path(__file__).resolve().parents[1] / "staging/project"


def apply(project=PROJECT):
    project = Path(project)
    path = project / "objects/UberCont/Create_0.gml"
    text = path.read_text("utf-8-sig")
    if len(re.findall(r"(?m)^#macro GAME_BUILD 3004\s*$", text)) != 1:
        raise RuntimeError("Release205 save protocol anchor changed")
    text, count = re.subn(r'(?m)^#macro GAME_VERSION "[^"\r\n]+"',
                          '#macro GAME_VERSION "2.0.5"', text)
    if count != 1:
        raise RuntimeError("Release205 runtime version anchor changed")
    path.write_text(text, "utf-8", newline="\n")
    path = project / "scripts/scrNTTEUpdate/scrNTTEUpdate.gml"
    text = path.read_text("utf-8-sig")
    for macro, value in (("NTTE_RELEASE_NUMBER", "103"),
                         ("NTTE_RELEASE_TAG", '"2.0.5"'),
                         ("NTTE_RELEASE_VERSION", '"2.0.5"'),
                         ("NTTE_RELEASE_REPO", '"https://github.com/ArkinTide/NTTE-NTUF-Mobile-Port"')):
        text, count = re.subn(r"(?m)^#macro " + macro + r"[^\r\n]*", "#macro " + macro + " " + value, text)
        if count != 1:
            raise RuntimeError("Release205 identity anchor changed: " + macro)
    path.write_text(text, "utf-8", newline="\n")
    for platform, fields in (
        ("windows", {"option_windows_version": "2.0.5.0"}),
        ("android", {"option_android_version": "2.0.5"}),
        ("ios", {"option_ios_version": "2.0.5", "option_ios_build_number": 103}),
    ):
        path = project / f"options/{platform}/options_{platform}.yy"
        text = path.read_text("utf-8-sig")
        data = json.loads(re.sub(r",(?=\s*[}\]])", "", text))
        for key, value in fields.items():
            if key not in data:
                raise RuntimeError("Release205 options anchor changed: " + key)
            data[key] = value
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return {"version": "2.0.5", "internal": 103, "save_protocol_changed": False}


if __name__ == "__main__":
    print(json.dumps(apply(), indent=2))
