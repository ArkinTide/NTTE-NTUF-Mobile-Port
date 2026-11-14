"""Verify the native 2.1.2 dual-fire case; never accept historical205 evidence."""
import json


def verify_bubbles212(smoke):
    prefix='NTUF BUBBLES212 '
    rows=[json.loads(line[len(prefix):]) for line in smoke.splitlines() if line.startswith(prefix)]
    assert len(rows)==2 and [row['rate'] for row in rows]==[30,60]
    expected={'rate','actual_general','controller_named_buttons','touch_joystick_and_ability',
              'idle_no_spray','release_stops','weapon_simultaneous','mode_off_fires','preference_off_original_controls'}
    for row in rows:
        assert set(row)==expected
        for key in expected-{'rate'}:assert row[key] is True or row[key]==1,(key,row[key])
    for summary in (
        'PASS NTUF BUBBLES212 saved bits/default, real touch mode button, simultaneous fire/release mapping, preserved charge/click, disabled preference, JSON, menu and other race',
        'PASS NTUF BUBBLES212 actual General + native controller + touch JoystickAttack/ButtonActive + real Player firing/source race EndStep at30/60Hz',
    ):
        assert smoke.count(summary)==1,summary
    return {'rows':rows,'physical_device_tested':False,
            'scope':'Real native General, controller and mobile-control sampling, ordinary Player weapon ammo use, source bubble charge use and saved preference at30/60Hz; no physical phone claim'}
