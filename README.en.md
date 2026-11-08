# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

Android/iOS source port of NTTE with **Uncharted Frontier (NTUF) 1.0.3.3**,
Undergrowth, Details+ and Simplified Chinese support. Current version **2.0.4**,
internal build **100**.

Get APK/IPA from the [MEGA download folder](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) and verify
`SHA256SUMS-NTTE-NTUF-2.0.4.txt`. GitHub distributes text source and release notes;
iOS requires re-signing. See the [2.0.4 notes](docs/RELEASE-2.0.4.md).

## 2.0.4 — NTTE + NTUF 2.0.4: weather, walls and input repairs

The newly compiled final Windows VM/input passed 67 explicitly selected native
cases. A hash-verified Python log records 256 passing checks. Earlier VM passes
are not inherited. See the [current validation summary](docs/validation/2.0.4-development-regression.json)
for exact cases and evidence.

Fix the blizzard right-edge seam, the Chinese Lightring label, area callback errors, and laboratory/HQ secret-room wall sides. Repair the reproduced City 17 hostile ghost possession of an allied host and Jungle wall-ambush landing handoff. Pocket Teleporter retains continuous stick angles and short taps; improve controller routing, Android device assignment and disconnect recovery. Reduce repeated module lookups and dense drone-interception work, coalescing overlapping flashes and sound requests while preserving individual hostile projectile destruction, native callbacks and random sequences. Fix premature native GameOver during Robot blue-screen revival and short 60 Hz menu taps being lost to repeated sampling; retain genuine YES Cyberspace travel and the original NO death flow. Check current local input ownership in character selection and settings so stale direction presses left by a removed touch joystick cannot keep changing menu choices.

Android versionCode is 3000100, retaining application/signing identities and checked
16KB layout. iOS build 100 requires re-signing; new game data uses a retained native
Runner without a fresh Mac native build. GAME_BUILD/save protocol remains 3004.

Persistent menu audio noise remains unresolved. Specific charmed-host possession
and wall-top Jungle awakening blockers have verified repairs; unknown invisible
enemy scenarios are not generally certified. Silent background desktop tests do not establish phone mixing or frame
rates. No physical Android/iOS, complete random campaign or universal FPS acceptance
is claimed.

## Source and building

`project/` is the accepted common source, `platforms/android/` holds Android text
overlays, and `frontier20/` holds adapters, offline dependencies, localization and
upstream text references. Artwork, audio, fonts, icons, commercial Runners, compiled
extensions and installers are absent from Git and must be obtained separately.
See [building](docs/BUILDING.en.md), [source policy](docs/SOURCE_ONLY.md) and
[source restoration](frontier20/SOURCE_REPRODUCTION.md).

[License](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md) are retained.
This is an unofficial port. History: [2.0.2](docs/RELEASE-2.0.2.md),
[2.0.0](docs/RELEASE-2.0.0.md).
