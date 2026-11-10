# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

Android/iOS source port of NTTE with **Uncharted Frontier (NTUF) 1.0.3.3**,
Undergrowth, Details+ and Simplified Chinese support. Current version **2.1.0**,
internal build **105**.

Get APK/IPA from the [MEGA download folder](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) and verify
`SHA256SUMS-NTTE-NTUF-2.1.0.txt`. GitHub distributes text source and release notes;
iOS requires re-signing. See the [2.1.0 notes](docs/RELEASE-2.1.0.md).

## 2.1.0 build105 — Content controls, walls and drone fixes

The newly compiled final Windows VM/input passed 28 explicitly selected native
cases. A hash-verified Python log records 403 passing checks. Earlier VM passes
are not inherited. See the [current validation summary](docs/validation/2.1.0-development-regression.json)
for exact cases and evidence.

Fix reciprocal allied-fire collisions for Hyperion drones and batch dense interception effects; repair duplicate Red Caves walls, isolated caps and road boundaries; match the Storms locked silhouette and translate the Beetle unlock hint. Add default-on independent NTUF and Undergrowth switches: disabling NTUF greys out its other settings, both switches are locked during live runs, and Continue retains the saved packs. Add NTTE-style NTUF charge bars, persistent achievement exclusion for console/practice/custom runs, and weather music in the triggering room. Fix native content-switch input, allied Powder Hammer provenance, and the complete Cyberspace return including old saves. Block console-run gold/content persistence and isolate NTTE/NTUF custom progress per preset slot.

Android versionCode is 3000105, retaining application/signing identities and checked
16KB layout. iOS build 105 requires re-signing; new game data uses a retained native
Runner without a fresh Mac native build. GAME_BUILD/save protocol remains 3004.

This release validates the selected content switches, charge HUD, achievement exclusion,
same-room weather music, drone collisions and red terrain scenarios. Unknown random
maps and every weapon combination are not generally certified. Silent background desktop tests do not establish phone mixing or frame
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
