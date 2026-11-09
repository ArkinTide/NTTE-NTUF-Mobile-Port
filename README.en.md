# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

Android/iOS source port of NTTE with **Uncharted Frontier (NTUF) 1.0.3.3**,
Undergrowth, Details+ and Simplified Chinese support. Current version **2.0.4**,
internal build **102**.

Get APK/IPA from the [MEGA download folder](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) and verify
`SHA256SUMS-NTTE-NTUF-2.0.4-build102.txt`. GitHub distributes text source and release notes;
iOS requires re-signing. See the [2.0.4 notes](docs/RELEASE-2.0.4.md).

## 2.0.4 build102 — NTTE + NTUF 2.0.4: mutation pool, passages, artwork and Ultimate Quest revision

The newly compiled final Windows VM/input passed 72 explicitly selected native
cases. A hash-verified Python log records 362 passing checks. Earlier VM passes
are not inherited. See the [current validation summary](docs/validation/2.0.4-build102-development-regression.json)
for exact cases and evidence.

Fix HQ augments and mini mutations leaking into ordinary level-ups while preserving dedicated acquisition and the explicit main-pool augment option. Repair hidden-path/solid-wall collision boundaries in the red crystal cave. Restore authored loadout portraits for Bubbles starter weapons while preserving ordinary weapon drawing fallback. Package missing boss introduction artwork and path aliases to prevent missing-artwork introduction errors. Preserve boss artwork through native pauses and restore it after interrupted introductions. Prevent ordinary level-clear exits during unfinished Ultimate Quest encounters while preserving sequential merges, reward unlocking and native Crown exits.

Android versionCode is 3000102, retaining application/signing identities and checked
16KB layout. iOS build 102 requires re-signing; new game data uses a retained native
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
