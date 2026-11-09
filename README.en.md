# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

Android/iOS source port of NTTE with **Uncharted Frontier (NTUF) 1.0.3.3**,
Undergrowth, Details+ and Simplified Chinese support. Current version **2.0.5**,
internal build **103**.

Get APK/IPA from the [MEGA download folder](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) and verify
`SHA256SUMS-NTTE-NTUF-2.0.5.txt`. GitHub distributes text source and release notes;
iOS requires re-signing. See the [2.0.5 notes](docs/RELEASE-2.0.5.md).

## 2.0.5 build103 — Resume audio, outline settings, walls and level exits

The newly compiled final Windows VM/input passed 82 explicitly selected native
cases. A hash-verified Python log records 398 passing checks. Earlier VM passes
are not inherited. See the [current validation summary](docs/validation/2.0.5-development-regression.json)
for exact cases and evidence.

- Address resume laser loops, Bubbles' B-skin tooltip and the locked Storms silhouette.
- Add player/Pet outline and color controls to Video settings, sharing the local healthbar color.
- Route Bubbles' preferred ability through attack controls.
- Address wall tops/gaps, Crown Vault exits, Lair return entrapment and invisible invulnerable Pirate entities.
- Count actual combat deaths for Carnivorous Enzymes, retaining its original thirteen-kill one-health heal and preventing duplicate counting.
- All 82 selected native cases on one VM and 398 Python checks passed. Claims remain limited to the selected evidence; Hardmode is unchanged.

Android versionCode is 3000103, retaining application/signing identities and checked
16KB layout. iOS build 103 requires re-signing; new game data uses a retained native
Runner without a fresh Mac native build. GAME_BUILD/save protocol remains 3004.

This release accepts only the selected resume-laser and Pirate lifecycle scenarios.
Other menu mixing and unknown invisible-enemy scenarios are not generally certified. Silent background desktop tests do not establish phone mixing or frame
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
