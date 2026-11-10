# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

Android/iOS source port of NTTE with **Uncharted Frontier (NTUF) 1.0.3.3**,
Undergrowth, Details+ and Simplified Chinese support. Current version **2.1.1**,
internal build **106**.

Get APK/IPA from the [MEGA download folder](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) and verify
`SHA256SUMS-NTTE-NTUF-2.1.1.txt`. GitHub distributes text source and release notes;
iOS requires re-signing. See the [2.1.1 notes](docs/RELEASE-2.1.1.md).

## 2.1.1 build106 — Disabled-content compatibility, water and Robot UI repairs

The newly compiled final Windows VM/input passed 34 explicitly selected native
cases. A hash-verified Python log records 403 passing checks. Earlier VM passes
are not inherited. See the [current validation summary](docs/validation/2.1.1-development-regression.json)
for exact cases and evidence.

Repair disabled NTUF scalar/fusion presets with per-character default starters and disk migration; hide disabled Bubbles selection/statistics and gate Undergrowth factories. Preserve native actor pixels in all water intermediates; optimize content queries/menu synchronization. Suppress authored unlock notices in console runs, normalize notification text color and anchor Robot YES/NO to the live viewport. Correct Custom starting-mutation overflow, reuse the settings scrollbar and preserve scrolled icon hitboxes.

Android versionCode is 3000106, retaining application/signing identities and checked
16KB layout. iOS build 106 requires re-signing; new game data uses a retained native
Runner without a fresh Mac native build. GAME_BUILD/save protocol remains 3004.

This release validates disabled-content preset migration, selection/statistics filtering,
water pixels, notification rendering, the Robot blue-screen lifecycle, and custom mutation
scrollbar dragging and final-row selection. Unknown random
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
