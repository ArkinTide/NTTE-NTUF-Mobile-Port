"""Small archived installer baselines, independent of the old host layout.

These exact seven files come from the authenticated 2026-11-11 archive. They
are test inputs, not production source or historical passing test evidence.
"""
from pathlib import Path
import hashlib

FIXTURE_ROOT = Path(__file__).resolve().parent / 'fixtures/frozen-archive20261111'
EXPECTED = {
    'host/objects/Player/Destroy_0.gml': '3a870056a703bc6bfb42d9ec2bbe0c0a26b5a64ff340fe266a423686e652daec',
    'host/objects/IDPDSpawn/Create_0.gml': '7f5b10b381c70b6c918a3bae28b4bd2a61a25bae979a9edc49115a80fda172e4',
    'host/objects/HyperCrystal/Create_0.gml': '305dfd23e184749ca631a56a78e401d569180070c22275e2f973193bb8f24a08',
    'frontier20/scripts/scrUndergrowthCallbacks/scrUndergrowthCallbacks.gml': 'fce2fb5b89e443b9357c572d4679cf628fa4f8f5e6889aa41337b7086c55f596',
    'frontier20/objects/WepPickup/Collision_Wall.gml': 'c4e83c0d200b339dc855680c235483fc6d182fadfe081fbc27a633d223c77e1d',
    'frontier20/objects/TopCont/Step_2.gml': '4dc3f59f399fef724bb49c04b6eec3311025bb8fdf9b3cce0517473d0793f446',
    'frontier20/objects/Player/Collision_Wall.gml': 'aaab1f0f2ee109be27988d0e06dad5f11dd750395430db52f38f1b630322332c',
}


def project(group):
    assert group in ('host', 'frontier20')
    for name, expected in EXPECTED.items():
        if name.startswith(group + '/'):
            path = FIXTURE_ROOT / name
            assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, ('Frozen fixture changed', name)
    return FIXTURE_ROOT / group
