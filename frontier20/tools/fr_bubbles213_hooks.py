"""Keep a valid Bubbles manual aim through the touch release dead zone."""
from pathlib import Path


def transform_touch(text):
    marker = "// FRONTIER213 BUBBLES VALID GESTURE RELEASE"
    if marker in text:
        assert text.count(marker) == 1
        return text
    anchor = "\t\t\n        if (!scrFRBubblesStartupTestsTouchButton(\"held\",index, mb_left) || (distance_to_point(mx, my) > rad * 3)) {"
    assert text.count(anchor) == 1, "Bubbles manual touch boundary changed"
    code = """\t\t
        // FRONTIER213 BUBBLES VALID GESTURE RELEASE
        scrFRBubblesManualRelease213(index,mx,my,dis,dir,
            scrFRBubblesStartupTestsTouchButton("pressed",index,mb_left),
            scrFRBubblesStartupTestsTouchButton("held",index,mb_left),
            scrFRBubblesStartupTestsTouchButton("released",index,mb_left));
"""
    return text.replace(anchor, code + anchor, 1)


def transform_fixture(text):
    marker = "// FRONTIER213 RAW TOUCH GESTURE FIXTURE"
    if marker in text:
        assert text.count(marker) == 1
        return text
    anchor = "function scrFRBubblesStartupTestsTouchState() {\n"
    assert text.count(anchor) == 1
    text = text.replace(anchor, anchor + "    // FRONTIER213 RAW TOUCH GESTURE FIXTURE\n"
        + "    var _fr213=scrFRBubbles213TouchState();\n"
        + "    if(is_struct(_fr213)) return _fr213;\n", 1)
    oldx = "return is_struct(_state)?x+rad:device_mouse_x_to_gui(_index);"
    oldy = "return is_struct(_state)?y:device_mouse_y_to_gui(_index);"
    assert text.count(oldx) == text.count(oldy) == 1
    return text.replace(oldx, "return is_struct(_state)?x+rad*(_state.touch[$ \"dx\"]??1):device_mouse_x_to_gui(_index);").replace(
        oldy, "return is_struct(_state)?y+rad*(_state.touch[$ \"dy\"]??0):device_mouse_y_to_gui(_index);")


def apply(project, native):
    project, native = Path(project), Path(native)
    paths = {
        project / "objects/JoystickAttack/Other_10.gml": transform_touch,
        project / "scripts/scrFrontier_bubbles_startup_tests/scrFrontier_bubbles_startup_tests.gml": transform_fixture,
        native / "bubbles_startup_tests.gml": transform_fixture,
    }
    writes = []
    for path, transform in paths.items():
        raw = path.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
        newline = "\r\n" if "\r\n" in text else "\n"
        result = transform(text.replace("\r\n", "\n"))
        data = (b"\xef\xbb\xbf" if bom else b"") + result.replace("\n", newline).encode("utf-8")
        writes.append((path, raw, data))
    for path, before, after in writes:
        if before != after:
            path.write_bytes(after)
    return {"changed": [str(p) for p, a, b in writes if a != b]}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(apply(root / "staging/project", root / "native"))
