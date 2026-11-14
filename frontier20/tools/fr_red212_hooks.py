"""Freeze only the current Red generator after pre-population safe spawning."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "staging/project"
REL = "scripts/scrNTTEFullRedAreaNative/scrNTTEFullRedAreaNative.gml"
BEFORE = "function scrNTTEFullRedPopulateNative() {scrPopulate();scrNTTEFullRedPopExtras();scrFRRedTerrain210Finish();}"
AFTER = """function scrNTTEFullRedPopulateNative() {
    // FRONTIER212 RED FINAL POPULATION BOUNDARY
    // The callback is bound to this GenCont. Its initial safe-spawn shifts
    // have finished before Alarm0. Appended rooms must not restart Step's
    // Floor-only translation after Wall/Fake/Helper geometry already exists.
    if(object_index==GenCont) safespawn=false;
    scrPopulate();scrNTTEFullRedPopExtras();scrFRRedTerrain210Finish();
}"""


def apply(project=PROJECT):
    path = Path(project) / REL
    source = path.read_text(encoding="utf-8")
    if AFTER in source:
        return
    if source.count(BEFORE) != 1:
        raise RuntimeError("Red212 requires the exact audited population callback")
    path.write_text(source.replace(BEFORE, AFTER), encoding="utf-8")


if __name__ == "__main__":
    apply()
