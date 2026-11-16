# Nuclear Throne: NTTE + Uncharted Frontier — Mobile Port

[简体中文](README.md) | [English](README.en.md)

Android/iOS source port of NTTE with **Uncharted Frontier (NTUF) 1.0.3.3**,
Undergrowth, Details+ and Simplified Chinese support. Current version **2.1.3**,
internal build **108**.

Get APK/IPA from the [MEGA download folder](https://mega.nz/folder/PfIDSaSZ#ZcRokP34or9J0JofsIgrEA) and verify
`SHA256SUMS-NTTE-NTUF-2.1.3.txt`. GitHub distributes text source and release notes;
iOS requires re-signing. See the [2.1.3 notes](docs/RELEASE-2.1.3.md).

## 2.1.3 build108 — Zone generation, Bubbles attacks and performance repairs

The newly compiled final Windows VM/input passed 32 explicitly selected native
cases. A hash-verified Python log records 160 passing checks. Earlier VM passes
are not inherited. See the [current validation summary](docs/validation/2.1.3-development-regression.json)
for exact cases and evidence.

Guard native instance access in data callbacks, selected homing targets that disappear, orphaned impact-drone hitboxes and sparse settings-category resets. Open a shoreline entrance through only newly generated walls when a Coast area-orb component is sealed. Preserve final-puzzle tile coordinates, artwork and interaction after floor replacement, and rerun ordered key merges, enemy gates, delivery and reward checks.

Consume fired fly larvae once and prevent killed larvae from spawning again; exclude the quest bone from cursed weapon chests. Preserve Bubbles' last valid aim when a manual-aim gesture returns to the dead zone before release; verify both starting weapons with ability mode enabled and disabled while retaining deliberate outside cancellation.

Add the default-on Match Crosshair Color switch to the outline/health-color page. Disabling it returns desktop, gamepad and touch crosshairs to white. Stabilize the normal menu spiral's complementary-mask sampling at 60 Hz while preserving other portal animation.

Require sustained CPU-processing headroom before a 60 Hz recovery probe. If the probe fails, remain at 30 Hz for the scene; a new generation, menu or opt-out resets this protection, while pausing preserves it. Five continuously stable seconds accept a recovery. Compensate only real inherited native Alarm slots, and prune fused Quasar/melee laser candidates before the unchanged precise collision checks. These shared paths also serve added maps and the embedded hard mode. Physical Android/iOS frame rates and elimination of every unexplained crash are not claimed.

Android versionCode is 3000108, retaining application/signing identities and checked
16KB layout. iOS build 108 requires re-signing; new game data uses a retained native
Runner without a fresh Mac native build. GAME_BUILD/save protocol remains 3004.

This release validates the current selected cases for zone routes, object lifecycles,
Bubbles attacks, the final puzzle, crosshair colors, frame-rate control and fused lasers. Unknown random
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
